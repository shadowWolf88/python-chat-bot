# TIER 1.1: Clinician Dashboard Fixes - World-Class Implementation Prompt

**Project**: Healing Space UK (Mental Health Therapy Platform)  
**Scope**: Fix 20+ broken clinician dashboard features  
**Effort**: 20-25 hours  
**Target Completion**: February 14-17, 2026  
**Status**: Ready for implementation

---

## 📋 EXECUTIVE SUMMARY

The Clinician Dashboard (accessed by therapists/NHS staff) is 95% complete but has **20+ broken features** preventing clinician use. These are NOT security issues (TIER 0-1 security is 100% complete), but **functionality gaps** that disable critical clinical workflows.

**Goal**: Fix all 20+ features such that:
- ✅ Every feature renders without errors
- ✅ Every feature loads correct data from database
- ✅ Every feature maintains existing security posture (CSRF, auth, rate limiting)
- ✅ Every feature passes corresponding test
- ✅ No existing functionality breaks
- ✅ Zero new security vulnerabilities introduced
- ✅ All changes fully documented

**Success Criteria**: 
- [ ] All 20+ features fixed and tested
- [ ] Zero breaking changes to existing endpoints
- [ ] Zero new security vulnerabilities
- [ ] 95%+ test coverage for fixed features
- [ ] All commits follow conventional commits standard
- [ ] Full documentation in DOCUMENTATION/8-PROGRESS/

---

## 🎯 THE 20+ BROKEN FEATURES (PRIORITY-ORDERED)

### CRITICAL - Block all clinician use (4 features)

1. **Dashboard Layout & Page Rendering** ⚠️ BLOCKER
   - **Problem**: Dashboard HTML structure is broken, tabs don't render
   - **Current State**: Frontend shows blank page or broken layout for clinician view
   - **Expected Behavior**: Clean tabbed interface with 8 tabs (Summary, Patients, Messages, Charts, Profile, Alerts, Appointments, Settings)
   - **Location**: `templates/index.html` (lines ~1000-1200, clinician dashboard section)
   - **Fix Approach**: Verify tab structure HTML exists and is properly styled, ensure CSS for `.clinician-dashboard` and `.dashboard-tab` exists and is not hidden
   - **Test**: Dashboard page loads, all 8 tabs visible, clicking tabs switches content

2. **Patient List (Assigned Clinicians Only)** ⚠️ BLOCKER
   - **Problem**: /api/clinician/patients endpoint returns empty or doesn't exist
   - **Current State**: Clinician cannot see list of assigned patients
   - **Expected Behavior**: Shows all patients assigned to this clinician with last session date, current risk level, next appointment
   - **Database Query**: `SELECT p.username, p.first_name, p.last_name, p.email, (SELECT MAX(date) FROM chat_history WHERE username=p.username) as last_session, (SELECT risk_level FROM risk_assessments WHERE username=p.username ORDER BY date DESC LIMIT 1) as current_risk FROM users p INNER JOIN clinician_patients cp ON p.username = cp.patient_username WHERE cp.clinician_username = %s ORDER BY p.first_name`
   - **API Endpoint**: `@app.route('/api/clinician/patients', methods=['GET'])`
     - **Auth**: Verify user has `role='clinician'`
     - **Response**: `{'patients': [{'username': '', 'first_name': '', 'last_name': '', 'email': '', 'last_session': '', 'risk_level': ''}, ...], 'count': N}`
   - **Frontend**: Populate `.patient-list` div with HTML: `<tr><td>name</td><td>last_session</td><td><span class="risk-{level}">{level}</span></td><td><button onclick="selectPatient('...')">View</button></td></tr>`
   - **Test**: Login as clinician, call GET /api/clinician/patients, verify returns 2-3 test patients with all fields populated

3. **Clinician Message Tab (Fix Dual Tab Bug)** ⚠️ BLOCKER
   - **Problem**: Frontend has TWO message tabs (therapist chat + clinician messages), should only have ONE clinician-specific tab
   - **Current State**: User sees "AI Therapist Chat" tab AND "Messages" tab, causing confusion and routing issues
   - **Expected Behavior**: Single "Messages" tab in clinician dashboard shows:
     - All unread messages from patients at top
     - Ability to reply to patient messages
     - Show message thread with timestamps and read status
   - **Location**: `templates/index.html` (search for duplicate `.therapist-chat` and `.messages` sections in clinician dashboard HTML)
   - **Fix Approach**: 
     1. REMOVE the `.therapist-chat` tab from clinician view (only patient view has AI therapist)
     2. KEEP the `.messages` tab for clinician-patient communication
     3. Ensure clinician messages endpoint routes to `/api/clinician/messages` NOT `/api/therapy/message`
   - **Test**: Login as clinician, verify only 1 "Messages" tab exists, send message to patient, verify message appears

