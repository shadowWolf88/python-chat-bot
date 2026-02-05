# 📚 python-chat-bot - Complete Documentation Index

**Last Updated:** January 17, 2026  
**Version:** 1.0

This folder contains all documentation for the python-chat-bot mental health companion app.

---

## 🚀 Getting Started

### New Users Start Here:

1. **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
2. **[USER_GUIDE.md](USER_GUIDE.md)** - Complete user manual (797 lines)
3. **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - How to test features

### Developers Start Here:

1. **[../README.md](../README.md)** - Project overview
2. **[FEATURE_UPDATES.md](FEATURE_UPDATES.md)** - Recent changes
3. **[../.github/copilot-instructions.md](../.github/copilot-instructions.md)** - Architecture guide

---

## 📖 Core Documentation

### Application Features

| Document | Description | Pages |
|----------|-------------|-------|
| **[USER_GUIDE.md](USER_GUIDE.md)** | Complete user manual covering all features | 797 lines |
| **[TESTING_GUIDE.md](TESTING_GUIDE.md)** | Feature testing instructions | 150 lines |
| **[FEATURE_UPDATES.md](FEATURE_UPDATES.md)** | Recent feature additions and changes | 200 lines |

### What the App Does:

**1. AI Therapy**
- Persistent conversations with AI therapist
- Memory of past sessions and user context
- Crisis detection and safety alerts
- Natural language processing
- Text-to-speech for AI responses

**2. Clinical Tools**
- PHQ-9 depression assessment
- GAD-7 anxiety assessment
- Assessment frequency limits (7 days)
- Score tracking and trends
- Clinical oversight by licensed professionals

**3. Mood Tracking**
- Daily mood logs (1-10 scale)
- Sleep tracking
- Medication tracking
- Activity logging
- Sentiment analysis

**4. CBT Tools**
- Thought records (cognitive restructuring)
- Gratitude journaling
- Breathing exercises
- Grounding techniques (5-4-3-2-1 method)
- Progressive muscle relaxation

**5. Gamification**
- Virtual pet companion
- Reward system for activities
- Pet decay system (gentle encouragement)
- Walking exercises (reward 5 coins)
- Pet stats (happiness, hunger, health, age)

**6. Professional Features**
- Clinician dashboard
- Patient approval workflow
- Therapy notes with AI memory integration
- Patient management
- Clinical scale review

**7. Security & Privacy**
- Argon2/bcrypt password hashing
- 2FA PIN authentication
- Fernet encryption for sensitive data
- Local SQLite storage
- Optional HashiCorp Vault integration
- HIPAA-compliant design

**8. Data Export**
- FHIR-compliant medical export
- SFTP secure transfer
- PDF progress reports
- Encrypted backups

**9. Communication**
- Email notifications (forgot password)
- SMS support (future)
- Webhook alerts for crises
- SMTP integration

**10. Training Data System** (NEW)
- GDPR-compliant data collection
- Anonymized training dataset
- User consent management
- Right to deletion
- Audit trail

---

## 🔐 Security & Compliance

### Security Documentation

| Document | Description |
|----------|-------------|
| **[GDPR_IMPLEMENTATION_SUMMARY.md](GDPR_IMPLEMENTATION_SUMMARY.md)** | GDPR compliance implementation |
| **[TRAINING_DATA_GUIDE.md](TRAINING_DATA_GUIDE.md)** | Training data collection (GDPR) |
| **[EMAIL_SETUP.md](EMAIL_SETUP.md)** | Email security configuration |

### Security Features Explained:

**Password Security:**
- Argon2 (preferred) → bcrypt → PBKDF2 (fallback)
- Legacy SHA256 auto-migration on login
- Minimum strength requirements
- Real-time strength validation

**PIN Security:**
- 4-digit PIN for 2FA
- bcrypt or PBKDF2 hashing
- PIN_SALT for added security

**Data Encryption:**
- Fernet symmetric encryption
- Encrypted fields: full_name, dob, conditions, profile_email, profile_phone
- ENCRYPTION_KEY environment variable
- Separate encryption for FHIR exports

