# Complete Documentation Index

**The complete guide to Healing Space UK documentation - organized by user type and topic.**

---

## 🎯 START HERE

**First time visiting? Pick your role:**

| Role | Start Here | What You'll Learn |
|------|-----------|-------------------|
| 👤 **Patient** | [What is Healing Space?](./0-START-HERE/What-is-Healing-Space.md) → [Getting Started](./0-START-HERE/Getting-Started.md) | How to use the app, all features, mental health resources |
| 👨‍⚕️ **Clinician** | [What is Healing Space?](./0-START-HERE/What-is-Healing-Space.md) → [Clinician Guide](./1-USER-GUIDES/Clinician-Guide.md) | Dashboard, patient management, risk alerts, messaging |
| 🏥 **NHS/Health Service** | [NHS Readiness Checklist](./2-NHS-COMPLIANCE/NHS-Readiness-Checklist.md) | Compliance requirements, deployment, safety standards |
| 🎓 **Researcher/University** | [University Readiness Checklist](./3-UNIVERSITY-TRIALS/University-Readiness-Checklist.md) | Trial setup, ethics, recruitment, measurement scales |
| 👨‍💻 **Developer** | [Developer Setup](./6-DEVELOPMENT/Developer-Setup.md) → [Architecture](./4-TECHNICAL/Architecture-Overview.md) | How to code, API reference, database schema |
| 🛠️ **DevOps/Operations** | [Railway Deployment](./5-DEPLOYMENT/Railway-Deployment.md) | Deploy to production, configuration, monitoring |

---

## 📚 Complete Section Guide

### **0. START HERE** (Introduction)
Essential entry points for all users:
- `README.md` - Master documentation overview (THIS FILE)
- `What-is-Healing-Space.md` - What it does, key features, benefits
- `Getting-Started.md` - 5-minute quickstart
- `Quick-Features-Overview.md` - Feature walkthrough

**Use when**: First time visiting, unsure where to start

---

### **1. USER GUIDES** (How to Use It)
Step-by-step guides for different user types:

**Patient Resources**
- `Patient-Guide.md` - Complete feature walkthrough
- `Getting-Started.md` - 5-minute setup
- `FAQ.md` - Frequently asked questions
- `Troubleshooting.md` - Common issues and solutions
- `Accessibility-Guide.md` - Screen readers, keyboard navigation

**Clinician Resources**
- `Clinician-Guide.md` - Dashboard, patient management, alerts
- `Crisis-Response-Guide.md` - How to respond to high-risk patients
- `Messaging-Guide.md` - Secure clinician-patient messaging

**Researcher Resources**
- `Researcher-Guide.md` - Data collection, trial management, analysis

**Use when**: You want to know HOW to use a feature

---

### **2. NHS COMPLIANCE** ⭐ CRITICAL
Compliance, safety, governance, legal:

**Checklists & Readiness**
- `NHS-Readiness-Checklist.md` - 8 mandatory requirements (✅ COMPLETE)
- `Pre-Deployment-Checklist.md` - Before going live
- `Governance-Documents.md` - Leadership, accountability, roles

**Clinical Safety**
- `Clinical-Safety-Case.md` - FDA-style clinical validation
- `Crisis-Response-Procedures.md` - Emergency protocols
- `Risk-Management.md` - Risk register, mitigation strategies
- `Quality-Assurance.md` - Testing, monitoring, continuous improvement

**Compliance & Legal**
- `Compliance-Framework.md` - NHS standards, IG44, security requirements
- `Data-Protection-Impact-Assessment.md` - GDPR, DPA compliance
- `Audit-Procedures.md` - Logging, retention, forensics
- `Breach-Response-Procedures.md` - Incident management

**Use when**: You're deploying to NHS or need regulatory evidence

---

### **3. UNIVERSITY TRIALS** ⭐ CRITICAL
Everything for conducting research:

