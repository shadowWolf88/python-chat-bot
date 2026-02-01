# Railway Environment Variables - Required Setup

## ✅ REQUIRED Variables (App won't work without these)

### 1. GROQ_API_KEY
- **Purpose:** AI chat functionality
- **Where to get:** https://console.groq.com/keys
- **Example:** `gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Critical:** Without this, AI therapy chat will not work

### 2. PIN_SALT
- **Purpose:** Secure PIN hashing for users
- **Value:** Any random secure string (16+ characters)
- **Example:** `mysecure_salt_2026_random_string`
- **Critical:** Without this, users cannot login with PINs

### 3. ENCRYPTION_KEY
- **Purpose:** Encrypt sensitive data in database
- **Format:** Must be a valid Fernet key (Base64, 32 bytes)
- **Generate with:**
  ```python
  from cryptography.fernet import Fernet
  print(Fernet.generate_key().decode())
  ```
- **Example:** `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6=`
- **Critical:** Without this, data encryption fails

### 4. PORT
- **Purpose:** Railway assigns this automatically
- **Value:** Usually `5000` or auto-assigned by Railway
- **Note:** You don't need to set this manually - Railway handles it

### 5. DEBUG
- **Purpose:** Control debug mode (0 = production, 1 = development)
- **Value:** `0` for production on Railway
- **Example:** `DEBUG=0`

---

## 🔧 OPTIONAL Variables (App works without, but features may be limited)

### Email Notifications (for appointment reminders, password reset)
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=noreply@yourapp.com
APP_URL=https://your-railway-app.up.railway.app
```

### SMS Notifications (Twilio integration)
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

### Safety Alerts (Webhook for crisis situations)
```env
ALERT_WEBHOOK_URL=https://hooks.slack.com/services/xxx
```

### Vault (if using HashiCorp Vault for secrets)
```env
VAULT_ADDR=https://vault.example.com
VAULT_TOKEN=your_vault_token
```

### API Configuration
```env
API_URL=https://api.groq.com/openai/v1/chat/completions
```

---

## 🚨 Common Railway Setup Issues

### Issue 1: App crashes with "No module named 'cryptography'"
**Fix:** Ensure `requirements.txt` or `requirements-pinned.txt` is in root directory

### Issue 2: Database data disappears after redeploy
**Fix:** Add a Railway Volume mounted to `/app/data` and update DB path in code, OR migrate to PostgreSQL

### Issue 3: "GROQ_API_KEY not found" errors
**Fix:** Go to Railway Dashboard → Your Service → Variables → Add `GROQ_API_KEY`

### Issue 4: Multiple services connected to same project
**Fix:** 
1. Each Railway project should have ONE service
2. If you connected another repo, create a NEW Railway project
3. Keep this app (python-chat-bot) in its OWN Railway project
4. Keep your learning bot in a SEPARATE Railway project

---

## 📋 Quick Verification Checklist

After setting variables in Railway, verify:

- [ ] `GROQ_API_KEY` is set and valid
- [ ] `PIN_SALT` is set (any secure random string)
- [ ] `ENCRYPTION_KEY` is set (valid Fernet key)
- [ ] `DEBUG=0` for production
- [ ] Service is deployed and running
- [ ] No build errors in Railway logs
- [ ] Health check passes: `https://your-app.up.railway.app/api/health`

---

## 🔑 How to Generate Required Keys

### Generate ENCRYPTION_KEY (run locally):
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Generate PIN_SALT:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🎯 Recommended Railway Setup

**Project Structure:**
```
Railway Project: Mental Health Chatbot
  └─ Service: python-chat-bot (this repo)
      └─ Variables: GROQ_API_KEY, PIN_SALT, ENCRYPTION_KEY, DEBUG=0
      └─ Domain: your-app.up.railway.app
      └─ Volume (optional): /app/data for persistent SQLite

Railway Project: Learning Bot (separate project!)
  └─ Service: your-learning-bot-repo
      └─ Its own variables
      └─ Its own domain
```

**DO NOT mix services from different repos in the same Railway project!**

---

## 🆘 If Things Are Broken

1. **Check Railway Logs:**
   - Railway Dashboard → Your Service → Deployments → Click latest → View Logs
   - Look for errors like "KeyError: GROQ_API_KEY" or "Fernet key must be 32 url-safe base64-encoded bytes"

2. **Verify Variables:**
   - Railway Dashboard → Your Service → Variables
   - Ensure GROQ_API_KEY, PIN_SALT, ENCRYPTION_KEY are all present

3. **Separate Repos:**
   - If you connected another repo to the same project, create a NEW Railway project
   - Redeploy this app (python-chat-bot) to its own project

4. **Test Locally First:**
   ```bash
   export GROQ_API_KEY="your_key"
   export PIN_SALT="your_salt"
   export ENCRYPTION_KEY="your_key"
   export DEBUG=1
   python3 api.py
   # Visit http://localhost:5000/api/health
   ```

---

## 📞 Need Help?

If things still aren't working:
1. Share Railway deployment logs
2. Confirm which variables are currently set
3. Describe the error you're seeing
