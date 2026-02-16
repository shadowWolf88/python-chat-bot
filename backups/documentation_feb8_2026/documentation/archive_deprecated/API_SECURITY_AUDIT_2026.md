# Healing Space - API Security Audit Report 2026

**Date**: February 4, 2026  
**Scope**: All 193+ API endpoints in api.py  
**Severity Assessment**: CRITICAL issues identified

---

## RECENT BUG FIXES (Feb 4, 2026)

### ✅ Fixed: AI "Thinking" Animation
- **Issue**: Animation displayed escaped HTML code instead of animated dots
- **Status**: FIXED (commit `80bca1a`)
- **Details**: Added `isRawHtml` parameter to `addMessage()` function
- **Testing**: All 4 core tests passing ✅

### ✅ Fixed: Shared Pet Database (Critical)
- **Issue**: All users shared same pet, new accounts inherited previous user's pet
- **Status**: FIXED (commit `80bca1a`)
- **Details**: Added `username` column to pet table, updated all 8 pet endpoints
- **Testing**: Per-user pet isolation working correctly ✅
- **Data**: Auto-migration for existing `pet_game.db` ✅

---

## FEATURE REQUEST - Internal Messaging System

**Requested By**: User (Feb 4, 2026)  
**Priority**: HIGH (After Phase 2 bugs fixed)  
**Time Estimate**: 6-8 hours

```
REQUIREMENTS:
- Developer ↔ Clinician: Full bidirectional messaging
- Developer ↔ User: Full bidirectional messaging (for bug testing)
- Clinician ↔ User: NOT ALLOWED (direct mailing disabled)
- Users can NEVER directly mail clinicians

ENDPOINTS NEEDED:
[ ] POST /api/messages/send - Send message
[ ] GET /api/messages/inbox - Get all messages for current user
[ ] GET /api/messages/conversation/<user1>/<user2> - Get conversation thread
[ ] DELETE /api/messages/<message_id> - Delete message
[ ] PATCH /api/messages/<message_id>/read - Mark as read

DATABASE SCHEMA:
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    sender_username TEXT NOT NULL,
    recipient_username TEXT NOT NULL,
    subject TEXT,
    body TEXT NOT NULL,
    is_read BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP,
    FOREIGN KEY (sender_username) REFERENCES users(username),
    FOREIGN KEY (recipient_username) REFERENCES users(username)
);
```

PERMISSION RULES:
- Dev can message clinician/user
- Clinician can message dev/user
- User can message dev/user (NOT clinician)
- All endpoints enforce sender role check
```

---

## MY ADDITIONS

1. i want you to work on the messages feature (internal messages) i want the user/clinician/dev to all be able to mail eachother (create new mails etc, recieve, send etc etc) the patient should NEVER be able to directly mail their clinician, this is purely between developer/clinician and developer/user for bug testing purposes. 




## Executive Summary

The API has **CRITICAL authentication vulnerabilities**:

1. ❌ **No Flask session validation** - Authentication uses `X-Username` header or query params
2. ❌ **Client-side authentication trust** - Users can claim any username without verification
3. ❌ **No role enforcement** - Endpoints check role but accept any username
4. ✅ **Some protection** - Database queries use parameterized statements (good!)
5. ⚠️ **Inconsistent patterns** - Some endpoints override with session-based auth

**Impact**: Any user can access/modify any other user's data by changing the `X-Username` header.

---

## CRITICAL VULNERABILITIES

### 🔴 **Issue #1: Broken Authentication Function**

**Location**: [api.py:2606](api.py#L2606)  
**Severity**: CRITICAL (10/10)

```python
def get_authenticated_username():
    # Placeholder: Replace with real authentication/session logic
    return request.headers.get('X-Username') or request.args.get('username')
```

**Problem**: 
- Trusts client-provided `X-Username` header entirely
- No validation that user owns the username
- No session verification
- Falls back to query parameter if header missing
- **Anyone can claim to be any user**

**Affected Endpoints**: ~150+ (every endpoint using `get_authenticated_username()`)

**Proof of Concept**:
```bash
# Attacker can read patient data as another user:
curl -H "X-Username: alice@healing-space.uk" https://www.healing-space.org.uk/api/patient/profile
# ^ Returns alice's private health data!

