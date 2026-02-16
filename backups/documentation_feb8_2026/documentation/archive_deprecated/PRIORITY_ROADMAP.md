# Healing Space - Priority Roadmap & Enhancement Plan

**Created:** January 25, 2026
**Project Status:** Functional web app deployed on Railway
**Goal:** Transform into professional-grade mental health platform

---

## Executive Summary

This document provides a prioritized roadmap based on a comprehensive audit of the Healing Space codebase. It covers security, clinical compliance, user experience, gamification, and NHS/private practice requirements.

**Current State:** 65 API endpoints, 20 database tables, AI therapy, clinical assessments, pet game, community features. Good foundation but significant gaps for professional deployment.

---

## Priority Matrix

| Priority | Category | Impact | Effort |
|----------|----------|--------|--------|
| P0 | **CRITICAL** - Security/Safety | Blocks everything | 1-2 weeks |
| P1 | **HIGH** - Clinical/Compliance | Required for professional use | 2-4 weeks |
| P2 | **MEDIUM** - User Experience | Improves adoption | 2-4 weeks |
| P3 | **LOW** - Nice-to-Have | Competitive edge | Ongoing |

---

## P0: CRITICAL - Fix Immediately

### Security Vulnerabilities

#### 1. Rate Limiting (Priority: CRITICAL)
**Problem:** No protection against brute-force attacks on login endpoints.

**Solution:**
```python
# Add to api.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")  # Max 5 login attempts per minute
def patient_login():
    ...
```

**Files to modify:** `api.py`
**Effort:** 2 hours
**Impact:** Prevents account takeovers

---

#### 2. CSRF Protection (Priority: CRITICAL)
**Problem:** Forms vulnerable to cross-site request forgery.

**Solution:**
```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# In templates, add to forms:
# <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

**Files to modify:** `api.py`, `templates/index.html`
**Effort:** 4 hours
**Impact:** Prevents malicious form submissions

---

#### 3. Session Timeout (Priority: CRITICAL)
**Problem:** Sessions never expire - tokens could be reused indefinitely.

**Solution:**
```python
# Add session expiry to login response
session_token = {
    'session_id': session_id,
    'expires_at': (datetime.utcnow() + timedelta(hours=2)).isoformat(),
    'username': username
}

# Add middleware to check expiry on every request
@app.before_request
def check_session_expiry():
    if request.endpoint in PROTECTED_ENDPOINTS:
        session_id = request.headers.get('X-Session-ID')
        if is_session_expired(session_id):
            return jsonify({'error': 'Session expired'}), 401
```

**Files to modify:** `api.py`
**Effort:** 4 hours
**Impact:** Reduces risk of session hijacking

---

#### 4. Remove Debug Fallbacks in Production (Priority: CRITICAL)
**Problem:** Debug mode generates insecure keys that could leak to production.

**Current code:**
```python
if not key:
    if DEBUG:
        key = Fernet.generate_key().decode()  # DANGEROUS!
```

**Solution:**
```python
if not key:
    if DEBUG:
        key = Fernet.generate_key().decode()
    else:
        raise RuntimeError("ENCRYPTION_KEY must be set in production!")
```

**Files to modify:** `api.py`, `secrets_manager.py`
**Effort:** 1 hour
**Impact:** Prevents accidental production security breach

---

### Safety Monitoring

#### 5. AI Disclaimer (Priority: CRITICAL)
**Problem:** No clear disclaimer that AI is not a replacement for professional therapy.

**Solution:** Add to chat interface and login flow:
```html
<div class="ai-disclaimer">
    <strong>Important:</strong> This AI companion is for support only and is NOT
    a replacement for professional mental health treatment. If you're in crisis,
    please contact Samaritans (116 123) or your local emergency services.
</div>
```

**Files to modify:** `templates/index.html`
**Effort:** 1 hour
**Impact:** Legal protection, user safety

---

#### 6. Enhanced Crisis Detection (Priority: CRITICAL)
**Problem:** Crisis detection relies only on keyword matching - too simplistic.

**Current:** Checks for words like "suicide", "kill myself", "end it all"

**Solution:** Add severity scoring:
```python
class SafetyMonitor:
    RISK_LEVELS = {
        'critical': ['kill myself', 'end my life', 'suicide plan', 'goodbye forever'],
        'high': ['want to die', 'hurt myself', 'self harm', 'no point living'],
        'moderate': ['hopeless', 'worthless', 'burden', 'give up'],
        'low': ['struggling', 'anxious', 'depressed', 'overwhelmed']
    }

    def assess_risk(self, message):
        for level, keywords in self.RISK_LEVELS.items():
            if any(kw in message.lower() for kw in keywords):
                return level
        return 'none'
