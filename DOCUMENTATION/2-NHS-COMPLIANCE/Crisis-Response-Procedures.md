# CRISIS RESPONSE PROTOCOL

**Status:** DRAFT - For University Ethics Review  
**Version:** 1.0  
**Date Created:** February 7, 2026  
**Organization:** Healing Space UK  
**Purpose:** Define system and clinical response to suicidal ideation detected via C-SSRS assessment

---

## 1. RISK STRATIFICATION & ALERT TRIGGERS

### Scoring Thresholds

Based on Columbia-Suicide Severity Rating Scale (C-SSRS):

**LOW RISK (Score 0-2)**
- Endorses: No suicidal thoughts OR rare thoughts without planning/intent
- Response: No alert. Routine clinician follow-up (within 1 week)
- Patient message: "Your responses don't indicate high suicide risk at this time"

**HIGH RISK (Score 3-4)**
- Endorses: Frequent suicidal thoughts OR planning/intent without frequency confirmation
- Response: **URGENT alert to clinician** (within 5 minutes)
- Patient message: "Your responses indicate elevated suicide risk. Your clinician will review this urgently."
- Required: Patient completes safety planning before closing assessment

**CRITICAL RISK (Score 5+ OR intent + plan + behavior)**
- Endorses: Daily suicidal thoughts AND active plan AND behavioral intent OR recent attempts
- Response: **IMMEDIATE alert to clinician** (within 1 minute) + escalation protocol
- Patient message: "You may be at immediate risk of suicide. Please contact your clinician immediately. If in immediate danger, call 999."
- Required: Patient completes safety planning. Clinician response required within 10 minutes.

---

## 2. SYSTEM ALERT PROTOCOL (Automated)

### 2.1 CRITICAL Risk Alert Sequence

```
[0 min] CRITICAL SCORE DETECTED
         ↓
[0 min] Generate alert: Patient name, score, risk category
         ↓
[0 min] Send email to assigned clinician (URGENT flag, bold red)
         Email content: "[URGENT] Patient [Name] - Suicide Risk Assessment CRITICAL
                        Score: [X]
                        Action required within 10 minutes
                        Link: [assessment review link]"
         ↓
[1 min] Send SMS to clinician phone (if on file)
        Content: "[URGENT] [Patient Name] scored CRITICAL on suicide assessment.
                 Review immediately. Check email for details."
         ↓
[1 min] In-app alert in clinician dashboard
        Highlighted RED, cannot be dismissed (must acknowledge)
         ↓
[10 min] If no response: Log escalation attempt
         ↓
[10 min] Send escalation email to secondary contact
         (supervisor, on-call clinician, or department head)
         Content: "[ESCALATION] No response to CRITICAL alert for [Patient Name].
                  Original alert sent 10 minutes ago.
                  Please respond immediately or contact clinician directly."
         ↓
[10 min] If patient still not contacted:
         System flags case for emergency procedures
         Log entry: "CRITICAL ALERT - 10 MIN NO RESPONSE - ESCALATE"
```

### 2.2 HIGH Risk Alert Sequence

```
[0 min] HIGH SCORE DETECTED
         ↓
[0 min] Generate alert: Patient name, score, HIGH risk
         ↓
[0 min] Send email to clinician (high priority, yellow/orange flag)
         Email content: "[HIGH PRIORITY] Patient [Name] - Suicide Risk Assessment HIGH
                        Score: [X]
                        Clinician review required. Patient must complete safety planning.
                        Link: [assessment review link]"
         ↓
[2 min] In-app alert in clinician dashboard
         Highlighted YELLOW/ORANGE, can be dismissed after acknowledging
         ↓
[30 min] If no response: Send reminder email
         ↓
[30 min] Log outcome if alert still not reviewed
         Flag for weekly clinical audit
```

---

## 3. CLINICIAN RESPONSE PROTOCOL

### 3.1 Initial Response (Required within 10 min for CRITICAL, 30 min for HIGH)

**Clinician must:**

1. **Acknowledge alert** (system logs time of acknowledgment)
   - Click "Reviewed" button in dashboard or email
   - System records: Date, time, clinician name

2. **Review assessment**
   - See patient's responses to all 6 C-SSRS questions
   - See calculated score + risk category
   - Review any previous assessments (trend analysis)
   - Review patient's safety plan (if exists)

3. **Immediate patient contact** (CRITICAL within 10 min, HIGH within 30 min)
   - **MUST BE PHONE CALL (not email/message)**
   - Patient may be in active crisis; voice contact needed
   - Document call:
     - Time contacted
     - Patient status (emotional state, immediate risk level)
     - Patient location (safe place? able to travel?)
     - Expressed intent (if any change from assessment)

4. **Decide response action** (one of the following):
   - **A) Schedule urgent in-person appointment** (same day if possible)
   - **B) Notify emergency contact** (patient's nominated family/friend, with consent)
   - **C) Emergency services** (call 999 if patient in immediate danger, unable to keep safe)
   - **D) Document patient status** (if unreachable - log attempts, next steps)

5. **Record clinical decision** in system:
   - Action taken (A/B/C/D)
   - Time taken
   - Patient response
   - Next review date
   - Any safety plan adjustments

