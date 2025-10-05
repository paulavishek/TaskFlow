"""
Quick script to list available Gemini models
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

import google.generativeai as genai
from django.conf import settings

# Configure API
api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.environ.get('GEMINI_API_KEY', '')

if api_key:
    genai.configure(api_key=api_key)
    
    print("\n" + "="*70)
    print("  AVAILABLE GEMINI MODELS")
    print("="*70 + "\n")
    
    try:
        models = genai.list_models()
        
        for model in models:
            print(f"Model: {model.name}")
            print(f"  Display Name: {model.display_name}")
            print(f"  Description: {model.description}")
            print(f"  Supported Methods: {', '.join(model.supported_generation_methods)}")
            print()
            
    except Exception as e:
        print(f"Error listing models: {str(e)}")
else:
    print("No API key configured")
