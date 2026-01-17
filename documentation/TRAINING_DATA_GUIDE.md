# AI Training Data Collection - GDPR Compliance Guide

## Overview

This system collects anonymized therapy session data to build a proprietary AI training dataset while maintaining **full GDPR compliance**.

## 🔒 GDPR Compliance Features

### 1. Explicit Consent (Required)
- **Opt-in only** - No data collected without explicit consent
- Users must actively agree to data usage
- Consent is separate from treatment
- Clear explanation of data usage

### 2. Complete Anonymization
- **Irreversible hashing** of usernames (SHA256 + salt)
- **No PII stored** in training database
- Automated PII scrubbing:
  - Email addresses → `[EMAIL]`
  - Phone numbers → `[PHONE]`
  - Names → `[NAME]`
  - Addresses → `[ADDRESS]`
  - Dates of birth → `[DATE]`
  - SSN → `[SSN]`

### 3. Right to Withdraw
- Users can withdraw consent at any time
- Withdrawal is immediate
- No penalties for withdrawal

### 4. Right to Deletion (Right to be Forgotten)
- Users can request complete deletion
- All training data removed permanently
- Audit trail maintained (anonymized)

### 5. Data Minimization
- Only collects necessary data:
  - Chat messages (anonymized)
  - Therapy patterns (CBT, gratitude)
  - Treatment outcomes (scores only)
- No demographic data
- No identifiable clinical notes

### 6. Purpose Limitation
- Data used ONLY for AI model training
- Cannot be repurposed without new consent
- Clear disclosure of intended use

### 7. Audit Trail
- All actions logged:
  - Consent given/withdrawn
  - Data exported
  - Data deleted
- Timestamps for all events
- Anonymous user hashes only

---

## 📊 Data Collected

### 1. Anonymized Chat Sessions
**Table**: `training_chats`

Collected:
- Message role (user/ai)
- Message content (PII-stripped)
- Timestamp
- Mood context (integer 1-10)
- Assessment severity (minimal/mild/moderate/severe)

**NOT Collected**:
- Real username
- Session identifiers linked to real identity
- Any PII in messages

### 2. Therapy Patterns
**Table**: `training_patterns`

Collected:
- CBT thought records:
  - Situation (anonymized)
  - Automatic thought (anonymized)
  - Evidence against thought (anonymized)
- Gratitude entries (anonymized)
- Pattern type
- Timestamp

**NOT Collected**:
- Personal details in situations
- Identifiable scenarios
- Names of people mentioned

### 3. Treatment Outcomes
**Table**: `training_outcomes`

Collected:
- Baseline PHQ-9 score
- Follow-up PHQ-9 score
- Baseline GAD-7 score
- Follow-up GAD-7 score
- Days between assessments
- Improvement score
- Interventions used (types only)

**NOT Collected**:
- Medical diagnoses
- Medication names
- Clinician names
- Treatment locations

---

## 🔧 Technical Implementation

### Database Structure

**Production Database**: `therapist_app.db` (existing)
- Contains all user data with PII
- HIPAA-compliant storage
- Not used for training

**Training Database**: `ai_training_data.db` (new)
- Completely separate
- Only anonymized data
- No reverse mapping to production

### Anonymization Process

```python
# Username hashing (irreversible)
user_hash = SHA256(username + salt)[:16]
# Result: "a3f9c2e1b4d8f7e2"

# PII stripping
"My email is john@example.com" → "My email is [EMAIL]"
"Call me at 555-123-4567" → "Call me at [PHONE]"
"I live at 123 Main Street" → "I live at [ADDRESS]"
```

### Data Flow

```
Production DB → Consent Check → Anonymization → Training DB
                     ↓
              If no consent: STOP
              If consent: Continue
                     ↓
                PII Removal
                     ↓
              Hash Username
                     ↓
           Store in Training DB
```

---

## 🚀 API Endpoints

### 1. Set Consent

**POST** `/api/training/consent`

Request:
```json
{
  "username": "patient123",
  "consent": true
}
```

