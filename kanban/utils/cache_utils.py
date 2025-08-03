"""
Cache utilities for AI API cost optimization in TaskFlow

This module provides cache management functions for AI-powered features
to reduce API costs by avoiding redundant calls to external AI services.
"""

import hashlib
import json
from django.core.cache import cache
from django.conf import settings
from typing import Optional, Any, Dict


def create_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Create a consistent cache key from prefix and arguments.
    
    Args:
        prefix: Cache key prefix (e.g., 'task_description', 'comments_summary')
        *args: Positional arguments to include in the key
        **kwargs: Keyword arguments to include in the key
    
    Returns:
        String cache key
    """
    # Create a deterministic string from all arguments
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items()) if kwargs else {}
    }
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    
    # Create a hash to ensure key length limits and avoid special characters
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    
    return f"ai_cache:{prefix}:{key_hash}"


def get_ai_cache_timeout(cache_type: str) -> int:
    """
    Get cache timeout for specific AI feature type.
    
    Args:
        cache_type: Type of AI cache (e.g., 'task_description', 'comments_summary')
    
    Returns:
        Cache timeout in seconds
    """
    timeouts = getattr(settings, 'AI_CACHE_TIMEOUT', {})
    return timeouts.get(cache_type, 3600)  # Default to 1 hour


def get_cached_ai_response(cache_type: str, *args, **kwargs) -> Optional[Any]:
    """
    Get cached AI response if available.
    
    Args:
        cache_type: Type of AI cache
        *args: Arguments used to generate the cache key
        **kwargs: Keyword arguments used to generate the cache key
    
    Returns:
        Cached response or None if not found
    """
    from .cache_metrics import CacheMetrics
    
    cache_key = create_cache_key(cache_type, *args, **kwargs)
    result = cache.get(cache_key)
    
    # Record metrics
    if result is not None:
        CacheMetrics.record_cache_hit(cache_type)
    else:
        CacheMetrics.record_cache_miss(cache_type)
    
    return result


def set_cached_ai_response(cache_type: str, response: Any, *args, **kwargs) -> None:
    """
    Cache an AI response.
    
    Args:
        cache_type: Type of AI cache
        response: The AI response to cache
        *args: Arguments used to generate the cache key
        **kwargs: Keyword arguments used to generate the cache key
    """
    cache_key = create_cache_key(cache_type, *args, **kwargs)
    timeout = get_ai_cache_timeout(cache_type)
    cache.set(cache_key, response, timeout)


def invalidate_ai_cache(cache_type: str, *args, **kwargs) -> None:
    """
    Invalidate a specific cached AI response.
    
    Args:
        cache_type: Type of AI cache
        *args: Arguments used to generate the cache key
        **kwargs: Keyword arguments used to generate the cache key
    """
    cache_key = create_cache_key(cache_type, *args, **kwargs)
    cache.delete(cache_key)


def invalidate_task_related_caches(task_id: int) -> None:
    """
    Invalidate all caches related to a specific task.
    This should be called when a task is updated significantly.
    
    Args:
        task_id: ID of the task that was updated
    """
    # Note: Since we use hashed keys, we can't easily delete by pattern
    # In a production environment with Redis, you could use pattern matching
    # For now, we'll implement specific invalidation in the views where needed
    pass


def invalidate_board_related_caches(board_id: int) -> None:
    """
    Invalidate all caches related to a specific board.
    This should be called when board structure or tasks change significantly.
    
    Args:
        board_id: ID of the board that was updated
    """
    # Invalidate board analytics cache
    invalidate_ai_cache('board_analytics', board_id=board_id)


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics for monitoring.
    Note: This works with local memory cache. For Redis, you'd use different commands.
    
    Returns:
        Dictionary with cache statistics
    """
    try:
        # This is a basic implementation for LocMemCache
        # For production with Redis, you'd use more sophisticated stats
        return {
            'cache_backend': 'locmem',
            'status': 'active',
            'note': 'Detailed stats available with Redis backend'
        }
    except Exception as e:
        return {
            'cache_backend': 'unknown',
            'status': 'error',
            'error': str(e)
        }