```

**Files to modify:** `api.py`
**Effort:** 4 hours
**Impact:** Better crisis intervention

---

## P1: HIGH - Required for Professional Use

### Clinical Compliance

#### 7. Add More Clinical Scales (Priority: HIGH)
**Problem:** Only PHQ-9 and GAD-7 - need more for comprehensive assessment.

**Add these validated scales:**
| Scale | Purpose | Questions |
|-------|---------|-----------|
| HADS | Hospital Anxiety/Depression (NHS standard) | 14 |
| PSQI | Pittsburgh Sleep Quality Index | 19 |
| PCL-5 | PTSD Checklist | 20 |
| AUDIT | Alcohol Use Disorders | 10 |
| CAGE | Quick alcohol screening | 4 |

**Files to modify:** `api.py`, `templates/index.html`
**Effort:** 2-3 days per scale
**Impact:** Clinical credibility, NHS readiness

---

#### 8. Clinician Review Workflow (Priority: HIGH)
**Problem:** AI-generated notes not reviewed/approved by clinicians.

**Solution:**
```python
# Add to clinician_notes table
ALTER TABLE clinician_notes ADD COLUMN status TEXT DEFAULT 'draft';
ALTER TABLE clinician_notes ADD COLUMN reviewed_by TEXT;
ALTER TABLE clinician_notes ADD COLUMN reviewed_at TIMESTAMP;

# Workflow: draft → pending_review → approved → locked
```

**Files to modify:** `api.py`
**Effort:** 1 day
**Impact:** Clinical governance compliance

---

#### 9. Structured Risk Assessment (Priority: HIGH)
**Problem:** No formal suicide/self-harm risk scoring.

**Solution:** Implement Columbia-Suicide Severity Rating Scale (C-SSRS):
```python
class RiskAssessment:
    def calculate_cssr_score(self, responses):
        """
        C-SSRS Categories:
        1. Wish to be dead
        2. Non-specific active suicidal thoughts
        3. Active suicidal ideation with method
        4. Active suicidal ideation with intent
        5. Active suicidal ideation with plan and intent
        """
        score = sum(1 for r in responses if r)
        if score >= 4:
            return 'imminent_risk'
        elif score >= 2:
            return 'high_risk'
        elif score >= 1:
            return 'moderate_risk'
        return 'low_risk'
```

**Files to modify:** `api.py`, `templates/index.html`
**Effort:** 2 days
**Impact:** Critical for clinical safety

---

### Data Protection

#### 10. Data Processing Agreements (Priority: HIGH)
**Problem:** No documented DPAs with Groq (AI), Railway (hosting).

**Action Items:**
- [ ] Request DPA from Groq API
- [ ] Request DPA from Railway
- [ ] Document data flows (what data goes where)
- [ ] Create data residency statement (EU/UK only)
- [ ] Add to Privacy Policy

**Files to create:** `documentation/DATA_PROCESSING_AGREEMENTS.md`
**Effort:** 1 week (involves vendor communication)
**Impact:** GDPR compliance

---

#### 11. Privacy Impact Assessment (Priority: HIGH)
**Problem:** No formal PIA documenting data risks.

**Create document covering:**
- Data collected (PII inventory)
- Processing purposes
- Legal basis (consent, legitimate interest)
- Retention periods
- Security measures
- Risk assessment
- Mitigation strategies

**Files to create:** `documentation/PRIVACY_IMPACT_ASSESSMENT.md`
**Effort:** 2 days
**Impact:** ICO compliance, NHS requirement

---

### Code Quality

#### 12. Refactor api.py into Blueprints (Priority: HIGH)
**Problem:** 6,105-line monolithic file is unmaintainable.

**Solution:** Split into Flask blueprints:
```
api/
├── __init__.py          # App factory
├── auth.py              # Authentication endpoints
├── therapy.py           # AI chat endpoints
├── clinical.py          # PHQ-9, GAD-7, risk assessment
├── mood.py              # Mood logging, habits
├── pet.py               # Pet game endpoints
├── community.py         # Posts, likes, replies
├── admin.py             # Developer/admin endpoints
├── export.py            # CSV, PDF, FHIR exports
└── utils/
    ├── database.py      # DB connections, queries
    ├── encryption.py    # Fernet encryption
    ├── auth.py          # Password hashing
    └── safety.py        # SafetyMonitor class
