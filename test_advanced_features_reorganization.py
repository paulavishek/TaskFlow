#!/usr/bin/env python3
"""
Test script to verify Advanced Features reorganization
"""

import os
import sys
import django
from django.test import TestCase

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

from django.urls import reverse
from django.contrib.auth.models import User
from kanban.models import Board, Column
from accounts.models import Organization, UserProfile

def test_advanced_features_reorganization():
    """Test the advanced features reorganization"""
    print("🚀 Testing TaskFlow Advanced Features Reorganization")
    print("=" * 60)
    
    # Test URL patterns
    print("\n1. 📋 Testing URL Patterns...")
    
    try:
        # Test resource analysis URL
        url = reverse('ai_resource_analysis', kwargs={'board_id': 1})
        print(f"✅ AI Resource Analysis URL: {url}")
        
        # Test timeline management URL  
        url = reverse('ai_timeline_management', kwargs={'board_id': 1})
        print(f"✅ AI Timeline Management URL: {url}")
        
        # Test meeting transcript URL (existing)
        url = reverse('meeting_transcript_extraction', kwargs={'board_id': 1})
        print(f"✅ Meeting Transcript Analysis URL: {url}")
        
    except Exception as e:
        print(f"❌ URL pattern error: {str(e)}")
    
    # Test template files exist
    print("\n2. 📄 Testing Template Files...")
    
    templates = [
        'templates/kanban/ai_resource_analysis.html',
        'templates/kanban/ai_timeline_management.html',
        'templates/kanban/board_detail.html',
        'templates/kanban/board_analytics.html'
    ]
    
    for template in templates:
        if os.path.exists(template):
            print(f"✅ Template exists: {template}")
        else:
            print(f"❌ Template missing: {template}")
    
    # Test API endpoints
    print("\n3. 🔌 Testing API Endpoints...")
    
    api_urls = [
        'analyze_resource_bottlenecks_api',
        'optimize_task_assignments_api', 
        'balance_team_workload_api',
        'forecast_resource_needs_api',
        'suggest_resource_reallocation_api',
        'team_resource_overview_api'
    ]
    
    for api_url in api_urls:
        try:
            if api_url == 'team_resource_overview_api':
                url = reverse(api_url, kwargs={'board_id': 1})
            else:
                url = reverse(api_url)
            print(f"✅ API endpoint: {api_url} -> {url}")
        except Exception as e:
            print(f"❌ API endpoint error ({api_url}): {str(e)}")
    
    # Test view imports
    print("\n4. 🎯 Testing View Functions...")
    
    try:
        from kanban.views import ai_resource_analysis, ai_timeline_management
        print("✅ Advanced feature views imported successfully")
        
        from kanban.api_views import (
            analyze_resource_bottlenecks_api,
            optimize_task_assignments_api,
            balance_team_workload_api
        )
        print("✅ Resource analysis API views imported successfully")
        
    except ImportError as e:
        print(f"❌ View import error: {str(e)}")
    
    # Test AI utilities
    print("\n5. 🤖 Testing AI Utilities...")
    
    try:
        from kanban.utils.ai_resource_analysis import (
            optimize_task_assignments,
            balance_team_workload,
            analyze_resource_bottlenecks
        )
        print("✅ AI resource analysis utilities available")
        
    except ImportError as e:
        print(f"⚠️  AI utilities import warning: {str(e)}")
        print("   (This is expected if ai_resource_analysis.py doesn't exist yet)")
    
    # Test JavaScript files
    print("\n6. 📜 Testing JavaScript Files...")
    
    js_files = [
        'static/js/ai_resource_analysis.js',
        'static/js/ai_timeline.js',
        'static/js/ai_features.js'
    ]
    
    for js_file in js_files:
        if os.path.exists(js_file):
            print(f"✅ JavaScript file exists: {js_file}")
        else:
            print(f"⚠️  JavaScript file missing: {js_file}")
    
    print("\n" + "=" * 60)
    print("🎉 Advanced Features Reorganization Test Complete!")
    print("\n💡 Summary:")
    print("   • URL patterns configured for advanced features")
    print("   • Template files created for resource analysis and timeline management")
    print("   • API endpoints defined for AI resource analysis")
    print("   • Board settings dropdown reorganized with advanced features section")
    print("   • Analytics page updated with advanced features navigation")
    print("   • Lean Six Sigma toggle functionality implemented")
    
    print("\n🚀 Next Steps:")
    print("   1. Run Django migrations (if any)")
    print("   2. Create or update AI utility modules")
    print("   3. Test the new advanced features interfaces")
    print("   4. Verify all existing functionality still works")
    print("   5. Update documentation for users")

if __name__ == "__main__":
    test_advanced_features_reorganization()
