# MESSAGING SYSTEM TEST CASES
## Comprehensive Test Suite for All Messaging Functionality

---

## TEST FILE STRUCTURE
```
tests/
├── test_messaging_core.py          # Core message send/receive
├── test_messaging_clinician.py      # Clinician-specific messaging
├── test_messaging_security.py       # Security & CSRF
├── test_messaging_ui.py             # Frontend UI tests
└── test_messaging_integration.py    # Full workflow tests
```

---

## CORE MESSAGING TESTS (test_messaging_core.py)

### Message Send Tests
```python
def test_send_message_happy_path():
    """User sends message to another user successfully"""
    # Setup: 2 users (user1, user2)
    # Action: user1 sends message to user2
    # Assert: Message stored in DB with correct sender/recipient
    # Assert: Message has sent_at timestamp
    # Assert: is_read = False (not yet read)

def test_send_message_missing_recipient():
    """Send fails when recipient not provided"""
    # Action: send with empty recipient field
    # Assert: Returns 400 with error message

def test_send_message_recipient_not_found():
    """Send fails when recipient doesn't exist"""
    # Action: send to nonexistent user
    # Assert: Returns 404 'Recipient not found'

def test_send_message_to_self():
    """User cannot send message to themselves"""
    # Action: user1 sends to user1
    # Assert: Returns 400 'Cannot send to yourself'

def test_send_message_content_too_long():
    """Message rejected if > 5000 chars"""
    # Action: send message with 5001 characters
    # Assert: Returns 400 'Message cannot exceed 5000 characters'

def test_send_message_subject_too_long():
    """Subject rejected if > 100 chars"""
    # Action: send with 101-char subject
    # Assert: Returns 400 'Subject cannot exceed 100 characters'

def test_send_message_requires_auth():
    """Unauthenticated request rejected"""
    # Action: send without session
    # Assert: Returns 401 'Authentication required'

def test_send_message_role_restriction_user_to_clinician():
    """Users cannot initiate messages to clinicians"""
    # Setup: user and clinician
    # Action: user sends to clinician
    # Assert: Returns 403 'Users may only reply to clinicians'

def test_send_message_rate_limited():
    """Rapid message sending is throttled"""
    # Action: Send 10 messages in 1 second
    # Assert: After 1st, get 429 'Rate limited'

def test_send_message_daily_limit():
    """User cannot send >500 messages per day"""
    # Action: Send 500 messages, then 501st
    # Assert: Returns 429 'Daily message limit exceeded'

def test_send_message_notification_sent():
    """Recipient receives notification on new message"""
    # Action: user1 sends to user2
    # Assert: send_notification() called with user2 + message preview

def test_send_message_logged_to_audit():
    """Message send logged to audit trail"""
    # Action: send message
    # Assert: audit_log table has entry with 'messaging', 'message_sent'
```

### Message Retrieval Tests
```python
def test_get_inbox_empty():
    """Empty inbox shows no messages"""
    # Setup: New user with no messages
    # Action: GET /api/messages/inbox
    # Assert: Returns conversations = []

def test_get_inbox_with_conversations():
    """Inbox shows all unique conversation partners"""
    # Setup: user1 with messages from user2 and user3
    # Action: GET /api/messages/inbox
    # Assert: Returns 2 conversations with correct partners

def test_get_inbox_shows_latest_message():
    """Each conversation shows most recent message"""
    # Setup: user1 has 5 messages from user2
    # Action: GET /api/messages/inbox
    # Assert: Shows only latest message, correct timestamp

def test_get_inbox_unread_count():
    """Conversation shows unread message count"""
    # Setup: 3 unread messages from user2 to user1
    # Action: GET /api/messages/inbox
    # Assert: Conversation shows unread_count = 3

def test_get_inbox_pagination():
    """Inbox supports pagination"""
    # Setup: user with 50 conversation partners
    # Action: GET /api/messages/inbox?page=1&limit=20
    # Assert: Returns 20 conversations
    # Action: GET /api/messages/inbox?page=2&limit=20
    # Assert: Returns next 20 conversations
    # Assert: total_conversations = 50

def test_get_inbox_pagination_out_of_range():
    """Invalid pagination returns empty or defaults"""
    # Action: GET /api/messages/inbox?page=999
    # Assert: Returns empty conversations or friendly error

def test_get_inbox_requires_auth():
    """Unauthenticated request rejected"""
    # Action: GET without session
    # Assert: Returns 401

def test_get_sent_messages():
    """User sees messages they sent"""
    # Setup: user1 sent messages to user2, user3
    # Action: GET /api/messages/sent
    # Assert: Returns both messages with is_read status

def test_get_sent_messages_respects_deletion():
    """Deleted messages don't show in sent"""
    # Setup: user1 deleted a sent message
    # Action: GET /api/messages/sent
    # Assert: Deleted message doesn't appear
```

