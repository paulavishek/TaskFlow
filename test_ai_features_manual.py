"""
Test script for manually testing all AI features in TaskFlow.

This script allows you to test each of the AI features integrated into TaskFlow
using the Gemini API. Run this script to verify each feature is working correctly.
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

# Import AI utility functions
from kanban.utils.ai_utils import (
    generate_task_description, 
    summarize_comments,
    generate_analytics_insights,
    suggest_lean_classification
)

def test_ai_features():
    """Test all AI features sequentially."""
    print("\n🤖 Manual Testing of TaskFlow AI Features 🤖\n")
    
    # Test 1: Task Description Generation
    print("📝 Testing Task Description Generation...")
    task_title = "Implement user authentication system"
    
    print(f"Task Title: {task_title}")
    description = generate_task_description(task_title)
    
    if description:
        print("\n✅ Success! Generated Task Description:")
        print("-------------------------------------------")
        print(description)
        print("-------------------------------------------\n")
    else:
        print("\n❌ Failed to generate task description\n")
    
    # Test 2: Comment Summarization
    print("📝 Testing Comment Summarization...")
    comments = [
        {
            'user': 'john_doe',
            'content': 'I think we should use JWT tokens for the authentication mechanism. They are more secure and easier to implement.',
            'created_at': '2023-06-05 10:15'
        },
        {
            'user': 'jane_smith',
            'content': 'Good idea. We should also ensure we handle token expiration properly with refresh tokens.',
            'created_at': '2023-06-05 10:25'
        },
        {
            'user': 'tech_lead',
            'content': 'Agreed with both suggestions. Let\'s also include rate limiting to prevent brute force attacks.',
            'created_at': '2023-06-05 11:00'
        },
        {
            'user': 'product_manager',
            'content': 'Make sure the UX is smooth - users shouldn\'t need to login too frequently. Aim for a 7-day token validity.',
            'created_at': '2023-06-05 14:30'
        }
    ]
    
    summary = summarize_comments(comments)
    
    if summary:
        print("\n✅ Success! Comment Summary:")
        print("-------------------------------------------")
        print(summary)
        print("-------------------------------------------\n")
    else:
        print("\n❌ Failed to summarize comments\n")
    
    # Test 3: Analytics Insights
    print("📝 Testing Analytics Insights Generation...")
    analytics_data = {
        'todo_count': 8,
        'in_progress_count': 5,
        'done_count': 12,
        'total_tasks': 25,
        'completion_rate': 48.0,
        'high_priority_count': 3,
        'urgent_priority_count': 1,
        'overdue_count': 2,
        'value_added_percent': 60.0,
        'non_value_added_percent': 24.0,
        'waste_percent': 16.0,
    }
    
    insights = generate_analytics_insights(analytics_data)
    
    if insights:
        print("\n✅ Success! Analytics Insights:")
        print("-------------------------------------------")
        print(insights)
        print("-------------------------------------------\n")
    else:
        print("\n❌ Failed to generate analytics insights\n")
    
    # Test 4: Lean Six Sigma Classification
    print("📝 Testing Lean Six Sigma Classification...")
    task_title = "Weekly status meeting with stakeholders"
    task_description = "Hold a 1-hour meeting every Friday to discuss project progress and address concerns from stakeholders."
    
    classification = suggest_lean_classification(task_title, task_description)
    
    if classification:
        print("\n✅ Success! LSS Classification:")
        print("-------------------------------------------")
        print(f"Classification: {classification.get('classification', 'Unknown')}")
        print(f"Justification: {classification.get('justification', 'No justification provided')}")
        print("-------------------------------------------\n")
    else:
        print("\n❌ Failed to suggest LSS classification\n")
    
    print("🏁 AI Features Testing Completed!")

if __name__ == "__main__":
    test_ai_features()
