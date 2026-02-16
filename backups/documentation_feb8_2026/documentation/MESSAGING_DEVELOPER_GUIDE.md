# Messaging System - Developer Quick Reference

## API Endpoints

### GET /api/messages/inbox
**Get messages received by user**
```bash
curl -X GET http://localhost:5000/api/messages/inbox \
  -H "Cookie: session=..." \
  -H "Content-Type: application/json"
```

**Response (200):**
```json
{
  "success": true,
  "conversations": [
    {
      "with_user": "therapist_name",
      "last_message_time": "2026-02-04T10:30:00",
      "last_message": "How are you feeling today?",
      "unread_count": 1
    }
  ],
  "total_unread": 1
}
```

---

### POST /api/messages/send
**Send a message**
```bash
curl -X POST http://localhost:5000/api/messages/send \
  -H "Cookie: session=..." \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: ..." \
  -d '{
    "recipient": "therapist_name",
    "subject": "Check-in",
    "content": "I am doing better this week"
  }'
```

**Response (201):**
```json
{
  "status": "sent",
  "message_id": 123,
  "recipient": "therapist_name",
  "sent_at": "2026-02-04T10:30:00"
}
```

**Permission Check:**
- Patient CANNOT send to clinician (returns 403)
- Everyone else can send to anyone
- Permission enforced in api.py lines 11519-11535

---

### GET /api/messages/sent (NEW)
**Get messages sent by user**
```bash
curl -X GET http://localhost:5000/api/messages/sent \
  -H "Cookie: session=..." \
  -H "Content-Type: application/json"
```

**Response (200):**
```json
{
  "success": true,
  "messages": [
    {
      "id": 123,
      "sender": "patient_username",
      "recipient": "therapist_name",
      "subject": "Check-in",
      "content": "I am doing better",
      "sent_at": "2026-02-04T10:30:00",
      "is_read": 1,
      "read_at": "2026-02-04T11:00:00"
    }
  ]
}
```

**Location:** api.py lines 11782-11811

---

### GET /api/messages/conversation/<username>
**Get specific conversation**
```bash
curl -X GET http://localhost:5000/api/messages/conversation/therapist_name \
  -H "Cookie: session=..." \
  -H "Content-Type: application/json"
```

---

### PATCH /api/messages/<id>/read
**Mark message as read**
```bash
curl -X PATCH http://localhost:5000/api/messages/123/read \
  -H "Cookie: session=..." \
  -H "Content-Type: application/json"
```

---

### GET /api/feedback/all (NEW)
**Get all feedback (DEVELOPER ONLY)**
```bash
curl -X GET http://localhost:5000/api/feedback/all \
  -H "Cookie: session=..." \
  -H "Content-Type: application/json"
```

**Response (200):**
```json
{
  "success": true,
  "feedback": [
    {
      "id": 1,
      "username": "patient_username",
      "user_role": "user",
      "category": "bug",
      "message": "App crashes on login",
      "status": "new",
      "created_at": "2026-02-04T10:00:00"
    }
  ]
}
```

**Response (403 - Non-developer):**
```json
{
  "error": "Access denied. This feature is for developers only."
}
```

**Location:** api.py lines 11824-11850

---

## JavaScript Functions

### switchMessageTab(tabName, buttonEl)
**Navigate between message subtabs**
```javascript
// Switch to sent messages tab
switchMessageTab('sent', document.querySelector('.message-subtab-btn'))

// Switch to inbox tab
switchMessageTab('inbox', document.querySelector('.message-subtab-btn'))

// Switch to new message tab
switchMessageTab('new', document.querySelector('.message-subtab-btn'))
```

**Location:** templates/index.html line 13294

---

### loadMessagesInbox()
**Load and display inbox messages**
```javascript
// Called when switching to inbox tab
loadMessagesInbox()

// Fetches from GET /api/messages/inbox
// Displays in #messagesInboxContainer
// Shows unread badges and timestamps
```

**Location:** templates/index.html line 13322

---

### loadMessagesSent()
**Load and display sent messages**
```javascript
// Called when switching to sent tab
loadMessagesSent()

// Fetches from GET /api/messages/sent
// Displays in #messagesSentContainer
// Shows read status (✓ or ⏳)
```

**Location:** templates/index.html line 13372

---

### sendNewMessage()
**Send a new message**
```javascript
// Called when clicking send button
sendNewMessage()

// Gets values from:
// - #messageRecipient
// - #messageSubject
// - #messageContent

// POSTs to /api/messages/send
// Shows success/error in #messageSendStatus
// Clears form on success
```

**Location:** templates/index.html line 13422

---

### loadFeedback()
**Load all feedback (developer only)**
```javascript
// Called when clicking feedback tab in developer dashboard
loadFeedback()

// Fetches from GET /api/feedback/all
// Displays in #feedbackContainer
// Shows category and status badges
// Supports filtering by category and status
```

**Location:** templates/index.html line 13128

---

