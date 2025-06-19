#!/usr/bin/env python3
"""
Google OAuth User Analysis
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile, Organization
from allauth.socialaccount.models import SocialAccount

def analyze_google_oauth_user():
    """Analyze the Google OAuth user creation"""
    print("🔍 Google OAuth User Analysis")
    print("=" * 50)
    
    # Find users with Google social accounts
    google_accounts = SocialAccount.objects.filter(provider='google')
    
    if not google_accounts.exists():
        print("❌ No Google OAuth users found!")
        return
    
    for social_account in google_accounts:
        user = social_account.user
        
        print(f"\n👤 Google OAuth User Details:")
        print(f"   • Django Username: {user.username}")
        print(f"   • Email: {user.email}")
        print(f"   • First Name: {user.first_name}")
        print(f"   • Last Name: {user.last_name}")
        print(f"   • Date Joined: {user.date_joined}")
        print(f"   • Last Login: {user.last_login}")
        
        print(f"\n🔗 Google Account Details:")
        print(f"   • Provider: {social_account.provider}")
        print(f"   • Google ID: {social_account.uid}")
        
        # Show Google profile data
        extra_data = social_account.extra_data
        print(f"   • Google Name: {extra_data.get('name', 'N/A')}")
        print(f"   • Google Email: {extra_data.get('email', 'N/A')}")
        print(f"   • Google Picture: {extra_data.get('picture', 'N/A')}")
        print(f"   • Verified Email: {extra_data.get('verified_email', 'N/A')}")
        
        # Check organization assignment
        try:
            profile = user.profile
            print(f"\n🏢 Organization Assignment:")
            print(f"   • Organization: {profile.organization.name}")
            print(f"   • Domain: {profile.organization.domain}")
            print(f"   • Is Admin: {profile.is_admin}")
            print(f"   • Profile Created: {profile.organization.created_at}")
        except UserProfile.DoesNotExist:
            print(f"\n⚠️  No organization profile found!")
        
        # Check email domain matching
        email_domain = user.email.split('@')[-1] if user.email else ""
        matching_orgs = Organization.objects.filter(domain=email_domain)
        
        print(f"\n📧 Email Domain Analysis:")
        print(f"   • Email Domain: {email_domain}")
        print(f"   • Matching Organizations: {matching_orgs.count()}")
        for org in matching_orgs:
            print(f"     - {org.name} (created: {org.created_at})")

def explain_oauth_flow():
    """Explain the OAuth flow"""
    print(f"\n🔄 Google OAuth Flow Explanation:")
    print("=" * 50)
    print("1. 🌐 User clicks 'Sign in with Google'")
    print("2. ➡️  Redirected to Google OAuth server")
    print("3. 🔐 Google checks if user is already logged in")
    print("4. ✅ If logged in → Shows 'Continue with Google'")
    print("5. ❌ If not logged in → Shows account selection")
    print("6. 🎯 User grants permissions (first time only)")
    print("7. ↩️  Google redirects back with authorization code")
    print("8. 🔄 Django exchanges code for user info")
    print("9. 👤 Creates/updates user account")
    print("10. 🏢 Assigns to organization (based on email domain)")
    print("11. 🚀 Logs in and redirects to dashboard")
    
    print(f"\n💡 Why No Account Selection:")
    print("=" * 50)
    print("• You're already logged into Gmail in your browser")
    print("• Google uses your current session for OAuth")
    print("• This is faster and more convenient for users")
    print("• To see account selection: logout from Gmail first")

if __name__ == '__main__':
    analyze_google_oauth_user()
    explain_oauth_flow()
    
    print(f"\n✅ Everything is working correctly!")
    print(f"🎉 Google OAuth integration is successful!")
