# Healing Space - Priority To-Do List

**Last Updated**: Feb 4, 2026 | **Next Review**: Feb 11, 2026

---

# SECTION 1: CRITICAL - FIX IMMEDIATELY (This Week)

## 🔴 #1: Test Suite Broken
**Time**: 2-3 hours  
**Blocker**: Cannot verify endpoints work  
**Why**: Tests expect Flask test client, not localhost server

```
TASKS:
[ ] Convert test_role_access.py to use app.test_client()
[ ] Fix test_appointments.py database setup
[ ] Fix test_integration_fhir_chat.py with proper fixtures
[ ] Create conftest.py with shared fixtures
[ ] Run: GROQ_API_KEY=test DEBUG=1 pytest -v tests/
[ ] Target: 100% pass rate (12/12)
[ ] Add GitHub Actions CI/CD on push

SUBTASKS:
- Remove requests.post(localhost) calls
- Use client = app.test_client() at test start
- Setup test user (patient/clinician/dev)
- Mock Groq API calls
- Use tmp_path for temp databases
```

## 🔴 #2: Password Reset Implementation
**Time**: 4-6 hours  
**Blocker**: Users cannot reset lost passwords  
**Why**: Chosen Twilio SMS (more reliable, bypasses email firewall)

```
TASKS:
[ ] Create Twilio account (get SID, Auth Token, Phone)
[ ] Add TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER to Railway Variables
[ ] Install twilio: pip install twilio
[ ] Create send_reset_sms() in api.py
[ ] Update forgot-password endpoint (ask for phone, send SMS)
[ ] Update confirm-reset endpoint (SMS code validation)
[ ] Test: Request reset → Receive SMS → Reset via code
[ ] Fallback: Show reset token in browser if SMS fails (DEBUG only)

SUBTASKS:
- Validate phone format (UK: +44 or 07xxx)
- Generate 6-digit code, store in database
- Expiry: 15 minutes
- Rate limit: 3 requests per user per hour
- Log to audit table
```

## 🔴 #3: API Security Audit
**Time**: 3-4 hours  
**Blocker**: Endpoints may be vulnerable  
**Why**: Not all endpoints validate user/role

```
CRITICAL CHECKS:
[ ] POST /api/therapy/chat - Verify username in body matches session
[ ] POST /api/mood/log - Verify username parameter
[ ] POST /api/cbt/* - Verify all CBT endpoints validate user
[ ] GET /api/debug/analytics - Remove or restrict to dev only
[ ] POST /api/admin/wipe - Security risk, document restricted access
[ ] All endpoints - Check for SQL injection (use parameterized queries)
[ ] All POST endpoints - Validate input length, format, type

MEDIUM PRIORITY:
[ ] Add rate limiting (5 req/sec per user)
[ ] Add CORS whitelist (restrict to www.healing-space.org.uk only)
[ ] Add session timeout (15 min inactivity)
[ ] Document all security measures
```

---

# SECTION 2: HIGH PRIORITY (Next 1-2 Weeks)

## Task #1: Database Validation & Constraints
**Time**: 4-5 hours
```
[ ] Add foreign keys: users(clinician_id) → users(id)
[ ] Add NOT NULL constraints where appropriate
[ ] Add CHECK constraints (e.g., PIN must be 4 digits)
[ ] Add DEFAULT values (e.g., created_at DATETIME DEFAULT NOW())
[ ] Review all queries for N+1 queries
[ ] Add indexes on frequently queried fields (username, email, created_at)
[ ] Test migrations with test database
```

## Task #2: Input Validation Consistency
**Time**: 3-4 hours
```
Backend must validate (never trust frontend):
[ ] Password: min 8 chars, has uppercase, number, special char
[ ] PIN: exactly 4 digits (0-9)
[ ] Email: valid format via regex
[ ] Username: 3-20 chars, alphanumeric + underscore
[ ] Phone: valid UK format (+44 or 07xxx)
[ ] Mood score: 1-10 range
[ ] All string inputs: max length checks (prevent abuse)

Files to update:
- api.py: /api/auth/register
- api.py: /api/auth/login
- api.py: /api/mood/log
- api.py: /api/cbt/* (all CBT endpoints)
```

## Task #3: Error Handling & Logging
**Time**: 4-5 hours
```
[ ] Replace all print() with logger.error()/logger.info()
[ ] Create logging.py module
[ ] Setup file-based logging (logs/ directory)
[ ] Configure CloudWatch for Railway logs
[ ] Add try/except to all database operations
[ ] Return proper HTTP status codes (400/401/403/500)
[ ] Never return stack traces to frontend
[ ] Log all state changes (for audit trail)

Log Events:
- User login/logout
- Authentication failures
- Password/PIN changes
- GDPR exports/deletes
- Approvals (accept/reject)
- Data exports
```

