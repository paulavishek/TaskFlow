#!/usr/bin/env python
"""
Demo script to showcase the AI enhancement features in TaskFlow.

This script sets up a sample board with realistic data to demonstrate
all five AI enhancement features.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

from django.contrib.auth.models import User
from kanban.models import Board, Column, Task, TaskLabel
from accounts.models import Organization

def create_demo_board():
    """Create a demo board with realistic project data."""
    print("🚀 Setting up TaskFlow AI Enhancement Demo")
    print("=" * 50)
    
    # Create demo user
    user, created = User.objects.get_or_create(
        username='demo_user',
        defaults={
            'email': 'demo@taskflow.com',
            'first_name': 'Demo',
            'last_name': 'User',
            'is_staff': True  # Allow access to admin
        }
    )
    
    if created:
        user.set_password('demo123')
        user.save()
        print(f"✓ Created demo user: {user.username} (password: demo123)")
    else:
        print(f"✓ Using existing demo user: {user.username}")
    
    # Create demo organization
    organization, created = Organization.objects.get_or_create(
        name='AI Demo Company',
        defaults={
            'created_by': user
        }
    )
    
    # Create demo board
    board, created = Board.objects.get_or_create(
        name='Mobile App Development Project',
        defaults={
            'description': 'Development of a cross-platform mobile application with real-time features',
            'created_by': user,
            'organization': organization
        }
    )
    
    if created:
        print(f"✓ Created demo board: {board.name}")
    else:
        print(f"✓ Using existing demo board: {board.name}")
    
    # Create columns
    columns_data = [
        ('Backlog', 0),
        ('To Do', 1),
        ('In Progress', 2),
        ('Code Review', 3),
        ('Testing', 4),
        ('Done', 5)
    ]
    
    for col_name, position in columns_data:
        column, created = Column.objects.get_or_create(
            name=col_name,
            board=board,
            defaults={'position': position}
        )
    
    print("✓ Created board columns")
    
    # Create realistic tasks
    tasks_data = [
        {
            'title': 'Design user authentication flow',
            'description': 'Create wireframes and user flow for login, registration, and password recovery',
            'priority': 'high',
            'column': 'To Do',
            'due_date': datetime.now() + timedelta(days=7)
        },
        {
            'title': 'Implement real-time chat feature',
            'description': 'Build WebSocket-based chat functionality with message persistence and notifications',
            'priority': 'medium',
            'column': 'In Progress',
            'due_date': datetime.now() + timedelta(days=14)
        },
        {
            'title': 'Optimize database queries for user dashboard',
            'description': 'Performance optimization for complex analytics queries causing slow load times',
            'priority': 'urgent',
            'column': 'Code Review',
            'due_date': datetime.now() + timedelta(days=2)
        },
        {
            'title': 'Create comprehensive API documentation',
            'description': 'Document all REST endpoints with examples, authentication, and error handling',
            'priority': 'low',
            'column': 'Backlog',
            'due_date': datetime.now() + timedelta(days=21)
        },
        {
            'title': 'Set up automated CI/CD pipeline',
            'description': 'Configure GitHub Actions for automated testing, building, and deployment',
            'priority': 'high',
            'column': 'Testing',
            'due_date': datetime.now() + timedelta(days=10)
        },
        {
            'title': 'Conduct user research interviews',
            'description': 'Interview 15 target users to validate product-market fit and gather feature feedback',
            'priority': 'medium',
            'column': 'Backlog',
            'due_date': datetime.now() + timedelta(days=30)
        },
        {
            'title': 'Integrate third-party payment processing',
            'description': 'Implement Stripe integration for subscription billing and one-time payments',
            'priority': 'high',
            'column': 'To Do',
            'due_date': datetime.now() + timedelta(days=12)
        },
        {
            'title': 'Launch comprehensive marketing campaign',
            'description': 'Multi-channel marketing campaign including social media, content marketing, and paid ads',
            'priority': 'medium',
            'column': 'Backlog',
            'due_date': datetime.now() + timedelta(days=45)
        }
    ]
    
    # Create additional team members
    team_members = [
        ('alice_dev', 'Alice', 'Developer'),
        ('bob_designer', 'Bob', 'Designer'),
        ('carol_qa', 'Carol', 'QA Engineer')
    ]
    
    created_users = []
    for username, first_name, last_name in team_members:
        team_user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@taskflow.com',
                'first_name': first_name,
                'last_name': last_name
            }
        )
        created_users.append(team_user)
        board.members.add(team_user)
    
    print(f"✓ Created {len(created_users)} team members")
    
    # Create tasks and assign to team members
    assignees = [user] + created_users
    
    for i, task_info in enumerate(tasks_data):
        column = Column.objects.get(name=task_info['column'], board=board)
        assignee = assignees[i % len(assignees)]
        
        task, created = Task.objects.get_or_create(
            title=task_info['title'],
            column=column,
            defaults={
                'description': task_info['description'],
                'priority': task_info['priority'],
                'created_by': user,
                'assigned_to': assignee,
                'due_date': task_info['due_date']
            }
        )
    
    print(f"✓ Created {len(tasks_data)} realistic tasks")
    
    # Create Lean Six Sigma labels
    lss_labels = [
        ('Value-Added', '#28a745', 'lean'),
        ('Necessary NVA', '#ffc107', 'lean'),
        ('Waste/Eliminate', '#dc3545', 'lean')
    ]
    
    for label_name, color, category in lss_labels:
        TaskLabel.objects.get_or_create(
            name=label_name,
            board=board,
            defaults={
                'color': color,
                'category': category
            }
        )
    
    print("✓ Created Lean Six Sigma labels")
    
    return board, user

def print_demo_instructions(board, user):
    """Print instructions for testing the AI features."""
    print("\n" + "🎯 AI ENHANCEMENT FEATURES DEMO" + "\n" + "=" * 50)
    print(f"Demo Board: {board.name}")
    print(f"Demo User: {user.username}")
    print(f"Board URL: http://localhost:8000/boards/{board.id}/")
    print(f"Analytics URL: http://localhost:8000/boards/{board.id}/analytics/")
    
    print("\n📋 FEATURES TO TEST:")
    print("\n1. 🧠 SMART TASK PRIORITIZATION")
    print("   • Go to the board and create a new task")
    print("   • Enter a title like 'Fix critical security vulnerability'")
    print("   • Click 'Suggest' next to Priority field")
    print("   • AI will analyze and suggest optimal priority")
    
    print("\n2. ⏰ INTELLIGENT DEADLINE PREDICTION")
    print("   • In the same task creation form")
    print("   • Click 'Predict' next to Due Date field")
    print("   • AI will suggest realistic deadline based on team context")
    
    print("\n3. 🎯 AUTOMATED TASK BREAKDOWN")
    print("   • Enter a complex task like 'Launch e-commerce platform'")
    print("   • Click 'Analyze & Break Down' in the complexity section")
    print("   • AI will suggest breaking it into manageable subtasks")
    
    print("\n4. 📊 WORKFLOW OPTIMIZATION")
    print("   • Go to Board Analytics page")
    print("   • Click 'Analyze Workflow' button")
    print("   • AI will identify bottlenecks and suggest improvements")
    
    print("\n5. 🏗️ SMART COLUMN RECOMMENDATIONS")
    print("   • Go to Board List page")
    print("   • Click 'New Board' button")
    print("   • Enter board details and select project type")
    print("   • Click 'Get AI Recommendations' for optimal columns")
    
    print("\n🔑 LOGIN CREDENTIALS:")
    print(f"   Username: {user.username}")
    print("   Password: demo123")
    
    print("\n🚀 START THE SERVER:")
    print("   python manage.py runserver")
    print("   Then visit: http://localhost:8000/")
    
    print("\n💡 TIPS:")
    print("   • Each AI feature provides reasoning for its suggestions")
    print("   • Try different task types to see varied AI responses")
    print("   • The more detailed your task descriptions, the better AI suggestions")
    print("   • AI responses may vary based on context and current board state")

def main():
    """Set up the demo environment."""
    try:
        board, user = create_demo_board()
        print_demo_instructions(board, user)
        
        print(f"\n✅ Demo setup completed successfully!")
        print(f"🕒 Setup completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Error setting up demo: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