**Readiness & Planning**
- `University-Readiness-Checklist.md` - 10 requirements (✅ COMPLETE)
- `Research-Ethics-Guide.md` - REC approval, consent, safeguarding
- `Study-Protocol-Template.md` - Protocol for REC submission

**Participant Management**
- `Consent-Forms.md` - Pre-written, ethics-approved consent
- `Recruitment-Materials.md` - Posters, emails, participant scripts
- `Participant-Information-Sheet.md` - Patient-facing information

**Data & Analysis**
- `Measurement-Scales.md` - C-SSRS, PHQ-9, GAD-7, CORE-OM, ORS
- `Data-Collection-Guide.md` - How participants log data, clinicians monitor, researchers export
- `Data-Analysis-Guide.md` - Statistical procedures, analysis plan

**Operations**
- `Safety-Monitoring-Guide.md` - Adverse events, stopping rules
- `Operational-Procedures-Guide.md` - SOPs, staff training, quality control
- `Publication-Guide.md` - Authorship, dissemination, open science

**Example**
- `Lincoln-University-Case-Study.md` - Real university implementation example

**Use when**: You're running a clinical trial or research study

---

### **4. TECHNICAL** (How It Works)
Architecture, design, implementation:

**System Design**
- `Architecture-Overview.md` - Components, data flow, technology stack
- `Database-Schema.md` - 43 tables, relationships, indexes
- `API-Reference.md` - All 210+ endpoints with examples

**Clinical Algorithms**
- `Risk-Scoring-Algorithm.md` - How risk scores are calculated
- `C-SSRS-Validation.md` - C-SSRS implementation validation
- `AI-Therapy-Prompts.md` - How AI generates responses

**Code Quality**
- `Code-Quality-Standards.md` - Coding standards, best practices
- `Testing-Strategy.md` - Unit tests, integration tests, E2E tests

**Use when**: You're a developer or need to understand system internals

---

### **5. DEPLOYMENT** (Getting It Running)
Installation, configuration, operations:

**Setup Guides**
- `Local-Setup.md` - Run on your computer (development)
- `Railway-Deployment.md` - Deploy to production (recommended, 5 min)
- `AWS-Deployment.md` - Deploy to AWS
- `Self-Hosted.md` - On-premises deployment

**Configuration**
- `Environment-Variables.md` - All configuration options
- `Database-Migration.md` - SQLite to PostgreSQL, schema updates
- `Email-Configuration.md` - Gmail, SendGrid setup
- `SSL-Certificates.md` - HTTPS setup

**Operations**
- `Monitoring-and-Alerts.md` - Error tracking, uptime, performance
- `Backup-and-Recovery.md` - Database backups, disaster recovery
- `Scaling.md` - How to scale for more users
- `Maintenance.md` - Regular maintenance tasks

**Use when**: You're deploying or operating the system

---

### **6. DEVELOPMENT** (Building Features)
How to contribute and develop:

**Getting Started**
- `Developer-Setup.md` - Clone, install, run in 10 minutes
- `Local-Development.md` - Development workflow, hot reload
- `Architecture-Overview.md` - (linked from Technical) System design

**Contributing**
- `Contributing-Guide.md` - Code standards, PR process
- `Git-Workflow.md` - Branching, commits, releases
- `Testing-Guide.md` - Writing tests, running test suite
- `Debugging-Guide.md` - Debugging tips, common issues

**Documentation**
- `Documentation-Standards.md` - How to write docs
- `Release-Process.md` - How to release new versions

**Use when**: You're adding features or fixing bugs

---

### **7. FEATURES** (What It Does)
Complete guides for each feature:

**Core Therapy Features**
- `AI-Therapy-Chat.md` - How AI chat works, examples
- `Mood-Tracking.md` - Logging, analytics, trends
- `Risk-Assessment.md` - C-SSRS, risk levels, crisis response

**Patient Tools**
- `CBT-Tools.md` - Goals, thought records, exposures, coping cards
- `Safety-Planning.md` - Creating and managing safety plans
- `Wellness-Rituals.md` - Pet game, habit tracking