## Task #4: Clinician Approval Notifications
**Time**: 3-4 hours
```
[ ] Implement polling notification check (every 5 seconds)
[ ] Notify clinician: "New patient request from [name]"
[ ] Add notification to navbar (red badge count)
[ ] Show pending approvals in list
[ ] Notify patient: "Clinician approved/rejected your request"
[ ] Real-time update (no page refresh needed)

Implementation:
- Frontend: setInterval(checkNotifications, 5000) in clinician-dashboard
- Backend: GET /api/notifications - with unread count
- Frontend: Auto-refresh approvals list when status changes
```

## Task #5: Dark Mode Implementation
**Time**: 2-3 hours
```
[ ] Dark mode on login selection page (patient/clinician/dev)
[ ] Theme switcher on main dashboard (☀️/🌙 button)
[ ] Persist to localStorage (remember user preference)
[ ] Apply to: Dashboard, CBT tools, Clinic dashboard
[ ] Test contrast ratios (WCAG AA standard)
[ ] Test on mobile devices

CSS Variables:
- --bg-primary, --bg-secondary
- --text-primary, --text-secondary
- --border-color, --accent-color
```

---

# SECTION 3: MEDIUM PRIORITY (2-4 Weeks)

## Task #1: Insights Tab Scrollability
**Time**: 1 hour
```
[ ] Add CSS: overflow-y: auto; max-height: 400px; to insights container
[ ] Add smooth scroll behavior
[ ] Add scrollbar styling (custom if needed)
[ ] Test with long insight text
```

## Task #2: AI "Thinking" Indicator
**Time**: 2 hours
```
[ ] Hide code blocks in AI response
[ ] Show only: "Thinking... ⏳" (min 2 second delay)
[ ] Replace spinner with animated dots
[ ] Test with Groq API responses
[ ] Ensure no technical jargon visible to users
```

## Task #3: Patient Info Change Notifications
**Time**: 2-3 hours
```
[ ] Trigger notification when patient updates: email, phone, address
[ ] Send to assigned clinician
[ ] Add to clinician notifications center
[ ] Log to audit table
[ ] Endpoint: POST /api/patient/profile (validate changes, notify clinician)
```

## Task #4: Database Schema Documentation
**Time**: 3-4 hours
```
[ ] Document all tables in README
[ ] Create ERD (Entity Relationship Diagram) - use dbdiagram.io
[ ] Add comments to every function in api.py
[ ] Document all database relationships
[ ] Create data dictionary (column names, types, meanings)
[ ] Store in documentation/ folder
```

## Task #5: Appointment Enhancements
**Time**: 4-5 hours
```
[ ] Clinician marks attendance (attended/no-show)
[ ] Auto-notify patient 24h before appointment
[ ] Suggest next appointment after session
[ ] Calendar view for clinicians (month/week/day)
[ ] Sync to Google Calendar (optional)
```

---

# SECTION 4: NICE-TO-HAVE (3-8 Weeks)

## Gamification Enhancements
```
[ ] Achievement badges (5 sessions, 30 mood logs, etc.)
[ ] Streak counter (consecutive days)
[ ] Weekly challenges (log mood 5x, complete CBT)
[ ] Pet evolution (baby → child → adult → elder)
[ ] Pet customization (hats, colors, accessories)
[ ] Leaderboard (optional, privacy mode)
```

## Engagement Features
```
[ ] Push notifications (PWA, daily checkins)
[ ] Weekly email summary
[ ] Mood trend analysis ("You're doing better! 📈")
[ ] Celebration milestones ("100 moods logged! 🎉")
[ ] Smart reminders (based on user patterns)
```

## New CBT Tools
```
[ ] Thought records (full 5-column version)
[ ] Behavioral experiments
[ ] Activity scheduling (depression toolkit)
[ ] Socratic questioning guide
[ ] Worry time scheduler
[ ] Values clarification (expanded)
```

## Clinician Dashboard
```
[ ] Session notes & progress notes (rich text)
[ ] Treatment plans (goals + milestones)
[ ] Risk assessment forms
[ ] Patient analytics (mood trends, outcomes)
[ ] Secure messaging
[ ] Video call integration (Twilio/Jitsi)
[ ] Appointment scheduling UI
[ ] FHIR export to file
```

---

# SECTION 5: FUTURE IDEAS & VIRAL GROWTH

