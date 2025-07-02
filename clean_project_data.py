#!/usr/bin/env python
"""
Clean Sample Data Script - Preserves Current Users
This script removes only project data (boards, tasks, etc.) while keeping your user accounts
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

def clean_project_data_only():
    """
    Clean only project data, preserve all users and their profiles/organizations
    """
    print("🧹 TaskFlow Project Data Cleaning")
    print("=" * 50)
    
    print("This will delete:")
    print("✅ All boards, tasks, columns, labels")
    print("✅ All comments and activities")
    print("✅ All meeting transcripts")
    print()
    print("This will PRESERVE:")
    print("🔒 All user accounts")
    print("🔒 All organizations")
    print("🔒 All user profiles")
    print()
    
    confirmation = input("Proceed with cleaning project data only? Type 'yes' to continue: ")
    if confirmation.lower() != 'yes':
        print("❌ Operation cancelled")
        return False
    
    try:
        with transaction.atomic():
            # Get initial counts
            board_count = Board.objects.count()
            task_count = Task.objects.count()
            comment_count = Comment.objects.count()
            user_count = User.objects.count()
            org_count = Organization.objects.count()
            
            print(f"\n📊 Current Database Status:")
            print(f"   Boards: {board_count}")
            print(f"   Tasks: {task_count}")
            print(f"   Comments: {comment_count}")
            print(f"   Users: {user_count} (will be preserved)")
            print(f"   Organizations: {org_count} (will be preserved)")
            print()
            
            # Delete in proper order to avoid foreign key constraints
            print("🗑️  Deleting project data...")
            
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
            
            # 4. Delete tasks
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
            
            # Show preserved data
            remaining_users = User.objects.count()
            remaining_orgs = Organization.objects.count()
            remaining_profiles = UserProfile.objects.count()
            
            print(f"\n🔒 Preserved Data:")
            print(f"   Users: {remaining_users}")
            print(f"   Organizations: {remaining_orgs}")
            print(f"   User Profiles: {remaining_profiles}")
            
            if remaining_users > 0:
                print(f"\n👥 Your User Accounts:")
                for user in User.objects.all():
                    user_type = "Superuser" if user.is_superuser else "Regular User"
                    print(f"   - {user.username} ({user.email}) [{user_type}]")
            
            print("\n🎉 Project data cleaned successfully!")
            print("=" * 50)
            print("✨ Your user accounts are preserved and ready for demo data!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error cleaning project data: {str(e)}")
        return False

def verify_clean_project_data():
    """Verify the project data is properly cleaned"""
    print("\n🔍 Verifying Clean Project Data...")
    
    project_counts = {
        'Boards': Board.objects.count(),
        'Tasks': Task.objects.count(),
        'Columns': Column.objects.count(),
        'Labels': TaskLabel.objects.count(),
        'Comments': Comment.objects.count(),
        'Activities': TaskActivity.objects.count(),
        'Transcripts': MeetingTranscript.objects.count(),
    }
    
    preserved_counts = {
        'Users': User.objects.count(),
        'Organizations': Organization.objects.count(),
        'User Profiles': UserProfile.objects.count(),
    }
    
    print("🗑️  Project Data (should be 0):")
    all_clean = True
    for item, count in project_counts.items():
        if count == 0:
            print(f"   ✅ {item}: {count}")
        else:
            print(f"   ⚠️  {item}: {count} (unexpected)")
            all_clean = False
    
    print("\n🔒 Preserved Data (should be > 0):")
    for item, count in preserved_counts.items():
        print(f"   ✅ {item}: {count}")
    
    if all_clean:
        print("\n🎉 Project data is completely clean!")
        print("🔒 User data is preserved!")
    else:
        print("\n⚠️  Some project data may still exist")
    
    return all_clean

if __name__ == "__main__":
    print("TaskFlow Project Data Cleaner")
    print("This script preserves your users while cleaning project data")
    print()
    
    # Clean the project data
    success = clean_project_data_only()
    
    if success:
        # Verify cleaning
        verify_clean_project_data()
        
        print("\n📋 Next Steps:")
        print("1. Login with your existing user account")
        print("2. Visit /demo/ to load demo scenarios")
        print("3. Experience the fresh demo data!")
        print("\n🚀 Your demo system is ready to test!")
    else:
        print("\n❌ Project data cleaning failed. Please check the errors above.")
        sys.exit(1)
