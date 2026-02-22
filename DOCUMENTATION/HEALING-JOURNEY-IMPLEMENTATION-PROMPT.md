# HEALING JOURNEY IMPLEMENTATION PROMPT
## The Definitive Technical Specification for HJ.1, HJ.2, and HJ.3
### Healing Space UK — World-Class Mental Health Platform
#### Authored: February 22, 2026 | For use by senior full-stack developer or AI system

---

> **To the implementer**: This document is the complete, exhaustive specification for implementing three transformative features of the Healing Journey layer. Every database schema, every endpoint, every UI component, and every line of logic is specified here. Your job is to implement this exactly — no shortcuts, no simplifications. This is the feature that transforms the platform from a clinical tool into something patients genuinely love. Execute with the care that deserves.

---

## CODEBASE CONTEXT (Essential — Read Before Writing Anything)

| Dimension | Detail |
|-----------|--------|
| **Backend** | `api.py` — 24,044 lines, Flask/PostgreSQL/Groq, monolithic |
| **Frontend** | `templates/index.html` — 24,475 lines, monolithic SPA |
| **DB Pattern** | `conn = get_db_connection(); cur = get_wrapped_cursor(conn); conn.commit(); conn.close()` |
| **Auth Pattern** | `username = get_authenticated_username()` → check `None` → `session.get('role')` |
| **CSRF Pattern** | `@CSRFProtection.require_csrf` decorator + frontend `(document.querySelector('meta[name="csrf-token"]') || {}).content || ''` |
| **Error Pattern** | `return handle_exception(e, 'function_name')` |
| **CSS Pattern** | ALL colours via CSS variables: `var(--text-primary)`, `var(--bg-card)`, `var(--accent-color)` — never hardcode |
| **Init DB** | Tables added in `init_db()` function at ~line 3957 in api.py |
| **Theme** | Light/dark themes via `data-theme` on `document.documentElement` |

### Critical Existing Functions to Understand
- `switchTab(tabName, buttonEl)` — line ~14135 in index.html
- `loadHomeTabData()` — line ~7659 in index.html
- `renderCBTToolsDashboard()` — line ~5327 in index.html
- `loadCBTTool(toolId)` — line ~5337 in index.html
- `saveCBTToolData(toolId)` — line ~5361 in index.html

### CBT_TOOLS Array (line 5309) — 15 tools with exact IDs
`CognitiveDistortionsQuiz`, `CoreBeliefsWorksheet`, `ThoughtDefusionExercise`,
`IfThenCopingPlan`, `CopingSkillsSelector`, `SelfCompassionLetter`,
`ProblemSolvingWorksheet`, `ExposureHierarchyBuilder`, `RelaxationAudioPlayer`,
`UrgeSurfingTimer`, `ValuesCardSort`, `StrengthsInventory`,
`SleepHygieneChecklist`, `SafetyPlanBuilder`, `ActivityScheduler`

### Patient Tab Structure (line 4733)
Home, AI Therapy, Mood & Habits, Safety Check, Gratitude, CBT Tools, My Pet,
Assessments, Community, Messages, Insights, Appointments, Medications, Progress,
About Me, History, Updates, Professional (hidden), Developer (hidden)

### Home Tab Structure (lines 4809–4992)
1. Welcome card (4811) — `.home-welcome-card`
2. Wellness ritual container (4825) — `#wellnessRitualContainer`
3. Daily tasks card (4870) — `.home-tasks-card` with streak display
4. Quick navigation (4893) — `.home-quick-nav`
5. Help card (4918) — `.home-help-card`
6. Pet status mini card (4947) — `.home-pet-card`
7. Developer feedback (4962)
8. Crisis resources (4983)

---

## SECTION 1: HJ.1 — THE QUEST SYSTEM

### 1.1 Philosophy
Quests are not gamification gimmicks — they are **reframed therapeutic homework**. Each quest maps directly to a clinical intervention. A patient completing "The Gratitude Grove" is doing exactly what their CBT protocol requires — logging gratitude entries — but they're doing it because they want to see their grove grow, not because they were assigned homework. The clinical outcome is identical; the engagement is transformed.

### 1.2 Database — Two New Tables

#### Table: `quest_definitions`
Add to `init_db()` after the `recovery_milestones` table block (~line 4169 in api.py):

```sql
CREATE TABLE IF NOT EXISTS quest_definitions (
    id SERIAL PRIMARY KEY,
    quest_key TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    subtitle TEXT,
    description TEXT NOT NULL,
    lore_text TEXT,
    quest_type TEXT NOT NULL DEFAULT 'skill',
    category TEXT DEFAULT 'general',
    icon TEXT DEFAULT '⚔️',
    xp_reward INTEGER DEFAULT 50,
    required_count INTEGER DEFAULT 1,
    tracking_metric TEXT,
    duration_days INTEGER,
    auto_assign BOOLEAN DEFAULT TRUE,
    difficulty TEXT DEFAULT 'gentle',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS patient_quests (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    quest_key TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    progress INTEGER DEFAULT 0,
    target INTEGER DEFAULT 1,
    assigned_by TEXT DEFAULT 'system',
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    expires_at TIMESTAMP,
    celebration_shown BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_patient_quests_username ON patient_quests(username);
CREATE INDEX IF NOT EXISTS idx_patient_quests_status ON patient_quests(username, status);
CREATE INDEX IF NOT EXISTS idx_quest_definitions_key ON quest_definitions(quest_key);
```

#### Seed Data — 20 Quest Definitions
After creating the tables, insert seed data (skip if already exists using ON CONFLICT DO NOTHING):

