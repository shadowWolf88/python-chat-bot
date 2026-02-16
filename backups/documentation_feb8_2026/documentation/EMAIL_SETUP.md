# Email Setup for Password Reset

## Why Emails Aren't Sending

The password reset feature requires SMTP credentials to send emails. Currently, these environment variables are not configured:

- `SMTP_USER` - Your Gmail address (e.g., yourapp@gmail.com)
- `SMTP_PASSWORD` - Your Gmail App Password (NOT your regular password)
- `SMTP_SERVER` - (optional, defaults to smtp.gmail.com)
- `SMTP_PORT` - (optional, defaults to 587)
- `FROM_EMAIL` - (optional, defaults to SMTP_USER)

## Gmail Setup Instructions

### 1. Enable 2-Factor Authentication
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification"

### 2. Create App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other (Custom name)"
3. Enter "Healing Space App"
4. Click "Generate"
5. **Copy the 16-character password** (shown once only)

### 3. Set Environment Variables

#### For Local Development:
```bash
export SMTP_USER="your.email@gmail.com"
export SMTP_PASSWORD="your-16-char-app-password"
export APP_URL="http://localhost:5000"
```

#### For Railway Deployment:
1. Go to Railway project settings
2. Add these variables:
   - `SMTP_USER`: your.email@gmail.com
   - `SMTP_PASSWORD`: your-16-char-app-password
   - `APP_URL`: https://your-app.up.railway.app

## Testing Email

After setting environment variables, restart the app and try:

```bash
curl -X POST http://localhost:5000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com"}'
```

Check console output for email errors.

## Alternative: Use Different Email Provider

### SendGrid (recommended for production):
```python
# In api.py, replace send_reset_email() with:
import sendgrid
from sendgrid.helpers.mail import Mail

sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
message = Mail(
    from_email='noreply@yourapp.com',
    to_emails=to_email,
    subject='Password Reset',
    html_content=html
)
sg.send(message)
```

## About Your Dr.Test Account

**I cannot retrieve your password** because passwords are securely hashed in the database. There are two options:

1. **Use the forgot password feature** (once emails are configured)
2. **Create a new account** with a password you remember
3. **Reset via database** (development only):

```python
# Run this to reset Dr.Test password to "newpassword123"
python3 -c "
import sqlite3
from main import hash_password
conn = sqlite3.connect('therapist_app.db')
new_hash = hash_password('newpassword123')
conn.execute('UPDATE users SET password_hash=? WHERE username=?', (new_hash, 'Dr.Test'))
conn.commit()
print('Password reset to: newpassword123')
"
```

## Security Note

Never commit SMTP credentials to Git. Always use environment variables or secrets management (HashiCorp Vault, Railway secrets, etc).
