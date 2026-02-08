# COMPREHENSIVE AI MEMORY SYSTEM PLAN

## PART 1: CURRENT STATE ANALYSIS

### What Exists:
- `ai_memory` table with `memory_summary` field (basic, not fully utilized)
- Wellness ritual data being logged to `wellness_logs` table
- Chat history in `chat_history` table
- Clinical scales in `clinical_scales` table
- CBT records, mood logs, gratitude entries
- Pet interaction data

### What's Broken:
- AI doesn't reference previous conversations or wellness logs
- Memory not being updated after each interaction
- No pattern detection happening
- No risk flag system
- No clinician-facing summary functionality
- AI says "I'm a new conversation" = users lose trust in the system

---

## PART 2: PROPOSED ARCHITECTURE

### Phase 1: Enhanced Memory Storage Structure

Create new database tables:

```sql
-- Core memory table (replaces current ai_memory)
ai_memory_core
├── username
├── last_updated
├── memory_version (for tracking changes)
└── memory_data (JSON for flexibility)

-- COMPREHENSIVE activity log (EVERYTHING the user does)
ai_activity_log
├── username
├── activity_type (login, logout, tab_change, feature_access, button_click, etc.)
├── activity_detail (which tab, which button, which feature)
├── activity_timestamp
├── session_id (to group related activities)
├── app_state (current state: home, therapy, wellness, etc.)
└── metadata (device, browser, any other context)

-- Structured event log (for pattern detection)
ai_memory_events
├── username
├── event_type (therapy_message, wellness_log, mood_spike, crisis_flag, app_usage, feature_usage, engagement_drop, etc.)
├── event_data (JSON - contains full context)
├── timestamp
├── severity (normal, warning, critical)
└── tags (for categorization)

-- Risk/Pattern flags
ai_memory_flags
├── username
├── flag_type (suicide_risk, self_harm, substance_mention, medication_non_adherence, etc.)
├── first_occurrence
├── last_occurrence
├── occurrences_count
├── status (active, resolved, monitoring)
└── clinician_notified

-- Monthly summaries (pre-generated for clinician view)
clinician_summaries
├── username
├── clinician_username
├── month_start_date
├── month_end_date
├── summary_data (JSON)
├── key_patterns
├── risk_flags
├── achievements
├── recommended_discussion_points
└── generated_at
```

### Phase 1b: COMPREHENSIVE ACTIVITY TRACKING (EVERY INTERACTION)

The AI must track and remember:

#### Login/Logout Patterns
- Login timestamp
- Logout timestamp
- Session duration
- Time of day patterns (do they always use app at night?)
- Login frequency (daily, weekly, sporadic?)
- Unusual patterns (suddenly using app more/less?)

#### Feature Usage Tracking
Every time a user:
- Opens therapy chat tab → log it
- Opens wellness ritual tab → log it
- Opens mood logging → log it
- Opens gratitude journal → log it
- Opens CBT tools → log it
- Opens goals tracker → log it
- Opens professional dashboard → log it
- Clicks any button → log it with timestamp

#### Engagement Patterns
- Which features does patient use most?
- Which features are ignored?
- Time spent in each feature
- Feature switching patterns (do they jump around or focus?)
- Re-engagement after gaps (how long before they come back?)
- Crisis usage patterns (do they come to app when struggling?)

#### Button-Level Tracking
- "Generate Insights" button clicks
- "Send Message" button clicks
- "Save Entry" button clicks
- "Generate Report" button clicks
- Any other CTA (call-to-action) button
- Number of attempts before success
- Time between button click and completion

