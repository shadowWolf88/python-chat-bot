# HEALING SPACE UK — MASTER PRODUCT ROADMAP
## World-Class Mental Health Platform: The Definitive Plan
### Audit Date: February 17, 2026 | Full Platform Audit + Strategic Vision

---

> **Vision**: Healing Space UK becomes the most clinically rigorous, technologically advanced, and genuinely human mental health platform in the UK — the tool that clinicians choose because it makes them better at their jobs, that patients love because it meets them where they are, and that sets the standard for what digital mental health care should be.

---

## CURRENT STATE SNAPSHOT (Feb 20, 2026 — updated)

| Dimension | Status |
|-----------|--------|
| **Security** | ✅ TIER 0-1 complete — 180+ tests passing, production-grade |
| **Backend** | api.py ~17,500 lines, Flask/PostgreSQL/Groq, 325+ endpoints |
| **Frontend** | index.html ~17,000 lines, monolithic SPA |
| **Database** | 52+ tables, PostgreSQL on Railway |
| **Patient Features** | 14 tabs, 17 CBT tools, AI therapy, pet, community, messaging, CORE-OM/ORS/SRS forms, SOS button |
| **Clinician Features** | Dashboard live, session notes, treatment plan builder, caseload outcome tracker, risk monitor, messaging |
| **Developer Features** | Terminal, AI chat, inbox, broadcast, QA, user mgmt, Post Update |
| **AI** | Groq-powered therapy chat, AI memory, risk detection, summaries, content-filter fallback |
| **Compliance** | GDPR foundations in place, NHS compliance not yet started |
| **Mobile** | Capacitor configured, not production-ready |
| **Tests** | 180+ passing, gaps in clinical logic coverage |

---

## WHAT HAS BEEN COMPLETED ✅

- Full TIER 0-1 security hardening (CSRF, rate limiting, XSS, session management, access control, connection pooling, anonymization, input validation, audit logging)
- Clinician dashboard with patient caseload, risk monitor, messaging, approvals
- Patient: 17 CBT tools, AI therapy with crisis detection, pet, community, mood/wellness logging, C-SSRS, safety planning, appointments, FHIR export
- Full internal messaging system (inbox, sent, compose, conversation threads, templates, scheduling, group messaging, search)
- Developer dashboard with terminal, AI assistant, inbox, broadcast, post updates, QA, user management, feedback, stats
- Dark/light theme system with full CSS variable coverage
- Notification system with dark mode support, human-readable notification labels (no more "undefined" headers)
- Remember Me sessions, developer inbox, Post Update feature (all Feb 17, 2026)
- Community forum, achievements/badges, gratitude logging, pet system
- FHIR data export, AI training data manager (GDPR-compliant)
- **Phase 1.1 — Session Notes** (Feb 20, 2026): SOAP/BIRP/free-text formats, 6 presenting-problem templates, draft/sign-off/24h-lock workflow, full note history per patient
- **Phase 1.2 — Treatment Plan Builder** (Feb 20, 2026): SMART goals with click-to-update status (active/achieved/modified/dropped), intervention selection, session parameters, outcome targets, clinician+patient co-signature, plan versioning, discharge criteria
- **Phase 1.3 — Extended Outcome Measures** (Feb 20, 2026): CORE-10, CORE-OM (34-item paginated, real questions from CORE System Trust), WEMWBS, ORS (VAS sliders), SRS (VAS sliders) — all with validated server-side scoring and severity banding; Caseload Outcome Tracker in clinician overview with trend arrows
- **Phase 1.6 — SOS Crisis Button** (Feb 2026): Persistent red button on every screen, crisis overlay with Samaritans/SHOUT/NHS 111, safety plan display, clinician alert, grounding exercises
- Message archive bug fixed (is_archived column migration + inbox filter)
- Groq API 400 content-filter handling: compassionate clinical fallback response instead of crash

---

## PHASE 1 — FOUNDATION POLISH & QUICK WINS
### Timeline: Weeks 1–4 | Focus: Fix gaps, complete half-built features, establish quality baseline

---

### 1.1 CLINICIAN: Session Notes System ✅ COMPLETE (Feb 20, 2026)
**Priority: CRITICAL — This is the #1 thing clinicians need that's missing**

Clinicians cannot do their jobs without session documentation. Every clinical session needs notes.

- **SOAP Notes** (Subjective, Objective, Assessment, Plan) — standard clinical format
- **BIRP Notes** (Behaviour, Intervention, Response, Plan) — alternative format
- **Free-text with structured prompts** — hybrid approach
- **Session note templates** per presenting problem (depression, anxiety, trauma, OCD, eating disorders)
- **Quick note entry** from patient detail view — one click to start
- **Note history** — full chronological log per patient
- **Sign-off / lock mechanism** — notes locked after 24 hours for audit purposes
- **Clinician can view their own notes history** with search and filter
- **Patient cannot see session notes** (clinical confidentiality by default)
- **Export session notes** as PDF for supervision, referral, or records requests

**Backend**: `session_notes` table, `GET/POST/PUT /api/clinician/session-notes/<patient>` endpoints
**Frontend**: New subtab in patient detail view, rich text editor with templates

---

### 1.2 CLINICIAN: Treatment Plan Builder ✅ COMPLETE (Feb 20, 2026)
**Priority: CRITICAL — Required for clinical governance**

Every patient needs a documented, co-produced treatment plan.

- **Goals** — SMART goals tied to presenting problems, with target dates
- **Interventions** — which CBT approaches, tools, or techniques will be used
- **Frequency & Duration** — planned session cadence
- **Review dates** — automatic reminders when a review is due
- **Patient co-signature** — patient can view and agree to their plan
- **Treatment plan versioning** — previous versions preserved
- **Link to outcomes** — PHQ-9/GAD-7/CORE-OM targets explicitly stated
- **Discharge criteria** — what success looks like (so clinician and patient both know when therapy ends)
- **Export to PDF** — for referrals, supervision, records

**Backend**: `treatment_plans` table
**Frontend**: New "Treatment Plan" subtab in patient detail view

---

### 1.3 CLINICIAN: CORE-OM / WEMWBS Outcome Measures ✅ COMPLETE (Feb 20, 2026)
**Priority: HIGH — Standard in UK mental health services**

