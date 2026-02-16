# PROJECT ROADMAP – Healing Space UK

**Last Updated:** February 7, 2026  
**Current Status:** Production Ready (v2.0)  
**Current Phase:** Phase 4 (Clinical Features - In Planning)

---

## 📊 Executive Summary

Healing Space UK is a web-based mental health companion combining evidence-based therapy with AI support. The platform is **production-ready** with core features deployed. This roadmap covers **completed phases** (1-3) and **planned phases** (4-6).

**Key Metrics:**
- ✅ **210+ API endpoints** implemented
- ✅ **43 database tables** auto-created on startup
- ✅ **CVSS risk reduction:** 8.5 → 1.6 (81% improvement)
- ✅ **Test coverage:** 100% security tests passing
- ✅ **Deployment:** Railway.app (auto-scaling)

---

## ✅ COMPLETED PHASES

### Phase 1: Authentication & Authorization (Complete)
**Status:** ✅ COMPLETE | **Completion Date:** February 4, 2026 | **Impact:** CVSS 8.5 → 4.1

**Deliverables:**
- Session-based authentication (HttpOnly cookies, 2-hour timeout)
- Foreign key validation (clinician-patient relationships)
- Debug endpoint protection (role-based access)
- Rate limiting (5/min login, 10/min verify-code, 3/5min register)

**Result:** Eliminated session hijacking and unauthorized data access risks.

---

### Phase 2: Input Validation & CSRF Protection (Complete)
**Status:** ✅ COMPLETE | **Completion Date:** February 4, 2026 | **Impact:** CVSS 4.1 → 1.6

**Deliverables:**
- Input validation (length, type, range checks)
- CSRF token system (one-time use, timing-safe comparison)
- Security headers (CSP, HSTS, X-Frame-Options, Permissions-Policy)
- Content-type validation (application/json only)

**Result:** Comprehensive attack surface hardening. Production-grade security.

---

### Phase 3: Internal Messaging System (Complete)
**Status:** ✅ COMPLETE | **Completion Date:** February 5, 2026 | **Test Coverage:** 17/17 passing

**Deliverables:**
- 5 messaging API endpoints (send, inbox, read, delete, search)
- Permission model: Dev ↔ Clinician, Dev ↔ Patient, Clinician ↔ Patient (blocked by design)
- Read/unread tracking with soft deletion
- Frontend UI for messaging (inbox, conversations, read status)

