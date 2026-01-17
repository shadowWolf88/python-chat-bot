# Railway Deployment Guide

## ✅ Your App is Ready for Railway!

Your app now has **two modes**:
1. **Desktop App**: `python3 main.py` (works exactly as before)
2. **Web API**: `python3 api.py` (new, for Railway deployment)

## 🚂 Deploy to Railway

### Step 1: Create Railway Project

1. Go to https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository: `shadowWolf88/python-chat-bot`
5. Railway will auto-detect Python and use the Procfile

### Step 2: Configure Environment Variables

In Railway dashboard → Variables tab, add these:

```bash
DEBUG=0
GROQ_API_KEY=your_groq_api_key_here
ENCRYPTION_KEY=your_encryption_key_here
PIN_SALT=your_pin_salt_here
API_URL=https://api.groq.com/openai/v1/chat/completions
```

**Get your actual values from your local `.env` file.**

### Step 3: Add Railway Volume (For Database Persistence)

⚠️ **Important**: Railway's filesystem is ephemeral. To persist your SQLite database:

1. In Railway dashboard → **Settings → Volumes**
2. Click **"New Volume"**
3. Mount path: `/app/data`
4. Size: 1GB (free tier includes 1GB)

Then update your code to use the volume (I can do this if needed).

### Step 4: Deploy

1. Railway will automatically deploy when you push to GitHub
2. Monitor deployment in Railway dashboard → **Deployments** tab
3. Check logs for any errors

### Step 5: Get Your URL

1. In Railway dashboard → **Settings → Networking**
2. Click **"Generate Domain"** for a free Railway subdomain
3. Your API will be available at: `https://your-app.railway.app`

## 🧪 Testing Your Deployment

Once deployed, test these endpoints:

### Health Check
```bash
curl https://your-app.railway.app/api/health
```

### Register User
```bash
curl -X POST https://your-app.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "Test123!", "pin": "1234"}'
```

### AI Chat
```bash
curl -X POST https://your-app.railway.app/api/therapy/chat \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "message": "I feel anxious today"}'
```

### Log Mood
```bash
curl -X POST https://your-app.railway.app/api/mood/log \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "mood_val": 7, "sleep_val": 8, "notes": "Feeling good"}'
```

## 📋 Available API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web interface |
| GET | `/api/health` | Health check |
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login user |
| POST | `/api/therapy/chat` | AI therapy chat |
| POST | `/api/mood/log` | Log mood entry |
| GET | `/api/mood/history` | Get mood history |
| POST | `/api/gratitude/log` | Log gratitude |
| GET | `/api/export/fhir` | Export FHIR data |
| POST | `/api/safety/check` | Safety check |

## 🔒 Security Notes

- All passwords are hashed with Argon2/bcrypt
- Data is encrypted with Fernet (same as desktop app)
- Audit logging works the same way
- FHIR exports are HMAC-signed

## 🐛 Troubleshooting

### Database not persisting
- Add Railway volume (see Step 3 above)
- Or migrate to Railway PostgreSQL plugin

### API returns 500 errors
- Check Railway logs: Dashboard → Deployments → View Logs
- Verify environment variables are set correctly
- Check GROQ_API_KEY is valid

### Deployment fails
- Check Railway build logs
- Ensure `requirements.txt` is in root directory
- Verify Python version compatibility

## 📊 Monitoring

View real-time logs in Railway:
```
Dashboard → Your Project → Deployments → [Latest] → View Logs
```

## 💡 Next Steps

### Option 1: Keep API-Only
- Build mobile app or web frontend that calls your API
- Desktop app continues to work locally

### Option 2: Add Web UI
- I can create a React/Vue frontend
- Full web version of your desktop app
- Progressive Web App (PWA) support

### Option 3: Migrate to PostgreSQL
- Better for production than SQLite
- Railway provides free PostgreSQL
- I can help with migration script

## 🔄 Updating Your Deployment

Any time you push to GitHub, Railway will automatically redeploy:

```bash
# Make changes to your code
git add .
git commit -m "Your update message"
git push origin main
# Railway will auto-deploy in ~2 minutes
```

## ✅ What Stays the Same

- ✅ Desktop app (`python3 main.py`) works exactly as before
- ✅ All features: therapy, mood logs, pet game, CBT tools
- ✅ All encryption and security mechanisms
- ✅ Database schema and migrations
- ✅ Audit logging
- ✅ FHIR exports

## 📞 Need Help?

If deployment fails or you need assistance:
1. Check Railway logs for specific errors
2. Verify all environment variables
3. Test locally first: `python3 api.py` then visit http://localhost:5000

---

**Your app is now ready for Railway! 🚀**
