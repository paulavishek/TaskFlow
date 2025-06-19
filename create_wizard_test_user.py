#!/usr/bin/env python
"""
Create a test user to demonstrate the Getting Started Wizard
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Organization, UserProfile

def create_test_user():
    """Create a test user without completing the wizard"""
    print("🧪 Creating test user for Getting Started Wizard demo")
    print("=" * 60)
    
    # Create organization
    org, created = Organization.objects.get_or_create(
        name='Test Company',
        defaults={
            'domain': 'testcompany.com',
            'created_by': User.objects.filter(is_superuser=True).first() or User.objects.first()
        }
    )
    
    if created:
        print(f"✅ Created organization: {org.name}")
    else:
        print(f"✅ Using existing organization: {org.name}")
    
    # Create test user
    username = 'newuser'
    password = 'testpass123'
    
    # Delete existing user if exists
    User.objects.filter(username=username).delete()
    
    user = User.objects.create_user(
        username=username,
        email=f'{username}@{org.domain}',
        password=password,
        first_name='New',
        last_name='User'
    )
    
    # Create user profile without completing wizard
    UserProfile.objects.create(
        user=user,
        organization=org,
        is_admin=False,
        completed_wizard=False  # This is the key - wizard not completed
    )
    
    print(f"✅ Created test user: {username}")
    print(f"✅ Password: {password}")
    print(f"✅ Email: {user.email}")
    print(f"✅ Wizard completed: No")
    
    print("\n" + "=" * 60)
    print("🎯 Test the Getting Started Wizard:")
    print("1. Go to: http://127.0.0.1:8000/accounts/login/")
    print(f"2. Login with: {username} / {password}")
    print("3. You should be redirected to the Getting Started Wizard!")
    print("4. Follow the wizard to create your first board and task")
    print("=" * 60)
    
    return user

def reset_existing_user_wizard():
    """Reset wizard for an existing user"""
    print("\n🔄 Reset wizard for existing users:")
    print("-" * 40)
    
    # Show users who can have their wizard reset
    users_with_profiles = User.objects.filter(profile__isnull=False)
    
    for user in users_with_profiles:
        profile = user.profile
        print(f"User: {user.username} (wizard completed: {profile.completed_wizard})")
        
        # Reset wizard for demonstration
        if profile.completed_wizard:
            profile.completed_wizard = False
            profile.wizard_completed_at = None
            profile.save()
            print(f"  ↻ Reset wizard for {user.username}")
    
    print("-" * 40)

if __name__ == "__main__":
    test_user = create_test_user()
    reset_existing_user_wizard()
    
    print("\n🚀 Ready to test the Getting Started Wizard!")
    print("Visit the login page and use the credentials above.")
