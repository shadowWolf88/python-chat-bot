Clinician Guide — Healing Space Trial

Purpose
- Overview: Provide clinician-facing instructions for running supervised trials of Healing Space with student clinicians.
- Goals: Safe onboarding, reliable data capture, clear crisis workflows, and minimal clinician friction.

Contents
1. Quick Summary
2. Roles & Responsibilities
3. Setup & Access
4. Clinical Workflow
5. Safety & Crisis Procedures
6. Data Handling & Privacy
7. Study Tasks & Schedule
8. Troubleshooting
9. Contacts

1. Quick Summary
- Platform: Flask web API + web UI served from `api.py`/`templates/index.html`.
- Clinician capabilities: view patient profiles, confirm appointment attendance, send approvals, view mood logs and PHQ/GAD results, export FHIR bundles when authorized.
- Trial objective: evaluate usability and clinical fit with student clinicians and volunteer patients.

2. Roles & Responsibilities
- Clinician (student clinician): follow the study protocol, obtain consent, run sessions, complete post-session forms, escalate safety concerns to supervisor.
- Study lead / supervisor: monitor alerts, review de-identified data if requested, and perform safety oversight.
- IT contact: manages accounts, technical issues, and deploys updates.

3. Setup & Access
- Account creation: Register via `/api/auth/register` or request provisioned accounts from study admin.
- Required environment: modern browser (Chrome/Edge/Firefox), stable internet. Local dev uses Python 3.10+.
- Recommended local test steps:
  - Create a venv: `python3 -m venv .venv`
  - Install deps: `.venv/bin/pip install -r requirements.txt`
  - Run app: `.venv/bin/python api.py` (defaults to `http://localhost:5000`)
- Clinician UI: log in, open patient list, use patient-detail modal to view upcoming appointments and attendance controls.

4. Clinical Workflow
- Pre-session
  - Verify patient consent and eligibility.
  - Review recent mood logs, clinical scales (PHQ-9/GAD-7), and prior session notes.
- During session
  - Use `/api/therapy/chat` to run in-session assistant if applicable.
  - For scheduled appointments, mark attendance using attendance controls; choose `attended`, `no_show`, or `cancelled` and optionally add a clinical note.
  - For crisis indicators, follow Safety workflow (section 5).
- Post-session
  - Complete clinician post-session evaluation form (see `Evaluation_Forms.md`).
  - Optionally export session bundle (FHIR) only if patient provided consent for data export.

5. Safety & Crisis Procedures
- The app includes `SafetyMonitor` which flags keywords and creates an alert in the `alerts` table.
- If SafetyMonitor flags high-risk language:
  - Immediately contact supervising clinician via phone/email.
  - Use the `send_crisis_alert(username)` webhook if configured to forward to the clinic response team.
  - Document the escalation in `audit_logs` using `log_event()`.
- For imminent risk: call emergency services and follow local clinical protocols. Do not rely solely on automated detection.

6. Data Handling & Privacy
- Data stores: three SQLite DBs by default: `therapist_app.db`, `pet_game.db`, `ai_training_data.db`.
- Encryption: PII stored encrypted with Fernet using `ENCRYPTION_KEY` env var. For testing, `DEBUG=1` allows temporary key generation.
- Consent: ensure `consent` is recorded in training data flow prior to using data for model training.
- FHIR exports: only export signed bundles when `ENCRYPTION_KEY` is set; otherwise exports are unsigned and for local/debug use only.
- GDPR: use `TrainingDataManager` for consent tracking, anonymization, and right-to-erasure flows.

7. Study Tasks & Schedule
- Pre-trial: clinician training session (90 minutes), account provisioning, and consent practice.
- Week-of-trial: run up to X sessions per clinician (adjust per study design), complete post-session evaluations.
- End-of-trial: complete final clinician usability survey and debrief.

8. Troubleshooting
- Missing appointments in UI: confirm DB has `appointments` rows, run `loadAppointments()` in front-end console.
- FHIR export errors: ensure `ENCRYPTION_KEY` present or skip signing; check `fhir_export.py` for timestamp column variants.
- Playwright/browser tests: install in `.venv` then run `python -m playwright install chromium`.

9. Contacts
- Study lead: [enter name/email]
- IT support: [enter name/email]
- Safety supervisor: [enter name/phone]

Appendix: Forms & references in this package
- `Consent_Form.md`
- `Study_Protocol.md`
- `Evaluation_Forms.md`
- `Quickstart_Local_Testing.md`


---
Document last updated: 2026-01-22
