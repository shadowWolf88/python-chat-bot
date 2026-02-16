# COMPREHENSIVE INTERNAL MESSAGING SYSTEM OVERHAUL PROMPT

## Executive Summary
You are a world class full stack developer, administrator, e-mail/internal messaging expert.
I want you to design and implement a world-class internal messaging system for Healing Space that enables seamless, feature-rich communication between patients, clinicians, and the developer account. The system must function like enterprise email (with threading, read receipts, search, etc.) while being optimized for mental health therapy workflows.

**Key Constraint:** Zero breaking changes. All modifications must be backward compatible with existing dashboards and systems.

---

## Phase 1: Requirements Analysis & Design

### 1.1 User Roles & Communication Paths

#### Patient Role
- **Can send/receive from:**
  - Assigned clinician (primary communication)
  - Developer account (bug reports, suggestions, help requests)
  - Other patients (optional: support group/peer messaging)

- **Key features needed:**
  - Dedicated Messaging tab in patient dashboard
  - Unread message indicators
  - Notification badges
  - Quick reply to latest clinician message
  - Message history with search

#### Clinician Role
- **Can send/receive from:**
  - Assigned patients (primary communication)
  - Other clinicians (consultations/handoffs)
  - Developer account (system issues, feature requests)

- **Key features needed:**
  - Messages section in clinical dashboard
  - Patient list with unread counts
  - Message templates for common responses
  - Bulk messaging capability (send to multiple patients)
  - Message history with filtering
  - Scheduled message sending

#### Developer Account
- **Can send/receive from:**
  - All patients (system announcements, bug updates)
  - All clinicians (system updates, new feature notices)
  - Receives: bug reports, feature suggestions, help requests from all users

- **Key features needed:**
  - Admin messaging console
  - Broadcast messaging (send to all/segment)
  - Message queue management
  - Analytics dashboard (message volume, response times)
  - System notification integration

#### System/Admin
- **Can:**
  - Send system notifications (new feature, maintenance, alerts)
  - Archive old messages
  - Monitor messaging system health

### 1.2 Message Types

1. **Direct Messages** - One-to-one communication
2. **Group Messages** - Multiple recipients (clinician to patient cohort)
3. **System Messages** - Automated notifications from app
4. **Broadcast Messages** - Admin announcements to all users
5. **Therapy Progress Summaries** - AI-generated message from therapist AI
6. **Appointment Reminders** - Scheduled system messages
7. **Wellness Check-ins** - Clinician automated reminders

### 1.3 Current System Issues (Analysis)

Based on previous implementation:
- ✗ SQL syntax errors (LIMIT ?) - FIXED in v2
- ✗ Session authentication on production (domain cookie) - FIXED in v2
- ✗ Incomplete conversation modal implementation
- ✗ Missing read receipts and typing indicators
- ✗ No message search functionality (added but incomplete)
- ✗ No message templates or scheduled sending
- ✗ No bulk messaging for clinicians
- ✗ Poor UI/UX for mobile viewing
- ✗ No rich text formatting support
- ✗ No file attachment support
- ✗ Missing notification system integration
- ✗ No message archival or retention policies

---

## Phase 2: Technical Architecture

### 2.1 Database Schema (Enhanced)

