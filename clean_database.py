#!/usr/bin/env python
"""
Clean Database Script for TaskFlow Demo System
This script safely removes all existing data while preserving the database structure
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction
from accounts.models import Organization, UserProfile
from kanban.models import Board, Column, Task, TaskLabel, Comment, TaskActivity, MeetingTranscript

def clean_database():
    """
    Safely clean all data while preserving superuser and database structure
    """
    print("🧹 TaskFlow Database Cleaning")
    print("=" * 50)
    
    # Ask for confirmation
    print("⚠️  WARNING: This will delete ALL data except superuser accounts!")
    print("This includes:")
    print("- All boards, tasks, columns, labels")
    print("- All organizations and user profiles")
    print("- All comments and activities")
    print("- All meeting transcripts")
    print("- All regular users (non-superusers)")
    print()
    
    confirmation = input("Are you sure you want to proceed? Type 'yes' to continue: ")
    if confirmation.lower() != 'yes':
        print("❌ Operation cancelled")
        return False
    
    try:
        with transaction.atomic():
            # Get initial counts
            board_count = Board.objects.count()
            task_count = Task.objects.count()
            user_count = User.objects.filter(is_superuser=False).count()
            org_count = Organization.objects.count()
            comment_count = Comment.objects.count()
            
            print(f"\n📊 Current Database Status:")
            print(f"   Boards: {board_count}")
            print(f"   Tasks: {task_count}")
            print(f"   Regular Users: {user_count}")
            print(f"   Organizations: {org_count}")
            print(f"   Comments: {comment_count}")
            print()
            
            # Delete in proper order to avoid foreign key constraints
            print("🗑️  Deleting data...")
            
            # 1. Delete meeting transcripts
            transcript_count = MeetingTranscript.objects.count()
            if transcript_count > 0:
                MeetingTranscript.objects.all().delete()
                print(f"✅ Deleted {transcript_count} meeting transcripts")
            
            # 2. Delete task activities
            activity_count = TaskActivity.objects.count()
            if activity_count > 0:
                TaskActivity.objects.all().delete()
                print(f"✅ Deleted {activity_count} task activities")
            
            # 3. Delete comments
            if comment_count > 0:
                Comment.objects.all().delete()
                print(f"✅ Deleted {comment_count} comments")
            
            # 4. Delete tasks (this will also handle labels through many-to-many)
            if task_count > 0:
                Task.objects.all().delete()
                print(f"✅ Deleted {task_count} tasks")
            
            # 5. Delete task labels
            label_count = TaskLabel.objects.count()
            if label_count > 0:
                TaskLabel.objects.all().delete()
                print(f"✅ Deleted {label_count} task labels")
            
            # 6. Delete columns
            column_count = Column.objects.count()
            if column_count > 0:
                Column.objects.all().delete()
                print(f"✅ Deleted {column_count} columns")
            
            # 7. Delete boards
            if board_count > 0:
                Board.objects.all().delete()
                print(f"✅ Deleted {board_count} boards")
            
            # 8. Delete user profiles
            profile_count = UserProfile.objects.count()
            if profile_count > 0:
                UserProfile.objects.all().delete()
                print(f"✅ Deleted {profile_count} user profiles")
            
            # 9. Delete organizations
            if org_count > 0:
                Organization.objects.all().delete()
                print(f"✅ Deleted {org_count} organizations")
            
            # 10. Delete regular users (preserve superusers)
            regular_users = User.objects.filter(is_superuser=False)
            if regular_users.exists():
                regular_users.delete()
                print(f"✅ Deleted {user_count} regular users")
            
            # Show remaining superusers
            superusers = User.objects.filter(is_superuser=True)
            if superusers.exists():
                print(f"👑 Preserved {superusers.count()} superuser(s):")
                for su in superusers:
                    print(f"   - {su.username} ({su.email})")
            
            print("\n🎉 Database cleaned successfully!")
            print("=" * 50)
            print("✨ Your database is now clean and ready for demo data!")
            print()
            print("Next steps:")
            print("1. Create a new user account or use existing superuser")
            print("2. Visit /demo/ to load demo scenarios")
            print("3. Test the AI features with fresh demo data")
            
            return True
            
    except Exception as e:
        print(f"❌ Error cleaning database: {str(e)}")
        return False

def create_fresh_demo_user():
    """Create a fresh demo user for testing"""
    print("\n👤 Creating Fresh Demo User...")
    
    username = 'demo_user'
    password = 'demo123'
    email = 'demo@taskflow.com'
    
    # Check if user exists
    if User.objects.filter(username=username).exists():
        print(f"ℹ️  User '{username}' already exists")
        return username, password
    
    try:
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name='Demo',
            last_name='User'
        )
        print(f"✅ Created demo user: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        return username, password
        
    except Exception as e:
        print(f"❌ Error creating demo user: {str(e)}")
        return None, None

def verify_clean_database():
    """Verify the database is properly cleaned"""
    print("\n🔍 Verifying Clean Database...")
    
    counts = {
        'Boards': Board.objects.count(),
        'Tasks': Task.objects.count(),
        'Columns': Column.objects.count(),
        'Labels': TaskLabel.objects.count(),
        'Comments': Comment.objects.count(),
        'Activities': TaskActivity.objects.count(),
        'Transcripts': MeetingTranscript.objects.count(),
        'Organizations': Organization.objects.count(),
        'User Profiles': UserProfile.objects.count(),
        'Regular Users': User.objects.filter(is_superuser=False).count(),
        'Superusers': User.objects.filter(is_superuser=True).count(),
    }
    
    all_clean = True
    for item, count in counts.items():
        if item in ['Superusers']:
            print(f"✅ {item}: {count} (preserved)")
        elif count == 0:
            print(f"✅ {item}: {count}")
        else:
            print(f"⚠️  {item}: {count} (unexpected)")
            if item != 'Superusers':
                all_clean = False
    
    if all_clean:
        print("\n🎉 Database is completely clean!")
    else:
        print("\n⚠️  Some data may still exist")
    
    return all_clean

if __name__ == "__main__":
    print("TaskFlow Database Cleaner")
    print("This script will prepare your database for demo testing")
    print()
    
    # Clean the database
    success = clean_database()
    
    if success:
        # Verify cleaning
        verify_clean_database()
        
        # Ask if user wants to create a demo user
        create_user = input("\nWould you like to create a fresh demo user for testing? (y/n): ")
        if create_user.lower() in ['y', 'yes']:
            username, password = create_fresh_demo_user()
            if username:
                print(f"\n🚀 Ready to test! Login with: {username} / {password}")
        
        print("\n📋 Next Steps:")
        print("1. Start your Django server: python manage.py runserver")
        print("2. Login with your user account")
        print("3. Visit /demo/ to load demo scenarios")
        print("4. Experience the guided tour!")
    else:
        print("\n❌ Database cleaning failed. Please check the errors above.")
        sys.exit(1)
