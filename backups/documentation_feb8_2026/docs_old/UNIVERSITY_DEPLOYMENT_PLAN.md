# University Deployment Plan: Lincoln University Psychology Department

**Status:** DRAFT - UNIVERSITY TRIAL FIRST  
**Last Updated:** February 7, 2026  
**Target:** Head of Psychology, Lincoln University  
**Timeline:** ASAP (6-8 weeks to MVP with governance documents)  
**Compliance Level:** University Institutional + NHS-Ready Framework

---

## 1. Strategic Overview

### Why University First?

| Aspect | University Trial | Full NHS Deployment |
|--------|------------------|-------------------|
| **Governance** | Department Head + Ethics Committee | Formal governance board + clinical leads |
| **Regulation** | University Research Ethics | NHS Digital standards (full compliance) |
| **Speed** | 6-8 weeks MVP | 12-16 weeks (includes NHS audit) |
| **Users** | Psychology students/staff + limited patients | Hundreds of NHS clinics/patients |
| **Liability** | University institutional indemnity | Professional indemnity insurance (£5-10K) |
| **Documentation** | Simplified clinical safety case | DCB0129 full clinical safety management |
| **Testing** | Clinical validation with university staff | Full NHS-level validation |

### Your Advantage

This approach **proves the concept** with real users while building the governance documents NHS will eventually require. By the time you approach NHS, you'll have:

✅ Validated C-SSRS algorithm in production  
✅ Real clinical feedback integrated  
✅ Proven safety controls working  
✅ University institutional backing (credibility for NHS)  
✅ Real-world incident history (if any) properly managed  

---

## 2. Lincoln University Approach Strategy

### 2.1 Pre-Contact Preparation (Week 1-2)

**Before emailing the Head of Psychology, you need:**

1. **One-page clinical summary** of your C-SSRS implementation
   - Key features: Risk scoring, clinician alerts, safety planning
   - Safety mechanisms: Audit trail, crisis response, role-based access
   - Data security: GDPR compliant, encrypted, secure backups

2. **Risk summary** (1-page)
   - Top 5 risks identified
   - How each is mitigated
   - What happens if system fails

3. **Governance proposal** (1-page)
   - What ethical approval you'll need
   - What the department will own (oversight)
   - What you'll provide (technical + maintenance)

4. **Timeline & resource requirements**
   - How much time from their team
   - Who needs to be involved
   - Commitment duration (e.g., 12-month trial)

5. **Ethics approval path**
   - University ethics committee requirements
   - Expected timeline (4-6 weeks)
   - What you'll submit

### 2.2 Contact Email Template

```
Subject: Digital Mental Health Research Tool - Partnership Opportunity

Dear [Head of Psychology Name],

I am developing Healing Space, a digital mental health companion tool using 
validated assessment protocols (Columbia-Suicide Severity Rating Scale). 
I am approaching the Psychology Department at Lincoln University as a partner 
for clinical validation and user testing.

The tool incorporates:
✓ Validated C-SSRS suicide risk assessment
✓ Clinician alert system for high-risk patients
✓ GDPR-compliant data handling (encrypted, audited)
✓ Comprehensive safety protocols

I am seeking a 12-month research partnership:
- Your role: Provide ethical oversight, clinical guidance, user testing
- My role: Technical development, maintenance, compliance documentation
- Expected outcome: Validated digital mental health tool ready for NHS deployment

Before formal engagement, I have prepared:
1. Technical overview & safety case (attached)
2. Risk management summary
3. University research ethics requirements
4. Resource commitment proposal

Would you be available for a 20-minute call to discuss this opportunity?

Best regards,
[Your Name]
[Your Title]
[Your Contact]
```

### 2.3 What the Psychology Department Will Expect

**Institutional Expectations:**

1. **Ethics Committee Approval**
   - University Research Ethics Committee will review
   - Expected questions: Patient safety, data handling, informed consent
   - Timeline: 4-6 weeks for approval

2. **Clinical Oversight**
   - Designated faculty member as "Clinical Advisor" (not full clinical lead yet)
   - Monthly check-ins on safety metrics
   - Access to all incident reports
   - Authority to pause trial if safety concerns emerge

