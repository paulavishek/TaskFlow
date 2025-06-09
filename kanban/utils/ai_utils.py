"""
Utility module for integrating with Google Generative AI (Gemini) API.

This module provides helper functions to call the Gemini API for various
AI-powered features in the TaskFlow application.
"""
import os
import logging
from typing import Dict, List, Optional

import google.generativeai as genai
from django.conf import settings

# Setup logging
logger = logging.getLogger(__name__)

# Configure the Gemini API with your API key
try:
    # Try to get from settings first (recommended for production)
    GEMINI_API_KEY = getattr(settings, 'GEMINI_API_KEY', None)
    
    # If not in settings, try environment variable (for development)
    if not GEMINI_API_KEY:
        GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
    else:
        logger.warning("GEMINI_API_KEY not set. AI features won't work.")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {str(e)}")

def get_model():
    """Get the Gemini model instance."""
    try:
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        logger.error(f"Error getting Gemini model: {str(e)}")
        return None

def generate_task_description(title: str) -> Optional[str]:
    """
    Generate a detailed task description and checklist from a task title.
    
    Args:
        title: The title of the task
        
    Returns:
        A generated description with a checklist or None if generation fails
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

def summarize_comments(comments: List[Dict]) -> Optional[str]:
    """
    Summarize a list of task comments.
    
    Args:
        comments: A list of comment dictionaries with 'user', 'content', and 'created_at'
        
    Returns:
        A summary of the comments or None if summarization fails
    """
    try:
        model = get_model()
        if not model or not comments:
            return None
            
        # Format comments for the prompt
        formatted_comments = "\n\n".join([
            f"User: {comment['user']}\nDate: {comment['created_at']}\n{comment['content']}" 
            for comment in comments
        ])
        
        prompt = f"""
        Summarize the following task comment thread concisely. Focus on key decisions,
        assignments, deadlines, and important information:
        
        {formatted_comments}
        
        Provide a brief summary (3-5 sentences).
        """
        
        response = model.generate_content(prompt)
        if response:
            return response.text.strip()
        return None
    except Exception as e:
        logger.error(f"Error summarizing comments: {str(e)}")
        return None

def generate_analytics_insights(analytics_data: Dict) -> Optional[str]:
    """
    Generate natural language insights from board analytics data.
    
    Args:
        analytics_data: Dictionary containing analytics data
        
    Returns:
        A string with insights and risk identification or None if generation fails
    """
    try:
        model = get_model()
        if not model:
            return None
            
        # Format analytics data for the prompt
        prompt = f"""
        Based on the following Kanban board analytics data, provide insights and identify potential risks.
        Focus on what's working well and areas that need attention:
        
        - Tasks in 'To Do': {analytics_data.get('todo_count', 0)}
        - Tasks in 'In Progress': {analytics_data.get('in_progress_count', 0)}
        - Tasks in 'Done': {analytics_data.get('done_count', 0)}
        - Overall Completion Rate: {analytics_data.get('completion_rate', 0)}%
        - Tasks with Due Date Overdue: {analytics_data.get('overdue_count', 0)}
        - High Priority Tasks: {analytics_data.get('high_priority_count', 0)}
        - Urgent Priority Tasks: {analytics_data.get('urgent_priority_count', 0)}
        - Value-Added Work: {analytics_data.get('value_added_percent', 0)}%
        - Non-Value-Added Work: {analytics_data.get('non_value_added_percent', 0)}%
        - Waste: {analytics_data.get('waste_percent', 0)}%
        
        Provide 3-5 sentences with clear insights. If there are risks to the project timeline
        or efficiency, clearly highlight them.
        """
        
        response = model.generate_content(prompt)
        if response:
            return response.text.strip()
        return None
    except Exception as e:
        logger.error(f"Error generating analytics insights: {str(e)}")
        return None

def suggest_lean_classification(title: str, description: str) -> Optional[Dict]:
    """
    Suggest Lean Six Sigma classification for a task based on its title and description.
    
    Args:
        title: The task title
        description: The task description
        
    Returns:
        A dictionary with suggested classification and justification or None if suggestion fails
    """
    try:
        model = get_model()
        if not model:
            return None
            
        prompt = f"""
        Based on this task's title and description, suggest a Lean Six Sigma classification
        (Value-Added, Necessary Non-Value-Added, or Waste/Eliminate) and briefly justify why.
        
        Task Title: {title}
        Task Description: {description or '(No description provided)'}
        
        Consider:
        - Value-Added (VA): Activities that transform the product/service in a way the customer values
        - Necessary Non-Value-Added (NNVA): Required activities that don't directly add value for the customer
        - Waste/Eliminate: Activities that consume resources without adding value
        
        Format your response as JSON:
        {{
            "classification": "Value-Added|Necessary Non-Value-Added|Waste/Eliminate",
            "justification": "1-2 sentences explaining why this classification fits"
        }}
        """
        
        response = model.generate_content(prompt)
        if response:
            # This is not perfect but extracting the response as if it's JSON
            # In a production app, we'd want better error handling
            import json
            response_text = response.text.strip()
            
            # Handle the case where the AI might include code block formatting
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].strip()
                
            return json.loads(response_text)
        return None
    except Exception as e:
        logger.error(f"Error suggesting lean classification: {str(e)}")
        return None