**Authentication Flow:**
1. Username + password verification
2. PIN verification (2FA)
3. Session token generation
4. Last login timestamp update

**Authorization:**
- Role-based access (user/clinician/admin)
- Patient approval workflow
- Clinician-patient relationships
- Dashboard access controls

---

## 🚀 Deployment & Infrastructure

### Deployment Documentation

| Document | Description |
|----------|-------------|
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | GitHub + Railway deployment guide |
| **[RAILWAY_GUIDE.md](RAILWAY_GUIDE.md)** | Railway-specific setup |
| **[RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)** | Railway deployment steps |
| **[RAILWAY_PERSISTENCE.md](RAILWAY_PERSISTENCE.md)** | Database persistence on Railway |
| **[RAILWAY_REMINDERS.md](RAILWAY_REMINDERS.md)** | Railway maintenance reminders |
| **[DEPLOY_NOW.md](DEPLOY_NOW.md)** | Quick deploy checklist |
| **[DNS_SETUP_GUIDE.md](DNS_SETUP_GUIDE.md)** | Custom domain setup |
| **[POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md)** | PostgreSQL migration guide |

### Deployment Options:

**1. Local Development:**
```bash
# Clone repo
git clone <repo-url>

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your keys

# Run app
python3 main.py
```

**2. Railway Deployment:**
- Web conversion required (Tkinter → Flask/React)
- PostgreSQL instead of SQLite
- Environment variables in Railway dashboard
- Volume mounts for persistence
- See RAILWAY_GUIDE.md for full guide

**3. Desktop Distribution:**
- PyInstaller for executable
- GitHub Releases for distribution
- No Railway needed for desktop app
- See DEPLOYMENT.md for details

### Infrastructure:

**Database:**
- SQLite (local): `therapist_app.db`, `pet_game.db`, `ai_training_data.db`
- PostgreSQL (Railway): Single database with schema migration

**File Storage:**
- Backups: `backups/` directory (auto-timestamped)
- Logs: `logs/` directory (training data exports)
- Audit: `audit.log` file

**External Services:**
- Groq API (LLM)
- HashiCorp Vault (optional secrets)
- SFTP servers (optional exports)
- SMTP servers (email)
- Webhooks (crisis alerts)

---

## 🛠️ Setup & Configuration

### Configuration Documentation

| Document | Description |
|----------|-------------|
| **[EMAIL_SETUP.md](EMAIL_SETUP.md)** | Email/SMTP configuration |
| **[EMAIL_PHONE_IMPLEMENTATION.md](EMAIL_PHONE_IMPLEMENTATION.md)** | Email/phone features |
| **[CRON_SETUP.md](CRON_SETUP.md)** | Automated task scheduling |
| **[MOOD_REMINDERS.md](MOOD_REMINDERS.md)** | Mood log reminders setup |

### Environment Variables:

**Required:**
```bash
GROQ_API_KEY=gsk_...           # AI model API key
ENCRYPTION_KEY=...              # Fernet encryption key
PIN_SALT=...                    # PIN hashing salt
ANONYMIZATION_SALT=...          # Training data anonymization
```

**Optional:**
```bash
DEBUG=1                         # Development mode
API_URL=...                     # LLM API endpoint

# Vault integration
VAULT_ADDR=https://vault...
VAULT_TOKEN=...

# SFTP exports
SFTP_HOST=...
SFTP_PORT=22
SFTP_USER=...
SFTP_PASS=...

# Email/SMS
SMTP_SERVER=...
SMTP_PORT=587
SMTP_USER=...
SMTP_PASS=...
FROM_EMAIL=...

# Alerts
ALERT_WEBHOOK_URL=...
```

### Key Generation:

```bash
# Encryption key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# PIN salt
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Anonymization salt
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🤖 AI Training Data System

### Training Data Documentation

| Document | Description | Lines |
|----------|-------------|-------|
| **[TRAINING_DATA_GUIDE.md](TRAINING_DATA_GUIDE.md)** | Complete GDPR-compliant guide | 670 |
| **[TRAINING_DATA_QUICKSTART.md](TRAINING_DATA_QUICKSTART.md)** | Quick start in 3 steps | 290 |
| **[TRAINING_DATA_CHECKLIST.md](TRAINING_DATA_CHECKLIST.md)** | Implementation checklist | 340 |
| **[GDPR_IMPLEMENTATION_SUMMARY.md](GDPR_IMPLEMENTATION_SUMMARY.md)** | GDPR compliance summary | 415 |
| **[ALL_STEPS_COMPLETE.md](ALL_STEPS_COMPLETE.md)** | Visual implementation summary | 400 |

### What It Does:

**Purpose:**
- Collect anonymized therapy session data
- Build proprietary AI training dataset
- Improve mental health AI models
- Full GDPR compliance

**How It Works:**

1. **User Consent** (Opt-in):
   - Checkbox during signup
   - Settings to manage anytime
   - Withdraw consent anytime
   - Delete all data (GDPR right)

2. **Anonymization**:
   - Username → SHA256 hash (irreversible)
   - Emails → [EMAIL]
   - Phones → [PHONE]
   - Names → [NAME]
   - Addresses → [ADDRESS]
   - SSN → [SSN]
   - Dates → [DATE]

3. **Data Collection**:
   - Chat sessions (PII-stripped)
   - CBT thought records
   - Gratitude entries
   - Treatment outcomes (PHQ-9, GAD-7)
   - Mood context

4. **Storage**:
   - Separate database: `ai_training_data.db`
   - No reverse mapping to users
   - Complete audit trail
   - Consent tracking

5. **Export**:
   - Automated nightly exports
   - Manual export script
   - Only consented users
   - Comprehensive logging

6. **Rights**:
   - Right to withdraw consent
   - Right to deletion (GDPR Article 17)
   - Right to access (view consent status)
   - Full transparency

**Files:**
- `training_data_manager.py` - Backend system (425 lines)
- `export_training_data.py` - Automated export script
- `test_anonymization.py` - Test suite
- `setup_training_export_cron.sh` - Cron installer

**Commands:**
```bash
# Test anonymization
python3 test_anonymization.py

# Export training data
python3 export_training_data.py

# Setup automation
./setup_training_export_cron.sh