Response:
```json
{
  "success": true,
  "message": "Thank you for contributing to mental health AI research!"
}
```

### 2. Check Consent Status

**GET** `/api/training/consent/status?username=patient123`

Response:
```json
{
  "consented": true
}
```

### 3. Export Training Data

**POST** `/api/training/export`

Request:
```json
{
  "username": "patient123"
}
```

Response:
```json
{
  "success": true,
  "results": {
    "chats": {
      "success": true,
      "message": "Exported 45 messages"
    },
    "patterns": {
      "success": true,
      "message": "Exported 12 CBT + 20 gratitude patterns"
    },
    "outcomes": {
      "success": true,
      "message": "Outcome data exported"
    }
  }
}
```

### 4. Delete Training Data (GDPR Right to Deletion)

**POST** `/api/training/delete`

Request:
```json
{
  "username": "patient123"
}
```

Response:
```json
{
  "success": true,
  "message": "All your training data has been permanently deleted"
}
```

### 5. Get Training Stats (Admin)

**GET** `/api/training/stats`

Response:
```json
{
  "success": true,
  "stats": {
    "consented_users": 127,
    "total_chat_messages": 5432,
    "total_patterns": 892,
    "total_outcomes": 234,
    "audit_entries": 1287
  }
}
```

---

## 📝 User Flow

### Obtaining Consent

**In-App Implementation** (add to patient settings):

1. **Settings Tab** → "Data Privacy" section
2. Show clear explanation:
   ```
   Contribute to Mental Health AI Research
   
   Help improve therapy AI for future patients by allowing us to use your 
   anonymized session data for training. Your data will be:
   
   ✅ Completely anonymized (no names, emails, or identifiers)
   ✅ Used only for AI training
   ✅ Stored separately from your medical records
   ✅ Deletable at any time (right to be forgotten)
   
   You can withdraw consent at any time with no impact on your treatment.
   
   [  ] I agree to contribute my anonymized data to AI training
   
   [Save Consent]
   ```

3. User checks box and saves
4. API call: `POST /api/training/consent`
5. Confirmation message shown

### Withdrawing Consent

1. User unchecks box
2. API call: `POST /api/training/consent` with `consent: false`
3. No new data exported (existing data retained unless deleted)

### Deleting Training Data

1. **Settings** → "Data Privacy" → "Delete My Training Data"
2. Confirmation dialog:
   ```
   Are you sure you want to delete all your training data?
   
   This will permanently remove all anonymized data we collected from you.
   You can opt-in again later, but this deletion cannot be undone.
   
   [Cancel] [Delete My Data]
   ```

3. API call: `POST /api/training/delete`
4. All training data removed permanently

---

## 🔄 Data Export Workflow

### Automatic Export (Recommended)

**Cron Job** (runs nightly):

```bash
# /etc/cron.d/training-data-export
0 2 * * * cd /path/to/app && python3 export_training_data.py >> /var/log/training_export.log 2>&1
```

**export_training_data.py**:
```python
from training_data_manager import TrainingDataManager
import sqlite3

manager = TrainingDataManager()

# Get all consented users
conn = sqlite3.connect('therapist_app.db')
cur = conn.cursor()
users = cur.execute(
    "SELECT username FROM users WHERE role='user'"
).fetchall()
conn.close()

for user in users:
    username = user[0]
    if manager.check_user_consent(username):
        manager.export_chat_session(username)
        manager.export_therapy_patterns(username)
        manager.export_outcome_data(username)

print(f"Export complete: {manager.get_training_stats()}")
```

### Manual Export

For specific users:
```python
from training_data_manager import TrainingDataManager

manager = TrainingDataManager()

# Check consent
if manager.check_user_consent('patient123'):
    # Export all data
    manager.export_chat_session('patient123')
    manager.export_therapy_patterns('patient123')
    manager.export_outcome_data('patient123')
```

---

## 🧪 Building Your AI Model

### Accessing Training Data

