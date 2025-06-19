"""
API Views for AI-powered features in TaskFlow

This module contains API view functions that handle requests from 
the front-end for AI-powered features.
"""
import json
import logging
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone

# Setup logging
logger = logging.getLogger(__name__)

from kanban.models import Task, Comment, Board, Column
from accounts.models import UserProfile
from django.contrib.auth.models import User
from kanban.utils.ai_utils import (
    generate_task_description, 
    summarize_comments,
    suggest_lean_classification,
    summarize_board_analytics,
    suggest_task_priority,
    predict_realistic_deadline,
    recommend_board_columns,
    suggest_task_breakdown,
    analyze_workflow_optimization,
    analyze_critical_path,
    predict_task_completion,
    generate_project_timeline,    extract_tasks_from_transcript
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

@login_required
@require_http_methods(["GET"])
def summarize_board_analytics_api(request, board_id):
    """
    API endpoint to summarize board analytics using AI
    """
    try:
        # Get the board and verify user access
        board = get_object_or_404(Board, id=board_id)
        
        # Check if user has access to this board
        if not (board.created_by == request.user or request.user in board.members.all()):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Gather analytics data (same as in board_analytics view)
        from django.db.models import Count, Q
        from django.utils import timezone
        from datetime import timedelta
        
        # Get all tasks for this board
        all_tasks = Task.objects.filter(column__board=board)
        total_tasks = all_tasks.count()
        
        # Completed tasks
        completed_count = Task.objects.filter(
            column__board=board, 
            column__name__icontains='done'
        ).count()
        
        # Calculate productivity
        total_progress_percentage = 0
        for task in all_tasks:
            if task.column.name.lower().find('done') >= 0:
                progress = 100
            else:
                progress = task.progress
            total_progress_percentage += progress
        
        productivity = 0
        if total_tasks > 0:
            productivity = (total_progress_percentage / (total_tasks * 100)) * 100
        
        # Overdue and upcoming tasks
        today = timezone.now().date()
        overdue_tasks = Task.objects.filter(
            column__board=board,
            due_date__date__lt=today
        ).exclude(column__name__icontains='done')
        
        upcoming_tasks = Task.objects.filter(
            column__board=board,
            due_date__date__gte=today,
            due_date__date__lte=today + timedelta(days=7)
        )
        
        # Lean Six Sigma metrics
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
        
        total_categorized = value_added_count + necessary_nva_count + waste_count
        value_added_percentage = 0
        if total_categorized > 0:
            value_added_percentage = (value_added_count / total_categorized) * 100
        
        # Task distribution by column
        columns = Column.objects.filter(board=board)
        tasks_by_column = []
        for column in columns:
            count = Task.objects.filter(column=column).count()
            tasks_by_column.append({'name': column.name, 'count': count})
        
        # Task distribution by priority
        priority_queryset = Task.objects.filter(column__board=board).values('priority').annotate(
            count=Count('id')
        ).order_by('priority')
        
        tasks_by_priority = []
        for item in priority_queryset:
            priority_name = dict(Task.PRIORITY_CHOICES).get(item['priority'], item['priority'])
            tasks_by_priority.append({'priority': priority_name, 'count': item['count']})
        
        # Task distribution by user
        user_queryset = Task.objects.filter(column__board=board).values(
            'assigned_to__username'
        ).annotate(count=Count('id')).order_by('-count')
        
        tasks_by_user = []
        for item in user_queryset:
            username = item['assigned_to__username'] or 'Unassigned'
            completed_user_tasks = Task.objects.filter(
                column__board=board,
                assigned_to__username=item['assigned_to__username'],
                column__name__icontains='done'
            ).count()
            
            user_completion_rate = 0
            if item['count'] > 0:
                user_completion_rate = (completed_user_tasks / item['count']) * 100
                
            tasks_by_user.append({
                'username': username,
                'count': item['count'],
                'completion_rate': int(user_completion_rate)
            })
        
        # Prepare analytics data for AI
        analytics_data = {
            'total_tasks': total_tasks,
            'completed_count': completed_count,
            'productivity': round(productivity, 1),
            'overdue_count': overdue_tasks.count(),
            'upcoming_count': upcoming_tasks.count(),
            'value_added_percentage': round(value_added_percentage, 1),
            'total_categorized': total_categorized,
            'tasks_by_lean_category': [
                {'name': 'Value-Added', 'count': value_added_count},
                {'name': 'Necessary NVA', 'count': necessary_nva_count},
                {'name': 'Waste/Eliminate', 'count': waste_count}
            ],
            'tasks_by_column': tasks_by_column,
            'tasks_by_priority': tasks_by_priority,
            'tasks_by_user': tasks_by_user
        }
        
        # Generate analytics summary
        summary = summarize_board_analytics(analytics_data)
        
        if not summary:
            return JsonResponse({'error': 'Failed to generate analytics summary'}, status=500)
            
        return JsonResponse({'summary': summary})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def suggest_task_priority_api(request):
    """
    API endpoint to suggest optimal priority for a task using AI
    """
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        title = data.get('title', '')
        description = data.get('description', '')
        due_date = data.get('due_date', '')
        
        if not title:
            return JsonResponse({'error': 'Title is required'}, status=400)
        
        # If task_id is provided, get board context
        board_context = {}
        if task_id:
            task = get_object_or_404(Task, id=task_id)
            board = task.column.board
            
            # Check access
            if not (board.created_by == request.user or request.user in board.members.all()):
                return JsonResponse({'error': 'Access denied'}, status=403)
        else:
            # For new tasks, try to get board from request
            board_id = data.get('board_id')
            if board_id:
                board = get_object_or_404(Board, id=board_id)
                if not (board.created_by == request.user or request.user in board.members.all()):
                    return JsonResponse({'error': 'Access denied'}, status=403)
            else:
                return JsonResponse({'error': 'Board ID or Task ID is required'}, status=400)
        
        # Gather board context for priority suggestion
        from django.db.models import Count
        all_tasks = Task.objects.filter(column__board=board)
        
        board_context = {
            'total_tasks': all_tasks.count(),
            'high_priority_count': all_tasks.filter(priority='high').count(),
            'urgent_count': all_tasks.filter(priority='urgent').count(),
            'overdue_count': all_tasks.filter(due_date__lt=timezone.now()).exclude(column__name__icontains='done').count(),
            'upcoming_deadlines': all_tasks.filter(
                due_date__gte=timezone.now(),
                due_date__lte=timezone.now() + timedelta(days=7)
            ).count()
        }
        
        task_data = {
            'title': title,
            'description': description,
            'due_date': due_date,
            'current_priority': data.get('current_priority', 'medium')
        }
        
        # Call AI function
        suggestion = suggest_task_priority(task_data, board_context)
        
        if not suggestion:
            return JsonResponse({'error': 'Failed to suggest priority'}, status=500)
            
        return JsonResponse(suggestion)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def predict_deadline_api(request):
    """
    API endpoint to predict realistic deadline for a task using AI
    """
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        title = data.get('title', '')
        description = data.get('description', '')
        priority = data.get('priority', 'medium')
        assigned_to = data.get('assigned_to', 'Unassigned')
        
        if not title:
            return JsonResponse({'error': 'Title is required'}, status=400)
        
        # Get board context for deadline prediction
        board_id = data.get('board_id')
        if task_id:
            task = get_object_or_404(Task, id=task_id)
            board = task.column.board
        elif board_id:
            board = get_object_or_404(Board, id=board_id)
        else:
            return JsonResponse({'error': 'Board ID or Task ID is required'}, status=400)
        
        # Check access
        if not (board.created_by == request.user or request.user in board.members.all()):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Gather team context for deadline prediction
        from django.db.models import Avg
        from django.utils import timezone
        
        # Calculate average completion times (simplified calculation)
        completed_tasks = Task.objects.filter(
            column__board=board, 
            column__name__icontains='done'
        )
        
        team_avg_completion = 5  # Default fallback
        assignee_avg_completion = 5  # Default fallback
        
        if completed_tasks.exists():
            # Simple calculation based on created_at to completion
            total_days = 0
            count = 0
            for task in completed_tasks:
                if task.updated_at and task.created_at:
                    days_to_complete = (task.updated_at - task.created_at).days
                    if days_to_complete > 0:  # Avoid zero or negative days
                        total_days += days_to_complete
                        count += 1
            
            if count > 0:
                team_avg_completion = total_days / count
        
        # Get assignee's current workload
        assignee_current_tasks = 0
        if assigned_to and assigned_to != 'Unassigned':
            from django.contrib.auth.models import User
            try:
                assignee_user = User.objects.get(username=assigned_to)
                assignee_current_tasks = Task.objects.filter(
                    column__board=board,
                    assigned_to=assignee_user
                ).exclude(column__name__icontains='done').count()
            except User.DoesNotExist:
                pass
        
        team_context = {
            'assignee_avg_completion_days': assignee_avg_completion,
            'team_avg_completion_days': team_avg_completion,
            'assignee_current_tasks': assignee_current_tasks,
            'similar_tasks_avg_days': team_avg_completion,  # Simplified
            'upcoming_holidays': []  # Could be enhanced to include actual holidays
        }
        
        task_data = {
            'title': title,
            'description': description,
            'priority': priority,
            'assigned_to': assigned_to
        }
        
        # Call AI function
        prediction = predict_realistic_deadline(task_data, team_context)
        
        if not prediction:
            return JsonResponse({'error': 'Failed to predict deadline'}, status=500)
            
        return JsonResponse(prediction)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def recommend_columns_api(request):
    """
    API endpoint to recommend optimal column structure for a board using AI
    """
    try:
        data = json.loads(request.body)
        board_id = data.get('board_id')
        
        if board_id:
            # Existing board - get current structure
            board = get_object_or_404(Board, id=board_id)
            
            # Check access
            if not (board.created_by == request.user or request.user in board.members.all()):
                return JsonResponse({'error': 'Access denied'}, status=403)
            
            existing_columns = [col.name for col in board.columns.all()]
            board_name = board.name
            board_description = board.description
            team_size = board.members.count() + 1  # +1 for creator
        else:
            # New board recommendations
            board_name = data.get('name', '')
            board_description = data.get('description', '')
            team_size = data.get('team_size', 1)
            existing_columns = []
        
        if not board_name:
            return JsonResponse({'error': 'Board name is required'}, status=400)
        
        board_data = {
            'name': board_name,
            'description': board_description,
            'team_size': team_size,
            'project_type': data.get('project_type', 'general'),
            'organization_type': data.get('organization_type', 'general'),
            'existing_columns': existing_columns
        }
        
        # Call AI function
        recommendation = recommend_board_columns(board_data)
        
        if not recommendation:
            return JsonResponse({'error': 'Failed to recommend columns'}, status=500)
            
        return JsonResponse(recommendation)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def suggest_task_breakdown_api(request):
    """
    API endpoint to suggest automated breakdown of complex tasks using AI
    """
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        title = data.get('title', '')
        description = data.get('description', '')
        
        if not title:
            return JsonResponse({'error': 'Title is required'}, status=400)
        
        # If task_id provided, verify access
        if task_id:
            task = get_object_or_404(Task, id=task_id)
            board = task.column.board
            
            # Check access
            if not (board.created_by == request.user or request.user in board.members.all()):
                return JsonResponse({'error': 'Access denied'}, status=403)
        
        task_data = {
            'title': title,
            'description': description,
            'priority': data.get('priority', 'medium'),
            'due_date': data.get('due_date', ''),
            'estimated_effort': data.get('estimated_effort', '')
        }
        
        # Call AI function
        breakdown = suggest_task_breakdown(task_data)
        
        if not breakdown:
            return JsonResponse({'error': 'Failed to suggest task breakdown'}, status=500)
            
        return JsonResponse(breakdown)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def analyze_workflow_optimization_api(request):
    """
    API endpoint to analyze workflow and suggest optimizations using AI
    """
    try:
        data = json.loads(request.body)
        board_id = data.get('board_id')
        
        if not board_id:
            return JsonResponse({'error': 'Board ID is required'}, status=400)
        
        board = get_object_or_404(Board, id=board_id)
        
        # Check access
        if not (board.created_by == request.user or request.user in board.members.all()):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Gather comprehensive board analytics (similar to existing analytics)
        from django.db.models import Count, Avg
        from django.utils import timezone
        from datetime import timedelta
        
        all_tasks = Task.objects.filter(column__board=board)
        total_tasks = all_tasks.count()
        
        # Calculate average completion time
        completed_tasks = all_tasks.filter(column__name__icontains='done')
        avg_completion_time = 5  # Default
        if completed_tasks.exists():
            total_days = 0
            count = 0
            for task in completed_tasks:
                if task.updated_at and task.created_at:
                    days = (task.updated_at - task.created_at).days
                    if days > 0:
                        total_days += days
                        count += 1
            if count > 0:
                avg_completion_time = total_days / count
        
        # Task distribution by column
        columns = Column.objects.filter(board=board)
        tasks_by_column = []
        for column in columns:
            count = Task.objects.filter(column=column).count()
            tasks_by_column.append({'name': column.name, 'count': count})
        
        # Task distribution by priority
        priority_queryset = all_tasks.values('priority').annotate(count=Count('id'))
        tasks_by_priority = []
        for item in priority_queryset:
            priority_name = dict(Task.PRIORITY_CHOICES).get(item['priority'], item['priority'])
            tasks_by_priority.append({'priority': priority_name, 'count': item['count']})
        
        # Task distribution by user
        user_queryset = all_tasks.values('assigned_to__username').annotate(count=Count('id'))
        tasks_by_user = []
        for item in user_queryset:
            username = item['assigned_to__username'] or 'Unassigned'
            completed_user_tasks = completed_tasks.filter(
                assigned_to__username=item['assigned_to__username']
            ).count()
            
            completion_rate = 0
            if item['count'] > 0:
                completion_rate = (completed_user_tasks / item['count']) * 100
                
            tasks_by_user.append({
                'username': username,
                'count': item['count'],
                'completion_rate': int(completion_rate)
            })
        
        # Calculate productivity
        total_progress = sum(task.progress for task in all_tasks)
        productivity = 0
        if total_tasks > 0:
            productivity = total_progress / total_tasks
        
        # Overdue count
        overdue_count = all_tasks.filter(
            due_date__lt=timezone.now()
        ).exclude(column__name__icontains='done').count()
        
        board_analytics = {
            'total_tasks': total_tasks,
            'tasks_by_column': tasks_by_column,
            'tasks_by_priority': tasks_by_priority,
            'tasks_by_user': tasks_by_user,
            'avg_completion_time_days': avg_completion_time,
            'overdue_count': overdue_count,
            'productivity': productivity,
            'weekly_velocity': []  # Could be enhanced with historical data
        }
        
        # Call AI function
        optimization = analyze_workflow_optimization(board_analytics)
        
        if not optimization:
            return JsonResponse({'error': 'Failed to analyze workflow'}, status=500)
            
        return JsonResponse(optimization)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def create_subtasks_api(request):
    """
    API endpoint to create multiple tasks from AI-generated subtask breakdown
    """
    try:
        data = json.loads(request.body)
        board_id = data.get('board_id')
        column_id = data.get('column_id')
        subtasks = data.get('subtasks', [])
        original_task_title = data.get('original_task_title', '')
        if not board_id or not subtasks:
            return JsonResponse({'error': 'Missing required fields (board_id, subtasks)'}, status=400)
              # Verify user has access to the board
        board = get_object_or_404(Board, id=board_id)
        if not (request.user in board.members.all() or request.user == board.created_by):
            return JsonResponse({'error': 'Access denied'}, status=403)
            
        # Get column - if not specified, use first column
        if column_id:
            column = get_object_or_404(Column, id=column_id, board=board)
        else:
            # Default to first column (usually "To Do")
            column = Column.objects.filter(board=board).order_by('position').first()
            if not column:
                return JsonResponse({'error': 'No columns found in board'}, status=400)
        
        created_tasks = []
        errors = []
        
        for i, subtask_data in enumerate(subtasks):
            try:
                # Extract subtask information
                title = subtask_data.get('title', '').strip()
                description = subtask_data.get('description', '').strip()
                estimated_effort = subtask_data.get('estimated_effort', '')
                priority = subtask_data.get('priority', 'medium').lower()
                
                # Validate data
                if not title:
                    errors.append(f"Subtask {i+1}: Title is required")
                    continue
                
                # Ensure priority is valid
                valid_priorities = ['low', 'medium', 'high', 'urgent']
                if priority not in valid_priorities:
                    priority = 'medium'
                
                # Parse estimated effort to get due date (if provided)
                due_date = None
                if estimated_effort and 'day' in estimated_effort.lower():
                    try:
                        # Extract number of days from strings like "2 days", "1 day"
                        import re
                        days_match = re.search(r'(\d+)', estimated_effort)
                        if days_match:
                            days = int(days_match.group(1))
                            due_date = timezone.now() + timedelta(days=days)
                    except:
                        pass  # If parsing fails, just leave due_date as None
                
                # Enhance description with effort information
                if estimated_effort:
                    if description:
                        description += f"\n\n**Estimated Effort:** {estimated_effort}"
                    else:
                        description = f"**Estimated Effort:** {estimated_effort}"
                
                # Add reference to original task
                if original_task_title:
                    description += f"\n\n*Subtask of: {original_task_title}*"
                
                # Create the task
                task = Task.objects.create(
                    title=title,
                    description=description,
                    column=column,
                    priority=priority,
                    due_date=due_date,
                    created_by=request.user,
                    position=Task.objects.filter(column=column).count()  # Add to end
                )
                
                created_tasks.append({
                    'id': task.id,
                    'title': task.title,
                    'priority': task.priority,
                    'due_date': task.due_date.isoformat() if task.due_date else None
                })
                
            except Exception as e:
                errors.append(f"Subtask {i+1}: {str(e)}")
        
        # Prepare response
        response_data = {
            'success': True,
            'created_count': len(created_tasks),
            'total_subtasks': len(subtasks),
            'created_tasks': created_tasks
        }
        
        if errors:
            response_data['errors'] = errors
            response_data['partial_success'] = True
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def analyze_critical_path_api(request):
    """
    API endpoint to analyze critical path and dependencies for a board using AI
    """
    try:
        data = json.loads(request.body)
        board_id = data.get('board_id')
        
        if not board_id:
            return JsonResponse({'error': 'Board ID is required'}, status=400)
            
        # Get the board and verify user access
        board = get_object_or_404(Board, id=board_id)
        
        # Check if user has access to this board
        if not (board.created_by == request.user or request.user in board.members.all()):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Gather tasks data for AI analysis
        tasks_data = []
        for task in board.columns.prefetch_related('tasks__predecessors', 'tasks__assigned_to').all():
            for task_obj in task.tasks.all():
                task_info = {
                    'id': task_obj.id,
                    'title': task_obj.title,
                    'column_name': task_obj.column.name,
                    'estimated_duration_hours': task_obj.estimated_duration_hours,
                    'estimated_start_date': task_obj.estimated_start_date.isoformat() if task_obj.estimated_start_date else None,
                    'due_date': task_obj.due_date.isoformat() if task_obj.due_date else None,
                    'progress': task_obj.progress,
                    'priority': task_obj.priority,
                    'assigned_to': task_obj.assigned_to.username if task_obj.assigned_to else None,
                    'is_milestone': task_obj.is_milestone,
                    'predecessors': [pred.id for pred in task_obj.predecessors.all()],
                }
                tasks_data.append(task_info)
        
        board_data = {
            'board_info': {
                'name': board.name,
                'description': board.description
            },
            'tasks': tasks_data
        }
        
        # Import the new AI function
        from kanban.utils.ai_utils import analyze_critical_path
        
        # Call AI analysis
        analysis_result = analyze_critical_path(board_data)
        
        if not analysis_result:
            return JsonResponse({'error': 'Failed to analyze critical path'}, status=500)
        
        # Update task fields with AI results
        if 'task_analysis' in analysis_result:
            for task_analysis in analysis_result['task_analysis']:
                try:
                    task_id = task_analysis.get('task_id')
                    task_obj = Task.objects.get(id=task_id, column__board=board)
                    
                    # Update AI-calculated fields
                    if task_analysis.get('earliest_start'):
                        task_obj.earliest_start = task_analysis['earliest_start']
                    if task_analysis.get('earliest_finish'):
                        task_obj.earliest_finish = task_analysis['earliest_finish']
                    if task_analysis.get('latest_start'):
                        task_obj.latest_start = task_analysis['latest_start']
                    if task_analysis.get('latest_finish'):
                        task_obj.latest_finish = task_analysis['latest_finish']
                    if task_analysis.get('slack_hours') is not None:
                        task_obj.slack_time_hours = task_analysis['slack_hours']
                    
                    task_obj.is_critical_path = task_analysis.get('is_critical', False)
                    task_obj.last_ai_analysis = timezone.now()
                    
                    # Store AI recommendations
                    if task_analysis.get('risk_factors'):
                        task_obj.ai_recommendations = f"Risk factors: {', '.join(task_analysis['risk_factors'])}"
                    
                    task_obj.save()
                    
                except Task.DoesNotExist:
                    continue
                except Exception as e:
                    logger.error(f"Error updating task {task_id}: {str(e)}")
        
        return JsonResponse(analysis_result)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def predict_task_completion_api(request):
    """
    API endpoint to predict task completion dates using AI
    """
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        
        if not task_id:
            return JsonResponse({'error': 'Task ID is required'}, status=400)
            
        # Get the task and verify user access
        task = get_object_or_404(Task, id=task_id)
        board = task.column.board
        
        # Check if user has access to this board
        if not (board.created_by == request.user or request.user in board.members.all()):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Prepare task data for AI analysis
        task_data = {
            'title': task.title,
            'progress': task.progress,
            'estimated_duration_hours': task.estimated_duration_hours,
            'actual_duration_hours': task.actual_duration_hours,
            'actual_start_date': task.actual_start_date.isoformat() if task.actual_start_date else None,
            'estimated_start_date': task.estimated_start_date.isoformat() if task.estimated_start_date else None,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'priority': task.priority,
            'assigned_to': task.assigned_to.username if task.assigned_to else None,
            'predecessors': [pred.id for pred in task.predecessors.all()],
        }
        
        # Get historical data for similar tasks (optional enhancement)
        historical_data = []
        similar_tasks = Task.objects.filter(
            column__board=board,
            assigned_to=task.assigned_to,
            progress=100
        ).exclude(id=task.id)[:5]
        
        for hist_task in similar_tasks:
            if hist_task.actual_duration_hours and hist_task.estimated_duration_hours:
                historical_data.append({
                    'title': hist_task.title,
                    'estimated_hours': hist_task.estimated_duration_hours,
                    'actual_hours': hist_task.actual_duration_hours,
                    'accuracy_percentage': min(100, (hist_task.estimated_duration_hours / hist_task.actual_duration_hours) * 100)
                })
        
        # Import the new AI function
        from kanban.utils.ai_utils import predict_task_completion
        
        # Call AI prediction
        prediction_result = predict_task_completion(task_data, historical_data)
        
        if not prediction_result:
            return JsonResponse({'error': 'Failed to predict task completion'}, status=500)
        
        # Update task with AI insights
        if 'recommendations' in prediction_result:
            recommendations_text = "; ".join([
                f"{rec.get('type', '')}: {rec.get('action', '')}" 
                for rec in prediction_result['recommendations'][:3]
            ])
            task.ai_recommendations = recommendations_text
            task.last_ai_analysis = timezone.now()
            task.save()
        
        return JsonResponse(prediction_result)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def generate_project_timeline_api(request):
    """
    API endpoint to generate AI-enhanced project timeline (Gantt-like view)
    """
    try:
        data = json.loads(request.body)
        board_id = data.get('board_id')
        
        if not board_id:
            return JsonResponse({'error': 'Board ID is required'}, status=400)
            
        # Get the board and verify user access
        board = get_object_or_404(Board, id=board_id)
        
        # Check if user has access to this board
        if not (board.created_by == request.user or request.user in board.members.all()):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Gather comprehensive board data
        tasks_data = []
        team_data = []
        
        # Collect tasks data
        for column in board.columns.prefetch_related('tasks__predecessors', 'tasks__assigned_to').all():
            for task_obj in column.tasks.all():
                task_info = {
                    'id': task_obj.id,
                    'title': task_obj.title,
                    'column_name': task_obj.column.name,
                    'estimated_duration_hours': task_obj.estimated_duration_hours,
                    'estimated_start_date': task_obj.estimated_start_date.isoformat() if task_obj.estimated_start_date else None,
                    'due_date': task_obj.due_date.isoformat() if task_obj.due_date else None,
                    'progress': task_obj.progress,
                    'priority': task_obj.priority,
                    'assigned_to': task_obj.assigned_to.username if task_obj.assigned_to else None,
                    'is_milestone': task_obj.is_milestone,
                    'predecessors': [pred.id for pred in task_obj.predecessors.all()],
                }
                tasks_data.append(task_info)
        
        # Collect team data
        all_users = set()
        for task in tasks_data:
            if task['assigned_to']:
                all_users.add(task['assigned_to'])
        
        for username in all_users:
            user_tasks = [t for t in tasks_data if t['assigned_to'] == username]
            team_data.append({
                'name': username,
                'task_count': len(user_tasks),
                'completed_tasks': len([t for t in user_tasks if t['progress'] == 100]),
                'in_progress_tasks': len([t for t in user_tasks if 0 < t['progress'] < 100])
            })
        
        board_data = {
            'board_info': {
                'name': board.name,
                'description': board.description
            },
            'tasks': tasks_data,
            'team': team_data
        }
        
        # Import the new AI function
        from kanban.utils.ai_utils import generate_project_timeline
        
        # Call AI timeline generation
        timeline_result = generate_project_timeline(board_data)
        
        if not timeline_result:
            return JsonResponse({'error': 'Failed to generate project timeline'}, status=500)
        
        return JsonResponse(timeline_result)
        
    except Exception as e:        return JsonResponse({'error': str(e)}, status=500)

# Meeting Transcript Extraction API Endpoints










@login_required
@require_http_methods(["POST"])
def update_user_skills_api(request):
    """
    API endpoint to update user skills and capacity information
    """
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        # If no user_id provided, update current user
        if not user_id:
            target_user = request.user
        else:
            target_user = get_object_or_404(User, id=user_id)
            
            # Check if current user can update this profile
            if target_user != request.user:
                # Only organization admins can update other users' profiles
                if not hasattr(request.user, 'profile') or not request.user.profile.is_admin:
                    return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(
            user=target_user,
            defaults={'organization': request.user.profile.organization}
        )
        
        # Update skills
        if 'skills' in data:
            skills = data['skills']
            if isinstance(skills, list):
                profile.skills = skills
        
        # Update capacity
        if 'weekly_capacity_hours' in data:
            capacity = data['weekly_capacity_hours']
            if isinstance(capacity, int) and capacity > 0:
                profile.weekly_capacity_hours = capacity
        
        # Update availability schedule
        if 'availability_schedule' in data:
            schedule = data['availability_schedule']
            if isinstance(schedule, dict):
                profile.availability_schedule = schedule
        
        # Update preferred task types
        if 'preferred_task_types' in data:
            task_types = data['preferred_task_types']
            if isinstance(task_types, list):
                profile.preferred_task_types = task_types
        
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'User profile updated successfully',
            'utilization_percentage': profile.utilization_percentage,
            'available_hours': profile.available_hours
        })
        
    except Exception as e:
        logger.error(f"Error updating user skills API: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def extract_tasks_from_transcript_api(request):
    """
    API endpoint to extract tasks from meeting transcript using AI
    """
    try:
        data = json.loads(request.body)
        transcript = data.get('transcript', '')
        board_id = data.get('board_id')
        meeting_context = data.get('meeting_context', {})
        
        if not transcript or not board_id:
            return JsonResponse({'error': 'Transcript and board ID are required'}, status=400)
            
        # Verify board access
        board = get_object_or_404(Board, id=board_id)
        if not (board.created_by == request.user or request.user in board.members.all()):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Extract tasks using AI
        from kanban.utils.ai_utils import extract_tasks_from_transcript
        extracted_tasks = extract_tasks_from_transcript(transcript, meeting_context, board)
        
        if not extracted_tasks:
            return JsonResponse({'error': 'Failed to extract tasks from transcript'}, status=500)
            
        return JsonResponse(extracted_tasks)
    except Exception as e:
        logger.error(f"Error in extract_tasks_from_transcript_api: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def create_tasks_from_extraction_api(request):
    """
    API endpoint to create tasks from reviewed/edited extraction results
    """
    try:
        data = json.loads(request.body)
        board_id = data.get('board_id')
        approved_tasks = data.get('approved_tasks', [])
        meeting_transcript_id = data.get('meeting_transcript_id')
        
        if not board_id or not approved_tasks:
            return JsonResponse({'error': 'Board ID and approved tasks are required'}, status=400)
        
        # Verify board access
        board = get_object_or_404(Board, id=board_id)
        if not (board.created_by == request.user or request.user in board.members.all()):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Get the "To Do" column
        todo_column = Column.objects.filter(
            board=board, 
            name__iregex=r'^(to do|todo)$'
        ).first()
        
        if not todo_column:
            todo_column = Column.objects.filter(board=board).order_by('position').first()
        
        created_tasks = []
        errors = []
        
        from kanban.utils.ai_utils import parse_due_date
        
        for task_data in approved_tasks:
            try:
                # Create task with AI-suggested properties
                task = Task.objects.create(
                    title=task_data.get('title'),
                    description=task_data.get('description', ''),
                    column=todo_column,
                    priority=task_data.get('priority', 'medium'),
                    due_date=parse_due_date(task_data.get('due_date_suggestion')),
                    created_by=request.user,
                    position=Task.objects.filter(column=todo_column).count(),
                )
                
                # Assign if suggested
                if task_data.get('suggested_assignee'):
                    try:
                        assignee = User.objects.get(username=task_data['suggested_assignee'])
                        if assignee in board.members.all() or assignee == board.created_by:
                            task.assigned_to = assignee
                            task.save()
                    except User.DoesNotExist:
                        pass
                
                created_tasks.append({
                    'id': task.id,
                    'title': task.title,
                    'url': f'/tasks/{task.id}/'
                })
                
            except Exception as e:
                errors.append(f"Failed to create task '{task_data.get('title', 'Unknown')}': {str(e)}")
        
        # Update meeting transcript record if provided
        if meeting_transcript_id:
            try:
                from kanban.models import MeetingTranscript
                transcript_record = MeetingTranscript.objects.get(
                    id=meeting_transcript_id,
                    created_by=request.user
                )
                transcript_record.tasks_created_count = len(created_tasks)
                transcript_record.processing_status = 'completed'
                transcript_record.processed_at = timezone.now()
                transcript_record.save()
            except MeetingTranscript.DoesNotExist:
                pass
        
        return JsonResponse({
            'success': True,
            'created_tasks': created_tasks,
            'errors': errors,
            'total_created': len(created_tasks)
        })
        
    except Exception as e:
        logger.error(f"Error in create_tasks_from_extraction_api: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def process_transcript_file_api(request):
    """
    API endpoint to process uploaded transcript file and extract text
    """
    try:
        if 'transcript_file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        uploaded_file = request.FILES['transcript_file']
        
        # Check file size (limit to 10MB)
        if uploaded_file.size > 10 * 1024 * 1024:
            return JsonResponse({'error': 'File size too large. Maximum 10MB allowed.'}, status=400)
        
        # Check file type
        allowed_extensions = ['.txt', '.docx', '.pdf']
        file_extension = uploaded_file.name.lower().split('.')[-1]
        if f'.{file_extension}' not in allowed_extensions:
            return JsonResponse({
                'error': f'Unsupported file type. Allowed: {", ".join(allowed_extensions)}'
            }, status=400)
        
        # Save file temporarily and extract text
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            from kanban.utils.ai_utils import extract_text_from_file
            extracted_text = extract_text_from_file(temp_file_path, file_extension)
            
            if not extracted_text:
                return JsonResponse({'error': 'Failed to extract text from file'}, status=500)
            
            return JsonResponse({
                'success': True,
                'extracted_text': extracted_text,
                'file_name': uploaded_file.name,
                'file_size': uploaded_file.size
            })
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        logger.error(f"Error in process_transcript_file_api: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# AI Resource Analysis API Views

@login_required
@require_http_methods(["POST"])
def analyze_resource_bottlenecks_api(request):
    """
    API endpoint to analyze resource bottlenecks using AI
    """
    try:
        data = json.loads(request.body)
        board_id = data.get('board_id')
        
        if not board_id:
            return JsonResponse({'error': 'Board ID is required'}, status=400)
        
        board = get_object_or_404(Board, id=board_id)
        
        # Check if user has access to the board
        if not (request.user in board.members.all() or 
                board.created_by == request.user or 
                request.user.profile.is_admin or 
                request.user == board.organization.created_by):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        from kanban.utils.ai_resource_analysis import analyze_resource_bottlenecks
        result = analyze_resource_bottlenecks(board_id)
        
        if result:
            return JsonResponse({
                'success': True,
                'analysis': result
            })
        else:
            return JsonResponse({'error': 'Failed to analyze resource bottlenecks'}, status=500)
            
    except Exception as e:
        logger.error(f"Error in analyze_resource_bottlenecks_api: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def optimize_task_assignments_api(request):
    """
    API endpoint to optimize task assignments using AI
    """
    try:
        data = json.loads(request.body)
        board_id = data.get('board_id')
        task_ids = data.get('task_ids', [])
        
        if not board_id:
            return JsonResponse({'error': 'Board ID is required'}, status=400)
        
        board = get_object_or_404(Board, id=board_id)
        
        # Check if user has access to the board
        if not (request.user in board.members.all() or 
                board.created_by == request.user or 
                request.user.profile.is_admin or 
                request.user == board.organization.created_by):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        from kanban.utils.ai_resource_analysis import optimize_task_assignments
        result = optimize_task_assignments(board_id, task_ids)
        
        if result:
            return JsonResponse({
                'success': True,
                'optimization': result
            })
        else:
            return JsonResponse({'error': 'Failed to optimize task assignments'}, status=500)
            
    except Exception as e:
        logger.error(f"Error in optimize_task_assignments_api: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def balance_team_workload_api(request):
    """
    API endpoint to balance team workload using AI
    """
    try:
        data = json.loads(request.body)
        board_id = data.get('board_id')
        
        if not board_id:
            return JsonResponse({'error': 'Board ID is required'}, status=400)
        
        board = get_object_or_404(Board, id=board_id)
        
        # Check if user has access to the board
        if not (request.user in board.members.all() or 
                board.created_by == request.user or 
                request.user.profile.is_admin or 
                request.user == board.organization.created_by):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        from kanban.utils.ai_resource_analysis import balance_team_workload
        result = balance_team_workload(board_id)
        
        if result:
            return JsonResponse({
                'success': True,
                'balance_analysis': result
            })
        else:
            return JsonResponse({'error': 'Failed to balance team workload'}, status=500)
            
    except Exception as e:
        logger.error(f"Error in balance_team_workload_api: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def forecast_resource_needs_api(request):
    """
    API endpoint to forecast resource needs using AI
    """
    try:
        data = json.loads(request.body)
        board_id = data.get('board_id')
        forecast_weeks = data.get('forecast_weeks', 4)
        
        if not board_id:
            return JsonResponse({'error': 'Board ID is required'}, status=400)
        
        board = get_object_or_404(Board, id=board_id)
        
        # Check if user has access to the board
        if not (request.user in board.members.all() or 
                board.created_by == request.user or 
                request.user.profile.is_admin or 
                request.user == board.organization.created_by):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        from kanban.utils.ai_resource_analysis import forecast_resource_needs
        result = forecast_resource_needs(board_id, forecast_weeks)
        
        if result:
            return JsonResponse({
                'success': True,
                'forecast': result
            })
        else:
            return JsonResponse({'error': 'Failed to forecast resource needs'}, status=500)
            
    except Exception as e:
        logger.error(f"Error in forecast_resource_needs_api: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def suggest_resource_reallocation_api(request):
    """
    API endpoint to suggest resource reallocation using AI
    """
    try:
        data = json.loads(request.body)
        board_id = data.get('board_id')
        
        if not board_id:
            return JsonResponse({'error': 'Board ID is required'}, status=400)
        
        board = get_object_or_404(Board, id=board_id)
        
        # Check if user has access to the board
        if not (request.user in board.members.all() or 
                board.created_by == request.user or 
                request.user.profile.is_admin or 
                request.user == board.organization.created_by):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        from kanban.utils.ai_resource_analysis import suggest_resource_reallocation
        result = suggest_resource_reallocation(board_id)
        
        if result:
            return JsonResponse({
                'success': True,
                'reallocation': result
            })
        else:
            return JsonResponse({'error': 'Failed to suggest resource reallocation'}, status=500)
            
    except Exception as e:
        logger.error(f"Error in suggest_resource_reallocation_api: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def team_resource_overview_api(request, board_id):
    """
    API endpoint to get team resource overview
    """
    try:
        board = get_object_or_404(Board, id=board_id)
        
        # Check if user has access to the board
        if not (request.user in board.members.all() or 
                board.created_by == request.user or 
                request.user.profile.is_admin or 
                request.user == board.organization.created_by):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Get team members and their task distribution
        team_members = board.members.all()
        team_overview = []
        
        for member in team_members:
            tasks = Task.objects.filter(column__board=board, assigned_to=member)
            profile = getattr(member, 'profile', None)
            
            member_data = {
                'id': member.id,
                'username': member.username,
                'full_name': f"{member.first_name} {member.last_name}".strip(),
                'email': member.email,
                'total_tasks': tasks.count(),
                'in_progress_tasks': tasks.filter(column__name__icontains='progress').count(),
                'completed_tasks': tasks.filter(column__name__icontains='done').count(),
                'overdue_tasks': tasks.filter(
                    due_date__lt=timezone.now()
                ).exclude(column__name__icontains='done').count(),
            }
            
            if profile:
                member_data.update({
                    'skills': profile.skills if hasattr(profile, 'skills') else {},
                    'capacity_hours': profile.capacity_hours if hasattr(profile, 'capacity_hours') else 40,
                    'current_workload': profile.current_workload if hasattr(profile, 'current_workload') else 0,
                    'quality_score': profile.quality_score if hasattr(profile, 'quality_score') else 0,
                })
            
            team_overview.append(member_data)
        
        return JsonResponse({
            'success': True,
            'team_overview': team_overview,
            'board_stats': {
                'total_tasks': Task.objects.filter(column__board=board).count(),
                'completed_tasks': Task.objects.filter(
                    column__board=board, 
                    column__name__icontains='done'
                ).count(),
                'in_progress_tasks': Task.objects.filter(
                    column__board=board, 
                    column__name__icontains='progress'
                ).count(),
            }
        })
            
    except Exception as e:
        logger.error(f"Error in team_resource_overview_api: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
