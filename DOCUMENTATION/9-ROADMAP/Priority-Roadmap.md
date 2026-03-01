# HEALING SPACE UK — MASTER PRODUCT ROADMAP
## World-Class Mental Health Platform: The Definitive Plan
### Audit Date: February 24, 2026 | Full Platform Audit + Strategic Vision

---

> **Vision**: Healing Space UK becomes the most clinically rigorous, technologically advanced, and genuinely human mental health platform in the UK — the tool that clinicians choose because it makes them better at their jobs, that patients love because it meets them where they are, and that sets the standard for what digital mental health care should be.
>
> **The Healing Journey Principle**: Every person using this platform is the hero of their own story. Therapy isn't a clinical process — it's an epic, deeply personal journey from darkness toward light. Our platform should feel like a sacred companion: part guide, part celebration, part magic. Less clipboard, more compass.

---

## CURRENT STATE SNAPSHOT (February 24, 2026)

| Dimension | Status |
|-----------|--------|
| **Security** | ✅ TIER 0-1 complete — production-grade CSRF, rate limiting, XSS, access control |
| **Backend** | api.py ~25,000 lines, Flask/PostgreSQL/Groq, 350+ endpoints |
| **Frontend** | index.html ~26,000 lines, monolithic SPA |
| **Database** | 55+ tables, PostgreSQL (local dev + Railway production) |
| **Patient Features** | 14 tabs, 17 CBT tools, AI therapy, pet, community, messaging, CORE-OM/ORS/SRS, SOS button, medication tracker, recovery milestones, wellness ritual |
| **Clinician Features** | Dashboard, session notes, treatment plans, outcome tracker, risk monitor, messaging, patient detail view (all 5 subtabs), medications view, progress view |
| **Developer Features** | Terminal, AI chat, inbox, broadcast, QA, user mgmt, Post Update |
| **AI** | Groq-powered therapy chat, AI memory, risk detection, summaries, content-filter fallback |
| **Risk Pipeline** | ✅ Unified + Predictive: C-SSRS → risk_alerts + notification; PHQ-9/GAD-7 → risk_alerts + notification; mood ≤ 3 → alert; outcome measures (severe) → alert; 27-signal predictive engine → yellow/orange/red flags |
| **Compliance** | GDPR foundations in place, NHS compliance not yet started |
| **Mobile** | Capacitor configured, not production-ready |
| **Tests** | 180+ passing, gaps in clinical logic coverage |

---

## WHAT HAS BEEN COMPLETED ✅

### Foundation (Pre Feb 2026)
- Full TIER 0-1 security hardening (CSRF, rate limiting, XSS, session management, access control, connection pooling, anonymization, input validation, audit logging)
- Clinician dashboard with patient caseload, risk monitor, messaging, approvals
- Patient: 17 CBT tools, AI therapy with crisis detection, pet, community, mood/wellness logging, C-SSRS, safety planning, appointments, FHIR export
- Full internal messaging system (inbox, sent, compose, threads, templates, scheduling, group messaging, search)
- Developer dashboard (terminal, AI assistant, inbox, broadcast, post updates, QA, user management, feedback, stats)
- Dark/light theme with full CSS variable coverage
- Notification system with human-readable notification labels
- Community forum, achievements/badges, gratitude logging, pet system
- FHIR data export, AI training data manager (GDPR-compliant)

### Phase 1.1 — Session Notes ✅ (Feb 20, 2026)
SOAP/BIRP/free-text formats, 6 presenting-problem templates, draft/sign-off/24h-lock workflow, full note history per patient

### Phase 1.2 — Treatment Plan Builder ✅ (Feb 20, 2026)
SMART goals with click-to-update status, intervention selection, session parameters, outcome targets, clinician+patient co-signature, plan versioning, discharge criteria

### Phase 1.3 — Extended Outcome Measures ✅ (Feb 20, 2026)
CORE-10, CORE-OM (34-item real questions), WEMWBS, ORS (VAS sliders), SRS (VAS sliders) — all with validated server-side scoring; Caseload Outcome Tracker with trend arrows

### Phase 1.4 — Waiting List Management ✅ (Feb 21, 2026)
Referral intake, urgency queue, capacity tracking, first appointment allocation, referral source tracking

### Phase 1.5 — Medication Tracker ✅ (Feb 21, 2026)
Patient medication list (add/edit/remove), daily dose logging (taken/missed/skipped), 30-day adherence chart, clinician read-only medication view with adherence stats

### Phase 1.6 — SOS Crisis Button ✅ (Feb 2026)
Persistent red button on every screen, crisis overlay with Samaritans/SHOUT/NHS 111, safety plan display, clinician alert, grounding exercises

### Phase 1.7 — Recovery Milestones & Progress Dashboard ✅ (Feb 21, 2026)
Visual milestone achievements, mood/PHQ-9/GAD-7 Canvas charts, streak tracking, baseline comparison, clinician milestone message system

### Risk Alert Pipeline Unification ✅ (Feb 22, 2026)
- C-SSRS: now writes to `risk_alerts` table + in-app notification (was email-only)
- PHQ-9/GAD-7: now writes to `risk_alerts` (with severity) in addition to legacy alerts
- Mood logging: creates risk alert when mood ≤ 3 (low=≤3, critical=≤2)
- Outcome measures: creates risk alert on severe CORE-10/ORS/PHQ-9 scores
- C-SSRS submission: fixed q1–q6 payload mapping (was always sending 0)
- `get_patient_detail`: merges both alert tables into unified, severity-sorted list

### Full Clinician Patient Data View ✅ (Feb 22, 2026)
- Assessments tab: C-SSRS history with risk level badges + all clinical scales
- Moods tab: mood logs + full wellness ritual logs (emotional narrative, homework, energy, social)
- Therapy tab: clinician notes + CBT records + gratitude journal + AI suggestions + full chat history
- Alerts tab: rich display with severity badges, source labels, acknowledged status

### 2.1 — AI-Powered Predictive Crisis Detection ✅ (Feb 24, 2026)
27-signal predictive engine across clinical + behavioral domains. `predictive_risk_flags` table with yellow/orange/red three-tier system, ON CONFLICT upsert, auto-resolve when conditions clear.

**Clinical signals** (15): CORE-10 elevated, CORE-OM risk domain, WEMWBS low wellbeing, ORS all-domain distress, C-SSRS escalation, PHQ-9 rapid deterioration, GAD-7 rapid deterioration, severe CORE-10/PHQ-9/ORS/C-SSRS threshold crossings, assessment gap (>14 days without any assessment)

**Behavioral signals** (12): Login recency drop, 7-day mood average decline, medication non-adherence, poor sleep quality, social isolation (community withdrawal), gratitude journal abandonment, CBT tool abandonment, quest disengagement, wellness log gap, low engagement composite

**Platform integration**: Hooked into `calculate_risk_score()` (runs on every risk calculation). `detect_patterns_endpoint()` scans all patients. `get_risk_dashboard()` triggers score recalculation for patients with missing/stale (>1h) assessments. Risk Monitor shows ⚡ Early Warning Signals card with tier counts. Patient rows show 🔴🟠🟡 pill counts. Patient Alerts tab renders full flag cards with AI reasoning, recommended action, and dismiss workflow. `/api/risk/predictive/<username>` and `/api/risk/predictive/<flag_id>/dismiss` endpoints.

### 2.5 Safeguarding & Duty of Care Workflow ✅ (Feb 28, 2026)
Full statutory safeguarding implementation — clinically and legally defensible.

