# Week 1 Quick Wins - API ENDPOINTS REFERENCE
**Date**: February 11, 2026  
**Version**: 1.0  
**Status**: Production Ready ✅  
**Features**: 4 new endpoints live on main branch

---

## 🚀 Quick Reference

| Endpoint | Method | Purpose | Auth | Rate Limit |
|----------|--------|---------|------|-----------|
| `/api/patient/progress/mood` | GET | Show patient mood progress % | Session | 10/min |
| `/api/patient/achievements` | GET | List unlocked achievements | Session | 30/min |
| `/api/patient/achievements/check-unlocks` | POST | Check & unlock new badges | Session | 5/min |
| `/api/patient/homework` | GET | View homework assignments | Session | 10/min |
| `/api/clinician/patients/search` | GET | Search patients (clinician) | Session | 20/min |

---

## 📚 Detailed Documentation

### 1. Get Mood Progress
```
GET /api/patient/progress/mood
```

**Authentication**: Session required ✅  
**Rate Limit**: 10 per minute  
**Response Time**: < 500ms

**Response** (200 OK):
```json
{
  "progress_percentage": 25.5,
  "trend": "improving",
  "first_mood": 5,
  "latest_mood": 7,
  "entries_count": 12,
  "status": "success"
}
```

**Fields**:
- `progress_percentage` (number): -100 to +100 scale
  - Calculation: ((latest - first) / 10) * 100
  - Negative = worsening, Positive = improving
- `trend` (string): "improving" | "declining" | "stable" | "insufficient_data" | "no_data"
  - Based on last 7 mood entries moving average
- `first_mood` (number): Initial mood value (1-10 scale)
- `latest_mood` (number): Most recent mood value
- `entries_count` (number): Total mood logs recorded

**Example Usage**:
```javascript
fetch('/api/patient/progress/mood', {
  method: 'GET',
  headers: { 'Content-Type': 'application/json' }
})
.then(r => r.json())
.then(data => console.log(`You've improved by ${data.progress_percentage}%`))
```

**Error Responses**:
```json
// 401 Unauthorized
{ "error": "Authentication required" }

// 500 Internal Server Error
{ "error": "An unexpected error occurred.", "error_id": "a1b2c3d4" }
```

---

### 2. Get Achievements
```
GET /api/patient/achievements
```

**Authentication**: Session required ✅  
**Rate Limit**: 30 per minute  
**Response Time**: < 500ms

**Response** (200 OK):
```json
{
  "earned": [
    {
      "id": 1,
      "name": "first_log",
      "type": "milestone",
      "description": "Logged your first mood entry",
      "icon": "🎯",
      "earned_at": "2026-02-11T10:30:00"
    },
    {
      "id": 2,
      "name": "streak_7",
      "type": "consistency",
      "description": "7-day mood tracking streak",
      "icon": "🔥",
      "earned_at": "2026-02-18T15:45:00"
    }
  ],
  "progress": {
    "mood_logging": {
      "total_entries": 12,
      "current_streak": 5,
      "next_milestone": 7
    },
    "achievements_earned": 2
  },
  "total_earned": 2,
  "status": "success"
}
```

**Badge Types**:
- `milestone`: One-time achievements (first_log, goal_achieved)
- `consistency`: Streak-based (streak_7, streak_30)
- `skill`: Skill mastery (cbt_completion, homework_done)

**Current Badges**:
1. `first_log` - First mood entry logged
2. `streak_7` - 7 consecutive days of logging
3. `streak_30` - 30 consecutive days of logging

**Extensible**: Add more badges in database without code changes

---

### 3. Check Achievement Unlocks
```
POST /api/patient/achievements/check-unlocks
```

**Authentication**: Session required ✅  
**Rate Limit**: 5 per minute  
**Idempotent**: Yes (prevents duplicate unlocks)

**Request Body**:
```json
{}  // No parameters required, checks all user's data
```

**Response** (200 OK):
```json
{
  "newly_unlocked": [
    {
      "name": "first_log",
      "title": "First Step"
    }
  ],
  "total_unlocked": 1,
  "status": "success"
}
```

**How It Works**:
1. Called after mood logging, goal completion, homework done
2. Queries user's activity (mood counts, streaks, etc.)
3. Checks each badge's unlock criteria
4. Inserts new achievements (with duplicate prevention)
5. Returns newly unlocked badges

**Logic**:
- `first_log`: mood_logs COUNT = 1
- `streak_7`: Check consecutive days = 7
- `streak_30`: Check consecutive days = 30

**Error Responses**:
```json
// 401 Unauthorized
{ "error": "Authentication required" }
```

**Example Flow**:
```javascript
// After user logs mood
await fetch('/api/patient/mood-log', { method: 'POST', body: ... });

// Check for new achievements
const achievements = await fetch('/api/patient/achievements/check-unlocks', {
  method: 'POST'
}).then(r => r.json());

