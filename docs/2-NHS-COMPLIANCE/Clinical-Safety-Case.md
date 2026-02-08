# CLINICAL SAFETY CASE: Healing Space C-SSRS Assessment

**Status:** DRAFT - For University Ethics Review  
**Version:** 1.0  
**Date Created:** February 7, 2026  
**Organization:** Healing Space UK  
**Purpose:** Demonstrate clinical safety controls for digital mental health assessment tool

---

## 1. CLINICAL EFFECTIVENESS

### The Assessment Tool: Columbia-Suicide Severity Rating Scale (C-SSRS)

**What is C-SSRS?**
- Validated suicide risk assessment instrument developed at Columbia University
- Published and peer-reviewed in clinical literature (30+ validation studies)
- Used in research hospitals, NHS mental health services, and clinical trials worldwide
- Public domain (freely available for non-commercial use)

**Why use C-SSRS?**
- Specifically designed to assess suicide risk (not general mental health)
- 6-question core assessment identifies: suicidal ideation, intensity, intent, planning, behavior
- Validated across diverse populations (adolescents to older adults)
- Quick to administer (5-10 minutes)
- Supports clinician decision-making (not diagnostic tool, assessment aid)

**Our Implementation:**
- We use the C-SSRS 4.0 core assessment (6 questions)
- Scoring algorithm matches published Columbia University documentation
- Questions presented in plain language (simplified from clinical version)
- Real-time scoring provides immediate risk categorization

---

## 2. SAFETY RISKS & MITIGATION CONTROLS

### Risk Analysis Table

