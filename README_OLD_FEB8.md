# Healing Space UK 🌿

**A mental health companion application combining evidence-based therapy with AI support.**

> **Version**: 2.0 (PostgreSQL) | **Status**: ✅ Production Ready | **Last Updated**: February 5, 2026

---

## 📚 Quick Navigation

### 🎯 Core Documentation
**Start with these canonical documents:**
- 📖 [Project Overview](./docs/PROJECT_OVERVIEW.md) – Architecture, design, security
- 🗺️ [Roadmap](./docs/ROADMAP.md) – What's built, what's next
- 📋 [Change Log](./docs/CHANGELOG.md) – Version history
- 🐛 [Known Issues](./docs/BUGS_AND_TECH_DEBT.md) – Current problems & workarounds
- 🔐 [Security & Compliance](./docs/SECURITY_AND_COMPLIANCE.md) – GDPR, HIPAA, NHS

**For navigation help:** See [Documentation Index](./docs/INDEX.md)

### 👤 Role-Based Guides
**Users:** [User Guide](./documentation/user_guides/USER_GUIDE.md)  
**Developers:** [Developer Setup](./documentation/developer_guides/QUICKSTART.md)  
**Clinicians:** [Clinician Guide](./documentation/user_guides/CLINICIAN_GUIDE.md)  
**DevOps:** [Railway Deployment](./documentation/infra_and_deployment/RAILWAY_DEPLOYMENT.md)

---

## ✨ Key Features

### For Patients
- 💬 **AI-Powered Therapy Sessions** - Confidential conversations with an intelligent therapist
- 📊 **Mood & Sleep Tracking** - Log daily emotional state and sleep patterns
- 🎯 **Personalized CBT Tools** - Evidence-based cognitive behavioral therapy exercises
- 💌 **Clinician Messaging** - Direct secure messaging with healthcare providers
- 🔐 **Complete Privacy** - GDPR-compliant, end-to-end encrypted

### For Clinicians
- 👥 **Patient Management** - Monitor multiple patients with consent
- 📈 **Treatment Analytics** - Track patient progress and outcomes
- 🧬 **AI Training** - Feed data into machine learning models for better predictions
- 📋 **Appointment Management** - Schedule and track sessions
- 🔔 **Automated Alerts** - Crisis detection with instant notifications

### Technical Highlights
- 🌐 **Web-Based** - Accessible from any browser (no installation required)
- 🗄️ **PostgreSQL** - Reliable, scalable database
- 🤖 **Groq LLM Integration** - Fast, accurate AI responses
- ⚡ **Flask REST API** - 210+ endpoints, fully documented
- 🧪 **Production Tested** - Comprehensive test suite

---

## 🚀 Getting Started

### Option 1: Deploy to Railway (Recommended)
See: [Railway Deployment Guide](./documentation/infra_and_deployment/RAILWAY_DEPLOYMENT.md)

### Option 2: Local Development
```bash
# Clone and setup
git clone <repository>
cd "python chat bot"

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
python3 init_postgresql.py

# Run development server
python3 api.py
# Visit http://localhost:5000
```

**Full setup guide:** [Developer Setup](./documentation/developer_guides/)

---

## 📂 Project Structure

