---
# Healing Space – Future Updates Roadmap

**Last Updated:** January 2026 (Post-Phase 6 Security Audit)

**Status:**
This roadmap lists only new and in-progress features. For a complete, chronological log of all completed work, see [ALL_STEPS_COMPLETE.md](ALL_STEPS_COMPLETE.md).

**Current Security Rating:** A (Production Ready)
**Issues Resolved:** 38/43 (88%)

---

## COMPLETED PHASES (Summary)

The following phases have been completed and are now in production:

### Phase 1-3: Security, Data Protection & Core Engagement ✅
- CSRF protection, XSS prevention, SQL injection prevention
- Shell injection prevention (command whitelist)
- Input validation and sanitization
- Argon2 password hashing with bcrypt/PBKDF2 fallback
- Fernet encryption for PII
- Rate limiting system
- Security headers (HSTS, CSP, X-Frame-Options, etc.)
- GDPR consent management for AI training
- Pet gamification system with coins, XP, shop, adventures
- Community features with moderation
- AI therapy chat with GROQ integration

### Phase 6: Security Audit (January 2026) ✅
- Comprehensive security audit completed
- All Critical (P0) and High (P1) issues resolved
- Production console suppression
- Global fetch error handling
- HTML sanitization across all user content
- Traceback leak prevention
- Authorization verification on all sensitive endpoints

---

## PHASE 4: CLINICAL FEATURES (IN PROGRESS)

### 4.1 Formal Suicide Risk Assessment 🔴 HIGH PRIORITY
- **Status:** Not Started
- **Rationale:** Clinical safety, regulatory requirement (NHS, NICE, CQC)
- **Implementation Steps:**
  - Integrate C-SSRS or equivalent assessment
  - Auto-alert clinician for high-risk responses
  - Lock high-risk features if severe risk detected
  - Emergency contact quick-dial integration
- **Dependencies:** Clinical validation, legal review

### 4.2 Treatment Goals Module
- **Status:** Not Started
- **Rationale:** Supports evidence-based, goal-oriented therapy
- **Implementation Steps:**
  - SMART goal creation UI (patient + clinician)
  - Progress tracking with milestones
  - Link goals to activities and session notes

### 4.3 Session Notes & Homework
- **Status:** Not Started
- **Rationale:** Improves therapy outcomes, supports clinical documentation
- **Implementation Steps:**
  - Clinician assigns homework; patient marks as complete
  - Due date reminders via notification system
  - Audit log all changes

### 4.4 Outcome Measurement (CORE-OM / ORS)
- **Status:** Not Started
- **Rationale:** Track therapy effectiveness beyond PHQ-9/GAD-7
- **Implementation Steps:**
  - Integrate CORE-OM and ORS forms
  - Auto-score and interpret results
  - Alert if scores deteriorate
- **Note:** PHQ-9 and GAD-7 already implemented

### 4.5 Relapse Prevention Plan
- **Status:** Not Started
- **Rationale:** Supports long-term recovery
- **Implementation Steps:**
  - User-friendly plan builder (warning signs, coping strategies)
  - Action plan for different risk levels
  - Regular review reminders

### 4.6 Medication Tracking Enhancement
- **Status:** Partially Complete
- **What's Done:** Basic medication logging in mood logs (name, strength)
- **Remaining:**
  - Separate daily adherence logging
  - Side effect tracking
  - Refill reminders
  - Export for GP/clinician

### 4.7 Clinical Safety Dashboard Enhancement
- **Status:** Partially Complete
- **What's Done:** Alert system, clinician alerts tab, 7-day alert tracking
- **Remaining:**
  - Consolidated safety dashboard view
  - Filters for patient, risk type, time period
  - Prioritization and escalation workflows

### 4.8 Cultural & Linguistic Inclusivity
- **Status:** Not Started
- **Rationale:** Accessibility for diverse populations
- **Implementation Steps:**
  - Multi-language support (top 5 patient languages)
  - Cultural sensitivity review
  - Language selection in profile

### 4.9 Clinical Escalation Protocols
- **Status:** Not Started
- **Rationale:** Clear, auditable escalation for high-risk cases
- **Implementation Steps:**
  - Define escalation pathways
  - Integrate into clinician UI
  - Log all escalations in audit trail

### 4.12 AI/LLM Safety & Explainability
- **Status:** Not Started
- **Rationale:** Ensures AI features are safe and transparent
- **Implementation Steps:**
  - "Why did I get this answer?" explainability
  - Regular AI output review for safety/bias
  - Clear disclaimers and human escalation

### 4.14 Crisis Follow-Up & Safety Planning
- **Status:** Partially Complete
- **What's Done:** Safety plan module, crisis resources
- **Remaining:**
  - Automated follow-up check-ins after crisis
  - Track completion of updated safety plans
  - Escalate if follow-up not completed

