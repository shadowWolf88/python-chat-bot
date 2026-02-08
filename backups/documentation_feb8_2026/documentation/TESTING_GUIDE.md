# Quick Testing Guide - New Features

## Test 1: Password Strength Validation

1. Click "Create Account" to go to registration
2. Try entering these passwords and watch the strength bar:
   - `abc123` → Weak (red) - too short, no uppercase, no special chars
   - `Password1` → Fair (yellow) - no special character
   - `Password1!` → Strong (green) - meets all requirements
3. Try to submit with a weak password → Should show error message
4. Submit with strong password → Should succeed

## Test 2: 2FA PIN Authentication

1. During registration, enter a 4-digit PIN (e.g., `1234`)
2. Complete registration
3. Try to login with correct username and password but wrong PIN → Should fail
4. Login with correct username, password, AND PIN → Should succeed
5. You should see "Welcome to Healing Space!"

## Test 3: Patient Approval Workflow

### As Patient:
1. Register a new patient account
2. Select a clinician from the dropdown
3. Enter strong password and 4-digit PIN
4. Submit registration
5. You should see: "Account created! Awaiting clinician approval."
6. Try to login → You'll get a message saying "Your clinician has not yet approved your account"
7. Click the notification bell (🔔) → You should see a notification about pending approval

### As Clinician:
1. Register a clinician account (click "Register as Clinician")
2. Enter username, password (no clinician selection needed)
3. Login as clinician
4. You should see the "👨‍⚕️ Professional" tab appear
5. Click the Professional tab
6. You'll see "Pending Patient Requests" section with the patient request
7. Click "✓ Approve" to approve the patient
8. Both you and the patient will receive notifications

### Back to Patient:
1. Login as the patient again
2. You should now have full access without the "pending approval" message
3. Check notifications bell → You'll see approval notification

## Test 4: Notification System

1. Login as any user
2. Look for the bell icon (🔔) in the top-right corner
3. If you have unread notifications, you'll see a red badge with the count
4. Click the bell to open the notification panel
5. Notifications are color-coded:
   - Blue background = unread
   - White background = read
6. Click any notification to mark it as read
7. The badge count should decrease
8. Notifications auto-refresh every 30 seconds

## Test 5: Clinician Dashboard Differentiation

### As Patient:
- You should NOT see the "👨‍⚕️ Professional" tab
- You only see patient-focused tabs (Therapy, Mood, Pet, etc.)

### As Clinician:
- You SHOULD see the "👨‍⚕️ Professional" tab
- Clicking it shows:
  - "Pending Patient Requests" section (yellow card)
  - "My Patients" section showing approved patients
  - Approve/Reject buttons for each pending request

## Common Test Scenarios

### Scenario 1: New Patient Signs Up
1. Patient creates account with weak password → REJECTED
2. Patient creates account with strong password → SUCCESS
3. Patient selects Dr. Smith as clinician → Pending approval created
4. Dr. Smith receives notification
5. Patient receives notification
6. Patient tries to login → Warning message about pending approval
7. Dr. Smith logs in → Sees pending request
8. Dr. Smith approves → Both notified
9. Patient logs in → Full access granted

### Scenario 2: Clinician Rejects Patient
1. Patient selects Dr. Jones
2. Dr. Jones receives notification
3. Dr. Jones clicks "✗ Reject"
4. Patient receives rejection notification
5. Patient can select a different clinician

### Scenario 3: Multiple Pending Approvals
1. 3 patients select Dr. Brown
2. Dr. Brown sees 3 pending requests
3. Dr. Brown approves 2, rejects 1
4. All patients receive appropriate notifications
5. Approved patients gain access
6. Rejected patient must choose different clinician

## Expected Results

✅ **Password Validation:**
- Weak passwords rejected
- Strength bar updates in real-time
- Clear error messages

✅ **2FA PIN:**
- Login requires PIN
- Wrong PIN blocks access
- Correct PIN grants access

✅ **Approval Workflow:**
- New patients start as "pending"
- Clinicians see pending requests
- Approve/reject triggers notifications
- Approved patients gain full access

✅ **Notifications:**
- Bell icon shows unread count
- Clicking bell opens panel
- Notifications mark as read when clicked
- Auto-refreshes every 30 seconds

✅ **Clinician Dashboard:**
- Only visible to clinicians
- Shows pending approvals
- Shows approved patients
- Quick approve/reject actions

## Troubleshooting

**"PIN must be 4 digits" error:**
- Make sure you enter exactly 4 digits (e.g., 1234)
- No letters or special characters

**"Password must contain..." error:**
- Password needs: lowercase, uppercase, number, special character
- Example: MyPass123!

**"Your clinician has not yet approved" message:**
- This is expected for new patients
- Wait for clinician to approve your request
- Check notifications for updates

**Notification bell not showing badge:**
- You have no unread notifications
- Refresh the page
- Check if notifications are being created

**Professional tab not visible:**
- Only clinicians see this tab
- Make sure you registered as a clinician, not a patient
- Try logging out and back in

## Database Inspection (For Developers)

Check pending approvals:
```sql
SELECT * FROM patient_approvals WHERE status='pending';
```

Check notifications:
```sql
SELECT * FROM notifications WHERE read=0 ORDER BY created_at DESC;
```

Check user roles:
```sql
SELECT username, role FROM users;
```

Check if user has PIN:
```sql
SELECT username, pin FROM users;
```