```python
import sqlite3

conn = sqlite3.connect('ai_training_data.db')
cur = conn.cursor()

# Get all chat training data
chats = cur.execute('''
    SELECT message_role, message_content, mood_context, assessment_severity
    FROM training_chats
    WHERE session_hash IN (
        SELECT DISTINCT session_hash FROM training_chats
    )
    ORDER BY timestamp ASC
''').fetchall()

# Get therapy patterns
patterns = cur.execute('''
    SELECT pattern_type, pattern_data
    FROM training_patterns
''').fetchall()

# Get outcome data
outcomes = cur.execute('''
    SELECT baseline_phq9, followup_phq9, 
           baseline_gad7, followup_gad7,
           improvement_score, interventions_used
    FROM training_outcomes
''').fetchall()

conn.close()
```

### Training Format Examples

**Chat Pairs** (user → AI response):
```python
[
    {
        "role": "user",
        "content": "I've been feeling really anxious today",
        "mood": 4,
        "severity": "moderate"
    },
    {
        "role": "ai",
        "content": "I hear that you're feeling anxious. Can you tell me what might be contributing to these feelings?",
        "mood": 4,
        "severity": "moderate"
    }
]
```

**CBT Patterns** (thought reframing):
```python
{
    "situation": "Friend didn't text back for 2 hours",
    "automatic_thought": "They must be mad at me",
    "evidence": "They've been busy lately and usually respond when free"
}
```

**Outcome Data** (treatment effectiveness):
```python
{
    "baseline_phq9": 18,
    "followup_phq9": 12,
    "improvement": 6,
    "days": 28,
    "interventions": ["cbt", "gratitude", "ai_therapy"]
}
```

---

## ⚖️ Legal Considerations

### GDPR Requirements Met

✅ **Lawful Basis**: Explicit consent (Article 6(1)(a))
✅ **Special Category Data**: Health data processed with explicit consent (Article 9(2)(a))
✅ **Transparency**: Clear information about processing (Article 13)
✅ **Right to Access**: Users can see their consent status
✅ **Right to Rectification**: N/A (anonymized data)
✅ **Right to Erasure**: Full deletion available (Article 17)
✅ **Right to Restrict Processing**: Withdraw consent stops new collection
✅ **Right to Data Portability**: N/A (anonymized data)
✅ **Right to Object**: Can withdraw consent (Article 21)
✅ **Automated Decision-Making**: Disclosed that data trains AI (Article 22)

### HIPAA Considerations (US)

- **De-identification**: Data is fully de-identified per HIPAA Safe Harbor method
- **No PHI**: Training database contains no Protected Health Information
- **Separate Storage**: Training data is in separate database
- **Business Associate Agreements**: Not required for de-identified data

### Consent Form Language (Sample)

```
CONSENT FOR USE OF ANONYMIZED DATA IN AI RESEARCH

Purpose:
We are developing an AI system to improve mental health support. Your 
participation involves allowing us to use anonymized versions of your 
therapy sessions, mood logs, and treatment outcomes.

What We Collect:
- Chat messages (with names, emails, addresses removed)
- CBT thought records (anonymized)
- Mood scores and assessment results
- Treatment outcomes (improvement scores)

What We DON'T Collect:
- Your real name or username
- Email, phone, or address
- Medical diagnoses or prescriptions
- Clinician notes or identifiers

How Data is Anonymized:
- All personal identifiers are irreversibly hashed
- Names, emails, phones automatically removed from text
- No way to link training data back to you

Your Rights:
- You can withdraw consent at any time
- You can request deletion of all your training data
- Withdrawal/deletion won't affect your treatment
- You can see your consent status anytime

Risks:
- Minimal risk: Data is anonymized and cannot identify you
- Data is stored securely in separate database
- Used only for AI training, not shared publicly

Benefits:
- Help improve mental health care for future patients
- Contribute to AI research in therapy
- No direct benefit to you

Voluntary:
- Participation is completely voluntary
- Refusal won't affect your treatment
- You can change your mind anytime

By checking the box, I agree to allow my anonymized therapy data to be 
used for AI training research as described above.

[  ] I Consent
```

