import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.contrib import messages
from django.db.models import Count, Q, Case, When, IntegerField, Max
from django.utils import timezone
from datetime import timedelta
import json
import csv
from django.contrib.auth.models import User
from django.core.management import call_command

# Configure logger
logger = logging.getLogger(__name__)

from .models import Board, Column, Task, TaskLabel, Comment, TaskActivity
from .forms import BoardForm, ColumnForm, TaskForm, TaskLabelForm, CommentForm, TaskMoveForm, TaskSearchForm
from accounts.models import UserProfile

@login_required
def dashboard(request):
    try:
        profile = request.user.profile
        organization = profile.organization
        
        # Check if user needs the getting started wizard (only for brand new users)
        if not profile.completed_wizard:
            # Check if this is a truly new user (no boards created, no tasks assigned)
            user_boards = Board.objects.filter(
                Q(organization=organization) & 
                (Q(created_by=request.user) | Q(members=request.user))
            ).distinct()
            
            user_tasks = Task.objects.filter(
                column__board__organization=organization,
                assigned_to=request.user
            )
            
            # Only show wizard for completely new users
            if user_boards.count() == 0 and user_tasks.count() == 0:
                return redirect('getting_started_wizard')
        
        boards = Board.objects.filter(
            Q(organization=organization) & 
            (Q(created_by=request.user) | Q(members=request.user))
        ).distinct()
        
        # Get analytics data
        task_count = Task.objects.filter(column__board__in=boards).count()
        completed_count = Task.objects.filter(
            column__board__in=boards, 
            column__name__icontains='done'
        ).count()
        
        # Get completion rate
        completion_rate = 0
        if task_count > 0:
            completion_rate = (completed_count / task_count) * 100
          # Get tasks due soon (next 3 days)
        due_soon = Task.objects.filter(
            column__board__in=boards,
            due_date__range=[timezone.now(), timezone.now() + timedelta(days=3)]
        ).count()
          # Get overdue tasks (due date in the past and not in done columns)
        overdue_count = Task.objects.filter(
            column__board__in=boards,
            due_date__lt=timezone.now()
        ).exclude(
            column__name__icontains='done'
        ).count()
        
        # Get detailed task data for modals
        all_tasks = Task.objects.filter(column__board__in=boards).select_related('column', 'assigned_to', 'column__board')
        completed_tasks = Task.objects.filter(
            column__board__in=boards, 
            column__name__icontains='done'
        ).select_related('column', 'assigned_to', 'column__board')
        overdue_tasks = Task.objects.filter(
            column__board__in=boards,
            due_date__lt=timezone.now()
        ).exclude(
            column__name__icontains='done'
        ).select_related('column', 'assigned_to', 'column__board')
        due_soon_tasks = Task.objects.filter(
            column__board__in=boards,
            due_date__range=[timezone.now(), timezone.now() + timedelta(days=3)]
        ).select_related('column', 'assigned_to', 'column__board')
        
        # Get sort preference from request (default to 'urgency')
        sort_by = request.GET.get('sort_tasks', 'urgency')
        
        # Base query for My Tasks
        my_tasks_query = Task.objects.filter(
            column__board__in=boards,
            assigned_to=request.user
        ).exclude(
            column__name__icontains='done'
        ).select_related('column', 'column__board', 'assigned_to')
        
        # Apply sorting based on user preference
        if sort_by == 'due_date':
            # Sort by: 1) Due date (soonest first), 2) Priority, 3) Creation date
            my_tasks = my_tasks_query.extra(
                select={
                    'priority_order': """
                        CASE priority 
                            WHEN 'urgent' THEN 1 
                            WHEN 'high' THEN 2 
                            WHEN 'medium' THEN 3 
                            WHEN 'low' THEN 4 
                            ELSE 5 
                        END
                    """,
                    'due_date_order': "CASE WHEN due_date IS NULL THEN 1 ELSE 0 END"
                }
            ).order_by('due_date_order', 'due_date', 'priority_order', 'created_at')[:8]
        elif sort_by == 'priority':
            # Sort by: 1) Priority level, 2) Due date, 3) Creation date
            my_tasks = my_tasks_query.extra(
                select={
                    'priority_order': """
                        CASE priority 
                            WHEN 'urgent' THEN 1 
                            WHEN 'high' THEN 2 
                            WHEN 'medium' THEN 3 
                            WHEN 'low' THEN 4 
                            ELSE 5 
                        END
                    """,
                    'due_date_order': "CASE WHEN due_date IS NULL THEN 1 ELSE 0 END"
                }
            ).order_by('priority_order', 'due_date_order', 'due_date', 'created_at')[:8]
        elif sort_by == 'recent':
            # Sort by: 1) Most recently created/updated, 2) Priority
            my_tasks = my_tasks_query.extra(
                select={
                    'priority_order': """
                        CASE priority 
                            WHEN 'urgent' THEN 1 
                            WHEN 'high' THEN 2 
                            WHEN 'medium' THEN 3 
                            WHEN 'low' THEN 4 
                            ELSE 5 
                        END
                    """
                }
            ).order_by('-updated_at', '-created_at', 'priority_order')[:8]
        else:  # Default: 'urgency'
            # Sort by: 1) Overdue tasks first, 2) Priority level, 3) Due date, 4) Creation date
            my_tasks = my_tasks_query.extra(
                select={
                    'is_overdue': "CASE WHEN due_date < datetime('now') THEN 1 ELSE 0 END",
                    'priority_order': """
                        CASE priority 
                            WHEN 'urgent' THEN 1 
                            WHEN 'high' THEN 2 
                            WHEN 'medium' THEN 3 
                            WHEN 'low' THEN 4 
                            ELSE 5 
                        END
                    """
                }
            ).order_by('-is_overdue', 'priority_order', 'due_date', 'created_at')[:8]
        
        # Count of my tasks (for stats)
        my_tasks_count = Task.objects.filter(
            column__board__in=boards,
            assigned_to=request.user
        ).exclude(
            column__name__icontains='done'
        ).count()        
        return render(request, 'kanban/dashboard.html', {
            'boards': boards,
            'task_count': task_count,
            'completed_count': completed_count,
            'completion_rate': round(completion_rate, 1),
            'due_soon': due_soon,
            'overdue_count': overdue_count,
            'all_tasks': all_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks,
            'due_soon_tasks': due_soon_tasks,
            'remaining_tasks': task_count - completed_count,
            'my_tasks': my_tasks,
            'my_tasks_count': my_tasks_count,
            'my_tasks_sort_by': sort_by,  # Current sort preference
            'now': timezone.now(),  # For comparing dates in the template
        })
    except UserProfile.DoesNotExist:
        return redirect('create_organization')

