# HEALING SPACE UK — MASTER PRODUCT ROADMAP
## The Definitive World-Class Vision
### Last Updated: March 2026 | Full Platform Audit v3.0

---

> **The Vision**
>
> Healing Space UK becomes the most clinically rigorous, genuinely human, and beautifully crafted mental health platform in the UK — the tool clinicians choose because it makes them better, that patients love because it truly meets them where they are, and that researchers trust because every data point is gold-standard.
>
> **The Healing Journey Principle**
> Every person using this platform is the hero of their own story. Recovery isn't a clinical process — it is an epic, deeply personal journey from darkness toward light. Our platform is the sacred companion: part guide, part celebration, part magic. Less clipboard, more compass. Every feature must earn its place by asking: *does this help someone move forward on their healing journey?*

---

## CURRENT STATE (March 2026)

| Dimension | Status | Notes |
|-----------|--------|-------|
| **Version** | v22.1.0 | Live at healing-space.org.uk |
| **Backend** | api.py ~27,500 lines | Flask / PostgreSQL / Groq AI |
| **Frontend** | index.html ~27,500 lines | Single-page app (SPA) |
| **Database** | 43+ tables, PostgreSQL | Railway production |
| **API Endpoints** | 210+ REST endpoints | Fully documented |
| **Security** | CSRF ✅ Rate-limiting ✅ Argon2 ✅ Input validation ✅ | Tier 0–1 complete |
| **Patient features** | 14 tabs, 17 CBT tools, AI therapy, pet companion, quests, spells, achievements, safety, messaging, community, medications, appointments, mood/wellness, history | Core complete |
| **Clinician features** | Dashboard, patient management, session notes, treatment plans, outcome measures, risk alerts, crisis detection, appointments (v2.6), DNA tracking, messaging | Core complete |
| **Developer features** | Terminal, AI chat, test runner, diagnostics, user management, broadcast | Complete |
| **Mobile** | Android APK (Capacitor) + iOS (WKWebView) | Live, ongoing fixes |
| **AI** | Groq-powered therapy, AI memory, risk prediction, smart polling | Live |
| **Documentation** | 150+ pages across 11 directories | Organised |
| **Test coverage** | 92% (40+ test files) | Comprehensive |

---

## ROADMAP STRUCTURE

This roadmap is split into **Phases** (strategic direction) and **Tracks** (parallel workstreams). Each item is tagged with:
- **Priority**: 🔴 Critical · 🟠 High · 🟡 Medium · 🟢 Nice-to-have
- **Theme tag**: `[SECURITY]` `[CLINICAL]` `[PATIENT-XP]` `[CLINICIAN-XP]` `[AI]` `[PLATFORM]` `[MOBILE]` `[DATA]`
- **Status**: ✅ Done · 🔄 In Progress · 📋 Planned · 💡 Idea

---

## PHASE 1 — HARDEN & COMPLETE (March–May 2026)
*Objective: Make every existing feature bulletproof. Fix all gaps before adding new ones.*

### 1.1 Security Hardening 🔴 [SECURITY]

| # | Item | Status | Notes |
|---|------|--------|-------|
| 1.1.1 | **Content Security Policy (CSP) headers** — prevent XSS via strict policy on scripts/styles/frames | 📋 | Add via Flask `after_request` |
| 1.1.2 | **HTTP security headers** — `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` | 📋 | One decorator touches all routes |
| 1.1.3 | **Session timeout enforcement** — auto-logout after 30min idle (patient) / 60min (clinician) with warning banner at -5min | 📋 | JS idle timer + server-side check |
| 1.1.4 | **Session revocation on password change** — all active sessions invalidated immediately | 📋 | Version token in DB |
| 1.1.5 | **Brute-force lockout on login** — 5 attempts → 15min lockout per IP + username | 🔄 | Rate limiting exists; need lockout table |
| 1.1.6 | **Generic error messages to clients** — never leak stack traces, DB errors, or field names | 📋 | Global error handler audit |
| 1.1.7 | **Systematic permission matrix audit** — every endpoint must declare required role; automated test verifies | 📋 | 210+ endpoints |
| 1.1.8 | **Dependency vulnerability scan** — `pip audit` + `npm audit` in CI | 📋 | Add to GitHub Actions |
| 1.1.9 | **SQL injection regression test** — automated scanner on all parameterised queries | 📋 | pytest-bandit |
| 1.1.10 | **GDPR data deletion cascade** — deleting a user removes ALL related data from all 43 tables | 📋 | Verify ON DELETE CASCADE coverage |
| 1.1.11 | **Penetration test prep checklist** — OWASP Top 10 self-audit document | 📋 | Required before NHS submission |

