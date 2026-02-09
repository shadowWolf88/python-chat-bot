# Healing Space – AI Agent Guide

## Quick Facts
- **Type**: Mental health therapy web app (Flask REST API + PostgreSQL)
- **Size**: 16,000+ line `api.py`, 16,000+ line frontend, 43 DB tables
- **Status**: Production-ready backend with critical security gaps (see TIER 0)
- **Deployment**: Railway via `Procfile`, auto-DB-init on startup
- **Test Coverage**: 92% (12/13 passing) but missing clinical features

---

## Critical Security Issues (TIER 0 – DO THESE FIRST)
These are active vulnerabilities blocking real users:

1. **Prompt injection in TherapistAI** [line 2536-2650]: User fields now sanitized via PromptInjectionSanitizer
   - Status: ✅ FIXED in TIER 0.7 - all wellness_data, medical context, stressors escaped before Groq API call
   - Verify: Check PromptInjectionSanitizer class methods in api.py for context escaping

2. **CSRF protection** [line ~450-490]: Double-submit pattern + token validation on all POST/PUT/DELETE
   - Status: ✅ FIXED in TIER 1.2 - X-CSRF-Token header required; exempt routes in CSRF_EXEMPT_ENDPOINTS
   - Verify: Every endpoint validates csrf_token before processing

3. **Rate limiting** [line ~2100]: Per-IP (login: 5/min) and per-user (register: 3/5min) throttling
   - Status: ✅ FIXED in TIER 1.3 - RateLimiter in-memory with Redis support for multi-instance
   - Verify: Check RateLimiter.check_limit() calls on auth routes

4. **Input validation** [line 219-300]: Centralized InputValidator for all text/number/email fields
   - Status: ✅ FIXED in TIER 1.4 - MAX_MESSAGE_LENGTH=10000, MAX_NOTE_LENGTH=50000, sanitized
   - Verify: All endpoints call InputValidator before DB operations

5. **XSS in frontend** [138+ instances in templates/index.html]: innerHTML replaced with textContent
   - Status: ⚠️ PARTIAL - client-side still has innerHTML uses; DOMPurify needed for rich content
   - Fix: Use `document.createTextNode()` or sanitize with DOMPurify for user-generated content

6. **Credentials in git**: All .env secrets rotated on Railway; git history scrubbed
   - Status: ✅ FIXED - .env in .gitignore; .env.example provides template
   - Action: Never commit .env, .env.local, or secrets files

**Key Endpoint Patterns to Verify When Adding Code**:
- All POST/PUT/DELETE must call `validate_csrf_token(request.headers.get('X-CSRF-Token'))`
- All create/update operations must validate input: `InputValidator.validate_text(...)`
- All database writes must use `%s` placeholders: `cur.execute(..., (params,))`
- All user actions must log: `log_event(username, 'category', 'action', 'details')` [audit.py:5]

---

## Architecture Map
```
api.py (16,927 lines, core application)
├─ Flask app + 210+ routes (imports CSRF, rate limiting, session auth)
├─ TherapistAI [line 2536] (Groq LLM integration with sanitized prompt injection)
├─ RiskScoringEngine [line 2800] (clinical + behavioral + conversational scoring)
├─ SafetyMonitor (real-time chat risk detection via analyze_chat_message import)
├─ PromptInjectionSanitizer (TIER 0.7: sanitizes user data before LLM)
├─ InputValidator [line 219] (centralized input validation)
├─ CSRFProtection [line ~450] (double-submit pattern + token validation)
├─ RateLimiter [line ~2100] (per-IP and per-user request throttling)
└─ PostgreSQL helpers (get_db_connection [line 2183], get_wrapped_cursor, init_db [line 3571])

Frontend
├─ templates/index.html (16k lines, monolithic SPA with modular JS)
├─ static/js/main.js (activity logging, DOM manipulation, API calls)
├─ static/css/style.css (responsive design)
└─ Mobile: android/, ios/ (Capacitor cross-platform wrapper)

Clinical Modules
├─ c_ssrs_assessment.py (Columbia-Suicide Severity Rating Scale assessments)
├─ safety_monitor.py (keyword detection for crisis triggers)
└─ ai_trainer.py (ML model training for risk scoring)

Database Support
├─ secrets_manager.py (Vault/env var fallback for credentials)
├─ audit.py [line 5: log_event()] (immutable audit log table)
├─ training_data_manager.py (GDPR consent + anonymization)
├─ fhir_export.py (HL7 FHIR export with HMAC validation)

Database Schema
├─ 43 tables auto-created in init_db() [line 3571]
├─ therapy: chat_history, insights, therapy_notes, audit_log
├─ clinical: risk_assessments, risk_alerts, clinical_scales, c_ssrs_responses
├─ cbt: goals, values_clarification, coping_cards, core_beliefs, sleep_diary, exposures
├─ user: users, sessions, clinician_patients, training_data_consent
└─ wellness: mood_logs, sleep_logs, activity_logs, pet_game
```

