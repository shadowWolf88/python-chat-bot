# 📋 Quick Reference Card

**Healing Space Mental Health App - Essential Commands & Info**

---

## 🚀 Start Here

### First Time Setup:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Run the app
python3 main.py
```

### Daily Use:
```bash
# Start application
python3 main.py

# Run tests
python3 test_anonymization.py
```

---

## 📚 Documentation Map

**Start here:** [00_INDEX.md](00_INDEX.md) - Complete documentation index

### By Category:

| Category | Key Documents |
|----------|--------------|
| **Getting Started** | QUICKSTART.md, USER_GUIDE.md |
| **Features** | USER_GUIDE.md, FEATURE_UPDATES.md |
| **Testing** | TESTING_GUIDE.md |
| **Security** | GDPR_IMPLEMENTATION_SUMMARY.md, EMAIL_SETUP.md |
| **Training Data** | TRAINING_DATA_GUIDE.md, TRAINING_DATA_QUICKSTART.md |
| **Deployment** | DEPLOYMENT.md, RAILWAY_GUIDE.md |
| **Configuration** | EMAIL_SETUP.md, CRON_SETUP.md |

---

## 🎯 Common Tasks

### User Actions:
```
✓ Create account         → Signup screen
✓ Start therapy chat     → New Conversation button
✓ Track mood            → Mood Tracker button
✓ Complete assessment   → Clinical Scales (7-day limit)
✓ Use CBT tools         → Coping Toolbox button
✓ Feed pet              → Self-Care Pet button
✓ View progress         → Progress Insights button
✓ Manage consent        → Settings → AI Research Data
```

### Admin Tasks:
```bash
# Backup database
cp therapist_app.db backups/backup_$(date +%Y%m%d).db

# Export training data
python3 export_training_data.py

# View logs
tail -f logs/training_export.log

# Check database
sqlite3 therapist_app.db "SELECT COUNT(*) FROM users;"

# Test anonymization
python3 test_anonymization.py
```

### Developer Tasks:
```bash
# Run full test suite
pytest tests/

# Check for errors
python3 -m py_compile main.py

# View git history
git log --oneline -10

# Update dependencies
pip install -r requirements.txt --upgrade
```

---

## 🗄️ Database Quick Reference

### Main Databases:

| Database | Purpose | Location |
|----------|---------|----------|
| `therapist_app.db` | Main app data | Project root |
| `pet_game.db` | Pet game stats | Project root |
| `ai_training_data.db` | Anonymized training data | Project root |

### Key Tables (therapist_app.db):

```sql
-- Users
SELECT * FROM users WHERE username='patient1';

-- Chat history
SELECT * FROM chat_history WHERE session_id='xxx' ORDER BY timestamp;

-- Mood logs
SELECT * FROM mood_logs WHERE username='patient1' ORDER BY entrestamp DESC;

-- Clinical scales
SELECT * FROM clinical_scales WHERE username='patient1' ORDER BY entry_timestamp DESC;

-- Training consent
SELECT username, training_consent FROM users WHERE training_consent=1;
```

---

## 🔑 Environment Variables

### Required:
```bash
GROQ_API_KEY=gsk_...           # AI API key
ENCRYPTION_KEY=...              # Fernet key
PIN_SALT=...                    # PIN hashing
ANONYMIZATION_SALT=...          # Training data
```

### Generate Keys:
```bash
# Encryption key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Salt (PIN or anonymization)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🐛 Troubleshooting Quick Fixes

### App Won't Start:
```bash
# Check Python version (need 3.8+)
python3 --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check for zombie processes
ps aux | grep python3
```

### Database Issues:
```bash
# Check database exists
ls -lh *.db

# Verify database integrity
sqlite3 therapist_app.db "PRAGMA integrity_check;"

# Restore from backup
cp backups/latest_backup.db therapist_app.db
```

### API Connection Issues:
```bash
# Test API key
curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/...

# Check .env loaded
python3 -c "import os; print(os.getenv('GROQ_API_KEY'))"
```

### Training Data Issues:
```bash
# Test anonymization
python3 test_anonymization.py

# Check consent
sqlite3 therapist_app.db "SELECT username, training_consent FROM users;"

# Manual export
python3 export_training_data.py
```

---

## 📊 Feature Checklist

### Core Features:

