from django.urls import path
from messaging import consumers

websocket_urlpatterns = [
    path('ws/chat-room/<int:room_id>/', consumers.ChatRoomConsumer.as_asgi()),
    path('ws/task-comments/<int:task_id>/', consumers.TaskCommentConsumer.as_asgi()),
]