```python
QUEST_SEEDS = [
    # --- DAILY RITUALS ---
    {'quest_key': 'daily_morning_compass', 'title': 'The Morning Compass', 'subtitle': 'Daily Ritual',
     'description': 'Complete your daily wellness check-in to orient yourself for the day ahead.',
     'lore_text': 'Every great journey begins with knowing where you stand.',
     'quest_type': 'daily', 'category': 'ritual', 'icon': '🧭', 'xp_reward': 30,
     'required_count': 1, 'tracking_metric': 'wellness_log', 'duration_days': 1},

    {'quest_key': 'daily_evening_lantern', 'title': 'The Evening Lantern', 'subtitle': 'Daily Ritual',
     'description': 'Log your mood and write one gratitude entry before the day ends.',
     'lore_text': 'Light a lantern in the dark — small moments of brightness matter most.',
     'quest_type': 'daily', 'category': 'ritual', 'icon': '🪔', 'xp_reward': 25,
     'required_count': 1, 'tracking_metric': 'mood_log', 'duration_days': 1},

    # --- SKILL QUESTS ---
    {'quest_key': 'skill_thought_challenger', 'title': 'The Thought Challenger', 'subtitle': '7-Day Skill Quest',
     'description': 'Use any CBT tool 3 times this week to build your mental resilience.',
     'lore_text': 'Thoughts are not facts. Learn to see them clearly.',
     'quest_type': 'skill', 'category': 'cbt', 'icon': '⚡', 'xp_reward': 150,
     'required_count': 3, 'tracking_metric': 'cbt_tool', 'duration_days': 7},

    {'quest_key': 'skill_breathing_stone', 'title': 'The Breathing Stone', 'subtitle': '5-Day Skill Quest',
     'description': 'Practice guided breathing 5 days in a row. Feel the calm settle.',
     'lore_text': 'The breath is the only anchor you carry everywhere.',
     'quest_type': 'skill', 'category': 'cbt', 'icon': '💨', 'xp_reward': 100,
     'required_count': 5, 'tracking_metric': 'cbt_tool:RelaxationAudioPlayer', 'duration_days': 7},

    {'quest_key': 'skill_compass_seeker', 'title': 'The Compass Seeker', 'subtitle': 'Skill Quest',
     'description': 'Complete a Problem Solving exercise when you face a challenge.',
     'lore_text': 'Every problem has a path through it. Find yours.',
     'quest_type': 'skill', 'category': 'cbt', 'icon': '🧭', 'xp_reward': 75,
     'required_count': 1, 'tracking_metric': 'cbt_tool:ProblemSolvingWorksheet', 'duration_days': 14},

    {'quest_key': 'skill_healing_salve', 'title': 'The Healing Salve', 'subtitle': 'Self-Compassion Quest',
     'description': 'Write a Self-Compassion Letter — to yourself, with the kindness you would give a friend.',
     'lore_text': 'Treat yourself with the care you would give to someone you love.',
     'quest_type': 'skill', 'category': 'cbt', 'icon': '💙', 'xp_reward': 110,
     'required_count': 1, 'tracking_metric': 'cbt_tool:SelfCompassionLetter', 'duration_days': 21},

    # --- EXPLORATION QUESTS ---
    {'quest_key': 'explore_gratitude_grove', 'title': 'The Gratitude Grove', 'subtitle': 'Exploration Quest',
     'description': 'Write 7 gratitude entries this week. Each one plants a seed in your grove.',
     'lore_text': 'A grove grows one seed at a time.',
     'quest_type': 'exploration', 'category': 'gratitude', 'icon': '🌿', 'xp_reward': 120,
     'required_count': 7, 'tracking_metric': 'gratitude_log', 'duration_days': 7},

    {'quest_key': 'explore_strength_runes', 'title': 'The Strength Runes', 'subtitle': 'Self-Discovery Quest',
     'description': 'Complete the Strengths Inventory to discover the powers within you.',
     'lore_text': 'Knowing your strengths is the first step to using them.',
     'quest_type': 'exploration', 'category': 'cbt', 'icon': '🔮', 'xp_reward': 80,
     'required_count': 1, 'tracking_metric': 'cbt_tool:StrengthsInventory', 'duration_days': 30},

    {'quest_key': 'explore_true_north', 'title': 'True North', 'subtitle': 'Values Quest',
     'description': 'Complete the Values Card Sort to discover what matters most to you.',
     'lore_text': 'When you know your true north, no storm can disorient you.',
     'quest_type': 'exploration', 'category': 'cbt', 'icon': '⭐', 'xp_reward': 100,
     'required_count': 1, 'tracking_metric': 'cbt_tool:ValuesCardSort', 'duration_days': 30},

    # --- ARC QUESTS (multi-week journeys) ---
    {'quest_key': 'arc_seven_day_dawn', 'title': 'The Seven-Day Dawn', 'subtitle': '7-Day Arc Quest',
     'description': 'Complete your wellness check-in every day for 7 days.',
     'lore_text': 'Seven sunrises. Seven choices to show up for yourself.',
     'quest_type': 'arc', 'category': 'ritual', 'icon': '🌅', 'xp_reward': 300,
     'required_count': 7, 'tracking_metric': 'wellness_log', 'duration_days': 14},

    {'quest_key': 'arc_mood_keeper', 'title': 'The Mood Keeper', 'subtitle': '7-Day Arc Quest',
     'description': 'Log your mood every day for 7 days. Awareness is the first step to change.',
     'lore_text': 'To know where you are going, you must first know where you are.',
     'quest_type': 'arc', 'category': 'mood', 'icon': '📊', 'xp_reward': 200,
     'required_count': 7, 'tracking_metric': 'mood_log', 'duration_days': 14},

    {'quest_key': 'arc_clarity_path', 'title': 'The Clarity Path', 'subtitle': '2-Week Arc Quest',
     'description': 'Use 5 different CBT tools over 2 weeks. Each one is a new skill.',
     'lore_text': 'Five paths forward. Choose them one by one.',
     'quest_type': 'arc', 'category': 'cbt', 'icon': '✨', 'xp_reward': 350,
     'required_count': 5, 'tracking_metric': 'cbt_tool_unique', 'duration_days': 14},

    {'quest_key': 'arc_roots_and_wings', 'title': 'Roots and Wings', 'subtitle': '21-Day Arc Quest',
     'description': 'Complete 21 wellness check-ins. Build the roots that allow you to grow wings.',
     'lore_text': 'Twenty-one days to build a habit. Twenty-one seeds planted.',
     'quest_type': 'arc', 'category': 'ritual', 'icon': '🦋', 'xp_reward': 500,
     'required_count': 21, 'tracking_metric': 'wellness_log', 'duration_days': 28},

    # --- COURAGE QUESTS (clinician-assigned) ---
    {'quest_key': 'courage_safety_shield', 'title': 'The Shield Pact', 'subtitle': 'Courage Quest',
     'description': 'Create or review your Safety Plan — a shield you carry always.',
     'lore_text': 'The bravest thing is knowing where to turn when the storm comes.',
     'quest_type': 'courage', 'category': 'safety', 'icon': '🛡️', 'xp_reward': 200,
     'required_count': 1, 'tracking_metric': 'cbt_tool:SafetyPlanBuilder',
     'duration_days': 30, 'auto_assign': False},

    {'quest_key': 'courage_exposure_steps', 'title': 'The Courage Steps', 'subtitle': 'Courage Quest',
     'description': 'Build your Exposure Hierarchy — map the challenges you will face, step by step.',
     'lore_text': 'Mountains are climbed one step at a time.',
     'quest_type': 'courage', 'category': 'cbt', 'icon': '🏔️', 'xp_reward': 180,
     'required_count': 1, 'tracking_metric': 'cbt_tool:ExposureHierarchyBuilder',
     'duration_days': 30, 'auto_assign': False},

    # --- CONNECTION QUESTS ---
    {'quest_key': 'connect_community_circle', 'title': 'The Circle', 'subtitle': 'Connection Quest',
     'description': 'Post in the community forum or respond to a peer. Connection is medicine.',
     'lore_text': 'No healer walks the path alone.',
     'quest_type': 'connection', 'category': 'community', 'icon': '🌐', 'xp_reward': 100,
     'required_count': 1, 'tracking_metric': 'community_post', 'duration_days': 7},

    # --- BONUS QUESTS ---
    {'quest_key': 'bonus_dream_ward', 'title': 'The Dream Ward', 'subtitle': 'Wellness Quest',
     'description': 'Complete the Sleep Hygiene Checklist to protect your nights.',
     'lore_text': 'Rest is not weakness. It is wisdom.',
     'quest_type': 'skill', 'category': 'wellness', 'icon': '🌙', 'xp_reward': 60,
     'required_count': 1, 'tracking_metric': 'cbt_tool:SleepHygieneChecklist', 'duration_days': 14},

    {'quest_key': 'bonus_wave_rider', 'title': 'The Wave Rider', 'subtitle': 'Urge Quest',
     'description': 'Use the Urge Surfing Timer when an urge arises. Ride it, do not fight it.',
     'lore_text': 'Urges are like waves — they rise, peak, and fall.',
     'quest_type': 'skill', 'category': 'wellness', 'icon': '🏄', 'xp_reward': 70,
     'required_count': 1, 'tracking_metric': 'cbt_tool:UrgeSurfingTimer', 'duration_days': 14},

    {'quest_key': 'bonus_the_arsenal', 'title': 'The Arsenal', 'subtitle': 'Skills Quest',
     'description': 'Use the Coping Skills Selector to build your personal toolkit.',
     'lore_text': 'A healer carries many tools. Know yours.',
     'quest_type': 'skill', 'category': 'cbt', 'icon': '🛠️', 'xp_reward': 65,
     'required_count': 1, 'tracking_metric': 'cbt_tool:CopingSkillsSelector', 'duration_days': 14},

    {'quest_key': 'bonus_if_then_binding', 'title': 'The If-Then Binding', 'subtitle': 'Preparation Quest',
     'description': 'Build your If-Then Coping Plan for the moments when you need it most.',
     'lore_text': 'Prepare your response before the storm hits.',
     'quest_type': 'skill', 'category': 'cbt', 'icon': '🔗', 'xp_reward': 65,
     'required_count': 1, 'tracking_metric': 'cbt_tool:IfThenCopingPlan', 'duration_days': 14},
]
```

### 1.3 Backend Endpoints (6 routes)

#### Route 1: `GET /api/user/quests`
Returns active quests, suggested quests, today's completed, and total XP earned.

```
Response: {
    active: [{id, quest_key, title, subtitle, description, lore_text, icon, quest_type,
               category, progress, target, pct, xp_reward, expires_at, assigned_by,
               assigned_at}],
    completed_today: [{id, quest_key, title, icon, xp_reward, completed_at}],
    suggested: [{quest_key, title, subtitle, description, icon, quest_type, xp_reward,
                  required_count, duration_days, difficulty}],  -- max 4, auto_assign=True, not active
    total_xp: int,
    completed_count: int
}
```

Logic for `suggested`: SELECT from quest_definitions WHERE auto_assign=TRUE AND is_active=TRUE AND quest_key NOT IN (SELECT quest_key FROM patient_quests WHERE username=? AND status IN ('active','completed')) LIMIT 4

#### Route 2: `POST /api/user/quests/accept`
Patient accepts a suggested quest.

```
Request:  { quest_key: "explore_gratitude_grove" }
Response: { success: true, quest_id: 42, message: "Quest accepted!", quest: {...} }
```

Logic: INSERT into patient_quests with status='active', expires_at = NOW() + duration_days * interval, target = required_count. Return 409 if already active.

#### Route 3: `POST /api/user/quests/<int:quest_id>/abandon`
Marks a quest as abandoned (soft delete).

```
Response: { success: true }
```

Auth: verify quest belongs to this user.

#### Route 4: `GET /api/clinician/patient/<patient_username>/quests`
Clinician view of patient quests.

```
Response: { active: [...], completed: [...last 10...], available_to_assign: [...all courage quests...] }
```

#### Route 5: `POST /api/clinician/patient/<patient_username>/quests/assign`
Clinician assigns a specific quest to a patient.

```
Request:  { quest_key: "courage_safety_shield" }
Response: { success: true, quest_id: 55 }
```

Sets `assigned_by` = clinician username. Sends in-app notification to patient.

#### Route 6: Internal Helper `_advance_quest_progress(username, metric, cur, conn)`
**This is the most important function.** Called from existing endpoints to auto-progress quests.

```python
def _advance_quest_progress(username, metric, cur, conn):
    """
    Advances progress for all active patient quests matching the given metric.
    metric examples: 'wellness_log', 'mood_log', 'gratitude_log',
                     'cbt_tool', 'cbt_tool:RelaxationAudioPlayer', 'cbt_tool_unique:ToolId'
    """
    try:
        active_quests = cur.execute("""
            SELECT pq.id, pq.quest_key, pq.progress, pq.target, qd.xp_reward, qd.tracking_metric
            FROM patient_quests pq
            JOIN quest_definitions qd ON pq.quest_key = qd.quest_key
            WHERE pq.username = %s AND pq.status = 'active'
            AND (pq.expires_at IS NULL OR pq.expires_at > NOW())
        """, (username,)).fetchall()

        for quest in active_quests:
            qid, qkey, progress, target, xp, q_metric = quest
            if not q_metric:
                continue

            # Exact match: 'wellness_log' matches 'wellness_log'
            # Prefix match: 'cbt_tool' matches 'cbt_tool:RelaxationAudioPlayer'
            # Specific match: 'cbt_tool:RelaxationAudioPlayer' matches only that tool
            # Unique tool match: 'cbt_tool_unique' — check if this is a new tool for this quest
            matches = False
            if metric == q_metric:
                matches = True
            elif metric.startswith('cbt_tool:') and q_metric == 'cbt_tool':
                matches = True  # Any CBT tool counts for generic 'cbt_tool' metric
            elif metric == q_metric:
                matches = True
            elif q_metric == 'cbt_tool_unique' and metric.startswith('cbt_tool:'):
                # Check if this specific tool already counted for this quest
                tool_id = metric.split(':')[1]
                already = cur.execute("""
                    SELECT COUNT(*) FROM quest_progress_log
                    WHERE quest_id = %s AND event_data = %s
                """, (qid, tool_id)).fetchone()
                # Note: quest_progress_log is a simple log table (id, quest_id, event_data, created_at)
                matches = (already[0] == 0) if already else True

            if not matches:
                continue

            new_progress = progress + 1
            if q_metric == 'cbt_tool_unique' and metric.startswith('cbt_tool:'):
                # Log this unique tool usage
                tool_id = metric.split(':')[1]
                try:
                    cur.execute(
                        "INSERT INTO quest_progress_log (quest_id, event_data) VALUES (%s, %s)",
                        (qid, tool_id)
                    )
                except:
                    pass  # table may not exist yet — graceful degradation

            if new_progress >= target:
                # Complete the quest
                cur.execute("""
                    UPDATE patient_quests SET status='completed', progress=%s,
                    completed_at=NOW() WHERE id=%s
                """, (target, qid))
                # Award XP to pet
                try:
                    cur.execute(
                        "UPDATE pet SET xp = xp + %s WHERE username = %s",
                        (xp, username)
                    )
                except:
                    pass
                # Create milestone for significant quests
                if xp >= 100:
                    try:
                        cur.execute("""
                            INSERT INTO recovery_milestones
                            (username, milestone_type, category, title, description, icon)
                            VALUES (%s, 'quest', 'achievement', %s, %s, %s)
                        """, (username, f"Quest Complete: {qkey}",
                              f"You completed the quest and earned {xp} XP!",
                              "⚔️"))
                    except:
                        pass
            else:
                cur.execute(
                    "UPDATE patient_quests SET progress=%s WHERE id=%s",
                    (new_progress, qid)
                )
        conn.commit()
    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        print(f"Quest progress update error: {e}")
```

