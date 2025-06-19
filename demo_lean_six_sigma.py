#!/usr/bin/env python
"""
Demo script to create sample data for Lean Six Sigma visualization
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

from django.contrib.auth.models import User
from kanban.models import Board, Column, Task, TaskLabel
from accounts.models import Organization, UserProfile

def create_demo_data():
    """Create demo data for Lean Six Sigma analytics"""
    
    # Get or create a demo user
    user, created = User.objects.get_or_create(
        username='demo_user',
        defaults={
            'email': 'demo@example.com',
            'first_name': 'Demo',
            'last_name': 'User'
        }
    )
    
    # Create or get demo organization
    organization, created = Organization.objects.get_or_create(
        name='Demo Organization',
        defaults={
            'domain': 'demo.com',
            'created_by': user
        }
    )
    
    # Create or get user profile
    user_profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'organization': organization,
            'is_admin': True
        }
    )
    
    # Create or get demo board
    board, created = Board.objects.get_or_create(
        name='Lean Six Sigma Demo Board',
        defaults={
            'created_by': user, 
            'description': 'Demo board showcasing Lean Six Sigma features',
            'organization': organization
        }
    )
      # Create columns if they don't exist
    columns = ['To Do', 'In Progress', 'Review', 'Done']
    column_objects = []
    for i, col_name in enumerate(columns):
        column, created = Column.objects.get_or_create(
            board=board,
            name=col_name,
            defaults={'position': i}
        )
        column_objects.append(column)
    
    # Create Lean Six Sigma labels
    lean_labels = [
        {'name': 'Value-Added', 'color': '#28a745', 'category': 'lean'},
        {'name': 'Necessary NVA', 'color': '#ffc107', 'category': 'lean'},
        {'name': 'Waste/Eliminate', 'color': '#dc3545', 'category': 'lean'},
    ]
    
    label_objects = []
    for label_data in lean_labels:
        label, created = TaskLabel.objects.get_or_create(
            board=board,
            name=label_data['name'],
            defaults={
                'color': label_data['color'],
                'category': label_data['category']
            }
        )
        label_objects.append(label)
    
    # Create sample tasks with different Lean Six Sigma categories
    sample_tasks = [
        # Value-Added tasks (10 tasks)
        {'title': 'Develop core product feature', 'column': 0, 'label': 0, 'progress': 75},
        {'title': 'Customer requirement analysis', 'column': 1, 'label': 0, 'progress': 60},
        {'title': 'Product testing and validation', 'column': 1, 'label': 0, 'progress': 45},
        {'title': 'User interface design', 'column': 0, 'label': 0, 'progress': 30},
        {'title': 'Database optimization', 'column': 2, 'label': 0, 'progress': 90},
        {'title': 'API development', 'column': 1, 'label': 0, 'progress': 55},
        {'title': 'Performance improvements', 'column': 0, 'label': 0, 'progress': 20},
        {'title': 'Customer feedback integration', 'column': 3, 'label': 0, 'progress': 100},
        {'title': 'Security enhancements', 'column': 2, 'label': 0, 'progress': 80},
        {'title': 'Mobile responsiveness', 'column': 1, 'label': 0, 'progress': 65},
        
        # Necessary NVA tasks (7 tasks)
        {'title': 'Compliance documentation', 'column': 0, 'label': 1, 'progress': 25},
        {'title': 'Regulatory approval process', 'column': 1, 'label': 1, 'progress': 40},
        {'title': 'Legal review of contracts', 'column': 0, 'label': 1, 'progress': 15},
        {'title': 'Financial audit preparation', 'column': 2, 'label': 1, 'progress': 70},
        {'title': 'Tax compliance filing', 'column': 3, 'label': 1, 'progress': 100},
        {'title': 'Insurance policy review', 'column': 1, 'label': 1, 'progress': 35},
        {'title': 'Vendor compliance check', 'column': 0, 'label': 1, 'progress': 10},
        
        # Waste/Eliminate tasks (2 tasks)
        {'title': 'Redundant status meetings', 'column': 0, 'label': 2, 'progress': 5},
        {'title': 'Manual data entry process', 'column': 1, 'label': 2, 'progress': 20},
    ]
    
    # Clear existing demo tasks first
    Task.objects.filter(column__board=board).delete()
    
    # Create the new tasks
    for task_data in sample_tasks:
        task = Task.objects.create(
            title=task_data['title'],
            description=f"Demo task for {lean_labels[task_data['label']]['name']} category",
            column=column_objects[task_data['column']],
            created_by=user,
            progress=task_data['progress']
        )
        task.labels.add(label_objects[task_data['label']])
    
    print(f"✅ Created demo board '{board.name}' with:")
    print(f"   📊 {len(sample_tasks)} tasks total")
    print(f"   ✅ {len([t for t in sample_tasks if t['label'] == 0])} Value-Added tasks (52.6%)")
    print(f"   ⚠️  {len([t for t in sample_tasks if t['label'] == 1])} Necessary NVA tasks (36.8%)")
    print(f"   ❌ {len([t for t in sample_tasks if t['label'] == 2])} Waste tasks (10.5%)")
    print(f"   🎯 Value-Added percentage: 52.6%")
    print(f"\n🌐 Access the analytics at: http://127.0.0.1:8000/boards/{board.id}/analytics/")
    
    return board

if __name__ == "__main__":
    board = create_demo_data()