## Viral Growth Strategy (Phase 2-3)
```
NHS Integration:
- Pilot with 1-2 NHS trusts
- Get Information Governance approval
- Train clinicians
- Measure outcomes

Marketing:
- Mental health media outreach
- Tech press (Product Hunt launch)
- LinkedIn B2B targeting
- Reddit mental health communities

Content:
- Blog: "CBT for Anxiety", "Mood Tracking Guide"
- Video tutorials (YouTube, TikTok)
- SEO optimization
```

## Freemium Model
```
PATIENT FREE:
- Unlimited mood logging
- All CBT tools
- Pet system
- Basic analytics

CLINICIAN PREMIUM (£200-500/month):
- Patient dashboard
- Session notes
- Appointment scheduling
- Secure messaging
- FHIR export
- Billing/invoicing

NHS ENTERPRISE:
- Custom deployment
- Dedicated support
- EHR integration
- Audit reports
- Price: £10k-50k+/year

TARGET REVENUE:
- Year 1: £5k MRR (proof of concept)
- Year 2: £100k MRR (50+ clinicians)
- Year 3: £500k MRR (viral growth)
```

## Enterprise Features
```
Multi-tenancy:
[ ] Each clinic has own instance
[ ] Admin dashboard (manage users, settings)
[ ] Invoice generation
[ ] Billing integration (Stripe)

Integrations:
[ ] EHR (OpenEHR, Epic, Cerner)
[ ] Video (Zoom, Teams, Jitsi)
[ ] Calendar (Google, Outlook)
[ ] Wearables (Fitbit, Oura)
[ ] SMS/WhatsApp
[ ] Zapier/IFTTT
```

## Developer Dashboard Ideas
```
Monitoring:
[ ] Request/error log viewer
[ ] API response time stats
[ ] Authentication logs
[ ] Session management

Database Tools:
[ ] Backup status & triggers
[ ] Data import/export tools
[ ] Schema viewer
[ ] Query builder

Audit & Compliance:
[ ] Audit log viewer
[ ] GDPR compliance reports
[ ] Right-to-erasure tracking
[ ] Consent audits

Feature Management:
[ ] Feature flags
[ ] A/B testing setup
[ ] Kill switches
[ ] Gradual rollout

System Config:
[ ] SMTP settings
[ ] API key management
[ ] Webhook configuration
[ ] Email templates
[ ] Theme customization

Dream Features:
[ ] Bug reproduction tool
[ ] Performance profiler
[ ] Dependency vulnerability scanner
[ ] Load testing tool
[ ] Chaos engineering
```

---

# ✅ COMPLETED ITEMS (Moved from Top)

## Registration & Onboarding
- ✅ Remove country selection (UK-only)
- ✅ Make clinician optional (checkbox)
- ✅ Clinician search by username/name
- ✅ Dropdown visibility fixed (hidden until search)
- ✅ PIN/password visibility toggles
- ✅ Password strength indicator
- ✅ Confirmation validation

## Authentication & Security
- ✅ Patient login/registration
- ✅ Clinician login/registration  
- ✅ Developer login/registration
- ✅ Password hashing (Argon2 → bcrypt → PBKDF2)
- ✅ Session management
- ✅ CSRF protection

## Core Features
- ✅ Therapy chat with Groq AI
- ✅ Mood logging & tracking
- ✅ Gratitude journal
- ✅ 8 CBT tools (Goals, Values, Self-compassion, Coping cards, Problem-solving, Exposure, Core beliefs, Sleep, Breathing, Relaxation)
- ✅ Crisis alert detection
- ✅ Appointment scheduling
- ✅ Pet gamification (Alfie)
- ✅ Dark theme support

## Data Management
- ✅ FHIR export (HMAC signed)
- ✅ GDPR consent system
- ✅ Training data anonymization
- ✅ Audit logging
- ✅ User profile management
- ✅ Backup system (auto daily)

## Infrastructure
- ✅ Flask REST API (65+ endpoints)
- ✅ SQLite database
- ✅ Railway deployment
- ✅ Responsive design (mobile-friendly)
- ✅ Gravatar integration
- ✅ Error handling

---

## How to Use This Document

### Daily Development
1. Check **CRITICAL** section first - fix blockers
2. Work top-to-bottom within each priority tier
3. Move completed tasks to checklist (✅)
4. Update time estimates as you work

### Weekly Planning
1. Review current sprint (1 week = ~30-40 hours)
2. Pick 2-3 HIGH priority tasks
3. Unblock CRITICAL issues
4. Estimate: CRITICAL (10h), HIGH (20h), MEDIUM (30h)

### Monthly Review
1. Move completed to bottom section
2. Update time estimates
3. Adjust priorities based on feedback
4. Create new tasks from issues/PRs

---

**Next Review**: Feb 11, 2026  
**Current Focus**: Test suite + Password reset + Security audit  
**Team Size**: 1 (solo development)
