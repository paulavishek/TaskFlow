"""
Simple utility script to test if the Gemini API key is working correctly.
Run this script from the command line to verify your setup.

Example usage:
    python test_gemini_api.py

If successful, it will generate a response from the Gemini API.
If unsuccessful, it will print an error message.
"""

import os
import sys
import django

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

import google.generativeai as genai
from django.conf import settings

def test_gemini_api():
    """Test the Gemini API connection and key."""
    try:
        # Get API key from settings
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key:
            print("Error: GEMINI_API_KEY not set in settings. Please add it to your .env file.")
            print("Example: GEMINI_API_KEY=your_key_here")
            return False
            
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Create a model instance
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Test with a simple prompt
        prompt = "Hello! Please respond with a short message to confirm the API is working."
        response = model.generate_content(prompt)
        
        if response:
            print("\n✅ Gemini API test successful!\n")
            print("Response from Gemini API:")
            print("-------------------------------------------")
            print(response.text.strip())
            print("-------------------------------------------\n")
            return True
        else:
            print("Error: Received empty response from Gemini API.")
            return False
    except Exception as e:
        print(f"\n❌ Gemini API test failed: {str(e)}")
        
        if "API key not valid" in str(e) or "invalid API key" in str(e).lower():
            print("\nPlease check that:")
            print("1. You have a valid Gemini API key")
            print("2. The key is correctly set in your .env file")
            print("3. Your key has sufficient quota/permissions")
            print("\nYou can get a Gemini API key from: https://makersuite.google.com/app/apikey")
        return False

if __name__ == "__main__":
    test_gemini_api()
