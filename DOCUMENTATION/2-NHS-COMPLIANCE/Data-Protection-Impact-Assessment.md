# DATA PROTECTION IMPACT ASSESSMENT (DPIA)

**Status:** DRAFT - For University Review  
**Version:** 1.0  
**Date Created:** February 7, 2026  
**Organization:** Healing Space UK  
**Purpose:** Compliance with UK GDPR (Data Protection Act 2018) when processing patient mental health data

---

## 1. DATA PROCESSING OVERVIEW

### Data Processed by Healing Space

**Patient Mental Health Data:**
- C-SSRS assessment responses (6 questions about suicidal ideation)
- Risk score + categorization (LOW/HIGH/CRITICAL)
- Assessment date/time
- Assigned clinician name
- Safety planning responses
- Mood check-in responses
- Free-text notes (if patient chooses to add comments)

**Clinical Notes:**
- Clinician response to alerts (action taken, time)
- Clinical decisions (safety plan reviewed, follow-up plan)
- Incident documentation (if adverse event)

**System Data (Audit Trail):**
- Who accessed what data, when
- What changes were made
- IP addresses (for security investigation)
- Login attempts (successful + failed)
- Alert log (when alerts sent, to whom, method)

**Personal Information:**
- Name
- Email address
- Phone number (if patient consents to SMS alerts)
- NHS number (if NHS patient)
- Date of birth (for age verification)
- Address (optional)

### Data Subjects
- **Patients:** Age 18+ receiving mental health care
- **Clinicians:** Therapists, counselors, psychologists with access to system

---

## 2. LAWFUL BASIS FOR PROCESSING

### Why are we allowed to process this data?

**Article 6 (Legal Basis):** UK GDPR requires lawful basis. Healing Space relies on:

#### Basis 1: Explicit Consent (Primary)
- Patient **explicitly consents** to assessment sharing with clinician
- Consent form (Patient Information Leaflet) obtained at signup
- Consent is **clear, specific, informed**
- Patient can **withdraw consent anytime** (right of objection)

#### Basis 2: Contract Necessity (Secondary)
- Processing is **necessary to deliver the service** (assessment + clinician feedback)
- Without sharing assessment with clinician, the tool doesn't work

#### Basis 3: Legal Obligation (if triggered)
- If patient at risk of suicide, we may contact emergency services without consent (duty of care)

### Special Categories (Article 9 - Sensitive Data)

Mental health data is **sensitive (Special Category) data.** Additional safeguards required:
- ✅ Explicit consent obtained (Patient Information Leaflet signed)
- ✅ Data encrypted in transit + at rest
- ✅ Access restricted to authorized staff only
- ✅ Regular security audits
- ✅ Incident response plan in place

---

## 3. DATA SUBJECTS' RIGHTS (GDPR Articles 15-22)

### Right to Access (Article 15)
**What:** Patient can request copy of all their data  
**Timeline:** Must comply within **30 calendar days**  
**How:** Patient submits request via web form or email  
**Implementation:** System exports all patient data (assessments, notes, audit trail) as PDF/CSV  
**Cost:** Free (no charge to patient)

