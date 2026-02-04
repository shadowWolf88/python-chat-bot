
# To-Do List 1
git add
## User Registration & Onboarding 
- Remove country selection from patient sign-up (UK-only). 
- Require both region and clinician username to locate clinician during sign-up.
- Review patient/clinician onboarding for missing elements (focus on security and useful initial data).

## Security & Authentication
- Ensure PIN/password “show/hide” toggle works on all sign-up forms.
- Enforce PIN/password “match” validation and security requirements.
- Set the default theme to dark mode on the login page, and ensure the light/dark switch reflects the current theme.
- Place the light/dark theme switcher on the initial login selection page (patient/clinician).
- Prevent users from changing name, NHS number, or DOB after initial setup; allow email/phone/address changes only with clinician approval.

## Insights & AI Assistant
- Make the Insights tab’s generated insight area scrollable to prevent content from being cut off.
- In the patient AI assistant, ensure the “thinking” indicator does not display code or text—only a minimum 2-second delay before each response.

## Notifications & Communication
- Notify clinicians when a user updates their personal information. asdf 

---

# Developer Dashboard – Features & Improvements

## User Management
- View all users (patients, clinicians, developers) with filters and search.
- Edit user details (role, status, etc.).
- Delete or deactivate users.
- Reset user passwords or PINs.

## Database Tools
- Wipe/reset database (with confirmation and audit logging).
- Export/import data (CSV, JSON, or FHIR).
- View database status (record counts, last backup, etc.).

## Audit & Security
- View audit logs (logins, deletions, exports, etc.).
- Manage developer accounts (add/remove/change roles).
- View and manage API keys/secrets (with masking).
- Session management (force logout, view active sessions).

## UI/UX
- Responsive design for mobile/tablet.
- Theme switcher (light/dark) affecting all dashboard elements.
- Accessible color contrast and ARIA labels.
- Confirmation dialogs for destructive actions.

## GDPR/Compliance
- Export user data on request.
- Anonymize or delete user data.
- View/manage consent records.

---

## Additional Developer Dashboard Suggestions

- **System Monitoring:** Show API uptime, request counts, and error rates (if available from platform).
- **Job Scheduler:** View and trigger background jobs (e.g., backups, exports), with status and logs.
- **Feature Flags:** Enable/disable experimental features for testing.
- **Environment Info:** Display current environment (production, staging, dev), app version, and deployment date.
- **Crash/Error Reporting:** View recent exceptions and error traces.
- **Notification Center:** See system alerts, deployment notices, or critical warnings.
- **API Usage Analytics:** Track API usage by endpoint, user, or time period.
- **Data Retention Tools:** Schedule and manage data purges for compliance.
- **Support Tools:** Quick links to documentation, support tickets, or contact forms.




* add the reset password function for all accounts too, make sure it sends a "reset password" link where the user/clinician can create and reguster a new passowrd

* is it possible to implement texts/LIVE notifications for free? 
* what else can we add to the onboarding flow to make it more concise from the start? would it be good to get a bit of background?
* I dont want the app to force people to HAVE to have a clinician, so when onboarding, make sure patients can check a box to say yes or no to having a clinician, and if they do, they allow them to search etc like we do already.
