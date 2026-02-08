# Railway Database Wipe Instructions

## Problem
When you wiped the local database, Railway still has its own separate database with old user data. That's why you're seeing "email in use" and "username in use" errors.

## Solution: Admin Database Wipe Tool

### Step 1: Set Admin Key in Railway
1. Go to Railway dashboard
2. Go to your project → Settings → Variables
3. Add new variable:
   - Name: `ADMIN_WIPE_KEY`
   - Value: `yourSecretKey123` (choose a strong secret)
4. Save and redeploy

### Step 2: Access the Admin Tool
After Railway redeploys, go to:
```
https://www.healing-space.org.uk/admin/wipe
```

### Step 3: Wipe the Database
1. Enter your `ADMIN_WIPE_KEY` secret
2. Click "WIPE DATABASE"
3. Confirm both warning prompts
4. Database will be wiped

### Alternative: Use curl/API directly

```bash
curl -X POST https://www.healing-space.org.uk/api/admin/wipe-database \
  -H "Content-Type: application/json" \
  -d '{"admin_key":"yourSecretKey123"}'
```

## What Gets Deleted
- ✅ All user accounts
- ✅ All patient-clinician relationships
- ✅ All chat history and sessions
- ✅ All mood logs
- ✅ All clinical assessments
- ✅ All appointments
- ✅ All notifications and alerts
- ✅ All audit logs

## What Stays Intact
- ✅ Database schema (all tables)
- ✅ Application code
- ✅ Configuration

## Security Features
- 🔐 Requires secret admin key
- 🔐 Key stored as environment variable
- 📝 Logs all wipe operations
- ⚠️ Requires double confirmation in web UI
- 🚫 Returns 403 if wrong key provided

## After Wiping
You can now:
1. Register fresh clinician accounts
2. Register fresh patient accounts
3. Create test data
4. Test all features

## Troubleshooting

**"Unauthorized - invalid admin key"**
- Check you set `ADMIN_WIPE_KEY` in Railway variables
- Ensure Railway redeployed after adding variable
- Verify you're using the exact key

**"Database wipe error"**
- Check Railway logs for details
- Verify database path is correct
- Ensure database isn't locked

**Page not loading**
- Ensure Railway deployed successfully
- Check Railway logs for startup errors
- Try accessing `/` first to verify app is running

## Local Testing
```bash
export ADMIN_WIPE_KEY=testkey123
python3 api.py

# Then visit http://localhost:5000/admin/wipe
```