```
/
├── api.py                          # Main Flask application (210 routes)
├── documentation/                  # Complete documentation hub
│   ├── 00_INDEX.md                # Master documentation index
│   ├── QUICKSTART.md              # 5-minute setup guide
│   ├── infra_and_deployment/      # Deployment, Railway, PostgreSQL
│   ├── developer_guides/          # API, auth, database setup
│   ├── feature_guides/            # Features, training, AI
│   ├── user_guides/               # Patient and clinician guides
│   ├── audit_and_compliance/      # Security, GDPR, audit reports
│   ├── testing_and_accessibility/ # Testing, validation reports
│   ├── roadmaps_and_plans/        # Future features, enhancement plans
│   └── archive/                   # Old documentation (for reference)
├── templates/                      # HTML templates
├── static/                         # CSS, JavaScript
├── tests/                          # Test suite (pytest)
├── project_management/             # Status tracking & roadmap
├── scripts/                        # Utility scripts
└── documentation/ (clinician_patient_trial_package/) # Trial materials

**Database**: PostgreSQL (Railway or local)
**Authentication**: Argon2/bcrypt + JWT  
**Encryption**: Fernet (AES-128)

---

## 🔐 Security & Compliance

- ✅ **GDPR Compliant** - Full right to deletion, data export, consent management
- ✅ **HIPAA-Ready** - Audit logging, encryption, access controls
- ✅ **Authentication** - Multi-factor 2FA support
- ✅ **Crisis Detection** - Automated safety monitoring with alerts
- ✅ **Encrypted Storage** - Sensitive data encrypted with Fernet
- ✅ **Audit Trail** - Complete logging of all system actions

See: [Security Audit Report](./documentation/audit_and_compliance/)
- Data encryption at rest using Fernet (ENCRYPTION_KEY environment variable).
- Password hashing with Argon2 (preferred), bcrypt fallback, and PBKDF2 fallback migration for legacy hashes.
- 2FA support via PIN with salted hashing (PIN_SALT).
- Audit logging for sensitive operations (audit.py).
- GDPR-aligned anonymization, user consent tracking, and data export/delete flows.

Integrations and optional components:
- Groq LLM integration (GROQ_API_KEY) for AI therapist (can be swapped for other LLM providers by adapting api integration).
- Optional HashiCorp Vault support (hvac) for secret management.
- Optional SFTP (paramiko) for secure file transfer of exports/backups.
- SMTP/webhook support for alerts and scheduled reminders.
- Optional PostgreSQL migration notes and guidance for cloud persistence.

Developer & operational features:
- Local backups folder with scheduled/automatic DB backups.
- CLI scripts and automation helpers (scripts/) for git hooks and deployment automation.
- Test suite (pytest) and testing guide in documentation/TESTING_GUIDE.md.
- CI/CD friendly structure and Railway deployment guidance.

## Architecture overview

- Desktop GUI: legacy_desktop/main.py — Tkinter + CustomTkinter UI with local SQLite databases and PDF report generation.
---

## 🧪 Testing

Run the test suite:
```bash
pytest -v tests/
```

Test results and coverage reports available in:
- [Testing Guide](./documentation/testing_and_accessibility/TESTING_GUIDE.md)
- [Latest Test Results](./documentation/testing_and_accessibility/TEST_RESULTS_2026_02_05.md)

---

## 🤝 Contributing

Before making changes, familiarize yourself with:
1. [API Documentation](./documentation/developer_guides/) - Endpoint reference
2. [Architecture](./documentation/00_INDEX.md#architecture) - System design
3. [Development Guide](./documentation/developer_guides/) - Best practices

---

## 📞 Support & Documentation

- **📖 Full Documentation**: [Documentation Hub](./documentation/00_INDEX.md)
- **🐛 Bug Reports**: See issue tracking in repository
- **💬 Messages**: [Messaging System Guide](./documentation/MESSAGING_USER_GUIDE.md)
- **📊 Training Data**: [Training Data Guide](./documentation/TRAINING_DATA_GUIDE.md)

---

## 📋 Key Resources

### For Deployment
- [Railway Deployment Guide](./documentation/infra_and_deployment/RAILWAY_DEPLOYMENT.md)
- [PostgreSQL Setup](./documentation/infra_and_deployment/POSTGRESQL_SETUP.md)
- [Environment Variables](./documentation/infra_and_deployment/RAILWAY_ENV_VARS.md)

### For Features
- [Feature Status & Roadmap](./documentation/roadmaps_and_plans/)
- [AI Training System](./documentation/feature_guides/AI_TRAINING_GUIDE.md)
- [Messaging System](./documentation/MESSAGING_USER_GUIDE.md)
- [Appointment Management](./documentation/APPOINTMENTS_SYSTEM.md)

### For Security & Compliance
- [API Security Audit](./documentation/audit_and_compliance/API_SECURITY_AUDIT_2026.md)
- [GDPR Implementation](./documentation/audit_and_compliance/GDPR_IMPLEMENTATION_SUMMARY.md)
- [Security Hardening](./documentation/audit_and_compliance/SECURITY_HARDENING_COMPLETE.md)

---

## 📈 Project Status

| Component | Status | Version | Last Update |
|-----------|--------|---------|-------------|
| Web API | ✅ Production | 2.0 | Feb 5, 2026 |
| Database | ✅ PostgreSQL | - | Feb 5, 2026 |
| Authentication | ✅ Complete | 2.0 | Feb 4, 2026 |
| Messaging | ✅ Complete | 1.0 | Feb 5, 2026 |
| AI Training | ✅ Complete | 1.0 | Jan 2026 |
| Clinician Features | ✅ Complete | 1.0 | Feb 2026 |

---

## 🔄 Recent Updates

**February 5, 2026**
- ✅ Fixed critical production blocker (fhir_export import)
- ✅ 100% PostgreSQL compliance verification
- ✅ Documentation consolidation complete
- ✅ Ready for production deployment

**February 4, 2026**
- ✅ Messaging system Phase 3 complete
- ✅ All 210 API endpoints functional
- ✅ Complete security audit
- ✅ Developer dashboard integration

See full history in documentation archive.

---

## 📜 License & Legal

This project is part of a **clinical trial** conducted by NHS trusts. Usage is restricted to:
- Authorized clinicians and patients in the trial
- Research and development purposes only
- Full compliance with GDPR and local data protection laws

For more information, see: [Clinician Patient Trial Package](./documentation/clinician_patient_trial_package/)

---

## 📧 Contact

For questions about:
- **Project Status**: See [documentation/00_INDEX.md](./documentation/00_INDEX.md)
- **Deployment Issues**: See [documentation/infra_and_deployment/](./documentation/infra_and_deployment/)
- **Feature Requests**: See [documentation/roadmaps_and_plans/](./documentation/roadmaps_and_plans/)
