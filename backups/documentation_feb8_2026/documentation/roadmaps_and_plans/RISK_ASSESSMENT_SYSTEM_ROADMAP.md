
## IMPLEMENTATION STATUS: COMPLETE (v8.2 Feb 7, 2026)

All 5 phases implemented. See api.py and templates/index.html for code.

You are implementing a comprehensive Risk Assessment & Patient Safety System for Healing Space UK, an NHS-aligned mental health web application built with Flask (Python) and PostgreSQL. You are the best developer in the world, i want you to complete the following task with world class results, without breaking anything that already exists on the project. This needs to be implemeneted in full detail, and push to github for me to test live on the railway site.

### Project Context
- **Backend:** Flask API (`api.py`) with PostgreSQL database
- **Frontend:** Single-page app in `templates/index.html`
- **AI Provider:** Groq API using `llama-3.3-70b-versatile` model
- **Authentication:** Session-based with CSRF protection and 2FA PIN
- **Existing Features:** Mood logging, CBT tools, AI therapy chat, pet game, clinician dashboard, community features
- **Database connections:** `get_db_connection()` for main DB, `get_pet_db_connection()` for pet DB, always use `get_wrapped_cursor(conn)` for cursors

### Critical Implementation Rules
1. Always use `get_wrapped_cursor(conn)` - NEVER use `conn.cursor()` directly
2. Use `ON CONFLICT ... DO UPDATE` for all upserts (PostgreSQL)
3. Use `LEAST()`/`GREATEST()` instead of `MIN()`/`MAX()` for value clamping in UPDATE statements
4. Column in mood_logs is `entrestamp` (NOT `entry_timestamp`)
5. All POST/PUT/DELETE endpoints need CSRF handling
6. Protect all clinician/developer endpoints with role verification
7. Use `handle_exception(e, endpoint_name)` for error handling
8. Use `log_event(username, category, action, details)` for audit logging

---

## PHASE 1: Database Schema & Risk Scoring Engine

### Prompt for Phase 1

```
You are implementing Phase 1 of the Risk Assessment System for Healing Space UK.

CONTEXT: Read api.py to understand the existing codebase patterns. The app uses Flask + PostgreSQL with get_db_connection() and get_wrapped_cursor(conn).

TASK: Create the database tables and core risk scoring engine.

### 1.1 Database Tables

Create these tables in the production database (add to schema_therapist_app_postgres.sql and create a migration):

```sql
-- Risk assessment scores calculated by the system
CREATE TABLE risk_assessments (
    id SERIAL PRIMARY KEY,
    patient_username TEXT NOT NULL,
    risk_score INTEGER NOT NULL DEFAULT 0,        -- 0-100 composite score
    risk_level TEXT NOT NULL DEFAULT 'low',        -- critical/high/moderate/low
    suicide_risk INTEGER DEFAULT 0,                -- 0-100 sub-score
    self_harm_risk INTEGER DEFAULT 0,              -- 0-100 sub-score
    crisis_risk INTEGER DEFAULT 0,                 -- 0-100 sub-score
    deterioration_risk INTEGER DEFAULT 0,          -- 0-100 sub-score
    contributing_factors TEXT,                      -- JSON array of factors
    ai_analysis TEXT,                               -- AI-generated analysis
    clinical_data_score INTEGER DEFAULT 0,         -- Score from PHQ-9, GAD-7 etc
    behavioral_score INTEGER DEFAULT 0,            -- Score from engagement patterns
    conversational_score INTEGER DEFAULT 0,        -- Score from AI chat analysis
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assessed_by TEXT DEFAULT 'system',             -- 'system' or clinician username
    CONSTRAINT valid_risk_level CHECK (risk_level IN ('critical', 'high', 'moderate', 'low'))
);
CREATE INDEX idx_risk_patient ON risk_assessments(patient_username);
CREATE INDEX idx_risk_level ON risk_assessments(risk_level);
CREATE INDEX idx_risk_date ON risk_assessments(assessed_at);

