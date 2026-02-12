# MESSAGING SYSTEM ARCHITECTURE & DATA FLOW DIAGRAMS

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         HEALING SPACE                            │
│                    Messaging System Architecture                 │
└─────────────────────────────────────────────────────────────────┘

┌────────────────┐
│   FRONTEND     │
├────────────────┤
│ HTML/JS (SPA)  │  Send Message
├────────────────┤  View Inbox
│ - Message Tab  │  Open Thread
│ - Inbox        │  Search
│ - Sent         │  Delete
│ - New Message  │  Reply
│ - Thread Modal │
└────────┬────────┘
         │ REST API + CSRF Token
         │
         ▼
┌─────────────────────────────────────────┐
│         BACKEND (Flask/Python)          │
├─────────────────────────────────────────┤
│  Authentication (Session)                │
│  CSRF Protection (token validation)      │
│  Rate Limiting (per-user, per-IP)       │
│  Access Control (role-based)             │
├─────────────────────────────────────────┤
│         MESSAGE ENDPOINTS                │
├─────────────────────────────────────────┤
│ POST   /api/messages/send                │ → Create message
│ GET    /api/messages/inbox               │ → List conversations
│ GET    /api/messages/sent                │ → List sent messages
│ GET    /api/messages/conversation/{user} │ → Get thread
│ POST   /api/messages/{id}/reply          │ → Reply to message
│ GET    /api/messages/search              │ → Search messages
│ PATCH  /api/messages/{id}/read           │ → Mark as read
│ DELETE /api/messages/{id}                │ → Soft delete
│ POST   /api/clinician/message            │ → Clinician send
└──────┬────────────────────────────────────┘
       │ Database Queries
       │
       ▼
┌────────────────────────────────────────┐
│       PostgreSQL Database               │
├────────────────────────────────────────┤
│ TABLE: messages                          │
│ ├── id (PK)                              │
│ ├── sender_username (FK)                 │
│ ├── recipient_username (FK)              │
│ ├── subject                              │
│ ├── content                              │
│ ├── parent_message_id (for threads)      │
│ ├── is_read                              │
│ ├── read_at                              │
│ ├── sent_at                              │
│ ├── is_deleted_by_sender ⚠️ MISSING     │
│ ├── is_deleted_by_recipient ⚠️ MISSING  │
│ └── deleted_at ⚠️ MISSING               │
│                                          │
│ INDEXES:                                 │
│ ├── idx_messages_sender                  │
│ ├── idx_messages_recipient               │
│ └── idx_messages_sent_at                 │
│                                          │
│ RELATED TABLES:                          │
│ ├── users (sender/recipient FK)          │
│ ├── patient_approvals (clinician auth)   │
│ └── audit_log (message actions)          │
└────────────────────────────────────────┘
```

---

## Message Send Flow (User to User)

```
USER A                          API                        DATABASE
   │                            │                            │
   ├─ Click Send Message        │                            │
   │  - Fill recipient, content │                            │
   ├─────────────────────────────────────────────────────────┤
   │ POST /api/messages/send                                 │
   │ {                                                        │
   │   recipient: "user_b",                                  │
   │   subject: "...",                                       │
   │   content: "...",                                       │
   │   X-CSRF-Token: "token123"                              │
   │ }                                                        │
   │                            ├─ Validate auth             │
   │                            ├─ Validate CSRF token       │
   │                            ├─ Validate input (length)   │
   │                            ├─ Check recipient exists    │
   │                            ├─ Check role permissions    │
   │                            ├─────────────────────────────────┤
   │                            │ INSERT INTO messages (...)  │
   │                            │                            │
   │                            │ ← returns message_id       │
   │                            ├─ log_event() for audit    │
   │                            ├─ send_notification()       │
   │                            │                            │
   │ ← 201 Created + message_id │                            │
   ├─ Show success message      │                            │
   ├─ Clear form                │                            │
   └─ Reload sent messages      │                            │

USER B
   │
   ├─ Receives notification    │
   │  [New message from User A]│
   ├─ Sees inbox badge: (1)    │
   ├─ Clicks Inbox tab         │
   │  GET /api/messages/inbox  │
   │                            ├─ Query all conversations  │
   │                            │ ← [User A: 1 unread]      │
   │ ← Conversation displayed   │                            │
   ├─ Clicks conversation      │
   │  GET /api/messages/       │
   │   conversation/user_a     │
   │                            ├─ Mark messages as read    │
   │                            │ UPDATE is_read = 1        │
   │ ← Conversation thread      │                            │
   │  shown in modal            │                            │
   └─ Reads message            │                            │

USER A
   │
   ├─ Checks sent messages     │
   │  GET /api/messages/sent   │
   │                            ├─ Query sender_username=A  │
   │ ← Shows: "To: User B"      │                            │
   │  "✓✓ Read" (blue status)   │ read_at timestamp set      │
   └─ Knows message was read   │
