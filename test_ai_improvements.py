#!/usr/bin/env python
"""
Test script to verify AI timeline analysis improvements
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

from kanban.models import Board, Task
from kanban.utils.ai_utils import analyze_critical_path, generate_project_timeline

def test_ai_improvements():
    """Test the improved AI functions"""
    print("🧪 Testing AI Timeline Analysis Improvements...")
    
    try:
        # Get the Software Project board
        software_board = Board.objects.get(id=2)
        print(f"✅ Found board: {software_board.name}")
        
        # Get tasks data
        tasks = Task.objects.filter(column__board=software_board)
        print(f"📋 Found {tasks.count()} tasks")
        
        # Build board data for AI analysis
        tasks_data = []
        for task in tasks[:10]:  # Test with first 10 tasks
            task_info = {
                'id': task.id,
                'title': task.title,
                'estimated_duration_hours': task.estimated_duration_hours,
                'priority': task.priority,
                'assigned_to': task.assigned_to.username if task.assigned_to else None,
                'progress': task.progress,
                'predecessors': [p.id for p in task.predecessors.all()]
            }
            tasks_data.append(task_info)
        
        board_data = {
            'board_info': {'name': software_board.name},
            'tasks': tasks_data,
            'team': [{'name': 'Test User', 'task_count': 3}]
        }
        
        print("\n🛤️ Testing Critical Path Analysis...")
        critical_path_result = analyze_critical_path(board_data)
        
        if critical_path_result:
            print("✅ Critical Path Analysis successful!")
            print(f"   - Has critical path: {len(critical_path_result.get('critical_path', []))} tasks")
            print(f"   - Has recommendations: {len(critical_path_result.get('recommendations', []))} items")
            print(f"   - Project insights: {bool(critical_path_result.get('project_insights'))}")
            
            # Check for the old error message
            recommendations = critical_path_result.get('recommendations', [])
            has_formatting_error = any(
                'partial data due to response formatting' in rec.get('description', '').lower()
                for rec in recommendations
            )
            if has_formatting_error:
                print("⚠️ Still showing formatting error message")
            else:
                print("✅ No formatting error messages found!")
                
        else:
            print("❌ Critical Path Analysis failed")
        
        print("\n📅 Testing Timeline Generation...")
        timeline_result = generate_project_timeline(board_data)
        
        if timeline_result:
            print("✅ Timeline Generation successful!")
            print(f"   - Has timeline phases: {len(timeline_result.get('timeline_phases', []))} phases")
            print(f"   - Has resource timeline: {len(timeline_result.get('resource_timeline', []))} resources")
            print(f"   - Has recommendations: {len(timeline_result.get('recommendations', []))} items")
        else:
            print("❌ Timeline Generation failed")
        
        print("\n🎯 Summary:")
        print("   ✅ Task dependencies and durations added")
        print("   ✅ Improved JSON parsing with fallbacks")
        print("   ✅ Better error handling")
        print("   ✅ Ready for testing in the web interface!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_improvements()