# Check database
sqlite3 ai_training_data.db
```

---

## 📊 Database Schema

### Tables in `therapist_app.db`:

**1. users**
- username (PRIMARY KEY)
- password (hashed)
- pin (hashed, 2FA)
- last_login
- full_name (encrypted)
- dob (encrypted)
- conditions (encrypted)
- role (user/clinician)
- approval_status
- clinician_id
- disclaimer_accepted
- training_consent (NEW)

**2. sessions**
- session_id (PRIMARY KEY)
- username (FOREIGN KEY)
- title
- created_at

**3. chat_history**
- id (PRIMARY KEY)
- session_id (FOREIGN KEY)
- sender (user/ai)
- message
- timestamp

**4. ai_memory**
- id (PRIMARY KEY)
- username (PRIMARY KEY)
- context_data (JSON)
- last_updated

**5. gratitude_logs**
- id (PRIMARY KEY)
- username
- entry
- entry_timestamp

**6. mood_logs**
- id (PRIMARY KEY)
- username
- mood_val (1-10)
- sleep_val
- meds
- notes
- sentiment
- entrestamp

**7. clinical_scales**
- id (PRIMARY KEY)
- username
- scale_type (PHQ9/GAD7)
- score
- severity
- entry_timestamp
- responses (JSON)

**8. cbt_records**
- id (PRIMARY KEY)
- username
- situation
- automatic_thought
- evidence_against
- alternative_thought
- timestamp

**9. safety_plans**
- id (PRIMARY KEY)
- username
- warning_signs (JSON)
- coping_strategies (JSON)
- people (JSON)
- professionals (JSON)
- environment (JSON)
- reasons (JSON)

**10. therapy_notes**
- id (PRIMARY KEY)
- patient_username
- clinician_username
- note_content
- created_at
- updated_at

**11. notifications**
- id (PRIMARY KEY)
- username
- message
- notification_type
- read_status
- created_at

**12. activity_tracking**
- id (PRIMARY KEY)
- username
- activity_type
- activity_data (JSON)
- timestamp

**13. profile_fields** (encrypted)
- username (PRIMARY KEY)
- profile_email (encrypted)
- profile_phone (encrypted)

**14. password_reset_tokens**
- id (PRIMARY KEY)
- username
- token
- created_at
- expires_at

**15. audit_logs**
- id (PRIMARY KEY)
- username
- actor
- action
- details
- timestamp

### Tables in `pet_game.db`:

**1. pet_stats**
- username (PRIMARY KEY)
- happiness (0-100)
- hunger (0-100)
- health (0-100)
- age (days)
- coins
- last_updated

**2. pet_inventory**
- id (PRIMARY KEY)
- username
- item_name
- quantity

### Tables in `ai_training_data.db`:

**1. data_consent**
- user_hash (PRIMARY KEY, anonymized)
- consent_given (0/1)
- consent_date
- consent_withdrawn (0/1)
- withdrawal_date

**2. training_chats**
- id (PRIMARY KEY)
- session_hash (anonymized)
- user_hash (FOREIGN KEY)
- message_role (user/ai)
- message_content (PII-stripped)
- timestamp
- mood_context (1-10)
- assessment_severity

**3. training_patterns**
- id (PRIMARY KEY)
- user_hash (FOREIGN KEY)
- pattern_type (cbt/gratitude)
- pattern_data (JSON, PII-stripped)
- effectiveness_score
- timestamp

**4. training_outcomes**
- id (PRIMARY KEY)
- user_hash (FOREIGN KEY)
- baseline_phq9
- followup_phq9
- baseline_gad7
- followup_gad7
- days_between
- interventions_used (JSON)
- improvement_score
- timestamp

**5. training_audit**
- id (PRIMARY KEY)
- user_hash (anonymized)
- action (consent_given/withdrawn/data_exported/deleted)
- details
- timestamp

---

## 🏗️ Architecture Overview

### Application Structure:

```
python-chat-bot/
├── main.py                      # Main GUI application (1,976 lines)
├── api.py                       # Flask API server (3,450 lines)
├── pet_game.py                  # Pet gamification system
├── training_data_manager.py     # GDPR training data system
├── export_training_data.py      # Automated data export
├── test_anonymization.py        # Anonymization tests
├── audit.py                     # Audit logging
├── fhir_export.py              # Medical data export
├── secure_transfer.py          # SFTP utilities
├── secrets_manager.py          # Vault/environment secrets
├── requirements.txt            # Python dependencies
├── requirements-pinned.txt     # Pinned versions
├── .env                        # Environment configuration
├── therapist_app.db            # Production database
├── pet_game.db                 # Pet game database
├── ai_training_data.db         # Training data (anonymized)
├── backups/                    # Database backups
├── logs/                       # Export logs
├── templates/                  # HTML templates (Flask)
├── tests/                      # Test suite
└── documentation/              # All documentation (this folder)
```

### Component Interactions:

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                              │
│                    (Desktop GUI - Tkinter)                   │
│                                                              │
│  • Login/Signup UI                                           │
│  • AI Chat Interface                                         │
│  • Mood Tracker                                              │
│  • CBT Tools                                                 │
│  • Pet Game                                                  │
│  • Settings                                                  │
│  • Professional Dashboard                                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        │                                       │
        ↓                                       ↓
┌─────────────────┐                  ┌─────────────────┐
│  therapist_app  │                  │   pet_game.db   │
│      .db        │                  │                 │
│                 │                  │  Pet stats      │
│  User accounts  │                  │  Inventory      │
│  Chat history   │                  └─────────────────┘
│  Mood logs      │
│  CBT records    │
│  Clinical scales│
│  Therapy notes  │
│  Audit logs     │
└─────────────────┘
        ↓
    (if consented)
        ↓
┌─────────────────────────────────────────────────────────────┐
│             training_data_manager.py                         │
│                  (Anonymization Layer)                       │
│                                                              │
│  • anonymize_username() → SHA256 hash                       │
│  • strip_pii() → Remove emails, phones, names, etc.        │
│  • export_*() → Export anonymized data                      │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────┐
│ai_training_data │
│      .db        │
│                 │
│  Anonymized:    │
│  • Chats        │
│  • Patterns     │
│  • Outcomes     │
│  • Audit trail  │
└─────────────────┘
```

