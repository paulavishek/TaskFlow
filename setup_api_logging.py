"""
Simple API Logging Setup for TaskFlow

This file shows you how to add basic logging to track AI API calls.
Copy the relevant parts to your Django settings.py and ai_utils.py files.
"""

# 1. ADD THIS TO YOUR settings.py file:
DJANGO_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'api_cost': {
            'format': '[{asctime}] {levelname}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'api_cost_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'api_costs.log',
            'formatter': 'api_cost',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'api_costs': {
            'handlers': ['api_cost_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# 2. ADD THIS FUNCTION TO YOUR ai_utils.py:
def log_api_cost(function_name, estimated_cost):
    """Log API call costs for monitoring"""
    import logging
    logger = logging.getLogger('api_costs')
    logger.info(f"API_CALL: {function_name} - Estimated cost: ${estimated_cost:.6f}")

# 3. EXAMPLE OF HOW TO MODIFY YOUR EXISTING FUNCTIONS:
# In your generate_task_description function, add these lines:

def example_generate_task_description(title):
    """Example of enhanced function with cost logging"""
    try:
        # ADD THIS LINE at the start of each AI function:
        log_api_cost("generate_task_description", 0.000101)
        
        # Your existing code here...
        # model = get_model()
        # response = model.generate_content(prompt)
        # etc.
        
        return "Generated description"
        
    except Exception as e:
        # Log errors too
        import logging
        logger = logging.getLogger('api_costs')
        logger.error(f"ERROR in generate_task_description: {str(e)}")
        return None

print("✅ Copy the relevant sections above to your Django project files")
print("📁 Main files to modify:")
print("   • settings.py (add logging config)")
print("   • kanban/utils/ai_utils.py (add log_api_cost calls)")
print("📊 After setup, check api_costs.log file for cost tracking")