4. **Clinician Summary/Overview Card** ⚠️ BLOCKER
   - **Problem**: /api/clinician/summary endpoint missing or returns incomplete data
   - **Current State**: Dashboard shows "No Data" or blank summary card
   - **Expected Behavior**: Shows clinician's workload summary:
     - Total patients assigned
     - Patients in crisis (risk_level='critical')
     - Total sessions this week
     - Upcoming appointments today
     - Unread messages count
   - **API Endpoint**: `@app.route('/api/clinician/summary', methods=['GET'])`
     - **Auth**: Verify `role='clinician'`
     - **Response**: `{'total_patients': N, 'critical_patients': N, 'sessions_this_week': N, 'appointments_today': N, 'unread_messages': N}`
     - **Database Queries**:
       ```sql
       SELECT COUNT(*) FROM clinician_patients WHERE clinician_username=%s  -- total_patients
       SELECT COUNT(*) FROM risk_assessments ra INNER JOIN clinician_patients cp ON ra.username=cp.patient_username WHERE cp.clinician_username=%s AND ra.risk_level='critical' AND ra.date >= NOW() - INTERVAL '7 days'  -- critical_patients
       SELECT COUNT(*) FROM chat_history ch INNER JOIN clinician_patients cp ON ch.username=cp.patient_username WHERE cp.clinician_username=%s AND ch.date >= DATE_TRUNC('week', NOW()) AND ch.role='assistant'  -- sessions_this_week
       SELECT COUNT(*) FROM appointments WHERE clinician_username=%s AND appointment_date=CURRENT_DATE AND status='scheduled'  -- appointments_today
       SELECT COUNT(*) FROM messages WHERE recipient_username=%s AND is_read=FALSE  -- unread_messages
       ```
   - **Test**: Login as clinician, GET /api/clinician/summary, verify all 5 fields return positive integers

### HIGH PRIORITY - Prevent clinician dashboard use (8 features)

5. **Patient Profile Tab** ⏳
   - **Problem**: Profile tab shows no data or incomplete patient info
   - **Current State**: Blank or shows only name, missing all medical context
   - **Expected Behavior**: Shows selected patient's:
     - Full name, email, phone, date of birth, gender
     - Current risk level + last assessment date
     - Assigned therapist name
     - Number of sessions completed
     - Current treatment goals (from therapy_goals table)
     - Recent mood log entries (last 7 days)
   - **API Endpoint**: `@app.route('/api/clinician/patient/<username>', methods=['GET'])`
     - **Auth**: Verify clinician is assigned to this patient via `clinician_patients` table
     - **Response**: `{'username': '', 'first_name': '', 'email': '', 'phone': '', 'dob': '', 'gender': '', 'risk_level': '', 'risk_date': '', 'sessions_count': N, 'treatment_goals': [...], 'recent_moods': [...]}`
   - **Test**: Login as clinician, select a patient, profile tab loads with all fields populated

6. **Charts/Analytics Tab** ⏳
   - **Problem**: Charts tab renders but shows no data, charts are blank
   - **Current State**: Chart containers exist but data doesn't load, axis labels show but no bars/lines
   - **Expected Behavior**: Displays patient's mood trends over 30 days:
     - Line chart: Daily mood scores (1-10) over last 30 days
     - Bar chart: Weekly activity count (hours of wellness activities)
     - Progress meter: Current risk level with 30-day trend
   - **API Endpoint**: `@app.route('/api/clinician/patient/<username>/analytics', methods=['GET'])`
     - **Auth**: Verify clinician assigned to patient
     - **Response**: `{'mood_data': [{'date': '2026-02-11', 'mood': 7}, ...], 'activity_data': [{'week': 'W1', 'hours': 5}, ...], 'risk_trend': 'stable|improving|worsening'}`
     - **Database**: Query `mood_logs` and `activity_logs` for username, aggregate by day/week
   - **Frontend**: Use existing chart library (Chart.js or similar) to render line+bar charts
   - **Test**: Login as clinician, navigate to patient profile, charts tab shows 30 data points + trend

