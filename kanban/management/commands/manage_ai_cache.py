"""
Management command for AI cache operations in TaskFlow

This command provides utilities to clear, inspect, and manage AI caches.
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
from kanban.utils.cache_utils import get_cache_stats
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Manage AI caches for cost optimization'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all AI caches',
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Display cache statistics',
        )
        parser.add_argument(
            '--clear-type',
            type=str,
            help='Clear specific cache type (task_description, comments_summary, board_analytics, etc.)',
        )
        parser.add_argument(
            '--settings',
            action='store_true',
            help='Display current cache settings',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_all_caches()
        elif options['clear_type']:
            self.clear_cache_type(options['clear_type'])
        elif options['stats']:
            self.show_cache_stats()
        elif options['settings']:
            self.show_cache_settings()
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Please specify an action: --clear, --stats, --clear-type, or --settings'
                )
            )

    def clear_all_caches(self):
        """Clear all AI caches."""
        try:
            cache.clear()
            self.stdout.write(
                self.style.SUCCESS('Successfully cleared all AI caches')
            )
            logger.info("All AI caches cleared via management command")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error clearing caches: {e}')
            )
            logger.error(f"Error clearing AI caches: {e}")

    def clear_cache_type(self, cache_type):
        """Clear caches of a specific type."""
        try:
            # Note: With hashed keys, we can't easily clear by pattern in LocMemCache
            # This would work better with Redis and pattern matching
            self.stdout.write(
                self.style.WARNING(
                    f'Clearing specific cache type "{cache_type}" is not directly supported '
                    'with the current LocMemCache backend. Consider using Redis for '
                    'production with pattern-based cache clearing.'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    'For now, use --clear to clear all caches.'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error clearing cache type {cache_type}: {e}')
            )

    def show_cache_stats(self):
        """Display cache statistics."""
        try:
            stats = get_cache_stats()
            self.stdout.write(
                self.style.SUCCESS('=== AI Cache Statistics ===')
            )
            for key, value in stats.items():
                self.stdout.write(f'{key}: {value}')
            
            # Try to get some additional info
            try:
                # Test cache functionality
                test_key = 'cache_test_key'
                cache.set(test_key, 'test_value', 1)
                test_result = cache.get(test_key)
                cache.delete(test_key)
                
                if test_result == 'test_value':
                    self.stdout.write(
                        self.style.SUCCESS('Cache is functioning properly')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('Cache test failed')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Cache test error: {e}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error getting cache stats: {e}')
            )

    def show_cache_settings(self):
        """Display current cache settings."""
        try:
            self.stdout.write(
                self.style.SUCCESS('=== AI Cache Settings ===')
            )
            
            # Show cache backend configuration
            cache_config = settings.CACHES.get('default', {})
            self.stdout.write(f"Backend: {cache_config.get('BACKEND', 'Not configured')}")
            self.stdout.write(f"Location: {cache_config.get('LOCATION', 'Default')}")
            self.stdout.write(f"Default Timeout: {cache_config.get('TIMEOUT', 'Not set')} seconds")
            
            # Show AI-specific cache timeouts
            ai_timeouts = getattr(settings, 'AI_CACHE_TIMEOUT', {})
            if ai_timeouts:
                self.stdout.write('\n=== AI Cache Timeouts ===')
                for cache_type, timeout in ai_timeouts.items():
                    hours = timeout // 3600
                    minutes = (timeout % 3600) // 60
                    self.stdout.write(f"{cache_type}: {timeout}s ({hours}h {minutes}m)")
            else:
                self.stdout.write('\nNo AI-specific cache timeouts configured')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error showing cache settings: {e}')
            )