PHQ-9 and GAD-7 exist but are insufficient. Add:

- **CORE-OM** (Clinical Outcomes in Routine Evaluation — 34-item) — the UK standard
- **CORE-10** — brief version for session-by-session tracking
- **WEMWBS** (Warwick-Edinburgh Mental Wellbeing Scale) — positive wellbeing
- **ORS** (Outcome Rating Scale) — 4-item ultra-brief session check-in
- **SRS** (Session Rating Scale) — therapeutic alliance measurement per session
- **Pre/post comparison** — change scores with clinical significance thresholds
- **Recovery trajectories** — is this patient on a recovery path?
- **Reliable Change Index** — has this person changed beyond measurement error?
- **Clinician dashboard** showing all patients' latest scores in one view

**Backend**: Extend `clinical_scales` table with new scale types
**Frontend**: Add to patient assessments tab, add to clinician overview

---

### 1.4 CLINICIAN: Waiting List Management
**Priority: HIGH — Every service has a waiting list**

- **Referral intake form** — capture referral source, presenting problem, urgency rating
- **Waiting list queue** — ordered by urgency, date received, risk level
- **Automated waiting time estimates** — based on current caseload capacity
- **Patient on waiting list portal** — patient sees their position, can do CBT self-help while waiting
- **First appointment allocation** — one-click to move from waiting list to active caseload
- **Capacity dashboard** — clinician's current caseload vs. max capacity
- **Referral source tracking** — GP, self-referral, IAPT, inpatient discharge

---

### 1.5 PATIENT: Medication Tracker & Reminders
**Priority: HIGH — Medication adherence is a major outcome predictor**

- **Medication list management** — add medications with dose, frequency, prescriber
- **Daily reminder system** — configurable notification times
- **Taken/missed log** — patient marks each dose
- **Side effect journal** — link side effects to mood data
- **Adherence chart** — weekly/monthly adherence rate
- **Clinician visibility** — clinician can see adherence data (with consent)
- **Refill reminder** — alert when medication supply is running low (based on dose + quantity)
- **'About my medication' info** — general educational info (not prescribing advice)

**Note**: Existing `patient_medications` table exists. This builds the full UI and reminder system.

---

### 1.6 PATIENT: Permanent SOS / Crisis Button ✅ COMPLETE (Feb 2026)
**Priority: CRITICAL — Safety feature that should have been Day 1**

- **Persistent red SOS button** visible on EVERY screen, every tab, always accessible
- **Crisis resource overlay** — immediate display of:
  - Samaritans: 116 123
  - Crisis text line: Text SHOUT to 85258
  - NHS 111 (option 2 for mental health)
  - Patient's personal emergency contacts (from safety plan)
  - Patient's clinician's emergency contact
  - Their safety plan — displayed immediately
- **One-tap call** links to crisis lines
- **Alert clinician** — optional button to send immediate alert to assigned clinician
- **Grounding exercises** — quick-access breathing, 5-4-3-2-1, box breathing
- **This is not** a replacement for 999 — always display "Call 999 if you or someone else is in immediate danger"

**Design**: Small floating button bottom-right of every view, expands to full overlay.

---

### 1.7 PATIENT: Recovery Milestones & Progress Dashboard
**Priority: HIGH — Patients need to see their journey**

- **Visual recovery timeline** — from first session to now
- **Milestone celebrations** — "You've been tracking your mood for 30 days", "First week without a red day", "PHQ-9 score dropped below 10 (mild range)" etc.
- **Progress chart** — mood trend over time with rolling average
- **CBT tool usage stats** — how many times they've used each tool
- **Streak tracking** — daily check-in streak, therapy session streak
- **Comparison to baseline** — "Your average mood is 2.3 points higher than when you started"
- **Clinician can send personal milestone messages** — e.g., "I noticed your PHQ-9 has improved significantly — well done"
- **Shareable summary card** — patient can download/share their recovery summary

---

### 1.8 DEVELOPER DASHBOARD: Real-Time System Monitoring
**Priority: HIGH — Currently flying blind**

- **Live error feed** — real-time display of Python exceptions and 500 errors
- **API latency dashboard** — response times for every endpoint, P50/P95/P99
- **Active users** — how many users are currently logged in and on which tab
- **Database performance** — slow query detection, connection pool status
- **Health check history** — uptime timeline, deployment markers
- **Error rate trends** — errors per hour/day with alerting thresholds
- **Memory & CPU** — Railway container metrics
- **Failed login attempts** — potential attack detection
- **API call volume** — which endpoints are hit most frequently

---

### 1.9 DEVELOPER DASHBOARD: User Journey Analytics
**Priority: HIGH — You can't improve what you don't measure**

- **Funnel analysis** — where do users drop off? (Registration → First mood log → First therapy session → 7-day streak)
- **Feature usage heatmap** — which tabs/tools are used most/least
- **Session duration** — how long do users spend per session
- **Retention cohorts** — day 1, 7, 30, 90 retention rates
- **Patient engagement score** — composite metric of activity, diversity of tools used, streak
- **Clinician efficiency metrics** — notes per session, time to respond to messages, caseload size
- **Outcome correlation dashboard** — which features correlate with best PHQ-9/GAD-7 improvement?

---

### 1.10 DEVELOPER DASHBOARD: Feature Flag & A/B Testing
**Priority: MEDIUM — Essential for iterating without risk**

- **Feature flag management** — toggle features on/off per role, per user, or % rollout
- **A/B test creation** — define variants, split traffic, measure outcomes
- **Rollout controls** — gradual rollout (5% → 25% → 50% → 100%)
- **Instant rollback** — disable any feature immediately
- **A/B results dashboard** — statistical significance, conversion rates

---

## PHASE 2 — CLINICAL EXCELLENCE
### Timeline: Months 1–3 | Focus: Make this the best clinical tool available

---

### 2.1 AI-POWERED PREDICTIVE CRISIS DETECTION
**Priority: CRITICAL — Could save lives**

The current safety monitor detects crisis in real-time chat. Extend this to predictive detection BEFORE crisis happens.

