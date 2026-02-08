# ARCHITECTURE OVERVIEW – Healing Space UK

**Version:** 2.0 (PostgreSQL) | **Last Updated:** February 7, 2026

---

## 🏗️ SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                      Healing Space UK v2.0                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
            ┌───▼────┐   ┌────▼─────┐  ┌──▼──────┐
            │  Web   │   │  Mobile  │  │ Desktop │
            │   UI   │   │  (Future)│  │(Legacy) │
            └───┬────┘   └────┬─────┘  └──┬──────┘
                │             │            │
                └─────────────┼────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Flask REST API   │
                    │   (api.py)        │
                    │  210+ Endpoints   │
                    └─────────┬─────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
        ┌───▼────┐        ┌───▼────┐      ┌───▼────┐
        │ Groq   │        │Postgres│      │ Email  │
        │  LLM   │        │   DB   │      │ SMTP   │
        │ (AI)   │        │(43 TBL)│      │ Config │
        └────────┘        └────────┘      └────────┘
                              │
                    ┌─────────▼─────────┐
                    │ Railway.app Cloud │
                    │  (Production)     │
                    └───────────────────┘
```

---

## 💾 DATABASE ARCHITECTURE

### Database: PostgreSQL (43 Tables)

**Connection:** Railway.app (production) or local (development)

**Environment Variables:**
- `DATABASE_URL` – Railway connection string
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` – Manual config

**Core Tables:**

#### Authentication (4 tables)
```
users
├── id (PK)
├── username (UNIQUE)
├── email (UNIQUE)
├── password_hash
├── password_algo (argon2, bcrypt, pbkdf2, sha256)
├── role (patient, clinician, developer)
├── is_verified
├── created_at

sessions
├── session_id (PK)
├── username (FK users)
├── created_at
├── expires_at

two_factor_codes
├── id (PK)
├── username (FK users)
├── code
├── used_at

login_attempts
├── id (PK)
├── username
├── timestamp
```

#### Therapy & Clinical (10 tables)
```
mood_logs
├── id (PK)
├── username (FK users)
├── mood_val (1-10)
├── entry_notes
├── entrestamp

therapy_sessions
├── id (PK)
├── patient (FK users)
├── clinician (FK users)
├── session_date
├── notes

messages
├── id (PK)
├── sender_username (FK users)
├── recipient_username (FK users)
├── sender_role, recipient_role
├── subject, body
├── is_read, deleted_at

assessments (PHQ-9, GAD-7)
├── id (PK)
├── username (FK users)
├── assessment_type
├── responses (JSON)
├── score
├── created_at

cbt_tools_usage
├── id (PK)
├── username (FK users)
├── tool_name
├── created_at
```

#### Gamification (3 tables)
```
pet
├── id (PK)
├── username (FK users, UNIQUE)
├── name, species, gender
├── hunger, happiness, energy, hygiene
├── coins, xp
├── stage, hat

pet_actions
├── id (PK)
├── username (FK users)
├── action
├── timestamp

daily_tasks
├── id (PK)
├── username (FK users)
├── task_type
├── completed_date
```

#### Appointments & Scheduling (4 tables)
```
appointments
├── id (PK)
├── patient (FK users)
├── clinician (FK users)
├── appointment_time
├── status (scheduled, completed, cancelled)
├── notes

appointment_availability
├── id (PK)
├── clinician (FK users)
├── day_of_week
├── start_time, end_time

clinician_availability
├── clinician (FK users)
├── slot_time
├── is_available
```

#### GDPR & Consent (4 tables)
```
user_consent
├── username (FK users)
├── consent_type
├── status (given, withdrawn)
├── consented_at

training_data_consent
├── username (FK users)
├── status
├── consented_at

user_data_export
├── id (PK)
├── username (FK users)
├── requested_at
├── completed_at
├── file_path

audit_log
├── id (PK)
├── action
├── username (FK users)
├── timestamp
├── details (JSON)
```

#### Alerts & Safety (3 tables)
```
alerts
├── id (PK)
├── user (FK users)
├── severity (critical, high, medium)
├── message
├── is_acknowledged
├── created_at

crisis_contacts
├── username (FK users)
├── name, phone, relationship

safety_plan
├── username (FK users)
├── warning_signs
├── coping_strategies
├── support_resources
```

#### Community & Interactions (5+ tables)
```
community_posts
├── id (PK)
├── author (FK users)
├── content
├── created_at

community_comments
├── id (PK)
├── post_id (FK community_posts)
├── author (FK users)
├── content

clinician_patients
├── clinician (FK users)
├── patient (FK users)

user_preferences
├── username (FK users)
├── theme, language
├── notification_settings (JSON)
```

