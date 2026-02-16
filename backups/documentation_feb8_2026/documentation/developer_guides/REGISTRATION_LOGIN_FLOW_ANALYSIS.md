# Healing Space - User Registration & Login Flow Analysis

**Generated:** February 4, 2026

---

## 1. Patient Registration Form

### Form Location
**File:** [templates/index.html](templates/index.html#L3037-L3123)
**Form ID:** `registerForm`
**Form Element:** Hidden div, shown on click of "Create Patient Account"

### Patient Registration Fields

| Field | ID | Type | Required | Notes |
|-------|-----|------|----------|-------|
| Full Name | `regFullName` | text | ✓ Required | Placeholder: "John Doe" |
| Date of Birth | `regDOB` | date | ✓ Required | Max set to today's date (prevents future dates) |
| Medical Conditions/Diagnosis | `regConditions` | textarea | ✓ Required | Text area (min-height: 80px), helps clinician provide better care |
| Country | `regCountry` | text | ✓ Required | Placeholder: "United Kingdom" |
| Area / Region | `regArea` | text | ✓ Required | Placeholder: "London, Manchester, etc." |
| Postcode | `regPostcode` | text | ✗ Optional | Placeholder: "SW1A 1AA" |
| NHS Number | `regNHS` | text | ✗ Optional | Max length: 12 chars, Placeholder: "123 456 7890" |
| Username | `regUsername` | text | ✓ Required | Placeholder: "Choose username" |
| Password | `regPassword` | password | ✓ Required | Includes password strength indicator (visual bar) |
| Confirm Password | `regConfirmPassword` | password | ✓ Required | Must match password field |
| PIN (4 digits) | `regPin` | password | ✓ Required | Max length: 4 chars, numeric only (4-digit 2FA PIN) |
| Confirm PIN | `regConfirmPin` | password | ✓ Required | Max length: 4 chars, must match PIN field |
| Email Address | `regEmail` | email | ✓ Required | Placeholder: "your.email@example.com" |
| Phone Number | `regPhone` | tel | ✓ Required | Placeholder: "+1234567890" |
| Select Your Clinician | `regClinician` | select dropdown | ✓ Required | Dynamically populated from /api/clinicians/list |

### Form Validation (Client-Side)
**Function:** `register()` ([templates/index.html](templates/index.html#L8083-L8200))

**Validations performed:**
1. Full name required
2. Date of birth required
3. Medical conditions/diagnosis required
4. Country and area required
5. Username, password, PIN, email, phone required (all filled)
6. Passwords match validation
7. PINs match validation
8. Clinician selected validation
9. Password minimum 8 characters
10. Password contains lowercase AND uppercase letters
11. Password contains at least one number
12. Password contains at least one special character
13. PIN is exactly 4 digits (numeric only)

### Error Handling
- **Validation errors** show via `showAuthMessage(message, 'error')`
- After successful client-side validation, registration data stored in `tempLoginData` object
- Shows disclaimer modal before completion
- Complete registration occurs in `completePatientRegistration()`

---

## 2. Country Selection Implementation

### Current Implementation

**Type:** Free-text input (NOT dropdown)

**HTML Structure:**
```html
<div class="form-group">
    <label>Country *</label>
    <input type="text" id="regCountry" placeholder="United Kingdom" required>
</div>

<div class="form-group">
    <label>Area / Region *</label>
    <input type="text" id="regArea" placeholder="London, Manchester, etc." required>
</div>
```

**File:** [templates/index.html](templates/index.html#L3057-L3065)

### Dynamic Clinician Filtering Based on Location

**Function:** `loadCliniciansForRegistration()` ([templates/index.html](templates/index.html#L8328-L8352))

**How it works:**
1. Event listeners attached to both country and area inputs in `showPatientRegister()`
2. When user **leaves** (blur) country or area field, `loadCliniciansForRegistration()` is called
3. Function reads current values from `regCountry` and `regArea` inputs
4. Makes API call to `/api/clinicians/list` with optional query parameters:
   - `?country=<value>`
   - `?area=<value>`
5. Backend searches for clinicians with CASE-INSENSITIVE LIKE matching

**JavaScript Code:**
```javascript
async function loadCliniciansForRegistration() {
    try {
        const country = document.getElementById('regCountry')?.value.trim() || '';
        const area = document.getElementById('regArea')?.value.trim() || '';
        
        let url = '/api/clinicians/list';
        const params = new URLSearchParams();
        if (country) params.append('country', country);
        if (area) params.append('area', area);
        if (params.toString()) url += '?' + params.toString();
        
        const response = await fetch(url);
        const data = await response.json();
        
        const select = document.getElementById('regClinician');
        if (response.ok && data.clinicians && data.clinicians.length > 0) {
            select.innerHTML = '<option value="">-- Select your clinician --</option>' +
                data.clinicians.map(c => 
                    `<option value="${c.username}">${c.full_name || c.username}${c.area ? ' (' + c.area + ')' : ''}</option>`
                ).join('');
        } else {
            select.innerHTML = '<option value="">No clinicians found in your area</option>';
        }
    } catch (error) {
        console.error('Error loading clinicians:', error);
        document.getElementById('regClinician').innerHTML = '<option value="">Error loading clinicians</option>';
    }
}
```

### Backend Clinician List Endpoint

**Route:** `/api/clinicians/list` [GET]
**File:** [api.py](api.py#L4225-L4261)

**Query Parameters:**
- `country` (optional): Case-insensitive partial match on `users.country`
- `area` (optional): Case-insensitive partial match on `users.area`

**Query Logic:**
```python
query = "SELECT username, full_name, country, area FROM users WHERE role='clinician'"

if country:
    query += " AND LOWER(country) LIKE LOWER(?)"
    params.append(f"%{country}%")

if area:
    query += " AND LOWER(area) LIKE LOWER(?)"
    params.append(f"%{area}%")

query += " ORDER BY username"
```

**Response Format:**
```json
{
    "clinicians": [
        {
            "username": "dr_smith",
            "full_name": "Dr. John Smith",
            "country": "United Kingdom",
            "area": "London"
        }
    ]
}
```

---

## 3. Clinician Requirement in Patient Registration

### Status: **REQUIRED**

**Evidence:**

1. **Frontend Validation** (Line [8129](templates/index.html#L8129)):
```javascript
if (!clinician_id) {
    showAuthMessage('Please select your clinician', 'error');
    return;
}
```

2. **Backend Validation** (Line [3085-3090](api.py#L3085-L3090)):
```python
if not clinician_id:
    return jsonify({'error': 'Please select your clinician'}), 400

conn = get_db_connection()
cur = conn.cursor()

# Verify clinician exists
clinician = cur.execute(
    "SELECT username FROM users WHERE username=? AND role='clinician'",
    (clinician_id,)
).fetchone()

if not clinician:
    conn.close()
    return jsonify({'error': 'Invalid clinician ID. Please select a valid clinician.'}), 400
```

3. **Database Operations** (Lines [3135-3138](api.py#L3135-L3138)):
```python
# Create pending approval request
cur.execute("INSERT INTO patient_approvals (patient_username, clinician_username, status) VALUES (?,?,?)",
           (username, clinician_id, 'pending'))

# Notify clinician of new patient request
cur.execute("INSERT INTO notifications (recipient_username, message, notification_type) VALUES (?,?,?)",
           (clinician_id, f'New patient request from {full_name} ({username})', 'patient_request'))
```

### Clinician Approval Workflow
1. Patient registers and selects a clinician
2. A `patient_approvals` record is created with status `'pending'`
3. Clinician receives a notification
4. Clinician must approve the patient before they can fully access the system
5. Patient sees "pending approval" status until clinician approves

---

## 4. Password/PIN Visibility Toggle - ALL Locations

### ⚠️ Issue Found: `togglePasswordVisibility()` Function Not Defined

The function `togglePasswordVisibility()` is called 8 times in registration/clinician forms but **is not defined anywhere** in the codebase (neither in [templates/index.html](templates/index.html) nor in [static/js/ux-enhancements.js](static/js/ux-enhancements.js)).

### Defined Toggle Function: `togglePassword()`

**Location:** [templates/index.html](templates/index.html#L11885-L11897)

```javascript
function togglePassword(inputId, button) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
        button.textContent = '🙈';
        button.title = 'Hide password';
    } else {
        input.type = 'password';
        button.textContent = '👁️';
        button.title = 'Show password';
    }
}
```

**Used in:** Login forms (developer, patient, clinician)

---

### Password/PIN Visibility Toggles - Complete List

#### **PATIENT LOGIN FORM**
**Form ID:** `patientLoginForm` | **File:** [templates/index.html](templates/index.html#L2970-L2999)

| Field | Input ID | Button Type | onclick Handler | Icon | Line |
|-------|----------|-------------|-----------------|------|------|
| Password | `loginPassword` | button | `togglePassword('loginPassword', this)` | 👁️ | [2982](templates/index.html#L2982) |
| PIN (2FA) | `loginPin` | button | `togglePassword('loginPin', this)` | 👁️ | [2991](templates/index.html#L2991) |

#### **CLINICIAN LOGIN FORM**
**Form ID:** `clinicianLoginForm` | **File:** [templates/index.html](templates/index.html#L3007-L3035)

| Field | Input ID | Button Type | onclick Handler | Icon | Line |
|-------|----------|-------------|-----------------|------|------|
| Password | `clinicianLoginPassword` | button | `togglePassword('clinicianLoginPassword', this)` | 👁️ | [3015](templates/index.html#L3015) |
| PIN (2FA) | `clinicianLoginPin` | button | `togglePassword('clinicianLoginPin', this)` | 👁️ | [3024](templates/index.html#L3024) |

#### **DEVELOPER LOGIN FORM**
**Form ID:** (Developer section) | **File:** [templates/index.html](templates/index.html#L2950-L2968)

| Field | Input ID | Button Type | onclick Handler | Icon | Line |
|-------|----------|-------------|-----------------|------|------|
| Password | `devLoginPassword` | button | `togglePassword('devLoginPassword', this)` | 👁️ | [2955](templates/index.html#L2955) |
| PIN (2FA) | `devLoginPin` | button | `togglePassword('devLoginPin', this)` | 👁️ | [2962](templates/index.html#L2962) |

#### **PATIENT REGISTRATION FORM** ⚠️ USING UNDEFINED FUNCTION
**Form ID:** `registerForm` | **File:** [templates/index.html](templates/index.html#L3037-L3123)

| Field | Input ID | Button ID | onclick Handler | Status | Line |
|-------|----------|-----------|-----------------|--------|------|
| Password | `regPassword` | `regPasswordToggle` | `togglePasswordVisibility('regPassword', 'regPasswordToggle')` | ❌ NOT DEFINED | [3077](templates/index.html#L3077) |
| Confirm Password | `regConfirmPassword` | `regConfirmPasswordToggle` | `togglePasswordVisibility('regConfirmPassword', 'regConfirmPasswordToggle')` | ❌ NOT DEFINED | [3088](templates/index.html#L3088) |
| PIN | `regPin` | `regPinToggle` | `togglePasswordVisibility('regPin', 'regPinToggle')` | ❌ NOT DEFINED | [3095](templates/index.html#L3095) |
| Confirm PIN | `regConfirmPin` | `regConfirmPinToggle` | `togglePasswordVisibility('regConfirmPin', 'regConfirmPinToggle')` | ❌ NOT DEFINED | [3102](templates/index.html#L3102) |

#### **CLINICIAN REGISTRATION FORM** ⚠️ USING UNDEFINED FUNCTION
**Form ID:** `clinicianRegisterForm` | **File:** [templates/index.html](templates/index.html#L3124-L3189)

| Field | Input ID | Button ID | onclick Handler | Status | Line |
|-------|----------|-----------|-----------------|--------|------|
| Password | `clinicianPassword` | `clinicianPasswordToggle` | `togglePasswordVisibility('clinicianPassword', 'clinicianPasswordToggle')` | ❌ NOT DEFINED | [3161](templates/index.html#L3161) |
| Confirm Password | `clinicianConfirmPassword` | `clinicianConfirmPasswordToggle` | `togglePasswordVisibility('clinicianConfirmPassword', 'clinicianConfirmPasswordToggle')` | ❌ NOT DEFINED | [3168](templates/index.html#L3168) |
| PIN | `clinicianPin` | `clinicianPinToggle` | `togglePasswordVisibility('clinicianPin', 'clinicianPinToggle')` | ❌ NOT DEFINED | [3175](templates/index.html#L3175) |
| Confirm PIN | `clinicianConfirmPin` | `clinicianConfirmPinToggle` | `togglePasswordVisibility('clinicianConfirmPin', 'clinicianConfirmPinToggle')` | ❌ NOT DEFINED | [3182](templates/index.html#L3182) |

### Password Strength Indicator

**Patient Registration Only**

| Element | ID | Purpose |
|---------|-----|---------|
| Strength Bar | `passwordStrengthBar` | Visual indicator (background color changes) |
| Strength Fill | `passwordStrengthFill` | Fills based on password strength (0-100%) |
| Strength Text | `passwordStrengthText` | Text feedback: "Weak", "Fair", "Good", "Strong" |

**Function:** `checkPasswordStrength()` ([templates/index.html](templates/index.html#L8050-L8082))

**Scoring Logic:**
- +25% for length >= 8 chars
- +25% for lowercase AND uppercase
- +25% for at least one digit
- +25% for special character

**Color Mapping:**
- 0-25%: Red (#dc3545) = "Weak"
- 26-50%: Amber (#ffc107) = "Fair"
- 51-75%: Cyan (#17a2b8) = "Good"
- 76-100%: Green (#28a745) = "Strong"

---

## 5. Password Reset Flow

### Forgot Password Form

**Location:** [templates/index.html](templates/index.html#L3192-L3210)
**Form ID:** `forgotPasswordForm`
**Fields:**
- Username: `forgotUsername`
- Email: `forgotEmail`

### Step 1: Request Password Reset

**Function:** `requestPasswordReset()` ([templates/index.html](templates/index.html#L7665-L7697))

**Frontend Call:**
```javascript
async function requestPasswordReset() {
    const username = document.getElementById('forgotUsername').value.trim();
    const email = document.getElementById('forgotEmail').value.trim();
    
    if (!username || !email) {
        showAuthMessage('Please enter your username and email', 'error');
        return;
    }
    
    // ... calls /api/auth/forgot-password
}
```

**API Endpoint:** `POST /api/auth/forgot-password` 
**File:** [api.py](api.py#L3301-L3366)

**Backend Logic:**

1. **Receive Request:**
   - Username and email from request body

2. **Verify User:**
   - Query: `SELECT email FROM users WHERE username=? AND email=?`
   - If user not found → return success anyway (security: don't reveal if user exists)

3. **Generate Reset Token:**
   - Create 32-character URL-safe random token
   - Set expiry to 1 hour from now
   - Store in database: `UPDATE users SET reset_token=?, reset_token_expiry=? WHERE username=?`

4. **Send Email:**
   - Call `send_reset_email(email, username, reset_token)`
   - Email includes reset link with token embedded
   - If email fails, still return success (token stored, user can contact support with username)

5. **Response:**
```json
{
    "success": true,
    "message": "If account exists, reset link sent"
}
```

6. **Logging:**
   - Logged as: `log_event(username, 'api', 'password_reset_requested', ...)`

---

### Step 2: Confirm Password Reset

**API Endpoint:** `POST /api/auth/confirm-reset`
**File:** [api.py](api.py#L3434-L3497)

**Request Body:**
```json
{
    "username": "string",
    "token": "string",
    "new_password": "string"
}
```

**Backend Logic:**

1. **Validate Input:**
   - Username, token, and new password required

2. **Validate Password Strength:**
   - Uses `validate_password_strength(new_password)`
   - Must be 8+ chars, contain lowercase, uppercase, number, special character

3. **Retrieve Stored Token:**
   - Query: `SELECT reset_token, reset_token_expiry FROM users WHERE username=?`

4. **Verify Token:**
   - Token must exist (not NULL)
   - Token must MATCH stored token (byte-for-byte)
   - If mismatch → log security event: `'invalid_reset_token'`

5. **Check Expiry:**
   - Parse stored expiry datetime
   - If current time > expiry → return "Reset token has expired"

6. **Update Password:**
   - Hash new password: `hash_password(new_password)`
   - Update database: `UPDATE users SET password=?, reset_token=NULL, reset_token_expiry=NULL WHERE username=?`
   - **Clear all sessions:** 
     - `DELETE FROM sessions WHERE username=?`
     - `DELETE FROM chat_sessions WHERE username=?`
   - This forces user to log in again with new password

7. **Response:**
```json
{
    "success": true,
    "message": "Password has been reset successfully. Please log in with your new password."
}
```

8. **Logging:**
   - Logged as: `log_event(username, 'security', 'password_reset_completed', ...)`

### Security Features

✓ **Rate limiting** on both endpoints via `@check_rate_limit` decorator
✓ **Token expiry** (1 hour)
✓ **Session invalidation** after password reset
✓ **Token mismatch logging** (security audit)
✓ **Non-revealing error messages** (doesn't confirm if user exists)
✓ **Password strength validation** (centralized function)

---

## 6. Backend Validation - Patient Registration Endpoint

### Endpoint Details

**Route:** `POST /api/auth/register`
**Rate Limiting:** Yes (`@check_rate_limit('register')`)
**File:** [api.py](api.py#L3030-L3150)

### Required Fields (Client → Backend)

| Field | Key | Type | Backend Validation |
|-------|-----|------|-------------------|
| Username | `username` | string | ✓ Must be unique, must not exist in users table |
| Password | `password` | string | ✓ Must pass `validate_password_strength()` |
| PIN | `pin` | string | ✓ Must be exactly 4 digits, numeric only (local validation) |
| Email | `email` | string | ✓ Must be unique, must not exist in users table |
| Phone | `phone` | string | ✓ Must be unique, must not exist in users table |
| Full Name | `full_name` | string | ✓ Required, cannot be empty |
| Date of Birth | `dob` | string (YYYY-MM-DD) | ✓ Required, cannot be empty |
| Medical Conditions | `conditions` | string | ✓ Required, cannot be empty |
| Country | `country` | string | ✓ Required, cannot be empty |
| Area | `area` | string | ✓ Required, cannot be empty |
| Clinician ID | `clinician_id` | string | ✓ Required, clinician must exist with `role='clinician'` |
| **Optional:** Postcode | `postcode` | string | ✓ Optional |
| **Optional:** NHS Number | `nhs_number` | string | ✓ Optional (max 12 chars) |
| Verified Identifier | `verified_identifier` | string | ⚠️ Required IF `REQUIRE_2FA_SIGNUP=1` |

### Validation Logic (Lines [3031-3161](api.py#L3031-L3161))

```python
# 1. Check all required fields present
if not username or not password or not pin or not email or not phone:
    return jsonify({'error': 'All fields are required'}), 400

# 2. Check 2FA verification if required
if os.getenv('REQUIRE_2FA_SIGNUP', '0') == '1':
    if not verified_identifier:
        return jsonify({'error': 'Please verify your email or phone number first'}), 400
    
    # Check verification exists and is valid
    verified = cur.execute(
        "SELECT id FROM verification_codes WHERE identifier=? AND verified=1 AND datetime(expires_at) > datetime('now')",
        (verified_identifier,)
    ).fetchone()
    
    if not verified:
        return jsonify({'error': 'Verification expired or invalid. Please verify again.'}), 400

# 3. Validate location fields
if not country or not area:
    return jsonify({'error': 'Country and area are required'}), 400

# 4. Validate full name and DOB
if not full_name:
    return jsonify({'error': 'Full name is required'}), 400

if not dob:
    return jsonify({'error': 'Date of birth is required'}), 400

# 5. Validate conditions
if not conditions:
    return jsonify({'error': 'Medical conditions/diagnosis is required'}), 400

# 6. Validate password strength (centralized function)
is_valid, error_msg = validate_password_strength(password)
if not is_valid:
    return jsonify({'error': error_msg}), 400

# 7. Validate clinician selected
if not clinician_id:
    return jsonify({'error': 'Please select your clinician'}), 400

# 8. Verify clinician exists
clinician = cur.execute(
    "SELECT username FROM users WHERE username=? AND role='clinician'",
    (clinician_id,)
).fetchone()

if not clinician:
    conn.close()
    return jsonify({'error': 'Invalid clinician ID. Please select a valid clinician.'}), 400

# 9. Check uniqueness constraints
if cur.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone():
    conn.close()
    return jsonify({'error': 'Username already exists'}), 409

if cur.execute("SELECT username FROM users WHERE email=?", (email,)).fetchone():
    conn.close()
    return jsonify({'error': 'Email already in use'}), 409

if cur.execute("SELECT username FROM users WHERE phone=?", (phone,)).fetchone():
    conn.close()
    return jsonify({'error': 'Phone number already in use'}), 409
```

### Password Strength Validation

**Function:** `validate_password_strength()` ([api.py](api.py) - search for function definition)

**Requirements:**
1. Minimum 8 characters
2. At least one lowercase letter
3. At least one uppercase letter
4. At least one digit
5. At least one special character

### Database Operations on Success

**1. Create user record:**
```python
cur.execute("INSERT INTO users (username, password, pin, email, phone, full_name, dob, conditions, last_login, role, country, area, postcode, nhs_number) 
VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
   (username, hashed_password, hashed_pin, email, phone, full_name, dob, conditions, datetime.now(), 'user', country, area, postcode, nhs_number))
```

**2. Create patient approval request:**
```python
cur.execute("INSERT INTO patient_approvals (patient_username, clinician_username, status) 
VALUES (?,?,?)",
   (username, clinician_id, 'pending'))
```

**3. Notify clinician:**
```python
cur.execute("INSERT INTO notifications (recipient_username, message, notification_type) 
VALUES (?,?,?)",
   (clinician_id, f'New patient request from {full_name} ({username})', 'patient_request'))
```

**4. Notify patient (pending approval):**
```python
cur.execute("INSERT INTO notifications (recipient_username, message, notification_type) 
VALUES (?,?,?)",
   (username, f'Your request to join Dr. {clinician_id} is pending approval', 'approval_pending'))
```

### Users Table Schema

**Initial Creation:** [api.py](api.py#L1923-L1928)

```sql
CREATE TABLE IF NOT EXISTS users 
(
    username TEXT PRIMARY KEY,
    password TEXT,
    pin TEXT,
    last_login TIMESTAMP,
    full_name TEXT,
    dob TEXT,
    conditions TEXT,
    role TEXT DEFAULT 'user',
    clinician_id TEXT,
    disclaimer_accepted INTEGER DEFAULT 0
)
```

**Added Columns (Migrations):** [api.py](api.py#L2276-L2323)

| Column | Type | Migration Added |
|--------|------|-----------------|
| `email` | TEXT | Line 2278 |
| `phone` | TEXT | Line 2283 |
| `reset_token` | TEXT | Line 2288 |
| `reset_token_expiry` | DATETIME | Line 2293 |
| `country` | TEXT | Line 2298 |
| `area` | TEXT | Line 2303 |
| `postcode` | TEXT | Line 2308 |
| `nhs_number` | TEXT | Line 2313 |
| `professional_id` | TEXT | Line 2318 |

### Success Response

**Status:** 201 Created

```json
{
    "success": true,
    "message": "Account created! Your clinician will approve your request shortly.",
    "username": "string",
    "pending_approval": true
}
```

### Error Responses

| HTTP Status | Error Message | Scenario |
|-------------|---------------|----------|
| 400 | "All fields are required" | Missing required fields |
| 400 | "Country and area are required" | Missing location |
| 400 | "Full name is required" | Missing name |
| 400 | "Date of birth is required" | Missing DOB |
| 400 | "Medical conditions/diagnosis is required" | Missing conditions |
| 400 | "[Password] must contain both lowercase and uppercase letters" | Weak password |
| 400 | "[Password] must be at least 8 characters" | Password too short |
| 400 | "[Password] must contain at least one number" | No digits |
| 400 | "[Password] must contain at least one special character" | No special chars |
| 400 | "Please select your clinician" | No clinician selected |
| 400 | "Invalid clinician ID. Please select a valid clinician." | Clinician doesn't exist |
| 409 | "Username already exists" | Duplicate username |
| 409 | "Email already in use" | Duplicate email |
| 409 | "Phone number already in use" | Duplicate phone |
| 400 | "Please verify your email or phone number first" | 2FA required but not verified |
| 400 | "Verification expired or invalid. Please verify again." | 2FA verification invalid |

---

## Summary Table

| Component | Status | Notes |
|-----------|--------|-------|
| Patient Registration Form | ✓ Complete | 14 fields (10 required, 2 optional, clinician required, location required) |
| Country Selection | ✓ Free-text | Text input with dynamic clinician filtering via API |
| Clinician Requirement | ✓ **REQUIRED** | Validated front and back end, triggers approval workflow |
| Password Visibility Toggle | ⚠️ **ISSUE** | Login forms use `togglePassword()` ✓ | Registration forms call undefined `togglePasswordVisibility()` ❌ |
| Password Reset - Request | ✓ Complete | 1-hour token expiry, rate-limited, non-revealing errors |
| Password Reset - Confirm | ✓ Complete | Token validation, password strength check, session invalidation |
| Backend Validation | ✓ Complete | All fields validated, uniqueness constraints, clinician verification |
| Database Schema | ✓ Complete | 9 columns + 9 migrated columns for patient profiles |

---

## ⚠️ Critical Issues Identified

### 1. **Undefined Function: `togglePasswordVisibility()`**
- **Impact:** Password/PIN visibility toggles in registration forms don't work
- **Locations:** 
  - Patient registration: Lines 3077, 3088, 3095, 3102
  - Clinician registration: Lines 3161, 3168, 3175, 3182
- **Solution:** Define function or replace with `togglePassword()`

### 2. **Inconsistent Toggle Implementation**
- **Login forms:** Use `togglePassword()` ✓ (defined at line 11885)
- **Registration forms:** Call `togglePasswordVisibility()` ❌ (undefined)
- **Solution:** Standardize on single function name

### 3. **Missing 2FA for Registration**
- Backend checks for `REQUIRE_2FA_SIGNUP` flag
- Frontend registration has no email/SMS verification UI
- **Solution:** Add verification code input if flag enabled

---

## References

- **API Endpoint Documentation:** [api.py](api.py#L3030-L3530)
- **HTML Registration Form:** [templates/index.html](templates/index.html#L3037-L3123)
- **JavaScript Functions:** [templates/index.html](templates/index.html#L8050-L8400)
- **Database Schema:** [api.py](api.py#L1919-L2330)