**Signals to analyze** (with consent):
- Sudden drop in mood logging frequency (patient going quiet)
- Rapid deterioration in PHQ-9/GAD-7 scores
- Language patterns in therapy chat changing (increased hopelessness language)
- Reduced engagement with positive tools (pet, gratitude, community)
- Missed appointments combined with mood decline
- Social withdrawal patterns in community forum activity
- Time of day changes (logging only at 3am)
- Decreased message response time (to clinician messages)

**Output**:
- **Yellow flag** — "Patient engagement has dropped significantly. Consider reaching out."
- **Orange flag** — "Multiple risk indicators detected. Review recommended within 24 hours."
- **Red flag** — Immediate alert to clinician + duty team (same as current crisis system)
- **AI reasoning** — why the system flagged this patient (transparent, explainable)
- **Recommended clinician action** — suggested response based on patient history

**Key principle**: AI flags, humans decide. No automated actions without clinician review.

---

### 2.2 AI CLINICAL INTELLIGENCE LAYER FOR CLINICIANS

Give clinicians superpowers with AI that does the heavy lifting:

**2.2a Weekly AI Patient Summary**
- Auto-generated every Monday for each patient
- Covers: mood trends (7-day), therapy chat themes, CBT tool usage, risk changes, any flags
- Plain English narrative + key stats
- One-click to review or dismiss
- Clinician can add their own notes to summary

**2.2b AI Session Preparation Brief**
- Before each appointment, auto-generate a "session prep" document
- Last session notes (brief), since-last-session activity, mood trend, open homework items
- Suggested topics/themes based on patient's current state
- Evidence-based suggestions ("Patient's PHQ-9 rose 4 points — consider reviewing medication adherence")

**2.2c AI Session Notes Assist**
- After a session, clinician types rough bullet points
- AI formats them into proper SOAP/BIRP structure
- Clinician reviews, edits, signs off
- AI suggests follow-up homework based on session themes

**2.2d Caseload Intelligence Dashboard**
- Which patients haven't been contacted in X days?
- Which patients' outcomes are stagnating?
- Which patients have had recent risk escalations?
- "Patients who may need a check-in" — AI-ranked list
- Caseload risk heatmap — visual overview of entire caseload by risk level

**2.2e Treatment Recommendation Engine**
- Based on presenting problem, PHQ-9/GAD-7 scores, previous treatment response
- Suggest evidence-based interventions (NICE guidelines aligned)
- "Patients with similar profiles responded well to Behavioural Activation + Thought Records"
- Not prescriptive — always "consider" rather than "must"

---

### 2.3 GROUP THERAPY MODULE
**Priority: HIGH — Major missing clinical capability**

- **Clinician can create a therapy group** — name, type (CBT, DBT, bereavement, anxiety etc.), max size, schedule
- **Group session facilitation** — in-app group messaging thread for between-session communication
- **Group CBT exercises** — shared worksheets that group members complete and share
- **Group mood check-in** — clinician can see aggregate mood of the group before a session
- **Group resources library** — clinician uploads/shares resources with the group
- **Individual vs. group tracking** — clinician sees both individual progress and group trends
- **Group alumni** — past members can maintain access to resources they found helpful

---

### 2.4 PEER SUPPORT & MENTORING
**Priority: MEDIUM — Powerful adjunct to therapy**

- **Peer mentor matching** — patients who have made significant recovery can opt-in as peer mentors
- **Mentor matching algorithm** — by presentation, age range, experience
- **Structured peer conversations** — safe, supported interaction with matched peer
- **Peer mentor training resources** — psychoeducation, how to support, what to do in crisis
- **Clinician oversight** — clinician sees peer support activity, can intervene if needed
- **Testimonials** — anonymized recovery stories from consenting users (inspiration)

---

### 2.5 DISCHARGE & OUTCOME REPORTING
**Priority: HIGH — Required for governance**

- **Discharge planning workflow** — clinician and patient agree discharge criteria upfront (linked to Treatment Plan)
- **Discharge summary generator** — AI-assisted summary of treatment, outcomes, ongoing recommendations
- **Post-discharge check-in schedule** — automatic 1-month, 3-month, 6-month follow-up nudges
- **Stepped care recommendations** — on discharge, recommend appropriate step-up/step-down services
- **Referral letter generator** — if patient needs higher-level care, generate referral letter draft
- **Anonymized outcome reporting** — aggregate data for service reports, NHS reporting, CQC
- **Comparative effectiveness** — which treatment approaches yield best outcomes? (anonymized)

---

### 2.6 CLINICAL SUPERVISION MODULE
**Priority: MEDIUM — Essential for professional standards**

- **Supervision booking** — clinicians can book supervision sessions within the platform
- **Case discussion threads** — anonymized patient discussions between clinician and supervisor
- **Supervision log** — mandatory supervision records (regulatory requirement)
- **Reflective journal** — clinician's private reflective practice notes
- **CPD tracking** — log continuing professional development hours
- **Peer case consultation** — with consent, brief anonymized case presentations for peer review

---

### 2.7 APPOINTMENT SYSTEM UPGRADE
**Priority: HIGH — Current system is basic**

Current state: appointments exist in DB, basic display. Need:

- **Full calendar view** — month/week/day, colour-coded by type
- **Clinician availability slots** — clinician sets available times
- **Patient self-booking** — patient picks from available slots (no more manual booking)
- **Video call integration** — built-in video or Whereby/Zoom link generation
- **Appointment reminders** — 48 hours, 24 hours, 1 hour before (SMS/email/in-app)
- **Did Not Attend (DNA) tracking** — record and alert on repeated DNAs
- **Waitlist buffer** — if appointment cancelled, automatically notify next patient on list
- **Recurring appointment patterns** — weekly, fortnightly slots
- **Cancellation policy enforcement** — 24-hour cancellation notice, reason capture
- **Telehealth vs. in-person tracking**

---

### 2.8 SAFEGUARDING & DUTY OF CARE WORKFLOW
**Priority: CRITICAL — Legal obligation**

