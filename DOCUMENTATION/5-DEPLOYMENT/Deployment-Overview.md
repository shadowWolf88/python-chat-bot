# Deployment Guide

## GitHub Setup

1. **Initialize Git repository** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Create GitHub repository**:
   - Go to https://github.com/new
   - Create a new repository (public or private)
   - Copy the repository URL

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/shadowWolf88/python-chat-bot.git
   git branch -M main
   git push -u origin main
   ```

## Railway Deployment

### Prerequisites
- Railway account (https://railway.app)
- GitHub repository created and pushed

### Step 1: Create Railway Project

1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will auto-detect Python and use the `Procfile`

### Step 2: Configure Environment Variables

In Railway dashboard, go to your project's Variables tab and add:

#### Required Variables
```
DEBUG=0
PIN_SALT=<generate-secure-random-string>
ENCRYPTION_KEY=<generate-fernet-key>
GROQ_API_KEY=<your-groq-api-key>
```

#### Optional Variables (for production features)
```
# HashiCorp Vault (optional)
VAULT_ADDR=https://your-vault-server.com
VAULT_TOKEN=<your-vault-token>

# SFTP Export (optional)
SFTP_HOST=sftp.example.com
SFTP_PORT=22
SFTP_USER=username
SFTP_PASS=password
SFTP_PKEY_PATH=/path/to/key
SFTP_REMOTE_DIR=/uploads

# Webhook Alerts (optional)
ALERT_WEBHOOK_URL=https://hooks.slack.com/your-webhook
API_URL=https://api.groq.com/openai/v1/chat/completions
```

### Step 3: Generate Secure Keys

Run these commands locally to generate secure keys:

#### Generate ENCRYPTION_KEY (Fernet):
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

#### Generate PIN_SALT (random string):
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 4: Database Persistence

⚠️ **Important**: Railway's ephemeral filesystem means SQLite databases will reset on each deployment.

**Solutions:**

1. **Railway Volumes** (Recommended):
   - In Railway dashboard, go to Settings → Volumes
   - Add a volume mounted at `/app/data`
   - Update `main.py` to use `/app/data/therapist_app.db`
   - Update `pet_game.py` to use `/app/data/pet_game.db`

2. **External Database** (Production):
   - Migrate to PostgreSQL (Railway provides free PostgreSQL)
   - Use Railway's PostgreSQL plugin
   - Modify code to use PostgreSQL instead of SQLite

3. **Cloud Storage Backup**:
   - Implement periodic backups to S3/Cloud Storage
   - Use existing backup mechanism in `backups/` directory

### Step 5: Deploy

1. Railway will automatically deploy on push to GitHub
2. Monitor logs in Railway dashboard
3. Check deployment status and errors

### Step 6: Set Up 8pm Mood Reminders

After deploying to Railway, set up automated mood reminders:

1. **Add GitHub Secret**:
   - Go to your GitHub repo → Settings → Secrets and variables → Actions
   - Add secret: `RAILWAY_APP_URL` = `https://your-app.railway.app`

2. **Enable GitHub Actions**:
   - The workflow is already in `.github/workflows/mood-reminders.yml`
   - It will automatically run at 8pm UTC daily
   - Test it manually from Actions tab

3. **Verify**:
   ```bash
   curl -X POST https://your-app.railway.app/api/mood/check-reminder \
     -H "Content-Type: application/json" \
     -d '{"force": true}'
   ```

📖 See [RAILWAY_REMINDERS.md](RAILWAY_REMINDERS.md) for detailed setup instructions.

### Step 7: Custom Domain (Optional)

1. In Railway dashboard, go to Settings → Domains
2. Click "Generate Domain" for free Railway subdomain
3. Or add your custom domain

## Desktop Application Consideration

⚠️ **Note**: This is a **desktop GUI application** using Tkinter/CustomTkinter. Railway is designed for web services.

**Options:**

1. **Convert to Web App**:
   - Replace Tkinter with Flask/FastAPI + React/Vue frontend
   - Keep backend logic, rebuild UI for web

2. **Desktop Distribution** (Better suited):
   - Use PyInstaller to create executables
   - Distribute via GitHub Releases
   - Users run locally with their own environment variables

3. **Hybrid Approach**:
   - Deploy API backend to Railway
   - Keep desktop GUI that connects to Railway API
   - Separates UI from data processing

## Recommended: Desktop Distribution

For a Tkinter app, consider this workflow instead:

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed \
  --add-data "requirements.txt:." \
  --name HealingSpace \
  main.py

# Distribute via GitHub Releases
```

Then create releases on GitHub with executables for different platforms.

## Environment Variables Security

- Never commit `.env` files or secrets to GitHub
- Use Railway's environment variables for production
- For local development, create `.env` file (already in `.gitignore`)
- Document all required variables in this file

## Monitoring & Logs

- **Railway Logs**: View real-time logs in Railway dashboard
- **Audit Logs**: Check `audit_logs` table in database
- **Alerts**: Configure `ALERT_WEBHOOK_URL` for crisis notifications

## Troubleshooting

### Database not persisting
- Add Railway volume (see Step 4)
- Or migrate to PostgreSQL

### Missing dependencies
- Ensure `requirements.txt` includes all packages
- Railway auto-installs from `requirements.txt`

### Tkinter display issues on Railway
- Tkinter requires X11/display server
- Railway doesn't provide GUI display
- Consider web conversion or local distribution

## Production Checklist

- [ ] All secrets configured in Railway
- [ ] Database persistence solution implemented
- [ ] `DEBUG=0` in production
- [ ] Vault integration configured (if using)
- [ ] SFTP credentials secured (if using)
- [ ] Webhook alerts tested
- [ ] Backups scheduled
- [ ] Monitoring setup
- [ ] Error tracking configured
- [ ] Consider architecture: Desktop vs Web

## Support

For issues, check:
- Railway logs for deployment errors
- `.github/copilot-instructions.md` for development guide
- Tests in `tests/test_app.py` for examples
