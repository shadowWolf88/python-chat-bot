# python-chat-bot 🌿

A mental health companion application (desktop and web) that combines AI therapy, mood tracking, CBT tools, clinical assessments, gamified self-care, clinician oversight, secure storage, and GDPR-compliant training-data collection.

## ⭐ PROJECT MANAGEMENT HUB

**👉 [Start Here: project_management/README.md](project_management/README.md)** ← Single source of truth for:
- Current status & metrics
- What's happening now (daily)
- What's coming next (roadmap)
- Decisions & approvals
- Project navigation

---

## Quick links

- **Project Management**: [project_management/](project_management/README.md) - Status, roadmap, decisions
- Documentation index: documentation/00_INDEX.md
- Documentation folder: documentation/
- User Guide: documentation/USER_GUIDE.md
- Quick Start: documentation/QUICKSTART.md
- Training Data & GDPR: documentation/TRAINING_DATA_GUIDE.md and documentation/GDPR_IMPLEMENTATION_SUMMARY.md
- Deployment: documentation/DEPLOYMENT.md

## What this repository contains

This project provides both a desktop (Tkinter/CustomTkinter) and web (Flask) version of the python-chat-bot mental health companion. The repository contains:

- Desktop UI (legacy_desktop/) — full-featured Tkinter desktop application and utilities.
- Web API (api.py + templates/) — Flask REST API and web UI designed for container/cloud deployment.
- Shared modules: secrets_manager.py, fhir_export.py, secure_transfer.py, audit.py, training_data_manager.py
- Databases (local SQLite by default): therapist_app.db, pet_game.db, ai_training_data.db
- Comprehensive documentation in documentation/ (full user & developer guides)
- Tests in tests/

## Features (complete)

User-facing features:
- AI Therapy Sessions: conversational AI therapist with persistent memory, session summaries, and therapy notes.
- Mood Tracking: daily mood logs, sleep, medications, activities, and optional reminders.
- Clinical Assessments: PHQ-9 and GAD-7 scoring, historical trend charts, and automated progress reports.
- CBT Toolkit: thought records, behavioral experiments, worksheets, and guided exercises.
- Pet Companion Gamification: virtual pet that reflects user wellbeing, rewards for self-care, and pet progression stored in pet_game.db.
- Clinician Features: professional dashboard, clinician notes, appointment calendar (desktop), and FHIR export for records review.
- Crisis Detection & Escalation: automated safety monitoring, alerting via webhooks/SMTP/SFTP, and configurable escalation rules.
- FHIR Export: HMAC-signed FHIR (R4) exports of medical/assessment data for interoperability.
- Training Data Collection: GDPR-aware anonymized dataset collection pipeline with opt-in/out controls, local staging (ai_training_data.db), and export scripts.

Security & privacy features:
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
- Web API: api.py — Flask REST API, used by the web UI (templates/) and suitable for Railway/container deployment.
- Databases: SQLite by default; three logical DBs used and documented:
  - therapist_app.db — main application data, users, sessions, mood logs, clinical scales.
  - pet_game.db — gamification, pet state, rewards.
  - ai_training_data.db — anonymized training examples and consent metadata.
- Security: Fernet encryption for sensitive fields, Argon2/bcrypt/PBKDF2 password handling, audit trails, HMAC-signed FHIR exports.
- Optional: HashiCorp Vault secrets manager integration (secrets_manager.py), SFTP export (secure_transfer.py), scheduled tasks (CRON_SETUP.md).

## Installation & Quick Start (desktop & web)

Prerequisites:
- Python 3.8+
- pip

Clone and install:

```bash
git clone https://github.com/shadowWolf88/python-chat-bot.git
cd python-chat-bot
pip install -r requirements.txt
```

Environment variables (minimum required):
- ENCRYPTION_KEY — Fernet key used to encrypt DB fields (generate with cryptography.Fernet.generate_key())
- PIN_SALT — random salt for PIN hashing (secrets.token_urlsafe(32))
- GROQ_API_KEY — API key for Groq LLM (or other configured LLM provider API key)

