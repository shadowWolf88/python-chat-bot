# Roadmap: Mobile App + Backend + Website Parity

Last updated: 2026-01-25
Branch: app-development-branch (created from Milestone-B-"DEV-options---trials-ready)")

Purpose
- Produce a clear, actionable plan to implement a cross-platform mobile app (Flutter) and a production-ready backend that reuses the Milestone‑B Python code and preserves all website features.
- Keep all changes isolated to this branch so the live Railway deployment on main is unaffected.

Note about completeness
- I performed an automated listing of files in the Milestone‑B branch and inspected file contents where available. GitHub's content API is paginated; results may be incomplete. View the full branch in GitHub for the definitive file list:
  https://github.com/shadowWolf88/python-chat-bot/tree/Milestone-B-%22DEV-options---trials-ready)

File-by-file audit (root and notable files)
- .env.example — Example environment variables. Action: create .env.example for backend and mobile, and document required vars in README.
- .gitignore — OK.
- .githooks/ — present (empty in API listing). Action: inspect hooks locally; preserve or migrate useful hooks.
- .github/ — workflows not fully listed; inspect UI for CI actions. Action: copy/modify workflows to run from app-development-branch and add mobile build workflows.
- .railway_deploy, .railwayignore, railway.toml, RAILWAY_* docs, deploy_railway.sh, reset_railway_db.py — Railway-specific deployment files and docs. Action: leave in repo for reference but add new deploy docs/scripts for chosen host (Render/Fly/Cloud Run) and ensure app-development-branch does not auto-deploy to Railway.
- Procfile — small; used by process managers. Action: convert to Docker CMD/entrypoint for containerized deploy.

Core application files
- api.py (215 KB) — Monolithic API/server logic. Contains routing, chat handling, model calls, and possibly web views. Action: High priority. Steps:
  1) Open and map endpoints to routes and model call locations.
  2) Extract chat logic into chat_core.py/service classes.
  3) Create api/ FastAPI scaffold with routes, models, and dependency injection.
  4) Add adapters/ for model providers (adapters/groq_adapter.py, adapters/therapy_adapter.py placeholder).

- ai_trainer.py (13.9 KB) — Training orchestration. Action: Move to training/ folder; ensure no runtime dependency in production API.
- training_data_manager.py (17.5 KB) — Data handling & anonymization. Action: Review for PII/PHI handling; run test_anonymization.py and harden exports.
- export_training_data.py (5.1 KB), fhir_export.py (7.5 KB) — Exports. Action: Audit for PHI exposure; ensure clinician exports require RBAC and logs.
- train_model.py, train_scheduler.py, training_config.py — Training pipeline; move under training/ and document.

Database / data files
- therapist_app.db (127 KB) — SQLite DB file likely for clinician tooling or dev seed. Action: Inspect schema and data; generate Alembic models and Postgres migrations. Remove or ignore DB binary from production branches; keep a seed SQL/fixture.

Security & secrets
- secrets_manager.py (2.1 KB), remove_secrets.py (2.3 KB) — Secret handling utilities. Action: review for hard-coded secrets and rotate any leaked secrets. Migrate secret storage to platform secret manager.
- secure_transfer.py (2.0 KB) — File/attachment logic. Action: ensure encryption-in-transit and storage with access controls.

Auth & compliance
- 2FA_SETUP.md — 2FA instructions. Action: implement 2FA flows server-side (TOTP or OTP via SMS/email) as endpoints; ensure mobile app supports flows.
- VALIDATION_REPORT.md, FEATURE_STATUS.md, CLINICIAN_FEATURES_2025.md — Documentation. Action: convert clinician feature requirements into tickets/PRs and prioritize compliance work.

Web/templates/tests
- templates/ — listed empty by API; check UI for templates used by web frontend. Action: Update web templates to use new API endpoints. Ensure website feature parity (chat, streaming, model options, trials, clinician dashboards).
- tests/ — empty listing. Action: Add unit/integration tests for API and adapters.
- test_anonymization.py (10.6 KB) — Good test coverage candidate; run and expand tests.

Dev tooling & scripts
- setup.sh, setup_dev.sh, setup_cron.sh, setup_training_export_cron.sh — Useful scripts for env setup & cron jobs. Action: convert key scripts into Dockerfile and entrypoint tasks, document cron jobs via GitHub Actions or host scheduler.
- send_mood_reminders.sh — Background job. Action: implement as scheduled job using host scheduler or a worker process with Redis + Celery or cron via platform.

Media & assets
- speech.mp3 (366 KB) — Media asset. Action: move large assets to object storage (S3) and reference via URLs. Remove binary from repo if unnecessary.

Large/generator scripts
- generate_dev_readme.py (31 KB) — generator script. Action: Review for utility; keep in tools/ if useful.

Priority files to inspect next (immediate actions)
1. api.py — open and map endpoints, streaming logic, model calls. (Critical for backend refactor.)
2. therapist_app.db — extract schema, generate migrations.
3. templates/ — check for frontend integration points.
4. RAILWAY_* docs & scripts — ensure not to auto-deploy from this branch; prepare non-Railway deploy.
5. training_data_manager.py & test_anonymization.py — verify anonymization before training exports.

Per-file next steps and PR suggestions
- PR: api-refactor — Extract chat core, add adapters folder, and scaffold FastAPI app (with OpenAPI docs). Include unit tests and Dockerfile. (High priority)
- PR: db-migration — Add SQLAlchemy models, Alembic migrations, and seed fixtures from therapist_app.db.
- PR: groq-adapter — Implement adapters/groq_adapter.py to proxy Groq API with streaming support.
- PR: web-integration — Update website templates/client to consume new API endpoints and streaming.
- PR: flutter-skeleton — Add Flutter project skeleton in mobile/flutter_app/ and implement basic chat UI.
- PR: ci-cd — Add GitHub Actions workflows for backend tests/build and mobile build pipelines.

Notes on Railway and deployments
- The repo contains many Railway-specific artifacts and docs. You asked to avoid deploying from main/Railway. Recommendation:
  - Do development & deploy from app-development-branch to chosen host (Render/Fly/Cloud Run).
  - Keep Railway files for reference but add new deployment docs and CI/CD to deploy from app-development-branch only.

Next immediate step (I will perform now if you confirm)
- Deep-inspect api.py and return a detailed mapping of its endpoints, handler functions, where model calls are made, streaming implementation, and any direct dependency on Railway or environment variables. This will form the basis for the api-refactor PR.

If you confirm, I will open api.py now, analyze its contents, and update this ROADMAP.md with exact function names and a step-by-step refactor plan based on the actual code.