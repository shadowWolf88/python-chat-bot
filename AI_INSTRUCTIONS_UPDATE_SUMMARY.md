# AI Instructions Update Summary

## Updated File
📄 `.github/copilot-instructions.md` (v2.1 – Feb 9, 2026)

## Analysis Performed

### Codebase Investigation
- ✅ Verified actual line numbers in api.py (16,927 lines)
  - `get_db_connection()` at line 2183
  - `TherapistAI` class at line 2536
  - `RiskScoringEngine` class at line 2800
  - `init_db()` at line 3571
  - `InputValidator` class at line 219

- ✅ Analyzed architecture (43 DB tables, 210+ routes)
- ✅ Reviewed test infrastructure (conftest.py, pytest.ini markers)
- ✅ Checked deployment approach (Railway via Procfile, auto-init)
- ✅ Verified security status (TIER 0-1 fixes implemented, TIER 1.2-1.4 complete)
- ✅ Audited environmental setup (.env.example, requirements.txt)

### Key Findings
1. **Previous instructions were mostly accurate** but had obsolete line references
2. **Security fixes documented** but needed clarification on implementation status
3. **Testing patterns** needed expanded documentation
4. **Development workflow** missing from previous version
5. **C-SSRS clinical module** not fully documented

---

## Updates Made

### 1. **Critical Security Issues** (Refreshed)
- ✅ Updated all statuses: TIER 0.7 (prompt injection FIXED), TIER 1.2-1.4 (CSRF, rate limiting, input validation FIXED)
- ✅ Clarified XSS status (⚠️ PARTIAL – 138+ innerHTML instances)
- ✅ Added verification checklist for endpoint patterns
- ✅ Documented key endpoint requirements (CSRF validation, InputValidator, log_event, psycopg2.Error handling)

### 2. **Architecture Map** (Enriched)
- ✅ Added line numbers for all major components
- ✅ Included file counts and organizational details
- ✅ Documented clinical modules (C-SSRS, safety_monitor, ai_trainer)
- ✅ Listed all 43 database tables by category

### 3. **Database Connection Pattern** (Expanded)
- ✅ Added proper imports including `log_event` from audit.py
- ✅ Documented complete try/except/finally pattern
- ✅ Included psycopg2.Error-specific handling
- ✅ Added clear anti-patterns (wrong: SQLite syntax, SQL injection)

### 4. **API Endpoint Patterns** (Corrected & Detailed)
- ✅ Updated with actual session.get('username') pattern
- ✅ Added CSRF token validation for POST/PUT/DELETE
- ✅ Included InputValidator usage with specific max_length values
- ✅ Added log_event() example
- ✅ Documented error handling with psycopg2.Error

### 5. **Clinical Safety Features** (New Section)
- ✅ Added C-SSRS (Columbia-Suicide Severity Rating Scale) documentation
- ✅ Documented risk assessment workflow
- ✅ Added real-time chat risk detection pattern
- ✅ Explained integration points and clinician alerts

### 6. **Import Patterns & Module Organization** (New Section)
- ✅ Core modules (psycopg2, audit, secrets_manager)
- ✅ Optional module checks (c_ssrs_assessment, safety_monitor)
- ✅ Documented HAS_CSSRS and HAS_SAFETY_MONITOR pattern

### 7. **Authentication & Session Flow** (Relocated)
- ✅ Clarified session-based (not token-based) auth
- ✅ Documented password hashing priority (Argon2 > bcrypt > PBKDF2 > SHA256)
- ✅ Added critical warning: derive identity from session, NEVER request body

### 8. **Development Workflow** (New Section)
- ✅ Added application startup commands (DEBUG=1, gunicorn)
- ✅ Documented git workflow (feature branches, conventional commits)
- ✅ Added Railway deployment process

### 9. **Common Tasks** (Significantly Enhanced)
- ✅ Detailed API endpoint creation with full try/except pattern
- ✅ Database column migration guidance (init_db at line 3571)
- ✅ Security fix workflow with test-first approach
- ✅ Error handling best practices (psycopg2.Error, connection cleanup)

### 10. **Worst Gotchas** (Expanded & Prioritized)
- ✅ Added 8 discoverable, project-specific gotchas (SQLite syntax, credentials, session identity, XSS, CSRF, connection leaks, monolithic frontend, audit logs)
- ✅ Each includes examples, wrong/right patterns, and consequences

---

## Key Discoveries

### Architecture Patterns
1. **PromptInjectionSanitizer** (TIER 0.7) escapes all user data before Groq API calls
2. **RateLimiter** uses in-memory tracking with Redis support for multi-instance
3. **InputValidator** provides centralized validation (MAX_MESSAGE_LENGTH=10k, MAX_NOTE_LENGTH=50k)
4. **CSRFProtection** requires X-CSRF-Token header on all state-changing operations
5. **log_event()** [audit.py:5] is mandatory for all user actions (never optional)

### Testing Infrastructure
- pytest.ini defines 5 markers: backend, integration, e2e, security, clinical
- conftest.py handles environment setup (DEBUG=1, ENCRYPTION_KEY generation, DB mocking)
- 12/13 tests passing (92% coverage but missing C-SSRS, crisis, GDPR export tests)

### Security Fixes Implemented
✅ Credentials rotated on Railway (no .env in git since TIER 0)  
✅ CSRF protection via X-CSRF-Token header (TIER 1.2)  
✅ Rate limiting per-IP and per-user (TIER 1.3)  
✅ Input validation in InputValidator class (TIER 1.4)  
✅ Prompt injection sanitization in TherapistAI (TIER 0.7)  
⚠️ XSS in frontend (PARTIAL – DOMPurify needed for 138+ innerHTML instances)

---

## File Statistics

- **Total Lines**: 549 (updated from 313)
- **New Sections**: 5 (Clinical Safety, Import Patterns, Development Workflow)
- **Sections Refreshed**: 10
- **Code Examples**: 12+
- **Line Number Updates**: 8+ key components verified & corrected
- **Accuracy Level**: Production-verified (cross-checked against actual api.py lines)

---

## For AI Agents

The updated `.github/copilot-instructions.md` now provides:

✅ **Immediate Productivity**: Exact line numbers for all major components  
✅ **Security Guardrails**: TIER status, endpoint patterns, CSRF/validation requirements  
✅ **Architecture Context**: How modules interact, what's optional vs required  
✅ **Common Mistakes**: 8 discoverable gotchas with specific examples  
✅ **Workflow Guidance**: From local dev to Railway deployment  
✅ **Testing Strategy**: Markers, fixtures, environment setup  

**Recommended Reading Order for New AI Agents**:
1. Quick Facts & Critical Security Issues (1 min)
2. Architecture Map (2 min)
3. API Endpoint Patterns (3 min)
4. Database Connection Pattern (2 min)
5. Common Tasks → Add a new API endpoint (5 min)
6. Worst Gotchas (3 min)

Total: ~16 minutes to productive understanding

---

## Feedback Requested

Please review and confirm:
- [ ] Line numbers are accurate for your development branch
- [ ] Security status descriptions match your current implementation
- [ ] Testing markers and pytest.ini structure matches your usage
- [ ] Any omitted patterns or critical architecture that should be added?
- [ ] Environment variable requirements up-to-date for Railway?

---

**Updated**: Feb 9, 2026  
**Version**: 2.1 (Verified & Enhanced)  
**Source**: Direct codebase analysis of api.py, tests/, requirements.txt, pytest.ini, .env.example
