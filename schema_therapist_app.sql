CREATE TABLE users 
                      (username TEXT PRIMARY KEY, password TEXT, pin TEXT, last_login TIMESTAMP, 
                       full_name TEXT, dob TEXT, conditions TEXT, role TEXT DEFAULT 'user', 
                       clinician_id TEXT, disclaimer_accepted INTEGER DEFAULT 0, email TEXT, phone TEXT, reset_token TEXT, reset_token_expiry DATETIME, country TEXT, area TEXT, postcode TEXT, nhs_number TEXT, professional_id TEXT);
CREATE TABLE sessions 
                      (session_id TEXT PRIMARY KEY, username TEXT, title TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE gratitude_logs 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, entry TEXT, entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, deleted_at DATETIME);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE mood_logs 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, mood_val INTEGER, 
                       sleep_val REAL, meds TEXT, notes TEXT, sentiment TEXT,
                       exercise_mins INTEGER DEFAULT 0, outside_mins INTEGER DEFAULT 0, water_pints REAL DEFAULT 0,
                       entrestamp DATETIME DEFAULT CURRENT_TIMESTAMP, deleted_at DATETIME);
CREATE TABLE safety_plans
                      (username TEXT PRIMARY KEY, triggers TEXT, coping TEXT, contacts TEXT);
CREATE TABLE ai_memory 
                      (username TEXT PRIMARY KEY, memory_summary TEXT, last_updated DATETIME);
CREATE TABLE cbt_records 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, situation TEXT, thought TEXT, evidence TEXT, entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, deleted_at DATETIME);
CREATE TABLE clinical_scales
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, scale_name TEXT, score INTEGER, severity TEXT, entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE community_posts
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, message TEXT, likes INTEGER DEFAULT 0, entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, category TEXT DEFAULT 'general', is_pinned INTEGER DEFAULT 0, deleted_at DATETIME);
CREATE TABLE audit_logs
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, actor TEXT, action TEXT, details TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE alerts
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, alert_type TEXT, details TEXT, status TEXT DEFAULT 'open', created_at DATETIME DEFAULT CURRENT_TIMESTAMP, deleted_at DATETIME);
CREATE TABLE patient_approvals
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_username TEXT, clinician_username TEXT, 
                       status TEXT DEFAULT 'pending', request_date DATETIME DEFAULT CURRENT_TIMESTAMP, 
                       approval_date DATETIME);
CREATE TABLE notifications
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, recipient_username TEXT, message TEXT, 
                       notification_type TEXT, read INTEGER DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE chat_history 
                      (session_id TEXT, sender TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, chat_session_id INTEGER);
CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE community_likes
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, reaction_type TEXT DEFAULT 'like', UNIQUE(post_id, username));
CREATE TABLE community_replies
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, deleted_at DATETIME);
CREATE TABLE clinician_notes
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, clinician_username TEXT, patient_username TEXT, note_text TEXT, 
                       is_highlighted INTEGER DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, deleted_at DATETIME);
CREATE TABLE appointments
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       clinician_username TEXT, 
                       patient_username TEXT,
                       appointment_date DATETIME, 
                       appointment_type TEXT DEFAULT 'consultation',
                       notes TEXT,
                       pdf_generated INTEGER DEFAULT 0,
                       pdf_path TEXT,
                       notification_sent INTEGER DEFAULT 0,
                       created_at DATETIME DEFAULT CURRENT_TIMESTAMP, patient_acknowledged INTEGER DEFAULT 0, patient_response TEXT, patient_response_date DATETIME, attendance_status TEXT DEFAULT 'scheduled', attendance_confirmed_by TEXT, attendance_confirmed_at DATETIME, deleted_at DATETIME);
CREATE TABLE chat_sessions
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT,
                       session_name TEXT,
                       created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                       last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
                       is_active INTEGER DEFAULT 0);
CREATE TABLE verification_codes
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       identifier TEXT,
                       code TEXT,
                       method TEXT,
                       created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                       expires_at DATETIME,
                       verified INTEGER DEFAULT 0);
CREATE TABLE dev_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_username TEXT,
        to_username TEXT,
        message TEXT,
        message_type TEXT DEFAULT 'info',
        read INTEGER DEFAULT 0,
        parent_message_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_message_id) REFERENCES dev_messages(id)
    );
CREATE TABLE dev_terminal_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        command TEXT,
        output TEXT,
        exit_code INTEGER,
        duration_ms INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
CREATE TABLE dev_ai_chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        session_id TEXT,
        role TEXT,
        message TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, channel TEXT, last_read DATETIME DEFAULT CURRENT_TIMESTAMP, UNIQUE(username, channel));
CREATE TABLE breathing_exercises
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT NOT NULL,
                       exercise_type TEXT NOT NULL,
                       duration_seconds INTEGER,
                       pre_anxiety_level INTEGER,
                       post_anxiety_level INTEGER,
                       notes TEXT,
                       completed INTEGER DEFAULT 1,
                       entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE relaxation_techniques
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT NOT NULL,
                       technique_type TEXT NOT NULL,
                       duration_minutes INTEGER,
                       effectiveness_rating INTEGER,
                       body_scan_areas TEXT,
                       notes TEXT,
                       entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE sleep_diary
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                       entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE core_beliefs
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT NOT NULL,
                       old_belief TEXT NOT NULL,
                       belief_origin TEXT,
                       evidence_for TEXT,
                       evidence_against TEXT,
                       new_balanced_belief TEXT,
                       belief_strength_before INTEGER,
                       belief_strength_after INTEGER,
                       is_active INTEGER DEFAULT 1,
                       entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                       last_reviewed DATETIME, deleted_at DATETIME);
