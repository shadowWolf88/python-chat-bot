# Railway Deployment Guide - Mood Reminder System

## 🚀 Quick Deploy to Railway

### 1. Set Environment Variables in Railway

Go to your Railway project settings and add:

```env
# Required for app
DEBUG=0
DB_PATH=/app/data/therapist_app.db
PORT=5000
GROQ_API_KEY=your_groq_api_key
PIN_SALT=your_secure_pin_salt
ENCRYPTION_KEY=your_fernet_key

# Your other secrets (Vault, SMTP, etc.)
```

### 2. Set Up GitHub Secret for Reminders

1. Go to your GitHub repo: **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `RAILWAY_APP_URL`
4. Value: Your Railway app URL (e.g., `https://your-app.railway.app`)
5. Click **Add secret**

### 3. Deploy to Railway

```bash
# Make sure all changes are committed
git add -A
git commit -m "Deploy mood reminder system with GitHub Actions"
git push origin main
```

Railway will automatically deploy when you push to main.

### 4. Enable GitHub Actions

The workflow is already created at `.github/workflows/mood-reminders.yml`

It will automatically:
- ✅ Run at 8pm UTC daily
- ✅ Call your Railway app's reminder endpoint
- ✅ Log results in GitHub Actions tab
- ✅ Can be triggered manually for testing

### 5. Test the Workflow

1. Go to your GitHub repo
2. Click **Actions** tab
3. Select **Daily Mood Reminders** workflow
4. Click **Run workflow** → **Run workflow**
5. Check the logs to verify it works

---

## 🕐 Timezone Adjustment

The workflow runs at **8pm UTC** by default. To adjust:

Edit `.github/workflows/mood-reminders.yml` line 5:

```yaml
# For different timezones:
- cron: '0 19 * * *'  # 7pm UTC = 8pm BST (UK summer)
- cron: '0 20 * * *'  # 8pm UTC = 8pm GMT (UK winter)
- cron: '0 21 * * *'  # 9pm UTC
```

Or if you want 8pm in a specific timezone, calculate:
- **US Eastern (EST)**: 8pm EST = 1am UTC next day → `0 1 * * *`
- **US Pacific (PST)**: 8pm PST = 4am UTC next day → `0 4 * * *`
- **UK (GMT)**: 8pm GMT = 8pm UTC → `0 20 * * *`
- **Australia (AEST)**: 8pm AEST = 10am UTC → `0 10 * * *`

---

## 📊 Monitor Reminders

### View Logs in GitHub Actions
1. Go to **Actions** tab in your repo
2. Click on **Daily Mood Reminders**
3. Click on any run to see logs

### View in Railway Logs
```bash
# In Railway deployment logs, search for:
POST /api/mood/check-reminder
```

### Test Manually
```bash
# Force reminder check (for testing)
curl -X POST https://your-app.railway.app/api/mood/check-reminder \
  -H "Content-Type: application/json" \
  -d '{"force": true}'
```

---

## ✅ Verification Checklist

After deployment:

- [ ] App deployed to Railway successfully
- [ ] `RAILWAY_APP_URL` secret added to GitHub
- [ ] GitHub Actions workflow enabled
- [ ] Test workflow runs successfully
- [ ] Reminder endpoint returns 200 OK
- [ ] Notifications appear in app for users without mood logs

---

## 🔧 Troubleshooting

### Workflow Not Running?

1. **Check GitHub Actions is enabled**:
   - Repo Settings → Actions → General
   - Ensure "Allow all actions" is selected

2. **Verify secret is set**:
   - Settings → Secrets → Actions
   - Should see `RAILWAY_APP_URL`

3. **Check cron syntax**:
   - Use [crontab.guru](https://crontab.guru/) to verify

### Reminders Not Sending?

1. **Test endpoint manually**:
   ```bash
   curl https://your-app.railway.app/api/mood/check-reminder \
     -X POST -H "Content-Type: application/json"
   ```

2. **Check Railway logs**:
   - Look for errors in API endpoint
   - Verify database connection

3. **Check notification table**:
   ```sql
   SELECT * FROM notifications 
   WHERE notification_type='mood_reminder' 
   ORDER BY created_at DESC LIMIT 5;
   ```

### Wrong Timezone?

- GitHub Actions runs in UTC
- Calculate your local 8pm in UTC
- Update cron expression in workflow file
- Commit and push changes

---

## 💰 Cost

**100% FREE!**

- Railway: Free tier includes 500 hours/month
- GitHub Actions: 2,000 minutes/month free
- This workflow uses ~1 minute/day = 30 minutes/month

---

## 🔐 Security

The workflow uses GitHub Secrets to store your Railway URL:
- ✅ Never exposed in logs
- ✅ Only accessible to your repository
- ✅ Encrypted at rest

---

## 🎯 Next Steps

Once deployed:

1. **Test immediately**: Use workflow_dispatch to trigger manually
2. **Wait for 8pm**: Verify automatic run works
3. **Check user notifications**: Log in as test user to see reminder
4. **Monitor for a week**: Ensure consistent daily execution

---

## 📝 Additional Notes

### Local Development
For local testing, use the `send_mood_reminders.sh` script:
```bash
./send_mood_reminders.sh
```

### Production
GitHub Actions automatically handles production reminders.

### Multiple Environments
To support staging/production:
1. Create separate secrets: `RAILWAY_APP_URL_STAGING`, `RAILWAY_APP_URL_PROD`
2. Create separate workflows for each environment
3. Adjust cron schedules if needed