```

---

## Message Reply Flow (Threading)

```
USER A (Original Sender)       API                      DATABASE
   │
   ├─ Send initial message
   │  INSERT message to USER B
   │  ← message_id = 123
   │
USER B (Recipient)
   │
   ├─ Open conversation         │
   │  GET /api/messages/        │
   │   conversation/user_a      │
   │                            ├─ SELECT * WHERE ... │
   │                            │ ← [msg 123 from A]  │
   │ ← Shows message 123        │
   │
   ├─ Click "Reply"             │
   │  ├─ Input appears          │
   │  ├─ Type reply content     │
   │  ├─ Click Send             │
   │                            │
   │  POST /api/messages/123/   │
   │   reply {content: "..."}   │
   │                            ├─ Get parent message │
   │                            ├─ Verify recipient   │
   │                            ├─ INSERT new message │
   │                            │  parent_msg_id=123  │
   │ ← 201 Created              │ ← message_id = 124  │
   │ ├─ Append reply to modal   │
   │ ├─ Send notification to A  │
   │ └─ Update unread badge     │
   │
USER A (Thread Continuity)
   │
   ├─ Get notification          │
   │  [User B replied]          │
   │
   ├─ Click conversation        │
   │  GET /api/messages/        │
   │   conversation/user_b      │
   │                            ├─ SELECT * WHERE    │
   │                            │  (sender/recipient) │
   │                            │ ← [msg 123, 124]   │
   │ ← Shows both:              │
   │  ├─ Msg 123 (original)     │
   │  └─ Msg 124 (reply)        │ Chronological order
   │
   └─ Conversation appears      │
      as thread (not separate)  │
```

---

## Search Message Flow

```
USER A                          API                      DATABASE
   │
   ├─ Click Search box
   ├─ Type: "budget meeting"
   ├─────────────────────────────────────────────────────┤
   │ GET /api/messages/search?q=budget&limit=20         │
   │                            │                        │
   │                            ├─ Validate input       │
   │                            ├─ Query content LIKE   │
   │                            │  %budget%             │
   │                            ├─────────────────────────┤
   │                            │ SELECT * FROM messages │
   │                            │ WHERE content LIKE ... │
   │                            │   AND sender=A         │
   │                            │   OR recipient=A       │
   │                            │ ORDER BY sent_at DESC  │
   │                            │                        │
   │                            │ ← 3 matches found      │
   │ ← Results display:         │                        │
   │  1. "Budget for Q1..."     │                        │
   │     From: manager          │                        │
   │  2. "Meeting notes..."     │                        │
   │     From: team lead        │                        │
   │  3. "Budget approved"      │                        │
   │     From: user_c           │                        │
   │
   ├─ Click result 1
   │  GET /api/messages/       │
   │   conversation/manager    │
   │                            ├─ Load full thread
   │ ← Opens conversation       │
   │  modal with manager        │
   │
   └─ Can now reply or delete  │
```

---

## Clinician Message Flow (Special Case)

```
CLINICIAN                       API                      DATABASE
   │
   ├─ Login as clinician       │
   ├─ Navigate to patients     │
   │  GET /api/clinician/      │
   │   patients (with messages) │
   │                            ├─ Query patient_approvals │
   │                            │  WHERE clinician=C    │
   │ ← Shows assigned patients  │
   │
   ├─ Select patient "john"    │
   ├─ Click "Send Message"     │
   │
   ├─────────────────────────────────────────────────┤
   │ POST /api/clinician/message                     │
   │ {                                                │
   │   recipient_username: "john",                   │
   │   message: "How are you feeling?",              │
   │   X-CSRF-Token: "token456" ← CRITICAL!         │
   │ }                                                │
   │                            │                    │
   │                            ├─ Validate auth    │
   │                            ├─ Check CSRF token │
   │                            ├─ Verify clinician │
   │                            │  is assigned to   │
   │                            │  john (patient_   │
   │                            │  approvals check) │
   │                            │                   │
   │                            ├─ Validate message │
   │                            │  (max 10000 chars)│
   │                            │                   │
   │                            ├─────────────────────┤
   │                            │ INSERT INTO messages│
   │                            │  sender=C,         │
   │                            │  recipient=john    │
   │                            │                    │
   │                            │ ← message_id=456  │
   │                            │                   │
   │                            ├─ log_event(C,    │
   │                            │  'clinician...') │
   │ ← 201 Created              │                   │
   │ ├─ Show success message    │                   │
   │ └─ Clear input             │                   │
   │
   ├─ View sent messages        │
   │  GET /api/messages/sent    │
   │                            ├─ Query sender=C   │
   │ ← Shows:                   │
   │  "To: john (patient)"      │
   │  "✓✓ Read" badge if john  │
   │  has opened it             │

