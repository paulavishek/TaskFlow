#!/usr/bin/env python
"""
Create a test user for testing the workflow optimization feature
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Organization, UserProfile
from kanban.models import Board, Column, Task

def create_test_user():
    """Create a test user with test data"""
    print("🔧 Creating test user for workflow optimization testing...")
    
    # Create or get test user
    username = "workflowtest"
    password = "test123456"
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': 'workflowtest@example.com',
            'first_name': 'Workflow',
            'last_name': 'Test'
        }
    )
    
    if created:
        user.set_password(password)
        user.save()
        print(f"✅ Created user: {username}")
    else:
        # Update password in case it changed
        user.set_password(password)
        user.save()
        print(f"✅ Updated user: {username}")
    
    # Create organization
    org, created = Organization.objects.get_or_create(
        name="Workflow Test Organization",
        defaults={
            'domain': 'workflowtest.com',
            'created_by': user
        }
    )
    
    # Create user profile
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'organization': org,
            'is_admin': True
        }
    )
    
    # Create test board with tasks
    board, created = Board.objects.get_or_create(
        name="Workflow Test Board",
        defaults={
            'organization': org,
            'created_by': user,
            'description': 'Test board for workflow optimization'
        }
    )
    board.members.add(user)
    
    # Create columns
    Column.objects.filter(board=board).delete()  # Clean slate
    
    todo_col = Column.objects.create(name='To Do', board=board, position=0)
    progress_col = Column.objects.create(name='In Progress', board=board, position=1)
    review_col = Column.objects.create(name='Review', board=board, position=2)  
    done_col = Column.objects.create(name='Done', board=board, position=3)
    
    # Create test tasks
    Task.objects.filter(column__board=board).delete()  # Clean slate
    
    # Create tasks with different priorities and statuses
    test_tasks = [
        # To Do tasks (creating bottleneck)
        {'title': 'Design Landing Page', 'column': todo_col, 'priority': 'high'},
        {'title': 'Set Up Analytics', 'column': todo_col, 'priority': 'medium'},
        {'title': 'Write Unit Tests', 'column': todo_col, 'priority': 'low'},
        {'title': 'Create User Documentation', 'column': todo_col, 'priority': 'medium'},
        {'title': 'Optimize Database Queries', 'column': todo_col, 'priority': 'high'},
        {'title': 'Set Up CI/CD Pipeline', 'column': todo_col, 'priority': 'low'},
        
        # In Progress tasks
        {'title': 'Implement User Authentication', 'column': progress_col, 'priority': 'high'},
        {'title': 'Build REST API', 'column': progress_col, 'priority': 'medium'},
        
        # Review tasks (creating bottleneck)
        {'title': 'Code Review for Login Feature', 'column': review_col, 'priority': 'high'},
        {'title': 'Security Audit', 'column': review_col, 'priority': 'high'},
        {'title': 'Performance Testing', 'column': review_col, 'priority': 'medium'},
        
        # Done tasks  
        {'title': 'Project Setup', 'column': done_col, 'priority': 'high'},
        {'title': 'Database Design', 'column': done_col, 'priority': 'medium'},
    ]
    
    for i, task_data in enumerate(test_tasks):
        Task.objects.create(
            title=task_data['title'],
            description=f"Test task: {task_data['title']}",
            column=task_data['column'],
            priority=task_data['priority'],
            created_by=user,
            assigned_to=user,
            position=i
        )
    
    print(f"✅ Created test board '{board.name}' with {len(test_tasks)} tasks")
    print(f"   📋 Board ID: {board.id}")
    print(f"   📊 Task distribution:")
    print(f"      • To Do: {Task.objects.filter(column=todo_col).count()} tasks")
    print(f"      • In Progress: {Task.objects.filter(column=progress_col).count()} tasks") 
    print(f"      • Review: {Task.objects.filter(column=review_col).count()} tasks")
    print(f"      • Done: {Task.objects.filter(column=done_col).count()} tasks")
    
    print("\n🎯 Test User Credentials:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"\n🌐 Test URLs:")
    print(f"   Login: http://127.0.0.1:8000/accounts/login/")
    print(f"   Board: http://127.0.0.1:8000/boards/{board.id}/")
    print(f"   Analytics: http://127.0.0.1:8000/boards/{board.id}/analytics/")
    
    return user, board

if __name__ == "__main__":
    create_test_user()
    print("\n✅ Test user and data created successfully!")
    print("You can now:")
    print("1. Log in with the credentials above")
    print("2. Go to the analytics page") 
    print("3. Test the 'Analyze Workflow' button")
