# CHANGELOG – Healing Space UK

**Format:** Date – Version | Summary | Area | Status

---

## Latest Changes (February 2026)

### 2026-02-07 – v2.1.2
- Fixed 8 critical UI bugs (duplicate IDs, modal visibility) (UI / Bug Fix)
- Standardized modal toggle functions to use style.display (UI / JavaScript)
- Created comprehensive documentation audit and consolidation (Documentation)
- **Status:** ✅ Deployed to production

### 2026-02-05 – v2.1.1
- Fixed 4 critical database schema issues (Pet table, daily_tasks, inbox query) (Database / Bug Fix)
- Ensured pet table exists on startup (Database / Migration)
- Auto-created missing daily_tasks table (Database / Migration)
- Fixed SQL syntax in get_inbox() endpoint (Backend / Bug Fix)
- **Status:** ✅ Deployed to production

### 2026-02-04 – v2.1
- Completed Phase 2: Input Validation & CSRF Protection (Security)
- Implemented CSRFProtection class with token validation (Security)
- Added InputValidator for all user input (Security)
- Enhanced security headers (CSP, HSTS, Permissions-Policy) (Security)
- CVSS improvement: 4.1 → 1.6 (81% reduction from v2.0) (Security)
- 12/12 security tests passing (Testing)
- **Status:** ✅ Deployed to production

### 2026-02-03 – v2.0.9
- Fixed 2 critical bugs: AI animation and shared pet database (Bug Fix)
- AI "thinking" animation now displays correctly with HTML support (AI / UI)
- Pet database now per-user (added username column) (Database / Bug Fix)
- **Status:** ✅ Deployed to production

---

## Phase 3 Implementation (Early February 2026)

### 2026-02-02 – v2.0.8
- Completed Phase 3: Internal Messaging System (Feature)
- Implemented 5 messaging endpoints (POST send, GET inbox, read, delete, search) (Backend / API)
- Added permission model (Dev ↔ Clinician, Dev ↔ Patient, Clinician ↔ Patient blocked) (Security)
- Created messaging database schema with read/unread tracking (Database)
- Added frontend UI for messaging (Inbox, conversations, read status) (UI)
- 17/17 messaging tests passing (Testing)
- **Status:** ✅ Deployed to production

### 2026-02-01 – v2.0.7
- Railway deployment optimizations (Deployment)
- Fixed session persistence across restarts (Backend / Sessions)
- Added auto-backup scheduling (Database / Operations)
- **Status:** ✅ Deployed to production

---

## Phase 2 Security Hardening (Late January 2026)

### 2026-01-29 – v2.0.6
- Phase 6 security audit completion (Security / Audit)
- Fixed 16 identified security issues (Security)
- Added comprehensive error handling (Backend / Error Handling)
- Suppressed production console output (Backend / Operations)
- CVSS: 2.1 (Medium risk, production acceptable) (Security / Metrics)
- **Status:** ✅ Deployed to production

### 2026-01-28 – v2.0.5
- Added TherapistAI get_insight method (AI / Backend)
- Refactored insights endpoint with custom date ranges (Backend / API)
- AI generates narrative summaries (AI / Features)
- Fixed indentation error in TherapistAI class (Backend / Bug Fix)
- **Status:** ✅ Deployed to production

### 2026-01-27 – v2.0.4
- Improved appointment calendar system (Feature)
- Added month/week/day views (UI / UX)
- Fixed appointment query performance (Backend / Performance)
- **Status:** ✅ Deployed to production

### 2026-01-26 – v2.0.3
- Fixed pet endpoints for Railway deployment (Backend / Database)
- Pet table now uses PostgreSQL (Database / Migration)
- Removed duplicate pet routes (Backend / Refactoring)
- **Status:** ✅ Deployed to production

### 2026-01-25 – v2.0.2
- Completed Phase 1: Authentication & Authorization (Security)
- Implemented session-based authentication (HttpOnly cookies) (Security / Auth)
- Added foreign key validation (clinician-patient) (Security / Authorization)
- Rate limiting on all endpoints (5/min login, 10/min 2FA) (Security)
- Protected debug endpoints with role checks (Security)
- CVSS: 4.1 (Low risk) (Security / Metrics)
- 12/12 security tests passing (Testing)
- **Status:** ✅ Deployed to production

### 2026-01-24 – v2.0.1
- Documentation and roadmap updates (Documentation)
- Added comprehensive feature status document (Documentation)
- Updated security audit report (Documentation / Audit)
- **Status:** ✅ Deployed to production

