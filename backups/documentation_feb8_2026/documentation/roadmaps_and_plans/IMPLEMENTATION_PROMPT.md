You are the best computer programmer in the world, and an absoulte GOD at AI programming.
I want you to read this prompt in full and action all parts with full, detailed, functionality on the live production site, whthout breaking or removing anything that already exists. 

---

## CONTEXT & GOALS

**System Goal:** Transform the AI from a stateless chatbot into a true therapeutic companion that:
- Remembers ALL previous conversations
- Tracks ALL user activities (login/logout, button clicks, feature access)
- Detects behavioral patterns automatically
- Provides continuity and personalization
- Enables clinicians with monthly summaries
- Catches early warning signs through behavior analysis
- Never forgets anything about the patient

**Technical Stack:**
- Backend: Python Flask with PostgreSQL
- Frontend: JavaScript (ES6+) single-page app
- AI: Groq API (llama-3.3-70b-versatile)
- Existing: Session-based auth, wellness logging, chat history, mood tracking

**Key Principle:** NOTHING is too small to track. Every login, logout, button click, feature access, and data entry matters. The AI sees the complete picture of what the patient does.

---

## PHASE 1: DATABASE INFRASTRUCTURE (Week 1-2)

### 1.1 Create New Tables in PostgreSQL

**Create `ai_memory_core` table:**
```sql
CREATE TABLE IF NOT EXISTS ai_memory_core (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    memory_version INT DEFAULT 1,
    memory_data JSONB NOT NULL DEFAULT '{}',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE,
    INDEX idx_username (username),
    INDEX idx_last_updated (last_updated)
);
```

**Purpose:** Single row per patient containing their complete AI memory in JSON format. Allows flexible schema and easy updates.

**What goes in memory_data JSON:**
```json
{
  "personal_context": {
    "preferred_name": "Sarah",
    "pronouns": "she/her",
    "family": ["Emma (sister)", "John (dad)"],
    "work": "Marketing coordinator",
    "living_situation": "Apartment in London",
    "key_stressors": ["work deadlines", "family conflict"]
  },
  "medical": {
    "diagnosis": ["Depression", "Anxiety"],
    "medications": [{"name": "Sertraline", "dose": "50mg", "frequency": "daily"}],
    "clinician": "Dr. Smith",
    "last_appointment": "2026-02-01"
  },
  "conversation_count": 287,
  "wellness_completion_rate": 0.87,
  "last_activity": "2026-02-06T15:32:01Z",
  "high_risk_flags": false,
  "engagement_status": "active",
  "updated_version": 1
}
```

---

**Create `ai_activity_log` table:**
```sql
CREATE TABLE IF NOT EXISTS ai_activity_log (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    -- Types: login, logout, feature_access, button_click, message_sent, data_saved, error
    activity_detail VARCHAR(500),
    -- Specific info: which button, which feature, which field
    activity_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(255),
    -- Groups related activities in one session
    app_state VARCHAR(100),
    -- Current tab/page: home, therapy, wellness, clinical, professional, etc.
    metadata JSONB,
    -- device info, browser, any other context
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE,
    INDEX idx_username (username),
    INDEX idx_timestamp (activity_timestamp),
    INDEX idx_session (session_id),
    INDEX idx_activity_type (activity_type)
);
```

**Purpose:** Comprehensive activity log. Every single interaction gets recorded. Used for pattern detection and anomaly identification.

**What gets logged:**
- User logs in → activity_type: "login", activity_detail: "session_123", session_id: "session_123"
- Opens therapy chat → activity_type: "feature_access", activity_detail: "therapy_chat_tab"
- Clicks "Send Message" button → activity_type: "button_click", activity_detail: "send_message_button"
- Saves wellness entry → activity_type: "data_saved", activity_detail: "mood=5, sleep=7, exercise=yes"
- User logs out → activity_type: "logout", activity_detail: "session_123"

---

**Create `ai_memory_events` table:**
```sql
CREATE TABLE IF NOT EXISTS ai_memory_events (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    -- Types: therapy_message, wellness_log, mood_spike, crisis_flag, app_usage, 
    -- feature_usage, engagement_drop, medication_mention, pattern_detected, etc.
    event_data JSONB NOT NULL,
    -- Full context of event as JSON
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    severity VARCHAR(20) DEFAULT 'normal',
    -- normal, warning, critical
    tags JSONB,
    -- Array of tags for categorization: ["work_stress", "sleep_issue", "escalation"]
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE,
    INDEX idx_username (username),
    INDEX idx_timestamp (event_timestamp),
    INDEX idx_severity (severity),
    INDEX idx_event_type (event_type)
);
```

**Purpose:** Structured event log for pattern detection. Every meaningful event is recorded here.

**What gets logged as events:**
- Therapy message sent: `{"message": "...", "length": 45, "tone": "neutral", "themes": ["work_stress"]}`
- Wellness completed: `{"mood": 5, "sleep": 7, "exercise": "walk", "social": "Emma"}`
- Mood spike detected: `{"previous_avg": 5.2, "current": 3.1, "drop": 2.1, "potential_triggers": ["work", "sleep"]}`
- App usage anomaly: `{"usual_time": "3pm", "actual_time": "2am", "severity": "warning"}`
- Engagement drop: `{"previous_daily_avg": 5, "current_daily_avg": 1, "days_no_engagement": 5}`

---

**Create `ai_memory_flags` table:**
```sql
CREATE TABLE IF NOT EXISTS ai_memory_flags (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    flag_type VARCHAR(100) NOT NULL,
    -- Types: suicide_risk, self_harm, substance_mention, medication_non_adherence,
    -- engagement_drop, isolation, crisis_pattern, unusual_usage, etc.
    flag_status VARCHAR(50) DEFAULT 'active',
    -- active, resolved, monitoring
    first_occurrence TIMESTAMP,
    last_occurrence TIMESTAMP,
    occurrences_count INT DEFAULT 1,
    severity_level INT DEFAULT 1,
    -- 1=low, 2=medium, 3=high, 4=critical
    clinician_notified BOOLEAN DEFAULT FALSE,
    clinician_notified_at TIMESTAMP,
    flag_metadata JSONB,
    -- Additional context about the flag
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE,
    INDEX idx_username (username),
    INDEX idx_flag_type (flag_type),
    INDEX idx_status (flag_status),
    INDEX idx_severity (severity_level)
);
```

**Purpose:** Risk and pattern flag system. Automatically tracks concerning patterns.