Optional environment variables:
- DEBUG — set to 1 for developer permissive fallbacks
- VAULT_ADDR, VAULT_TOKEN — HashiCorp Vault settings
- SFTP_HOST, SFTP_USERNAME, SFTP_PASSWORD — SFTP uploads
- ALERT_WEBHOOK_URL — crisis alert webhook
- SMTP config variables — used for email alerts

Generate keys example:

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Run (desktop):

```bash
# Desktop UI (requires tkinter/customtkinter)
python3 legacy_desktop/main.py
```

Run (web API/server):

```bash
export ENCRYPTION_KEY=...
export PIN_SALT=...
export GROQ_API_KEY=...
python3 api.py
# or use the provided railway/docker configurations for container deploy
```

See documentation/QUICKSTART.md for full step-by-step instructions (including Windows instructions and PyInstaller notes).

## Testing

Install pytest and run tests:

```bash
pip install pytest
export DEBUG=1
export PIN_SALT=testsalt
export ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
pytest -v
```

See documentation/TESTING_GUIDE.md for end-to-end and integration testing details.

## Deployment

This repository includes deployment guides for:
- Local desktop distribution (PyInstaller) — see DEPLOYMENT.md and legacy_desktop notes
- Containerized web deployment (Railway, Docker) — see documentation/DEPLOYMENT.md and railway.toml
- Persistence strategies (SQLite vs PostgreSQL) and migration instructions — see documentation/POSTGRESQL_SETUP.md
- Optional automated deploy hooks and scripts (scripts/setup-git-hooks.sh)

## Configuration & Maintenance

- Automated backups: backups/ (local) and secure upload via SFTP if configured.
- Cron/periodic tasks: CRON_SETUP.md documents scheduled exports, reminders, and backups.
- Logging & audit: audit.py records sensitive actions; rotate logs and secure backups.

## GDPR, Training Data & Privacy

- Training data is collected only with explicit user consent and can be reviewed/exported/deleted per user request.
- Anonymization pipeline and storage lives in ai_training_data.db; see documentation/TRAINING_DATA_GUIDE.md for details and opt-out procedures.
- GDPR_IMPLEMENTATION_SUMMARY.md covers compliance mapping, data subject rights, retention, and deletion workflows.

## Security

- All sensitive data encrypted at rest with Fernet (ENCRYPTION_KEY).
- Passwords hashed with Argon2 (preferred), bcrypt fallback; legacy hashes are migrated on login.
- 2FA PIN with salted hashing using PIN_SALT.
- HMAC-signed FHIR exports for integrity.
- Optional HashiCorp Vault integration for production secret management.

## Crisis & Safety

- Crisis detection runs on message content and assessment scores; configurable rules trigger alerts via webhook/email/SFTP.
- Built-in escalation procedures and clinician notification flow are documented in the User Guide and crisis sections.

## Contributing

- Read .github/copilot-instructions.md for architecture notes.
- Run tests and linters before submitting PRs.
- Documentation is required for new features; add or update files in documentation/.

## Support & Disclaimer

This app is a mental health companion and not a substitute for professional medical care. In case of emergency, contact local emergency services.

For technical support: consult documentation/00_INDEX.md and open issues on GitHub if needed.

## Files & Structure (high-level)

```
python-chat-bot/
├── api.py                      # Flask API (web)
├── templates/                  # Web UI templates
├── legacy_desktop/             # Desktop-only GUI and utilities
├── documentation/              # Complete documentation and guides
├── requirements.txt
├── tests/
├── scripts/                    # automation scripts and hooks
├── fhir_export.py
├── secrets_manager.py
├── secure_transfer.py
├── audit.py
└── backups/
```

## Version & Last Updated

Version: 1.0
Last Updated: 2026-01-24

---