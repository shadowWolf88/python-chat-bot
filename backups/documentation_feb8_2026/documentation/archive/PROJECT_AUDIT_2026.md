# Healing Space - Project Audit & Roadmap (Feb 4, 2026)

## Executive Summary
- **Status**: MVP-ready with 65+ endpoints, working auth, AI therapy, CBT tools
- **Production**: Live on Railway (www.healing-space.org.uk)
- **Test Pass Rate**: 58% (7 of 12 tests passing; 3 auth tests need fixes, 1 skipped)
- **Critical Issues**: Test suite broken (auth/endpoints), password reset pending implementation
- **Next Priority**: Fix test suite → Security audit → Feature consolidation

---

# SECTION 1: TO-DO PRIORITY LIST (Technical Foundation)

## ✅ COMPLETED (Moved to Bottom)
- ✅ Remove country selection from patient sign-up (UK-only)
- ✅ Optional clinician selection with checkbox on registration
- ✅ PIN/password "show/hide" toggle works on all forms
- ✅ CBT tools authentication fixed (clinician search working)
- ✅ Clinician search by username/full name implemented
- ✅ Dropdown visibility improved (hidden until search results)
- ✅ CSRF token protection implemented
- ✅ User registration form redesigned (optional clinician)
- ✅ Theme switcher infrastructure in place
- ✅ Mood tracking functional
- ✅ Gratitude logging working
- ✅ Therapy chat history retrieval working
- ✅ Appointment scheduling endpoints working

---

## 🔴 CRITICAL BUGS (Fix Immediately)

### Bug #1: Test Suite Broken - Auth Tests Failing
**Impact**: Cannot verify auth endpoints work correctly  
**Status**: 3 of 12 tests failing (test_role_access.py)  
**Root Cause**: Tests expect server at localhost:5000 but it's not running  
**Fix Priority**: 🔴 CRITICAL
```
- Fix test isolation: Use app.test_client() instead of requests.post()
- Update test_role_access.py, test_integration_fhir_chat.py, test_appointments.py
- Set up test fixtures for user creation, login
- Run: pytest -v tests/ with DEBUG=1
- Target: 100% pass rate
```

### Bug #2: Password Reset Not Working *LEAVE FOR NOW*
**Impact**: Users cannot reset lost passwords  
**Status**: Endpoint created but email blocked by Railway SMTP firewall  
**Root Cause**: Railway blocks port 25 and 587 outbound SMTP  
**Fix Priority**: 🔴 CRITICAL
```
Options (choose one):
A) Twilio SMS (free tier: $15 credit, ~300 SMS) - Recommended
B) SendGrid (free tier: 100 emails/day, API-based, bypasses SMTP)
C) Lambda/Webhook for async email delivery

Selected: SMS via Twilio (more reliable, better UX)
Timeline: When user ready (added to backlog)
```

### Bug #3: Clinician Approval Workflow Missing Notifications
**Impact**: Clinicians don't get notified of pending approvals  
**Status**: Approvals table exists, notifications partially working  
**Root Cause**: Notification center needs real-time updates  
**Fix Priority**: 🟡 HIGH
```
- Add real-time polling to notifications tab
- Notify clinician when patient requests connection
- Notify patient when clinician approves/rejects
- Auto-refresh approvals list when status changes
```

---

## 🟡 HIGH PRIORITY (Next Sprint)

### 1. Database Consistency & Validation
**Tasks**:
- Validate all user input on backend (length, format, SQL injection)
- Add foreign key constraints (clinician_id, user_id)
- Add NOT NULL constraints where needed
- Audit database migrations for completeness
- Add default values for new columns

**Affected Files**: api.py (init_db function)

### 2. API Endpoint Security Audit
**Tasks**:
- Verify all endpoints check authentication (username in session)
- Verify all endpoints check authorization (role-based access)
- Remove @app.route('/api/admin/wipe') - security risk
- Add rate limiting (prevent brute force)
- Add request validation on all POST/PUT endpoints