CREATE TABLE exposure_hierarchy
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT NOT NULL,
                       fear_situation TEXT NOT NULL,
                       initial_suds INTEGER,
                       target_suds INTEGER,
                       hierarchy_rank INTEGER,
                       status TEXT DEFAULT 'not_started',
                       entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE exposure_attempts
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       exposure_id INTEGER NOT NULL,
                       username TEXT NOT NULL,
                       pre_suds INTEGER,
                       peak_suds INTEGER,
                       post_suds INTEGER,
                       duration_minutes INTEGER,
                       coping_strategies_used TEXT,
                       notes TEXT,
                       attempt_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY (exposure_id) REFERENCES exposure_hierarchy(id));
CREATE TABLE problem_solving
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT NOT NULL,
                       problem_description TEXT NOT NULL,
                       problem_importance INTEGER,
                       brainstormed_solutions TEXT,
                       chosen_solution TEXT,
                       action_steps TEXT,
                       outcome TEXT,
                       status TEXT DEFAULT 'in_progress',
                       entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                       completed_timestamp DATETIME);
CREATE TABLE coping_cards
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT NOT NULL,
                       card_title TEXT NOT NULL,
                       situation_trigger TEXT,
                       unhelpful_thought TEXT,
                       helpful_response TEXT,
                       coping_strategies TEXT,
                       is_favorite INTEGER DEFAULT 0,
                       times_used INTEGER DEFAULT 0,
                       entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                       last_used DATETIME, deleted_at DATETIME);
CREATE TABLE self_compassion_journal
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT NOT NULL,
                       difficult_situation TEXT,
                       self_critical_thoughts TEXT,
                       common_humanity TEXT,
                       kind_response TEXT,
                       self_care_action TEXT,
                       mood_before INTEGER,
                       mood_after INTEGER,
                       entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE values_clarification
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT NOT NULL,
                       value_name TEXT NOT NULL,
                       value_description TEXT,
                       importance_rating INTEGER,
                       current_alignment INTEGER,
                       life_area TEXT,
                       related_goals TEXT,
                       is_active INTEGER DEFAULT 1,
                       entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                       last_reviewed DATETIME);
CREATE TABLE goals
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT NOT NULL,
                       goal_title TEXT NOT NULL,
                       goal_description TEXT,
                       goal_type TEXT,
                       target_date DATE,
                       related_value_id INTEGER,
                       status TEXT DEFAULT 'active',
                       progress_percentage INTEGER DEFAULT 0,
                       entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                       completed_timestamp DATETIME, deleted_at DATETIME,
                       FOREIGN KEY (related_value_id) REFERENCES values_clarification(id));
CREATE TABLE goal_milestones
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       goal_id INTEGER NOT NULL,
                       username TEXT NOT NULL,
                       milestone_title TEXT NOT NULL,
                       milestone_description TEXT,
                       target_date DATE,
                       is_completed INTEGER DEFAULT 0,
                       completed_timestamp DATETIME,
                       entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, deleted_at DATETIME,
                       FOREIGN KEY (goal_id) REFERENCES goals(id));
CREATE TABLE goal_checkins
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       goal_id INTEGER NOT NULL,
                       username TEXT NOT NULL,
                       progress_notes TEXT,
                       obstacles TEXT,
                       next_steps TEXT,
                       motivation_level INTEGER,
                       checkin_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY (goal_id) REFERENCES goals(id));
CREATE TABLE feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        category TEXT NOT NULL,
        message TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        resolved_at DATETIME,
        admin_notes TEXT
    , deleted_at DATETIME);
CREATE TABLE daily_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        task_type TEXT NOT NULL,
        completed INTEGER DEFAULT 0,
        completed_at DATETIME,
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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        tool_type TEXT NOT NULL,
        data TEXT NOT NULL,
        mood_rating INTEGER,
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    , deleted_at DATETIME);
CREATE INDEX idx_feedback_username ON feedback(username);
CREATE INDEX idx_feedback_status ON feedback(status);
CREATE INDEX idx_daily_tasks_username ON daily_tasks(username);
CREATE INDEX idx_daily_tasks_username_date ON daily_tasks(username, task_date);
CREATE INDEX idx_cbt_tool_entries_username ON cbt_tool_entries(username);
CREATE INDEX idx_cbt_tool_entries_tool_type ON cbt_tool_entries(username, tool_type);
CREATE TABLE messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_username TEXT NOT NULL,
        recipient_username TEXT NOT NULL,
        subject TEXT,
        content TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        read_at DATETIME,
        sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        deleted_at DATETIME,
        is_deleted_by_sender INTEGER DEFAULT 0,
        is_deleted_by_recipient INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
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