- **Safeguarding concern logging** — structured recording of any child/adult protection concerns
- **Multi-agency referral form** — generate completed MASH/safeguarding referral documentation
- **Duty clinician system** — out-of-hours coverage assignment and contact
- **Escalation protocol** — step-by-step workflow when risk becomes critical
- **Legal/ethical decision log** — record Gillick competency decisions, capacity assessments
- **Mandatory reporting tracker** — legal obligations met and documented
- **Secure information sharing** — encrypted channel for inter-agency communication

---

## PHASE 3 — PATIENT EMPOWERMENT & ENGAGEMENT
### Timeline: Months 2–4 | Focus: Make patients want to come back every day

---

### 3.1 PERSONALIZED DAILY RITUAL ENGINE
**Priority: HIGH — Engagement depends on habit formation**

Instead of generic tabs, each patient gets a personalized daily experience:

- **Morning check-in ritual** — customized 2-minute daily opener (mood, sleep, one intention)
- **Daily challenge** — AI-selected based on their goals and progress ("Today's challenge: Go outside for 10 minutes")
- **Evening wind-down** — brief gratitude, day reflection, tomorrow's intention
- **Habit streaks** — personalized to their specific habits (not generic)
- **Personalized reminders** — learn when this patient is most responsive and send notifications then
- **Ritual builder** — patient designs their own morning/evening routine with tools from the platform

---

### 3.2 PSYCHOEDUCATION LIBRARY
**Priority: HIGH — Therapy works better when patients understand the model**

- **Video library** — short (3-5 min) evidence-based psychoeducation videos
- **Articles** — clinical-quality plain-English articles on mental health topics
- **Topics**: depression, anxiety, OCD, trauma, bipolar, personality disorders, sleep, relationships, medication
- **Clinician curated** — clinician can assign specific articles to a patient ("Please read this before our next session")
- **Reading history** — clinician can see what patient has read
- **Progress quizzes** — optional understanding checks
- **Downloadable resources** — worksheets, guides to take offline

---

### 3.3 MINDFULNESS & MEDITATION CENTRE
**Priority: MEDIUM — Major evidence base, expected feature**

- **Guided meditation library** — 5 to 30 minute sessions, voice-guided
- **Sleep meditations** — specifically for insomnia and sleep anxiety
- **Breathwork library** — beyond box breathing: 4-7-8, Wim Hof, trauma-sensitive breathwork
- **Body scan exercises** — MBCT/MBSR aligned
- **Progressive muscle relaxation** — audio guided
- **Completion tracking** — streaks, minutes practiced, favourite sessions
- **Clinician prescription** — assign specific practices as homework
- **Mindfulness check-in** — 5-second pre-session mindfulness moment before therapy chat

---

### 3.4 WEARABLE & HEALTH DATA INTEGRATION
**Priority: MEDIUM — Future standard of care**

- **Apple Health / HealthKit** — steps, sleep, heart rate, HRV
- **Google Fit** — Android equivalent
- **Fitbit API** — sleep stages, activity, resting heart rate
- **Oura Ring** — readiness, sleep quality
- **Automatic mood-health correlation** — "On days you sleep <6 hours, your mood is 2.1 points lower on average"
- **Clinician insights** — anonymized data visible with patient consent
- **Interventions based on data** — low sleep detected → automatic sleep hygiene resource suggestion

---

### 3.5 FAMILY & CARER PORTAL
**Priority: MEDIUM — Carers are critical in recovery**

- **Carer account type** — linked to patient with explicit consent
- **Carer view** — limited, patient-controlled visibility (not session notes — never clinical content)
- **Shared goals** — patient can share specific goals with carer
- **Carer resources** — how to support someone with depression/anxiety/trauma
- **Crisis plan sharing** — patient can share their safety plan with carer
- **Carer messaging** — message clinician directly (if patient consents)
- **Carer wellbeing check** — brief carer burden assessment (caring takes a toll)

---

### 3.6 GAMIFICATION 2.0
**Priority: MEDIUM — Existing pet system can be significantly extended**

Current state: Basic pet system with some achievements. Extend:

- **Full achievement system** — 50+ achievements across all platform areas
- **Recovery badges** — meaningful clinical milestone badges (not just streaks)
- **Pet evolution** — pet grows, changes, unlocks new environments as patient progresses
- **Challenges** — weekly CBT challenges with rewards
- **XP system** — unified XP across all activities
- **Leaderboards** — opt-in community leaderboards (anonymized) for weekly challenges
- **Seasonal events** — holiday-themed challenges and special pet accessories
- **Reward shop expansion** — more items, themes, customizations
- **Friend system** — patients can add recovery buddies (opt-in, anonymized)

---

### 3.7 VOICE MOOD LOGGING
**Priority: MEDIUM — Accessibility and engagement**

- **Voice note mood logging** — speak your mood instead of typing
- **Transcription** — convert to text for analysis
- **Tone analysis** — detect emotional valence from voice (requires explicit consent)
- **Voice therapy journaling** — record voice journal entries
- **Voice commands** — "Log my mood as 7", "Start breathing exercise"
- **Accessibility** — critical for users with motor difficulties or dyslexia

---

### 3.8 PEER RECOVERY COMMUNITY 2.0
**Priority: MEDIUM — Current community is basic**

Current state: Community posts exist but basic. Extend:

- **Themed rooms** — separate spaces for different presentations (anxiety room, depression room, general)
- **Anonymous posting mode** — post without username visible
- **Moderation tools** — AI content moderation + human moderator role
- **Community challenges** — group challenges (e.g., "7-day outdoor challenge")
- **Recovery stories** — dedicated section for sharing recovery journeys
- **Community events** — virtual group mindfulness sessions, Q&A with professionals
- **Crisis detection in community** — safety monitor extended to community posts
- **Resource sharing** — community-curated helpful resources

---

### 3.9 PERSONALIZED RELAPSE PREVENTION PLAN
**Priority: HIGH — Critical for sustained recovery**

- **Warning signs identification** — patient documents their personal early warning signs
- **Personal triggers** — what makes things worse for this patient specifically
- **Coping strategy ranking** — which strategies work best for them (learned from usage data)
- **Social support map** — who they can call, what they can ask for
- **Graded response plan** — "If I notice X, I will do Y. If Y doesn't help, I will do Z"
- **Clinician co-produced** — clinician and patient complete it together
- **Living document** — updated throughout therapy as patient learns more about themselves
- **Crisis plan integration** — seamlessly connects to safety plan

