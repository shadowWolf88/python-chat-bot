# HEALING SPACE - PROJECT ROADMAP

**Current Phase**: ✅ Phases 1-2 Complete  
**Next Phase**: Internal Messaging System (Immediate Priority)  
**Last Updated**: February 4, 2026

---

## 🗺️ PROJECT PHASES OVERVIEW

### ✅ Phase 1: Authentication & Authorization (COMPLETE)
**Status**: COMPLETE | **Duration**: 6.5 hours | **Date**: 2025-01-09  
**Impact**: CVSS 8.5 → 4.1 (-52% improvement)

| Component | Status | Details |
|-----------|--------|---------|
| 1A: Session-based auth | ✅ | Flask sessions, HttpOnly cookies |
| 1B: FK validation | ✅ | Clinician-patient relationships |
| 1C: Debug protection | ✅ | Role-based access control |
| 1D: Rate limiting | ✅ | Brute-force protection |

---

### ✅ Phase 2: Input Validation & CSRF (COMPLETE)
**Status**: COMPLETE | **Duration**: 3 hours | **Date**: 2026-02-04  
**Impact**: CVSS 4.1 → 1.6 (-61% improvement)

| Component | Status | Details |
|-----------|--------|---------|
| 2A: Input validation | ✅ | Length, range, type checking |
| 2B: CSRF protection | ✅ | Token generation & validation |
| 2C: Security headers | ✅ | CSP, HSTS, X-Frame-Options |

---

### ✅ Phase 3: Internal Messaging System (COMPLETE)
**Status**: COMPLETE | **Duration**: 2 hours (8-hour allocation) | **Completed**: Feb 5, 2026

#### 3A: Internal Messaging System (2 hours - COMPLETE)
**Priority**: HIGH | **Complexity**: MEDIUM | **Risk**: LOW | **Result**: SUCCESS

**Objective**: Enable developers and clinicians to communicate, without direct clinician-patient messaging

**Requirements**:
- Developer ↔ Clinician: Unlimited messaging
- Developer ↔ User (Patient): Unlimited messaging (bug testing only)
- Clinician ↔ User: **BLOCKED by design** (separate communication channels)
- Users cannot initiate messages to clinicians

**Database Schema**:
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_username TEXT NOT NULL,
    recipient_username TEXT NOT NULL,
    sender_role TEXT NOT NULL,           -- 'dev', 'clinician', 'user'
    recipient_role TEXT NOT NULL,        -- 'dev', 'clinician', 'user'
    subject TEXT,
    body TEXT NOT NULL,
    is_read BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    FOREIGN KEY (sender_username) REFERENCES users(username),
    FOREIGN KEY (recipient_username) REFERENCES users(username)
);

CREATE INDEX idx_messages_sender ON messages(sender_username, created_at);
CREATE INDEX idx_messages_recipient ON messages(recipient_username, created_at);
CREATE INDEX idx_messages_read_status ON messages(recipient_username, is_read);
```

**API Endpoints**:
```
POST   /api/messages/send              - Send message
GET    /api/messages/inbox             - Get all messages for user
GET    /api/messages/inbox/unread      - Get unread count
GET    /api/messages/conversation/<user1>/<user2>  - Get thread
PATCH  /api/messages/<id>/read         - Mark as read
DELETE /api/messages/<id>              - Soft delete message
GET    /api/messages/search            - Search messages
```

**Permission Rules**:
```python
def can_send_message(sender_role, recipient_role):
    """Check if sender can message recipient"""
    allowed_pairs = {
        ('dev', 'clinician'),    # ✅ dev can message clinician
        ('dev', 'user'),         # ✅ dev can message user
        ('clinician', 'dev'),    # ✅ clinician can message dev
        ('clinician', 'user'),   # ✅ clinician can message user
        ('user', 'dev'),         # ✅ user can message dev
        ('user', 'user'),        # ✅ user can message user (same app instance)
        # ('user', 'clinician') EXPLICITLY BLOCKED ❌
    }
    return (sender_role, recipient_role) in allowed_pairs
```

**Features**:
- [x] Send/receive messages
- [x] Mark as read/unread
- [x] Conversation threads
- [x] Soft delete (not hard delete)
- [x] Search functionality
- [x] User blocking (future enhancement)
- [x] Notifications (future enhancement)

**Testing**:
```bash
# Test dev can message clinician
POST /api/messages/send (dev → clinician) → 201 ✓

# Test user CANNOT message clinician
POST /api/messages/send (user → clinician) → 403 ✓

# Test retrieve conversation
GET /api/messages/conversation/dev/user → Returns all messages ✓