### 2026-01-23 – v2.0
- PostgreSQL migration complete (Database / Migration)
- SQLite removed from production (Database / Migration)
- All 43 database tables auto-created (Database / Schema)
- GDPR compliance verified (Security / Compliance)
- Fernet encryption for sensitive data (Security / Encryption)
- **Status:** ✅ Deployed to production, production-ready

---

## Early January 2026 Development

### 2026-01-22 – v1.9
- Added role-specific disclaimers (Legal / UX)
- UK legal protection statements (Legal)
- Improved signup flow clarity (UX)
- **Status:** ✅ Deployed

### 2026-01-20 – v1.8
- Clinician dashboard reorganization (UI / Feature)
- Added organized subtabs (UI)
- Improved clinician patient search (Feature)
- Analytics dashboard for clinicians (Feature / UI)
- **Status:** ✅ Deployed

### 2026-01-19 – v1.7
- Fixed patient analytics mood query (Backend / Bug Fix)
- Corrected column references (entrestamp vs timestamp) (Database / Bug Fix)
- **Status:** ✅ Deployed

### 2026-01-18 – v1.6
- Removed analytics tab (UI / UX)
- Redesigned appointments calendar (UI / Feature)
- Added month/week/day calendar views (UI)
- **Status:** ✅ Deployed

### 2026-01-17 – v1.5
- Added password show/hide toggle (UI / UX)
- Completed appointment calendar system (Feature)
- Added sleep chart feature (Feature / Charts)
- Improved insights with custom date ranges (Backend / API)
- Fixed insights column name mismatch (Backend / Bug Fix)
- **Status:** ✅ Deployed

### 2026-01-16 – v1.4
- Added pet rewards system (Gamification)
- Pet rewards for self-care activities (Gamification)
- Session persistence and "Remember Me" (Feature / Auth)
- Fixed JavaScript syntax errors (Frontend / Bug Fix)
- **Status:** ✅ Deployed

### 2026-01-15 – v1.3
- AI memory integration (AI / Feature)
- Chat initialization system (AI / Feature)
- Added model training script (AI / Training)
- Improved login flow (UX / Auth)
- **Status:** ✅ Deployed

### 2026-01-14 – v1.2
- Implemented clinician system (Feature / Major)
- Clinician registration and dashboard (Feature)
- Patient-clinician linking (Feature / Security)
- Role-based access control (RBAC) (Security)
- Added all original app features (Completeness)
  - Community board
  - Safety plan
  - Progress insights with charts
  - CSV/PDF export
  - Sleep hygiene guides
  - Professional dashboard
- **Status:** ✅ Deployed, feature parity achieved

### 2026-01-13 – v1.1
- Added password special character requirements (Security)
- Enhanced registration validation (Security / UX)
- Fixed missing database columns (Database / Bug Fix)
- **Status:** ✅ Deployed

### 2026-01-12 – v1.0
- Initial web application launch (Release)
- Flask REST API (Backend / Architecture)
- PostgreSQL database (Database / Infrastructure)
- Responsive design (UI / UX)
- GDPR compliance (Security / Legal)
- AI therapy with Groq LLM (AI / Feature)
- Mood/sleep tracking (Feature)
- CBT tools (Feature)
- Crisis detection (Feature / Safety)
- Appointment management (Feature)
- FHIR export (Feature / Integration)
- Audit logging (Compliance / Logging)
- Encryption with Fernet (Security / Encryption)
- **Status:** ✅ Deployed, production-ready

---

## Format Key

**Area Tags:**
- `Backend / API` – REST API endpoint changes
- `Backend / Database` – Database operations, queries
- `Backend / Error Handling` – Error handling improvements
- `Security` – Security fixes and enhancements
- `UI / UX` – User interface and experience
- `Database / Migration` – Schema migrations
- `Database / Schema` – Schema changes
- `Feature` – New feature implementation
- `Bug Fix` – Bug fixes
- `Testing` – Test coverage and test improvements
- `Documentation` – Documentation updates
- `Deployment` – Deployment and infrastructure
- `Legal` – Legal and compliance
- `Gamification` – Gamification features
- `AI` – AI/LLM features
- `Compliance` – Compliance and regulation
- `Encryption` – Encryption and cryptography
- `Audit` – Audit reports and assessments

---

## Version Numbering

**Format:** Major.Minor.Patch

- **Major (2.x):** Significant platform changes (PostgreSQL migration = v2.0)
- **Minor (x.1):** Feature or phase completion
- **Patch (x.x.1):** Bug fixes and improvements

---

**Last Updated:** February 7, 2026  
**Total Versions:** 30+  
**Current Status:** Production Ready (v2.1.2)