---

## PHASE 4 — ADVANCED AI & INTELLIGENCE
### Timeline: Months 3–6 | Focus: AI that genuinely improves clinical outcomes

---

### 4.1 CONVERSATIONAL AI THERAPY EVOLUTION
**Priority: HIGH — Core differentiator**

Current state: AI therapy chat with crisis detection and memory. Evolve to:

- **Therapeutic modality specialization** — AI adapts approach based on clinician's chosen modality (CBT, ACT, DBT, CFT, EMDR-informed)
- **Session arc** — AI structures longer conversations with a beginning, middle, end
- **Homework generation** — AI suggests personalized homework based on session content
- **Formulation awareness** — AI incorporates the clinician's case formulation into responses
- **Between-session AI therapist** — available 24/7, but clearly positioned as supplement not replacement
- **Tone calibration** — patient can adjust AI's communication style (warmer/more direct/more validating)
- **Crisis moment protocol** — special mode when in acute distress, different from regular therapy mode
- **Session summaries** — after each AI therapy session, auto-generate a summary for the patient to keep
- **Therapy skill practice** — AI drills CBT skills (thought challenging, behavioural experiments) in conversation form

---

### 4.2 MOOD PREDICTION ENGINE
**Priority: HIGH — Genuinely innovative**

Using accumulated patient data (with consent):

- **7-day mood forecast** — predicted mood trajectory based on patterns
- **Risk factor identification** — "Historically, your mood drops on Mondays and after poor sleep"
- **Proactive intervention** — predicted bad day → app suggests extra support that morning
- **Seasonality detection** — SAD patterns, anniversary reactions
- **Menstrual cycle tracking** (opt-in, for applicable users) — correlation with mood patterns
- **Pattern disruption alerts** — "Your pattern is breaking in an unusual way — want to talk about it?"

---

### 4.3 AI INTAKE & ASSESSMENT
**Priority: HIGH — Transforms the onboarding experience**

Currently: manual registration then immediate therapy access. Replace with:

- **Conversational intake assessment** — AI conducts a warm, structured initial assessment
- **Presenting problem identification** — through natural conversation, not checkbox forms
- **Automatic PHQ-9/GAD-7 completion** — embedded naturally in intake conversation
- **Risk screening** — C-SSRS style questions woven into natural dialogue
- **Formulation hypothesis** — AI generates a provisional formulation for clinician review
- **Treatment matching** — based on intake, suggest appropriate treatment approach and intensity
- **Clinician assignment** — match patient to most suitable clinician based on speciality and availability
- **Waiting list intelligent placement** — based on urgency from intake assessment

---

### 4.4 NATURAL LANGUAGE CLINICAL DOCUMENTATION
**Priority: HIGH — Clinician efficiency multiplier**

- **Voice-to-notes** — clinician speaks after session, AI generates structured notes
- **Meeting transcription** — with consent, transcribe and summarise clinical conversations
- **Bulk note generation** — clinician reviews week of sessions, AI drafts notes from voice/text prompts
- **Letter drafting** — AI drafts GP letters, referral letters, court reports from clinical notes
- **SNOMED coding** — AI suggests SNOMED CT codes for diagnoses and presentations
- **ICD-11 code suggestion** — based on assessment data, suggest ICD-11 diagnostic codes
- **Audit extraction** — pull clinical data for service audits automatically

---

### 4.5 THERAPEUTIC ALLIANCE MEASUREMENT
**Priority: MEDIUM — Research-backed outcome predictor**

- **Alliance tracking** — embed Session Rating Scale (SRS) at end of every session
- **Alliance trend** — is the relationship strengthening or weakening over time?
- **Rupture detection** — sudden alliance drop flagged to supervisor/clinician
- **Patient-clinician fit score** — based on alliance data, predict compatibility
- **Micro-moment analysis** — in AI therapy conversations, detect moments of connection vs. disconnection

---

### 4.6 ANONYMIZED POPULATION INSIGHTS
**Priority: MEDIUM — Research gold mine**

With appropriate consent and rigorous anonymization:

- **Outcome benchmarking** — how does this patient's trajectory compare to similar cases?
- **Treatment effectiveness data** — which interventions work best for which presentations?
- **Service-level reporting** — aggregate data for NHS reporting, commissioning evidence
- **Research partnerships** — anonymized dataset for academic mental health research
- **National benchmarking** — compare outcomes to IAPT national dataset

---

## PHASE 5 — PLATFORM SCALE & INTEGRATIONS
### Timeline: Months 4–8 | Focus: Enterprise-ready, NHS-compatible, market leadership

---

### 5.1 NHS & SYSTEM INTEGRATIONS
**Priority: HIGH — Required for NHS adoption**

- **NHS Login** — integrate with NHS Login for patient authentication (no separate registration)
- **NHS Spine** — patient demographics, GP registration, NHS number
- **GP Connect** — read GP records (medications, allergies, past medical history)
- **EMIS / SystmOne / Rio** — two-way data sharing with primary and secondary care EPRs
- **IAPT IDS** — IAPT Integrated Dataset submission (mandatory for NHS IAPT services)
- **SNOMED CT coding** — all clinical entries coded to NHS standard
- **HL7 FHIR R4** — full compliance for interoperability (existing FHIR export upgraded to R4)
- **NHS 111 / Crisis Care** — direct referral pathway integration

---

### 5.2 MULTI-TENANCY ARCHITECTURE
**Priority: HIGH — Required for commercial scale**

Currently: Single-tenant (one organization). Evolve to:

- **Organization model** — each NHS Trust / private practice / university is an isolated tenant
- **Custom branding** — logo, colour scheme, name, custom domain
- **Tenant admin** — organization admin can manage their own clinicians and settings
- **Data isolation** — tenant A cannot see tenant B's data (GDPR critical)
- **Subscription tiers** — per-clinician pricing, per-patient pricing, enterprise unlimited
- **Usage analytics per tenant** — organization gets their own analytics dashboard
- **SSO integration** — NHS email, university SSO, practice Active Directory

---

### 5.3 MOBILE APPS (iOS & ANDROID)
**Priority: HIGH — Patients expect this**