- [x] AI Therapy Chat
- [x] Persistent Memory
- [x] Mood Tracking
- [x] Sleep Tracking
- [x] Medication Tracking
- [x] PHQ-9 Assessment
- [x] GAD-7 Assessment
- [x] CBT Thought Records
- [x] Gratitude Journal
- [x] Breathing Exercises
- [x] Grounding Exercises
- [x] Virtual Pet
- [x] Coin Rewards
- [x] Pet Walking
- [x] Crisis Detection
- [x] Safety Plan
- [x] Panic Button
- [x] Clinician Dashboard
- [x] Patient Approval
- [x] Therapy Notes
- [x] Progress Reports
- [x] PDF Export
- [x] FHIR Export
- [x] Email Notifications
- [x] Password Reset
- [x] 2FA PIN
- [x] Session Persistence
- [x] "Remember Me"
- [x] Training Data Collection
- [x] GDPR Compliance
- [x] Anonymization
- [x] Audit Trail

---

## 🔒 Security Quick Reference

### Authentication:
- Username + Password (Argon2/bcrypt/PBKDF2)
- 2FA PIN (bcrypt/PBKDF2)
- Session tokens
- "Remember Me" (7 days)

### Encryption:
- Fernet symmetric encryption
- Encrypted fields: full_name, dob, conditions, profile_email, profile_phone
- HMAC signing for FHIR exports

### Privacy:
- Local SQLite storage
- No cloud sync (by default)
- Optional SFTP exports
- GDPR-compliant training data
- Audit logging

---

## 📞 Crisis Resources

**In case of emergency:**

- 🇬🇧 **UK**: 999 (Emergency) / 111 (NHS)
- 🇺🇸 **USA**: 988 (Crisis Lifeline) / 911
- 🇨🇦 **Canada**: 988 / 911

**Within the app:**
- Red "PANIC BUTTON" at top of main menu
- Provides crisis resources and contacts
- Can trigger webhooks if configured

---

## 📁 File Locations

### Configuration:
- `.env` - Environment variables
- `requirements.txt` - Python dependencies

### Databases:
- `therapist_app.db` - Main database
- `pet_game.db` - Pet stats
- `ai_training_data.db` - Training data

### Logs:
- `audit.log` - Security audit trail
- `logs/training_export.log` - Export logs

### Backups:
- `backups/` - Auto-created database backups
- Pattern: `therapist_app_YYYYMMDD_HHMMSS.db.bak`

### Code:
- `main.py` - Main GUI (1,976 lines)
- `api.py` - Flask API (3,450 lines)
- `training_data_manager.py` - Training data (425 lines)
- `pet_game.py` - Pet gamification
- `audit.py` - Audit logging
- `fhir_export.py` - Medical exports
- `secure_transfer.py` - SFTP
- `secrets_manager.py` - Secret management

---

## 🎓 Training Data Commands

### Test:
```bash
python3 test_anonymization.py
```

### Export:
```bash
python3 export_training_data.py
```

### Setup Automation:
```bash
./setup_training_export_cron.sh
```

### Check Database:
```bash
sqlite3 ai_training_data.db <<EOF
SELECT COUNT(*) as consented_users FROM data_consent WHERE consent_given=1;
SELECT COUNT(*) as total_chats FROM training_chats;
SELECT COUNT(*) as total_patterns FROM training_patterns;
SELECT COUNT(*) as total_outcomes FROM training_outcomes;
EOF
```

---

## 🔗 Quick Links

- [Complete Index](00_INDEX.md)
- [User Guide](USER_GUIDE.md)
- [Training Data Guide](TRAINING_DATA_GUIDE.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Testing Guide](TESTING_GUIDE.md)

---

## 💡 Pro Tips

1. **Enable DEBUG mode** in development: `export DEBUG=1`
2. **Backup before updates**: `cp therapist_app.db backups/before_update.db`
3. **Check logs regularly**: `tail -f logs/training_export.log`
4. **Test after changes**: `python3 test_anonymization.py`
5. **Review audit trail**: `tail -100 audit.log`
6. **Monitor consent rates**: Check training_consent column weekly
7. **Verify PII stripping**: Review training_chats table samples

---

**Last Updated:** January 17, 2026  
**Quick Reference Version:** 1.0

*For detailed information, see [00_INDEX.md](00_INDEX.md)*
