# 2FA Verification System Setup

## Overview
The system now supports **optional** 2-factor authentication during user signup via:
- ✉️ **Email** (using SMTP)
- 📱 **SMS** (using Twilio)

## How It Works

### 1. User Registration Flow
1. User enters registration details (email/phone)
2. User selects verification method (Email or SMS)
3. System sends 6-digit code
4. User enters code to verify
5. Registration completes after verification

### 2. API Endpoints

#### Send Verification Code
```bash
POST /api/auth/send-verification
{
  "identifier": "user@example.com",  # or phone "+1234567890"
  "method": "email"                  # or "sms"
}
```

#### Verify Code
```bash
POST /api/auth/verify-code
{
  "identifier": "user@example.com",
  "code": "123456"
}
```

#### Register (with verification)
```bash
POST /api/auth/register
{
  "username": "johndoe",
  "password": "SecurePass123!",
  "email": "user@example.com",
  "phone": "+1234567890",
  "verified_identifier": "user@example.com",  # The verified email/phone
  ...other fields
}
```

## Configuration

### Enable/Disable 2FA
Set environment variable:
```bash
REQUIRE_2FA_SIGNUP=1  # Enable (default: 0 = disabled)
```

### Email Setup (SMTP)
Required environment variables:
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
```

**Gmail Setup:**
1. Go to Google Account settings
2. Enable 2-Step Verification
3. Generate App Password
4. Use that password for `SMTP_PASSWORD`

### SMS Setup (Twilio)
Required environment variables:
```bash
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

**Twilio Setup:**
1. Sign up at https://www.twilio.com
2. Get free trial account ($15 credit)
3. Get phone number
4. Copy Account SID and Auth Token
5. Install library: `pip install twilio`

### Railway Deployment
Add these variables in Railway dashboard:
- Settings → Variables → Add all required env vars

## Database
New table created automatically:
```sql
CREATE TABLE verification_codes (
  id INTEGER PRIMARY KEY,
  identifier TEXT,           -- email or phone
  code TEXT,                 -- 6-digit code
  method TEXT,              -- 'email' or 'sms'
  created_at DATETIME,
  expires_at DATETIME,      -- 10 minutes from creation
  verified INTEGER          -- 0 or 1
)
```

## Testing Locally

### Test Email
```bash
# Set environment variables
export SMTP_USER=your-email@gmail.com
export SMTP_PASSWORD=your-app-password
export REQUIRE_2FA_SIGNUP=1

# Start server
python3 api.py

# Test with curl
curl -X POST http://localhost:5000/api/auth/send-verification \
  -H "Content-Type: application/json" \
  -d '{"identifier":"test@example.com","method":"email"}'
```

### Test SMS
```bash
# Add Twilio credentials
export TWILIO_ACCOUNT_SID=your_sid
export TWILIO_AUTH_TOKEN=your_token
export TWILIO_PHONE_NUMBER=+1234567890

# Install twilio
pip install twilio

# Test SMS
curl -X POST http://localhost:5000/api/auth/send-verification \
  -H "Content-Type: application/json" \
  -d '{"identifier":"+1234567890","method":"sms"}'
```

## Frontend Integration

You'll need to update the registration UI to:
1. Add "Send Verification Code" button
2. Show code input field
3. Verify code before submitting registration
4. Include `verified_identifier` in registration payload

Example flow:
```javascript
// Step 1: Send code
await fetch('/api/auth/send-verification', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    identifier: email,
    method: 'email'
  })
});

// Step 2: User enters code, verify it
const verifyResponse = await fetch('/api/auth/verify-code', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    identifier: email,
    code: userEnteredCode
  })
});

// Step 3: If verified, proceed with registration
if (verifyResponse.ok) {
  await fetch('/api/auth/register', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      ...registrationData,
      verified_identifier: email
    })
  });
}
```

## Security Features
- ✅ Codes expire after 10 minutes
- ✅ One-time use (marked as verified after use)
- ✅ Old codes automatically cleared when requesting new one
- ✅ Validation checks before registration
- ✅ Graceful fallback if SMTP/Twilio not configured

## Optional Mode
By default, 2FA is **optional** (REQUIRE_2FA_SIGNUP=0):
- If configured: Users can choose to verify
- If not configured: Registration works without verification
- Set to 1 to make it mandatory

## Troubleshooting

**Email not sending:**
- Check SMTP credentials
- Gmail: Use App Password, not regular password
- Check firewall/network allows port 587

**SMS not sending:**
- Verify Twilio credentials
- Check phone number format (+1234567890)
- Ensure twilio library installed
- Check Twilio account balance

**Code not working:**
- Check if code expired (10 minute limit)
- Verify identifier matches exactly
- Check database for verification_codes table