Current state: Capacitor configured but not production-ready.

- **Full native wrapper** (Capacitor or React Native)
- **Push notifications** — crisis alerts, appointment reminders, daily check-in nudges
- **Biometric authentication** — Face ID / fingerprint for quick, secure access
- **Offline mode** — core CBT tools available without internet (safety plan always accessible)
- **Background sync** — mood logs sync when connectivity returns
- **Home screen widgets** — quick mood log without opening app
- **Apple Health / Google Fit integration** — automatic data pull
- **App Store & Play Store** deployment
- **WCAG 2.1 AA compliant** throughout

---

### 5.4 VIDEO THERAPY INTEGRATION
**Priority: HIGH — Standard of care post-COVID**

- **Built-in video sessions** (Daily.co or Jitsi self-hosted for NHS data requirements)
- **Session recording** (with explicit consent) — encrypted, clinician-controlled
- **AI transcription** — automatic session transcript for notes
- **Waiting room** — patient waits while clinician finishes previous session
- **Technical check page** — camera/mic test before session
- **Low-bandwidth mode** — audio-only option for poor connections
- **Session notes panel** — clinician can take notes in split-screen during session
- **Screen share** — for reviewing worksheets together

---

### 5.5 PROGRESSIVE WEB APP (PWA)
**Priority: MEDIUM — Before mobile apps land**

- **Service worker** — offline caching of critical resources
- **Install prompt** — "Add to Home Screen" for iOS/Android
- **Offline CBT tools** — safety plan, breathing, grounding always available
- **Background sync** — offline entries sync on reconnect
- **Push notifications** via Web Push API

---

### 5.6 CALENDAR & EXTERNAL INTEGRATIONS
**Priority: MEDIUM**

- **Google Calendar sync** — appointments appear in patient/clinician Google calendar
- **Outlook / Microsoft 365** — same for NHS staff using Office
- **iCal** — universal calendar support
- **Zapier / Make.com** — enable custom automations for non-technical admins
- **Webhook system** — clinicians/orgs can subscribe to events (new assessment, crisis alert)
- **Slack integration** — duty clinician alerts to Slack channel
- **Email digest** — weekly summary email (patient and clinician versions)

---

## PHASE 6 — COMPLIANCE, GOVERNANCE & CERTIFICATION
### Timeline: Ongoing | Focus: NHS readiness, legal robustness, regulatory excellence

---

### 6.1 NHS DIGITAL CERTIFICATION (DTAC)
**Priority: CRITICAL for NHS — Digital Technology Assessment Criteria**

- **Clinical Safety (DCB0129/DCB0160)** — Clinical Risk Management File, Clinical Safety Officer, Hazard Log
- **Data Protection (DSPT)** — Data Security & Protection Toolkit — mandatory for NHS
- **Cyber Essentials Plus** — NCSC certification
- **DTAC Assessment** — pass the Digital Technology Assessment Criteria
- **NICE Evidence Standards** — evidence for clinical effectiveness claims
- **CQC registration** (if applicable) — Care Quality Commission

---

### 6.2 GDPR COMPLETE IMPLEMENTATION
**Priority: HIGH**

Gaps identified:
- Comprehensive data export (Article 20) — include ALL data: AI insights, session notes, risk assessments, safety plans
- Automated data retention policies — chat history not indefinite (7 year max then auto-delete)
- Breach notification mechanism — 72-hour ICO notification procedure
- Consent management UI — granular consent per data use (treatment, research, AI training, analytics)
- UK-format PII stripping — NHS numbers, UK postcodes, National Insurance numbers
- GDPR audit trail — who exported, deleted, or viewed sensitive data and when
- **Right to erasure** — complete, verified deletion including backups
- **Data minimisation** — only collect what's clinically necessary

---

### 6.3 FIELD-LEVEL ENCRYPTION
**Priority: HIGH — Clinical data requires maximum protection**

Fernet encryption available but not applied. Encrypt at rest:
- Therapy chat content
- C-SSRS responses
- Safety plans
- Session notes
- Diagnoses
- Safeguarding records

---

### 6.4 COMPREHENSIVE AUDIT LOGGING
**Priority: HIGH — Required for NHS and CQC**

- Every access to patient data logged (who, what, when, from where)
- 7-year retention (NHS standard)
- Tamper-evident logs (hash-chained)
- Audit log viewer in developer dashboard
- Automated compliance reports — "Show all access to Patient X's records in the last 90 days"
- Clinician access audit — visible to patient on request

---

### 6.5 CI/CD PIPELINE & QUALITY GATES
**Priority: HIGH — Production maturity**

- **GitHub Actions pipeline**:
  - Automated tests on every PR
  - Security scanning (pip-audit, bandit, Trivy)
  - Code coverage check (fail if <80%)
  - Staging deployment on merge to main
  - Production deployment gated on manual approval
  - SAST (Static Application Security Testing)
- **Dependabot** — automated dependency updates
- **Pre-commit hooks** — linting, formatting, secret scanning
- **OpenAPI spec** — auto-generated and validated in CI

---

### 6.6 PENETRATION TESTING & SECURITY PROGRAMME
**Priority: HIGH**

- Annual CREST-certified penetration test
- Continuous vulnerability scanning (Snyk, GitHub security alerts)
- Bug bounty programme — responsible disclosure
- Security headers audit (CSP, HSTS, X-Frame-Options, Permissions-Policy)
- Web Application Firewall (WAF)
- DDoS protection (Cloudflare)
- Certificate pinning for mobile apps

---

## PHASE 7 — ARCHITECTURE EXCELLENCE
### Timeline: Months 6–12 | Focus: Technical foundation for the next 5 years

---

### 7.1 FRONTEND ARCHITECTURE MODERNISATION
**Priority: HIGH — Current monolith is unsustainable**

Current: 16,500-line monolithic HTML with all JS/CSS inline.

Target:
- **Component-based architecture** (React or Svelte — chosen for stability and ecosystem)
- **Vite build system** — fast development, optimized production bundles
- **CSS modules** — scoped styles, no leakage
- **Code splitting** — lazy-load tabs and features
- **TypeScript** — type safety, better IDE support, fewer bugs
- **Storybook** — component library with visual testing
- **Playwright** — E2E testing
- **Bundle size target**: Core load <200KB gzipped (currently ~762KB)

