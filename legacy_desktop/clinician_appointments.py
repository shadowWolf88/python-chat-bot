#!/usr/bin/env python3
"""
Clinician Appointment Calendar and PDF Report Generator
Handles appointment booking, reminders, and patient progress report PDFs
"""

import os
import sqlite3
import customtkinter as ctk
from tkinter import messagebox, filedialog, simpledialog
from datetime import datetime, timedelta
from audit import log_event

# PDF generation imports
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    print("Warning: reportlab not installed. PDF export will be disabled.")


# Import decryption from main
try:
    from main import decrypt_text
except ImportError:
    # Fallback if imported before main loads
    def decrypt_text(text):
        return text


class AppointmentManager:
    """Handles clinician appointments and PDF generation"""
    
    def __init__(self, parent, clinician_username):
        self.parent = parent
        self.clinician_username = clinician_username
        
    def setup_appointment_tab(self, tab_widget):
        """Setup appointment calendar tab with booking and notifications"""
        ctk.CTkLabel(tab_widget, text="📅 Appointment Calendar", font=("Arial", 22, "bold")).pack(pady=10)
        
        # Book new appointment section
        book_frame = ctk.CTkFrame(tab_widget)
        book_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(book_frame, text="Book Face-to-Face Appointment", font=("Arial", 16, "bold")).pack(pady=5)
        
        # Patient selection
        patient_frame = ctk.CTkFrame(book_frame)
        patient_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(patient_frame, text="Patient:").pack(side="left", padx=5)
        
        conn = sqlite3.connect("therapist_app.db")
        patients = conn.cursor().execute("SELECT username FROM users WHERE role='patient' OR role IS NULL").fetchall()
        conn.close()
        
        patient_names = [p[0] for p in patients]
        self.patient_dropdown = ctk.CTkComboBox(patient_frame, values=patient_names if patient_names else ["No patients"], width=200)
        self.patient_dropdown.pack(side="left", padx=5)
        
        # Date/Time selection
        date_frame = ctk.CTkFrame(book_frame)
        date_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(date_frame, text="Date (YYYY-MM-DD):").pack(side="left", padx=5)
        self.date_entry = ctk.CTkEntry(date_frame, width=120)
        self.date_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(date_frame, text="Time (HH:MM):").pack(side="left", padx=5)
        self.time_entry = ctk.CTkEntry(date_frame, width=80)
        self.time_entry.pack(side="left", padx=5)
        
        # Notes
        notes_frame = ctk.CTkFrame(book_frame)
        notes_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(notes_frame, text="Notes:").pack(anchor="w", padx=5)
        self.appt_notes = ctk.CTkTextbox(notes_frame, height=60)
        self.appt_notes.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(book_frame, text="📅 Book Appointment", command=self.book_appointment, fg_color="#27ae60", height=40).pack(pady=10)
        
        # Upcoming appointments list
        ctk.CTkLabel(tab_widget, text="Upcoming Appointments", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.appt_scroll = ctk.CTkScrollableFrame(tab_widget, height=300)
        self.appt_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.refresh_appointments()
    
    def book_appointment(self):
        """Book a new appointment and schedule PDF generation reminder"""
        patient = self.patient_dropdown.get()
        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()
        notes = self.appt_notes.get("1.0", "end-1c").strip()
        
        if not patient or patient == "No patients":
            messagebox.showerror("Error", "Please select a patient")
            return
        
        if not date_str or not time_str:
            messagebox.showerror("Error", "Please enter both date and time")
            return
        
        # Validate and parse datetime
        try:
            appt_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            if appt_datetime < datetime.now():
                messagebox.showerror("Error", "Appointment date must be in the future")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid date/time format. Use YYYY-MM-DD and HH:MM")
            return
        
        # Save appointment
        conn = sqlite3.connect("therapist_app.db")
        conn.execute("""INSERT INTO appointments (clinician_username, patient_username, appointment_date, 
                        appointment_type, notes) VALUES (?, ?, ?, 'Face-to-Face', ?)""",
                     (self.clinician_username, patient, appt_datetime.strftime("%Y-%m-%d %H:%M:%S"), notes))
        conn.commit()
        conn.close()
        
        log_event(self.clinician_username, 'clinician', 'appointment_booked', 
                 f"Booked appointment with {patient} on {appt_datetime}")
        
        messagebox.showinfo("Success", f"Appointment booked with {patient} on {date_str} at {time_str}")
        
        # Clear form
        self.date_entry.delete(0, 'end')
        self.time_entry.delete(0, 'end')
        self.appt_notes.delete("1.0", "end")
        
        self.refresh_appointments()
    
    def refresh_appointments(self):
        """Refresh the appointments list"""
        # Clear existing
        for widget in self.appt_scroll.winfo_children():
            widget.destroy()
        
        conn = sqlite3.connect("therapist_app.db")
        appointments = conn.cursor().execute("""
            SELECT id, patient_username, appointment_date, notes, pdf_generated, notification_sent
            FROM appointments WHERE clinician_username=? AND appointment_date >= datetime('now')
            ORDER BY appointment_date ASC""", (self.clinician_username,)).fetchall()
        conn.close()
        
        if not appointments:
            ctk.CTkLabel(self.appt_scroll, text="No upcoming appointments", text_color="gray").pack(pady=20)
            return
        
        for appt in appointments:
            appt_id, patient, date_str, notes, pdf_gen, notif_sent = appt
            appt_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            days_until = (appt_date - datetime.now()).days
            
            frame = ctk.CTkFrame(self.appt_scroll)
            frame.pack(fill="x", pady=5, padx=5)
            
            # Color code by urgency
            if days_until <= 2:
                color = "#e74c3c"  # Red - urgent
            elif days_until <= 7:
                color = "#f39c12"  # Orange - soon
            else:
                color = "#2ecc71"  # Green - future
            
            ctk.CTkLabel(frame, text=f"👤 {patient}", font=("Arial", 13, "bold")).pack(anchor="w", padx=10, pady=2)
            ctk.CTkLabel(frame, text=f"📅 {appt_date.strftime('%Y-%m-%d at %H:%M')}", font=("Arial", 11)).pack(anchor="w", padx=10)
            ctk.CTkLabel(frame, text=f"⏰ In {days_until} days", text_color=color, font=("Arial", 11, "bold")).pack(anchor="w", padx=10)
            
            if notes:
                ctk.CTkLabel(frame, text=f"📝 {notes[:50]}...", font=("Arial", 10), text_color="gray").pack(anchor="w", padx=10)
            
            # Status indicators
            status_text = []
            if pdf_gen:
                status_text.append("✅ PDF Ready")
            if notif_sent:
                status_text.append("🔔 Notified")
            if status_text:
                ctk.CTkLabel(frame, text=" | ".join(status_text), font=("Arial", 9), text_color="#95a5a6").pack(anchor="w", padx=10)
            
            # Action buttons
            btn_frame = ctk.CTkFrame(frame)
            btn_frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkButton(btn_frame, text="📄 Generate PDF", width=120, height=30,
                         command=lambda p=patient, aid=appt_id: PDFReportGenerator(self.clinician_username).generate_patient_pdf(p, aid)).pack(side="left", padx=5)
            ctk.CTkButton(btn_frame, text="🗑️ Cancel", width=100, height=30, fg_color="#e74c3c",
                         command=lambda aid=appt_id: self.cancel_appointment(aid)).pack(side="left", padx=5)
    
    def cancel_appointment(self, appt_id):
        """Cancel an appointment"""
        if messagebox.askyesno("Confirm", "Cancel this appointment?"):
            conn = sqlite3.connect("therapist_app.db")
            conn.execute("DELETE FROM appointments WHERE id=?", (appt_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Appointment cancelled")
            self.refresh_appointments()
    
    def check_upcoming_appointments(self):
        """Check for appointments in 2 days and send notifications for PDF generation"""
        conn = sqlite3.connect("therapist_app.db")
        cursor = conn.cursor()
        
        # Find appointments 2 days out that haven't been notified
        two_days_ahead = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        appointments = cursor.execute("""
            SELECT id, patient_username, appointment_date FROM appointments
            WHERE clinician_username=? AND DATE(appointment_date)=? AND notification_sent=0
        """, (self.clinician_username, two_days_ahead)).fetchall()
        
        for appt_id, patient, appt_date in appointments:
            # Create notification
            message = f"⚠️ Appointment with {patient} in 2 days ({appt_date}). Generate progress PDF!"
            cursor.execute("INSERT INTO notifications (recipient_username, message, notification_type) VALUES (?, ?, 'appointment_reminder')",
                          (self.clinician_username, message))
            
            # Mark notification as sent
            cursor.execute("UPDATE appointments SET notification_sent=1 WHERE id=?", (appt_id,))
            
            log_event(self.clinician_username, 'system', 'appointment_reminder', 
                     f"2-day reminder for appointment with {patient}")
        
        conn.commit()
        conn.close()


class PDFReportGenerator:
    """Generates comprehensive PDF progress reports for patients"""
    
    def __init__(self, clinician_username):
        self.clinician_username = clinician_username
    
    def generate_patient_pdf(self, patient_username, appointment_id=None, prompt_save=True):
        """Generate comprehensive PDF report for a patient"""
        if not HAS_REPORTLAB:
            messagebox.showerror("Error", "reportlab library not installed. Cannot generate PDF.")
            return
        
        # Create patient data folder if it doesn't exist
        patient_folder = os.path.join("patient_data", patient_username)
        os.makedirs(patient_folder, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"{patient_username}_progress_report_{timestamp}.pdf"
        pdf_path = os.path.join(patient_folder, pdf_filename)
        
        try:
            # Fetch all patient data
            conn = sqlite3.connect("therapist_app.db")
            cursor = conn.cursor()
            
            # Profile
            profile = cursor.execute(
                "SELECT full_name, dob, conditions FROM users WHERE username=?", 
                (patient_username,)).fetchone()
            
            # Clinical scales
            scales = cursor.execute(
                "SELECT scale_name, score, severity, entry_timestamp FROM clinical_scales WHERE username=? ORDER BY entry_timestamp DESC LIMIT 20",
                (patient_username,)).fetchall()
            
            # Mood logs
            moods = cursor.execute(
                "SELECT mood_val, sleep_val, meds, notes, sentiment, exercise_mins, outside_mins, water_pints, entry_timestamp FROM mood_logs WHERE username=? ORDER BY entry_timestamp DESC LIMIT 30",
                (patient_username,)).fetchall()
            
            # Gratitude
            grats = cursor.execute(
                "SELECT entry, entry_timestamp FROM gratitude_logs WHERE username=? ORDER BY entry_timestamp DESC LIMIT 20",
                (patient_username,)).fetchall()
            
            # CBT records
            cbt = cursor.execute(
                "SELECT situation, thought, evidence, entry_timestamp FROM cbt_records WHERE username=? ORDER BY entry_timestamp DESC LIMIT 15",
                (patient_username,)).fetchall()
            
            # Safety plan
            safety = cursor.execute(
                "SELECT triggers, coping FROM safety_plans WHERE username=?",
                (patient_username,)).fetchone()
            
            # AI memory
            ai_mem = cursor.execute(
                "SELECT memory_summary, last_updated FROM ai_memory WHERE username=?",
                (patient_username,)).fetchone()
            
            conn.close()
            
            # Create PDF
            doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                                   rightMargin=72, leftMargin=72,
                                   topMargin=72, bottomMargin=18)
            
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=30,
                alignment=1  # Center
            )
            story.append(Paragraph(f"Clinical Progress Report", title_style))
            story.append(Paragraph(f"Patient: {patient_username}", styles['Heading2']))
            
            if profile:
                try:
                    full_name = decrypt_text(profile[0])
                    dob = decrypt_text(profile[1])
                    conditions = decrypt_text(profile[2])
                    story.append(Paragraph(f"Name: {full_name}", styles['Normal']))
                    story.append(Paragraph(f"DOB: {dob}", styles['Normal']))
                    story.append(Paragraph(f"Medical History: {conditions}", styles['Normal']))
                except:
                    pass
            
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
            story.append(Paragraph(f"Clinician: {self.clinician_username}", styles['Normal']))
            story.append(Spacer(1, 0.5*inch))
            
            # Clinical Assessments
            story.append(Paragraph("Clinical Assessments (PHQ-9 & GAD-7)", styles['Heading2']))
            if scales:
                scale_data = [['Date', 'Scale', 'Score', 'Severity']]
                for s in scales[:10]:
                    scale_data.append([s[3][:10], s[0], str(s[1]), s[2]])
                
                scale_table = Table(scale_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 1.5*inch])
                scale_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(scale_table)
            else:
                story.append(Paragraph("No clinical assessments recorded.", styles['Normal']))
            
            story.append(Spacer(1, 0.5*inch))
            
            # Mood & Health History
            story.append(Paragraph("Mood & Health History (Last 30 Days)", styles['Heading2']))
            if moods:
                for m in moods[:15]:
                    notes = decrypt_text(m[3]) if m[3] else "No notes"
                    mood_text = f"<b>{m[8][:10]}</b>: Mood {m[0]}/10, Sleep {m[1]}hrs, Meds: {m[2]}, Exercise: {m[5]}min"
                    story.append(Paragraph(mood_text, styles['Normal']))
                    if notes and notes != "No notes":
                        story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;Notes: {notes[:200]}", styles['Italic']))
                    story.append(Spacer(1, 0.1*inch))
            else:
                story.append(Paragraph("No mood logs recorded.", styles['Normal']))
            
            story.append(PageBreak())
            
            # Gratitude Journal
            story.append(Paragraph("Gratitude Journal Entries", styles['Heading2']))
            if grats:
                for g in grats[:10]:
                    try:
                        entry_text = decrypt_text(g[0])
                        story.append(Paragraph(f"<b>[{g[1][:10]}]</b>: {entry_text}", styles['Normal']))
                        story.append(Spacer(1, 0.1*inch))
                    except:
                        pass
            else:
                story.append(Paragraph("No gratitude entries recorded.", styles['Normal']))
            
            story.append(Spacer(1, 0.3*inch))
            
            # CBT Records
            story.append(Paragraph("CBT Thought Records", styles['Heading2']))
            if cbt:
                for c in cbt[:10]:
                    try:
                        situation = decrypt_text(c[0])
                        thought = decrypt_text(c[1])
                        evidence = decrypt_text(c[2])
                        story.append(Paragraph(f"<b>Date:</b> {c[3][:10]}", styles['Normal']))
                        story.append(Paragraph(f"<b>Situation:</b> {situation}", styles['Normal']))
                        story.append(Paragraph(f"<b>Thought:</b> {thought}", styles['Normal']))
                        story.append(Paragraph(f"<b>Evidence:</b> {evidence}", styles['Normal']))
                        story.append(Spacer(1, 0.2*inch))
                    except:
                        pass
            else:
                story.append(Paragraph("No CBT records recorded.", styles['Normal']))
            
            story.append(PageBreak())
            
            # Safety Plan
            story.append(Paragraph("Safety Plan", styles['Heading2']))
            if safety:
                story.append(Paragraph(f"<b>Triggers:</b> {safety[0]}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph(f"<b>Coping Strategies:</b> {safety[1]}", styles['Normal']))
            else:
                story.append(Paragraph("No safety plan created.", styles['Normal']))
            
            story.append(Spacer(1, 0.3*inch))
            
            # AI Memory Summary
            if ai_mem:
                story.append(Paragraph("AI Therapy Context Summary", styles['Heading2']))
                try:
                    memory_text = decrypt_text(ai_mem[0])
                    story.append(Paragraph(memory_text, styles['Normal']))
                    story.append(Paragraph(f"<i>Last updated: {ai_mem[1]}</i>", styles['Italic']))
                except:
                    pass
            
            # Build PDF
            doc.build(story)
            
            # Update database with PDF info
            if appointment_id:
                conn = sqlite3.connect("therapist_app.db")
                conn.execute(
                    "UPDATE appointments SET pdf_generated=1, pdf_path=? WHERE id=?",
                    (pdf_path, appointment_id))
                conn.commit()
                conn.close()
            
            log_event(self.clinician_username, 'clinician', 'pdf_generated',
                     f"Generated PDF for patient {patient_username}")
            
            if prompt_save:
                # Ask user where to save
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    initialfile=pdf_filename,
                    filetypes=[("PDF files", "*.pdf")])
                
                if save_path:
                    import shutil
                    shutil.copy2(pdf_path, save_path)
                    messagebox.showinfo("Success", f"PDF saved to:\n{save_path}\n\nOriginal stored in: {pdf_path}")
                else:
                    messagebox.showinfo("Success", f"PDF generated and stored in:\n{pdf_path}")
            else:
                messagebox.showinfo("Success", f"PDF generated and stored in:\n{pdf_path}")
            
            return pdf_path
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
