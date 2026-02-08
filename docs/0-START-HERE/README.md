# 📘 Healing Space UK Documentation

**Welcome!** This is the complete documentation for Healing Space UK - a mental health companion web application combining evidence-based therapy with AI support.

> **Version**: 2.0 (PostgreSQL) | **Status**: ✅ Production-Ready (Feb 8, 2026) | **Live**: [healing-space.org.uk](https://healing-space.org.uk)

---

## 🎯 Quick Navigation

**Choose your path based on who you are:**

### 👤 I'm a **Patient or User**
Start here to learn how to use Healing Space:
- [Patient Guide](../1-USER-GUIDES/Patient-Guide.md) - Learn all features, from mood tracking to AI therapy
- [Getting Started](../0-START-HERE/Getting-Started.md) - 5-minute setup
- [FAQ](../1-USER-GUIDES/FAQ.md) - Common questions
- [Troubleshooting](../1-USER-GUIDES/Troubleshooting.md) - Having problems?

### 👨‍⚕️ I'm a **Clinician or Healthcare Provider**
Learn how to manage patients and use clinical features:
- [Clinician Guide](../1-USER-GUIDES/Clinician-Guide.md) - Dashboard, patient management, alerts
- [Crisis Response Protocol](../2-NHS-COMPLIANCE/Crisis-Response-Procedures.md) - How to handle emergencies
- [Data Access & Privacy](../2-NHS-COMPLIANCE/Data-Protection-Impact-Assessment.md) - GDPR/patient data

### 🏥 I'm with the **NHS or Healthcare Organization**
Ready to deploy or integrate Healing Space:
- [NHS Readiness Checklist](../2-NHS-COMPLIANCE/NHS-Readiness-Checklist.md) - 8 mandatory compliance items
- [Compliance Framework](../2-NHS-COMPLIANCE/Compliance-Framework.md) - NHS standards, IG44, security
- [Deployment Guide](../5-DEPLOYMENT/NHS-Deployment.md) - How to roll out
- [Clinical Safety Case](../2-NHS-COMPLIANCE/Clinical-Safety-Case.md) - Clinical governance

### 🎓 I'm a **Researcher or University**
Conducting clinical trials or research:
- [University Readiness Checklist](../3-UNIVERSITY-TRIALS/University-Readiness-Checklist.md) - 10 requirements
- [Research Ethics Guide](../3-UNIVERSITY-TRIALS/Research-Ethics-Guide.md) - Ethics approval, consent, REC submission
- [Study Protocol Template](../3-UNIVERSITY-TRIALS/Study-Protocol-Template.md) - Design your trial
- [Measurement Scales](../3-UNIVERSITY-TRIALS/Measurement-Scales.md) - C-SSRS, PHQ-9, GAD-7, etc.

### 👨‍💻 I'm a **Developer**
Building features or maintaining the codebase:
- [Developer Setup](../6-DEVELOPMENT/Developer-Setup.md) - Get coding in 10 minutes
- [Architecture Overview](../4-TECHNICAL/Architecture-Overview.md) - System design, components
- [API Reference](../4-TECHNICAL/API-Reference.md) - All 210+ endpoints documented
- [Contributing Guide](../6-DEVELOPMENT/Contributing-Guide.md) - Code standards, PR process

### 🛠️ I'm an **Operations or DevOps Engineer**
Deploying, monitoring, maintaining:
- [Railway Deployment](../5-DEPLOYMENT/Railway-Deployment.md) - Deploy to production in 5 min
- [Environment Setup](../5-DEPLOYMENT/Environment-Variables.md) - Configuration guide
- [Monitoring & Alerts](../5-DEPLOYMENT/Monitoring-and-Alerts.md) - Uptime, performance, alerts
- [Backup & Recovery](../5-DEPLOYMENT/Backup-and-Recovery.md) - Database backups, disaster recovery

---

## 📚 Documentation by Section

### **0. START HERE** (This Section)
Essential introduction and quick navigation

### **1. USER GUIDES**
- Patient Guide - Feature walkthrough
- Clinician Guide - Dashboard and patient management
- Researcher Guide - Trial setup and data collection
- FAQ & Troubleshooting - Common issues
- Accessibility Guide - WCAG compliance, screen readers

### **2. NHS COMPLIANCE** ⭐ CRITICAL
- **NHS Readiness Checklist** - 8 mandatory requirements
- **Compliance Framework** - IG44, security, governance
- **Clinical Safety Case** - FDA/NHS-style safety evidence
- **Data Protection Impact Assessment** - GDPR, DPA compliance
- **Governance Documents** - Leadership, accountability, policies
- **Risk Management** - Risk register, mitigation
- **Audit Procedures** - Logging, retention, breach response

### **3. UNIVERSITY TRIALS** ⭐ CRITICAL
- **University Readiness Checklist** - 10 requirements for trials
- **Research Ethics Guide** - REC approval, informed consent, ethics
- **Study Protocol Template** - Randomization, sample size, analysis
- **Consent Forms** - Patient and clinician consent
- **Recruitment Materials** - Posters, emails, scripts
- **Measurement Scales** - Clinical outcome tools (C-SSRS, PHQ-9, GAD-7)
- **Data Collection Guide** - How to gather and export trial data
- **Example Implementation** - University of Lincoln case study

### **4. TECHNICAL**
- Architecture Overview - System design, components, data flow
- Database Schema - 43 tables, relationships, indexed fields
- API Reference - All 210+ endpoints with request/response examples
- Clinical Algorithms - Risk scoring, C-SSRS calculation, AI prompt engineering
- Security Implementation - Authentication, encryption, CSRF, rate limiting
- Code Quality Standards - Linting, testing, documentation

### **5. DEPLOYMENT**
- Local Setup - Run on your machine for development
- Railway Deployment - Deploy to production (recommended)
- Environment Variables - Configuration for dev/staging/production
- Database Migration - SQLite to PostgreSQL, schema changes
- Email Configuration - Gmail/SendGrid setup
- Monitoring & Alerts - Error tracking, uptime, performance dashboards
- Backup & Recovery - Automated backups, point-in-time recovery

### **6. DEVELOPMENT**
- Developer Setup - Clone, install, run in 10 minutes
- Contributing Guide - Code standards, Git workflow, pull requests
- Testing Guide - Unit tests, integration tests, E2E tests
- Debugging Guide - Common issues, logs, error handling
- Git Workflow - Branching, commits, release process

### **7. FEATURES**
Complete guide to each feature:
- Mood Tracking - Logging, analytics, trends
- AI Therapy - Chat with therapist bot, conversation history
- CBT Tools - Goals, values, coping cards, exposures, safety plans
- Clinician Dashboard - Patient overview, risk alerts, messaging
- Messaging System - Secure clinician-patient communication
- Risk Assessment - C-SSRS scoring, crisis detection
- Appointments - Booking and scheduling
- Community Features - Forums, peer support
- Pet Game - Wellness ritual gamification

### **8. SECURITY**
Deep-dive into security measures:
- Security Overview - Defense in depth strategy
- Authentication - Session-based, CSRF tokens, 2FA
- Encryption - At-rest (Fernet), in-transit (HTTPS/TLS)
- CSRF Protection - Token validation, same-site cookies
- Rate Limiting - Brute force prevention, DDoS mitigation
- Input Validation - Injection prevention, sanitization
- Vulnerability Disclosure - Responsible disclosure policy
- Breach Response - Incident management procedures
- Audit Logging - Event tracking, retention, forensics

### **9. ROADMAP**
- Priority Roadmap - TIER 0-6 delivery plan with timelines
- Feature Backlog - Future enhancements by priority
- Known Issues - Current bugs, workarounds
- Tech Debt - Refactoring needed, performance optimization
- Changelog - Version history with breaking changes

### **10. REFERENCE**
Quick reference materials:
- Glossary - Technical and clinical terms
- Abbreviations - Common acronyms
- Architecture Decisions - Why we chose this tech
- License Info - Open source licenses
- Credits - Team and contributors

---

## 🔥 Critical Documents

**If you have limited time, read THESE FIRST:**

1. **[What is Healing Space?](What-is-Healing-Space.md)** - 5 min overview
2. **[Features Overview](../0-START-HERE/Quick-Features-Overview.md)** - What it does
3. **Your role-specific guide** (see Quick Navigation above)
4. **[Architecture Overview](../4-TECHNICAL/Architecture-Overview.md)** - How it works (technical)

---

## 📋 By Use Case

### "I want to deploy this to production"
1. [NHS Readiness Checklist](../2-NHS-COMPLIANCE/NHS-Readiness-Checklist.md)
2. [Railway Deployment](../5-DEPLOYMENT/Railway-Deployment.md)
3. [Environment Variables](../5-DEPLOYMENT/Environment-Variables.md)
4. [Monitoring & Alerts](../5-DEPLOYMENT/Monitoring-and-Alerts.md)

### "I want to run a clinical trial"
1. [University Readiness Checklist](../3-UNIVERSITY-TRIALS/University-Readiness-Checklist.md)
2. [Research Ethics Guide](../3-UNIVERSITY-TRIALS/Research-Ethics-Guide.md)
3. [Study Protocol Template](../3-UNIVERSITY-TRIALS/Study-Protocol-Template.md)
4. [Data Collection Guide](../3-UNIVERSITY-TRIALS/Data-Collection-Guide.md)

### "I want to integrate this with NHS systems"
1. [Compliance Framework](../2-NHS-COMPLIANCE/Compliance-Framework.md)
2. [Clinical Safety Case](../2-NHS-COMPLIANCE/Clinical-Safety-Case.md)
3. [Data Protection](../2-NHS-COMPLIANCE/Data-Protection-Impact-Assessment.md)
4. [Governance Documents](../2-NHS-COMPLIANCE/Governance-Documents.md)

### "I want to understand the code"
1. [Architecture Overview](../4-TECHNICAL/Architecture-Overview.md)
2. [API Reference](../4-TECHNICAL/API-Reference.md)
3. [Database Schema](../4-TECHNICAL/Database-Schema.md)
4. [Developer Setup](../6-DEVELOPMENT/Developer-Setup.md)

### "I want to add a new feature"
1. [Developer Setup](../6-DEVELOPMENT/Developer-Setup.md)
2. [Contributing Guide](../6-DEVELOPMENT/Contributing-Guide.md)
3. [Testing Guide](../6-DEVELOPMENT/Testing-Guide.md)
4. [Architecture Overview](../4-TECHNICAL/Architecture-Overview.md)

### "I'm a patient and just want to use it"
1. [Getting Started](Getting-Started.md) - 5 minute guide
2. [Patient Guide](../1-USER-GUIDES/Patient-Guide.md) - Full feature walkthrough
3. [FAQ](../1-USER-GUIDES/FAQ.md) - Common questions
4. [Troubleshooting](../1-USER-GUIDES/Troubleshooting.md) - Having issues?

---

## 🌍 Key Facts

| Aspect | Details |
|--------|---------|
| **Type** | Mental health companion web app |
| **Tech Stack** | Flask (Python), PostgreSQL, Groq LLM, React frontend |
| **Users** | Patients, clinicians, researchers |
| **Features** | Mood tracking, AI therapy, CBT tools, risk assessment, clinician dashboard |
| **Compliance** | GDPR, NHS IG44, clinical safety standards |
| **Status** | Production-ready, actively maintained |
| **License** | [See LICENSE](../10-REFERENCE/License-Info.md) |
| **Deployment** | Railway, AWS, self-hosted options |
| **Database** | PostgreSQL (43 tables, normalized schema) |
| **API** | REST with 210+ endpoints |
| **Testing** | 92% test coverage, automated CI/CD |

---

## ⚡ Quick Facts

- **Setup Time**: 5 minutes (local) or 5 minutes (Railway)
- **Documentation**: 150+ pages across 10 sections
- **Code**: 16,800 lines backend + 16,000 lines frontend
- **Database**: 43 tables, auto-migrated on startup
- **Security**: HTTPS, CSRF tokens, encryption at rest, rate limiting
- **Accessibility**: WCAG 2.1 compliant
- **Mobile**: Web-based, responsive design (iOS/Android via Capacitor)

---

## 🚀 Getting Started (30 Seconds)

**Want to try it right now?**

```bash
# 1. Clone
git clone https://github.com/shadowWolf88/Healing-Space-UK.git
cd "python chat bot"

# 2. Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env with your settings (GROQ_API_KEY, etc.)

# 4. Run
python3 api.py
# Visit http://localhost:5000
```

**Full setup guide:** [Developer Setup](../6-DEVELOPMENT/Developer-Setup.md)

---

## 💬 Questions or Issues?

- **Technical Help**: See [Troubleshooting](../1-USER-GUIDES/Troubleshooting.md) or [Debugging Guide](../6-DEVELOPMENT/Debugging-Guide.md)
- **NHS/Compliance**: Contact your Clinical Lead
- **Research/Trials**: See [University Trials](../3-UNIVERSITY-TRIALS/)
- **Security Issues**: See [Vulnerability Disclosure](../8-SECURITY/Vulnerability-Disclosure.md)
- **General Questions**: Check [FAQ](../1-USER-GUIDES/FAQ.md)

---

## 📖 Document Index by Topic

### User Experience
- Patient Guide
- Clinician Guide
- Getting Started
- FAQ
- Troubleshooting
- Accessibility Guide

### Clinical & Safety
- Clinical Safety Case
- Crisis Response Procedures
- Risk Assessment Documentation
- Measurement Scales
- C-SSRS Algorithm

### Compliance & Legal
- NHS Compliance Framework
- Data Protection Impact Assessment
- Governance Documents
- Compliance Checklist
- Vulnerability Disclosure

### Research & Trials
- University Readiness Checklist
- Research Ethics Guide
- Study Protocol Template
- Consent Forms
- Data Collection Guide

### Technical & Architecture
- Architecture Overview
- Database Schema
- API Reference
- Climate Algorithms
- Code Quality Standards

### Operations & Deployment
- Railway Deployment
- Local Setup
- Environment Variables
- Database Migration
- Monitoring & Alerts
- Backup & Recovery

### Development
- Developer Setup
- Contributing Guide
- Testing Guide
- Debugging Guide
- Git Workflow

### Security
- Security Overview
- Authentication
- Encryption
- CSRF Protection
- Rate Limiting
- Input Validation
- Breach Response
- Audit Logging

---

## ✅ Version Information

| Item | Value |
|------|-------|
| **Current Version** | 2.0 (PostgreSQL) |
| **Release Date** | Feb 8, 2026 |
| **Status** | ✅ Production-Ready |
| **Last Updated** | Feb 8, 2026 |
| **Python Version** | 3.9+ |
| **Database** | PostgreSQL 12+ |

---

## 📄 Document History

- **Feb 8, 2026**: Complete documentation restructure and consolidation
- **Feb 5, 2026**: Version 2.0 released (PostgreSQL migration complete)
- **Jan 28, 2026**: Clinical features complete
- **Jan 1, 2026**: Initial production launch

---

**Last Updated**: February 8, 2026  
**Maintained by**: Development Team  
**Next Review**: May 8, 2026  