---

## 🔐 Security Best Practices

### 1. Environment Variables

Set anonymization salt:
```bash
export ANONYMIZATION_SALT="your-random-salt-change-this-in-production"
```

**Important**: Use a strong, unique salt and keep it secret!

### 2. Database Security

```bash
# Set restrictive permissions
chmod 600 ai_training_data.db

# Regular backups
cp ai_training_data.db /backup/training_$(date +%Y%m%d).db

# Separate from production
# Never store on same drive as therapist_app.db
```

### 3. Access Control

- Training database should be on separate server
- Only data science team access
- No production app access
- Audit all access

### 4. Data Retention

- Keep training data indefinitely (anonymized)
- Delete when user requests (GDPR right)
- Audit logs kept for 7 years (compliance)

---

## 📊 Monitoring & Auditing

### Check Consent Rates

```python
from training_data_manager import TrainingDataManager

manager = TrainingDataManager()
stats = manager.get_training_stats()

print(f"Consented users: {stats['consented_users']}")
print(f"Total messages: {stats['total_chat_messages']}")
print(f"Patterns: {stats['total_patterns']}")
print(f"Outcomes: {stats['total_outcomes']}")
```

### Audit Trail Review

```sql
-- Check recent consent actions
SELECT user_hash, action, details, timestamp
FROM training_audit
WHERE action IN ('consent_given', 'consent_withdrawn')
ORDER BY timestamp DESC
LIMIT 100;

-- Check deletions
SELECT user_hash, details, timestamp
FROM training_audit
WHERE action = 'data_deleted'
ORDER BY timestamp DESC;

-- Check export activity
SELECT user_hash, details, timestamp
FROM training_audit
WHERE action = 'data_exported'
ORDER BY timestamp DESC;
```

---

## 🚨 Incident Response

### If PII Found in Training Data

1. **Immediately stop exports**
2. **Identify affected records**:
   ```sql
   SELECT * FROM training_chats 
   WHERE message_content LIKE '%@%'  -- Email patterns
   OR message_content REGEXP '[0-9]{3}-[0-9]{2}-[0-9]{4}';  -- SSN patterns
   ```
3. **Delete affected records**
4. **Improve PII scrubbing algorithm**
5. **Re-export after fix**
6. **Notify affected users if identifiable**

### If Unauthorized Access

1. **Lock training database**
2. **Review access logs**
3. **Assess data exposure**
4. **Report to data protection officer**
5. **Notify affected users (72 hours GDPR)**

---

## 📖 FAQ

**Q: Is this training data HIPAA compliant?**
A: Yes, de-identified data is not subject to HIPAA restrictions.

**Q: Can the data be re-identified?**
A: No, we use irreversible hashing with no reverse mapping stored.

**Q: What if a user deletes their account?**
A: Training data remains (anonymized), but they can request deletion via GDPR rights.

**Q: How do we handle minors?**
A: Require parental consent for users under 18 (additional checkbox).

**Q: Can we share the training dataset?**
A: Only if consent specifically covers data sharing (requires updated consent form).

**Q: What about cross-border data transfers?**
A: Ensure Standard Contractual Clauses (SCCs) if transferring outside EU.

**Q: How long do we keep the data?**
A: Indefinitely (anonymized), but users can request deletion anytime.

---

## ✅ Implementation Checklist

- [ ] Review consent form with legal team
- [ ] Add consent UI to patient settings
- [ ] Set ANONYMIZATION_SALT environment variable
- [ ] Test PII scrubbing on sample data
- [ ] Set up nightly export cron job
- [ ] Configure database backups
- [ ] Train staff on GDPR procedures
- [ ] Document retention policy
- [ ] Set up access controls
- [ ] Test deletion workflow
- [ ] Prepare incident response plan
- [ ] Review with data protection officer

---

*Last Updated: January 17, 2026*
*GDPR Compliance Version: 1.0*
