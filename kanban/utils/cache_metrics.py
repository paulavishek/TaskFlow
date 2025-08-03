"""
Cache monitoring utilities for TaskFlow AI features

This module provides functions to track cache hit rates and estimated cost savings.
"""

from django.core.cache import cache
from django.conf import settings
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class CacheMetrics:
    """Class to track and calculate cache metrics for AI cost optimization."""
    
    # Estimated cost per API call (in USD) - adjust based on your Gemini pricing
    API_COSTS = {
        'task_description': 0.001,      # Small prompt
        'comments_summary': 0.002,      # Medium prompt with comments data
        'board_analytics': 0.003,       # Large prompt with analytics data
        'lss_classification': 0.001,    # Small prompt
        'task_priority': 0.002,         # Medium prompt with context
        'deadline_prediction': 0.002,   # Medium prompt
        'column_recommendations': 0.002, # Medium prompt
        'task_breakdown': 0.003,        # Large prompt
        'workflow_optimization': 0.003, # Large prompt
    }
    
    @staticmethod
    def record_cache_hit(cache_type: str):
        """Record a cache hit for metrics tracking."""
        try:
            key = f"cache_metrics:hits:{cache_type}"
            current_hits = cache.get(key, 0)
            cache.set(key, current_hits + 1, 86400)  # Store for 24 hours
            
            # Also record daily total
            today = datetime.now().strftime('%Y-%m-%d')
            daily_key = f"cache_metrics:daily_hits:{today}:{cache_type}"
            daily_hits = cache.get(daily_key, 0)
            cache.set(daily_key, daily_hits + 1, 86400)
            
        except Exception as e:
            logger.error(f"Error recording cache hit: {e}")
    
    @staticmethod
    def record_cache_miss(cache_type: str):
        """Record a cache miss for metrics tracking."""
        try:
            key = f"cache_metrics:misses:{cache_type}"
            current_misses = cache.get(key, 0)
            cache.set(key, current_misses + 1, 86400)
            
            # Also record daily total
            today = datetime.now().strftime('%Y-%m-%d')
            daily_key = f"cache_metrics:daily_misses:{today}:{cache_type}"
            daily_misses = cache.get(daily_key, 0)
            cache.set(daily_key, daily_misses + 1, 86400)
            
        except Exception as e:
            logger.error(f"Error recording cache miss: {e}")
    
    @staticmethod
    def get_cache_hit_rate(cache_type: str) -> dict:
        """Get cache hit rate for a specific cache type."""
        try:
            hits_key = f"cache_metrics:hits:{cache_type}"
            misses_key = f"cache_metrics:misses:{cache_type}"
            
            hits = cache.get(hits_key, 0)
            misses = cache.get(misses_key, 0)
            total = hits + misses
            
            hit_rate = (hits / total * 100) if total > 0 else 0
            
            return {
                'cache_type': cache_type,
                'hits': hits,
                'misses': misses,
                'total_requests': total,
                'hit_rate_percentage': round(hit_rate, 2)
            }
        except Exception as e:
            logger.error(f"Error getting cache hit rate: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def get_all_cache_metrics() -> dict:
        """Get comprehensive cache metrics for all cache types."""
        try:
            metrics = {}
            total_hits = 0
            total_misses = 0
            total_savings = 0
            
            for cache_type in CacheMetrics.API_COSTS.keys():
                type_metrics = CacheMetrics.get_cache_hit_rate(cache_type)
                metrics[cache_type] = type_metrics
                
                if 'error' not in type_metrics:
                    hits = type_metrics['hits']
                    cost_per_call = CacheMetrics.API_COSTS[cache_type]
                    savings = hits * cost_per_call
                    
                    type_metrics['estimated_savings_usd'] = round(savings, 4)
                    type_metrics['cost_per_call_usd'] = cost_per_call
                    
                    total_hits += hits
                    total_misses += type_metrics['misses']
                    total_savings += savings
            
            overall_hit_rate = (total_hits / (total_hits + total_misses) * 100) if (total_hits + total_misses) > 0 else 0
            
            return {
                'individual_metrics': metrics,
                'overall_summary': {
                    'total_hits': total_hits,
                    'total_misses': total_misses,
                    'total_requests': total_hits + total_misses,
                    'overall_hit_rate_percentage': round(overall_hit_rate, 2),
                    'total_estimated_savings_usd': round(total_savings, 4)
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting all cache metrics: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def get_daily_metrics(date_str: str = None) -> dict:
        """Get cache metrics for a specific day."""
        try:
            if not date_str:
                date_str = datetime.now().strftime('%Y-%m-%d')
            
            daily_metrics = {}
            total_daily_hits = 0
            total_daily_misses = 0
            total_daily_savings = 0
            
            for cache_type in CacheMetrics.API_COSTS.keys():
                hits_key = f"cache_metrics:daily_hits:{date_str}:{cache_type}"
                misses_key = f"cache_metrics:daily_misses:{date_str}:{cache_type}"
                
                hits = cache.get(hits_key, 0)
                misses = cache.get(misses_key, 0)
                total = hits + misses
                
                hit_rate = (hits / total * 100) if total > 0 else 0
                cost_per_call = CacheMetrics.API_COSTS[cache_type]
                savings = hits * cost_per_call
                
                daily_metrics[cache_type] = {
                    'hits': hits,
                    'misses': misses,
                    'total_requests': total,
                    'hit_rate_percentage': round(hit_rate, 2),
                    'estimated_savings_usd': round(savings, 4)
                }
                
                total_daily_hits += hits
                total_daily_misses += misses
                total_daily_savings += savings
            
            overall_daily_hit_rate = (total_daily_hits / (total_daily_hits + total_daily_misses) * 100) if (total_daily_hits + total_daily_misses) > 0 else 0
            
            return {
                'date': date_str,
                'daily_metrics': daily_metrics,
                'daily_summary': {
                    'total_hits': total_daily_hits,
                    'total_misses': total_daily_misses,
                    'total_requests': total_daily_hits + total_daily_misses,
                    'overall_hit_rate_percentage': round(overall_daily_hit_rate, 2),
                    'total_estimated_savings_usd': round(total_daily_savings, 4)
                }
            }
        except Exception as e:
            logger.error(f"Error getting daily metrics: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def reset_metrics():
        """Reset all cache metrics (useful for testing or new tracking periods)."""
        try:
            # This is a basic implementation for LocMemCache
            # For Redis, you could use pattern-based deletion
            logger.warning("Metrics reset not fully implemented for LocMemCache. Consider clearing entire cache.")
            return {'status': 'warning', 'message': 'Use cache.clear() to reset all metrics'}
        except Exception as e:
            logger.error(f"Error resetting metrics: {e}")
            return {'error': str(e)}
