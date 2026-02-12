# MESSAGING SYSTEM - QUICK REFERENCE & CODE LOCATIONS
## Exact File Locations of All Issues

---

## BACKEND (api.py)

### Issue #1: SQL Syntax Error - get_conversation()
**Location**: [api.py - line 15157](api.py#L15157)
**Problem**: Uses SQLite `?` instead of PostgreSQL `%s`
```python
# WRONG (Line 15157):
cur.execute('... ORDER BY sent_at ASC LIMIT ?', (..., limit))

# SHOULD BE:
cur.execute('... ORDER BY sent_at ASC LIMIT %s', (..., limit))
```
**Impact**: Crashes when fetching conversations on PostgreSQL

---

### Issue #2: Missing Database Columns in Message Table
**Location**: api.py init_db() function (around line 3571)
**Problem**: Message table missing columns referenced in delete code
- Missing: `is_deleted_by_sender`
- Missing: `is_deleted_by_recipient`  
- Missing: `deleted_at`

**Used in**:
- Line 15346: `is_deleted_by_sender = 1`
- Line 15350: `is_deleted_by_recipient = 1`
- Line 15355: `deleted_at = CURRENT_TIMESTAMP`

**Migration Needed**:
```python
ALTER TABLE messages ADD COLUMN is_deleted_by_sender BOOLEAN DEFAULT FALSE;
ALTER TABLE messages ADD COLUMN is_deleted_by_recipient BOOLEAN DEFAULT FALSE;
ALTER TABLE messages ADD COLUMN deleted_at TIMESTAMP;
```

---

### Issue #3: Missing Reply Endpoint
**Location**: api.py - MISSING (line ~15200 area)
**Problem**: No `/api/messages/<id>/reply` endpoint exists
**Should implement**:
```python
@app.route('/api/messages/<int:message_id>/reply', methods=['POST'])
def reply_to_message(message_id):
    # Get original message sender
    # Create new message from current user to original sender
    # Link via parent_message_id
    # Auto-mark original as read
```

---

### Issue #4: Missing Search Endpoint
**Location**: api.py - MISSING
**Problem**: No `/api/messages/search` endpoint
**Should implement**:
```python
@app.route('/api/messages/search', methods=['GET'])
def search_messages():
    # GET params: q, sender, start_date, end_date, limit, offset
    # Search in content + subject + sender
    # Return paginated results
```

---

### Issue #5: Clinician Message Endpoint - CSRF Not Verified in Frontend
**Location**: api.py line 18253 (endpoint requires CSRF)
**Problem**: Frontend function doesn't include CSRF token
```python
# API requires (line 18253):
token = request.headers.get('X-CSRF-Token')
if not token or not validate_csrf_token(token):
    return jsonify({'error': 'CSRF token invalid'}), 403

# But frontend sendNewMessage (line 15700) includes it
# Need dedicated sendClinicianMessage() for clinician tab
```

---

### Issue #6: Inbox Pagination Not Implemented in Backend
**Location**: api.py get_inbox() [lines 15027-15123]
**Problem**: Loads all conversations at once, no offset/limit support
```python
# Current: returns all conversations
# Need: offset = (page - 1) * limit
#       ORDER BY last_message_time DESC
#       LIMIT limit OFFSET offset
```

---

### Issue #7: No Message Notification System
**Location**: api.py line 15016
**Problem**: `send_notification()` called but unclear implementation
```python
send_notification(
    recipient,
    f"New message from {sender}: {subject if subject else content[:50]}",
    'dev_message'
)
```
**Need to ensure**: 
- Badge count updates
- Real-time notification delivery
- User gets alerted to new messages

---

## FRONTEND (templates/index.html)

### Issue #8: Clinician Message Form Missing Handler Function
**Location**: templates/index.html line 5976
**Problem**: Button calls `sendNewMessage()` but should call dedicated function
```html
<!-- Line 5976 -->
<button class="btn" onclick="sendNewMessage()" style="flex: 1;">📤 Send Message</button>
<!-- Should be: -->
<button class="btn" onclick="sendClinicianMessage()" style="flex: 1;">📤 Send Message</button>
```

**Elements for clinician messaging**:
- Input ID: `clinMessageRecipient` (line 5959)
- Input ID: `clinMessageSubject` (line 5965)
- Input ID: `clinMessageContent` (line 5971)

**Need to create**:
```javascript
async function sendClinicianMessage() {
    // Get values from clinMessage* IDs
    // POST to /api/clinician/message with CSRF token
    // Show status in messageSendStatus div
}
```

---

### Issue #9: Message Thread View is Stub
**Location**: templates/index.html line 15730
**Problem**: Function only shows alert, doesn't display thread
```javascript
// Line 15730:
async function viewMessageThread(withUser, context) {
    console.log(`Opening conversation with ${withUser} from ${context}`);
    alert(`Message thread with ${withUser} (detailed view coming soon)`);
}

// Should instead:
// 1. Fetch /api/messages/conversation/{withUser}
// 2. Create modal with full thread
// 3. Show reply input
// 4. Mark messages as read
```

---

### Issue #10: Message Modal Incomplete
**Location**: templates/index.html lines 15774-15920
**Problem**: Modal created in viewMessageConversation() but:
- No reply input section
- No reply button
- Modal closes on send (bad UX for threading)

**Should add to modal**:
```javascript
// After messages container:
// Reply section (hidden by default):
<div id="replySection" style="padding: 15px; border-top: 1px solid #ddd;">
    <label>Reply:</label>
    <textarea id="replyInput" placeholder="Type your response..." rows="3"></textarea>
    <button onclick="sendReply(withUser, messageModalId)">Send Reply</button>
</div>
```

---

### Issue #11: No Message Status Indicators
**Location**: templates/index.html lines 15601-15653 (sent messages display)
**Problem**: Shows read/unread but not sent/delivered status
```html
<!-- Line 15619 -->
<span style="background: ${msg.is_read ? '#4caf50' : '#999'};...
<!-- Shows only read status, not:
     - "✓ Sent" vs "✓✓ Delivered" vs "✓✓ Read" -->
```

---

### Issue #12: No Message Search UI
**Location**: templates/index.html messaging tab
**Problem**: No search box or search functionality
**Should add**:
```html
<!-- In messaging tab header -->
<input type="text" id="messageSearchBox" placeholder="🔍 Search messages...">
<button onclick="searchMessages()">Search</button>
<div id="searchResults"></div>
```

**Function needed**:
```javascript
async function searchMessages() {
    const query = document.getElementById('messageSearchBox').value;
    const response = await fetch(`/api/messages/search?q=${query}`);
    const results = await response.json();
    // Display results
}
```

---

### Issue #13: Conversation Context Lost on Refresh
**Location**: templates/index.html line 15774
**Problem**: Modal is temporary, closes on refresh/navigation
**Solution**: Store conversation state in sessionStorage
```javascript
sessionStorage.setItem('openConversation', withUser);
// On page load, check and re-open if needed
```

---

### Issue #14: Missing Reply Button in Conversation
**Location**: templates/index.html - viewMessageConversation() function
**Problem**: No button for inline replies
**Should add in modal message display**:
```html
<button class="reply-btn" onclick="replyToMessage(${msg.id})">↩️ Reply</button>
```

---

### Issue #15: CSRF Token Not in Clinician Message Request
**Location**: templates/index.html line 5976 (clinician send button)
**Problem**: sendNewMessage() function includes CSRF for user messages (line 15700)
```javascript
// Line 15700 - has CSRF token:
headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrfToken
}

// But clinician button calls same function which may fail
// Need separate sendClinicianMessage() with proper CSRF handling
```

---

## SUMMARY TABLE

| Issue # | File | Line | Severity | Fix Type | Status |
|---------|------|------|----------|----------|--------|
| 1 | api.py | 15157 | 🔴 CRITICAL | SQL Syntax | Not Fixed |
| 2 | api.py | 3571 | 🔴 CRITICAL | Migration | Not Fixed |
| 3 | api.py | ~15200 | 🟠 HIGH | New Endpoint | Not Built |
| 4 | api.py | N/A | 🟠 HIGH | New Endpoint | Not Built |
| 5 | api.py | 18253 | 🟠 HIGH | Frontend Link | Not Fixed |
| 6 | api.py | 15027 | 🟠 HIGH | Pagination | Not Fixed |
| 7 | api.py | 15016 | 🟡 MEDIUM | Verification | Unclear |
| 8 | index.html | 5976 | 🟠 HIGH | Function Link | Not Fixed |
| 9 | index.html | 15730 | 🟠 HIGH | Implementation | Stub Only |
| 10 | index.html | 15774 | 🟠 HIGH | UI Addition | Incomplete |
| 11 | index.html | 15619 | 🟡 MEDIUM | UI Enhancement | Not Added |
| 12 | index.html | N/A | 🟡 MEDIUM | Feature | Not Built |
| 13 | index.html | 15774 | 🟡 MEDIUM | State Mgmt | Not Fixed |
| 14 | index.html | 15799 | 🟠 HIGH | Button/Feature | Missing |
| 15 | index.html | 5976 | 🔴 CRITICAL | CSRF Handling | Broken |

---

## PRIORITY ORDER FOR FIXING

### Must Fix First (Critical)
1. **Issue #1**: SQL Syntax - GET conversation crashes
2. **Issue #2**: Database schema - DELETE operations fail
3. **Issue #15**: CSRF token - Clinician messages fail

### High Priority (System Breaking)
4. **Issue #3**: Reply endpoint - Can't reply to messages
5. **Issue #8**: Clinician UI function - Clinicians can't send
6. **Issue #9**: Thread view - Can't see conversations

### Medium Priority (Feature Complete)
7. **Issue #4**: Search endpoint - Can't find messages
8. **Issue #10**: Modal reply section - Threading broken
9. **Issue #6**: Pagination - Large inboxes slow

### Polish/Enhancement
10. **Issue #11**: Status indicators
11. **Issue #12**: Search UI
12. **Issue #13**: Conversation state
13. **Issue #14**: Reply button
14. **Issue #5**: Notification system

---

## IMPLEMENTATION SEQUENCE

```
1. Fix Database (30 min)
   → Add missing columns
   → Create indexes

2. Fix Backend APIs (3-4 hours)
   → Fix SQL syntax errors
   → Implement reply endpoint
   → Implement search endpoint
   → Fix pagination
   → Verify CSRF handling

3. Fix Frontend UI (3-4 hours)
   → Create sendClinicianMessage()
   → Implement viewMessageThread() modal
   → Add reply input to modal
   → Add search UI
   → Fix status indicators

4. Test Everything (2-3 hours)
   → Unit tests for endpoints
   → Integration tests for flows
   → Frontend testing
   → Verify no regressions

5. Document & Deploy (1 hour)
   → Update API docs
   → Create user guide
   → Commit to git
```

---

**Created**: February 2026  
**Last Updated**: [Current Date]  
**Comprehensive Prompt Location**: [COMPREHENSIVE_MESSAGING_FIX_PROMPT.md](COMPREHENSIVE_MESSAGING_FIX_PROMPT.md)
