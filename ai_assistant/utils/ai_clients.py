import os
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """Google Gemini AI client - Simplified for single model"""
    
    def __init__(self):
        try:
            import google.generativeai as genai
            self.genai = genai
            api_key = getattr(settings, 'GEMINI_API_KEY', None)
            if not api_key:
                raise ValueError("GEMINI_API_KEY not configured in settings")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("Gemini client initialized successfully")
        except ImportError:
            logger.error("google-generativeai package not installed")
            self.model = None
        except Exception as e:
            logger.error(f"Error initializing Gemini client: {e}")
            self.model = None
    
    def get_response(self, prompt, system_prompt=None, history=None):
        """
        Get response from Gemini model
        
        Args:
            prompt (str): User prompt
            system_prompt (str): System context
            history (list): Chat history
            
        Returns:
            dict: Response with content and token info
        """
        if not self.model:
            return {
                'content': 'Gemini service is unavailable',
                'error': 'Model not initialized',
                'tokens': 0
            }
        
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = self.model.generate_content(full_prompt)
            
            return {
                'content': response.text,
                'error': None,
                'tokens': len(response.text.split()),  # Approximate token count
            }
        
        except Exception as e:
            logger.error(f"Error getting Gemini response: {e}")
            return {
                'content': f"Error: {str(e)}",
                'error': str(e),
                'tokens': 0
            }