3. **Data Security Assurance**
   - Compliance with UK GDPR (you've already got this)
   - Confirmation of encryption & audit logging
   - Data processor agreement (university owns data)
   - Breach notification protocol

4. **Insurance & Liability**
   - University institutional insurance may cover the trial
   - Confirm with their insurance team
   - You're not legally liable if university approves the protocol

5. **Publication Rights**
   - University may want to publish findings
   - You should negotiate IP ownership (usually you retain app, university gets research publication)
   - Joint publication with university boosts NHS credibility later

---

## 3. Critical Governance Documents for University Trial

### 3.1 What You MUST Have (Non-Negotiable)

These 4 documents are essential for ANY mental health digital tool, even in university:

#### Document 1: Clinical Safety Case (2-3 pages)

**Purpose:** Show that you've thought through safety and have controls in place.

```markdown
# CLINICAL SAFETY CASE: Healing Space C-SSRS Assessment

## 1. Clinical Effectiveness
- C-SSRS is a validated, published assessment tool
- Used in research institutions worldwide
- Your implementation matches published scoring algorithm

## 2. Top Safety Risks & Controls

| Risk | Mitigation Control | Owner |
|------|-------------------|-------|
| Incorrect scoring | Algorithm validated against published C-SSRS, unit tested (100% coverage) | Dev |
| Missed high-risk patient | Automatic clinician alert within 2 minutes of HIGH/CRITICAL score | System |
| System failure mid-assessment | Session recovery, offline capability, real-time backup | Dev |
| Clinician doesn't respond | Escalation alerts after 30 min, secondary contact notification | System |
| Unauthorized patient access | Role-based access control, encryption, audit logging | Dev |

## 3. Safety Monitoring
- Daily review of alert logs
- Weekly safety incident review (even if none)
- Monthly clinical advisor check-in
- Automatic escalation of CRITICAL scores

## 4. Incident Response
If a patient at risk is not detected:
1. System logs trigger date/time
2. Immediate review by clinical advisor
3. Documentation of what was missed
4. Algorithm adjustment or system correction
5. Affected patient contacted within 24 hours

## Signed by:
Clinical Advisor: [Name] Date: [TBD - after Lincoln engagement]
Developer: [You] Date: [Today]
```

#### Document 2: Data Protection Impact Assessment (DPIA)

**Status:** You've already mostly done this. Just need to finalize:

```markdown
# DATA PROTECTION IMPACT ASSESSMENT (DPIA)

## Data Processed
- Patient mental health assessments
- Clinician clinical notes
- Alert logs (who responded to what, when)

## Lawful Basis
- Consent: Patient explicitly consents to assessment sharing with clinician
- Clinical effectiveness: Necessary for mental health treatment

## Data Subjects' Rights
- Right to access: Patient can export assessment history
- Right to erasure: Patient can request account deletion (anonymized assessments retained)
- Right to data portability: FHIR export available
- Right to object: Patient can opt out of specific clinicians

## Security Measures
- Data at rest: Fernet encryption
- Data in transit: TLS 1.2+
- Access control: Role-based (patient views own, clinician views assigned)
- Audit logging: All access logged, no deletion, only new versions

## Risks & Mitigation
- Risk: Unauthorized access → Control: Encryption + access control
- Risk: Data breach → Control: Encryption + breach notification within 72 hours
- Risk: System failure → Control: Daily backup + tested recovery

## DPO Sign-Off
You (as DPO for university trial) or university's DPO
```

#### Document 3: Crisis Response Protocol

**This is CRITICAL and non-negotiable for any mental health app:**

```markdown
# CRISIS RESPONSE PROTOCOL

## When is a Patient in Crisis?

**CRITICAL Score** (Immediate Action Required)
- Score 5 on "Suicidal Ideation with Intent & Plan/Behavior"
- Triggers: AUTOMATIC ALERT to assigned clinician + immediate backup alert

**HIGH Score** (Urgent Response Required)
- Score 4 on suicidal ideation items (intent or plan, but not both)
- Triggers: Alert to clinician, escalation if no response in 30 min

**MEDIUM Score** (Routine Follow-up)
- Score 3 or escalating trend
- Triggers: Flag in clinician dashboard, scheduled follow-up

## System Actions on CRITICAL Score

```
CRITICAL SCORE DETECTED
    ↓
Send email alert to assigned clinician (immediate)
Send SMS alert to clinician (if phone on file) [1 min after email]
Send in-app notification (clinician dashboard) [immediately]
    ↓
[If no response in 10 min]
Send escalation email to secondary contact/supervisor [10 min]
    ↓
[If no response in 30 min total]
Log escalation alert + flag for emergency contact procedure
    ↓
Clinician selects action:
  A) Call patient immediately
  B) Emergency contact notification
  C) Emergency services (999)
  D) Document patient was unreachable / in safe location