# Or as a clinician:
curl -H "X-Username: dr_smith" https://www.healing-space.org.uk/api/professional/patients
# ^ Returns all patients under dr_smith's account!
```

**Fix Required**:
```python
def get_authenticated_username():
    """Get username from Flask session (secure) - NOT from client headers"""
    try:
        # Use session to identify user (set during login)
        username = session.get('username')
        role = session.get('role')
        
        if not username or not role:
            return None
            
        # Verify session user exists and role matches
        conn = get_db_connection()
        cur = conn.cursor()
        result = cur.execute(
            "SELECT role FROM users WHERE username=? AND role=?",
            (username, role)
        ).fetchone()
        conn.close()
        
        return username if result else None
    except Exception:
        return None
```

---

### 🔴 **Issue #2: Debug Endpoint Exposes User Data**

**Location**: [api.py:2783](api.py#L2783)  
**Severity**: CRITICAL (9/10)

```python
@app.route('/api/debug/analytics/<clinician>', methods=['GET'])
def debug_analytics(clinician):
    """Debug endpoint to see what analytics data would be returned"""
```

**Problem**:
- No authentication check on `/api/debug/analytics/<clinician>`
- Allows anyone to enumerate clinician names and see their analytics
- Query clinician parameter directly from URL (no validation)
- Reveals sensitive business metrics

**Proof of Concept**:
```bash
curl https://www.healing-space.org.uk/api/debug/analytics/dr_smith
# Returns: {
#   "clinician": "dr_smith",
#   "clinician_exists": true,
#   "patient_count": 25,
#   "session_stats": {...}
# }
```

**Fix Required**:
- Add `@require_role('developer')` decorator
- OR completely remove (not needed for production)
- OR return 403 if not DEBUG mode

---

### 🔴 **Issue #3: Developer Terminal Command Execution**

**Location**: [api.py:3751](api.py#L3751)  
**Severity**: CRITICAL (8/10) - Mitigated by whitelist

```python
@app.route('/api/developer/terminal/execute', methods=['POST'])
def execute_terminal():
    """Execute terminal command with restricted whitelist"""
```

**Problem**:
- Trusts `username` from JSON body (uses get_authenticated_username issue)
- Executes arbitrary system commands
- Whitelist is good, but authentication bypass negates it

**Proof of Concept**:
```bash
curl -X POST https://www.healing-space.org.uk/api/developer/terminal/execute \
  -H "Content-Type: application/json" \
  -d '{"username": "malicious_dev", "command": "cat /etc/passwd"}'
```

**Fix Required**:
- Use proper session authentication (fix Issue #1)
- Add rate limiting (max 10 commands/minute)
- Log all executions to audit table
- Require MFA for terminal access

---

### 🔴 **Issue #4: User Data Endpoint Parameter Injection**

**Location**: Multiple endpoints  
**Severity**: HIGH (8/10)

Examples:
- `/api/professional/patient/<username>` - Returns data for any username
- `/api/professional/notes/<patient_username>` - No clinician verification
- `/api/analytics/patient/<username>` - Uses `clinician_username` parameter, not verified

**Proof of Concept**:
```bash
# Any clinician can fetch any patient's data (if they know username)
curl "https://www.healing-space.org.uk/api/professional/patient/alice"
# Returns: { patient_data, therapy_sessions, notes }