### 1.2 Clinical Completeness 🔴 [CLINICAL]

| # | Item | Status | Notes |
|---|------|--------|-------|
| 1.2.1 | **CORE-OM full UI** — scoring, interpretation, trend graph, clinician view | 🔄 | Backend done; UI incomplete |
| 1.2.2 | **ORS (Outcome Rating Scale)** — 4-item visual analogue scale, weekly completion, session tracking | 📋 | Simple, high-value for trials |
| 1.2.3 | **SRS (Session Rating Scale)** — post-session alliance feedback (4 items), auto-delivered after each session note is signed | 📋 | Critical for therapy outcome research |
| 1.2.4 | **Homework feedback loop** — patient marks homework complete/attempted/struggled → clinician sees status + optional note before next session | 📋 | Close the loop on homework |
| 1.2.5 | **Goal progress dashboard** — patient can see each CBT goal with % progress bar, milestone history, clinician notes | 📋 | Backend exists; needs UI |
| 1.2.6 | **Relapse prevention plan** — structured template: warning signs, coping steps, crisis contacts, created in-session by clinician + patient together | 📋 | High clinical value |
| 1.2.7 | **Safety plan upgrade** — Stanleys' Safety Planning Intervention (SPI) format: reasons for living, warning signs, distraction, contacts, means restriction | 🔄 | Partial; needs SPI format |
| 1.2.8 | **Medication adherence improvements** — taken/not taken per dose, side-effect logging, missed-dose alert to clinician | 🔄 | Column exists; UI incomplete |
| 1.2.9 | **Weekly outcome measure reminders** — automated nudge (in-app + email) for patients to complete PHQ-9/GAD-7/CORE-OM weekly | 📋 | Backend scheduler exists |
| 1.2.10 | **Clinician waiting list management** — approve/reject with reason, bulk approve, estimated wait time display | 🔄 | Backend partially done |

### 1.3 Patient Experience Fixes 🟠 [PATIENT-XP]

| # | Item | Status | Notes |
|---|------|--------|-------|
| 1.3.1 | **Onboarding flow** — 4-step wizard on first login: welcome → what to expect → meet your companion → first mood check-in | 📋 | No onboarding currently exists |
| 1.3.2 | **Empty state screens** — every tab that's empty should show a warm, encouraging prompt, not a blank card | 📋 | Quick UI polish pass |
| 1.3.3 | **Mobile nav polish** — ⋮ drawer active state, keyboard accessibility (tab through items) | 🔄 | Drawer implemented March 2026 |
| 1.3.4 | **Offline indicator** — banner when connection lost; retry logic on API calls | 📋 | Critical for NHS patients on poor networks |
| 1.3.5 | **Page load skeleton screens** — replace loading spinners with skeleton placeholders | 📋 | Perceived performance improvement |
| 1.3.6 | **Notification preferences** — patient controls what they're notified about (appointments, reminders, messages, quest updates) | 📋 | Backend structure exists |
| 1.3.7 | **Account settings page** — change password, change PIN, update email/phone, download my data, delete account | 📋 | GDPR required |
| 1.3.8 | **Clinician assignment display** — patient always sees their assigned clinician's name, photo, and next appointment on home tab | 📋 | Visibility of care relationship |

### 1.4 Technical Debt 🟠 [PLATFORM]

| # | Item | Status | Notes |
|---|------|--------|-------|
| 1.4.1 | **Split `api.py`** — refactor 27,500-line monolith into Flask Blueprints: `auth`, `patient`, `clinician`, `messaging`, `ai`, `admin`, `developer` | 📋 | Major but necessary for maintainability |
| 1.4.2 | **Split `index.html`** — extract large JS sections into separate bundled modules using Vite or vanilla ES modules | 📋 | Enables caching and parallel loading |
| 1.4.3 | **Consistent API error format** — every endpoint returns `{success, error, code, details}` | 📋 | Currently inconsistent |
| 1.4.4 | **Pagination everywhere** — all list endpoints (mood logs, appointments, messages) must support `page` + `per_page` | 📋 | Performance at scale |
| 1.4.5 | **Database index audit** — review all 43 tables, add missing indexes on foreign keys and search columns | 📋 | Query performance |
| 1.4.6 | **Remove duplicate CSS** — merge `theme-fixes.css` into `theme-variables.css`; reduce total CSS from 123KB | 📋 | Load time improvement |
| 1.4.7 | **GitHub Actions CI pipeline** — lint, test, security scan on every PR; block merge on failure | 📋 | Quality gate |
| 1.4.8 | **Automated database backup** — daily PostgreSQL `pg_dump` to S3/Railway volumes with 30-day retention | 📋 | Disaster recovery |

