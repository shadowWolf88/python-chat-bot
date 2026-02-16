# Clinician Appointment Calendar & PDF Reports

## Overview

The **Clinician Appointment Calendar** system provides comprehensive appointment management and automated patient progress report generation for clinicians. This feature integrates seamlessly with the existing Clinician Dashboard to streamline face-to-face appointment scheduling and patient data reporting.

---

## Features

### 📅 Appointment Calendar

1. **Book Face-to-Face Appointments**
   - Select patient from dropdown
   - Set date and time (YYYY-MM-DD HH:MM format)
   - Add appointment notes
   - Automatic validation (future dates only)

2. **Visual Appointment Management**
   - Color-coded urgency:
     - 🔴 **Red**: 0-2 days (urgent)
     - 🟠 **Orange**: 3-7 days (soon)
     - 🟢 **Green**: 7+ days (future)
   - Shows days until appointment
   - Status indicators: ✅ PDF Ready, 🔔 Notified

3. **Quick Actions**
   - 📄 **Generate PDF**: Create progress report
   - 🗑️ **Cancel**: Remove appointment

### 📄 PDF Progress Reports

1. **Comprehensive Patient Data**
   - Patient profile (name, DOB, medical history)
   - Clinical assessments (PHQ-9, GAD-7) with scores table
   - Mood & health logs (last 30 days)
   - Gratitude journal entries
   - CBT thought records
   - Safety plan (triggers & coping strategies)
   - AI therapy context summary

2. **Professional Formatting**
   - Uses reportlab library (better than fpdf)
   - Clean, professional layout with tables
   - Multi-page support with page breaks
   - Proper headers and sections

3. **Storage System**
   - PDFs stored in `patient_data/<username>/` folders
   - Automatic folder creation per patient
   - Timestamp-based filenames
   - File browser integration

### 🔔 Automated Notifications

