# 🚂 Deploy to Railway - Quick Guide

**Date:** January 17, 2026  
**Status:** Ready to Deploy

---

## ⚠️ Important: Desktop vs Web App

This project has **TWO components**:

1. **Desktop App (main.py)** - Tkinter GUI for local use
2. **Web API (api.py)** - Flask REST API for Railway deployment

**Railway can ONLY host the Web API**, not the desktop GUI.

---

## 🚀 Quick Deploy to Railway

### Option 1: Deploy via Railway CLI (Fastest)

```bash
# 1. Install Railway CLI
npm i -g @railway/cli
# or: brew install railway

# 2. Login to Railway
railway login

# 3. Initialize project
cd "/home/computer001/Documents/Healing Space UK"
railway init

# 4. Link to Railway project (if exists) or create new
railway link

# 5. Deploy!
railway up

# 6. Add environment variables
railway variables set GROQ_API_KEY="your_groq_api_key"
railway variables set PIN_SALT="your_pin_salt_here"
railway variables set ENCRYPTION_KEY="your_encryption_key"
railway variables set DEBUG="0"

# 7. Open in browser
railway open
```

---

### Option 2: Deploy via GitHub (Recommended)

#### Step 1: Connect GitHub to Railway

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose: **`shadowWolf88/python-chat-bot`**
5. Railway will auto-detect Python and deploy

#### Step 2: Configure Environment Variables

In Railway Dashboard → Variables, add:

```env
GROQ_API_KEY=your_groq_api_key_here
PIN_SALT=your_secure_pin_salt
ENCRYPTION_KEY=your_fernet_encryption_key
DEBUG=0
API_URL=https://api.groq.com/openai/v1/chat/completions

# Optional (for email notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Optional (for SMS)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890

# Optional (for alerts)
ALERT_WEBHOOK_URL=your_webhook_url
```

#### Step 3: Add Database Volume (Persistent Storage)

Railway's filesystem is **ephemeral** - data is lost on redeploy!

**Add a Volume:**
1. In Railway Dashboard → Storage
2. Click **"+ New Volume"**
3. Mount path: `/app/data`
4. Restart service

**Or use PostgreSQL:**
1. Click **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Railway will provide `DATABASE_URL`
3. Update code to use PostgreSQL (see migration guide below)

#### Step 4: Check Deployment

```bash
# Your app will be available at:
https://your-app-name.railway.app

# Health check:
https://your-app-name.railway.app/api/health

# Web interface:
https://your-app-name.railway.app/
```

---

## 📁 Files Already Configured

✅ **Procfile** - Tells Railway how to start the app
```
web: gunicorn api:app
```

✅ **railway.toml** - Railway configuration
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "gunicorn api:app"
```

✅ **requirements.txt** - Python dependencies

✅ **api.py** - Web server with health check endpoint

---

## 🔧 What Gets Deployed

When you deploy to Railway, you get:

### ✅ Web Interface (`templates/index.html`)
- Full therapy chat interface
- Mood tracking
- Gratitude journal
- CBT tools
- Safety plan
- Progress insights

### ✅ REST API Endpoints (`api.py`)

**Authentication:**
- `POST /api/signup` - Create account
- `POST /api/login` - User login

**Therapy:**
- `POST /api/chat` - Send message to AI therapist
- `GET /api/sessions` - List therapy sessions
- `POST /api/session/new` - Create new session

**Mood & Health:**
- `POST /api/mood` - Log mood entry
- `GET /api/mood/history` - Get mood logs
- `POST /api/gratitude` - Add gratitude entry

**Clinical:**
- `POST /api/clinical/phq9` - Submit PHQ-9 assessment
- `POST /api/clinical/gad7` - Submit GAD-7 assessment
- `GET /api/clinical/scores` - Get assessment history

**Safety:**
- `POST /api/safety-plan` - Save safety plan
- `GET /api/safety-plan` - Get safety plan
- `POST /api/panic` - Trigger panic button

**Export:**
- `GET /api/export/csv` - Export data as CSV
- `GET /api/export/fhir` - Export as FHIR bundle

**Health:**
- `GET /api/health` - Service health check

### ❌ NOT Deployed (Desktop Only)
- Tkinter GUI (main.py)
- Pet game with graphics
- Desktop notifications
- TTS (text-to-speech)
- Local file dialogs

---

## 🗄️ Database Options

### Option 1: SQLite with Volume (Simple)

**Pros:**
- No code changes needed
- Quick setup
- Free

**Cons:**
- Lost on volume deletion
- Not scalable
- Single instance only

**Setup:**
1. Railway Dashboard → Storage → + New Volume
2. Mount path: `/app/data`
3. Restart service

### Option 2: PostgreSQL (Recommended)

**Pros:**
- Persistent
- Scalable
- Multiple instances
- Automatic backups

**Cons:**
- Requires code migration
- Railway charges after free tier

**Setup:**
1. Railway Dashboard → + New → Database → PostgreSQL
2. Get `DATABASE_URL` from variables
3. Migrate code (see below)

---

## 🔄 PostgreSQL Migration Guide

If you want to use PostgreSQL instead of SQLite:

### 1. Install Dependencies

Add to `requirements.txt`:
```txt
psycopg2-binary
sqlalchemy
```

### 2. Update Database Connection

Replace SQLite connections in `api.py`:

```python
# OLD (SQLite)
conn = sqlite3.connect("therapist_app.db")

# NEW (PostgreSQL)
import psycopg2
from urllib.parse import urlparse

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # PostgreSQL
        conn = psycopg2.connect(database_url)
        return conn
    else:
        # Fallback to SQLite
        return sqlite3.connect("therapist_app.db")