7. **Mood Logs View (Clinician Perspective)** ⏳
   - **Problem**: Mood logs tab shows no entries or "No Data"
   - **Current State**: Query not running or table returns empty
   - **Expected Behavior**: Lists all mood entries for selected patient:
     - Date, mood score (1-10), energy level, notes
     - Sortable by date (newest first)
     - Filterable by date range
     - Shows weekly average mood at bottom
   - **API Endpoint**: `@app.route('/api/clinician/patient/<username>/mood-logs', methods=['GET'])`
     - **Query Params**: `?start_date=2026-01-11&end_date=2026-02-11` (optional)
     - **Response**: `{'logs': [{'date': '2026-02-11', 'mood': 7, 'energy': 8, 'notes': '...'}, ...], 'week_avg': 6.5}`
     - **Database**: `SELECT date, mood_score, energy_level, notes FROM mood_logs WHERE username=%s ORDER BY date DESC`
   - **Test**: Login as clinician, select patient, mood logs tab shows 5-10 entries with dates

8. **Therapy Assessment Results** ⏳
   - **Problem**: Assessments tab blank, no PHQ-9/GAD-7 results visible
   - **Current State**: Endpoint missing or returns no data
   - **Expected Behavior**: Shows patient's clinical assessment scores:
     - PHQ-9 score (depression assessment): 0-27 range with interpretation
     - GAD-7 score (anxiety assessment): 0-21 range with interpretation
     - Date administered
     - Treatment recommendations based on score
   - **API Endpoint**: `@app.route('/api/clinician/patient/<username>/assessments', methods=['GET'])`
     - **Response**: `{'phq9': {'score': 15, 'interpretation': 'moderate', 'date': '2026-02-10'}, 'gad7': {'score': 12, 'interpretation': 'moderate', 'date': '2026-02-10'}}`
     - **Database**: Query `clinical_scales` table for username
   - **Test**: Login as clinician, select patient, assessments show PHQ-9 and GAD-7 scores

9. **Therapy History / Session Notes** ⏳
   - **Problem**: History tab empty or shows wrong data
   - **Current State**: Session notes not loading or endpoint returns empty array
   - **Expected Behavior**: Lists all therapy sessions for patient:
     - Session date, duration, notes from clinician, patient session mood (before/after)
     - Filterable by date range
     - Shows total session count
   - **API Endpoint**: `@app.route('/api/clinician/patient/<username>/sessions', methods=['GET'])`
     - **Response**: `{'sessions': [{'date': '2026-02-10', 'duration': 45, 'notes': 'Discussed anxiety...', 'mood_before': 5, 'mood_after': 7}, ...], 'total': N}`
     - **Database**: Query `therapy_notes` table for username, ordered by date DESC
   - **Test**: Login as clinician, select patient, history shows 3+ session entries

10. **Risk Alerts Tab** ⏳
    - **Problem**: Alerts tab shows no critical alerts or risk indicators
    - **Current State**: Alert data not loading, no visual indicators for crisis situations
    - **Expected Behavior**: Shows all risk-related alerts for assigned patients:
      - List of patients currently in HIGH/CRITICAL risk
      - Recent risk assessments (last 7 days)
      - Keyword triggers detected in chat (if safety_monitor enabled)
      - Color-coded by severity (red=critical, orange=high, yellow=moderate)
      - Ability to mark alert as "acknowledged"
    - **API Endpoint**: `@app.route('/api/clinician/risk-alerts', methods=['GET'])`
      - **Response**: `{'alerts': [{'patient_name': '', 'risk_level': 'critical', 'date': '', 'trigger': 'suicidal_ideation', 'acknowledged': false}, ...], 'total': N}`
      - **Database**: Query `risk_alerts` table where clinician_username matches assigned clinician, join with users for patient name
    - **Test**: Login as clinician, risk alerts tab shows 2-5 alerts with different severity levels

