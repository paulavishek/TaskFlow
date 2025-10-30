from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.contrib.auth.models import User

from kanban.models import Board, Task
from .models import ChatRoom, ChatMessage, TaskThreadComment, Notification
from .forms import ChatRoomForm, ChatMessageForm, TaskThreadCommentForm, MentionForm


@login_required
def chat_room_list(request, board_id):
    """List all chat rooms for a board"""
    board = get_object_or_404(Board, id=board_id)
    
    # Check if user is board member
    if request.user not in board.members.all():
        django_messages.error(request, 'You do not have access to this board.')
        return redirect('board_list')
    
    chat_rooms = board.chat_rooms.all()
    context = {
        'board': board,
        'chat_rooms': chat_rooms,
    }
    return render(request, 'messaging/chat_room_list.html', context)


@login_required
def chat_room_detail(request, room_id):
    """Display a specific chat room"""
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    
    # Check if user is member
    if request.user not in chat_room.members.all():
        django_messages.error(request, 'You do not have access to this room.')
        return redirect('board_list')
    
    # Get recent messages (last 50)
    messages = chat_room.messages.all().order_by('-created_at')[:50]
    messages = reversed(list(messages))
    
    form = ChatMessageForm()
    
    context = {
        'chat_room': chat_room,
        'messages': messages,
        'form': form,
    }
    return render(request, 'messaging/chat_room_detail.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def create_chat_room(request, board_id):
    """Create a new chat room for a board"""
    board = get_object_or_404(Board, id=board_id)
    
    # Check if user is board admin/creator
    if request.user != board.created_by and request.user not in board.members.all():
        django_messages.error(request, 'You do not have permission to create rooms.')
        return redirect('chat_room_list', board_id=board_id)
    
    if request.method == 'POST':
        form = ChatRoomForm(request.POST, board=board)
        if form.is_valid():
            chat_room = form.save(commit=False)
            chat_room.board = board
            chat_room.created_by = request.user
            chat_room.save()
            
            # Add members
            form.save_m2m()
            
            # Always add creator as member
            chat_room.members.add(request.user)
            
            django_messages.success(request, f'Chat room "{chat_room.name}" created successfully!')
            return redirect('chat_room_detail', room_id=chat_room.id)
    else:
        form = ChatRoomForm(board=board)
    
    context = {
        'form': form,
        'board': board,
    }
    return render(request, 'messaging/create_chat_room.html', context)


@login_required
@require_http_methods(["POST"])
def send_chat_message(request, room_id):
    """Send a message to a chat room (for non-WebSocket clients)"""
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    
    if request.user not in chat_room.members.all():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    form = ChatMessageForm(request.POST)
    if form.is_valid():
        message = form.save(commit=False)
        message.chat_room = chat_room
        message.author = request.user
        message.save()
        
        # Process mentions
        message.notify_mentioned_users()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'id': message.id,
                'username': message.author.username,
                'message': message.content,
                'timestamp': message.created_at.isoformat(),
            })
        else:
            return redirect('chat_room_detail', room_id=room_id)
    
    return JsonResponse({'error': 'Invalid message'}, status=400)


@login_required
@require_http_methods(["GET", "POST"])
def task_thread_comments(request, task_id):
    """View and manage real-time task thread comments"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user has access to this task
    board = task.column.board
    if request.user not in board.members.all():
        django_messages.error(request, 'You do not have access to this task.')
        return redirect('board_list')
    
    if request.method == 'POST':
        form = TaskThreadCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            
            # Process mentions
            comment.notify_mentioned_users()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'id': comment.id,
                    'username': comment.author.username,
                    'content': comment.content,
                    'timestamp': comment.created_at.isoformat(),
                }, status=201)
            else:
                django_messages.success(request, 'Comment added successfully!')
                return redirect('task_thread_comments', task_id=task_id)
    else:
        form = TaskThreadCommentForm()
    
    comments = task.thread_comments.all().order_by('-created_at')
    
    context = {
        'task': task,
        'comments': comments,
        'form': form,
    }
    return render(request, 'messaging/task_thread_comments.html', context)


@login_required
@require_http_methods(["GET"])
def get_mentions(request):
    """API endpoint for mention autocomplete"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 1:
        return JsonResponse({'results': []})
    
    # Find users matching the query
    users = User.objects.filter(
        Q(username__istartswith=query) | Q(first_name__istartswith=query)
    ).values('id', 'username', 'first_name')[:10]
    
    results = [
        {
            'id': user['id'],
            'text': user['username'],
            'display': f"{user['username']}" + (f" ({user['first_name']})" if user['first_name'] else "")
        }
        for user in users
    ]
    
    return JsonResponse({'results': results})


@login_required
def notifications(request):
    """View all notifications for the user"""
    user_notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    
    # Mark as read if requested
    if request.GET.get('mark_read'):
        user_notifications.update(is_read=True)
    
    context = {
        'notifications': user_notifications,
    }
    return render(request, 'messaging/notifications.html', context)


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notifications')


@login_required
@require_http_methods(["GET"])
def get_unread_notification_count(request):
    """API endpoint to get unread notification count"""
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({'count': count})


@login_required
@require_http_methods(["GET"])
def message_history(request, room_id):
    """Get message history for a chat room (pagination)"""
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    
    if request.user not in chat_room.members.all():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    offset = int(request.GET.get('offset', 0))
    limit = 20
    
    messages = chat_room.messages.all().order_by('-created_at')[offset:offset + limit]
    messages = reversed(list(messages))
    
    messages_data = [
        {
            'id': msg.id,
            'username': msg.author.username,
            'content': msg.content,
            'timestamp': msg.created_at.isoformat(),
            'mentioned_users': [u.username for u in msg.mentioned_users.all()]
        }
        for msg in messages
    ]
    
    return JsonResponse({'messages': messages_data})


@login_required
@require_http_methods(["GET"])
def task_comment_history(request, task_id):
    """Get comment history for a task (pagination)"""
    task = get_object_or_404(Task, id=task_id)
    board = task.column.board
    
    if request.user not in board.members.all():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    offset = int(request.GET.get('offset', 0))
    limit = 20
    
    comments = task.comments.all().order_by('-created_at')[offset:offset + limit]
    comments = reversed(list(comments))
    
    comments_data = [
        {
            'id': comment.id,
            'username': comment.author.username,
            'content': comment.content,
            'timestamp': comment.created_at.isoformat(),
            'mentioned_users': [u.username for u in comment.mentioned_users.all()]
        }
        for comment in comments
    ]
    
    return JsonResponse({'comments': comments_data})
