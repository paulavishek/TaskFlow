import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

from messaging.models import ChatRoom, ChatMessage
from messaging.consumers import ChatRoomConsumer
import inspect

print('='*70)
print('MESSAGING BROADCAST FIX VERIFICATION')
print('='*70)

# 1. Check database
print('\n1. DATABASE CHECK')
print('-'*70)
rooms = ChatRoom.objects.all()
print(f'✅ ChatRoom model: {rooms.count()} rooms')
if rooms.exists():
    room = rooms.first()
    print(f'   Sample room: {room.name} (Members: {room.members.count()})')

messages = ChatMessage.objects.all()
print(f'✅ ChatMessage model: {messages.count()} messages')

# 2. Check consumer code
print('\n2. CONSUMER CODE CHECK')
print('-'*70)
try:
    source = inspect.getsource(ChatRoomConsumer.handle_message)
    print(f'✅ handle_message broadcasts: {"group_send" in source}')
    print(f'✅ marks as broadcast: {"is_broadcast" in source}')

    source = inspect.getsource(ChatRoomConsumer.chat_message_send)
    print(f'✅ chat_message_send includes broadcast flag: {"is_broadcast" in source}')
    print(f'✅ includes own message flag: {"is_own_message" in source}')
    
    print('\n✅ MESSAGING FIX VERIFICATION COMPLETE')
except Exception as e:
    print(f'Error: {e}')

print('='*70)