11. **Appointment Booking System** ⏳
    - **Problem**: Appointment booking disabled or non-functional
    - **Current State**: Button shows but clicking does nothing, or page errors
    - **Expected Behavior**: Clinician can schedule/view/modify appointments with patients:
      - View upcoming appointments for patient
      - Schedule new appointment (date/time picker)
      - Cancel/reschedule existing appointment
      - Send appointment reminder to patient
    - **API Endpoints**:
      - GET `/api/clinician/patient/<username>/appointments` → List appointments
      - POST `/api/clinician/patient/<username>/appointments` → Schedule new (body: `{date, time, duration, notes}`)
      - PUT `/api/clinician/appointments/<appointment_id>` → Reschedule
      - DELETE `/api/clinician/appointments/<appointment_id>` → Cancel
    - **Database**: `appointments` table (appointment_id, clinician_username, patient_username, appointment_date, appointment_time, duration, status, notes)
    - **Test**: Schedule appointment 7 days from now, verify appears in list, cancel it, verify deleted

12. **Write New Message to Patient** ⏳
    - **Problem**: Message input box doesn't send, or endpoint missing
    - **Current State**: Text input renders but send button does nothing or returns 404
    - **Expected Behavior**: Clinician can send secure message to patient (distinct from AI chat):
      - Text input for message body
      - Send button submits to /api/clinician/message
      - Message appears in conversation thread
      - Patient receives notification
      - Message marked as read when patient opens
    - **API Endpoint**: `@app.route('/api/clinician/message', methods=['POST'])`
      - **Body**: `{'recipient_username': 'patient123', 'message': '...'}`
      - **Auth**: Verify sender is clinician assigned to patient
      - **Response**: `{'success': true, 'message_id': N, 'timestamp': ''}`
      - **Database**: Insert into `messages` table (sender_username, recipient_username, message_text, timestamp, is_read)
      - **Notification**: Send email/notification to patient if configured
    - **Test**: Send message from clinician to patient, message appears in both users' message lists

### MEDIUM PRIORITY - Quality of life (5+ features)

13. **Wellness Ritual Tracking** ⏳
    - **Problem**: Wellness ritual display missing or incomplete
    - **Expected Behavior**: Shows patient's completed wellness rituals/habits for the week
    - **API**: `/api/clinician/patient/<username>/wellness-rituals`

14. **AI Clinician Summary** ⏳
    - **Problem**: AI-generated summary of patient progress not rendering
    - **Expected Behavior**: Uses TherapistAI to generate 1-paragraph clinical summary of patient's progress/insights
    - **API**: `@app.route('/api/clinician/patient/<username>/ai-summary', methods=['GET'])`
      - **Auth**: Clinician assigned to patient
      - **Logic**: Gather recent mood logs, assessments, session notes → pass to TherapistAI → return 1-paragraph summary
    - **Response**: `{'summary': 'Based on 4 sessions, patient shows improving mood trends...', 'generated_at': ''}`

15. **Patient Notes Editor** ⏳
    - **Problem**: Clinician cannot add/edit private notes about patient
    - **Expected Behavior**: Persistent text editor for clinician to store clinical observations
    - **API**: 
      - POST `/api/clinician/patient/<username>/notes` → `{'note': '...', 'category': 'observation|treatment_plan|progress'}`
      - GET → returns notes

16. **Settings Tab** ⏳
    - **Problem**: Settings tab missing or incomplete
    - **Expected Behavior**: Clinician can configure:
      - Default session duration
      - Preferred notification methods
      - Patient list sort preference (by name, risk, last session)
    - **API**: `/api/clinician/settings` (GET/PUT)

17-20+. **Minor UI Fixes**
    - Wellness ritual chart colors
    - Date picker accessibility
    - Mobile responsiveness for dashboard tabs
    - Print appointment/notes functionality

---

## 🏗️ IMPLEMENTATION FRAMEWORK

### CRITICAL PREREQUISITES (READ FIRST)

**You MUST understand these before starting:**

1. **Session & Auth Pattern** [see copilot-instructions.md line ~100]
   ```python
   # EVERY endpoint MUST verify session identity FIRST
   username = session.get('username')
   if not username:
       return jsonify({'error': 'Authentication required'}), 401
   
   # VERIFY clinician role for dashboard endpoints
   cur.execute('SELECT role FROM users WHERE username=%s', (username,))
   user = cur.fetchone()
   if user['role'] != 'clinician':
       return jsonify({'error': 'Clinician access required'}), 403
   ```

