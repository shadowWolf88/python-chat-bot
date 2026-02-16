# Clinician Setup & Patient Linking - COMPLETE ✅

## Summary

The complete clinician registration and patient-clinician linking workflow has been successfully tested and verified. All core functionality is working correctly on localhost:5000.

---

## Setup Status

### ✅ Completed Tasks

1. **Clinician Registration**
   - Endpoint: `POST /api/auth/clinician/register`
   - Status: ✅ Working (HTTP 201)
   - Required fields: username, password, pin, email, phone, professional_id, country, area
   - Database: User created with role='clinician'

2. **Patient Registration with Clinician Linking**
   - Endpoint: `POST /api/auth/register` (with `clinician_id` parameter)
   - Status: ✅ Working (HTTP 201)
   - Result: `pending_approval=true` in response
   - Database: Patient linked to clinician via `clinician_id` field

3. **Clinician Login & Session Authentication**
   - Endpoint: `POST /api/auth/login`
   - Status: ✅ Working (HTTP 200)
   - Returns: CSRF token, user role, clinician status info

4. **Pending Patient Approvals Retrieval**
   - Endpoint: `GET /api/approvals/pending?clinician=<clinician_username>`
   - Status: ✅ Working (HTTP 200)
   - Returns: Array of pending patient requests with approval IDs

5. **Patient Approval by Clinician**
   - Endpoint: `POST /api/approvals/<approval_id>/approve`
   - Status: ✅ Working (HTTP 200)
   - Result: `status='approved'` updated in patient_approvals table

---

## Test Results

### Test Case: Complete Workflow

**Clinician: dr_sarah_2026**
```json
{
  "username": "dr_sarah_2026",
  "password": "ClinPass123!@",
  "pin": "5555",
  "email": "dr.sarah@clinic.com",
  "phone": "+441234555666",
  "full_name": "Dr. Sarah Mitchell",
  "professional_id": "CP123456",
  "country": "UK",
  "area": "London"
}
```

**Patient: patient_john_2026**
```json
{
  "username": "patient_john_2026",
  "password": "PatPass456!@",
  "pin": "6666",
  "email": "john.patient@example.com",
  "phone": "+441555666777",
  "full_name": "John Patient",
  "dob": "1985-05-20",
  "conditions": "Depression",
  "country": "UK",
  "area": "London",
  "clinician_id": "dr_sarah_2026"
}
```

### Database Verification

**Patient Record:**
```
Username: patient_john_2026
Clinician ID: dr_sarah_2026
Role: user
```

**Clinician Record:**
```
Username: dr_sarah_2026
Role: clinician
```

**Approval Record:**
```
ID: 1002
Patient: patient_john_2026
Clinician: dr_sarah_2026
Status: approved ✅
Request Date: 2026-02-11 20:00:15.074914
Approval Date: 2026-02-11 20:02:04.473576
```

---

## API Endpoints Reference

### Authentication

#### Clinician Registration
```http
POST /api/auth/clinician/register
Content-Type: application/json
X-CSRF-Token: <token>

{
  "username": "string",
  "password": "string (8+ chars, mixed case, special char, number)",
  "pin": "string (exactly 4 digits)",
  "email": "string (valid email format)",
  "phone": "string (valid phone format)",
  "full_name": "string",
  "professional_id": "string (required)",
  "country": "string",
  "area": "string"
}

Response 201:
{
  "success": true,
  "message": "Clinician account created successfully"
}
```

#### Patient Registration with Clinician Link
```http
POST /api/auth/register
Content-Type: application/json
X-CSRF-Token: <token>

{
  "username": "string",
  "password": "string",
  "pin": "string (exactly 4 digits)",
  "email": "string",
  "phone": "string",
  "full_name": "string",
  "dob": "YYYY-MM-DD",
  "conditions": "string",
  "country": "string",
  "area": "string",
  "clinician_id": "string (optional - username of clinician)"
}

Response 201:
{
  "success": true,
  "message": "Account created! Your clinician will approve your request shortly.",
  "username": "patient_john_2026",
  "pending_approval": true
}
```

#### Clinician Login
```http
POST /api/auth/login
Content-Type: application/json
X-CSRF-Token: <token>

{
  "username": "string",
  "password": "string",
  "pin": "string (4 digits)"
}

Response 200:
{
  "success": true,
  "message": "Login successful",
  "username": "dr_sarah_2026",
  "role": "clinician",
  "approval_status": "approved",
  "clinician_id": null,
  "clinician_name": null,
  "disclaimer_accepted": false,
  "csrf_token": "string"
}
```

### Approvals Management

#### Get Pending Patient Approvals
```http
GET /api/approvals/pending?clinician=<clinician_username>
X-CSRF-Token: <token>

Response 200:
{
  "pending_approvals": [
    {
      "id": 1002,
      "patient_username": "patient_john_2026",
      "request_date": "Wed, 11 Feb 2026 20:00:15 GMT"
    }
  ]
}
```

#### Approve Patient Request
```http
POST /api/approvals/<approval_id>/approve
Content-Type: application/json
X-CSRF-Token: <token>

{}

Response 200:
{
  "success": true,
  "message": "Patient approved successfully"
}
```

---

## Database Schema

### users table (relevant columns)
```sql
username TEXT PRIMARY KEY
role TEXT DEFAULT 'user'  -- 'user', 'clinician', 'developer'
clinician_id TEXT  -- References clinician's username
email TEXT
phone TEXT
professional_id TEXT  -- Required for clinicians
country TEXT
area TEXT
```