### 4.16 Advanced Clinical Reporting
- **Status:** Partially Complete
- **What's Done:** AI-generated summaries, PDF/FHIR export
- **Remaining:**
  - Anonymized data export for research
  - Benchmarking and trend analysis

---

## PHASE 5: UX, ACCESSIBILITY & PRIVACY

### 5.1 Reorganize Navigation Tabs
- **Status:** Not Started
- **Rationale:** Improve mobile usability
- **Implementation:** Group tabs into logical categories

### 5.2 Add ARIA Labels for Accessibility 🔴 HIGH PRIORITY
- **Status:** Not Started
- **Rationale:** WCAG compliance, screen reader support
- **Implementation:** ARIA labels, roles, states on all elements

### 5.3 Keyboard Navigation
- **Status:** Not Started
- **Rationale:** Accessibility for non-mouse users
- **Implementation:** Tab/arrow navigation, focus indicators

### 5.4 Dark Mode
- **Status:** Not Started
- **Rationale:** User preference, reduced eye strain
- **Implementation:** CSS prefers-color-scheme + manual toggle

### 5.5 Offline Support (PWA)
- **Status:** Not Started
- **Rationale:** Access to support tools without internet
- **Implementation:** Service worker, offline queue, data sync

### 5.6 Trauma-Informed Design Review
- **Status:** Not Started
- **Implementation:** Content warnings, opt-out for sensitive features

### 5.7 Gender & Identity Inclusivity
- **Status:** Not Started
- **Implementation:** Expanded gender/pronoun options in profile

### 5.8 Accessibility Testing & Certification
- **Status:** Not Started
- **Implementation:** WCAG 2.2 AA testing and certification

### 5.9 Privacy UX & Data Transparency
- **Status:** Partially Complete
- **What's Done:** GDPR export, training data consent
- **Remaining:** Visual data use explanations, privacy settings UI

### 5.10 Safety Net Features (Panic Button, Quick Exit)
- **Status:** Not Started
- **Implementation:** Visible panic button, quick exit to hide app

### 5.11 Plain Language & Health Literacy
- **Status:** Not Started
- **Implementation:** Review all content for plain language

### 5.12 Digital Therapeutics & Guided Interventions
- **Status:** Partially Complete
- **What's Done:** Breathing exercises, CBT thought records
- **Remaining:** Guided mindfulness, personalized recommendations

### 5.13 User-Controlled Data Portability & Deletion
- **Status:** Complete ✅
- **What's Done:** CSV/PDF/JSON/FHIR export, training data deletion

---

## PHASE 6: NOTIFICATIONS & ENGAGEMENT

### 6.1 Push Notifications 🔴 HIGH PRIORITY
- **Status:** Not Started
- **Rationale:** Critical for engagement and medication reminders
- **Implementation:** Firebase Cloud Messaging integration
- **Note:** In-app notifications already implemented

### 6.2 Gamification Expansion
- **Status:** Partially Complete
- **What's Done:** Pet system, coins, XP, shop, adventures
- **Remaining:**
  - Achievement badges
  - Progress levels/ranks
  - Weekly challenges
  - Optional leaderboards (anonymous)

### 6.3 Personalized Insights
- **Status:** Complete ✅
- **What's Done:** AI-generated insights, trend analysis

### 6.4 Patient Engagement Analytics
- **Status:** Partially Complete
- **What's Done:** Activity statistics, dashboard metrics
- **Remaining:** Drop-off analysis, engagement dashboards for admins

### 6.5 Just-in-Time Interventions
- **Status:** Not Started
- **Implementation:** Detect disengagement patterns, trigger support

### 6.6 Personalisation & Adaptive Content
- **Status:** Not Started
- **Implementation:** Adapt content/reminders based on preferences

### 6.7 Multi-Channel Communication
- **Status:** Not Started
- **Implementation:** SMS and email integration alongside in-app

---

## PHASE 7: CLINICIAN TOOLS

### 7.1 Caseload Dashboard
- **Status:** Complete ✅
- **What's Done:** Patient list, risk flags, alerts, last contact

### 7.2 Session Documentation
- **Status:** Not Started
- **Implementation:** SOAP note templates, ICD-10 codes

### 7.3 Patient Progress Reports
- **Status:** Complete ✅
- **What's Done:** PDF/JSON export with consent tracking

### 7.4 Supervision Tools
- **Status:** Not Started
- **Implementation:** Flag cases for supervisor, feedback system

### 7.5 Clinician Wellbeing Monitoring
- **Status:** Not Started
- **Implementation:** Optional wellbeing check-ins, workload flags

