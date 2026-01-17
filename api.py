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
from datetime import datetime, timedelta
import sys
import secrets
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

# Database path - use volume on Railway, local otherwise
def get_db_path():
    """Get database path - use Railway volume if available"""
    if os.path.exists('/app/data'):
        # Railway volume mounted
        return '/app/data/therapist_app.db'
    return 'therapist_app.db'

DB_PATH = get_db_path()

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
    conn = sqlite3.connect(DB_PATH)
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
    cursor.execute('''CREATE TABLE IF NOT EXISTS community_likes
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, UNIQUE(post_id, username))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS community_replies
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS clinician_notes
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, clinician_username TEXT, patient_username TEXT, note_text TEXT, 
                       is_highlighted INTEGER DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
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
    
    # Add email and phone columns if they don't exist
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN reset_token_expiry DATETIME")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
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
            conn = sqlite3.connect(DB_PATH)
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
        """Get AI response for therapy chat with full context"""
        try:
            # Get user context from AI memory
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            memory = cur.execute(
                "SELECT memory_summary FROM ai_memory WHERE username=?",
                (self.username,)
            ).fetchone()
            
            # Get clinician notes for context
            clinician_notes = cur.execute(
                "SELECT note_text FROM clinician_notes WHERE patient_username=? ORDER BY created_at DESC LIMIT 3",
                (self.username,)
            ).fetchall()
            
            conn.close()
            
            # Build system prompt with context
            system_prompt = "You are a compassionate AI therapist. Provide supportive, empathetic responses."
            
            if memory:
                system_prompt += f"\n\nPatient context: {memory[0]}"
            
            if clinician_notes:
                notes_text = "; ".join([note[0] for note in clinician_notes])
                system_prompt += f"\n\nClinician's recent notes: {notes_text[:300]}"
            
            messages = [{"role": "system", "content": system_prompt}]
            
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
        email = data.get('email')
        phone = data.get('phone')
        full_name = data.get('full_name')
        dob = data.get('dob')
        conditions = data.get('conditions')
        clinician_id = data.get('clinician_id')  # Required for patients
        
        if not username or not password or not pin or not email or not phone:
            return jsonify({'error': 'All fields are required'}), 400
        
        if not full_name:
            return jsonify({'error': 'Full name is required'}), 400
        
        if not dob:
            return jsonify({'error': 'Date of birth is required'}), 400
        
        if not conditions:
            return jsonify({'error': 'Medical conditions/diagnosis is required'}), 400
        
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
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Verify clinician exists
        clinician = cur.execute(
            "SELECT username FROM users WHERE username=? AND role='clinician'",
            (clinician_id,)
        ).fetchone()
        
        if not clinician:
            conn.close()
            return jsonify({'error': 'Invalid clinician ID. Please select a valid clinician.'}), 400
        
        # Check if username exists
        if cur.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone():
            conn.close()
            return jsonify({'error': 'Username already exists'}), 409
        
        # Check if email exists
        if cur.execute("SELECT username FROM users WHERE email=?", (email,)).fetchone():
            conn.close()
            return jsonify({'error': 'Email already in use'}), 409
        
        # Check if phone exists
        if cur.execute("SELECT username FROM users WHERE phone=?", (phone,)).fetchone():
            conn.close()
            return jsonify({'error': 'Phone number already in use'}), 409
        
        # Hash credentials
        hashed_password = hash_password(password)
        hashed_pin = hash_pin(pin)
        
        # Create user with full profile information
        cur.execute("INSERT INTO users (username, password, pin, email, phone, full_name, dob, conditions, last_login, role) VALUES (?,?,?,?,?,?,?,?,?,?)",
                   (username, hashed_password, hashed_pin, email, phone, full_name, dob, conditions, datetime.now(), 'user'))
        
        # Create pending approval request
        cur.execute("INSERT INTO patient_approvals (patient_username, clinician_username, status) VALUES (?,?,?)",
                   (username, clinician_id, 'pending'))
        
        # Notify clinician of new patient request
        cur.execute("INSERT INTO notifications (recipient_username, message, notification_type) VALUES (?,?,?)",
                   (clinician_id, f'New patient request from {full_name} ({username})', 'patient_request'))
        
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
        
        conn = sqlite3.connect(DB_PATH)
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

@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset email"""
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        
        if not username or not email:
            return jsonify({'error': 'Username and email required'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Verify user exists and email matches
        user = cur.execute(
            "SELECT email FROM users WHERE username=? AND email=?",
            (username, email)
        ).fetchone()
        
        if not user:
            # Don't reveal if user exists for security
            return jsonify({'success': True, 'message': 'If account exists, reset link sent'}), 200
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        expiry = datetime.now() + timedelta(hours=1)
        
        # Store token
        cur.execute(
            "UPDATE users SET reset_token=?, reset_token_expiry=? WHERE username=?",
            (reset_token, expiry, username)
        )
        conn.commit()
        conn.close()
        
        # Send email
        try:
            send_reset_email(email, username, reset_token)
            log_event(username, 'api', 'password_reset_requested', f'Reset requested for {email}')
            
            return jsonify({
                'success': True,
                'message': 'Password reset link sent to your email'
            }), 200
        except Exception as email_error:
            # Email failed but token is stored - provide helpful error
            return jsonify({
                'error': 'Failed to send email. Please contact support or try again later.',
                'details': str(email_error) if DEBUG else None
            }), 500
        
    except Exception as e:
        print(f"Password reset error: {e}")
        return jsonify({'error': 'Password reset failed', 'details': str(e) if DEBUG else None}), 500

def send_reset_email(to_email, username, reset_token):
    """Send password reset email via SMTP"""
    try:
        # Get SMTP credentials from environment
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_user = os.getenv('SMTP_USER')
        smtp_password = os.getenv('SMTP_PASSWORD')
        from_email = os.getenv('FROM_EMAIL', smtp_user)
        
        if not smtp_user or not smtp_password:
            error_msg = "SMTP credentials not configured. Set SMTP_USER and SMTP_PASSWORD environment variables."
            print(error_msg)
            raise Exception(error_msg)
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Healing Space - Password Reset'
        msg['From'] = from_email
        msg['To'] = to_email
        
        # Reset URL (use Railway URL or localhost)
        base_url = os.getenv('APP_URL', 'http://localhost:5000')
        reset_url = f"{base_url}/reset-password?token={reset_token}&username={username}"
        
        html = f"""
        <html>
          <body>
            <h2>Password Reset Request</h2>
            <p>Hello {username},</p>
            <p>You requested to reset your password. Click the link below to reset it:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>This link expires in 1 hour.</p>
            <p>If you didn't request this, please ignore this email.</p>
            <br>
            <p>Best regards,<br>Healing Space Team</p>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        print(f"Reset email sent to {to_email}")
        return True
        
    except Exception as e:
        error_msg = f"Email send error: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)

@app.route('/api/auth/clinician/register', methods=['POST'])
def clinician_register():
    """Register a new clinician account"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        pin = data.get('pin')
        full_name = data.get('full_name', '')
        email = data.get('email')
        phone = data.get('phone')
        
        if not username or not password or not pin or not email or not phone:
            return jsonify({'error': 'All fields are required'}), 400
        
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
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Check if username exists
        if cur.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone():
            conn.close()
            return jsonify({'error': 'Username already exists'}), 409
        
        # Check if email exists
        if cur.execute("SELECT username FROM users WHERE email=?", (email,)).fetchone():
            conn.close()
            return jsonify({'error': 'Email already in use'}), 409
        
        # Check if phone exists
        if cur.execute("SELECT username FROM users WHERE phone=?", (phone,)).fetchone():
            conn.close()
            return jsonify({'error': 'Phone number already in use'}), 409
        
        # Insert new clinician
        cur.execute(
            "INSERT INTO users (username, password, pin, role, full_name, email, phone, last_login) VALUES (?,?,?,?,?,?,?,?)",
            (username, hashed_password, hashed_pin, 'clinician', full_name, email, phone, datetime.now())
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
        
        conn = sqlite3.connect(DB_PATH)
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
        conn = sqlite3.connect(DB_PATH)
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
        
        conn = sqlite3.connect(DB_PATH)
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
        conn = sqlite3.connect(DB_PATH)
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
        
        conn = sqlite3.connect(DB_PATH)
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
        conn = sqlite3.connect(DB_PATH)
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
        conn = sqlite3.connect(DB_PATH)
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

def update_ai_memory(username):
    """Update AI memory with recent user activity summary including clinician notes"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Get recent activities
        recent_moods = cur.execute(
            "SELECT mood_val, notes, entrestamp FROM mood_logs WHERE username=? ORDER BY entrestamp DESC LIMIT 5",
            (username,)
        ).fetchall()
        
        recent_assessments = cur.execute(
            "SELECT scale_name, score, severity FROM clinical_scales WHERE username=? ORDER BY entry_timestamp DESC LIMIT 3",
            (username,)
        ).fetchall()
        
        recent_cbt = cur.execute(
            "SELECT thought, evidence FROM cbt_records WHERE username=? ORDER BY entry_timestamp DESC LIMIT 3",
            (username,)
        ).fetchall()
        
        recent_alerts = cur.execute(
            "SELECT alert_type, details FROM alerts WHERE username=? ORDER BY created_at DESC LIMIT 3",
            (username,)
        ).fetchall()
        
        # Get clinician notes (including face-to-face appointment notes)
        clinician_notes = cur.execute(
            "SELECT note_text, created_at FROM clinician_notes WHERE patient_username=? ORDER BY created_at DESC LIMIT 5",
            (username,)
        ).fetchall()
        
        # Get gratitude entries
        recent_gratitude = cur.execute(
            "SELECT entry FROM gratitude_logs WHERE username=? ORDER BY entry_timestamp DESC LIMIT 3",
            (username,)
        ).fetchall()
        
        # Build memory summary
        memory_parts = []
        
        if recent_moods:
            avg_mood = sum(m[0] for m in recent_moods) / len(recent_moods)
            memory_parts.append(f"Recent mood average: {avg_mood:.1f}/10")
            if recent_moods[0][1]:  # Latest mood note
                memory_parts.append(f"Latest concern: {recent_moods[0][1][:100]}")
        
        if recent_assessments:
            latest = recent_assessments[0]
            memory_parts.append(f"Latest assessment: {latest[0]} - {latest[2]} severity (score: {latest[1]})")
        
        if recent_cbt:
            memory_parts.append(f"Working on CBT: {len(recent_cbt)} recent exercises")
        
        if recent_alerts:
            memory_parts.append(f"⚠️ Safety concerns: {len(recent_alerts)} recent alerts")
        
        if clinician_notes:
            memory_parts.append(f"Clinician notes: {len(clinician_notes)} recent entries")
            # Include most recent highlighted note
            highlighted = cur.execute(
                "SELECT note_text FROM clinician_notes WHERE patient_username=? AND is_highlighted=1 ORDER BY created_at DESC LIMIT 1",
                (username,)
            ).fetchone()
            if highlighted:
                memory_parts.append(f"Key note: {highlighted[0][:100]}")
        
        if recent_gratitude:
            memory_parts.append(f"Practicing gratitude: {len(recent_gratitude)} recent entries")
        
        memory_summary = "; ".join(memory_parts) if memory_parts else "New user, no activity yet"
        
        # Update or insert memory
        cur.execute(
            "INSERT OR REPLACE INTO ai_memory (username, memory_summary, last_updated) VALUES (?,?,?)",
            (username, memory_summary, datetime.now())
        )
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"AI memory update error: {e}")

def send_notification(username, message, notification_type='info'):
    """Helper function to send notification to user"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO notifications (recipient_username, message, notification_type) VALUES (?,?,?)",
            (username, message, notification_type)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Notification error: {e}")
        return False

def reward_pet(action, activity_type=None):
    """Helper function to reward pet for user activities
    
    Pet Attribute Effects:
    - Base boost: +3 to ALL attributes (hunger, happiness, energy, hygiene)
    - Mood logging: +10 happiness, +5 energy (total: +13 happiness, +8 energy, +3 hunger/hygiene)
    - Gratitude: +10 happiness, +5 energy (total: +13 happiness, +8 energy, +3 hunger/hygiene)
    - CBT exercises: +15 coins, +20 XP (vs base 5 coins, 15 XP)
    - Assessments: +20 coins, +30 XP (vs base 5 coins, 15 XP)
    - Therapy: +10 hunger, +10 happiness, +10 energy, +5 hygiene, +30 XP
    
    Attributes deplete over time at 0.5 per hour (gentle decay).
    """
    try:
        conn = sqlite3.connect("pet_game.db")
        cur = conn.cursor()
        pet = cur.execute("SELECT * FROM pet LIMIT 1").fetchone()
        
        if not pet:
            conn.close()
            return False
        
        # Standardized rewards matching pet_game.py
        base_boost = 3
        coin_gain = 5
        xp_gain = 15
        
        # Apply specific bonuses
        hun = base_boost
        hap = base_boost
        en = base_boost
        hyg = base_boost
        
        if action == 'mood':
            hap += 10
            en += 5
        elif action == 'gratitude':
            hap += 10
            en += 5
        elif action == 'therapy':
            hun += 10
            hap += 10
            en += 10
            hyg += 5
            xp_gain = 30
        
        if activity_type == 'cbt':
            coin_gain += 10
            xp_gain += 5
        elif activity_type == 'clinical':
            coin_gain += 15
            xp_gain += 15
        
        # Calculate new stats
        new_hunger = max(0, min(100, pet[4] + hun))
        new_happiness = max(0, min(100, pet[5] + hap))
        new_energy = max(0, min(100, pet[6] + en))
        new_hygiene = max(0, min(100, pet[7] + hyg))
        new_coins = pet[8] + coin_gain
        new_xp = pet[9] + xp_gain
        
        # Check evolution
        stage = pet[10]
        if new_xp >= 500 and stage == 'Baby':
            stage = 'Child'
        elif new_xp >= 1500 and stage == 'Child':
            stage = 'Adult'
        
        cur.execute(
            "UPDATE pet SET hunger=?, happiness=?, energy=?, hygiene=?, coins=?, xp=?, stage=?, last_updated=? WHERE id=?",
            (new_hunger, new_happiness, new_energy, new_hygiene, new_coins, new_xp, stage, time.time(), pet[0])
        )
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Pet reward error: {e}")
        return False

@app.route('/api/therapy/chat', methods=['POST'])
def therapy_chat():
    """AI therapy chat endpoint"""
    try:
        data = request.json
        username = data.get('username')
        message = data.get('message')
        
        if not username or not message:
            return jsonify({'error': 'Username and message required'}), 400
        
        # Update AI memory before chat
        update_ai_memory(username)
        
        # Use TherapistAI class
        ai = TherapistAI(username)
        
        # Get conversation history
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        history = cur.execute(
            "SELECT sender, message FROM chat_history WHERE session_id=? ORDER BY timestamp DESC LIMIT 10",
            (f"{username}_session",)
        ).fetchall()
        
        # Get AI memory to include in context
        memory = cur.execute(
            "SELECT memory_summary FROM ai_memory WHERE username=?",
            (username,)
        ).fetchone()
        
        conn.close()
        
        # Get AI response using existing logic
        response = ai.get_response(message, history[::-1])
        
        # Save to chat history
        conn = sqlite3.connect(DB_PATH)
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

@app.route('/api/therapy/history', methods=['GET'])
def get_chat_history():
    """Get chat history for a user"""
    try:
        username = request.args.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        history = cur.execute(
            "SELECT sender, message, timestamp FROM chat_history WHERE session_id=? ORDER BY timestamp ASC",
            (f"{username}_session",)
        ).fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'history': [{'sender': h[0], 'message': h[1], 'timestamp': h[2]} for h in history]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/therapy/greeting', methods=['POST'])
def get_therapy_greeting():
    """Get personalized greeting based on user context"""
    try:
        data = request.json
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        # Update AI memory with latest context
        update_ai_memory(username)
        
        # Use TherapistAI to generate contextual greeting
        ai = TherapistAI(username)
        
        # Get user context
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        memory = cur.execute(
            "SELECT memory_summary FROM ai_memory WHERE username=?",
            (username,)
        ).fetchone()
        
        # Check if they logged mood today
        logged_today = cur.execute(
            "SELECT mood_val FROM mood_logs WHERE username=? AND date(entrestamp) = date('now', 'localtime')",
            (username,)
        ).fetchone()
        
        conn.close()
        
        # Build contextual greeting prompt
        context_parts = []
        if memory and memory[0]:
            context_parts.append(f"Patient context: {memory[0]}")
        if logged_today:
            context_parts.append(f"They logged their mood today (mood: {logged_today[0]}/10)")
        else:
            context_parts.append("They haven't logged their mood today yet")
        
        greeting_prompt = f"Greet the user warmly and ask how they're doing today. Context: {'; '.join(context_parts)}. Keep it brief (2-3 sentences)."
        
        greeting = ai.get_response(greeting_prompt, [])
        
        return jsonify({
            'success': True,
            'greeting': greeting
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/therapy/initialize', methods=['POST'])
def initialize_chat():
    """Initialize chat for new users - creates first AI interaction and memory bank"""
    try:
        data = request.json
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Check if chat already initialized (has any chat history)
        existing_chat = cur.execute(
            "SELECT COUNT(*) FROM chat_history WHERE session_id=?",
            (f"{username}_session",)
        ).fetchone()[0]
        
        if existing_chat > 0:
            conn.close()
            return jsonify({
                'success': True,
                'message': 'Chat already initialized',
                'already_exists': True
            }), 200
        
        # Get user profile info
        user_info = cur.execute(
            "SELECT full_name, dob, conditions FROM users WHERE username=?",
            (username,)
        ).fetchone()
        
        full_name = user_info[0] if user_info and user_info[0] else username
        dob = user_info[1] if user_info and user_info[1] else "not provided"
        conditions = user_info[2] if user_info and user_info[2] else "not yet shared"
        
        # Create initial welcome message from AI
        ai = TherapistAI(username)
        welcome_prompt = f"""This is the first time meeting {full_name}. Their medical conditions: {conditions}. 
        Create a warm, professional welcome message (2-3 sentences) that:
        1. Introduces yourself as their AI therapy companion
        2. Explains you'll be tracking their progress and supporting their mental health journey
        3. Asks them to share what brings them here today
        Keep it warm, professional, and encouraging."""
        
        welcome_message = ai.get_response(welcome_prompt, [])
        
        # Save welcome message to chat history
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(
            "INSERT INTO chat_history (session_id, sender, message, timestamp) VALUES (?,?,?,?)",
            (f"{username}_session", 'ai', welcome_message, timestamp)
        )
        
        # Initialize AI memory with profile data
        initial_memory = f"Patient: {full_name}. Date of Birth: {dob}. Medical conditions: {conditions}. First session: {timestamp}."
        cur.execute(
            "INSERT OR REPLACE INTO ai_memory (username, memory_summary, last_updated) VALUES (?,?,?)",
            (username, initial_memory, timestamp)
        )
        
        conn.commit()
        conn.close()
        
        log_event(username, 'system', 'chat_initialized', 'First-time chat and memory bank created')
        
        return jsonify({
            'success': True,
            'message': 'Chat initialized successfully',
            'welcome_message': welcome_message,
            'already_exists': False
        }), 201
        
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
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Check if user already logged mood today
        existing_today = cur.execute(
            """SELECT id FROM mood_logs 
               WHERE username=? AND date(entrestamp) = date('now', 'localtime')""",
            (username,)
        ).fetchone()
        
        if existing_today:
            conn.close()
            return jsonify({'error': 'You have already logged your mood today. Only one entry per day is allowed.'}), 409
        
        # Format medications if it's an array
        if isinstance(meds, list):
            meds_str = ", ".join([f"{m.get('name')} {m.get('strength')}mg (x{m.get('quantity', 1)})" for m in meds])
        else:
            meds_str = meds
        
        cur.execute(
            """INSERT INTO mood_logs (username, mood_val, sleep_val, meds, notes, sentiment, 
               water_pints, exercise_mins, outside_mins) VALUES (?,?,?,?,?,?,?,?,?)""",
            (username, mood_val, sleep_val, meds_str, notes, 'Neutral', water_pints, exercise_mins, outside_mins)
        )
        conn.commit()
        log_id = cur.lastrowid
        conn.close()
        
        # Update AI memory with new activity
        update_ai_memory(username)
        
        # Reward pet for self-care activity
        reward_pet('mood')
        
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
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        logs = cur.execute(
            """SELECT id, mood_val, sleep_val, meds, notes, entrestamp, 
               water_pints, exercise_mins, outside_mins 
               FROM mood_logs WHERE username=? ORDER BY entrestamp DESC LIMIT ?""",
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
    """Log gratitude entry - automatically updates AI memory"""
    try:
        data = request.json
        username = data.get('username')
        entry = data.get('entry')
        
        if not username or not entry:
            return jsonify({'error': 'Username and entry required'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO gratitude_logs (username, entry) VALUES (?,?)", (username, entry))
        conn.commit()
        log_id = cur.lastrowid
        conn.close()
        
        # AUTO-UPDATE AI MEMORY
        update_ai_memory(username)
        
        # Reward pet for self-care activity
        reward_pet('gratitude')
        
        log_event(username, 'api', 'gratitude_logged', 'Gratitude entry added, AI memory updated')
        
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
    """Reward pet for user self-care actions - matches original desktop app logic"""
    try:
        data = request.json
        action = data.get('action')  # 'therapy', 'mood', 'gratitude', 'breathing', 'cbt', 'clinical'
        activity_type = data.get('activity_type')  # 'cbt', 'clinical', etc.
        
        conn = sqlite3.connect("pet_game.db")
        cur = conn.cursor()
        pet = cur.execute("SELECT * FROM pet LIMIT 1").fetchone()
        
        if not pet:
            conn.close()
            return jsonify({'success': False, 'message': 'No pet'}), 200
        
        # Standardized rewards matching pet_game.py
        base_boost = 3
        coin_gain = 5
        xp_gain = 15
        
        # Apply specific bonuses (matching original desktop app)
        hun = base_boost
        hap = base_boost
        en = base_boost
        hyg = base_boost
        
        if action == 'mood':
            hap += 10
            en += 5
        elif action == 'gratitude':
            hap += 10
            en += 5
        elif action == 'therapy':
            hun += 10
            hap += 10
            en += 10
            hyg += 5
            xp_gain = 30
        
        if activity_type == 'cbt':
            coin_gain += 10
            xp_gain += 5
        elif activity_type == 'clinical':
            coin_gain += 15
            xp_gain += 15
        
        # Calculate new stats
        new_hunger = max(0, min(100, pet[4] + hun))
        new_happiness = max(0, min(100, pet[5] + hap))
        new_energy = max(0, min(100, pet[6] + en))
        new_hygiene = max(0, min(100, pet[7] + hyg))
        new_coins = pet[8] + coin_gain
        new_xp = pet[9] + xp_gain
        
        # Check evolution
        stage = pet[10]
        if new_xp >= 500 and stage == 'Baby':
            stage = 'Child'
        elif new_xp >= 1500 and stage == 'Child':
            stage = 'Adult'
        
        cur.execute(
            "UPDATE pet SET hunger=?, happiness=?, energy=?, hygiene=?, coins=?, xp=?, stage=?, last_updated=? WHERE id=?",
            (new_hunger, new_happiness, new_energy, new_hygiene, new_coins, new_xp, stage, time.time(), pet[0])
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'coins_earned': coin_gain,
            'xp_earned': xp_gain,
            'new_coins': new_coins,
            'new_xp': new_xp,
            'new_stage': stage,
            'evolved': stage != pet[10]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pet/shop', methods=['GET'])
def pet_shop():
    """Get shop items"""
    try:
        items = [
            {'id': 'apple', 'name': '🍎 Apple', 'description': '+20 Hunger', 'cost': 10, 'effect': 'hunger', 'value': 20},
            {'id': 'cupcake', 'name': '🧁 Cupcake', 'description': '+40 Hunger, +10 Happiness', 'cost': 25, 'effect': 'multi', 'hunger': 40, 'happiness': 10},
            {'id': 'tophat', 'name': '🎩 Top Hat', 'description': 'Cosmetic', 'cost': 100, 'effect': 'hat', 'value': '🎩'},
            {'id': 'bow', 'name': '🎀 Bow', 'description': 'Cosmetic', 'cost': 100, 'effect': 'hat', 'value': '🎀'},
            {'id': 'crown', 'name': '👑 Crown', 'description': 'Cosmetic', 'cost': 500, 'effect': 'hat', 'value': '👑'}
        ]
        return jsonify({'items': items}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pet/buy', methods=['POST'])
def pet_buy():
    """Purchase shop item"""
    try:
        data = request.json
        item_id = data.get('item_id')
        
        # Get shop items
        items = {
            'apple': {'cost': 10, 'effect': 'hunger', 'value': 20},
            'cupcake': {'cost': 25, 'effect': 'multi', 'hunger': 40, 'happiness': 10},
            'tophat': {'cost': 100, 'effect': 'hat', 'value': '🎩'},
            'bow': {'cost': 100, 'effect': 'hat', 'value': '🎀'},
            'crown': {'cost': 500, 'effect': 'hat', 'value': '👑'}
        }
        
        if item_id not in items:
            return jsonify({'error': 'Invalid item'}), 400
        
        item = items[item_id]
        
        conn = sqlite3.connect("pet_game.db")
        cur = conn.cursor()
        pet = cur.execute("SELECT * FROM pet LIMIT 1").fetchone()
        
        if not pet:
            conn.close()
            return jsonify({'error': 'No pet found'}), 404
        
        if pet[8] < item['cost']:
            conn.close()
            return jsonify({'error': 'Not enough coins'}), 400
        
        # Apply effect
        new_coins = pet[8] - item['cost']
        new_hunger = pet[4]
        new_happiness = pet[5]
        new_hat = pet[13] if len(pet) > 13 else 'None'
        
        if item['effect'] == 'hunger':
            new_hunger = min(100, pet[4] + item['value'])
        elif item['effect'] == 'multi':
            new_hunger = min(100, pet[4] + item['hunger'])
            new_happiness = min(100, pet[5] + item['happiness'])
        elif item['effect'] == 'hat':
            new_hat = item['value']
        
        cur.execute(
            "UPDATE pet SET hunger=?, happiness=?, coins=?, hat=?, last_updated=? WHERE id=?",
            (new_hunger, new_happiness, new_coins, new_hat, time.time(), pet[0])
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'new_coins': new_coins,
            'new_hunger': new_hunger,
            'new_happiness': new_happiness,
            'new_hat': new_hat
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pet/declutter', methods=['POST'])
def pet_declutter():
    """Declutter task - throw away worries"""
    try:
        data = request.json
        worries = data.get('worries', [])
        
        if not worries or len(worries) == 0:
            return jsonify({'error': 'Please provide at least one worry'}), 400
        
        conn = sqlite3.connect("pet_game.db")
        cur = conn.cursor()
        pet = cur.execute("SELECT * FROM pet LIMIT 1").fetchone()
        
        if not pet:
            conn.close()
            return jsonify({'error': 'No pet found'}), 404
        
        # Boost hygiene and happiness
        new_hygiene = min(100, pet[7] + 40)
        new_happiness = min(100, pet[5] + 5)
        new_xp = pet[9] + 15
        new_coins = pet[8] + 5
        
        cur.execute(
            "UPDATE pet SET hygiene=?, happiness=?, xp=?, coins=?, last_updated=? WHERE id=?",
            (new_hygiene, new_happiness, new_xp, new_coins, time.time(), pet[0])
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'The room (and your mind) is clearer!',
            'coins_earned': 5,
            'new_coins': new_coins
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pet/adventure', methods=['POST'])
def pet_adventure():
    """Start adventure (30 min walk)"""
    try:
        conn = sqlite3.connect("pet_game.db")
        cur = conn.cursor()
        pet = cur.execute("SELECT * FROM pet LIMIT 1").fetchone()
        
        if not pet:
            conn.close()
            return jsonify({'error': 'No pet found'}), 404
        
        if pet[6] < 20:  # Energy check
            conn.close()
            return jsonify({'error': 'Pet is too tired for a walk!'}), 400
        
        # Set adventure end time (30 minutes from now)
        adventure_end = time.time() + (30 * 60)
        new_energy = pet[6] - 20
        
        cur.execute(
            "UPDATE pet SET energy=?, adventure_end=?, last_updated=? WHERE id=?",
            (new_energy, adventure_end, time.time(), pet[0])
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Pet is on an adventure!',
            'return_time': adventure_end
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pet/check-return', methods=['POST'])
def pet_check_return():
    """Check if pet returned from adventure and give rewards"""
    try:
        conn = sqlite3.connect("pet_game.db")
        cur = conn.cursor()
        pet = cur.execute("SELECT * FROM pet LIMIT 1").fetchone()
        
        if not pet:
            conn.close()
            return jsonify({'error': 'No pet found'}), 404
        
        adventure_end = pet[11]
        
        if adventure_end > 0 and time.time() >= adventure_end:
            # Pet returned!
            import random
            bonus_coins = random.randint(10, 50)
            
            new_coins = pet[8] + bonus_coins
            new_xp = pet[9] + 20
            
            cur.execute(
                "UPDATE pet SET coins=?, xp=?, adventure_end=0, last_updated=? WHERE id=?",
                (new_coins, new_xp, time.time(), pet[0])
            )
            conn.commit()
            conn.close()
            
            return jsonify({
                'returned': True,
                'message': f'{pet[1]} returned with {bonus_coins} coins and a cool leaf! 🍃',
                'coins_earned': bonus_coins,
                'new_coins': new_coins
            }), 200
        else:
            conn.close()
            return jsonify({'returned': False}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pet/apply-decay', methods=['POST'])
def pet_apply_decay():
    """Apply time-based stat decay"""
    try:
        conn = sqlite3.connect("pet_game.db")
        cur = conn.cursor()
        pet = cur.execute("SELECT * FROM pet LIMIT 1").fetchone()
        
        if not pet:
            conn.close()
            return jsonify({'error': 'No pet found'}), 404
        
        now = time.time()
        last_updated = pet[12]
        hours_passed = (now - last_updated) / 3600
        
        # Very gentle decay (user doesn't feel like they're neglecting pet)
        # 0.3 per hour = ~7 points per day, not overwhelming
        if hours_passed > 1.0:
            decay = int(hours_passed * 0.3)
            
            new_hunger = max(20, pet[4] - decay)
            new_energy = max(20, pet[6] - decay)
            new_hygiene = max(20, pet[7] - int(decay / 3))
            
            cur.execute(
                "UPDATE pet SET hunger=?, energy=?, hygiene=?, last_updated=? WHERE id=?",
                (new_hunger, new_energy, new_hygiene, now, pet[0])
            )
            conn.commit()
        
        conn.close()
        return jsonify({'success': True}), 200
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
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO cbt_records (username, situation, thought, evidence) VALUES (?,?,?,?)",
            (username, situation, thought, evidence or '')
        )
        conn.commit()
        record_id = cur.lastrowid
        conn.close()
        
        # AUTO-UPDATE AI MEMORY
        update_ai_memory(username)
        
        # Reward pet for CBT activity
        reward_pet('therapy', 'cbt')
        
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
        
        conn = sqlite3.connect(DB_PATH)
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
    """Submit PHQ-9 depression assessment (once per fortnight)"""
    try:
        data = request.json
        username = data.get('username')
        scores = data.get('scores')  # Array of 9 scores (0-3 each)
        
        if not username or not scores or len(scores) != 9:
            return jsonify({'error': 'Username and 9 scores required'}), 400
        
        # Check if user already submitted PHQ-9 in last 14 days
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        last_assessment = cur.execute(
            """SELECT entry_timestamp FROM clinical_scales 
               WHERE username=? AND scale_name='PHQ-9' 
               ORDER BY entry_timestamp DESC LIMIT 1""",
            (username,)
        ).fetchone()
        
        if last_assessment:
            last_date = datetime.fromisoformat(last_assessment[0])
            days_since = (datetime.now() - last_date).days
            if days_since < 14:
                conn.close()
                return jsonify({
                    'error': f'PHQ-9 can only be submitted once per fortnight. Please wait {14 - days_since} more days.'
                }), 400
        
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
        
        cur.execute(
            "INSERT INTO clinical_scales (username, scale_name, score, severity) VALUES (?,?,?,?)",
            (username, 'PHQ-9', total, severity)
        )
        
        # Get clinician for notification
        clinician = cur.execute(
            "SELECT clinician_id FROM users WHERE username=?",
            (username,)
        ).fetchone()
        
        conn.commit()
        conn.close()
        
        # Send notifications
        send_notification(
            username,
            f"PHQ-9 assessment completed. Score: {total} ({severity}). Next assessment available in 14 days.",
            'assessment'
        )
        
        if clinician and clinician[0]:
            send_notification(
                clinician[0],
                f"Patient {username} completed PHQ-9 assessment. Score: {total} ({severity}).",
                'patient_assessment'
            )
        
        # AUTO-UPDATE AI MEMORY
        update_ai_memory(username)
        
        # Reward pet for clinical assessment
        reward_pet('therapy', 'clinical')
        
        return jsonify({'success': True, 'score': total, 'severity': severity}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clinical/gad7', methods=['POST'])
def submit_gad7():
    """Submit GAD-7 anxiety assessment (once per fortnight)"""
    try:
        data = request.json
        username = data.get('username')
        scores = data.get('scores')  # Array of 7 scores (0-3 each)
        
        if not username or not scores or len(scores) != 7:
            return jsonify({'error': 'Username and 7 scores required'}), 400
        
        # Check if user already submitted GAD-7 in last 14 days
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        last_assessment = cur.execute(
            """SELECT entry_timestamp FROM clinical_scales 
               WHERE username=? AND scale_name='GAD-7' 
               ORDER BY entry_timestamp DESC LIMIT 1""",
            (username,)
        ).fetchone()
        
        if last_assessment:
            last_date = datetime.fromisoformat(last_assessment[0])
            days_since = (datetime.now() - last_date).days
            if days_since < 14:
                conn.close()
                return jsonify({
                    'error': f'GAD-7 can only be submitted once per fortnight. Please wait {14 - days_since} more days.'
                }), 400
        
        total = sum(scores)
        if total <= 4:
            severity = "Minimal"
        elif total <= 9:
            severity = "Mild"
        elif total <= 14:
            severity = "Moderate"
        else:
            severity = "Severe"
        
        cur.execute(
            "INSERT INTO clinical_scales (username, scale_name, score, severity) VALUES (?,?,?,?)",
            (username, 'GAD-7', total, severity)
        )
        
        # Get clinician for notification
        clinician = cur.execute(
            "SELECT clinician_id FROM users WHERE username=?",
            (username,)
        ).fetchone()
        
        conn.commit()
        conn.close()
        
        # Send notifications
        send_notification(
            username,
            f"GAD-7 assessment completed. Score: {total} ({severity}). Next assessment available in 14 days.",
            'assessment'
        )
        
        if clinician and clinician[0]:
            send_notification(
                clinician[0],
                f"Patient {username} completed GAD-7 assessment. Score: {total} ({severity}).",
                'patient_assessment'
            )
        
        # AUTO-UPDATE AI MEMORY
        update_ai_memory(username)
        
        # Reward pet for clinical assessment
        reward_pet('therapy', 'clinical')
        
        return jsonify({'success': True, 'score': total, 'severity': severity}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === COMMUNITY SUPPORT BOARD ===
@app.route('/api/community/posts', methods=['GET'])
def get_community_posts():
    """Get recent community posts"""
    try:
        username = request.args.get('username', '')  # Optional - to check if user liked posts
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        posts = cur.execute(
            "SELECT id, username, message, likes, entry_timestamp FROM community_posts ORDER BY entry_timestamp DESC LIMIT 20"
        ).fetchall()
        
        post_list = []
        for p in posts:
            post_id = p[0]
            # Check if current user liked this post
            liked_by_user = False
            if username:
                liked = cur.execute(
                    "SELECT 1 FROM community_likes WHERE post_id=? AND username=?",
                    (post_id, username)
                ).fetchone()
                liked_by_user = liked is not None
            
            post_list.append({
                'id': post_id,
                'username': p[1],
                'message': p[2],
                'likes': p[3] or 0,
                'timestamp': p[4],
                'liked_by_user': liked_by_user
            })
        
        conn.close()
        return jsonify({'posts': post_list}), 200
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
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO community_posts (username, message) VALUES (?,?)",
            (username, message)
        )
        conn.commit()
        conn.close()
        
        # AUTO-UPDATE AI MEMORY
        update_ai_memory(username)
        
        return jsonify({'success': True}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/community/post/<int:post_id>/like', methods=['POST'])
def like_community_post(post_id):
    """Like or unlike a community post"""
    try:
        data = request.json
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Check if already liked
        existing_like = cur.execute(
            "SELECT 1 FROM community_likes WHERE post_id=? AND username=?",
            (post_id, username)
        ).fetchone()
        
        if existing_like:
            # Unlike - remove like and decrement count
            cur.execute("DELETE FROM community_likes WHERE post_id=? AND username=?", (post_id, username))
            cur.execute("UPDATE community_posts SET likes = likes - 1 WHERE id=?", (post_id,))
        else:
            # Like - add like and increment count
            cur.execute("INSERT INTO community_likes (post_id, username) VALUES (?,?)", (post_id, username))
            cur.execute("UPDATE community_posts SET likes = likes + 1 WHERE id=?", (post_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/community/post/<int:post_id>', methods=['DELETE'])
def delete_community_post(post_id):
    """Delete a community post (only by author)"""
    try:
        data = request.json
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Verify post belongs to user
        post = cur.execute(
            "SELECT username FROM community_posts WHERE id=?",
            (post_id,)
        ).fetchone()
        
        if not post:
            conn.close()
            return jsonify({'error': 'Post not found'}), 404
        
        if post[0] != username:
            conn.close()
            return jsonify({'error': 'You can only delete your own posts'}), 403
        
        # Delete post and related data
        cur.execute("DELETE FROM community_posts WHERE id=?", (post_id,))
        cur.execute("DELETE FROM community_likes WHERE post_id=?", (post_id,))
        cur.execute("DELETE FROM community_replies WHERE post_id=?", (post_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/community/post/<int:post_id>/reply', methods=['POST'])
def create_reply(post_id):
    """Create a reply to a community post"""
    try:
        data = request.json
        username = data.get('username')
        message = data.get('message')
        
        if not username or not message:
            return jsonify({'error': 'Username and message required'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO community_replies (post_id, username, message) VALUES (?,?,?)",
            (post_id, username, message)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/community/post/<int:post_id>/replies', methods=['GET'])
def get_replies(post_id):
    """Get replies for a community post"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        replies = cur.execute(
            "SELECT username, message, timestamp FROM community_replies WHERE post_id=? ORDER BY timestamp ASC",
            (post_id,)
        ).fetchall()
        conn.close()
        
        return jsonify({'replies': [
            {
                'username': r[0],
                'message': r[1],
                'timestamp': r[2]
            } for r in replies
        ]}), 200
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
        
        conn = sqlite3.connect(DB_PATH)
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
        
        conn = sqlite3.connect(DB_PATH)
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
        
        # AUTO-UPDATE AI MEMORY
        update_ai_memory(username)
        
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
        
        conn = sqlite3.connect(DB_PATH)
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
        
        conn = sqlite3.connect(DB_PATH)
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
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Get recent mood data for trends
        moods = cur.execute(
            "SELECT mood_val, sleep_val, entrestamp FROM mood_logs WHERE username=? ORDER BY entrestamp DESC LIMIT 7",
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
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Get only APPROVED patients assigned to this clinician
        users = cur.execute(
            """SELECT u.username FROM users u
               JOIN patient_approvals pa ON u.username = pa.patient_username
               WHERE u.role='user' AND pa.clinician_username=? AND pa.status='approved'""",
            (clinician_username,)
        ).fetchall()
        
        patient_list = []
        for user in users:
            username = user[0]
            
            # Get recent mood average
            mood_avg = cur.execute(
                "SELECT AVG(mood_val) FROM mood_logs WHERE username=? AND entrestamp > datetime('now', '-7 days')",
                (username,)
            ).fetchone()[0] or 0
            
            # Get alert count (use alerts table, not safety_alerts)
            alert_count = cur.execute(
                "SELECT COUNT(*) FROM alerts WHERE username=? AND created_at > datetime('now', '-7 days')",
                (username,)
            ).fetchone()[0]
            
            # Get latest assessment
            latest_scale = cur.execute(
                "SELECT scale_name, score, severity, entry_timestamp FROM clinical_scales WHERE username=? ORDER BY entry_timestamp DESC LIMIT 1",
                (username,)
            ).fetchone()
            
            # Get last login
            last_login = cur.execute(
                "SELECT last_login FROM users WHERE username=?",
                (username,)
            ).fetchone()
            
            patient_list.append({
                'username': username,
                'avg_mood_7d': round(mood_avg, 1),
                'alert_count_7d': alert_count,
                'last_login': last_login[0] if last_login and last_login[0] else None,
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
        print(f"ERROR in get_patients: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/professional/patient/<username>', methods=['GET'])
def get_patient_detail(username):
    """Get detailed patient data including chat history, diary, habits (for professional dashboard)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Profile
        profile = cur.execute(
            "SELECT full_name, dob, conditions, email, phone FROM users WHERE username=?",
            (username,)
        ).fetchone()
        
        # Recent moods with ALL habit data
        moods = cur.execute(
            "SELECT mood_val, sleep_val, exercise_mins, outside_mins, water_pints, meds, notes, entrestamp FROM mood_logs WHERE username=? ORDER BY entrestamp DESC LIMIT 30",
            (username,)
        ).fetchall()
        
        # AI Chat history
        chat_history = cur.execute(
            "SELECT sender, message, timestamp FROM chat_history WHERE session_id=? ORDER BY timestamp DESC LIMIT 50",
            (f"{username}_session",)
        ).fetchall()
        
        # Gratitude entries
        gratitude = cur.execute(
            "SELECT entry, entry_timestamp FROM gratitude_logs WHERE username=? ORDER BY entry_timestamp DESC LIMIT 20",
            (username,)
        ).fetchall()
        
        # CBT records
        cbt_records = cur.execute(
            "SELECT situation, thought, evidence, entry_timestamp FROM cbt_records WHERE username=? ORDER BY entry_timestamp DESC LIMIT 20",
            (username,)
        ).fetchall()
        
        # Recent alerts (use alerts table with correct columns)
        alerts = cur.execute(
            "SELECT alert_type, details, created_at FROM alerts WHERE username=? ORDER BY created_at DESC LIMIT 10",
            (username,)
        ).fetchall()
        
        # Clinical scales
        scales = cur.execute(
            "SELECT scale_name, score, severity, entry_timestamp FROM clinical_scales WHERE username=? ORDER BY entry_timestamp DESC LIMIT 10",
            (username,)
        ).fetchall()
        
        # Clinician notes
        notes = cur.execute(
            "SELECT id, note_text, is_highlighted, created_at FROM clinician_notes WHERE patient_username=? ORDER BY created_at DESC LIMIT 20",
            (username,)
        ).fetchall()
        
        conn.close()
        
        return jsonify({
            'username': username,
            'profile': {
                'username': username,
                'name': profile[0] if profile else '',
                'dob': profile[1] if profile else '',
                'conditions': profile[2] if profile else '',
                'email': profile[3] if profile else '',
                'phone': profile[4] if profile else ''
            },
            'recent_moods': [
                {
                    'mood': m[0], 
                    'sleep': m[1] or 0, 
                    'exercise': m[2] or 0,
                    'outside': m[3] or 0,
                    'water': m[4] or 0,
                    'meds': m[5] or '',
                    'notes': m[6] or '', 
                    'timestamp': m[7]
                } for m in moods
            ],
            'chat_history': [
                {'sender': c[0], 'message': c[1], 'timestamp': c[2]} for c in chat_history
            ],
            'gratitude_entries': [
                {'entry': g[0], 'timestamp': g[1]} for g in gratitude
            ],
            'cbt_records': [
                {'situation': c[0], 'thought': c[1], 'evidence': c[2], 'timestamp': c[3]} for c in cbt_records
            ],
            'recent_alerts': [
                {'type': a[0], 'message': a[1], 'timestamp': a[2]} for a in alerts
            ],
            'clinical_scales': [
                {'name': s[0], 'score': s[1], 'severity': s[2], 'timestamp': s[3]} for s in scales
            ],
            'clinician_notes': [
                {'id': n[0], 'note': n[1], 'highlighted': bool(n[2]), 'timestamp': n[3]} for n in notes
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/professional/ai-summary', methods=['POST'])
def generate_ai_summary():
    """Generate AI clinical summary for a patient"""
    try:
        data = request.json
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        # Fetch patient data
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Get profile
        profile = cur.execute(
            "SELECT full_name, conditions FROM users WHERE username=?",
            (username,)
        ).fetchone()
        
        # Get recent moods (last 30 days) with ALL habit data
        moods = cur.execute(
            "SELECT mood_val, sleep_val, exercise_mins, outside_mins, water_pints, meds, notes, entrestamp FROM mood_logs WHERE username=? ORDER BY entrestamp DESC LIMIT 30",
            (username,)
        ).fetchall()
        
        # Get recent alerts (last 30 days)
        alerts = cur.execute(
            "SELECT alert_type, details, created_at FROM alerts WHERE username=? AND created_at > datetime('now', '-30 days') ORDER BY created_at DESC",
            (username,)
        ).fetchall()
        
        # Get latest assessments
        scales = cur.execute(
            "SELECT scale_name, score, severity FROM clinical_scales WHERE username=? ORDER BY entry_timestamp DESC LIMIT 5",
            (username,)
        ).fetchall()
        
        # Get recent therapy chat messages (sample themes)
        chat_messages = cur.execute(
            "SELECT message FROM chat_history WHERE session_id=? AND sender='user' ORDER BY timestamp DESC LIMIT 10",
            (f"{username}_session",)
        ).fetchall()
        
        # Get gratitude entries
        gratitude = cur.execute(
            "SELECT entry FROM gratitude_logs WHERE username=? ORDER BY entry_timestamp DESC LIMIT 5",
            (username,)
        ).fetchall()
        
        # Get CBT exercises
        cbt_records = cur.execute(
            "SELECT situation, thought, evidence FROM cbt_records WHERE username=? ORDER BY entry_timestamp DESC LIMIT 5",
            (username,)
        ).fetchall()
        
        # Get clinician notes (especially highlighted ones)
        clinician_notes = cur.execute(
            "SELECT note_text, is_highlighted FROM clinician_notes WHERE patient_username=? ORDER BY created_at DESC LIMIT 5",
            (username,)
        ).fetchall()
        
        conn.close()
        
        # Build context for AI
        patient_name = profile[0] if profile else username
        conditions = profile[1] if profile and profile[1] else "Not specified"
        
        avg_mood = sum(m[0] for m in moods) / len(moods) if moods else 0
        avg_sleep = sum(m[1] or 0 for m in moods) / len(moods) if moods else 0
        avg_exercise = sum(m[2] or 0 for m in moods) / len(moods) if moods else 0
        avg_outside = sum(m[3] or 0 for m in moods) / len(moods) if moods else 0
        avg_water = sum(m[4] or 0 for m in moods) / len(moods) if moods else 0
        
        # Mood trend (recent vs older)
        if len(moods) >= 6:
            recent_mood = sum(m[0] for m in moods[:3]) / 3
            older_mood = sum(m[0] for m in moods[-3:]) / 3
            mood_trend = "improving" if recent_mood > older_mood else "declining" if recent_mood < older_mood else "stable"
        else:
            mood_trend = "insufficient data"
        
        alert_count = len(alerts)
        gratitude_count = len(gratitude)
        cbt_count = len(cbt_records)
        
        # Build prompt with comprehensive data
        prompt = f"""You are a clinical psychologist reviewing patient data. Generate a concise professional clinical summary (3-4 paragraphs).

Patient: {patient_name}
Known Conditions: {conditions}

Data Summary (Last 30 Days):
- Average Mood: {avg_mood:.1f}/10 (Trend: {mood_trend})
- Average Sleep: {avg_sleep:.1f} hours
- Average Exercise: {avg_exercise:.1f} minutes
- Average Outdoor Time: {avg_outside:.1f} minutes
- Average Water Intake: {avg_water:.1f} pints
- Safety Alerts: {alert_count}
- Gratitude Entries: {gratitude_count}
- CBT Exercises Completed: {cbt_count}

Latest Assessments:
{chr(10).join([f"- {s[0]}: {s[1]} ({s[2]})" for s in scales]) if scales else "No assessments completed"}

Recent Therapy Chat Themes (user concerns):
{chr(10).join([f"- {msg[0][:100]}" for msg in chat_messages[:5]]) if chat_messages else "No recent therapy sessions"}

Gratitude Practice:
{chr(10).join([f"- {g[0][:80]}" for g in gratitude[:3]]) if gratitude else "No gratitude entries"}

CBT Work:
{chr(10).join([f"- Situation: {c[0][:60]}..." for c in cbt_records[:3]]) if cbt_records else "No CBT exercises"}

Clinician Notes:
{chr(10).join([f"- {'[KEY] ' if n[1] else ''}{n[0][:100]}" for n in clinician_notes]) if clinician_notes else "No clinician notes yet"}

Recent Alerts:
{chr(10).join([f"- {a[0]}: {a[1]}" for a in alerts[:3]]) if alerts else "No recent alerts"}

Please provide:
1. Overall clinical impression considering all data sources
2. Key concerns or risk factors
3. Notable trends in mood, habits, and engagement
4. Recommended clinical actions or interventions
5. Progress in self-help activities (gratitude, CBT)

Keep it professional and evidence-based."""

        # Call AI API
        if GROQ_API_KEY and API_URL:
            try:
                response = requests.post(
                    API_URL,
                    headers={
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 800
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    ai_response = response.json()
                    summary = ai_response['choices'][0]['message']['content']
                    
                    return jsonify({
                        'success': True,
                        'summary': summary
                    }), 200
                else:
                    # Fallback to basic summary
                    pass
            except Exception as e:
                print(f"AI summary error: {e}")
                # Fallback to basic summary
                pass
        
        # Fallback: Basic summary
        summary = f"""CLINICAL SUMMARY - {patient_name}

OVERVIEW:
Patient has recorded {len(moods)} mood entries over the last 30 days with an average mood rating of {avg_mood:.1f}/10. Mood trend appears {mood_trend}. {"⚠️ ALERT: " + str(alert_count) + " safety alerts have been triggered." if alert_count > 0 else "No safety alerts recorded."}

CURRENT STATUS:
{"Latest assessment: " + scales[0][0] + " - " + scales[0][2] + " severity (Score: " + str(scales[0][1]) + ")" if scales else "No formal assessments completed."}
Sleep average: {avg_sleep:.1f} hours per night
Exercise average: {avg_exercise:.0f} minutes per day

CLINICAL NOTES:
{"⚠️ REQUIRES IMMEDIATE ATTENTION - Multiple safety alerts indicate elevated risk." if alert_count > 3 else "Patient appears stable based on available data." if alert_count == 0 else "Monitor for concerning patterns."}
{"Engagement with therapy is " + ("excellent" if therapy_sessions > 20 else "moderate" if therapy_sessions > 5 else "limited") + f" ({therapy_sessions} interactions recorded)." if therapy_sessions else "Patient has not engaged with therapy features yet."}

RECOMMENDATIONS:
{"URGENT: Schedule immediate clinical assessment due to safety concerns." if alert_count > 3 else "Continue monitoring mood patterns and sleep quality." if avg_mood < 5 else "Maintain current treatment plan."} Consider formal assessment if not completed recently."""

        return jsonify({
            'success': True,
            'summary': summary,
            'fallback': True
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== CLINICIAN NOTES & PDF EXPORT =====
@app.route('/api/professional/notes', methods=['POST'])
def create_clinician_note():
    """Create a note about a patient - automatically updates AI memory"""
    try:
        data = request.json
        clinician_username = data.get('clinician_username')
        patient_username = data.get('patient_username')
        note_text = data.get('note_text')
        is_highlighted = data.get('is_highlighted', False)
        
        if not clinician_username or not patient_username or not note_text:
            return jsonify({'error': 'Clinician, patient, and note text required'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO clinician_notes (clinician_username, patient_username, note_text, is_highlighted) VALUES (?,?,?,?)",
            (clinician_username, patient_username, note_text, 1 if is_highlighted else 0)
        )
        note_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        # AUTO-UPDATE AI MEMORY when clinician adds note
        update_ai_memory(patient_username)
        
        log_event(clinician_username, 'api', 'clinician_note_created', f'Note for {patient_username}, AI memory updated')
        
        return jsonify({'success': True, 'note_id': note_id, 'message': 'Note saved and AI memory updated'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/professional/notes/<patient_username>', methods=['GET'])
def get_clinician_notes(patient_username):
    """Get all notes for a patient"""
    try:
        clinician_username = request.args.get('clinician')
        
        if not clinician_username:
            return jsonify({'error': 'Clinician username required'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        notes = cur.execute(
            "SELECT id, note_text, is_highlighted, created_at FROM clinician_notes WHERE clinician_username=? AND patient_username=? ORDER BY created_at DESC",
            (clinician_username, patient_username)
        ).fetchall()
        conn.close()
        
        return jsonify({'notes': [
            {
                'id': n[0],
                'text': n[1],
                'highlighted': bool(n[2]),
                'timestamp': n[3]
            } for n in notes
        ]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/professional/notes/<int:note_id>', methods=['DELETE'])
def delete_clinician_note(note_id):
    """Delete a clinician note"""
    try:
        data = request.json
        clinician_username = data.get('clinician_username')
        
        if not clinician_username:
            return jsonify({'error': 'Clinician username required'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Verify note belongs to clinician
        note = cur.execute(
            "SELECT clinician_username FROM clinician_notes WHERE id=?",
            (note_id,)
        ).fetchone()
        
        if not note:
            conn.close()
            return jsonify({'error': 'Note not found'}), 404
        
        if note[0] != clinician_username:
            conn.close()
            return jsonify({'error': 'Unauthorized'}), 403
        
        cur.execute("DELETE FROM clinician_notes WHERE id=?", (note_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/professional/export-summary', methods=['POST'])
def export_patient_summary():
    """Generate HTML summary for patient with custom date range (for PDF conversion)"""
    try:
        data = request.json
        clinician_username = data.get('clinician_username')
        patient_username = data.get('patient_username')
        start_date = data.get('start_date')  # Optional YYYY-MM-DD
        end_date = data.get('end_date')  # Optional YYYY-MM-DD
        
        if not clinician_username or not patient_username:
            return jsonify({'error': 'Clinician and patient usernames required'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Get patient profile
        profile = cur.execute(
            "SELECT full_name, dob, conditions FROM users WHERE username=?",
            (patient_username,)
        ).fetchone()
        
        # Build date filters
        mood_filter = ""
        mood_params = [patient_username]
        if start_date:
            mood_filter += " AND entrestamp >= ?"
            mood_params.append(start_date)
        if end_date:
            mood_filter += " AND entrestamp <= ?"
            mood_params.append(end_date)
        
        # Get moods
        moods = cur.execute(
            f"SELECT mood_val, sleep_val, exercise_mins, notes, entrestamp FROM mood_logs WHERE username=?{mood_filter} ORDER BY entrestamp DESC",
            tuple(mood_params)
        ).fetchall()
        
        # Get assessments
        assess_params = [patient_username]
        assess_filter = ""
        if start_date:
            assess_filter += " AND entry_timestamp >= ?"
            assess_params.append(start_date)
        if end_date:
            assess_filter += " AND entry_timestamp <= ?"
            assess_params.append(end_date)
        
        assessments = cur.execute(
            f"SELECT scale_name, score, severity, entry_timestamp FROM clinical_scales WHERE username=?{assess_filter} ORDER BY entry_timestamp DESC",
            tuple(assess_params)
        ).fetchall()
        
        # Get clinician notes
        notes = cur.execute(
            "SELECT note_text, is_highlighted, created_at FROM clinician_notes WHERE clinician_username=? AND patient_username=? ORDER BY created_at DESC",
            (clinician_username, patient_username)
        ).fetchall()
        
        # Get alerts
        alert_params = [patient_username]
        alert_filter = ""
        if start_date:
            alert_filter += " AND created_at >= ?"
            alert_params.append(start_date)
        if end_date:
            alert_filter += " AND created_at <= ?"
            alert_params.append(end_date)
        
        alerts = cur.execute(
            f"SELECT alert_type, details, created_at FROM alerts WHERE username=?{alert_filter} ORDER BY created_at DESC",
            tuple(alert_params)
        ).fetchall()
        
        conn.close()
        
        # Calculate stats
        period_text = "All Time"
        if start_date and end_date:
            period_text = f"{start_date} to {end_date}"
        elif start_date:
            period_text = f"From {start_date}"
        elif end_date:
            period_text = f"Until {end_date}"
        
        avg_mood = sum(m[0] for m in moods) / len(moods) if moods else 0
        avg_sleep = sum(m[1] or 0 for m in moods) / len(moods) if moods else 0
        
        # Build HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        h2 {{ color: #333; margin-top: 30px; border-bottom: 2px solid #e0e0e0; padding-bottom: 5px; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 30px; }}
        .stats {{ display: flex; gap: 30px; margin: 20px 0; }}
        .stat {{ text-align: center; }}
        .stat-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
        .stat-value {{ font-size: 28px; font-weight: bold; color: #667eea; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th {{ background: #667eea; color: white; padding: 10px; text-align: left; }}
        td {{ padding: 8px; border-bottom: 1px solid #e0e0e0; }}
        .highlight {{ background: #fff3cd; padding: 12px; border-left: 4px solid #ffc107; margin: 10px 0; }}
        .note {{ background: #f8f9fa; padding: 12px; border-radius: 6px; margin: 10px 0; }}
        .alert {{ background: #ffebee; padding: 12px; border-left: 4px solid #e74c3c; margin: 10px 0; }}
    </style>
</head>
<body>
    <h1>Clinical Summary: {patient_username}</h1>
    
    <div class="header">
        <p><strong>Patient:</strong> {profile[0] if profile and profile[0] else patient_username}</p>
        <p><strong>Conditions:</strong> {profile[2] if profile and profile[2] else 'Not specified'}</p>
        <p><strong>Report Period:</strong> {period_text}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Clinician:</strong> Dr. {clinician_username}</p>
    </div>
    
    <h2>Summary Statistics</h2>
    <div class="stats">
        <div class="stat">
            <div class="stat-value">{avg_mood:.1f}/10</div>
            <div class="stat-label">Average Mood</div>
        </div>
        <div class="stat">
            <div class="stat-value">{avg_sleep:.1f}h</div>
            <div class="stat-label">Average Sleep</div>
        </div>
        <div class="stat">
            <div class="stat-value">{len(moods)}</div>
            <div class="stat-label">Mood Entries</div>
        </div>
        <div class="stat">
            <div class="stat-value">{len(alerts)}</div>
            <div class="stat-label">Safety Alerts</div>
        </div>
    </div>
    
    <h2>Clinician Notes</h2>
    {''.join([f'<div class="{"highlight" if n[1] else "note"}"><strong>{n[2][:10]}</strong><br>{n[0]}</div>' for n in notes]) if notes else '<p>No clinical notes recorded</p>'}
    
    <h2>Assessment Results</h2>
    {'<table><tr><th>Assessment</th><th>Score</th><th>Severity</th><th>Date</th></tr>' + ''.join([f'<tr><td>{a[0]}</td><td>{a[1]}</td><td>{a[2]}</td><td>{a[3][:10]}</td></tr>' for a in assessments]) + '</table>' if assessments else '<p>No assessments completed in this period</p>'}
    
    <h2>Safety Alerts</h2>
    {''.join([f'<div class="alert"><strong>{a[0]}:</strong> {a[1]}<br><small>{a[2][:19]}</small></div>' for a in alerts]) if alerts else '<p style="color: #28a745;">✓ No safety alerts in this period</p>'}
    
    <h2>Mood History (Last 30 Entries)</h2>
    {'<table><tr><th>Date</th><th>Mood</th><th>Sleep</th><th>Exercise</th><th>Notes</th></tr>' + ''.join([f'<tr><td>{m[4][:10]}</td><td>{m[0]}/10</td><td>{m[1] or 0}h</td><td>{m[2] or 0}min</td><td style="max-width:200px;">{(m[3] or "-")[:50]}</td></tr>' for m in moods[:30]]) + '</table>' if moods else '<p>No mood entries in this period</p>'}
    
    <hr style="margin-top: 40px;">
    <p style="text-align: center; color: #999; font-size: 11px;">Confidential - Generated by Healing Space Therapy App for {clinician_username}</p>
</body>
</html>"""
        
        return jsonify({
            'success': True,
            'html': html,
            'period': period_text,
            'stats': {
                'avg_mood': round(avg_mood, 1),
                'avg_sleep': round(avg_sleep, 1),
                'total_entries': len(moods),
                'alert_count': len(alerts),
                'assessment_count': len(assessments)
            }
        }), 200
        
    except Exception as e:
        print(f"Export summary error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ===== ADMIN / TESTING ENDPOINTS =====
@app.route('/api/admin/reset-users', methods=['POST'])
def reset_all_users():
    """DANGER: Delete all users, approvals, and notifications (for testing only)"""
    try:
        data = request.json
        confirm = data.get('confirm')
        
        # Require explicit confirmation
        if confirm != 'DELETE_ALL_USERS':
            return jsonify({'error': 'Must provide confirm="DELETE_ALL_USERS" to proceed'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Delete all users and related data
        cur.execute("DELETE FROM users")
        cur.execute("DELETE FROM patient_approvals")
        cur.execute("DELETE FROM notifications")
        cur.execute("DELETE FROM sessions")
        cur.execute("DELETE FROM chat_history")
        cur.execute("DELETE FROM mood_logs")
        cur.execute("DELETE FROM gratitude_logs")
        cur.execute("DELETE FROM cbt_records")
        cur.execute("DELETE FROM clinical_scales")
        cur.execute("DELETE FROM safety_plans")
        cur.execute("DELETE FROM ai_memory")
        cur.execute("DELETE FROM community_posts")
        cur.execute("DELETE FROM alerts")
        
        conn.commit()
        
        # Get counts to verify
        user_count = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        approval_count = cur.execute("SELECT COUNT(*) FROM patient_approvals").fetchone()[0]
        
        conn.close()
        
        log_event('admin', 'api', 'database_reset', 'All users and data deleted for testing')
        
        return jsonify({
            'success': True,
            'message': 'All users and related data deleted',
            'users_remaining': user_count,
            'approvals_remaining': approval_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === DAILY MOOD REMINDER ===
@app.route('/api/mood/check-reminder', methods=['POST'])
def check_mood_reminder():
    """Check if user logged mood today and send reminder notification if not (called at 8pm)"""
    try:
        from datetime import datetime
        
        # Get current time
        now = datetime.now()
        current_hour = now.hour
        
        # Only run at 8pm (20:00) or if forced for testing
        force = request.json.get('force', False) if request.json else False
        
        if not force and current_hour != 20:
            return jsonify({'message': 'Not 8pm yet, reminders not sent'}), 200
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Get all active patients
        users = cur.execute(
            "SELECT username FROM users WHERE role='user'"
        ).fetchall()
        
        reminders_sent = 0
        
        for user in users:
            username = user[0]
            
            # Check if user logged mood today
            logged_today = cur.execute(
                """SELECT id FROM mood_logs 
                   WHERE username=? AND date(entrestamp) = date('now', 'localtime')""",
                (username,)
            ).fetchone()
            
            if not logged_today:
                # Send reminder notification
                cur.execute(
                    "INSERT INTO notifications (recipient_username, message, notification_type) VALUES (?,?,?)",
                    (username, "🕗 Reminder: Don't forget to log your mood and habits for today!", 'mood_reminder')
                )
                reminders_sent += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'reminders_sent': reminders_sent,
            'message': f'Sent {reminders_sent} mood reminders'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mood/check-today', methods=['GET'])
def check_mood_today():
    """Check if user has logged mood today"""
    try:
        username = request.args.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        logged_today = cur.execute(
            """SELECT id, entrestamp FROM mood_logs 
               WHERE username=? AND date(entrestamp) = date('now', 'localtime')""",
            (username,)
        ).fetchone()
        
        conn.close()
        
        return jsonify({
            'logged_today': logged_today is not None,
            'timestamp': logged_today[1] if logged_today else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === TRAINING DATA MANAGEMENT (GDPR-COMPLIANT) ===
from training_data_manager import TrainingDataManager

training_manager = TrainingDataManager(DB_PATH)

@app.route('/api/training/consent', methods=['POST'])
def set_training_consent():
    """Allow user to opt-in/opt-out of training data collection"""
    try:
        data = request.json
        username = data.get('username')
        consent = data.get('consent', True)
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        success = training_manager.set_user_consent(username, consent)
        
        message = (
            "Thank you for contributing to mental health AI research! "
            "Your anonymized data will help improve therapy support for others."
            if consent else
            "Your consent has been withdrawn. No training data will be collected."
        )
        
        return jsonify({
            'success': success,
            'message': message
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/training/consent/status', methods=['GET'])
def get_training_consent_status():
    """Check user's training data consent status"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        has_consent = training_manager.check_user_consent(username)
        
        return jsonify({
            'consented': has_consent
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/training/export', methods=['POST'])
def export_training_data():
    """Export user's anonymized data to training database (if consented)"""
    try:
        data = request.json
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        # Check consent
        if not training_manager.check_user_consent(username):
            return jsonify({
                'error': 'User has not consented to training data usage'
            }), 403
        
        # Export all data types
        results = {}
        
        # Chat sessions
        success, msg = training_manager.export_chat_session(username)
        results['chats'] = {'success': success, 'message': msg}
        
        # Therapy patterns (CBT, gratitude)
        success, msg = training_manager.export_therapy_patterns(username)
        results['patterns'] = {'success': success, 'message': msg}
        
        # Treatment outcomes
        success, msg = training_manager.export_outcome_data(username)
        results['outcomes'] = {'success': success, 'message': msg}
        
        return jsonify({
            'success': True,
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/training/delete', methods=['POST'])
def delete_training_data():
    """GDPR Right to Deletion - Remove user's training data"""
    try:
        data = request.json
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        success = training_manager.delete_user_training_data(username)
        
        return jsonify({
            'success': success,
            'message': 'All your training data has been permanently deleted'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/training/stats', methods=['GET'])
def get_training_stats():
    """Get training database statistics (admin only)"""
    try:
        stats = training_manager.get_training_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
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