**Current Endpoints Needing Review**:
- POST /api/auth/register (partial validation)
- POST /api/therapy/chat (needs user validation)
- POST /api/mood/log (needs user validation)
- POST /api/cbt/* (all need input validation)

### 3. Error Handling & Logging
**Tasks**:
- Replace all `print()` with `logger.error()` / `logger.info()`
- Add proper error responses (400/401/403/500 with messages)
- Add try/except to all database operations
- Log all state changes (approval, password reset, GDPR exports)
- Setup CloudWatch or file-based logging for Railway

### 4. Password Reset Implementation
**Tasks**:
- Set up Twilio account (get SID, Token, Phone)
- Add twilio to requirements.txt
- Create send_reset_sms() function
- Update forgot-password endpoint to send SMS
- Update confirm-reset endpoint to validate token
- Test: request reset → receive SMS → reset password

### 5. Test Suite Fixes (CRITICAL)
**Tasks**:
```
- Fix test_role_access.py: Use test client instead of localhost
- Fix test_appointments.py: Mock database properly
- Fix test_integration_fhir_chat.py: Setup test user fixtures
- Create conftest.py with shared test fixtures
- Target: 100% pass rate
```

**Run Tests**:
```bash
GROQ_API_KEY=test_key DEBUG=1 pytest -v tests/
```

### 6. Frontend/Backend Validation Mismatch
**Tasks**:
- Frontend validates: password strength, PIN format, email format
- Backend MUST validate same rules (don't trust frontend)
- Add backend validation for:
  - Password: min 8 chars, number, letter, special char
  - PIN: exactly 4 digits
  - Email: valid format
  - Username: alphanumeric, 3-20 chars
  - Phone: valid UK format

**Files to Update**: api.py (/api/auth/register, /api/auth/login)

---

## 🟠 MEDIUM PRIORITY (1-2 Weeks)

### 1. Dark Mode / Theme Switching
**Status**: Infrastructure exists, needs frontend completion
**Tasks**:
- Dark mode on login selection page
- Theme switcher on main dashboard
- Persist theme preference to localStorage
- Apply theme to all CBT tools and clinic dashboards
- Test on desktop and mobile

### 2. Insights Tab Scrollability
**Status**: Generated insights area gets cut off
**Tasks**:
- Add `overflow-y: auto; max-height: 400px;` to insights container
- Test with long insights
- Add smooth scroll behavior

### 3. AI Assistant "Thinking" Indicator
**Status**: Shows code/technical text, should be hidden
**Tasks**:
- Hide code blocks from user view
- Show only: "Thinking... ⏳" (2 second minimum)
- Replace code output with spinner/dots animation
- Test with Groq API

### 4. Patient Notifications on Info Changes
**Status**: Endpoint exists, clinician notifications missing
**Tasks**:
- Trigger notification when patient updates: email, phone, address
- Send to assigned clinician
- Add to notifications center
- Log to audit table

### 5. Database Schema Documentation
**Tasks**:
- Document all tables and columns
- Add comments to api.py init_db()
- Create ERD (Entity Relationship Diagram)
- Document foreign keys and constraints

---

## 🔵 NICE-TO-HAVE (3+ Weeks)

### 1. Appointment Management Enhancement
**Status**: Endpoints exist, attendance tracking missing
**Tasks**:
- Clinician can mark appointments attended/no-show
- Auto-notify patient of appointment reminders
- Suggest next appointment after session
- Add calendar view for clinicians

### 2. FHIR Export Enhancement
**Status**: Export works but needs validation
**Tasks**:
- Verify FHIR compliance (HMAC signing, validation)
- Add digital signature verification
- Test with NHS systems
- Document export process for clinicians

### 3. AI Training Data Management
**Status**: GDPR consent exists, anonymization needs work
**Tasks**:
- Verify anonymization removes PII
- Add consent tracking UI
- Allow users to opt-out from training
- Implement right-to-erasure
- Test anonymization with real data

---

---

# SECTION 2: FUTURE PLANS (Product Roadmap)

## Phase 1: MVP to NHS-Grade (Next 3 Months)

### NHS/Healthcare Compliance
```
MUST-HAVE for NHS implementation:
- ✅ FHIR export (90% done, needs testing)
- ✅ GDPR compliance (consent system in place)
- ❌ IG Toolkit compliance checklist
- ❌ Information Asset Register
- ❌ Data Protection Impact Assessment (DPIA)
- ❌ Incident response procedures
- ❌ Annual security review
- ✅ Audit logging (done)
- ✅ Encryption (Fernet, HTTPS)

Timeline: 2-4 weeks for documentation, 1 week for testing
```

### Security Hardening
```
- Add API rate limiting (5 requests/second per user)
- Implement CORS properly (whitelist domains only)
- Add CSRF token to all forms
- Implement session timeout (15 min inactivity)
- Add 2FA for clinicians/developers
- Rotate encryption key process
- Implement secret rotation
- Add Web Application Firewall (WAF) on Railway
```

### Production Monitoring
```
- Setup error tracking (Sentry integration)
- Add uptime monitoring (Pingdom or similar)
- Setup performance monitoring (New Relic Lite)
- Database backups to S3 (automated, daily)
- Implement log aggregation (CloudWatch or ELK)
```

---

## Phase 2: Engaging Patients (Months 4-6)

### Gamification Enhancements
```
Current: Pet system (Alfie), XP, coins
Additions:
- Achievement badges (5 therapy sessions, 30 mood logs, etc)
- Streak counter (consecutive days of logging)
- Weekly challenges (log mood 5x, complete 1 CBT exercise)
- Leaderboard (optional, privacy-respecting)
- Pet customization (hats, colors, accessories)
- Pet evolution (baby → child → adult → elder stages)
```

### Engagement Features
```
- Push notifications (Brave/Chrome PWA)
- In-app notifications (daily checkins: "How are you feeling?")
- Smart reminders (based on user patterns)
- Mood trend analysis ("You're doing better! 📈")
- Weekly email summary (mood, therapy sessions, progress)
- Celebration milestones ("You've logged 100 moods! 🎉")
```

### Social/Community (Optional)
```
- Anonymous peer support forum (moderated)
- Share strategies with peers (with consent)
- Community challenges (e.g., "30-day gratitude challenge")
- User testimonials (collected with consent)
- Resource library (curated articles, videos, coping strategies)
```

### Content Expansion
```
NEW CBT Tools:
- Thought records (full 5-column)
- Behavioral experiment tracker
- Activity scheduling (depression/low mood)
- Socratic questioning guide
- Worry time scheduler
- Values clarification (expanded)

NEW Self-Care:
- Sleep tracking (via wearables or manual log)
- Exercise tracking
- Nutrition logging (simple)
- Medication reminders
- Water intake reminder
```

---

## Phase 3: Clinician Toolkit (Months 6-9)

### Clinician Dashboard Enhancements
```
CURRENT: View patient list, see mood logs, approve connections
ADDITIONS:

Case Management:
- Session notes/progress notes (rich text editor)
- Patient treatment plan (goals + milestones)
- Risk assessment form (suicide risk, self-harm)
- Clinical observations (structured notes)
- Prescription tracking (link to medications)
- Referral management (to specialists)

Analytics:
- Patient outcomes dashboard (mood trends, session attendance)
- Cohort analysis (compare similar patients)
- Crisis trends (identify at-risk patients)
- Treatment effectiveness (outcomes by CBT tool used)
- Caseload capacity (how many patients, workload)

Communication:
- Secure messaging with patients (encrypted)
- Appointment scheduling (Calendly integration)
- Video call integration (Twilio, Jitsi)
- Session recording (with consent, encrypted)
- Document sharing (treatment plans, worksheets)

Care Coordination:
- Referral system (to other clinicians/services)
- Care team management (if multi-disciplinary)
- Letter generation (GP letters, referrals)
- Shared care plans (for patients under multiple clinicians)
```

### Clinician Onboarding
```
- Video walkthrough (5 min)
- Interactive checklist (first 5 tasks)
- Templates library (session notes, risk assessment)
- Customizable dashboard (drag-drop widgets)
- Mobile app (read-only patient data)
```

---

## Phase 4: Enterprise Features (Months 9-12)

### Organization/Clinic Features
```
- Multi-tenancy (each clinic has own instance)
- Admin dashboard (manage clinicians, patients, settings)
- Invoice generation (for private clinics)
- Billing integration (Stripe)
- Team management (assign clinicians to clinics)
- Audit reports (compliance for leadership)
- Patient batch import (CSV upload)
- Customizable branding (logo, colors, name)
```

### Advanced Analytics
```
- Executive dashboard (KPIs, metrics)
- Tableau/Power BI integration (data export)
- Predictive analytics (identify at-risk patients)
- Treatment outcome tracking (vs. benchmarks)
- Wait time metrics
- Staff utilization reports
```

### Integration Ecosystem
```
- EHR Integration (OpenEHR, Epic, Cerner)
- Payment Processing (Stripe, GoCardless)
- Video Conferencing (Zoom, Teams, Jitsi)
- Calendar Sync (Google Calendar, Outlook)
- Wearable Integration (Fitbit, Oura Ring - optional)
- SMS/WhatsApp integration (patient comms)
- Slack integration (clinician alerts)
- Zapier/IFTTT integration (automation)
```

---

## Developer Dashboard Roadmap

### Current State
```
✅ Terminal access (execute commands)
✅ Message center (internal comms)
✅ User list (view all users)
✅ User deletion
✅ Stats dashboard (basic)
✅ AI chat (for testing)
```

### Phase 1: Monitoring & Debugging (1-2 weeks)
```
NOTE: Railway doesn't expose system health (no CPU, memory API available)
WORKAROUND: Calculate from logs and response times

Features:
- Request log viewer (last 1000 requests, filterable)
- Error log viewer (last 100 errors, grouped by type)
- API response time stats (avg, p95, p99)
- Database query log (slow queries)
- Authentication log (login attempts, failures)
- API endpoint list (with hit counts)
- Session management (view active sessions, force logout)
- Environment variable list (masked passwords)
```

### Phase 2: Database Tools (2-3 weeks)
```
- Database backup status (last backup time, size)
- Manual backup trigger (on-demand backup)
- Backup restore (restore from backup with confirmation)
- Data import tool (CSV → database)
- Data export (full export, user export, patient cohort)
- Schema viewer (list tables, columns, types)
- Query builder (write custom queries, view results)
- Table size stats (which tables taking most space)
```

### Phase 3: Audit & Compliance (2-3 weeks)
```
- Audit log viewer (all state changes, deletions, exports)
- GDPR compliance report (user consents, data locations)
- Right-to-erasure tracking (pending erasures, completed)
- Anonymization verification (check data is truly anonymized)
- Training data export (for AI model improvement)
- Consent audit (who consented to what, when)
```

### Phase 4: Feature Management (1-2 weeks)
```
- Feature flags dashboard (enable/disable features)
- A/B testing setup (test new features with % of users)
- Rollout management (gradual rollout to users)
- Kill switch (disable feature immediately if issues)
- Feature documentation (what features are enabled)
```

### Phase 5: System Configuration (1-2 weeks)
```
- SMTP configuration (update email settings without code)
- API key management (create/revoke API keys)
- Webhook management (configure alert webhooks)
- Theme customization (colors, fonts, branding)
- Email templates (customize password reset, notification emails)
- SMS template (customize SMS messages)
- Retention policy (auto-delete old data after N days)
```

### Dream Features (Phase 6+)
```
- Bug reproduction tool (replay user session, reproduce bug)
- Performance profiler (identify slow functions)
- Database migration tool (schema changes with rollback)
- Automated testing dashboard (run tests, see results)
- Dependency vulnerability scanner (check for outdated packages)
- Load testing tool (simulate user traffic)
- Chaos engineering (simulate failures, test resilience)
```

---

## Viral Growth & User Acquisition

### Initial Launch Strategy (Phase 1)
```
1. NHS Integration
   - Work with 1-2 NHS trusts (pilot)
   - Get approval from Information Governance
   - Train clinicians on platform
   - Measure outcomes, gather feedback

2. PR & Marketing
   - Mental health media (Mind, Rethink, Young Minds)
   - Tech press (Techcrunch, Product Hunt launch)
   - LinkedIn B2B targeting (NHS clinicians, private practice)
   - Reddit mental health communities (honest discussion)

3. SEO & Content
   - Blog: "CBT tools for anxiety", "Mood tracking guide"
   - Guides: "How to use this platform with your therapist"
   - Video tutorials (YouTube, TikTok)
```

### Growth Hacks (Phase 2-3)
```
- Referral program (invite friend = both get badge/coins)
- Free trial for clinicians (30 days, no credit card)
- Freemium model (basic features free, premium for clinicians)
- Partner with therapy services (integration, co-marketing)
- University partnerships (research + usage)
- Mental health apps directory listings (MindApps, Psychreg)
```

### Monetization Strategy (Phase 3+)
```
Model: Freemium for patients, Premium for clinicians

FREE Tier (Patient):
- Unlimited mood logging
- All CBT tools
- Therapy chat (limited: 10 messages/week)
- Pet system
- Basic analytics

PREMIUM Tier (Clinician):
- Unlimited patients
- Full patient management dashboard
- Appointment scheduling
- Secure messaging
- FHIR export
- Billing/invoicing
- Price: £200-500/month or £2000-5000/year

Patient Premium (Optional):
- Unlimited therapy chat
- Video calls with clinician
- Priority support
- Ad-free experience
- Price: £9.99-19.99/month

NHS Enterprise:
- Custom deployment
- Dedicated support
- Integration with NHS EHR
- Audit reports
- Price: Custom (£10k-50k+/year)

Revenue Model:
- 70% from clinicians (B2B SaaS)
- 20% from patient premium
- 10% from NHS contracts
- Target: £100k MRR at year 2, £500k at year 3
```

---

---

# SECTION 3: COMPLETION CHECKLIST & PROJECT STATUS

## Test Results Summary
```
PASSING (7/12):
✅ test_calendar_page_headless - UI loads correctly
✅ test_init_db_creates_tables - Database initializes
✅ test_password_verify_and_migration - Password hashing works
✅ test_alert_persistence - Crisis alerts persist
✅ test_fhir_export_signed_and_valid - FHIR export valid
✅ browser_smoke_test passes - Headless browser works

FAILING (3/12):
❌ test_role_access (all 3 variants) - Auth tests need localhost server
❌ test_analytics_includes_appointments - Bad request on analytics
❌ test_attendance_endpoint - Missing auth

SKIPPED (1/12):
⏭️ test_sftp_helper_when_missing_paramiko - Paramiko not installed (OK)

FIX PRIORITY: High - need to fix auth tests + server startup issue
```

---

## Code Quality Checklist

| Area | Status | Notes |
|------|--------|-------|
| **Security** | 🟡 70% | Auth working, needs rate limiting, CSRF complete |
| **Testing** | 🟡 58% | 7/12 passing, auth tests need fixes |
| **Documentation** | 🔴 40% | API endpoints documented, missing user guides |
| **Error Handling** | 🟡 60% | Some endpoints have try/except, many use print() |
| **Validation** | 🟠 50% | Frontend validation works, backend needs enhancement |
| **Logging** | 🔴 40% | Using print(), should use logger |
| **Code Style** | 🟠 65% | Mostly consistent, some functions too long |
| **Database** | 🟢 85% | Schema solid, needs foreign keys |
| **API Design** | 🟢 80% | RESTful, consistent, good coverage |
| **Frontend** | 🟢 85% | Responsive, accessible, feature-complete |

---

## Dependency Status
```
PROD READY:
✅ flask (web framework)
✅ flask-cors (cross-origin)
✅ cryptography (Fernet encryption)
✅ requests (HTTP)

OPTIONAL:
❌ argon2 (password hashing - fallback: bcrypt)
❌ bcrypt (password hashing)
❌ paramiko (SFTP uploads)
❌ vault (HashiCorp Vault secrets)

NEEDED SOON:
❌ twilio (SMS for password reset)
⚠️  sentry (error tracking - recommended)
⚠️  python-dotenv (env vars - should use already)
```

---

## Known Issues & Technical Debt

### High Priority
1. **Test suite broken** - Auth tests expect localhost, use test client instead
2. **Password reset blocked** - Railway SMTP firewall, need SMS alternative
3. **Clinician notifications** - Missing real-time updates, use polling
4. **No database foreign keys** - Data integrity risk, add constraints

### Medium Priority
1. **print() logging** - Should use logger module
2. **Long functions** - Some functions exceed 100 lines
3. **Magic numbers** - Hardcoded values scattered in code
4. **No rate limiting** - Brute force vulnerability
5. **Validation inconsistent** - Frontend and backend differ

### Low Priority
1. **Code comments lacking** - Functions need docstrings
2. **No API versioning** - /api/v1/ would future-proof
3. **Error messages generic** - Could be more helpful
4. **Mobile testing** - Limited testing on phones

---

## Next Steps (This Week)

### Monday-Tuesday: Fix Test Suite
```
1. Convert test_role_access.py to use Flask test client
2. Fix test_appointments.py database setup
3. Fix test_integration_fhir_chat.py fixtures
4. Run pytest -v tests/ until 100% pass
5. Add CI/CD (GitHub Actions) to run tests on push
```

### Wednesday-Thursday: Password Reset
```
1. Set up Twilio account (5 min)
2. Add twilio to requirements.txt
3. Create send_reset_sms() function
4. Test with real phone (get SMS code)
5. Deploy to Railway
```

### Friday: Security Audit
```
1. Review all endpoints for auth checks
2. Add input validation to registration
3. Add rate limiting middleware
4. Document security findings
5. Create security checklist for NHS compliance
```

---

## Completed Items (Moved from Top)
- ✅ Patient registration (UK-only, optional clinician)
- ✅ Clinician login and dashboard
- ✅ Patient therapy chat with Groq AI
- ✅ Mood logging and tracking
- ✅ CBT tools (8 different tools)
- ✅ Crisis alerts (SafetyMonitor)
- ✅ Appointment scheduling
- ✅ FHIR export
- ✅ GDPR consent system
- ✅ Audit logging
- ✅ Password hashing with fallback
- ✅ Session management
- ✅ Gravatar integration
- ✅ Pet gamification system
- ✅ Dark theme support
- ✅ Responsive design
- ✅ CSRF protection
- ✅ Role-based access control
- ✅ Clinician search functionality
- ✅ Email configuration (Zoho, pending SMS)

---

**Last Updated**: Feb 4, 2026  
**Next Audit**: Feb 11, 2026  
**Deployed On**: Railway (www.healing-space.org.uk)
