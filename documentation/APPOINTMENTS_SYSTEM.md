# Appointments System Documentation

## Overview
Bidirectional appointment booking system where clinicians can schedule appointments and patients can view, acknowledge, and respond to them.

## Features

### For Clinicians
- **Book Appointments**: Schedule appointments for patients with date, time, and notes
- **View Patient Status**: See whether patients have:
  - Read/acknowledged the appointment (✓ Read / ○ Unread)
  - Accepted, declined, or are pending response (✓ Accepted / ✗ Declined / ⏳ Pending)
  - Response timestamp when available
- **Cancel Appointments**: Remove appointments as needed
- **Urgency Indicators**: Appointments within 2 days are highlighted

### For Patients
- **View Appointments**: See all upcoming appointments in dedicated tab
- **Mandatory Acknowledgment**: Must check "I have read and understood this appointment" box before responding
- **Accept/Decline**: Clear action buttons to respond to appointments
- **Status Tracking**: See appointment status (accepted/declined/pending)
- **Automatic Notifications**: Clinician receives notification when patient responds

## Technical Implementation

### Database Schema
```sql
-- Added to appointments table:
ALTER TABLE appointments ADD COLUMN patient_acknowledged INTEGER DEFAULT 0;
ALTER TABLE appointments ADD COLUMN patient_response TEXT DEFAULT 'pending';
ALTER TABLE appointments ADD COLUMN patient_response_date DATETIME;
```

### API Endpoints

#### GET /api/appointments
- **Query Parameters**:
  - `clinician={username}` - Get appointments created by this clinician
  - `patient={username}` - Get appointments for this patient
- **Returns**: Array of appointment objects with response data

#### POST /api/appointments
- **Body**: `{patient_username, appointment_date, appointment_type, notes}`
- **Action**: Creates new appointment with `patient_response='pending'`

#### POST /api/appointments/<id>/respond
- **Body**: `{patient_username, acknowledged, response}`
- **Validation**:
  - Must include `acknowledged: true`
  - Response must be 'accepted' or 'declined'
  - Patient must match appointment
- **Actions**:
  - Updates `patient_acknowledged = 1`
  - Sets `patient_response` and `patient_response_date`
  - Sends notification to clinician
  - Logs event for audit

### UI Components

#### Patient Dashboard - Appointments Tab
**Location**: Between "Progress Insights" and "About Me" tabs

**Features**:
- Appointment cards showing:
  - Clinician name
  - Date and time (formatted)
  - Type and notes
  - Status badge (color-coded)
- For pending appointments:
  - Acknowledgment checkbox (required)
  - Accept button (green)
  - Decline button (red)
  - Buttons disabled until checkbox is ticked
- For responded appointments:
  - Status display
  - Response timestamp
  - No action buttons

#### Clinician Dashboard - Appointments Section
**Enhancements**:
- Patient response status badges:
  - ✓ Accepted (green)
  - ✗ Declined (red)
  - ⏳ Pending (yellow)
- Acknowledgment indicator:
  - ✓ Read (green)
  - ○ Unread (gray)
- Response timestamp display

## User Flow

### Clinician Creates Appointment
1. Clinician clicks "Schedule New Appointment"
2. Selects patient, date/time, and adds notes
3. Submits form
4. Appointment created with status "Pending"

### Patient Receives Appointment
1. Patient logs in and sees appointments tab
2. Opens tab and sees appointment card
3. Reads appointment details
4. **Must tick acknowledgment checkbox**
5. Clicks "Accept" or "Decline"
6. Confirms decision
7. Appointment updated, clinician notified

### Clinician Sees Response
1. Refreshes appointments view
2. Sees updated status badges:
   - Read indicator changes to ✓ Read
   - Response shows ✓ Accepted or ✗ Declined
   - Timestamp displays when response was submitted
3. Receives notification about patient's decision

## Validation & Security

### Mandatory Acknowledgment
- JavaScript checks checkbox before allowing response
- Backend validates `acknowledged=true` in request
- Alert shown if user attempts to respond without reading

### Appointment Ownership
- Backend verifies patient username matches appointment
- Only assigned patient can respond
- Clinician receives notification confirming authentic response

### Audit Trail
- All appointment responses logged in `audit_logs` table
- Includes: username, action, appointment_id, response, timestamp

## Code Locations

### Backend (api.py)
- **Database migrations**: Lines 241-268
- **GET endpoint**: Lines 3621-3681
- **POST create**: Lines 3686-3690
- **POST respond**: Lines 3722-3781

### Frontend (templates/index.html)
- **Patient sidebar button**: Line 1175
- **Patient tab content**: Lines 1597-1607
- **Patient JavaScript**: Lines 3852-3954
- **Clinician view update**: Lines 4636-4664

## Testing Checklist

- [ ] Clinician can create appointment
- [ ] Patient sees appointment in tab
- [ ] Patient cannot respond without ticking checkbox
- [ ] Patient can accept appointment
- [ ] Patient can decline appointment
- [ ] Clinician sees "✓ Read" after acknowledgment
- [ ] Clinician sees "✓ Accepted" or "✗ Declined" status
- [ ] Response timestamp displays correctly
- [ ] Clinician receives notification
- [ ] Audit log captures event
- [ ] Past appointments display correctly
- [ ] Empty state shows appropriate message

## Future Enhancements
- Filter appointments (upcoming/past/responded)
- Appointment reminders (email/SMS)
- Reschedule functionality
- Calendar view
- Export to calendar apps (.ics)
- Appointment type categories with colors
- Recurring appointments

## Support
For issues or questions, check audit logs and browser console for detailed error messages.