```sql
-- Messages table (core structure)
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER,
    sender_username VARCHAR(255) NOT NULL,
    recipient_username VARCHAR(255),  -- NULL for group/broadcast
    message_type VARCHAR(50) NOT NULL,  -- 'direct', 'group', 'system', 'broadcast'
    subject VARCHAR(255),
    content TEXT NOT NULL,
    
    -- Rich content support
    content_html TEXT,  -- Sanitized HTML for formatting
    attachments JSONB,  -- [{'url': '...', 'name': '...', 'size': ...}]
    
    -- Status tracking
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    is_archived_by_sender BOOLEAN DEFAULT FALSE,
    is_archived_by_recipient BOOLEAN DEFAULT FALSE,
    
    -- Soft delete (per-user deletion)
    is_deleted_by_sender BOOLEAN DEFAULT FALSE,
    is_deleted_by_recipient BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    
    -- Scheduling & delivery
    scheduled_for TIMESTAMP,  -- For scheduled sending
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivery_status VARCHAR(50) DEFAULT 'sent',  -- 'draft', 'scheduled', 'sent', 'delivered', 'failed'
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (conversation_id) REFERENCES conversations(id),
    FOREIGN KEY (sender_username) REFERENCES users(username),
    INDEX idx_sender_recipient (sender_username, recipient_username),
    INDEX idx_conversation (conversation_id),
    INDEX idx_sent_at (sent_at)
);

-- Conversations table (threading)
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,  -- 'direct', 'group', 'thread'
    subject VARCHAR(255),
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP,
    participant_count INTEGER,
    is_archived BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (created_by) REFERENCES users(username),
    INDEX idx_created_at (created_at)
);

-- Conversation participants (for group messages)
CREATE TABLE conversation_participants (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL,
    username VARCHAR(255) NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_read_at TIMESTAMP,
    is_muted BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (conversation_id) REFERENCES conversations(id),
    FOREIGN KEY (username) REFERENCES users(username),
    UNIQUE (conversation_id, username)
);

-- Message receipts (read, delivered, typing)
CREATE TABLE message_receipts (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL,
    username VARCHAR(255) NOT NULL,
    receipt_type VARCHAR(50) NOT NULL,  -- 'delivered', 'read', 'typing'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (message_id) REFERENCES messages(id),
    FOREIGN KEY (username) REFERENCES users(username)
);

-- Message templates (for clinicians)
CREATE TABLE message_templates (
    id SERIAL PRIMARY KEY,
    creator_username VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),  -- 'follow-up', 'encouragement', 'appointment', etc.
    is_public BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (creator_username) REFERENCES users(username),
    UNIQUE (creator_username, name)
);

-- Blocked users (prevent messages)
CREATE TABLE blocked_users (
    id SERIAL PRIMARY KEY,
    blocker_username VARCHAR(255) NOT NULL,
    blocked_username VARCHAR(255) NOT NULL,
    reason VARCHAR(255),
    blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (blocker_username) REFERENCES users(username),
    FOREIGN KEY (blocked_username) REFERENCES users(username),
    UNIQUE (blocker_username, blocked_username)
);

-- Message notifications (push notifications, email digests)
CREATE TABLE message_notifications (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL,
    recipient_username VARCHAR(255) NOT NULL,
    notification_type VARCHAR(50),  -- 'in_app', 'email', 'push'
    sent_at TIMESTAMP,
    read_at TIMESTAMP,
    
    FOREIGN KEY (message_id) REFERENCES messages(id),
    FOREIGN KEY (recipient_username) REFERENCES users(username)
);
```

### 2.2 API Endpoints (Comprehensive)

#### Direct Messaging
- `POST /api/messages/send` - Send direct message
- `GET /api/messages/conversations` - List all conversations
- `GET /api/messages/conversation/<user>` - Get thread with user
- `POST /api/messages/<id>/reply` - Reply to message (in thread)
- `GET /api/messages/search?q=<query>` - Full-text search
- `PATCH /api/messages/<id>/read` - Mark as read
- `PATCH /api/messages/<id>/archive` - Archive message
- `DELETE /api/messages/<id>` - Delete message (soft delete)

#### Group/Bulk Messaging
- `POST /api/messages/group/send` - Send to group
- `POST /api/messages/broadcast` - Send to all (admin only)
- `POST /api/messages/schedule` - Schedule message for later
- `GET /api/messages/scheduled` - List scheduled messages
- `PATCH /api/messages/scheduled/<id>/cancel` - Cancel scheduled

#### Templates & Drafts
- `GET /api/messages/templates` - List message templates
- `POST /api/messages/templates` - Create template
- `PATCH /api/messages/templates/<id>` - Update template
- `DELETE /api/messages/templates/<id>` - Delete template
- `POST /api/messages/draft` - Save draft message
- `GET /api/messages/drafts` - List drafts

#### Notifications & Status
- `GET /api/messages/unread-count` - Get total unread
- `GET /api/messages/status/<id>` - Get delivery status
- `POST /api/messages/<id>/typing` - Send typing indicator
- `GET /api/messages/typing/<user>` - Get typing status

#### Admin/Developer
- `GET /api/admin/messages/analytics` - Message analytics
- `GET /api/admin/messages/queue` - Pending messages
- `POST /api/admin/messages/resend/<id>` - Resend failed
- `PATCH /api/admin/users/<username>/block` - Block user

