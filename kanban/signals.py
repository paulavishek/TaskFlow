"""
Django signals for cache invalidation in TaskFlow

This module contains signal handlers that automatically invalidate
relevant AI caches when tasks, comments, or boards are modified.
"""

from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.core.cache import cache
import logging

from .models import Task, Comment, Board, Column
from .utils.cache_utils import invalidate_board_related_caches

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Task)
def invalidate_task_caches(sender, instance, created, **kwargs):
    """
    Invalidate relevant caches when a task is created or updated.
    """
    try:
        board_id = instance.column.board.id
        
        # Always invalidate board analytics cache when any task changes
        invalidate_board_related_caches(board_id)
        
        # If this is a significant update (not just a save), log it
        if not created:
            logger.info(f"Task {instance.id} updated - invalidated board {board_id} analytics cache")
        else:
            logger.info(f"Task {instance.id} created - invalidated board {board_id} analytics cache")
            
    except Exception as e:
        logger.error(f"Error invalidating task caches: {e}")


@receiver(post_delete, sender=Task)
def invalidate_task_caches_on_delete(sender, instance, **kwargs):
    """
    Invalidate relevant caches when a task is deleted.
    """
    try:
        board_id = instance.column.board.id
        invalidate_board_related_caches(board_id)
        logger.info(f"Task {instance.id} deleted - invalidated board {board_id} analytics cache")
    except Exception as e:
        logger.error(f"Error invalidating task caches on delete: {e}")


@receiver(post_save, sender=Comment)
def invalidate_comment_caches(sender, instance, created, **kwargs):
    """
    Invalidate comment summary cache when a new comment is added.
    """
    try:
        if created:
            task_id = instance.task.id
            # Since we use a timestamp-based cache key for comments,
            # the cache will automatically be invalidated when a new comment
            # is added because the timestamp changes
            logger.info(f"New comment added to task {task_id} - cache will auto-invalidate")
    except Exception as e:
        logger.error(f"Error handling comment cache invalidation: {e}")


@receiver(post_delete, sender=Comment)
def invalidate_comment_caches_on_delete(sender, instance, **kwargs):
    """
    Invalidate comment summary cache when a comment is deleted.
    """
    try:
        task_id = instance.task.id
        logger.info(f"Comment deleted from task {task_id} - cache will auto-invalidate")
    except Exception as e:
        logger.error(f"Error handling comment cache invalidation on delete: {e}")


@receiver(m2m_changed, sender=Task.labels.through)
def invalidate_task_label_caches(sender, instance, action, **kwargs):
    """
    Invalidate caches when task labels (especially Lean Six Sigma) are modified.
    """
    try:
        if action in ['post_add', 'post_remove', 'post_clear']:
            board_id = instance.column.board.id
            invalidate_board_related_caches(board_id)
            logger.info(f"Task {instance.id} labels changed - invalidated board {board_id} analytics cache")
    except Exception as e:
        logger.error(f"Error invalidating label caches: {e}")


@receiver(post_save, sender=Column)
def invalidate_column_caches(sender, instance, created, **kwargs):
    """
    Invalidate board caches when columns are modified.
    """
    try:
        board_id = instance.board.id
        invalidate_board_related_caches(board_id)
        
        if created:
            logger.info(f"Column {instance.id} created - invalidated board {board_id} analytics cache")
        else:
            logger.info(f"Column {instance.id} updated - invalidated board {board_id} analytics cache")
    except Exception as e:
        logger.error(f"Error invalidating column caches: {e}")


@receiver(post_delete, sender=Column)
def invalidate_column_caches_on_delete(sender, instance, **kwargs):
    """
    Invalidate board caches when columns are deleted.
    """
    try:
        board_id = instance.board.id
        invalidate_board_related_caches(board_id)
        logger.info(f"Column {instance.id} deleted - invalidated board {board_id} analytics cache")
    except Exception as e:
        logger.error(f"Error invalidating column caches on delete: {e}")
