#!/usr/bin/env python3
"""
Setup script for Google OAuth configuration in Django admin
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

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.core.management import call_command


def setup_google_oauth():
    """Set up Google OAuth application in Django admin"""
    
    print("🔧 Setting up Google OAuth Configuration...")
    print("=" * 50)
    
    # Update site domain
    try:
        site = Site.objects.get(pk=1)
        site.domain = 'localhost:8000'
        site.name = 'TaskFlow Development'
        site.save()
        print("✅ Updated site configuration")
    except Site.DoesNotExist:
        site = Site.objects.create(
            pk=1,
            domain='localhost:8000',
            name='TaskFlow Development'
        )
        print("✅ Created site configuration")
    
    # Check if Google OAuth app already exists
    try:
        google_app = SocialApp.objects.get(provider='google')
        print("ℹ️  Google OAuth app already exists")
        
        # Update with environment variables if available
        client_id = os.getenv('GOOGLE_OAUTH2_CLIENT_ID', '')
        client_secret = os.getenv('GOOGLE_OAUTH2_CLIENT_SECRET', '')
        
        if client_id and client_secret:
            google_app.client_id = client_id
            google_app.secret = client_secret
            google_app.save()
            google_app.sites.add(site)
            print("✅ Updated Google OAuth credentials from environment")
        else:
            print("⚠️  No Google OAuth credentials found in environment")
            
    except SocialApp.DoesNotExist:
        # Create new Google OAuth app
        client_id = os.getenv('GOOGLE_OAUTH2_CLIENT_ID', 'your-client-id-here')
        client_secret = os.getenv('GOOGLE_OAUTH2_CLIENT_SECRET', 'your-client-secret-here')
        
        google_app = SocialApp.objects.create(
            provider='google',
            name='Google OAuth2',
            client_id=client_id,
            secret=client_secret,
        )
        google_app.sites.add(site)
        print("✅ Created Google OAuth app configuration")
    
    print("\n" + "=" * 50)
    print("🎯 Google OAuth Setup Instructions")
    print("=" * 50)
    
    print("\n1. 📋 Google Cloud Console Setup:")
    print("   • Go to: https://console.cloud.google.com/")
    print("   • Create a new project or select an existing one")
    print("   • Enable the Google+ API")
    print("   • Create OAuth 2.0 credentials")
    
    print("\n2. 🔧 OAuth 2.0 Configuration:")
    print("   • Application type: Web application")
    print("   • Authorized JavaScript origins:")
    print("     - http://localhost:8000")
    print("     - https://yourdomain.com (for production)")
    print("   • Authorized redirect URIs:")
    print("     - http://localhost:8000/accounts/google/login/callback/")
    print("     - https://yourdomain.com/accounts/google/login/callback/")
    
    print("\n3. 🔑 Environment Variables:")
    print("   • Copy your Client ID and Client Secret")
    print("   • Add to your .env file:")
    print("     GOOGLE_OAUTH2_CLIENT_ID=your-client-id-here")
    print("     GOOGLE_OAUTH2_CLIENT_SECRET=your-client-secret-here")
    
    print("\n4. 🚀 Testing:")
    print("   • Restart your Django server")
    print("   • Visit: http://localhost:8000/accounts/login/")
    print("   • Click 'Sign in with Google'")
    
    print("\n5. 📊 Admin Configuration:")
    print("   • Visit: http://localhost:8000/admin/socialaccount/socialapp/")
    print("   • Update the Google OAuth app with your actual credentials")
    
    current_config = SocialApp.objects.filter(provider='google').first()
    if current_config:
        print(f"\n📋 Current Configuration:")
        print(f"   • Provider: {current_config.provider}")
        print(f"   • Client ID: {current_config.client_id}")
        print(f"   • Secret: {'*' * len(current_config.secret) if current_config.secret else 'Not set'}")
        print(f"   • Sites: {', '.join([site.domain for site in current_config.sites.all()])}")
    
    print("\n✅ Google OAuth setup completed!")
    print("💡 Don't forget to update your credentials in the Django admin or .env file!")


if __name__ == '__main__':
    setup_google_oauth()