**Auto-Creation:**  
All 43 tables are automatically created on startup (see [api.py](api.py) `init_db()` function). Tables use `IF NOT EXISTS` to prevent errors on restart.

---

## 🌐 FRONTEND ARCHITECTURE

### Single-Page Application (SPA)

**Framework:** Vanilla JavaScript (no React/Vue/Angular)  
**File:** `templates/index.html` (~15,820 lines)

**Structure:**
```
index.html
├── HTML (sections)
│   ├── <head> - Meta, styles
│   ├── <body>
│   │   ├── Landing page
│   │   ├── Auth section (login/register)
│   │   ├── Patient dashboard
│   │   ├── Clinician dashboard
│   │   └── Developer dashboard
│   │
├── CSS (~3,000 lines)
│   ├── Global styles
│   ├── Theme variables (light/dark)
│   ├── Responsive design (mobile-first)
│   ├── Component styles
│   └── Dark mode selectors [data-theme="dark"]
│
└── JavaScript (~10,000 lines)
    ├── Global state
    │   ├── currentUser
    │   ├── currentUserRole
    │   ├── currentUserTheme
    │
    ├── Auth functions
    │   ├── completeLogin()
    │   ├── handleLogout()
    │   ├── register()
    │
    ├── Navigation
    │   ├── switchTab(tabName)
    │   ├── switchPatientTab(tabName)
    │   ├── switchClinicalTab(tabName)
    │
    ├── Features
    │   ├── Mood logging
    │   ├── AI therapy chat
    │   ├── Messaging
    │   ├── Appointments
    │   ├── Pet game
    │   ├── Assessments (PHQ-9, GAD-7)
    │
    ├── Global fetch override
    │   └── Auto-injects credentials: 'include'
    │
    └── Utilities
        ├── formatDate()
        ├── showModal()
        ├── hideModal()
        ├── toggleTheme()
```

### Navigation Model

**Tab Structure:**
```
Landing Page
    ↓
Main Dashboard (by role)
├── Patient View
│   ├── Home
│   ├── Mood Tracking
│   ├── AI Therapy Chat
│   ├── Appointments
│   ├── Assessments (PHQ-9, GAD-7)
│   ├── Coping Tools (CBT, Sleep, etc.)
│   ├── Pet Game
│   ├── Insights
│   ├── Messages
│   ├── Community
│   └── Settings
│
├── Clinician View
│   ├── Patient Dashboard
│   ├── Patient Search
│   ├── Analytics
│   ├── Appointments
│   ├── Messages
│   └── Settings
│
└── Developer View
    ├── User Management
    ├── Audit Logs
    ├── Health Check
    └── Debug Tools
```

### CSS Architecture

**Theme System:**
```css
:root {
  --primary-color: #2c5aa0;
  --secondary-color: #6c5ce7;
  --success-color: #00b894;
  --danger-color: #d63031;
  --text-primary: #2d3436;
  --text-secondary: #636e72;
  --bg-primary: #ffffff;
  --bg-secondary: #f5f6fa;
}

[data-theme="dark"] {
  --primary-color: #74b9ff;
  --text-primary: #ecf0f1;
  --bg-primary: #2d3436;
}
```

**Responsive Breakpoints:**
```css
/* Mobile-first approach */
@media (min-width: 768px) { /* Tablet */ }
@media (min-width: 1024px) { /* Desktop */ }
@media (min-width: 1440px) { /* Large desktop */ }
```

---

## 🔌 BACKEND API ARCHITECTURE

### Flask Application (`api.py`)

**Framework:** Flask + Flask-CORS + Flask-Limiter  
**Structure:** Single file (15,625 lines)

**Sections:**

#### 1. Database Connection
```python
def get_db_connection():
    """PostgreSQL connection (Railway or local)"""
    
def get_wrapped_cursor(conn):
    """Error-safe cursor wrapper"""
```

#### 2. Authentication (30+ endpoints)
```python
@app.route('/api/auth/register', methods=['POST'])
@app.route('/api/auth/login', methods=['POST'])
@app.route('/api/auth/logout', methods=['POST'])
@app.route('/api/auth/verify-2fa', methods=['POST'])
@app.route('/api/auth/check-session', methods=['GET'])
```

