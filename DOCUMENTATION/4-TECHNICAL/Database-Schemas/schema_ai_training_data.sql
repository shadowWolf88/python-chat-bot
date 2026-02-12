CREATE TABLE data_consent
                      (user_hash TEXT PRIMARY KEY,
                       consent_given INTEGER DEFAULT 0,
                       consent_date DATETIME,
                       consent_withdrawn INTEGER DEFAULT 0,
                       withdrawal_date DATETIME);
CREATE TABLE training_chats
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       session_hash TEXT,
                       user_hash TEXT,
                       message_role TEXT,
                       message_content TEXT,
                       timestamp DATETIME,
                       mood_context INTEGER,
                       assessment_severity TEXT,
                       FOREIGN KEY (user_hash) REFERENCES data_consent(user_hash));
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE training_patterns
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_hash TEXT,
                       pattern_type TEXT,
                       pattern_data TEXT,
                       effectiveness_score REAL,
                       timestamp DATETIME,
                       FOREIGN KEY (user_hash) REFERENCES data_consent(user_hash));
CREATE TABLE training_outcomes
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_hash TEXT,
                       baseline_phq9 INTEGER,
                       baseline_gad7 INTEGER,
                       followup_phq9 INTEGER,
                       followup_gad7 INTEGER,
                       days_between INTEGER,
                       interventions_used TEXT,
                       improvement_score REAL,
                       timestamp DATETIME,
                       FOREIGN KEY (user_hash) REFERENCES data_consent(user_hash));
CREATE TABLE training_audit
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_hash TEXT,
                       action TEXT,
                       details TEXT,
                       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
