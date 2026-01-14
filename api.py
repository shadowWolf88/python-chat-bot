"""
Flask API wrapper for Healing Space Therapy App
Provides REST API endpoints while keeping desktop app intact
"""
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import json
import hashlib
import requests
from datetime import datetime
import sys

# Import existing modules (avoid importing main.py which has tkinter)
from secrets_manager import SecretsManager
from audit import log_event
from fhir_export import export_patient_fhir

# Import password hashing libraries with fallbacks (same logic as main.py)
try:
    from argon2 import PasswordHasher
    _ph = PasswordHasher()
    HAS_ARGON2 = True
except Exception:
    _ph = None
    HAS_ARGON2 = False

try:
    import bcrypt
    HAS_BCRYPT = True
except Exception:
    bcrypt = None
    HAS_BCRYPT = False

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Initialize with same settings as main app
DEBUG = os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes')

# Load secrets
secrets = SecretsManager(debug=DEBUG)
GROQ_API_KEY = secrets.get_secret("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
API_URL = os.environ.get("API_URL", "https://api.groq.com/openai/v1/chat/completions")
PIN_SALT = secrets.get_secret("PIN_SALT") or os.environ.get("PIN_SALT") or 'dev_fallback_salt'

# Password/PIN hashing functions (copied from main.py to avoid tkinter import)
def hash_password(password: str) -> str:
    """Hash password using Argon2 > bcrypt > PBKDF2 fallback"""
    if HAS_ARGON2 and _ph:
        return _ph.hash(password)
    if HAS_BCRYPT:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    # Fallback PBKDF2
    import hashlib
    salt = hashlib.sha256(password.encode()).hexdigest()[:16]
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 200000)
    return f"pbkdf2${dk.hex()}"

def verify_password(stored: str, password: str) -> bool:
    """Verify password against stored hash"""
    if not stored:
        return False
    if HAS_ARGON2 and _ph and stored.startswith('$argon2'):
        try:
            _ph.verify(stored, password)
            return True
        except Exception:
            return False
    if HAS_BCRYPT and stored.startswith("$2"):
        return bcrypt.checkpw(password.encode(), stored.encode())
    if stored.startswith("pbkdf2$"):
        dk = stored.split("$", 1)[1]
        salt = hashlib.sha256(password.encode()).hexdigest()[:16]
        new = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 200000).hex()
        return new == dk
    # Legacy SHA256 support
    if len(stored) == 64 and all(c in '0123456789abcdef' for c in stored.lower()):
        return hashlib.sha256(password.encode()).hexdigest() == stored
    return False

def hash_pin(pin: str) -> str:
    """Hash PIN using bcrypt or PBKDF2"""
    if HAS_BCRYPT:
        return bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()
    salt = hashlib.sha256(PIN_SALT.encode()).hexdigest()[:16]
    dk = hashlib.pbkdf2_hmac('sha256', pin.encode(), salt.encode(), 100000)
    return f"pbkdf2${dk.hex()}"

def check_pin(pin: str, stored: str) -> bool:
    """Verify PIN against stored hash"""
    if not stored:
        return False
    if stored.startswith("$2") and HAS_BCRYPT:
        return bcrypt.checkpw(pin.encode(), stored.encode())
    if stored.startswith("pbkdf2$"):
        dk = stored.split("$", 1)[1]
        salt = hashlib.sha256(PIN_SALT.encode()).hexdigest()[:16]
        new = hashlib.pbkdf2_hmac('sha256', pin.encode(), salt.encode(), 100000).hex()
        return new == dk
    return pin == stored