2. **CSRF Token Requirement** [line ~450-490 in api.py]
   ```python
   # POST/PUT/DELETE MUST validate X-CSRF-Token header
   if request.method in ['POST', 'PUT', 'DELETE']:
       token = request.headers.get('X-CSRF-Token')
       if not validate_csrf_token(token):
           return jsonify({'error': 'CSRF token invalid'}), 403
   ```

3. **Database Connection Pattern** [line 2183 in api.py]
   ```python
   # ALWAYS use PostgreSQL syntax (%s placeholders, NOT ?)
   try:
       conn = get_db_connection()
       cur = get_wrapped_cursor(conn)
       cur.execute('SELECT * FROM users WHERE username=%s', (username,))
       result = cur.fetchone()
       conn.commit()
       log_event(username, 'category', 'action', 'details')  # ALWAYS log
       return jsonify({'success': True}), 200
   except psycopg2.Error as e:
       conn.rollback()
       app.logger.error(f'DB error: {e}')
       return jsonify({'error': 'Operation failed'}), 500
   finally:
       conn.close()
   ```

4. **Input Validation** [line 219-300 in api.py]
   ```python
   # ALWAYS validate user input before DB operations
   text, error = InputValidator.validate_text(data.get('message'), max_length=10000)
   if error:
       return jsonify({'error': error}), 400
   ```

5. **Verify Clinician Assignment** (CRITICAL for dashboard endpoints)
   ```python
   # BEFORE accessing patient data, verify clinician is assigned
   cur.execute(
       'SELECT * FROM clinician_patients WHERE clinician_username=%s AND patient_username=%s',
       (username, selected_patient_username)
   )
   if not cur.fetchone():
       return jsonify({'error': 'Not assigned to this patient'}), 403
   ```

---

### STEP-BY-STEP IMPLEMENTATION APPROACH

**Phase 1: Identify Missing Endpoints (2-3 hours)**
1. Search api.py for each endpoint listed above
2. If endpoint missing → Create skeleton with auth + CSRF validation
3. If endpoint exists → Test it, identify why it fails
4. Document findings in IMPLEMENTATION_PROGRESS.md

**Phase 2: Fix Database Queries (4-5 hours)**
1. Verify each table exists in PostgreSQL (check init_db() at line 3571)
2. Write/test queries manually using test data
3. Verify queries return correct data structure
4. Test with 2-3 different patients to ensure no hardcoding

**Phase 3: Fix Frontend Integration (5-6 hours)**
1. Locate corresponding HTML sections in templates/index.html
2. Verify API calls use correct endpoint URLs
3. Verify fetch() includes X-CSRF-Token header
4. Verify data binding (populating HTML with API response)
5. Test end-to-end: Login as clinician → Navigate to feature → Verify renders

**Phase 4: Write Tests (4-5 hours)**
1. For each feature, create test in tests/test_clinician_dashboard.py
2. Test should:
   - Verify auth check (non-clinician gets 403)
   - Verify CSRF check (missing token gets 403)
   - Verify endpoint returns correct JSON schema
   - Verify data is correct (sample query result matches response)
   - Verify no SQL injection vulnerabilities
3. Run pytest to confirm all tests pass

**Phase 5: Integration Testing (2-3 hours)**
1. Create test clinician + test patients in test database
2. Login as clinician
3. Navigate through entire dashboard
4. Verify all 12 critical + high-priority features work end-to-end
5. Verify no error logs in healing_space.log
6. Check that existing features (mood logging, AI chat, etc.) still work

**Phase 6: Documentation (1-2 hours)**
1. Document each fix in DOCUMENTATION/8-PROGRESS/TIER-1.1-IMPLEMENTATION-LOG.md
2. Update Completion-Status.md with progress
3. Commit each fix with message: `fix: clinician-dashboard-[feature-name]`

---

## ⚙️ TECHNICAL SPECIFICATIONS

### Database Tables You'll Need