---

## PHASE 2 — ELEVATE THE EXPERIENCE (June–September 2026)
*Objective: Make the platform genuinely exceptional — features that delight patients and empower clinicians.*

### 2.1 The Healing Journey — Immersive Gamification Expansion 🟠 [PATIENT-XP]

The "Healing Journey" is the platform's beating heart. Every therapeutic action is woven into an epic narrative:

| # | Item | Status | Notes |
|---|------|--------|-------|
| 2.1.1 | **Journey Map** — visual timeline of the patient's healing journey: milestones unlocked, chapters completed, current chapter visible. Like an RPG world map. Accessible from Home tab. | 📋 | The showpiece feature |
| 2.1.2 | **Healing Chapters system** — therapy is structured as narrative chapters: e.g., "The Dark Forest" (assessment), "Finding the Light" (early CBT), "The Summit" (consolidation). Clinician advances chapters. | 📋 | Give the journey shape and meaning |
| 2.1.3 | **Companion evolution** — pet companion visually evolves (3 stages) as patient reaches major milestones. Each stage has new animations, different name, different appearance. | 📋 | Emotional investment in progress |
| 2.1.4 | **Spell crafting system** — patients collect "ingredients" (completing CBT exercises) to craft new spells (coping skills). Visual crafting UI. | 📋 | Gamify CBT skill-building |
| 2.1.5 | **Guild system (peer support)** — patients can optionally join a "Guild of Seekers" — anonymous peer group with guided weekly check-ins, moderated by AI + clinician. | 📋 | Community + accountability |
| 2.1.6 | **Seasonal events** — limited-time quests tied to real events: World Mental Health Day (Oct 10), New Year reset quests, Spring renewal quests. | 📋 | Ongoing engagement |
| 2.1.7 | **Achievement wall** — dedicated tab or section showing all earned badges with the story of how they were earned, shareable (anonymised) as a digital badge. | 📋 | Pride and reflection |
| 2.1.8 | **Daily ritual customisation** — patient builds their own morning ritual from a library (breathing, gratitude, affirmation, movement, journaling) and gets a daily "ritual card" to complete. Ritual completion tracked. | 📋 | Personalised self-care routine |
| 2.1.9 | **XP and levels system** — unified experience points across all actions (mood logs, CBT exercises, quests, therapy sessions). Level up unlocks cosmetic rewards for companion. | 📋 | Unified progression sense |
| 2.1.10 | **"Today's Quest" home widget** — daily highlighted quest on the home tab, one-tap start, progress visible | 📋 | Reduce friction to engage |

### 2.2 AI Companion Upgrade 🟠 [AI]

| # | Item | Status | Notes |
|---|------|--------|-------|
| 2.2.1 | **Persona system** — patient chooses their companion's personality: "The Sage" (wise/gentle), "The Warrior" (motivational/direct), "The Empath" (warm/nurturing). AI adapts tone and phrasing accordingly. | 📋 | Personalised AI relationship |
| 2.2.2 | **Long-term memory upgrade** — AI remembers key facts, themes, breakthroughs across all sessions. "Last time you mentioned feeling overwhelmed at work — how did that go?" | 🔄 | ai_memory exists; needs richer recall |
| 2.2.3 | **Session summaries for patients** — after each therapy chat, AI generates a 3-point "What we explored today" summary. Patient can save/share with clinician. | 📋 | Consolidate learning |
| 2.2.4 | **Mood-adaptive responses** — AI detects mood score from latest log and adapts opening of every session ("I can see you've been having a tough week...") | 📋 | Empathic AI contextualisation |
| 2.2.5 | **CBT homework suggester** — AI analyses patterns in mood logs and session history, proactively suggests the most relevant CBT exercise for this week | 📋 | Intelligent care between sessions |
| 2.2.6 | **Crisis language detection upgrade** — expand keyword list, add semantic similarity scoring (not just exact match), reduce false positives | 🔄 | Ongoing; safety_monitor.py |
| 2.2.7 | **AI-generated crisis plan** — when C-SSRS flags moderate+, AI drafts a personalised safety plan pre-populated with patient's stated reasons for living, contacts, etc. Clinician reviews. | 📋 | AI + clinical collaboration |
| 2.2.8 | **Multilingual AI responses** — detect patient language preference, respond in Welsh / Urdu / Punjabi / Polish (top UK minority languages) | 📋 | NHS equity requirement |
| 2.2.9 | **Voice input for therapy chat** — microphone button → speech-to-text → send as message (Web Speech API, no server-side processing) | 📋 | Accessibility + naturalness |
| 2.2.10 | **AI insight generation** — weekly AI-written "Insight of the Week" personalised summary delivered to patient: "Your mood is 23% higher on days you complete your morning ritual." | 📋 | Data made meaningful |