```

## Clinician Responsibilities

1. **Respond within 30 minutes** of CRITICAL alert
2. **Contact patient directly** (call, not message)
3. **Document the interaction**: Patient status, safety plan reviewed, actions taken
4. **If patient in immediate danger**: Call 999, don't rely on app
5. **Follow up within 24 hours** with safety plan review

## Patient Safety Planning (if HIGH or CRITICAL)

After assessment, system forces patient to:
1. Identify warning signs (what happens before crisis)
2. Identify internal coping strategies (things they can do themselves)
3. List people to contact (trusted friends/family)
4. List professional resources (therapist phone, crisis line 116 123, 999)
5. Ways to make environment safer (remove means)

Safety plan stored in system + email sent to patient + clinician review required

## Emergency Escalation (if system fails)

If system fails to send alert:
1. Backup email from system admin to all clinicians: "SYSTEM FAILURE - check dashboard manually"
2. Offline backup: Printed patient list with emergency contacts maintained at clinic
3. Post-incident review: Why did alert fail? Fix + test

## Incident Documentation

Every CRITICAL score must be documented:
- Timestamp of assessment
- Score + scoring rationale
- Alerts sent (who, when, method)
- Clinician response (time, action)
- Patient outcome (safe, engaged with safety plan, etc.)
- Incident review (was anything missed? why?)

## Sign-Off

Clinical Advisor: _________________ Date: _______
Developer: _________________ Date: _______
```

#### Document 4: Patient Information Leaflet (PIU - Plain Language)

```markdown
# HEALING SPACE: WHAT YOU NEED TO KNOW

## What is Healing Space?

Healing Space is a digital tool that helps your therapist or counselor understand 
how you're feeling and provide better support. It uses a scientific assessment called 
the C-SSRS (Columbia-Suicide Severity Rating Scale) which has been used in research 
hospitals for 20+ years.

## What Will Happen?

1. **You complete a simple questionnaire** (5-10 minutes)
   - Questions about your mood, thoughts, and how you're coping
   - You answer honestly - there are no "right" answers
   
2. **Your clinician reviews your answers** (within 24 hours)
   - They can see your score and provide feedback
   - They use this to guide your treatment
   
3. **If you're at risk of suicide**, the system alerts your clinician immediately
   - This is to keep you safe
   - Your clinician will contact you

## What Happens to Your Data?

✅ Your assessment data is **encrypted** (secret code that only you and your clinician can read)  
✅ Your data is stored securely on UK servers  
✅ You can download a copy of your data anytime  
✅ You can ask to delete your account (we'll remove personal details)  

## Important Safety Information

**This app is NOT a replacement for emergency help.**

If you are thinking about harming yourself RIGHT NOW:
- **Call your clinician immediately**
- **Call emergency services: 999** (UK)
- **Call Samaritans: 116 123** (available 24/7, free)

The app helps your clinician understand you better, but for urgent help, 
you must contact a person directly.

## Your Rights

- You can pause or stop using the app anytime
- You can ask to see all your data
- You can ask us to delete your account
- You can ask us to share your data with another provider
- You have the right to privacy under UK law

## Questions?

Contact: [Your name] - [Your email]

---

I UNDERSTAND:
☐ This app helps my clinician understand my mental health
☐ It is NOT a replacement for emergency services (999 for immediate danger)
☐ My data is encrypted and secure
☐ I can ask for my data or delete my account anytime
☐ My clinician will review my assessments

Patient Name: _________________________ Date: _______
Patient Signature: ___________________
```