### 7.6 Clinical Supervision & Peer Support
- **Status:** Not Started
- **Implementation:** Supervision session tracking, peer groups

### 7.7 Clinical Workflow Automation
- **Status:** Partially Complete
- **What's Done:** Appointment reminders, notification system
- **Remaining:** Workflow templates, checklists

---

## PHASE 8: COMPLIANCE & DATA GOVERNANCE

### 8.1 Comprehensive Audit Logging
- **Status:** Complete ✅
- **What's Done:** Event logging with username, actor, action, timestamp

### 8.2 Data Retention Policies
- **Status:** Not Started
- **Implementation:** Configurable retention, auto-archive/delete

### 8.3 Consent Management
- **Status:** Partially Complete
- **What's Done:** AI training consent with withdrawal
- **Remaining:** Consent tracking for all data use types

### 8.4 GDPR Data Export
- **Status:** Complete ✅
- **What's Done:** CSV, PDF, JSON, FHIR export

### 8.5 Data Subject Rights Automation
- **Status:** Partially Complete
- **What's Done:** Export and deletion available
- **Remaining:** Automated workflow for rectification requests

### 8.6 Third-Party Risk Management
- **Status:** Not Started
- **Implementation:** Vendor inventory, risk assessments, DPAs

### 8.7 Algorithmic Fairness & Bias Auditing
- **Status:** Not Started
- **Implementation:** Regular AI bias audits

### 8.8 Data Breach Response
- **Status:** Not Started
- **Implementation:** Breach response plan, automated detection

---

## PHASE 9: INFRASTRUCTURE & SCALABILITY

### 9.1 Database Backups 🔴 HIGH PRIORITY
- **Status:** Not Started
- **Implementation:** Daily encrypted backups, off-site storage

### 9.2 Error Monitoring
- **Status:** Not Started
- **Implementation:** Sentry integration

### 9.3 Performance Monitoring
- **Status:** Not Started
- **Implementation:** API/DB response tracking

### 9.4 Staging Environment
- **Status:** Not Started
- **Implementation:** Railway staging app, config parity

### 9.5 Disaster Recovery
- **Status:** Not Started
- **Implementation:** DRP/BCP documentation and testing

### 9.6 Green Hosting
- **Status:** Not Started
- **Implementation:** Carbon footprint assessment

### 9.7 Interoperability & Open Standards
- **Status:** Partially Complete
- **What's Done:** FHIR export with HMAC signing
- **Remaining:** Additional NHS system integrations

---

## PHASE 10: CONTINUOUS IMPROVEMENT

### 10.1 Continuous Quality Improvement
- **Status:** Ongoing
- **Implementation:** Quarterly review cycles

### 10.2 Regulatory & Standards Tracking
- **Status:** Ongoing
- **Implementation:** Monitor GDPR, NHS, CQC changes

---

## NEW FEATURES TO CONSIDER (Added January 2026)

Based on codebase analysis and modern mental health app best practices:

### Technical Improvements 🔧

#### Automated Testing Suite 🔴 CRITICAL
- **Rationale:** No tests currently exist - critical for production stability
- **Implementation:**
  - Unit tests for API endpoints (pytest)
  - Integration tests for database operations
  - Frontend tests (Jest/Cypress)
  - CI/CD pipeline with test gates
- **Priority:** HIGH - Should be done before major new features

#### WebSocket Real-time Updates
- **Rationale:** Currently using polling for chat, inefficient
- **Implementation:**
  - Flask-SocketIO integration
  - Real-time chat message delivery
  - Live notification updates
  - Pet stat updates without refresh

#### API Documentation (OpenAPI/Swagger)
- **Rationale:** 65+ endpoints undocumented
- **Implementation:**
  - Flask-RESTX or Flasgger integration
  - Auto-generated API docs
  - Interactive API testing UI

#### Database Migration to PostgreSQL
- **Rationale:** SQLite fine for now, but PostgreSQL scales better
- **Implementation:**
  - SQLAlchemy ORM migration
  - PostgreSQL on Railway
  - Connection pooling

### Security Enhancements 🔒

#### App-Based 2FA (TOTP)
- **Rationale:** PIN-based 2FA is good, TOTP is industry standard
- **Implementation:**
  - Google Authenticator/Authy support
  - QR code setup flow
  - Backup codes

#### Biometric Authentication
- **Rationale:** Better mobile UX
- **Implementation:**
  - Capacitor biometric plugin
  - Fingerprint/FaceID support
  - Fallback to PIN

#### End-to-End Encryption for Messages
- **Rationale:** Enhanced privacy for patient-clinician communication
- **Implementation:**
  - Signal Protocol or similar
  - Key exchange mechanism
  - Encrypted message storage