if (achievements.newly_unlocked.length > 0) {
  // Show celebration UI
  showConfetti();
  playSound('achievement-unlock.mp3');
  displayNotification(`🎉 ${achievements.newly_unlocked[0].title}!`);
}
```

---

### 4. Get Homework
```
GET /api/patient/homework
```

**Authentication**: Session required ✅  
**Rate Limit**: 20 per minute  
**Response Time**: < 500ms

**Query Parameters**:
```
GET /api/patient/homework?week=current&include_feedback=true
```

**Response** (200 OK):
```json
{
  "homework": [
    {
      "id": 1,
      "assignment": "Stressful meeting scenario...",
      "type": "CBT Exercise",
      "timestamp": "2026-02-11T14:30:00",
      "status": "completed"
    },
    {
      "id": 2,
      "assignment": "Anxiety at work situation...",
      "type": "CBT Exercise",
      "timestamp": "2026-02-08T10:15:00",
      "status": "completed"
    }
  ],
  "this_week_count": 2,
  "completion_rate": 100.0,
  "status": "success"
}
```

**Fields**:
- `homework` (array): List of assignments
  - `id` (number): Assignment ID
  - `assignment` (string): First 50 chars of assignment
  - `type` (string): "CBT Exercise" | "Homework Task" | "Exposure Practice"
  - `timestamp` (ISO 8601): When completed
  - `status` (string): "completed" | "pending" | "overdue"
- `this_week_count` (number): Count from past 7 days
- `completion_rate` (number): 0-100 percentage

**Source**: cbt_records from past 7 days

---

## CLINICIAN DASHBOARD ENDPOINTS

### 5. Search Patients
```
GET /api/clinician/patients/search
```

**Authentication**: Session + Clinician role required ✅  
**Rate Limit**: 50 per minute  
**Response Time**: < 1500ms (depends on patient count)

**Query Parameters**:
```
GET /api/clinician/patients/search
  ?q=John                          # Search query (name, username, email)
  &risk_level=high                 # Filter: low|moderate|high|critical
  &status=active                   # Filter: active|inactive
  &sort_by=risk_level              # Sort: name|risk_level|last_session
  &page=1                          # Page number (1-indexed)
  &limit=20                        # Results per page (5-50)
```

**Response** (200 OK):
```json
{
  "success": true,
  "patients": [
    {
      "username": "john_doe",
      "name": "John Doe",
      "email": "john@example.com",
      "last_session": "2026-02-10T14:30:00",
      "last_assessment": "2026-02-09T09:00:00",
      "risk_level": "moderate",
      "open_alerts": 1
    },
    {
      "username": "jane_smith",
      "name": "Jane Smith",
      "email": "jane@example.com",
      "last_session": "2026-02-11T10:00:00",
      "last_assessment": "2026-02-11T08:30:00",
      "risk_level": "low",
      "open_alerts": 0
    }
  ],
  "pagination": {
    "total": 45,
    "page": 1,
    "limit": 20,
    "pages": 3
  }
}
```

**Search Behavior**:
- `q`: Case-insensitive substring match (ILIKE)
  - Searches: username, full_name, email
- `risk_level`: Exact match from latest risk_assessment
- `status=active`: last_login > 30 days ago
- `status=inactive`: last_login < 30 days ago or NULL

**Sorting**:
- `name`: Alphabetical by full_name
- `risk_level`: High to Low (critical first)
- `last_session`: Most recent first

**Pagination**:
- Default: page=1, limit=20
- Max limit: 50 results per page
- Total pages calculated: ceil(total / limit)

**Access Control**:
- Only returns patients assigned to logged-in clinician
- Via patient_approvals table with status='approved'
- Role check: user.role = 'clinician'

**Error Responses**:
```json
// 401 Unauthorized
{ "error": "Authentication required" }

// 403 Forbidden (non-clinician)
{ "error": "Clinician access required" }

// 500 Database Error
{ "error": "Database operation failed" }
```

**Example Usage**:
```javascript
// Search for high-risk patients
const response = await fetch(
  '/api/clinician/patients/search?risk_level=high&sort_by=last_session'
);
const data = await response.json();