### 3.2 What You SHOULD Have (Highly Recommended)

#### Document 5: Risk Register (Simplified)

1-page table covering:
- Top 5-8 risks (scored by severity × probability)
- Current mitigation controls
- Residual risk after controls
- Clinical advisor sign-off

#### Document 6: Ethics Approval Template

Summary of what the University Research Ethics Committee will review:
- Research question (e.g., "Is Healing Space effective for mental health assessment?")
- Participant safety measures
- Informed consent process
- Data handling procedures
- Approval checklist

---

## 4. Fast-Track Implementation Schedule (ASAP Approach)

### Phase 1: University Engagement (Week 1-3)

**Week 1:**
- [ ] Finalize Clinical Safety Case (3-page document)
- [ ] Finalize DPIA (1-page summary)
- [ ] Draft Patient Information Leaflet
- [ ] Create 1-page governance proposal
- [ ] Draft Lincoln contact email

**Week 2:**
- [ ] Contact Head of Psychology at Lincoln
- [ ] Schedule 20-30 min call
- [ ] Respond to initial questions
- [ ] Agree on ethics approval path

**Week 3:**
- [ ] Submit to University Research Ethics Committee
- [ ] Respond to ethics committee feedback (likely round 1)

### Phase 2: Code Implementation (Week 2-6, in parallel with ethics)

**Week 2-3 (Parallel with ethics submission):**
- [ ] Database schema: `c_ssrs_assessments`, `risk_assessments`, `safety_plans` tables
- [ ] API endpoints: Assessment start/save/submit
- [ ] Scoring algorithm + unit tests (100% coverage)

**Week 4-5:**
- [ ] Clinician dashboard: Real-time alerts, patient list, risk trends
- [ ] Patient UI: Guided 8-question C-SSRS flow
- [ ] Crisis alert system: Email/SMS/in-app notifications
- [ ] Safety planning flow: Trigger if HIGH/CRITICAL score

**Week 6:**
- [ ] Full integration test: End-to-end assessment flow
- [ ] Clinician testing: Alert responsiveness
- [ ] Patient UAT: Usability testing
- [ ] Accessibility: WCAG 2.1 AA compliance check

### Phase 3: Ethics Approval & Launch (Week 7-8)

**Week 7:**
- [ ] Receive ethics approval (or address feedback)
- [ ] Final safety review with Clinical Advisor
- [ ] Staging deployment with Lincoln staff

**Week 8:**
- [ ] Production deployment to Railway
- [ ] Clinician training
- [ ] Patient recruitment & onboarding
- [ ] Live monitoring (first week critical)

---

## 5. What You'll Tell Lincoln

### The Pitch (30 seconds)

> "Healing Space is a digital mental health tool that uses validated assessment protocols to help clinicians provide better support. We're building it to NHS standards and want to validate it with real users at Lincoln University before wider deployment. We need your department's clinical oversight and the chance to work with psychology staff and students. The university provides intellectual oversight, we handle all technical development and maintenance."

### The Ask (What you need from them)

| What | Why | Time commitment |
|-----|-----|-----------------|
| **Clinical Advisor** | To review safety protocols, sign off on clinical decisions | 2 hours/month |
| **Ethics Approval** | To validate patient safety measures and data handling | One submission (handled by you, reviewed by committee) |
| **User Testing** | Real clinicians & students to test the system | 5-10 volunteers, 1-2 hours each |
| **Patient Participants** (optional) | Real patient data validates clinical effectiveness | Start with staff only, add patients after ethics approval |
| **Institutional Backing** | For credibility when approaching NHS later | Letter of recommendation |

### What You Offer