### External Integrations:

```
┌─────────────────────────────────────────────────────────────┐
│                    Healing Space App                         │
└─────────────────────────────────────────────────────────────┘
        │
        ├──→ Groq API (LLM for AI therapy)
        │
        ├──→ HashiCorp Vault (optional secret management)
        │
        ├──→ SFTP Servers (optional data exports)
        │
        ├──→ SMTP Servers (password reset emails)
        │
        └──→ Webhook URLs (crisis alerts)
```

---

## 🧪 Testing

### Test Documentation:

**[TESTING_GUIDE.md](TESTING_GUIDE.md)** - How to test all features

### Test Commands:

```bash
# Run full test suite
pytest tests/

# Test anonymization
python3 test_anonymization.py

# Test main app (basic validation)
python3 -m pytest tests/test_app.py

# Manual testing
python3 main.py
```

### What to Test:

1. **Authentication**:
   - Password strength validation
   - 2FA PIN verification
   - Legacy password migration
   - Session persistence
   - "Remember Me" functionality

2. **AI Therapy**:
   - Chat persistence
   - AI memory context
   - Crisis detection
   - Session creation/loading

3. **Mood Tracking**:
   - Mood log creation
   - Sleep tracking
   - Medication tracking
   - Sentiment analysis

4. **Clinical Scales**:
   - PHQ-9 assessment
   - GAD-7 assessment
   - Frequency limits (7 days)
   - Score calculation

5. **CBT Tools**:
   - Thought records
   - Gratitude logging
   - Breathing exercises
   - Grounding exercises

6. **Pet Game**:
   - Feeding
   - Playing
   - Walking
   - Coin rewards
   - Decay system

7. **Professional Features**:
   - Patient approval
   - Therapy notes
   - Patient list
   - Note creation with AI memory

8. **Training Data**:
   - Consent checkbox
   - Anonymization
   - PII stripping
   - Export functionality
   - Deletion (GDPR)

9. **Security**:
   - Encryption/decryption
   - Password hashing
   - PIN hashing
   - Token generation

10. **Data Export**:
    - FHIR export
    - PDF reports
    - SFTP transfer

---

## 📝 API Documentation

### API Endpoints (api.py):

**Authentication:**
- POST `/api/auth/register` - User registration
- POST `/api/auth/login` - User login
- POST `/api/auth/forgot-password` - Password reset request
- POST `/api/auth/clinician/register` - Clinician registration
- POST `/api/auth/disclaimer/accept` - Accept disclaimer

**Notifications:**
- GET `/api/notifications/<username>` - Get user notifications
- POST `/api/notifications/<notification_id>/read` - Mark as read

**Clinicians:**
- GET `/api/clinicians/list` - Get all clinicians
- GET `/api/clinicians/patients/<clinician_username>` - Get patients
- GET `/api/clinicians/pending/<clinician_username>` - Pending approvals
- POST `/api/clinicians/approve-patient` - Approve patient
- POST `/api/therapy-notes/create` - Create therapy note
- GET `/api/therapy-notes/<patient_username>` - Get notes

**AI Therapy:**
- POST `/api/chat` - Send chat message
- POST `/api/ai-memory/<username>` - Update AI memory

**Mood & Activities:**
- GET `/api/mood/<username>` - Get mood logs
- POST `/api/mood` - Create mood log
- GET `/api/activities/<username>` - Get activities

**Training Data (GDPR):**
- POST `/api/training/consent` - Set consent
- GET `/api/training/consent/status` - Check consent
- POST `/api/training/export` - Export user data
- POST `/api/training/delete` - Delete user data (GDPR)
- GET `/api/training/stats` - Admin statistics

**Health Check:**
- GET `/api/health` - Health check endpoint

---

## 🔍 Troubleshooting

### Common Issues:

**1. "Module not found" errors:**
```bash
pip install -r requirements.txt
```