```

**Effort:** 3-5 days
**Impact:** Maintainability, team collaboration, easier testing

---

#### 13. Add Database Indexes (Priority: HIGH)
**Problem:** Queries will slow significantly with 1000+ patients.

**Solution:**
```sql
-- Add to database initialization
CREATE INDEX IF NOT EXISTS idx_mood_logs_username ON mood_logs(username);
CREATE INDEX IF NOT EXISTS idx_chat_history_username ON chat_history(username);
CREATE INDEX IF NOT EXISTS idx_clinical_scales_username ON clinical_scales(username);
CREATE INDEX IF NOT EXISTS idx_alerts_username ON alerts(username);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_appointments_clinician ON appointments(clinician);
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient);
```

**Files to modify:** `api.py` (init_database function)
**Effort:** 2 hours
**Impact:** 10-100x faster queries at scale

---

## P2: MEDIUM - Improves User Experience

### Authentication UX

#### 14. Biometric Login for Mobile (Priority: MEDIUM)
**Problem:** PIN entry on every login is friction.

**Solution:** Already have Capacitor plugin infrastructure. Add:
```javascript
// In templates/index.html
import { BiometricAuth } from '@capacitor-community/biometric';

async function tryBiometricLogin() {
    const result = await BiometricAuth.authenticate({
        reason: 'Log in to Healing Space'
    });
    if (result.verified) {
        // Use stored credentials
        autoLogin();
    }
}
```

**Files to modify:** `templates/index.html`, add Capacitor plugin
**Effort:** 1 day
**Impact:** Faster mobile login experience

---

#### 15. "Remember Device" for PIN (Priority: MEDIUM)
**Problem:** PIN required every single login, even on same device.

**Solution:**
```javascript
// Store device fingerprint
const deviceId = await generateDeviceFingerprint();
localStorage.setItem('trusted_device', deviceId);

// Backend checks if device is trusted
if (is_trusted_device(device_id)):
    skip_pin_verification = True
```

**Files to modify:** `api.py`, `templates/index.html`
**Effort:** 4 hours
**Impact:** Reduced login friction

---

### Chat Experience

#### 16. Typing Indicator (Priority: MEDIUM)
**Problem:** No feedback while AI is generating response.

**Solution:**
```javascript
// Show typing indicator
function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';
    chatContainer.appendChild(indicator);
}

// In sendMessage():
showTypingIndicator();
const response = await fetch('/api/therapy/chat', ...);
hideTypingIndicator();
```

**Files to modify:** `templates/index.html`
**Effort:** 2 hours
**Impact:** Better perceived responsiveness

---

#### 17. Message Search (Priority: MEDIUM)
**Problem:** Can't search through chat history.

**Solution:**
```python
@app.route('/api/therapy/search', methods=['GET'])
def search_chat_history():
    query = request.args.get('q')
    username = request.args.get('username')

    conn = get_db_connection()
    results = conn.execute('''
        SELECT * FROM chat_history
        WHERE username = ? AND message LIKE ?
        ORDER BY timestamp DESC LIMIT 50
    ''', (username, f'%{query}%')).fetchall()

    return jsonify([dict(r) for r in results])
```

**Files to modify:** `api.py`, `templates/index.html`
**Effort:** 4 hours
**Impact:** Easier to find past conversations

---

### Mood Tracking

#### 18. Quick Mood Log (Priority: MEDIUM)
**Problem:** Current mood log requires 6+ fields - too much friction.

**Solution:** Add "quick log" option:
```javascript
function quickMoodLog() {
    // Just mood (1-10) and one note
    // Other fields optional or use yesterday's values as defaults
    showQuickMoodModal();
}
```

**Files to modify:** `templates/index.html`
**Effort:** 3 hours
**Impact:** Higher daily engagement

---

#### 19. Mood Streak Rewards (Priority: MEDIUM)
**Problem:** No incentive for consistent daily logging.

**Solution:**
```python
def calculate_streak_bonus(username):
    # Check consecutive days logged
    streak = get_mood_streak(username)

    if streak >= 7:
        return 50  # 50 coins for week streak
    elif streak >= 30:
        return 200  # 200 coins for month streak
    return 0
