Study Protocol — Healing Space Pilot

Study title
- "Healing Space: feasibility and acceptability pilot with student clinicians and volunteers"

Objectives
- Primary: Assess feasibility and clinician-patient usability.
- Secondary: Evaluate acceptability, safety signal detection, and data collection pipelines.

Design
- Single-arm feasibility pilot over 4 weeks per participant.

Participants
- Clinicians: medical/psychology students (supervised). Training provided.
- Patients: volunteer adult students, screened for suitability. Exclude active suicidality requiring urgent care.

Procedures
- Screening & consent
- Baseline measures: PHQ-9, GAD-7, demographics
- Intervention: up to X sessions over 4 weeks; mood logging encouraged daily/weekly.
- Data collection: app logs, clinician forms, automated alerts, post-trial surveys.

Safety monitoring
- Real-time alerts via `SafetyMonitor` to supervisors.
- Weekly safety review by supervising clinician.

Outcomes & Measures
- Recruitment and retention rates
- Completion rates for mood logs and appointments
- Clinician & patient usability scores (Likert)
- Number and handling of safety alerts

Data management
- Secure storage in project DBs; encrypted PII via `ENCRYPTION_KEY`.
- Anonymization pipeline: `training_data_manager.py` for any data used in training.

Ethics
- Local IRB approval required prior to recruitment.
- Consent template: `Consent_Form.md`.

Timeline
- 2 weeks training/provisioning; 4 weeks piloting; 2 weeks analysis and debrief.

Sample size
- Pilot: 10 clinicians + 30 patients (flexible) to test processes.

Reporting
- Aggregate de-identified summary to the head of department and IRB.

Document last updated: 2026-01-22