#### Hooks — Add `_advance_quest_progress()` calls to these existing endpoints:
1. **After wellness log saved** (`/api/wellness-log/submit`): `_advance_quest_progress(username, 'wellness_log', cur, conn)`
2. **After mood logged** (`/api/mood/log`): `_advance_quest_progress(username, 'mood_log', cur, conn)`
3. **After gratitude saved** (`/api/gratitude`): `_advance_quest_progress(username, 'gratitude_log', cur, conn)`
4. **After CBT tool saved** (`/api/cbt-tools/save`): `_advance_quest_progress(username, f'cbt_tool:{tool_type}', cur, conn)`

Also add a helper `quest_progress_log` table:
```sql
CREATE TABLE IF NOT EXISTS quest_progress_log (
    id SERIAL PRIMARY KEY,
    quest_id INTEGER NOT NULL,
    event_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 1.4 Frontend — Quest Board

**Location**: Replace the `.home-tasks-card` section (lines 4870–4890 in index.html) with the Quest Board. Keep streak display. Keep the wellness ritual button.

**Quest Board HTML structure**:
```html
<!-- Quest Board -->
<div class="card quest-board-card" id="questBoardCard" style="margin-top: 20px;">
    <div class="quest-board-header">
        <div style="display:flex; align-items:center; gap:10px;">
            <span style="font-size:1.8em;">⚔️</span>
            <div>
                <h3 style="margin:0;">Your Quest Board</h3>
                <p style="margin:0; color:var(--text-secondary); font-size:0.85em;">
                    <span id="questXpTotal">0</span> XP earned · <span id="questCompletedCount">0</span> quests completed
                </p>
            </div>
        </div>
        <button onclick="showQuestAcceptModal()" class="btn btn-primary" style="padding:8px 16px; font-size:0.9em;">
            + Accept Quest
        </button>
    </div>

    <!-- Streak display (kept from original) -->
    <div class="streak-display" id="streakDisplay" style="margin: 12px 0;">
        <span class="streak-icon">🔥</span>
        <span class="streak-count" id="streakCount">0</span> day streak
    </div>

    <!-- Active Quests -->
    <div id="activeQuestsList">
        <p style="color:var(--text-muted); font-size:0.9em; text-align:center; padding:20px;">
            Loading your quests...
        </p>
    </div>
</div>

<!-- Quest Accept Modal -->
<div id="questAcceptModal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.7);
     z-index:9000; display:flex; align-items:center; justify-content:center; padding:20px;" onclick="hideQuestModal(event)">
    <div style="background:var(--bg-card); border-radius:16px; padding:28px; max-width:600px; width:100%;
                max-height:80vh; overflow-y:auto; box-shadow:0 20px 60px rgba(0,0,0,0.5);" onclick="event.stopPropagation()">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
            <h3 style="margin:0;">⚔️ Choose Your Quest</h3>
            <button onclick="document.getElementById('questAcceptModal').style.display='none'"
                    style="background:none; border:none; font-size:1.5em; cursor:pointer; color:var(--text-muted);">×</button>
        </div>
        <div id="suggestedQuestsList">Loading available quests...</div>
    </div>
</div>

<!-- Quest Completion Celebration -->
<div id="questCelebration" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.8);
     z-index:9999; align-items:center; justify-content:center; padding:20px; flex-direction:column;">
    <div style="text-align:center; color:white;">
        <div id="questCelebrationIcon" style="font-size:5em; margin-bottom:20px;">⚔️</div>
        <h2 id="questCelebrationTitle" style="font-size:2em; margin-bottom:10px;">Quest Complete!</h2>
        <p id="questCelebrationLore" style="font-style:italic; color:rgba(255,255,255,0.8); margin-bottom:15px;"></p>
        <p id="questCelebrationXP" style="font-size:1.3em; color:#fbbf24; font-weight:700;"></p>
        <button onclick="document.getElementById('questCelebration').style.display='none'"
                class="btn btn-primary" style="margin-top:20px;">Continue →</button>
    </div>
</div>
```

**Quest JavaScript functions** (add near `loadHomeTabData` ~line 7659):

```javascript
// ============ QUEST SYSTEM ============
async function loadQuestBoard() {
    try {
        const resp = await fetch('/api/user/quests', { credentials: 'include' });
        if (!resp.ok) return;
        const data = await resp.json();

        // Update XP + count
        document.getElementById('questXpTotal').textContent = data.total_xp || 0;
        document.getElementById('questCompletedCount').textContent = data.completed_count || 0;

        // Render active quests
        renderActiveQuests(data.active || []);

        // Store suggested for modal
        window._suggestedQuests = data.suggested || [];

        // Check for newly completed quests to celebrate
        if (data.active && data.active.some(q => q.just_completed)) {
            const jc = data.active.find(q => q.just_completed);
            showQuestCelebration(jc);
        }
    } catch (e) {
        console.error('Quest board load error:', e);
    }
}

function renderActiveQuests(quests) {
    const el = document.getElementById('activeQuestsList');
    if (!quests.length) {
        el.innerHTML = `
            <div style="text-align:center; padding:20px; color:var(--text-muted);">
                <p style="font-size:1.1em;">No active quests.</p>
                <p style="font-size:0.9em;">Accept a quest above to begin your journey.</p>
            </div>`;
        return;
    }

    const questTypeColor = {
        daily: '#10b981', skill: '#6366f1', exploration: '#f59e0b',
        arc: '#8b5cf6', courage: '#ef4444', connection: '#06b6d4'
    };

    el.innerHTML = quests.slice(0, 4).map(q => {
        const pct = Math.round((q.progress / q.target) * 100);
        const daysLeft = q.expires_at ?
            Math.max(0, Math.ceil((new Date(q.expires_at) - Date.now()) / 86400000)) : null;
        const typeColor = questTypeColor[q.quest_type] || '#6366f1';

        return `
        <div class="quest-item" style="border:1.5px solid var(--border-color); border-radius:12px;
             padding:16px; margin-bottom:12px; background:var(--bg-secondary); position:relative;
             border-left:4px solid ${typeColor};">
            <div style="display:flex; align-items:flex-start; gap:12px;">
                <span style="font-size:2em; flex-shrink:0;">${q.icon}</span>
                <div style="flex:1; min-width:0;">
                    <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                        <strong style="font-size:1em;">${q.title}</strong>
                        <span style="font-size:0.75em; padding:2px 8px; border-radius:10px;
                               background:${typeColor}22; color:${typeColor}; font-weight:600;">
                            ${q.subtitle || q.quest_type}
                        </span>
                    </div>
                    <p style="color:var(--text-secondary); font-size:0.85em; margin:4px 0 8px 0; line-height:1.4;">
                        ${q.description}
                    </p>
                    ${q.lore_text ? `<p style="color:var(--text-muted); font-size:0.8em; font-style:italic; margin:0 0 8px 0;">"${q.lore_text}"</p>` : ''}
                    <!-- Progress bar -->
                    <div style="background:var(--border-color); border-radius:4px; height:8px; margin-bottom:6px; overflow:hidden;">
                        <div style="width:${pct}%; background:${typeColor}; height:100%; border-radius:4px;
                                    transition:width 0.5s ease;"></div>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:0.8em; color:var(--text-muted);">
                        <span>${q.progress} / ${q.target} ${q.progress >= q.target ? '✅' : ''}</span>
                        <span style="display:flex; gap:10px;">
                            <span style="color:#fbbf24;">+${q.xp_reward} XP</span>
                            ${daysLeft !== null ? `<span>${daysLeft}d left</span>` : ''}
                        </span>
                    </div>
                </div>
                <button onclick="abandonQuest(${q.id})" title="Abandon quest"
                        style="background:none; border:none; cursor:pointer; color:var(--text-muted);
                               font-size:0.8em; flex-shrink:0; padding:4px;">✕</button>
            </div>
        </div>`;
    }).join('') + (quests.length > 4 ? `<p style="text-align:center; color:var(--text-muted); font-size:0.85em;">${quests.length - 4} more active quests</p>` : '');
}

async function showQuestAcceptModal() {
    document.getElementById('questAcceptModal').style.display = 'flex';
    const el = document.getElementById('suggestedQuestsList');

    if (window._suggestedQuests && window._suggestedQuests.length) {
        renderSuggestedQuests(window._suggestedQuests);
    } else {
        el.innerHTML = '<p style="text-align:center; color:var(--text-muted); padding:30px;">All available quests are already active or completed. Check back soon!</p>';
    }
}

function hideQuestModal(e) {
    if (e.target === document.getElementById('questAcceptModal')) {
        document.getElementById('questAcceptModal').style.display = 'none';
    }
}