### 3.2 Secondary Contact (If Primary Clinician Unavailable)

If assigned clinician doesn't respond within:
- **CRITICAL: 10 minutes** → escalate to supervisor/on-call
- **HIGH: 30 minutes** → send reminder

**Escalation process:**
1. System sends alert to pre-designated secondary clinician (e.g., practice manager, on-call psychiatrist)
2. Secondary clinician reviews assessment + attempts to reach patient
3. Documents action taken
4. Notifies primary clinician of escalation

---

## 4. PATIENT SAFETY PLANNING (Mandatory for HIGH/CRITICAL)

### System-Enforced Safety Planning Flow

If score is HIGH or CRITICAL, patient MUST complete before closing assessment:

**Step 1: Warning Signs**
- Question: "What warning signs tell you that a crisis is developing?"
- Examples provided: Inability to sleep, increased substance use, social withdrawal, etc.
- Patient writes own list (3-5 items)

**Step 2: Internal Coping Strategies**
- Question: "What can you do on your own to cope when you feel like this?"
- Examples: Distraction (hobby, exercise), mindfulness, journaling, etc.
- Patient selects + personalizes (at least 2)

**Step 3: People & Social Settings to Distract From Suicidal Thoughts**
- Question: "Who do you trust? Where can you go to feel safer?"
- Patient lists people (family, friends, support groups) + places
- Minimum: 2 people, 1 safe place

**Step 4: Professional Resources**
- Pre-populated with:
  - Assigned clinician phone + availability
  - Crisis line: Samaritans 116 123 (24/7)
  - Emergency: 999
  - Local A&E contact
- Patient can add additional resources

**Step 5: Means Safety**
- Question: "Are there ways to make your environment safer right now?"
- Examples: Secure medications, remove sharp objects, tell someone of your location
- Patient reviews + documents (optional, but recommended)

**Step 6: Clinician Review**
- Safety plan emailed to patient
- Safety plan shared with assigned clinician
- **Clinician must review safety plan within 24 hours** + document:
  - "Safety plan adequate? Yes/No"
  - Any modifications needed?
  - Follow-up plan (when to re-assess)

---

## 5. MONITORING & FOLLOW-UP

### High Risk Patient Monitoring

After HIGH/CRITICAL assessment:

**Weekly check-in (first 4 weeks):**
- Simple mood question: "How have you been feeling this week? (1-10 scale)"
- If response ≤5 → trigger clinician review
- Automated reminder email to patient (Friday)

**Monthly safety planning review (ongoing):**
- Patient reviews safety plan
- Updates if circumstances changed
- Clinician confirms plan still adequate

**If trending toward HIGH again:**
- System alerts clinician: "Trend alert: [Patient Name] scores trending up (3 of last 5 = HIGH)"
- Clinician initiates urgent review

---

## 6. SYSTEM FAILURE SCENARIOS

### If Alert System Fails

**Scenario:** Assessment submitted but alert not sent to clinician

**Failsafe 1 (Automated):**
- System sends backup alert to system admin within 10 min
- Admin manually emails all assigned clinicians: "SYSTEM ALERT FAILURE - Please check dashboard manually"

**Failsafe 2 (Manual Process):**
- Printed patient list + emergency contacts maintained at clinic
- If system down >1 hour, clinic staff manually calls clinicians
- Patients directed to call Samaritans (116 123) or 999 if urgent

**Failsafe 3 (Post-Incident):**
- Root cause analysis (why did alert fail?)
- System fix verified before re-deployment
- Affected patients contacted within 24 hours

---

## 7. INCIDENT DOCUMENTATION & REVIEW

### Mandatory Documentation

Every CRITICAL or HIGH assessment must be documented with:

1. **Assessment Details**
   - Date/time submitted
   - Patient responses (all 6 questions)
   - Score + risk category

2. **Alert Details**
   - Time alert generated
   - Clinician alerted (name)
   - Time alert delivered
   - Time clinician acknowledged
   - Time clinician responded

3. **Clinical Response**
   - Date/time patient contacted
   - Method (phone call)
   - Patient status
   - Action taken (A/B/C/D from section 3.1)
   - Safety plan completed? Y/N
   - Follow-up plan

4. **Outcome**
   - Patient safe? Confirmed by clinician
   - Any adverse events?
   - Any escalations needed?
   - Next review date

### Weekly Safety Review

Every Friday, Clinical Advisor reviews:
- All HIGH/CRITICAL assessments from past week
- Response time metrics (avg, min, max)
- Any delayed responses (>30 min for HIGH, >10 min for CRITICAL)
- Any failed alerts or system issues
- Patient outcomes (safe, engaged with plan, etc.)

---

## 8. CLINICAL ADVISOR SIGN-OFF

**This protocol is realistic and achievable:**

Clinical Advisor: _________________________ (Name, Title, Registration #)  
Qualifications: ___________________________  
Affiliation: ______________________________  
Date: _____________________  
Signature: _____________________________

**Note:** Clinical advisor must confirm that the 10-minute response time for CRITICAL alerts is achievable in their practice setting. If not, we adjust the protocol.

---

**Document Version History:**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Feb 7, 2026 | Initial draft for university ethics review | Developer |