-- Real-time risk alerts for clinicians
CREATE TABLE risk_alerts (
    id SERIAL PRIMARY KEY,
    patient_username TEXT NOT NULL,
    clinician_username TEXT,                        -- Assigned clinician
    alert_type TEXT NOT NULL,                       -- suicide_risk/self_harm/crisis/deterioration/keyword_flag
    severity TEXT NOT NULL DEFAULT 'moderate',      -- critical/high/moderate/low
    title TEXT NOT NULL,                            -- Short alert title
    details TEXT,                                   -- Detailed description
    source TEXT,                                    -- chat/mood/assessment/behavioral/manual
    ai_confidence REAL,                             -- 0.0-1.0 AI confidence in flag
    risk_score_at_time INTEGER,                     -- Risk score when alert was created
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by TEXT,
    acknowledged_at TIMESTAMP,
    action_taken TEXT,                              -- What the clinician did
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_severity CHECK (severity IN ('critical', 'high', 'moderate', 'low'))
);
CREATE INDEX idx_risk_alerts_patient ON risk_alerts(patient_username);
CREATE INDEX idx_risk_alerts_unacknowledged ON risk_alerts(acknowledged) WHERE acknowledged = FALSE;
CREATE INDEX idx_risk_alerts_clinician ON risk_alerts(clinician_username);

