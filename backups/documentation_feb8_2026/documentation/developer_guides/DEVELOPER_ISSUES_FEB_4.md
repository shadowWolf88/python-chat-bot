# Developer Account Issues - February 4, 2026

## Issue #1: Feedback Message Not Arriving ✅ RESOLVED (By Design)

**What happened:** Submitted a "bug report" from the home screen that showed "message sent" but never appeared on the dashboard.

**Why this happened:** The "Send Feedback" form on the home screen is NOT the messaging system - it's a feedback/logging feature.

- **Home screen form** → stores in `feedback` table (for developers to review)
- **Messages tab form** → stores in `messages` table (user-to-user messaging)

**Status:** This is working as designed. The feedback WAS saved to the feedback table. You can view it in the developer dashboard under feedback logs (if that exists).

**If you want to send a message instead:**
1. Go to the **Messages** tab
2. Send a message to a clinician/therapist
3. It will appear in their inbox

---

## Issue #2: Clinician Dashboard Visible for Developer Account ⚠️ REQUIRES FIX

**What happened:** Developer account can see the "Professional Dashboard" (clinician view) when it shouldn't.

**Root Cause:** The developer account in the database has `role='clinician'` instead of `role='developer'`.

**How the frontend decides what to show:**
```javascript
if (currentUserRole === 'clinician') {
    // Show professional/clinician dashboard
    document.getElementById('professionalTabBtn').style.display = 'block';
} else if (currentUserRole === 'developer') {
    // Show developer dashboard only
    document.getElementById('developerTabBtn').style.display = 'block';
} else {
    // Show patient dashboard
}
```

**How to fix:**

### Option 1: Check Database (Recommended)
```bash
sqlite3 therapist_app.db
SELECT username, role FROM users WHERE username='[your_dev_username]';
```

If the role is `clinician`, update it:
```sql
UPDATE users SET role='developer' WHERE username='[your_dev_username]';
```

### Option 2: Using Python
```python
import sqlite3
conn = sqlite3.connect('therapist_app.db')
cur = conn.cursor()
cur.execute("UPDATE users SET role='developer' WHERE username='[your_dev_username]'")
conn.commit()
conn.close()
```

### Option 3: Re-register as Developer
If the above doesn't work, the account might need to be recreated with the correct role:
1. Delete/rename the old account
2. Create a new developer account (if there's an admin endpoint)

---

## Verification

After fixing, log in again and you should:
- ❌ NOT see the "Professional" tab
- ✅ See the "Developer" tab with terminal/admin features
- ✅ NOT see patient tabs (therapy, mood, gratitude, CBT, pet, etc.)

If you still see the clinician dashboard after the fix, clear browser cache and log out/in again.

---

## Summary

| Issue | Type | Status | Action |
|-------|------|--------|--------|
| Feedback message not received | Design | ✅ Working as intended | None - feedback goes to feedback table |
| Clinician dashboard visibility | Bug | ⚠️ Role mismatch | Update `role` to `developer` in database |

