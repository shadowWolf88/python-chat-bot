# TIER 1.1: Implementation Roadmap

**Target Completion**: February 17, 2026  
**Total Effort**: 20-25 hours  
**Scope**: 20+ broken clinician dashboard features

---

## 📅 SPRINT BREAKDOWN

### SPRINT 1: CRITICAL BLOCKERS (8-10 hours)

#### Sprint 1a: Backend - Create 4 Critical Endpoints (6-8 hours)

**1. GET `/api/clinician/summary`** (2-3 hours)
```python
def get_clinician_summary():
    """Dashboard overview: patient count, risk alerts, sessions, appointments, messages"""
    # Requires: Session auth, Role check (clinician)
    # Database:
    # - COUNT FROM clinician_patients WHERE clinician_username=%s
    # - COUNT FROM risk_assessments WHERE ... AND risk_level='critical'
    # - COUNT FROM chat_history WHERE clinician_username AND date > 7_days_ago
    # - COUNT FROM appointments WHERE clinician_username AND date = today
    # - COUNT FROM messages WHERE recipient_username AND is_read=false
    # Response: {total_patients, critical_patients, sessions_this_week, appointments_today, unread_messages}
    # Security: CSRF token required
    # Logging: log_event(username, 'clinician', 'view_summary', '')
```

**2. GET `/api/clinician/patient/<username>/mood-logs`** (2-3 hours)
```python
def get_patient_mood_logs(username):
    """Get 30-day mood trend for patient"""
    # Requires: Session auth, Role check (clinician), Assignment check
    # Database:
    # - SELECT * FROM mood_logs WHERE patient_username=%s ORDER BY date DESC LIMIT 30
    # - Calculate week_avg, trend (up/down/stable)
    # Response: {logs: [{date, mood, note}], week_avg, trend}
    # Pagination: Limit 30, offset parameter
    # Security: Verify clinician_patients association
    # Logging: log_event(username, 'clinician', 'view_mood_logs', f'patient={username}')
```

**3. GET `/api/clinician/patient/<username>/analytics`** (2-3 hours)
```python
def get_patient_analytics(username):
    """Mood/activity trends for charts"""
    # Requires: Session auth, Role check, Assignment check
    # Database:
    # - Aggregate mood_logs by week (SUM/AVG/COUNT)
    # - Aggregate activity_logs by week (duration, type)
    # - Risk trend (last 30 days of risk_assessments)
    # Response: {mood_data: [{week, avg, count}], activity_data: [{week, duration, type}], risk_trend}
    # Charts: Support 7-day, 30-day, 90-day views
    # Security: Same assignment check
    # Logging: log_event(...)
```

**4. GET `/api/clinician/patient/<username>/assessments`** (2-3 hours)
```python
def get_patient_assessments(username):
    """Latest PHQ-9 & GAD-7 scores"""
    # Requires: Session auth, Role check, Assignment check
    # Database:
    # - SELECT * FROM clinical_scales WHERE patient_username AND assessment_type IN ('PHQ-9', 'GAD-7')
    # Response: {phq9: {score, interpretation, date}, gad7: {score, interpretation, date}}
    # Interpretation: Score ranges (none/mild/moderate/severe/very_severe)
    # Security: Assignment check
    # Logging: log_event(...)
```

#### Sprint 1b: Frontend - Fix Dashboard Layout (2-3 hours)

**1. Fix Dashboard Rendering** (1-2 hours)
```html
<!-- In templates/index.html, clinician section -->
<!-- Ensure all divs are visible (remove display: none on dashboard-layout) -->
<!-- Add CSS: .dashboard-layout { display: grid; } (if hidden) -->
<!-- Check: All 8 tabs visible (Summary, Patients, Patient Details, Messages, etc.) -->
```

**2. Remove Duplicate Message Tab** (30 mins)
```html
<!-- Delete .therapist-chat tab from clinician view (keep only .messages) -->
<!-- Remove all event listeners for deleted tab -->
<!-- Test: Only 1 message tab visible -->
```

---

### SPRINT 2: HIGH PRIORITY (12-15 hours)

#### Sprint 2a: Backend - Create 6 High-Priority Endpoints (8-10 hours)