-- Risk keywords and phrases to monitor in conversations
CREATE TABLE risk_keywords (
    id SERIAL PRIMARY KEY,
    keyword TEXT NOT NULL,
    category TEXT NOT NULL,                         -- suicide/self_harm/crisis/substance/violence
    severity_weight INTEGER DEFAULT 5,              -- 1-10 how much this contributes to risk
    is_active BOOLEAN DEFAULT TRUE,
    added_by TEXT DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Patient crisis contacts (NHS requirement)
CREATE TABLE crisis_contacts (
    id SERIAL PRIMARY KEY,
    patient_username TEXT NOT NULL,
    contact_name TEXT NOT NULL,
    relationship TEXT,
    phone TEXT,
    email TEXT,
    is_primary BOOLEAN DEFAULT FALSE,
    is_professional BOOLEAN DEFAULT FALSE,          -- GP, psychiatrist etc
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_crisis_contacts_patient ON crisis_contacts(patient_username);

-- Risk review log (clinician reviews of risk assessments)
CREATE TABLE risk_reviews (
    id SERIAL PRIMARY KEY,
    risk_assessment_id INTEGER REFERENCES risk_assessments(id),
    patient_username TEXT NOT NULL,
    clinician_username TEXT NOT NULL,
    review_notes TEXT,
    risk_level_override TEXT,                       -- Clinician can override AI assessment
    action_plan TEXT,
    next_review_date DATE,
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 1.2 Risk Scoring Engine

Create a `RiskScoringEngine` class in api.py that calculates composite risk scores.

The scoring algorithm should:

**A. Clinical Data Score (0-40 points)**
- PHQ-9 score >= 20 (severe depression): +15 points
- PHQ-9 score >= 15 (moderately severe): +10 points
- PHQ-9 Item 9 > 0 (suicidal ideation): +15 points (CRITICAL FLAG)
- GAD-7 score >= 15 (severe anxiety): +10 points
- GAD-7 score >= 10 (moderate anxiety): +5 points

**B. Behavioral Score (0-30 points)**
- No mood log in 3+ days: +5 points
- No mood log in 7+ days: +10 points
- No app login in 5+ days: +5 points
- Sudden mood drop (>4 points in 48hrs): +10 points
- Consistent low mood (<3/10 for 5+ days): +10 points
- Stopped using CBT tools (was active, now inactive 7+ days): +5 points
- Late night activity (2-5am consistently): +5 points
- Safety plan not viewed when mood <3: +5 points

**C. Conversational Score (0-30 points)**
- Suicide-related keywords detected: +15 points (CRITICAL FLAG)
- Self-harm keywords detected: +10 points
- Hopelessness language patterns: +5 points
- Absolutist language ("always", "never", "nothing"): +3 points
- Withdrawal language ("don't care", "give up"): +5 points
- Mentions of plans/methods: +15 points (CRITICAL FLAG)
- Flat affect (very short responses repeatedly): +3 points
- Sudden tone change (positive to very negative): +5 points

**Composite Score Calculation:**
- 0-25: LOW risk (green)
- 26-50: MODERATE risk (yellow)
- 51-75: HIGH risk (orange)
- 76-100: CRITICAL risk (red)

**Auto-alert Triggers:**
- Any CRITICAL FLAG → Immediate alert to clinician
- Score moves from LOW/MODERATE to HIGH → Alert
- Score moves to CRITICAL → Alert + notification
- PHQ-9 Item 9 > 2 → Immediate safety protocol

### 1.3 Seed Risk Keywords

Insert default risk monitoring keywords:

```sql
-- Suicide risk keywords
INSERT INTO risk_keywords (keyword, category, severity_weight) VALUES
('want to die', 'suicide', 10),
('kill myself', 'suicide', 10),
('end it all', 'suicide', 10),
('no point living', 'suicide', 9),
('better off dead', 'suicide', 9),
('suicidal', 'suicide', 10),
('take my own life', 'suicide', 10),
('not worth living', 'suicide', 8),
('can''t go on', 'suicide', 7),
('goodbye forever', 'suicide', 9),
('final goodbye', 'suicide', 9),
('no way out', 'suicide', 7),
('ending my life', 'suicide', 10),
('overdose', 'suicide', 8),
('hang myself', 'suicide', 10),

-- Self-harm keywords
('cut myself', 'self_harm', 8),
('hurting myself', 'self_harm', 8),
('self harm', 'self_harm', 7),
('burn myself', 'self_harm', 8),
('hit myself', 'self_harm', 7),
('punish myself', 'self_harm', 6),
('scratch myself', 'self_harm', 6),
('deserve pain', 'self_harm', 7),

-- Crisis keywords
('panic attack', 'crisis', 5),
('can''t breathe', 'crisis', 6),
('emergency', 'crisis', 7),
('help me', 'crisis', 5),
('scared', 'crisis', 3),
('terrified', 'crisis', 5),
('losing control', 'crisis', 6),
('going crazy', 'crisis', 5),
('breaking down', 'crisis', 6),
('can''t cope', 'crisis', 6),

-- Substance abuse keywords
('drinking too much', 'substance', 6),
('taking drugs', 'substance', 7),
('relapsed', 'substance', 8),
('need a drink', 'substance', 5),
('using again', 'substance', 7),

-- Violence keywords
('hurt someone', 'violence', 8),
('want to hit', 'violence', 7),
('violent thoughts', 'violence', 8),
('rage', 'violence', 5);
```

### 1.4 API Endpoints

Create these endpoints:

```python
# GET /api/risk/score/<username> - Calculate and return current risk score
# GET /api/risk/history/<username> - Risk score history over time
# POST /api/risk/alert - Create manual risk alert
# GET /api/risk/alerts - Get active alerts for clinician
# PATCH /api/risk/alert/<alert_id>/acknowledge - Acknowledge alert
# PATCH /api/risk/alert/<alert_id>/resolve - Resolve alert with action notes
# GET /api/risk/keywords - Get active risk keywords
# POST /api/risk/keywords - Add new risk keyword
```

All endpoints must:
- Verify clinician role (except patient-facing endpoints)
- Use get_wrapped_cursor(conn)
- Use handle_exception(e, endpoint_name)
- Use log_event() for audit trail
- Include proper CSRF handling
```

---

## PHASE 2: AI-Powered Conversation Monitoring

### Prompt for Phase 2

```
You are implementing Phase 2 of the Risk Assessment System for Healing Space UK.

CONTEXT: Phase 1 has been completed. The risk_assessments, risk_alerts, and risk_keywords tables exist. The RiskScoringEngine class exists in api.py.

TASK: Integrate real-time AI conversation monitoring into the therapy chat.

### 2.1 Chat Message Risk Scanner

Modify the existing `/api/therapy/chat` endpoint (therapy_chat function) to:

1. BEFORE sending to AI: Scan the user's message against risk_keywords table
2. If keywords detected:
   a. Calculate keyword severity score
   b. Run AI analysis on the message for context (a keyword in "I'm not suicidal" is different from "I want to kill myself")
   c. Create risk_alert if warranted
   d. Update risk_assessments with new conversational_score
3. AFTER AI responds: Ensure the AI response is appropriate for the risk level
4. If CRITICAL risk detected:
   a. AI must include safety resources in response
   b. Create immediate alert for clinician
   c. Log the event

### 2.2 AI Risk Analysis Function

Create a function that uses Groq API to analyze conversation context:

```python
def analyze_conversation_risk(username, message, recent_history):
    """Use AI to analyze conversation for risk indicators.

    Returns:
        dict: {
            'risk_detected': bool,
            'risk_type': str,  # suicide/self_harm/crisis/none
            'confidence': float,  # 0.0-1.0
            'reasoning': str,
            'suggested_response_approach': str,
            'immediate_action_needed': bool
        }
    """
```

The AI prompt should instruct the model to:
- Analyze the message IN CONTEXT of the conversation history
- Distinguish between discussing past experiences vs current intent
- Identify protective factors (e.g., "I used to feel that way but not anymore")
- Rate confidence level
- NOT over-flag normal emotional expression
- Flag escalating patterns across multiple messages
- Consider cultural and linguistic nuances

### 2.3 Safety Response Protocol

When risk is detected in chat, modify the AI's system prompt to include:

For MODERATE risk:
- Acknowledge feelings empathetically
- Gently explore the situation
- Suggest coping strategies from their safety plan
- Mention professional support availability

For HIGH risk:
- Express genuine concern
- Ask directly about safety (in appropriate therapeutic manner)
- Reference their safety plan
- Encourage contacting their clinician
- Provide crisis line numbers

For CRITICAL risk:
- Express urgent concern
- Provide immediate crisis resources:
  - Samaritans: 116 123 (24/7, free)
  - NHS Crisis Line: 111 (option 2)
  - Crisis Text Line: Text "SHOUT" to 85258
  - Emergency: 999
- Encourage immediate contact with emergency services if in danger
- Create immediate clinician alert
- Log as critical safety event

### 2.4 Conversation Pattern Analysis

Create a scheduled function (or call it periodically) that analyzes conversation patterns over time:

```python
def analyze_conversation_patterns(username, days=7):
    """Analyze conversation patterns over time for risk indicators.

    Checks for:
    - Increasing negativity trend
    - Decreasing message length (withdrawal)
    - Increasing frequency (distress)
    - Time-of-day patterns (late night = higher risk)
    - Topic escalation (mild concern → severe distress)

    Returns updated behavioral_score and conversational_score
    """
```
```

---

## PHASE 3: Clinician Risk Dashboard

### Prompt for Phase 3

```
You are implementing Phase 3 of the Risk Assessment System for Healing Space UK.

CONTEXT: Phases 1-2 are complete. Risk scoring, conversation monitoring, and alerts all work.

TASK: Build the clinician-facing Risk Monitor dashboard.

### 3.1 Professional Tab - Risk Monitor Subtab

Add a new subtab to the Professional tab in templates/index.html:

Button: `<button class="clinical-subtab-btn" onclick="switchClinicalTab('riskmonitor', this)">🚨 Risk Monitor</button>`

### 3.2 Risk Monitor Dashboard Layout

```html
<div id="clinicalRiskmonitorTab" class="clinical-subtab-content" style="display: none;">
    <!-- Quick Stats Bar -->
    <div class="card" style="background: linear-gradient(135deg, #1a1a2e, #16213e); color: white;">
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 15px;">
            <div style="text-align: center;">
                <div style="font-size: 2em; font-weight: bold;" id="criticalCount">0</div>
                <div style="color: #ff4444;">🔴 Critical</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2em; font-weight: bold;" id="highCount">0</div>
                <div style="color: #ff8800;">🟠 High</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2em; font-weight: bold;" id="moderateCount">0</div>
                <div style="color: #ffcc00;">🟡 Moderate</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2em; font-weight: bold;" id="lowCount">0</div>
                <div style="color: #44ff44;">🟢 Low</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2em; font-weight: bold;" id="unreviewedAlerts">0</div>
                <div style="color: #ff6666;">⚠️ Unreviewed</div>
            </div>
        </div>
    </div>

    <!-- Active Alerts Section -->
    <div class="card">
        <h3>⚠️ Active Alerts</h3>
        <div id="activeAlertsList">Loading alerts...</div>
    </div>

    <!-- Patient Risk Overview -->
    <div class="card">
        <h3>👥 Patient Risk Overview</h3>
        <div style="display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap;">
            <button onclick="filterRiskPatients('all')" class="btn">All</button>
            <button onclick="filterRiskPatients('critical')" class="btn" style="background:#ff4444;">Critical</button>
            <button onclick="filterRiskPatients('high')" class="btn" style="background:#ff8800;">High</button>
            <button onclick="filterRiskPatients('moderate')" class="btn" style="background:#ccaa00;">Moderate</button>
        </div>
        <div id="riskPatientsList">Loading...</div>
    </div>

    <!-- Risk Detail Modal (when clicking on a patient) -->
    <div id="riskDetailModal" style="display:none;">
        <!-- Patient risk breakdown, history chart, conversation flags, action buttons -->
    </div>
</div>
```

### 3.3 Risk Detail View

When clinician clicks on a patient in the risk list, show:

1. **Risk Score Breakdown** - Visual bar chart showing:
   - Clinical Score (PHQ-9, GAD-7 contribution)
   - Behavioral Score (engagement patterns)
   - Conversational Score (chat analysis)
   - Total composite score with risk level badge

2. **Risk Timeline** - Line chart showing risk score over time (last 30 days)

3. **Active Alerts** - List of unacknowledged alerts with:
   - Alert type and severity
   - Source (chat message, mood log, assessment)
   - Timestamp
   - [Acknowledge] [Resolve] [Escalate] buttons

4. **Flagged Conversations** - Recent chat messages that triggered risk flags:
   - Message text (highlighted keywords)
   - AI confidence level
   - Context (surrounding messages)
   - [False Positive] [Confirmed Risk] buttons

5. **Contributing Factors** - Detailed list:
   - Latest assessment scores
   - Mood trend (with mini chart)
   - Engagement level
   - Safety plan status
   - Last clinician contact

6. **Action Panel**:
   - [Send Urgent Message] - Direct message to patient
   - [Schedule Emergency Appointment]
   - [Update Safety Plan]
   - [Contact Emergency Services Protocol]
   - [Add Clinical Note]
   - [Override Risk Level] - With mandatory justification

### 3.4 API Endpoints for Dashboard

```python
# GET /api/risk/dashboard - Overview stats for clinician
# GET /api/risk/patients - All patients with risk scores (sorted by risk)
# GET /api/risk/patient/<username>/detail - Full risk detail for one patient
# GET /api/risk/patient/<username>/timeline - Risk score history
# GET /api/risk/patient/<username>/flags - Flagged conversations
# POST /api/risk/patient/<username>/review - Submit clinical review
# POST /api/risk/patient/<username>/escalate - Escalate to supervisor/crisis team
```
```

---

## PHASE 4: Patient-Facing Safety Features

### Prompt for Phase 4

```
You are implementing Phase 4 of the Risk Assessment System for Healing Space UK.

CONTEXT: Phases 1-3 are complete. The backend risk engine and clinician dashboard work.

TASK: Build patient-facing safety features that provide immediate support.

### 4.1 Crisis Resources Page

Create an always-accessible crisis resources section visible to ALL users.

**Location:** Accessible from every tab via a persistent "🆘 Crisis Support" button in the header/footer.

**UK-Specific Crisis Resources (NHS-aligned):**

```
IMMEDIATE DANGER:
- Emergency Services: 999
- Nearest A&E Department

MENTAL HEALTH CRISIS:
- NHS Mental Health Crisis Line: 111 (press 2)
- Samaritans: 116 123 (24/7, free, confidential)
- Crisis Text Line: Text "SHOUT" to 85258
- CALM (Campaign Against Living Miserably): 0800 58 58 58 (5pm-midnight)
- Papyrus (Under 35s): 0800 068 41 41
- Childline (Under 18s): 0800 1111

SELF-HARM SUPPORT:
- Self-Injury Support: 0808 800 8088 (available evenings)
- National Self-Harm Network: Forum at nshn.co.uk

SUBSTANCE MISUSE:
- Frank (Drug Support): 0300 123 6600
- Drinkline: 0300 123 1110
- Alcoholics Anonymous: 0800 917 7650

DOMESTIC ABUSE:
- National Domestic Abuse Helpline: 0808 2000 247
- Men's Advice Line: 0808 801 0327
- Galop (LGBT+): 0800 999 5428

EATING DISORDERS:
- Beat Eating Disorders: 0808 801 0677

ANXIETY/DEPRESSION:
- Mind Infoline: 0300 123 3393
- Anxiety UK: 03444 775 774
- Depression Alliance: Self-help groups

VETERANS:
- Combat Stress: 0800 138 1619
- Veterans' Gateway: 0808 802 1212

BEREAVEMENT:
- Cruse Bereavement Care: 0808 808 1677

LOCAL NHS SERVICES:
- GP Surgery: [Patient's registered GP]
- Community Mental Health Team (CMHT): [Linked via clinician]
- Local Crisis Team: [Based on patient's postcode/area]

ONLINE RESOURCES:
- NHS Every Mind Matters: nhs.uk/every-mind-matters
- Mind: mind.org.uk
- Hub of Hope (find local services): hubofhope.co.uk
```

### 4.2 Safety Plan Builder (Enhanced)

Enhance the existing safety plan with structured NHS-compliant sections:

1. **Warning Signs** - What do I notice when I start to feel bad?
   - Physical signs (not sleeping, stomach aches)
   - Emotional signs (feeling hopeless, angry)
   - Behavioral signs (isolating, not eating)
   - Thought patterns (everything is my fault, no one cares)

2. **Internal Coping Strategies** - Things I can do alone
   - Distraction activities
   - Relaxation techniques (linked to CBT tools)
   - Self-soothing activities
   - Physical activities

3. **People & Places That Provide Distraction**
   - Name, contact, how they help
   - Places that feel safe

4. **People I Can Ask for Help**
   - Friends/family contacts
   - Professional contacts
   - How to reach them

5. **Professionals & Services I Can Contact**
   - GP details
   - Clinician details
   - Crisis team details
   - Emergency services

6. **Making My Environment Safe**
   - Steps to remove means
   - Who can help with this

7. **My Reasons for Living**
   - People, pets, goals, values

8. **Emergency Plan**
   - If I feel I might act on thoughts: call...
   - If I have harmed myself: call...
   - My nearest A&E is...

### 4.3 Automated Safety Check-ins

When the system detects elevated risk:

1. **Gentle Check-in Notification:**
   "Hey [name], we noticed you might be going through a tough time. Would you like to chat, or would it help to look at your safety plan?"
   - [Chat with AI] [View Safety Plan] [I'm OK] [Call Crisis Line]

2. **Daily Safety Check (for high-risk patients):**
   Added to daily tasks:
   - "How are you feeling right now?" (1-10 scale)
   - "Are you having any thoughts of harming yourself?" (Yes/No + details)
   - Quick safety plan reminder

3. **Inactivity Check:**
   If high-risk patient hasn't logged in for 48 hours:
   - Send push notification
   - Alert clinician
   - Offer to call crisis support

### 4.4 Signposting System

Create intelligent signposting that suggests relevant resources based on:

1. **Mood-based signposting:**
   - Mood < 3: Show crisis resources prominently
   - Mood 3-5: Suggest coping tools + professional support
   - Mood 5-7: Encourage continued engagement
   - Mood > 7: Celebrate progress

2. **Assessment-based signposting:**
   - After PHQ-9 > 15: Link to depression resources
   - After GAD-7 > 10: Link to anxiety resources
   - After any concerning score: Prompt safety plan review

3. **Context-based signposting:**
   - Mentions substance use → Substance support resources
   - Mentions relationship issues → Relationship counselling
   - Mentions work stress → Occupational health resources
   - Mentions bereavement → Bereavement support
   - Mentions eating issues → Eating disorder support

4. **NHS Service Finder Integration:**
   Based on patient's registered postcode/area:
   - Find local IAPT services
   - Find nearest A&E
   - Find local crisis team contact
   - Find local support groups

### 4.5 Wellbeing Action Plan (NHS Standard)

Implement the NHS 5 Steps to Mental Wellbeing as trackable goals:
1. Connect with other people
2. Be physically active
3. Learn new skills
4. Give to others
5. Pay attention to the present moment (mindfulness)

Each step becomes a trackable daily task with progress monitoring.
```

---

## PHASE 5: NHS Compliance, Audit Trail & Reporting

### Prompt for Phase 5

```
You are implementing Phase 5 of the Risk Assessment System for Healing Space UK.

CONTEXT: Phases 1-4 are complete.

TASK: Ensure full NHS compliance, create audit trails, and build reporting features.

### 5.1 NHS Data Security Standards (DSPT)

Implement compliance with NHS Data Security and Protection Toolkit:

1. **Data Access Logging:**
   - Log every access to patient risk data
   - Log every risk score calculation
   - Log every alert acknowledgement/resolution
   - Log every clinician override of risk level
   - Retain logs for minimum 8 years (NHS requirement)

2. **Consent Management:**
   - Patient consent for AI monitoring (informed consent)
   - Opt-in/opt-out for conversation analysis
   - Clear explanation of what is monitored and why
   - Ability to withdraw consent at any time
   - Consent recorded with timestamp in consent_log table

3. **Data Minimisation:**
   - Only store necessary risk data
   - Auto-archive risk assessments older than 12 months
   - Anonymise data used for algorithm improvement
   - Patient right to data deletion (with clinical retention exceptions)

4. **Access Controls:**
   - Only assigned clinician can view patient risk data
   - Supervisor override requires justification
   - Developer access prohibited for clinical data
   - Two-factor authentication for risk data access

### 5.2 NICE Guidelines Integration

Align with NICE Clinical Guidelines:

1. **CG133 - Self-harm (longer-term management):**
   - Risk assessment after every self-harm episode
   - Structured follow-up plan
   - Psychosocial assessment integration

2. **CG90 - Depression in adults:**
   - PHQ-9 monitoring at every review
   - Stepped care model integration
   - Treatment response tracking

3. **CG113 - Generalised anxiety disorder:**
   - GAD-7 regular monitoring
   - CBT tool effectiveness tracking
   - Medication review reminders

4. **NG225 - Self-harm assessment:**
   - Structured risk assessment tools
   - Safety planning template (NHS standard)
   - Follow-up scheduling

### 5.3 Clinical Reporting

Generate reports for clinical governance:

1. **Individual Patient Report:**
   - Risk score history
   - Alert history and resolutions
   - Assessment score trends
   - Engagement metrics
   - Treatment response
   - Safety plan compliance

2. **Caseload Report:**
   - All patients by risk level
   - Overdue reviews
   - Unacknowledged alerts
   - Engagement trends
   - Outcome measures

3. **Service Report:**
   - Total active patients
   - Risk distribution
   - Alert response times
   - Intervention outcomes
   - Service capacity metrics

4. **Incident Report (SIRI/STEIS format):**
   - Serious incident documentation
   - Timeline of events
   - Actions taken
   - Lessons learned
   - Required notifications (CQC, CCG, ICB)

### 5.4 Safeguarding Integration

1. **Safeguarding Alerts:**
   - Flag potential safeguarding concerns
   - Mandatory reporting prompts for clinicians
   - MASH (Multi-Agency Safeguarding Hub) referral template
   - Children Act / Care Act compliance flags

2. **Duty of Care Documentation:**
   - Record all clinical decisions
   - Document risk assessment rationale
   - Record information sharing decisions
   - Maintain decision audit trail

### 5.5 Multi-Disciplinary Team (MDT) Features

1. **Risk Case Conference Notes:**
   - Template for MDT discussions
   - Action assignment and tracking
   - Follow-up scheduling
   - Outcome recording

2. **Information Sharing:**
   - Controlled sharing between clinicians
   - Information sharing agreement templates
   - Caldicott principles compliance
   - Record of all information shared

### 5.6 CQC Compliance Features

1. **Safe Domain:**
   - Risk assessment documentation
   - Incident reporting
   - Safeguarding compliance
   - Medication monitoring (if applicable)

2. **Effective Domain:**
   - Outcome measurement (ReQoL, SWEMWBS)
   - Evidence-based practice tracking
   - Clinical audit support

3. **Caring Domain:**
   - Patient satisfaction tracking (existing feedback feature)
   - Person-centred care documentation
   - Shared decision making records

4. **Responsive Domain:**
   - Waiting time monitoring
   - Complaint handling integration
   - Service accessibility measures

5. **Well-led Domain:**
   - Governance reporting
   - Staff supervision records
   - Policy compliance tracking
```

---

## Implementation Priority Order

| Priority | Phase | Feature | Risk Impact |
|----------|-------|---------|-------------|
| P0 | 1 | Risk scoring engine + database | Foundation for everything |
| P0 | 2.1 | Chat keyword scanning | Immediate safety detection |
| P0 | 4.1 | Crisis resources page | Patient immediate access to help |
| P1 | 2.2 | AI risk analysis | Contextual understanding |
| P1 | 3.1 | Risk monitor dashboard | Clinician visibility |
| P1 | 4.2 | Enhanced safety plan | NHS compliance |
| P1 | 4.3 | Automated check-ins | Proactive safety |
| P2 | 3.3 | Risk detail view | Clinical decision support |
| P2 | 4.4 | Signposting system | Patient support |
| P2 | 5.1 | NHS data security | Compliance |
| P3 | 5.2 | NICE guidelines | Clinical governance |
| P3 | 5.3 | Clinical reporting | Service management |
| P3 | 5.4 | Safeguarding integration | Legal compliance |
| P3 | 5.5 | MDT features | Team working |
| P3 | 5.6 | CQC compliance | Regulatory |

---

## Testing Checklist

- [ ] Risk score calculates correctly for all scenarios
- [ ] Critical risk triggers immediate alert
- [ ] Chat keyword scanning doesn't false-positive on safe usage
- [ ] AI risk analysis considers conversation context
- [ ] Clinician receives alerts in real-time
- [ ] Patient can access crisis resources from any page
- [ ] Safety plan follows NHS template
- [ ] Signposting matches patient's needs
- [ ] All risk data access is logged
- [ ] Patient consent is properly recorded
- [ ] Reports generate correctly
- [ ] Data retention policies enforced
- [ ] Clinician can override AI risk assessment
- [ ] Emergency protocol works end-to-end
- [ ] CSRF protection on all risk endpoints
- [ ] Role-based access enforced on all endpoints

---

## Notes for Developer

- The risk system should NEVER prevent a patient from accessing help
- False negatives (missing real risk) are far worse than false positives (over-flagging)
- The AI should err on the side of caution
- All clinical features must be auditable
- Patient-facing language must be warm, non-clinical, and non-judgmental
- Risk scores are CLINICAL TOOLS, not diagnoses
- The system augments clinical judgment, it does NOT replace it
- NHS Duty of Candour applies - be transparent about monitoring
- Consider cultural sensitivity in keyword detection
- The system must work on mobile (responsive design)
- Performance: Risk scoring should complete in <2 seconds
- Never show raw risk scores to patients - only show supportive messaging