```

### 3. Update SQL Syntax

PostgreSQL differences:
- `?` → `%s` for parameters
- `INTEGER PRIMARY KEY AUTOINCREMENT` → `SERIAL PRIMARY KEY`
- `datetime()` → `NOW()`
- `DATETIME DEFAULT CURRENT_TIMESTAMP` → `TIMESTAMP DEFAULT NOW()`

### 4. Migrate Data

```bash
# Export from SQLite
sqlite3 therapist_app.db .dump > backup.sql

# Import to PostgreSQL (after converting syntax)
psql $DATABASE_URL < migrated_backup.sql
```

---

## 🔐 Environment Variables Reference

### Required:
- `GROQ_API_KEY` - AI API key (get from groq.com)
- `PIN_SALT` - Salt for PIN hashing (generate securely)
- `ENCRYPTION_KEY` - Fernet key for data encryption (generate with `Fernet.generate_key()`)

### Generate Encryption Key:
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

### Generate PIN Salt:
```python
import secrets
print(secrets.token_urlsafe(32))
```

### Optional:
- `DEBUG` - Set to `0` for production
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USER`, `EMAIL_PASSWORD` - Email alerts
- `TWILIO_*` - SMS notifications
- `ALERT_WEBHOOK_URL` - Webhook for crisis alerts
- `ADMIN_PASSWORD` - Admin/clinician dashboard access

---

## 📊 Monitoring & Logs

### View Logs:
```bash
# Via CLI
railway logs

# Via Dashboard
Railway Dashboard → Deployments → View Logs
```

### Health Check:
```bash
curl https://your-app.railway.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-01-17T12:00:00"
}
```

---

## 🚨 Troubleshooting

### "Application failed to respond"
**Fix:** Check logs for errors
```bash
railway logs
```

### "Module not found"
**Fix:** Ensure all dependencies in `requirements.txt`
```bash
railway logs | grep "ModuleNotFoundError"
```

### "Database locked"
**Fix:** Use PostgreSQL instead of SQLite for production
- SQLite doesn't handle concurrent connections well

### "502 Bad Gateway"
**Fix:** Check if app is binding to correct port
```python
# api.py should have:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

### Data Loss After Redeploy
**Fix:** Add a Volume or use PostgreSQL

---

## 🔄 Continuous Deployment

Railway auto-deploys when you push to GitHub:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin main

# Railway automatically:
# 1. Detects push
# 2. Builds new image
# 3. Deploys
# 4. Health checks
# 5. Switches traffic
```

---

## 💰 Railway Pricing

**Free Tier (Hobby Plan):**
- $5 free credit per month
- Suitable for testing
- Sleeps after inactivity

**Paid Plans:**
- Usage-based pricing
- Starts ~$5-20/month
- No sleep mode
- Better performance

**Estimated Costs for This App:**
- Small traffic: $5-10/month
- Medium traffic: $20-40/month
- Includes: Compute + Database + Bandwidth

---

## 📝 Deployment Checklist

Before deploying:

- [ ] Commit all code to GitHub
- [ ] Push to main branch: `git push origin main`
- [ ] Create Railway account at [railway.app](https://railway.app)
- [ ] Connect GitHub repo
- [ ] Add environment variables (GROQ_API_KEY, PIN_SALT, ENCRYPTION_KEY)
- [ ] Add database volume or PostgreSQL
- [ ] Test health endpoint: `/api/health`
- [ ] Test web interface: `/`
- [ ] Check logs for errors
- [ ] Set up monitoring/alerts
- [ ] Document your app URL

After deploying:

- [ ] Test user signup
- [ ] Test login
- [ ] Test AI chat
- [ ] Test mood logging
- [ ] Verify data persistence (add entry, redeploy, check if still there)
- [ ] Test on mobile device
- [ ] Set up custom domain (optional)

---

## 🌐 Custom Domain (Optional)

1. Railway Dashboard → Settings → Domains
2. Click **"Generate Domain"** (free .railway.app subdomain)
3. Or add custom domain:
   - Add CNAME record: `your-domain.com` → `your-app.railway.app`
   - Verify in Railway

---

## 🔗 Useful Links

- **Railway Dashboard:** https://railway.app/dashboard
- **Railway Docs:** https://docs.railway.app
- **Your Repo:** https://github.com/shadowWolf88/python-chat-bot
- **Groq API:** https://console.groq.com/keys

---

## 🆘 Need Help?

### Check Logs First:
```bash
railway logs --tail 100
```

### Common Issues:
1. **503 errors** → Check if service is running
2. **Database errors** → Add volume or use PostgreSQL
3. **Module errors** → Update requirements.txt
4. **Auth errors** → Set environment variables
5. **AI not responding** → Check GROQ_API_KEY

### Documentation:
- [DEPLOYMENT.md](documentation/DEPLOYMENT.md) - Detailed deployment guide
- [RAILWAY_GUIDE.md](documentation/RAILWAY_GUIDE.md) - Railway-specific guide
- [00_INDEX.md](documentation/00_INDEX.md) - Complete system documentation

---

## 🎉 Success!

Once deployed, share your app:
```
🌐 Web App: https://your-app.railway.app
📊 Health: https://your-app.railway.app/api/health
📱 Mobile-friendly interface included
```

**Note:** The desktop app (main.py) is for local use only. Railway hosts the web version (api.py).

---

**Last Updated:** January 17, 2026  
**Ready to Deploy:** ✅ YES  
**All Files Configured:** ✅ YES