**Clinician Tools**
- `Clinician-Dashboard.md` - Patient overview, risk alerts
- `Patient-Messaging.md` - Secure clinician-patient messaging
- `Risk-Alerts.md` - How clinicians get notified of high-risk users
- `Treatment-Planning.md` - Collaborative goal setting

**Collaborative Features**
- `Clinician-Appointments.md` - Scheduling sessions
- `Community-Features.md` - Forums, peer support
- `Data-Sharing.md` - How clinicians see patient data

**Research Features**
- `Data-Export.md` - Export for research, de-identification
- `Participant-Enrollment.md` - Trial participant management
- `Outcome-Tracking.md` - Measurement scale administration

**Use when**: You want to learn about a specific feature

---

### **8. SECURITY** (Keeping It Safe)
Deep-dive into security and privacy:

**Core Security**
- `Security-Overview.md` - Defense-in-depth strategy
- `Authentication.md` - Session-based auth, CSRF tokens, 2FA
- `Encryption.md` - At-rest (AES-256), in-transit (HTTPS/TLS)
- `Input-Validation.md` - Injection prevention, sanitization
- `Rate-Limiting.md` - Brute force protection, DDoS mitigation

**Advanced Security**
- `CSRF-Protection.md` - Cross-site request forgery prevention
- `XSS-Prevention.md` - Cross-site scripting prevention
- `SQL-Injection-Prevention.md` - SQL injection protection
- `Password-Security.md` - Hashing, minimum requirements

**Operations & Incident Management**
- `Vulnerability-Disclosure.md` - Responsible disclosure policy
- `Breach-Response-Procedures.md` - Incident management
- `Audit-Logging.md` - Event tracking, retention, forensics
- `Penetration-Testing.md` - Regular security testing

**Privacy**
- `Privacy-Policy.md` - User-facing privacy notice
- `Data-Retention.md` - How long we keep data
- `User-Rights.md` - Accessing, exporting, deleting your data

**Use when**: You care about security and privacy (you should!)

---

### **9. ROADMAP** (What's Next)
Plans, progress, future direction:

**Current Status**
- `Priority-Roadmap.md` - TIER 0-6 roadmap with timelines (TIER 1-4 IN PROGRESS)
- `Implementation-Status.md` - What's done, what's in progress

**Planned Features**
- `Feature-Backlog.md` - Future features by priority
- `Enhancements.md` - Nice-to-have improvements

**Issues & Technical Debt**
- `Known-Issues.md` - Current bugs with workarounds
- `Tech-Debt.md` - Refactoring needed, performance optimization
- `Performance-Roadmap.md` - Scaling, optimization plans

**Version History**
- `Changelog.md` - Version history with breaking changes

**Use when**: You want to know what's coming next or what's broken

---

### **10. REFERENCE** (Quick Lookup)
Quick references, glossaries, credits:

**Quick References**
- `Glossary.md` - Technical and clinical terms defined
- `Abbreviations.md` - Common acronyms (NHS, GDPR, CBT, etc.)
- `Architecture-Decisions.md` - Why we chose this tech stack
- `Dependencies.md` - All Python packages and versions

**Administrative**
- `License-Info.md` - Open source license
- `Credits.md` - Team and contributors
- `Contact-Info.md` - Support email, social media

**Use when**: You need a definition or quick fact

---

## 🔍 Find What You Need

### By Task

**"I want to..."**