### filterFeedback()
**Filter feedback by category/status**
```javascript
// Called when clicking filter button
filterFeedback()

// Reads values from:
// - #feedbackCategoryFilter
// - #feedbackStatusFilter

// Client-side filtering of displayed feedback
// Hides non-matching items
```

**Location:** templates/index.html line 13168

---

## Database Schema

### messages table
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_username TEXT NOT NULL,
    recipient_username TEXT NOT NULL,
    subject TEXT,
    content TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    read_at DATETIME,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    deleted_at DATETIME,
    is_deleted_by_sender INTEGER DEFAULT 0,
    is_deleted_by_recipient INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(sender_username) REFERENCES users(username),
    FOREIGN KEY(recipient_username) REFERENCES users(username),
    CHECK (sender_username != recipient_username)
)
```

### feedback table
```sql
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    role TEXT,
    category TEXT,
    message TEXT,
    status TEXT DEFAULT 'new',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(username) REFERENCES users(username)
)
```

---

## Testing

### Run All Messaging Tests
```bash
GROQ_API_KEY="test-key" pytest -v tests/test_messaging.py
```

### Run Specific Test Class
```bash
GROQ_API_KEY="test-key" pytest -v tests/test_messaging.py::TestMessagesSentEndpoint
GROQ_API_KEY="test-key" pytest -v tests/test_messaging.py::TestFeedbackAllEndpoint
```

### Run With Full Output
```bash
GROQ_API_KEY="test-key" pytest -xvs tests/test_messaging.py
```

---

## Permission Matrix

| Action | Patient | Clinician | Therapist | Admin | Developer |
|--------|---------|-----------|-----------|-------|-----------|
| Send to therapist | ✅ | ✅ | ✅ | ✅ | ✅ |
| Send to clinician | ❌ | ✅ | ✅ | ✅ | ✅ |
| Send to patient | ❌ | ✅ | ✅ | ✅ | ✅ |
| Send to user | ✅ | ✅ | ✅ | ✅ | ✅ |
| Send to dev | ✅ | ✅ | ✅ | ✅ | ✅ |
| View own inbox | ✅ | ✅ | ✅ | ✅ | ✅ |
| View own sent | ✅ | ✅ | ✅ | ✅ | ✅ |
| View all feedback | ❌ | ❌ | ❌ | ❌ | ✅ |
| Mark as read | ✅ | ✅ | ✅ | ✅ | ✅ |
| Delete message | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## Common Debugging

### Check if messages are being saved
```python
import sqlite3
conn = sqlite3.connect('therapist_app.db')
cur = conn.cursor()
messages = cur.execute('SELECT * FROM messages').fetchall()
print(f"Total messages: {len(messages)}")
```

### Check feedback table
```python
feedback = cur.execute('SELECT * FROM feedback').fetchall()
print(f"Total feedback: {len(feedback)}")
```

### Verify permissions are working
```bash
# Try to send message as patient to clinician (should fail)
curl -X POST http://localhost:5000/api/messages/send \
  -H "Cookie: session=patient_session" \
  -d '{"recipient": "clinician", "content": "test"}'
# Should return 403 Forbidden
```

### Check session is valid
```bash
curl -X GET http://localhost:5000/api/messages/inbox \
  -H "Cookie: session=invalid_session"
# Should return 401 Unauthorized
```

---

## File Locations

| Component | File | Lines |
|-----------|------|-------|
| GET /api/messages/sent | api.py | 11782-11811 |
| GET /api/feedback/all | api.py | 11824-11850 |
| Permission checks | api.py | 11519-11535 |
| Patient messages UI | templates/index.html | 4625-4687 |
| Clinician messages UI | templates/index.html | 5019-5067 |
| Developer feedback UI | templates/index.html | 5049-5072 |
| Messaging JS functions | templates/index.html | 13108-13349 |
| Feedback JS functions | templates/index.html | 13108-13194 |
| Tests - Messaging | tests/test_messaging.py | Full file |
| Tests - Role access | tests/test_role_access.py | Full file |

---

## Troubleshooting

### Endpoint returns 401
**Problem:** User not authenticated  
**Solution:** Check session cookie is valid, user is logged in

### Endpoint returns 403
**Problem:** User doesn't have permission  
**Solution:** Check role permissions matrix, verify sender/recipient relationship

### Messages don't appear
**Problem:** Messages not loading in UI  
**Solution:** 
1. Check /api/messages/inbox returns 200
2. Check console for JavaScript errors
3. Verify message table has data
4. Check is_deleted_by_sender = 0

### Feedback not showing
**Problem:** Feedback tab shows no results  
**Solution:**
1. Verify user is a developer (role = 'developer')
2. Check /api/feedback/all returns 200
3. Check feedback table has data
4. Clear browser cache

---

## Performance Tips

- **Pagination:** Add LIMIT/OFFSET for large message volumes
- **Caching:** Cache recent conversations (Redis)
- **Indexes:** Add indexes on sender_username, recipient_username
- **Search:** Use full-text search for message content
- **Archive:** Move old messages to archive table

---

**Last Updated:** February 4, 2026  
**Version:** 1.0
