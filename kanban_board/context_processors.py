from django.conf import settings

def static_version(request):
    """Add STATIC_VERSION to template context for cache busting"""
    return {
        'STATIC_VERSION': getattr(settings, 'STATIC_VERSION', '1')
    }