@login_required
def board_list(request):
    try:
        profile = request.user.profile
        organization = profile.organization
        boards = Board.objects.filter(
            Q(organization=organization) & 
            (Q(created_by=request.user) | Q(members=request.user))
        ).distinct()
        
        # For board_list, we only display boards, creation is handled by create_board view
        form = BoardForm()
        
        return render(request, 'kanban/board_list.html', {
            'boards': boards,
            'form': form
        })
    except UserProfile.DoesNotExist:
        return redirect('create_organization')

@login_required
def create_board(request):
    try:
        profile = request.user.profile
        organization = profile.organization
        
        if request.method == 'POST':
            form = BoardForm(request.POST)
            if form.is_valid():
                board = form.save(commit=False)
                board.organization = organization
                board.created_by = request.user
                board.save()
                board.members.add(request.user)
                  # Check if there are recommended columns to create
                recommended_columns_json = request.POST.get('recommended_columns')
                if recommended_columns_json:
                    try:
                        recommended_columns = json.loads(recommended_columns_json)
                        
                        # Create the recommended columns
                        for i, column_data in enumerate(recommended_columns):
                            Column.objects.create(
                                name=column_data['name'],
                                board=board,
                                position=i
                            )
                        
                        messages.success(request, f'Board "{board.name}" created successfully with {len(recommended_columns)} AI-recommended columns!')
                    except (json.JSONDecodeError, KeyError) as e:
                        # Fallback to default columns if there's an error with recommended columns
                        default_columns = ['To Do', 'In Progress', 'Done']
                        for i, name in enumerate(default_columns):
                            Column.objects.create(name=name, board=board, position=i)
                        messages.success(request, f'Board "{board.name}" created successfully with default columns!')
                else:
                    # No recommended columns, create default ones
                    default_columns = ['To Do', 'In Progress', 'Done']
                    for i, name in enumerate(default_columns):
                        Column.objects.create(name=name, board=board, position=i)
                    messages.success(request, f'Board "{board.name}" created successfully!')
                
                return redirect('board_detail', board_id=board.id)
        else:
            form = BoardForm()
        
        return render(request, 'kanban/create_board.html', {
            'form': form
        })
    except UserProfile.DoesNotExist:
        return redirect('create_organization')

@login_required
def board_detail(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    # Check if user has access to this board
    if not (board.created_by == request.user or request.user in board.members.all()):
        return HttpResponseForbidden("You don't have access to this board.")
    columns = Column.objects.filter(board=board)
    
    # Create default columns if none exist (only for boards created without AI recommendations)
    if not columns.exists():
        default_columns = ['To Do', 'In Progress', 'Done']
        for i, name in enumerate(default_columns):
            Column.objects.create(name=name, board=board, position=i)
        columns = Column.objects.filter(board=board)
    else:
        # Ensure "To Do" column exists - recreate if missing (for compatibility)
        has_todo = columns.filter(name__iregex=r'^(to do|todo)$').exists()
        if not has_todo:
            # Get the highest position and add "To Do" at the beginning
            max_position = columns.aggregate(max_pos=Max('position'))['max_pos'] or -1
            
            # Shift all existing columns one position to the right
            for column in columns.order_by('-position'):
                column.position += 1
                column.save()
                
            # Create "To Do" column at position 0
            Column.objects.create(name='To Do', board=board, position=0)
            columns = Column.objects.filter(board=board)  # Refresh queryset
    
    # Initialize the search form
    search_form = TaskSearchForm(request.GET or None, board=board)
    
    # Get all tasks for this board (with filtering if search is active)
    tasks = Task.objects.filter(column__board=board)
    
    # Apply search filters if the form is valid
    any_filter_active = False
    if search_form.is_valid() and any(search_form.cleaned_data.values()):
        any_filter_active = True
        # Filter by column
        if search_form.cleaned_data.get('column'):
            tasks = tasks.filter(column=search_form.cleaned_data['column'])
        
        # Filter by priority
        if search_form.cleaned_data.get('priority'):
            tasks = tasks.filter(priority=search_form.cleaned_data['priority'])
          # Filter by label
        if search_form.cleaned_data.get('label'):
            tasks = tasks.filter(labels=search_form.cleaned_data['label'])
        
        # Filter by label category (Lean Six Sigma)
        if search_form.cleaned_data.get('label_category'):
            category = search_form.cleaned_data['label_category']
            if category == 'lean':
                # All Lean Six Sigma labels
                tasks = tasks.filter(labels__category='lean')
            elif category == 'regular':
                # Only regular labels
                tasks = tasks.filter(labels__category='regular')
            elif category == 'lean_va':
                # Value-Added tasks
                tasks = tasks.filter(labels__name='Value-Added', labels__category='lean')
            elif category == 'lean_nva':
                # Necessary Non-Value-Added tasks
                tasks = tasks.filter(labels__name='Necessary NVA', labels__category='lean')
            elif category == 'lean_waste':
                # Waste/Eliminate tasks
                tasks = tasks.filter(labels__name='Waste/Eliminate', labels__category='lean')
        
        # Filter by assignee
        if search_form.cleaned_data.get('assignee'):
            tasks = tasks.filter(assigned_to=search_form.cleaned_data['assignee'])
        
        # Filter by search term (in title or description)
        if search_form.cleaned_data.get('search_term'):
            search_term = search_form.cleaned_data['search_term']
            tasks = tasks.filter(
                Q(title__icontains=search_term) | 
                Q(description__icontains=search_term)
            )
    
    # Get all labels for this board
    labels = TaskLabel.objects.filter(board=board)
    
    # Get all organization members for the member dropdown
    try:
        organization = request.user.profile.organization
        organization_members = UserProfile.objects.filter(organization=organization)
    except UserProfile.DoesNotExist:
        organization_members = []
    
    return render(request, 'kanban/board_detail.html', {
        'board': board,
        'columns': columns,
        'tasks': tasks,
        'labels': labels,
        'organization_members': organization_members,
        'now': timezone.now(),  # Used for due date comparison
        'search_form': search_form,  # Add the search form to the context
        'any_filter_active': any_filter_active,  # Add the flag for active filters
    })

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    board = task.column.board
    
    # Check if user has access to this board
    if not (board.created_by == request.user or request.user in board.members.all()):
        return HttpResponseForbidden("You don't have access to this task.")
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, board=board)
        if form.is_valid():
            task = form.save()
            # Record activity
            TaskActivity.objects.create(
                task=task,
                user=request.user,
                activity_type='updated',
                description=f"Updated task details for '{task.title}'"
            )
            messages.success(request, 'Task updated successfully!')
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskForm(instance=task, board=board)
    
    # Handle comments
    if request.method == 'POST' and 'content' in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            
            # Record activity
            TaskActivity.objects.create(
                task=task,
                user=request.user,
                activity_type='commented',
                description=f"Commented on '{task.title}'"
            )
            
            messages.success(request, 'Comment added successfully!')
            return redirect('task_detail', task_id=task.id)
    else:
        comment_form = CommentForm()
    
    # Get all comments for this task
    comments = Comment.objects.filter(task=task)
    
    # Get all activities for this task
    activities = TaskActivity.objects.filter(task=task)
    
    return render(request, 'kanban/task_detail.html', {
        'task': task,
        'board': board,
        'form': form,
        'comment_form': comment_form,
        'comments': comments,
        'activities': activities,
    })