PATIENT (john)
   │
   ├─ Gets notification         │
   │  [New message from Dr C]   │
   │
   ├─ Open inbox                │
   │  GET /api/messages/inbox   │
   │                            ├─ Query all senders │
   │ ← Sees conversation with C │                    │
   │
   ├─ Click conversation        │
   │  GET /api/messages/        │
   │   conversation/clinician_c │
   │                            ├─ SELECT * WHERE   │
   │                            │  (john sent msg   │
   │                            │   OR received)    │
   │                            │ ← Message from C  │
   │ ← Shows message            │
   │
   ├─ Click Reply               │
   │  POST /api/messages/       │
   │   {msg_id}/reply           │
   │                            ├─ Verify john is   │
   │                            │  recipient        │
   │                            ├─ INSERT reply     │
   │                            │  parent=msg_id    │
   │ ← Reply sent               │
   │
   └─ Send notification to C    │
      [john replied]            │
```

---

## Security & CSRF Token Flow

```
FRONTEND                        BACKEND
(Browser)                       (API)
   │
   ├─ On Page Load
   ├─────────────────────────────────────────┤
   │ GET /api/csrf-token                     │
   │                            ├─ Generate  │
   │                            │  new token │
   │                            │ ← csrfToken│
   │ Store in JS variable:      │
   │ let csrfToken = "xyz123"   │
   │
   ├─ Send Message
   │  Form submission            │
   ├─────────────────────────────────────────┤
   │ POST /api/messages/send                 │
   │ Headers: {                              │
   │   'X-CSRF-Token': csrfToken,  ← Include│
   │   'Content-Type': 'application/json'    │
   │ }                                       │
   │ Body: {recipient, content, ...}        │
   │                            │           │
   │                            ├─ Extract  │
   │                            │  token    │
   │                            │  from     │
   │                            │  header   │
   │                            ├─ Validate│
   │                            │  token   │
   │                            ├─ Check   │
   │                            │  matches │
   │                            │  session │
   │                            │           │
   │                            ├─ If valid│
   │                            │ ← 201    │
   │ ├─ Show success            │  Created │
   │ └─ Update UI               │           │
   │                            │
   │                            ├─ If invalid
   │ ← 403 Forbidden            │
   │ ├─ Show error: "CSRF failed"
   │ └─ Don't update UI
```

---

## Message Deletion Flow (Soft Delete)

```
USER A (Sender)                 API                      DATABASE
   │
   ├─ See message they sent     │
   ├─ Click Delete button       │
   │                            │
   │  DELETE /api/messages/123  │
   │                            ├─ Verify user=sender │
   │                            ├─ UPDATE messages    │
   │                            │ SET                 │
   │                            │  is_deleted_by_     │
   │                            │  sender = 1         │
   │                            │ WHERE id=123        │
   │ ← 204 No Content           │                     │
   │ ├─ Message disappears      │                     │
   │  from sent list            │                     │
   │
USER B (Recipient)
   │
   ├─ Message still visible     │
   ├─ User B's copy still exists│
   │  in inbox                  │
   │
   ├─ User B also deletes       │
   │  DELETE /api/messages/123  │
   │                            ├─ Verify user=rcpt  │
   │                            ├─ UPDATE messages   │
   │                            │ SET                │
   │                            │  is_deleted_by_    │
   │                            │  recipient = 1     │
   │                            ├─ Check if both     │
   │                            │  deleted:          │
   │                            │  is_deleted_by_    │
   │                            │  sender = 1 AND    │
   │                            │  is_deleted_by_    │
   │                            │  recipient = 1     │
   │                            ├─ UPDATE messages   │
   │                            │ SET                │
   │                            │  deleted_at =      │
   │                            │  NOW()             │
   │ ← 204 No Content           │                    │
   │
   ├─ Now hidden from:          │
   │  - User A's sent list      │
   │  - User B's inbox          │
   │  - Search results          │
   │
   └─ But NOT permanently
      deleted (recovery possible)
```

---

## Data Model - Message Table

### Current Schema (INCOMPLETE)
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    sender_username VARCHAR(255) REFERENCES users(username),
    recipient_username VARCHAR(255) REFERENCES users(username),
    subject VARCHAR(255),
    content TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- MISSING COLUMNS ⚠️
    -- is_deleted_by_sender BOOLEAN DEFAULT FALSE;
    -- is_deleted_by_recipient BOOLEAN DEFAULT FALSE;
    -- deleted_at TIMESTAMP NULL;
    -- parent_message_id INTEGER (for threading)
);
```

