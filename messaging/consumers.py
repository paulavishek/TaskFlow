import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatMessage, ChatRoom, TaskThreadComment, UserTypingStatus, Notification
from kanban.models import Task
from datetime import datetime


class ChatRoomConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time chat room messaging"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_room_{self.room_id}'
        self.user = self.scope['user']
        
        # Check if user is authorized
        if not self.user.is_authenticated:
            await self.close()
            return
        
        is_authorized = await self.is_user_authorized()
        if not is_authorized:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Notify others that user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_join',
                'username': self.user.username,
                'user_id': self.user.id
            }
        )
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Notify others that user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_leave',
                'username': self.user.username,
                'user_id': self.user.id
            }
        )
        
        # Remove typing status
        await self.remove_typing_status()
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'chat_message':
                await self.handle_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'stop_typing':
                await self.handle_stop_typing(data)
        
        except json.JSONDecodeError:
            pass
    
    async def handle_message(self, data):
        """Handle a chat message"""
        message_text = data.get('message', '').strip()
        
        if not message_text:
            return
        
        # Save message to database
        message_obj = await self.save_message(message_text)
        
        # Broadcast message to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message_send',
                'message_id': message_obj['id'],
                'username': self.user.username,
                'user_id': self.user.id,
                'message': message_text,
                'timestamp': message_obj['timestamp'],
                'mentioned_users': message_obj['mentioned_users']
            }
        )
        
        # Remove typing status after sending
        await self.remove_typing_status()
    
    async def handle_typing(self, data):
        """Handle user typing notification"""
        await self.update_typing_status()
        
        # Broadcast typing indicator
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_typing',
                'username': self.user.username,
                'user_id': self.user.id
            }
        )
    
    async def handle_stop_typing(self, data):
        """Handle user stop typing notification"""
        await self.remove_typing_status()
        
        # Broadcast stop typing
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_stop_typing',
                'username': self.user.username,
                'user_id': self.user.id
            }
        )
    
    # Message handlers for group_send
    async def chat_message_send(self, event):
        """Send a chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message_id': event['message_id'],
            'username': event['username'],
            'user_id': event['user_id'],
            'message': event['message'],
            'timestamp': event['timestamp'],
            'mentioned_users': event['mentioned_users']
        }))
    
    async def user_join(self, event):
        """Send user join notification"""
        await self.send(text_data=json.dumps({
            'type': 'user_join',
            'username': event['username'],
            'user_id': event['user_id']
        }))
    
    async def user_leave(self, event):
        """Send user leave notification"""
        await self.send(text_data=json.dumps({
            'type': 'user_leave',
            'username': event['username'],
            'user_id': event['user_id']
        }))
    
    async def user_typing(self, event):
        """Send typing indicator"""
        await self.send(text_data=json.dumps({
            'type': 'user_typing',
            'username': event['username'],
            'user_id': event['user_id']
        }))
    
    async def user_stop_typing(self, event):
        """Send stop typing notification"""
        await self.send(text_data=json.dumps({
            'type': 'user_stop_typing',
            'username': event['username'],
            'user_id': event['user_id']
        }))
    
    # Database operations
    @database_sync_to_async
    def is_user_authorized(self):
        """Check if user is authorized to access this room"""
        try:
            chat_room = ChatRoom.objects.get(id=self.room_id)
            return chat_room.members.filter(id=self.user.id).exists()
        except ChatRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, message_text):
        """Save message to database and extract mentions"""
        import re
        
        try:
            chat_room = ChatRoom.objects.get(id=self.room_id)
            message = ChatMessage.objects.create(
                chat_room=chat_room,
                author=self.user,
                content=message_text
            )
            
            # Extract and add mentioned users
            mentions = re.findall(r'@(\w+)', message_text)
            mentioned_users = []
            
            for mention in set(mentions):
                try:
                    mentioned_user = User.objects.get(username=mention)
                    message.mentioned_users.add(mentioned_user)
                    mentioned_users.append(mention)
                    
                    # Create notification for mentioned user
                    if mentioned_user != self.user:
                        Notification.objects.create(
                            recipient=mentioned_user,
                            sender=self.user,
                            notification_type='MENTION',
                            chat_message=message,
                            text=f'{self.user.username} mentioned you in {chat_room.name}'
                        )
                except User.DoesNotExist:
                    pass
            
            return {
                'id': message.id,
                'timestamp': message.created_at.isoformat(),
                'mentioned_users': mentioned_users
            }
        except ChatRoom.DoesNotExist:
            return {'id': None, 'timestamp': None, 'mentioned_users': []}
    
    @database_sync_to_async
    def update_typing_status(self):
        """Update user typing status"""
        try:
            chat_room = ChatRoom.objects.get(id=self.room_id)
            typing_status, created = UserTypingStatus.objects.get_or_create(
                chat_room=chat_room,
                user=self.user
            )
            return typing_status
        except ChatRoom.DoesNotExist:
            return None
    
    @database_sync_to_async
    def remove_typing_status(self):
        """Remove user typing status"""
        try:
            UserTypingStatus.objects.filter(
                chat_room_id=self.room_id,
                user=self.user
            ).delete()
        except:
            pass


class TaskCommentConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time task thread comments"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        self.room_group_name = f'task_thread_comments_{self.task_id}'
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        is_authorized = await self.is_user_authorized()
        if not is_authorized:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'comment':
                await self.handle_comment(data)
        except json.JSONDecodeError:
            pass
    
    async def handle_comment(self, data):
        """Handle a new comment"""
        comment_text = data.get('comment', '').strip()
        
        if not comment_text:
            return
        
        # Save comment to database
        comment_obj = await self.save_comment(comment_text)
        
        # Broadcast comment to task subscribers
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'comment_send',
                'comment_id': comment_obj['id'],
                'username': self.user.username,
                'user_id': self.user.id,
                'comment': comment_text,
                'timestamp': comment_obj['timestamp'],
                'mentioned_users': comment_obj['mentioned_users']
            }
        )
    
    async def comment_send(self, event):
        """Send a comment to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'new_comment',
            'comment_id': event['comment_id'],
            'username': event['username'],
            'user_id': event['user_id'],
            'comment': event['comment'],
            'timestamp': event['timestamp'],
            'mentioned_users': event['mentioned_users']
        }))
    
    @database_sync_to_async
    def is_user_authorized(self):
        """Check if user is authorized to access this task"""
        try:
            task = Task.objects.get(id=self.task_id)
            # Check if user is assigned, created task, or board member
            board = task.column.board
            return (
                task.assigned_to == self.user or 
                task.created_by == self.user or 
                board.members.filter(id=self.user.id).exists()
            )
        except Task.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_comment(self, comment_text):
        """Save comment to database and extract mentions"""
        import re
        
        try:
            task = Task.objects.get(id=self.task_id)
            comment = TaskThreadComment.objects.create(
                task=task,
                author=self.user,
                content=comment_text
            )
            
            # Extract and add mentioned users
            mentions = re.findall(r'@(\w+)', comment_text)
            mentioned_users = []
            
            for mention in set(mentions):
                try:
                    mentioned_user = User.objects.get(username=mention)
                    comment.mentioned_users.add(mentioned_user)
                    mentioned_users.append(mention)
                    
                    # Create notification for mentioned user
                    if mentioned_user != self.user:
                        Notification.objects.create(
                            recipient=mentioned_user,
                            sender=self.user,
                            notification_type='MENTION',
                            task_thread_comment=comment,
                            text=f'{self.user.username} mentioned you in a comment on task "{task.title}"'
                        )
                except User.DoesNotExist:
                    pass
            
            return {
                'id': comment.id,
                'timestamp': comment.created_at.isoformat(),
                'mentioned_users': mentioned_users
            }
        except Task.DoesNotExist:
            return {'id': None, 'timestamp': None, 'mentioned_users': []}