```sql
-- Verify these tables exist in PostgreSQL:

users (username, first_name, last_name, email, phone, date_of_birth, gender, role, password_hash, created_date)
clinician_patients (clinician_username, patient_username, assigned_date)
mood_logs (username, date, mood_score, energy_level, notes)
activity_logs (username, date, activity_type, duration_hours)
clinical_scales (username, assessment_type, score, date)  -- PHQ-9, GAD-7
therapy_notes (username, clinician_username, session_date, duration, notes, mood_before, mood_after)
appointments (appointment_id, clinician_username, patient_username, appointment_date, appointment_time, duration, status, notes)
messages (message_id, sender_username, recipient_username, message_text, timestamp, is_read)
risk_assessments (username, risk_level, date, assessment_method)
risk_alerts (alert_id, patient_username, clinician_username, risk_level, date, trigger_keyword, acknowledged)
therapy_goals (goal_id, username, goal_text, start_date, target_date, status)
```

Run this to verify all tables exist:
```python
cur.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public'
""")
tables = [row['table_name'] for row in cur.fetchall()]
print(tables)  # Should show all 11+ tables
```

### Response Schema Examples

**Patient List Response** (for testing):
```json
{
  "patients": [
    {
      "username": "alex_smith",
      "first_name": "Alex",
      "last_name": "Smith",
      "email": "alex@example.com",
      "last_session": "2026-02-10T14:30:00Z",
      "risk_level": "moderate"
    }
  ],
  "count": 1
}
```

**Clinician Summary Response**:
```json
{
  "total_patients": 5,
  "critical_patients": 1,
  "sessions_this_week": 8,
  "appointments_today": 2,
  "unread_messages": 3
}
```

**Patient Profile Response**:
```json
{
  "username": "alex_smith",
  "first_name": "Alex",
  "last_name": "Smith",
  "email": "alex@example.com",
  "phone": "+44 7700 000000",
  "dob": "1995-06-15",
  "gender": "Non-binary",
  "risk_level": "moderate",
  "risk_date": "2026-02-10",
  "sessions_count": 12,
  "treatment_goals": [
    {
      "goal_id": 1,
      "goal_text": "Reduce anxiety to 5/10",
      "status": "in_progress"
    }
  ],
  "recent_moods": [
    {
      "date": "2026-02-10",
      "mood": 6,
      "energy": 7
    }
  ]
}
```

---

## 🛡️ SECURITY GUARDRAILS

**DO NOT VIOLATE THESE:**

1. ✅ **Authentication**: Every endpoint must verify session username first
   - ❌ WRONG: `username = request.json.get('username')`
   - ✅ RIGHT: `username = session.get('username')`

2. ✅ **Role Verification**: Clinician-only endpoints must check `role='clinician'`
   - ❌ WRONG: Skip role check, assume all logged-in users are clinicians
   - ✅ RIGHT: `if user['role'] != 'clinician': return 403`

3. ✅ **Assignment Verification**: Clinician can only access assigned patients
   - ❌ WRONG: Allow clinician to see any patient's data
   - ✅ RIGHT: Check `clinician_patients` table before returning patient data

4. ✅ **CSRF Protection**: POST/PUT/DELETE must validate X-CSRF-Token
   - ❌ WRONG: Skip CSRF for clinician dashboard endpoints
   - ✅ RIGHT: All POST/PUT/DELETE validate token

5. ✅ **SQL Injection Prevention**: Always use %s placeholders
   - ❌ WRONG: `cur.execute(f"SELECT * FROM users WHERE username={username}")`
   - ✅ RIGHT: `cur.execute("SELECT * FROM users WHERE username=%s", (username,))`

6. ✅ **Input Validation**: Validate all user input
   - ❌ WRONG: Trust request data directly
   - ✅ RIGHT: Use `InputValidator.validate_text()` before DB operations

7. ✅ **Error Handling**: Never leak internal details in error responses
   - ❌ WRONG: `return jsonify({'error': f'Database error: {e}'}), 500`
   - ✅ RIGHT: Log error internally, return generic message to user

8. ✅ **Audit Logging**: Log all clinician actions
   - ❌ WRONG: Forget to call `log_event()`
   - ✅ RIGHT: `log_event(username, 'clinician_dashboard', 'viewed_patient', patient_username)`

---

## 📊 TESTING STRATEGY

### Unit Tests (For Each Endpoint)

Create `tests/test_clinician_dashboard.py`:

```python
def test_clinician_summary_requires_auth(client):
    """Unauthenticated request returns 401"""
    response = client.get('/api/clinician/summary')
    assert response.status_code == 401

def test_clinician_summary_requires_role(client, test_user):
    """Non-clinician cannot access clinician endpoints"""
    response = client.get('/api/clinician/summary', headers={"X-Session": test_user['session']})
    assert response.status_code == 403

def test_clinician_summary_returns_correct_schema(client, clinician_user):
    """Clinician can access summary with correct response schema"""
    response = client.get('/api/clinician/summary', headers={"X-Session": clinician_user['session']})
    assert response.status_code == 200
    data = response.json()
    assert 'total_patients' in data
    assert 'critical_patients' in data
    assert isinstance(data['total_patients'], int)

def test_clinician_patient_list_excludes_unassigned(client, clinician_user, other_patient):
    """Clinician cannot see unassigned patients"""
    response = client.get('/api/clinician/patients', headers={"X-Session": clinician_user['session']})
    data = response.json()
    usernames = [p['username'] for p in data['patients']]
    assert other_patient['username'] not in usernames
```

### Integration Tests

```python
def test_clinician_dashboard_workflow(client, clinician_user, patient_user):
    """Full clinician workflow: login → view summary → select patient → view profile"""
    # 1. Get clinician summary
    response = client.get('/api/clinician/summary', headers={...})
    assert response.status_code == 200
    
    # 2. Get patient list
    response = client.get('/api/clinician/patients', headers={...})
    assert len(response.json()['patients']) > 0
    
    # 3. Get patient profile
    response = client.get(f'/api/clinician/patient/{patient_user["username"]}', headers={...})
    assert response.status_code == 200
    
    # 4. Get patient analytics
    response = client.get(f'/api/clinician/patient/{patient_user["username"]}/analytics', headers={...})
    assert response.status_code == 200
    assert 'mood_data' in response.json()
```

### End-to-End Tests

```python
def test_clinician_e2e_dashboard_load(selenium_browser, clinician_credentials):
    """Clinician can load and navigate full dashboard without errors"""
    selenium_browser.login(clinician_credentials)
    
    # Load dashboard
    selenium_browser.get('/dashboard')
    assert selenium_browser.find_element_by_id('clinician-dashboard')
    
    # All 8 tabs should be visible
    tabs = selenium_browser.find_elements_by_class_name('dashboard-tab')
    assert len(tabs) == 8
    
    # Click each tab and verify content loads
    for tab in tabs:
        tab.click()
        # Verify no console errors
        logs = selenium_browser.get_log('browser')
        errors = [l for l in logs if l['level'] == 'SEVERE']
        assert len(errors) == 0, f"Console errors in {tab.text}: {errors}"
```

### Test Data Setup

In `conftest.py`, create fixtures:

```python
@pytest.fixture
def clinician_user(db_connection):
    """Create test clinician with assigned patients"""
    cur = db_connection.cursor()
    cur.execute("""
        INSERT INTO users (username, first_name, role, password_hash, created_date)
        VALUES ('dr_johnson', 'Dr. Johnson', 'clinician', %s, NOW())
    """, (hash_password('password'),))
    db_connection.commit()
    
    # Assign 2 test patients
    cur.execute("""
        INSERT INTO clinician_patients (clinician_username, patient_username)
        VALUES ('dr_johnson', 'patient1'), ('dr_johnson', 'patient2')
    """)
    db_connection.commit()
    return {'username': 'dr_johnson', 'password': 'password'}
```

---

## 📝 GIT COMMIT STRATEGY

Each fix should be a **separate, atomic commit** following conventional commits:

```bash
git commit -m "fix: clinician-summary-endpoint-missing-critical-patients-count"
git commit -m "fix: clinician-patient-list-returns-empty-array"
git commit -m "fix: clinician-dashboard-remove-duplicate-messages-tab"
git commit -m "fix: clinician-profile-tab-missing-treatment-goals"
git commit -m "fix: clinician-charts-analytics-endpoint-returns-no-data"
...
```

Each commit message should:
1. Start with `fix:` or `test:` or `docs:`
2. Describe the broken feature
3. Be concise but clear

---

## 📚 DOCUMENTATION REQUIREMENTS

After each feature is fixed, document it:

### File: DOCUMENTATION/8-PROGRESS/TIER-1.1-IMPLEMENTATION-LOG.md