data.patients.forEach(p => {
  if (p.open_alerts > 0) {
    highlightAsUrgent(p);
  }
});
```

---

## SECURITY IMPLEMENTATIONS

### Authentication
- ✅ All endpoints require Flask session
- ✅ Session checked via `session.get('username')`
- ✅ Role-based access control (clinician endpoints)

### Input Validation
- ✅ Search queries: MAX 100 characters
- ✅ Sort field: Validated against allowed values
- ✅ Risk level: Enum validation
- ✅ Pagination: Constraints (min 5, max 50)

### SQL Injection Prevention
- ✅ All queries use parameterized statements (%s placeholders)
- ✅ No string interpolation of user input
- ✅ psycopg2 handles escaping automatically

### Data Protection
- ✅ Error messages don't leak internal details
- ✅ Error IDs provided for support reference
- ✅ Exceptions logged internally, generic response to client

### Logging
- ✅ All operations logged: log_event(username, category, action, details)
- ✅ Audit trail for compliance
- ✅ Performance monitoring possible

---

## PERFORMANCE CHARACTERISTICS

**Progress Endpoint**:
- Queries: 3 (SELECT COUNT, two mood logs)
- Indexes used: mood_logs(username, entry_timestamp)
- Latency: 50-200ms typical

**Achievements Endpoint**:
- Queries: 1 (single SELECT with ORDER BY)
- Indexes used: achievements(username)
- Latency: 30-100ms typical

**Check Unlocks Endpoint**:
- Queries: ~8 (CHECK each badge + INSERT)
- Transaction: Single commit
- Latency: 100-300ms typical

**Patient Search Endpoint**:
- Queries: 2 (COUNT + SELECT with filtering)
- Indexes used: users(username), patient_approvals, risk_assessments
- Latency: 200-1500ms (varies with dataset)
- Pagination reduces result set size

---

## DATABASE SCHEMA REFERENCE

### achievements Table
```sql
CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL REFERENCES users,
    badge_name TEXT NOT NULL,
    badge_type TEXT NOT NULL,
    description TEXT,
    icon_emoji TEXT,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(username, badge_name)
)

CREATE INDEX idx_achievements_username ON achievements(username);
CREATE INDEX idx_achievements_earned_at ON achievements(earned_at);
```

### notification_preferences Table
```sql
CREATE TABLE notification_preferences (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE REFERENCES users,
    preferred_time_of_day TEXT DEFAULT '09:00',
    notification_frequency TEXT DEFAULT 'daily',
    topics_enabled JSONB DEFAULT '{"mood_reminder": true, ...}',
    smart_timing_enabled BOOLEAN DEFAULT TRUE,
    sound_enabled BOOLEAN DEFAULT TRUE,
    email_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

CREATE INDEX idx_notification_prefs_username ON notification_preferences(username);
```

---

## TESTING THE ENDPOINTS

### Using curl
```bash
# Get mood progress
curl -b "session=YOUR_SESSION_ID" \
  http://localhost:5000/api/patient/progress/mood

# Get achievements
curl -b "session=YOUR_SESSION_ID" \
  http://localhost:5000/api/patient/achievements

# Check unlocks (POST)
curl -b "session=YOUR_SESSION_ID" \
  -X POST \
  http://localhost:5000/api/patient/achievements/check-unlocks

# Get homework
curl -b "session=YOUR_SESSION_ID" \
  http://localhost:5000/api/patient/homework

# Search patients (clinician)
curl -b "session=CLINICIAN_SESSION_ID" \
  "http://localhost:5000/api/clinician/patients/search?q=John&risk_level=high"
```

### Using Postman
1. Create collection: "Quick Wins Week 1"
2. Add request for each endpoint
3. Set Authorization: Cookie with session
4. Test each parameter combination

### Using Python requests
```python
import requests

session = requests.Session()
# Login first...
session.cookies.set('session', 'YOUR_SESSION_TOKEN')

# Test progress
resp = session.get('http://localhost:5000/api/patient/progress/mood')
print(resp.json())

# Test search
resp = session.get(
    'http://localhost:5000/api/clinician/patients/search',
    params={'q': 'John', 'risk_level': 'high'}
)
print(resp.json())
```

---

## INTEGRATION WITH FRONTEND

### React Example: Progress Display
```javascript
useEffect(() => {
  fetch('/api/patient/progress/mood')
    .then(r => r.json())
    .then(data => {
      setProgress(data.progress_percentage);
      setTrend(data.trend);
      // Update UI
    });
}, []);
```

### Vue Example: Achievements
```javascript
async getAchievements() {
  const response = await fetch('/api/patient/achievements');
  this.achievements = (await response.json()).earned;
}
```

### Angular Example: Patient Search
```typescript
searchPatients(query: string) {
  return this.http.get('/api/clinician/patients/search', {
    params: {
      q: query,
      risk_level: this.selectedRiskLevel,
      sort_by: 'name'
    }
  });
}
```

---

## TROUBLESHOOTING

**401 Unauthorized**:
- Check session cookie is set
- Verify session hasn't expired
- Clear browser cookies and re-login

**403 Forbidden (Search endpoint)**:
- User is not a clinician
- Contact admin to update user role

**500 Internal Server Error**:
- Check server logs for error ID
- Database connection issue
- Contact support with error ID

**Slow response (Search)**:
- Many patients in system
- Use pagination to reduce results
- Add more specific search criteria

---

**Last Updated**: February 11, 2026  
**Version**: 1.0 (This Week Implementation)  
**Next**: Phase 2 Frontend Implementation (Feb 18-25)
