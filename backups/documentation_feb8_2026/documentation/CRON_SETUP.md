# 🕗 8pm Mood Reminder Setup (Cron Job)

## Quick Setup (2 steps)

### 1. Run the setup script
```bash
./setup_cron.sh
```

This will automatically:
- Make scripts executable
- Add cron job to run at 8pm daily
- Show you the configuration

### 2. Done! 🎉

The reminders will now be sent automatically at 8pm every day.

---

## What This Does

- **Checks at 8pm daily** if users logged their mood
- **Sends in-app notification** to users who haven't logged yet
- **Logs results** to `/tmp/mood_reminder_cron.log`
- **100% free** - runs on your local machine/server

---

## Testing & Monitoring

### Test the script manually
```bash
./send_mood_reminders.sh
```

### View the logs
```bash
tail -f /tmp/mood_reminder_cron.log
```

### Check cron is installed
```bash
crontab -l | grep mood
```

You should see:
```
0 20 * * * /home/computer001/Documents/Healing Space UK/send_mood_reminders.sh
```

---

## For Production (Railway)

If deploying to Railway, change the API URL:

1. Edit `send_mood_reminders.sh`:
   ```bash
   API_URL="https://your-app.railway.app"
   ```

2. Or set it as an environment variable:
   ```bash
   export API_URL="https://your-app.railway.app"
   ```

3. Run setup again:
   ```bash
   ./setup_cron.sh
   ```

---

## Troubleshooting

### Reminders not sending?

1. **Check API is running**:
   ```bash
   curl http://localhost:5000/api/health
   ```

2. **Test manually with force**:
   ```bash
   curl -X POST http://localhost:5000/api/mood/check-reminder \
     -H "Content-Type: application/json" \
     -d '{"force": true}'
   ```

3. **Check cron logs**:
   ```bash
   grep CRON /var/log/syslog
   ```

4. **Verify script has execute permission**:
   ```bash
   ls -l send_mood_reminders.sh
   ```
   Should show `-rwxr-xr-x`

### Change the time?

Edit cron with:
```bash
crontab -e
```

Change `0 20` to your preferred hour:
- `0 19` = 7pm
- `0 21` = 9pm
- `30 20` = 8:30pm

---

## Removing the Cron Job

```bash
crontab -e
```

Delete the line containing `send_mood_reminders.sh`, save and exit.

---

## How It Works

```
8:00 PM Daily
    ↓
Cron triggers send_mood_reminders.sh
    ↓
Script calls /api/mood/check-reminder
    ↓
API checks who hasn't logged mood today
    ↓
Sends notification to those users
    ↓
Logs result to /tmp/mood_reminder_cron.log
```

---

## Next Steps

Want to customize? Check [MOOD_REMINDERS.md](MOOD_REMINDERS.md) for:
- Email reminders
- Custom reminder times per user
- Streak tracking
- Adherence analytics
