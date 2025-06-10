"""
TaskFlow Data Population Script
--------------------------------
This script populates the database with test data for manually testing all features
including the AI-powered features.
"""
import os
import sys
import django
from django.utils import timezone
from datetime import timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

# Import models
from django.contrib.auth.models import User
from accounts.models import Organization, UserProfile
from kanban.models import Board, Column, TaskLabel, Task, Comment, TaskActivity

def main():
    print("Starting to populate the database with test data for all features...")
    
    # Run the existing populate_test_data management command
    print("Running Django management command: populate_test_data")
    os.system('python manage.py populate_test_data')
    
    # Add additional data for AI features testing
    print("\nAdding additional test data for AI features...\n")
    
    # Get users
    try:
        admin_user = User.objects.get(username='admin')
        john_doe = User.objects.get(username='john_doe')
        jane_smith = User.objects.get(username='jane_smith')
        robert_johnson = User.objects.get(username='robert_johnson')
        print("Retrieved users successfully")
    except User.DoesNotExist:
        print("Error: Required users don't exist. Make sure populate_test_data command ran successfully.")
        return
    
    # Get the Software Project board
    try:
        software_board = Board.objects.get(name='Software Project')
        print(f"Retrieved board: {software_board.name}")
    except Board.DoesNotExist:
        print("Error: Software Project board doesn't exist.")
        return
    
    # Get columns
    try:
        backlog_column = Column.objects.get(name='Backlog', board=software_board)
        todo_column = Column.objects.get(name='To Do', board=software_board)
        in_progress_column = Column.objects.get(name='In Progress', board=software_board)
        review_column = Column.objects.get(name='Review', board=software_board)
        done_column = Column.objects.get(name='Done', board=software_board)
        print("Retrieved columns successfully")
    except Column.DoesNotExist:
        print("Error: Required columns don't exist.")
        return
    
    # Get lean labels
    try:
        value_added_label = TaskLabel.objects.get(name='Value-Added', board=software_board)
        necessary_nva_label = TaskLabel.objects.get(name='Necessary NVA', board=software_board)
        waste_label = TaskLabel.objects.get(name='Waste/Eliminate', board=software_board)
        print("Retrieved Lean Six Sigma labels successfully")
    except TaskLabel.DoesNotExist:
        print("Error: Required labels don't exist.")
        return
    
    # Create tasks with multiple comments for testing the comment summarization feature
    task_with_comments = Task.objects.create(
        title='Implement AI-powered task recommendations',
        description='Build a machine learning system that suggests tasks to users based on their work patterns and priorities',
        priority='high',
        due_date=timezone.now() + timedelta(days=10),
        column=in_progress_column,
        created_by=admin_user,
        assigned_to=john_doe,
        progress=30
    )
    task_with_comments.labels.add(value_added_label)
    print(f"Created task for testing comment summarization: {task_with_comments.title}")
    
    # Create multiple comments on this task
    comments = [
        {
            'content': 'I\'ve started researching machine learning models for task recommendation systems. Looking at collaborative filtering approaches.',
            'user': john_doe,
            'days_ago': 5
        },
        {
            'content': 'Make sure to consider the cold start problem. New users won\'t have enough historical data.',
            'user': robert_johnson,
            'days_ago': 4
        },
        {
            'content': 'Good point, Robert. I\'m thinking of using a hybrid approach that combines content-based and collaborative filtering.',
            'user': john_doe,
            'days_ago': 4
        },
        {
            'content': 'I\'ve analyzed our database structure. We\'ll need to track user interactions more closely to get useful input data.',
            'user': john_doe,
            'days_ago': 3
        },
        {
            'content': 'The recommendation algorithm should prioritize high-value tasks based on our LSS classification.',
            'user': admin_user,
            'days_ago': 2
        },
        {
            'content': 'I agree with the LSS prioritization. Also, I\'ve completed the data collection module. Moving on to the model training part now.',
            'user': john_doe, 
            'days_ago': 1
        },
        {
            'content': 'We need to schedule a review meeting next week to evaluate the initial model results.',
            'user': robert_johnson,
            'days_ago': 1
        }
    ]
    
    for comment_data in comments:
        created_at = timezone.now() - timedelta(days=comment_data['days_ago'])
        comment = Comment.objects.create(
            task=task_with_comments,
            user=comment_data['user'],
            content=comment_data['content'],
        )
        # Update the created_at time (need to do it separately due to auto_now_add=True)
        Comment.objects.filter(id=comment.id).update(created_at=created_at)
        print(f"Added comment from {comment_data['user'].username} ({comment_data['days_ago']} days ago)")
    
    # Create tasks for testing the task description generation
    tasks_for_description_generation = [
        {
            'title': 'Optimize database queries',
            'column': todo_column,
            'priority': 'medium',
            'created_by': admin_user,
            'assigned_to': robert_johnson,
            'labels': [necessary_nva_label]
        },
        {
            'title': 'Implement user onboarding tutorial',
            'column': backlog_column,
            'priority': 'low',
            'created_by': john_doe,
            'assigned_to': jane_smith,
            'labels': [value_added_label]
        },
        {
            'title': 'Refactor authentication middleware',
            'column': todo_column,
            'priority': 'high',
            'created_by': robert_johnson,
            'assigned_to': robert_johnson,
            'labels': [necessary_nva_label]
        }
    ]
    
    for task_data in tasks_for_description_generation:
        task = Task.objects.create(
            title=task_data['title'],
            column=task_data['column'],
            priority=task_data['priority'],
            created_by=task_data['created_by'],
            assigned_to=task_data['assigned_to']
        )
        for label in task_data['labels']:
            task.labels.add(label)
        print(f"Created task for testing description generation: {task.title}")
    
    # Create tasks for testing the lean classification
    tasks_for_lean_classification = [
        {
            'title': 'Create automated deployment pipeline',
            'description': 'Set up CI/CD pipeline to automate the testing and deployment process',
            'column': todo_column,
            'priority': 'high',
            'created_by': admin_user,
            'assigned_to': robert_johnson
        },
        {
            'title': 'Conduct usability testing sessions',
            'description': 'Schedule and run usability tests with real users to identify UX improvements',
            'column': backlog_column,
            'priority': 'medium',
            'created_by': jane_smith,
            'assigned_to': jane_smith
        },
        {
            'title': 'Update outdated documentation',
            'description': 'Review and update all technical documentation to reflect recent changes',
            'column': todo_column,
            'priority': 'low',
            'created_by': robert_johnson,
            'assigned_to': john_doe
        },
        {
            'title': 'Fix flaky integration tests',
            'description': 'Identify and fix integration tests that are producing inconsistent results',
            'column': in_progress_column,
            'priority': 'medium',
            'created_by': robert_johnson,
            'assigned_to': robert_johnson
        }
    ]
    
    for task_data in tasks_for_lean_classification:
        task = Task.objects.create(
            title=task_data['title'],
            description=task_data['description'],
            column=task_data['column'],
            priority=task_data['priority'],
            created_by=task_data['created_by'],
            assigned_to=task_data['assigned_to']
        )
        print(f"Created task for testing lean classification: {task.title}")
    
    # Create completed tasks with various progress levels for analytics insights
    completed_tasks = [
        {
            'title': 'Implement login and authentication',
            'description': 'Create secure authentication system with login, logout and password reset',
            'column': done_column,
            'priority': 'high',
            'progress': 100,
            'created_by': admin_user,
            'assigned_to': robert_johnson,
            'labels': [value_added_label],
            'days_ago': 15
        },
        {
            'title': 'Design database schema',
            'description': 'Create database models and relationships for the application',
            'column': done_column,
            'priority': 'urgent',
            'progress': 100,
            'created_by': admin_user,
            'assigned_to': john_doe,
            'labels': [value_added_label],
            'days_ago': 20
        },
        {
            'title': 'Setup development environment',
            'description': 'Configure Docker containers for consistent development environment',
            'column': done_column,
            'priority': 'medium',
            'progress': 100,
            'created_by': robert_johnson,
            'assigned_to': robert_johnson,
            'labels': [necessary_nva_label],
            'days_ago': 25
        },
        {
            'title': 'Remove deprecated API endpoints',
            'description': 'Clean up old API endpoints that are no longer in use',
            'column': done_column,
            'priority': 'low',
            'progress': 100,
            'created_by': robert_johnson,
            'assigned_to': robert_johnson,
            'labels': [waste_label],
            'days_ago': 10
        }
    ]
    
    for task_data in completed_tasks:
        created_at = timezone.now() - timedelta(days=task_data['days_ago'])
        task = Task.objects.create(
            title=task_data['title'],
            description=task_data['description'],
            column=task_data['column'],
            priority=task_data['priority'],
            progress=task_data['progress'],
            created_by=task_data['created_by'],
            assigned_to=task_data['assigned_to']
        )
        # Update created_at time
        Task.objects.filter(id=task.id).update(created_at=created_at)
        
        for label in task_data['labels']:
            task.labels.add(label)
        
        # Add activity for moving to done
        TaskActivity.objects.create(
            task=task,
            user=task_data['assigned_to'],
            activity_type='moved',
            description=f'Task moved to Done column'
        )
        print(f"Created completed task for analytics testing: {task.title}")
    
    print("\nDatabase has been populated with test data for all features!")
    print("You can now log in with the following credentials:")
    print("Username: admin, Password: admin123")
    print("Username: john_doe, Password: test1234")
    print("Username: jane_smith, Password: test1234")
    print("Username: robert_johnson, Password: test1234")

if __name__ == "__main__":
    main()
