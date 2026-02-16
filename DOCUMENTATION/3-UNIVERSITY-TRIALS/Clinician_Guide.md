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
- Platform: Healing Space is delivered as a hosted website. Clinicians and patients access it via a browser at the study URL (provided by the study admin).
- Clinician capabilities: view patient profiles, confirm appointment attendance, send approvals, view mood logs and PHQ/GAD results, and export patient data only when consent and admin permissions allow.
- Trial objective: evaluate usability and clinical fit with student clinicians and volunteer patients.

2. Roles & Responsibilities
- Clinician (student clinician): follow the study protocol, obtain consent, run sessions, complete post-session forms, escalate safety concerns to supervisor.
- Study lead / supervisor: monitor alerts, review de-identified data if requested, and perform safety oversight.
- IT contact: manages accounts, technical issues, and deploys updates.

3. Setup & Access
- Web access (recommended): the study admin will provide the site URL and account credentials. Open the URL in a modern browser (Chrome, Edge, Firefox) and log in with your assigned account. See `Web_Access_Guide.md` for step-by-step browser-only instructions.
- Clinician UI: after login, open your patient list, click a patient to view mood logs, clinical scales, upcoming appointments, and attendance controls.

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
- Data is stored securely on the hosted server and access is restricted to authorized study staff.
- Personally identifying information (PII) is protected and encrypted by the study administrators; clinicians should not need to manage encryption keys.
- Consent: only export or share identifiable patient data when explicit consent has been recorded.
- For technical details about storage, encryption, and anonymization workflows (for IT/study admins), see `Data_Use_and_GDPR.md`.

7. Study Tasks & Schedule
- Pre-trial: clinician training session (90 minutes), account provisioning, and consent practice.
- Week-of-trial: run up to X sessions per clinician (adjust per study design), complete post-session evaluations.
- End-of-trial: complete final clinician usability survey and debrief.

8. Troubleshooting
- If you cannot see a patient, appointment, or specific data in the UI: sign out and sign in again, then contact the study IT support (see `Support_Contacts.md`).
- If you encounter an error when exporting data or any unexpected behavior, do not attempt developer fixes — record the issue and contact IT/support with the time, patient username, and a short description.
- For any access or login problems, contact the study IT support rather than attempting local installation or debugging.

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