### Conversation Thread Tests
```python
def test_get_conversation_full_history():
    """Fetch full conversation history with user"""
    # Setup: 5 messages exchanged between user1 and user2
    # Action: GET /api/messages/conversation/user2
    # Assert: Returns all 5 messages in chronological order

def test_get_conversation_marks_as_read():
    """Opening conversation auto-marks messages as read"""
    # Setup: 3 unread messages from user2 to user1
    # Action: GET /api/messages/conversation/user2
    # Assert: Messages returned with is_read = true
    # Assert: DB updated to is_read = 1

def test_get_conversation_shows_direction():
    """Each message shows who sent it"""
    # Setup: Messages from both directions
    # Action: GET /api/messages/conversation/user2
    # Assert: Each message has sender field correctly set

def test_get_conversation_limit():
    """Fetch conversation with limit parameter"""
    # Setup: 100 messages between user1 and user2
    # Action: GET /api/messages/conversation/user2?limit=20
    # Assert: Returns only 20 most recent messages

def test_get_conversation_requires_auth():
    """Unauthenticated request rejected"""
    # Action: GET without session
    # Assert: Returns 401

def test_get_conversation_participant_access():
    """Only conversation participants can fetch"""
    # Setup: user1 ↔ user2 conversation
    # Action: user3 tries GET /api/messages/conversation/user2 as user3
    # Assert: Returns 403 or only shows own messages to user3
```

### Message Read Status Tests
```python
def test_mark_message_as_read():
    """Message can be marked as read"""
    # Setup: Unread message
    # Action: PATCH /api/messages/{id}/read
    # Assert: is_read = 1, read_at set to now

def test_mark_message_read_idempotent():
    """Marking already-read message succeeds"""
    # Setup: Already read message
    # Action: PATCH /api/messages/{id}/read
    # Assert: Returns 200 (no error)

def test_mark_message_read_non_recipient():
    """Only recipient can mark as read"""
    # Setup: user1 received message from user2
    # Action: user2 PATCH /api/messages/{id}/read
    # Assert: Returns 403 'Not the recipient'

def test_mark_message_read_not_found():
    """Marking nonexistent message fails"""
    # Action: PATCH /api/messages/99999/read
    # Assert: Returns 404 'Message not found'

def test_mark_message_read_requires_auth():
    """Requires authentication"""
    # Action: PATCH without session
    # Assert: Returns 401
```

### Message Deletion Tests
```python
def test_delete_message_by_sender():
    """Sender can delete their message"""
    # Setup: user1 sent message to user2
    # Action: user1 DELETE /api/messages/{id}
    # Assert: is_deleted_by_sender = 1
    # Assert: Message still visible to user2

def test_delete_message_by_recipient():
    """Recipient can delete received message"""
    # Setup: user1 received message from user2
    # Action: user1 DELETE /api/messages/{id}
    # Assert: is_deleted_by_recipient = 1
    # Assert: Message still visible to user2

def test_delete_message_soft_deletes():
    """Message marked deleted, not permanently removed"""
    # Action: user1 DELETE /api/messages/{id}
    # Assert: deleted_at = now
    # Assert: Message not returned in inbox/sent

def test_delete_message_both_deleted_hides():
    """When both sides delete, message is hidden"""
    # Setup: user1 and user2 exchange message
    # Action: user1 DELETE, then user2 DELETE
    # Assert: Message doesn't appear to either user
    # Assert: DB has deleted_at timestamp

def test_delete_message_not_participant():
    """Non-participant cannot delete"""
    # Setup: user1 ↔ user2 message
    # Action: user3 DELETE /api/messages/{id}
    # Assert: Returns 403 'Cannot delete'

def test_delete_message_not_found():
    """Delete nonexistent message fails"""
    # Action: DELETE /api/messages/99999
    # Assert: Returns 404

def test_delete_message_requires_auth():
    """Requires authentication"""
    # Action: DELETE without session
    # Assert: Returns 401
```

---

## CLINICIAN MESSAGING TESTS (test_messaging_clinician.py)

