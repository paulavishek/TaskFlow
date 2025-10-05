"""
Protected AI Utils Integration

This shows how to integrate the protection system with your existing AI functions.
Copy these modifications to your kanban/utils/ai_utils.py file.
"""

import logging
from typing import Dict, Optional
from api_protection_system import api_cost_protection, FUNCTION_COSTS

# Setup logger
logger = logging.getLogger(__name__)

# Import the AI model function from your existing ai_utils
try:
    from kanban.utils.ai_utils import get_model
except ImportError:
    def get_model():
        """Fallback if ai_utils not available"""
        import google.generativeai as genai
        return genai.GenerativeModel('gemini-2.5-flash')

# Example of how to modify your existing functions:

@api_cost_protection("generate_task_description", FUNCTION_COSTS["generate_task_description"])
def generate_task_description(title: str) -> Optional[str]:
    """
    Generate a detailed task description with cost protection
    """
    try:
        model = get_model()
        if not model:
            return None
            
        prompt = f"""
        Based on this task title: "{title}", generate a detailed task description 
        with an objective and a checklist of smaller steps.
        
        Format your response like this (in Markdown):
        
        **Objective:** [Brief description of what this task aims to accomplish]
        
        **Checklist:**
        - [ ] First subtask
        - [ ] Second subtask
        - [ ] Third subtask
        (and so on)
        
        Keep it concise but thorough. Include approximately 4-6 subtasks.
        """
        
        response = model.generate_content(prompt)
        if response:
            return response.text.strip()
        return None
    except Exception as e:
        logger.error(f"Error generating task description: {str(e)}")
        return None

@api_cost_protection("summarize_board_analytics", FUNCTION_COSTS["summarize_board_analytics"])
def summarize_board_analytics(analytics_data: Dict) -> Optional[str]:
    """
    Generate an AI-powered summary of board analytics with cost protection
    """
    try:
        model = get_model()
        if not model:
            return None
            
        # ... rest of your existing implementation ...
        
    except Exception as e:
        logger.error(f"Error summarizing board analytics: {str(e)}")
        return None

# Continue this pattern for all your AI functions...

def check_protection_status():
    """Helper function to check current protection status"""
    from api_protection_system import get_status_report
    return get_status_report()

# Add this to your views.py or create a new endpoint
def api_cost_status_view(request):
    """View to check API cost status"""
    from django.http import JsonResponse
    from api_protection_system import get_status_report
    
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    status = get_status_report()
    return JsonResponse(status)