**Flags that should be auto-created:**
- suicide_risk (highest priority)
- self_harm
- substance_mention
- medication_non_adherence (hasn't taken meds)
- engagement_drop (missing logs = red flag)
- isolation (less social contact reported)
- unusual_usage (accessing at 3am when they never do)
- crisis_pattern (escalating language detected)
- exercise_abandonment (stopped exercising)
- sleep_deterioration (sleeping much less)

---

**Create `clinician_summaries` table:**
```sql
CREATE TABLE IF NOT EXISTS clinician_summaries (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    clinician_username VARCHAR(255) NOT NULL,
    month_start_date DATE NOT NULL,
    month_end_date DATE NOT NULL,
    summary_data JSONB NOT NULL,
    -- Complete summary data (see below)
    key_patterns JSONB,
    -- Array of detected patterns
    risk_flags JSONB,
    -- Array of active risk flags with details
    achievements JSONB,
    -- Progress on goals, positive trends
    recommended_discussion_points JSONB,
    -- Suggested topics for next appointment
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    viewed_at TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE,
    FOREIGN KEY (clinician_username) REFERENCES users(username) ON DELETE CASCADE,
    INDEX idx_username (username),
    INDEX idx_clinician (clinician_username),
    INDEX idx_month (month_start_date),
    UNIQUE(username, clinician_username, month_start_date)
);
```

**Purpose:** Pre-generated monthly summaries for clinicians.

**What goes in summary_data:**
```json
{
  "wellness_metrics": {
    "ritual_completion_rate": 0.87,
    "average_mood": 6.2,
    "mood_trend": "improving",
    "mood_change": "+0.8",
    "average_sleep": 6.5,
    "sleep_trend": "improving",
    "exercise_frequency": "4x/week",
    "social_engagement": "moderate",
    "medication_adherence": 0.95
  },
  "patterns": [
    {"pattern": "exercise_mood_correlation", "correlation": 0.87, "direction": "positive"},
    {"pattern": "sunday_sleep_drop", "average_hours": 5.2, "concern": "anticipatory_anxiety"}
  ],
  "coping_strategies": {
    "effective": [
      {"strategy": "20min_walk", "used": 8, "effective": 7, "effectiveness_rate": 0.875}
    ],
    "less_effective": [
      {"strategy": "meditation", "used": 1, "effective": 0, "effectiveness_rate": 0}
    ]
  },
  "therapy_themes": {
    "work_stress": {"percentage": 42, "trend": "increasing"},
    "family_dynamics": {"percentage": 28, "trend": "stable"}
  },
  "engagement": {
    "app_logins": 26,
    "therapy_messages": 142,
    "wellness_entries": 26,
    "trend": "stable"
  }
}
```

---

### 1.2 Database Migration Strategy

In `api.py` in the `init_db()` function:

1. Add table creation for all 5 tables using try/except pattern (never drop columns)
2. Check if columns exist before altering
3. Add migration timestamps to track schema versions
4. Log any migrations that run

```python
def init_db():
    conn = get_db_connection()
    cur = get_wrapped_cursor(conn)
    
    # ... existing tables ...
    
    # NEW: ai_memory_core table
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ai_memory_core (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                memory_version INT DEFAULT 1,
                memory_data JSONB NOT NULL DEFAULT '{}',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_ai_memory_username ON ai_memory_core(username);
            CREATE INDEX IF NOT EXISTS idx_ai_memory_updated ON ai_memory_core(last_updated);
        """)
        conn.commit()
        print("✓ ai_memory_core table OK")
    except Exception as e:
        print(f"⚠ ai_memory_core migration: {e}")
        conn.rollback()
    
    # NEW: ai_activity_log table
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ai_activity_log (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                activity_type VARCHAR(100) NOT NULL,
                activity_detail VARCHAR(500),
                activity_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id VARCHAR(255),
                app_state VARCHAR(100),
                metadata JSONB,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_activity_username ON ai_activity_log(username);
            CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON ai_activity_log(activity_timestamp);
            CREATE INDEX IF NOT EXISTS idx_activity_session ON ai_activity_log(session_id);
        """)
        conn.commit()
        print("✓ ai_activity_log table OK")
    except Exception as e:
        print(f"⚠ ai_activity_log migration: {e}")
        conn.rollback()
    
    # ... repeat for ai_memory_events, ai_memory_flags, clinician_summaries ...
    
    conn.close()
```

---

## PHASE 2: BACKEND API ENDPOINTS (Week 2-3)

### 2.1 Activity Logging Endpoint

**Endpoint: `POST /api/activity/log`**

Purpose: Frontend sends activity batch (multiple activities from current session) to backend

```python
@app.route('/api/activity/log', methods=['POST'])
def log_activity():
    """
    Receives batch of activities from frontend and stores them.
    
    Request format:
    {
        "activities": [
            {
                "activity_type": "login",
                "activity_detail": "session_123",
                "app_state": "home",
                "session_id": "session_123",
                "metadata": {"device": "chrome", "os": "windows"}
            },
            {
                "activity_type": "feature_access",
                "activity_detail": "therapy_chat",
                "app_state": "therapy"
            },
            ...
        ]
    }
    
    Response: {"success": true, "activities_logged": 5}
    """
    try:
        authenticated_user = get_authenticated_username()
        if not authenticated_user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        activities = data.get('activities', [])
        
        if not activities or not isinstance(activities, list):
            return jsonify({'error': 'Activities must be a non-empty list'}), 400
        
        conn = get_db_connection()
        cur = get_wrapped_cursor(conn)
        
        logged_count = 0
        for activity in activities:
            # Validate required fields
            activity_type = activity.get('activity_type')
            if not activity_type:
                continue
            
            activity_detail = activity.get('activity_detail', '')
            session_id = activity.get('session_id', '')
            app_state = activity.get('app_state', '')
            metadata = activity.get('metadata', {})
            
            # Insert activity log
            cur.execute("""
                INSERT INTO ai_activity_log 
                (username, activity_type, activity_detail, session_id, app_state, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (authenticated_user, activity_type, activity_detail, session_id, app_state, json.dumps(metadata)))
            logged_count += 1
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'activities_logged': logged_count
        }), 200
    
    except Exception as e:
        log_event('activity_logging_error', f'Error logging activities: {str(e)}')
        return jsonify({'error': 'Failed to log activities', 'detail': str(e)}), 500
```

---

### 2.2 Memory Update Endpoint

**Endpoint: `POST /api/ai/memory/update`**

Purpose: Update the AI memory core after significant interactions

```python
@app.route('/api/ai/memory/update', methods=['POST'])
def update_ai_memory():
    """
    Updates the core memory after interaction.
    
    Request format:
    {
        "event_type": "therapy_message",
        "event_data": {
            "message": "...",
            "length": 45,
            "themes": ["work_stress"],
            "tone": "concerned"
        },
        "severity": "normal"
    }
    
    Response: {"success": true, "memory_updated": true, "version": 2}
    """
    try:
        authenticated_user = get_authenticated_username()
        if not authenticated_user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        event_type = data.get('event_type')
        event_data = data.get('event_data', {})
        severity = data.get('severity', 'normal')
        tags = data.get('tags', [])
        
        if not event_type:
            return jsonify({'error': 'event_type required'}), 400
        
        conn = get_db_connection()
        cur = get_wrapped_cursor(conn)
        
        # 1. Log the event
        cur.execute("""
            INSERT INTO ai_memory_events 
            (username, event_type, event_data, severity, tags)
            VALUES (%s, %s, %s, %s, %s)
        """, (authenticated_user, event_type, json.dumps(event_data), severity, json.dumps(tags)))
        
        # 2. Check for flags that should be raised
        flags_to_check = check_event_for_flags(event_type, event_data)
        for flag_type, flag_severity in flags_to_check:
            update_or_create_flag(conn, cur, authenticated_user, flag_type, flag_severity)
        
        # 3. Update memory core with latest info
        memory_updated = update_memory_core(conn, cur, authenticated_user, event_type, event_data)
        
        conn.commit()
        
        # Get updated memory version
        memory = cur.execute(
            "SELECT memory_version FROM ai_memory_core WHERE username = %s",
            (authenticated_user,)
        ).fetchone()
        memory_version = memory[0] if memory else 1
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'memory_updated': memory_updated,
            'version': memory_version
        }), 200
    
    except Exception as e:
        log_event('memory_update_error', f'Error updating memory: {str(e)}')
        return jsonify({'error': 'Failed to update memory', 'detail': str(e)}), 500
```

**Helper function: `check_event_for_flags`**

```python
def check_event_for_flags(event_type, event_data):
    """
    Analyzes event for concerning patterns and returns flags to raise.
    Returns: [(flag_type, severity_level), ...]
    """
    flags = []
    
    # Check for suicide/self-harm mentions
    if event_type == 'therapy_message':
        message = event_data.get('message', '').lower()
        if any(word in message for word in ['suicide', 'kill myself', 'end it']):
            flags.append(('suicide_risk', 4))  # Critical
        if any(word in message for word in ['self harm', 'cut myself', 'hurt myself']):
            flags.append(('self_harm', 4))  # Critical
        if any(word in message for word in ['drugs', 'cocaine', 'heroin']):
            flags.append(('substance_mention', 3))  # High
    
    # Check for engagement drops
    if event_type == 'engagement_analysis':
        if event_data.get('engagement_trend') == 'declining':
            flags.append(('engagement_drop', 2))  # Medium
    
    # Check for unusual usage patterns
    if event_type == 'app_usage':
        time_of_use = event_data.get('time_of_use')
        if time_of_use == 'late_night_unusual':
            flags.append(('unusual_usage', 2))  # Medium
    
    return flags
```

**Helper function: `update_memory_core`**

```python
def update_memory_core(conn, cur, username, event_type, event_data):
    """
    Updates the core memory JSON with latest information.
    """
    try:
        # Get current memory
        result = cur.execute(
            "SELECT memory_data, memory_version FROM ai_memory_core WHERE username = %s",
            (username,)
        ).fetchone()
        
        if not result:
            # Create new memory record
            initial_memory = {
                "personal_context": {},
                "medical": {},
                "conversation_count": 0,
                "wellness_completion_rate": 0,
                "last_activity": datetime.now().isoformat(),
                "engagement_status": "active",
                "high_risk_flags": False
            }
            cur.execute(
                "INSERT INTO ai_memory_core (username, memory_data, memory_version) VALUES (%s, %s, %s)",
                (username, json.dumps(initial_memory), 1)
            )
            memory_data = initial_memory
            memory_version = 1
        else:
            memory_data = json.loads(result[0])
            memory_version = result[1]
        
        # Update based on event type
        if event_type == 'therapy_message':
            memory_data['conversation_count'] = memory_data.get('conversation_count', 0) + 1
            memory_data['last_activity'] = datetime.now().isoformat()
        
        elif event_type == 'wellness_log':
            # Update engagement metrics
            total_logs = cur.execute(
                "SELECT COUNT(*) FROM wellness_logs WHERE username = %s",
                (username,)
            ).fetchone()[0]
            memory_data['wellness_entries_total'] = total_logs
        
        elif event_type == 'mood_spike':
            memory_data['last_mood_spike'] = datetime.now().isoformat()
        
        # Check for any active critical flags
        critical_flags = cur.execute(
            "SELECT COUNT(*) FROM ai_memory_flags WHERE username = %s AND severity_level >= 4 AND flag_status = 'active'",
            (username,)
        ).fetchone()[0]
        memory_data['high_risk_flags'] = critical_flags > 0
        
        memory_data['last_updated'] = datetime.now().isoformat()
        memory_version += 1
        
        # Save updated memory
        cur.execute(
            "UPDATE ai_memory_core SET memory_data = %s, memory_version = %s, last_updated = CURRENT_TIMESTAMP WHERE username = %s",
            (json.dumps(memory_data), memory_version, username)
        )
        
        return True
    except Exception as e:
        print(f"Error updating memory core: {e}")
        return False
```

---

### 2.3 AI Memory Retrieval Endpoint

**Endpoint: `GET /api/ai/memory`**

Purpose: Get the complete memory for AI system prompt injection

```python
@app.route('/api/ai/memory', methods=['GET'])
def get_ai_memory():
    """
    Returns formatted memory for AI system prompt.
    Used by TherapistAI.get_response() to build context.
    
    Response: Complete memory object with all context
    """
    try:
        authenticated_user = get_authenticated_username()
        if not authenticated_user:
            return jsonify({'error': 'Authentication required'}), 401
        
        conn = get_db_connection()
        cur = get_wrapped_cursor(conn)
        
        # Get core memory
        memory_result = cur.execute(
            "SELECT memory_data FROM ai_memory_core WHERE username = %s",
            (authenticated_user,)
        ).fetchone()
        
        core_memory = json.loads(memory_result[0]) if memory_result else {}
        
        # Get recent events (last 7 days)
        recent_events = cur.execute("""
            SELECT event_type, event_data, event_timestamp 
            FROM ai_memory_events 
            WHERE username = %s 
            AND event_timestamp >= NOW() - INTERVAL '7 days'
            ORDER BY event_timestamp DESC
            LIMIT 50
        """, (authenticated_user,)).fetchall()
        
        # Get active flags
        active_flags = cur.execute("""
            SELECT flag_type, severity_level, occurrences_count, last_occurrence
            FROM ai_memory_flags 
            WHERE username = %s AND flag_status = 'active'
            ORDER BY severity_level DESC
        """, (authenticated_user,)).fetchall()
        
        # Get recent activity summary
        recent_activities = cur.execute("""
            SELECT activity_type, COUNT(*) as count, MAX(activity_timestamp) as last_activity
            FROM ai_activity_log
            WHERE username = %s
            AND activity_timestamp >= NOW() - INTERVAL '24 hours'
            GROUP BY activity_type
        """, (authenticated_user,)).fetchall()
        
        # Get conversation count
        conversation_count = cur.execute(
            "SELECT COUNT(*) FROM chat_history WHERE session_id = %s",
            (f"{authenticated_user}_session",)
        ).fetchone()[0]
        
        # Format response
        memory_for_ai = {
            "personal_context": core_memory.get("personal_context", {}),
            "medical": core_memory.get("medical", {}),
            "conversation_count": conversation_count,
            "recent_events": [
                {
                    "type": event[0],
                    "data": json.loads(event[1]),
                    "timestamp": event[2].isoformat()
                }
                for event in recent_events
            ],
            "active_flags": [
                {
                    "flag_type": flag[0],
                    "severity": flag[1],
                    "occurrences": flag[2],
                    "last_occurrence": flag[3].isoformat()
                }
                for flag in active_flags
            ],
            "recent_activities": {
                activity[0]: {
                    "count": activity[1],
                    "last_activity": activity[2].isoformat()
                }
                for activity in recent_activities
            },
            "engagement_status": core_memory.get("engagement_status", "unknown"),
            "last_activity": core_memory.get("last_activity", None)
        }
        
        cur.close()
        conn.close()
        
        return jsonify(memory_for_ai), 200
    
    except Exception as e:
        log_event('memory_retrieval_error', f'Error retrieving memory: {str(e)}')
        return jsonify({'error': 'Failed to retrieve memory', 'detail': str(e)}), 500
```

---

### 2.4 Pattern Detection Endpoint (Nightly Batch)

**Endpoint: `POST /api/ai/patterns/detect`**

Purpose: Nightly job to analyze activities and detect patterns

```python
@app.route('/api/ai/patterns/detect', methods=['POST'])
def detect_patterns():
    """
    Nightly batch job that processes all activities for the day and detects patterns.
    Should be called by a cron job: 0 2 * * * (2am daily)
    
    Detects:
    - Engagement drops
    - Unusual usage times
    - Mood-sleep-exercise correlations
    - Behavioral changes
    - Risk escalations
    """
    try:
        # Get all users with recent activity (more efficient than all users)
        conn = get_db_connection()
        cur = get_wrapped_cursor(conn)
        
        active_users = cur.execute("""
            SELECT DISTINCT username FROM ai_activity_log
            WHERE activity_timestamp >= NOW() - INTERVAL '24 hours'
        """).fetchall()
        
        patterns_detected = 0
        
        for user_tuple in active_users:
            username = user_tuple[0]
            
            # Detect engagement patterns
            detect_engagement_patterns(conn, cur, username)
            
            # Detect usage time anomalies
            detect_usage_anomalies(conn, cur, username)
            
            # Detect health correlations
            detect_health_patterns(conn, cur, username)
            
            # Detect escalation patterns
            detect_escalation_patterns(conn, cur, username)
            
            patterns_detected += 1
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'patterns_detected': patterns_detected,
            'users_analyzed': len(active_users)
        }), 200
    
    except Exception as e:
        log_event('pattern_detection_error', f'Error detecting patterns: {str(e)}')
        return jsonify({'error': 'Failed to detect patterns', 'detail': str(e)}), 500

def detect_engagement_patterns(conn, cur, username):
    """Detect engagement drops and disengagement"""
    # Get last 7 days activity
    last_7_days = cur.execute("""
        SELECT COUNT(DISTINCT DATE(activity_timestamp)) as login_days
        FROM ai_activity_log
        WHERE username = %s
        AND activity_timestamp >= NOW() - INTERVAL '7 days'
    """, (username,)).fetchone()[0]
    
    # Get previous 7 days activity
    prev_7_days = cur.execute("""
        SELECT COUNT(DISTINCT DATE(activity_timestamp)) as login_days
        FROM ai_activity_log
        WHERE username = %s
        AND activity_timestamp >= NOW() - INTERVAL '14 days'
        AND activity_timestamp < NOW() - INTERVAL '7 days'
    """, (username,)).fetchone()[0]
    
    # Check for drop
    if prev_7_days > 0 and last_7_days < prev_7_days * 0.6:
        # More than 40% drop = concern
        update_or_create_flag(
            conn, cur, username, 'engagement_drop', 2,
            {'previous_days': prev_7_days, 'current_days': last_7_days}
        )

def detect_usage_anomalies(conn, cur, username):
    """Detect unusual usage patterns (time of day, frequency)"""
    # Get typical usage time
    typical_time = cur.execute("""
        SELECT EXTRACT(HOUR FROM activity_timestamp) as hour, COUNT(*) as frequency
        FROM ai_activity_log
        WHERE username = %s
        AND activity_timestamp >= NOW() - INTERVAL '30 days'
        GROUP BY EXTRACT(HOUR FROM activity_timestamp)
        ORDER BY frequency DESC
        LIMIT 1
    """, (username,)).fetchone()
    
    if not typical_time:
        return
    
    typical_hour = int(typical_time[0])
    
    # Check if today used at unusual time
    today_hours = cur.execute("""
        SELECT EXTRACT(HOUR FROM activity_timestamp) as hour
        FROM ai_activity_log
        WHERE username = %s
        AND DATE(activity_timestamp) = CURRENT_DATE
    """, (username,)).fetchall()
    
    for hour_tuple in today_hours:
        hour = int(hour_tuple[0])
        if hour < 6 and typical_hour >= 12:  # Late night when usually daytime
            update_or_create_flag(
                conn, cur, username, 'unusual_usage', 2,
                {'typical_hour': typical_hour, 'current_hour': hour, 'pattern': 'late_night'}
            )

def detect_health_patterns(conn, cur, username):
    """Detect correlations between sleep, mood, and exercise"""
    # Get last 30 days of mood/sleep/exercise
    moods = cur.execute("""
        SELECT DATE(entrestamp) as day, mood_val, sleep_val
        FROM mood_logs
        WHERE username = %s
        AND entrestamp >= NOW() - INTERVAL '30 days'
        ORDER BY entrestamp
    """, (username,)).fetchall()
    
    if len(moods) < 5:
        return  # Not enough data
    
    # Simple correlation: do they sleep more on good mood days?
    good_mood_days = [sleep for _, mood, sleep in moods if mood >= 6 and sleep]
    bad_mood_days = [sleep for _, mood, sleep in moods if mood <= 4 and sleep]
    
    if good_mood_days and bad_mood_days:
        avg_good = sum(good_mood_days) / len(good_mood_days)
        avg_bad = sum(bad_mood_days) / len(bad_mood_days)
        
        if avg_good > avg_bad:
            # Sleep correlates with mood
            # Log this as a positive pattern
            pass

def detect_escalation_patterns(conn, cur, username):
    """Detect escalating risk language"""
    # Get recent therapy messages
    messages = cur.execute("""
        SELECT message, timestamp
        FROM chat_history
        WHERE session_id = %s
        AND timestamp >= NOW() - INTERVAL '7 days'
        ORDER BY timestamp DESC
        LIMIT 20
    """, (f"{username}_session",)).fetchall()
    
    if len(messages) < 2:
        return
    
    # Look for escalation in language
    # Check if recent messages are more concerning than before
    recent_severity = analyze_message_severity(messages[0][0])
    older_severity = analyze_message_severity(messages[-1][0])
    
    if recent_severity > older_severity * 1.5:
        # Significant escalation detected
        update_or_create_flag(
            conn, cur, username, 'crisis_pattern', 3,
            {'escalation_detected': True, 'recent_severity': recent_severity}
        )

def analyze_message_severity(message):
    """Analyze message for concerning language"""
    severity = 0
    concerning_words = {
        'suicide': 10, 'kill': 8, 'death': 7, 'hopeless': 6, 'worthless': 6,
        'nothing matters': 8, 'everyone hate': 7, 'alone': 5
    }
    
    message_lower = message.lower()
    for word, value in concerning_words.items():
        if word in message_lower:
            severity = max(severity, value)
    
    return severity
```

---

### 2.5 Clinician Summary Generation (Weekly/Monthly)

**Endpoint: `POST /api/clinician/summaries/generate`**

Purpose: Generate monthly summaries for clinicians

```python
@app.route('/api/clinician/summaries/generate', methods=['POST'])
def generate_clinician_summaries():
    """
    Generates monthly summaries for all clinician-patient relationships.
    Should be called at end of month or on demand.
    """
    try:
        conn = get_db_connection()
        cur = get_wrapped_cursor(conn)
        
        # Get all approved patient-clinician relationships
        approvals = cur.execute("""
            SELECT patient_username, clinician_username 
            FROM patient_approvals 
            WHERE status = 'approved'
        """).fetchall()
        
        summaries_generated = 0
        today = date.today()
        month_start = date(today.year, today.month, 1)
        month_end = date(today.year, today.month + 1, 1) - timedelta(days=1) if today.month < 12 else date(today.year + 1, 1, 1) - timedelta(days=1)
        
        for patient, clinician in approvals:
            summary = generate_single_summary(conn, cur, patient, clinician, month_start, month_end)
            if summary:
                summaries_generated += 1
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'summaries_generated': summaries_generated,
            'month': f"{month_start.strftime('%B %Y')}"
        }), 200
    
    except Exception as e:
        log_event('summary_generation_error', f'Error generating summaries: {str(e)}')
        return jsonify({'error': 'Failed to generate summaries', 'detail': str(e)}), 500

def generate_single_summary(conn, cur, patient_username, clinician_username, month_start, month_end):
    """Generate a single monthly summary"""
    try:
        # Get wellness metrics
        wellness_data = cur.execute("""
            SELECT AVG(mood) as avg_mood, 
                   COUNT(*) as total_entries,
                   AVG(sleep) as avg_sleep,
                   COUNT(DISTINCT DATE(entrestamp)) as days_logged
            FROM mood_logs
            WHERE username = %s
            AND entrestamp >= %s
            AND entrestamp < %s + INTERVAL '1 day'
        """, (patient_username, month_start, month_end)).fetchone()
        
        # Get therapy activity
        therapy_count = cur.execute("""
            SELECT COUNT(*) FROM chat_history
            WHERE session_id = %s
            AND timestamp >= %s
            AND timestamp < %s + INTERVAL '1 day'
        """, (f"{patient_username}_session", month_start, month_end)).fetchone()[0]
        
        # Get wellness ritual completion
        wellness_ritual_completion = cur.execute("""
            SELECT COUNT(*) FROM wellness_logs
            WHERE username = %s
            AND created_at >= %s
            AND created_at < %s + INTERVAL '1 day'
        """, (patient_username, month_start, month_end)).fetchone()[0]
        
        # Get active flags
        flags = cur.execute("""
            SELECT flag_type, severity_level, occurrences_count
            FROM ai_memory_flags
            WHERE username = %s
            AND flag_status = 'active'
        """, (patient_username,)).fetchall()
        
        # Assemble summary
        summary_data = {
            "wellness_metrics": {
                "average_mood": float(wellness_data[0]) if wellness_data[0] else None,
                "total_entries": wellness_data[1],
                "average_sleep": float(wellness_data[2]) if wellness_data[2] else None,
                "days_logged": wellness_data[3],
                "completion_rate": (wellness_data[3] / 30) * 100 if wellness_data[3] else 0
            },
            "therapy_activity": {
                "total_messages": therapy_count,
                "average_per_week": therapy_count / 4,
                "engagement_level": "high" if therapy_count > 16 else "medium" if therapy_count > 8 else "low"
            },
            "active_concerns": [
                {
                    "flag": flag[0],
                    "severity": flag[1],
                    "occurrences": flag[2]
                }
                for flag in flags
            ]
        }
        
        # Insert summary
        cur.execute("""
            INSERT INTO clinician_summaries
            (username, clinician_username, month_start_date, month_end_date, summary_data, generated_at)
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (username, clinician_username, month_start_date)
            DO UPDATE SET summary_data = %s, generated_at = CURRENT_TIMESTAMP
        """, (patient_username, clinician_username, month_start, month_end, json.dumps(summary_data), json.dumps(summary_data)))
        
        return True
    
    except Exception as e:
        print(f"Error generating summary for {patient_username}: {e}")
        return False
```

---

### 2.6 TherapistAI Enhancement

Modify `TherapistAI.get_response()` to inject memory context:

```python
def get_response(self, user_message, history=None, wellness_data=None):
    """
    Enhanced to include complete memory context in system prompt.
    """
    # NEW: Get AI memory for this user
    # This would be called via API inside this function or passed in
    memory_context = self.build_memory_context(self.username)
    
    # Build enhanced system prompt with memory
    system_prompt = f"""
You are a compassionate, continuous AI therapy companion for {memory_context.get('preferred_name', 'friend')}.

=== YOUR MEMORY OF THIS PERSON ===

CONVERSATION HISTORY:
- This is conversation #{memory_context.get('conversation_count', 1)}
- You've been supporting them since {memory_context.get('signup_date', 'recently')}
- Last conversation: {memory_context.get('last_conversation_date', 'today')}

RECENT IMPORTANT CONTEXT (Last 7 days):
{self.format_recent_events(memory_context.get('recent_events', []))}

ABOUT THEM:
- Name: {memory_context.get('preferred_name', 'friend')}
- Diagnoses: {', '.join(memory_context.get('diagnoses', ['not specified']))}
- Current medication: {memory_context.get('current_medications', 'unknown')}
- Clinician: {memory_context.get('clinician_name', 'unknown')}
- Working on: {memory_context.get('current_goals', 'personal growth')}

PATTERNS I'VE NOTICED:
{self.format_detected_patterns(memory_context.get('patterns', []))}

WHAT HELPS THEM MOST:
{self.format_coping_strategies(memory_context.get('effective_strategies', []))}

⚠️ IMPORTANT ALERTS:
{self.format_alerts(memory_context.get('active_flags', []))}

TODAY'S CONTEXT:
- Mood reported: {wellness_data.get('mood') if wellness_data else 'unknown'}
- Sleep last night: {wellness_data.get('sleep') if wellness_data else 'unknown'} hours
- Exercise: {wellness_data.get('exercise') if wellness_data else 'not reported'}
- Usage time: {self.get_usage_context()} (unusual if different from normal)

YOUR INSTRUCTIONS:
1. ALWAYS reference previous conversations when relevant
2. Notice patterns and mention them naturally
3. Celebrate progress you've witnessed
4. Acknowledge recurring struggles
5. Remember their goals and how they're progressing
6. If this is unusual usage time, gently ask if they're okay
7. If engagement is dropping, express concern and check in
8. If active flags exist, be extra attentive to warning signs
9. Provide continuity - show you truly know them
10. Never say "I'm a new conversation" or "I don't remember"

EXAMPLES OF GOOD RESPONSES:
- "I noticed your mood improved last week when you started exercising regularly - keep that going"
- "You mentioned work stress being worse on Monday mornings - is this Monday feeling the same?"
- "You've been doing your wellness check-in consistently for 27 days - that's real commitment"
- "You usually message me in the afternoons but it's 2am - are you okay? Trouble sleeping?"
- "Your engagement has dropped this week - is everything alright? I want to make sure you're getting support"
"""
    
    # Make API call with enhanced prompt
    response = self.call_groq_api(system_prompt, history, user_message)
    
    # Log this conversation to memory
    self.log_conversation_to_memory(user_message, response)
    
    return response

def build_memory_context(self, username):
    """Build complete memory context for system prompt"""
    try:
        # Call /api/ai/memory endpoint
        # This would be better as a method that can be called directly
        # or pass it in from api.py
        memory = fetch_user_memory(username)
        return memory
    except:
        return {}

def format_recent_events(self, events):
    """Format recent events for readability"""
    if not events:
        return "No recent events"
    
    formatted = ""
    for event in events[:5]:  # Last 5 events
        event_type = event.get('type', 'unknown')
        if event_type == 'therapy_message':
            formatted += f"- Talked about: {event.get('data', {}).get('themes', [])}\n"
        elif event_type == 'wellness_log':
            formatted += f"- Logged wellness data\n"
        elif event_type == 'mood_spike':
            formatted += f"- Mood dropped: {event.get('data', {}).get('drop', 'unknown')}\n"
    
    return formatted

def format_detected_patterns(self, patterns):
    """Format detected patterns"""
    if not patterns:
        return "No patterns detected yet"
    
    formatted = ""
    for pattern in patterns[:5]:
        formatted += f"- {pattern.get('pattern', 'unknown')}: {pattern.get('description', '')}\n"
    
    return formatted

def format_coping_strategies(self, strategies):
    """Format effective coping strategies"""
    if not strategies:
        return "Still learning what helps them most"
    
    formatted = ""
    for strategy in strategies:
        effectiveness = strategy.get('effectiveness_rate', 0)
        formatted += f"- {strategy.get('name', 'unknown')}: {effectiveness*100:.0f}% effective\n"
    
    return formatted

def format_alerts(self, flags):
    """Format active alert flags"""
    if not flags:
        return "No concerning flags"
    
    formatted = ""
    for flag in flags:
        formatted += f"- {flag.get('flag_type', 'unknown')}: {flag.get('severity', 'unknown')} severity\n"
    
    return formatted

def get_usage_context(self):
    """Determine if usage time is unusual"""
    # Get current hour
    current_hour = datetime.now().hour
    # Compare to typical usage pattern (would be stored in memory)
    # Return "unusual - typically morning, now evening" etc
    return "normal time"

def log_conversation_to_memory(self, user_message, ai_response):
    """Log conversation to ai_memory_events"""
    # This would call POST /api/ai/memory/update with conversation data
    pass
```

---

## PHASE 3: FRONTEND ACTIVITY TRACKING (Week 3)

### 3.1 Activity Logger Module (JavaScript)

Create new file: `static/js/activity-logger.js`

```javascript
/**
 * Activity Logger
 * 
 * Tracks EVERY user interaction and sends to backend for logging.
 * Batches activities to avoid excessive requests.
 */

class ActivityLogger {
    constructor() {
        this.currentSessionId = this.generateSessionId();
        this.activities = [];
        this.batchSize = 10;
        this.batchTimer = null;
        this.batchInterval = 300000; // 5 minutes
        
        this.setupEventListeners();
        this.startBatchTimer();
        this.logLoginEvent();
    }
    
    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    setupEventListeners() {
        // Track page/tab changes
        document.addEventListener('click', (e) => this.handleClick(e));
        
        // Track form submissions (saving data)
        document.addEventListener('submit', (e) => this.handleFormSubmit(e));
        
        // Track tab changes
        document.addEventListener('tabchange', (e) => this.logTabChange(e));
        
        // Track logout
        window.addEventListener('beforeunload', () => this.handleLogout());
        
        // Track visibility changes (minimize app)
        document.addEventListener('visibilitychange', () => this.handleVisibilityChange());
    }
    
    logActivity(activityType, activityDetail = '', appState = '') {
        const activity = {
            activity_type: activityType,
            activity_detail: activityDetail,
            session_id: this.currentSessionId,
            app_state: appState || this.getCurrentAppState(),
            metadata: {
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
            }
        };
        
        this.activities.push(activity);
        
        // Send immediately if batch is full
        if (this.activities.length >= this.batchSize) {
            this.sendBatch();
        }
    }
    
    handleClick(event) {
        const target = event.target;
        
        // Don't log every click, only meaningful ones
        if (target.tagName === 'BUTTON' || target.classList.contains('clickable')) {
            const buttonText = target.innerText || target.id || 'unknown_button';
            this.logActivity('button_click', buttonText, this.getCurrentAppState());
        }
    }
    
    handleFormSubmit(event) {
        const form = event.target;
        const formId = form.id || 'unknown_form';
        
        // Collect field names (not values for privacy)
        const fields = Array.from(form.elements)
            .filter(el => el.name)
            .map(el => el.name)
            .join(', ');
        
        this.logActivity('form_submit', `${formId}: ${fields}`, this.getCurrentAppState());
    }
    
    logTabChange(event) {
        const tabName = event.detail?.tabName || 'unknown_tab';
        this.logActivity('tab_change', tabName, tabName);
    }
    
    handleVisibilityChange() {
        if (document.hidden) {
            this.logActivity('app_minimized', '', this.getCurrentAppState());
        } else {
            this.logActivity('app_resumed', '', this.getCurrentAppState());
        }
    }
    
    logLoginEvent() {
        this.logActivity('login', this.currentSessionId, 'home');
    }
    
    handleLogout() {
        this.logActivity('logout', this.currentSessionId, this.getCurrentAppState());
        this.sendBatch(true); // Force send before page unloads
    }
    
    getCurrentAppState() {
        // Determine current tab/state
        const activeTab = document.querySelector('[role="tabpanel"][aria-hidden="false"]');
        if (activeTab) {
            return activeTab.id || 'unknown_state';
        }
        return 'home';
    }
    
    startBatchTimer() {
        this.batchTimer = setInterval(() => {
            if (this.activities.length > 0) {
                this.sendBatch();
            }
        }, this.batchInterval);
    }
    
    sendBatch(urgent = false) {
        if (this.activities.length === 0) return;
        
        const batchToSend = [...this.activities];
        this.activities = []; // Clear activities array
        
        const payload = { activities: batchToSend };
        
        const options = {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        };
        
        // Use sendBeacon if urgent (logout), fetch otherwise
        if (urgent && navigator.sendBeacon) {
            navigator.sendBeacon('/api/activity/log', JSON.stringify(payload));
        } else {
            fetch('/api/activity/log', options)
                .then(response => {
                    if (!response.ok) {
                        console.warn('Activity logging failed, will retry next batch');
                        // Re-add activities to queue
                        this.activities = batchToSend.concat(this.activities);
                    }
                })
                .catch(error => {
                    console.warn('Activity logging error:', error);
                    // Re-add activities to queue for retry
                    this.activities = batchToSend.concat(this.activities);
                });
        }
    }
    
    destroy() {
        clearInterval(this.batchTimer);
    }
}

// Initialize activity logger
const activityLogger = new ActivityLogger();
```

### 3.2 Integration Points

Add to main `templates/index.html`:

**After login, initialize:**
```javascript
// After successful login
activityLogger = new ActivityLogger();
```

**On tab change (add to existing tab change handlers):**
```javascript
// Existing tab switching code
function switchTab(tabName) {
    // ... existing tab switch code ...
    
    // NEW: Log tab change
    document.dispatchEvent(new CustomEvent('tabchange', {
        detail: { tabName: tabName }
    }));
}
```

**When user logs out:**
```javascript
function logout() {
    // NEW: Log logout (will send batch before redirect)
    if (activityLogger) {
        activityLogger.handleLogout();
    }
    
    // Existing logout code...
    window.location.href = '/logout';
}
```

**When therapy message is sent:**
```javascript
async function sendMessage() {
    // Existing code...
    
    // NEW: Log the message send with analysis
    const messageLength = message.length;
    const hasConcernWords = ['suicide', 'self harm', 'hopeless'].some(word => message.toLowerCase().includes(word));
    
    activityLogger.logActivity('message_sent', `length:${messageLength}, concern:${hasConcernWords}`, 'therapy');
    
    // Continue with existing fetch...
}
```

**When wellness data is saved:**
```javascript
async function saveWellnessEntry() {
    // Existing code...
    
    // NEW: Log wellness entry
    const wellnessData = {
        mood: document.getElementById('mood').value,
        sleep: document.getElementById('sleep').value,
        exercise: document.getElementById('exercise').value,
        // ... other fields
    };
    
    activityLogger.logActivity('wellness_saved', JSON.stringify(wellnessData), 'wellness');
    
    // Continue with existing fetch...
}
```

---

## PHASE 4: AI INTEGRATION (Week 4)

### 4.1 Modify Therapy Chat Endpoint

In `/api/therapy/chat` endpoint in `api.py`:

```python
@app.route('/api/therapy/chat', methods=['POST'])
def therapy_chat():
    """
    Enhanced to update AI memory and pass memory context to AI.
    """
    try:
        authenticated_user = get_authenticated_username()
        if not authenticated_user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        message = data.get('message')
        wellness_data = data.get('wellness_data', {})
        
        if not message:
            return jsonify({'error': 'Message required'}), 400
        
        conn = get_db_connection()
        cur = get_wrapped_cursor(conn)
        
        # Get conversation history
        session_id = f"{authenticated_user}_session"
        history = cur.execute("""
            SELECT sender, message, timestamp FROM chat_history
            WHERE session_id = %s
            ORDER BY timestamp DESC
            LIMIT 20
        """, (session_id,)).fetchall()
        
        # NEW: Get AI memory context
        ai_memory = get_user_ai_memory(cur, authenticated_user)
        
        # Send to AI with enhanced context
        ai = TherapistAI(authenticated_user)
        ai_response = ai.get_response(
            user_message=message,
            history=history,
            wellness_data=wellness_data,
            memory_context=ai_memory  # NEW
        )
        
        # NEW: Log interaction to memory
        log_therapy_interaction_to_memory(
            conn, cur, authenticated_user, message, ai_response
        )
        
        # Save chat history
        cur.execute("""
            INSERT INTO chat_history (session_id, sender, message, timestamp)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
        """, (session_id, authenticated_user, message))
        
        cur.execute("""
            INSERT INTO chat_history (session_id, sender, message, timestamp)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
        """, (session_id, "TherapistAI", ai_response))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': ai_response,
            'conversation_id': session_id
        }), 200
    
    except Exception as e:
        log_event('therapy_chat_error', str(e))
        return jsonify({'error': 'Failed to process chat', 'detail': str(e)}), 500

def get_user_ai_memory(cur, username):
    """Get AI memory for context injection"""
    try:
        result = cur.execute(
            "SELECT memory_data FROM ai_memory_core WHERE username = %s",
            (username,)
        ).fetchone()
        
        return json.loads(result[0]) if result else {}
    except:
        return {}

def log_therapy_interaction_to_memory(conn, cur, username, user_message, ai_response):
    """Log therapy interaction to ai_memory_events"""
    try:
        # Analyze message for themes and severity
        themes = analyze_message_themes(user_message)
        severity = analyze_message_severity(user_message)
        
        event_data = {
            "message": user_message,
            "length": len(user_message),
            "word_count": len(user_message.split()),
            "themes": themes,
            "severity": severity,
            "response_length": len(ai_response),
            "timestamp": datetime.now().isoformat()
        }
        
        cur.execute("""
            INSERT INTO ai_memory_events (username, event_type, event_data, severity)
            VALUES (%s, %s, %s, %s)
        """, (username, 'therapy_message', json.dumps(event_data), 'warning' if severity >= 6 else 'normal'))
        
    except Exception as e:
        print(f"Error logging therapy interaction: {e}")
```

---

## PHASE 5: CLINICIAN FEATURES (Week 5)

### 5.1 Clinician Summary Endpoint

Create endpoint for clinicians to view summaries:

```python
@app.route('/api/clinician/summaries', methods=['GET'])
def get_clinician_summaries():
    """
    Returns monthly summaries for all patients approved with this clinician.
    """
    try:
        authenticated_user = get_authenticated_username()
        if not authenticated_user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Verify user is a clinician
        conn = get_db_connection()
        cur = get_wrapped_cursor(conn)
        
        user_role = cur.execute(
            "SELECT role FROM users WHERE username = %s",
            (authenticated_user,)
        ).fetchone()[0]
        
        if user_role != 'clinician':
            return jsonify({'error': 'Only clinicians can view summaries'}), 403
        
        # Get approved patients
        patients = cur.execute("""
            SELECT patient_username FROM patient_approvals
            WHERE clinician_username = %s AND status = 'approved'
        """, (authenticated_user,)).fetchall()
        
        summaries = []
        for patient_tuple in patients:
            patient_username = patient_tuple[0]
            
            # Get most recent summary (current month or last month)
            today = date.today()
            month_start = date(today.year, today.month, 1)
            
            summary = cur.execute("""
                SELECT summary_data, generated_at FROM clinician_summaries
                WHERE username = %s
                AND clinician_username = %s
                AND month_start_date = %s
                LIMIT 1
            """, (patient_username, authenticated_user, month_start)).fetchone()
            
            if summary:
                summaries.append({
                    'patient': patient_username,
                    'summary': json.loads(summary[0]),
                    'generated_at': summary[1].isoformat()
                })
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'summaries': summaries
        }), 200
    
    except Exception as e:
        log_event('summary_retrieval_error', str(e))
        return jsonify({'error': 'Failed to retrieve summaries', 'detail': str(e)}), 500
```

---

## PHASE 6: TESTING & DEPLOYMENT

### 6.1 Test Suite

Create `tests/test_ai_memory_system.py`:

```python
import pytest
import json
from datetime import datetime, timedelta

class TestActivityLogging:
    def test_log_activity_requires_auth(self, client):
        response = client.post('/api/activity/log', json={'activities': []})
        assert response.status_code == 401
    
    def test_log_activity_success(self, client, logged_in_session):
        activities = [
            {'activity_type': 'login', 'activity_detail': 'session_123'},
            {'activity_type': 'feature_access', 'activity_detail': 'therapy_chat'},
            {'activity_type': 'button_click', 'activity_detail': 'send_message'}
        ]
        response = client.post(
            '/api/activity/log',
            json={'activities': activities},
            headers={'Cookie': logged_in_session}
        )
        assert response.status_code == 200
        assert response.json()['activities_logged'] == 3
    
    def test_activity_stored_in_database(self, client, logged_in_session, db):
        activities = [
            {'activity_type': 'login', 'activity_detail': 'session_123'}
        ]
        client.post(
            '/api/activity/log',
            json={'activities': activities},
            headers={'Cookie': logged_in_session}
        )
        
        # Verify in database
        cur = db.cursor()
        result = cur.execute(
            "SELECT activity_type FROM ai_activity_log ORDER BY id DESC LIMIT 1"
        ).fetchone()
        assert result[0] == 'login'

class TestMemoryUpdates:
    def test_memory_update_requires_auth(self, client):
        response = client.post('/api/ai/memory/update', json={})
        assert response.status_code == 401
    
    def test_memory_core_created_on_first_event(self, client, logged_in_session):
        response = client.post(
            '/api/ai/memory/update',
            json={
                'event_type': 'therapy_message',
                'event_data': {'message': 'test'},
                'severity': 'normal'
            },
            headers={'Cookie': logged_in_session}
        )
        assert response.status_code == 200
        assert response.json()['memory_updated'] is True

class TestPatternDetection:
    def test_detect_engagement_drop(self, client, db, logged_in_session):
        # Create mock activity logs showing engagement drop
        # Then run pattern detection
        # Verify engagement_drop flag is created
        pass
    
    def test_detect_unusual_usage_time(self, client, db, logged_in_session):
        # Create activity logs at unusual time
        # Run pattern detection
        # Verify unusual_usage flag
        pass

class TestClinicalianSummaries:
    def test_clinician_can_view_approved_patients_summaries(self, client, logged_in_clinician):
        response = client.get(
            '/api/clinician/summaries',
            headers={'Cookie': logged_in_clinician}
        )
        assert response.status_code == 200
        assert 'summaries' in response.json()
    
    def test_clinician_cannot_view_unapproved_patient_summary(self, client, logged_in_clinician, patient):
        # Patient not in approved list
        response = client.get(
            f'/api/clinician/summaries?patient={patient}',
            headers={'Cookie': logged_in_clinician}
        )
        assert response.status_code == 403
```

### 6.2 Deployment Checklist

- [ ] All 5 new tables created in production database
- [ ] All API endpoints tested with valid/invalid inputs
- [ ] Activity logging working on frontend (check Network tab)
- [ ] Batch activities sending every 5 minutes
- [ ] Memory updates working after therapy chat
- [ ] Pattern detection running nightly
- [ ] Clinician summaries generating monthly
- [ ] AI memory injected into system prompts
- [ ] No sensitive data logged
- [ ] Error handling covers all edge cases
- [ ] Database indexes in place for performance
- [ ] Rate limiting on /api/activity/log to prevent spam

---

## CRITICAL IMPLEMENTATION NOTES

1. **Batch Activity Logging:** Activities must be batched (not sent individually) to avoid overwhelming the server
2. **Privacy:** Never log message content in activity log, only metadata
3. **Performance:** Use PostgreSQL indexes on all frequently-queried columns
4. **Error Handling:** All endpoints must gracefully handle database errors
5. **Memory Update Frequency:** Update ai_memory_core after every significant event
6. **Flag Severity Levels:** 1=low, 2=medium, 3=high, 4=critical (only 4 triggers immediate clinician alert)
7. **Pattern Detection:** Run nightly via cron job, not on-demand API calls
8. **Clinician Access:** Verify patient approval before returning any data
9. **Patient Privacy:** Ensure patient memory view doesn't expose raw flags, only summarized insights
10. **Data Retention:** Keep detailed activity logs for 12 months, summaries indefinitely

---

## SUCCESS CRITERIA

When complete, the system should:

✅ Track EVERY user action (login, logout, button click, feature access)  
✅ Update AI memory after every significant interaction  
✅ Detect behavioral patterns automatically (nightly)  
✅ Raise flags for concerning patterns automatically  
✅ AI includes memory context in system prompt  
✅ AI never says "new conversation"  
✅ AI references previous conversations naturally  
✅ Clinicians see monthly summaries with actionable insights  
✅ Clinician can identify at-risk patients from dashboard  
✅ All data stored encrypted and securely  
✅ GDPR-compliant deletion on request  
✅ No performance degradation despite increased logging  

---

## ESTIMATED EFFORT

- **Phase 1:** Database setup - 2-3 days
- **Phase 2:** Backend endpoints - 4-5 days
- **Phase 3:** Frontend activity logging - 2-3 days
- **Phase 4:** AI integration - 2-3 days
- **Phase 5:** Clinician features - 2-3 days
- **Phase 6:** Testing & deployment - 2-3 days

**Total:** 2-3 weeks for complete implementation

---

## QUESTIONS DURING IMPLEMENTATION

If stuck, check:
1. **Database Connection:** Verify PostgreSQL is running and migrations succeed
2. **API Response:** Test all endpoints with curl/Postman before frontend integration
3. **Frontend Integration:** Check browser console for fetch errors
4. **Memory Injection:** Verify AI system prompt includes memory context
5. **Batch Processing:** Ensure activities batch correctly (test with 100+ activities)
6. **Performance:** Monitor query times on ai_activity_log (should use indexes)
7. **Privacy:** Audit logging to ensure no PII in activity logs

---

## AUTO-DISCOVERY OF NEW FEATURES

### Principle: Zero-Config AI Memory Integration

When ANY new feature, tab, endpoint, or interactive element is added to the patient dashboard, the AI memory system MUST automatically detect and incorporate it — with ZERO manual wiring required for basic tracking.

### How It Works

**1. Frontend Auto-Detection (activity-logger.js):**

The `ActivityLogger` class uses global DOM event listeners that automatically capture:
- **New tab added** → `switchTab()` dispatches a `tabchange` event → ActivityLogger logs it
- **New button added** → Any `<button>`, `<a>`, `[role="button"]`, `.clickable`, or `.tab-btn` click is captured → logged automatically
- **New form/save action** → If it uses a `<button>` → click logged automatically
- **Visibility changes** → App minimize/resume tracked automatically

No changes to `activity-logger.js` are needed for basic interaction tracking.

**2. Backend Auto-Detection:**

The system automatically captures new features through existing infrastructure:
- If the new endpoint calls `log_event()` → it appears in audit_logs → AI sees it
- If the new endpoint saves to ANY table with a `username` column → nightly pattern detection can query it
- If the new feature sends data via `POST /api/ai/memory/update` with a new `event_type` → it flows into `ai_memory_events` automatically
- The `update_ai_memory()` function dynamically builds memory summaries from all tracked tables

**3. The Auto-Discovery Contract:**

When building ANY new patient-facing feature, follow these rules:

```
RULE 1: USE EXISTING ACTIVITY LOGGING (Zero code needed)
  - Frontend: Use standard <button> elements (ActivityLogger captures them)
  - Frontend: If adding a new tab, use switchTab() (tabchange event fires automatically)
  - Frontend: For significant saves, add one line:
    activityLogger.logActivity('feature_name_saved', 'metadata', 'tab_name');

RULE 2: LOG TO AI MEMORY ON SAVE (One line of code)
  - Backend: After saving new data, insert into ai_memory_events:
    cur.execute("""
        INSERT INTO ai_memory_events (username, event_type, event_data, severity)
        VALUES (%s, %s, %s, 'normal')
    """, (username, 'new_feature_name', json.dumps(event_data)))

RULE 3: INCLUDE IN update_ai_memory() (Small block of code)
  - Add a query for the new table to the update_ai_memory() function
  - This ensures the AI's text memory_summary includes the new data
  - Pattern: fetch recent entries → summarize → append to memory_parts[]

RULE 4: ADD TO PATTERN DETECTION (if applicable)
  - If the feature produces data that could indicate risk or patterns,
    add a detection function in the nightly batch job
  - Example: "journaling_abandonment" if user stops using a new journal feature
```

**4. What Happens Automatically (No Code Changes Needed):**

| New Feature Added | What AI Memory Sees Automatically |
|---|---|
| New tab in dashboard | Tab change logged, feature_access recorded |
| New button anywhere | Button click logged with label text |
| New save/submit action | Button click logged |
| New data entry form | ActivityLogger captures the interaction |
| New API endpoint called | If it uses log_event(), audit trail created |

**5. What Requires ONE Line of Code:**

| New Feature Added | One Line to Add |
|---|---|
| New data saved to DB | `activityLogger.logActivity('feature_saved', 'metadata', 'tab');` in frontend |
| New significant event | `INSERT INTO ai_memory_events` in the backend endpoint |
| New data table queried by AI | Add query block in `update_ai_memory()` function |

**6. What Requires a Small Block of Code:**

| New Feature Added | Code to Add |
|---|---|
| New pattern to detect | Add detection function in nightly batch job |
| New risk flag type | Add to `check_event_for_flags()` keyword lists |
| New clinician summary metric | Add query in `generate_single_summary()` |

### Example: Adding a New "Journal" Feature

```
Step 1: Create the feature (new tab, new endpoint, new table)
Step 2: Frontend already auto-tracks tab switches and button clicks (free)
Step 3: In the save endpoint, add ONE insert to ai_memory_events:
        cur.execute("INSERT INTO ai_memory_events (username, event_type, event_data)
                     VALUES (%s, 'journal_entry', %s)", (username, json.dumps(data)))
Step 4: In update_ai_memory(), add a query:
        recent_journal = cur.execute(
            "SELECT ... FROM journal WHERE username = %s ORDER BY ... LIMIT 5",
            (username,)
        ).fetchall()
        if recent_journal:
            memory_parts.append(f"Journal: {len(recent_journal)} recent entries")
Step 5: Done. AI now knows about journal entries, tracks engagement,
        and can reference them in conversations.
```

### The Golden Rule

> **If a patient can interact with it, the AI must know about it.**
> The system is designed so that 90% of tracking happens automatically.
> The remaining 10% requires at most 3-5 lines of code per new feature.