- **`safeguarding_concerns` table** — permanent legal record, 27-column schema, status workflow: open → referred → monitoring → closed (never DELETE)
- **`duty_clinician` table** — UNIQUE(duty_date, is_out_of_hours) rota, one daytime + one OOH slot per day
- **9 API endpoints**: GET stats, LIST concerns, POST concern, GET detail, PATCH status, GET patient concerns, GET duty rota, POST duty (upsert), DELETE duty slot
- **Immediate risk cascade**: immediate_risk=True triggers critical risk_alert INSERT + duty clinician notification + async email
- **UK statutory frameworks**: Working Together 2018, Care Act 2014, MCA 2005, Gillick competence, MASH, MARAC, Section 47/17, Prevent
- **Frontend**: 🛡️ Safeguarding clinical subtab (stats, duty widget, concern list) + patient-level safeguarding subtab
- **Legal disclaimer** banner on all safeguarding screens
- **Form**: concern category (10 options), statutory framework, disclosure method, Gillick/capacity section, multi-agency referral section (MASH/Police/CAMHS/MARAC/GP/Social Care/LA/Other), supervisor consultation
- **AI-powered**: `openConcernDetail()` reuses risk detail modal; `suggestTestFix()` sends failures to AI assistant
- **Audit trail**: `log_event()` on every concern creation, status change, duty assignment

### 2.6 — Appointment System Upgrade ✅ (Feb 28, 2026)
World-class appointment management replacing the basic clinician-only scheduling with a full clinical workflow.

- **DB schema**: 12 new columns on `appointments` (duration_minutes, location_type, video_link, is_recurring, recurring_pattern, recurring_until, recurring_group_id, recurring_index, cancelled_by, cancellation_reason, reminder_48h_sent, reminder_24h_sent) — all idempotent `ALTER TABLE IF NOT EXISTS` migrations
- **`clinician_availability` table** — recurring weekly slots (day_of_week) and specific-date blocks (is_blocked), with slot_duration_minutes and index for fast querying
- **Recurring appointments** — up to 12 occurrences linked by UUID `recurring_group_id`, pure stdlib month arithmetic (no external deps). Cancel entire series or single occurrence
- **Location types**: In-Person 🏢, Video Call 📹, Phone 📞 — with location badge on all appointment cards
- **Video call link field** — clinician pastes Zoom/Whereby/Teams URL; "📹 Join Video Call →" button appears on patient card and clinician day-view tile (sanitized URL, rel=noopener)
- **Automated reminders** (dispatched via `/api/poll`, idempotent): 48h reminder (in-app + email to patient + clinician), 24h reminder with video link included. UPDATE...RETURNING pattern prevents duplicate sends
- **Availability Manager modal** — clinician sets recurring weekly slots (day, start/end, slot duration) and blocks specific dates (holidays, training). Rules persist in `clinician_availability`
- **Patient self-booking** — slot picker grid (7-day view, week navigation); available=green, taken=grey-disabled. Patient requests via POST /api/appointments with preferred location; clinician notification sent
- **DNA Report modal** — last 90 days: dna_count, total appointments, DNA rate per patient. ⚠️ banner auto-shows when ≥3-DNA patients detected (fires silently on `loadAppointments`)
- **Calendar enhancements**: month/week/day views now colour-coded by attendance_status (attended=green, scheduled=purple, no_show/missed=red, pending=amber, declined=grey) with location icons on tiles
- **Soft-delete on cancel**: `deleted_at` timestamp rather than hard DELETE; `cancelled_by` + `cancellation_reason` stored for audit trail
- **6 new endpoints**: GET/POST/DELETE `/api/clinician/availability`, GET `/api/appointments/available-slots`, GET `/api/appointments/dna-report`, PATCH `/api/appointments/<id>`
- **Patient appointment cards**: location badge, duration, "📹 Join Video Call →" link, 🔄 Recurring indicator
- **`clinician_username` field** added to patient profile API response (enables self-booking)

### Smart Refresh (Tab Visibility Engine) ✅ (Feb 28, 2026)
Active tab content auto-refreshes when the user returns to the page (no constant 10s polling flicker).

- `_refreshActiveTabContent()` called on `visibilitychange → visible` and on `switchTab()`
- Handles: Risk Monitor, Safeguarding, Analytics, Waiting List, Appointments, Messages, Community, Notifications
- `setTimeout(_refreshActiveTabContent, 100)` after every main tab switch

### Real-Time Smart Polling Engine ✅ (Feb 24, 2026)
Replaced scattered 60s `setInterval` calls with a centralised smart polling engine.

- `/api/poll` lightweight endpoint returns counts-only (notifications, messages, risk_alerts, role) in ~3 fast DB queries — never returns 401
- Polls at **10s** when tab is visible, **60s** when tab is hidden (Visibility API)
- On tab focus: immediate re-poll + notification reload
- **Toast notifications** bottom-right: new message/risk alert toasts are clickable to navigate directly to the relevant tab
- **Browser Notification API**: clinicians get OS-level alerts for new messages even when Healing Space is in the background (permission requested on login)
- Immediate re-poll after sending a message (instant badge update for recipient)
- Risk Monitor auto-refreshes every 2 minutes when active tab
- `showToast()` upgraded to support `onClick` navigation, all color types (info/success/warning/error), proper fade animation

### Bug Fixes ✅ (Feb 24, 2026)
- **Risk dashboard staleness**: `get_risk_dashboard()` now triggers `calculate_risk_score()` for patients with missing or >1h stale assessments — patients with severe PHQ-9/CORE-10 scores now immediately appear at correct risk level
- **CSRF on therapy note save**: `saveClinicianNote()` now includes `X-CSRF-Token` header (was causing "CSRF token invalid" error)
- **Medication adherence columns**: Fixed `taken` / `logged_at` → `status='taken'` / `log_date` in both `calculate_behavioral_score()` and `run_predictive_signals()` (schema mismatch was silently causing 0% adherence readings)

---

## THE HEALING JOURNEY — GAMIFICATION & ENGAGEMENT VISION
### *"Less clipboard, more compass. Less clinic, more quest."*

This is the transformative layer that turns Healing Space UK from a clinical tool into something people genuinely love using — and that makes the clinical work go deeper.

**The Core Metaphor**: Every patient is the **Hero** of their own healing quest. Their therapist is the **Guide** — not a superior, but a wise companion who has walked this path before. The platform is the **Sanctuary** — a safe world they carry in their pocket. Progress through therapy isn't filling forms; it's **levelling up**, **earning powers**, **unlocking new chapters**.

This layer sits **on top** of the clinical engine — the outcomes, the PHQ-9 scores, the session notes all remain exactly as clinical as they need to be. The magic is how we *present* that journey to the patient.

---

### HJ.1 THE QUEST SYSTEM ✅ (Feb 22, 2026)
**Priority: HIGH — Core engagement mechanic**

Reframe therapeutic work as quests. Each quest corresponds to a real clinical intervention or homework task:

**Quest Types**:
- **Daily Rituals** — "The Morning Compass" (complete your wellness check-in), "The Evening Lantern" (log gratitude + mood)
- **Skill Quests** — "The Thought Challenger" (complete 3 CBT thought records this week), "The Breathing Stone" (practice box breathing 5 days running)
- **Exploration Quests** — "The Shadow Journal" (write about a difficult emotion), "The Gratitude Grove" (log 7 gratitude entries)
- **Courage Quests** — clinician-assigned behavioural experiments ("Face one avoided situation this week")
- **Connection Quests** — community participation, peer support interactions
- **Arc Quests** — multi-week journeys tied to the full CBT programme ("The 8-Week Clarity Path")

