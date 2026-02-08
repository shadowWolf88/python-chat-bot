# WINS BOARD - STRENGTHS-BASED MICRO-LOGGING
## Implementation Prompt (Section 2 of Patient Engagement Strategy)

---

## CONTEXT & GOALS

**Feature Goal:** Create a celebratory "Wins Board" where patients log small daily wins and achievements — retraining their brain to notice agency, resilience, and self-efficacy instead of focusing on deficits.

**Why This Matters Clinically:**
- Mental health apps over-index on problems ("How are you struggling?"), reinforcing a deficit model
- Patients internalize "I'm broken" when every interaction is about what's wrong
- Strengths-based approaches (positive psychology) show that noticing wins builds resilience
- The AI needs positive signals, not just pathology, to understand the whole patient
- Clinicians need to see resilience patterns alongside risk patterns

**Technical Stack:**
- Backend: Python Flask with PostgreSQL (psycopg2)
- Frontend: JavaScript (ES6+) single-page app in `templates/index.html`
- AI: Groq API (llama-3.3-70b-versatile) via TherapistAI class
- Auth: `get_authenticated_username()` (Flask session primary)
- DB: `get_db_connection()` + `get_wrapped_cursor(conn)`
- Existing AI Memory: `ai_memory_events` table, `update_ai_memory()` function, `ActivityLogger` class

**Key Principle:** This is NOT a journal or gratitude log (those exist separately). This is a quick, dopamine-hit, celebratory micro-logger. Think Twitter-length wins, not diary entries.

---

## PHASE 1: DATABASE

### 1.1 Create `patient_wins` Table

```sql
CREATE TABLE IF NOT EXISTS patient_wins (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    win_type TEXT NOT NULL,
    win_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_wins_username ON patient_wins(username);
CREATE INDEX IF NOT EXISTS idx_wins_created ON patient_wins(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_wins_user_date ON patient_wins(username, created_at DESC);
```

**win_type values:** `had_a_laugh`, `self_care`, `kept_promise`, `tried_new`, `stood_up`, `got_outside`, `helped_someone`, `custom`

### 1.2 Migration Strategy

Add to `init_db()` using the unconditional migration pattern (check if table exists, create if not). Place alongside the existing wellness_logs and AI memory table migrations.

---

## PHASE 2: BACKEND API

### 2.1 POST /api/wins/log

Log a new win. One win per call.

```
Request:
{
    "win_type": "got_outside",
    "win_text": "Walked to the park even though it was raining"
}

Response (201):
{
    "success": true,
    "win_id": 42,
    "message": "Win logged!"
}
```

**Implementation details:**
- Auth required via `get_authenticated_username()`
- Validate `win_type` is one of the allowed values
- Validate `win_text` is 1-500 characters
- After insert: log to `ai_memory_events` with event_type `'win_logged'`
- After insert: call `update_ai_memory(username)` to refresh AI memory summary
- After insert: call `mark_daily_task_complete(username, 'log_win')` if that function exists

### 2.2 GET /api/wins/recent

Get recent wins for the logged-in user.

```
Request: GET /api/wins/recent?limit=20

Response (200):
{
    "wins": [
        {
            "id": 42,
            "win_type": "got_outside",
            "win_text": "Walked to the park even though it was raining",
            "created_at": "2026-02-06T14:30:00"
        }
    ],
    "total_count": 15,
    "this_week_count": 5
}
```

### 2.3 GET /api/wins/stats

Get win statistics for clinician dashboard and AI context.

```
Request: GET /api/wins/stats?username=patient1

Response (200):
{
    "total_wins": 47,
    "this_week": 5,
    "last_week": 3,
    "trend": "improving",
    "top_types": [
        {"type": "got_outside", "count": 12},
        {"type": "self_care", "count": 9}
    ],
    "streak_days": 3
}
```

**Note:** This endpoint should also work for clinicians viewing patient data (verify clinician-patient relationship via `patient_approvals`).

---

## PHASE 3: FRONTEND

### 3.1 Home Tab - Wins Board Card

Place AFTER the Daily Wellness Ritual card and BEFORE the Daily Tasks card on the home tab.

**HTML Structure:**
```html
<div id="winsBoardCard" class="card home-wins-card" style="margin-top: 20px;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
        <h3 style="margin: 0;">🏆 Wins Board</h3>
        <span id="winsWeekCount" style="background: var(--primary-color); color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85em;">0 this week</span>
    </div>

    <!-- Quick Win Buttons (preset suggestions) -->
    <div id="winsPresets" style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px;">
        <!-- Rendered dynamically -->
    </div>

    <!-- Custom Win Input -->
    <div style="display: flex; gap: 8px;">
        <input type="text" id="customWinInput" class="wellness-text-input"
               placeholder="+ What went well today?" maxlength="500"
               style="flex: 1; min-width: 0;">
        <button class="btn btn-primary" onclick="logCustomWin()"
                style="white-space: nowrap;">Add Win</button>
    </div>

    <!-- Recent Wins Display -->
    <div id="recentWinsList" style="margin-top: 15px; max-height: 200px; overflow-y: auto;">
        <!-- Rendered dynamically -->
    </div>
</div>
```

### 3.2 Preset Win Buttons

Render these as clickable chips/pills:

```javascript
const WIN_PRESETS = [
    { type: 'had_a_laugh', emoji: '😄', label: 'Had a laugh' },
    { type: 'self_care', emoji: '💆', label: 'Did something kind for myself' },
    { type: 'kept_promise', emoji: '🤝', label: 'Kept a promise' },
    { type: 'tried_new', emoji: '🌟', label: 'Tried something new' },
    { type: 'stood_up', emoji: '💪', label: 'Stood up for myself' },
    { type: 'got_outside', emoji: '🌳', label: 'Got outside' },
    { type: 'helped_someone', emoji: '❤️', label: 'Helped someone' }
];
```

Each preset button:
- On click: prompts for optional detail text (or logs immediately with preset label)
- Shows brief celebratory feedback ("Win logged! 🎉")
- Animates into the recent wins list

### 3.3 Recent Wins Display

Show wins as a compact timeline:
```
🌳 Got outside - "Walked to the park" - 2 hours ago
💪 Stood up for myself - "Said no to overtime" - Yesterday
😄 Had a laugh - Today
```

### 3.4 JavaScript Functions

```javascript
// Load and render wins on home tab
async function loadWinsBoard()

// Log a preset win (type + optional custom text)
async function logPresetWin(winType, defaultText)

// Log a custom win from the text input
async function logCustomWin()

// Render recent wins in the list
function renderRecentWins(wins)

// Show celebratory feedback
function showWinCelebration(winText)
```

### 3.5 Integration Points

- Call `loadWinsBoard()` in `loadHomeTabData()` or after home tab renders
- Call `loadWinsBoard()` when switching to home tab in `switchTab()`
- Log to ActivityLogger: `activityLogger.logActivity('win_logged', winType, 'home')`

---

## PHASE 4: AI MEMORY INTEGRATION

### 4.1 Log Wins to AI Memory Events

After each win is logged, insert into `ai_memory_events`:
```python
cur.execute("""
    INSERT INTO ai_memory_events (username, event_type, event_data, severity)
    VALUES (%s, 'win_logged', %s, 'normal')
""", (username, json.dumps({
    'win_type': win_type,
    'win_text': win_text,
    'timestamp': datetime.now().isoformat()
})))
```

### 4.2 Update AI Memory Summary

In the existing `update_ai_memory()` function, add a query for recent wins:
```python
# Recent wins
recent_wins = cur.execute("""
    SELECT win_type, win_text, created_at FROM patient_wins
    WHERE username = %s ORDER BY created_at DESC LIMIT 5
""", (username,)).fetchall()
if recent_wins:
    wins_text = '; '.join([f"{w[0]}: {w[1]}" for w in recent_wins])
    memory_parts.append(f"Recent wins: {wins_text}")
```

### 4.3 AI Context Enhancement

The TherapistAI should reference wins naturally:
- "I see you got outside today even though it was raining — that takes real effort"
- "You've logged 5 wins this week, up from 3 last week — you're noticing more good things"
- "You mentioned standing up for yourself yesterday — how did that feel?"

---

## PHASE 5: CLINICIAN VISIBILITY

### 5.1 Patient Detail View

Add wins data to the `/api/professional/patient/<username>` endpoint response:
```python
# Patient wins (last 30 days)
wins = cur.execute("""
    SELECT win_type, win_text, created_at FROM patient_wins
    WHERE username = %s AND created_at > CURRENT_TIMESTAMP - INTERVAL '30 days'
    ORDER BY created_at DESC
""", (username,)).fetchall()
```

Include in the response JSON as `'recent_wins'`.

### 5.2 Clinician Dashboard Display

In the AI summary for clinician, include:
- "5 wins this week (avg 2.3/week previously) — Patient showing increased self-awareness and agency"
- Top win types: shows what the patient celebrates most
- Trend: increasing/decreasing/stable

---

## STYLING

Use existing `.card` class with theme variables. Win preset buttons should use:
```css
.win-preset-btn {
    padding: 8px 16px;
    border-radius: 20px;
    border: 2px solid var(--primary-color);
    background: transparent;
    color: var(--text-color);
    cursor: pointer;
    font-size: 0.9em;
    transition: all 0.2s;
}
.win-preset-btn:hover {
    background: var(--primary-color);
    color: white;
}
```

Individual win entries in the timeline:
```css
.win-entry {
    padding: 10px 0;
    border-bottom: 1px solid var(--border-color);
    font-size: 0.95em;
    display: flex;
    align-items: center;
    gap: 8px;
}
.win-entry:last-child {
    border-bottom: none;
}
.win-time {
    color: var(--text-secondary);
    font-size: 0.8em;
    white-space: nowrap;
}
```

---

## SUCCESS CRITERIA

When complete:
- Patient can log wins from preset buttons or custom text
- Wins appear instantly in the board with celebratory feedback
- AI references wins in therapy conversations naturally
- Clinician sees wins in patient detail view
- Weekly count badge updates in real-time
- Activity logging captures win events
- AI memory includes recent wins context
- No breaking changes to existing functionality

---

## AUTO-DISCOVERY

This feature follows the auto-discovery contract:
- Frontend: Uses standard `<button>` elements → ActivityLogger captures clicks automatically
- Backend: Logs to `ai_memory_events` → AI memory system picks it up
- Memory: Added to `update_ai_memory()` → appears in AI context
- Pattern detection: Win frequency trends can be monitored by nightly batch job