---

## Database Connection Pattern
**CRITICAL**: Always use PostgreSQL, never SQLite in production. Import log_event from audit.py [line 5].

```python
# Pattern used throughout api.py (line 2183)
from audit import log_event  # REQUIRED for all DB operations

conn = get_db_connection()  # Supports both DATABASE_URL (Railway) and individual env vars
cur = get_wrapped_cursor(conn)  # Returns psycopg2 cursor with method chaining

try:
    # Always use %s placeholders for parameter binding (PostgreSQL syntax)
    cur.execute('SELECT * FROM users WHERE username=%s', (username,))
    result = cur.fetchone()
    
    # For INSERT/UPDATE/DELETE, commit transaction
    cur.execute('INSERT INTO mood_logs (username, mood, date) VALUES (%s, %s, %s)', 
                (username, mood, date.today()))
    conn.commit()
    
    # ALWAYS log user actions for audit trail
    log_event(username, 'wellness', 'mood_logged', f'mood={mood}')
    
except psycopg2.Error as e:
    conn.rollback()
    # Handle database error safely without leaking connection details
    return jsonify({'error': 'Database operation failed'}), 500
finally:
    conn.close()

# WRONG (will fail in production):
cur.execute('SELECT * FROM users WHERE username=?', (username,))  # SQLite syntax
cur.execute(f'SELECT * FROM users WHERE username={username}')      # SQL injection vulnerability
```

**Connection helpers**:
- `get_db_connection(timeout=30.0)` [line 2183]: Creates PostgreSQL connection with timeout
- `get_wrapped_cursor(conn)`: Returns cursor for method chaining
- Always close connection in `finally` block to prevent connection leaks

---

## API Endpoint Patterns
All endpoints follow this structure (examples start around line 500):

```python
@app.route('/api/<resource>/<action>', methods=['GET|POST|PUT|DELETE'])
def handler():
    # 1. Get authenticated user from session
    username = session.get('username')
    if not username:
        return jsonify({'error': 'Authentication required'}), 401
    
    # 2. Get request data and validate input
    data = request.json or {}
    text, error = InputValidator.validate_text(data.get('text'), max_length=10000)
    if error:
        return jsonify({'error': error}), 400
    
    # 3. Validate CSRF token on state-changing operations
    if request.method in ['POST', 'PUT', 'DELETE']:
        token = request.headers.get('X-CSRF-Token')
        if not token or not validate_csrf_token(token):
            return jsonify({'error': 'CSRF token invalid'}), 403
    
    # 4. DB operation with try/except
    try:
        conn = get_db_connection()
        cur = get_wrapped_cursor(conn)
        cur.execute('INSERT INTO table (...) VALUES (%s, ...)', (...))
        conn.commit()
        log_event(username, 'category', 'action', 'details')  # ALWAYS log user actions
        return jsonify({'success': True, 'id': new_id}), 201
    except psycopg2.Error as e:
        conn.rollback()
        app.logger.error(f'DB error in handler: {e}')
        return jsonify({'error': 'Operation failed'}), 500
    finally:
        conn.close()
```

**Key conventions**:
- **Validate input**: Use `InputValidator.validate_text()` or `validate_message()` before DB operations
- **Log everything**: Use `log_event(username, category, action, details)` [audit.py:5] for audit trail
- **Return jsonify**: Always return Flask `jsonify()` with status code, never raw dicts
- **Handle CSRF**: POST/PUT/DELETE require `X-CSRF-Token` header (routes in CSRF_EXEMPT_ENDPOINTS are exempt)
- **Auth check first**: Every endpoint must verify session before DB access
- **Database safety**: Never interpolate user input into SQL; always use `%s` with params tuple
- **Connection cleanup**: Always use try/finally to ensure `conn.close()` is called

---

## Clinical Safety Features (C-SSRS & Risk Detection)