#### 3. Patient Features (80+ endpoints)
```python
# Mood tracking
@app.route('/api/mood/log', methods=['POST'])
@app.route('/api/mood/get', methods=['GET'])

# Therapy chat
@app.route('/api/therapy/chat', methods=['POST'])

# Appointments
@app.route('/api/appointments/schedule', methods=['POST'])

# Assessments
@app.route('/api/assessments/phq9', methods=['POST'])
@app.route('/api/assessments/gad7', methods=['POST'])

# Pet game
@app.route('/api/pet/state', methods=['GET'])
@app.route('/api/pet/action/<action>', methods=['POST'])

# Messaging
@app.route('/api/messages/send', methods=['POST'])
@app.route('/api/messages/inbox', methods=['GET'])
```

#### 4. Clinician Features (40+ endpoints)
```python
@app.route('/api/clinician/patients', methods=['GET'])
@app.route('/api/clinician/patient/<username>', methods=['GET'])
@app.route('/api/clinician/analytics/<username>', methods=['GET'])
@app.route('/api/clinician/search', methods=['POST'])
```

#### 5. Security (20+ endpoints)
```python
@app.route('/api/security/audit-log', methods=['GET'])
@app.route('/api/security/password-reset', methods=['POST'])
@app.route('/api/security/export-data', methods=['GET'])
@app.route('/api/security/delete-account', methods=['POST'])
```

#### 6. AI Therapy
```python
class TherapistAI:
    def chat(self, message, history) -> str
    def get_insight(self, entries) -> str
    
# Uses Groq LLM (configurable)
```

#### 7. Safety & Monitoring
```python
class SafetyMonitor:
    def is_high_risk(self, text) -> bool
    
def send_crisis_alert(username, risk_level, message)
```

#### 8. Utilities
```python
class InputValidator
class CSRFProtection
class TrainingDataManager
class FHIRExporter
```

### Request/Response Pattern

**Request:**
```javascript
fetch('/api/endpoint', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrfToken
    },
    credentials: 'include',  // Auto-injected by global override
    body: JSON.stringify({...})
})
```

**Response:**
```python
# Success
{
    "success": true,
    "data": {...},
    "message": "Operation completed"
}

# Error
{
    "error": "Description",
    "code": "ERROR_CODE",
    "status": 400
}
```

**Global Fetch Override (Lines 6069-6110):**  
Every fetch request automatically includes `credentials: 'include'` for session authentication.

---

## 🔐 SECURITY ARCHITECTURE

### Authentication Flow

```
1. User Registration
   ├── Input validation
   ├── Password hashing (Argon2 > bcrypt > PBKDF2 > SHA256)
   ├── Create user record
   └── Return auth token

2. User Login
   ├── Validate credentials
   ├── Create session (HttpOnly, Secure, SameSite=Lax)
   ├── Session expires in 2 hours
   └── Return CSRF token

3. API Requests
   ├── Check session validity
   ├── Verify CSRF token (POST/PUT/DELETE)
   ├── Validate user role/permissions
   └── Execute endpoint

4. Logout
   ├── Delete session
   └── Clear cookies
```

### Authorization Model

**Role-Based Access Control (RBAC):**
```
Patient
├── Own data only
├── Can access own therapy, mood, pet
├── Can message clinicians/developers
├── Cannot access other patients' data

Clinician
├── Own patients only (via clinician_patients FK)
├── Can view patient data
├── Can send messages
├── Cannot access other clinicians' patients

Developer
├── Full admin access
├── Audit logs
├── Health checks
├── Debug tools
```

### Encryption

**Data at Rest:**
- Sensitive fields: Fernet encryption (AES-128)
- Passwords: Argon2/bcrypt/PBKDF2
- 2FA codes: Salted hash

**Data in Transit:**
- HTTPS only (Railway enforced)
- HSTS header (1-year max-age)
- CSP headers (strict)

### CSRF Protection

**Token System:**
- Generated on login
- Included in `X-CSRF-Token` header
- One-time use (invalidated after verification)
- Timing-safe comparison

---

## 📊 DATA FLOW EXAMPLES

### Mood Logging Flow

```
1. Patient opens "Mood" tab
2. Enters mood (1-10), notes
3. JavaScript validates input
4. POST /api/mood/log
   ├── Session check ✓
   ├── CSRF token check ✓
   ├── Input validation (1-10 range) ✓
   ├── Insert into mood_logs table
   └── Trigger SafetyMonitor
5. Response: {success: true, mood_id: 123}
6. Frontend updates UI, refreshes analytics
```

### Therapy Chat Flow

