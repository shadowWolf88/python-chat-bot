# Additional Features & Roadmap

This document lists high-impact ideas to add to Healing Space (UK), why each helps, estimated complexity, and brief implementation notes. Use it as a decision/roadmap doc for development, research partnerships, and grant applications.

---

## Summary

Target audience: developers, researchers, clinicians, and project managers.

Purpose: Capture suggested enhancements across clinical readiness, product UX, security, data & AI, infrastructure, developer experience and business strategy. Each item includes a short rationale and a suggested implementation note so contributors (including students or pilot partners) can pick tasks.

---

## 1) Clinical & Research Readiness

- Research pilot module (Complexity: medium)
  - Why: Makes the app study-ready for feasibility pilots and academic collaborations.
  - Implementation note: Add a "Study Admin" panel to configure trials (inclusion/exclusion, schedule), tag participant data with a trial ID, add consent flow hooks, and export trial bundles (CSV / FHIR). Document a pilot protocol template.

- Built-in outcome scheduling (low)
  - Why: Automates PHQ-9/GAD-7 scheduling and reminders for trials and clinical workflows.
  - Implementation note: Extend appointments to schedule assessments and add a cron/worker job for scheduled reminders and in-app prompts.

- Research sandbox & synthetic dataset (medium)
  - Why: Enables testing and student work without using real PII or production data.
  - Implementation note: Provide a seed script that creates a synthetic demo DB and a documented pipeline for generating anonymized synthetic exports.

---

## 2) Product & User Experience

- Progressive Web App (PWA) & mobile polish (medium)
  - Why: Better mobile UX and installability without building native apps immediately.
  - Implementation note: Add manifest.json, a service worker for caching, and run Lighthouse audits. Ensure the login/auth flows are PWA-friendly.

- Offline-first mood logging & sync (high)
  - Why: Users with intermittent connectivity can still log mood and later sync—critical for engagement.
  - Implementation note: Use an offline queue in IndexedDB/localStorage and implement a reconciliation endpoint. Design conflict resolution rules.

- Onboarding & guided tours (low)
  - Why: Improves retention and reduces support overhead.
  - Implementation note: Add first-run checklist, progressive disclosure UX and tooltips for key screens.

- Accessibility & WCAG compliance (low → medium)
  - Why: Required for clinical settings and inclusive design; helpful for REC signoff and procurement.
  - Implementation note: Add ARIA attributes, keyboard navigation, color contrast checks and automated axe-core tests in CI.

- Internationalisation (i18n) (medium)
  - Why: Prepare for non-English users and multi-region pilots.
  - Implementation note: Extract UI strings, adopt a simple i18n library and ship English (UK) plus one other language as a pilot.

---

## 3) Safety, Security & Privacy (priority)

- Secret management & key rotation (medium)
  - Why: Improves production security and compliance.
  - Implementation note: Add HashiCorp Vault integration docs, scripts for rotating ENCRYPTION_KEY, and support for multiple active keys for decrypting legacy records.

- Improved logging & monitoring (low → medium)
  - Why: Faster detection of outages, errors, and safety-critical failures.
  - Implementation note: Integrate Sentry (or self-hosted Sentry/LogDNA), structured logs, and alerts for 5xx spikes and failed safety webhooks.

- Harden auth & abuse protections (low)
  - Why: Prevents brute force and protects study participants.
  - Implementation note: Add rate-limiting, account lockouts, optional CAPTCHA for signups, email verification, and failed-login alerts.

- Threat model & DPIA (medium)
  - Why: Needed for REC approvals and institutional partnerships.
  - Implementation note: Produce a documented threat model, a Data Protection Impact Assessment (DPIA), and retention/deletion policies.

---

## 4) Data, AI & Interoperability

- Model evaluation & de-risking pipeline (medium → high)
  - Why: Ensures AI responses are auditable, safe and clinically acceptable.
  - Implementation note: Add logging of assistant outputs, add a red-team prompt suite, automated checks for safety-related outputs, and an evaluation dashboard.

- Explainability & session summaries (low → medium)
  - Why: Clinicians need concise summaries and rationales for AI suggestions.
  - Implementation note: Generate brief AI summaries and highlight flagged items (safety, risk scores, key themes) alongside a short trace of reasoning when possible.

- Expand FHIR integration (medium)
  - Why: Better interoperability with EHRs and clinician workflows.
  - Implementation note: Add additional FHIR resource types, batching support, and consider SMART on FHIR readiness for future EHR integration.

- Analytics & events pipeline (low → medium)
  - Why: Track engagement, safety event frequency, and trial metrics.
  - Implementation note: Add event tracking (e.g., PostHog/Matomo/self-hosted), standard events and dashboards for PIs and ops.

---

## 5) Infrastructure & Operations

