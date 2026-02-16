# PHASE 3 IMPLEMENTATION - INTERNAL MESSAGING SYSTEM

**Start Date**: February 5, 2026  
**Target Duration**: 8 hours  
**Scope Decision**: Option B - Balanced (Feb 4, user approved)  
**Status**: 🟢 READY TO START  

---

## 📋 SCOPE & SPECIFICATION

### Feature: Internal Messaging System
**Purpose**: Enable secure communication between therapists, clinicians, admins, and users within the healing-space platform.

### Scope - Option B (Balanced - 8 Hours)
- ✅ Soft delete messages (not permanent)
- ✅ Read/unread tracking with timestamps
- ✅ Inbox view with conversation preview
- ✅ Conversation history retrieval (full thread)
- ✅ Role-based access control (3 user types)
- ❌ Real-time push notifications (Phase 5)
- ❌ Media attachments (Phase 6)
- ❌ Message search/filtering (Phase 6)
- ❌ Scheduled messages (Phase 6)

**Contrast to Other Options**:
- Option A (Minimal - 6h): No soft delete, no read tracking, basic endpoints only
- Option C (Full - 10h): Includes push notifications, search, scheduled messages
- **Chosen**: Option B balances functionality with timeline (8h is achievable in one sprint)

---

## 🗄️ DATABASE SCHEMA

### 1. New Table: `messages`

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_username TEXT NOT NULL,
    recipient_username TEXT NOT NULL,
    subject TEXT,  -- Short title (optional, e.g., "Patient Check-In")
    content TEXT NOT NULL,  -- Message body (max 5000 chars)
    is_read INTEGER DEFAULT 0,  -- 0=unread, 1=read
    read_at TIMESTAMP,  -- When recipient marked as read
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,  -- NULL=visible, timestamp=soft deleted
    is_deleted_by_sender INTEGER DEFAULT 0,  -- Track sender delete separately
    is_deleted_by_recipient INTEGER DEFAULT 0,  -- Track recipient delete separately
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY(sender_username) REFERENCES users(username),
    FOREIGN KEY(recipient_username) REFERENCES users(username),
    CHECK (sender_username != recipient_username)  -- Prevent self-messages
);

-- Indexes for performance
CREATE INDEX idx_messages_recipient ON messages(recipient_username, is_read);
CREATE INDEX idx_messages_conversation ON messages(sender_username, recipient_username);
CREATE INDEX idx_messages_deleted ON messages(deleted_at);
```

### 2. Migration Logic
- Add table to `init_db()` in [api.py](api.py)
- Use try/except pattern (never drop columns)
- Backward compatible (existing databases auto-migrate)

### 3. Example Data (for testing)
```python
# Test fixture: messages between therapist and user
therapist -> user: "How are you feeling today?"
user -> therapist: "Better, mood improved to 7/10"
therapist -> user: "Great! Let's explore..."
```

---

## 🔌 API ENDPOINTS (5 Total)

### Endpoint 1: Send Message
```
POST /api/messages/send
Required: Authorization header (session token)
Body:
{
    "recipient": "string (username)",
    "subject": "string (optional, max 100 chars)",
    "content": "string (required, max 5000 chars)"
}

Success Response (201):
{
    "message_id": 42,
    "sent_at": "2026-02-05T10:30:45Z",
    "status": "sent"
}

Errors:
- 400: Invalid recipient, missing content, message too long
- 401: Unauthorized (no session)
- 403: Forbidden (blocked user, role violation)
- 404: Recipient not found
```

### Endpoint 2: Get Inbox
```
GET /api/messages/inbox?page=1&limit=20&unread_only=false
Required: Authorization header
Query Params:
- page: 1-N (default 1)
- limit: 10-50 (default 20)
- unread_only: true|false (default false)

Success Response (200):
{
    "conversations": [
        {
            "with_user": "therapist_username",
            "last_message": "How are you feeling...",
            "last_message_time": "2026-02-05T10:30:45Z",
            "unread_count": 3,
            "is_latest_from_them": true
        },
        ...
    ],
    "total_unread": 5,
    "page": 1,
    "page_size": 20,
    "total_conversations": 7
}
```

### Endpoint 3: Get Conversation
```
GET /api/messages/conversation/<username>?limit=50
Required: Authorization header
Path Params:
- username: Target conversation partner

Success Response (200):
{
    "messages": [
        {
            "id": 42,
            "sender": "user_a",
            "recipient": "user_b",
            "content": "Hello...",
            "subject": null,
            "is_read": true,
            "read_at": "2026-02-05T10:35:00Z",
            "sent_at": "2026-02-05T10:30:45Z"
        },
        ...
    ],
    "participant_count": 2
}
```

### Endpoint 4: Mark as Read
```
PATCH /api/messages/<message_id>/read
Required: Authorization header
Body: {}

Success Response (200):
{
    "message_id": 42,
    "is_read": true,
    "read_at": "2026-02-05T10:40:00Z"
}

Errors:
- 404: Message not found
- 403: User not recipient
```

### Endpoint 5: Delete Message (Soft Delete)
```
DELETE /api/messages/<message_id>
Required: Authorization header

Success Response (204 No Content)

Soft Delete Logic:
- If user is sender: set is_deleted_by_sender = 1
- If user is recipient: set is_deleted_by_recipient = 1
- If both marked deleted: set deleted_at = NOW (permanent hide)
- Deleted messages never returned in API calls

