# Quick Reference - Clinician & Patient Workflow

## Server Status
```bash
# Check if Flask is running
ps aux | grep "python api.py"

# Restart Flask (if needed)
cd "/home/computer001/Documents/python chat bot"
./.venv/bin/python api.py > /tmp/flask.log 2>&1 &

# Check logs
tail -f /tmp/flask.log
```

## Test Credentials
```
Clinician: dr_sarah_2026 / ClinPass123!@ / PIN: 5555
Patient: patient_john_2026 / PatPass456!@ / PIN: 6666
```

## Quick API Tests

### Get CSRF Token (Required for all requests)
```bash
curl -s http://localhost:5000/api/csrf-token | jq .csrf_token
```

### Register Clinician
```bash
CSRF_TOKEN=$(curl -s http://localhost:5000/api/csrf-token | jq -r .csrf_token)

curl -X POST http://localhost:5000/api/auth/clinician/register \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
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
  }' | jq .
```

### Clinician Login (Save Session)
```bash
CSRF_TOKEN=$(curl -s http://localhost:5000/api/csrf-token | jq -r .csrf_token)

curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -d '{
    "username": "dr_sarah_2026",
    "password": "ClinPass123!@",
    "pin": "5555"
  }' \
  -c cookies.txt | jq .
```

### Register Patient with Clinician Link
```bash
CSRF_TOKEN=$(curl -s http://localhost:5000/api/csrf-token | jq -r .csrf_token)

curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
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
  }' | jq .
```

### Get Pending Approvals (Authenticated)
```bash
# First login (see above), then:
CSRF_TOKEN=$(curl -s http://localhost:5000/api/csrf-token | jq -r .csrf_token)

curl -X GET "http://localhost:5000/api/approvals/pending?clinician=dr_sarah_2026" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -b cookies.txt | jq .
```

### Approve Patient Request
```bash
CSRF_TOKEN=$(curl -s http://localhost:5000/api/csrf-token | jq -r .csrf_token)

# Replace 1002 with actual approval ID from pending list
curl -X POST http://localhost:5000/api/approvals/1002/approve \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -b cookies.txt | jq .
```

## Database Queries

### Check Clinician Exists
```bash
PGPASSWORD="healing_space_dev_password" psql -h localhost -U healing_space_user -d healing_space_test \
  -c "SELECT username, role FROM users WHERE username='dr_sarah_2026';"
```

### Check Patient Linked to Clinician
```bash
PGPASSWORD="healing_space_dev_password" psql -h localhost -U healing_space_user -d healing_space_test \
  -c "SELECT username, clinician_id FROM users WHERE username='patient_john_2026';"
```

### Check Approval Status
```bash
PGPASSWORD="healing_space_dev_password" psql -h localhost -U healing_space_user -d healing_space_test \
  -c "SELECT patient_username, clinician_username, status, approval_date FROM patient_approvals WHERE patient_username='patient_john_2026';"
```

## Common Issues

### "Port 5000 already in use"
```bash
lsof -i :5000
kill -9 <PID>
```

### "CSRF token invalid"
- Ensure X-CSRF-Token header is included
- Get fresh token before each major operation
- Token is specific to each request

### "Professional ID is required"
- Clinician registration requires `professional_id` field
- Example: "GMC123456", "RCCP789", "CP123456"

### "Country and area are required"
- Both fields required for clinician registration
- Examples: country="UK", area="London"

### Database Connection Refused
```bash
# Check PostgreSQL is running
systemctl status postgresql

# Check user permissions
PGPASSWORD="healing_space_dev_password" psql -h localhost -U healing_space_user -d healing_space_test -c "SELECT 1;"
```

## Environment (.env)
```bash
DATABASE_URL=postgresql://healing_space_user:healing_space_dev_password@localhost:5432/healing_space_test
DEBUG=1
SECRET_KEY=healing_space_dev_secret_key_12345678901234567890
PIN_SALT=healing_space_dev_pin_salt_value_here
ENCRYPTION_KEY=jj8DaMSWoxgEcXuCn_Cz3xn-UEI9Zggbk0tY7V83cN8=
```

## Documentation Files
- Full workflow: [CLINICIAN_SETUP_COMPLETE.md](CLINICIAN_SETUP_COMPLETE.md)
- API patterns: [.github/copilot-instructions.md](.github/copilot-instructions.md)
- Database schema: api.py lines 3571+ (init_db function)
- Clinician registration: api.py lines 5820-5900
- Approval endpoints: api.py lines 6707-6760

## What Works
✅ Clinician registration with professional_id  
✅ Clinician login & session management  
✅ Patient registration with clinician_id linking  
✅ Clinician views pending patient requests  
✅ Clinician approves patient requests  
✅ Patient-clinician relationship stored in database  
✅ CSRF protection on all state-changing operations  
✅ Rate limiting configured for development (50/min register)  

## What's Next
- [ ] Patient dashboard showing clinician info
- [ ] Clinician dashboard with approved patients list
- [ ] Two-way messaging between clinician and patient
- [ ] Clinician can view patient therapy history
- [ ] Treatment plan management
- [ ] Crisis alerts to clinician
- [ ] Video consultation integration
