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
                       full_name TEXT, dob TEXT, conditions TEXT, role TEXT DEFAULT 'user')''')
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
        
        if not username or not password or not pin:
            return jsonify({'error': 'Username, password, and PIN required'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        
        # Check if user exists
        if cur.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone():
            conn.close()
            return jsonify({'error': 'Username already exists'}), 409
        
        # Hash credentials
        hashed_password = hash_password(password)
        hashed_pin = hash_pin(pin)
        
        # Create user
        cur.execute("INSERT INTO users (username, password, pin, last_login) VALUES (?,?,?,?)",
                   (username, hashed_password, hashed_pin, datetime.now()))
        conn.commit()
        conn.close()
        
        log_event(username, 'api', 'user_registered', 'Registration via API')
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'username': username
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        user = cur.execute("SELECT username, password FROM users WHERE username=?", (username,)).fetchone()
        conn.close()
        
        if not user or not verify_password(user[1], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        log_event(username, 'api', 'user_login', 'Login via API')
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'username': username
        }), 200
        
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
    """Log mood entry"""
    try:
        data = request.json
        username = data.get('username')
        mood_val = data.get('mood_val')
        sleep_val = data.get('sleep_val', 0)
        meds = data.get('meds', '')
        notes = data.get('notes', '')
        
        if not username or mood_val is None:
            return jsonify({'error': 'Username and mood_val required'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO mood_logs (username, mood_val, sleep_val, meds, notes, sentiment) VALUES (?,?,?,?,?,?)",
            (username, mood_val, sleep_val, meds, notes, 'Neutral')
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
    """Get mood history for user"""
    try:
        username = request.args.get('username')
        limit = request.args.get('limit', 30)
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        logs = cur.execute(
            "SELECT id, mood_val, sleep_val, meds, notes, entry_timestamp FROM mood_logs WHERE username=? ORDER BY entry_timestamp DESC LIMIT ?",
            (username, limit)
        ).fetchall()
        conn.close()
        
        result = [{
            'id': log[0],
            'mood_val': log[1],
            'sleep_val': log[2],
            'meds': log[3],
            'notes': log[4],
            'timestamp': log[5]
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

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=DEBUG)
