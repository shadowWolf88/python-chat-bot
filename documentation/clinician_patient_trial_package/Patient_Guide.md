Patient Guide — Healing Space Trial

Purpose
- Help participants understand the study, the platform, privacy, and how to use the app safely.

Contents
1. Welcome & Overview
2. Participation & Consent
3. How to Use the App
4. What To Expect in Sessions
5. Data & Privacy
6. Safety & Support
7. Withdrawal
8. FAQ

1. Welcome & Overview
- Healing Space is a digital mental health support platform used for guided conversations, mood tracking, and optional clinician-supported sessions.
- As a trial participant you will use the web app to log mood, complete brief questionnaires (PHQ-9, GAD-7), and optionally attend sessions with a student clinician.

2. Participation & Consent
- Voluntary: participation is voluntary. You may withdraw at any time without penalty.
- Consent: before joining, you will review and sign the consent form provided by the study team. Sensitive personal data will be protected. See `Consent_Form.md`.

3. How to Use the App (Web users — non-technical)
- Access: the study admin will give you a URL and account credentials. Open the URL in a browser and log in.
- Dashboard: after logging in you can view mood logs, pet gamification features, and scheduled appointments.
- Logging mood: use the "Mood" tab to enter mood, sleep, meds and short notes. Logs help clinicians and researchers understand changes over time.
- Chat: optional AI-assisted chat for guided support; not a replacement for crisis care.

Developer notes (admins only): local dev and install instructions are in `Quickstart_Local_Testing.md` and are not required for participants.

4. What To Expect in Sessions
- Student clinicians will conduct sessions under supervision.
- Sessions may be audio/video or text-based, depending on study settings.
- Attendance: clinicians will mark whether you attended; this helps the study track engagement.

5. Data & Privacy
- What is stored: mood logs, clinical scales, chat transcripts, and appointment metadata.
- Encryption: PII is encrypted at rest when `ENCRYPTION_KEY` is configured by the administrators.
- Anonymization: training/analysis data is anonymized per the project's GDPR workflows; you may opt-out of having your data used for model training.

6. Safety & Support
- If you experience a crisis, contact emergency services immediately.
- The app includes automated crisis detection but it is imperfect — always escalate to a clinician if concerned.
- Support contacts: your supervising clinician and the study helpline (provided during consent).

7. Withdrawal
- To withdraw, notify the study team. Data already used in analysis may not be removable from derived datasets; raw data can be deleted per GDPR workflows.

8. FAQ
- Q: Is the AI a clinician? A: No. The AI provides supportive prompts only; it does not provide medical advice.
- Q: Who can access my data? A: Study team members with approved access; exports are only produced with consent.

Document last updated: 2026-01-22