---

### 7.2 BACKEND MODULARISATION
**Priority: HIGH — api.py at 17,000 lines is unmaintainable**

Target:
- **Flask Blueprints** per domain: `auth`, `therapy`, `clinical`, `messaging`, `community`, `admin`, `developer`, `pet`, `wellness`, `cbt`
- **Service layer** — business logic separated from route handlers
- **Repository pattern** — data access abstracted from business logic
- **SQLAlchemy ORM** — replace raw psycopg2 for most queries
- **Pydantic models** — request/response validation with auto-documentation
- **Async endpoints** (FastAPI migration consideration for high-throughput routes)

---

### 7.3 DATABASE SCHEMA NORMALISATION
**Priority: MEDIUM**

Issues identified:
- Inconsistent timestamp naming (entry_timestamp vs created_at vs entrestamp)
- TEXT fields storing JSON (should be JSONB)
- Username as primary key (should be UUID)
- Missing soft delete on several tables
- No foreign key constraints on some relationships
- Missing indexes on frequently-queried columns

Migration strategy: Zero-downtime migrations, backward-compatible.

---

### 7.4 CACHING LAYER
**Priority: MEDIUM**

- **Redis** — session storage, rate limiting, caching
- **Cache frequent reads**: clinician caseload, patient profile, app updates, notification counts
- **Cache invalidation strategy** — event-driven (patient logs mood → invalidate their cache)
- **Response caching** for static-ish API responses (CBT tools list, meditation library)

---

### 7.5 OPENAPI DOCUMENTATION
**Priority: MEDIUM**

- Auto-generated API docs (Swagger UI / Redoc)
- Request/response schemas
- Authentication documentation
- Rate limit documentation
- Changelog per endpoint version
- SDK generation for future mobile and third-party integrations

---

### 7.6 ACCESSIBILITY (WCAG 2.1 AA)
**Priority: HIGH — Legal requirement (Equality Act 2010), also right thing to do**

- Full WCAG 2.1 AA audit across every view
- ARIA labels on all interactive elements (290+ currently missing)
- Keyboard navigation throughout (no mouse required)
- Screen reader testing (NVDA, JAWS, VoiceOver)
- Focus management in modals and dynamic content
- Colour contrast compliance (all text combinations)
- Skip links and landmark regions
- Form error announcement
- Audio descriptions for any visual-only content

---

## PHASE 8 — MARKET LEADERSHIP & FUTURE VISION
### Timeline: Months 9–18 | Focus: Establishing Healing Space UK as the category leader

---

### 8.1 CLINICIAN MARKETPLACE
**Priority: HIGH — Business model and access**

- **Public-facing clinician directory** — patients can find and request a specific clinician
- **Clinician profiles** — specialities, approaches, availability, fee structure
- **Patient-clinician matching** — AI-assisted matching based on presenting problem and clinician speciality
- **Waitlist self-management** — patients join a clinician's waitlist directly
- **Review system** (anonymized, moderated) — patient feedback on their experience
- **Clinician verification** — BACP/UKCP/BPS registration validation via API

---

### 8.2 RESEARCH MODULE
**Priority: MEDIUM — Revenue and impact**

- **Anonymized research dataset** — with rigorous consent and ethics approval
- **Research API** — for approved academic partners to access aggregated, anonymized data
- **Randomized Controlled Trial (RCT) support** — randomization engine for embedded studies
- **Patient recruitment platform** — patients can opt-in to relevant research studies
- **Outcome data contribution** — contribute to IAPT national dataset
- **Publication-ready reporting** — export data in formats for academic papers

---

### 8.3 INTERNATIONAL EXPANSION
**Priority: MEDIUM — Post-UK**

- **Multi-language support** — Welsh (legal requirement for NHS Wales), then Spanish, Arabic, Urdu, Polish (UK population needs)
- **RTL language support** — Arabic, Farsi
- **Cultural adaptation** — not just translation but cultural relevance of CBT examples
- **EU GDPR compliance** — for European expansion
- **US HIPAA compliance** — if expanding to US market
- **Australia / New Zealand** — similar regulatory landscape to UK

---

### 8.4 AI THERAPIST V2 — AUTONOMOUS SUPPORT CAPABILITY
**Priority: MEDIUM-HIGH — The future of scalable mental health care**

Important: This is a *support tool*, always with human oversight. For:
- Between-session support only
- Step 2 (low-intensity) presentations only
- Always with a named clinician supervisor
- Clear boundaries: AI cannot diagnose, prescribe, or replace therapy

Features:
- **Structured CBT protocol delivery** — AI can guide through full CBT programme (e.g., Beating the Blues equivalent)
- **Automated progress monitoring** — PHQ-9 every 2 weeks automatically, alerts clinician to deterioration
- **Personalised between-session exercises** — AI sets and follows up on homework
- **Outcome equivalent to low-intensity human IAPT** — the clinical bar to reach

---

### 8.5 PLATFORM API & DEVELOPER ECOSYSTEM
**Priority: MEDIUM — For long-term growth**

- **Public API** — allow third-party apps to integrate (with patient consent)
- **Webhook system** — real-time events for integrations
- **Developer portal** — documentation, API keys, sandbox environment
- **App marketplace** — approved third-party extensions (e.g., a specialist trauma tool that integrates with the platform)
- **White-label SDK** — for other organisations to build on Healing Space infrastructure

---

### 8.6 REAL-WORLD EVIDENCE PLATFORM
**Priority: MEDIUM — NHS funding lever**

- **Real-world outcome data** — continuously improving, published annually
- **Health economic analysis** — cost per quality-adjusted life year (QALY) improvement
- **NHS commissioning support pack** — everything a CCG/ICB needs to commission the platform
- **NICE submission** — evidence submission for NICE recommendation (transformational for NHS adoption)
- **Academic partnerships** — UCL, King's, Oxford mental health research groups

---

## DEVELOPER DASHBOARD — COMPLETE VISION
### Everything a developer should be able to do without leaving the platform

