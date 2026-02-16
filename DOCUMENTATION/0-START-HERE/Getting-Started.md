# Getting Started - 5 Minute Guide

**Welcome to Healing Space!** This guide will help you get up and running in 5 minutes.

---

## ⚡ Quick Start (Choose Your Path)

### 🌐 Option 1: Try It Online (Recommended - 2 min)
Visit [healing-space.org.uk](https://healing-space.org.uk) and click "Sign Up"
- No installation needed
- See all features immediately
- Create an account in 2 minutes

### 💻 Option 2: Run Locally (10 min)
Want to run it on your computer for development or testing?

#### Prerequisites
- Python 3.10+
- PostgreSQL 14+ (for production-like testing)

#### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/shadowWolf88/Healing-Space-UK.git
cd "python chat bot"

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up PostgreSQL (choose one):

## Option A: Install PostgreSQL locally
# macOS: brew install postgresql
# Linux (Ubuntu): sudo apt install postgresql postgresql-contrib
# Windows: https://www.postgresql.org/download/windows/

# Start PostgreSQL service and create database:
# createdb healing_space_test
# psql -U postgres -c "ALTER USER postgres PASSWORD 'yourpassword';"

## Option B: Use Docker (easier)
docker run -d --name healing_space_db \
  -e POSTGRES_PASSWORD=healing_space_dev \
  -p 5432:5432 \
  postgres:15

# 5. Configure environment
cp .env.example .env

# Edit .env and add:
export DEBUG=1
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=healing_space_test
export DB_USER=postgres
export DB_PASSWORD=your_password  # or 'healing_space_dev' if using Docker
export GROQ_API_KEY=gsk_...  # Get free key from https://console.groq.com
export SECRET_KEY=your_random_secret_key
export ENCRYPTION_KEY=your_encryption_key  # Generate: python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 6. Run the application
python3 api.py

# 7. Visit http://localhost:5000 in your browser
# All tables will auto-create on startup
```

**Full setup guide:** [Developer Setup Guide](../6-DEVELOPMENT/Developer-Setup.md)  
**Local testing docs:** [Testing Guide](../6-DEVELOPMENT/Testing-Guide.md)

### 🚀 Option 3: Deploy to Production (Railway)
Want to deploy for real users?

See: [Railway Deployment](../5-DEPLOYMENT/Railway-Deployment.md) (takes ~10 minutes)

---

## 📝 First Steps After Sign Up

### Step 1: Create Your Account (1 min)
1. Click "Sign Up"
2. Enter email and password
3. Verify your email
4. Done! ✅

### Step 2: Complete Your Profile (2 min)
1. Click "My Profile"
2. Add your age and basic info
3. Set your preferences (email reminders, etc.)
4. Save ✅

### Step 3: Take a Risk Assessment (5 min)
1. Go to "Assessments"
2. Complete the C-SSRS (Suicide Risk Assessment)
3. Complete PHQ-9 (Depression) and GAD-7 (Anxiety)
4. See your risk level ✅

### Step 4: Try AI Chat (5 min)
1. Click "Therapy Chat"
2. Type: "I've been feeling anxious lately"
3. Chat with the AI therapist
4. See how it works ✅

### Step 5: Log Your Mood (2 min)
1. Click "Mood Tracking"
2. Rate your mood (1-10)
3. Add any notes
4. Track sleep and exercise too ✅

---

## 🎯 Core Features Overview

### 💬 AI Therapy Chat
Talk to an intelligent therapist anytime. The AI remembers your context and provides evidence-based responses.

**Try it**: Click "Therapy Chat" → Type something like:
- "I'm feeling depressed"
- "I can't sleep"
- "Help me with anxiety"

### 📊 Mood Tracking
Log your mood daily to see trends over time.

**Try it**: Click "Mood" → Rate 1-10 → See your chart

### 🎯 CBT Tools
Evidence-based tools for therapy homework:
- Goal setting
- Thought records
- Behavioral experiments
- Coping cards
- Safety planning

**Try it**: Click "CBT Tools" → Pick one → Get started

### 💬 Clinician Messaging
Send secure messages to your therapist (if you have one).

**Try it**: Click "Messages" → Compose → Send

### 📈 Mood & Risk Dashboard
See your progress at a glance.

**Try it**: Click "Dashboard" → See your stats

---

## 🆘 Safety Features

**If you're in crisis:**
1. Click the **SOS** button (red, top right)
2. See emergency contacts
3. Call 999 (UK) or text 50808 (Shout crisis text line)

**The AI will:**
- Detect crisis keywords in your messages
- Alert your clinician if you're registered with one
- Provide crisis resources

---

## ❓ How to Get Help

### In-App Help
- Click **?** icon in top-right corner
- See tutorials for each feature

### Documentation
- **Patient Guide**: [Patient-Guide.md](../1-USER-GUIDES/Patient-Guide.md)
- **FAQ**: [FAQ.md](../1-USER-GUIDES/FAQ.md)
- **Troubleshooting**: [Troubleshooting.md](../1-USER-GUIDES/Troubleshooting.md)

### Contact Support
- Email: [support@healing-space.org.uk](mailto:support@healing-space.org.uk)
- Message clinician directly (if registered)
- See [Crisis Support](#safety-features) for emergencies

---

## 🔐 Privacy & Security

**Your data is protected:**
- ✅ All communication encrypted (HTTPS)
- ✅ Password secured with encryption
- ✅ You can request to download your data anytime
- ✅ You can delete your account and all data
- ✅ GDPR compliant

**Read more**: [Data Protection](../2-NHS-COMPLIANCE/Data-Protection-Impact-Assessment.md)

---

## 🎓 Next Steps

**Are you a:**

👤 **Patient wanting to learn more?**  
→ [Patient Guide](../1-USER-GUIDES/Patient-Guide.md)

👨‍⚕️ **Clinician registering patients?**  
→ [Clinician Guide](../1-USER-GUIDES/Clinician-Guide.md)

👨‍💻 **Developer wanting to understand the code?**  
→ [Architecture Overview](../4-TECHNICAL/Architecture-Overview.md)

🏥 **NHS organization considering deployment?**  
→ [NHS Readiness Checklist](../2-NHS-COMPLIANCE/NHS-Readiness-Checklist.md)

🎓 **Researcher running a trial?**  
→ [University Readiness Checklist](../3-UNIVERSITY-TRIALS/University-Readiness-Checklist.md)

---

## ⏱️ Typical Daily Use (15 minutes)

**What a typical user might do:**

1. **Log mood** (2 min)
   - Rate how you're feeling
   - Note any changes

2. **Chat with AI** (10 min)
   - Discuss what's on your mind
   - Get therapy suggestions
   - Practice coping skills

3. **Do a CBT exercise** (5 min)
   - Complete homework from therapist
   - Or work on your own goals

4. **Check alerts** (1 min)
   - See if clinician messaged you
   - View upcoming appointments

**Total: 15-20 minutes, totally optional!**

---

## 🚀 You're Ready!

**Let's get started:**

1. ✅ Sign up at [healing-space.org.uk](https://healing-space.org.uk)
2. ✅ Complete your profile
3. ✅ Take the C-SSRS assessment
4. ✅ Try AI chat
5. ✅ Log your mood

**Questions?** See [FAQ](../1-USER-GUIDES/FAQ.md)  
**Having issues?** See [Troubleshooting](../1-USER-GUIDES/Troubleshooting.md)  
**Want more details?** Read [Patient Guide](../1-USER-GUIDES/Patient-Guide.md)

---

**Welcome aboard! 🌿**

Last Updated: February 8, 2026
