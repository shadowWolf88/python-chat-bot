CREATE TABLE users 
                      (username TEXT PRIMARY KEY, password TEXT, pin TEXT, last_login TIMESTAMP, 
                       full_name TEXT, dob TEXT, conditions TEXT, role TEXT DEFAULT 'user', 
                       clinician_id TEXT, disclaimer_accepted INTEGER DEFAULT 0, email TEXT, phone TEXT, reset_token TEXT, reset_token_expiry TIMESTAMP, country TEXT, area TEXT, postcode TEXT, nhs_number TEXT, professional_id TEXT);
CREATE TABLE sessions 
                      (session_id TEXT PRIMARY KEY, username TEXT, title TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE gratitude_logs 
                      (id SERIAL PRIMARY KEY, username TEXT, entry TEXT, entry_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, deleted_at TIMESTAMP);
CREATE TABLE safety_plans
                      (username TEXT PRIMARY KEY, triggers TEXT, coping TEXT, contacts TEXT);
CREATE TABLE ai_memory 
                      (username TEXT PRIMARY KEY, memory_summary TEXT, last_updated TIMESTAMP);
CREATE TABLE cbt_records 
                      (id SERIAL PRIMARY KEY, username TEXT, situation TEXT, thought TEXT, evidence TEXT, entry_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, deleted_at TIMESTAMP);
CREATE TABLE clinical_scales
                      (id SERIAL PRIMARY KEY, username TEXT, scale_name TEXT, score INTEGER, severity TEXT, entry_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE community_posts
                      (id SERIAL PRIMARY KEY, username TEXT, message TEXT, likes INTEGER DEFAULT 0, entry_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, category TEXT DEFAULT 'general', is_pinned INTEGER DEFAULT 0, deleted_at TIMESTAMP);
CREATE TABLE audit_logs
                      (id SERIAL PRIMARY KEY, username TEXT, actor TEXT, action TEXT, details TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE alerts
                      (id SERIAL PRIMARY KEY, username TEXT, alert_type TEXT, details TEXT, status TEXT DEFAULT 'open', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, deleted_at TIMESTAMP);
CREATE TABLE patient_approvals
                      (id SERIAL PRIMARY KEY, patient_username TEXT, clinician_username TEXT, 
                       status TEXT DEFAULT 'pending', request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                       approval_date TIMESTAMP);
CREATE TABLE notifications
                      (id SERIAL PRIMARY KEY, recipient_username TEXT, message TEXT, 
                       notification_type TEXT, read INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE chat_history 
                      (session_id TEXT, sender TEXT, message TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, chat_session_id INTEGER);
CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE community_likes
                      (id SERIAL PRIMARY KEY, post_id INTEGER, username TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, reaction_type TEXT DEFAULT 'like', UNIQUE(post_id, username));
CREATE TABLE community_replies
                      (id SERIAL PRIMARY KEY, post_id INTEGER, username TEXT, message TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, deleted_at TIMESTAMP);
CREATE TABLE clinician_notes
                      (id SERIAL PRIMARY KEY, clinician_username TEXT, patient_username TEXT, note_text TEXT, 
                       is_highlighted INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, deleted_at TIMESTAMP);
CREATE TABLE appointments
                      (id SERIAL PRIMARY KEY, 
                       clinician_username TEXT, 
                       patient_username TEXT,
                       appointment_date TIMESTAMP, 
                       appointment_type TEXT DEFAULT 'consultation',
                       notes TEXT,
                       pdf_generated INTEGER DEFAULT 0,
                       pdf_path TEXT,
                       notification_sent INTEGER DEFAULT 0,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, patient_acknowledged INTEGER DEFAULT 0, patient_response TEXT, patient_response_date TIMESTAMP, attendance_status TEXT DEFAULT 'scheduled', attendance_confirmed_by TEXT, attendance_confirmed_at TIMESTAMP, deleted_at TIMESTAMP);
CREATE TABLE chat_sessions
                      (id SERIAL PRIMARY KEY,
                       username TEXT,
                       session_name TEXT,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       is_active INTEGER DEFAULT 0);
CREATE TABLE verification_codes
                      (id SERIAL PRIMARY KEY,
                       identifier TEXT,
                       code TEXT,
                       method TEXT,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       expires_at TIMESTAMP,
                       verified INTEGER DEFAULT 0);
CREATE TABLE dev_messages (
        id SERIAL PRIMARY KEY,
        from_username TEXT,
        to_username TEXT,
        message TEXT,
        message_type TEXT DEFAULT 'info',
        read INTEGER DEFAULT 0,
        parent_message_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    );
CREATE TABLE dev_terminal_logs (
        id SERIAL PRIMARY KEY,
        username TEXT,
        command TEXT,
        output TEXT,
        exit_code INTEGER,
        duration_ms INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
CREATE TABLE dev_ai_chats (
        id SERIAL PRIMARY KEY,
        username TEXT,
        session_id TEXT,
        role TEXT,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_clinician_id ON users(clinician_id);
CREATE INDEX idx_mood_logs_username ON mood_logs(username);
CREATE INDEX idx_mood_logs_entrestamp ON mood_logs(entrestamp);
CREATE INDEX idx_mood_logs_username_entrestamp ON mood_logs(username, entrestamp);
CREATE INDEX idx_sessions_username ON sessions(username);
CREATE INDEX idx_chat_history_session_id ON chat_history(session_id);
CREATE INDEX idx_chat_history_chat_session_id ON chat_history(chat_session_id);
CREATE INDEX idx_chat_history_timestamp ON chat_history(timestamp);
CREATE INDEX idx_chat_sessions_username ON chat_sessions(username);
CREATE INDEX idx_chat_sessions_username_active ON chat_sessions(username, is_active);
CREATE INDEX idx_alerts_username ON alerts(username);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_username_status ON alerts(username, status);
CREATE INDEX idx_patient_approvals_clinician ON patient_approvals(clinician_username);
CREATE INDEX idx_patient_approvals_patient ON patient_approvals(patient_username);
CREATE INDEX idx_patient_approvals_status ON patient_approvals(status);
CREATE INDEX idx_patient_approvals_clinician_status ON patient_approvals(clinician_username, status);
CREATE INDEX idx_clinical_scales_username ON clinical_scales(username);
CREATE INDEX idx_clinical_scales_entry_timestamp ON clinical_scales(entry_timestamp);
CREATE INDEX idx_notifications_recipient ON notifications(recipient_username);
CREATE INDEX idx_notifications_read ON notifications(read);
CREATE INDEX idx_notifications_recipient_read ON notifications(recipient_username, read);
CREATE INDEX idx_appointments_clinician ON appointments(clinician_username);
CREATE INDEX idx_appointments_patient ON appointments(patient_username);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_audit_logs_username ON audit_logs(username);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_gratitude_logs_username ON gratitude_logs(username);
CREATE INDEX idx_cbt_records_username ON cbt_records(username);
CREATE INDEX idx_community_posts_username ON community_posts(username);
CREATE INDEX idx_community_posts_timestamp ON community_posts(entry_timestamp);
CREATE INDEX idx_community_replies_post_id ON community_replies(post_id);
CREATE INDEX idx_clinician_notes_clinician ON clinician_notes(clinician_username);
CREATE INDEX idx_clinician_notes_patient ON clinician_notes(patient_username);
CREATE INDEX idx_verification_codes_identifier ON verification_codes(identifier);
CREATE TABLE community_channel_reads
                      (id SERIAL PRIMARY KEY, username TEXT, channel TEXT, last_read TIMESTAMP DEFAULT CURRENT_TIMESTAMP, UNIQUE(username, channel));
CREATE TABLE breathing_exercises
                      (id SERIAL PRIMARY KEY,
                       username TEXT NOT NULL,
                       exercise_type TEXT NOT NULL,
                       duration_seconds INTEGER,
                       pre_anxiety_level INTEGER,
                       post_anxiety_level INTEGER,
                       notes TEXT,
                       completed INTEGER DEFAULT 1,
                       entry_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE relaxation_techniques
                      (id SERIAL PRIMARY KEY,
                       username TEXT NOT NULL,
                       technique_type TEXT NOT NULL,
                       duration_minutes INTEGER,
                       effectiveness_rating INTEGER,
                       body_scan_areas TEXT,
                       notes TEXT,
                       entry_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE sleep_diary
                      (id SERIAL PRIMARY KEY,
                       username TEXT NOT NULL,
                       sleep_date DATE NOT NULL,
                       bedtime TEXT,
                       wake_time TEXT,
                       time_to_fall_asleep INTEGER,
                       times_woken INTEGER DEFAULT 0,
                       total_sleep_hours REAL,
                       sleep_quality INTEGER,
                       dreams_nightmares TEXT,
                       factors_affecting TEXT,
                       morning_mood INTEGER,
                       notes TEXT,
                       entry_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE core_beliefs
                      (id SERIAL PRIMARY KEY,
                       username TEXT NOT NULL,
                       old_belief TEXT NOT NULL,
                       belief_origin TEXT,
                       evidence_for TEXT,
                       evidence_against TEXT,
                       new_balanced_belief TEXT,
                       belief_strength_before INTEGER,
                       belief_strength_after INTEGER,
                       is_active INTEGER DEFAULT 1,
                       entry_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       last_reviewed TIMESTAMP, deleted_at TIMESTAMP);
CREATE TABLE exposure_hierarchy
                      (id SERIAL PRIMARY KEY,
                       username TEXT NOT NULL,
                       fear_situation TEXT NOT NULL,
                       initial_suds INTEGER,
                       target_suds INTEGER,
                       hierarchy_rank INTEGER,
                       status TEXT DEFAULT 'not_started',
                       entry_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE exposure_attempts
                      (id SERIAL PRIMARY KEY,
                       exposure_id INTEGER NOT NULL,
                       username TEXT NOT NULL,
                       pre_suds INTEGER,
                       peak_suds INTEGER,
                       post_suds INTEGER,
                       duration_minutes INTEGER,
                       coping_strategies_used TEXT,
                       notes TEXT,
                       attempt_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY (exposure_id) REFERENCES exposure_hierarchy(id));
CREATE TABLE problem_solving
                      (id SERIAL PRIMARY KEY,
                       username TEXT NOT NULL,
                       problem_description TEXT NOT NULL,
                       problem_importance INTEGER,
                       brainstormed_solutions TEXT,
                       chosen_solution TEXT,
                       action_steps TEXT,
                       outcome TEXT,
                       status TEXT DEFAULT 'in_progress',
                       entry_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       completed_timestamp TIMESTAMP);
CREATE TABLE coping_cards
                      (id SERIAL PRIMARY KEY,
                       username TEXT NOT NULL,
                       card_title TEXT NOT NULL,
                       situation_trigger TEXT,
                       unhelpful_thought TEXT,
                       helpful_response TEXT,
                       coping_strategies TEXT,
                       is_favorite INTEGER DEFAULT 0,
                       times_used INTEGER DEFAULT 0,
                       entry_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       last_used TIMESTAMP, deleted_at TIMESTAMP);
CREATE TABLE self_compassion_journal
                      (id SERIAL PRIMARY KEY,
                       username TEXT NOT NULL,
                       difficult_situation TEXT,
                       self_critical_thoughts TEXT,
                       common_humanity TEXT,
                       kind_response TEXT,
                       self_care_action TEXT,
                       mood_before INTEGER,
                       mood_after INTEGER,
                       entry_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE values_clarification
                      (id SERIAL PRIMARY KEY,
                       username TEXT NOT NULL,
                       value_name TEXT NOT NULL,
                       value_description TEXT,
                       importance_rating INTEGER,
                       current_alignment INTEGER,
                       life_area TEXT,
                       related_goals TEXT,
                       is_active INTEGER DEFAULT 1,
                       entry_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       last_reviewed TIMESTAMP);
CREATE TABLE goals
                      (id SERIAL PRIMARY KEY,
                       username TEXT NOT NULL,
                       goal_title TEXT NOT NULL,
                       goal_description TEXT,
                       goal_type TEXT,
                       target_date DATE,
                       related_value_id INTEGER,
                       status TEXT DEFAULT 'active',
                       progress_percentage INTEGER DEFAULT 0,
                       entry_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       completed_timestamp TIMESTAMP, deleted_at TIMESTAMP,
                       FOREIGN KEY (related_value_id) REFERENCES values_clarification(id));
CREATE TABLE goal_milestones
                      (id SERIAL PRIMARY KEY,
                       goal_id INTEGER NOT NULL,
                       username TEXT NOT NULL,
                       milestone_title TEXT NOT NULL,
                       milestone_description TEXT,
                       target_date DATE,
                       is_completed INTEGER DEFAULT 0,
                       completed_timestamp TIMESTAMP,
                       entry_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, deleted_at TIMESTAMP,
                       FOREIGN KEY (goal_id) REFERENCES goals(id));
CREATE TABLE goal_checkins
                      (id SERIAL PRIMARY KEY,
                       goal_id INTEGER NOT NULL,
                       username TEXT NOT NULL,
                       progress_notes TEXT,
                       obstacles TEXT,
                       next_steps TEXT,
                       motivation_level INTEGER,
                       checkin_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY (goal_id) REFERENCES goals(id));
CREATE TABLE feedback (
        id SERIAL PRIMARY KEY,
        username TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        category TEXT NOT NULL,
        message TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP,
        admin_notes TEXT
    , deleted_at TIMESTAMP);
CREATE TABLE daily_tasks (
        id SERIAL PRIMARY KEY,
        username TEXT NOT NULL,
        task_type TEXT NOT NULL,
        completed INTEGER DEFAULT 0,
        completed_at TIMESTAMP,
        task_date DATE DEFAULT (date('now')),
        UNIQUE(username, task_type, task_date)
    );
CREATE TABLE daily_streaks (
        username TEXT PRIMARY KEY,
        current_streak INTEGER DEFAULT 0,
        longest_streak INTEGER DEFAULT 0,
        last_complete_date DATE,
        total_bonus_coins INTEGER DEFAULT 0,
        total_bonus_xp INTEGER DEFAULT 0
    );
CREATE TABLE cbt_tool_entries (
        id SERIAL PRIMARY KEY,
        username TEXT NOT NULL,
        tool_type TEXT NOT NULL,
        data TEXT NOT NULL,
        mood_rating INTEGER,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    , deleted_at TIMESTAMP);
CREATE INDEX idx_feedback_username ON feedback(username);
CREATE INDEX idx_feedback_status ON feedback(status);
CREATE INDEX idx_daily_tasks_username ON daily_tasks(username);
CREATE INDEX idx_daily_tasks_username_date ON daily_tasks(username, task_date);
CREATE INDEX idx_cbt_tool_entries_username ON cbt_tool_entries(username);
CREATE INDEX idx_cbt_tool_entries_tool_type ON cbt_tool_entries(username, tool_type);
CREATE TABLE messages (
        id SERIAL PRIMARY KEY,
        sender_username TEXT NOT NULL,
        recipient_username TEXT NOT NULL,
        subject TEXT,
        content TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        read_at TIMESTAMP,
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        deleted_at TIMESTAMP,
        is_deleted_by_sender INTEGER DEFAULT 0,
        is_deleted_by_recipient INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(sender_username) REFERENCES users(username),
        FOREIGN KEY(recipient_username) REFERENCES users(username),
        CHECK (sender_username != recipient_username)
    );
CREATE INDEX idx_messages_recipient ON messages(recipient_username, is_read);
CREATE INDEX idx_messages_conversation ON messages(sender_username, recipient_username);
CREATE INDEX idx_messages_deleted ON messages(deleted_at);
CREATE INDEX idx_messages_sent_at ON messages(sent_at);
CREATE INDEX idx_appointments_active ON appointments(patient_username, deleted_at);
CREATE INDEX idx_appointments_clinician_active ON appointments(clinician_username, deleted_at);
CREATE INDEX idx_clinician_notes_active ON clinician_notes(patient_username, deleted_at);
CREATE INDEX idx_feedback_active ON feedback(username, deleted_at);
CREATE INDEX idx_alerts_active ON alerts(username, deleted_at);
CREATE INDEX idx_community_posts_active ON community_posts(username, deleted_at);
CREATE INDEX idx_community_replies_active ON community_replies(post_id, deleted_at);
CREATE INDEX idx_cbt_records_active ON cbt_records(username, deleted_at);
CREATE INDEX idx_mood_logs_active ON mood_logs(username, deleted_at);
CREATE INDEX idx_goals_active ON goals(username, deleted_at);

-- ==========================================
-- RISK ASSESSMENT SYSTEM (Phase 1)
-- ==========================================
CREATE TABLE risk_assessments (
    id SERIAL PRIMARY KEY,
    patient_username TEXT NOT NULL,
    risk_score INTEGER NOT NULL DEFAULT 0,
    risk_level TEXT NOT NULL DEFAULT 'low',
    suicide_risk INTEGER DEFAULT 0,
    self_harm_risk INTEGER DEFAULT 0,
    crisis_risk INTEGER DEFAULT 0,
    deterioration_risk INTEGER DEFAULT 0,
    contributing_factors TEXT,
    ai_analysis TEXT,
    clinical_data_score INTEGER DEFAULT 0,
    behavioral_score INTEGER DEFAULT 0,
    conversational_score INTEGER DEFAULT 0,
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assessed_by TEXT DEFAULT 'system',
    CONSTRAINT valid_risk_level CHECK (risk_level IN ('critical', 'high', 'moderate', 'low'))
);
CREATE INDEX idx_risk_patient ON risk_assessments(patient_username);
CREATE INDEX idx_risk_level ON risk_assessments(risk_level);
CREATE INDEX idx_risk_date ON risk_assessments(assessed_at);

CREATE TABLE risk_alerts (
    id SERIAL PRIMARY KEY,
    patient_username TEXT NOT NULL,
    clinician_username TEXT,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'moderate',
    title TEXT NOT NULL,
    details TEXT,
    source TEXT,
    ai_confidence REAL,
    risk_score_at_time INTEGER,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by TEXT,
    acknowledged_at TIMESTAMP,
    action_taken TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_severity CHECK (severity IN ('critical', 'high', 'moderate', 'low'))
);
CREATE INDEX idx_risk_alerts_patient ON risk_alerts(patient_username);
CREATE INDEX idx_risk_alerts_unacknowledged ON risk_alerts(acknowledged) WHERE acknowledged = FALSE;
CREATE INDEX idx_risk_alerts_clinician ON risk_alerts(clinician_username);

CREATE TABLE risk_keywords (
    id SERIAL PRIMARY KEY,
    keyword TEXT NOT NULL,
    category TEXT NOT NULL,
    severity_weight INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT TRUE,
    added_by TEXT DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE crisis_contacts (
    id SERIAL PRIMARY KEY,
    patient_username TEXT NOT NULL,
    contact_name TEXT NOT NULL,
    relationship TEXT,
    phone TEXT,
    email TEXT,
    is_primary BOOLEAN DEFAULT FALSE,
    is_professional BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_crisis_contacts_patient ON crisis_contacts(patient_username);

CREATE TABLE risk_reviews (
    id SERIAL PRIMARY KEY,
    risk_assessment_id INTEGER REFERENCES risk_assessments(id),
    patient_username TEXT NOT NULL,
    clinician_username TEXT NOT NULL,
    review_notes TEXT,
    risk_level_override TEXT,
    action_plan TEXT,
    next_review_date DATE,
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced safety plans (8 NHS-compliant sections)
CREATE TABLE IF NOT EXISTS enhanced_safety_plans (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE REFERENCES users(username) ON DELETE CASCADE,
    warning_signs JSONB DEFAULT '{}',
    internal_coping JSONB DEFAULT '{}',
    distraction_people_places JSONB DEFAULT '{}',
    people_for_help JSONB DEFAULT '{}',
    professionals_services JSONB DEFAULT '{}',
    environment_safety JSONB DEFAULT '{}',
    reasons_for_living JSONB DEFAULT '{}',
    emergency_plan JSONB DEFAULT '{}',
    last_reviewed TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI monitoring consent
CREATE TABLE IF NOT EXISTS ai_monitoring_consent (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    consent_given BOOLEAN DEFAULT FALSE,
    consent_date TIMESTAMP,
    withdrawn_date TIMESTAMP,
    consent_text TEXT,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
