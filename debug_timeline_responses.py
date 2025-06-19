#!/usr/bin/env python
"""
Debug critical path and timeline analysis responses
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
from kanban.models import Board

def debug_timeline_responses():
    """Debug the actual timeline analysis responses"""
    print("🔍 Debugging Timeline Analysis Responses")
    print("=" * 50)
    
    # Create test client
    client = Client()
    
    # Login as avishek user
    user = User.objects.get(username='avishek')
    client.force_login(user)
    
    # Get first board
    board = Board.objects.first()
    
    print(f"📋 Testing board: {board.name} (ID: {board.id})")
    
    # Test critical path endpoint
    print("\n🎯 Testing Critical Path Analysis...")
    try:
        response = client.post('/api/analyze-critical-path/', 
                              data=json.dumps({'board_id': board.id}),
                              content_type='application/json')
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n📊 Critical Path Raw Response:")
            print(json.dumps(data, indent=2))
            
            print("\n🔍 Analysis of Critical Path Response Structure:")
            for key, value in data.items():
                print(f"- {key}: {type(value)}")
                if isinstance(value, list) and value:
                    print(f"  First item type: {type(value[0])}")
                    print(f"  First item: {value[0]}")
        else:
            print(f"❌ Critical Path Error: {response.content.decode()}")
    except Exception as e:
        print(f"❌ Critical Path Exception: {str(e)}")
    
    # Test timeline generation endpoint
    print("\n📅 Testing Timeline Generation...")
    try:
        response = client.post('/api/generate-project-timeline/', 
                              data=json.dumps({'board_id': board.id}),
                              content_type='application/json')
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n📊 Timeline Generation Raw Response:")
            print(json.dumps(data, indent=2))
            
            print("\n🔍 Analysis of Timeline Response Structure:")
            for key, value in data.items():
                print(f"- {key}: {type(value)}")
                if isinstance(value, list) and value:
                    print(f"  First item type: {type(value[0])}")
                    print(f"  First item: {value[0]}")
        else:
            print(f"❌ Timeline Error: {response.content.decode()}")
    except Exception as e:
        print(f"❌ Timeline Exception: {str(e)}")

if __name__ == '__main__':
    debug_timeline_responses()