### 2.3 Clinician Experience Upgrade 🟠 [CLINICIAN-XP]

| # | Item | Status | Notes |
|---|------|--------|-------|
| 2.3.1 | **Caseload dashboard** — at-a-glance view of all patients: risk traffic lights, last seen, next appointment, outstanding homework, overdue outcome measures, all in one grid | 📋 | Clinical triage made easy |
| 2.3.2 | **Session prep assistant** — before each appointment, AI generates a 1-page briefing: recent mood trend, last session key themes, outstanding goals, recent alerts | 📋 | Save clinician 10min of prep |
| 2.3.3 | **Smart session note templates** — SOAP / BIRP / free-text with AI-assisted auto-fill: "Based on today's session topics, here's a draft..." | 🔄 | Session notes exist; AI assist needed |
| 2.3.4 | **Treatment plan co-authoring** — live edit treatment plan with patient (patient sees and can comment, clinician finalises). Collaborative care. | 📋 | Patient agency in their plan |
| 2.3.5 | **Supervisor mode** — senior clinician can view a supervisee's caseload (with appropriate consent), add supervision notes, flag cases for discussion | 📋 | Essential for NHS team working |
| 2.3.6 | **Discharge summary generator** — AI drafts a structured discharge summary from session notes, outcome measures, treatment plan progression | 📋 | Save significant admin time |
| 2.3.7 | **Outcome measure trend visualisation** — sparkline charts for PHQ-9 / GAD-7 / CORE-OM on patient profile; colour-coded thresholds | 📋 | Clinical insight at a glance |
| 2.3.8 | **Safeguarding concern logging** — structured form: concern type, risk level, action taken, referral made, timestamp. Audit trail. | 📋 | MASH / safeguarding compliance |
| 2.3.9 | **Notification preferences** — clinician controls which alerts they receive and how (in-app, email, push) | 📋 | Reduce alert fatigue |
| 2.3.10 | **Bulk messaging** — send appointment reminders, outcome measure requests, group updates to multiple patients in one action | 📋 | Time efficiency at scale |
| 2.3.11 | **Patient notes tagging** — add tags to session notes (#anxiety, #sleep, #relationship, #medication) — enables topic-based search across notes | 📋 | Clinical intelligence |

### 2.4 Messaging System Upgrade 🟡 [PLATFORM]

| # | Item | Status | Notes |
|---|------|--------|-------|
| 2.4.1 | **Real-time messaging (WebSocket)** — replace polling with WebSocket for instant message delivery. No more 10s delay. | 📋 | Major UX improvement |
| 2.4.2 | **Message encryption at rest** — all messages encrypted in DB using patient's derived key | 🔄 | Fernet available; not fully deployed |
| 2.4.3 | **File attachments** — send PDFs, images (max 10MB) — useful for worksheets, letters, resources | 📋 | Clinical utility |
| 2.4.4 | **Message reactions** — emoji reactions to messages (👍 ❤️ ✅) — reduces back-and-forth "noted" replies | 📋 | Natural communication |
| 2.4.5 | **Clinician "out of office"** — set availability window; patient sees "Dr Smith responds within 2 working days" | 📋 | Manage expectations |
| 2.4.6 | **Crisis escalation in messaging** — if patient message triggers risk score ≥ high, message thread is flagged with banner and crisis resources appear | 📋 | Safety net in messaging |

### 2.5 Community Hub Expansion 🟡 [PATIENT-XP]

| # | Item | Status | Notes |
|---|------|--------|-------|
| 2.5.1 | **Themed channels** — "#anxiety-support", "#depression", "#sleep-struggles", "#wins-board", "#cbt-practice", "#medication-chat" | 📋 | Targeted peer support |
| 2.5.2 | **Weekly guided thread** — clinician or system posts a Monday prompt: "This week's reflection: What one small act of self-care will you commit to?" — community responds | 📋 | Structured community engagement |
| 2.5.3 | **Peer badges** — earn "Encourager" badge for 20 supportive replies, "Storyteller" for sharing 5 personal updates, etc. | 📋 | Reward prosocial behaviour |
| 2.5.4 | **Anonymous mode** — option to post in community as "Healing Space Member #447" rather than username | 📋 | Reduce stigma barrier |
| 2.5.5 | **Content moderation queue** — flagged posts go to clinician review queue before publication | 📋 | Safety for vulnerable community |
| 2.5.6 | **Live group sessions** — clinician hosts a scheduled "drop-in" session in a community thread, time-limited, moderated | 📋 | Group therapy lite |

### 2.6 Appointment System (already implemented) ✅ [CLINICIAN-XP]

*Version 2.6 delivered March 2026. Remaining items:*

| # | Item | Status | Notes |
|---|------|--------|-------|
| 2.6.1 | Clinician availability slots | ✅ | Complete |
| 2.6.2 | Patient self-booking | ✅ | Complete |
| 2.6.3 | Video call link field | ✅ | Complete |
| 2.6.4 | Recurring appointments (max 12) | ✅ | Complete |
| 2.6.5 | 48h + 24h reminders | ✅ | Complete |
| 2.6.6 | DNA report | ✅ | Complete |
| 2.6.7 | **Group appointments** — clinician creates session for 2–8 patients (group therapy). Separate attendance per patient. | 📋 | Next appointment iteration |
| 2.6.8 | **Telehealth session launcher** — "Start call" button that auto-opens the video_link for both clinician + patient simultaneously | 📋 | Remove friction for video sessions |
| 2.6.9 | **Appointment letter generation** — auto-generate a formatted appointment confirmation letter (PDF) for sending to patient | 📋 | NHS administrative standard |
| 2.6.10 | **iCal/Google Calendar export** — patient and clinician can add appointment to device calendar with one tap | 📋 | Reduce DNAs |

---

## PHASE 3 — RESEARCH & SCALE (October 2026–March 2027)
*Objective: Transform the platform into a world-class research instrument and scale to NHS-wide deployment.*

### 3.1 Researcher / University Dashboard 🟠 [DATA]

| # | Item | Status | Notes |
|---|------|--------|-------|
| 3.1.1 | **Researcher role** — dedicated role with read-only access to anonymised trial data, outcome measures, usage metrics | 📋 | Required for university trials |
| 3.1.2 | **Study management** — create/manage study cohorts, enrol patients, set measurement schedule (T0/T1/T3/T6/T12 months) | 📋 | Research protocol management |
| 3.1.3 | **Consent management** — granular consent tracking: "I consent to my data being used for X study" per participant | 📋 | Ethics board requirement |
| 3.1.4 | **Data export suite** — export in CSV / SPSS / R / FHIR / JSON formats; time-period filtering; per-measure selection | 🔄 | CSV/FHIR exist; SPSS/R needed |
| 3.1.5 | **Anonymisation pipeline** — before export, all identifiable fields are replaced with pseudonymised IDs consistently | 📋 | GDPR + ethics requirement |
| 3.1.6 | **Engagement analytics** — researcher sees: DAU/WAU/MAU, feature usage heatmap, dropout point analysis, session duration by week | 📋 | Engagement science |
| 3.1.7 | **Randomisation module** — for RCT trials: assign patients to intervention vs control group randomly; track by group | 📋 | Gold standard trials |
| 3.1.8 | **Dropout prediction** — ML model predicts which patients are likely to disengage in the next 14 days; flag to clinician | 📋 | Retention science |
| 3.1.9 | **Publication-ready report** — generate a formatted summary of trial results: N, completion rates, outcome measure changes, effect sizes | 📋 | University deliverable |

### 3.2 Advanced AI & Predictive Analytics 🟡 [AI]

| # | Item | Status | Notes |
|---|------|--------|-------|
| 3.2.1 | **Predictive crisis model** — trained on platform data, predicts crisis risk 7 days ahead based on behavioural signals (login frequency, mood patterns, session engagement) | 🔄 | v2.1 started; needs training data |
| 3.2.2 | **Personalised treatment recommendations** — AI analyses similar patient profiles and suggests treatment protocol adjustments to clinician | 📋 | Precision mental healthcare |
| 3.2.3 | **Natural language processing on session notes** — extract themes, sentiment, topic clusters from session notes — show clinician trend ("anxiety themes appeared in 7 of last 10 sessions") | 📋 | Clinical intelligence layer |
| 3.2.4 | **CBT effectiveness scoring** — which CBT tools are most used and correlated with mood improvement per patient — AI reports "Thought records appear most effective for you" | 📋 | Personalised therapy optimisation |
| 3.2.5 | **Fine-tuned therapy model** — train a small model on anonymised platform conversations to improve AI therapy responses beyond generic LLM | 📋 | Proprietary AI edge |
| 3.2.6 | **Outcome prediction** — at intake, AI predicts likely PHQ-9 trajectory at 12 weeks based on presenting scores + demographics (for research benchmarking) | 📋 | Research instrument |

### 3.3 NHS Integration & Interoperability 🔴 [PLATFORM]

| # | Item | Status | Notes |
|---|------|--------|-------|
| 3.3.1 | **FHIR R4 full compliance** — all clinical data structures mapped to HL7 FHIR R4 standard | 🔄 | FHIR export exists; needs full mapping |
| 3.3.2 | **NHS Login integration** — allow patients to sign in via NHS Login (CIS2) — removes registration friction | 📋 | Major adoption enabler |
| 3.3.3 | **EMIS/SystmOne read integration** — import patient demographics, medications, diagnoses from GP system | 📋 | Requires EMIS/TPP API access |
| 3.3.4 | **GP summary export** — generate a GP-ready letter summarising therapy progress, outcome measures, discharge plan | 📋 | Continuity of care |
| 3.3.5 | **Referral pathway integration** — accept referrals from IAPT systems (PCMIS, IAPTus) electronically | 📋 | NHS standard pathway |
| 3.3.6 | **NHS Digital Data Security and Protection Toolkit** — annual submission, all controls evidenced | 📋 | Mandatory for NHS contracts |
| 3.3.7 | **ISO 27001 / Cyber Essentials Plus** — formal certification to unlock NHS procurement | 📋 | NHS SCC requirement |
| 3.3.8 | **DCB0129 Clinical Risk Management** — complete clinical safety file per NHSE standards | 📋 | Pre-market requirement |
| 3.3.9 | **IG Toolkit / DTAC compliance** — Digital Technology Assessment Criteria submission | 📋 | Mandatory for NHS rollout |

### 3.4 Platform Scalability & Infrastructure 🟠 [PLATFORM]

| # | Item | Status | Notes |
|---|------|--------|-------|
| 3.4.1 | **Multi-tenancy** — each NHS Trust or University gets an isolated data environment with its own branding, clinician team, and patient pool | 📋 | Required for multi-site deployment |
| 3.4.2 | **Horizontal scaling** — Kubernetes / Docker Compose setup; multiple gunicorn workers; load balancer | 📋 | Scale to thousands of patients |
| 3.4.3 | **Read replica** — PostgreSQL primary/replica setup; analytical queries go to replica | 📋 | Performance isolation |
| 3.4.4 | **CDN for static assets** — serve JS/CSS/images via Cloudflare or AWS CloudFront | 📋 | Reduce load time by ~60% |
| 3.4.5 | **Monitoring & alerting** — Sentry for error tracking, Datadog/Prometheus for metrics, PagerDuty for on-call | 📋 | Production operations |
| 3.4.6 | **Automated testing in CI** — 100% of existing tests running on every push; coverage gate ≥ 90% | 📋 | Quality assurance at scale |
| 3.4.7 | **Feature flags** — roll out new features to % of users before full release | 📋 | Safe deployment |
| 3.4.8 | **Disaster recovery plan** — RTO < 4 hours, RPO < 1 hour; tested quarterly | 📋 | NHS SLA requirement |

---

## PHASE 4 — MARKET LEADERSHIP (2027+)
*Objective: Features that make Healing Space UK uniquely irreplaceable.*

### 4.1 Wearable & Biometric Integration 🟡 [PATIENT-XP]

| # | Item | Status | Notes |
|---|------|--------|-------|
| 4.1.1 | **Fitbit / Apple Watch / Garmin integration** — import sleep, heart rate, activity data; correlate with mood logs | 💡 | Objective biometric data |
| 4.1.2 | **HRV (heart rate variability)** — import from wearable; correlate with stress/anxiety scores | 💡 | Physiological anxiety marker |
| 4.1.3 | **Sleep tracker deep integration** — automatic sleep diary from wearable data; clinician alert on severely disrupted sleep patterns | 💡 | Reduce self-report burden |
| 4.1.4 | **Movement-based quests** — quest: "Go for a 20-minute walk today" — auto-verified via step count from phone/wearable | 💡 | Behavioural activation gamified |

### 4.2 Accessibility & Inclusivity 🔴 [PATIENT-XP]

| # | Item | Status | Notes |
|---|------|--------|-------|
| 4.2.1 | **WCAG 2.2 AA full audit** — keyboard navigation, screen reader labels, colour contrast ratios on every component | 🟠 | NHS equality requirement |
| 4.2.2 | **Easy Read mode** — simplified language, larger text, icon-led navigation for users with learning disabilities | 📋 | Inclusive design |
| 4.2.3 | **Welsh language support** — full UI translation + AI responses in Welsh | 📋 | NHS Wales requirement |
| 4.2.4 | **Multi-language support** — i18n framework; community translations for Urdu, Punjabi, Polish, Arabic | 📋 | Serve diverse UK populations |
| 4.2.5 | **High contrast + dyslexia-friendly modes** — dedicated theme variants | 📋 | Accessibility themes |
| 4.2.6 | **Text-to-speech for AI responses** — option to have the AI companion speak responses aloud | 📋 | Accessibility + emotional connection |

### 4.3 Family & Carer Portal 🟡 [CLINICAL]

| # | Item | Status | Notes |
|---|------|--------|-------|
| 4.3.1 | **Carer account type** — with patient consent, a named carer can view: upcoming appointments, current quest progress, mood trend (last 7 days), safety plan | 📋 | Family involvement in recovery |
| 4.3.2 | **Carer resource hub** — curated articles: "Supporting someone with depression", "Understanding CBT", "When to call for help" | 📋 | Psychoeducation for carers |
| 4.3.3 | **Family messaging** — carer can message the clinician directly (separate thread from patient messages) | 📋 | Three-way care coordination |

### 4.4 Group Therapy Platform 🟡 [CLINICAL]

| # | Item | Status | Notes |
|---|------|--------|-------|
| 4.4.1 | **Group therapy sessions** — clinician creates a group (4–8 patients), group has shared calendar, group messaging, and group session notes | 📋 | IAPT Group CBT model |
| 4.4.2 | **Psychoeducation modules** — structured 8-week online courses (e.g., "Understanding Anxiety") delivered to a group with homework | 📋 | Scalable therapy delivery |
| 4.4.3 | **Group progress dashboard** — anonymised view of group mood trend, engagement, homework completion rate | 📋 | Group clinical oversight |

### 4.5 Marketplace & Ecosystem 🟢 [PLATFORM]

| # | Item | Status | Notes |
|---|------|--------|-------|
| 4.5.1 | **CBT tool library** — clinicians can build and share custom CBT tools/worksheets as templates | 💡 | Platform network effect |
| 4.5.2 | **Quest builder** — clinician designs bespoke quests for individual patients | 💡 | Personalised gamification |
| 4.5.3 | **Open API** — public API for approved third-party integrations (e.g., mindfulness apps, GP systems) | 💡 | Ecosystem play |
| 4.5.4 | **White-label offering** — private therapy practices can deploy their own branded version | 💡 | Commercial scaling |

---

## WHAT'S MISSING (Gap Analysis)

*Features present in leading platforms (Kooth, Big Health, SilverCloud, Wysa, Limbic) that we should address:*

| Gap | Competitor | Our Plan | Phase |
|-----|-----------|----------|-------|
| Onboarding flow | All | Phase 1 (1.3.1) | 1 |
| WCAG 2.2 accessibility | SilverCloud | Phase 4 (4.2.1) | 4 |
| Welsh language | NHS Wales apps | Phase 4 (4.2.3) | 4 |
| NHS Login SSO | Kooth | Phase 3 (3.3.2) | 3 |
| FHIR full compliance | Major EHRs | Phase 3 (3.3.1) | 3 |
| RCT randomisation module | SilverCloud | Phase 3 (3.1.7) | 3 |
| Carer/family portal | Kooth | Phase 4 (4.3.1) | 4 |
| Group therapy | SilverCloud | Phase 4 (4.4.1) | 4 |
| Wearable integration | Big Health | Phase 4 (4.1.1) | 4 |
| Session prep AI assistant | None (novel) | Phase 2 (2.3.2) | 2 |
| Healing Journey map | None (novel) | Phase 2 (2.1.1) | 2 |
| Companion persona system | None (novel) | Phase 2 (2.2.1) | 2 |
| Discharge summary AI | Partial (SilverCloud) | Phase 2 (2.3.6) | 2 |
| Dropout prediction | Big Health | Phase 3 (3.1.8) | 3 |

---

## UNIQUE DIFFERENTIATORS (What makes us world-class)

These are the features no other UK mental health platform has — our moat:

1. **🗺️ The Healing Journey Map** — a visual, narrative journey through recovery. Not a dashboard. A story.
2. **🐾 The Living Companion** — a virtual companion that truly evolves based on the patient's engagement, creating genuine emotional investment in progress.
3. **⚔️ Spell Crafting for CBT** — gamified skill acquisition: earn ingredients by practising CBT tools, craft spells (coping strategies) you can use in real life.
4. **🔮 Session Prep AI** — before every session, the clinician gets an AI-generated briefing. No other platform offers this.
5. **🛡️ Predictive Crisis Detection** — 7-day early warning model based on behavioural patterns (not just keyword matching).
6. **📖 Healing Chapters** — therapy as narrative chapters that the clinician and patient advance together, giving the journey shape, arc, and meaning.
7. **🎭 Companion Persona** — patient chooses their AI companion's personality. The AI adapts its tone, vocabulary, and approach. Truly personalised.
8. **💡 CBT Effectiveness Analytics** — which tools are working best for *this specific patient*, shown as data. No other platform attempts this.

---

## SECURITY ROADMAP SNAPSHOT

| Tier | Items | Status |
|------|-------|--------|
| **Tier 0** — Critical (no passwords in code, DB credentials, password hashing) | 4/4 | ✅ Complete |
| **Tier 1** — Production blockers (CSRF, rate limiting, session, XSS, input validation) | 8/11 | 🔄 3 outstanding |
| **Tier 2** — Clinical safety (C-SSRS, crisis alerts, safety planning, outcome measures) | 4/10 | 🔄 6 outstanding |
| **Tier 3** — NHS certification (CSP headers, penetration test, NHS DSP Toolkit, DTAC) | 0/8 | 📋 Phase 3 |
| **Tier 4** — Market leadership (ISO 27001, NHS Login, multi-tenancy, SOC 2) | 0/6 | 📋 Phase 4 |

---

## HEALING JOURNEY THEME PRINCIPLES

*Every feature should map to the healing journey metaphor. This table is a quick-reference:*

| Real World | Journey Metaphor |
|-----------|-----------------|
| Signing up | Answering the Call to Adventure |
| First mood check-in | Entering the Forest |
| CBT thought record | Finding a Map Fragment |
| Completing a quest | Defeating a Shadow |
| Pet companion | Your Familiar / Guide Spirit |
| Earning a spell | Learning Ancient Wisdom |
| Achievement badge | A Scar of Honour |
| Crisis moment | The Dark Night of the Soul |
| Safety plan | The Shield of Light |
| Therapy session | Counsel with the Wise Elder |
| Discharge | Return of the Hero |
| Helping others in community | Becoming a Guide for Others |

---

## PRIORITISED BACKLOG (Next 90 Days — March–May 2026)

These are the highest-value items to implement first, sequenced by impact/effort ratio:

| # | Feature | Impact | Effort | Phase |
|---|---------|--------|--------|-------|
| 1 | Patient onboarding wizard | 🔴 High | Low | 1.3.1 |
| 2 | CSP + security headers | 🔴 High | Low | 1.1.1 |
| 3 | Session timeout enforcement | 🔴 High | Low | 1.1.3 |
| 4 | CORE-OM full UI | 🟠 High | Medium | 1.2.1 |
| 5 | SRS after-session feedback | 🟠 High | Low | 1.2.3 |
| 6 | Homework feedback loop | 🟠 High | Medium | 1.2.4 |
| 7 | Goal progress dashboard | 🟠 High | Medium | 1.2.5 |
| 8 | Healing Journey Map (MVP) | 🟠 High | High | 2.1.1 |
| 9 | Companion persona system | 🟠 High | Medium | 2.2.1 |
| 10 | Caseload dashboard for clinician | 🟠 High | Medium | 2.3.1 |
| 11 | Session prep AI assistant | 🟡 Medium | Medium | 2.3.2 |
| 12 | Account settings page | 🟠 High | Low | 1.3.7 |
| 13 | Split api.py into Blueprints | 🟡 Medium | High | 1.4.1 |
| 14 | Outcome measure trend charts | 🟡 Medium | Low | 2.3.7 |
| 15 | ORS weekly scale | 🟡 Medium | Low | 1.2.2 |

---

## VERSION HISTORY

| Version | Date | Summary |
|---------|------|---------|
| v22.1.0 | March 2026 | Mobile ⋮ drawer nav, appointment v2.6 (availability, self-booking, video, recurring, reminders, DNA) |
| v2.1 | Feb 2026 | AI predictive crisis detection, smart polling |
| v2.0 | Feb 2026 | Complete security hardening (CSRF, rate limiting, Argon2), messaging system v2, developer dashboard |
| v1.x | Jan 2026 | University trials launch, CBT tools, gamification, clinical assessments |

---

*This roadmap is a living document. Review monthly. Every item must pass the Healing Journey test: does this help someone move forward on their journey? If yes, build it. If not, question it.*

---

**Document maintained by:** Development Team
**Location:** `DOCUMENTATION/9-ROADMAP/MASTER_ROADMAP.md`
**Next review:** June 2026