```
1. Patient types message in chat
2. POST /api/therapy/chat
   ├── Session check ✓
   ├── CSRF token check ✓
   ├── Store message in history
   ├── Call TherapistAI.chat()
   │   └── Call Groq API with context
   ├── Receive AI response
   ├── Store AI response
   └── SafetyMonitor.is_high_risk() check
3. Response: {success: true, response: "AI text", risk: false}
4. Frontend displays response
5. Animation: dots → AI text
```

### Clinician Patient View Flow

```
1. Clinician searches for patient
2. POST /api/clinician/search {query: "John"}
   ├── Session check ✓
   ├── Role check (clinician) ✓
   ├── Query users table
   ├── Filter results (only assigned patients)
   └── Return list
3. Click patient: GET /api/clinician/patient/john
   ├── Session check ✓
   ├── Role check (clinician) ✓
   ├── Foreign key check (john in clinician's patients) ✓
   ├── Get mood logs
   ├── Get assessments
   ├── Get therapy summary
   └── Return dashboard data
4. Frontend displays patient profile with analytics
```

---

## 🚀 DEPLOYMENT ARCHITECTURE

### Railway.app Cloud Deployment

**Environment:**
- **Region:** Auto-selected
- **Auto-scaling:** Enabled
- **Database:** PostgreSQL (managed)
- **Domain:** www.healing-space.org.uk (custom)

**Build Process:**
```bash
1. Git push to main
2. Railway webhook triggered
3. Clone repository
4. Install dependencies (requirements.txt)
5. Set environment variables (from Railway dashboard)
6. Run: python api.py (Procfile)
7. App boots on dynamic port ($PORT)
8. Health check: /api/health
```

**Environment Variables:**
```
DATABASE_URL=postgresql://...
GROQ_API_KEY=...
ENCRYPTION_KEY=...
PIN_SALT=...
SECRET_KEY=...
DEBUG=0 (production)
```

**Persistence:**
- PostgreSQL managed by Railway (persists across restarts)
- Backups auto-created
- No ephemeral filesystem storage

---

## 🔄 REQUEST LIFECYCLE

```
HTTP Request
    ↓
Flask receives request
    ↓
Session middleware
├─ Verify session exists
├─ Check session expiry
└─ Load user context
    ↓
Route handler
├─ CSRF token validation (POST/PUT/DELETE)
├─ Input validation
├─ Role/permission check
├─ Database operations
└─ Response generation
    ↓
Middleware (responses)
├─ Security headers
├─ CORS headers
└─ Error handling
    ↓
HTTP Response
    ↓
Frontend receives (credentials included)
    ↓
JavaScript processes
├─ Check status code
├─ Update UI
└─ Show notifications
```

---

## 📁 KEY FILE LOCATIONS

| File | Purpose | Lines |
|------|---------|-------|
| `api.py` | Flask API, database, auth, AI | 15,625 |
| `templates/index.html` | Frontend SPA | 15,820 |
| `secrets_manager.py` | Vault/env secrets | 200+ |
| `audit.py` | Logging system | 150+ |
| `training_data_manager.py` | GDPR/consent | 300+ |
| `fhir_export.py` | FHIR/HMAC export | 200+ |
| `requirements.txt` | Dependencies | 30+ |

---

## 🔗 INTEGRATION POINTS

**Groq LLM API:**
- Endpoint: https://api.groq.com/v1/messages
- Auth: GROQ_API_KEY header
- Used for: AI therapy responses, insights generation

**Email (SMTP):**
- Configured via env vars
- Used for: Password resets, alerts, reminders

**Crisis Webhooks:**
- POST to ALERT_WEBHOOK_URL
- Payload: {username, risk_level, timestamp, message}
- Used for: External alert systems

**SFTP (Optional):**
- Requires: paramiko library + SFTP_* env vars
- Used for: Secure data export transfer

**HashiCorp Vault (Optional):**
- For: Secrets management instead of env vars
- Requires: HAS_VAULT feature flag

---

## 📈 PERFORMANCE CHARACTERISTICS

**API Response Times (Target):**
- Authentication: <50ms
- Mood logs: <100ms
- Therapy chat: <2000ms (includes LLM latency)
- Clinician search: <200ms
- Analytics: <500ms

**Database Query Optimization:**
- Indexed: username, created_at, is_read, sender/recipient
- Typical query: <50ms
- Bulk operations: <500ms

**Scalability:**
- Railway auto-scaling handles up to 10K concurrent users
- PostgreSQL connection pool: 20 connections
- No connection limits per user

---

**Last Updated:** February 7, 2026  
**Architecture Version:** 2.0 (PostgreSQL)  
**Next Review:** February 28, 2026
