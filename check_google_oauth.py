#!/usr/bin/env python3
"""
Check Google OAuth Configuration
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

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

def check_google_oauth_config():
    """Check the current Google OAuth configuration"""
    print("🔍 Checking Google OAuth Configuration...")
    print("=" * 50)
    
    # Check sites
    sites = Site.objects.all()
    print(f"📍 Sites configured: {list(sites)}")
    
    # Check Google OAuth apps
    google_apps = SocialApp.objects.filter(provider='google')
    print(f"🔧 Google OAuth apps found: {google_apps.count()}")
    
    if google_apps.exists():
        for app in google_apps:
            print(f"\n📱 Google OAuth App Details:")
            print(f"   • Name: {app.name}")
            print(f"   • Provider: {app.provider}")
            print(f"   • Client ID: {app.client_id}")
            print(f"   • Has Secret: {'Yes' if app.secret else 'No'}")
            print(f"   • Secret Preview: {app.secret[:10]}..." if app.secret else "   • Secret: None")
            print(f"   • Associated Sites: {list(app.sites.all())}")
            
            # Check if this is a test configuration
            if app.client_id == 'your-client-id-here' or app.client_id == 'test-client-id':
                print(f"   ⚠️  WARNING: Using placeholder/test credentials!")
                print(f"   ❌ This will cause 'invalid_client' error")
    else:
        print("❌ No Google OAuth apps configured!")
    
    # Check environment variables
    print(f"\n🔑 Environment Variables:")
    client_id = os.getenv('GOOGLE_OAUTH2_CLIENT_ID', '')
    client_secret = os.getenv('GOOGLE_OAUTH2_CLIENT_SECRET', '')
    
    print(f"   • GOOGLE_OAUTH2_CLIENT_ID: {'Set' if client_id else 'Not set'}")
    print(f"   • GOOGLE_OAUTH2_CLIENT_SECRET: {'Set' if client_secret else 'Not set'}")
    
    if client_id:
        print(f"   • Client ID Preview: {client_id[:20]}...")
    if client_secret:
        print(f"   • Client Secret Preview: {client_secret[:10]}...")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if not google_apps.exists() or any(app.client_id in ['your-client-id-here', 'test-client-id'] for app in google_apps):
        print("   1. ❌ Invalid/Test credentials detected")
        print("   2. 🔧 You need to set up real Google OAuth credentials")
        print("   3. 📋 Visit Google Cloud Console: https://console.cloud.google.com/")
        print("   4. 🔑 Create OAuth 2.0 credentials")
        print("   5. 📝 Update the SocialApp in Django admin")
    else:
        print("   ✅ Configuration looks good!")

if __name__ == '__main__':
    check_google_oauth_config()