```

**Files to modify:** `api.py`
**Effort:** 4 hours
**Impact:** Gamified habit formation

---

## P3: GAMIFICATION ENHANCEMENTS

### Pet Game Improvements

#### 20. Pet-Therapy Connection (Priority: HIGH for engagement)
**Problem:** Pet game feels disconnected from therapy goals.

**Solution:** Make pet health reflect user engagement:
```python
def update_pet_from_therapy(username):
    """Pet health improves when user does therapy activities."""
    activities_today = count_activities_today(username)
    mood_logged = has_mood_logged_today(username)
    cbt_done = has_cbt_exercise_today(username)

    # Pet thrives when user engages
    happiness_boost = (
        (10 if mood_logged else 0) +
        (15 if cbt_done else 0) +
        (5 * activities_today)
    )

    update_pet_stats(username, happiness_delta=happiness_boost)
```

**Visual feedback:**
```html
<div class="pet-feedback">
    "Your pet feels happier because you did a breathing exercise! +15 happiness"
</div>
```

**Files to modify:** `api.py`, `templates/index.html`
**Effort:** 1 day
**Impact:** Therapeutic gamification

---

#### 21. Pet Evolution/Leveling (Priority: MEDIUM)
**Problem:** No progression - pet stays the same forever.

**Solution:**
```python
# Pet stages based on XP
PET_STAGES = {
    'baby': (0, 100),      # XP 0-100
    'child': (100, 500),   # XP 100-500
    'teen': (500, 1500),   # XP 500-1500
    'adult': (1500, 5000), # XP 1500-5000
    'elder': (5000, None)  # XP 5000+
}

def get_pet_stage(xp):
    for stage, (min_xp, max_xp) in PET_STAGES.items():
        if max_xp is None or xp < max_xp:
            return stage
    return 'elder'
```

**Add visual changes:** Different sprites for each stage

**Files to modify:** `api.py`, `templates/index.html`
**Effort:** 2 days
**Impact:** Long-term engagement

---

#### 22. Achievements System (Priority: MEDIUM)
**Problem:** No achievements or badges for accomplishments.

**Solution:**
```python
ACHIEVEMENTS = {
    'first_mood': {'name': 'First Steps', 'desc': 'Log your first mood', 'coins': 50},
    'week_streak': {'name': 'Consistent', 'desc': '7-day mood streak', 'coins': 100},
    'month_streak': {'name': 'Dedicated', 'desc': '30-day mood streak', 'coins': 500},
    'first_cbt': {'name': 'Mind Trainer', 'desc': 'Complete first CBT exercise', 'coins': 50},
    'community_helper': {'name': 'Supporter', 'desc': 'Reply to 10 community posts', 'coins': 100},
    'pet_master': {'name': 'Pet Whisperer', 'desc': 'Keep pet at 100% happiness for 7 days', 'coins': 200},
}
```

**Files to modify:** `api.py`, `templates/index.html`
**Effort:** 1 day
**Impact:** Milestone motivation

---

#### 23. Expand Pet Shop (Priority: LOW)
**Problem:** Only 10 items - limited variety.

**Add categories:**
- **Food:** 10 items (basic → gourmet)
- **Toys:** 10 items (ball → interactive games)
- **Medicine:** 5 items (vitamins → treatments)
- **Cosmetics:** 15 items (hats, collars, backgrounds)
- **Seasonal:** 10 items (holiday specials)

**Total: 50 items**

**Files to modify:** `api.py`
**Effort:** 1 day
**Impact:** Variety and collectibility

---

#### 24. Pet Adventures Expansion (Priority: LOW)
**Problem:** Adventures are random with no strategy.

**Add adventure types:**
```python
ADVENTURES = {
    'park_walk': {
        'duration': 5,  # minutes
        'energy_cost': 10,
        'rewards': {'coins': (5, 15), 'happiness': (5, 10)},
        'events': ['found_treat', 'made_friend', 'got_tired']
    },
    'treasure_hunt': {
        'duration': 15,
        'energy_cost': 25,
        'rewards': {'coins': (20, 50), 'xp': (10, 30)},
        'events': ['found_chest', 'got_lost', 'found_rare_item']
    },
    'training': {
        'duration': 10,
        'energy_cost': 20,
        'rewards': {'xp': (15, 25)},
        'events': ['learned_trick', 'too_tired', 'mastered_skill']
    }
}
```

**Files to modify:** `api.py`, `templates/index.html`
**Effort:** 2 days
**Impact:** Strategic gameplay

---

## P4: NHS/PRIVATE PRACTICE REQUIREMENTS

### Documentation (Required for Institutional Adoption)

#### 25. Clinical Governance Documentation (Priority: HIGH)
**Create these documents:**

| Document | Purpose |
|----------|---------|
| Clinical Protocol | How AI therapy sessions work |
| Risk Management Policy | How crises are handled |
| Data Protection Policy | GDPR/HIPAA compliance |
| Adverse Event Reporting | Incident procedures |
| User Safety Guidelines | Safe use of platform |

**Files to create:** `documentation/clinical/` folder
**Effort:** 1 week
**Impact:** NHS procurement requirement

---

#### 26. Security Assessment (Priority: HIGH)
**Required actions:**

1. **Penetration Testing** (£5K-10K external)
   - OWASP Top 10 vulnerability assessment
   - API security testing
   - Authentication bypass attempts

2. **Vulnerability Scan** (Use OWASP ZAP - free)
   - Automated scanning
   - Fix all critical/high findings

3. **Security Policy**
   - Incident response plan
   - Vulnerability disclosure
   - Security contacts

**Files to create:** `documentation/security/`
**Effort:** 2-4 weeks
**Impact:** Security certification

---

#### 27. FHIR API Expansion (Priority: MEDIUM)
**Problem:** FHIR export exists but not full API.

**Add FHIR endpoints:**
```python
@app.route('/fhir/Patient/<username>', methods=['GET'])
def fhir_patient(username):
    """Return patient data in FHIR Patient resource format."""
    ...