### Fixed Schema (COMPLETE)
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    sender_username VARCHAR(255) NOT NULL REFERENCES users(username),
    recipient_username VARCHAR(255) NOT NULL REFERENCES users(username),
    subject VARCHAR(255),
    content TEXT NOT NULL,
    parent_message_id INTEGER REFERENCES messages(id),  -- For threading
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted_by_sender BOOLEAN DEFAULT FALSE,         -- ✅ ADDED
    is_deleted_by_recipient BOOLEAN DEFAULT FALSE,      -- ✅ ADDED
    deleted_at TIMESTAMP NULL,                          -- ✅ ADDED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_messages_sender ON messages(sender_username);
CREATE INDEX idx_messages_recipient ON messages(recipient_username);
CREATE INDEX idx_messages_sent_at ON messages(sent_at DESC);
CREATE INDEX idx_messages_parent ON messages(parent_message_id);
CREATE INDEX idx_messages_not_deleted ON messages(deleted_at) WHERE deleted_at IS NULL;
```

---

## System States & Transitions

```
┌─────────────────────────────────┐
│   MESSAGE LIFECYCLE             │
└─────────────────────────────────┘

[CREATED]
   │ INSERT INTO messages
   │ is_read=FALSE
   │
   ├─ For sender: Immediately "sent"
   │
   ▼
[UNREAD by RECIPIENT]
   │ Recipient hasn't opened conversation yet
   │ Appears in inbox with unread badge
   │
   ▼
[READ by RECIPIENT]
   │ PATCH /api/messages/{id}/read
   │ is_read=TRUE, read_at=NOW()
   │ Sender sees "✓✓ Read" status
   │
   ├─ Deleted by sender (before recipient reads):
   │  is_deleted_by_sender=TRUE
   │  Still visible to recipient
   │
   ├─ Deleted by recipient:
   │  is_deleted_by_recipient=TRUE
   │  Still visible to sender
   │
   ▼
[BOTH DELETED]
   │ is_deleted_by_sender=TRUE AND
   │ is_deleted_by_recipient=TRUE
   │
   ▼
[HIDDEN] (soft deleted)
   │ deleted_at=NOW()
   │ Doesn't appear in queries (WHERE deleted_at IS NULL)
   │ But record still in database
   │
   └─ Can be restored if needed
     (admin/recovery function)
```

---

## Performance Considerations

```
┌─────────────────────────────────────────────────────────────┐
│           QUERY PERFORMANCE WITH INDEXES                   │
└─────────────────────────────────────────────────────────────┘

SLOW ❌ (Without indexes)
GET /api/messages/inbox
  └─ SELECT with 1000+ rows
  └─ Full table scan
  └─ Response time: 3-5 seconds
  └─ Database CPU: 80%

FAST ✅ (With indexes)
GET /api/messages/inbox
  └─ SELECT using idx_messages_recipient
  └─ Only relevant rows scanned
  └─ Response time: < 100ms
  └─ Database CPU: 5%

OPTIMIZATION TECHNIQUES:
1. Index on sender_username
2. Index on recipient_username
3. Index on sent_at DESC (for sorting)
4. Partial index: WHERE deleted_at IS NULL
5. Pagination: LIMIT 20 OFFSET 0
6. Caching: Message count in session
```

---

## Error Handling Flows

```
┌─────────────────────────────────────────────────────────────┐
│               ERROR SCENARIOS & RESPONSES                   │
└─────────────────────────────────────────────────────────────┘

USER SENDS MESSAGE → API

CHECKS:
  ├─ Is user authenticated? → No → 401 Unauthorized
  │
  ├─ Is recipient provided? → No → 400 Bad Request
  │
  ├─ Does recipient exist? → No → 404 Not Found
  │
  ├─ Is message too long? → Yes → 400 Bad Request
  │
  ├─ Is CSRF token valid? → No → 403 Forbidden
  │
  ├─ Can user message recipient? → No → 403 Forbidden
  │    (user→clinician not allowed)
  │
  ├─ Rate limit exceeded? → Yes → 429 Too Many Requests
  │
  └─ All checks pass → INSERT → 201 Created ✓


VIEW CONVERSATION → API

CHECKS:
  ├─ Is user authenticated? → No → 401 Unauthorized
  │
  ├─ Is conversation participant? → No → 403 Forbidden
  │    (only sender/recipient can view)
  │
  ├─ Database error? → Yes → 500 Internal Error
  │    (don't expose DB details)
  │
  └─ All checks pass → SELECT → 200 OK ✓


DELETE MESSAGE → API

CHECKS:
  ├─ Is user authenticated? → No → 401 Unauthorized
  │
  ├─ Does message exist? → No → 404 Not Found
  │
  ├─ Is user sender or recipient? → No → 403 Forbidden
  │
  └─ All checks pass → UPDATE → 204 No Content ✓
```

---

**Diagram Version**: 1.0  
**Last Updated**: February 2026  
**Status**: Complete Messaging Architecture Documented