| # | Risk | Clinical Impact | Probability | Mitigation Control | How We Test It | Owner |
|---|------|-----------------|-------------|-------------------|-----------------|-------|
| **1** | **C-SSRS algorithm scores incorrectly** | Underestimation of risk → delayed intervention; overestimation → unnecessary alarm | LOW (algorithm is validated) | Unit tests covering 100% of scoring logic (all 0-5 values for each question, edge cases). Algorithm validation against published C-SSRS manual. | Run test suite before each deployment. Manual validation of 10 random assessments monthly. | Dev Team |
| **2** | **Missed high-risk patient** (HIGH/CRITICAL score not detected by system) | Patient at risk of suicide not alerted to clinician | MEDIUM (system failure possible) | Automated alert system fires within 2 minutes of HIGH/CRITICAL score submission. Multiple alert channels (email + SMS + in-app). Audit log captures all assessments. | Alert responsiveness testing: submit HIGH score, measure time to clinician notification. Test each channel weekly. | Dev Team + Clinical Advisor |
| **3** | **Clinician fails to respond to alert** | Patient at risk but clinician unaware or delayed response | MEDIUM (human factor) | Escalation protocol: if no response in 10 min → escalation alert to secondary contact. If no response in 30 min → flag for emergency procedures. Clear procedure documented. | Weekly audit of alert response times. Monthly incident review. | Clinical Advisor |
| **4** | **System fails mid-assessment** (database down, network interruption) | Assessment data lost, patient/clinician unaware | LOW (recovery controls in place) | Real-time backup of assessment data. Session recovery mechanism (patient can resume from where they left off). Offline capability (assessment captured locally, synced when online). | Backup tested monthly. Failure scenario testing: intentionally down system, verify recovery. | Dev Team |
| **5** | **Unauthorized access to patient mental health data** | Breach of confidentiality, GDPR violation, patient harm | LOW (encryption + access control) | Fernet encryption at rest. TLS 1.2+ encryption in transit. Role-based access control (RBAC): patient views own data only, clinician views assigned patients only. Audit logging of all data access. | Annual security audit. Quarterly penetration testing. Daily audit log review for suspicious access. | Security Officer |
| **6** | **Patient data breach** (stolen credentials, database compromise) | Unauthorized disclosure of mental health data | LOW (encryption + monitoring) | Data encrypted at rest (patient can't be re-identified). Encryption keys managed securely (not in code). Automated backup + encrypted storage. Daily backup integrity checks. GDPR breach notification process (notify affected parties within 72 hours). | Monthly backup recovery drills. Quarterly data breach simulations. | Security Officer |
| **7** | **Incorrect patient-clinician link** (assessment goes to wrong clinician) | Wrong clinician reviews assessment; intended clinician misses high-risk patient | LOW (system-enforced) | Explicit assignment in system (no auto-assignment). Patient confirms clinician assignment at start of assessment. Audit log shows who can access what. | Manual verification on 100% of assessments (sampling not adequate). Monthly random audit. | Clinical Advisor |
| **8** | **Patient safety deteriorates between assessments** (suicide risk increases rapidly between check-ins) | Assessment interval too long, risk not detected | MEDIUM (process control) | Mood check-in reminders (weekly if at-risk, monthly if stable). Escalation rules in dashboard (trending HIGH scores trigger alert). Clinician can request urgent re-assessment. | Monthly review of assessment frequency vs. risk level. Incident review if patient deteriorates between assessments. | Clinical Advisor |

---

## 3. SAFETY MONITORING & INCIDENT MANAGEMENT

### Daily/Weekly/Monthly Review Process

**Daily (Automated):**
- System audit log reviewed: Any alerts that didn't fire? Any access anomalies? Any system errors during assessments?
- CRITICAL/HIGH assessments list generated: Quick check that clinicians were contacted

**Weekly (Manual Review):**
- Clinical Advisor reviews: All CRITICAL/HIGH assessments from past week
  - Did clinician respond within 30 minutes?
  - Was response action appropriate?
  - Any patterns (e.g., specific clinician slow to respond)?
- System stability check: Any downtime? Any failed assessments?
- Alert responsiveness: Spot-check 5 recent alerts, confirm notification reached clinician

**Monthly (Governance Review):**
- Full incident review: Any adverse events? Any near-misses? Any risks realized?
- Risk register updated: Any new risks identified? Any controls failing?
- Performance metrics: Assessment completion rate, alert response time, false positive rate
- Safety meeting: Clinical Advisor + Developer + any relevant staff

### Incident Reporting & Response

**What counts as an incident?**
- Patient harmed or at increased risk due to system failure
- Assessment not completed due to system error
- Alert not sent to clinician
- Data breach or unauthorized access
- Clinician unable to access patient assessment

**Incident Response Protocol:**

```
INCIDENT DETECTED
  ↓
1. IMMEDIATE (within 1 hour)
   - If patient safety at risk: Contact patient/clinician immediately by phone
   - Document: What happened, when, to whom, what evidence?
   - Assess: Is patient safe now? Any immediate action needed?
  ↓
2. SHORT-TERM (within 24 hours)
   - Root cause analysis: Why did this happen? System error? Human error? Process gap?
   - Containment: Prevent it happening to other patients (e.g., pause feature if broken)
   - Communication: Notify affected patients/clinicians
  ↓
3. MEDIUM-TERM (within 7 days)
   - Investigation complete: Document findings
   - Fix implemented: Code change, process change, or control adjustment
   - Verification: Test that fix works, unlikely to reoccur
   - Update risk register: Was this risk already documented? Do controls need strengthening?
  ↓
4. LONG-TERM (ongoing)
   - Post-incident review: Monthly discussion in safety meeting
   - Learning: What did we learn? How do we prevent similar incidents?
   - Monitoring: Enhanced monitoring for similar issues
```

---

## 4. CLINICAL ADVISOR SIGN-OFF

**This Clinical Safety Case is approved by:**

Clinical Advisor: _________________________ (Name, Title, Registration #)  
Qualifications: ___________________________  
Date: _____________________  
Signature: _____________________________

**Developer Sign-Off:**

Developer: _________________________ (Name)  
Date: _____________________  
Signature: _____________________________

---

**Document Version History:**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Feb 7, 2026 | Initial draft for university ethics review | Developer |