@app.route('/fhir/Observation', methods=['GET'])
def fhir_observations():
    """Return mood logs as FHIR Observation resources."""
    ...

@app.route('/fhir/QuestionnaireResponse', methods=['GET'])
def fhir_questionnaire_responses():
    """Return PHQ-9/GAD-7 as FHIR QuestionnaireResponse."""
    ...
```

**Files to modify:** `api.py`, `fhir_export.py`
**Effort:** 3-5 days
**Impact:** NHS system integration

---

## Implementation Timeline

### Phase 1: Security & Safety (Weeks 1-2)
- [ ] Rate limiting
- [ ] CSRF protection
- [ ] Session timeout
- [ ] AI disclaimer
- [ ] Enhanced crisis detection

### Phase 2: Clinical Compliance (Weeks 3-6)
- [ ] Add HADS scale
- [ ] Clinician review workflow
- [ ] Risk assessment (C-SSRS)
- [ ] Data Processing Agreements
- [ ] Privacy Impact Assessment

### Phase 3: Code Quality (Weeks 7-10)
- [ ] Refactor api.py into blueprints
- [ ] Add database indexes
- [ ] Add unit tests (60% coverage)
- [ ] Structured logging

### Phase 4: UX Improvements (Weeks 11-14)
- [ ] Biometric login
- [ ] Typing indicator
- [ ] Quick mood log
- [ ] Mood streaks

### Phase 5: Gamification (Weeks 15-18)
- [ ] Pet-therapy connection
- [ ] Pet evolution
- [ ] Achievements system
- [ ] Expanded shop

### Phase 6: NHS Readiness (Months 5-6)
- [ ] Clinical governance docs
- [ ] Security assessment
- [ ] FHIR API expansion
- [ ] Penetration testing

---

## Cost Estimates

| Category | DIY Cost | Outsourced Cost |
|----------|----------|-----------------|
| Security fixes | £0 | £2K-5K |
| Clinical scales | £0 | £5K-10K |
| Penetration testing | £0 (ZAP) | £5K-15K |
| ISO 27001 cert | N/A | £10K-20K |
| Clinical trial | N/A | £50K-100K |
| Legal review | N/A | £5K-10K |
| **Total (minimal)** | **£0** | **£77K-160K** |

---

## Success Metrics

### Engagement
- Daily active users (DAU)
- Mood log completion rate (target: 70%)
- Average session duration
- Pet interaction frequency

### Clinical
- PHQ-9 score improvement over 8 weeks
- GAD-7 score improvement over 8 weeks
- Crisis intervention rate
- Clinician satisfaction score

### Technical
- API response time (target: <500ms)
- Uptime (target: 99.5%)
- Error rate (target: <0.1%)
- Security vulnerabilities (target: 0 critical)

---

## Next Steps

1. **This week:** Implement P0 security fixes
2. **Next week:** Add AI disclaimer and enhanced crisis detection
3. **This month:** Complete clinical scales and compliance docs
4. **This quarter:** Refactor codebase and add gamification
5. **This year:** Pursue NHS certification path

---

**Document Version:** 1.0
**Last Updated:** January 25, 2026
**Author:** Claude Code Assistant