#### Blocked/Permissions
- `POST /api/messages/block/<username>` - Block user
- `DELETE /api/messages/block/<username>` - Unblock user
- `GET /api/messages/blocked` - List blocked users

### 2.3 Frontend Components

#### Patient Dashboard
- **Messaging Tab** (main access point)
  - Conversation list (most recent first)
  - Unread count badges
  - Search bar
  - New message button
  - Conversation detail view with full thread
  - Reply composer with rich text
  - Read receipts (✓✓ blue for read)
  - Timestamp display

#### Clinician Dashboard
- **Messages Section** (high visibility)
  - Patient inbox with unread filters
  - Quick stats (unread count, response time)
  - Message templates dropdown
  - Bulk send feature
  - Scheduled messages calendar
  - Message history with filters
  - Patient conversation threads

#### Admin/Developer Console
- **Messaging Hub**
  - Analytics dashboard (message volume, response times)
  - Broadcast message composer
  - User blocking/restrictions
  - System notifications
  - Message queue monitoring
  - Delivery failure alerts

---

## Phase 3: Implementation Strategy

### 3.1 User Experience

#### For Patients
1. Click "Messages" tab in dashboard
2. See conversation list (clinician, developer, other patients)
3. Click conversation to open full thread
4. Type reply in composer at bottom
5. See typing indicator when clinician is typing
6. Get notification when message arrives
7. See read receipt (✓✓) when clinician reads it

#### For Clinicians
1. Dashboard shows "Messages" widget with unread count
2. Click to open messaging panel
3. See patient list with unread indicators
4. Click patient to open conversation
5. Use template dropdown for quick responses
6. Can schedule reminder messages for patients
7. Can send message to multiple patients at once

#### For Developer
1. Access admin console → Messages section
2. Send system announcements to all users
3. Monitor message queue and delivery
4. View message analytics
5. Respond to bug reports/suggestions
6. Block problematic users if needed

### 3.2 Visual Design

**Conversation List:**
- Card-based layout
- User avatar/initials
- Username and last message preview (truncated)
- Timestamp (Today/Yesterday/Date)
- Unread badge (red dot or count)
- Hover effects (highlight, show actions)

**Message Composer:**
- Full-width textarea with auto-expand
- Toolbar with: Bold, Italic, Link, Emoji, Attachment
- Submit button (Send / Schedule / Save Draft)
- Character counter (optional)
- Mentions support (@clinician, @developer)

**Message Bubbles:**
- Own messages: right-aligned, blue background
- Other messages: left-aligned, gray background
- Timestamp on hover
- Read receipt indicator (✓✓ blue when read)
- Delete/Archive/Report options (three-dot menu)

**Notifications:**
- Toast for new message
- Badge on Messages tab
- Unread count in sidebar
- (Optional) Email digest of missed messages

### 3.3 No Breaking Changes Guarantee

- Keep all existing message endpoints functional
- Add new endpoints without modifying old ones
- Database migrations must be backward compatible
- Frontend component updates should not affect existing features
- Session/authentication logic unchanged
- CSRF protection maintained throughout

---

## Phase 4: Security & Compliance

### 4.1 Security Measures
- ✓ CSRF token validation on all POST endpoints
- ✓ SQL injection prevention (parameterized queries)
- ✓ XSS prevention (sanitize HTML, escape user input)
- ✓ Access control (users can only see their own messages)
- ✓ Message content encryption at rest (optional)
- ✓ Rate limiting on message sending (prevent spam)
- ✓ Input validation (max message length, file size limits)
- ✓ Audit logging (all message actions logged)

### 4.2 Clinical Compliance
- ✓ Message archival for compliance records
- ✓ No automatic message deletion (audit trail)
- ✓ Read receipts for accountability
- ✓ Timestamp accuracy
- ✓ User accountability (who sent what, when)
- ✓ GDPR right to be forgotten (soft delete option)
- ✓ Message content cannot be edited (immutable)

### 4.3 Privacy
- ✓ Patients cannot see other patients' messages
- ✓ Clinicians can only see assigned patients' messages
- ✓ Messages are person-to-person (no broadcast to wrong audience)
- ✓ Block functionality to prevent unwanted contact
- ✓ Clinician cannot reply to clinical information in wrong thread

---

## Phase 5: Testing Strategy