**Current**: Terminal, AI chat, inbox, broadcast, QA tests, user management, feedback, stats, Post Update

**To Add**:

| Feature | Purpose |
|---------|---------|
| Real-time error feed | See Python exceptions as they happen |
| API latency heatmap | P50/P95/P99 for every endpoint |
| Database query analyser | Slow queries, explain plans |
| Active session viewer | Who's logged in right now |
| Deployment timeline | Git commits mapped to usage/error changes |
| Feature flag manager | Toggle features without code changes |
| A/B test dashboard | Results and statistical significance |
| Audit log viewer | Who accessed what, when |
| GDPR compliance dashboard | Consent rates, deletion requests, export requests |
| User journey funnel | Where users drop off |
| Cohort analysis | Retention by registration cohort |
| Feature usage heatmap | Which tools/tabs are used most |
| Outcome analytics | Which features correlate with best outcomes |
| System health monitor | CPU, memory, DB connections, Railway metrics |
| Backup manager | Create, list, restore database backups |
| Environment variable manager | View (not edit) active config |
| Scheduled job manager | View/manage cron jobs and scheduled tasks |
| Email delivery dashboard | Track notification delivery rates |
| GitHub Actions status | CI/CD pipeline status embedded |

---

## CLINICIAN DASHBOARD — COMPLETE VISION
### Everything a clinician needs, nothing they don't

**Current**: Patient caseload, risk monitor, messages, appointments, approvals, AI summary

**To Complete**:

| Feature | Status |
|---------|--------|
| Session notes (SOAP/BIRP) | ✅ Complete |
| Treatment plan builder | ✅ Complete |
| CORE-OM / WEMWBS / ORS / SRS | ✅ Complete |
| Waiting list management | Missing |
| Discharge workflow | Missing |
| Referral letter generator | Missing |
| Group therapy module | Missing |
| Clinical supervision log | Missing |
| Safeguarding workflow | Missing |
| AI weekly patient summaries | Missing |
| AI session prep brief | Missing |
| Predictive crisis alerts | Missing |
| Caseload capacity dashboard | Missing |
| Outcome trajectory charts | Missing |
| Video therapy integration | Missing |
| Peer consultation forum | Missing |
| CPD tracker | Missing |
| Reflective journal | Missing |

---

## PATIENT EXPERIENCE — COMPLETE VISION
### Every feature a patient could need on their recovery journey

**Current**: AI therapy, 17 CBT tools, mood tracking, pet, community, messaging, safety plan, appointments

**To Complete**:

| Feature | Status |
|---------|--------|
| SOS / Crisis button (always visible) | ✅ Complete |
| Medication tracker & reminders | Missing |
| Recovery milestones dashboard | Missing |
| Psychoeducation library | Missing |
| Mindfulness & meditation library | Missing |
| Personalized daily ritual | Missing |
| Relapse prevention plan | Missing |
| Wearable data integration | Missing |
| Family/carer portal | Missing |
| Voice mood logging | Missing |
| Video therapy sessions | Missing |
| Peer mentor matching | Missing |
| Personalized homework from clinician | Missing |
| Treatment plan visibility | ✅ Complete |
| PWA / offline mode | Missing |
| Native mobile apps | Missing |
| Weekly progress email digest | Missing |

---

## EFFORT & PRIORITY MATRIX

| Phase | Priority | Effort | Impact |
|-------|----------|--------|--------|
| 1 — Foundation Polish | **NOW** | Medium | High |
| 2 — Clinical Excellence | **Q2 2026** | High | Very High |
| 3 — Patient Engagement | **Q2-Q3 2026** | Medium | High |
| 4 — AI & Intelligence | **Q3 2026** | High | Very High |
| 5 — Scale & Integrations | **Q3-Q4 2026** | Very High | Very High |
| 6 — Compliance | **Ongoing** | Medium | Critical |
| 7 — Architecture | **Q3-Q4 2026** | Very High | Medium (long-term) |
| 8 — Market Leadership | **2027** | Very High | Transformational |

---

## THE NON-NEGOTIABLES (Must happen before clinical deployment)

1. ✅ Security hardening (complete)
2. ✅ SOS crisis button on every screen (complete Feb 2026)
3. ✅ Session notes system (complete Feb 20, 2026)
4. ✅ Treatment plan documentation (complete Feb 20, 2026)
5. ✅ CORE-OM outcome measures (complete Feb 20, 2026)
6. ⏳ Safeguarding workflow
7. ⏳ Field-level encryption for clinical data
8. ⏳ GDPR comprehensive implementation
9. ⏳ Clinical risk management documentation (DCB0129)
10. ⏳ DSPT/DTAC compliance

---

## ON AUTOMATIC GITHUB → UPDATES TAB INTEGRATION

*The developer asked about this during roadmap creation (Feb 17, 2026).*

**Yes, this is achievable**. Implementation:

1. Add a GitHub Actions workflow on push to `main`
2. Action calls `POST /api/dev/updates` with the commit message, author, and auto-incremented version
3. The update appears in all users' "What's New" tab automatically
4. Filtering: Only pushes with commit messages starting with specific prefixes trigger updates (e.g., `feat:`, `fix:`, `improve:`)
5. The API endpoint already exists — only the GitHub Action needs to be added

This is a small task (~1 hour) that can be added any time.

---

## GUIDING PRINCIPLES FOR EVERYTHING WE BUILD

1. **Clinical first** — every feature must be defensible to a clinician reviewer
2. **Privacy by design** — assume the most sensitive data, protect accordingly
3. **Trauma-informed** — no jarring alerts, no clinical language without explanation, no time pressure
4. **Evidence-based** — tie features to NICE guidelines, published literature
5. **Accessible** — WCAG 2.1 AA minimum, designed for cognitive load, not just visual accessibility
6. **AI assists, humans decide** — AI never acts without clinician review on clinical matters
7. **Transparent** — patients know how their data is used, clinicians know how AI decisions are made
8. **Sustainable** — build for the long term, not the quick win
9. **World class** — the question is always "would this be at home in the best mental health platform in the world?"

---

*Roadmap generated: February 17, 2026. Last updated: February 20, 2026. Next review: April 2026.*
*This document should be reviewed quarterly and updated after each major milestone.*