1. **2-Day Appointment Reminders**
   - System checks appointments daily
   - Sends notification 2 days before appointment
   - Reminder message: "⚠️ Appointment with [patient] in 2 days. Generate progress PDF!"
   - Automatic notification tracking (won't spam)

2. **Notification Types**
   - In-dashboard notifications
   - Linked to specific appointments
   - Status tracking to prevent duplicates

---

## How to Use

### For Clinicians

#### 1. Access the Dashboard
```
Main App → Admin/Clinician Button → Enter Credentials
```

#### 2. Book an Appointment
1. Navigate to **"📅 Appointments"** tab
2. Select patient from dropdown
3. Enter date (YYYY-MM-DD) and time (HH:MM)
4. Add optional notes
5. Click **"📅 Book Appointment"**

**Example:**
- Patient: `john_doe`
- Date: `2026-01-25`
- Time: `14:30`
- Notes: `Follow-up on anxiety treatment`

#### 3. Generate PDF Report
**Option A - From Appointments Tab:**
1. Find the appointment in the list
2. Click **"📄 Generate PDF"** button
3. Choose where to save the PDF
4. PDF is saved to both:
   - Your selected location
   - `patient_data/<username>/` folder

**Option B - From PDF Reports Tab:**
1. Navigate to **"📄 PDF Reports"** tab
2. Select patient from dropdown
3. Click **"📥 Generate & Download PDF"**
4. Choose save location

#### 4. Manage Generated PDFs
- View all generated PDFs in **PDF Reports** tab
- See file size, creation date, patient
- **📂 Open Folder**: View patient's PDF folder
- **📥 Download**: Save copy to new location

#### 5. Cancel Appointments
1. Find appointment in list
2. Click **"🗑️ Cancel"** button
3. Confirm cancellation

---

## Database Schema

### `appointments` Table
```sql
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clinician_username TEXT,
    patient_username TEXT,
    appointment_date DATETIME,
    appointment_type TEXT DEFAULT 'Face-to-Face',
    notes TEXT,
    pdf_generated INTEGER DEFAULT 0,
    pdf_path TEXT,
   notification_sent INTEGER DEFAULT 0,
   attendance_status TEXT DEFAULT 'scheduled',
   attendance_confirmed_by TEXT,
   attendance_confirmed_at DATETIME,
   created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(clinician_username) REFERENCES users(username),
    FOREIGN KEY(patient_username) REFERENCES users(username)
)
```

**Fields:**
- `id`: Unique appointment ID
- `clinician_username`: Who booked the appointment
- `patient_username`: Patient for appointment
- `appointment_date`: Date and time (YYYY-MM-DD HH:MM:SS)
- `appointment_type`: Type of appointment (default: Face-to-Face)
- `notes`: Optional notes about appointment
- `pdf_generated`: 0 = not generated, 1 = generated
- `pdf_path`: Path to generated PDF file
- `notification_sent`: 0 = not sent, 1 = reminder sent
- `created_at`: When appointment was booked

---

## File Structure

```
patient_data/
├── patient1/
│   ├── patient1_progress_report_20260117_120000.pdf
│   ├── patient1_progress_report_20260120_143000.pdf
│   └── ...
├── patient2/
│   ├── patient2_progress_report_20260118_095500.pdf
│   └── ...
└── ...
```

**Filename Format:**
```
{username}_progress_report_{YYYYMMDD}_{HHMMSS}.pdf
```

**Example:**
```
john_doe_progress_report_20260117_143022.pdf
```

---

## Technical Details

### Dependencies

**New Dependency:**
```txt
reportlab==4.4.9  # Professional PDF generation
```

**Install:**
```bash
pip install reportlab
# or
pip install -r requirements.txt
```

### Module Structure

**New File: `clinician_appointments.py`**
- `AppointmentManager`: Handles appointment booking and calendar UI
- `PDFReportGenerator`: Creates comprehensive PDF reports

**Integration Points:**
- `main.py`: Updated ProfessionalDashboard to use appointment system
- `init_db()`: Added appointments table creation
- Database: therapist_app.db

### PDF Generation

**Uses reportlab** (not fpdf):
- Better formatting
- Professional tables
- Multi-page support
- Paragraph wrapping
- Custom styles

**PDF Structure:**
1. Title page with patient info
2. Clinical assessments table
3. Mood & health history
4. Page break
5. Gratitude entries
6. CBT thought records
7. Page break
8. Safety plan
9. AI therapy summary

---

## Notification System

### How It Works

1. **Check Trigger:**
   - Called when clinician opens dashboard
   - Checks for appointments exactly 2 days in future

2. **Notification Creation:**
   - Creates entry in `notifications` table
   - Message: "⚠️ Appointment with {patient} in 2 days. Generate progress PDF!"
   - Type: `appointment_reminder`

3. **Post-Appointment Attendance Confirmation**
   - Clinicians can confirm whether a patient attended an appointment.
   - Status values: `attended`, `no_show`, `missed`.
   - The system updates the `appointments` record (`attendance_status`, `attendance_confirmed_by`, `attendance_confirmed_at`) and creates a notification of type `appointment_attendance` for the patient.
   - Example: Clinician marks appointment `123` as `attended` via `/api/appointments/123/attendance` (POST `{ "clinician_username": "dr_smith", "status": "attended" }`).


3. **Tracking:**
   - Sets `notification_sent = 1` in appointments table
   - Prevents duplicate notifications

4. **Audit Log:**
   - Logs all notifications to audit trail
   - Event: `appointment_reminder`
   - Actor: `system`

### Manual Check
```python
appointment_mgr.check_upcoming_appointments()
```

---

## Security & Privacy

### Access Control
- ✅ Only clinicians can access
- ✅ Clinician account required (role = 'clinician')
- ✅ Admin fallback with DEBUG mode

### Data Protection
- ✅ PDFs stored in secure `patient_data/` folder
- ✅ Encrypted patient data (name, DOB, conditions)
- ✅ Decryption happens during PDF generation
- ✅ Audit logging for all PDF generation events

### Audit Events
```
- appointment_booked: When appointment is created
- pdf_generated: When PDF is generated
- appointment_reminder: When 2-day notification sent
```

---

## Configuration

### Environment Variables
None required - uses existing encryption and database setup.

### Optional Settings
- PDF save location (user-selected per generation)
- Patient folder structure (automatic)

---

## Troubleshooting

### "reportlab not installed" Error
**Solution:**
```bash
pip install reportlab --break-system-packages
```

### PDF Not Generating
**Check:**
1. Patient has data in database
2. Encryption key is properly configured
3. `patient_data/` folder permissions

**Debug:**
```python
# Check if reportlab is available
python3 -c "import reportlab; print(reportlab.__version__)"
```

### Appointment Not Showing
**Check:**
1. Date is in the future
2. Correct patient username
3. Database connection

**SQL Query:**
```sql
SELECT * FROM appointments WHERE clinician_username='your_username';
```

### Notification Not Sent
**Check:**
1. Appointment date is exactly 2 days in future
2. `notification_sent = 0` in database
3. Dashboard has been opened (triggers check)

**Manual Trigger:**
```python
# In clinician dashboard
self.appointment_mgr.check_upcoming_appointments()
```

---

## Examples

### Example 1: Book Appointment for Next Week
```
Patient: alice_smith
Date: 2026-01-24
Time: 10:00
Notes: Monthly check-in, discuss medication adjustment
```

### Example 2: Generate PDF Before Appointment
```
1. Open "📅 Appointments" tab
2. Find appointment with alice_smith (24/01)
3. Click "📄 Generate PDF"
4. Save to: ~/Downloads/alice_smith_report.pdf
5. PDF also stored in: patient_data/alice_smith/
```

### Example 3: View All Patient PDFs
```
1. Open "📄 PDF Reports" tab
2. Browse generated reports by patient
3. Click "📂 Open Folder" to see all reports for a patient
4. Click "📥 Download" to save copy elsewhere
```

---

## API Reference

### AppointmentManager Class

```python
appointment_mgr = AppointmentManager(parent_widget, clinician_username)

# Setup UI
appointment_mgr.setup_appointment_tab(tab_widget)

# Book appointment
appointment_mgr.book_appointment()

# Refresh list
appointment_mgr.refresh_appointments()

# Cancel appointment
appointment_mgr.cancel_appointment(appointment_id)

# Check for notifications
appointment_mgr.check_upcoming_appointments()
```

### PDFReportGenerator Class

```python
pdf_gen = PDFReportGenerator(clinician_username)

# Generate PDF
pdf_path = pdf_gen.generate_patient_pdf(
    patient_username="john_doe",
    appointment_id=123,  # Optional
    prompt_save=True     # Ask where to save
)
```

---

## Future Enhancements

### Planned Features
- [ ] Email notifications for appointments
- [ ] SMS reminders to patients
- [ ] Recurring appointment templates
- [ ] PDF email delivery to patients
- [ ] Appointment rescheduling
- [ ] Video call integration
- [ ] Calendar export (iCal format)
- [ ] Appointment history archive

### Possible Improvements
- [ ] Customizable notification timeframes
- [ ] PDF template customization
- [ ] Batch PDF generation
- [ ] Appointment search/filter
- [ ] Patient appointment portal
- [ ] Insurance integration
- [ ] Billing integration

---

## Changelog

### Version 1.0 (January 17, 2026)
- ✅ Initial release
- ✅ Appointment calendar with booking
- ✅ PDF progress report generation (reportlab)
- ✅ 2-day appointment notifications
- ✅ Patient data folder organization
- ✅ Visual appointment management
- ✅ Urgency color coding
- ✅ Audit logging integration

---

## Support

### Need Help?
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review [USER_GUIDE.md](USER_GUIDE.md)
3. Check audit logs: `audit_logs` table
4. Review console output for errors

### Report Issues
- Open GitHub issue with:
  - Steps to reproduce
  - Error messages
  - Screenshot (if applicable)
  - Database query results

---

**Last Updated:** January 17, 2026  
**Module:** clinician_appointments.py  
**Dependencies:** reportlab, customtkinter, sqlite3  
**Database Tables:** appointments, notifications
