# 🚀 Railway Deployment Checklist

## ✅ Pre-Deployment (Done)
- [x] All changes committed to GitHub
- [x] GitHub Actions workflow created
- [x] Documentation updated
- [x] Code pushed to main branch

---

## 📋 Next Steps (Do These Now)

### 1. Set Up GitHub Secret (1 minute)

1. Go to: https://github.com/shadowWolf88/python-chat-bot/settings/secrets/actions
2. Click **"New repository secret"**
3. Name: `RAILWAY_APP_URL`
4. Value: Your Railway app URL (get from Railway dashboard)
   - Format: `https://your-app-name.railway.app`
   - **Important**: No trailing slash!
5. Click **"Add secret"**

### 2. Railway Should Auto-Deploy

Railway monitors your GitHub repo and will automatically deploy when you push.

**Check deployment status:**
1. Go to: https://railway.app/dashboard
2. Select your project
3. Watch the deployment logs
4. Wait for "Deployment successful" message

### 3. Verify Deployment (2 minutes)

Test the reminder endpoint:
```bash
# Replace with your actual Railway URL
curl -X POST https://your-app-name.railway.app/api/mood/check-reminder \
  -H "Content-Type: application/json" \
  -d '{"force": true}'
```

Expected response:
```json
{
  "success": true,
  "reminders_sent": 0,
  "message": "Sent 0 mood reminders"
}
```

### 4. Test GitHub Actions (2 minutes)

1. Go to: https://github.com/shadowWolf88/python-chat-bot/actions
2. Click **"Daily Mood Reminders"**
3. Click **"Run workflow"** dropdown
4. Click **"Run workflow"** button
5. Wait 30 seconds and refresh
6. Click on the workflow run to see logs
7. Verify it shows "✅ Reminders sent successfully"

---

## 🎯 What Happens Now

### Automatic Daily Reminders
- **Time**: 8pm UTC (adjust in workflow file if needed)
- **Frequency**: Every day
- **How**: GitHub Actions calls your Railway app
- **Logs**: Available in GitHub Actions tab
- **Cost**: FREE (within GitHub's free tier)

### For UK Time (GMT/BST)
- **Winter (GMT)**: 8pm GMT = 8pm UTC ✅ (current setting)
- **Summer (BST)**: 8pm BST = 7pm UTC (change to `0 19 * * *`)

---

## 🔍 Verification Commands

### Check Railway deployment:
```bash
# Health check
curl https://your-app-name.railway.app/api/health

# Check specific user's mood status
curl "https://your-app-name.railway.app/api/mood/check-today?username=testuser"
```

### Check GitHub Actions:
- Dashboard: https://github.com/shadowWolf88/python-chat-bot/actions
- Workflow file: `.github/workflows/mood-reminders.yml`

### Check logs in Railway:
1. Railway Dashboard → Your Project
2. Click on "Deployments"
3. Click on latest deployment
4. View logs for any errors

---

## 🐛 Troubleshooting

### Railway not deploying?
```bash
# Force a deployment by making a small change
git commit --allow-empty -m "Trigger Railway deployment"
git push origin main
```

### GitHub Actions not running?
1. Check Settings → Actions → General
2. Ensure "Allow all actions and reusable workflows" is selected
3. Save if changed

### Wrong timezone?
Edit `.github/workflows/mood-reminders.yml` line 5:
```yaml
# Change this line:
- cron: '0 20 * * *'  # Current: 8pm UTC

# To your preferred time (examples):
- cron: '0 19 * * *'  # 7pm UTC (8pm BST UK summer)
- cron: '0 1 * * *'   # 1am UTC (8pm EST US)
- cron: '0 4 * * *'   # 4am UTC (8pm PST US)
```

Then commit and push:
```bash
git add .github/workflows/mood-reminders.yml
git commit -m "Update reminder time to match timezone"
git push origin main
```

---

## 📚 Documentation

- **Full setup guide**: [RAILWAY_REMINDERS.md](RAILWAY_REMINDERS.md)
- **Deployment guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Mood system details**: [MOOD_REMINDERS.md](MOOD_REMINDERS.md)
- **Local cron setup**: [CRON_SETUP.md](CRON_SETUP.md)

---

## ✨ All Done!

Once you complete steps 1-4 above:
- ✅ App deployed to Railway
- ✅ Daily reminders automated with GitHub Actions
- ✅ Users get notified at 8pm if they haven't logged mood
- ✅ One mood entry per day enforced
- ✅ 100% FREE solution

**Test it tonight at 8pm UTC to verify it works! 🎉**
