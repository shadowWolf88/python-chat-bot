# GitHub Webhook Manual Setup for Railway Auto-Deploy

**Problem**: No webhook found in GitHub for Railway auto-deploy  
**Solution**: Set up manually through Railway web dashboard

---

## Quick Setup (5 minutes)

### Step 1: Open Railway Dashboard
```
https://railway.app
```

Login with your GitHub account (it should show your projects)

### Step 2: Select Your Project
Look for: **"Healing Space"** or **"Healing Space Main"**
Click to open the project

### Step 3: Connect GitHub Repository

In the project page, look for one of these:
- **"Source"** section at the top
- **"Deploy"** or **"GitHub"** tab
- **"Settings"** → **"Repository"** or **"Git"**

Click the option to **"Connect Repository"** or **"Link GitHub"**

### Step 4: Select Your Repository
When prompted:
1. **Organization**: `shadowWolf88`
2. **Repository**: `Healing-Space-UK`
3. **Branch**: `main`

### Step 5: Confirm
Click "Connect" or "Link" to complete

---

## Verify It's Working

### Check GitHub Webhook
Go to: https://github.com/shadowWolf88/Healing-Space-UK/settings/hooks

You should now see a **Railway webhook** with:
- ✅ Recent deliveries showing push events
- ✅ Green checkmarks on successful deliveries

### Test Auto-Deploy
Make a small test change and push:
```bash
echo "# Test $(date)" >> README.md
git add README.md
git commit -m "Test auto-deploy webhook"
git push origin main
```

Watch Railway logs:
```bash
railway logs
```

Within 30 seconds you should see:
- `Building...`
- New deployment activity
- App restart

---

## If Webhook Still Doesn't Appear

Try these alternatives:

### Option A: Use Railway up Command (Manual Deploy)
```bash
cd /home/computer001/Documents/python\ chat\ bot
railway up
```

This immediately deploys your current code without webhook.

### Option B: Redeploy from Railway Dashboard
1. Go to https://railway.app/project/[your-project-id]
2. Click "Redeploy" button
3. Wait for build to complete

### Option C: Check Railway Logs for Errors
```bash
railway logs | grep -i error
```

If you see database or deployment errors, investigate those first.

---

## What Auto-Deploy Does

Once webhook is set up:
- Every push to `main` branch automatically triggers deployment
- Railway pulls latest code from GitHub
- Runs build (nixpacks detects Python)
- Deploys to production
- No manual intervention needed

---

## Troubleshooting

### Webhook Not Triggering?
- Verify GitHub webhook exists and has recent deliveries
- Check Railway project is set to main branch
- Try manual deployment with `railway up`

### Deploy Fails?
- Check Railway logs: `railway logs`
- Look for build errors (Python import, missing dependencies)
- Check environment variables: `railway variable list`

### Database Not Connecting?
- Look for: `✅ Database connection: SUCCESSFUL` in logs
- If FAILED, check `DATABASE_URL` is set correctly
- Verify PostgreSQL service is running

---

**Created**: February 4, 2026  
**For**: Healing Space UK deployment
