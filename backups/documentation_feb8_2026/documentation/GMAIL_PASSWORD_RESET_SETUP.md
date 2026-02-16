# Gmail Password Reset Setup Guide

**Date**: February 5, 2026  
**Purpose**: Configure email-based password reset using Gmail SMTP  
**Status**: Production Ready

---

## 📋 Overview

This guide walks you through setting up Gmail SMTP for password reset emails in Healing Space. Users will receive password reset links via email when they request them.

---

## 🔧 Step 1: Create a Gmail Account (or use existing)

You'll need a Gmail account to act as the "sender" for password reset emails. This can be:
- A dedicated account like `healing-space-noreply@gmail.com`
- An existing clinical admin email
- Any Gmail account you can access

**Important**: This account needs to send emails, so ensure you have access to it.

---

## 🔐 Step 2: Enable 2-Factor Authentication (Required)

Gmail requires 2FA to be enabled for app-specific passwords.

1. Go to [Google Account Security Settings](https://myaccount.google.com/security)
2. On the left, click **"2-Step Verification"**
3. Click **"Enable 2-Step Verification"**
4. Follow the prompts (you'll verify via phone or backup codes)
5. Confirm 2FA is enabled (you should see a checkmark)

---

## 🔑 Step 3: Generate App-Specific Password

Once 2FA is enabled, generate an app-specific password for Healing Space:

1. Go back to [Google Account Security Settings](https://myaccount.google.com/security)
2. Look for **"App passwords"** in the left menu (only appears if 2FA is enabled)
3. Click **"App passwords"**
4. Select:
   - App: **"Mail"**
   - Device: **"Windows Computer"** (or your platform)
5. Click **"Generate"**
6. **Copy the password** that appears (it looks like: `xxxx xxxx xxxx xxxx`)
7. Save this password temporarily - you'll need it in the next step

---

## 🚀 Step 4: Configure Environment Variables on Railway

You need to set these variables in your Railway environment:

| Variable | Value | Example |
|----------|-------|---------|
| `MAIL_SERVER` | `smtp.gmail.com` | `smtp.gmail.com` |
| `MAIL_PORT` | `587` | `587` |
| `MAIL_USE_TLS` | `True` | `True` |
| `MAIL_USERNAME` | Your Gmail address | `healing-space-noreply@gmail.com` |
| `MAIL_PASSWORD` | App-specific password from Step 3 | `xxxx xxxx xxxx xxxx` |
| `MAIL_DEFAULT_SENDER` | Display name for emails | `Healing Space <noreply@healing-space.org.uk>` |
| `RESET_PASSWORD_LINK` | Your app's domain | `https://www.healing-space.org.uk` |

### How to Set Variables on Railway:

1. **Go to your Railway project**: https://railway.app/dashboard
2. **Click your project** (Healing Space UK)
3. **Click "Variables"** in the top menu
4. **Add each variable above** with the corresponding value
5. **Click "Save"**
6. **Deploy** (redeploy your service for changes to take effect)

### Example Railway Variables:
```
MAIL_SERVER = smtp.gmail.com
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = healing-space-noreply@gmail.com
MAIL_PASSWORD = xxxx xxxx xxxx xxxx
MAIL_DEFAULT_SENDER = Healing Space <noreply@healing-space.org.uk>
RESET_PASSWORD_LINK = https://www.healing-space.org.uk
```

---

## 🧪 Step 5: Test the Email Configuration

### Test Locally (Optional):

```bash
export MAIL_SERVER=smtp.gmail.com
export MAIL_PORT=587
export MAIL_USE_TLS=True
export MAIL_USERNAME=your-gmail@gmail.com
export MAIL_PASSWORD="your app password"
export MAIL_DEFAULT_SENDER="Healing Space <noreply@healing-space.org.uk>"

python3 api.py
```

### Test in Production:

1. **Go to your app**: https://www.healing-space.org.uk
2. **Click "Forgot Password?"**
3. **Enter your email** (or test email)
4. **Check the email inbox** for the reset link within 1-2 minutes

---

## 📧 Step 6: Verify Email Sending Works

The password reset flow should now work:

1. User visits `/forgot-password`
2. Enters their username/email
3. System calls `/api/send-reset-email`
4. Email is sent via Gmail SMTP
5. User receives link like: `https://www.healing-space.org.uk/reset-password?token=abc123...`
6. User clicks link, creates new password
7. Password is updated in database

### If emails don't arrive:

**Check Railway logs** for SMTP errors:
```bash
railway logs
```

**Common issues**:
- ❌ "Invalid credentials" → Wrong Gmail/password in variables
- ❌ "Less secure apps" → Need app-specific password (not regular password)
- ❌ "2FA not enabled" → Gmail requires 2FA for app passwords
- ❌ "Port 587 refused" → Some networks block SMTP; try port 465 with `MAIL_USE_TLS=False`

---

## 🔒 Security Considerations

### Email Security Best Practices:

1. **Use app-specific password**, NOT your main Gmail password
   - App passwords can be revoked independently
   - If compromised, doesn't affect your main account

2. **Never commit credentials** to GitHub
   - Always use Railway environment variables
   - Never hardcode passwords in code

3. **Use a dedicated Gmail account** (optional but recommended)
   - Separate from personal/admin email
   - Easier to rotate if compromised

4. **Enable 2FA** on the Gmail account
   - Required for app-specific passwords
   - Protects the account itself

5. **Log all password resets**
   - System logs who reset passwords and when
   - Check logs for suspicious activity

---

## 🛠️ Troubleshooting

### Issue: "Connection refused"
```
Solution: Check MAIL_PORT and MAIL_SERVER variables
- Gmail SMTP: smtp.gmail.com:587 (with TLS)
- Or use: smtp.gmail.com:465 (with SSL, set MAIL_USE_TLS=False)
```

### Issue: "Invalid credentials"
```
Solution: Verify Gmail setup
1. Check MAIL_USERNAME is correct (full email)
2. Verify MAIL_PASSWORD is the app-specific password, not regular password
3. Confirm 2FA is enabled on Gmail account
4. Test credentials locally first
```

### Issue: "SSL/TLS error"
```
Solution: Check TLS settings
- MAIL_USE_TLS = True (for port 587)
- MAIL_USE_TLS = False (for port 465 with SSL)
```

### Issue: Emails arrive but link is broken
```
Solution: Check RESET_PASSWORD_LINK variable
- Should be your production URL: https://www.healing-space.org.uk
- OR: https://healing-space-uk.up.railway.app (if using Railway URL)
```

### Issue: Emails not arriving at all
```
Solutions to try:
1. Check spam/junk folder
2. Test another email address
3. Check Railway logs: railway logs | grep -i mail
4. Verify sender email (MAIL_DEFAULT_SENDER) is valid
5. Request resend of email
```

---

## 📝 API Endpoints

### Send Password Reset Email
```http
POST /api/send-reset-email
Content-Type: application/json

{
  "email": "user@example.com"
}

Response:
{
  "success": true,
  "message": "Reset email sent to user@example.com"
}
```

### Reset Password with Token
```http
POST /api/reset-password
Content-Type: application/json

{
  "token": "reset_token_here",
  "new_password": "NewSecurePassword123!"
}

Response:
{
  "success": true,
  "message": "Password reset successfully"
}
```

---

## 🔄 Implementation Details

### Code Location:
- **Password reset endpoints**: `api.py` (lines containing `reset-password` or `send-reset-email`)
- **Email sending**: Uses Flask-Mail or direct SMTP
- **Token generation**: Secure tokens with expiration

### Reset Token Features:
- ✅ Secure random token generation
- ✅ Expiration time (typically 1 hour)
- ✅ One-time use (token invalidated after use)
- ✅ Rate limiting to prevent abuse
- ✅ Audit logging of all resets

---

## 📊 Email Configuration Summary

| Setting | Value |
|---------|-------|
| **SMTP Server** | `smtp.gmail.com` |
| **Port** | `587` (TLS) or `465` (SSL) |
| **Authentication** | Username/Password (app-specific) |
| **Encryption** | TLS or SSL |
| **Sender Email** | Your Gmail account |
| **Link Expiry** | 1 hour (configurable) |
| **Rate Limit** | 5 resets per hour per user |

---

## ✅ Verification Checklist

- [ ] Gmail account created and accessible
- [ ] 2FA enabled on Gmail account
- [ ] App-specific password generated
- [ ] All environment variables set on Railway
- [ ] Railway redeployed after setting variables
- [ ] Test email sent and received
- [ ] Reset link works and redirects correctly
- [ ] New password takes effect after reset
- [ ] Audit log shows reset events

---

## 📞 Support

If emails aren't working:

1. **Check Railway logs**: Railway dashboard → Select project → View Logs
2. **Look for SMTP errors**: Search logs for "mail", "smtp", or "error"
3. **Verify credentials locally**: Test with local Flask app
4. **Check email provider**: Ensure Gmail account can send

---

## 🔐 Additional Security Notes

### NEVER:
- ❌ Use your personal Gmail password
- ❌ Commit credentials to GitHub
- ❌ Share app password in Slack/email
- ❌ Use less-secure apps setting (use app-specific password instead)

### ALWAYS:
- ✅ Use app-specific passwords
- ✅ Enable 2FA on the Gmail account
- ✅ Store credentials in Railway environment variables
- ✅ Rotate credentials regularly
- ✅ Monitor logs for failed attempts

---

**Setup Time**: ~10 minutes  
**Complexity**: Low  
**Security Level**: ⭐⭐⭐⭐⭐ (Recommended)

For more info, see: [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
