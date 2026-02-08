Data Use & GDPR Notes

Overview
- Purpose: describe how participant data will be stored, encrypted, anonymized, and shared for research.

Storage
- Primary DB: `therapist_app.db` (users, chat_history, clinical_scales, appointments, alerts).
- Ancillary DBs: `pet_game.db`, `ai_training_data.db`.

Encryption & Secrets
- `ENCRYPTION_KEY` (Fernet) encrypts PII fields. Provide via env var or SecretsManager.
- Avoid committing keys to source control.

Anonymization
- Use `training_data_manager.py` to anonymize data for training. Workflow:
  1. Confirm `data_consent` in DB.
  2. Run anonymization pipeline that strips PII and replaces user IDs with hashed tokens.

Right to be Forgotten
- Implement `delete_training_data(username)` to remove anonymized training entries and mark consent revoked.

Exports
- FHIR exports are HMAC-signed when `ENCRYPTION_KEY` is present.
- Exports require documented consent for external sharing.

Access Control
- Limit access to study team. Use secure channels for sharing logs and reports.

Ethics & IRB
- Include data management plan with IRB application. Provide sample consent form in `Consent_Form.md`.

Document last updated: 2026-01-22