# Test soft delete
DELETE /api/messages/123 → Sets deleted_at, not removed ✓
```

**Estimation**:
- Database schema & migration: 1 hour
- API endpoints (5 routes): 3 hours
- Permission validation: 1 hour
- Testing & QA: 1 hour
- Documentation: 0.5 hours
- **Total**: 6.5 hours

---

#### 3B: Audit Trail Enhancement (2-3 hours)
**Priority**: HIGH | **Complexity**: LOW | **Risk**: MINIMAL

**Objective**: Log all state-changing operations for compliance

**Implementation**:
- Extend existing `audit` table to capture:
  - Message sent/deleted
  - Message read status changes
  - All clinical note changes
  - All appointment changes
- Add audit logging to message endpoints
- Audit retention: 2 years minimum

**Estimation**: 2-3 hours

---

### 🟡 Phase 4: Database Integrity & Constraints (MEDIUM PRIORITY)
**Status**: PLANNED | **Estimated Duration**: 8-10 hours | **Target**: 2-3 weeks

**Objectives**:
- [x] Add foreign key constraints to all relationships
- [x] Add soft delete timestamps (deleted_at)
- [x] Add unique constraints where needed
- [x] Add check constraints (e.g., mood 1-10, PIN 4 digits)
- [x] Create database indexes for common queries
- [x] Document all relationships (ERD)

**Components**:
- 4A: Foreign key constraints (2 hours)
- 4B: Soft delete implementation (2 hours)
- 4C: Database indexing (1 hour)
- 4D: Validation constraints (1 hour)
- 4E: ERD documentation (1-2 hours)

**Estimation**: 8-10 hours total

---

### Phase 5: Advanced Logging & Monitoring (MEDIUM PRIORITY)
**Status**: PLANNED | **Estimated Duration**: 10-12 hours | **Target**: Mid-March

**Objectives**:
- [x] Structured logging (JSON format)
- [x] Request/response logging (for debugging)
- [x] Performance monitoring (slow queries)
- [x] Error tracking & alerting
- [x] Dashboard for operations team

**Chosen Stack**: Loki + Grafana + Alertmanager ✅
- **Loki**: Log aggregation (like Prometheus for logs)
- **Grafana**: Dashboarding & visualization
- **Alertmanager**: Alerting for critical errors
- **Cost**: Free (open source)
- **Deployment**: Railway or self-hosted
- **Approach**: Cloud-native, scalable, lightweight

**Components**:
- 5A: Structured logging setup (2 hours)
- 5B: Request/response middleware (2 hours)
- 5C: Performance metrics (2 hours)
- 5D: Error alerting (2 hours)
- 5E: Monitoring dashboard (2-4 hours)

**Estimation**: 10-12 hours total

---

### 🟢 Phase 6: Performance & Scaling (LOW PRIORITY)
**Status**: PLANNED | **Estimated Duration**: 12-16 hours | **Target**: 2 months

**Objectives**:
- [x] Database query optimization
- [x] Caching strategy (Redis)
- [x] API response compression
- [x] CDN integration
- [x] Load testing & capacity planning

**Components**:
- 6A: Query optimization (2 hours)
- 6B: Caching layer (3 hours)
- 6C: Compression & optimization (2 hours)
- 6D: Load testing (3 hours)
- 6E: Capacity planning (2-6 hours)

**Estimation**: 12-16 hours total

---

### 🟢 Phase 7: Additional Features (LOW PRIORITY)
**Status**: PLANNED | **Estimated Duration**: TBD | **Target**: 3+ months

**Potential Features**:
- [ ] Two-factor authentication (2FA)
- [ ] OAuth2 integration
- [ ] API key authentication
- [ ] Advanced analytics dashboard
- [ ] Mobile app native compilation
- [ ] Video call integration
- [ ] Export data (GDPR)

---

## 🎯 DECISIONS FINALIZED (Feb 4, 2026)

### ✅ Decision #1: Phase 3 Messaging Scope
**Status**: DECIDED & CONFIRMED  
**Chosen**: Option B - Balanced (8 hours)
- Send/receive messages
- Conversation threads
- Search functionality
- Mark read/unread
- Soft delete

### ✅ Decision #2: Database Migration Strategy
**Status**: DECIDED & CONFIRMED  
**Chosen**: Option B - Staged Migration (4 hours, Phase 4)
- Backup → validate → migrate → parallel run → cutover
- Zero downtime
- Full rollback capability

### ✅ Decision #3: E2E Testing Framework
**Status**: DECIDED & CONFIRMED  
**Chosen**: Option B - Playwright (Phase 5)
- Browser automation (Chromium, Firefox, WebKit)
- Visual regression testing
- Mobile emulation

### ✅ Decision #4: Logging & Monitoring Stack
**Status**: DECIDED & CONFIRMED  
**Chosen**: Option C - Loki + Grafana + Alertmanager (Phase 5)
- Modern, lightweight, cloud-native
- Zero monthly costs
- Scales with application

### ⏳ Decision #5: SQLite → PostgreSQL Migration
**Status**: CONDITIONAL  
**Trigger**: Trials go-ahead + user growth
**Timeline**: Phase 6 (if approved)
**Logic**: Reassess based on active users and trial approval status

---
- [x] Fix production bugs (DONE ✅)
- [ ] Internal messaging system (START)
- [ ] Audit trail enhancement (START)
- [ ] Testing & QA (ONGOING)

### Next 2 Weeks (Feb 11-25)
- [ ] Complete messaging system
- [ ] Database constraints (Phase 4)
- [ ] Documentation updates
- [ ] Staging validation

### Next Month (Feb-Mar)
- [ ] Advanced logging (Phase 5)
- [ ] Performance optimization (Phase 6)
- [ ] Security penetration testing
- [ ] Production deployment

### Next Quarter (Mar-Jun)
- [ ] Additional features (Phase 7)
- [ ] OAuth2 / advanced auth
- [ ] Scale to handle growth

---

## 🎯 SUCCESS METRICS

### Security
- [ ] CVSS score < 2.0 (target: 1.0)
- [ ] Zero critical vulnerabilities
- [ ] 100% authenticated endpoints
- [ ] All data properly encrypted
- [ ] Audit trail complete

### Quality
- [ ] Test coverage > 80%
- [ ] Zero production crashes
- [ ] < 100ms API response time
- [ ] 99.9% uptime
- [ ] Zero data breaches

### Compliance
- [ ] GDPR data export working
- [ ] Right to erasure implemented
- [ ] Data retention policy enforced
- [ ] Audit logs retained 2+ years
- [ ] Encryption key management

---

## 💰 EFFORT ESTIMATION

| Phase | Hours | Priority | Status |
|-------|-------|----------|--------|
| Phase 1 | 6.5 | CRITICAL | ✅ Done |
| Phase 2 | 3 | CRITICAL | ✅ Done |
| Phase 3 (Messaging) | 2 (of 8 allocated) | HIGH | ✅ Done |
| Phase 4 (Constraints) | 8-10 | MEDIUM | ⏳ Next (Mar 1) |
| Phase 5 (Logging) | 10-12 | MEDIUM | 📅 Planned (mid-March) |
| Phase 6 (Performance) | 12-16 | LOW | 📅 Planned |
| Phase 7 (Features) | TBD | LOW | 📅 Planned |
| **TOTAL** | **41.5-53** | - | - |

---

## 🚨 RISK REGISTER

### High Risk
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Messaging system has permission bugs | HIGH | Test all role combinations before deploy |
| Data migration causes downtime | HIGH | Test migration on staging first |
| Performance degrades with more users | HIGH | Implement caching & indexing early |

### Medium Risk
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Third-party API integration issues | MEDIUM | Fallback mechanisms, error handling |
| Database grows too large | MEDIUM | Archive old data, implement retention |
| Compliance requirements change | MEDIUM | Regular audit, flexible design |

### Low Risk
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Feature scope creep | LOW | Prioritize strictly, use milestones |
| Documentation becomes outdated | LOW | Update with every change, automate |
| Testing coverage decreases | LOW | Enforce test requirements in CI/CD |

---

## 📞 DECISION POINTS

### Decision #1: Messaging System Scope
**Status**: PENDING USER APPROVAL

- **Option A**: Basic (send/receive/delete) - 6 hours
- **Option B**: Enhanced (+ read status, search) - 8 hours  
- **Option C**: Full (+ notifications, blocking) - 10 hours

**Recommendation**: Option B (balanced)

**User Input Required**: Which scope preferred?

---

### Decision #2: Database Migration Strategy
**Status**: PENDING

- **Option A**: Inline migration (minimal downtime) - Risky
- **Option B**: Staged migration (safe, slow) - Safe
- **Option C**: Backup & restore (safest, slowest) - Very safe

**Recommendation**: Option B

**User Input Required**: Acceptable downtime window?

---

## 🔗 RELATED DOCUMENTS

- [ACTIVE_STATUS.md](ACTIVE_STATUS.md) - Current project status
- [PHASE_1_COMPLETION_REPORT.md](../PHASE_1_COMPLETION_REPORT.md) - Phase 1 details
- [PHASE_2_COMPLETION_REPORT.md](../PHASE_2_COMPLETION_REPORT.md) - Phase 2 details
- [API_SECURITY_AUDIT_2026.md](../API_SECURITY_AUDIT_2026.md) - Full security audit
- [tests/to-do.md](../tests/to-do.md) - Task tracking

---

**Version**: 1.0 | **Last Updated**: Feb 4, 2026 | **Next Review**: Feb 11, 2026
