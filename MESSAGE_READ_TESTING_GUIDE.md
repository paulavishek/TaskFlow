# Message Read Feature - Quick Test Guide

## Setup
1. Make sure the server is running: `python manage.py runserver`
2. Have at least 2 users logged in (use different browsers/tabs)
3. Both users should be members of the same chat room

## Test Scenario 1: Basic Read Status

### Steps
1. **User A** sends a message: "Hello team"
2. Observe: Message shows "Read by 1/4" (only User A)
3. **User B** hovers over the message
4. **User B** clicks "Mark as Read"
5. Observe: Message updates to "Read by 2/4"
6. **User A** should see the count update to "2/4" in real-time

## Test Scenario 2: Read by All

### Steps
1. **User A** sends: "Please read this"
2. All 4 room members mark it as read
3. Observe: Message shows "✓✓ Read by all" with double-check icon
4. Button becomes grayed out and disabled

## Test Scenario 3: Notification Badge

### Steps
1. Start with an empty chat room
2. **User A** sends 3 messages
3. **User B** views notification badge in navbar
4. Observe: Badge shows "3" (unread messages)
5. **User B** marks 2 messages as read
6. Observe: Badge updates to "1"
7. **User B** marks the last message as read
8. Observe: Badge disappears
9. Navigate away and back
10. Observe: Badge is still gone (persists)

## Test Scenario 4: Real-time Synchronization

### Steps
1. Open chat room in 2 browser windows (same user or different users)
2. **Window 1**: Mark a message as read
3. **Window 2**: Observe the read count updates immediately (no refresh needed)
4. Message status synchronizes across both windows

## Test Scenario 5: Own Messages

### Steps
1. **User A** sends "My message"
2. Observe: User A's message shows "Mark as Read" button is NOT visible
3. Other users can mark it as read
4. Read count shows: "Read by 2/4" (not including User A)

## Test Scenario 6: Author Can See Delete, Not Mark as Read

### Steps
1. **User A** sends a message
2. User A hovers over it
3. Observe: Shows "Delete" button, NO "Mark as Read" button
4. **User B** hovers over same message
5. Observe: Shows "Mark as Read" button, NO "Delete" button

## Expected Outcomes

✅ Messages show accurate read count (e.g., "Read by 2/4")  
✅ "Mark as Read" button appears on hover for others' messages  
✅ Read count updates in real-time across all connected users  
✅ "Read by all" shows when all members have marked it  
✅ Double-check icon (✓✓) appears for fully read messages  
✅ Notification badge counts unread messages correctly  
✅ Badge decreases as messages are marked read  
✅ Badge disappears when no unread messages remain  
✅ Status persists after page refresh  
✅ Status synchronizes across browser tabs/windows

## Troubleshooting

### Badge not updating
- Check: Notification badge refresh interval (default 30 seconds)
- Try: Wait 30 seconds or refresh the page
- Try: Open browser console (F12) and manually call `updateUnreadMessageCount()`

### Read button not appearing
- Check: Make sure you're hovering over another user's message
- Check: You can't mark your own messages as read
- Try: Use different browsers/users to test

### Real-time sync not working
- Check: WebSocket connection status in browser console
- Check: Both users are in the same chat room
- Try: Refresh the page and try again

### Read count not updating
- Check: Make sure all users are in the same chat room
- Try: Close and reopen the chat room
- Try: Clear browser cache and reload

## Performance Notes

- Unread count updates: Every 30 seconds automatically
- WebSocket updates: Real-time when marking as read
- Database queries: Optimized with bulk operations
- No page reloads required for any operation

## Success Criteria

The feature is working correctly when:
1. Messages display accurate read counts
2. Buttons update immediately without page refresh
3. Notification badge reflects actual unread messages
4. All users see synchronized status updates
5. Read status persists across sessions
