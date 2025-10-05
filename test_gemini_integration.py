"""
Test script to verify Gemini API integration is working properly.

This script tests the core AI functionality to ensure:
1. API key is properly configured
2. Gemini API is accessible
3. Basic AI features are functional
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from kanban.utils.ai_utils import (
    get_model,
    generate_task_description,
    suggest_lean_classification,
    suggest_task_priority
)
from django.conf import settings

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def test_api_key():
    """Test if API key is configured"""
    print_header("TEST 1: API Key Configuration")
    
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    
    if not api_key:
        api_key = os.environ.get('GEMINI_API_KEY', '')
    
    if api_key:
        # Mask the API key for security
        masked_key = api_key[:10] + "..." + api_key[-5:] if len(api_key) > 15 else "***"
        print(f"✓ API Key is configured: {masked_key}")
        print(f"✓ Key length: {len(api_key)} characters")
        return True
    else:
        print("✗ API Key is NOT configured!")
        print("\nTo configure your API key:")
        print("1. Create a .env file in the project root")
        print("2. Add: GEMINI_API_KEY=your-actual-api-key-here")
        print("3. Or set the GEMINI_API_KEY environment variable")
        return False

def test_model_initialization():
    """Test if Gemini model can be initialized"""
    print_header("TEST 2: Model Initialization")
    
    try:
        model = get_model()
        
        if model:
            print(f"✓ Gemini model initialized successfully")
            print(f"✓ Model type: {type(model).__name__}")
            return True
        else:
            print("✗ Failed to initialize Gemini model")
            return False
    except Exception as e:
        print(f"✗ Error initializing model: {str(e)}")
        return False

def test_task_description_generation():
    """Test task description generation"""
    print_header("TEST 3: Task Description Generation")
    
    try:
        test_title = "Implement user authentication system"
        print(f"Test input: '{test_title}'")
        print("\nGenerating description...")
        
        description = generate_task_description(test_title)
        
        if description:
            print(f"\n✓ Description generated successfully!")
            print(f"\n--- Generated Description ---")
            print(description[:300] + "..." if len(description) > 300 else description)
            print(f"\n✓ Description length: {len(description)} characters")
            return True
        else:
            print("✗ Failed to generate description")
            return False
    except Exception as e:
        print(f"✗ Error generating description: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_lean_classification():
    """Test Lean Six Sigma classification"""
    print_header("TEST 4: Lean Six Sigma Classification")
    
    try:
        test_title = "Review and approve expense reports"
        test_description = "Monthly review of team expense submissions for compliance"
        
        print(f"Test input:")
        print(f"  Title: '{test_title}'")
        print(f"  Description: '{test_description}'")
        print("\nGenerating classification...")
        
        classification = suggest_lean_classification(test_title, test_description)
        
        if classification:
            print(f"\n✓ Classification generated successfully!")
            print(f"\n--- Classification Result ---")
            print(f"Classification: {classification.get('classification', 'N/A')}")
            print(f"Justification: {classification.get('justification', 'N/A')}")
            return True
        else:
            print("✗ Failed to generate classification")
            return False
    except Exception as e:
        print(f"✗ Error generating classification: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_priority_suggestion():
    """Test task priority suggestion"""
    print_header("TEST 5: Task Priority Suggestion")
    
    try:
        task_data = {
            'title': 'Fix critical security vulnerability',
            'description': 'SQL injection vulnerability discovered in login form',
            'due_date': '2025-10-08',  # Tomorrow
            'current_priority': 'medium'
        }
        
        board_context = {
            'total_tasks': 25,
            'high_priority_count': 3,
            'urgent_count': 1,
            'overdue_count': 2,
            'upcoming_deadlines': 5
        }
        
        print(f"Test input:")
        print(f"  Task: '{task_data['title']}'")
        print(f"  Due Date: {task_data['due_date']}")
        print(f"  Board has {board_context['urgent_count']} urgent tasks")
        print("\nGenerating priority suggestion...")
        
        suggestion = suggest_task_priority(task_data, board_context)
        
        if suggestion:
            print(f"\n✓ Priority suggestion generated successfully!")
            print(f"\n--- Priority Suggestion ---")
            print(f"Suggested Priority: {suggestion.get('suggested_priority', 'N/A')}")
            print(f"Confidence: {suggestion.get('confidence', 'N/A')}")
            print(f"Reasoning: {suggestion.get('reasoning', 'N/A')[:150]}...")
            return True
        else:
            print("✗ Failed to generate priority suggestion")
            return False
    except Exception as e:
        print(f"✗ Error generating priority suggestion: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  GEMINI API INTEGRATION TEST SUITE")
    print("  TaskFlow - AI-Powered Kanban Board")
    print("="*70)
    
    # Track test results
    results = {}
    
    # Run tests
    results['API Key Configuration'] = test_api_key()
    
    if not results['API Key Configuration']:
        print("\n" + "="*70)
        print("  TESTS STOPPED: API Key not configured")
        print("="*70)
        return
    
    results['Model Initialization'] = test_model_initialization()
    results['Task Description Generation'] = test_task_description_generation()
    results['Lean Classification'] = test_lean_classification()
    results['Priority Suggestion'] = test_priority_suggestion()
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {test_name}")
    
    print(f"\n{'='*70}")
    print(f"  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"  Status: ✓ ALL TESTS PASSED - Gemini API is fully functional!")
    elif passed > 0:
        print(f"  Status: ⚠ PARTIAL - Some features working, check failures above")
    else:
        print(f"  Status: ✗ FAILED - Gemini API is not working properly")
    
    print(f"{'='*70}\n")
    
    # Print next steps
    if passed == total:
        print("\n🎉 CONGRATULATIONS!")
        print("\nYour Gemini API integration is working perfectly!")
        print("\nYou can now use AI features in your TaskFlow application:")
        print("  • Smart task description generation")
        print("  • Lean Six Sigma classification")
        print("  • Intelligent priority suggestions")
        print("  • Board analytics summarization")
        print("  • Workflow optimization recommendations")
        print("  • And many more AI-powered features!")
        print("\nStart your Django server and explore the AI features:")
        print("  python manage.py runserver")
    else:
        print("\n⚠ ATTENTION NEEDED")
        print("\nSome tests failed. Common issues:")
        print("  1. API key might be invalid or expired")
        print("  2. Network connectivity issues")
        print("  3. Gemini API quota exceeded")
        print("  4. Required Python packages not installed")
        print("\nTroubleshooting:")
        print("  • Verify your API key at: https://aistudio.google.com/app/apikey")
        print("  • Check your internet connection")
        print("  • Ensure google-generativeai package is installed")

if __name__ == '__main__':
    main()
