#!/usr/bin/env python
"""
Create a test board with sample data to test the AI Analytics feature
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

from django.contrib.auth.models import User
from kanban.models import Board, Column, Task, TaskLabel
from accounts.models import Organization, UserProfile
from datetime import datetime, timedelta
from django.utils import timezone

def create_test_data():
    """Create test data for AI analytics demonstration"""
    
    try:
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('adminpass123')
            admin_user.save()
            print("✅ Created admin user")
        else:
            print("✅ Admin user already exists")
        
        # Get or create organization
        org, created = Organization.objects.get_or_create(
            name='Test Organization',
            defaults={
                'domain': 'test.com',
                'created_by': admin_user
            }
        )
        
        if created:
            print("✅ Created test organization")
        else:
            print("✅ Test organization already exists")
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={'organization': org}
        )
        
        if created:
            print("✅ Created admin user profile")
        else:
            print("✅ Admin user profile already exists")
        
        # Create test board
        board, created = Board.objects.get_or_create(
            name='AI Analytics Test Board',
            defaults={
                'description': 'A sample board to demonstrate AI analytics features',
                'organization': org,
                'created_by': admin_user
            }
        )
        
        if created:
            board.members.add(admin_user)
            print("✅ Created test board")
        else:
            print("✅ Test board already exists")
        
        # Create columns
        columns_data = [
            ('To Do', 0),
            ('In Progress', 1),
            ('Review', 2),
            ('Done', 3)
        ]
        
        columns = []
        for name, position in columns_data:
            column, created = Column.objects.get_or_create(
                name=name,
                board=board,
                defaults={'position': position}
            )
            columns.append(column)
            if created:
                print(f"✅ Created column: {name}")
        
        # Create Lean Six Sigma labels
        lean_labels_data = [
            ('Value-Added', 'lean', '#28a745'),
            ('Necessary NVA', 'lean', '#ffc107'),
            ('Waste/Eliminate', 'lean', '#dc3545')
        ]
        
        for name, category, color in lean_labels_data:
            label, created = TaskLabel.objects.get_or_create(
                name=name,
                board=board,
                defaults={
                    'category': category,
                    'color': color
                }
            )
            if created:
                print(f"✅ Created lean label: {name}")
        
        # Create sample tasks
        tasks_data = [
            {
                'title': 'Implement user authentication system',
                'description': 'Create secure login and registration functionality',
                'column': 'Done',
                'priority': 'high',
                'progress': 100,
                'lean_label': 'Value-Added'
            },
            {
                'title': 'Set up database backup system',
                'description': 'Implement automated database backups',
                'column': 'Done',
                'priority': 'medium',
                'progress': 100,
                'lean_label': 'Necessary NVA'
            },
            {
                'title': 'Create dashboard analytics',
                'description': 'Build comprehensive analytics dashboard',
                'column': 'In Progress',
                'priority': 'high',
                'progress': 75,
                'lean_label': 'Value-Added'
            },
            {
                'title': 'Write API documentation',
                'description': 'Document all API endpoints',
                'column': 'To Do',
                'priority': 'low',
                'progress': 0,
                'lean_label': 'Necessary NVA'
            },
            {
                'title': 'Fix duplicate code issues',
                'description': 'Refactor and eliminate code duplication',
                'column': 'Review',
                'priority': 'medium',
                'progress': 90,
                'lean_label': 'Waste/Eliminate'
            },
            {
                'title': 'Implement user profile features',
                'description': 'Add profile picture and settings',
                'column': 'In Progress',
                'priority': 'medium',
                'progress': 50,
                'lean_label': 'Value-Added'
            },
            {
                'title': 'Update dependencies',
                'description': 'Update all project dependencies to latest versions',
                'column': 'To Do',
                'priority': 'low',
                'progress': 0,
                'lean_label': 'Necessary NVA',
                'due_date': timezone.now() + timedelta(days=2)
            },
            {
                'title': 'Remove unused legacy code',
                'description': 'Clean up old unused code files',
                'column': 'To Do',
                'priority': 'low',
                'progress': 0,
                'lean_label': 'Waste/Eliminate',
                'due_date': timezone.now() - timedelta(days=1)  # Overdue
            }
        ]
        
        for task_data in tasks_data:
            column = next(c for c in columns if c.name == task_data['column'])
            
            task, created = Task.objects.get_or_create(
                title=task_data['title'],
                column=column,
                defaults={
                    'description': task_data['description'],
                    'priority': task_data['priority'],
                    'progress': task_data['progress'],
                    'created_by': admin_user,
                    'assigned_to': admin_user,
                    'due_date': task_data.get('due_date')
                }
            )
            
            if created:
                # Add lean label
                lean_label = TaskLabel.objects.get(
                    name=task_data['lean_label'],
                    board=board
                )
                task.labels.add(lean_label)
                print(f"✅ Created task: {task_data['title']}")
        
        print(f"\n🎉 Test data created successfully!")
        print(f"Board ID: {board.id}")
        print(f"Board Name: {board.name}")
        print(f"Total Tasks: {Task.objects.filter(column__board=board).count()}")
        print(f"You can now test the AI Analytics feature at:")
        print(f"http://127.0.0.1:8000/board/{board.id}/analytics/")
        
        return board.id
        
    except Exception as e:
        print(f"❌ Error creating test data: {str(e)}")
        return None

if __name__ == "__main__":
    print("🚀 Creating test data for AI Analytics...")
    print("="*50)
    board_id = create_test_data()
    print("="*50)
