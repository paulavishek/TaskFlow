from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.contrib import messages

from .models import (
    WikiPage, WikiCategory, WikiAttachment, WikiLink, 
    MeetingNotes, WikiPageVersion, WikiLinkBetweenPages, WikiPageAccess
)
from .forms import (
    WikiPageForm, WikiCategoryForm, WikiAttachmentForm, WikiLinkForm,
    MeetingNotesForm, WikiPageSearchForm, QuickWikiLinkForm
)
from kanban.models import Board, Task
from accounts.models import Organization


class WikiBaseView(LoginRequiredMixin, UserPassesTestMixin):
    """Base view for wiki operations"""
    
    def test_func(self):
        """Check if user belongs to the organization"""
        org = self.get_organization()
        if not org:
            return False
        # Check if user has a profile in this organization
        return hasattr(self.request.user, 'profile') and self.request.user.profile.organization == org
    
    def get_organization(self):
        """Get organization from URL or user's default"""
        org_id = self.kwargs.get('org_id')
        if org_id:
            return get_object_or_404(Organization, pk=org_id)
        # Get organization from user's profile
        if hasattr(self.request.user, 'profile') and self.request.user.profile:
            return self.request.user.profile.organization
        return None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = self.get_organization()
        context['organization'] = org
        context['categories'] = WikiCategory.objects.filter(organization=org)
        return context


class WikiCategoryListView(WikiBaseView, ListView):
    """List all wiki categories for an organization"""
    model = WikiCategory
    template_name = 'wiki/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20
    
    def get_queryset(self):
        org = self.get_organization()
        return WikiCategory.objects.filter(organization=org).prefetch_related('pages')


