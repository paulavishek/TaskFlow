# kanban/utils/dependency_suggestions.py
"""
AI-powered task dependency analysis and suggestion engine
Analyzes task descriptions to suggest parent-child relationships and task dependencies
"""

import json
import logging
from typing import List, Dict, Optional
from django.utils import timezone
from kanban.models import Task

logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    """
    Analyzes task descriptions to suggest dependencies
    Uses NLP and keyword matching to find related tasks
    """
    
    # Keywords that indicate parent-child relationships
    PARENT_KEYWORDS = ['implement', 'setup', 'configure', 'initialize', 'design', 'architect', 'plan']
    CHILD_KEYWORDS = ['test', 'validate', 'verify', 'debug', 'fix', 'optimize', 'refactor']
    DEPENDENCY_KEYWORDS = ['requires', 'depends on', 'after', 'once', 'following', 'completion']
    BLOCKING_KEYWORDS = ['blocks', 'blocked by', 'waiting for', 'pending']
    
    @staticmethod
    def analyze_task_description(task: Task, board=None) -> Dict:
        """
        Analyze a task's description to suggest dependencies
        
        Args:
            task: The Task object to analyze
            board: Optional board to limit search scope
            
        Returns:
            Dictionary with suggested dependencies and confidence scores
        """
        if not task.description:
            return {
                'parent_suggestions': [],
                'related_suggestions': [],
                'blocking_suggestions': [],
                'confidence': 0,
                'analysis': 'No description provided for analysis'
            }
        
        try:
            # Tokenize and prepare text
            description_lower = task.description.lower()
            
            # Find similar tasks in the same column or board
            if board:
                other_tasks = Task.objects.filter(column__board=board).exclude(id=task.id)
            else:
                other_tasks = Task.objects.filter(column=task.column).exclude(id=task.id)
            
            parent_suggestions = []
            related_suggestions = []
            blocking_suggestions = []
            
            # Analyze each other task
            for other_task in other_tasks:
                if not other_task.description:
                    continue
                
                other_desc_lower = other_task.description.lower()
                
                # Check for parent-child relationships
                parent_score = DependencyAnalyzer._calculate_parent_relationship_score(
                    description_lower, other_desc_lower, task, other_task
                )
                
                if parent_score > 0.5:
                    parent_suggestions.append({
                        'task_id': other_task.id,
                        'task_title': other_task.title,
                        'confidence': round(parent_score, 2),
                        'reason': 'Task appears to be a prerequisite'
                    })
                
                # Check for related tasks
                related_score = DependencyAnalyzer._calculate_relatedness_score(
                    description_lower, other_desc_lower
                )
                
                if related_score > 0.6:
                    related_suggestions.append({
                        'task_id': other_task.id,
                        'task_title': other_task.title,
                        'confidence': round(related_score, 2),
                        'reason': 'Tasks share similar context or requirements'
                    })
                
                # Check for blocking relationships
                blocking_score = DependencyAnalyzer._calculate_blocking_score(
                    description_lower, other_desc_lower
                )
                
                if blocking_score > 0.6:
                    blocking_suggestions.append({
                        'task_id': other_task.id,
                        'task_title': other_task.title,
                        'confidence': round(blocking_score, 2),
                        'reason': 'This task may be blocked by or block the other task'
                    })
            
            # Sort by confidence and limit results
            parent_suggestions.sort(key=lambda x: x['confidence'], reverse=True)
            related_suggestions.sort(key=lambda x: x['confidence'], reverse=True)
            blocking_suggestions.sort(key=lambda x: x['confidence'], reverse=True)
            
            overall_confidence = max(
                [s['confidence'] for s in parent_suggestions] +
                [s['confidence'] for s in related_suggestions] +
                [s['confidence'] for s in blocking_suggestions] +
                [0]
            )
            
            return {
                'parent_suggestions': parent_suggestions[:3],  # Top 3 suggestions
                'related_suggestions': related_suggestions[:3],
                'blocking_suggestions': blocking_suggestions[:3],
                'confidence': round(overall_confidence, 2),
                'analysis': f"Found {len(parent_suggestions)} potential parent tasks, "
                          f"{len(related_suggestions)} related tasks, and "
                          f"{len(blocking_suggestions)} potentially blocking tasks"
            }
        
        except Exception as e:
            logger.error(f"Error analyzing task dependencies: {str(e)}")
            return {
                'parent_suggestions': [],
                'related_suggestions': [],
                'blocking_suggestions': [],
                'confidence': 0,
                'analysis': f'Error during analysis: {str(e)}'
            }
    
    @staticmethod
    def _calculate_parent_relationship_score(desc1: str, desc2: str, task1: Task, task2: Task) -> float:
        """Calculate probability that task2 is a parent of task1"""
        score = 0
        
        # Check if desc1 contains parent keywords and desc2 contains child keywords
        task1_has_child_keywords = any(keyword in desc1 for keyword in DependencyAnalyzer.CHILD_KEYWORDS)
        task2_has_parent_keywords = any(keyword in desc2 for keyword in DependencyAnalyzer.PARENT_KEYWORDS)
        
        if task1_has_child_keywords and task2_has_parent_keywords:
            score += 0.4
        
        # Check for explicit dependency mentions
        for keyword in DependencyAnalyzer.DEPENDENCY_KEYWORDS:
            if keyword in desc1 and task2.title.lower() in desc1:
                score += 0.3
        
        # Check column position (earlier columns might indicate parent tasks)
        if task2.column and task1.column:
            if task2.column.position < task1.column.position:
                score += 0.2
        
        return min(score, 1.0)
    
    @staticmethod
    def _calculate_relatedness_score(desc1: str, desc2: str) -> float:
        """Calculate how related two tasks are based on descriptions"""
        score = 0
        
        # Simple word overlap scoring
        words1 = set(desc1.split())
        words2 = set(desc2.split())
        
        if len(words1) > 0 and len(words2) > 0:
            overlap = len(words1.intersection(words2))
            total = len(words1.union(words2))
            score = overlap / total if total > 0 else 0
        
        return score
    
    @staticmethod
    def _calculate_blocking_score(desc1: str, desc2: str) -> float:
        """Calculate if one task blocks the other"""
        score = 0
        
        # Check for explicit blocking keywords
        for keyword in DependencyAnalyzer.BLOCKING_KEYWORDS:
            if keyword in desc1:
                score += 0.3
        
        return min(score, 1.0)