### 5.1 Unit Tests
- Message creation (all user types)
- Message retrieval (permissions correct)
- Read receipt updating
- Archive/delete functionality
- Message search
- Template system
- Scheduled sending

### 5.2 Integration Tests
- Patient sends to clinician (appears in clinician dashboard)
- Clinician replies to patient (notification received)
- Developer broadcasts to all (appears for all users)
- Message search finds correct results
- Blocking prevents message delivery
- Scheduled messages send at correct time

### 5.3 UI/UX Tests
- Conversation list loads quickly
- Message composer is responsive
- Read receipts update in real-time
- Typing indicators appear/disappear
- Search returns relevant results
- Mobile view is functional and beautiful

### 5.4 Security Tests
- Unauthorized users cannot access others' messages
- SQL injection attempts blocked
- CSRF tokens validated
- Rate limiting prevents spam
- Blocked users cannot send messages
- Admin features require authentication

---

## Phase 6: Implementation Roadmap

### Sprint 1 (Week 1-2): Core Infrastructure
- [ ] Database schema migration (new tables)
- [ ] Core API endpoints (send, receive, list, delete)
- [ ] Basic authentication & access control
- [ ] Message storage and retrieval
- [ ] Audit logging integration

### Sprint 2 (Week 3-4): UI Implementation
- [ ] Messaging tab in patient dashboard
- [ ] Messages section in clinician dashboard
- [ ] Conversation list component
- [ ] Message composer with rich text
- [ ] Read receipt indicators

### Sprint 3 (Week 5-6): Advanced Features
- [ ] Message search functionality
- [ ] Message templates for clinicians
- [ ] Scheduled messaging
- [ ] Typing indicators (WebSocket optional)
- [ ] Bulk/group messaging

### Sprint 4 (Week 7-8): Admin & Polish
- [ ] Developer console & broadcasting
- [ ] Message analytics dashboard
- [ ] User blocking functionality
- [ ] Message archival system
- [ ] Performance optimization

### Sprint 5 (Week 9-10): Testing & Documentation
- [ ] Comprehensive test suite (>85% coverage)
- [ ] Security audit and penetration testing
- [ ] User documentation and guides
- [ ] API documentation
- [ ] Deployment checklist

---

## Phase 7: Documentation Requirements

### Documents to Create/Update
1. **MESSAGING_SYSTEM_ARCHITECTURE.md**
   - System design overview
   - Database schema diagram
   - API endpoint reference

2. **MESSAGING_USER_GUIDE.md**
   - For patients: how to message clinician
   - For clinicians: how to message patients
   - For admin: how to broadcast messages

3. **MESSAGING_DEVELOPER_GUIDE.md**
   - API endpoint documentation
   - Code examples
   - Integration patterns

4. **MESSAGING_DEPLOYMENT.md**
   - Database migration steps
   - Environment variables needed
   - Rollback procedures
   - Testing checklist

5. **MESSAGING_SECURITY.md**
   - Security architecture
   - Encryption details
   - Compliance features
   - Threat model

6. **MESSAGING_TROUBLESHOOTING.md**
   - Common issues and fixes
   - Debug endpoints
   - Log analysis guide

**All documents must:**
- Be saved in `DOCUMENTATION/4-TECHNICAL/Messaging-System/`
- Include implementation status
- Have examples and code snippets
- Be updated as features are completed

---

## Phase 8: Integration Points

### Existing Systems to Integrate
1. **Patient Dashboard**
   - Add Messaging tab
   - Show unread badge
   - Link to clinician profile

2. **Clinician Dashboard**
   - Add Messages widget
   - Show patient list with unread counts
   - Link to patient profiles

3. **Notifications System**
   - Send notification on new message
   - Toast for urgent messages
   - Email digest option

4. **Audit System**
   - Log all message actions
   - Track message delivery
   - Record read timestamps

5. **User Management**
   - Check role-based permissions
   - Validate user existence before sending
   - Handle user deletion (archive messages)

6. **Session Management**
   - Maintain session domain cookie fix
   - Ensure messages available across subdomains
   - Timeout handling

---

## Phase 9: Feature Ideas (Beyond MVP)