**Mechanics**:
- Quest has a title, description, what the patient will gain ("You'll develop the skill of…"), an expected effort indicator, and a reward
- Quests awarded by clinician or auto-suggested by platform based on patient's progress
- Progress bar within each quest
- Quest completion triggers milestone celebration

**Implemented**: `quest_definitions` (20 seeded quests), `patient_quests`, `quest_progress_log` tables. `_advance_quest_progress()` helper hooked into wellness/mood/gratitude/CBT endpoints. 6 API endpoints (GET quests, accept, abandon, clinician view/assign, spell cast, spell library). Frontend: Quest Board replaces daily tasks widget, Accept Quest modal, completion celebration overlay.

---

### HJ.2 THE SPELL LIBRARY (REFRAMED CBT TOOLS) ✅ (Feb 22, 2026)
**Priority: HIGH — Reframes the existing toolset**

The 17 CBT tools already exist. The change is purely in presentation — **spells are skills** you learn to cast when you need them:

| Clinical Tool | Spell Name | Description |
|--------------|------------|-------------|
| Thought Record | **Clarity Spell** | Examine and reframe unhelpful thoughts |
| Breathing Exercise | **Calm Breath** | Regulate your nervous system instantly |
| Behavioural Activation | **Spark of Motion** | Break the depression cycle with action |
| Grounding (5-4-3-2-1) | **Anchor Ritual** | Return to the present moment |
| Problem Solving | **The Compass** | Navigate from stuck to moving |
| Values Clarification | **True North** | Connect to what matters most |
| Worry Time | **The Containment Vessel** | Contain anxiety to its proper time |
| Gratitude Journal | **Gratitude Seeds** | Plant moments of brightness |
| Self-compassion | **The Healing Salve** | Treat yourself with the care you'd give a friend |
| Progressive Muscle Relaxation | **The Stone Melting** | Release tension from the body |

**Implementation**:
- Each tool page gets a subtle "spell name" as a secondary header — the clinical name stays prominent
- Completing a tool for the first time "learns" the spell — small animation, added to Spell Library
- Spell Library page shows all mastered spells with usage count ("Cast 23 times")
- Spells have a "power level" that increases with usage frequency (visual indicator only)
**Implemented**: `spell_mastery` DB table (cast_count, power_level 1-5). `SPELL_MAP` constant with 15 spell names/elements/flavors/colours. Modified CBT tool grid shows spell name + colour stripe. `loadAndRecordSpell()` records mastery. Spell Library toggle view shows mastered spells with power orbs + cast count, unmastered as locked scrolls. First-cast "Spell Learned!" animation overlay. `POST /api/user/spell/cast` + `GET /api/user/spells` endpoints.

---

### HJ.3 THE SANCTUARY (HOME SCREEN REDESIGN) ✅ (Feb 22, 2026)
**Priority: MEDIUM — Major UX transformation**

The home screen evolves from a dashboard of widgets to a **living, personalised sanctuary**:

**Sanctuary Elements**:
- **The Hearth** — daily wellness ritual (currently wellness check-in) — warm, welcoming
- **The Quest Board** — current active quests, progress, what's next
- **The Mood Garden** — mood log visualised as a garden: high mood = blooming flowers, low mood = rain clouds (but beautiful rain, not depressing)
- **The Spell Circle** — 3 recommended spells for today based on current state
- **The Milestone Wall** — achievements displayed as glowing stones or illuminated scrolls
- **Your Companion** — the pet, but evolved into a spirit animal / familiar concept
- **The Weekly Ember** — weekly progress summary, flame grows with engagement

**Design Principles**:
- Warm, earthy palette option (alongside existing themes) — forest greens, amber, deep purples
- Gentle animations — nothing jarring, nothing clinical
- Seasonal changes — autumn colours, winter snow in the sanctuary background
- Deeply personal — patient's name woven in, their milestones visible

**Implemented**: Sanctuary CSS theme (`[data-theme="sanctuary"]`) with amber/forest/navy palette + custom CSS variables. Animations: sanctuaryFloat, emberFlicker, spellPulse. Home tab fully redesigned with 7 sections: Sanctuary Header, The Hearth (wellness ritual), Quest Board, Mood Garden (Canvas), Spell Circle (3 contextual spells), Milestone Wall, Companion (pet), Weekly Ember (streak flames). 🌿 theme toggle button in header.

---

### HJ.4 THE FAMILIAR (PET EVOLUTION SYSTEM)
**Priority: MEDIUM — Extends existing pet system**

The existing pet becomes a **healing familiar** — a spirit companion that grows as the patient heals:

**Evolution Path** (5 stages tied to clinical milestones):
1. **Seedling** — the familiar is just a glowing seed (registration → first week)
2. **Sprout** — a small, curious creature emerges (7-day streak, first PHQ-9)
3. **Companion** — the familiar is fully formed, animated, responsive (30-day streak, PHQ-9 improvement)
4. **Guide** — the familiar gains wisdom markings, helps suggest daily actions (60-day engagement, moderate → mild on PHQ-9)
5. **Elder** — majestic, fully evolved, becomes a visible symbol of the journey (significant clinical recovery)

**Familiar Types** (patient chooses at start or it morphs based on their style):
- The Fox (clever, curious — suits analytical/CBT patients)
- The Owl (wise, calm — suits reflective/mindfulness patients)
- The Wolf (brave, loyal — suits trauma-focused patients)
- The Deer (gentle, sensitive — suits anxiety patients)
- The Bear (strong, grounded — suits depression patients)

**Mechanics**:
- Familiar responds to mood: sad = nuzzles closer; happy = playful animations
- Feeding the familiar = completing daily wellness ritual
- Familiar sends "messages" = nudges in the familiar's voice ("I noticed you haven't cast a Clarity Spell in a while. Want to try one today?")

---

### HJ.5 THE ACHIEVEMENT CONSTELLATION
**Priority: MEDIUM — Extends existing achievement system**

50+ achievements across all platform areas, presented as stars forming constellations in a night sky:

**Constellation Groups**:
- **The Seeker's Path** — engagement milestones (7-day streak, 30-day streak, 100-day streak)
- **The Healer's Tools** — CBT tool mastery (first use, 10 uses, 50 uses of each spell)
- **The Courage Stones** — facing difficult things (first thought record, first safety check, first crisis survived)
- **The Gratitude Grove** — gratitude practice (10, 50, 100 entries)
- **The Chart of Progress** — clinical milestones (PHQ-9 drops from severe → moderate → mild → minimal)
- **The Connection Web** — community and peer engagement
- **The Ritual Keeper** — wellness ritual completion streaks
- **The Bright Days** — sustained wellbeing (7 consecutive mood ≥ 7 days)
- **The Night Survived** — especially meaningful: completing a crisis moment and continuing

**Presentation**:
- Night sky canvas with stars forming meaningful shapes
- Each constellation has a name and a one-line story ("The Seeker's Path: You chose to look within")
- Newly unlocked constellations animate beautifully on the screen
- Achievement notification: not a badge pop-up — a gentle glowing message from the familiar

---

### HJ.6 THE CLINICIAN AS GUIDE
**Priority: HIGH — Reframes the therapeutic relationship**

The clinician view doesn't change clinically — but the patient-facing language does:

**Clinician Identity in the Platform**:
- Patients see their clinician referred to as their **"Guide"** (configurable — clinician can change to their preference)
- Guide can send **Milestone Scrolls** — personal messages when they notice a breakthrough (already built in 1.7 — expand the design)
- Guide can assign **Quest Packs** — themed sets of homework/tools for a specific therapeutic goal
- Guide can send **Daily Encouragements** — short messages that arrive in the sanctuary like notes left by a guide
- Guide's weekly summary note (if written) appears in the patient's sanctuary as a **"Letter from Your Guide"**
- The treatment plan, when visible to the patient, is presented as **"Your Map"** — where you're going and how you'll get there

---

### HJ.7 RECOVERY VISUALIZATION — THE JOURNEY MAP
**Priority: HIGH — Patients need to *see* their journey**

A visual timeline of the entire therapeutic journey — from the first day to today:

**The Journey Map shows**:
- The starting point: first mood log, first session, baseline PHQ-9
- Key moments marked as **waypoints**: first milestone, crisis survived, breakthrough session
- The path forward: treatment plan goals as upcoming destinations
- Animated journey: a small figure (or the familiar) moves along the path as the patient progresses
- Mood encoded in the landscape: dark periods are foggy/stormy sections; bright periods are sunlit clearings
- The path is always continuing forward — even after setbacks, the path keeps going

**Design**: Canvas-rendered, scrollable horizontally, deeply personal

---

## PHASE 2 — CLINICAL EXCELLENCE
### Timeline: Q2 2026 | Focus: Make this the best clinical tool available

---

### 2.1 AI-POWERED PREDICTIVE CRISIS DETECTION ✅ COMPLETE (Feb 24, 2026)
**Priority: CRITICAL — Could save lives**

Extend current real-time detection to predictive detection BEFORE crisis:

**Signals** (with consent):
- Sudden drop in mood logging frequency (patient going quiet)
- Rapid PHQ-9/GAD-7 deterioration
- Language shifts in therapy chat (hopelessness markers)
- Reduced engagement with positive tools (pet, gratitude, community)
- Missed appointments + mood decline together
- Social withdrawal in community activity
- Time-of-day changes (logging only at 3am)
- Decreased response time to clinician messages

**Output**:
- 🟡 Yellow flag — "Patient engagement dropped significantly. Consider reaching out."
- 🟠 Orange flag — "Multiple risk indicators detected. Review recommended within 24 hours."
- 🔴 Red flag — Immediate alert + duty clinician escalation
- **AI reasoning visible** — why it flagged (explainable AI, never a black box)
- **Recommended action** — suggested response based on patient history

**Principle**: AI flags. Humans decide. No automated clinical actions.

---

### 2.2 AI CLINICAL INTELLIGENCE LAYER
**Priority: HIGH**

**2.2a Weekly AI Patient Summary** — auto-generated Monday, covers mood trends, chat themes, CBT usage, risk changes, plain English narrative

**2.2b AI Session Prep Brief** — before each appointment: last session summary, since-last-session activity, suggested topics based on patient state, open homework items

**2.2c AI Session Notes Assist** — clinician types bullet points after session, AI formats to SOAP/BIRP, clinician reviews + signs off, AI suggests homework from session themes

**2.2d Caseload Intelligence Dashboard** — patients not contacted in X days, stagnating outcomes, recent escalations, AI-ranked "check-in needed" list

**2.2e Treatment Recommendation Engine** — based on presentation, PHQ-9/GAD-7, treatment response history → suggest NICE-aligned evidence-based interventions

---

### 2.3 DISCHARGE & OUTCOME REPORTING
**Priority: HIGH**

- Discharge planning workflow tied to Treatment Plan criteria
- AI-assisted discharge summary (treatment summary, outcomes, ongoing recommendations)
- Post-discharge check-in schedule (1/3/6 month automated nudges)
- Stepped care recommendations (step-up/step-down services)
- Referral letter generator (AI draft from clinical notes)
- Anonymized aggregate outcome reporting for service reports

---

### 2.4 GROUP THERAPY MODULE
**Priority: HIGH**

- Create therapy groups (CBT, DBT, bereavement, anxiety) with max size + schedule
- Between-session group messaging thread
- Group CBT exercises (shared worksheets)
- Group mood check-in (aggregate mood before session)
- Individual vs. group progress tracking

---

### 2.5 SAFEGUARDING & DUTY OF CARE WORKFLOW ✅ COMPLETE (Feb 28, 2026)
**Priority: CRITICAL — Legal obligation** — FULLY IMPLEMENTED

- ✅ Safeguarding concern structured logging (27-column permanent record)
- ✅ Multi-agency referral tracking (MASH, Police, CAMHS, MARAC, GP, Social Care, LA)
- ✅ Duty clinician rota system (daytime + OOH slots, upsert on conflict)
- ✅ Escalation workflow: immediate_risk=True → critical alert + email + notification cascade
- ✅ Gillick competency / MCA 2005 capacity assessment fields
- ✅ Mandatory reporting tracker (status: open → referred → monitoring → closed)
- ⏳ Encrypted inter-agency information sharing (future: secure messaging to MASH)

---

### 2.6 APPOINTMENT SYSTEM UPGRADE
**Priority: HIGH — Current system is basic**

- Full calendar view (month/week/day, colour-coded)
- Clinician availability slot management
- Patient self-booking from available slots
- Video call integration (built-in or Whereby/Zoom link)
- Appointment reminders (48h, 24h, 1h — SMS/email/in-app)
- DNA tracking + repeated DNA alerts
- Recurring appointment patterns
- Telehealth vs. in-person tracking

---

### 2.7 CLINICAL SUPERVISION MODULE
**Priority: MEDIUM**

- Supervision booking within platform
- Anonymized case discussion threads
- Mandatory supervision log (regulatory requirement)
- Clinician reflective journal (private)
- CPD tracking (log hours)
- Peer case consultation (anonymized, consent-gated)

---

## PHASE 3 — PATIENT EMPOWERMENT & ENGAGEMENT
### Timeline: Q2–Q3 2026 | Focus: Make patients want to come back every day

---

### 3.0 ONBOARDING REDESIGN — ALL USER TYPES
**Priority: HIGH — First impressions define retention and clinical safety**

> *"The first five minutes in a therapist's waiting room shapes everything that follows. Our onboarding is that waiting room. It needs to feel warm, safe, and unhurried — while collecting exactly what we need and nothing more."*

#### The Problem
Feedback confirms the current patient sign-up is long, form-heavy, and clinical in tone. It asks for everything at once before the user has experienced any value. This creates drop-off at the very point we most need engagement, and it puts unnecessary burden on users who may already be vulnerable. The same issue affects clinicians: our current form doesn't validate their professional registration, creating a clinical governance gap.

#### UK Regulatory Requirements — What MUST Be Collected

**For ALL users:**
- Full legal name *(required for clinical record and GDPR identity)*
- Date of birth *(age verification — 18+ for standard registration; separate under-18 pathway needed)*
- Email address *(account identity, legal communications)*
- Password or OAuth credential
- Explicit GDPR consent *(UK GDPR Art. 6 + Art. 9 — special category health data)*
- Acknowledgment: "This platform is not an emergency service"
- Marketing/research consent *(separate, opt-in, clearly distinguished)*

