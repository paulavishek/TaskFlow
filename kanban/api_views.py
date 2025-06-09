"""
API Views for AI-powered features in TaskFlow

This module contains API view functions that handle requests from 
the front-end for AI-powered features.
"""
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from kanban.models import Task, Comment
from kanban.utils.ai_utils import (
    generate_task_description, 
    summarize_comments,
    generate_analytics_insights,
    suggest_lean_classification
)

@login_required
@require_http_methods(["POST"])
def generate_task_description_api(request):
    """
    API endpoint to generate a task description using AI
    """
    try:
        data = json.loads(request.body)
        title = data.get('title', '')
        
        if not title:
            return JsonResponse({'error': 'Title is required'}, status=400)
            
        # Call AI util function to generate description
        description = generate_task_description(title)
        
        if not description:
            return JsonResponse({'error': 'Failed to generate description'}, status=500)
            
        return JsonResponse({'description': description})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def summarize_comments_api(request, task_id):
    """
    API endpoint to summarize task comments using AI
    """
    try:
        # Get the task and verify user access
        task = get_object_or_404(Task, id=task_id)
        board = task.column.board
        
        # Check if user has access to this board/task
        if not (board.created_by == request.user or request.user in board.members.all()):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Format comments for AI
        comments_data = []
        for comment in task.comments.all().order_by('created_at'):
            comments_data.append({
                'user': comment.user.username,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
            })
            
        if not comments_data:
            return JsonResponse({'summary': 'No comments to summarize.'})
            
        # Generate summary
        summary = summarize_comments(comments_data)
        
        if not summary:
            return JsonResponse({'error': 'Failed to generate summary'}, status=500)
            
        return JsonResponse({'summary': summary})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def board_analytics_insights_api(request, board_id):
    """
    API endpoint to generate insights from board analytics
    """
    try:
        from django.db.models import Count, Q
        from django.utils import timezone
        
        # Get the board and verify user access
        from kanban.models import Board
        board = get_object_or_404(Board, id=board_id)
        
        # Check if user has access to this board
        if not (board.created_by == request.user or request.user in board.members.all()):
            return JsonResponse({'error': 'Access denied'}, status=403)
            
        # Get analytics data
        columns = board.columns.all()
        tasks = Task.objects.filter(column__board=board)
        
        # Get task counts for each column
        column_tasks = {}
        for column in columns:
            column_tasks[column.name.lower()] = tasks.filter(column=column).count()
            
        # Find done column(s) - usually columns with "done" or "complete" in the name
        done_columns = columns.filter(
            Q(name__icontains='done') | 
            Q(name__icontains='complete') | 
            Q(name__icontains='finished')
        )
        
        # If no done-like columns found, assume the last column is done
        if not done_columns.exists():
            done_columns = [columns.order_by('position').last()]
            
        # Count tasks in each status
        todo_count = column_tasks.get('to do', 0)
        in_progress_count = column_tasks.get('in progress', 0)
        done_count = sum(column_tasks.get(col.name.lower(), 0) for col in done_columns)
        
        # Calculate completion rate
        total_tasks = tasks.count()
        completion_rate = (done_count / total_tasks * 100) if total_tasks > 0 else 0
        
        # Count tasks by priority
        high_priority_count = tasks.filter(priority='high').count()
        urgent_priority_count = tasks.filter(priority='urgent').count()
        
        # Count overdue tasks
        overdue_count = tasks.filter(
            due_date__lt=timezone.now()
        ).exclude(
            column__in=done_columns
        ).count()
        
        # Get Lean Six Sigma data
        va_tasks = tasks.filter(labels__category='lean', labels__name='Value-Added').count()
        nva_tasks = tasks.filter(labels__category='lean', labels__name='Necessary NVA').count()
        waste_tasks = tasks.filter(labels__category='lean', labels__name='Waste/Eliminate').count()
        
        # Calculate LSS percentages
        total_lss_tasks = va_tasks + nva_tasks + waste_tasks
        
        if total_lss_tasks > 0:
            value_added_percent = va_tasks / total_lss_tasks * 100
            non_value_added_percent = nva_tasks / total_lss_tasks * 100
            waste_percent = waste_tasks / total_lss_tasks * 100
        else:
            value_added_percent = 0
            non_value_added_percent = 0
            waste_percent = 0
            
        # Compile analytics data for AI
        analytics_data = {
            'todo_count': todo_count,
            'in_progress_count': in_progress_count,
            'done_count': done_count,
            'total_tasks': total_tasks,
            'completion_rate': round(completion_rate, 1),
            'high_priority_count': high_priority_count,
            'urgent_priority_count': urgent_priority_count,
            'overdue_count': overdue_count,
            'value_added_percent': round(value_added_percent, 1),
            'non_value_added_percent': round(non_value_added_percent, 1),
            'waste_percent': round(waste_percent, 1),
        }
        
        # Generate insights
        insights = generate_analytics_insights(analytics_data)
        
        if not insights:
            return JsonResponse({'error': 'Failed to generate insights'}, status=500)
            
        return JsonResponse({
            'insights': insights,
            'analytics': analytics_data
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def suggest_lss_classification_api(request):
    """
    API endpoint to suggest Lean Six Sigma classification for a task
    """
    try:
        data = json.loads(request.body)
        title = data.get('title', '')
        description = data.get('description', '')
        
        if not title:
            return JsonResponse({'error': 'Title is required'}, status=400)
            
        # Call AI util function to suggest classification
        suggestion = suggest_lean_classification(title, description)
        
        if not suggestion:
            return JsonResponse({'error': 'Failed to suggest classification'}, status=500)
            
        return JsonResponse(suggestion)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
