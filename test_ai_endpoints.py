#!/usr/bin/env python
"""
Simple test script to check if AI endpoints are working
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

import requests
from django.contrib.auth.models import User
from django.test import Client
from kanban.models import Board

def test_ai_endpoints():
    """Test the AI endpoints"""
    print("🧪 Testing AI Endpoints")
    print("=" * 40)
    
    # Create a test client
    client = Client()
    
    # Login as admin
    admin_user = User.objects.filter(username='admin').first()
    if not admin_user:
        print("❌ Admin user not found")
        return
    
    # Login the client
    client.force_login(admin_user)
    
    # Get the first board
    board = Board.objects.first()
    if not board:
        print("❌ No boards found")
        return
    
    print(f"📋 Testing with board: {board.name} (ID: {board.id})")
    
    # Test AI summary endpoint
    print("\n🤖 Testing AI Summary endpoint...")
    try:
        response = client.get(f'/api/summarize-board-analytics/{board.id}/')
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if 'error' in data:
                print(f"❌ Error: {data['error']}")
            else:
                print("✅ AI Summary endpoint working")
                print(f"Summary length: {len(data.get('summary', ''))}")
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(response.content.decode()[:200])
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test workflow optimization endpoint
    print("\n⚙️ Testing Workflow Optimization endpoint...")
    try:
        response = client.post('/api/analyze-workflow-optimization/', 
                              data={'board_id': board.id},
                              content_type='application/json')
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if 'error' in data:
                print(f"❌ Error: {data['error']}")
            else:
                print("✅ Workflow Optimization endpoint working")
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(response.content.decode()[:200])
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test critical path endpoint
    print("\n🎯 Testing Critical Path endpoint...")
    try:
        response = client.post('/api/analyze-critical-path/', 
                              data={'board_id': board.id},
                              content_type='application/json')
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if 'error' in data:
                print(f"❌ Error: {data['error']}")
            else:
                print("✅ Critical Path endpoint working")
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(response.content.decode()[:200])
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == '__main__':
    test_ai_endpoints()