**Additional — Patients only:**
- Safety screen: "Are you experiencing a mental health crisis right now?" → Yes = immediate crisis overlay, SOS resources, do NOT continue to sign-up (offer crisis contact instead)
- Professional care: "Are you currently under the care of a mental health professional?" *(informs suggested features and risk defaults)*
- Optional: preferred name (may differ from legal name)
- Deferred: everything else (NHS number, address, phone, emergency contact, presenting problem, baseline assessments — all collected after first login during profile completion)

**Additional — Clinicians only:**
- Professional registration body (BACP / UKCP / BPS / NMC / HCPC / GMC / BABCP — dropdown)
- Professional registration number *(for verification against body's register)*
- Agreed to Healing Space UK's Practitioner Agreement and Clinical Governance Policy
- Employer/Practice name *(optional at signup, required before first patient assigned)*
- Indemnity insurance confirmation *(required before patient access granted)*
- Background check: confirmation DBS certificate is current and on file

**Developers/Admins:**
- Admin-created only — no self-registration. Current approach is correct.

#### Minimum Viable Sign-Up Per Role — The "3-Screen Rule"

**Patient Onboarding (3 screens + email verification):**
```
Screen 1 — "Let's Begin"
  • First name + Email + Password (or Google/Apple OAuth)
  • Safety gate: "Are you in crisis right now?" [No, I'm okay / I need help right now]
    → Crisis branch: SOS resources, Samaritans, NHS 111 — do not proceed to sign-up
  • Progress indicator: ●○○

Screen 2 — "Just a Moment"
  • Date of birth (18+ check, clear error if under 18 with explanation and CAMHS signposting)
  • Are you currently working with a mental health professional? [Yes / No / Not sure]
  • Progress indicator: ●●○

Screen 3 — "A Few Important Things"
  • Plain-English GDPR summary (3 bullet points, link to full policy)
    - "We store your health data to support your care"
    - "You can download or delete your data at any time"
    - "We never sell your data"
  • Checkbox: "I agree to the Terms of Service and Privacy Policy" (required)
  • Checkbox: "I'd like to receive helpful tips and updates by email" (optional, pre-unchecked)
  • Progress indicator: ●●●

Post-registration:
  • Email verification link sent (must verify before accessing app)
  • Welcome screen with: "Your sanctuary is ready. Take a moment to make it yours →"
  • Progressive profile setup offered (not mandatory): preferred name, therapy goals (freetext), how they heard about us
  • Baseline PHQ-9/GAD-7 offered as first "quest" — warm framing: "This helps us understand where you're starting from"
```

**Clinician Onboarding (4 screens + email verification + admin approval):**
```
Screen 1 — "Welcome, Healer"
  • Full name + Email + Password
  • Professional body (dropdown: BACP, UKCP, BPS, NMC, HCPC, GMC, BABCP, Other)
  • Registration number
  • Progress indicator: ●○○○

Screen 2 — "Your Practice"
  • Practice / employer name (optional)
  • Modalities practiced (checkboxes: CBT, ACT, DBT, EMDR, Psychodynamic, Integrative, etc.)
  • Primary client group (Adults / CAMHS / Older Adults / Mixed)
  • Progress indicator: ●●○○

Screen 3 — "Governance Essentials"
  • DBS check current and on file: [Yes — confirm] [No — we'll send guidance]
  • Professional indemnity insurance: [Yes — confirm] [No — we'll send guidance]
  • I agree to the Practitioner Agreement (plain-English summary + link to full doc)
  • I agree to the Clinical Governance Policy (plain-English summary + link)
  • Progress indicator: ●●●○

Screen 4 — "Almost There"
  • GDPR consent (same as patient — health data processing)
  • "How would you describe your role?" [Therapist / Counsellor / Psychologist / Psychiatrist / Other]
  • Brief bio (optional, shown to patients if desired)
  • Progress indicator: ●●●●

Post-registration:
  • Email verification + admin approval queue (clinician sees "Your account is pending review — usually within 1 working day")
  • Background verification: auto-lookup against BACP/UKCP public registers where API available (manual review for others)
  • On approval: welcome email with quick-start guide, first patient setup walkthrough
```

#### Modern UX Patterns to Implement

| Pattern | Rationale |
|---------|-----------|
| **OAuth (Google/Apple)** | 40-60% of users prefer not creating a new password; reduces friction and abandonment |
| **One question per screen** (for mobile) | Reduces cognitive load, especially for people in distress |
| **Warm, conversational copy** | "What should we call you?" not "Enter first name" |
| **Illustrated progress indicator** | Small sanctuary illustration that "grows" as steps complete |
| **Inline validation** | Errors shown as you type, not on submit |
| **No asterisks / mandatory fields language** | Every field shown is required unless labelled "(optional)" |
| **Magic link option** | Email-based login as alternative to password (improves accessibility) |
| **Autosave** | Save progress so returning users don't restart from step 1 |
| **"Why do we ask this?"** tooltips | For any field that might feel intrusive — builds trust |
| **Smart defaults** | Pre-fill DOB picker to reasonable adult range; default to UK |

#### Progressive Post-Signup Profile Completion
After signing in for the first time, a patient is gently prompted (never blocked) to optionally complete:
- Emergency contact (name + phone) — nudged once, then dismissible
- Presenting concern summary (freetext, shows in clinician view)
- Therapy goals ("What would you like to be different in your life?")
- Baseline clinical assessments (PHQ-9, GAD-7 framed as "Let's see where you're starting from")
- Profile photo (optional — used in community and treatment plan)
- Notification preferences

This profile completion bar is visible in settings and on the home screen until 100% — but accessing any feature is never blocked by incomplete profile.

#### Under-18 Pathway
Currently the platform is adults-only. This section should clarify:
- Users under 18 are redirected to age-appropriate resources (YoungMinds, CAMHS.nhs.uk, Kooth)
- A roadmap item to build a fully compliant under-18 experience (requires Gillick competency framework, parental consent workflow, mandatory safeguarding protocols) is captured in Phase 6 (Compliance)

#### Technical Implementation Notes
- **Auth**: Add Google OAuth + Apple OAuth via `Authlib` or `Flask-Dance`
- **Magic link**: Generate time-limited JWT token, email link, auto-login on click
- **BACP/UKCP register lookup**: BACP has a public search API; UKCP has a public directory (scrape-safe); build async verification job
- **Admin approval queue**: New clinician accounts set `status='pending'`; admin approval sets `status='active'`; automated email at each stage
- **Age gate**: Server-side validation of DOB → under-18 blocked with error + signposting
- **Safety gate**: Crisis check on Step 1 — if "I need help now" selected → no account created, full crisis resources shown, session flagged for analytics (anonymized)
- **GDPR consent storage**: `user_consents` table — consent type, version, timestamp, IP hash; required for lawful basis evidence
- **Multi-step form state**: Store partial form in `session` (not localStorage) to survive page reload; clear on completion or abandonment >1h

#### Onboarding Metrics to Track
- Sign-up start → completion rate (target: >75%)
- Step-by-step drop-off funnel
- Time to first meaningful action (first mood log, first CBT tool, first clinician contact)
- Time from clinician registration to first patient assigned
- Crisis-gate activation rate (important safeguarding metric)
- OAuth vs. email/password split

---

### 3.1 PSYCHOEDUCATION LIBRARY
**Priority: HIGH**

- Video library (3–5 min evidence-based explainers)
- Clinical-quality plain-English articles: depression, anxiety, OCD, trauma, bipolar, sleep, relationships, medication
- Clinician can assign specific articles as homework
- Reading history visible to clinician
- Downloadable worksheets and guides

---

### 3.2 MINDFULNESS & MEDITATION CENTRE
**Priority: MEDIUM**

- Guided meditation library (5–30 min)
- Sleep meditations
- Breathwork library (4-7-8, Wim Hof, trauma-sensitive)
- Body scan (MBCT/MBSR aligned)
- Progressive muscle relaxation audio
- Completion tracking and favourites
- Clinician prescription (assign as homework)

---

### 3.3 PERSONALIZED RELAPSE PREVENTION PLAN
**Priority: HIGH — Critical for sustained recovery**

- Personal warning signs identification
- Trigger mapping (what makes things worse for this person)
- Coping strategy ranking (learned from actual usage data)
- Social support map (who to call, what to ask for)
- Graded response plan ("If X, then Y. If Y fails, then Z")
- Clinician co-produced
- Living document updated throughout therapy
- Connected to safety plan

---

### 3.4 FAMILY & CARER PORTAL
**Priority: MEDIUM**

- Carer account type linked to patient (explicit consent)
- Limited patient-controlled visibility (no clinical content)
- Shared goals visible to carer
- Crisis plan sharing
- Carer resources (how to support someone)
- Carer wellbeing check (brief carer burden assessment)

---

### 3.5 WEARABLE & HEALTH DATA INTEGRATION
**Priority: MEDIUM — Future standard of care**

- Apple Health / HealthKit, Google Fit, Fitbit API
- Automatic mood-health correlation ("On days you sleep <6h, your mood is 2.1 pts lower")
- Clinician insights (anonymized, with consent)
- Interventions based on data (low sleep detected → sleep hygiene resource)

---

### 3.6 VOICE MOOD LOGGING
**Priority: MEDIUM — Accessibility and engagement**

- Speak mood instead of typing
- Transcription to text
- Tone analysis (with explicit consent)
- Voice therapy journaling
- Accessibility: critical for motor difficulties, dyslexia

---

### 3.7 PEER RECOVERY COMMUNITY 2.0
**Priority: MEDIUM**

- Themed rooms (anxiety, depression, general)
- Anonymous posting mode
- AI + human moderation
- Community challenges
- Recovery stories section
- Safety monitor extended to community posts
- Virtual group events (mindfulness, Q&A with professionals)

---

## PHASE 4 — ADVANCED AI & INTELLIGENCE
### Timeline: Q3 2026 | Focus: AI that genuinely improves clinical outcomes

---

### 4.1 CONVERSATIONAL AI THERAPY EVOLUTION
**Priority: HIGH — Core differentiator**

- Therapeutic modality specialization (CBT, ACT, DBT, CFT, EMDR-informed)
- Session arc structure (beginning, middle, end)
- Personalised homework generation from session content
- Formulation awareness (AI incorporates clinician's case formulation)
- Tone calibration (patient adjusts communication style)
- Crisis moment protocol (distinct from regular therapy mode)
- Session summaries (auto-generated for patient to keep)
- CBT skill drilling in conversation form

---

### 4.2 MOOD PREDICTION ENGINE
**Priority: HIGH — Genuinely innovative**

- 7-day mood forecast based on patient's own patterns
- Risk factor identification ("Your mood drops on Mondays and after poor sleep")
- Proactive intervention (predicted bad day → extra support that morning)
- Seasonality detection (SAD patterns, anniversary reactions)
- Pattern disruption alerts

---

### 4.3 AI INTAKE & ASSESSMENT
**Priority: HIGH**

- Conversational intake (warm, structured, not checkbox forms)
- PHQ-9/GAD-7 embedded naturally in dialogue
- C-SSRS screening woven into conversation
- Provisional formulation for clinician review
- Treatment matching (approach + intensity)
- Clinician assignment (speciality + availability match)
- Waiting list intelligent placement (urgency from intake)

---

### 4.4 NATURAL LANGUAGE CLINICAL DOCUMENTATION
**Priority: HIGH — Clinician efficiency multiplier**

- Voice-to-notes (speak after session, AI generates SOAP/BIRP)
- AI drafts GP letters, referral letters, court reports from clinical notes
- ICD-11 code suggestion from assessment data
- Audit data extraction (pull clinical data for service audits automatically)

---

### 4.5 ANONYMIZED POPULATION INSIGHTS
**Priority: MEDIUM**

- Outcome benchmarking vs. similar cases
- Treatment effectiveness data (which interventions work for which presentations)
- Service-level aggregate reporting for NHS
- National benchmarking vs. IAPT dataset

---

## PHASE 5 — PLATFORM SCALE & INTEGRATIONS
### Timeline: Q3–Q4 2026 | Focus: Enterprise-ready, NHS-compatible

---

### 5.1 NHS & SYSTEM INTEGRATIONS
**Priority: HIGH — Required for NHS adoption**

- NHS Login (patient authentication)
- NHS Spine (demographics, GP registration, NHS number)
- GP Connect (medications, allergies, past medical history)
- EMIS / SystmOne / Rio (two-way EPR sharing)
- IAPT IDS submission (mandatory for NHS IAPT)
- HL7 FHIR R4 full compliance
- NHS 111 / Crisis Care direct referral pathway

---

### 5.2 MULTI-TENANCY ARCHITECTURE
**Priority: HIGH — Required for commercial scale**

- Organisation model (NHS Trust / private practice / university = isolated tenant)
- Custom branding (logo, colours, domain)
- Tenant admin (manage own clinicians and settings)
- Data isolation (GDPR critical)
- Subscription tiers (per-clinician, per-patient, enterprise)
- SSO (NHS email, university SSO, practice Active Directory)

---

### 5.3 MOBILE APPS (iOS & ANDROID)
**Priority: HIGH — Patients expect this**

- Full native wrapper (Capacitor)
- Push notifications (crisis alerts, appointment reminders, daily nudges)
- Biometric authentication (Face ID / fingerprint)
- Offline mode (core CBT tools + safety plan always accessible)
- Home screen widgets (quick mood log without opening app)
- App Store + Play Store deployment
- WCAG 2.1 AA compliant throughout

---

### 5.4 VIDEO THERAPY INTEGRATION
**Priority: HIGH — Standard of care**

- Built-in video sessions (Daily.co or Jitsi self-hosted for NHS data requirements)
- Waiting room
- Session notes panel (split-screen during session)
- Low-bandwidth audio-only mode
- Screen share for reviewing worksheets together

---

### 5.5 PROGRESSIVE WEB APP (PWA)
**Priority: MEDIUM — Before mobile apps**

- Service worker (offline caching)
- Install prompt ("Add to Home Screen")
- Offline CBT tools (safety plan, breathing, grounding always available)
- Background sync
- Web Push notifications

---

### 5.6 CALENDAR & EXTERNAL INTEGRATIONS
**Priority: MEDIUM**

- Google Calendar / Outlook sync for appointments
- Zapier / Make.com for custom automations
- Webhook system (subscribe to events: new assessment, crisis alert)
- Email digest (weekly summary — patient and clinician versions)

---

## PHASE 6 — COMPLIANCE, GOVERNANCE & CERTIFICATION
### Timeline: Ongoing | Focus: NHS readiness, legal robustness

---

### 6.1 NHS DIGITAL CERTIFICATION (DTAC)
**Priority: CRITICAL for NHS adoption**

- Clinical Safety (DCB0129/DCB0160) — Clinical Risk Management File, Clinical Safety Officer, Hazard Log
- DSPT — Data Security & Protection Toolkit (mandatory NHS)
- Cyber Essentials Plus (NCSC)
- DTAC Assessment
- NICE Evidence Standards
- CQC registration (if applicable)

---

### 6.2 GDPR COMPLETE IMPLEMENTATION
**Priority: HIGH**

Gaps to close:
- Comprehensive Article 20 data export (ALL data: AI insights, session notes, risk assessments, safety plans)
- Automated data retention policies (chat history: 7-year max then auto-delete)
- 72-hour ICO breach notification procedure
- Granular consent management UI (treatment, research, AI training, analytics)
- UK PII stripping (NHS numbers, postcodes, NI numbers)
- Right to erasure — complete, verified deletion including backups

---

### 6.3 FIELD-LEVEL ENCRYPTION
**Priority: HIGH — Clinical data demands maximum protection**

Fernet encryption available, not yet applied. Encrypt at rest:
- Therapy chat content
- C-SSRS responses
- Safety plans
- Session notes
- Diagnoses
- Safeguarding records

---

### 6.4 COMPREHENSIVE AUDIT LOGGING
**Priority: HIGH**

- Every patient data access logged (who, what, when, from where)
- 7-year retention (NHS standard)
- Tamper-evident logs
- Audit log viewer in developer dashboard
- Automated compliance reports
- Clinician access audit (visible to patient on request)

---

### 6.5 CI/CD PIPELINE & QUALITY GATES
**Priority: HIGH**

- GitHub Actions: automated tests on every PR, security scanning (pip-audit, bandit), coverage gate (>80%), staging deploy on merge, production deploy gated on manual approval
- Dependabot — automated dependency updates
- Pre-commit hooks — linting, secret scanning
- OpenAPI spec — auto-generated and validated in CI

---

## PHASE 7 — ARCHITECTURE EXCELLENCE
### Timeline: Q3–Q4 2026 | Focus: Technical foundation for the next 5 years

---

### 7.1 FRONTEND ARCHITECTURE MODERNISATION
**Priority: HIGH — Current monolith is approaching limits**

Current: ~24,000-line monolithic HTML with inline JS/CSS.

Target:
- Component-based architecture (React or Svelte)
- Vite build system
- CSS modules (scoped styles)
- Code splitting (lazy-load tabs)
- TypeScript
- Storybook component library
- Playwright E2E testing
- Bundle size target: <200KB gzipped

---

### 7.2 BACKEND MODULARISATION
**Priority: HIGH — api.py at 20,000 lines needs splitting**

- Flask Blueprints per domain: `auth`, `therapy`, `clinical`, `messaging`, `community`, `admin`, `developer`, `pet`, `wellness`, `cbt`
- Service layer (business logic from route handlers)
- Repository pattern (data access abstracted)
- Pydantic models (request/response validation)
- SQLAlchemy ORM (replace most raw psycopg2)

---

### 7.3 DATABASE SCHEMA NORMALISATION
**Priority: MEDIUM**

Issues:
- Inconsistent timestamp naming (`entry_timestamp` vs `created_at` vs `entrestamp`)
- TEXT fields that should be JSONB
- Username as primary key (should be UUID)
- Missing FK constraints on some relationships

Migration strategy: zero-downtime, backward-compatible.

---

### 7.4 CACHING LAYER
**Priority: MEDIUM**

- Redis — session storage, rate limiting, caching
- Cache: clinician caseload, patient profile, notification counts
- Event-driven invalidation

---

### 7.5 ACCESSIBILITY (WCAG 2.1 AA)
**Priority: HIGH — Legal requirement (Equality Act 2010)**

- Full WCAG 2.1 AA audit
- ARIA labels on all interactive elements
- Full keyboard navigation
- Screen reader testing (NVDA, JAWS, VoiceOver)
- Colour contrast compliance
- Skip links and landmark regions

---

## PHASE 8 — MARKET LEADERSHIP & FUTURE VISION
### Timeline: 2027 | Focus: Category leadership

---

### 8.1 CLINICIAN MARKETPLACE
- Public-facing clinician directory
- Patient-clinician AI matching
- Clinician verification (BACP/UKCP/BPS via API)
- Review system (anonymized, moderated)

---

### 8.2 REAL-WORLD EVIDENCE PLATFORM
- Continuous outcome data (published annually)
- Health economic analysis (cost per QALY)
- NHS commissioning support pack
- NICE submission (transformational for adoption)
- Academic partnerships (UCL, King's, Oxford)

---

### 8.3 INTERNATIONAL EXPANSION
- Welsh (legal requirement — NHS Wales)
- Spanish, Arabic, Urdu, Polish (UK population needs)
- EU GDPR compliance (European expansion)
- US HIPAA compliance (US market)

---

### 8.4 AI THERAPIST V2 — AUTONOMOUS SUPPORT
*(For Step 2 / low-intensity presentations only, always clinician-supervised)*
- Structured CBT protocol delivery (Beating the Blues equivalent)
- Automated PHQ-9 monitoring with deterioration alerts
- Personalized between-session exercises with follow-up
- Outcome equivalent to low-intensity IAPT: the clinical bar

---

## COMPLETION STATUS MATRICES

### Clinician Dashboard

| Feature | Status |
|---------|--------|
| Session notes (SOAP/BIRP) | ✅ Complete (Feb 20) |
| Treatment plan builder | ✅ Complete (Feb 20) |
| CORE-OM / WEMWBS / ORS / SRS | ✅ Complete (Feb 20) |
| Waiting list management | ✅ Complete (Feb 21) |
| Medication view per patient | ✅ Complete (Feb 22) |
| Patient moods + wellness logs | ✅ Complete (Feb 22) |
| Patient CBT records + gratitude | ✅ Complete (Feb 22) |
| Patient chat history view | ✅ Complete (Feb 22) |
| Patient C-SSRS history | ✅ Complete (Feb 22) |
| Unified risk alert panel | ✅ Complete (Feb 22) |
| Recovery progress tab | ✅ Complete (Feb 21) |
| Outcome trajectory charts | ✅ Complete (Feb 21) |
| Discharge workflow | ⏳ Missing |
| Referral letter generator | ⏳ Missing |
| Group therapy module | ⏳ Missing |
| Clinical supervision log | ⏳ Missing |
| Safeguarding workflow | ⏳ Missing |
| AI weekly patient summaries | ⏳ Missing |
| AI session prep brief | ⏳ Missing |
| Predictive crisis alerts | ✅ Complete (Feb 24) |
| Video therapy integration | ⏳ Missing |
| CPD tracker | ⏳ Missing |

### Patient Experience

| Feature | Status |
|---------|--------|
| AI therapy chat | ✅ Complete |
| 17 CBT tools | ✅ Complete |
| Mood logging | ✅ Complete |
| Wellness ritual (10-step) | ✅ Complete |
| SOS crisis button (all screens) | ✅ Complete |
| Medication tracker | ✅ Complete (Feb 22) |
| Recovery milestones | ✅ Complete (Feb 21) |
| Progress dashboard + charts | ✅ Complete (Feb 21) |
| C-SSRS safety assessment | ✅ Complete |
| Safety plan | ✅ Complete |
| Community forum | ✅ Complete |
| Pet / familiar | ✅ Complete (basic) |
| Gratitude journal | ✅ Complete |
| Clinical assessments (PHQ-9, GAD-7, CORE-OM, ORS, SRS) | ✅ Complete |
| Appointments | ✅ Complete (basic) |
| Quest system | ✅ Complete (Feb 22) |
| Healing Journey / sanctuary redesign | ✅ Complete (Feb 22) |
| Spell library presentation layer | ✅ Complete (Feb 22) |
| Familiar evolution system | ⏳ Designed, not built |
| Achievement constellation | ⏳ Designed, not built |
| Journey Map visualisation | ⏳ Designed, not built |
| Psychoeducation library | ⏳ Missing |
| Mindfulness / meditation | ⏳ Missing |
| Relapse prevention plan | ⏳ Missing |
| Family / carer portal | ⏳ Missing |
| PWA / offline mode | ⏳ Missing |
| Native mobile apps | ⏳ Missing |
| Wearable integration | ⏳ Missing |
| Streamlined onboarding (all roles) | ⏳ Designed (see 3.0), not built |

### Risk & Safety Pipeline

| Signal | Alert Created | Clinician Notified |
|--------|--------------|-------------------|
| C-SSRS completed (any level) | ✅ risk_alerts | ✅ in-app + email |
| PHQ-9 Moderate+ | ✅ alerts + risk_alerts | ✅ in-app |
| GAD-7 Moderate+ | ✅ alerts + risk_alerts | ✅ in-app |
| Mood ≤ 3/10 | ✅ risk_alerts | ✅ in-app |
| Outcome measure severe | ✅ risk_alerts | ✅ in-app |
| Chat risk keywords | ✅ risk_alerts | ✅ email |
| Mood trend decline (predictive) | ✅ predictive_risk_flags | ✅ in-app toast + Risk Monitor |
| Engagement drop (predictive) | ✅ predictive_risk_flags | ✅ in-app toast + Risk Monitor |
| Real-time badge/notification updates | ✅ smart polling (10s) | ✅ OS browser notification |

---

## DEVELOPER DASHBOARD — COMPLETE VISION

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
| Feature usage heatmap | Which tools/tabs used most |
| Outcome analytics | Which features correlate with best PHQ-9 improvement |
| System health monitor | CPU, memory, DB connections |
| GitHub Actions status | CI/CD pipeline embedded |

---

## EFFORT & PRIORITY MATRIX

| Phase | Priority | Effort | Impact | Target |
|-------|----------|--------|--------|--------|
| Healing Journey (HJ.1–HJ.3) ✅ | **DONE** | Medium | Very High | Feb 2026 |
| 2.1 Predictive Crisis Detection ✅ | **DONE** | High | Critical | Feb 2026 |
| 2.5 Safeguarding & Duty of Care ✅ | **DONE** | High | Critical | Feb 2026 |
| Real-Time Polling Engine ✅ | **DONE** | Medium | High | Feb 2026 |
| Smart Tab Refresh ✅ | **DONE** | Low | Medium | Feb 2026 |
| Developer Dashboard (Logs/Diagnostics/Verbose Tests) ✅ | **DONE** | Medium | High | Feb 2026 |
| Mobile Menu Fix ✅ | **DONE** | Low | High | Feb 2026 |
| Healing Journey (HJ.4–HJ.7) | **Q2 2026** | Medium | High | Q2 2026 |
| 2.2–2.4, 2.6–2.7 — Clinical Excellence | **Q2 2026** | High | Very High | Q2–Q3 2026 |
| 3.0 — Onboarding Redesign | **Q2 2026** | Medium | Very High | Q2 2026 |
| 3 — Patient Empowerment | **Q2–Q3 2026** | Medium | High | Q3 2026 |
| 4 — AI & Intelligence | **Q3 2026** | High | Very High | Q3 2026 |
| 5 — Scale & Integrations | **Q3–Q4 2026** | Very High | Very High | Q4 2026 |
| 6 — Compliance | **Ongoing** | Medium | Critical | Ongoing |
| 7 — Architecture | **Q3–Q4 2026** | Very High | Medium (long-term) | Q4 2026 |
| 8 — Market Leadership | **2027** | Very High | Transformational | 2027 |

---

## THE NON-NEGOTIABLES (Before clinical deployment)

1. ✅ Security hardening
2. ✅ SOS crisis button on every screen
3. ✅ Session notes system
4. ✅ Treatment plan documentation
5. ✅ CORE-OM outcome measures
6. ✅ Unified risk alert pipeline
7. ✅ Full patient data visible to clinician
8. ✅ Safeguarding workflow (2.5 — full implementation Feb 28, 2026)
9. ⏳ Field-level encryption for clinical data
10. ⏳ GDPR comprehensive implementation
11. ⏳ Clinical risk management documentation (DCB0129)
12. ⏳ DSPT/DTAC compliance

---

## GUIDING PRINCIPLES FOR EVERYTHING WE BUILD

1. **Clinical first** — every feature defensible to a clinician reviewer
2. **Privacy by design** — assume the most sensitive data, protect accordingly
3. **Trauma-informed** — no jarring alerts, no clinical jargon without explanation, no time pressure
4. **Evidence-based** — tied to NICE guidelines and published literature
5. **Accessible** — WCAG 2.1 AA minimum, designed for cognitive load
6. **AI assists, humans decide** — AI never acts without clinician review on clinical matters
7. **Transparent** — patients know how their data is used; clinicians know how AI works
8. **The Healing Journey** — every interaction should honour that this person is doing something brave and hard. Make it feel that way.
9. **World class** — the question is always: "Would this be at home in the best mental health platform in the world?"

---

## ON GITHUB → UPDATES TAB INTEGRATION

Achievable in ~1 hour:
1. GitHub Actions workflow on push to `main`
2. Action calls `POST /api/dev/updates` with commit message, author, auto-incremented version
3. Update appears in all users' "What's New" tab automatically
4. Filter: only commits prefixed `feat:`, `fix:`, `improve:` trigger updates
5. API endpoint already exists — only the GitHub Action needs adding

---

*Roadmap last updated: February 28, 2026.*

**Session summary (Feb 28, 2026):**
- ✅ **2.5 Safeguarding & Duty of Care Workflow** — full UK statutory implementation (9 endpoints, 2 tables, complete clinical form, immediate-risk cascade, duty clinician rota). Test suite: `tests/backend/test_safeguarding.py` (50+ test cases)
- ✅ **Smart Tab Refresh** — `_refreshActiveTabContent()` on visibility restore + tab switch (Risk Monitor, Safeguarding, Analytics, Messages, Community, Notifications, Waiting List, Appointments)
- ✅ **Developer Dashboard — Verbose Test Runner** — `POST /api/developer/tests/verbose` (configurable scope, traceback depth short/long/full, saved to DB); 🛡️ Safeguarding test scope button; 🤖 Suggest Fix button pipes failures into AI assistant
- ✅ **Developer Dashboard — Live Log Viewer** — `GET /api/developer/logs/view` (level filter ALL/DEBUG/INFO/WARNING/ERROR/CRITICAL, search, 100–1000 line window); live tail mode (5s interval); 📋 Logs subtab; CSS chip buttons
- ✅ **Developer Dashboard — Diagnostics Panel** — `GET /api/developer/diagnostics` (DB table counts + sizes, active PG connections, recent log errors, latest test run, route count, environment); 🔬 Diagnostics subtab with stats cards
- ✅ **Mobile Menu Fix** — extended breakpoint to 900px; sidebar switches to horizontal scrollable tab bar at top; `flex-shrink: 0`; compact button sizing for 480px screens

*Next review: April 2026.*
*This document should be reviewed quarterly and updated after each major milestone.*