### Columbia-Suicide Severity Rating Scale (C-SSRS)
Located in [c_ssrs_assessment.py](c_ssrs_assessment.py):
```python
# C-SSRS assessment lifecycle:
assessment = CSSRSAssessment(username)
assessment.start_interview()  # Guided Q&A for suicide risk assessment

# Core questions (suicidality screening):
# 1. Ideation (frequency, intensity)
# 2. Intensity (how close to acting)
# 3. Behavior (self-injury, attempts, plans)
# 4. Deterrents (reasons to live)

# Response stored in risk_assessments table with:
# - c_ssrs_responses: Detailed answers + timestamps
# - risk_level: 'low'|'moderate'|'high'|'critical'
# - safety_plan: Coping strategies + emergency contacts
```

**Integration pattern**: 
- Triggered on login if >30 days since last assessment OR risk_level changed
- Results feed into RiskScoringEngine for clinician alerts
- Safety plan auto-shared with assigned clinician

### Real-time Chat Risk Detection
When user sends message in `/api/therapy/message`:
```python
if HAS_SAFETY_MONITOR:
    risk_flags = analyze_chat_message(message)  # Returns keyword matches
    if risk_flags['severity'] in ['high', 'critical']:
        # Auto-escalate: create alert for clinician
        RiskScoringEngine.update_conversational_score(username, risk_flags)
```

---

## Import Patterns & Module Organization

### Core modules (always available):
```python
import psycopg2          # Database errors: psycopg2.Error
from audit import log_event  # Audit trail - NEVER forget this!
from secrets_manager import get_secret  # Env var/Vault fallback
```

### Optional modules (check availability):
```python
# c_ssrs_assessment.py (may not be installed)
try:
    from c_ssrs_assessment import CSSRSAssessment
    HAS_CSSRS = True
except ImportError:
    HAS_CSSRS = False  # Disable C-SSRS endpoints

# safety_monitor.py (may not be installed)  
try:
    from safety_monitor import analyze_chat_message
    HAS_SAFETY_MONITOR = True
except ImportError:
    HAS_SAFETY_MONITOR = False  # Disable real-time detection
```

Always check availability before calling (e.g., `if HAS_CSSRS: ...`)

---

## Authentication & Session Flow
Session-based (Flask session), NOT token-based:

```python
# Login flow:
# 1. Verify password: verify_password(stored_hash, user_password)
# 2. Set session: session['username'] = username; session.permanent = True
# 3. Generate CSRF token: CSRFProtection.generate_csrf_token(username)

# In requests:
# 1. Check session: username = session.get('username')
# 2. Validate CSRF: X-CSRF-Token header [line ~450-490]
# 3. Access data: cur.execute(..., (username,))

# Password hashing priority:
# Argon2 > bcrypt > PBKDF2 (fallback) > SHA256 (legacy, auto-migrates on login)
```

**Critical**: Always derive identity from session, NEVER from request body

---

## CBT Tools Endpoints
Full CRUD for therapy exercises (goals, values, coping cards, exposures, etc.):

```python
# Pattern (all similar):
@app.route('/api/cbt/<tool>', methods=['POST|GET|PUT|DELETE'])
# POST: Create with InputValidator
# GET: List with pagination
# PUT: Update only provided fields
# DELETE: Soft delete (recommended) or hard delete

# Examples: /api/cbt/goals, /api/cbt/values, /api/cbt/coping-card
# Each has summarize_*() helper for AI memory context
```
TherapistAI class [line 2536]:

```python
# Init with user context
ai = TherapistAI(username)

# Get response with memory context (see RiskScoringEngine)
response = ai.get_response(
    user_message,
    history=[(role, text), ...],      # Recent chat history
    wellness_data={'mood': 7, ...},   # From mood logs
    memory_context={'personal_context': {...}, 'recent_events': [...]},  # AI memory
    risk_context='critical'            # 'none'|'moderate'|'high'|'critical'
)

# Groq API details:
# - Endpoint: https://api.groq.com/openai/v1/chat/completions
# - Model: llama-3.3-70b-versatile
# - Prompt injection risk: FIXED in TIER 0.7 - User fields sanitized by PromptInjectionSanitizer
# - Memory: Each response recreates context (no persistent vector DB yet)

# TIER 0.7 Sanitization:
# All user data passed to LLM is sanitized via PromptInjectionSanitizer:
# - wellness_data: mood, sleep, energy values only (no free text)
# - memory_context: pre-computed summaries from database
# - chat_history: validated message pairs before injection
```

