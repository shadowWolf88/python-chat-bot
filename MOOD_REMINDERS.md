# Daily Mood Logging & 8pm Reminders

## Overview
The app now enforces **one mood entry per day** and sends **reminder notifications at 8pm** if a user hasn't logged their mood yet.

## Features

### 1. Daily Limit Enforcement
- Users can only log one mood entry per day
- Uses date comparison: `date(entrestamp) = date('now', 'localtime')`
- Returns **409 Conflict** error if user tries to log twice in same day
- Frontend shows friendly message: "✓ You've already logged your mood today! See you tomorrow! 😊"
- Checkmark (✓) appears on Mood & Habits tab after logging

### 2. 8pm Reminder Notifications
- Automated check at 8pm daily to find users who haven't logged mood
- Sends in-app notification: "🕗 Reminder: Don't forget to log your mood and habits for today!"
- Only sends to users who have NO mood entry for current day

## API Endpoints

### Check if Mood Logged Today
```
GET /api/mood/check-today?username=<username>
```
**Response:**
```json
{
  "logged_today": true,
  "timestamp": "2025-01-13 14:30:45"
}
```

### Send Reminder Notifications (Manual Trigger)
```
POST /api/mood/check-reminder
Content-Type: application/json

{
  "force": true
}
```
**Response:**
```json
{
  "success": true,
  "reminders_sent": 12,
  "message": "Sent 12 mood reminders"
}
```

## Setting Up Automated Reminders

### Option 1: Cron Job (Linux/Mac)
Edit crontab:
```bash
crontab -e
```

Add this line to run at 8pm daily:
```cron
0 20 * * * curl -X POST http://localhost:5000/api/mood/check-reminder -H "Content-Type: application/json"
```

For Railway/production deployment:
```cron
0 20 * * * curl -X POST https://your-app.railway.app/api/mood/check-reminder -H "Content-Type: application/json"
```

### Option 2: APScheduler (Python Background Task)
Install APScheduler:
```bash
pip install apscheduler
```

Add to `api.py` (after imports):
```python
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

def send_daily_reminders():
    """Background job to send 8pm reminders"""
    with app.app_context():
        requests.post('http://localhost:5000/api/mood/check-reminder')

scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_reminders, 'cron', hour=20, minute=0)
scheduler.start()
```

### Option 3: Railway Cron (Cloud Deployment)
Create `.railway/cron.json`:
```json
{
  "jobs": [
    {
      "schedule": "0 20 * * *",
      "command": "curl -X POST $RAILWAY_PUBLIC_DOMAIN/api/mood/check-reminder"
    }
  ]
}
```

### Option 4: GitHub Actions (Free Scheduler)
Create `.github/workflows/mood-reminders.yml`:
```yaml
name: Daily Mood Reminders

on:
  schedule:
    - cron: '0 20 * * *'  # 8pm UTC daily
  workflow_dispatch:  # Manual trigger

jobs:
  send-reminders:
    runs-on: ubuntu-latest
    steps:
      - name: Send Reminder Notifications
        run: |
          curl -X POST https://your-app.railway.app/api/mood/check-reminder \
            -H "Content-Type: application/json"
```

## Testing

### Manual Test (Force Reminder Check)
```bash
curl -X POST http://localhost:5000/api/mood/check-reminder \
  -H "Content-Type: application/json" \
  -d '{"force": true}'
```

### Check Mood Status for User
```bash
curl "http://localhost:5000/api/mood/check-today?username=testuser"
```

### Test Daily Limit (Try logging twice)
1. Log mood once (should succeed)
2. Try logging again immediately (should return 409 error)
3. Check frontend shows: "✓ You've already logged your mood today!"

## Database Schema

### mood_logs Table
```sql
CREATE TABLE mood_logs (
    id INTEGER PRIMARY KEY,
    username TEXT,
    mood_val INTEGER,
    sleep_val REAL,
    water_pints REAL,
    exercise_mins INTEGER,
    outside_mins INTEGER,
    meds TEXT,
    notes TEXT,
    entrestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### notifications Table
```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY,
    recipient_username TEXT,
    message TEXT,
    notification_type TEXT,
    is_read INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Troubleshooting

### Reminders Not Sending
1. Check cron job is running: `crontab -l`
2. Check cron logs: `grep CRON /var/log/syslog`
3. Test endpoint manually with force flag
4. Verify notifications table has entries: `SELECT * FROM notifications WHERE notification_type='mood_reminder'`

### Users Can't Log Mood
1. Check if they already logged today: query `mood_logs` for today's date
2. Verify `entrestamp` column exists and uses DATETIME
3. Check timezone settings match server timezone

### Checkmark Not Appearing
1. Verify `/api/mood/check-today` returns correct status
2. Check browser console for JavaScript errors
3. Ensure `checkMoodStatus()` is called on login

## Production Deployment

### Railway
1. Set up cron using Railway cron jobs or GitHub Actions
2. Ensure `DB_PATH` points to persistent volume (`/app/data/therapist_app.db`)
3. Add health check endpoint to verify reminders are working

### Environment Variables
```env
DEBUG=0
DB_PATH=/app/data/therapist_app.db
PORT=5000
```

### Monitoring
- Log reminder sends to track engagement
- Monitor notification delivery rates
- Track daily mood logging completion percentage

## Future Enhancements

### Priority 1
- [ ] Add user preference for reminder time (not just 8pm)
- [ ] Allow users to disable reminders
- [ ] Send email reminders (in addition to in-app)

### Priority 2
- [ ] Show streak of consecutive days with mood logs
- [ ] Gamify with badges for consistent logging
- [ ] Add snooze functionality (remind in 1 hour)

### Priority 3
- [ ] Clinician dashboard showing patient adherence rates
- [ ] Weekly summary reports
- [ ] Predictive reminders based on user patterns