### Patient Features 👤

#### Voice Journaling
- **Rationale:** Voice input exists for chat, extend to journaling
- **Implementation:**
  - Audio recording for mood/gratitude entries
  - Speech-to-text transcription
  - Audio playback in history

#### Mood Prediction ML
- **Rationale:** Predictive support based on historical patterns
- **Implementation:**
  - ML model trained on user mood history
  - Pattern recognition (sleep, activity correlations)
  - Proactive support suggestions

#### Wearable Integration
- **Rationale:** Passive data collection reduces user burden
- **Implementation:**
  - Apple Health / Google Fit integration
  - Fitbit, Garmin APIs
  - Automatic sleep/activity import

#### Peer Support Matching
- **Rationale:** Connect patients with similar experiences
- **Implementation:**
  - Anonymous matching algorithm
  - Moderated peer chat
  - Shared experience groups

#### Family/Support Person Portal
- **Rationale:** Involve support network in care
- **Implementation:**
  - Limited access accounts for family
  - Patient-controlled data sharing
  - Crisis notification to family

### Clinician Features 👨‍⚕️

#### Video/Telehealth Integration
- **Rationale:** Remote therapy sessions
- **Implementation:**
  - Twilio/Daily.co integration
  - In-app video calls
  - Session recording (with consent)

#### AI Symptom Checker
- **Rationale:** Pre-session symptom assessment
- **Implementation:**
  - AI-powered symptom questionnaire
  - Triage recommendations
  - Integration with appointment booking

#### Group Therapy Support
- **Rationale:** Scalable therapy delivery
- **Implementation:**
  - Group session scheduling
  - Shared chat rooms
  - Attendance tracking

---

## PRIORITY MATRIX

### Immediate (Before Public Launch)
1. **Automated Testing Suite** - No tests is a critical gap
2. **Database Backups** - Data loss prevention
3. **Push Notifications** - User engagement
4. **ARIA Labels/Accessibility** - Legal compliance

### Short-term (Q1 2026)
1. Formal Suicide Risk Assessment (C-SSRS)
2. Dark Mode
3. Error Monitoring (Sentry)
4. Staging Environment

### Medium-term (Q2 2026)
1. WebSocket real-time updates
2. Gamification expansion (badges, challenges)
3. Video/Telehealth integration
4. Multi-language support

### Long-term (Q3-Q4 2026)
1. Wearable integration
2. ML mood prediction
3. PostgreSQL migration
4. Peer support matching

---

## IMPLEMENTATION PHASES & SEQUENCING

1. **Security** - Complete ✅
2. **Data Protection** - Complete ✅
3. **Patient Engagement** - Complete ✅
4. **Clinical Features** - In Progress (40%)
5. **UX, Accessibility, Privacy** - In Progress (20%)
6. **Notifications & Engagement** - In Progress (30%)
7. **Clinician Tools** - In Progress (50%)
8. **Compliance & Audit** - In Progress (40%)
9. **Infrastructure & Resilience** - In Progress (15%)
10. **Continuous Improvement** - Ongoing

---

## COST ESTIMATES (If Outsourcing)

| Phase | Hours | Estimated Cost (UK) | Status |
|-------|-------|---------------------|--------|
| Security | 25 | £2,500 - £3,750 | Complete ✅ |
| Data Protection | 16 | £1,600 - £2,400 | Complete ✅ |
| Core Engagement | 38 | £3,800 - £5,700 | Complete ✅ |
| Clinical | 34 | £3,400 - £5,100 | 40% Done |
| UX/Accessibility | 34 | £3,400 - £5,100 | 20% Done |
| Notifications | 20 | £2,000 - £3,000 | 30% Done |
| Clinician Tools | 32 | £3,200 - £4,800 | 50% Done |
| Compliance | 24 | £2,400 - £3,600 | 40% Done |
| Infrastructure | 30 | £3,000 - £4,500 | 15% Done |
| New Features | 60 | £6,000 - £9,000 | Not Started |
| **TOTAL** | **313** | **£31,300 - £46,950** |  |

*Based on £100-150/hour for experienced developer*

---

## NOTES & GUIDANCE

1. **Automated testing is critical** - Implement before adding major new features
2. **Accessibility is a legal requirement** - WCAG 2.2 AA compliance needed
3. **Clinical features require validation** - Consult licensed clinicians
4. **Push notifications drive retention** - High priority for engagement
5. **Backups are non-negotiable** - Implement before handling more patient data
6. **Test with real users** - Gather feedback at every phase

---

*Document created: January 2026*
*Last major update: January 2026 (Post-Security Audit)*
*Next review: After Phase 4 completion*