```python
def test_clinician_send_message_to_patient():
    """Clinician can send message to assigned patient"""
    # Setup: Clinician assigned to patient (patient_approvals)
    # Action: clinician POST /api/clinician/message
    # Assert: Message sent successfully

def test_clinician_send_message_csrf_required():
    """Clinician message requires CSRF token"""
    # Setup: Clinician-patient assignment
    # Action: POST /api/clinician/message without X-CSRF-Token
    # Assert: Returns 403 'CSRF token invalid'

def test_clinician_send_message_verify_assignment():
    """Clinician can only message assigned patients"""
    # Setup: Clinician1 assigned to patient1, not patient2
    # Action: clinician1 sends to patient2
    # Assert: Returns 403 'Not assigned to this patient'

def test_clinician_send_message_role_check():
    """Only clinician role can use endpoint"""
    # Setup: User with 'user' role
    # Action: POST /api/clinician/message
    # Assert: Returns 403 'Clinician access required'

def test_clinician_message_content_validation():
    """Message content validated (max 10000 chars)"""
    # Action: Send 10001 character message
    # Assert: Returns 400 'Message too long'

def test_clinician_message_requires_recipient():
    """Recipient required"""
    # Action: Send without recipient_username
    # Assert: Returns 400 'Recipient required'

def test_clinician_message_requires_content():
    """Message content required"""
    # Action: Send empty message
    # Assert: Returns 400 'Message required'

def test_clinician_message_logged():
    """Clinician messages logged to audit"""
    # Action: Send clinician message
    # Assert: audit_log entry with 'clinician_dashboard', 'send_message'

def test_clinician_patient_cannot_initiate():
    """Patient cannot initiate to clinician (only reply)"""
    # Setup: Patient and clinician, no prior message
    # Action: patient sends to clinician
    # Assert: Returns 403 'Only reply to clinicians'

def test_clinician_patient_can_reply():
    """Patient CAN reply to clinician message"""
    # Setup: Clinician sent message to patient
    # Action: Patient replies
    # Assert: Message sent successfully
```

---

## SECURITY TESTS (test_messaging_security.py)

```python
def test_xss_in_message_content():
    """Malicious HTML in message is escaped"""
    # Action: Send message with <script>alert('xss')</script>
    # Assert: Stored message has content escaped
    # Assert: Frontend sanitizes with sanitizeHTML()

def test_sql_injection_in_message():
    """SQL injection in message is prevented"""
    # Action: Send message with DROP TABLE messages;--
    # Assert: Message stored as literal text, not executed

def test_csrf_token_required_on_post():
    """POST requires valid CSRF token"""
    # Action: POST /api/messages/send without X-CSRF-Token
    # Assert: Returns 403 'CSRF token invalid'

def test_csrf_token_required_on_delete():
    """DELETE requires valid CSRF token (if implemented)"""
    # Action: DELETE /api/messages/{id} without token
    # Assert: Returns 403 or 401

def test_message_access_control():
    """Users can only access their own messages"""
    # Setup: user1 message from user2 to user1
    # Action: user3 tries to read this message
    # Assert: Returns 403 or message not included in results

def test_message_manipulation_prevented():
    """Users cannot modify messages from others"""
    # Setup: user1 sent message to user2
    # Action: user2 tries to PUT /api/messages/{id} to change content
    # Assert: Returns 403 or endpoint not available

def test_rate_limiting_prevents_spam():
    """Rate limiting prevents message spam"""
    # Action: Send 10 messages as fast as possible
    # Assert: After threshold, get 429 'Rate limited'

def test_audit_trail_complete():
    """All message actions logged"""
    # Actions: send, read, delete, search
    # Assert: Each appears in audit_log with proper details
```

---

## UI TESTS (test_messaging_ui.py)

```python
def test_inbox_loads_on_page():
    """Messaging inbox loads when messaging tab clicked"""
    # Setup: Logged in user with messages
    # Action: Click messaging tab
    # Assert: loadMessagesInbox() called
    # Assert: Inbox displays with conversations

def test_send_message_button_visible():
    """Send message button visible and clickable"""
    # Action: Navigate to messages tab
    # Assert: 'Send Message' button visible
    # Assert: Clicking opens send form

def test_message_form_validation_ui():
    """Form validates before sending"""
    # Action: Try to send with empty content
    # Assert: Form shows validation error
    # Assert: No API call made

def test_clinician_message_button_visible():
    """Clinician role sees message button"""
    # Setup: Logged in as clinician
    # Action: Navigate to messaging area
    # Assert: Send message button visible

def test_user_message_button_limited():
    """User cannot initiate to clinician"""
    # Setup: Logged in as user
    # Action: Try to message clinician
    # Assert: Form blocks or shows error message

def test_message_thread_modal_opens():
    """Clicking conversation opens thread modal"""
    # Setup: Conversation in inbox
    # Action: Click on conversation
    # Assert: Modal opens with thread
    # Assert: Messages display in order

def test_thread_modal_shows_both_directions():
    """Modal shows messages from both parties"""
    # Setup: Exchange between user1 and user2
    # Action: Open thread as user1
    # Assert: Shows messages from both users
    # Assert: Own messages on right, other on left

def test_search_box_visible():
    """Message search box present"""
    # Action: Open messaging tab
    # Assert: Search input visible
    # Assert: Can type and search

def test_unread_badge_updates():
    """Unread message count shows in badge"""
    # Setup: New message received
    # Assert: Badge shows count
    # Assert: Badge removes when message read
```

