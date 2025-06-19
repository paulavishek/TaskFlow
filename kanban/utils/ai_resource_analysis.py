"""
AI-Powered Smart Resource Analysis Utilities

This module provides intelligent resource analysis capabilities using Gemini AI
to optimize task assignments, predict bottlenecks, and manage team workload.
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg

from kanban.utils.ai_utils import get_model
from kanban.models import Task, Board
from accounts.models import UserProfile

logger = logging.getLogger(__name__)


def optimize_task_assignments(board_id: int, task_ids: List[int] = None) -> Optional[Dict]:
    """
    AI-powered optimization of task assignments based on skills, availability, and workload.
    
    Args:
        board_id: ID of the board to analyze
        task_ids: Optional list of specific task IDs to optimize (if None, analyzes all unassigned/suboptimal tasks)
        
    Returns:
        Dictionary with assignment optimization recommendations
    """
    try:
        model = get_model()
        if not model:
            return None
            
        from kanban.models import Board
        board = Board.objects.get(id=board_id)
        
        # Get tasks to analyze
        if task_ids:
            tasks_to_analyze = Task.objects.filter(
                id__in=task_ids,
                column__board=board
            )
        else:
            # Analyze unassigned tasks and tasks with low skill match scores
            tasks_to_analyze = Task.objects.filter(
                Q(column__board=board) & (Q(assigned_to__isnull=True) | Q(skill_match_score__lt=70))
            ).exclude(column__name__icontains='done')
        
        tasks_data = []
        for task in tasks_to_analyze:
            tasks_data.append({
                'id': task.id,
                'title': task.title,
                'description': task.description[:200] if task.description else '',
                'estimated_hours': task.estimated_duration_hours,
                'priority': task.priority,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'required_skills': task.required_skills,
                'complexity': task.complexity_score,
                'current_assignee': task.assigned_to.username if task.assigned_to else None,
                'current_skill_match': task.skill_match_score,
                'collaboration_required': task.collaboration_required
            })
        
        # Get team data with availability and skills
        team_data = []
        board_members = list(board.members.all()) + [board.created_by]
        
        for user in set(board_members):
            if not hasattr(user, 'profile'):
                continue
                
            profile = user.profile
            current_tasks = Task.objects.filter(
                column__board=board,
                assigned_to=user
            ).exclude(column__name__icontains='done')
            
            # Calculate performance metrics
            completed_tasks = Task.objects.filter(
                assigned_to=user,
                progress=100
            )[:20]
            
            avg_quality = profile.quality_score
            avg_speed = profile.average_task_completion_time or 8.0  # Default 8 hours per task
            
            # Historical accuracy (estimated vs actual time)
            accuracy_score = 100
            if completed_tasks:
                accuracy_scores = []
                for task in completed_tasks:
                    if task.estimated_duration_hours and task.actual_duration_hours:
                        accuracy = min(100, (task.estimated_duration_hours / task.actual_duration_hours) * 100)
                        accuracy_scores.append(accuracy)
                if accuracy_scores:
                    accuracy_score = sum(accuracy_scores) / len(accuracy_scores)
            
            team_data.append({
                'username': user.username,
                'skills': profile.skills,
                'capacity_hours': profile.weekly_capacity_hours,
                'available_hours': profile.available_hours,
                'utilization_percentage': profile.utilization_percentage,
                'current_tasks_count': current_tasks.count(),
                'quality_score': avg_quality,
                'average_completion_time': avg_speed,
                'estimation_accuracy': accuracy_score,
                'preferred_task_types': profile.preferred_task_types,
                'collaboration_score': profile.collaboration_score
            })
        
        prompt = f"""
        Optimize task assignments for maximum efficiency and team satisfaction:
        
        ## Tasks to Assign/Reassign:
        {json.dumps(tasks_data, indent=2)}
        
        ## Team Resource Profiles:
        {json.dumps(team_data, indent=2)}
        
        Consider these factors for optimal assignments:
        1. **Skill Matching**: Match required skills with team member expertise
        2. **Workload Balancing**: Don't overload high performers
        3. **Development Opportunities**: Give growth tasks to suitable members
        4. **Collaboration Fit**: Consider team dynamics and collaboration scores
        5. **Deadline Pressure**: Factor in urgency and team member speed
        6. **Quality Requirements**: Match quality needs with performer quality scores
        
        Format response as JSON:
        {{
            "optimization_summary": {{
                "total_tasks_analyzed": 0,
                "assignments_changed": 0,
                "average_skill_match_improvement": 0,
                "workload_balance_score": 1-10
            }},
            "optimal_assignments": [
                {{
                    "task_id": 0,
                    "task_title": "title",
                    "current_assignee": "username or null",
                    "recommended_assignee": "username",
                    "skill_match_score": 1-100,
                    "workload_impact": "low|medium|high",
                    "reasoning": "why this assignment is optimal",
                    "collaboration_suggestions": ["other team members to involve if needed"],
                    "estimated_completion_improvement": "X days faster/slower"
                }}
            ],
            "workload_rebalancing": [
                {{
                    "person": "username",
                    "current_utilization": 85,
                    "recommended_utilization": 75,
                    "actions": ["specific tasks to reassign or add"]
                }}
            ],
            "skill_development_opportunities": [
                {{
                    "person": "username",
                    "skill_to_develop": "skill name",
                    "suitable_tasks": ["task titles for learning"],
                    "mentorship_suggestion": "who could mentor"
                }}
            ],
            "resource_optimization_tips": ["actionable tips for better resource utilization"]
        }}
        """
        
        response = model.generate_content(prompt)
        if response:
            response_text = response.text.strip()
            
            # Handle code block formatting
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].strip()
                
            return json.loads(response_text)
        return None
        
    except Exception as e:
        logger.error(f"Error optimizing task assignments: {str(e)}")
        return None


def balance_team_workload(board_id: int) -> Optional[Dict]:
    """
    Dynamically balance team workload using AI analysis.
    
    Args:
        board_id: ID of the board to analyze
        
    Returns:
        Dictionary with workload balancing recommendations
    """
    try:
        model = get_model()
        if not model:
            return None
            
        from kanban.models import Board
        board = Board.objects.get(id=board_id)
        
        # Analyze current workload distribution
        team_workload = []
        board_members = list(board.members.all()) + [board.created_by]
        
        for user in set(board_members):
            if not hasattr(user, 'profile'):
                continue
                
            profile = user.profile
            current_tasks = Task.objects.filter(
                column__board=board,
                assigned_to=user
            ).exclude(column__name__icontains='done')
            
            # Calculate workload metrics
            total_hours = sum([task.estimated_duration_hours for task in current_tasks])
            high_priority_tasks = current_tasks.filter(priority__in=['high', 'urgent']).count()
            overdue_tasks = current_tasks.filter(due_date__lt=timezone.now()).count()
            
            # Get stress indicators
            stress_score = 0
            if profile.utilization_percentage > 100:
                stress_score += 30
            if profile.utilization_percentage > 85:
                stress_score += 20
            if overdue_tasks > 0:
                stress_score += overdue_tasks * 10
            if high_priority_tasks > 3:
                stress_score += (high_priority_tasks - 3) * 5
                
            team_workload.append({
                'username': user.username,
                'capacity_hours': profile.weekly_capacity_hours,
                'assigned_hours': total_hours,
                'utilization_percentage': profile.utilization_percentage,
                'available_hours': profile.available_hours,
                'active_tasks_count': current_tasks.count(),
                'high_priority_tasks': high_priority_tasks,
                'overdue_tasks': overdue_tasks,
                'stress_score': min(100, stress_score),  # Cap at 100
                'skills': profile.skill_names,
                'quality_score': profile.quality_score,
                'productivity_trend': profile.productivity_trend
            })
        
        # Identify tasks that could be redistributed
        redistributable_tasks = Task.objects.filter(
            column__board=board,
            assigned_to__isnull=False,
            progress__lt=25  # Tasks that haven't been started significantly
        ).exclude(column__name__icontains='done')
        
        task_redistribution_candidates = []
        for task in redistributable_tasks:
            task_redistribution_candidates.append({
                'id': task.id,
                'title': task.title,
                'current_assignee': task.assigned_to.username,
                'estimated_hours': task.estimated_duration_hours,
                'priority': task.priority,
                'required_skills': [skill.get('name', '') for skill in task.required_skills],
                'complexity': task.complexity_score,
                'progress': task.progress
            })
        
        prompt = f"""
        Analyze team workload and suggest optimal rebalancing strategies:
        
        ## Current Team Workload:
        {json.dumps(team_workload, indent=2)}
        
        ## Tasks Available for Redistribution:
        {json.dumps(task_redistribution_candidates, indent=2)}
        
        Analyze for:
        1. **Overload Risk**: Team members approaching burnout (>85% utilization)
        2. **Underutilization**: Team members with available capacity
        3. **Skill-Based Redistribution**: Better skill matches for existing assignments
        4. **Stress Balancing**: Distribute high-priority/complex tasks evenly
        5. **Development Opportunities**: Use workload balancing for skill growth
        
        Format response as JSON:
        {{
            "workload_health_score": 1-10,
            "imbalance_severity": "low|medium|high|critical",
            "overloaded_members": [
                {{
                    "username": "name",
                    "current_utilization": 95,
                    "stress_score": 75,
                    "recommended_reduction": 10,
                    "tasks_to_reassign": ["task titles"]
                }}
            ],
            "underutilized_members": [
                {{
                    "username": "name", 
                    "current_utilization": 45,
                    "available_capacity": 20,
                    "suitable_additional_tasks": ["task titles"],
                    "skill_development_opportunities": ["skills they could learn"]
                }}
            ],
            "redistribution_plan": [
                {{
                    "task_title": "title",
                    "from_user": "current assignee",
                    "to_user": "new assignee", 
                    "reasoning": "why this redistribution helps",
                    "skill_match_improvement": 15,
                    "workload_balance_impact": "description"
                }}
            ],
            "workload_balancing_strategies": [
                {{
                    "strategy": "pair_programming|task_splitting|skill_sharing|deadline_adjustment",
                    "description": "specific strategy description",
                    "affected_members": ["usernames"],
                    "expected_benefit": "what this achieves"
                }}
            ],
            "long_term_recommendations": ["suggestions for sustainable workload management"]
        }}
        """
        
        response = model.generate_content(prompt)
        if response:
            response_text = response.text.strip()
            
            # Handle code block formatting
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].strip()
                
            return json.loads(response_text)
        return None
        
    except Exception as e:
        logger.error(f"Error balancing team workload: {str(e)}")
        return None


def suggest_resource_reallocation(board_id: int) -> Optional[Dict]:
    """
    Suggest real-time resource reallocation based on current conditions.
    
    Args:
        board_id: ID of the board to analyze
        
    Returns:
        Dictionary with real-time reallocation suggestions
    """
    try:
        model = get_model()
        if not model:
            return None
            
        from kanban.models import Board
        board = Board.objects.get(id=board_id)
        
        # Get current state snapshot
        current_time = timezone.now()
        
        # Identify urgent situations
        urgent_tasks = Task.objects.filter(
            Q(due_date__lte=current_time + timedelta(days=2)) |  # Due within 2 days
            Q(priority='urgent'),
            column__board=board
        ).exclude(column__name__icontains='done')
        
        # Blocked or delayed tasks
        blocked_tasks = Task.objects.filter(
            Q(due_date__lt=current_time) |  # Overdue
            Q(progress=0, created_at__lte=current_time - timedelta(days=3)),  # Not started for 3+ days
            column__board=board
        ).exclude(column__name__icontains='done')
        
        # Team availability analysis
        team_availability = []
        board_members = list(board.members.all()) + [board.created_by]
        
        for user in set(board_members):
            if not hasattr(user, 'profile'):
                continue
                
            profile = user.profile
            current_tasks = Task.objects.filter(
                column__board=board,
                assigned_to=user
            ).exclude(column__name__icontains='done')
            
            # Immediate availability (next 3 days)
            immediate_workload = current_tasks.filter(
                due_date__lte=current_time + timedelta(days=3)
            )
            immediate_hours = sum([task.estimated_duration_hours for task in immediate_workload])
            
            team_availability.append({
                'username': user.username,
                'immediate_availability': max(0, (profile.weekly_capacity_hours / 7 * 3) - immediate_hours),
                'skills': profile.skill_names,
                'current_utilization': profile.utilization_percentage,
                'quality_score': profile.quality_score,
                'active_urgent_tasks': current_tasks.filter(priority='urgent').count(),
                'active_overdue_tasks': current_tasks.filter(due_date__lt=current_time).count()
            })
        
        # Format urgent and blocked tasks
        urgent_tasks_data = []
        for task in urgent_tasks:
            urgent_tasks_data.append({
                'id': task.id,
                'title': task.title,
                'assigned_to': task.assigned_to.username if task.assigned_to else None,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'priority': task.priority,
                'estimated_hours': task.estimated_duration_hours,
                'required_skills': [skill.get('name', '') for skill in task.required_skills]
            })
        
        blocked_tasks_data = []
        for task in blocked_tasks:
            blocked_tasks_data.append({
                'id': task.id,
                'title': task.title,
                'assigned_to': task.assigned_to.username if task.assigned_to else None,
                'days_overdue': (current_time.date() - task.due_date.date()).days if task.due_date else 0,
                'estimated_hours': task.estimated_duration_hours,
                'required_skills': [skill.get('name', '') for skill in task.required_skills]
            })
        
        prompt = f"""
        Analyze current resource situation and suggest immediate reallocation for optimal performance:
        
        ## Urgent Tasks Requiring Immediate Attention:
        {json.dumps(urgent_tasks_data, indent=2)}
        
        ## Blocked/Delayed Tasks:
        {json.dumps(blocked_tasks_data, indent=2)}
        
        ## Team Immediate Availability:
        {json.dumps(team_availability, indent=2)}
        
        Focus on:
        1. **Crisis Management**: Address urgent and overdue tasks first
        2. **Skill Matching**: Quick wins with optimal skill matches
        3. **Load Balancing**: Redistribute to prevent individual overload
        4. **Quality Assurance**: Don't compromise quality for speed
        5. **Collaboration**: Suggest pair work for complex urgent tasks
        
        Format response as JSON:
        {{
            "reallocation_urgency": "low|medium|high|critical",
            "immediate_actions_required": true/false,
            "crisis_tasks": [
                {{
                    "task_id": 0,
                    "task_title": "title",
                    "current_assignee": "username or null",
                    "action": "reassign|add_support|escalate",
                    "recommended_assignee": "username",
                    "support_team": ["additional usernames if needed"],
                    "reasoning": "why this action is urgent",
                    "time_sensitivity": "hours until critical"
                }}
            ],
            "immediate_reallocations": [
                {{
                    "from_user": "username",
                    "to_user": "username", 
                    "tasks_to_move": ["task titles"],
                    "reasoning": "why move these tasks",
                    "estimated_time_saved": "X hours",
                    "risk_mitigation": "what problems this prevents"
                }}
            ],
            "collaborative_assignments": [
                {{
                    "primary_assignee": "username",
                    "support_members": ["usernames"],
                    "task_title": "title",
                    "collaboration_type": "pair_programming|review_support|knowledge_sharing",
                    "expected_outcome": "faster completion and knowledge transfer"
                }}
            ],
            "preventive_measures": [
                {{
                    "issue": "what future problem to prevent",
                    "action": "specific preventive action",
                    "implementation_time": "when to do this"
                }}
            ],
            "performance_monitoring": [
                "key metrics to watch for next reallocation decisions"
            ]
        }}
        """
        
        response = model.generate_content(prompt)
        if response:
            response_text = response.text.strip()
            
            # Handle code block formatting
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].strip()
                
            return json.loads(response_text)
        return None
        
    except Exception as e:
        logger.error(f"Error suggesting resource reallocation: {str(e)}")
        return None