✅ **No cost to the university** (you cover hosting, development, insurance)  
✅ **Publication rights** (university can publish research findings)  
✅ **IP ownership** (university doesn't own the app, but has research license)  
✅ **Ongoing support** (bug fixes, feature requests, maintenance for 12 months minimum)  
✅ **Joint credibility** (both benefit from successful launch - good for their reputation)

---

## 6. Timeline to NHS Deployment

| Phase | Timeline | Output |
|-------|----------|--------|
| **University MVP** | 6-8 weeks | Working system + real clinical data |
| **University Trial** | 3-6 months | Validated effectiveness + incident history (should be clean) |
| **NHS Preparation** | 8-12 weeks | Full clinical safety case + risk register + formal governance docs |
| **NHS Deployment** | Ongoing | Rolled out to NHS partners |

**Total: ~12-16 months from start to first NHS deployment**

But you'll have a working, validated system in 8 weeks that proves the concept.

---

## 7. Critical Success Factors (Don't Skip These)

### Technical (Non-Negotiable)

✅ **C-SSRS algorithm validates 100%** against published standard  
✅ **Crisis alerts fire within 2 minutes** (tested, timed)  
✅ **Encryption is real** (Fernet keys properly managed)  
✅ **Audit logging captures everything** (who accessed what, when, why)  
✅ **System handles failure gracefully** (doesn't lose assessment data)

### Clinical (Non-Negotiable)

✅ **Clinical Safety Case is signed by a clinician**  
✅ **Crisis Response Protocol is realistic** (clinicians actually can respond in 30 min)  
✅ **Patient information is in plain language** (not jargon-heavy)  
✅ **Safety measures are testable** (you can prove alerts work)

### Governance (Non-Negotiable)

✅ **Ethics approval granted before launch** (non-negotiable for any patient trial)  
✅ **Incident response plan is documented** (what happens if something goes wrong)  
✅ **Data security is verified** (encryption confirmed, access controls tested)  
✅ **Clinical Advisor is accessible** (responds within 48 hours to safety concerns)

---

## 8. Cost & Resource Summary (University Phase)

| Cost | Item | Estimate |
|------|------|----------|
| **Development** | Your time (if unpaid), or contractor | £0-20K |
| **Hosting** | Railway (existing) | £50-100/month |
| **Legal** | One legal review (optional for university phase) | £0-2K |
| **Insurance** | Professional indemnity (optional for university phase, covered by university institutional insurance) | £0 (university covers) |
| **Backup/Testing** | Database backups + monitoring | Included in Railway |
| **Total** | | ~£50-100/month operating cost |

**No upfront licensing cost for C-SSRS** (it's freely available for non-commercial use)

---

## 9. Next Steps for YOU (This Week)

### TODAY (Feb 7)
- [ ] Review & refine your Clinical Safety Case
- [ ] Ensure Crisis Response Protocol is realistic & clear
- [ ] Draft Patient Information Leaflet in plain language

### BY FEB 10
- [ ] Create governance proposal (1-page summary of what Lincoln provides vs. you provide)
- [ ] Research Head of Psychology at Lincoln University (LinkedIn, university website)
- [ ] Draft initial contact email

### BY FEB 14
- [ ] Send contact email to Lincoln University
- [ ] Prepare for initial call (talking points, demo walkthrough)
- [ ] Begin implementing C-SSRS database schema (in parallel)

### BY FEB 28 (ASAP Milestone)
- [ ] Ethics approval submitted
- [ ] C-SSRS assessment API implemented & tested
- [ ] Clinician alert system working
- [ ] Patient UI complete

---

## Document Status

**Status:** DRAFT - UNIVERSITY DEPLOYMENT FIRST  
**Version:** 1.0  
**Created:** February 7, 2026  
**Target Audience:** You + Lincoln University Psychology Department  
**Next Review:** After Lincoln engagement confirmed (Feb 14)

---

## Questions Answered

1. ✅ **Clinical Lead:** You're targeting Lincoln's Head of Psychology (smart move - institutional backing helps NHS later)
2. ✅ **Deployment model:** University first (faster, less regulated), then NHS (slower, but you'll have proof it works)
3. ✅ **Timeline:** ASAP (6-8 weeks to MVP, 3-6 months university trial, then NHS)
4. ✅ **Legal/Insurance:** Skip for now (university covers institutional liability for the trial)
5. ✅ **Clinician testing:** You'll get this during university trial (staff first, then students with permission)

You're in a great position: University partnership = credibility for NHS pitch later.