**5. GET `/api/clinician/patient/<username>/sessions`** (2-3 hours)
```python
def get_patient_sessions(username):
    """Therapy session history with summaries"""
    # Database: SELECT * FROM chat_history WHERE patient_username ORDER BY date DESC LIMIT 50
    # Add: session_id, duration, topic (inferred from messages), summary (AI-generated)
    # Pagination: Support offset/limit
    # Response: {sessions: [{id, date, duration, topic, summary}]}
```

**6. GET `/api/clinician/risk-alerts`** (2-3 hours)
```python
def get_risk_alerts():
    """All risk alerts for clinician's patients"""
    # Database: SELECT * FROM risk_alerts WHERE clinician_username ORDER BY date DESC
    # Filter: By patient, by severity, by status (open/closed)
    # Response: {alerts: [{id, patient, severity, message, date, status}]}
```

**7-8. GET/POST/PUT/DELETE `/api/clinician/patient/<username>/appointments`** (4-5 hours)
```python
def manage_appointments(username):
    """Create/read/update/delete appointments"""
    # GET: Retrieve all appointments for patient
    # POST: Create new appointment (requires: date, time, type, notes)
    # PUT: Update appointment details
    # DELETE: Cancel appointment
    # Database: appointments table
    # Response: {appointments: [{id, date, time, type, notes, patient, clinician}]}
```

**9. POST `/api/clinician/message`** (2-3 hours)
```python
def send_message():
    """Send message to patient"""
    # Requires: recipient_username, message_text
    # Database: INSERT INTO messages
    # Response: {id, timestamp, status}
    # Security: CSRF token, validate recipient
```

#### Sprint 2b: Frontend - Implement Tab Navigation (2-3 hours)

**1. Tab Click Handlers** (1-2 hours)
```javascript
// In static/js/main.js or templates/index.html
document.querySelectorAll('.tab-button').forEach(btn => {
    btn.addEventListener('click', (e) => {
        // Hide all content divs
        // Show selected content div
        // Update active tab styling
    });
});
```

**2. Content Visibility Toggle** (1 hour)
```javascript
// Ensure .tab-content divs show/hide correctly
// Test: Click each tab, verify content appears
```

---

### SPRINT 3: MEDIUM PRIORITY (5-8 hours)

**10. GET `/api/clinician/patient/<username>/wellness-rituals`** (1-2 hours)
```python
def get_wellness_rituals(username):
    """Patient's wellness tracking/goals"""
    # Database: coping_cards, goals, values_clarification
    # Response: {rituals: [{id, type, description, frequency}]}
```

**11. GET/PUT `/api/clinician/settings`** (2-3 hours)
```python
def manage_settings():
    """Clinician notification & display preferences"""
    # Database: clinician_settings table (may need to create)
    # GET: Retrieve settings
    # PUT: Update settings
    # Response: {notifications_enabled, alert_frequency, display_mode}
```

**12. Fix Existing Endpoints** (2-3 hours)
```python
# GET /api/professional/patients
# - Add: first_name, last_name, email, last_session, risk_level
# - Verify: Auth check, role check

# GET /api/professional/patient/<username>
# - Add: treatment_goals, recent_sessions
# - Verify: Assignment check

# GET/POST /api/appointments
# - Use session auth instead of query params
# - Fix: Response schema
```

---

## 🛠️ IMPLEMENTATION TEMPLATES

### Endpoint Template (CRITICAL for all endpoints)
```python
@app.route('/api/clinician/summary', methods=['GET'])
def get_clinician_summary():
    # 1. AUTH CHECK
    username = session.get('username')
    if not username:
        return jsonify({'error': 'Authentication required'}), 401
    
    # 2. ROLE CHECK
    if session.get('role') != 'clinician':
        return jsonify({'error': 'Clinician access required'}), 403
    
    # 3. DATABASE QUERY
    try:
        conn = get_db_connection()
        cur = get_wrapped_cursor(conn)
        
        # Build response from multiple queries
        cur.execute('SELECT COUNT(*) as count FROM clinician_patients WHERE clinician_username=%s', (username,))
        total_patients = cur.fetchone()['count']
        
        # More queries...
        
        # MUST COMMIT for consistency
        conn.commit()
        
        # 4. LOGGING
        log_event(username, 'clinician', 'view_summary', '')
        
        # 5. RESPONSE
        return jsonify({
            'success': True,
            'total_patients': total_patients,
            # ... more fields
        }), 200
        
    except psycopg2.Error as e:
        conn.rollback()
        app.logger.error(f'DB error in get_clinician_summary: {e}')
        return jsonify({'error': 'Database operation failed'}), 500
    finally:
        conn.close()
```

