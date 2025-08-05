"""
Django Settings Additions for API Protection

Add these to your kanban_board/settings.py file to enable comprehensive protection.
"""

import os

# Add to your INSTALLED_APPS if creating a management command:
INSTALLED_APPS = [
    # ... your existing apps ...
    'django.contrib.admin',
    'django.contrib.auth',
    # ... etc ...
]

# API Protection Settings
API_PROTECTION = {
    'DAILY_LIMIT': float(os.getenv('DAILY_API_LIMIT', '0.50')),
    'MONTHLY_LIMIT': float(os.getenv('MONTHLY_API_LIMIT', '5.00')),
    'ENABLE_PROTECTION': True,
    'BYPASS_IN_DEV': os.getenv('BYPASS_API_LIMITS_DEV', 'False').lower() == 'true',
    'ALERT_THRESHOLDS': [0.25, 0.50, 0.75, 0.90],  # Alert at 25%, 50%, 75%, 90% of limits
}

# Enhanced Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'api_protection': {
            'format': '[{asctime}] {levelname} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
            'formatter': 'verbose',
        },
        'api_protection_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'api_protection.log',
            'formatter': 'api_protection',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'api_protection': {
            'handlers': ['api_protection_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'kanban.utils.ai_utils': {
            'handlers': ['api_protection_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Add middleware for API protection (optional)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... your existing middleware ...
    # 'kanban.middleware.APIProtectionMiddleware',  # Create this if needed
]

# Cache settings for better protection coordination
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'ai-cache',
        'TIMEOUT': 3600,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        }
    }
}

# Email notifications for cost alerts (optional)
# Note: Only enable email alerts in production
# if not DEBUG:  # Commented out - add DEBUG import first if needed
#     EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#     # Configure your email settings for alerts
#     COST_ALERT_EMAILS = ['your-email@example.com']
