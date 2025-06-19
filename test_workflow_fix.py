#!/usr/bin/env python
"""
Test the updated workflow optimization formatting
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

def test_workflow_fix():
    """Test the workflow optimization fix"""
    print("🔧 Testing Workflow Optimization Fix")
    print("=" * 40)
    
    # Create test client
    client = Client()
    
    # Login as avishek user
    user = User.objects.get(username='avishek')
    client.force_login(user)
    
    # Get first board
    board = Board.objects.first()
    
    # Test workflow optimization endpoint
    response = client.post('/api/analyze-workflow-optimization/', 
                          data=json.dumps({'board_id': board.id}),
                          content_type='application/json')
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API Response is working")
        
        # Check expected fields
        expected_fields = ['overall_health_score', 'optimization_recommendations', 'quick_wins', 'workflow_insights', 'next_steps']
        for field in expected_fields:
            if field in data:
                print(f"✅ {field}: Found")
                if isinstance(data[field], list):
                    print(f"   - Contains {len(data[field])} items")
                elif isinstance(data[field], str):
                    print(f"   - Length: {len(data[field])}")
                else:
                    print(f"   - Value: {data[field]}")
            else:
                print(f"❌ {field}: Missing")
        
        # Test optimization recommendations structure
        if 'optimization_recommendations' in data and data['optimization_recommendations']:
            print(f"\n📊 First recommendation structure:")
            first_rec = data['optimization_recommendations'][0]
            for key, value in first_rec.items():
                print(f"   - {key}: {value}")
                
        print(f"\n🎯 The JavaScript should now properly display:")
        print(f"   - Health Score: {data.get('overall_health_score', 'N/A')}/10")
        print(f"   - Recommendations: {len(data.get('optimization_recommendations', []))} items")
        print(f"   - Quick Wins: {len(data.get('quick_wins', []))} items")
        print(f"   - Next Steps: {len(data.get('next_steps', []))} items")
        
    else:
        print(f"❌ API Error: {response.status_code}")
        print(response.content.decode())

if __name__ == '__main__':
    test_workflow_fix()