@login_required
def create_task(request, board_id, column_id=None):
    board = get_object_or_404(Board, id=board_id)
    
    # Check if user has access to this board
    if not (board.created_by == request.user or request.user in board.members.all()):
        return HttpResponseForbidden("You don't have access to this board.")
    if column_id:
        column = get_object_or_404(Column, id=column_id, board=board)
    else:
        # Try to get "To Do" column first, otherwise get the first available column
        column = Column.objects.filter(
            board=board, 
            name__iregex=r'^(to do|todo)$'
        ).first()
        
        if not column:
            # If no "To Do" column exists, get the first column
            column = Column.objects.filter(board=board).order_by('position').first()
        
        # If still no column exists, this is an error state
        if not column:
            messages.error(request, 'No columns exist on this board. Please create a column first.')
            return redirect('board_detail', board_id=board.id)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, board=board)
        if form.is_valid():
            task = form.save(commit=False)
            task.column = column
            task.created_by = request.user
            # Set position to be at the end of the column
            last_position = Task.objects.filter(column=column).order_by('-position').first()
            task.position = (last_position.position + 1) if last_position else 0
            task.save()
            # Save many-to-many relationships
            form.save_m2m()
            
            # Record activity
            TaskActivity.objects.create(
                task=task,
                user=request.user,
                activity_type='created',
                description=f"Created task '{task.title}'"
            )
            
            messages.success(request, 'Task created successfully!')
            return redirect('board_detail', board_id=board.id)
    else:
        form = TaskForm(board=board)
    
    return render(request, 'kanban/create_task.html', {
        'form': form,
        'board': board,
        'column': column
    })

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    board = task.column.board
    
    # Check if user has access to this board
    if not (board.created_by == request.user or request.user in board.members.all()):
        return HttpResponseForbidden("You don't have access to this task.")
    
    if request.method == 'POST':
        board_id = task.column.board.id
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('board_detail', board_id=board_id)
    
    return render(request, 'kanban/delete_task.html', {'task': task})