### Nice-to-Have Features
- Message reactions (👍 👎 ❤️)
- Message pinning (save important messages)
- Message tags/labels for organization
- Auto-replies (vacation, out of office)
- Message encryption (end-to-end)
- Voice messages (record and send)
- File sharing (PDFs, images)
- Message forwarding
- Message translation (multilingual)
- AI message suggestions (write better messages)
- Message scheduling with reminder
- Snooze message (resurface later)
- Dark mode for messaging UI
- Desktop notifications
- Offline message queue

---

## Phase 10: Quality Assurance Checklist

Before launch:
- [ ] All 286 existing routes still working
- [ ] No SQL errors (all PostgreSQL syntax)
- [ ] Session cookies work on production domain
- [ ] CSRF tokens validated on all POST endpoints
- [ ] Input validation prevents injection attacks
- [ ] Messages properly encrypted/escaped
- [ ] Access control prevents unauthorized viewing
- [ ] Database queries optimized (indexes added)
- [ ] Error handling graceful (no 500 errors)
- [ ] Tests passing (>85% coverage)
- [ ] Documentation complete and current
- [ ] Performance acceptable (<500ms response time)
- [ ] Mobile UI responsive and functional
- [ ] Accessibility standards met (WCAG 2.1 AA)
- [ ] Clinician workflows tested
- [ ] Patient workflows tested
- [ ] Admin/developer workflows tested
- [ ] Backup/disaster recovery tested
- [ ] Rollback procedure verified

---

## Success Criteria

✅ **System works flawlessly**
- All message types can be sent/received
- No data loss or corruption
- Messages persist correctly
- Search finds all relevant messages

✅ **Users love the UX**
- Intuitive navigation
- Fast response times (<1 second)
- Beautiful, modern design
- Works perfectly on mobile

✅ **Secure and compliant**
- No security vulnerabilities
- HIPAA compliant (if needed)
- GDPR right to be forgotten
- Audit trail complete

✅ **Well integrated**
- Works with existing dashboards
- Notifications system active
- Audit logging functioning
- Session management solid

✅ **Fully documented**
- User guides written
- API documented
- Architecture diagrams
- Deployment procedures

---

## Implementation Notes

**Key Principle:** This system should feel like a best-in-class email/messaging platform but optimized for mental health therapy.

**Design Philosophy:**
- Simple for patients (just message clinician)
- Powerful for clinicians (templates, scheduling, bulk)
- Comprehensive for admin (analytics, monitoring, broadcasting)
- Secure throughout (encryption, access control, audit logging)

**Technical Philosophy:**
- Use existing patterns (session auth, CSRF, input validation)
- Add new tables, don't modify existing ones
- Backward compatible with current system
- Well-tested before deployment
- Documented for future maintenance

---

## Git Workflow

```bash
# Create feature branch
git checkout -b feat/messaging-system-overhaul

# Implement following sprints above
# Regular commits with clear messages
git commit -m "feat: implement core message endpoints and database"
git commit -m "feat: build patient messaging UI"
git commit -m "feat: add clinician templates and scheduling"
# etc.

# Final merge to main with comprehensive commit message
git commit -m "feat: complete internal messaging system overhaul

- Implement 20+ messaging API endpoints
- Add conversation threading and search
- Build responsive messaging UI for all roles
- Add message templates and scheduling
- Implement read receipts and typing indicators
- Add user blocking and permissions
- Create admin broadcasting console
- Comprehensive test coverage (85%+)
- Full documentation and deployment guides
- Zero breaking changes - all existing features intact"

git push origin feat/messaging-system-overhaul
# Create pull request, get review, merge to main
```

---

## Estimated Timeline

- **Week 1-2:** Database + Core API = 40 hours
- **Week 3-4:** UI Implementation = 45 hours
- **Week 5-6:** Advanced Features = 40 hours
- **Week 7-8:** Admin + Polish = 35 hours
- **Week 9-10:** Testing + Docs = 30 hours

**Total: ~190 hours (~5 weeks with full-time focus)**

---

## Success Metrics

After implementation, measure:
1. Message delivery time (target: <100ms)
2. User adoption (% using messaging)
3. Message read rate (% messages read)
4. Average response time (clinician to patient)
5. User satisfaction (survey feedback)
6. System reliability (uptime >99.9%)
7. Security incidents (target: 0)
8. Bug reports (severity tracking)

---

*This prompt provides a complete specification for implementing a world-class messaging system. Follow each phase sequentially, maintain backward compatibility, and update documentation continuously.*