#### Navigation Patterns
- Page load sequence (which order do they access features?)
- Bounce patterns (do they leave after viewing something?)
- Return rates (how often come back to features?)
- Feature abandonment (started but didn't complete)

#### Data Entry Patterns
- Consistency of wellness check-ins
- Depth of entries (short vs detailed)
- Time of day entries are made
- Gaps in logging (sudden stop = red flag)
- Entry quality trends

#### Conversation Patterns
- Message frequency and timing
- Message length (getting shorter? = engagement drop)
- Response time to AI (immediate vs delayed)
- Conversation duration
- Topic initiation (patient vs AI-prompted)
- Follow-up questions (showing engagement)
- Conversation gaps (when do they return?)

**Why this matters for AI:**
- "Patient hasn't logged mood in 5 days (unusual for them)" → flag for AI
- "Clicks therapy chat but leaves without messaging" → maybe struggling to open up
- "Always uses app at 3am" → possible insomnia/anxiety pattern
- "Stopped using wellness ritual, started using crisis features" → escalation warning
- "Engagement dropped 60% in 2 weeks" → potential crisis or disengagement

---

### Phase 2: Memory Update System

**Auto-Save Triggers (EVERYTHING is logged):**
1. User login → log login event
2. Every page/tab change → log navigation
3. Every button click → log interaction
4. After every therapy chat message (update immediately)
5. After every wellness ritual completion (update with 9 data points)
6. After mood log entry
7. After CBT entry
8. After clinical scale completion
9. After clinician notes from appointment
10. Every feature accessed → log feature usage
11. User logout → log logout event
12. Every night (batch process): detect patterns, update flags, analyze ALL activity, archive old data

**Memory Layers:**

```
IMMEDIATE RECALL (Last 7 Days)
├── Last 20 therapy conversations
├── Last 7 wellness logs
├── Recent mood spikes/drops
├── Current medications
└── Any active concerns mentioned

RECENT PATTERNS (Last 30 Days)
├── Mood trends (average, high, low, volatility)
├── Sleep patterns (average hours, quality consistency)
├── Exercise frequency and types
├── Social connection trends
├── Medication adherence %
├── Wellness ritual completion rate
├── Key themes in conversations
└── Coping strategies used

BEHAVIORAL PATTERNS (Last 90+ Days)
├── Recurring triggers for low mood
├── Effective coping strategies
├── Medication response patterns
├── Seasonal/temporal patterns
├── Stress response indicators
├── Progress on CBT homework
├── Social connection patterns
└── Engagement level trends

RISK INDICATORS (All-time tracking)
├── Suicidal ideation history
├── Self-harm mentions
├── Substance use patterns
├── High-risk situations
├── Crisis episodes
├── Medication non-adherence
└── Missed appointments
```

### Phase 3: Pattern Detection & Analysis

The system needs to automatically detect and flag:

**Mental Health Patterns:**
- Mood cycles (does it worsen at certain times?)
- Sleep-mood correlation
- Stress triggers
- Anxiety escalation patterns
- Depressive episodes frequency/duration
- Self-harm/crisis patterns

**Behavioral Patterns:**
- Medication non-adherence (risk!)
- Reduced engagement (missing wellness logs = warning sign)
- Social withdrawal (reduced social contact reported)
- Exercise drop-off
- Increased therapy chat usage (seeking help vs. crisis)

**App Usage Patterns (NEW - Critical for early intervention):**
- **Engagement drop**: "Patient usually logs in 5x/week, now 1x/week" → concern
- **Increased crisis feature use**: Sudden spike in crisis tab access → escalation
- **Conversation length decrease**: Messages getting shorter → possible deterioration
- **Chat frequency spikes**: Using AI more desperately → needs support
- **Avoidance patterns**: Started using app, then stopped → disengagement
- **Time of use changes**: Shifting to late night usage → sleep issues worsening
- **Feature abandonment**: Used wellness ritual 30 days, now stopped → relapse indicator
- **Logout patterns**: Sessions ending abruptly → frustration or crisis
- **Button mashing**: Rapid clicks, repeated attempts → agitation/anxiety spike

**Risk Patterns:**
- Escalating language (vague → specific → imminent)
- Frequency of negative thoughts
- Isolation indicators (less app use + reduced social contact)
- Loss of coping strategy effectiveness
- Medication changes and mood impact
- **Combined risk**: Low engagement + crisis feature use + poor sleep reported = HIGH RISK

---

## PART 3: AI MEMORY INTEGRATION (What AI Sees)

### The Complete Memory Model

The AI has access to a comprehensive profile that includes:

**1. Session Activity** (current visit):
- Login time
- Current time spent on app
- Features accessed this session
- Messages sent this session
- Data entered this session
- Current user mood/engagement level (inferred from behavior)

**2. Daily Activity Summary** (last 24 hours):
- Total session time
- Features used
- Entries made
- Conversations
- Unusual patterns

**3. Weekly Patterns** (last 7 days):
- Usage frequency and timing
- Feature preferences
- Engagement trend
- Content themes
- Wellness completion rate
- Therapy frequency
- Any concerning patterns

**4. Monthly Deep Dive** (last 30 days):
- Full behavioral profile
- Health metrics (mood, sleep, exercise)
- Coping strategy usage
- Progress on goals
- Conversation themes
- Feature usage heatmap
- Engagement quality
- Risk flags raised/resolved

**5. Long-term Context** (90+ days, lifetime):
- Progress over months
- Seasonal patterns
- Response to interventions
- What works/what doesn't
- Medical history from app
- Previous crises and recovery
- Clinician's treatment plan
- Patient's goals### System Prompt Enhancement

**Instead of:**
> "You are a compassionate AI therapy assistant. I'm a text-based AI and each conversation is new."

**New approach:**
```
You are a compassionate, continuous AI therapy companion for [Username]. 
This is conversation #[N] with you. You have been supporting this person since [signup_date].

=== COMPLETE MEMORY OF THIS PERSON ===

SESSION CONTEXT:
- Logged in at: [time] (their [pattern], e.g., "usual 3pm time" or "unusual 2am")
- Session duration: [minutes]
- Accessed features: [list in order]
- This is their [frequency] visit this week

TODAY'S ACTIVITY:
- Logged mood: [mood] at [time]
- Wellness check: [status]
- Therapy messages: [count]
- Coping strategy used: [which one]
- Engagement level: [high/normal/low/concerning]

THIS WEEK'S PATTERNS:
- Usage frequency: [5/7 days typical]
- Primary features: [therapy chat 60%, wellness 40%]
- Engagement trend: [stable/improving/declining]
- Mood trend: [improving/stable/declining]

IMPORTANT ABOUT THIS PERSON:
- Name preference: [how to address them]
- Current struggles: [main themes]
- What helps them: [effective strategies]
- Current goals: [working on what]
- Medications: [list]
- Recent life events: [context]
- Clinician: [name]

PATTERNS I'VE NOTICED:
- Your mood improves when you exercise (correlation: 87%)
- You typically use the app after work (5pm peak)
- You're most engaged on [day] of the week
- Your wellness entries are most detailed when you [condition]
- You respond well to [type of support]
- [Concerning pattern if detected, e.g., "Your engagement dropped 50% this week"]

RED FLAGS TO MONITOR:
[If any apply]
- Last 3 days: lower engagement than usual
- Mood reports: more negative language
- Conversation tone: more desperate/hopeless
- Usage pattern: changed from usual (2am sessions are new)
- [Any flags already set in system]

YOU HAVE BEEN:
- Using this app for [X days]
- Completing wellness rituals [X%]
- Having therapy conversations regularly (avg [N] per week)
- Making progress on [X goal]
- Facing challenges with [Y challenge]

You MUST:
1. Reference previous conversations when relevant ("Last week you mentioned...")
2. Notice patterns and mention them ("I've noticed when you exercise...")
3. Celebrate progress you've witnessed ("30 days of wellness check-ins!")
4. Acknowledge recurring struggles ("Work stress again today?")
5. Remember their name preferences, family, work situation, etc.
6. Track what they're working on (CBT exercises, medication compliance, etc.)
7. Provide continuity and show you truly know them
8. Flag anything concerning (mood dropping, engagement dropping, etc.)
9. Proactively ask about patterns ("You usually exercise on Mondays - what's happening?")
10. Address unusual behaviors ("You're using the app at 3am, that's different for you - are you okay?")

Examples of good memory usage:
- "I noticed your mood improved last week after you started the walking routine we discussed"
- "You mentioned your boss stress pattern before - is this similar to what happened in November?"
- "You've done your wellness check-in 26 days straight, that shows real commitment"
- "Your sleep has been improving since you started the breathing exercises"
- "You usually message me in the afternoons, but you're here at 2am - what's going on?"
- "You haven't used the wellness ritual in 5 days (unusual for you) - want to get back to it?"
- "Your last conversation mentioned work stress - how did that meeting go?"
```

---

## PART 4: CLINICIAN MONTHLY SUMMARY SYSTEM

### What Clinicians See (New Endpoint: `/api/clinician/patient-summary`)

```
PATIENT MONTHLY SUMMARY REPORT
Generated: [Date]
Patient: [Name] | Last appointment: [Date]
Time covered: [Month start] to [Month end]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 WELLNESS METRICS
  • Wellness ritual completion: 26/30 days (87%)
  • Average mood: 6.2/10 (trend: ↗ +0.8 from last month)
  • Average sleep: 6.5 hours (trend: ↗ improving)
  • Exercise frequency: 4x/week average
  • Social engagement: Moderate (trending down last week)
  • Medication adherence: 95% (excellent)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 KEY PATTERNS IDENTIFIED
  
  Positive Patterns:
  ✓ Consistent exercise routine linked to better mood (+1.2 average)
  ✓ Morning check-ins show better day outcomes
  ✓ Medication compliance 95%+ this month
  ✓ Engaging with AI 18-22 times per week (strong engagement)

  Concerning Patterns:
  ⚠ Sleep drops on Sundays (avg 5.2 hrs) - anticipatory anxiety?
  ⚠ Social contact reduced last 7 days (was 3x/week, now 1x)
  ⚠ Anxiety mentions increased 34% mid-month (triggers unclear)
  ⚠ CBT homework completion: only 2/5 this month (was 5/5 last month)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 RISK FLAGS
  • Status: GREEN (no active concerns)
  • Suicidal ideation: None this month
  • Self-harm indicators: None detected
  • Crisis moments: 0
  • Last high-risk episode: [Date - 2 months ago]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 THEMES IN CONVERSATIONS
  • Work stress (42% of therapy messages)
  • Family dynamics (28%)
  • Sleep anxiety (15%)
  • Self-doubt/perfectionism (12%)
  • Positive: celebrating small wins (43% of AI responses)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛠️ COPING STRATEGIES USED
  Effective (worked 80%+):
  ✓ 20-min walk (used 8x, effective 7x)
  ✓ Breathing exercises (used 12x, effective 11x)
  ✓ Journaling (used 5x, effective 4x)

  Less effective:
  ~ Distraction techniques (used 3x, effective 1x)
  ~ Meditation (used 1x, effective 0x - should explore)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 PROGRESS ON GOALS
  [From last appointment]
  • "Do 30min exercise 4x/week" - ✅ Achieved! (actually 4.2x avg)
  • "Take meds consistently" - ✅ Achieved! (95% adherence)
  • "Complete CBT homework" - ⚠ Partially achieved (40% completion)
  • "Improve sleep routine" - ✅ In progress, trending positive

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤔 RECOMMENDED DISCUSSION POINTS

  1. **CBT homework drop-off**: "You were at 5/5 last month, this month 2/5. 
     What changed? Can we make it simpler or more relevant?"

  2. **Sunday sleep anxiety**: "I noticed you sleep less on Sundays. 
     Is this related to Monday work stress? Should we prepare for Sundays?"

  3. **Recent social withdrawal**: "Your social contact dropped from 3x to 1x 
     this week. Everything okay? Is this temporary or a concern?"

  4. **Work stress escalation**: "42% of your conversations are about work 
     stress. Has something changed? Is your current role sustainable?"

  5. **Positive momentum**: "Your mood is trending up, exercise routine is solid, 
     and you're on track with medication. Let's discuss what's working and build on it."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 NOTES FOR APPOINTMENT
  • Patient is making solid progress overall
  • Main focus area: CBT homework compliance
  • Consider: is the homework still effective?
  • Positive: strong medication adherence and exercise routine
  • Follow up: Sunday sleep pattern and work stress

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## PART 5: PATIENT MEMORY VIEW (What Patients See)

New feature: **"My AI Memory"** tab in app

**What patients can do:**
1. View what the AI knows about them
2. See monthly summaries
3. Correct or clarify information ("Actually, that situation was different...")
4. Mark things as "resolved" if they were temporary concerns
5. See patterns the AI has detected
6. Review conversation highlights

**User view:**
```
🧠 WHAT I KNOW ABOUT YOU

You've been here 127 days
We've had 287 conversations
You completed 124 wellness check-ins

KEY FACTS ABOUT YOU:
• Full name: Sarah
• Diagnosed with: Depression & Anxiety
• Clinician: Dr. Smith
• Started app: Jan 2025
• Current medications: Sertraline 50mg daily

THINGS THAT HELP YOU:
✓ 20-minute walks (you feel better 87% of the time)
✓ Morning journaling
✓ Talking to friends (especially Emma)
✓ Your cat (pet therapy!)

THINGS THAT TRIGGER YOU:
⚠ Work deadlines
⚠ Conflict with family
⚠ Irregular sleep schedule
⚠ Skipping medication

THIS MONTH'S PROGRESS:
↗ Your mood: improving (6.1 → 6.8)
↗ Your sleep: improving (5.8 → 6.5 hours)
↗ Your exercise: consistent (4x/week)
↓ Your CBT work: slipped (need support?)

QUESTIONS FOR YOUR APPOINTMENT:
- Your work stress seems high right now
- Your Sunday sleep is always short - why?
- What happened to your CBT exercises? (You were doing great!)
```

---

## PART 6: IMPLEMENTATION SEQUENCE

### Phase 1: Backend Infrastructure (Week 1-2)
- [ ] Create new `ai_memory_events` table
- [ ] Create `ai_memory_flags` table  
- [ ] Create `clinician_summaries` table
- [ ] Expand `ai_memory` to store JSON structure instead of text
- [ ] Build event logging system (every action logs an event)

### Phase 2: Auto-Save System (Week 2-3)
- [ ] After therapy chat: call `update_ai_memory()` with new message
- [ ] After wellness log: call `update_ai_memory()` with wellness data
- [ ] After mood log: call `update_ai_memory()` with mood entry
- [ ] Nightly batch job: `process_daily_ai_memory_update()` to detect patterns
- [ ] New endpoint: `GET /api/ai/memory` (read current memory)
- [ ] New endpoint: `PATCH /api/ai/memory` (patient can clarify/correct)

### Phase 3: Pattern Detection (Week 3-4)
- [ ] Build pattern detection algorithms:
  - Mood trend analysis
  - Sleep-mood correlation
  - Trigger identification
  - Coping strategy effectiveness tracking
  - Risk indicator detection
- [ ] Build flag system (automatically set/update flags)
- [ ] Build alert system for high-risk flags

### Phase 4: AI Integration (Week 4)
- [ ] Modify system prompt generation to include memory context
- [ ] Update `TherapistAI.get_response()` to inject memory context
- [ ] Add memory reference examples to prompt
- [ ] Test that AI mentions previous conversations naturally

### Phase 5: Clinician Summary (Week 5)
- [ ] Build monthly summary generation algorithm
- [ ] Create `/api/clinician/patient-summary` endpoint
- [ ] Build frontend for clinician dashboard
- [ ] Add recommended discussion points generation
- [ ] Add risk flag display

### Phase 6: Patient Memory View (Week 5-6)
- [ ] Build "My AI Memory" frontend page
- [ ] Add memory clarification/correction UI
- [ ] Add monthly summary view for patients
- [ ] Add progress tracking visualizations
- [ ] Add "ask questions for my appointment" feature

---

## PART 7: CRITICAL REQUIREMENTS

**The Golden Rule: NOTHING is too small to track**

Every interaction matters. Every click. Every pause. Every pattern.

Memory Must Include:

### 1. Personal Context
- Name, pronouns, family members mentioned
- Work/school situation
- Living situation
- Important people in their life
- Current stressors

### 2. Medical History (from app)
- Diagnosis (anxiety, depression, etc.)
- Medications (names, dosages)
- Medication side effects mentioned
- Clinician's name
- Last appointment date/outcomes

### 3. Behavioral Patterns
- What triggers mood changes
- What helps them feel better
- Sleep patterns
- Exercise habits
- Social patterns
- CBT homework progress

### 4. Conversation Themes
- What they talk about most
- Recurring worries/thoughts
- Progress made on issues
- Current struggles
- Past issues (resolved vs ongoing)

### 5. Risk Monitoring
- Any mention of self-harm
- Any mention of suicidal thoughts
- Crisis moments
- Escalating language patterns
- Warning signs unique to this person

### 6. Engagement Metrics
- How often they use app
- Which features they use most
- Wellness ritual completion
- Therapy chat frequency
- Recovery patterns

### 7. APP ACTIVITY LOG (COMPREHENSIVE) ← CRITICAL
- **Login times**: Every time they access app
- **Logout times**: When they leave
- **Session duration**: How long they stay
- **Feature access**: Which tab they click and in what order
- **Button clicks**: Every interaction
- **Entry timestamps**: When they save data
- **Time gaps**: How long between visits
- **Entry volume**: How much they write
- **Message patterns**: How they communicate
- **Feature abandonment**: Started feature but didn't complete
- **Error states**: Any failed interactions
- **Device/browser**: How they're accessing
- **Location data**: If available (time zone changes)
- **Engagement quality**: Are entries thoughtful or rushed?

---

## PART 8: SPECIAL FEATURES TO ADD

### 1. Conversation Context Injection
```
When AI detects a pattern:
"You mentioned work stress is worse when you skip sleep - 
I've noticed this pattern before too [specific dates]. 
Should we focus on your sleep tonight?"
```

### 2. Progress Celebration
```
"It's been 30 days since you last reported self-harm thoughts. 
You're using your coping strategies really well. 
That takes real strength."
```

### 3. Clinician Integration Point
```
After each appointment, clinician can:
- Record session notes → AI incorporates into memory
- Update treatment plan → AI references in conversations
- Mark progress on goals → AI tracks and celebrates
```

### 4. Early Warning System
```
If flags are detected:
- Clinician gets notified (via dashboard)
- Patient gets gentle check-in from AI
- Escalation path to crisis resources if needed
- No false alarms - only significant patterns
```

### 5. Personalized Insights
```
AI proactively asks questions based on patterns:
"Your mood usually improves on days you exercise. 
You haven't exercised in 3 days - want to go for that walk?"

"You mentioned work stress last week and had poor sleep. 
How's work today? Let's check in."
```

---

## PART 9: DATA PRIVACY & ETHICS

### Patient Controls:
- Patient can request memory deletion (right to be forgotten)
- Patient can see everything the AI knows
- Patient can correct misinterpretations
- Patient can mark things as "private" (not shared with clinician)
- Clear consent that memory is shared with clinician

### Clinician Controls:
- Can only see their own patients' summaries
- Can see flagged concerns
- Cannot modify patient memory (can only note in appointment)
- Summary is read-only (for assessment)

### Data Security:
- Memory stored encrypted
- Regular backups
- Audit log of who accessed what
- GDPR compliance for deletion requests

---

## PART 10: IMPLEMENTATION QUESTIONS

Questions to answer before building:

### 1. Memory Retention
- How far back to keep detailed conversation history? **(suggest: 1 year)**
- How far back for patterns? **(suggest: 2+ years)**
- Archive old data or delete after X years?

### 2. Update Frequency
- Real-time after each interaction (best) or batch daily?
- Performance impact on chat response time?

### 3. Clinician Access
- Should clinician see full conversations or just summary?
- Should clinician be able to see real-time updates or only monthly?
- Should clinician get alerts for critical flags?

### 4. Patient Transparency
- Should patients know exactly when AI is using memory?
- Should they see the memory update in real-time?
- How much detail in the "My Memory" view?

### 5. AI Safety
- How to prevent AI from over-indexing on old problems?
- How to handle conflicting information (patient said X but later Y)?
- How to validate pattern detection is accurate?

### 6. Escalation
- What flags trigger clinician notification?
- What flags trigger immediate crisis response?
- How to integrate with crisis hotline if needed?

---

## SUMMARY

This system transforms the AI from a "stateless chatbot" to a true **therapeutic partner** that:

✅ **Remembers everything** (auto-save after each interaction)
✅ **Understands patterns** (automatically detects behavioral trends)
✅ **Provides continuity** (references past conversations naturally)
✅ **Enables clinicians** (monthly summaries with actionable insights)
✅ **Empowers patients** (see their progress, clarify misunderstandings)
✅ **Catches risks early** (pattern-based warning system)
✅ **Celebrates progress** (acknowledges growth over time)
✅ **Tracks EVERYTHING** (login/logout, features, buttons, data entry - nothing is too small)

### The key principle:
The app becomes a **complete mental health companion** that works together with the clinician, not against them. The AI does the continuous monitoring and support, the clinician does the monthly deep-dive and treatment adjustments.

---

## PART 11: COMPREHENSIVE ACTIVITY TRACKING (NEW SECTION)

### Why Track EVERYTHING?

The AI can only help if it sees the **complete picture**. A patient might say "I'm fine" but their behavior tells the truth:
- Haven't logged mood in 5 days (avoidance)
- Using app only at 3am (insomnia/anxiety)
- Clicking crisis features but not reaching out (silent struggle)
- Abandoned wellness ritual (relapse indicator)
- Messages getting shorter (deterioration)
- Accessing app 10x but not messaging (avoidance)

**These patterns are invisible without comprehensive tracking.**

### What to Track

**Every Login/Logout:**
```
2026-02-06 15:23:14 - LOGIN (session_5487)
2026-02-06 15:23:45 - FEATURE_ACCESS: Therapy Chat
2026-02-06 15:24:02 - BUTTON_CLICK: "Send Message"
2026-02-06 15:24:03 - MESSAGE_SENT: "Had a rough day at work"
2026-02-06 15:26:15 - FEATURE_CHANGE: to Wellness Ritual
2026-02-06 15:31:22 - BUTTON_CLICK: "Save Entry"
2026-02-06 15:31:23 - DATA_SAVED: mood=5, sleep=6, exercise=no
2026-02-06 15:32:01 - LOGOUT (session_5487)
Result: 8 minute session, 2 features, completed both interactions
```

**Every 24 Hours, Generate Daily Summary:**
```
DATE: 2026-02-06
Sessions: 3 (15:23-15:32, 18:15-18:47, 23:45-23:58)
Total time: 34 minutes
Features used: [Therapy Chat 2x, Wellness Ritual 1x]
Data entered: [mood, sleep]
Messages sent: 1
Engagement: Normal
Patterns: Used app at 3 different times (morning, evening, late night - late night is unusual)
Concerns: Late night session at 23:45 (insomnia indicator?)
```

**Weekly Pattern Analysis:**
```
WEEK OF: 2026-02-01 to 2026-02-07

LOGIN FREQUENCY:
- Expected: 5-7 days/week (based on history)
- Actual: 6 days/week ✓
- Unusual: None

TIME OF DAY PATTERN:
- Morning (6-12am): 2 logins
- Afternoon (12-6pm): 8 logins (most frequent)
- Evening (6pm-midnight): 6 logins
- Night (midnight-6am): 1 login ⚠️ (new pattern)

FEATURE USAGE:
- Therapy Chat: 12 interactions (60%)
- Wellness Ritual: 5 interactions (25%)
- Mood Logging: 3 interactions (15%)
- Feature abandoned: None ✓

ENGAGEMENT QUALITY:
- Message length: Avg 28 words (normal)
- Entry completeness: 100% of entries have all fields ✓
- Response time: Avg 2 min to AI response (normal)
- Bounce rate: 0 abandonment ✓

TREND ANALYSIS:
- Engagement: ↗ Slightly up (+5%)
- Mood: ↗ Improving (5.1 → 5.8)
- Sleep: ↗ Better (6.2 → 6.8 hours)
- Consistency: ✓ Excellent

FLAGS: None currently

ACTION: Continue current pattern, monitor late-night usage
```

### What This Enables for AI

**Example Conversation with Full Tracking:**
```
Patient logs in at 2:47am (unusual for them)
AI sees: "This person usually uses app at 3pm, never at 2am before. They're here now."

Patient: "Can't sleep"

AI (with full memory):
"You're up late - that's not typical for you. You've been sleeping better 
this week (6.8 hours average). What changed tonight? Is this anxiety about 
something specific, or just a rough night?"

Patient: "Work stress about tomorrow"

AI:
"You mentioned work stress 4 times this week - that seems elevated. 
Last time you had this pattern [date], it lasted 3 days and resolved 
when you talked to your boss. Want to try that approach again?"

Patient: "Maybe. But I also haven't exercised in 5 days"

AI:
"Yeah, I noticed - your mood usually improves after exercise (87% correlation). 
You did 3x last week, nothing this week. When work gets stressful, exercise 
helps you more than anything else. Should we plan a walk for tomorrow morning, 
before work?"
```

**This is only possible because AI sees:**
- ✓ It's 2am (unusual)
- ✓ Sleep quality has been improving
- ✓ This is 4th work stress mention this week
- ✓ Historical pattern when stressed
- ✓ No exercise in 5 days (vs typical 3x/week)
- ✓ Mood-exercise correlation data
- ✓ What works for THIS person

### Implementation Checklist

For complete activity tracking to work:

**Frontend (JavaScript):**
- [ ] Log every page/tab load
- [ ] Log every button click with context
- [ ] Log message send/receive
- [ ] Log form submissions
- [ ] Log session start/end (login/logout)
- [ ] Log time spent per feature
- [ ] Log error states
- [ ] Send activity logs to backend in batches (every 5 min or on logout)

**Backend (Python):**
- [ ] Create `ai_activity_log` table
- [ ] Create activity logging endpoint: `POST /api/activity/log`
- [ ] Process incoming activity batch
- [ ] Link activities to user sessions
- [ ] Nightly batch process activities into `ai_memory_events`
- [ ] Generate daily/weekly summaries from activities
- [ ] Detect anomalies (unusual patterns)
- [ ] Trigger alerts for concerning patterns

**Database:**
- [ ] `ai_activity_log` table with proper indexing
- [ ] Retention policy (keep 12 months of detailed logs)
- [ ] Archive/compress older logs
- [ ] Query optimization for pattern analysis

**AI Integration:**
- [ ] Modify system prompt to include activity context
- [ ] Teach AI to reference patterns naturally
- [ ] Enable proactive outreach based on patterns
- [ ] Integrate anomaly flags into responses

### Privacy Note

All activity is tracked server-side, encrypted, and:
- Only visible to patient and their clinician
- Can be deleted per GDPR right to erasure
- Is explained to patient at signup ("We track your app usage to help the AI understand you better")
- Does NOT track content of messages or personal data beyond what they enter

---

## PART 12: AUTO-DISCOVERY OF NEW FEATURES

### Principle: Zero-Config AI Memory Integration

When a developer adds ANY new feature, tab, endpoint, or interactive element to the patient dashboard, the AI memory system MUST automatically detect and incorporate it — with ZERO manual wiring required.

### How It Works

**1. Frontend Auto-Detection (activity-logger.js already handles this):**

The `ActivityLogger` class tracks ALL button clicks, tab changes, and form submissions globally via DOM event listeners. This means:
- **New tab added?** → `switchTab()` dispatches a `tabchange` event → ActivityLogger logs it automatically
- **New button added?** → Any `<button>` click is captured by the global click handler → logged automatically
- **New form/save action?** → If it uses a `<button>` or dispatches a custom event → logged automatically

No changes to `activity-logger.js` are needed when new features are added.

**2. Backend Auto-Detection (update_ai_memory already handles this):**

The `update_ai_memory()` function in `api.py` dynamically queries ALL data tables the user has interacted with. When a new table is added:
- If the new endpoint calls `log_event()` → it appears in audit_logs → AI sees it
- If the new endpoint saves to ANY table with a `username` column → the nightly pattern detection can query it
- If the new feature sends data via `/api/ai/memory/update` with a new `event_type` → it flows into `ai_memory_events` automatically

**3. The Auto-Discovery Contract:**

When building ANY new patient feature, the developer MUST follow these rules:

```
RULE 1: USE EXISTING ACTIVITY LOGGING
  - Frontend: Use standard <button> elements (ActivityLogger captures them)
  - Frontend: If adding a new tab, use switchTab() (tabchange event fires automatically)
  - Frontend: For significant saves, add one line:
    activityLogger.logActivity('feature_name_saved', 'metadata', 'tab_name');

RULE 2: LOG TO AI MEMORY ON SAVE
  - Backend: After saving new data, call:
    log_therapy_interaction_to_memory(conn, cur, username, data_summary, '')
    OR insert directly into ai_memory_events:
    cur.execute("INSERT INTO ai_memory_events (username, event_type, event_data, severity) VALUES (%s, %s, %s, 'normal')",
                (username, 'new_feature_name', json.dumps(event_data)))

RULE 3: INCLUDE IN update_ai_memory()
  - Add a query for the new table to the update_ai_memory() function
  - This ensures the AI's text memory_summary includes the new data
  - Pattern: fetch recent entries → summarize → append to memory_parts[]

RULE 4: ADD TO PATTERN DETECTION (if applicable)
  - If the feature produces data that could indicate risk or patterns,
    add a detection function in detect_patterns_endpoint()
  - Example: "journaling_abandonment" if user stops using a new journal feature
```

**4. What Happens Automatically (No Code Changes Needed):**

| New Feature Added | What AI Memory Sees Automatically |
|---|---|
| New tab in dashboard | Tab change logged, feature_access recorded |
| New button anywhere | Button click logged with label text |
| New save/submit action | Form submit or button click logged |
| New data entry form | ActivityLogger captures the interaction |
| New API endpoint called | If it uses log_event(), audit trail created |

**5. What Requires ONE Line of Code:**

| New Feature Added | One Line to Add |
|---|---|
| New data saved to DB | `activityLogger.logActivity('feature_saved', 'metadata', 'tab');` in frontend |
| New significant event | `INSERT INTO ai_memory_events` in the backend endpoint |
| New data table queried by AI | Add query block in `update_ai_memory()` function |

**6. What Requires a Small Block of Code:**

| New Feature Added | Code to Add |
|---|---|
| New pattern to detect | Add detection function in nightly batch job |
| New risk flag type | Add to `check_event_for_flags()` keyword lists |
| New clinician summary metric | Add query in `generate_single_summary()` |

### Example: Adding a "Gratitude Journal V2" Feature

```
Step 1: Create the feature (new tab, new endpoint, new table)
Step 2: Frontend already auto-tracks tab switches and button clicks ✓
Step 3: In the save endpoint, add ONE insert to ai_memory_events:
        cur.execute("INSERT INTO ai_memory_events (username, event_type, event_data) VALUES (%s, 'gratitude_v2', %s)", (username, json.dumps(data)))
Step 4: In update_ai_memory(), add a query:
        recent_gratitude_v2 = cur.execute("SELECT ... FROM gratitude_v2 WHERE username = %s ORDER BY ... LIMIT 5", (username,)).fetchall()
        if recent_gratitude_v2:
            memory_parts.append(f"Gratitude V2: {len(recent_gratitude_v2)} entries")
Step 5: Done. AI now knows about gratitude entries, tracks engagement,
        and can reference them in conversations.
```

### The Golden Rule

> **If a patient can interact with it, the AI must know about it.**
> The system is designed so that 90% of tracking happens automatically.
> The remaining 10% requires at most 3-5 lines of code per new feature.

---

## NEXT STEPS

Ready to proceed with implementation? Start with Phase 1 (database infrastructure)?