class WikiPageListView(WikiBaseView, ListView):
    """List all wiki pages for a category or organization"""
    model = WikiPage
    template_name = 'wiki/page_list.html'
    context_object_name = 'pages'
    paginate_by = 20
    
    def get_queryset(self):
        org = self.get_organization()
        queryset = WikiPage.objects.filter(organization=org, is_published=True)
        
        category_id = self.kwargs.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__contains=query)
            )
        
        return queryset.select_related('category', 'created_by').order_by('-is_pinned', '-updated_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = self.get_organization()
        context['search_form'] = WikiPageSearchForm(self.request.GET, organization=org)
        context['category_id'] = self.kwargs.get('category_id')
        return context


class WikiPageDetailView(WikiBaseView, DetailView):
    """Display a wiki page with all details"""
    model = WikiPage
    template_name = 'wiki/page_detail.html'
    context_object_name = 'page'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        org = self.get_organization()
        return WikiPage.objects.filter(organization=org)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.object
        context['attachments'] = page.attachments.all()
        context['linked_tasks'] = WikiLink.objects.filter(
            wiki_page=page, link_type='task'
        ).select_related('task')
        context['linked_boards'] = WikiLink.objects.filter(
            wiki_page=page, link_type='board'
        ).select_related('board')
        context['related_meeting_notes'] = page.meeting_notes_references.all()
        context['versions'] = page.versions.all()[:5]
        context['breadcrumb'] = page.get_breadcrumb()
        context['incoming_links'] = page.incoming_links.select_related('source_page')
        
        return context
    
    def get(self, request, *args, **kwargs):
        """Increment view count on page load"""
        response = super().get(request, *args, **kwargs)
        self.object.increment_view_count()
        return response


class WikiPageCreateView(WikiBaseView, CreateView):
    """Create a new wiki page"""
    model = WikiPage
    form_class = WikiPageForm
    template_name = 'wiki/page_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.get_organization()
        return kwargs
    
    def form_valid(self, form):
        org = self.get_organization()
        form.instance.organization = org
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        
        # Create initial version
        WikiPageVersion.objects.create(
            page=self.object,
            version_number=1,
            title=self.object.title,
            content=self.object.content,
            edited_by=self.request.user,
            change_summary='Initial creation'
        )
        
        messages.success(self.request, f'Wiki page "{self.object.title}" created successfully!')
        return response
    
    def get_success_url(self):
        return self.object.get_absolute_url()


class WikiPageUpdateView(WikiBaseView, UpdateView):
    """Update an existing wiki page"""
    model = WikiPage
    form_class = WikiPageForm
    template_name = 'wiki/page_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        org = self.get_organization()
        return WikiPage.objects.filter(organization=org)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.get_organization()
        return kwargs
    
    def form_valid(self, form):
        old_content = WikiPage.objects.get(pk=self.object.pk).content
        form.instance.updated_by = self.request.user
        form.instance.version += 1
        response = super().form_valid(form)
        
        # Create version history entry
        if old_content != form.instance.content:
            WikiPageVersion.objects.create(
                page=self.object,
                version_number=self.object.version,
                title=self.object.title,
                content=old_content,
                edited_by=self.request.user,
                change_summary=self.request.POST.get('change_summary', '')
            )
        
        messages.success(self.request, f'Wiki page "{self.object.title}" updated successfully!')
        return response
    
    def get_success_url(self):
        return self.object.get_absolute_url()


class WikiPageDeleteView(WikiBaseView, DeleteView):
    """Delete a wiki page"""
    model = WikiPage
    template_name = 'wiki/page_confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        org = self.get_organization()
        return WikiPage.objects.filter(organization=org)
    
    def get_success_url(self):
        org = self.get_organization()
        return reverse_lazy('wiki:category_list', kwargs={'org_id': org.id})


class WikiCategoryCreateView(WikiBaseView, CreateView):
    """Create a new wiki category"""
    model = WikiCategory
    form_class = WikiCategoryForm
    template_name = 'wiki/category_form.html'
    
    def form_valid(self, form):
        org = self.get_organization()
        form.instance.organization = org
        response = super().form_valid(form)
        messages.success(self.request, f'Category "{self.object.name}" created!')
        return response
    
    def get_success_url(self):
        org = self.get_organization()
        return reverse_lazy('wiki:category_list', kwargs={'org_id': org.id})


class WikiCategoryUpdateView(WikiBaseView, UpdateView):
    """Edit an existing wiki category"""
    model = WikiCategory
    form_class = WikiCategoryForm
    template_name = 'wiki/category_form.html'
    pk_url_kwarg = 'pk'
    
    def get_queryset(self):
        org = self.get_organization()
        return WikiCategory.objects.filter(organization=org)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Category "{self.object.name}" updated!')
        return response
    
    def get_success_url(self):
        org = self.get_organization()
        return reverse_lazy('wiki:category_list', kwargs={'org_id': org.id})


class WikiCategoryDeleteView(WikiBaseView, DeleteView):
    """Delete a wiki category"""
    model = WikiCategory
    template_name = 'wiki/category_confirm_delete.html'
    pk_url_kwarg = 'pk'
    
    def get_queryset(self):
        org = self.get_organization()
        return WikiCategory.objects.filter(organization=org)
    
    def delete(self, request, *args, **kwargs):
        org = self.get_organization()
        messages.success(request, f'Category deleted successfully!')
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        org = self.get_organization()
        return reverse_lazy('wiki:category_list', kwargs={'org_id': org.id})


class WikiLinkCreateView(WikiBaseView, CreateView):
    """Link a wiki page to a task or board"""
    model = WikiLink
    form_class = WikiLinkForm
    template_name = 'wiki/link_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.get_organization()
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_slug = self.kwargs.get('slug')
        if page_slug:
            context['page'] = get_object_or_404(
                WikiPage,
                slug=page_slug,
                organization=self.get_organization()
            )
        return context
    
    def form_valid(self, form):
        page_slug = self.kwargs.get('slug')
        page = get_object_or_404(
            WikiPage,
            slug=page_slug,
            organization=self.get_organization()
        )
        form.instance.wiki_page = page
        form.instance.created_by = self.request.user
        
        # Set the appropriate link (task or board)
        if form.cleaned_data.get('task'):
            form.instance.task = form.cleaned_data['task']
            form.instance.link_type = 'task'
        else:
            form.instance.board = form.cleaned_data['board']
            form.instance.link_type = 'board'
        
        response = super().form_valid(form)
        messages.success(self.request, 'Wiki page linked successfully!')
        return response
    
    def get_success_url(self):
        page_slug = self.kwargs.get('slug')
        return reverse_lazy('wiki:page_detail', kwargs={'slug': page_slug})


@login_required
def wiki_search(request):
    """Search wiki pages and meeting notes"""
    org = request.user.profile.organization if hasattr(request.user, 'profile') else None
    if not org:
        return redirect('home')
    
    query = request.GET.get('q', '')
    results = {
        'pages': [],
        'notes': [],
        'tasks': [],
        'boards': []
    }
    
    if query:
        # Search wiki pages
        results['pages'] = WikiPage.objects.filter(
            organization=org,
            is_published=True
        ).filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )[:10]
        
        # Search meeting notes
        results['notes'] = MeetingNotes.objects.filter(
            organization=org
        ).filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )[:10]
        
        # Search tasks
        from kanban.models import Board
        results['tasks'] = Task.objects.filter(
            column__board__organization=org
        ).filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )[:10]
        
        # Search boards
        results['boards'] = Board.objects.filter(
            organization=org,
            name__icontains=query
        )[:10]
    
    return render(request, 'wiki/search_results.html', {
        'query': query,
        'results': results,
        'organization': org
    })