function renderSuggestedQuests(quests) {
    const el = document.getElementById('suggestedQuestsList');
    const questTypeColor = {
        daily: '#10b981', skill: '#6366f1', exploration: '#f59e0b',
        arc: '#8b5cf6', courage: '#ef4444', connection: '#06b6d4'
    };
    el.innerHTML = quests.map(q => {
        const typeColor = questTypeColor[q.quest_type] || '#6366f1';
        const durationText = q.duration_days === 1 ? 'Daily reset' :
            q.duration_days ? `${q.duration_days} days to complete` : 'No time limit';
        return `
        <div style="border:1.5px solid var(--border-color); border-radius:12px; padding:16px;
             margin-bottom:12px; border-left:4px solid ${typeColor}; background:var(--bg-secondary);">
            <div style="display:flex; align-items:flex-start; gap:12px;">
                <span style="font-size:2.2em;">${q.icon}</span>
                <div style="flex:1;">
                    <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-bottom:4px;">
                        <strong>${q.title}</strong>
                        <span style="font-size:0.75em; padding:2px 8px; border-radius:10px;
                               background:${typeColor}22; color:${typeColor}; font-weight:600;">
                            ${q.subtitle || q.quest_type}
                        </span>
                    </div>
                    <p style="color:var(--text-secondary); font-size:0.85em; margin:4px 0 8px 0;">${q.description}</p>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:0.8em; color:var(--text-muted);">
                            Goal: ${q.required_count}x · ${durationText}
                        </span>
                        <div style="display:flex; gap:8px; align-items:center;">
                            <span style="color:#fbbf24; font-size:0.85em; font-weight:600;">+${q.xp_reward} XP</span>
                            <button onclick="acceptQuest('${q.quest_key}', this)"
                                    class="btn btn-primary" style="padding:6px 14px; font-size:0.85em;">
                                Accept
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>`;
    }).join('');
}

async function acceptQuest(questKey, btnEl) {
    if (btnEl) { btnEl.disabled = true; btnEl.textContent = '...'; }
    try {
        const resp = await fetch('/api/user/quests/accept', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json',
                       'X-CSRF-Token': CSRF_TOKEN() },
            body: JSON.stringify({ quest_key: questKey })
        });
        const data = await resp.json();
        if (data.success) {
            document.getElementById('questAcceptModal').style.display = 'none';
            loadQuestBoard();
            showToast('⚔️ Quest accepted! Your journey begins.', 'success');
        } else {
            if (btnEl) { btnEl.disabled = false; btnEl.textContent = 'Accept'; }
            showToast(data.error || 'Could not accept quest.', 'error');
        }
    } catch (e) {
        if (btnEl) { btnEl.disabled = false; btnEl.textContent = 'Accept'; }
    }
}

async function abandonQuest(questId) {
    if (!confirm('Abandon this quest? Your progress will be lost.')) return;
    try {
        await fetch(`/api/user/quests/${questId}/abandon`, {
            method: 'POST', credentials: 'include',
            headers: { 'X-CSRF-Token': CSRF_TOKEN() }
        });
        loadQuestBoard();
        showToast('Quest abandoned.', 'info');
    } catch (e) {}
}

function showQuestCelebration(quest) {
    const cel = document.getElementById('questCelebration');
    document.getElementById('questCelebrationIcon').textContent = quest.icon || '⚔️';
    document.getElementById('questCelebrationTitle').textContent = `Quest Complete: ${quest.title}`;
    document.getElementById('questCelebrationLore').textContent = `"${quest.lore_text || 'Well done, brave soul.'}"`;
    document.getElementById('questCelebrationXP').textContent = `+${quest.xp_reward} XP earned`;
    cel.style.display = 'flex';
    setTimeout(() => { cel.style.display = 'none'; }, 8000);
}
```

**Hook into `loadHomeTabData()`**: After the existing data loads, add `loadQuestBoard()`.

---

## SECTION 2: HJ.2 — THE SPELL LIBRARY

### 2.1 Philosophy
The 15 CBT tools already work. Patients just don't use them enough because "Cognitive Distortions Quiz" sounds like homework. "The Mirror of Truth" sounds like magic. The clinical content is identical. The framing transforms everything. This is the power of narrative — the same intervention, experienced completely differently.

### 2.2 Spell Metadata (JavaScript constant — add near CBT_TOOLS array, line 5325)

```javascript
const SPELL_MAP = {
    'CognitiveDistortionsQuiz':  { spell: 'The Mirror of Truth',    element: '🔮', flavor: 'See your thoughts as they truly are',          color: '#6366f1', power_element: 'Mind'   },
    'CoreBeliefsWorksheet':      { spell: 'The Root Reading',        element: '🌳', flavor: 'Unearth the beliefs that shape your world',     color: '#059669', power_element: 'Earth'  },
    'ThoughtDefusionExercise':   { spell: 'The Cloud Walk',          element: '☁️', flavor: 'Unhook from thoughts that hold you back',       color: '#7dd3fc', power_element: 'Air'    },
    'IfThenCopingPlan':          { spell: 'The If-Then Binding',     element: '🔗', flavor: 'Prepare your response before the storm',        color: '#f59e0b', power_element: 'Will'   },
    'CopingSkillsSelector':      { spell: 'The Arsenal',             element: '🛠️', flavor: 'Build your personal toolkit of resilience',    color: '#8b5cf6', power_element: 'Craft'  },
    'SelfCompassionLetter':      { spell: 'The Healing Salve',       element: '💙', flavor: 'Treat yourself with the care you deserve',      color: '#06b6d4', power_element: 'Heart'  },
    'ProblemSolvingWorksheet':   { spell: 'The Compass',             element: '🧭', flavor: 'Navigate from stuck to moving forward',         color: '#10b981', power_element: 'Wisdom' },
    'ExposureHierarchyBuilder':  { spell: 'The Courage Steps',       element: '🏔️', flavor: 'Map your path through what frightens you',     color: '#f97316', power_element: 'Fire'   },
    'RelaxationAudioPlayer':     { spell: 'Calm Breath',             element: '💨', flavor: 'Regulate your nervous system instantly',        color: '#a78bfa', power_element: 'Breath' },
    'UrgeSurfingTimer':          { spell: 'The Wave Rider',          element: '🏄', flavor: 'Ride the urge, do not fight it',                color: '#0ea5e9', power_element: 'Water'  },
    'ValuesCardSort':            { spell: 'True North',              element: '⭐', flavor: 'Connect to what matters most to you',           color: '#fbbf24', power_element: 'Spirit' },
    'StrengthsInventory':        { spell: 'The Strength Rune',       element: '💪', flavor: 'Discover the powers that already live in you',  color: '#84cc16', power_element: 'Body'   },
    'SleepHygieneChecklist':     { spell: 'The Dream Ward',          element: '🌙', flavor: 'Protect your nights and restore your days',     color: '#818cf8', power_element: 'Rest'   },
    'SafetyPlanBuilder':         { spell: 'The Shield Pact',         element: '🛡️', flavor: 'Forge your plan for when the storm comes',      color: '#ef4444', power_element: 'Shield' },
    'ActivityScheduler':         { spell: 'Spark of Motion',         element: '⚡', flavor: 'Break the stillness and reclaim your energy',   color: '#f59e0b', power_element: 'Energy' },
};
```

### 2.3 Database

```sql
CREATE TABLE IF NOT EXISTS spell_mastery (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    tool_id TEXT NOT NULL,
    first_cast_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cast_count INTEGER DEFAULT 1,
    last_cast_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    power_level INTEGER DEFAULT 1,
    UNIQUE(username, tool_id)
);
CREATE INDEX IF NOT EXISTS idx_spell_mastery_username ON spell_mastery(username);
```

### 2.4 Backend Endpoints

#### `POST /api/user/spell/cast`
```
Request:  { tool_id: "RelaxationAudioPlayer" }
Response: { success: true, is_first_cast: bool, cast_count: int, power_level: int }
```

Logic: UPSERT into spell_mastery. Power level calculation:
- cast_count >= 50 → power_level 5
- cast_count >= 20 → power_level 4
- cast_count >= 10 → power_level 3
- cast_count >= 3  → power_level 2
- else             → power_level 1

Also advance quest progress: call `_advance_quest_progress(username, f'cbt_tool:{tool_id}', cur, conn)`

#### `GET /api/user/spells`
```
Response: {
    mastered: [{tool_id, spell_name, element, flavor, cast_count, power_level,
                first_cast_at, last_cast_at}],
    unmastered: [{tool_id, spell_name, element, flavor}],  -- those with no mastery row
    total_casts: int
}
```

### 2.5 Frontend — CBT Tab Modifications

#### Modified `renderCBTToolsDashboard()`:
Add a toggle header with two views: "Tool Grid" and "📖 Spell Library"

```javascript
// At top of CBT tab section, add view state
let _cbtView = 'tools'; // 'tools' or 'library'

function renderCBTToolsDashboard() {
    const dash = document.getElementById('cbtToolsDashboard');
    dash.innerHTML = CBT_TOOLS.map(tool => {
        const spell = SPELL_MAP[tool.id];
        return `
        <button class="cbt-tool-btn" onclick="loadAndRecordSpell('${tool.id}')"
                style="padding:20px 12px; border-radius:14px; border:2px solid var(--border-color);
                       background:var(--bg-card); display:flex; flex-direction:column; align-items:center;
                       gap:8px; cursor:pointer; transition:all 0.2s; box-shadow:0 2px 8px var(--shadow-color);
                       position:relative; overflow:hidden;">
            ${spell ? `<div style="position:absolute; top:0; left:0; right:0; height:3px; background:${spell.color};"></div>` : ''}
            <span style="font-size:2.2em;">${tool.icon}</span>
            <span style="font-size:0.95em; font-weight:700; text-align:center; line-height:1.2;">${tool.name}</span>
            ${spell ? `
            <span style="font-size:0.75em; color:${spell.color}; font-style:italic; text-align:center; line-height:1.2;">
                ${spell.element} ${spell.spell}
            </span>` : ''}
            <span id="masteryBadge_${tool.id}" style="font-size:0.7em; display:none; color:#fbbf24;"></span>
        </button>`;
    }).join('');
    loadSpellMasteryBadges();
}