@login_required
def create_column(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    # Check if user has access to this board
    if not (board.created_by == request.user or request.user in board.members.all()):
        return HttpResponseForbidden("You don't have access to this board.")
    
    if request.method == 'POST':
        form = ColumnForm(request.POST)
        if form.is_valid():
            column = form.save(commit=False)
            column.board = board
            # Set position to be at the end
            last_position = Column.objects.filter(board=board).order_by('-position').first()
            column.position = (last_position.position + 1) if last_position else 0
            column.save()
            messages.success(request, 'Column created successfully!')
            return redirect('board_detail', board_id=board.id)
    else:
        form = ColumnForm()
    
    return render(request, 'kanban/create_column.html', {
        'form': form,
        'board': board
    })

@login_required
def create_label(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    # Check if user has access to this board
    if not (board.created_by == request.user or request.user in board.members.all()):
        return HttpResponseForbidden("You don't have access to this board.")
    
    if request.method == 'POST':
        form = TaskLabelForm(request.POST)
        if form.is_valid():
            label = form.save(commit=False)
            label.board = board
            label.save()
            messages.success(request, 'Label created successfully!')
            return redirect('board_detail', board_id=board.id)
    else:
        form = TaskLabelForm()    
        return render(request, 'kanban/create_label.html', {
        'form': form,
        'board': board,
        'has_lean_labels': board.labels.filter(category='lean').exists(),
        'has_regular_labels': board.labels.filter(category='regular').exists()
    })

@login_required
def delete_label(request, label_id):
    label = get_object_or_404(TaskLabel, id=label_id)
    board = label.board
    
    # Check if user has access to this board
    if not (board.created_by == request.user or request.user in board.members.all()):
        return HttpResponseForbidden("You don't have access to this board.")
    
    # Delete the label
    label_name = label.name
    label.delete()
    messages.success(request, f'Label "{label_name}" has been deleted.')
    
    return redirect('create_label', board_id=board.id)

@login_required
def board_analytics(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    # Check if user has access to this board
    if not (board.created_by == request.user or request.user in board.members.all()):
        return HttpResponseForbidden("You don't have access to this board.")
    
    # Get columns for this board
    columns = Column.objects.filter(board=board)
    
    # Get tasks by column
    tasks_by_column = []
    for column in columns:
        count = Task.objects.filter(column=column).count()
        tasks_by_column.append({
            'name': column.name,
            'count': count
        })
    
    # Get tasks by priority - convert QuerySet to list of dictionaries
    priority_queryset = Task.objects.filter(column__board=board).values('priority').annotate(
        count=Count('id')
    ).order_by('priority')
    
    tasks_by_priority = []
    for item in priority_queryset:
        # Convert priority codes to readable names
        priority_name = dict(Task.PRIORITY_CHOICES).get(item['priority'], item['priority'])
        tasks_by_priority.append({
            'priority': priority_name,
            'count': item['count']
        })
    
    # Get tasks by assigned user - convert QuerySet to list of dictionaries
    user_queryset = Task.objects.filter(column__board=board).values(
        'assigned_to__username'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    tasks_by_user = []
    for item in user_queryset:
        username = item['assigned_to__username'] or 'Unassigned'
        # Count completed tasks for this user
        completed_user_tasks = Task.objects.filter(
            column__board=board,
            assigned_to__username=item['assigned_to__username'],
            column__name__icontains='done'
        ).count()
        
        # Calculate completion percentage
        user_completion_rate = 0
        if item['count'] > 0:
            user_completion_rate = (completed_user_tasks / item['count']) * 100
            
        tasks_by_user.append({
            'username': username,
            'count': item['count'],
            'completed': completed_user_tasks,
            'completion_rate': int(user_completion_rate)
        })
    
    # Get completion rate over time (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    completed_tasks_queryset = TaskActivity.objects.filter(
        task__column__board=board,
        activity_type='moved',
        description__contains='Done',
        created_at__gte=thirty_days_ago
    ).values('created_at__date').annotate(
        count=Count('id')
    ).order_by('created_at__date')
    
    completed_tasks = []
    for item in completed_tasks_queryset:
        completed_tasks.append({
            'date': item['created_at__date'].strftime('%Y-%m-%d'),
            'count': item['count']
        })
    
    # Calculate productivity based on task progress
    total_tasks = Task.objects.filter(column__board=board).count()
    
    # Get all tasks and their progress values
    all_tasks = Task.objects.filter(column__board=board)
    
    # Sum of completed tasks (100% progress or in Done column)
    done_column_tasks = Task.objects.filter(
        column__board=board, 
        column__name__icontains='done'
    )
    completed_count = done_column_tasks.count() # Count completed tasks for this board
    
    # Set tasks in Done column to 100% progress for calculation
    total_progress_percentage = 0
    for task in all_tasks:
        # If task is in Done column, count as 100%
        if task.column.name.lower().find('done') >= 0:
            progress = 100
        else:
            # Handle None progress values by defaulting to 0
            progress = task.progress if task.progress is not None else 0
        
        total_progress_percentage += progress
    
    # Calculate overall productivity based on progress of all tasks
    productivity = 0
    if total_tasks > 0:
        productivity = (total_progress_percentage / (total_tasks * 100)) * 100      # Get tasks due soon (next 7 days)
    today = timezone.now().date()
    upcoming_tasks = Task.objects.filter(
        column__board=board,
        due_date__isnull=False,
        due_date__date__gte=today,
        due_date__date__lte=today + timedelta(days=7)
    ).order_by('due_date')
    
    # Get overdue tasks (due date in the past and not in done columns)
    overdue_tasks = Task.objects.filter(
        column__board=board,
        due_date__isnull=False,
        due_date__date__lt=today
    ).exclude(
        column__name__icontains='done'
    ).order_by('due_date')
    
    # Get count of overdue tasks
    overdue_count = overdue_tasks.count()
    
    # Lean Six Sigma Metrics
    # Get tasks by value added category
    value_added_count = Task.objects.filter(
        column__board=board, 
        labels__name='Value-Added', 
        labels__category='lean'
    ).count()
    
    necessary_nva_count = Task.objects.filter(
        column__board=board, 
        labels__name='Necessary NVA', 
        labels__category='lean'
    ).count()
    
    waste_count = Task.objects.filter(
        column__board=board, 
        labels__name='Waste/Eliminate', 
        labels__category='lean'
    ).count()
    
    # Calculate value-added percentage
    total_categorized = value_added_count + necessary_nva_count + waste_count
    value_added_percentage = 0
    if total_categorized > 0:
        value_added_percentage = (value_added_count / total_categorized) * 100
      # Tasks by Lean Six Sigma category
    tasks_by_lean_category = [
        {'name': 'Value-Added', 'count': value_added_count, 'color': '#28a745'},
        {'name': 'Necessary NVA', 'count': necessary_nva_count, 'color': '#ffc107'},
        {'name': 'Waste/Eliminate', 'count': waste_count, 'color': '#dc3545'}
    ]
    return render(request, 'kanban/board_analytics.html', {
        'board': board,
        'columns': columns,
        'tasks': all_tasks,  # Add all tasks to the template context
        'tasks_by_column': tasks_by_column,  # Raw data for JSON encoding in template
        'tasks_by_priority': tasks_by_priority,  # Raw data for JSON encoding in template
        'tasks_by_user': tasks_by_user,  # Raw data for JSON encoding in template
        'completed_tasks': completed_tasks,  # Raw data for JSON encoding in template
        'tasks_by_lean_category': tasks_by_lean_category, # Raw data for JSON encoding in template
        'productivity': round(productivity, 1),
        'upcoming_tasks': upcoming_tasks,
        'overdue_tasks': overdue_tasks,  # Add overdue tasks
        'overdue_count': overdue_count,  # Add overdue count
        'total_tasks': total_tasks,
        'completed_count': completed_count,
        'now': timezone.now(),  # For comparing dates in the template
        # Lean Six Sigma metrics
        'value_added_percentage': round(value_added_percentage, 1),
        'total_categorized': total_categorized,
    })

@login_required
def move_task(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        task_id = data.get('taskId')
        column_id = data.get('columnId')
        position = data.get('position', 0)
        
        task = get_object_or_404(Task, id=task_id)
        new_column = get_object_or_404(Column, id=column_id)
        
        # Check if user has access to this board
        board = new_column.board
        if not (board.created_by == request.user or request.user in board.members.all()):
            return JsonResponse({'error': "You don't have access to this board."}, status=403)
        
        old_column = task.column
        task.column = new_column
        task.position = position
        
        # Auto-update progress to 100% when moved to a "Done" column
        if new_column.name.lower().find('done') >= 0:
            task.progress = 100
        
        task.save()
        
        # Record activity
        TaskActivity.objects.create(
            task=task,
            user=request.user,
            activity_type='moved',
            description=f"Moved task '{task.title}' from '{old_column.name}' to '{new_column.name}'"
        )
        
        # If progress was set to 100% automatically, record that too
        if new_column.name.lower().find('done') >= 0 and task.progress == 100:
            TaskActivity.objects.create(
                task=task,
                user=request.user,
                activity_type='updated',
                description=f"Automatically updated progress for '{task.title}' to 100% (Done)"
            )
        
        # Reorder tasks in the column
        tasks_to_reorder = Task.objects.filter(column=new_column).exclude(id=task_id)
        for i, t in enumerate(tasks_to_reorder):
            new_position = i
            if i >= position:
                new_position = i + 1
            t.position = new_position
            t.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def add_board_member(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    # Check if user is the board creator, superuser, or has access to the board
    if not (board.created_by == request.user or 
            request.user.is_superuser or 
            request.user in board.members.all()):
        return HttpResponseForbidden("You don't have permission to add members to this board.")
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                # Check if user is in the same organization
                if user.profile.organization == request.user.profile.organization:
                    # Add user to board members if not already a member
                    if user not in board.members.all():
                        board.members.add(user)
                        messages.success(request, f'{user.username} added to the board successfully!')
                    else:
                        messages.info(request, f'{user.username} is already a member of this board.')
                else:
                    messages.error(request, 'You can only add members from your organization.')
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User does not have a profile.')
        else:
            messages.error(request, 'No user selected.')
    
    return redirect('board_detail', board_id=board.id)

@login_required
def delete_board(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    # Check if user has permission to delete this board
    # Allow deletion if user is:
    # 1. Board creator
    # 2. Organization admin (if they have access to the board)
    # 3. Organization creator
    user_profile = getattr(request.user, 'profile', None)
    has_permission = (
        board.created_by == request.user or  # Board creator
        (user_profile and user_profile.is_admin and 
         (request.user in board.members.all() or board.created_by == request.user)) or  # Organization admin with board access
        (user_profile and request.user == board.organization.created_by)  # Organization creator
    )
    
    if not has_permission:
        return HttpResponseForbidden("You don't have permission to delete this board.")
    
    # Delete the board
    if request.method == 'POST':
        board_name = board.name
        board.delete()
        messages.success(request, f'Board "{board_name}" has been deleted.')
        return redirect('board_list')
    
    return redirect('board_detail', board_id=board_id)

@login_required
def organization_boards(request):
    try:
        profile = request.user.profile
        organization = profile.organization
        
        # Get all boards for this organization, even if user is not a member
        all_org_boards = Board.objects.filter(organization=organization)
        
        # Determine which boards the user is a member of
        user_boards = Board.objects.filter(
            Q(organization=organization) & 
            (Q(created_by=request.user) | Q(members=request.user))
        ).distinct()
        
        # Create a list to track which boards the user is a member of
        user_board_ids = user_boards.values_list('id', flat=True)
        
        return render(request, 'kanban/organization_boards.html', {
            'all_org_boards': all_org_boards,
            'user_board_ids': user_board_ids,
            'organization': organization
        })
    except UserProfile.DoesNotExist:
        return redirect('organization_choice')

@login_required
def join_board(request, board_id):
    """Allow users to join boards in their organization that they aren't already members of"""
    board = get_object_or_404(Board, id=board_id)
    
    # Check if user is in the same organization as the board
    try:
        user_profile = request.user.profile
        if user_profile.organization != board.organization:
            messages.error(request, "You cannot join boards outside your organization.")
            return redirect('organization_boards')
    except UserProfile.DoesNotExist:
        messages.error(request, "You need to set up a profile first.")
        return redirect('organization_choice')
    
    # Check if user is already a member
    if request.user in board.members.all() or board.created_by == request.user:
        messages.info(request, f"You are already a member of the board '{board.name}'.")
    else:
        # Add user to board members
        board.members.add(request.user)
        messages.success(request, f"You've successfully joined the board '{board.name}'!")
    
    return redirect('board_detail', board_id=board.id)

@login_required
def move_column(request, column_id, direction):
    """
    Move a column left or right in the board sequence based on its position
    """
    column = get_object_or_404(Column, id=column_id)
    board = column.board
    
    # Check if user has access to this board
    if not (board.created_by == request.user or request.user in board.members.all()):
        return HttpResponseForbidden("You don't have access to this board.")
    
    # Get all columns in order of position
    columns = list(Column.objects.filter(board=board).order_by('position'))
    current_index = next((i for i, col in enumerate(columns) if col.id == column.id), -1)
    
    if current_index == -1:
        messages.error(request, "Could not find the column position.")
        return redirect('board_detail', board_id=board.id)
    
    # Determine target position based on direction
    if direction == 'left' and current_index > 0:
        # Move column to the left
        target_index = current_index - 1
    elif direction == 'right' and current_index < len(columns) - 1:
        # Move column to the right
        target_index = current_index + 1
    else:
        # Can't move further in that direction
        messages.info(request, f"Cannot move column {direction}.")
        return redirect('board_detail', board_id=board.id)
    
    # Instead of just swapping positions, we'll reorder all columns properly
    if target_index != current_index:
        # Remove column from current position
        moved_column = columns.pop(current_index)
        # Insert column at new position
        columns.insert(target_index, moved_column)
        
        # Update all column positions
        for i, col in enumerate(columns):
            if col.position != i:
                col.position = i
                col.save()
        
        messages.success(request, f"Column '{column.name}' moved {direction}.")
    
    return redirect('board_detail', board_id=board.id)

@login_required
def reorder_columns(request):
    """Handle AJAX request to reorder columns via drag and drop"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        column_id = data.get('columnId')
        new_position = data.get('position', 0)
        board_id = data.get('boardId')
        
        column = get_object_or_404(Column, id=column_id)
        board = get_object_or_404(Board, id=board_id)
        
        # Check if user has access to this board
        if not (board.created_by == request.user or request.user in board.members.all()):
            return JsonResponse({'error': "You don't have access to this board."}, status=403)
        
        # Get all columns in order
        columns = list(Column.objects.filter(board=board).order_by('position'))
        
        # Find the column in the list
        current_index = next((i for i, col in enumerate(columns) if col.id == column.id), -1)
        
        if current_index == -1:
            return JsonResponse({'error': 'Column not found'}, status=400)
        
        # Remove column from current position and insert at new position
        moved_column = columns.pop(current_index)
        columns.insert(new_position, moved_column)
        
        # Update all column positions
        for i, col in enumerate(columns):
            if col.position != i:
                col.position = i
                col.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def reorder_multiple_columns(request):
    """Handle AJAX request to reorder multiple columns at once via the index-based approach"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            columns_data = data.get('columns', [])
            board_id = data.get('boardId')
            
            board = get_object_or_404(Board, id=board_id)
            
            # Check if user has access to this board
            if not (board.created_by == request.user or request.user in board.members.all()):
                return JsonResponse({'error': "You don't have access to this board."}, status=403)
            
            # Create a dictionary to map column_id to position
            position_map = {item['columnId']: item['position'] for item in columns_data}
            
            # Get all columns for this board
            db_columns = Column.objects.filter(board=board)
            
            # Update positions in bulk
            for column in db_columns:
                if str(column.id) in position_map:
                    column.position = position_map[str(column.id)]
            
            # Ensure positions are sequential (0, 1, 2, ...) by sorting and reassigning
            sorted_columns = sorted(db_columns, key=lambda col: col.position)
            for index, column in enumerate(sorted_columns):
                column.position = index
                column.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Columns rearranged successfully'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def delete_column(request, column_id):
    """Delete a column and all of its tasks"""
    column = get_object_or_404(Column, id=column_id)
    board = column.board
    
    # Check if user has access to this board
    if not (board.created_by == request.user or request.user in board.members.all()):
        return HttpResponseForbidden("You don't have access to this board.")
    
    # Prevent deletion of "To Do" column as it's required for task creation
    if column.name.lower() in ['to do', 'todo']:
        messages.error(request, 'Cannot delete the "To Do" column as it is required for creating new tasks.')
        return redirect('board_detail', board_id=board.id)
    
    if request.method == 'POST':
        # Store column name for success message
        column_name = column.name
        
        # Delete the column (will cascade delete all tasks in this column)
        column.delete()
        
        # Reorder remaining columns to ensure sequential positions
        remaining_columns = Column.objects.filter(board=board).order_by('position')
        for index, col in enumerate(remaining_columns):
            if col.position != index:
                col.position = index
                col.save()
                
        messages.success(request, f'Column "{column_name}" and its tasks have been deleted.')
        return redirect('board_detail', board_id=board.id)
    
    return render(request, 'kanban/delete_column.html', {
        'column': column,
        'board': board
    })

@login_required
def update_task_progress(request, task_id):
    """
    Update the progress percentage of a task through an AJAX request.
    Expects 'direction' parameter: 'increase' or 'decrease'.
    Increases or decreases by 10% increments.
    """
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            task = get_object_or_404(Task, id=task_id)
            board = task.column.board
            
            # Check if user has access to this board
            if not (board.created_by == request.user or request.user in board.members.all()):
                return JsonResponse({'error': "You don't have access to this task."}, status=403)
            
            data = json.loads(request.body)
            direction = data.get('direction')
            
            # Update progress based on direction
            if direction == 'increase':
                # Ensure we don't go above 100%
                task.progress = min(100, task.progress + 10)
            elif direction == 'decrease':
                # Ensure we don't go below 0%
                task.progress = max(0, task.progress - 10)
            else:
                return JsonResponse({'error': 'Invalid direction parameter'}, status=400)
            
            # Save the updated task
            task.save()
            
            # Record activity
            TaskActivity.objects.create(
                task=task,
                user=request.user,
                activity_type='updated',
                description=f"Updated progress for '{task.title}' to {task.progress}%"
            )
            
            # Return the updated progress
            return JsonResponse({
                'success': True,
                'progress': task.progress,
                'colorClass': get_progress_color_class(task.progress)
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def get_progress_color_class(progress):
    """Helper function to determine the progress bar color class based on percentage"""
    if progress < 30:
        return 'bg-danger'
    elif progress < 70:
        return 'bg-warning'
    else:
        return 'bg-success'

@login_required
def export_board(request, board_id):
    """Export a board's data to JSON or CSV format"""
    board = get_object_or_404(Board, id=board_id)
    
    # Check if user has access to this board
    if not (board.created_by == request.user or request.user in board.members.all()):
        return HttpResponseForbidden("You don't have access to this board.")
    
    export_format = request.GET.get('format', 'json')
    
    # Get all columns for this board
    columns = Column.objects.filter(board=board).order_by('position')
    
    # Build the board data structure
    board_data = {
        'board': {
            'name': board.name,
            'description': board.description,
            'created_at': board.created_at.isoformat(),
        },
        'columns': []
    }
    
    # Add columns and tasks
    for column in columns:
        column_data = {
            'name': column.name,
            'position': column.position,
            'tasks': []
        }
        
        tasks = Task.objects.filter(column=column).order_by('position')
        
        for task in tasks:
            # Get task labels
            labels = list(task.labels.values_list('name', flat=True))
            
            task_data = {
                'title': task.title,
                'description': task.description,
                'position': task.position,
                'created_at': task.created_at.isoformat(),
                'updated_at': task.updated_at.isoformat(),
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'assigned_to': task.assigned_to.username if task.assigned_to else None,
                'created_by': task.created_by.username,
                'labels': labels,
                'priority': task.priority,
                'progress': task.progress,
            }
            column_data['tasks'].append(task_data)
        
        board_data['columns'].append(column_data)
    
    if export_format == 'json':
        response = HttpResponse(json.dumps(board_data, indent=2), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{board.name}_export.json"'
        return response
    elif export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{board.name}_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Column', 'Task Title', 'Description', 'Position', 'Created At', 'Updated At', 
                         'Due Date', 'Assigned To', 'Created By', 'Labels', 'Priority', 'Progress'])
        
        for column in columns:
            tasks = Task.objects.filter(column=column).order_by('position')
            for task in tasks:
                labels = ", ".join(list(task.labels.values_list('name', flat=True)))
                writer.writerow([
                    column.name,
                    task.title,
                    task.description,
                    task.position,
                    task.created_at,
                    task.updated_at,
                    task.due_date if task.due_date else '',
                    task.assigned_to.username if task.assigned_to else '',
                    task.created_by.username,
                    labels,
                    task.priority,
                    task.progress
                ])
        
        return response
    else:
        messages.error(request, "Unsupported export format specified")
        return redirect('board_detail', board_id=board.id)

@login_required
def import_board(request):
    """Import a board from a JSON file"""
    if request.method != 'POST':
        return redirect('board_list')
    
    # Check if user has a profile and organization
    try:
        profile = request.user.profile
        organization = profile.organization
    except UserProfile.DoesNotExist:
        messages.error(request, "You must be part of an organization to import a board.")
        return redirect('create_organization')
    
    # Check if file was uploaded
    if 'import_file' not in request.FILES:
        messages.error(request, "No file was uploaded")
        return redirect('board_list')
        
    import_file = request.FILES['import_file']
    
    # Check file extension
    if not import_file.name.endswith('.json'):
        messages.error(request, "Only JSON files are supported for import")
        return redirect('board_list')
    
    # Try to parse the JSON file
    try:
        imported_data = json.load(import_file)
        
        # Basic validation of imported data structure
        if 'board' not in imported_data or 'columns' not in imported_data:
            messages.error(request, "Invalid board data format")
            return redirect('board_list')
            
        # Create the new board
        board_data = imported_data['board']
        new_board = Board.objects.create(
            name=board_data.get('name', 'Imported Board'),
            description=board_data.get('description', ''),
            organization=organization,
            created_by=request.user
        )
        new_board.members.add(request.user)
        
        # Create columns
        for col_index, column_data in enumerate(imported_data['columns']):
            column = Column.objects.create(
                name=column_data.get('name', f'Column {col_index+1}'),
                board=new_board,
                position=column_data.get('position', col_index)
            )
            
            # Create tasks for this column
            for task_index, task_data in enumerate(column_data.get('tasks', [])):
                # Create the task
                new_task = Task.objects.create(
                    title=task_data.get('title', f'Task {task_index+1}'),
                    description=task_data.get('description', ''),
                    column=column,
                    position=task_data.get('position', task_index),
                    created_by=request.user,
                    priority=task_data.get('priority', 'medium'),
                    progress=task_data.get('progress', 0)
                )
                
                # Handle assigned_to if provided
                assigned_username = task_data.get('assigned_to')
                if assigned_username:
                    try:
                        assigned_user = User.objects.get(username=assigned_username)
                        # Only set if user is in the same organization
                        if hasattr(assigned_user, 'profile') and assigned_user.profile.organization == organization:
                            new_task.assigned_to = assigned_user
                            new_task.save()
                    except User.DoesNotExist:
                        pass  # Skip if user doesn't exist
                
                # Handle labels if provided
                label_names = task_data.get('labels', [])
                for label_name in label_names:
                    # Try to find an existing label with this name, or create a new one
                    label, created = TaskLabel.objects.get_or_create(
                        name=label_name,
                        board=new_board,
                        defaults={'color': '#FF5733'}  # Default color for new labels
                    )
                    new_task.labels.add(label)
        
        messages.success(request, f"Board '{new_board.name}' imported successfully!")
        return redirect('board_detail', board_id=new_board.id)
        
    except json.JSONDecodeError:
        messages.error(request, "Invalid JSON file")
        return redirect('board_list')
    except Exception as e:
        messages.error(request, f"Error importing board: {str(e)}")
        return redirect('board_list')

@login_required
def add_lean_labels(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    # Check if user has access to this board
    if not (board.created_by == request.user or request.user in board.members.all()):
        return HttpResponseForbidden("You don't have access to this board.")
    
    if request.method == 'POST':
        # Call the management command to add the labels
        call_command('add_lean_labels', board_id=board_id)
        messages.success(request, 'Lean Six Sigma labels added successfully!')
    
    return redirect('create_label', board_id=board.id)

def welcome(request):
    """
    Welcome page view that will be shown to users who are not logged in.
    Logged in users will be redirected to the dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Add cache busting timestamp
    import time
    cache_buster = str(int(time.time()))
    
    return render(request, 'kanban/welcome.html', {
        'cache_buster': cache_buster
    })

@login_required
def test_ai_features(request):
    """Test page for AI features debugging"""
    return render(request, 'kanban/test_ai_features.html')

@login_required
def edit_board(request, board_id):
    board = get_object_or_404(Board, id=board_id)
      # Check if user is the board creator or a member
    if not (board.created_by == request.user or request.user in board.members.all()):
        return HttpResponseForbidden("You don't have permission to edit this board.")
    
    if request.method == 'POST':
        form = BoardForm(request.POST, instance=board)
        if form.is_valid():
            form.save()
            messages.success(request, f'Board "{board.name}" updated successfully!')
            return redirect('board_detail', board_id=board.id)
    else:
        form = BoardForm(instance=board)
    
    return render(request, 'kanban/edit_board.html', {
        'form': form,
        'board': board
    })

@login_required
def meeting_transcript_extraction(request, board_id):
    """
    View for extracting tasks from meeting transcripts using AI
    """
    try:
        # Verify board access
        board = get_object_or_404(Board, id=board_id)
        if not (board.created_by == request.user or request.user in board.members.all()):
            return HttpResponseForbidden("You don't have access to this board.")
        
        # Get previous meeting transcripts for this board (if model exists)
        try:
            from kanban.models import MeetingTranscript
            previous_extractions = MeetingTranscript.objects.filter(
                board=board,
                created_by=request.user
            ).order_by('-created_at')[:10]
        except:
            previous_extractions = []
        
        context = {
            'board': board,
            'today': timezone.now().date(),
            'previous_extractions': previous_extractions,
            'board_members': board.members.all(),
        }
        
        return render(request, 'kanban/meeting_transcript.html', context)
        
    except Exception as e:
        logger.error(f"Error in meeting transcript extraction view: {str(e)}")
        messages.error(request, 'Error loading meeting transcript page. Please try again.')
        return redirect('board_detail', board_id=board_id)

# Getting Started Wizard Views
@login_required
def getting_started_wizard(request):
    """
    Getting Started Wizard for new users
    """
    try:
        profile = request.user.profile
        organization = profile.organization
        
        # Get user's basic info for personalization
        context = {
            'user': request.user,
            'organization': organization,
            'profile': profile,
            'is_repeat_visitor': profile.completed_wizard,  # Show different messaging for repeat visitors
        }
        
        return render(request, 'kanban/getting_started_wizard.html', context)
        
    except UserProfile.DoesNotExist:
        return redirect('organization_choice')

@login_required
def complete_wizard(request):
    """
    Mark the wizard as completed for the user
    """
    if request.method == 'POST':
        try:
            profile = request.user.profile
            profile.completed_wizard = True
            profile.wizard_completed_at = timezone.now()
            profile.save()
            
            messages.success(request, 'Welcome to TaskFlow! You\'re all set to start managing your projects.')
            return redirect('dashboard')
            
        except UserProfile.DoesNotExist:
            return redirect('organization_choice')
    
    return redirect('getting_started_wizard')

@login_required
def wizard_create_board(request):
    """
    Create a board during the getting started wizard
    """
    if request.method == 'POST':
        try:
            profile = request.user.profile
            organization = profile.organization
            
            # Get board data from the request
            board_name = request.POST.get('board_name', '').strip()
            board_description = request.POST.get('board_description', '').strip()
            use_ai_columns = request.POST.get('use_ai_columns') == 'true'
            
            if not board_name:
                return JsonResponse({'error': 'Board name is required'}, status=400)
            
            # Create the board
            board = Board.objects.create(
                name=board_name,
                description=board_description,
                organization=organization,
                created_by=request.user
            )
            board.members.add(request.user)
            
            # If AI columns are requested, get AI recommendations
            if use_ai_columns:
                from .utils.ai_utils import recommend_board_columns
                
                board_data = {
                    'name': board_name,
                    'description': board_description,
                    'team_size': 1,
                    'project_type': 'general',
                    'organization_type': 'general',
                    'existing_columns': []
                }
                
                recommendation = recommend_board_columns(board_data)
                
                if recommendation and recommendation.get('recommended_columns'):
                    # Create AI-recommended columns
                    for i, column_data in enumerate(recommendation['recommended_columns']):
                        Column.objects.create(
                            name=column_data['name'],
                            board=board,
                            position=i
                        )
                else:
                    # Fallback to default columns
                    default_columns = ['To Do', 'In Progress', 'Done']
                    for i, name in enumerate(default_columns):
                        Column.objects.create(name=name, board=board, position=i)
            else:
                # Create default columns
                default_columns = ['To Do', 'In Progress', 'Done']
                for i, name in enumerate(default_columns):
                    Column.objects.create(name=name, board=board, position=i)
            
            return JsonResponse({
                'success': True,
                'board_id': board.id,
                'board_name': board.name,
                'message': 'Board created successfully!'
            })
            
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User profile not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def wizard_create_task(request):
    """
    Create a task during the getting started wizard
    """
    if request.method == 'POST':
        try:
            profile = request.user.profile
            
            # Get task data from the request
            board_id = request.POST.get('board_id')
            task_title = request.POST.get('task_title', '').strip()
            task_description = request.POST.get('task_description', '').strip()
            use_ai_description = request.POST.get('use_ai_description') == 'true'
            
            if not board_id or not task_title:
                return JsonResponse({'error': 'Board ID and task title are required'}, status=400)
            
            # Get the board and verify access
            board = get_object_or_404(Board, id=board_id)
            if not (board.created_by == request.user or request.user in board.members.all()):
                return JsonResponse({'error': 'Access denied'}, status=403)
            
            # Get the first column (To Do column)
            first_column = board.columns.first()
            if not first_column:
                return JsonResponse({'error': 'No columns found in board'}, status=404)
            
            # If AI description is requested, enhance the description
            if use_ai_description and not task_description:
                from .utils.ai_utils import enhance_task_description
                
                task_data = {
                    'title': task_title,
                    'description': task_description,
                    'board_context': board.name,
                    'column_context': first_column.name
                }
                
                enhanced = enhance_task_description(task_data)
                if enhanced and enhanced.get('enhanced_description'):
                    task_description = enhanced['enhanced_description']
            
            # Create the task
            task = Task.objects.create(
                title=task_title,
                description=task_description,
                column=first_column,
                created_by=request.user,
                assigned_to=request.user,
                priority='medium'
            )
            
            return JsonResponse({
                'success': True,
                'task_id': task.id,
                'task_title': task.title,
                'task_description': task.description,
                'board_id': board.id,
                'message': 'Task created successfully!'
            })
            
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User profile not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def reset_wizard(request):
    """
    Reset the wizard for a user (admin feature or for testing)
    """
    if request.method == 'POST':
        try:
            profile = request.user.profile
            profile.completed_wizard = False
            profile.wizard_completed_at = None
            profile.save()
            
            messages.success(request, 'Getting Started Wizard has been reset. You will see it on your next dashboard visit.')
            return redirect('dashboard')
            
        except UserProfile.DoesNotExist:
            return redirect('organization_choice')
    
    return redirect('dashboard')