@login_required
def meeting_notes_list(request):
    """List all meeting notes for an organization"""
    org = request.user.profile.organization if hasattr(request.user, 'profile') else None
    if not org:
        return redirect('home')
    
    notes = MeetingNotes.objects.filter(organization=org).prefetch_related('attendees')
    
    # Filter by related board if specified
    board_id = request.GET.get('board_id')
    if board_id:
        notes = notes.filter(related_board_id=board_id)
    
    return render(request, 'wiki/meeting_notes_list.html', {
        'notes': notes,
        'organization': org,
        'board_id': board_id
    })


@login_required
def meeting_notes_create(request):
    """Create meeting notes"""
    org = request.user.profile.organization if hasattr(request.user, 'profile') else None
    if not org:
        return redirect('home')
    
    if request.method == 'POST':
        form = MeetingNotesForm(request.POST, organization=org)
        if form.is_valid():
            notes = form.save(commit=False)
            notes.organization = org
            notes.created_by = request.user
            notes.save()
            
            # Add attendees
            attendee_usernames = request.POST.get('attendee_usernames', '').split(',')
            for username in attendee_usernames:
                try:
                    user = User.objects.get(username=username.strip())
                    notes.attendees.add(user)
                except User.DoesNotExist:
                    pass
            
            messages.success(request, 'Meeting notes created successfully!')
            return redirect('wiki:meeting_notes_detail', pk=notes.pk)
    else:
        form = MeetingNotesForm(organization=org)
    
    return render(request, 'wiki/meeting_notes_form.html', {
        'form': form,
        'organization': org
    })


@login_required
def meeting_notes_detail(request, pk):
    """Display meeting notes"""
    org = request.user.profile.organization if hasattr(request.user, 'profile') else None
    if not org:
        return redirect('home')
    
    notes = get_object_or_404(MeetingNotes, pk=pk, organization=org)
    
    return render(request, 'wiki/meeting_notes_detail.html', {
        'notes': notes,
        'organization': org
    })


@login_required
@require_http_methods(['GET', 'POST'])
def quick_link_wiki(request, content_type, object_id):
    """Quick link wiki pages to tasks or boards"""
    org = request.user.profile.organization if hasattr(request.user, 'profile') else None
    if not org:
        return JsonResponse({'error': 'No organization found'}, status=400)
    
    if content_type == 'task':
        item = get_object_or_404(Task, pk=object_id, column__board__organization=org)
    elif content_type == 'board':
        item = get_object_or_404(Board, pk=object_id, organization=org)
    else:
        return JsonResponse({'error': 'Invalid content type'}, status=400)
    
    if request.method == 'GET':
        form = QuickWikiLinkForm(organization=org)
        return render(request, 'wiki/quick_link_modal.html', {
            'form': form,
            'content_type': content_type,
            'object_id': object_id,
            'item': item
        })
    
    form = QuickWikiLinkForm(request.POST, organization=org)
    if form.is_valid():
        pages = form.cleaned_data['wiki_pages']
        for page in pages:
            WikiLink.objects.get_or_create(
                wiki_page=page,
                link_type=content_type,
                **{content_type: item},
                defaults={
                    'created_by': request.user,
                    'description': form.cleaned_data['link_description']
                }
            )
        
        return JsonResponse({'success': True, 'message': 'Wiki pages linked successfully!'})
    
    return JsonResponse({'error': form.errors}, status=400)


@login_required
def wiki_page_history(request, slug):
    """View wiki page version history"""
    org = request.user.profile.organization if hasattr(request.user, 'profile') else None
    if not org:
        return redirect('home')
    
    page = get_object_or_404(WikiPage, slug=slug, organization=org)
    versions = page.versions.all()
    
    return render(request, 'wiki/page_history.html', {
        'page': page,
        'versions': versions,
        'organization': org
    })


@login_required
def wiki_page_restore(request, slug, version_number):
    """Restore a previous version of a wiki page"""
    org = request.user.profile.organization if hasattr(request.user, 'profile') else None
    if not org:
        return redirect('home')
    
    page = get_object_or_404(WikiPage, slug=slug, organization=org)
    version = get_object_or_404(WikiPageVersion, page=page, version_number=version_number)
    
    # Create new version with restored content
    page.content = version.content
    page.title = version.title
    page.version += 1
    page.updated_by = request.user
    page.save()
    
    WikiPageVersion.objects.create(
        page=page,
        version_number=page.version,
        title=page.title,
        content=version.content,
        edited_by=request.user,
        change_summary=f'Restored from version {version_number}'
    )
    
    messages.success(request, f'Page restored to version {version_number}')
    return redirect('wiki:page_detail', slug=slug)


# Import User model
from django.contrib.auth.models import User