---

## INTEGRATION TESTS (test_messaging_integration.py)

```python
def test_full_messaging_flow_user_to_user():
    """Complete flow: user1 sends to user2, user2 reads"""
    # 1. user1 sends message
    # 2. Verify appears in user2 inbox (unread)
    # 3. user2 opens conversation
    # 4. Verify message marked as read
    # 5. Verify user1 sees read status in sent

def test_full_messaging_flow_clinician_to_patient():
    """Complete clinician workflow"""
    # 1. Clinician assigned to patient
    # 2. Clinician sends message with CSRF token
    # 3. Patient receives notification
    # 4. Patient sees message in inbox
    # 5. Patient opens conversation
    # 6. Patient replies
    # 7. Clinician sees reply with read receipt

def test_conversation_threading():
    """Multi-message conversation maintains order"""
    # 1. user1 sends message A
    # 2. user2 replies with message B
    # 3. user1 replies with message C
    # 4. Both fetch conversation
    # Assert: Order is A, B, C (chronological)

def test_message_search_workflow():
    """User can search and find messages"""
    # 1. user1 sends 50 messages about "budget"
    # 2. User searches for "budget"
    # Assert: All 50 returned in results
    # Assert: Can click result to open conversation

def test_message_deletion_workflow():
    """Delete message hides from both users"""
    # 1. user1 sends to user2
    # 2. user1 deletes (soft)
    # 3. Verify user1 doesn't see it
    # 4. Verify user2 still sees it
    # 5. user2 deletes
    # 6. Verify both users can't see it
    # 7. Verify DB has deleted_at timestamp

def test_large_inbox_performance():
    """Large inbox doesn't slow down"""
    # Setup: 1000 conversations
    # Action: GET /api/messages/inbox
    # Assert: Response time < 1 second (with pagination)
    # Assert: Browser displays smoothly

def test_message_notification_delivery():
    """Messages trigger notifications"""
    # 1. user1 sends to user2
    # 2. Verify send_notification() called
    # 3. Verify notification content correct
    # 4. Verify user2 receives notification

def test_rate_limiting_comprehensive():
    """Rate limiting works across multiple scenarios"""
    # Scenario 1: 6 messages in 60 seconds (per-user limit: 5/min)
    # Assert: 6th is rate limited
    # Scenario 2: Different users send lots (should not affect each other)
    # Assert: Both succeed (limit is per-user)
    # Scenario 3: Burst then wait (limit should reset)
    # Assert: Can send after wait period
```

---

## TEST EXECUTION GUIDE

### Run All Messaging Tests
```bash
pytest tests/test_messaging_*.py -v
```

### Run Specific Test Category
```bash
pytest tests/test_messaging_core.py -v           # Core functionality
pytest tests/test_messaging_clinician.py -v      # Clinician tests
pytest tests/test_messaging_security.py -v       # Security tests
pytest tests/test_messaging_ui.py -v             # Frontend tests
pytest tests/test_messaging_integration.py -v    # Integration tests
```

### Run Single Test
```bash
pytest tests/test_messaging_core.py::test_send_message_happy_path -v
```

### Generate Coverage Report
```bash
pytest tests/test_messaging_*.py --cov=api --cov-report=html
```

---

## EXPECTED TEST RESULTS

**Total Test Cases**: 85+  
**Expected Pass Rate**: 100%  
**Coverage Target**: 95%+ of messaging code  
**Execution Time**: < 2 minutes

---

## TEST DATA FIXTURES NEEDED

```python
# conftest.py additions
@pytest.fixture
def test_user():
    """Create test user"""
    # Create user1, user2, user3 with different roles

@pytest.fixture  
def test_messages():
    """Create test messages"""
    # Create 5 messages between test users

@pytest.fixture
def test_clinician_assignment():
    """Create clinician-patient assignment"""
    # Create patient_approvals record

@pytest.fixture
def test_large_inbox():
    """Create 50+ conversations"""
    # For performance testing
```

---

**Status**: Ready for Implementation  
**Last Updated**: February 2026