# Without verifying the clinician actually treats this patient!
```

**Fix Required**:
- Verify clinician-patient relationship in database
- Use FK constraints: `clinician_id` → `users.id`
- Check: `SELECT COUNT(*) FROM clinician_patients WHERE clinician=? AND patient=?`

---

## HIGH-PRIORITY VULNERABILITIES

### 🟠 **Issue #5: No Input Validation on Many Endpoints**

**Endpoints**:
- `/api/therapy/chat` - No length limit on message
- `/api/mood/log` - mood_val not validated (should be 1-10)
- `/api/cbt/*` - No maximum length on text fields (DOS attack)

**Example**:
```bash
# DOS: Send gigantic message
curl -X POST https://www.healing-space.org.uk/api/therapy/chat \
  -d '{"message": "'$(python3 -c 'print("A"*10000000)')'"}'
# Server tries to process 10MB message → consumes RAM
```

**Fix Required**:
```python
# Add validation decorator:
MAX_MESSAGE_LENGTH = 10000  # 10KB
MAX_TEXT_FIELD = 1000

# In therapy/chat endpoint:
message = data.get('message', '').strip()
if not message or len(message) > MAX_MESSAGE_LENGTH:
    return jsonify({'error': 'Message must be 1-10000 characters'}), 400
```

---

### 🟠 **Issue #6: No Rate Limiting**

**Problem**:
- `/api/therapy/chat` - No limit on chat requests
- `/api/auth/login` - No brute-force protection
- `/api/auth/verify-code` - No limit on code attempts (6-digit code = 1M attempts)

**Proof of Concept**:
```bash
# Brute force 6-digit code in seconds
for i in {000000..999999}; do
  curl -X POST https://www.healing-space.org.uk/api/auth/verify-code \
    -d "{\"username\": \"alice\", \"code\": \"$i\"}"
done
```

**Fix Required**:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")  # Max 5 login attempts/minute
def login():
    ...

@app.route('/api/auth/verify-code', methods=['POST'])
@limiter.limit("10 per minute")  # Max 10 code attempts/minute
def verify_code():
    ...
```

---

### 🟠 **Issue #7: CSRF Token Protection Missing**

**Location**: [api.py:3845](api.py#L3845)

```python
@app.route('/api/csrf-token', methods=['GET'])
def get_csrf_token():
    """Get CSRF token for form submissions"""
    token = secrets.token_urlsafe(32)
    resp = jsonify({'csrf_token': token})
    return resp
```

**Problem**:
- CSRF token endpoint exists but NOT validated on POST endpoints
- All POST requests should validate `X-CSRF-Token` header
- No session association with CSRF token

**Example Vulnerability - CSRF Attack**:
```html
<!-- Attacker website: evilsite.com -->
<form action="https://www.healing-space.org.uk/api/mood/log" method="POST">
  <input name="mood_val" value="1">
  <input name="notes" value="I'm suicidal">
  <script>form.submit()</script>
</form>
<!-- If user visits, auto-posts "suicide note" to their therapy -->
```

**Fix Required**:
- Generate CSRF token per session (during login)
- Validate on ALL POST/PUT/DELETE endpoints
- Store in database tied to user

---

## MEDIUM-PRIORITY ISSUES

### 🟡 **Issue #8: No HTTPS enforcement**

**Problem**:
- API accessible over HTTP
- Credentials/data can be intercepted

**Fix**:
```python
@app.before_request
def force_https():
    if not request.is_secure and not DEBUG:
        return redirect(request.url.replace('http://', 'https://'), code=301)
```

---

### 🟡 **Issue #9: Insufficient Encryption**

**Status**: Using Fernet (good)  
**Problem**: Encryption key in environment (check ENCRYPTION_KEY env var)

**Recommendation**: Use AWS KMS or HashiCorp Vault for key management

---

### 🟡 **Issue #10: No Content-Type Validation**

**Problem**:
- Accepts any Content-Type on JSON endpoints
- Could accept XML, form-data, etc.

**Fix**:
```python
@app.before_request
def validate_content_type():
    if request.method in ['POST', 'PUT'] and request.endpoint:
        if 'application/json' not in request.content_type:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
```

---

## ENDPOINT INVENTORY

### Authentication Endpoints (9 endpoints)
| Endpoint | Method | Auth | Risk |
|----------|--------|------|------|
| `/api/auth/login` | POST | ❌ No auth needed | 🔴 Brute-force risk |
| `/api/auth/register` | POST | ❌ | ✅ OK |
| `/api/auth/verify-code` | POST | ❌ | 🔴 No rate limit |
| `/api/auth/forgot-password` | POST | ❌ | 🟡 Medium |
| `/api/auth/confirm-reset` | POST | ❌ | 🟡 Medium |
| `/api/auth/clinician/register` | POST | ❌ | ✅ OK (approval needed) |
| `/api/auth/developer/register` | POST | ❌ | ✅ OK (code required) |
| `/api/auth/send-verification` | POST | ❌ | ✅ OK |
| `/api/auth/disclaimer/accept` | POST | ✅ Session | ✅ OK |

### Therapy Endpoints (7 endpoints) ⚠️ HIGH RISK
| Endpoint | Method | Auth | Risk |
|----------|--------|------|------|
| `/api/therapy/chat` | POST | 🔴 X-Username | 🔴 **Data breach** |
| `/api/therapy/history` | GET | 🔴 X-Username | 🔴 **Data breach** |
| `/api/therapy/sessions` | GET | 🔴 X-Username | 🔴 **Data breach** |
| `/api/therapy/initialize` | POST | 🔴 X-Username | 🔴 **Data breach** |
| `/api/therapy/greeting` | POST | 🔴 X-Username | 🔴 **Data breach** |
| `/api/therapy/export` | GET | 🔴 X-Username | 🔴 **Data breach** |
| `/api/therapy/sessions/<id>` | GET | 🔴 X-Username | 🔴 **Data breach** |

### Clinical Endpoints (2 endpoints) ⚠️ HIGH RISK
| Endpoint | Method | Auth | Risk |
|----------|--------|------|------|
| `/api/clinical/gad7` | POST | 🔴 X-Username | 🔴 **Data breach** |
| `/api/clinical/phq9` | POST | 🔴 X-Username | 🔴 **Data breach** |

### CBT Tools Endpoints (25+ endpoints) ⚠️ HIGH RISK
All CBT endpoints use `get_authenticated_username()` - **vulnerable to identity spoofing**

### Professional/Clinician Endpoints (10 endpoints) ⚠️ HIGH RISK
| Endpoint | Method | Auth | Risk |
|----------|--------|------|------|
| `/api/professional/patients` | GET | 🔴 X-Username | 🔴 **Returns all patients** |
| `/api/professional/patient/<username>` | GET | 🔴 X-Username | 🔴 **No FK check** |
| `/api/professional/notes` | POST | 🔴 X-Username | 🔴 **No clinician verify** |
| `/api/professional/notes/<patient_username>` | GET | 🔴 X-Username | 🔴 **No FK check** |
| `/api/professional/ai-summary` | GET | 🔴 X-Username | 🟡 Medium |
| `/api/professional/export-summary` | POST | 🔴 X-Username | 🟡 Medium |

### Admin Endpoints (2 endpoints)
| Endpoint | Method | Auth | Risk |
|----------|--------|------|------|
| `/api/admin/wipe` | GET | ❌ None | ✅ Just serves HTML |
| `/api/admin/wipe-database` | POST | ✅ ADMIN_WIPE_KEY | ✅ **Protected** |

### Developer Endpoints (5 endpoints) ⚠️ HIGH RISK (if auth is broken)
| Endpoint | Method | Auth | Risk |
|----------|--------|------|------|
| `/api/developer/terminal/execute` | POST | 🔴 X-Username | 🔴 **Code execution** |
| `/api/developer/messages/send` | POST | 🔴 X-Username | 🟡 Medium |
| `/api/developer/messages/list` | GET | 🔴 X-Username | 🟡 Medium |
| `/api/developer/messages/reply` | POST | 🔴 X-Username | 🟡 Medium |
| `/api/developer/stats` | GET | 🔴 X-Username | 🟡 Medium |

### Data Export Endpoints (3 endpoints) ⚠️ HIGH RISK
| Endpoint | Method | Auth | Risk |
|----------|--------|------|------|
| `/api/export/fhir` | GET | 🔴 X-Username | 🔴 **HIPAA violation** |
| `/api/export/csv` | GET | 🔴 X-Username | 🔴 **HIPAA violation** |
| `/api/export/pdf` | GET | 🔴 X-Username | 🔴 **HIPAA violation** |

---

## REMEDIATION PLAN

### Phase 1: CRITICAL (24 hours)
- [ ] Fix `get_authenticated_username()` to use Flask session
- [ ] Validate clinician-patient relationship (FK checks)
- [ ] Remove or protect `/api/debug/analytics/<clinician>`
- [ ] Add rate limiting to auth endpoints (login, verify-code)

### Phase 2: HIGH (1 week)
- [ ] Add input validation to all endpoints (length limits, type checks)
- [ ] Implement CSRF token validation on all POST/PUT/DELETE
- [ ] Add HTTPS enforcement
- [ ] Audit all user data endpoints for proper FK checks

### Phase 3: MEDIUM (2 weeks)
- [ ] Implement Content-Type validation
- [ ] Add request/response logging for security audit trails
- [ ] Review and update database schema with FK constraints
- [ ] Add security headers (CSP, X-Frame-Options, etc.)

### Phase 4: NICE-TO-HAVE (1 month)
- [ ] Add MFA for sensitive operations
- [ ] Implement API key authentication for CLI tools
- [ ] Add OAuth2 for third-party integrations
- [ ] Security penetration testing

---

## Database Schema Security

### Current Issues
- ❌ No foreign key constraints
- ❌ No `updated_at` timestamps on sensitive tables
- ❌ No deletion tracking (soft deletes)

### Recommended Changes
```sql
-- Add FK constraints:
ALTER TABLE therapy_sessions ADD CONSTRAINT fk_user
  FOREIGN KEY (patient_username) REFERENCES users(username);

ALTER TABLE clinician_notes ADD CONSTRAINT fk_clinician
  FOREIGN KEY (clinician_username) REFERENCES users(username);

ALTER TABLE clinician_notes ADD CONSTRAINT fk_patient
  FOREIGN KEY (patient_username) REFERENCES users(username);

-- Add soft delete tracking:
ALTER TABLE users ADD deleted_at TIMESTAMP DEFAULT NULL;

-- Add audit timestamps:
ALTER TABLE therapy_sessions ADD created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE therapy_sessions ADD updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
```

---

## Testing Security Fixes

### Test Case 1: Authentication Bypass Attempt
```bash
# Before fix: Should return alice's data (VULNERABLE)
curl -H "X-Username: alice" https://www.healing-space.org.uk/api/patient/profile

# After fix: Should return 401 Unauthorized (SECURE)
# Expected: {"error": "Invalid session"}
```

### Test Case 2: Cross-User Data Access
```bash
# Before fix: Dr. Smith can read any patient's data
curl -H "X-Username: dr_smith" https://www.healing-space.org.uk/api/professional/patient/bob

# After fix: Should check FK and return 403 if not assigned
# Expected: {"error": "Patient not assigned to clinician"}
```

### Test Case 3: Rate Limiting
```bash
# Before fix: Can attempt unlimited logins
for i in {1..1000}; do
  curl -X POST https://www.healing-space.org.uk/api/auth/login -d '{"username":"test","password":"wrong"}'
done

# After fix: Should return 429 Too Many Requests after 5 attempts
# Expected: {"error": "Rate limit exceeded"}
```

---

## Compliance Implications

### GDPR Violations
- ❌ No session validation = potential unauthorized access (Article 32)
- ❌ No audit logs for data access = no accountability (Article 5)
- ❌ No rate limiting = DoS vulnerability (Article 32)

### HIPAA Violations
- ❌ No encryption in transit (HTTP allowed)
- ❌ No access controls (anyone can access patient data)
- ❌ No audit trail for therapy sessions

### NHS Digital Standards
- ❌ DCB0160 - Requires strong authentication
- ❌ Data Security and Protection Toolkit - Fails access control section

---

## Summary

**Current State**: 🔴 **PRODUCTION UNSAFE**

| Category | Status | Details |
|----------|--------|---------|
| Authentication | 🔴 BROKEN | Trusts client headers |
| Authorization | 🔴 BROKEN | No FK validation |
| Input Validation | 🟠 WEAK | Missing length limits |
| Encryption | 🟡 OK | Fernet enabled |
| Rate Limiting | 🔴 NONE | No protection |
| CSRF Protection | 🟠 INCOMPLETE | Token exists, not validated |
| HTTPS | ⚠️ UNCLEAR | Need to verify Railway config |
| Audit Logging | 🟡 PARTIAL | Some events logged |

**Recommendation**: **DO NOT RUN IN PRODUCTION** until Issues #1-4 are resolved.

---

## Next Steps

1. **Immediate** (Today): Fix authentication function to use Flask session
2. **This Week**: Add FK validation and rate limiting
3. **Before Production**: Complete Phase 1 + Phase 2 remediation

**Estimated Time**: 8-12 hours of development + testing