- Docker-compose + seeded demo DB (low)
  - Why: Faster onboarding for contributors and reproducible demos for students/partners.
  - Implementation note: Provide docker-compose.yml using Postgres or SQLite, an env example, and a seed script to populate demo users and data.

- CI/CD & test coverage (low → medium)
  - Why: Keep regressions out and speed feature delivery.
  - Implementation note: Add GitHub Actions for linting, unit tests, security scan (bandit/semgrep), and a deploy workflow. Add coverage reporting and a badge.

- Data persistence & DB migration notes for Railway (low)
  - Why: Prevents data loss in cloud deployments.
  - Implementation note: Document Railway volume setup, provide optional PostgreSQL config and migration scripts.

- Feature flags & staged rollouts (medium)
  - Why: Safely release changes and run A/B tests.
  - Implementation note: Implement a simple flagging mechanism (open-source Unleash or PostHog feature flags).

---

## 6) Developer Experience & Community

- API docs & SDK (low → medium)
  - Why: Encourages integrations and student projects.
  - Implementation note: Generate OpenAPI spec for api.py and create small Python/JS SDK stubs.

- Contributor onboarding & templates (low)
  - Why: Attract students and external contributors.
  - Implementation note: Add CONTRIBUTING.md, ISSUE_TEMPLATE.md, PR_TEMPLATE.md, Code of Conduct, and a curated list of "good first issues".

- Reproducible dev environment (low)
  - Why: Removes friction for students and reviewers.
  - Implementation note: Provide Makefile or dev script, a seeded demo DB and precise .env.example guidance.

---

## 7) Product features & engagement

- Personalized interventions & nudges (medium)
  - Why: Improve clinical outcomes and engagement.
  - Implementation note: Build a rules engine to schedule nudges and small interventions tied to mood/assessment triggers.

- Gamification expansion (low → medium)
  - Why: Increase retention through the pet companion and achievements.
  - Implementation note: Add achievements, streaks and an optional opt-in leaderboard with strict privacy defaults.

- Integrations (low → medium)
  - Why: Improves usefulness in clinical and daily life contexts.
  - Implementation note: Calendar sync (iCal), SMS reminders (Twilio), university SAML/Social logins, and wearable/HealthKit integration as longer-term items.

---

## 8) Legal, Compliance & Partnerships

- NHS / local trust partnership checklist (low)
  - Why: Needed to run clinical pilots with NHS partners.
  - Implementation note: Document hosting requirements, data flow diagrams, and SLAs needed for NHS partners and procurement.

- Brand & domain consolidation (low)
  - Why: Reduce name confusion and secure UK branding (you own healing-space.org.uk).
  - Implementation note: Reserve domains and social handles, and consider trademarking a distinct word/word+logo if scaling commercially.

---

## 9) UX Content & Safety

- Localised crisis resources & configurable escalation templates (low)
  - Why: Provide correct, local emergency guidance and reduce risk.
  - Implementation note: Auto-detect country via IP/user profile and show local numbers; make escalation templates configurable per pilot.

- CBT worksheets & printable templates (low)
  - Why: Clinicians often need printable artifacts for sessions.
  - Implementation note: Add fillable PDF/print views and downloadable CBT worksheets.

---

## 10) Business & sustainability

- Monetisation / tiering strategy (low)
  - Why: Long-term sustainability while respecting privacy.
  - Implementation note: Define free vs paid features and ensure paid tier respects privacy (no data sales). Consider clinician/organisation licensing.

- Grants & pilot funding pack (low)
  - Why: Helps secure pilot resources and academic partners.
  - Implementation note: Prepare a short grant pack (budget, deliverables, outcomes) suitable for internal university seed funds or NIHR small grants.

---

## Suggested Prioritised Roadmap (high-level)

- Immediate (days → 2 weeks): docker-compose dev environment + seeded demo DB; CONTRIBUTING.md; CI linter/tests; accessibility fixes; diagnostic page promotion.
- Short term (1 → 3 months): PWA basics, OpenAPI docs, event analytics (PostHog), secret management improvements (Vault notes + rotation script), sandbox dataset.
- Medium (3 → 9 months): Offline sync, model safety/evaluation pipeline, FHIR/SMART readiness, trial/study admin module, monitoring/alerts.
- Long term (9+ months): EHR integrations, native mobile apps or improved Capacitor flows, large-scale pilots/RCTs and scaling architecture.

---

## Starter tasks I can implement for you

Pick one or more and I will create issues/PRs, generate code stubs, or produce documentation:
- Docker-compose + seed data
- OpenAPI spec for api.py
- GitHub Actions CI workflow (lint/tests/security)
- Accessibility checklist + axe-core tests
- CONTRIBUTING.md and Good First Issues list
- Outreach / pilot documents for university partners

---

## Contact & Notes

This document is intended to be a living roadmap. Update priorities based on pilot needs, available student contributors, and funding.

Last updated: 2026-01-24