# Gmail Password Reset Setup Guide

**Complete guide to configure Gmail for password reset emails in Healing Space**

This guide walks you through setting up Gmail (or Google Workspace) to send password reset emails from your Healing Space application.

---

## 📋 Table of Contents

1. [Quick Summary](#quick-summary)
2. [Step 1: Create a Google Account](#step-1-create-a-google-account)
3. [Step 2: Enable 2-Factor Authentication](#step-2-enable-2-factor-authentication)
4. [Step 3: Generate App Password](#step-3-generate-app-password)
5. [Step 4: Configure Healing Space Environment Variables](#step-4-configure-healing-space-environment-variables)
6. [Step 5: Test the Setup](#step-5-test-the-setup)
7. [Step 6: Deploy to Production](#step-6-deploy-to-production)
8. [Troubleshooting](#troubleshooting)

---

## Quick Summary

To enable Gmail for password resets:

1. **Create a Gmail account** (or use existing)
2. **Enable 2FA** on the account
3. **Generate an App Password** (16-character code)
4. **Set 4 environment variables** in your application
5. **Test** password reset functionality
6. **Deploy** to production

**Time Required**: ~10 minutes

---

## Step 1: Create a Google Account

You have two options:

### Option A: Create a New Gmail Account (Recommended)

1. Go to [https://accounts.google.com/signup](https://accounts.google.com/signup)
2. Fill in the details:
   - **First name**: e.g., "Healing"
   - **Last name**: e.g., "Space"
   - **Email**: Create a new Gmail address (e.g., `healing-space-noreply@gmail.com`)
   - **Password**: Create a strong password
3. Complete phone verification and other steps
4. **Write down** the email and password

### Option B: Use Existing Gmail Account

If you already have a Gmail account, you can use it. Just make sure you have access to the account settings.

---

## Step 2: Enable 2-Factor Authentication

Google requires 2FA to use App Passwords (which are more secure than your main password).

**Steps**:

1. Go to [https://myaccount.google.com/security](https://myaccount.google.com/security)
2. Sign in if necessary
3. Under **"How you sign in to Google"**, click **"2-Step Verification"**
4. Click **"Get Started"**
5. Follow the on-screen instructions:
   - Verify your phone number
   - Choose verification method (SMS or call)
   - Complete verification
   - Save backup codes in a safe place

✅ **2FA is now enabled on this account**

---

## Step 3: Generate App Password

App Passwords allow applications to authenticate without knowing your main Gmail password.

**Steps**:

1. Go to [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Sign in if necessary
3. You'll see: "Select the app and device you want to generate the app password for"
4. Under **"Select app"**, choose **"Mail"**
5. Under **"Select device"**, choose **"Windows Computer"** (or your platform)
6. Click **"Generate"**
7. Google will show a **16-character password** (format: `xxxx xxxx xxxx xxxx`)

**Copy this password** - you'll need it in Step 4.

Example: `abcd efgh ijkl mnop`

---

## Step 4: Configure Healing Space Environment Variables

Now you need to set environment variables so the application can send emails.

### For Local Development (`.env` file):

Create or edit `.env` file in your Healing Space root directory:

```env
# Gmail Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-gmail@gmail.com
SMTP_PASSWORD=your-app-password-here
FROM_EMAIL=your-gmail@gmail.com
APP_URL=http://localhost:5000
```

**Replace with your values**:
- `your-gmail@gmail.com` = The Gmail address you created/use
- `your-app-password-here` = The 16-character App Password (without spaces)

Example:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=healing-space-noreply@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
FROM_EMAIL=healing-space-noreply@gmail.com
APP_URL=http://localhost:5000
```

### For Production (Railway):

1. Go to your Railway project dashboard
2. Click **"Variables"** tab
3. Add the same environment variables:

| Variable | Value |
|----------|-------|
| `SMTP_SERVER` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USER` | your Gmail address |
| `SMTP_PASSWORD` | 16-character App Password |
| `FROM_EMAIL` | your Gmail address |
| `APP_URL` | Your production URL (e.g., `https://www.healing-space.org.uk`) |

**Important**: 
- Use the **App Password**, NOT your Gmail password
- Remove spaces from the 16-character password
- `APP_URL` must be your actual domain (used in reset email links)

---

## Step 5: Test the Setup

### Test Locally:

1. Start your Healing Space application:
   ```bash
   python3 api.py
   ```

2. Go to the web app at `http://localhost:5000`

3. Click **"Forgot Password"**

4. Enter an email address associated with a user account (e.g., dev account)

5. Check your email for the reset link

**Expected result**: You should receive a password reset email within 30 seconds.

### If You Don't Receive the Email:

Check the application logs for error messages. Common issues:
- Email not entered correctly
- User account doesn't exist
- SMTP credentials wrong
- Gmail blocking the connection

---

## Step 6: Deploy to Production

Once testing is successful:

1. **Add environment variables to Railway** (see Production section in Step 4)
2. **Redeploy** your application:
   ```bash
   git push origin main
   # Railway auto-deploys, or manually trigger deployment
   ```
3. **Test in production** by trying the "Forgot Password" flow on your live domain

---

## 📧 How Password Reset Emails Work

When a user clicks "Forgot Password":

1. **API endpoint** validates the email address
2. **Generates reset token** (secure, unique, expires in 1 hour)
3. **Sends email** via SMTP to Gmail
4. **Email contains**: Reset link with token and username
5. **User clicks link** to reset password
6. **Token validated** and password updated

**Security Features**:
- Tokens expire after 1 hour
- Tokens are cryptographically secure
- Only one reset per user at a time
- Email must match registered email address

---

## ✅ Email Content Template

Users will receive an email like this:

```
From: healing-space-noreply@gmail.com
To: patient@example.com
Subject: python-chat-bot - Password Reset

---

Password Reset Request

Hello [username],

You requested to reset your password. Click the link below to reset it:

[Reset Password Link]

This link expires in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
python-chat-bot Team
```

---

## 🔒 Security Best Practices

1. **Use App Passwords**, not your main Gmail password
   - App Passwords are more secure and limited in scope
   - You can revoke them anytime

2. **Enable 2FA** on your Gmail account
   - Protects your email account from unauthorized access
   - Required for App Passwords

3. **Keep credentials secure**
   - Never commit `.env` file to Git
   - Use environment variables in production
   - Rotate credentials periodically

4. **Monitor sent emails**
   - Regularly check "Sent" folder
   - Set up alerts for suspicious activity

---

## 🚨 Troubleshooting

### "Email not sent - SMTP credentials not configured"

**Solution**: Verify environment variables are set:

```bash
# Local development
echo $SMTP_USER
echo $SMTP_PASSWORD

# Production (Railway)
# Check Variables tab in Railway dashboard
```

### "Authentication failed" or "535 5.7.8 Username and password not accepted"

**Causes & Solutions**:

1. **Wrong App Password**
   - Ensure you copied the full 16-character password
   - Remove any spaces
   - App Password != Gmail password

2. **Gmail account not set up correctly**
   - Verify 2FA is enabled
   - Generate a new App Password
   - Wait 5 minutes before retrying

3. **App Password was revoked**
   - Generate a new one at [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

### "Less secure apps" error

**Solution**: This is outdated. If you're using App Passwords (which you should be), ignore this error. The setup is correct.

### "Cannot verify user's email" on password reset page

**Causes**:

1. Email address not registered in the system
2. Email doesn't match user's registered email
3. No password reset requested yet

**Solution**:
- Verify user exists in the system
- Use correct email address
- Request a new password reset

### Emails going to spam folder

**Solution**:

1. Add your Gmail address to contacts/safe senders
2. Mark emails as "Not Spam" in email client
3. Check if email has proper formatting and doesn't trigger spam filters

---

## 📚 Related Documentation

- [Email Setup Guide](./EMAIL_SETUP.md) - General email configuration
- [Registration & Login Flow](./developer_guides/REGISTRATION_LOGIN_FLOW_ANALYSIS.md) - How auth works
- [Environment Variables](./infra_and_deployment/RAILWAY_ENV_VARS.md) - All app environment variables

---

## ⏱️ Summary Checklist

- ✅ Gmail account created or selected
- ✅ 2-Factor Authentication enabled
- ✅ App Password generated (16 characters)
- ✅ Environment variables set (local)
- ✅ Environment variables set (production)
- ✅ Local testing successful
- ✅ Production deployment complete
- ✅ Tested in production

---

## 🆘 Still Having Issues?

1. **Check application logs** for specific error messages
2. **Verify email configuration** in `.env` or Railway Variables
3. **Test SMTP connection** separately:
   ```python
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('your-email@gmail.com', 'your-app-password')
   print("✅ Connection successful")
   ```
4. **Review Gmail security settings** - no unusual account activity

---

**Last Updated**: February 5, 2026  
**Status**: ✅ Production Ready  
**Tested With**: Gmail, Google Workspace