async function loadSpellMasteryBadges() {
    try {
        const resp = await fetch('/api/user/spells', { credentials: 'include' });
        if (!resp.ok) return;
        const data = await resp.json();
        (data.mastered || []).forEach(s => {
            const el = document.getElementById(`masteryBadge_${s.tool_id}`);
            if (el) {
                const stars = '⭐'.repeat(s.power_level);
                el.textContent = `${stars} Cast ${s.cast_count}×`;
                el.style.display = 'block';
            }
        });
    } catch (e) {}
}

async function loadAndRecordSpell(toolId) {
    // Record the cast (fire-and-forget)
    fetch('/api/user/spell/cast', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': CSRF_TOKEN() },
        body: JSON.stringify({ tool_id: toolId })
    }).then(r => r.json()).then(data => {
        if (data.is_first_cast) {
            showSpellLearnedAnimation(toolId);
        }
    }).catch(() => {});
    // Then load the tool
    loadCBTTool(toolId);
}

function showSpellLearnedAnimation(toolId) {
    const spell = SPELL_MAP[toolId];
    if (!spell) return;
    const overlay = document.createElement('div');
    overlay.style.cssText = `position:fixed; inset:0; background:rgba(0,0,0,0.85); z-index:9999;
        display:flex; align-items:center; justify-content:center; flex-direction:column;
        animation:fadeIn 0.3s ease;`;
    overlay.innerHTML = `
        <div style="text-align:center; color:white; padding:40px;">
            <div style="font-size:4em; margin-bottom:16px; animation:spellPulse 0.6s ease infinite alternate;">
                ${spell.element}
            </div>
            <h2 style="margin:0 0 8px 0; font-size:1.8em;">✨ Spell Learned!</h2>
            <h3 style="margin:0 0 12px 0; color:${spell.color}; font-size:1.4em;">${spell.spell}</h3>
            <p style="color:rgba(255,255,255,0.75); font-style:italic; margin:0 0 20px 0;">"${spell.flavor}"</p>
            <p style="font-size:0.9em; color:rgba(255,255,255,0.5);">Added to your Spell Library</p>
        </div>`;
    overlay.addEventListener('click', () => overlay.remove());
    document.body.appendChild(overlay);
    setTimeout(() => overlay.remove(), 4000);
}
```

#### Spell Library View (switchable within CBT tab):
Add a "📖 Spell Library" button in the CBT tab header that shows the library view:

```javascript
function showSpellLibrary() {
    const loader = document.getElementById('cbtToolLoader');
    const dash = document.getElementById('cbtToolsDashboard');
    dash.style.display = 'none';
    loader.innerHTML = '<div style="text-align:center; color:var(--text-muted); padding:20px;">Loading Spell Library...</div>';

    fetch('/api/user/spells', { credentials: 'include' })
        .then(r => r.json())
        .then(data => {
            const mastered = data.mastered || [];
            const unmastered = data.unmastered || [];

            loader.innerHTML = `
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                    <h3 style="margin:0;">📖 Your Spell Library</h3>
                    <button onclick="closeSpellLibrary()" class="btn btn-secondary">← Back to Tools</button>
                </div>
                ${mastered.length ? `
                <p style="color:var(--text-secondary); margin-bottom:15px;">
                    <strong>${mastered.length}</strong> spell${mastered.length !== 1 ? 's' : ''} mastered ·
                    <strong>${data.total_casts || 0}</strong> total casts
                </p>
                <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:16px; margin-bottom:28px;">
                    ${mastered.map(s => {
                        const spell = SPELL_MAP[s.tool_id] || {};
                        const powerOrbs = Array.from({length:5}, (_, i) =>
                            `<span style="color:${i < s.power_level ? spell.color || '#fbbf24' : 'var(--border-color)'}; font-size:0.9em;">◆</span>`
                        ).join('');
                        const lastUsed = s.last_cast_at ? new Date(s.last_cast_at).toLocaleDateString('en-GB', {day:'numeric',month:'short'}) : '';
                        return `
                        <div style="border:2px solid ${spell.color || 'var(--border-color)'}33; border-radius:14px;
                             padding:18px; background:var(--bg-secondary); position:relative; overflow:hidden;
                             cursor:pointer;" onclick="loadAndRecordSpell('${s.tool_id}')">
                            <div style="position:absolute; top:0; left:0; right:0; height:3px; background:${spell.color || 'var(--accent-color)'};"></div>
                            <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
                                <span style="font-size:2.2em;">${spell.element || '🔮'}</span>
                                <div>
                                    <strong style="display:block; color:${spell.color || 'var(--text-primary)'};">${s.spell_name || spell.spell}</strong>
                                    <span style="font-size:0.8em; color:var(--text-muted);">${s.tool_id.replace(/([A-Z])/g,' $1').trim()}</span>
                                </div>
                            </div>
                            <p style="color:var(--text-secondary); font-size:0.85em; font-style:italic; margin:0 0 12px 0;">"${spell.flavor || ''}"</p>
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <div>${powerOrbs}</div>
                                <span style="font-size:0.8em; color:var(--text-muted);">Cast ${s.cast_count}× · ${lastUsed}</span>
                            </div>
                        </div>`;
                    }).join('')}
                </div>` : ''}

                ${unmastered.length ? `
                <h4 style="color:var(--text-muted); margin-bottom:12px;">📜 Spells Yet to be Learned</h4>
                <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px;">
                    ${unmastered.map(s => {
                        const spell = SPELL_MAP[s.tool_id] || {};
                        return `
                        <div style="border:1.5px dashed var(--border-color); border-radius:12px; padding:16px;
                             opacity:0.6; cursor:pointer;" onclick="loadAndRecordSpell('${s.tool_id}')">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <span style="font-size:1.8em; filter:grayscale(0.7);">${spell.element || '?'}</span>
                                <div>
                                    <strong style="display:block; font-size:0.9em;">${spell.spell || s.tool_id}</strong>
                                    <span style="font-size:0.75em; color:var(--text-muted);">Not yet learned · Tap to learn</span>
                                </div>
                            </div>
                        </div>`;
                    }).join('')}
                </div>` : '<p style="color:var(--success-color); text-align:center; padding:20px;">🌟 All spells mastered! Truly legendary.</p>'}
            </div>`;
        })
        .catch(() => {
            loader.innerHTML = '<p style="color:var(--danger-color);">Could not load spell library.</p>';
        });
}

function closeSpellLibrary() {
    document.getElementById('cbtToolsDashboard').style.display = 'grid';
    document.getElementById('cbtToolLoader').innerHTML = '';
    renderCBTToolsDashboard();
}
```

**Add to CBT tab HTML header** (after `<h3>Cognitive Behavioral Therapy Tools</h3>`):
```html
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
    <p style="color:var(--text-secondary); margin:0;">Select a tool below. Each one has a spell name — hover to see it.</p>
    <button onclick="showSpellLibrary()" class="btn btn-secondary" style="white-space:nowrap; padding:8px 16px;">
        📖 Spell Library
    </button>
</div>
```

---

## SECTION 3: HJ.3 — THE SANCTUARY

### 3.1 Philosophy
The home screen is the patient's first experience every time they open the app. Currently it's functional but clinical. The Sanctuary transforms it into a living, breathing environment that feels personal, warm, and magical. The clinical components are all still there — they're just wrapped in a narrative that honours the patient's journey.

### 3.2 CSS — Sanctuary Theme

Add to the CSS section (after existing `:root` and `[data-theme="dark"]` blocks):

```css
/* === SANCTUARY THEME === */
[data-theme="sanctuary"] {
    --bg-primary: linear-gradient(160deg, #0d1b2a 0%, #1b2838 40%, #2d1b47 100%);
    --bg-secondary: #1a2235;
    --bg-card: #1e2d47;
    --bg-input: #243352;
    --bg-sidebar: #141f30;
    --bg-hover: rgba(244,162,97,0.08);
    --text-primary: #e8e4d9;
    --text-secondary: #b0a990;
    --text-muted: #7a7260;
    --border-color: #2a3d5a;
    --shadow-color: rgba(0,0,0,0.5);
    --accent-color: #f4a261;
    --accent-gradient: linear-gradient(135deg, #f4a261, #e76f51);
    --success-color: #40916c;
    --danger-color: #ef4444;
    --warning-color: #f4a261;
    /* Sanctuary-specific */
    --sanctuary-forest: #2d6a4f;
    --sanctuary-amber: #f4a261;
    --sanctuary-crimson: #e76f51;
    --sanctuary-purple: #7c3aed;
    --sanctuary-gold: #d4a017;
    --sanctuary-mist: rgba(244,162,97,0.08);
}

/* Sanctuary card glow effect */
[data-theme="sanctuary"] .card {
    border: 1px solid rgba(244,162,97,0.12);
    box-shadow: 0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(244,162,97,0.05);
}

[data-theme="sanctuary"] .tab-btn.active {
    background: var(--accent-gradient);
    color: white;
}

/* Sanctuary-specific animations */
@keyframes sanctuaryFloat {
    0%, 100% { transform: translateY(0px); }
    50%       { transform: translateY(-6px); }
}

@keyframes sanctuaryGlow {
    0%, 100% { box-shadow: 0 0 10px rgba(244,162,97,0.2); }
    50%       { box-shadow: 0 0 25px rgba(244,162,97,0.45); }
}

@keyframes emberFlicker {
    0%,100% { transform: scaleX(1) scaleY(1); opacity: 1; }
    25%      { transform: scaleX(0.95) scaleY(1.05); opacity: 0.95; }
    75%      { transform: scaleX(1.04) scaleY(0.97); opacity: 0.98; }
}

@keyframes spellPulse {
    0%   { transform: scale(1); }
    100% { transform: scale(1.15); }
}

/* Sanctuary home elements */
.sanctuary-section {
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    transition: box-shadow 0.3s ease;
}

.sanctuary-section:hover {
    box-shadow: 0 8px 32px var(--shadow-color);
}

.sanctuary-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
}

.sanctuary-icon {
    font-size: 1.6em;
    flex-shrink: 0;
}

.sanctuary-title {
    font-size: 1em;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
}

.sanctuary-subtitle {
    font-size: 0.8em;
    color: var(--text-muted);
    margin: 0;
    font-style: italic;
}

.mood-garden-canvas {
    width: 100%;
    height: 120px;
    border-radius: 12px;
    background: var(--bg-secondary);
    display: block;
}

.spell-circle-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
}