```markdown
# TIER 1.1 Implementation Log

## Feature #1: Dashboard Layout & Page Rendering
- **Status**: ✅ FIXED (2 hours)
- **Problem**: HTML structure broken, tabs not rendering
- **Solution**: Verified tab HTML exists, fixed CSS display property
- **Endpoint**: N/A (frontend-only fix)
- **Test**: Dashboard loads, all 8 tabs visible
- **Commit**: abc1234
- **Notes**: Required CSS fix for `.clinician-dashboard { display: block }` (was `display: none`)

## Feature #2: Patient List
- **Status**: ✅ FIXED (3 hours)
- **Problem**: Endpoint missing or returns empty
- **Solution**: Created GET /api/clinician/patients endpoint with proper query
- **Endpoint**: GET /api/clinician/patients
- **Database**: Joins users + clinician_patients tables
- **Test**: test_clinician_patient_list (3 tests)
- **Commit**: def5678
```

### Update: DOCUMENTATION/8-PROGRESS/Completion-Status.md

After each feature, update the table:

```markdown
| Item | Description | Status | Hours | Commit |
|------|-------------|--------|-------|--------|
| **1.1** | Clinician Dashboard (20+ features) | ⏳ IN PROGRESS | 20-25 | See log |
| 1.1.1 | Dashboard Layout | ✅ FIXED | 2 | abc1234 |
| 1.1.2 | Patient List | ✅ FIXED | 3 | def5678 |
```

---

## 🚀 SUCCESS CRITERIA (FINAL ACCEPTANCE)

This implementation is **COMPLETE** when:

- [ ] All 12 CRITICAL + HIGH priority features are fixed
- [ ] Each feature has passing test coverage
- [ ] Dashboard loads without errors
- [ ] All 8 tabs render correctly
- [ ] Clinician can view assigned patients
- [ ] Clinician can view patient data (profile, mood logs, assessments, etc.)
- [ ] Clinician can schedule/view appointments
- [ ] Clinician can send messages to patients
- [ ] Risk alerts display correctly
- [ ] No existing functionality broken (run full test suite)
- [ ] Zero new security vulnerabilities
- [ ] All commits follow conventional commits format
- [ ] TIER-1.1-IMPLEMENTATION-LOG.md documents all fixes
- [ ] Completion-Status.md shows TIER 1.1 ✅ COMPLETE
- [ ] No stray documentation files (all docs in DOCUMENTATION/)
- [ ] Code review passed (no hardcoding, proper auth checks, etc.)

---

## ❓ COMMON GOTCHAS & HOW TO AVOID THEM

1. **Forgetting Auth Check**: Dashboard endpoint accessible to non-clinicians
   - ✅ VERIFY: Every endpoint has `if role != 'clinician': return 403`

2. **Forgot Assignment Check**: Clinician can see all patients, not just assigned ones
   - ✅ VERIFY: Query filters by `clinician_patients` table join

3. **Empty Response**: Endpoint returns `{'patients': []}` instead of data
   - ✅ DEBUG: Check database has test data, run query manually first

4. **XSS from Patient Names**: Patient first_name rendered with innerHTML
   - ✅ VERIFY: Use `textContent` not `innerHTML` for user data

5. **CSRF Validation Missing**: POST endpoints fail with 403
   - ✅ VERIFY: All POST/PUT/DELETE endpoints validate X-CSRF-Token header

6. **SQL Syntax Error**: Using `?` placeholder instead of `%s`
   - ✅ VERIFY: All queries use `%s` (PostgreSQL), not `?` (SQLite)

7. **Forgot Connection Close**: Connection leak causes pool exhaustion
   - ✅ VERIFY: All endpoints have `finally: conn.close()`

8. **Stale Test Data**: Tests pass locally but fail in CI
   - ✅ FIX: Use fixtures in conftest.py, clean up after each test

---

## 🎯 FINAL NOTES

This prompt is designed to be **self-contained** and **executable** without external context. It includes:

✅ Complete problem specification (20+ features)  
✅ Priority ordering (critical → medium)  
✅ Technical implementation details (endpoints, responses, queries)  
✅ Security guardrails (auth, CSRF, injection prevention)  
✅ Testing strategy (unit, integration, E2E)  
✅ Documentation requirements  
✅ Success criteria  
✅ Common gotchas  

**You can paste this entire prompt into Claude and receive a complete, working implementation.**

---

**Version**: 1.0 (February 11, 2026)  
**Prepared by**: GitHub Copilot  
**Project**: Healing Space UK - TIER 1.1 Implementation  
**Target**: Production-ready clinician dashboard