Errors:
- 404: Message not found
- 403: User not sender/recipient
```

---

## 🔐 ROLE-BASED ACCESS CONTROL

### Permissions Matrix

| From → To | Therapist | Clinician | User | Admin | Restrictions |
|-----------|-----------|-----------|------|-------|---|
| **Therapist** | ✅ | ✅ | ✅ | ✅ | Can message anyone |
| **Clinician** | ✅ | ✅ | ✅ | ✅ | Can message anyone |
| **User** | ✅ | ❌ | ✅ | ✅ | Can REPLY to therapist/clinician, message other users, message admin |
| **Admin** | ✅ | ✅ | ✅ | ✅ | Can message anyone, monitor all |

### Implementation (in send_message endpoint):
```python
# Get sender and recipient roles
sender_role = get_user_role(sender_username)
recipient_role = get_user_role(recipient_username)

# Check permission
if sender_role == 'user' and recipient_role == 'clinician':
    # Users cannot initiate messages to clinicians
    return {"error": "Users may only reply to clinicians"}, 403

# For clinician/therapist: always allow
# For user: only allow to therapist, other users, or admin
allowed_recipients = {
    'therapist': ['therapist', 'clinician', 'user', 'admin'],
    'clinician': ['therapist', 'clinician', 'user', 'admin'],
    'user': ['therapist', 'user', 'admin'],  # NOT clinician
    'admin': ['therapist', 'clinician', 'user', 'admin']
}

if recipient_role not in allowed_recipients[sender_role]:
    return {"error": "Permission denied"}, 403
```

---

## ✅ TESTING STRATEGY

### Unit Tests (3 tests)
1. **test_send_message_valid**: Create message, verify in database
2. **test_send_message_invalid**: Bad recipient, missing content → errors
3. **test_soft_delete**: Mark deleted, verify hidden from queries

### Integration Tests (5 tests)
1. **test_inbox_unread_count**: Verify unread_count calculation
2. **test_conversation_ordering**: Messages in chronological order
3. **test_role_restrictions**: User can't message clinician, therapist can
4. **test_mark_read**: Timestamp updates correctly
5. **test_both_deleted**: Message hidden when both marked deleted

### Full Test Coverage
- ✅ Happy path (send, read, delete)
- ✅ Error cases (invalid input, permissions)
- ✅ Edge cases (self-messages blocked, empty conversation)
- ✅ Performance (pagination working, indexes effective)

### Test File
Create: [tests/test_messaging.py](tests/test_messaging.py)  
Target: 100% endpoint coverage

---

## 📅 IMPLEMENTATION TIMELINE (8 Hours)

### Hour 1: Database Schema & Migration
- [ ] Add `messages` table to `init_db()` in [api.py](api.py)
- [ ] Implement table creation with proper indexes
- [ ] Test migration on fresh database
- [ ] Verify backward compatibility with existing databases

### Hours 2-4: Core API Endpoints (3 hours)
- [ ] POST /api/messages/send (1h)
  - Validate input, check roles, store in DB
- [ ] GET /api/messages/inbox (1h)
  - Pagination, unread count, conversation preview
- [ ] GET /api/messages/conversation/<username> (1h)
  - Full history, proper ordering, performance

### Hours 5-6: Additional Endpoints (2 hours)
- [ ] PATCH /api/messages/<id>/read (0.5h)
  - Mark as read, update timestamp
- [ ] DELETE /api/messages/<id> (soft delete) (0.5h)
  - Track sender/recipient deletion separately
  - Hide when both deleted
- [ ] Input validation & error handling (1h)
  - Max message length (5000 chars)
  - Recipient must exist
  - Prevent self-messages

### Hour 7: Testing
- [ ] Write unit tests for all 5 endpoints
- [ ] Write integration tests for role restrictions
- [ ] Run full test suite: target 100% passing
- [ ] Test coverage: target > 80% for messaging module

### Hour 8: Documentation & Deployment
- [ ] Update API documentation with messaging endpoints
- [ ] Test on staging/production
- [ ] Deploy to Railway via git push
- [ ] Verify endpoints working in production
- [ ] Update ACTIVE_STATUS.md with completion

---

## 🚀 DEPLOYMENT CHECKLIST

- [ ] All tests passing (11 + new messaging tests)
- [ ] Code review complete
- [ ] Database migration tested on staging
- [ ] Performance verified (indexes effective)
- [ ] Security validated (role checks working)
- [ ] Documentation updated
- [ ] Railway deployment successful
- [ ] Smoke test on production (send message, verify in inbox)

---

## 📚 RELATED DOCUMENTATION

- [ROADMAP.md](ROADMAP.md) - Phase 3 full specification
- [DECISIONS.md](DECISIONS.md) - Decision B (Balanced scope)
- [api.py](api.py) - Implementation target file
- [tests/test_messaging.py](tests/test_messaging.py) - To be created

---

## 🎯 SUCCESS CRITERIA

✅ All 5 endpoints implemented and working  
✅ Role-based access control enforced  
✅ Soft delete functioning (not permanent)  
✅ Read/unread tracking with timestamps  
✅ Test coverage > 80%  
✅ All tests passing  
✅ Deployed to production successfully  
✅ No security vulnerabilities introduced  
✅ Performance acceptable (< 200ms response time)  
✅ Documentation complete  

---

## 🔗 NEXT PHASE CONTEXT

After Phase 3 completion (Feb 12):
- **Phase 4** (Mar 1-15): Database constraints & PostgreSQL preparation
- **Phase 5** (mid-March): Advanced logging (Loki/Grafana) + E2E testing (Playwright)
- **Phase 6+**: Performance optimization, additional features

---

*Document created: Feb 4, 2026, 14:30 UTC*  
*Status: Ready for implementation sprint starting Feb 5*