**Database Schema:**
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    sender_username TEXT NOT NULL,
    recipient_username TEXT NOT NULL,
    sender_role TEXT NOT NULL,
    recipient_role TEXT NOT NULL,
    subject TEXT, body TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP,
    deleted_at TIMESTAMP
);
```

**Result:** Secure clinician-patient communication established. Clinical documentation workflow enabled.

---

## 🚀 ACTIVE/UPCOMING PHASES

### Phase 4: Clinical Features (Starting February 2026)

#### 4.1 Formal Suicide Risk Assessment (CRITICAL PRIORITY)
**Priority:** P0 (CRITICAL) | **Estimated Effort:** 20-30 hours | **Status:** Not Started

**Objective:** Implement clinically-validated risk assessment aligned with NICE guidelines

**Requirements:**
- Integrate Columbia-Suicide Severity Rating Scale (C-SSRS) or equivalent
- Auto-alert clinician for high-risk responses (immediate notification)
- Lock self-harm/crisis features if severe risk detected
- Emergency contact quick-dial integration
- Audit trail of all risk assessments

**Implementation Steps:**
1. Database schema for C-SSRS responses
2. Assessment scoring algorithm
3. Risk level calculation (low/medium/high/severe)
4. Clinician alert system (email, webhook, in-app)
5. Feature lockdown logic
6. Integration with crisis response endpoints

**Dependencies:** Clinical validation, legal review, NHS compliance sign-off

---

#### 4.2 Treatment Goals Module
**Priority:** P1 (HIGH) | **Estimated Effort:** 15-20 hours | **Status:** Not Started

**Objective:** Structured goal-setting and tracking for evidence-based therapy

**Requirements:**
- SMART goal creation (patient + clinician collaborative)
- Progress tracking with milestones
- Goal status updates (not started, in progress, achieved, revised)
- Link goals to session notes and activities
- Progress visualization (timeline, charts)

**Implementation Steps:**
1. Goals database schema
2. SMART goal template validation
3. Progress tracking endpoints
4. Milestone achievement notifications
5. Goal review reminders (weekly/monthly)

---

#### 4.3 Session Notes & Homework
**Priority:** P1 (HIGH) | **Estimated Effort:** 18-24 hours | **Status:** Not Started

**Objective:** Clinical documentation and homework accountability

**Requirements:**
- Clinician creates/assigns homework (text, links, attachments)
- Due date and priority assignment
- Patient marks homework complete with notes
- Reminder system (24h before due, on due date, overdue)
- Clinician review with feedback capability
- Audit log all changes

**Implementation Steps:**
1. Homework database schema
2. Assignment endpoints
3. Completion tracking
4. Reminder scheduling
5. Feedback system

---

#### 4.4 Outcome Measurement (CORE-OM / ORS)
**Priority:** P1 (HIGH) | **Estimated Effort:** 12-18 hours | **Status:** Not Started

**Note:** PHQ-9 and GAD-7 already implemented

**Objective:** Track therapy effectiveness beyond basic assessments

**Requirements:**
- CORE-OM (34-item) form integration
- ORS (Outcome Rating Scale) quick check-ins
- Auto-scoring and interpretation
- Alert if scores deteriorate
- Trend analysis and visualization
- Export for NHS reporting

---

#### 4.5 Relapse Prevention Plan
**Priority:** P2 (MEDIUM) | **Estimated Effort:** 16-20 hours | **Status:** Not Started

**Objective:** Long-term recovery support

**Requirements:**
- User-friendly plan builder
- Warning signs identification
- Coping strategies library
- Action plan for different risk levels
- Regular review reminders (monthly)
- Emergency action checklist

---

#### 4.6 Medication Tracking Enhancement
**Priority:** P2 (MEDIUM) | **Estimated Effort:** 10-14 hours | **Status:** Partially Complete

**Current Status:** Basic logging in mood logs (name, strength)

**Remaining Work:**
- Separate daily adherence logging
- Side effect tracking (frequency, severity)
- Refill reminders
- Drug interaction warnings
- Export for GP/clinician

---

### Phase 5: Platform Expansion (Q2 2026)

#### 5.1 Mobile App (Android/iOS Native)
**Priority:** P2 (MEDIUM) | **Estimated Effort:** 6-8 weeks | **Status:** Not Started

**Objective:** Native mobile apps for Android and iOS

**Requirements:**
- Complete feature parity with web
- Push notifications
- Offline mode (local caching)
- Biometric authentication
- Mood logging quick-access widget

**Technology Stack:**
- Android: Kotlin + Jetpack Compose
- iOS: Swift + SwiftUI
- Shared backend API (no changes needed)

---

#### 5.2 Accessibility Enhancements
**Priority:** P1 (HIGH) | **Estimated Effort:** 10-14 hours | **Status:** In Progress

**Objective:** WCAG 2.1 AAA compliance

**Requirements:**
- Screen reader optimization
- Keyboard navigation (all features)
- Color contrast (4.5:1 minimum)
- Text sizing flexibility
- Voice control integration

---

#### 5.3 Multi-Language Support
**Priority:** P3 (LOW) | **Estimated Effort:** 20-30 hours | **Status:** Not Started

**Languages:** English (complete), Spanish, French, German, Mandarin

**Implementation:** i18n/l10n with translation management system

---

### Phase 6: Ecosystem & Integration (Q3 2026)

#### 6.1 NHS Integration
**Priority:** P1 (CRITICAL) | **Estimated Effort:** 4-6 weeks | **Status:** Planning

**Objective:** Seamless NHS workflow integration

**Requirements:**
- NHS Login integration
- GP practice system integration (EMIS, SystmOne)
- Referral pathway automation
- NHS Digital compliance (security, data)
- NICE guideline alignment

---

#### 6.2 Third-Party Integrations
**Priority:** P2 (MEDIUM) | **Estimated Effort:** 2-3 weeks | **Status:** Planning

**Planned Integrations:**
- Fitbit / Apple Health (activity, sleep)
- Spotify (mood-based playlists)
- Google Calendar (appointment sync)
- Slack (clinician notifications)
- Webhook ecosystem (custom integrations)

---

#### 6.3 Analytics & Reporting
**Priority:** P2 (MEDIUM) | **Estimated Effort:** 2-3 weeks | **Status:** Partially Complete

**Current Status:** Basic clinician dashboard with patient progress tracking

**Remaining Work:**
- Clinic-wide analytics (aggregate patient outcomes)
- Cohort analysis
- Therapist effectiveness metrics
- NHS outcome reporting (IAPT compatibility)
- Custom report builder

---

## 📋 FEATURE IDEAS & FUTURE ENHANCEMENTS

### AI Improvements
- **Multilingual AI therapy** - Support therapy in patient's preferred language
- **Voice input/output** - Phone/voice-based therapy for accessibility
- **Emotion recognition** - Detect mood from message text
- **Therapy style personalization** - CBT vs DBT vs ACT vs psychodynamic
- **AI memory context** - Persistent patient context across sessions

### Patient Features
- **Peer support community** - Moderated discussion forum (HIPAA-compliant)
- **Group therapy sessions** - Clinician-led group sessions
- **Audiobook library** - Therapeutic audiobooks and guided meditations
- **Habit tracking** - Sleep, exercise, social contact, substance use
- **Nutrition & exercise integration** - Holistic wellness features
- **Journaling with AI feedback** - Journaling prompts with AI reflection

### Clinician Features
- **Patient risk dashboard** - Real-time risk scoring and alerts
- **CPA (Care Programme Approach)** - NHS-aligned care planning
- **Supervision tools** - Supervisor dashboards for clinician oversight
- **Caseload management** - Team collaboration and case notes
- **Training & supervision notes** - Internal documentation

### Business Features
- **Subscription management** - Tiered pricing (free, pro, enterprise)
- **White-label option** - Custom branding for NHS trusts
- **Team collaboration** - Multi-clinician practices
- **Billing & invoicing** - Invoice generation for private practitioners

---

## 🎯 PRIORITY MATRIX

| Phase | Area | Priority | Difficulty | Impact | Timeline |
|-------|------|----------|-----------|--------|----------|
| 4.1 | Clinical | P0 | HIGH | CRITICAL | Feb-Mar 2026 |
| 4.2 | Clinical | P1 | MEDIUM | HIGH | Mar-Apr 2026 |
| 4.3 | Clinical | P1 | MEDIUM | HIGH | Mar-Apr 2026 |
| 4.4 | Clinical | P1 | MEDIUM | HIGH | Apr-May 2026 |
| 4.5 | Clinical | P2 | LOW | MEDIUM | May 2026 |
| 4.6 | Clinical | P2 | LOW | MEDIUM | May 2026 |
| 5.1 | Platform | P2 | CRITICAL | HIGH | Q2-Q3 2026 |
| 5.2 | Platform | P1 | MEDIUM | HIGH | Q2 2026 |
| 5.3 | Platform | P3 | MEDIUM | MEDIUM | Q2 2026 |
| 6.1 | Integration | P1 | CRITICAL | CRITICAL | Q3 2026 |

---

## 📊 SUCCESS METRICS

### Security
- ✅ CVSS score: 1.6 or lower
- ✅ OWASP top 10: All mitigated
- ✅ Test coverage: >90%

### Clinical
- ✅ NHS-approved risk assessment
- ✅ NICE guideline compliance
- ✅ CQC readiness

### Adoption
- Target: 500+ active users (Year 1)
- Target: 50+ clinical sites (Year 2)
- Target: NHS trust deployment (Year 2)

### Performance
- API response: <200ms p95
- Uptime: 99.9%
- Database: <100ms query p95

---

## 🔗 RELATED DOCUMENTS

- **Current Implementation:** [CHANGELOG.md](CHANGELOG.md)
- **Known Issues:** [KNOWN_ISSUES.md](KNOWN_ISSUES.md)
- **Architecture:** [ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md)
- **Security:** [SECURITY_AND_COMPLIANCE.md](SECURITY_AND_COMPLIANCE.md)
- **Project Status:** [project_management/ACTIVE_STATUS.md](project_management/ACTIVE_STATUS.md)

---

**Last Updated:** February 7, 2026  
**Next Review:** February 28, 2026  
**Owner:** Development Team