def init_db():
    """Initialize database with all required tables"""
    conn = sqlite3.connect("therapist_app.db")
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (username TEXT PRIMARY KEY, password TEXT, pin TEXT, last_login TIMESTAMP, 
                       full_name TEXT, dob TEXT, conditions TEXT, role TEXT DEFAULT 'user', 
                       clinician_id TEXT, disclaimer_accepted INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS sessions 
                      (session_id TEXT PRIMARY KEY, username TEXT, title TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS gratitude_logs 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, entry TEXT, entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS mood_logs 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, mood_val INTEGER, 
                       sleep_val REAL, meds TEXT, notes TEXT, sentiment TEXT,
                       exercise_mins INTEGER DEFAULT 0, outside_mins INTEGER DEFAULT 0, water_pints REAL DEFAULT 0,
                       entrestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS safety_plans
                      (username TEXT PRIMARY KEY, triggers TEXT, coping TEXT, contacts TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS ai_memory 
                      (username TEXT PRIMARY KEY, memory_summary TEXT, last_updated DATETIME)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS cbt_records 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, situation TEXT, thought TEXT, evidence TEXT, entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS clinical_scales
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, scale_name TEXT, score INTEGER, severity TEXT, entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS community_posts
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, message TEXT, likes INTEGER DEFAULT 0, entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS audit_logs
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, actor TEXT, action TEXT, details TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS alerts
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, alert_type TEXT, details TEXT, status TEXT DEFAULT 'open', created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS patient_approvals
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_username TEXT, clinician_username TEXT, 
                       status TEXT DEFAULT 'pending', request_date DATETIME DEFAULT CURRENT_TIMESTAMP, 
                       approval_date DATETIME)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS notifications
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, recipient_username TEXT, message TEXT, 
                       notification_type TEXT, read INTEGER DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS chat_history 
                      (session_id TEXT, sender TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
    
    conn.commit()
    conn.close()

class SafetyMonitor:
    """Safety monitoring for crisis detection"""
    def __init__(self):
        self.risk_keywords = [
            "kill myself", "suicide", "end my life", "want to die",
            "hurt myself", "self harm", "don't want to live", 
            "better off dead", "swallow pills", "overdose", "hanging myself", 
            "hurt someone else", "violent thoughts", "feeling hopeless", "no reason to live"
        ]

    def is_high_risk(self, text):
        clean_text = text.lower().strip()
        return any(phrase in clean_text for phrase in self.risk_keywords)
    
    def send_crisis_alert(self, user_details):
        try:
            username = user_details if isinstance(user_details, str) else user_details.get('username')
            details = str(user_details)
            conn = sqlite3.connect("therapist_app.db")
            conn.execute("INSERT INTO alerts (username, alert_type, details) VALUES (?,?,?)", (username, 'crisis', details))
            conn.commit()
            conn.close()
            log_event(username or 'unknown', 'system', 'crisis_alert_sent', details)
            return True
        except Exception:
            return False

class TherapistAI:
    """AI therapy interface"""
    def __init__(self, username=None):
        self.username = username
        self.headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    def get_response(self, user_message, chat_history=None):
        """Get AI response for therapy chat"""
        try:
            messages = [{"role": "system", "content": "You are a compassionate AI therapist. Provide supportive, empathetic responses."}]
            
            if chat_history:
                for sender, msg in chat_history[-10:]:
                    role = "assistant" if sender == "ai" else "user"
                    messages.append({"role": role, "content": msg})
            
            messages.append({"role": "user", "content": user_message})
            
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = requests.post(API_URL, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"I apologize, but I'm having trouble connecting right now. Error: {str(e)}"

# Crisis resources text
CRISIS_RESOURCES = """
*** IMPORTANT SAFETY NOTICE ***
If you are feeling overwhelmed and considering self-harm or ending your life, please reach out for help immediately. 

- UK: Call 999 or 111, or text SHOUT to 85258.
- USA/Canada: Call or text 988.
- International: Visit findahelpline.com
"""

# Initialize database on startup
try:
    init_db()
except Exception as e:
    print(f"Database initialization: {e}")

@app.route('/')
def index():
    """Serve simple web interface"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'healthy',
        'service': 'Healing Space Therapy API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        pin = data.get('pin')
        clinician_id = data.get('clinician_id')  # Required for patients
        
        if not username or not password or not pin:
            return jsonify({'error': 'Username, password, and PIN required'}), 400
        
        # Validate password complexity
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        if not any(c.islower() for c in password) or not any(c.isupper() for c in password):
            return jsonify({'error': 'Password must contain both uppercase and lowercase letters'}), 400
        if not any(c.isdigit() for c in password):
            return jsonify({'error': 'Password must contain at least one number'}), 400
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            return jsonify({'error': 'Password must contain at least one special character'}), 400
        
        if not clinician_id:
            return jsonify({'error': 'Please select your clinician'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        
        # Verify clinician exists
        clinician = cur.execute(
            "SELECT username FROM users WHERE username=? AND role='clinician'",
            (clinician_id,)
        ).fetchone()
        
        if not clinician:
            conn.close()
            return jsonify({'error': 'Invalid clinician ID. Please select a valid clinician.'}), 400
        
        # Check if user exists
        if cur.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone():
            conn.close()
            return jsonify({'error': 'Username already exists'}), 409
        
        # Hash credentials
        hashed_password = hash_password(password)
        hashed_pin = hash_pin(pin)
        
        # Create user WITHOUT clinician link (pending approval)
        cur.execute("INSERT INTO users (username, password, pin, last_login, role) VALUES (?,?,?,?,?)",
                   (username, hashed_password, hashed_pin, datetime.now(), 'user'))
        
        # Create pending approval request
        cur.execute("INSERT INTO patient_approvals (patient_username, clinician_username, status) VALUES (?,?,?)",
                   (username, clinician_id, 'pending'))
        
        # Notify clinician of new patient request
        cur.execute("INSERT INTO notifications (recipient_username, message, notification_type) VALUES (?,?,?)",
                   (clinician_id, f'New patient request from {username}', 'patient_request'))
        
        # Notify patient that request is pending
        cur.execute("INSERT INTO notifications (recipient_username, message, notification_type) VALUES (?,?,?)",
                   (username, f'Your request to join Dr. {clinician_id} is pending approval', 'approval_pending'))
        
        conn.commit()
        conn.close()
        
        log_event(username, 'api', 'user_registered', f'Registration via API, pending approval from clinician: {clinician_id}')
        
        return jsonify({
            'success': True,
            'message': 'Account created! Your clinician will approve your request shortly.',
            'username': username,
            'pending_approval': True
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user with 2FA PIN"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        pin = data.get('pin')  # Required for 2FA
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        if not pin:
            return jsonify({'error': 'PIN required for 2FA authentication'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        user = cur.execute("SELECT username, password, role, pin, clinician_id FROM users WHERE username=?", (username,)).fetchone()
        
        if not user:
            conn.close()
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verify password
        if not verify_password(user[1], password):
            conn.close()
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verify PIN (2FA)
        stored_pin = user[3]
        if not check_pin(pin, stored_pin):
            conn.close()
            return jsonify({'error': 'Invalid PIN'}), 401
        
        role = user[2] or 'user'
        clinician_id = user[4]
        
        # Check disclaimer acceptance
        disclaimer_accepted = cur.execute(
            "SELECT disclaimer_accepted FROM users WHERE username=?",
            (username,)
        ).fetchone()[0]
        
        # Check approval status for patients
        approval_status = 'approved'
        if role == 'user':
            approval = cur.execute(
                "SELECT status FROM patient_approvals WHERE patient_username=? ORDER BY request_date DESC LIMIT 1",
                (username,)
            ).fetchone()
            if approval:
                approval_status = approval[0]
        
        conn.close()
        
        log_event(username, 'api', 'user_login', 'Login via API with 2FA')
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'username': username,
            'role': role,
            'approval_status': approval_status,
            'clinician_id': clinician_id,
            'disclaimer_accepted': bool(disclaimer_accepted)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/clinician/register', methods=['POST'])
def clinician_register():
    """Register a new clinician account"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        pin = data.get('pin')
        full_name = data.get('full_name', '')
        
        if not username or not password or not pin:
            return jsonify({'error': 'Username, password, and PIN required'}), 400
        
        # Validate password complexity
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        if not any(c.islower() for c in password) or not any(c.isupper() for c in password):
            return jsonify({'error': 'Password must contain both uppercase and lowercase letters'}), 400
        if not any(c.isdigit() for c in password):
            return jsonify({'error': 'Password must contain at least one number'}), 400
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            return jsonify({'error': 'Password must contain at least one special character'}), 400
        
        if len(pin) != 4 or not pin.isdigit():
            return jsonify({'error': 'PIN must be exactly 4 digits'}), 400
        
        hashed_password = hash_password(password)
        hashed_pin = hash_pin(pin)
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        
        # Check if username exists
        existing = cur.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone()
        if existing:
            conn.close()
            return jsonify({'error': 'Username already exists'}), 409
        
        # Insert new clinician
        cur.execute(
            "INSERT INTO users (username, password, pin, role, full_name, last_login) VALUES (?,?,?,?,?,?)",
            (username, hashed_password, hashed_pin, 'clinician', full_name, datetime.now())
        )
        conn.commit()
        conn.close()
        
        log_event(username, 'api', 'clinician_registered', 'Clinician registration via API')
        
        return jsonify({'success': True, 'message': 'Clinician account created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/disclaimer/accept', methods=['POST'])
def accept_disclaimer():
    """Mark disclaimer as accepted for user"""
    try:
        data = request.json
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        cur.execute("UPDATE users SET disclaimer_accepted=1 WHERE username=?", (username,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clinicians/list', methods=['GET'])
def get_clinicians():
    """Get list of all clinicians for patient signup"""
    try:
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        clinicians = cur.execute(
            "SELECT username, full_name FROM users WHERE role='clinician' ORDER BY username"
        ).fetchall()
        conn.close()
        
        return jsonify({
            'clinicians': [
                {'username': c[0], 'full_name': c[1] or c[0]}
                for c in clinicians
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === NOTIFICATIONS ===
@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Get notifications for user"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        notifications = cur.execute(
            "SELECT id, message, notification_type, read, created_at FROM notifications WHERE recipient_username=? ORDER BY created_at DESC LIMIT 20",
            (username,)
        ).fetchall()
        conn.close()
        
        return jsonify({
            'notifications': [
                {
                    'id': n[0],
                    'message': n[1],
                    'type': n[2],
                    'read': bool(n[3]),
                    'created_at': n[4]
                } for n in notifications
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        cur.execute("UPDATE notifications SET read=1 WHERE id=?", (notification_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === PATIENT APPROVAL SYSTEM ===
@app.route('/api/approvals/pending', methods=['GET'])
def get_pending_approvals():
    """Get pending patient approval requests for clinician"""
    try:
        clinician = request.args.get('clinician')
        if not clinician:
            return jsonify({'error': 'Clinician username required'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        approvals = cur.execute(
            "SELECT id, patient_username, request_date FROM patient_approvals WHERE clinician_username=? AND status='pending' ORDER BY request_date DESC",
            (clinician,)
        ).fetchall()
        conn.close()
        
        return jsonify({
            'pending_approvals': [
                {
                    'id': a[0],
                    'patient_username': a[1],
                    'request_date': a[2]
                } for a in approvals
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/approvals/<int:approval_id>/approve', methods=['POST'])
def approve_patient(approval_id):
    """Approve patient request"""
    try:
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        
        # Get approval details
        approval = cur.execute(
            "SELECT patient_username, clinician_username FROM patient_approvals WHERE id=?",
            (approval_id,)
        ).fetchone()
        
        if not approval:
            conn.close()
            return jsonify({'error': 'Approval request not found'}), 404
        
        patient_username, clinician_username = approval
        
        # Update approval status
        cur.execute(
            "UPDATE patient_approvals SET status='approved', approval_date=? WHERE id=?",
            (datetime.now(), approval_id)
        )
        
        # Link patient to clinician
        cur.execute(
            "UPDATE users SET clinician_id=? WHERE username=?",
            (clinician_username, patient_username)
        )
        
        # Notify patient of approval
        cur.execute(
            "INSERT INTO notifications (recipient_username, message, notification_type) VALUES (?,?,?)",
            (patient_username, f'Dr. {clinician_username} has approved your request! You can now access all features.', 'approval_accepted')
        )
        
        # Notify clinician
        cur.execute(
            "INSERT INTO notifications (recipient_username, message, notification_type) VALUES (?,?,?)",
            (clinician_username, f'You approved {patient_username} as your patient', 'patient_approved')
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Patient approved successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/approvals/<int:approval_id>/reject', methods=['POST'])
def reject_patient(approval_id):
    """Reject patient request"""
    try:
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        
        # Get approval details
        approval = cur.execute(
            "SELECT patient_username, clinician_username FROM patient_approvals WHERE id=?",
            (approval_id,)
        ).fetchone()
        
        if not approval:
            conn.close()
            return jsonify({'error': 'Approval request not found'}), 404
        
        patient_username, clinician_username = approval
        
        # Update approval status
        cur.execute(
            "UPDATE patient_approvals SET status='rejected' WHERE id=?",
            (approval_id,)
        )
        
        # Notify patient of rejection
        cur.execute(
            "INSERT INTO notifications (recipient_username, message, notification_type) VALUES (?,?,?)",
            (patient_username, f'Dr. {clinician_username} declined your request. Please select another clinician.', 'approval_rejected')
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Patient request rejected'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/therapy/chat', methods=['POST'])
def therapy_chat():
    """AI therapy chat endpoint"""
    try:
        data = request.json
        username = data.get('username')
        message = data.get('message')
        
        if not username or not message:
            return jsonify({'error': 'Username and message required'}), 400
        
        # Use TherapistAI class
        ai = TherapistAI(username)
        
        # Get conversation history
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        history = cur.execute(
            "SELECT sender, message FROM chat_history WHERE session_id=? ORDER BY timestamp DESC LIMIT 10",
            (f"{username}_session",)
        ).fetchall()
        conn.close()
        
        # Get AI response using existing logic
        response = ai.get_response(message, history[::-1])
        
        # Save to chat history
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO chat_history (session_id, sender, message) VALUES (?,?,?)",
                   (f"{username}_session", "user", message))
        cur.execute("INSERT INTO chat_history (session_id, sender, message) VALUES (?,?,?)",
                   (f"{username}_session", "ai", response))
        conn.commit()
        conn.close()
        
        log_event(username, 'api', 'therapy_chat', 'Chat message sent')
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mood/log', methods=['POST'])
def log_mood():
    """Log mood entry with full tracking (water, exercise, meds with strength)"""
    try:
        data = request.json
        username = data.get('username')
        mood_val = data.get('mood_val')
        sleep_val = data.get('sleep_val', 0)
        meds = data.get('meds', '')  # Now expects JSON array of {name, strength, quantity}
        notes = data.get('notes', '')
        water_pints = data.get('water_pints', 0)
        exercise_mins = data.get('exercise_mins', 0)
        outside_mins = data.get('outside_mins', 0)
        
        if not username or mood_val is None:
            return jsonify({'error': 'Username and mood_val required'}), 400
        
        # Format medications if it's an array
        if isinstance(meds, list):
            meds_str = ", ".join([f"{m.get('name')} {m.get('strength')}mg (x{m.get('quantity', 1)})" for m in meds])
        else:
            meds_str = meds
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO mood_logs (username, mood_val, sleep_val, meds, notes, sentiment, 
               water_pints, exercise_mins, outside_mins) VALUES (?,?,?,?,?,?,?,?,?)""",
            (username, mood_val, sleep_val, meds_str, notes, 'Neutral', water_pints, exercise_mins, outside_mins)
        )
        conn.commit()
        log_id = cur.lastrowid
        conn.close()
        
        log_event(username, 'api', 'mood_logged', f'Mood: {mood_val}')
        
        return jsonify({
            'success': True,
            'message': 'Mood logged successfully',
            'log_id': log_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mood/history', methods=['GET'])
def mood_history():
    """Get mood history for user with all tracking data"""
    try:
        username = request.args.get('username')
        limit = request.args.get('limit', 30)
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        logs = cur.execute(
            """SELECT id, mood_val, sleep_val, meds, notes, entry_timestamp, 
               water_pints, exercise_mins, outside_mins 
               FROM mood_logs WHERE username=? ORDER BY entry_timestamp DESC LIMIT ?""",
            (username, limit)
        ).fetchall()
        conn.close()
        
        result = [{
            'id': log[0],
            'mood_val': log[1],
            'sleep_val': log[2],
            'meds': log[3],
            'notes': log[4],
            'timestamp': log[5],
            'water_pints': log[6] if len(log) > 6 else 0,
            'exercise_mins': log[7] if len(log) > 7 else 0,
            'outside_mins': log[8] if len(log) > 8 else 0
        } for log in logs]
        
        return jsonify({
            'success': True,
            'logs': result,
            'count': len(result)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gratitude/log', methods=['POST'])
def log_gratitude():
    """Log gratitude entry"""
    try:
        data = request.json
        username = data.get('username')
        entry = data.get('entry')
        
        if not username or not entry:
            return jsonify({'error': 'Username and entry required'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO gratitude_logs (username, entry) VALUES (?,?)", (username, entry))
        conn.commit()
        log_id = cur.lastrowid
        conn.close()
        
        log_event(username, 'api', 'gratitude_logged', 'Gratitude entry added')
        
        return jsonify({
            'success': True,
            'message': 'Gratitude logged successfully',
            'log_id': log_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/fhir', methods=['GET'])
def export_fhir():
    """Export user data in FHIR format"""
    try:
        username = request.args.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        # Use existing FHIR export function
        bundle = export_patient_fhir(username)
        
        log_event(username, 'api', 'fhir_export', 'FHIR data exported via API')
        
        return jsonify({
            'success': True,
            'bundle': json.loads(bundle)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/safety/check', methods=['POST'])
def safety_check():
    """Check text for safety concerns"""
    try:
        data = request.json
        text = data.get('text')
        username = data.get('username')
        
        if not text:
            return jsonify({'error': 'Text required'}), 400
        
        # Use SafetyMonitor
        monitor = SafetyMonitor()
        is_high_risk = monitor.is_high_risk(text)
        
        if is_high_risk and username:
            monitor.send_crisis_alert(username)
            log_event(username, 'api', 'crisis_alert', 'High risk detected via API')
        
        return jsonify({
            'success': True,
            'is_high_risk': is_high_risk,
            'crisis_resources': CRISIS_RESOURCES if is_high_risk else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== PET GAME ENDPOINTS =====
@app.route('/api/pet/status', methods=['GET'])
def pet_status():
    """Get pet status"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = sqlite3.connect("pet_game.db")
        cur = conn.cursor()
        pet = cur.execute("SELECT * FROM pet LIMIT 1").fetchone()
        conn.close()
        
        if not pet:
            return jsonify({'exists': False}), 200
        
        return jsonify({
            'exists': True,
            'pet': {
                'name': pet[1], 'species': pet[2], 'gender': pet[3],
                'hunger': pet[4], 'happiness': pet[5], 'energy': pet[6],
                'hygiene': pet[7], 'coins': pet[8], 'xp': pet[9],
                'stage': pet[10], 'hat': pet[13] if len(pet) > 13 else 'None'
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pet/create', methods=['POST'])
def pet_create():
    """Create new pet"""
    try:
        data = request.json
        name = data.get('name')
        species = data.get('species', 'Dog')
        gender = data.get('gender', 'Neutral')
        
        if not name:
            return jsonify({'error': 'Pet name required'}), 400
        
        conn = sqlite3.connect("pet_game.db")
        cur = conn.cursor()
        
        # Create table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pet (
                id INTEGER PRIMARY KEY,
                name TEXT, species TEXT, gender TEXT,
                hunger INTEGER, happiness INTEGER, energy INTEGER, hygiene INTEGER,
                coins INTEGER, xp INTEGER, stage TEXT, adventure_end REAL,
                last_updated REAL, hat TEXT
            )
        """)
        
        # Insert pet
        cur.execute("""
            INSERT INTO pet (name, species, gender, hunger, happiness, energy, hygiene, 
                           coins, xp, stage, adventure_end, last_updated, hat)
            VALUES (?, ?, ?, 70, 70, 70, 80, 0, 0, 'Baby', 0, ?, 'None')
        """, (name, species, gender, datetime.now().timestamp()))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Pet created!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pet/feed', methods=['POST'])
def pet_feed():
    """Feed pet (from shop)"""
    try:
        data = request.json
        item_cost = data.get('cost', 10)
        
        conn = sqlite3.connect("pet_game.db")
        cur = conn.cursor()
        pet = cur.execute("SELECT * FROM pet LIMIT 1").fetchone()
        
        if not pet:
            conn.close()
            return jsonify({'error': 'No pet found'}), 404
        
        coins = pet[8]
        if coins < item_cost:
            conn.close()
            return jsonify({'error': 'Not enough coins'}), 400
        
        # Update pet
        new_hunger = min(100, pet[4] + 30)
        new_coins = coins - item_cost
        cur.execute("UPDATE pet SET hunger=?, coins=? WHERE id=?", (new_hunger, new_coins, pet[0]))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'new_hunger': new_hunger, 'coins': new_coins}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pet/reward', methods=['POST'])
def pet_reward():
    """Reward pet for user self-care actions"""
    try:
        data = request.json
        action = data.get('action')  # 'therapy', 'mood', 'gratitude', 'breathing'
        
        conn = sqlite3.connect("pet_game.db")
        cur = conn.cursor()
        pet = cur.execute("SELECT * FROM pet LIMIT 1").fetchone()
        
        if not pet:
            conn.close()
            return jsonify({'success': False, 'message': 'No pet'}), 200
        
        # Reward logic (from original pet_game.py)
        coins_earned = 5
        xp_earned = 10
        happiness_boost = 5
        
        new_coins = pet[8] + coins_earned
        new_xp = pet[9] + xp_earned
        new_happiness = min(100, pet[5] + happiness_boost)
        
        cur.execute("UPDATE pet SET coins=?, xp=?, happiness=? WHERE id=?",
                   (new_coins, new_xp, new_happiness, pet[0]))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'coins_earned': coins_earned,
            'new_coins': new_coins,
            'new_xp': new_xp
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== CBT TOOLS ENDPOINTS =====
@app.route('/api/cbt/thought-record', methods=['POST'])
def cbt_thought_record():
    """Save CBT thought record"""
    try:
        data = request.json
        username = data.get('username')
        situation = data.get('situation')
        thought = data.get('thought')
        evidence = data.get('evidence')
        
        if not all([username, situation, thought]):
            return jsonify({'error': 'Username, situation, and thought required'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO cbt_records (username, situation, thought, evidence) VALUES (?,?,?,?)",
            (username, situation, thought, evidence or '')
        )
        conn.commit()
        record_id = cur.lastrowid
        conn.close()
        
        return jsonify({'success': True, 'record_id': record_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cbt/records', methods=['GET'])
def get_cbt_records():
    """Get user's CBT thought records"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        records = cur.execute(
            "SELECT id, situation, thought, evidence, entry_timestamp FROM cbt_records WHERE username=? ORDER BY entry_timestamp DESC LIMIT 20",
            (username,)
        ).fetchall()
        conn.close()
        
        result = [{
            'id': r[0], 'situation': r[1], 'thought': r[2],
            'evidence': r[3], 'timestamp': r[4]
        } for r in records]
        
        return jsonify({'success': True, 'records': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== CLINICAL SCALES ENDPOINTS =====
@app.route('/api/clinical/phq9', methods=['POST'])
def submit_phq9():
    """Submit PHQ-9 depression assessment"""
    try:
        data = request.json
        username = data.get('username')
        scores = data.get('scores')  # Array of 9 scores (0-3 each)
        
        if not username or not scores or len(scores) != 9:
            return jsonify({'error': 'Username and 9 scores required'}), 400
        
        total = sum(scores)
        if total <= 4:
            severity = "Minimal"
        elif total <= 9:
            severity = "Mild"
        elif total <= 14:
            severity = "Moderate"
        elif total <= 19:
            severity = "Moderately Severe"
        else:
            severity = "Severe"
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO clinical_scales (username, scale_name, score, severity) VALUES (?,?,?,?)",
            (username, 'PHQ-9', total, severity)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'score': total, 'severity': severity}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clinical/gad7', methods=['POST'])
def submit_gad7():
    """Submit GAD-7 anxiety assessment"""
    try:
        data = request.json
        username = data.get('username')
        scores = data.get('scores')  # Array of 7 scores (0-3 each)
        
        if not username or not scores or len(scores) != 7:
            return jsonify({'error': 'Username and 7 scores required'}), 400
        
        total = sum(scores)
        if total <= 4:
            severity = "Minimal"
        elif total <= 9:
            severity = "Mild"
        elif total <= 14:
            severity = "Moderate"
        else:
            severity = "Severe"
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO clinical_scales (username, scale_name, score, severity) VALUES (?,?,?,?)",
            (username, 'GAD-7', total, severity)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'score': total, 'severity': severity}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === COMMUNITY SUPPORT BOARD ===
@app.route('/api/community/posts', methods=['GET'])
def get_community_posts():
    """Get recent community posts"""
    try:
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        posts = cur.execute(
            "SELECT username, message, likes, entry_timestamp FROM community_posts ORDER BY entry_timestamp DESC LIMIT 20"
        ).fetchall()
        conn.close()
        
        return jsonify({'posts': [
            {
                'username': p[0],
                'message': p[1],
                'likes': p[2] or 0,
                'timestamp': p[3]
            } for p in posts
        ]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/community/post', methods=['POST'])
def create_community_post():
    """Create a new community post"""
    try:
        data = request.json
        username = data.get('username')
        message = data.get('message')
        
        if not username or not message:
            return jsonify({'error': 'Username and message required'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO community_posts (username, message) VALUES (?,?)",
            (username, message)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === SAFETY PLAN ===
@app.route('/api/safety-plan', methods=['GET'])
def get_safety_plan():
    """Get user's safety plan"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        plan = cur.execute(
            "SELECT triggers, coping_strategies, support_contacts, professional_contacts FROM safety_plans WHERE username=?",
            (username,)
        ).fetchone()
        conn.close()
        
        if plan:
            return jsonify({
                'triggers': plan[0],
                'coping_strategies': plan[1],
                'support_contacts': plan[2],
                'professional_contacts': plan[3]
            }), 200
        else:
            return jsonify({'triggers': '', 'coping_strategies': '', 'support_contacts': '', 'professional_contacts': ''}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/safety-plan', methods=['POST'])
def save_safety_plan():
    """Save or update user's safety plan"""
    try:
        data = request.json
        username = data.get('username')
        triggers = data.get('triggers', '')
        coping = data.get('coping_strategies', '')
        support = data.get('support_contacts', '')
        professional = data.get('professional_contacts', '')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        # Check if plan exists
        existing = cur.execute("SELECT username FROM safety_plans WHERE username=?", (username,)).fetchone()
        if existing:
            cur.execute(
                "UPDATE safety_plans SET triggers=?, coping_strategies=?, support_contacts=?, professional_contacts=? WHERE username=?",
                (triggers, coping, support, professional, username)
            )
        else:
            cur.execute(
                "INSERT INTO safety_plans (username, triggers, coping_strategies, support_contacts, professional_contacts) VALUES (?,?,?,?,?)",
                (username, triggers, coping, support, professional)
            )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === DATA EXPORT ===
@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export user data as CSV"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        import io
        import csv
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Profile
        writer.writerow(["USER PROFILE"])
        prof = cur.execute("SELECT full_name, dob, conditions FROM users WHERE username=?", (username,)).fetchone()
        if prof:
            writer.writerow(["username", username])
            writer.writerow(["full_name", prof[0]])
            writer.writerow(["dob", prof[1]])
            writer.writerow(["conditions", prof[2]])
        writer.writerow([])
        
        # Mood logs
        writer.writerow(["MOOD_LOGS"])
        writer.writerow(["timestamp", "mood_val", "sleep_val", "meds", "notes", "sentiment", "exercise_mins", "outside_mins", "water_pints"])
        for r in cur.execute("SELECT entry_timestamp, mood_val, sleep_val, meds, notes, sentiment, exercise_mins, outside_mins, water_pints FROM mood_logs WHERE username=? ORDER BY entry_timestamp DESC", (username,)).fetchall():
            writer.writerow([r[0], r[1], r[2], r[3], r[4] or "", r[5], r[6], r[7], r[8]])
        writer.writerow([])
        
        # Gratitude
        writer.writerow(["GRATITUDE_LOGS"])
        writer.writerow(["timestamp", "entry"])
        for r in cur.execute("SELECT entry_timestamp, entry FROM gratitude_logs WHERE username=? ORDER BY entry_timestamp DESC", (username,)).fetchall():
            writer.writerow([r[0], r[1]])
        writer.writerow([])
        
        # CBT
        writer.writerow(["CBT_RECORDS"])
        writer.writerow(["timestamp", "situation", "thought", "evidence"])
        for r in cur.execute("SELECT entry_timestamp, situation, thought, evidence FROM cbt_records WHERE username=? ORDER BY entry_timestamp DESC", (username,)).fetchall():
            writer.writerow([r[0], r[1], r[2], r[3]])
        writer.writerow([])
        
        # Clinical Scales
        writer.writerow(["CLINICAL_SCALES"])
        writer.writerow(["timestamp", "scale_name", "score", "severity"])
        for r in cur.execute("SELECT entry_timestamp, scale_name, score, severity FROM clinical_scales WHERE username=? ORDER BY entry_timestamp DESC", (username,)).fetchall():
            writer.writerow([r[0], r[1], r[2], r[3]])
        
        conn.close()
        
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = f"attachment; filename={username}_data.csv"
        response.headers["Content-Type"] = "text/csv"
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/pdf', methods=['GET'])
def export_pdf():
    """Export user data as PDF report"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        try:
            from fpdf import FPDF
        except ImportError:
            return jsonify({'error': 'PDF library not available'}), 500
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt=f"Mental Health Report - {username}", ln=True, align='C')
        pdf.ln(5)
        
        # Profile
        prof = cur.execute("SELECT full_name, dob, conditions FROM users WHERE username=?", (username,)).fetchone()
        if prof:
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 8, txt="Profile", ln=True)
            pdf.set_font("Arial", size=11)
            pdf.multi_cell(0, 6, txt=f"Name: {prof[0]}\nDOB: {prof[1]}\nConditions: {prof[2]}")
            pdf.ln(3)
        
        # Mood logs
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 8, txt="Mood Logs", ln=True)
        pdf.set_font("Arial", size=11)
        moods = cur.execute("SELECT entry_timestamp, mood_val, sleep_val, meds FROM mood_logs WHERE username=? ORDER BY entry_timestamp DESC LIMIT 10", (username,)).fetchall()
        for m in moods:
            pdf.multi_cell(0, 6, txt=f"[{m[0]}] Mood: {m[1]}/10, Sleep: {m[2]}h, Meds: {m[3] or 'None'}")
        pdf.ln(3)
        
        # Clinical scales
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 8, txt="Clinical Assessments", ln=True)
        pdf.set_font("Arial", size=11)
        scales = cur.execute("SELECT entry_timestamp, scale_name, score, severity FROM clinical_scales WHERE username=? ORDER BY entry_timestamp DESC", (username,)).fetchall()
        for s in scales:
            pdf.multi_cell(0, 6, txt=f"[{s[0]}] {s[1]}: Score {s[2]} ({s[3]})")
        
        conn.close()
        
        import tempfile
        import os
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name)
        
        with open(temp_file.name, 'rb') as f:
            pdf_data = f.read()
        
        os.unlink(temp_file.name)
        
        response = make_response(pdf_data)
        response.headers["Content-Disposition"] = f"attachment; filename={username}_report.pdf"
        response.headers["Content-Type"] = "application/pdf"
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === PROGRESS INSIGHTS ===
@app.route('/api/insights', methods=['GET'])
def get_insights():
    """Get AI-generated progress insights"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        
        # Get recent mood data for trends
        moods = cur.execute(
            "SELECT mood_val, sleep_val, entry_timestamp FROM mood_logs WHERE username=? ORDER BY entry_timestamp DESC LIMIT 7",
            (username,)
        ).fetchall()
        
        # Get recent gratitude entries
        gratitudes = cur.execute(
            "SELECT entry FROM gratitude_logs WHERE username=? ORDER BY entry_timestamp DESC LIMIT 5",
            (username,)
        ).fetchall()
        
        # Get CBT records
        cbt = cur.execute(
            "SELECT COUNT(*) FROM cbt_records WHERE username=?",
            (username,)
        ).fetchone()[0]
        
        # Get safety plan
        safety = cur.execute(
            "SELECT triggers, coping_strategies FROM safety_plans WHERE username=?",
            (username,)
        ).fetchone()
        
        conn.close()
        
        # Calculate trends
        mood_trend = "stable"
        if len(moods) >= 3:
            recent_avg = sum(m[0] for m in moods[:3]) / 3
            older_avg = sum(m[0] for m in moods[3:]) / max(1, len(moods) - 3)
            if recent_avg > older_avg + 1:
                mood_trend = "improving"
            elif recent_avg < older_avg - 1:
                mood_trend = "declining"
        
        avg_mood = sum(m[0] for m in moods) / len(moods) if moods else 0
        avg_sleep = sum(m[1] for m in moods) / len(moods) if moods else 0
        
        insight = f"Your average mood over the last 7 entries is {avg_mood:.1f}/10 (trend: {mood_trend}). "
        insight += f"Average sleep: {avg_sleep:.1f} hours. "
        insight += f"You've completed {cbt} CBT thought records. "
        insight += f"You've logged {len(gratitudes)} gratitude entries recently. "
        
        if mood_trend == "declining":
            insight += "Consider reaching out to your support network or reviewing your safety plan."
        elif mood_trend == "improving":
            insight += "Great progress! Keep up the self-care routines that are working for you."
        
        return jsonify({
            'insight': insight,
            'mood_data': [{'value': m[0], 'timestamp': m[2]} for m in reversed(moods)],
            'sleep_data': [{'value': m[1], 'timestamp': m[2]} for m in reversed(moods)],
            'avg_mood': round(avg_mood, 1),
            'avg_sleep': round(avg_sleep, 1),
            'trend': mood_trend
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === PROFESSIONAL DASHBOARD ===
@app.route('/api/professional/patients', methods=['GET'])
def get_patients():
    """Get list of all patients assigned to logged-in clinician"""
    try:
        clinician_username = request.args.get('clinician')
        
        if not clinician_username:
            return jsonify({'error': 'Clinician username required'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        
        # Get only patients assigned to this clinician
        users = cur.execute(
            "SELECT username FROM users WHERE role='user' AND clinician_id=?",
            (clinician_username,)
        ).fetchall()
        
        patient_list = []
        for user in users:
            username = user[0]
            
            # Get recent mood average
            mood_avg = cur.execute(
                "SELECT AVG(mood_val) FROM mood_logs WHERE username=? AND entry_timestamp > datetime('now', '-7 days')",
                (username,)
            ).fetchone()[0] or 0
            
            # Get alert count
            alert_count = cur.execute(
                "SELECT COUNT(*) FROM safety_alerts WHERE username=? AND entry_timestamp > datetime('now', '-7 days')",
                (username,)
            ).fetchone()[0]
            
            # Get latest assessment
            latest_scale = cur.execute(
                "SELECT scale_name, score, severity, entry_timestamp FROM clinical_scales WHERE username=? ORDER BY entry_timestamp DESC LIMIT 1",
                (username,)
            ).fetchone()
            
            patient_list.append({
                'username': username,
                'avg_mood_7d': round(mood_avg, 1),
                'alert_count_7d': alert_count,
                'latest_assessment': {
                    'name': latest_scale[0],
                    'score': latest_scale[1],
                    'severity': latest_scale[2],
                    'date': latest_scale[3]
                } if latest_scale else None
            })
        
        conn.close()
        return jsonify({'patients': patient_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/professional/patient/<username>', methods=['GET'])
def get_patient_detail(username):
    """Get detailed patient data (for professional dashboard)"""
    try:
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        
        # Profile
        profile = cur.execute(
            "SELECT full_name, dob, conditions FROM users WHERE username=?",
            (username,)
        ).fetchone()
        
        # Recent moods
        moods = cur.execute(
            "SELECT mood_val, sleep_val, entry_timestamp FROM mood_logs WHERE username=? ORDER BY entry_timestamp DESC LIMIT 10",
            (username,)
        ).fetchall()
        
        # Recent alerts
        alerts = cur.execute(
            "SELECT alert_type, message, entry_timestamp FROM safety_alerts WHERE username=? ORDER BY entry_timestamp DESC LIMIT 5",
            (username,)
        ).fetchall()
        
        # Clinical scales
        scales = cur.execute(
            "SELECT scale_name, score, severity, entry_timestamp FROM clinical_scales WHERE username=? ORDER BY entry_timestamp DESC LIMIT 5",
            (username,)
        ).fetchall()
        
        conn.close()
        
        return jsonify({
            'username': username,
            'profile': {
                'name': profile[0] if profile else '',
                'dob': profile[1] if profile else '',
                'conditions': profile[2] if profile else ''
            },
            'recent_moods': [
                {'mood': m[0], 'sleep': m[1], 'timestamp': m[2]} for m in moods
            ],
            'recent_alerts': [
                {'type': a[0], 'message': a[1], 'timestamp': a[2]} for a in alerts
            ],
            'clinical_scales': [
                {'name': s[0], 'score': s[1], 'severity': s[2], 'timestamp': s[3]} for s in scales
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=DEBUG)