.spell-circle-item {
    border: 1.5px solid var(--border-color);
    border-radius: 12px;
    padding: 14px 10px;
    text-align: center;
    cursor: pointer;
    background: var(--bg-secondary);
    transition: all 0.2s ease;
}

.spell-circle-item:hover {
    border-color: var(--accent-color);
    background: var(--sanctuary-mist, rgba(244,162,97,0.05));
    transform: translateY(-2px);
}

.milestone-stone {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 10px;
    background: var(--bg-secondary);
    margin-bottom: 8px;
    border-left: 3px solid var(--sanctuary-gold, #d4a017);
}

.weekly-ember-container {
    display: flex;
    align-items: flex-end;
    justify-content: center;
    gap: 8px;
    padding: 10px 0;
}

.ember-day {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}

.ember-flame {
    width: 28px;
    border-radius: 4px 4px 2px 2px;
    transition: height 0.5s ease, background 0.5s ease;
    background: linear-gradient(to top, #e76f51, #f4a261);
}

.ember-flame.lit {
    animation: emberFlicker 2s ease infinite;
}

.ember-flame.unlit {
    background: var(--border-color);
    animation: none;
}

.ember-day-label {
    font-size: 0.65em;
    color: var(--text-muted);
    text-align: center;
}
```

### 3.3 Theme Toggle — Add Sanctuary Theme Button

The existing theme toggle cycles light↔dark. Add a "🌿 Sanctuary" button alongside it (or extend the toggle).

In the header/theme toggle area, add:
```html
<button id="sanctuaryThemeBtn" onclick="setSanctuaryTheme()" title="Sanctuary Theme"
        style="background: linear-gradient(135deg, #2d6a4f, #40916c); color: white;
               border: none; border-radius: 8px; padding: 6px 12px; cursor: pointer;
               font-size: 0.85em; font-weight: 600;">
    🌿 Sanctuary
</button>
```

```javascript
function setSanctuaryTheme() {
    const html = document.documentElement;
    if (html.getAttribute('data-theme') === 'sanctuary') {
        // Toggle back to light
        html.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
    } else {
        html.setAttribute('data-theme', 'sanctuary');
        localStorage.setItem('theme', 'sanctuary');
    }
}

// Extend theme initialization to handle sanctuary
// In the existing theme init code, add sanctuary check:
// if (saved === 'sanctuary') document.documentElement.setAttribute('data-theme', 'sanctuary');
```

### 3.4 Home Tab — The Sanctuary Redesign

**Replace the home tab content** (lines 4809–4992) with the Sanctuary layout. Keep the wellness ritual container exactly as-is but wrap it in sanctuary styling. Keep the crisis card. Remove the help card, feedback card. Add the new sanctuary sections.

**New home tab layout order:**
1. **Sanctuary Header** — personalized greeting + season + companion name
2. **The Hearth** — wellness ritual (existing `#wellnessRitualContainer`, kept intact)
3. **The Quest Board** — active quests mini-widget (new `#questBoardCard`)
4. **The Mood Garden** — Canvas chart of last 7 mood logs
5. **The Spell Circle** — 3 recommended spells
6. **The Milestone Wall** — last 3 achievements + streak
7. **Your Companion** — pet card (redesigned)
8. **The Weekly Ember** — 7-day engagement visualization
9. **Crisis resources** (always keep this)

#### JavaScript — Sanctuary Data Loader

```javascript
async function loadSanctuaryData() {
    try {
        // Load mood history for garden
        const moodResp = await fetch('/api/mood/history?limit=7', { credentials: 'include' });
        if (moodResp.ok) {
            const moodData = await moodResp.json();
            drawMoodGarden(moodData.entries || moodData.moods || []);
        }
        // Load achievements for milestone wall
        const achResp = await fetch('/api/patient/achievements', { credentials: 'include' });
        if (achResp.ok) {
            const achData = await achResp.json();
            renderMilestoneWall(achData.achievements || achData || []);
        }
        // Load pet for companion
        const petResp = await fetch('/api/pet', { credentials: 'include' });
        if (petResp.ok) {
            const petData = await petResp.json();
            renderCompanionCard(petData);
        }
        // Render spell circle (uses local spell map, plus mastery if available)
        renderSpellCircle();
        // Render weekly ember
        renderWeeklyEmber();
        // Load quest board
        loadQuestBoard();
    } catch (e) {
        console.error('Sanctuary load error:', e);
    }
}

function drawMoodGarden(entries) {
    const canvas = document.getElementById('moodGardenCanvas');
    if (!canvas || !canvas.getContext) return;
    const ctx = canvas.getContext('2d');
    const W = canvas.width = canvas.offsetWidth || 600;
    const H = canvas.height = 120;

    // Sky gradient based on average mood
    const avgMood = entries.length ? entries.reduce((s, e) => s + (e.mood_val || e.mood || 5), 0) / entries.length : 5;
    const skyGrad = ctx.createLinearGradient(0, 0, 0, H * 0.6);
    if (avgMood >= 7) {
        skyGrad.addColorStop(0, '#87ceeb');
        skyGrad.addColorStop(1, '#b8e4f7');
    } else if (avgMood >= 4) {
        skyGrad.addColorStop(0, '#9ab5c8');
        skyGrad.addColorStop(1, '#c4d8e8');
    } else {
        skyGrad.addColorStop(0, '#6a7a8a');
        skyGrad.addColorStop(1, '#8a9aaa');
    }
    ctx.fillStyle = skyGrad;
    ctx.fillRect(0, 0, W, H);

    // Ground
    const groundGrad = ctx.createLinearGradient(0, H * 0.65, 0, H);
    groundGrad.addColorStop(0, '#2d6a4f');
    groundGrad.addColorStop(1, '#1a3d2a');
    ctx.fillStyle = groundGrad;
    ctx.fillRect(0, H * 0.65, W, H);

    // Draw 7 garden elements, evenly spaced
    const days = Math.max(entries.length, 1);
    const spacing = W / (days + 1);

    entries.slice(-7).forEach((entry, i) => {
        const mood = entry.mood_val || entry.mood || 5;
        const x = spacing * (i + 1);
        const groundY = H * 0.65;

        if (mood >= 8) {
            // Sunflower
            drawSunflower(ctx, x, groundY, mood);
        } else if (mood >= 6) {
            // Simple flower
            drawSimpleFlower(ctx, x, groundY, mood);
        } else if (mood >= 4) {
            // Small green plant
            drawPlant(ctx, x, groundY, mood);
        } else if (mood >= 2) {
            // Tiny sprout with cloud
            drawSprout(ctx, x, groundY, mood);
            drawCloud(ctx, x, groundY - 45, 'gentle');
        } else {
            // Rain cloud (gentle, artistic)
            drawSprout(ctx, x, groundY, 1);
            drawCloud(ctx, x, groundY - 45, 'rain');
        }

        // Day label
        const dayNames = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
        const d = entry.timestamp ? new Date(entry.timestamp) : new Date();
        ctx.fillStyle = 'rgba(255,255,255,0.7)';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(d.toLocaleDateString('en-GB',{weekday:'short'}), x, H - 4);
    });

    if (!entries.length) {
        ctx.fillStyle = 'rgba(255,255,255,0.5)';
        ctx.font = '14px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Log your mood to see your garden grow 🌱', W / 2, H / 2);
    }
}

function drawSunflower(ctx, x, groundY, mood) {
    const h = 35 + mood * 2;
    // Stem
    ctx.strokeStyle = '#40916c'; ctx.lineWidth = 2.5;
    ctx.beginPath(); ctx.moveTo(x, groundY); ctx.lineTo(x, groundY - h); ctx.stroke();
    // Petals
    ctx.fillStyle = '#f4d03f';
    for (let p = 0; p < 8; p++) {
        const angle = (p / 8) * Math.PI * 2;
        ctx.beginPath();
        ctx.ellipse(x + Math.cos(angle) * 8, groundY - h + Math.sin(angle) * 8, 5, 3, angle, 0, Math.PI * 2);
        ctx.fill();
    }
    ctx.fillStyle = '#8B4513';
    ctx.beginPath(); ctx.arc(x, groundY - h, 6, 0, Math.PI * 2); ctx.fill();
}

function drawSimpleFlower(ctx, x, groundY, mood) {
    const h = 25 + mood * 2;
    ctx.strokeStyle = '#40916c'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(x, groundY); ctx.lineTo(x, groundY - h); ctx.stroke();
    const colors = ['#ff6b9d','#ff8c94','#ffa07a','#ffb6c1'];
    ctx.fillStyle = colors[mood % colors.length];
    for (let p = 0; p < 5; p++) {
        const angle = (p / 5) * Math.PI * 2;
        ctx.beginPath();
        ctx.arc(x + Math.cos(angle) * 6, groundY - h + Math.sin(angle) * 6, 4, 0, Math.PI * 2);
        ctx.fill();
    }
    ctx.fillStyle = '#ffd700';
    ctx.beginPath(); ctx.arc(x, groundY - h, 3.5, 0, Math.PI * 2); ctx.fill();
}

function drawPlant(ctx, x, groundY, mood) {
    const h = 18 + mood;
    ctx.strokeStyle = '#40916c'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(x, groundY); ctx.lineTo(x, groundY - h); ctx.stroke();
    // Leaves
    ctx.fillStyle = '#40916c';
    ctx.beginPath(); ctx.ellipse(x - 6, groundY - h * 0.6, 7, 4, -0.5, 0, Math.PI*2); ctx.fill();
    ctx.beginPath(); ctx.ellipse(x + 6, groundY - h * 0.4, 7, 4, 0.5, 0, Math.PI*2); ctx.fill();
}

function drawSprout(ctx, x, groundY, mood) {
    const h = 12;
    ctx.strokeStyle = '#95d5b2'; ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.moveTo(x, groundY); ctx.lineTo(x, groundY - h);
    ctx.bezierCurveTo(x, groundY - h - 4, x + 5, groundY - h - 4, x + 5, groundY - h - 7);
    ctx.stroke();
}

function drawCloud(ctx, x, y, type) {
    ctx.fillStyle = type === 'rain' ? 'rgba(130,150,180,0.7)' : 'rgba(200,220,240,0.6)';
    ctx.beginPath(); ctx.arc(x, y, 10, 0, Math.PI*2); ctx.fill();
    ctx.beginPath(); ctx.arc(x-8, y+3, 7, 0, Math.PI*2); ctx.fill();
    ctx.beginPath(); ctx.arc(x+8, y+3, 7, 0, Math.PI*2); ctx.fill();
    if (type === 'rain') {
        ctx.fillStyle = 'rgba(100,140,200,0.6)';
        ctx.fillRect(x-4, y+10, 1.5, 5);
        ctx.fillRect(x+1, y+12, 1.5, 5);
        ctx.fillRect(x+5, y+10, 1.5, 4);
    }
}

function renderMilestoneWall(achievements) {
    const el = document.getElementById('milestoneWallContent');
    if (!el) return;
    const recent = achievements.slice(0, 3);
    if (!recent.length) {
        el.innerHTML = '<p style="color:var(--text-muted); font-size:0.9em; text-align:center; padding:10px;">Complete your first quest or log your mood to earn your first milestone ✨</p>';
        return;
    }
    el.innerHTML = recent.map(a => `
        <div class="milestone-stone">
            <span style="font-size:1.4em;">${a.icon_emoji || a.icon || '🏆'}</span>
            <div>
                <strong style="display:block; font-size:0.9em;">${a.badge_name || a.title}</strong>
                <span style="font-size:0.78em; color:var(--text-muted);">${a.description || ''}</span>
            </div>
        </div>`).join('');
}

function renderCompanionCard(petData) {
    const el = document.getElementById('companionDisplay');
    if (!el || !petData) return;
    // Determine familiar name based on species/name
    const petEmoji = petData.species === 'cat' ? '🐱' :
                     petData.species === 'dog' ? '🐶' :
                     petData.species === 'rabbit' ? '🐰' :
                     petData.species === 'fox' ? '🦊' : '🐾';
    el.innerHTML = `
        <div style="display:flex; align-items:center; gap:16px;">
            <span style="font-size:3em; animation: sanctuaryFloat 3s ease infinite;">${petEmoji}</span>
            <div style="flex:1;">
                <strong style="display:block; font-size:1em;">${petData.name || 'Your Companion'}</strong>
                <p style="font-size:0.8em; color:var(--text-muted); margin:2px 0 6px 0;">
                    Stage: ${petData.stage || 'Baby'} · ⭐ ${petData.xp || 0} XP · 🪙 ${petData.coins || 0}
                </p>
                <div style="display:flex; gap:8px; flex-wrap:wrap;">
                    <div style="flex:1; min-width:60px;">
                        <div style="font-size:0.7em; color:var(--text-muted); margin-bottom:3px;">Happiness</div>
                        <div style="height:5px; background:var(--border-color); border-radius:3px;">
                            <div style="width:${Math.min(100, petData.happiness || 70)}%; height:100%;
                                        background:#10b981; border-radius:3px;"></div>
                        </div>
                    </div>
                    <div style="flex:1; min-width:60px;">
                        <div style="font-size:0.7em; color:var(--text-muted); margin-bottom:3px;">Energy</div>
                        <div style="height:5px; background:var(--border-color); border-radius:3px;">
                            <div style="width:${Math.min(100, petData.energy || 70)}%; height:100%;
                                        background:#f59e0b; border-radius:3px;"></div>
                        </div>
                    </div>
                </div>
            </div>
            <button onclick="switchTab('pet', document.querySelector('[onclick*=\\"pet\\"]'))"
                    class="btn btn-secondary" style="padding:6px 12px; font-size:0.8em;">Visit →</button>
        </div>`;
}

function renderSpellCircle() {
    const el = document.getElementById('spellCircleGrid');
    if (!el) return;
    // Pick 3 contextually relevant spells (vary by time of day + random seed)
    const hour = new Date().getHours();
    let recommended;
    if (hour < 10) {
        // Morning: grounding, breathing, planning
        recommended = ['RelaxationAudioPlayer', 'IfThenCopingPlan', 'ProblemSolvingWorksheet'];
    } else if (hour < 14) {
        // Midday: active CBT
        recommended = ['CognitiveDistortionsQuiz', 'ValuesCardSort', 'CopingSkillsSelector'];
    } else if (hour < 18) {
        // Afternoon: reflection
        recommended = ['CoreBeliefsWorksheet', 'ThoughtDefusionExercise', 'StrengthsInventory'];
    } else {
        // Evening: wind-down
        recommended = ['SleepHygieneChecklist', 'SelfCompassionLetter', 'UrgeSurfingTimer'];
    }

    el.innerHTML = recommended.map(toolId => {
        const spell = SPELL_MAP[toolId] || { spell: toolId, element: '✨', flavor: '', color: 'var(--accent-color)' };
        const tool = (window.CBT_TOOLS || []).find(t => t.id === toolId) || { icon: spell.element };
        return `
        <div class="spell-circle-item" onclick="switchTab('cbt', document.querySelector('[onclick*=\\"cbt\\"]')); setTimeout(() => loadAndRecordSpell('${toolId}'), 300);">
            <div style="font-size:2em; margin-bottom:6px;">${spell.element}</div>
            <div style="font-weight:700; font-size:0.8em; color:${spell.color}; margin-bottom:3px;">${spell.spell}</div>
            <div style="font-size:0.72em; color:var(--text-muted); line-height:1.3; font-style:italic;">${spell.flavor}</div>
        </div>`;
    }).join('');
}

async function renderWeeklyEmber() {
    const el = document.getElementById('weeklyEmberContainer');
    if (!el) return;
    const dayNames = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
    const today = new Date();
    const days = [];
    for (let i = 6; i >= 0; i--) {
        const d = new Date(today);
        d.setDate(d.getDate() - i);
        days.push(d);
    }
    // Check wellness logs for each day (simplified: use streak count from pet/wellness API)
    // For now, use the streak count from existing data + estimate
    let streakCount = 0;
    try {
        const resp = await fetch('/api/wellness-log/streak', { credentials: 'include' });
        if (resp.ok) { const d = await resp.json(); streakCount = d.streak || 0; }
    } catch {}

    el.innerHTML = days.map((d, i) => {
        const isLit = i >= (7 - Math.min(streakCount, 7));
        const height = isLit ? (20 + (i + 1) * 6) : 10;
        return `
        <div class="ember-day">
            <div class="ember-flame ${isLit ? 'lit' : 'unlit'}" style="height:${height}px;"></div>
            <span class="ember-day-label">${dayNames[d.getDay() === 0 ? 6 : d.getDay() - 1]}</span>
        </div>`;
    }).join('');
}
```

### 3.5 The Sanctuary HTML (Complete Home Tab Replacement)

Replace the entire `<div id="homeTab" ...>` content with:

```html
<div id="homeTab" class="tab-content active">

    <!-- Sanctuary Header -->
    <div class="card sanctuary-section" style="background: var(--bg-card);">
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;">
            <div>
                <h2 id="homeWelcomeMessage" style="margin:0 0 4px 0; font-size:1.4em;">Welcome to your Sanctuary</h2>
                <p id="homeLastLogin" style="margin:0; color:var(--text-secondary); font-size:0.85em;">Loading...</p>
            </div>
            <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
                <div class="home-version-info">
                    <span class="app-version" style="font-size:0.75em; color:var(--text-muted);">Healing Space UK v22.1.0</span>
                </div>
            </div>
        </div>
        <div class="motivational-quote" id="homeMotivationalQuote" style="margin-top:12px;
             padding:12px 16px; background:var(--bg-secondary); border-radius:10px;
             color:var(--text-secondary); font-style:italic; font-size:0.9em; border-left:3px solid var(--accent-color);">
            Every day is a fresh start. You're doing great.
        </div>
    </div>

    <!-- The Hearth (Wellness Ritual) -->
    <div id="wellnessRitualContainer" class="card wellness-chat-card" style="margin-top: 20px;">
        <div style="display:flex; align-items:center; gap:8px; padding: 16px 20px 0 20px;">
            <span style="font-size:1.4em;">🔥</span>
            <h3 style="margin:0; font-size:1em; font-weight:700;">The Hearth</h3>
            <span style="font-size:0.78em; color:var(--text-muted); font-style:italic;">Your daily wellness ritual</span>
        </div>
        <!-- Chat Header -->
        <div class="wellness-chat-header">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.8em;">💙</span>
                <div>
                    <h3 id="wellnessGreeting" style="margin: 0;">How are you really doing today?</h3>
                    <p style="margin: 0; color: var(--text-secondary); font-size: 0.9em;">Check in with a quick wellness ritual (2-3 min)</p>
                </div>
            </div>
        </div>
        <div style="padding: 0 20px;">
            <div class="progress-bar-container" style="margin: 15px 0 10px 0;">
                <div class="progress-bar-fill" id="wellnessProgressBar" style="width: 0%"></div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <span class="progress-text" id="wellnessProgressText" style="font-size: 0.85em;">Step 1 of 10</span>
                <button id="wellnessCollapseBtn" class="wellness-close-btn" onclick="toggleWellnessChat()" title="Minimize"
                        style="background: none; border: none; font-size: 1.2em; cursor: pointer; color: var(--text-secondary);">−</button>
            </div>
        </div>
        <div id="wellnessConversation" class="wellness-chat-messages"></div>
        <div id="wellnessAlreadyLogged" class="wellness-already-logged"
             style="display: none; text-align: center; padding: 15px; background: var(--bg-secondary);
                    border-radius: 8px; margin: 15px; position: relative;">
            <button onclick="toggleWellnessChat()"
                    style="position: absolute; top: 8px; right: 8px; background: none; border: none;
                           font-size: 1.2em; cursor: pointer; color: var(--text-secondary);" title="Minimize">−</button>
            <p style="font-size: 1.1em; margin: 0 0 8px 0;">🔥 Hearth tended for today!</p>
            <p style="color: var(--text-secondary); margin: 0; font-size: 0.95em;">You've completed your wellness ritual. Come back tomorrow.</p>
        </div>
        <div class="wellness-input-area" style="padding: 0 20px 20px 20px; display: flex; gap: 10px; justify-content: space-between;">
            <button id="wellnessPrevBtn" class="btn btn-secondary" onclick="previousWellnessStep()" style="display: none; flex: 1;">← Back</button>
            <button id="wellnessSkipBtn" class="btn btn-secondary" onclick="skipWellnessStep()" style="flex: 1;">Skip</button>
            <button id="wellnessNextBtn" class="btn btn-primary" onclick="nextWellnessStep()" style="flex: 1;">Next →</button>
            <button id="wellnessSubmitBtn" class="btn btn-success" onclick="submitWellnessRitual()" style="display: none; flex: 1;">✓ Done</button>
        </div>
    </div>

    <!-- The Quest Board -->
    <div class="card quest-board-card sanctuary-section" id="questBoardCard" style="margin-top: 20px;">
        <div class="sanctuary-header">
            <span class="sanctuary-icon">⚔️</span>
            <div>
                <h3 class="sanctuary-title" style="margin:0;">The Quest Board</h3>
                <p class="sanctuary-subtitle" style="margin:0;">
                    <span id="questXpTotal">0</span> XP earned · <span id="questCompletedCount">0</span> completed
                </p>
            </div>
            <button onclick="showQuestAcceptModal()" class="btn btn-primary"
                    style="margin-left:auto; padding:7px 14px; font-size:0.85em; white-space:nowrap;">
                + Quest
            </button>
        </div>
        <div class="streak-display" id="streakDisplay">
            <span class="streak-icon">🔥</span>
            <span class="streak-count" id="streakCount">0</span> day streak
        </div>
        <div id="activeQuestsList">
            <p style="color:var(--text-muted); font-size:0.9em; text-align:center; padding:16px;">
                Loading your quests...
            </p>
        </div>
    </div>

    <!-- The Mood Garden -->
    <div class="card sanctuary-section" style="margin-top: 20px;">
        <div class="sanctuary-header">
            <span class="sanctuary-icon">🌿</span>
            <div>
                <h3 class="sanctuary-title">The Mood Garden</h3>
                <p class="sanctuary-subtitle">Your last 7 days, growing in colour</p>
            </div>
        </div>
        <canvas id="moodGardenCanvas" class="mood-garden-canvas"></canvas>
        <p style="text-align:center; font-size:0.78em; color:var(--text-muted); margin-top:8px;">
            Higher mood = brighter blooms · Log daily to watch your garden grow
        </p>
    </div>

    <!-- The Spell Circle -->
    <div class="card sanctuary-section" style="margin-top: 20px;">
        <div class="sanctuary-header">
            <span class="sanctuary-icon">🌀</span>
            <div>
                <h3 class="sanctuary-title">The Spell Circle</h3>
                <p class="sanctuary-subtitle">Three spells suggested for this moment</p>
            </div>
        </div>
        <div id="spellCircleGrid" class="spell-circle-grid">
            <!-- Rendered by renderSpellCircle() -->
        </div>
    </div>

    <!-- The Milestone Wall -->
    <div class="card sanctuary-section" style="margin-top: 20px;">
        <div class="sanctuary-header">
            <span class="sanctuary-icon">🏆</span>
            <div>
                <h3 class="sanctuary-title">The Milestone Wall</h3>
                <p class="sanctuary-subtitle">Your earned achievements glow here</p>
            </div>
            <button onclick="switchTab('progress', document.querySelector('[onclick*=&quot;progress&quot;]'))"
                    class="btn btn-secondary" style="margin-left:auto; padding:6px 12px; font-size:0.8em;">
                View All
            </button>
        </div>
        <div id="milestoneWallContent">
            <p style="color:var(--text-muted); font-size:0.85em; text-align:center; padding:10px;">Loading achievements...</p>
        </div>
    </div>

    <!-- Your Companion -->
    <div class="card sanctuary-section" id="companionSection" style="margin-top: 20px;">
        <div class="sanctuary-header">
            <span class="sanctuary-icon">🐾</span>
            <div>
                <h3 class="sanctuary-title">Your Companion</h3>
                <p class="sanctuary-subtitle">Growing with you</p>
            </div>
        </div>
        <div id="companionDisplay">
            <p style="color:var(--text-muted); text-align:center; padding:10px;">Loading companion...</p>
        </div>
    </div>

    <!-- The Weekly Ember -->
    <div class="card sanctuary-section" style="margin-top: 20px;">
        <div class="sanctuary-header">
            <span class="sanctuary-icon">🕯️</span>
            <div>
                <h3 class="sanctuary-title">The Weekly Ember</h3>
                <p class="sanctuary-subtitle">Each day you check in, the flame grows</p>
            </div>
        </div>
        <div id="weeklyEmberContainer" class="weekly-ember-container">
            <!-- Rendered by renderWeeklyEmber() -->
        </div>
    </div>

    <!-- Crisis Resources (Always Visible) -->
    <div class="card crisis-resources-box home-safety-card" style="margin-top: 20px;">
        <h4 class="crisis-title">🆘 Need Immediate Help?</h4>
        <p><strong>Samaritans:</strong> Call 116 123 (24/7 free)</p>
        <p><strong>Crisis Text Line:</strong> Text SHOUT to 85258</p>
        <p><strong>NHS Crisis:</strong> Call 111 (option 2)</p>
        <button class="btn btn-secondary" style="margin-top: 15px;"
                onclick="switchTab('cbt', document.querySelector('[onclick*=&quot;cbt&quot;]')); setTimeout(() => loadCBTTool('SafetyPlanBuilder'), 200);">
            View Safety Plan Builder
        </button>
    </div>

    <!-- Quest System Overlays (always present) -->
    <!-- Quest Accept Modal -->
    <div id="questAcceptModal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.75);
         z-index:9000; align-items:center; justify-content:center; padding:20px;">
        <div style="background:var(--bg-card); border-radius:16px; padding:28px; max-width:600px;
                    width:100%; max-height:85vh; overflow-y:auto; box-shadow:0 20px 60px rgba(0,0,0,0.5);"
             onclick="event.stopPropagation()">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                <h3 style="margin:0;">⚔️ Choose Your Quest</h3>
                <button onclick="document.getElementById('questAcceptModal').style.display='none'"
                        style="background:none; border:none; font-size:1.5em; cursor:pointer; color:var(--text-muted);">×</button>
            </div>
            <div id="suggestedQuestsList">
                <p style="text-align:center; color:var(--text-muted); padding:20px;">Loading available quests...</p>
            </div>
        </div>
    </div>

    <!-- Quest Completion Celebration -->
    <div id="questCelebration" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.88);
         z-index:9999; align-items:center; justify-content:center; padding:20px; flex-direction:column;">
        <div style="text-align:center; color:white; max-width:400px;">
            <div id="questCelebrationIcon" style="font-size:5em; margin-bottom:20px;">⚔️</div>
            <h2 id="questCelebrationTitle" style="font-size:1.8em; margin-bottom:10px;">Quest Complete!</h2>
            <p id="questCelebrationLore" style="font-style:italic; color:rgba(255,255,255,0.75); margin-bottom:15px; line-height:1.5;"></p>
            <p id="questCelebrationXP" style="font-size:1.3em; color:#fbbf24; font-weight:700; margin-bottom:20px;"></p>
            <button onclick="document.getElementById('questCelebration').style.display='none'"
                    class="btn btn-primary">Continue Your Journey →</button>
        </div>
    </div>

</div>
```

### 3.6 Update `loadHomeTabData()` and `switchTab()`

In `loadHomeTabData()`, ADD after existing loads:
```javascript
loadSanctuaryData();
```

In `switchTab()`, case `'home'`:
```javascript
case 'home':
    loadHomeTabData();
    loadSanctuaryData();  // ADD THIS
    initializeWellnessRitual();
    loadWinsBoard?.();
    break;
```

---

## IMPLEMENTATION CONSTRAINTS

1. **Never hardcode colours** — use CSS variables only
2. **CSRF on all POST/PUT/DELETE** — `@CSRFProtection.require_csrf` + frontend header
3. **Auth on every endpoint** — `get_authenticated_username()` → None check → role check
4. **Error handling** — `return handle_exception(e, 'endpoint_name')`
5. **DB pattern** — `conn = get_db_connection(); cur = get_wrapped_cursor(conn); ... conn.commit(); conn.close()`
6. **Don't break existing features** — wellness ritual, pet, CBT tools, streak display all must still work
7. **Mobile-first** — all grids use `repeat(auto-fit, ...)`, avoid fixed widths
8. **Canvas responsive** — set canvas.width = canvas.offsetWidth before drawing
9. **Quest progress is additive** — never subtract, never skip committed progress
10. **Seed data is idempotent** — use `ON CONFLICT (quest_key) DO NOTHING` for seeds

---

## COMMIT STRATEGY

After HJ.1: `Feat: Quest System (HJ.1) — patient quests, auto-progress hooks, quest board`
After HJ.2: `Feat: Spell Library (HJ.2) — CBT tools reframed as spells with mastery tracking`
After HJ.3: `Feat: The Sanctuary (HJ.3) — home screen redesign with mood garden, ember, spell circle`

---

*This prompt authored February 22, 2026. Implement precisely as specified.*
