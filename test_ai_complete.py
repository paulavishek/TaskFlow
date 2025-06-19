#!/usr/bin/env python
"""
End-to-end test of AI Analytics features
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

import json
from django.test import Client
from django.contrib.auth.models import User
from kanban.models import Board, Column, Task

def test_ai_analytics_complete():
    """Complete test of AI analytics features"""
    print("🔬 Complete AI Analytics Test")
    print("=" * 50)
    
    # Create test client
    client = Client()
    
    # Get or create test user
    user = User.objects.filter(username='avishek').first()
    if not user:
        print("❌ Test user not found")
        return
    
    # Login
    client.force_login(user)
    print(f"✅ Logged in as {user.username}")
    
    # Get first board with some tasks
    board = Board.objects.filter(created_by=user).first()
    if not board:
        print("❌ No boards found for user")
        return
    
    print(f"📋 Using board: {board.name} (ID: {board.id})")
    
    # Check board has some data
    task_count = Task.objects.filter(column__board=board).count()
    print(f"📊 Board has {task_count} tasks")
    
    # Test 1: AI Summary
    print("\n🤖 Testing AI Summary...")
    response = client.get(f'/api/summarize-board-analytics/{board.id}/')
    if response.status_code == 200:
        data = response.json()
        if 'summary' in data:
            print("✅ AI Summary working!")
            summary = data['summary'][:200] + "..." if len(data['summary']) > 200 else data['summary']
            print(f"📝 Summary preview: {summary}")
        else:
            print(f"❌ No summary in response: {data}")
    else:
        print(f"❌ AI Summary failed: {response.status_code}")
        print(response.content.decode()[:200])
    
    # Test 2: Workflow Optimization
    print("\n⚙️ Testing Workflow Optimization...")
    response = client.post('/api/analyze-workflow-optimization/', 
                          data=json.dumps({'board_id': board.id}),
                          content_type='application/json')
    if response.status_code == 200:
        data = response.json()
        print("✅ Workflow Optimization working!")
        if 'analysis' in data:
            analysis = data['analysis'][:200] + "..." if len(data['analysis']) > 200 else data['analysis']
            print(f"📊 Analysis preview: {analysis}")
        if 'recommendations' in data:
            print(f"💡 Found {len(data['recommendations'])} recommendations")
    else:
        print(f"❌ Workflow Optimization failed: {response.status_code}")
        print(response.content.decode()[:200])
    
    # Test 3: Timeline Generation
    print("\n📅 Testing Timeline Generation...")
    response = client.post('/api/generate-project-timeline/', 
                          data=json.dumps({'board_id': board.id}),
                          content_type='application/json')
    if response.status_code == 200:
        data = response.json()
        print("✅ Timeline Generation working!")
        if 'timeline' in data:
            timeline = data['timeline'][:200] + "..." if len(data['timeline']) > 200 else data['timeline']
            print(f"📅 Timeline preview: {timeline}")
    else:
        print(f"❌ Timeline Generation failed: {response.status_code}")
        print(response.content.decode()[:200])
    
    # Test 4: Analytics page loads
    print("\n🌐 Testing Analytics Page...")
    response = client.get(f'/boards/{board.id}/analytics/')
    if response.status_code == 200:
        print("✅ Analytics page loads successfully!")
        # Check if AI elements are in the page
        content = response.content.decode()
        if 'generate-ai-summary' in content:
            print("✅ AI Summary button found in page")
        if 'analyze-workflow-btn' in content:
            print("✅ Workflow Optimization button found in page")
        if 'analyze-critical-path-btn' in content:
            print("✅ Critical Path button found in page")
    else:
        print(f"❌ Analytics page failed to load: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 AI Analytics testing complete!")
    print("📍 You can now visit: http://127.0.0.1:8000/boards/{}/analytics/".format(board.id))
    print("🔑 Login with: avishek / password123")
    print("=" * 50)

if __name__ == '__main__':
    test_ai_analytics_complete()
