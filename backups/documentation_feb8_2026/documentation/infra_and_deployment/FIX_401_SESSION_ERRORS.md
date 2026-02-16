# Fix 401 Unauthorized Session Errors on Production

## Problem

You're getting **HTTP 401 Unauthorized** errors on multiple endpoints:
- `/api/messages/inbox`
- `/api/home/data`
- `/api/feedback`
- And other protected endpoints

Session cookies ARE being sent from the browser (visible in request headers), but the API rejects them.

## Root Cause

**Missing `SECRET_KEY` environment variable on Railway.**

Flask uses the `SECRET_KEY` to **encrypt and decrypt session cookies**. Without this:

1. The app generates a temporary key using the container hostname
2. When the container restarts (redeploy, scaling, server restart), the hostname changes
3. The SECRET_KEY changes
4. All existing session cookies become **unencryptable** (Flask can't decrypt them)
5. Users see 401 Unauthorized errors

## Solution

### Step 1: Generate a Secure SECRET_KEY

Run this command locally:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Example output:**
```
VyuBxj_oO69TcSj81wguirrLsK3f7F9JioFrGeSTHqI
```

**Copy this value** - you'll need it in the next step.

### Step 2: Add SECRET_KEY to Railway

1. Go to **Railway Dashboard**
2. Select your **Healing Space** service/project
3. Click **Variables** (or Variables tab)
4. Click **+ New Variable**
5. Set:
   - **Key:** `SECRET_KEY`
   - **Value:** Paste the key you generated above
6. Click **Save** or **Update**

### Step 3: Redeploy the App

After adding the variable, Railway will automatically redeploy. Monitor the logs to ensure:
- ✅ Deployment succeeds
- ✅ No "SECRET_KEY not set" warning messages
- ✅ App starts without errors

### Step 4: Test

1. Log in as a patient/user
2. Click the **Messages** tab
3. Verify you can see your inbox without 401 errors
4. Send a test message
5. Try other endpoints like `/api/home/data`

## Why This Happened

The `api.py` code at lines 84-95 has a fallback for missing SECRET_KEY:

```python
# CRITICAL: SECRET_KEY must be persistent across app restarts
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    print("⚠️  WARNING: SECRET_KEY not set in environment...")
    # Generate a temporary key based on hostname
    hostname = socket.gethostname()
    SECRET_KEY = hashlib.sha256(hostname.encode()).hexdigest()[:32]
```

**The fallback breaks on production** because:
- Containers are ephemeral (temporary)
- Hostnames change with each restart
- Session keys become invalid

## Prevention

Add `SECRET_KEY` to **REQUIRED environment variables** for all deployments:

- ✅ **Development:** Set locally before running `python3 api.py`
- ✅ **Production (Railway):** Add to Variables tab
- ✅ **Testing:** Add to pytest fixtures or env

## Verification

After deploying, check that the warning is gone:

1. Railway Dashboard → Deployments → Latest Deployment → Logs
2. Search for "SECRET_KEY"
3. Should NOT see: `⚠️  WARNING: SECRET_KEY not set in environment`
4. Should see app starting normally

## Fallback Troubleshooting

If users still get 401 errors after adding SECRET_KEY:

1. **Wait 2-3 minutes** for Railway to finish redeploy
2. **Clear browser cookies**: Press Ctrl+Shift+Delete → Clear browsing data → Cookies
3. **Log in again** to create new session with new key
4. **Test messaging again**

If still failing:

1. Verify the `SECRET_KEY` value was saved (check Railway Variables page)
2. Check that `DEBUG=0` (not development mode)
3. Confirm `/api/health` endpoint returns 200 OK
4. Contact support with Railway logs

## Security Notes

- ✅ The SECRET_KEY is safe to share in deployment instructions (not sensitive)
- ✅ Each deployment can use a different SECRET_KEY
- ✅ Users only need to log in once per SECRET_KEY change
- ✅ This is Flask best practice for production deployments

## Summary

| Issue | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Missing SECRET_KEY | Add to Railway Variables |
| Sessions invalid after restart | Hostname-based key changes | Persistent SECRET_KEY env var |
| Fallback key generation | Temporary workaround in code | Use env var instead |

**Status:** Ready to deploy - just add the `SECRET_KEY` variable to Railway.