### patient_approvals table
```sql
id SERIAL PRIMARY KEY
patient_username TEXT NOT NULL
clinician_username TEXT NOT NULL
status TEXT DEFAULT 'pending'  -- 'pending', 'approved', 'rejected'
request_date TIMESTAMP
approval_date TIMESTAMP
```

---

## Configuration

### Environment Variables (.env)
```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=healing_space_test
DB_USER=healing_space_user
DB_PASSWORD=healing_space_dev_password

# Flask
SECRET_KEY=healing_space_dev_secret_key_12345678901234567890
PIN_SALT=healing_space_dev_pin_salt_value_here
DEBUG=1

# Security
ENCRYPTION_KEY=jj8DaMSWoxgEcXuCn_Cz3xn-UEI9Zggbk0tY7V83cN8=

# Optional
GROQ_API_KEY=sk_test_placeholder_for_local_development
```

### Rate Limiting (Development Mode)
- Registration: 50 requests per 60 seconds (DEBUG=1)
- Login: 5 requests per minute
- Modified in api.py line 2281: `'register': (50, 60) if DEBUG else (3, 300)`

---

## Server Information

### Flask Server
- **Status**: Running
- **Host**: http://localhost:5000
- **Process**: `.venv/bin/python api.py`
- **Auto-reload**: Enabled in DEBUG mode

### PostgreSQL Connection
- **Host**: localhost
- **Port**: 5432
- **Database**: healing_space_test
- **User**: healing_space_user
- **Connection Pool**: Min 2, Max 20 connections

---

## Next Steps (Optional Enhancements)

1. **Patient Dashboard**: Display assigned clinician and approval status
2. **Clinician Dashboard**: List of approved patients with patient details
3. **Two-way Messaging**: Direct communication between clinician and patient
4. **Patient Records**: Clinician can view patient therapy history and notes
5. **Treatment Plans**: Clinician can create and update treatment plans
6. **Crisis Alerts**: Real-time alerts for high-risk patient behavior
7. **Video Consultations**: Integrate video conferencing for remote sessions

---

## Known Limitations

1. No patient rejection workflow (can only approve or ignore)
2. No patient removal/discharge workflow
3. No bulk patient import for clinicians
4. No multi-clinician assignment per patient
5. Limited patient filtering/search for clinicians

---

## Troubleshooting

### Port 5000 Already in Use
```bash
# Kill existing Flask process
pkill -f "python api.py"

# Restart Flask
./.venv/bin/python api.py > /tmp/flask.log 2>&1 &
```

### Database Connection Issues
```bash
# Verify PostgreSQL is running
ps aux | grep postgres

# Check database exists
PGPASSWORD="healing_space_dev_password" psql -h localhost -U healing_space_user -l | grep healing_space_test

# Reset sequences if duplicate key errors occur
./.venv/bin/python reset_railway_db.py
```

### CSRF Token Errors
```bash
# Ensure X-CSRF-Token header is included on all POST/PUT/DELETE requests
# Get fresh token before each request from /api/csrf-token endpoint
```

---

## Security Notes

### CSRF Protection
- All state-changing operations (POST, PUT, DELETE) require `X-CSRF-Token` header
- Token obtained from `GET /api/csrf-token` endpoint
- Token regenerated on each request

### Authentication
- Password hashing: Argon2 > bcrypt > PBKDF2
- PIN: Exactly 4 digits, salted with PIN_SALT
- Session-based authentication (not token-based)

### Rate Limiting
- Prevents brute force attacks
- Development mode: 50/min register, 5/min login
- Production mode: 3/5min register, 5/min login

---

## Testing Commands

### Test Clinician Registration
```bash
curl -X POST http://localhost:5000/api/auth/clinician/register \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: <token>" \
  -d '{
    "username": "dr_test",
    "password": "Test123!@",
    "pin": "1234",
    "email": "dr@test.com",
    "phone": "+441234567890",
    "full_name": "Dr. Test",
    "professional_id": "TEST123",
    "country": "UK",
    "area": "London"
  }'
```

### Test Patient Registration with Clinician
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: <token>" \
  -d '{
    "username": "patient_test",
    "password": "Test456!@",
    "pin": "5678",
    "email": "patient@test.com",
    "phone": "+441234567891",
    "full_name": "Patient Test",
    "dob": "1990-01-01",
    "conditions": "Anxiety",
    "country": "UK",
    "area": "London",
    "clinician_id": "dr_test"
  }'
```

### Test Clinician Login & Get Pending Approvals
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: <token>" \
  -d '{
    "username": "dr_test",
    "password": "Test123!@",
    "pin": "1234"
  }' \
  -c cookies.txt

curl -X GET "http://localhost:5000/api/approvals/pending?clinician=dr_test" \
  -H "X-CSRF-Token: <new_token>" \
  -b cookies.txt
```

---

## Files Modified This Session

1. **api.py** (lines 27-31, 2281)
   - Added python-dotenv auto-loading
   - Modified rate limiting for DEBUG mode

2. **.env** (created)
   - Database configuration
   - Flask secrets
   - Encryption keys

---

## References

- Copilot Instructions: [.github/copilot-instructions.md](.github/copilot-instructions.md)
- API Patterns: See `api.py` lines 5820-5900 (clinician registration), 6707-6760 (approvals)
- Database: See `api.py` lines 3571+ (init_db function with 45+ tables)

---

**Status**: ✅ READY FOR PRODUCTION TESTING  
**Last Verified**: 2026-02-11 20:02:04 UTC  
**Next Phase**: Patient dashboard, two-way messaging, treatment plans