| Task | Start With |
|------|-----------|
| ...use Healing Space as a patient | [Patient Guide](./1-USER-GUIDES/Patient-Guide.md) |
| ...manage patients as a clinician | [Clinician Guide](./1-USER-GUIDES/Clinician-Guide.md) |
| ...deploy to NHS | [NHS Readiness Checklist](./2-NHS-COMPLIANCE/NHS-Readiness-Checklist.md) |
| ...run a clinical trial | [University Readiness Checklist](./3-UNIVERSITY-TRIALS/University-Readiness-Checklist.md) |
| ...deploy to production | [Railway Deployment](./5-DEPLOYMENT/Railway-Deployment.md) |
| ...write code | [Developer Setup](./6-DEVELOPMENT/Developer-Setup.md) |
| ...understand the architecture | [Architecture Overview](./4-TECHNICAL/Architecture-Overview.md) |
| ...understand security | [Security Overview](./8-SECURITY/Security-Overview.md) |
| ...check if something's secure | [Vulnerability Disclosure](./8-SECURITY/Vulnerability-Disclosure.md) |
| ...report a bug | [Contributing Guide](./6-DEVELOPMENT/Contributing-Guide.md) |
| ...publish research | [Publication Guide](./3-UNIVERSITY-TRIALS/Publication-Guide.md) |

### By Topic

**Compliance & Safety**
- NHS: [NHS Readiness Checklist](./2-NHS-COMPLIANCE/NHS-Readiness-Checklist.md)
- GDPR: [Data Protection](./2-NHS-COMPLIANCE/Data-Protection-Impact-Assessment.md)
- Clinical Safety: [Clinical Safety Case](./2-NHS-COMPLIANCE/Clinical-Safety-Case.md)
- Crisis: [Crisis Response Procedures](./2-NHS-COMPLIANCE/Crisis-Response-Procedures.md)

**Deployment**
- Local: [Local Setup](./5-DEPLOYMENT/Local-Setup.md)
- Railway: [Railway Deployment](./5-DEPLOYMENT/Railway-Deployment.md)
- AWS: [AWS Deployment](./5-DEPLOYMENT/AWS-Deployment.md)
- Configuration: [Environment Variables](./5-DEPLOYMENT/Environment-Variables.md)

**Features**
- AI Therapy: [AI Therapy Chat](./7-FEATURES/AI-Therapy-Chat.md)
- Mood Tracking: [Mood Tracking](./7-FEATURES/Mood-Tracking.md)
- Risk Assessment: [Risk Assessment](./7-FEATURES/Risk-Assessment.md)
- CBT Tools: [CBT Tools](./7-FEATURES/CBT-Tools.md)

**Development**
- Setup: [Developer Setup](./6-DEVELOPMENT/Developer-Setup.md)
- API: [API Reference](./4-TECHNICAL/API-Reference.md)
- Database: [Database Schema](./4-TECHNICAL/Database-Schema.md)
- Testing: [Testing Guide](./6-DEVELOPMENT/Testing-Guide.md)

**Security**
- Overview: [Security Overview](./8-SECURITY/Security-Overview.md)
- Authentication: [Authentication](./8-SECURITY/Authentication.md)
- Encryption: [Encryption](./8-SECURITY/Encryption.md)
- Incident Response: [Breach Response](./8-SECURITY/Breach-Response-Procedures.md)

---

## 📊 Documentation Statistics

| Metric | Value |
|--------|-------|
| **Total Sections** | 10 (0-9) |
| **Total Documents** | 150+ |
| **Total Words** | 250,000+ |
| **Code Examples** | 100+ |
| **Diagrams** | 20+ |
| **Checklists** | 15+ |
| **Last Updated** | February 8, 2026 |

---

## ✨ Key Highlights

### Top Documents to Read First
1. [What is Healing Space?](./0-START-HERE/What-is-Healing-Space.md) - 10 min
2. [Getting Started](./0-START-HERE/Getting-Started.md) - 5 min
3. Your role-specific guide (Patient/Clinician/Developer/etc.) - 20 min
4. [Architecture Overview](./4-TECHNICAL/Architecture-Overview.md) - 15 min (if technical)

### Most Critical for Compliance
1. [NHS Readiness Checklist](./2-NHS-COMPLIANCE/NHS-Readiness-Checklist.md) - ✅ 8/8 COMPLETE
2. [University Readiness Checklist](./3-UNIVERSITY-TRIALS/University-Readiness-Checklist.md) - ✅ 10/10 COMPLETE
3. [Clinical Safety Case](./2-NHS-COMPLIANCE/Clinical-Safety-Case.md)
4. [Data Protection Impact Assessment](./2-NHS-COMPLIANCE/Data-Protection-Impact-Assessment.md)