class DependencyGraphGenerator:
    """
    Generates visual dependency graphs and trees from task relationships
    """
    
    @staticmethod
    def generate_dependency_tree(task: Task, include_subtasks: bool = True, 
                                include_related: bool = False) -> Dict:
        """
        Generate a tree structure representing task dependencies
        
        Args:
            task: Root task to generate tree from
            include_subtasks: Include child tasks in tree
            include_related: Include related tasks
            
        Returns:
            Dictionary representing the dependency tree
        """
        tree_node = {
            'id': task.id,
            'title': task.title,
            'description': task.description[:100] if task.description else '',
            'status': task.column.name if task.column else 'Unknown',
            'assigned_to': task.assigned_to.username if task.assigned_to else 'Unassigned',
            'priority': task.priority,
            'level': task.get_dependency_level(),
            'children': [],
            'related': [],
            'parent': None
        }
        
        # Add parent reference
        if task.parent_task:
            tree_node['parent'] = {
                'id': task.parent_task.id,
                'title': task.parent_task.title
            }
        
        # Add subtasks
        if include_subtasks:
            for subtask in task.subtasks.all():
                tree_node['children'].append(
                    DependencyGraphGenerator.generate_dependency_tree(subtask, include_subtasks, include_related)
                )
        
        # Add related tasks
        if include_related:
            for related in task.related_tasks.all():
                tree_node['related'].append({
                    'id': related.id,
                    'title': related.title
                })
        
        return tree_node
    
    @staticmethod
    def generate_dependency_graph(board, root_task_id: Optional[int] = None) -> Dict:
        """
        Generate a full dependency graph for visualization
        
        Args:
            board: Board to generate graph from
            root_task_id: Optional specific task to focus on
            
        Returns:
            Dictionary representing the full dependency graph
        """
        nodes = []
        edges = []
        
        tasks = Task.objects.filter(column__board=board)
        
        # Create nodes
        for task in tasks:
            nodes.append({
                'id': task.id,
                'label': f"{task.title[:30]}...",
                'full_title': task.title,
                'priority': task.priority,
                'status': task.column.name if task.column else 'Unknown',
                'level': task.get_dependency_level()
            })
        
        # Create edges for parent-child relationships
        for task in tasks:
            if task.parent_task:
                edges.append({
                    'from': task.parent_task.id,
                    'to': task.id,
                    'type': 'parent-child'
                })
            
            # Add related task edges
            for related in task.related_tasks.all():
                edges.append({
                    'from': task.id,
                    'to': related.id,
                    'type': 'related'
                })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'root_id': root_task_id
        }


def analyze_and_suggest_dependencies(task: Task, board=None, auto_link: bool = False) -> Dict:
    """
    Main entry point for dependency analysis
    
    Args:
        task: Task to analyze
        board: Board context (optional)
        auto_link: Whether to automatically create links to top suggestions
        
    Returns:
        Analysis result with suggestions
    """
    analyzer = DependencyAnalyzer()
    result = analyzer.analyze_task_description(task, board)
    
    # Store suggestions on task
    task.suggested_dependencies = {
        'analysis_timestamp': timezone.now().isoformat(),
        'suggestions': result
    }
    task.last_dependency_analysis = timezone.now()
    
    # Optionally auto-link top parent suggestion
    if auto_link and result['parent_suggestions']:
        top_parent = result['parent_suggestions'][0]
        if top_parent['confidence'] > 0.7:
            try:
                parent_task = Task.objects.get(id=top_parent['task_id'])
                if not task.has_circular_dependency(parent_task):
                    task.parent_task = parent_task
            except Task.DoesNotExist:
                logger.warning(f"Suggested parent task {top_parent['task_id']} not found")
    
    task.save()
    return result
