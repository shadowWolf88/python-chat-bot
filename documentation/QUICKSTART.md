# GitHub & Railway Deployment - Quick Reference

## ✅ Files Created

The following files have been created for GitHub and Railway deployment:

1. **`.gitignore`** - Excludes sensitive files, databases, and generated content
2. **`Procfile`** - Railway/Heroku process definition
3. **`railway.toml`** - Railway-specific configuration
4. **`.env.example`** - Template for environment variables
5. **`README.md`** - Project documentation
6. **`DEPLOYMENT.md`** - Comprehensive deployment guide
7. **`setup.sh`** - Automated setup script
8. **`.github/workflows/ci.yml`** - GitHub Actions CI/CD pipeline

## 🚀 Quick Start - GitHub

```bash
# 1. Review and add new files
git status
git add .gitignore README.md DEPLOYMENT.md .env.example Procfile railway.toml setup.sh .github/

# 2. Commit changes
git commit -m "Add deployment configuration for GitHub and Railway"

# 3. Create GitHub repository at https://github.com/new
# Then push your code:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## 🚂 Quick Start - Railway

### Option 1: Web Service (Requires Conversion)
Railway is designed for web services. Your app uses Tkinter (desktop GUI), which won't work directly.

**You need to either:**
1. Convert UI to web (Flask/FastAPI + React)
2. Create headless API mode
3. Skip Railway entirely (see Option 2)

### Option 2: Desktop Distribution (RECOMMENDED)
Since this is a desktop app, better options are:

```bash
# Install PyInstaller
pip install pyinstaller

# Create standalone executable
pyinstaller --onefile --windowed \
  --name "HealingSpace" \
  --add-data "requirements.txt:." \
  main.py

# Distribute via GitHub Releases
# Upload the executable from dist/ folder to GitHub Releases
```

## 🔑 Generate Required Keys

```bash
# Generate ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"

# Generate PIN_SALT
python3 -c "import secrets; print('PIN_SALT=' + secrets.token_urlsafe(32))"

# Get your Groq API key from: https://console.groq.com/keys
```

## 📝 Environment Variables for Railway

If you decide to convert to a web app, set these in Railway dashboard:

```
DEBUG=0
ENCRYPTION_KEY=<your-fernet-key>
PIN_SALT=<your-salt>
GROQ_API_KEY=<your-groq-key>
API_URL=https://api.groq.com/openai/v1/chat/completions
```

## ⚠️ Important Notes

1. **Database Persistence**: Railway's filesystem is ephemeral
   - Add Railway Volume for SQLite persistence
   - Or migrate to Railway's PostgreSQL

2. **Tkinter GUI**: Won't work on Railway without display server
   - Consider web conversion or desktop distribution

3. **Secrets Security**: Never commit `.env` file
   - Use Railway environment variables
   - Keep secrets out of code

## 📚 Next Steps

1. **Read DEPLOYMENT.md** for comprehensive deployment guide
2. **Run setup.sh** for automated local setup
3. **Choose deployment strategy**:
   - Desktop distribution via GitHub Releases (recommended)
   - Or web conversion for Railway deployment

## 🆘 Need Help?

- See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions
- Check [.github/copilot-instructions.md](.github/copilot-instructions.md) for development guide
- Review [tests/test_app.py](tests/test_app.py) for code examples

## 📊 CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`) will automatically:
- Run tests on push/PR
- Check security vulnerabilities
- Run code linting
- Generate reports

Configure secrets in GitHub repository settings:
- `TEST_ENCRYPTION_KEY` (optional, auto-generated if not set)