---

## Risk Assessment System
`RiskScoringEngine.calculate_risk_score()` [line 2800]:

```python
# Composite risk score (0-100):
# - Clinical score (0-40): PHQ-9, GAD-7 assessments + recent alerts
# - Behavioral score (0-30): Mood trends, engagement, CBT tool use
# - Conversational score (0-30): Keyword detection in chat

# Risk levels:
# - 0-25: low (green)
# - 26-50: moderate (yellow)
# - 51-75: high (orange)
# - 76-100: critical (red)

# Usage:
risk = RiskScoringEngine.calculate_risk_score(username)
if risk['risk_level'] == 'critical':
    # Auto-create risk alerts for clinician
    # Run crisis response protocol
```

**Critical keywords** managed in database table `risk_keywords` (add via admin UI, not hardcoded)

---

## CBT Tools Endpoints
Full CRUD for therapy exercises (goals, values, coping cards, exposures, etc.):

```python
# Pattern (all similar):
@app.route('/api/cbt/<tool>', methods=['POST|GET|PUT|DELETE'])
# POST: Create with InputValidator
# GET: List with pagination
# PUT: Update only provided fields
# DELETE: Soft delete (recommended) or hard delete

# Examples: /api/cbt/goals, /api/cbt/values, /api/cbt/coping-card
# Each has summarize_*() helper for AI memory context
```

---

## Environment Variables
**REQUIRED** for production:
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db    # Railway provides this
GROQ_API_KEY=gsk_...                                 # From https://console.groq.com
ENCRYPTION_KEY=<44-char Fernet key>                  # Generate: python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
SECRET_KEY=<32+ random chars>                         # Session encryption
PIN_SALT=<random string>                              # PIN hashing salt
DEBUG=0                                               # Disable in production (enables CORS, skips HTTPS)

# OPTIONAL:
ALERT_WEBHOOK_URL=https://...                        # Crisis alert webhook
ALLOWED_ORIGINS=https://healing-space.org.uk,...     # CORS whitelist
DISABLE_CSRF=0                                        # For testing only
```

---

## Testing
Run tests with: `.venv/bin/python -m pytest -v tests/` (requires PostgreSQL)

**Test structure** (tests/ directory):
- conftest.py: Shared fixtures, Flask test client, mock database
- test_app.py: Auth, session, basic endpoints
- test_postgresql_api.py: DB operations
- test_messaging.py: Clinician messaging
- test_role_access.py: Access control
- integration/, e2e/: Integration and end-to-end tests

**Test markers** (from pytest.ini):
```bash
pytest -m backend        # Backend unit tests
pytest -m integration    # Integration tests
pytest -m e2e            # End-to-end journey tests
pytest -m security       # Security-focused tests
pytest -m clinical       # Clinical safety tests (C-SSRS, risk assessment)
```

**Gotchas**:
- Must set `DEBUG=1` for tests to pass (conftest.py sets this automatically)
- Tests need live PostgreSQL connection (not SQLite)
- No C-SSRS, crisis, GDPR export tests (major coverage gap)
- Use fixtures in conftest.py; clean up test data after each test

---

## Development Workflow

### Running the Application
```bash
# Development (with auto-reload)
DEBUG=1 GROQ_API_KEY=gsk_... python3 api.py

# Production-like (gunicorn)
gunicorn api:app --bind 0.0.0.0:8000