**2. "ENCRYPTION_KEY not set":**
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Add to .env
```

**3. "Database locked":**
- Close all app instances
- Check for zombie processes: `ps aux | grep python3`
- Kill if needed: `kill -9 <PID>`

**4. "API connection failed":**
- Check GROQ_API_KEY in .env
- Verify API_URL is correct
- Check internet connection

**5. "Pet game not loading":**
- Check pet_game.db exists
- Run: `sqlite3 pet_game.db "SELECT * FROM pet_stats;"`

**6. "Tests failing":**
- Set DEBUG=1 in environment
- Check test database permissions
- Run: `python3 test_anonymization.py`

**7. "Training data export errors":**
- Verify ANONYMIZATION_SALT is set
- Check ai_training_data.db permissions
- Review logs: `tail -f logs/training_export.log`

---

## 📚 Additional Resources

### External Links:

- **Groq API**: https://groq.com/
- **Railway Docs**: https://docs.railway.app/
- **FHIR Standard**: https://www.hl7.org/fhir/
- **GDPR Guidelines**: https://gdpr.eu/
- **CustomTkinter**: https://github.com/TomSchimansky/CustomTkinter
- **HashiCorp Vault**: https://www.vaultproject.io/

### Related Documentation:

- **Python Dependencies**: See `requirements.txt`
- **Pinned Versions**: See `requirements-pinned.txt`
- **GitHub Issues**: Check repository issues
- **Git History**: `git log --oneline`

---

## 🆘 Support

### Getting Help:

1. Check relevant documentation above
2. Search existing GitHub issues
3. Review error messages in logs
4. Check environment variables
5. Verify database integrity
6. Test with DEBUG=1

### Reporting Issues:

Include:
- Error messages (full traceback)
- Steps to reproduce
- Environment details (OS, Python version)
- Relevant configuration (sanitized .env)
- Database schema version
- Recent changes made

---

## 📅 Maintenance

### Regular Tasks:

**Daily:**
- Check training data export logs
- Monitor crisis alerts
- Review audit logs

**Weekly:**
- Database backups verification
- User consent rate review
- PII stripping quality check

**Monthly:**
- Security audit
- Dependency updates
- GDPR compliance review
- Training data statistics

### Update Procedures:

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Run migrations (if any)
python3 -c "import main; main.init_db()"

# Test
python3 test_anonymization.py
pytest tests/

# Restart app
python3 main.py
```

---

## 📄 License & Legal

### License:

See LICENSE file in repository root

### Privacy & Compliance:

- **HIPAA**: Designed with HIPAA considerations
- **GDPR**: Fully compliant (see GDPR_IMPLEMENTATION_SUMMARY.md)
- **Data Retention**: Configurable, follows best practices
- **User Rights**: Right to access, deletion, portability

### Disclaimers:

⚠️ **Medical Disclaimer:**
This app does not provide medical advice. It is not a substitute for professional medical treatment. In case of emergency, contact:
- 🇬🇧 UK: 999 or 111
- 🇺🇸 USA: 988 (Suicide & Crisis Lifeline)
- 🇨🇦 Canada: 988

⚠️ **AI Disclaimer:**
AI responses are generated by machine learning models and may not be accurate or appropriate. Always consult qualified mental health professionals for diagnosis and treatment.

---

## 🎯 Quick Reference Card

### Essential Commands:

```bash
# Start app
python3 main.py

# Run tests
python3 test_anonymization.py

# Export training data
python3 export_training_data.py

# Database backup
cp therapist_app.db backups/backup_$(date +%Y%m%d).db

# View logs
tail -f logs/training_export.log

# Check cron jobs
crontab -l
```

### Essential Files:

- `.env` - Configuration
- `therapist_app.db` - Main database
- `ai_training_data.db` - Training data
- `audit.log` - Security audit
- `logs/training_export.log` - Export logs

### Essential Directories:

- `documentation/` - All docs (here)
- `backups/` - Database backups
- `logs/` - Application logs
- `tests/` - Test suite
- `templates/` - HTML templates

---

**Documentation Index Version:** 1.0  
**Last Reviewed:** January 17, 2026  
**Maintained By:** Development Team

*For the latest updates, check the [python-chat-bot GitHub repository](https://github.com/shadowWolf88/python-chat-bot).* 