### CSRF-Protected Endpoint Template
```python
@app.route('/api/clinician/patient/<username>/appointments', methods=['POST'])
def create_appointment(username):
    # 1-2: Auth + Role checks (same as above)
    clinician = session.get('username')
    if not clinician or session.get('role') != 'clinician':
        return jsonify({'error': 'Authentication required'}), 401
    
    # 3. CSRF VALIDATION
    token = request.headers.get('X-CSRF-Token')
    if not token or not validate_csrf_token(token):
        return jsonify({'error': 'CSRF token invalid'}), 403
    
    # 4. INPUT VALIDATION
    data = request.json or {}
    date, error = InputValidator.validate_date(data.get('date'))
    if error:
        return jsonify({'error': error}), 400
    
    # 5. ASSIGNMENT CHECK (Verify clinician manages this patient)
    try:
        conn = get_db_connection()
        cur = get_wrapped_cursor(conn)
        cur.execute(
            'SELECT 1 FROM clinician_patients WHERE clinician_username=%s AND patient_username=%s',
            (clinician, username)
        )
        if not cur.fetchone():
            conn.close()
            return jsonify({'error': 'Patient not assigned'}), 403
        
        # 6. DATABASE INSERT
        cur.execute(
            'INSERT INTO appointments (clinician_username, patient_username, date, time, notes) VALUES (%s, %s, %s, %s, %s)',
            (clinician, username, date, data.get('time'), data.get('notes', ''))
        )
        conn.commit()
        
        # 7. LOGGING
        log_event(clinician, 'clinician', 'create_appointment', f'patient={username}')
        
        # 8. RESPONSE
        return jsonify({'success': True, 'appointment_id': cur.lastrowid}), 201
        
    except psycopg2.Error as e:
        conn.rollback()
        app.logger.error(f'DB error: {e}')
        return jsonify({'error': 'Operation failed'}), 500
    finally:
        conn.close()
```

---

## ⏱️ TIMELINE

| Phase | Duration | Target Dates | Status |
|-------|----------|-------------|--------|
| 1: Endpoint Audit | 4 hours | Feb 11 | ✅ DONE |
| 2a: Critical Endpoints | 6-8 hours | Feb 12-13 | ⏳ TODO |
| 2b: Dashboard UI | 2-3 hours | Feb 13 | ⏳ TODO |
| 3: High-Priority | 8-10 hours | Feb 14-15 | ⏳ TODO |
| 4: Medium-Priority | 5-8 hours | Feb 15-16 | ⏳ TODO |
| 5: Testing | 4-5 hours | Feb 16-17 | ⏳ TODO |
| 6: Documentation | 1-2 hours | Feb 17 | ⏳ TODO |
| **TOTAL** | **20-25 hours** | **Feb 17** | ⏳ IN PROGRESS |

---

## 🚀 EXECUTION OPTIONS

### Option A: Fast Track (Implement all at once - 20-25 hours)
1. Use this roadmap as spec
2. Implement all endpoints following templates
3. Test each endpoint
4. Deploy

### Option B: Sprint-Based (Implement sprint-by-sprint - same duration, more checkpoints)
1. Complete Sprint 1 CRITICAL endpoints first (8-10 hours)
2. Deploy & test
3. Complete Sprint 2 HIGH-priority (12-15 hours)
4. Deploy & test
5. Complete Sprint 3 MEDIUM-priority (5-8 hours)

### Option C: Reference Implementation (Use comprehensive prompt directly)
1. Copy TIER-1.1-COMPREHENSIVE-PROMPT.md
2. Paste to Claude with instruction: "Implement all 20 features from this spec"
3. Apply results to codebase
4. Test and deploy

---

**Next Step**: Begin SPRINT 1a - Create critical endpoints  
**Owner**: Implementation agent  
**Review**: After each sprint completion