### Most Useful for Developers
1. [Developer Setup](./6-DEVELOPMENT/Developer-Setup.md)
2. [Architecture Overview](./4-TECHNICAL/Architecture-Overview.md)
3. [API Reference](./4-TECHNICAL/API-Reference.md)
4. [Contributing Guide](./6-DEVELOPMENT/Contributing-Guide.md)

---

## 🎓 Learning Paths

### Path 1: Patient (15 minutes)
1. [Getting Started](./0-START-HERE/Getting-Started.md)
2. [Patient Guide](./1-USER-GUIDES/Patient-Guide.md)
3. [FAQ](./1-USER-GUIDES/FAQ.md)

### Path 2: Clinician (30 minutes)
1. [What is Healing Space?](./0-START-HERE/What-is-Healing-Space.md)
2. [Clinician Guide](./1-USER-GUIDES/Clinician-Guide.md)
3. [Risk Assessment](./7-FEATURES/Risk-Assessment.md)
4. [Crisis Response](./2-NHS-COMPLIANCE/Crisis-Response-Procedures.md)

### Path 3: NHS (2 hours)
1. [What is Healing Space?](./0-START-HERE/What-is-Healing-Space.md)
2. [NHS Readiness Checklist](./2-NHS-COMPLIANCE/NHS-Readiness-Checklist.md)
3. [Clinical Safety Case](./2-NHS-COMPLIANCE/Clinical-Safety-Case.md)
4. [Data Protection](./2-NHS-COMPLIANCE/Data-Protection-Impact-Assessment.md)
5. [Governance](./2-NHS-COMPLIANCE/Governance-Documents.md)
6. [Deployment Guide](./5-DEPLOYMENT/)

### Path 4: Researcher (3 hours)
1. [What is Healing Space?](./0-START-HERE/What-is-Healing-Space.md)
2. [University Readiness Checklist](./3-UNIVERSITY-TRIALS/University-Readiness-Checklist.md)
3. [Research Ethics Guide](./3-UNIVERSITY-TRIALS/Research-Ethics-Guide.md)
4. [Study Protocol Template](./3-UNIVERSITY-TRIALS/Study-Protocol-Template.md)
5. [Measurement Scales](./3-UNIVERSITY-TRIALS/Measurement-Scales.md)
6. [Data Collection Guide](./3-UNIVERSITY-TRIALS/Data-Collection-Guide.md)

### Path 5: Developer (4 hours)
1. [Developer Setup](./6-DEVELOPMENT/Developer-Setup.md)
2. [Architecture Overview](./4-TECHNICAL/Architecture-Overview.md)
3. [API Reference](./4-TECHNICAL/API-Reference.md)
4. [Database Schema](./4-TECHNICAL/Database-Schema.md)
5. [Contributing Guide](./6-DEVELOPMENT/Contributing-Guide.md)

### Path 6: DevOps (2 hours)
1. [Architecture Overview](./4-TECHNICAL/Architecture-Overview.md)
2. [Railway Deployment](./5-DEPLOYMENT/Railway-Deployment.md)
3. [Environment Variables](./5-DEPLOYMENT/Environment-Variables.md)
4. [Monitoring & Alerts](./5-DEPLOYMENT/Monitoring-and-Alerts.md)

---

## 💬 Questions?

**Can't find what you're looking for?**

1. Try the search function (Ctrl+F or Cmd+F)
2. Check the [Glossary](./10-REFERENCE/Glossary.md)
3. See the relevant role guide (Patient/Clinician/Developer)
4. Email [support@healing-space.org.uk](mailto:support@healing-space.org.uk)

---

**Last Updated**: February 8, 2026  
**Version**: 2.0  
**Status**: ✅ Production-Ready

