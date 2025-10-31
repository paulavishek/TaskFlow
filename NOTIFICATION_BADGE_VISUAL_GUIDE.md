# Notification Badge - Quick Visual Guide

## Navigation Bar Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Digital Kanban  | Dashboard | Boards | AI Assistant | Messages [5]  ▼ User│
└─────────────────────────────────────────────────────────────────────────────┘
                                                              ↑
                                                        RED BADGE
                                                      (Unread Count)
```

## Badge States

### State 1: No Unread Messages
```
Messages  (badge hidden)
```

### State 2: Few Unread Messages
```
Messages [3]
         └─ Red badge showing count
```

### State 3: Many Unread Messages
```
Messages [99+]
         └─ Capped at 99+ for large numbers
```

## Behavior Flow

```
User Opens Application
        ↓
Badge loads on page
        ↓
JavaScript calls API endpoint
        ↓
API counts unread messages from last 24 hours
        ↓
Badge displays count (or hides if 0)
        ↓
Every 30 seconds: Auto-refresh count
        ↓
User opens a chat room → sees all messages
        ↓
Next refresh: Count decreases (messages already read)
```

## Real-Time Example

**Scenario**: Multiple team members in "Feature Planning" room

```
Timeline:
─────────────────────────────────────

11:00 AM
- Alice sends message: "Let's discuss the new feature"
- Badge shows [1]

11:05 AM
- Bob sends message: "Sure, I'm ready"
- Badge shows [2] (unless Alice has viewed room)

11:10 AM
- Charlie sends message: "Count me in too"
- Badge shows [3]

11:15 AM
- USER opens chat room and reads all messages
- Next 30-second refresh: Badge shows [0] or disappears

11:45 AM
- Dave sends message: "Update: feature is in progress"
- Badge shows [1] again
```

## How Count is Calculated

```
Algorithm:
─────────

For each room where user is a member:
  └─ Count messages from last 24 hours
     └─ Exclude messages authored by current user
        └─ Sum total across all rooms

Result: Total unread message count
```

## Feature Highlights

✨ **Smart Counting**
- Only counts last 24 hours (doesn't show ancient messages)
- Excludes your own messages
- Counts across all rooms you're a member of

⚡ **Fast & Efficient**
- Lightweight API call
- Only runs every 30 seconds
- Non-blocking fetch requests
- Works even on slow connections

🎨 **Visual Design**
- Bootstrap 5 red badge color
- Positioned at top-right of icon
- Uses Font Awesome icons
- Responsive on all devices

🔄 **Auto-Refresh**
- Updates automatically every 30 seconds
- No page reload needed
- Graceful error handling
- Works in background

## Integration Points

```
base.html
    ├── Navigation Bar
    │   └── Messages Link with Badge
    │
    └── JavaScript
        ├── updateUnreadMessageCount() function
        ├── DOMContentLoaded event listener
        └── 30-second interval timer


messaging/views.py
    └── get_unread_message_count(request)
        ├── Queries ChatRoom members
        ├── Counts messages (last 24 hours)
        └── Returns JSON response


messaging/urls.py
    └── Route: messages/unread-count/
        └── Maps to get_unread_message_count view
```

## Browser Developer Tools Testing

### Check API Response
```javascript
// In Browser Console:
fetch('/messages/messages/unread-count/')
  .then(r => r.json())
  .then(d => console.log(d))

// Expected output:
// {unread_count: 5}
```

### Test Badge Visibility
```javascript
// In Browser Console:
document.getElementById('unread-message-badge').style.display // Shows 'block' or 'none'
document.getElementById('unread-count').textContent // Shows the number
```

### Trigger Manual Refresh
```javascript
// In Browser Console:
updateUnreadMessageCount()
```

---

**Quick Test Steps**:
1. Open Dashboard (go to any page)
2. Open Browser DevTools (F12)
3. Go to Console tab
4. Run: `fetch('/messages/messages/unread-count/').then(r => r.json()).then(d => console.log(d))`
5. Check if badge appears in navbar
6. Have a teammate send a message
7. Wait ~30 seconds or run `updateUnreadMessageCount()` to refresh
8. Badge count should update
