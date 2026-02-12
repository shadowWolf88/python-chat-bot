CREATE TABLE data_consent
                      (user_hash TEXT PRIMARY KEY,
                       consent_given INTEGER DEFAULT 0,
                       consent_date TIMESTAMP,
                       consent_withdrawn INTEGER DEFAULT 0,
                       withdrawal_date TIMESTAMP);
CREATE TABLE training_chats
                      (id SERIAL PRIMARY KEY,
                       session_hash TEXT,
                       user_hash TEXT,
                       message_role TEXT,
                       message_content TEXT,
                       timestamp TIMESTAMP,
                       mood_context INTEGER,
                       assessment_severity TEXT,
                       FOREIGN KEY (user_hash) REFERENCES data_consent(user_hash));
CREATE TABLE training_outcomes
                      (id SERIAL PRIMARY KEY,
                       user_hash TEXT,
                       baseline_phq9 INTEGER,
                       baseline_gad7 INTEGER,
                       followup_phq9 INTEGER,
                       followup_gad7 INTEGER,
                       days_between INTEGER,
                       interventions_used TEXT,
                       improvement_score REAL,
                       timestamp TIMESTAMP,
                       FOREIGN KEY (user_hash) REFERENCES data_consent(user_hash));
CREATE TABLE training_audit
                      (id SERIAL PRIMARY KEY,
                       user_hash TEXT,
                       action TEXT,
                       details TEXT,
                       timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
