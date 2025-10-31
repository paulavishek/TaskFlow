from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # Messaging Hub
    path('', views.messaging_hub, name='hub'),
    
    # Chat Rooms
    path('board/<int:board_id>/rooms/', views.chat_room_list, name='chat_room_list'),
    path('board/<int:board_id>/rooms/create/', views.create_chat_room, name='create_chat_room'),
    path('room/<int:room_id>/', views.chat_room_detail, name='chat_room_detail'),
    
    # Messages
    path('room/<int:room_id>/send/', views.send_chat_message, name='send_chat_message'),
    path('room/<int:room_id>/history/', views.message_history, name='message_history'),
    
    # Task Thread Comments
    path('task/<int:task_id>/comments/', views.task_thread_comments, name='task_thread_comments'),
    path('task/<int:task_id>/comments/history/', views.task_comment_history, name='task_comment_history'),
    
    # Mentions
    path('mentions/', views.get_mentions, name='get_mentions'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/count/', views.get_unread_notification_count, name='get_unread_notification_count'),
    
    # Unread Messages
    path('messages/unread-count/', views.get_unread_message_count, name='get_unread_message_count'),
    
    # Delete Messages
    path('message/<int:message_id>/delete/', views.delete_chat_message, name='delete_chat_message'),
    path('room/<int:room_id>/clear/', views.clear_chat_room_messages, name='clear_chat_room_messages'),
]