# With database initialization
python3 api.py  # Runs init_db() on startup (auto-creates 43 tables)
```

### Making Code Changes
1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and test: `pytest -v tests/`
3. Verify security: Check for InputValidator calls, CSRF tokens, log_event calls
4. Commit: `git commit -m "feat: description"` (follows conventional commits)
5. Push: `git push origin feature/my-feature`
6. Railway auto-deploys from main branch

### Deployment to Railway
```bash
git push origin main
# Railway automatically:
# 1. Runs migrations (init_db() on startup)
# 2. Sets environment variables from Railway dashboard
# 3. Starts gunicorn server
# Check logs: railway logs
```

---

## Common Tasks

### Add a new API endpoint
1. Get authenticated user: `username = session.get('username')`
2. Validate input: Use `InputValidator.validate_text()`, `validate_message()`, etc.
3. Validate CSRF on state-changing: `if request.method in ['POST', 'PUT', 'DELETE']: validate_csrf_token(...)`
4. DB operation:
   ```python
   try:
       conn = get_db_connection()
       cur = get_wrapped_cursor(conn)
       cur.execute('...', (params,))
       conn.commit()
       log_event(username, 'category', 'action', 'details')
       return jsonify({'success': True}), 201
   except psycopg2.Error as e:
       conn.rollback()
       app.logger.error(f'Error: {e}')
       return jsonify({'error': 'Operation failed'}), 500
   finally:
       conn.close()
   ```

### Add a database column
1. Locate init_db() at line 3571
2. Add migration in try/except block:
   ```python
   try:
       cur.execute('ALTER TABLE table_name ADD COLUMN new_col TYPE;')
       conn.commit()
   except psycopg2.Error as e:
       if 'already exists' not in str(e):
           raise  # Re-raise if it's a different error
   ```
3. **NEVER drop columns** (data destruction risk)
4. Test locally: `rm healing_space.db && python3 api.py` (forces reinit)

### Fix a security issue
1. Identify vulnerability type (XSS, injection, auth bypass, etc.)
2. Check docs/MASTER_ROADMAP.md TIER 0/1 for priority
3. Write test first to reproduce: `tests/test_security_*.py`
4. Implement fix + test + verify existing tests pass
5. Log fix: `log_event('system', 'security', 'fix_applied', 'description')`
6. Update this file with new patterns if pattern-based

### Handle errors safely
- **Always use psycopg2.Error** (not generic Exception) to distinguish DB errors
- **Never expose internal error messages** in responses (log them instead)
- **Always rollback on error**: `conn.rollback()` before returning error response
- **Always close connections**: Use try/finally or context manager

---

## Debugging Tips

1. **Check logs**: `log_event()` writes to audit_log table (line ~200)
2. **Enable DEBUG mode**: `export DEBUG=1` (relaxes CSRF, enables error details, skips HTTPS)
3. **Database queries**: Use psql or Railway's web console to check table data
4. **Session issues**: Check Flask session cookie validity, timeout (30 days default)
5. **AI issues**: Verify GROQ_API_KEY format (gsk_ prefix), check Groq API status
6. **Encryption issues**: Ensure ENCRYPTION_KEY is valid Fernet format (44 chars base64)

---

## Worst Gotchas

1. **SQLite vs PostgreSQL syntax**: Code uses `%s` placeholders (PostgreSQL), NOT `?` (SQLite)
   - Wrong: `cur.execute('SELECT * FROM users WHERE id=?', (1,))`
   - Right: `cur.execute('SELECT * FROM users WHERE id=%s', (1,))`

2. **Credential leakage**: .env was previously committed; all production secrets rotated
   - Never commit .env, .env.local, or generated keys
   - Use .env.example as template only

3. **Session vs request identity**: Derive user identity ONLY from Flask session, never request body
   - Wrong: `username = request.json.get('username')`
   - Right: `username = session.get('username')`

4. **XSS via innerHTML**: 138+ instances in templates/index.html still use innerHTML with user content
   - Use `textContent` for user-generated data (mood names, pet names, plan titles)
   - Only use innerHTML if content is pre-sanitized or trusted (not user input)

5. **Missing CSRF tokens**: POST/PUT/DELETE fail silently without X-CSRF-Token header
   - Frontend must include: `headers: {'X-CSRF-Token': token}`
   - Check CSRF_EXEMPT_ENDPOINTS in api.py for auth routes that skip validation

6. **Connection leaks**: Forgetting `conn.close()` in finally block exhausts connection pool
   - Always structure as:
     ```python
     try: ... except: ... finally: conn.close()
     ```

7. **Monolithic frontend**: 16k-line HTML file with inline JS/CSS is very hard to maintain
   - Consider splitting into modular components when adding features
   - Avoid adding hundreds of lines of inline JS; use static/js/ files instead

8. **Missing audit logs**: Endpoints that forget `log_event()` leave no security trail
   - Every POST/PUT/DELETE on patient data must log to audit_log table
   - Pattern: `log_event(username, 'category', 'action', 'optional_details')`

---

## Key References
- docs/MASTER_ROADMAP.md: Detailed priority-ordered bug/feature list (TIER 0-4)
- README.md: User-facing overview + deployment guides
- secrets_manager.py: Secret retrieval (Vault/env var fallback)
- audit.py: Event logging system
- training_data_manager.py: GDPR consent + anonymization

---

Updated: Feb 9, 2026 | Version: 2.1 (Verified & Enhanced) | For detailed roadmap, see docs/MASTER_ROADMAP.md