### Right to Deletion (Article 17 - "Right to be Forgotten")
**What:** Patient can request deletion of account  
**Timeline:** 30 days to comply (some exceptions)  
**How:** Patient submits deletion request via system  
**Implementation:**
- Personal details deleted (name, email, phone, address)
- Assessment responses anonymized (can't re-identify patient)
- Audit trail retained (can't delete - 6-year legal hold)
- Clinician notified of deletion

### Right to Data Portability (Article 20)
**What:** Patient can request export in portable format (FHIR, CSV)  
**Timeline:** 30 days to comply  
**How:** Patient submits export request  
**Implementation:** System generates FHIR XML or CSV export, patient downloads

### Right to Object (Article 21)
**What:** Patient can object to processing (e.g., "don't share with clinician")  
**Timeline:** Comply immediately or explain why not  
**How:** Patient submits objection  
**Implementation:**
- If objection: Stop sharing data with clinician, but retain for safety (if at-risk)
- Clinician notified: Can't access new assessments unless emergency

---

## 4. SECURITY MEASURES (Technical & Organizational)

### Confidentiality (Data Encryption)

**Data at Rest:**
- Algorithm: **Fernet encryption** (AES-128 in CBC mode)
- Key management: Encryption key stored in environment variable (not in code)
- Recovery: Encrypted backups stored securely
- ✅ **Patient can't be identified if database stolen**

**Data in Transit:**
- Protocol: **HTTPS/TLS 1.2+** for all connections
- Certificate: Valid SSL certificate (Railway-managed)
- Verification: Browser confirms server identity before connection
- ✅ **Data can't be intercepted during transmission**

### Integrity (Audit Logging)

**Every access logged:**
- Who (clinician ID)
- What (which patient, which data)
- When (timestamp)
- Why (function called)
- Outcome (success/failure)
- IP address (for security investigation)

**Immutable audit trail:**
- Logs can't be deleted (only new entries added)
- Changes to assessments create new version (old retained)
- Data changes tracked (old value → new value)

✅ **Non-repudiation: Can prove who did what when**

### Availability (Backup & Recovery)

**Daily automated backups:**
- Database backed up daily to encrypted storage
- Tested monthly (recovery drill to ensure backups work)
- 30-day retention (older backups deleted to manage costs)
- Geographic redundancy (backups in separate data center if possible)

**Failover mechanisms:**
- Real-time database replication (if main server fails, backup takes over)
- Session recovery (if patient's assessment interrupted, can resume where they left off)

✅ **Patient data won't be lost**

### Authenticity (Access Control)

**Role-Based Access Control (RBAC):**
- **Patients:** Can only view own assessments + safety plans
- **Clinicians:** Can only view assigned patients' assessments
- **Administrators:** Full access (only for technical issues), audited heavily
- **System:** No access to decrypted data (encrypted at application level)

**Password Security:**
- Passwords hashed with **Argon2** (industry best practice)
- Fallback: bcrypt (if Argon2 unavailable)
- Minimum 8 characters, complexity encouraged (not enforced to avoid user frustration)
- No plaintext passwords stored
- Password reset link expires after 1 hour

✅ **Only authorized people can access data**

---

## 5. DATA PROTECTION RISKS & MITIGATIONS

### Risk Analysis

| Risk | Likelihood | Impact | Mitigation | Residual Risk |
|------|-----------|--------|----------|---------------|
| **Unauthorized access to patient data** | LOW | HIGH | RBAC + encryption + audit logging | MINIMAL |
| **Data breach (stolen credentials)** | LOW | HIGH | Encryption at rest + password hashing + 2FA (future) | MINIMAL |
| **Accidental data deletion** | MEDIUM | HIGH | Daily encrypted backups + recovery testing | LOW |
| **Clinician accesses wrong patient** | LOW | MEDIUM | Explicit patient assignment + audit logging | MINIMAL |
| **System failure mid-assessment** | LOW | MEDIUM | Session recovery + real-time backup | MINIMAL |
| **Data breach via backup** | LOW | HIGH | Encrypted backups + secure storage | MINIMAL |
| **Insider threat (rogue admin)** | VERY LOW | HIGH | Audit logging (admin access logged + reviewed) | MINIMAL |
| **Third-party compromise** (Railway provider) | LOW | HIGH | Data encrypted (Railway can't read it) + contract requirements | LOW |

---

## 6. DATA RETENTION & DISPOSAL

### Retention Schedule

| Data Type | Retention | Reason |
|-----------|-----------|--------|
| **Assessment responses** | Until patient deletion request | Needed for clinician decision-making |
| **Audit logs** | 6 years minimum | Legal/regulatory requirement (NHS, incident investigation) |
| **Backup copies** | 30 days | Disaster recovery (older backups deleted) |
| **Consent records** | Until withdrawn | Evidence of legal basis for processing |
| **Safety plans** | Until updated/superseded | Clinical necessity (may be referenced in future assessments) |
| **Login records** | 1 year | Security monitoring (detect unusual patterns) |

### Disposal Method

**When patient requests deletion:**
1. Personal identifiers deleted (name, email, phone, DOB)
2. Assessment responses anonymized (can't link to patient)
3. Audit trail retained (can't delete - 6-year legal hold)
4. Backup deleted (after 30 days if no recovery needed)
5. Clinician notified of deletion

---

## 7. DATA SHARING AGREEMENTS

### Internal (University)

**Psychology Department Head** (Clinical Oversight):
- Purpose: Quality assurance + incident review
- Data access: De-identified assessment summaries (names removed)
- Frequency: Monthly
- Contract: University Data Processing Agreement

### External (Third-Parties)

**Railway (Hosting Provider)** - Data Processor:
- Purpose: Store + maintain database
- Data access: Encrypted data (can't read it)
- Agreement: Data Processing Agreement (included in Railway terms)
- Safeguards: Encrypted backups, secure data centers

**Email Service** (for alerts) - Data Processor:
- Purpose: Send clinician alerts + password reset emails
- Data access: Patient name + clinician email (only)
- Agreement: Data Processing Agreement
- Safeguards: Secure email transmission (TLS)

**No sharing with:**
- ❌ Insurance companies
- ❌ Employers
- ❌ Marketing companies
- ❌ Government agencies (unless court order)
- ❌ Third-party researchers (without explicit patient consent)

---

## 8. INCIDENT RESPONSE & BREACH NOTIFICATION

### Data Breach Scenario

If unauthorized access detected:

**Immediate (1 hour):**
- Stop the breach (isolate compromised system)
- Assess scope (how many patients, what data)
- Preserve evidence (logs, screenshots)

**Short-term (24 hours):**
- Root cause analysis (how did this happen?)
- Notification to Information Commissioner's Office (ICO) if 20+ people affected
- Notification to affected patients within 72 hours

**Recovery (7 days):**
- Fix implemented (close the vulnerability)
- Verification: Can't happen again
- Update risk register

---

## Document Status

**Status:** DRAFT - For University Review  
**Version:** 1.0  
**Created:** February 7, 2026  
**Next Review:** After ethics approval (quarterly thereafter)

---

**Version History:**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Feb 7, 2026 | Initial draft for university DPIA requirement | Developer |
