#!/usr/bin/env python
"""
Demo script to create a test user and show the improved Lean Six Sigma visualization
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

from django.contrib.auth.models import User
from kanban.models import Board, Column, Task, TaskLabel
from accounts.models import Organization, UserProfile

def create_test_user():
    """Create a test user for easy login"""
    
    # Create test user
    username = 'testuser'
    password = 'testpass123'
    email = 'test@demo.com'
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        print(f"✅ Test user '{username}' already exists")
    else:
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name='Test',
            last_name='User'
        )
        print(f"✅ Created test user '{username}' with password '{password}'")
    
    # Ensure user has an organization and profile
    if not hasattr(user, 'profile'):
        # Create organization if needed
        org, created = Organization.objects.get_or_create(
            name='Test Organization',
            defaults={
                'domain': 'test.com',
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
        print(f"✅ Created user profile and organization")
    
    # Get the demo board
    try:
        board = Board.objects.get(name='Lean Six Sigma Demo Board')
        print(f"✅ Found demo board: {board.name}")
        print(f"   📊 URL: http://127.0.0.1:8000/boards/{board.id}/analytics/")
        
        # Add user to board members if not already
        if user not in board.members.all() and board.created_by != user:
            board.members.add(user)
            print(f"✅ Added test user to board members")
            
    except Board.DoesNotExist:
        print("❌ Demo board not found. Run demo_lean_six_sigma.py first.")
        return None
    
    print(f"\n🔑 Login credentials:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"\n🌐 Access the enhanced LSS analytics at:")
    print(f"   http://127.0.0.1:8000/accounts/login/")
    print(f"   Then go to: http://127.0.0.1:8000/boards/{board.id}/analytics/")
    
    return user, board

if __name__ == "__main__":
    create_test_user()
