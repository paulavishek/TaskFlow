from django.db import models
from django.contrib.auth.models import User
from kanban.models import Task, Board
from django.db.models import Q
from django.utils import timezone


class TaskThreadComment(models.Model):
    """Real-time comments on individual tasks with @mention support"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='thread_comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_thread_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # @mention support
    mentioned_users = models.ManyToManyField(User, related_name='mentioned_in_task_threads', blank=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['task', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author.username} on Task {self.task.id}"
    
    def get_mentioned_usernames(self):
        """Extract @mentions from content (format: @username)"""
        import re
        mentions = re.findall(r'@(\w+)', self.content)
        return list(set(mentions))  # Remove duplicates
    
    def notify_mentioned_users(self):
        """Create notifications for mentioned users"""
        for mention in self.get_mentioned_usernames():
            try:
                user = User.objects.get(username=mention)
                if user != self.author:
                    Notification.objects.create(
                        recipient=user,
                        sender=self.author,
                        notification_type='MENTION',
                        task_comment=self,
                        text=f'{self.author.username} mentioned you in a comment on task "{self.task.title}"'
                    )
            except User.DoesNotExist:
                pass


class ChatRoom(models.Model):
    """Board-level chat rooms for team synchronization"""
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='chat_rooms')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, related_name='chat_rooms', blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['board', 'name']
        indexes = [
            models.Index(fields=['board', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.board.name})"
    
    def get_room_group_name(self):
        """Get the channel group name for WebSocket"""
        return f'chat_room_{self.id}'


class ChatMessage(models.Model):
    """Messages in a chat room"""
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # @mention support
    mentioned_users = models.ManyToManyField(User, related_name='mentioned_in_chat', blank=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['chat_room', 'created_at']),
        ]
    
    def __str__(self):
        return f"Message by {self.author.username} in {self.chat_room.name}"
    
    def get_mentioned_usernames(self):
        """Extract @mentions from content (format: @username)"""
        import re
        mentions = re.findall(r'@(\w+)', self.content)
        return list(set(mentions))  # Remove duplicates
    
    def notify_mentioned_users(self):
        """Create notifications for mentioned users"""
        for mention in self.get_mentioned_usernames():
            try:
                user = User.objects.get(username=mention)
                if user != self.author:
                    Notification.objects.create(
                        recipient=user,
                        sender=self.author,
                        notification_type='MENTION',
                        chat_message=self,
                        text=f'{self.author.username} mentioned you in {self.chat_room.name}: "{self.content[:50]}"'
                    )
            except User.DoesNotExist:
                pass


class Notification(models.Model):
    """Notifications for mentions and activity"""
    NOTIFICATION_TYPES = [
        ('MENTION', 'Mention'),
        ('COMMENT', 'Comment Reply'),
        ('CHAT_MESSAGE', 'Chat Message'),
        ('ACTIVITY', 'Activity Update'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    text = models.TextField()
    
    # Links to related objects
    task_thread_comment = models.ForeignKey(TaskThreadComment, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    chat_message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} notification for {self.recipient.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save()


class UserTypingStatus(models.Model):
    """Track user typing status in chat rooms"""
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='typing_users')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_update = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['chat_room', 'user']
    
    def is_typing(self, timeout_seconds=10):
        """Check if user is still typing (not older than timeout)"""
        elapsed = (timezone.now() - self.last_update).total_seconds()
        return elapsed < timeout_seconds
    
    def __str__(self):
        return f"{self.user.username} typing in {self.chat_room.name}"
