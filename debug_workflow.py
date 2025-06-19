#!/usr/bin/env python
"""
Debug workflow optimization response
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

def debug_workflow_response():
    """Debug the actual workflow optimization response"""
    print("🔍 Debugging Workflow Optimization Response")
    print("=" * 50)
    
    # Create test client
    client = Client()
    
    # Login as avishek user
    user = User.objects.get(username='avishek')
    client.force_login(user)
    
    # Get first board
    board = Board.objects.first()
    
    # Test workflow optimization endpoint
    print(f"📋 Testing board: {board.name} (ID: {board.id})")
    
    response = client.post('/api/analyze-workflow-optimization/', 
                          data=json.dumps({'board_id': board.id}),
                          content_type='application/json')
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n📊 Raw Response:")
        print(json.dumps(data, indent=2))
        
        print("\n🔍 Analysis of Response Structure:")
        for key, value in data.items():
            print(f"- {key}: {type(value)} = {value}")
            if isinstance(value, list) and value:
                print(f"  First item type: {type(value[0])}")
                print(f"  First item: {value[0]}")
    else:
        print(f"❌ Error: {response.content.decode()}")

if __name__ == '__main__':
    debug_workflow_response()
