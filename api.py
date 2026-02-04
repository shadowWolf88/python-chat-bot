from flask import Flask, request, jsonify, render_template, send_from_directory, make_response, Response, g, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import psycopg2
from psycopg2.extras import RealDictCursor, execute_batch
import os
import json
import hashlib
import socket
import requests
from datetime import datetime, timedelta
import sys
import secrets
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Pet Table Ensurer ---
def ensure_pet_table():
    """Ensure the pet table exists in PostgreSQL with username support"""
    conn = get_pet_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'pet'
            )
        """)
        
        if not cur.fetchone()[0]:
            # Create new table with username column for multi-user support
            cur.execute("""
                CREATE TABLE IF NOT EXISTS pet (
                    id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    name TEXT, species TEXT, gender TEXT,
                    hunger INTEGER DEFAULT 70, happiness INTEGER DEFAULT 70,
                    energy INTEGER DEFAULT 70, hygiene INTEGER DEFAULT 80,
                    coins INTEGER DEFAULT 0, xp INTEGER DEFAULT 0,
                    stage TEXT DEFAULT 'Baby', adventure_end REAL DEFAULT 0,
                    last_updated REAL, hat TEXT DEFAULT 'None'
                )
            """)
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error ensuring pet table: {e}")
        conn.rollback()
    finally:
        conn.close()

def get_pet_db_connection():
    """Get pet database connection to PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            port=os.environ.get('DB_PORT', '5432'),
            database=os.environ.get('DB_NAME_PET', 'healing_space_pet_test'),
            user=os.environ.get('DB_USER', 'healing_space'),
            password=os.environ.get('DB_PASSWORD', 'healing_space_dev_pass')
        )
        return conn
    except psycopg2.Error as e:
        print(f"Failed to connect to PostgreSQL pet database: {e}")
        raise

def normalize_pet_row(pet_row):
    """Convert pet row values to proper types"""
    if not pet_row:
        return None
    # pet schema: id, username, name, species, gender, hunger, happiness, energy, hygiene, coins, xp, stage, adventure_end, last_updated, hat
    return (
        int(pet_row[0]),      # id
        pet_row[1],           # username (text)
        pet_row[2],           # name (text)
        pet_row[3],           # species (text)
        pet_row[4],           # gender (text)
        int(pet_row[5]),      # hunger (int)
        int(pet_row[6]),      # happiness (int)
        int(pet_row[7]),      # energy (int)
        int(pet_row[8]),      # hygiene (int)
        int(pet_row[9]),      # coins (int)
        int(pet_row[10]),     # xp (int)
        pet_row[11],          # stage (text)
        float(pet_row[12]) if pet_row[12] else 0.0,  # adventure_end (real)
        float(pet_row[13]) if pet_row[13] else time.time(),  # last_updated (real)
        pet_row[14]           # hat (text)
    )

# Import existing modules (avoid importing main.py which has tkinter)
from secrets_manager import SecretsManager
from audit import log_event
import fhir_export
from training_data_manager import TRAINING_DB_PATH

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

# Configure Flask session support for secure authentication (Phase 1A)
# CRITICAL: SECRET_KEY must be persistent across app restarts
# If not set in environment, log warning and use a deterministic fallback
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    print("⚠️  WARNING: SECRET_KEY not set in environment. Sessions will NOT persist across restarts.")
    print("           Set SECRET_KEY in Railway environment variables for production.")
    # Use machine-based deterministic key (better than random for stability)
    # This ensures consistent key during single session but warns on restart
    import socket
    import hashlib
    hostname = socket.gethostname()
    SECRET_KEY = hashlib.sha256(hostname.encode()).hexdigest()[:32]

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_COOKIE_SECURE'] = not os.getenv('DEBUG', '').lower() in ('1', 'true', 'yes')  # HTTPS in production
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)  # 2-hour timeout

# Initialize rate limiter (Phase 1D)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

# Initialize with same settings as main app
DEBUG = os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes')

# ================== PHASE 2A: INPUT VALIDATION ==================

class InputValidator:
    """Phase 2A: Centralized input validation to prevent injection attacks"""
    
    # Maximum field lengths
    MAX_MESSAGE_LENGTH = 10000
    MAX_NOTE_LENGTH = 50000
    MAX_TITLE_LENGTH = 500
    MAX_USERNAME_LENGTH = 100
    MAX_EMAIL_LENGTH = 255
    
    # Minimum field lengths
    MIN_MESSAGE_LENGTH = 1
    MIN_PASSWORD_LENGTH = 8
    MIN_USERNAME_LENGTH = 3
    
    @staticmethod
    def validate_text(text, max_length=1000, min_length=1, field_name='text'):
        """Validate text field"""
        if text is None:
            return None, f"{field_name} cannot be None"
        
        text = str(text).strip()
        
        if len(text) < min_length:
            return None, f"{field_name} must be at least {min_length} character(s)"
        
        if len(text) > max_length:
            return None, f"{field_name} cannot exceed {max_length} characters (got {len(text)})"
        
        return text, None
    
    @staticmethod
    def validate_message(message):
        """Validate user message for therapy chat"""
        if not message or not isinstance(message, str):
            return None, "Message is required and must be a string"
        return InputValidator.validate_text(
            message,
            max_length=InputValidator.MAX_MESSAGE_LENGTH,
            min_length=InputValidator.MIN_MESSAGE_LENGTH,
            field_name="Message"
        )
    
    @staticmethod
    def validate_note(note_text):
        """Validate clinician note"""
        if not note_text or not isinstance(note_text, str):
            return None, "Note text is required and must be a string"
        return InputValidator.validate_text(
            note_text,
            max_length=InputValidator.MAX_NOTE_LENGTH,
            min_length=InputValidator.MIN_MESSAGE_LENGTH,
            field_name="Note"
        )
    
    @staticmethod
    def validate_integer(value, min_val=None, max_val=None, field_name='value'):
        """Validate integer field with optional range check"""
        try:
            val = int(value)
            
            if min_val is not None and val < min_val:
                return None, f"{field_name} must be at least {min_val}"
            
            if max_val is not None and val > max_val:
                return None, f"{field_name} cannot exceed {max_val}"
            
            return val, None
        except (ValueError, TypeError):
            return None, f"{field_name} must be an integer"
    
    @staticmethod
    def validate_mood(mood_value):
        """Validate mood rating (1-10)"""
        return InputValidator.validate_integer(
            mood_value,
            min_val=1,
            max_val=10,
            field_name="Mood rating"
        )
    
    @staticmethod
    def validate_sleep(sleep_value):
        """Validate sleep rating (0-10)"""
        return InputValidator.validate_integer(
            sleep_value,
            min_val=0,
            max_val=10,
            field_name="Sleep rating"
        )
    
    @staticmethod
    def validate_anxiety(anxiety_value):
        """Validate anxiety/stress rating (0-10)"""
        return InputValidator.validate_integer(
            anxiety_value,
            min_val=0,
            max_val=10,
            field_name="Anxiety rating"
        )
    
    @staticmethod
    def validate_title(title):
        """Validate title field"""
        if not title or not isinstance(title, str):
            return None, "Title is required and must be a string"
        return InputValidator.validate_text(
            title,
            max_length=InputValidator.MAX_TITLE_LENGTH,
            min_length=1,
            field_name="Title"
        )
    
    @staticmethod
    def validate_username(username):
        """Validate username field"""
        if not username or not isinstance(username, str):
            return None, "Username is required and must be a string"
        return InputValidator.validate_text(
            username,
            max_length=InputValidator.MAX_USERNAME_LENGTH,
            min_length=InputValidator.MIN_USERNAME_LENGTH,
            field_name="Username"
        )

# ================== PHASE 2B: CSRF PROTECTION ==================

class CSRFProtection:
    """Phase 2B: Prevent Cross-Site Request Forgery attacks"""
    
    @staticmethod
    def generate_csrf_token(username):
        """Generate a CSRF token for the user and store in session"""
        token = secrets.token_urlsafe(32)
        session[f'csrf_token_{username}'] = {
            'token': token,
            'created_at': datetime.utcnow().isoformat(),
            'attempts': 0
        }
        session.permanent = True
        return token
    
    @staticmethod
    def validate_csrf_token(username, provided_token):
        """Validate CSRF token from request header"""
        if not username or not provided_token:
            return False, "CSRF token missing"
        
        token_data = session.get(f'csrf_token_{username}')
        if not token_data:
            return False, "No CSRF token in session (try logging in again)"
        
        stored_token = token_data.get('token')
        
        # Prevent token reuse by tracking attempts
        token_data['attempts'] = token_data.get('attempts', 0) + 1
        if token_data['attempts'] > 10:
            session.pop(f'csrf_token_{username}', None)
            return False, "CSRF token validation failed too many times (suspicious activity)"
        
        # Timing-safe comparison
        if not secrets.compare_digest(stored_token, provided_token):
            return False, "CSRF token invalid"
        
        # Invalidate token after successful validation (one-time use)
        session.pop(f'csrf_token_{username}', None)
        
        return True, "CSRF token valid"
    
    @staticmethod
    def require_csrf(f):
        """Decorator to require CSRF token for POST/PUT/DELETE requests"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip CSRF for GET requests
            if request.method == 'GET':
                return f(*args, **kwargs)
            
            # Get authenticated user
            username = get_authenticated_username()
            if not username:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Get CSRF token from header
            csrf_token = request.headers.get('X-CSRF-Token')
            
            # In DEBUG mode, allow missing CSRF for testing (with warning)
            if DEBUG and not csrf_token:
                print(f"WARNING: Missing CSRF token in DEBUG mode (user: {username})")
                return f(*args, **kwargs)
            
            # Validate CSRF token
            is_valid, message = CSRFProtection.validate_csrf_token(username, csrf_token)
            if not is_valid:
                log_event(username, 'security', 'csrf_validation_failed', message)
                return jsonify({'error': message}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function

# ================== CBT: GOAL SETTING/TRACKING ENDPOINTS ==================

def get_last_insert_id(cursor):
    """
    Get the ID of the last inserted row in PostgreSQL.
    Use after an INSERT ... RETURNING id statement.
    """
    try:
        row = cursor.fetchone()
        return row[0] if row else None
    except Exception:
        return None

@app.route('/api/cbt/goals', methods=['POST'])
def create_goal():
    """Create a new goal entry"""
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        required = ['goal_title']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        goal_title = data['goal_title']
        goal_description = data.get('goal_description')
        goal_type = data.get('goal_type')
        target_date = data.get('target_date')
        related_value_id = data.get('related_value_id')
        status = data.get('status', 'active')
        progress_percentage = data.get('progress_percentage', 0)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO goals (username, goal_title, goal_description, goal_type, target_date, related_value_id, status, progress_percentage) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (username, goal_title, goal_description, goal_type, target_date, related_value_id, status, progress_percentage))
        conn.commit()
        log_event(username, 'cbt', 'goal_created', f"Goal: {goal_title}")
        conn.close()
        return jsonify({'success': True, 'message': 'Goal entry created'}), 201
    except Exception as e:
        return handle_exception(e, 'create_goal')

@app.route('/api/cbt/goals', methods=['GET'])
def list_goals():
    """List all goal entries for the authenticated user"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT * FROM goals WHERE username=? ORDER BY entry_timestamp DESC', (username,)).fetchall()
        conn.close()
        result = [dict(zip([c[0] for c in cur.description], row)) for row in rows]
        return jsonify({'entries': result}), 200
    except Exception as e:
        return handle_exception(e, 'list_goals')

@app.route('/api/cbt/goals/<int:entry_id>', methods=['GET'])
def get_goal(entry_id):
    """Get a single goal entry by ID"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM goals WHERE id=? AND username=?', (entry_id, username)).fetchone()
        conn.close()
        if not row:
            return jsonify({'error': 'Entry not found'}), 404
        result = dict(zip([c[0] for c in cur.description], row))
        return jsonify(result), 200
    except Exception as e:
        return handle_exception(e, 'get_goal')

@app.route('/api/cbt/goals/<int:entry_id>', methods=['PUT'])
def update_goal(entry_id):
    """Update a goal entry"""
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM goals WHERE id=? AND username=?', (entry_id, username)).fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Entry not found'}), 404
        fields = ['goal_title', 'goal_description', 'goal_type', 'target_date', 'related_value_id', 'status', 'progress_percentage']
        updates = {k: data[k] for k in fields if k in data}
        set_clause = ', '.join([f"{k}=?" for k in updates.keys()])
        values = list(updates.values()) + [entry_id, username]
        cur.execute(f'UPDATE goals SET {set_clause} WHERE id=? AND username=?', values)
        conn.commit()
        log_event(username, 'cbt', 'goal_updated', f"ID: {entry_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Entry updated'}), 200
    except Exception as e:
        return handle_exception(e, 'update_goal')

@app.route('/api/cbt/goals/<int:entry_id>', methods=['DELETE'])
def delete_goal(entry_id):
    """Delete a goal entry"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM goals WHERE id=? AND username=?', (entry_id, username)).fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Entry not found'}), 404
        cur.execute('DELETE FROM goals WHERE id=? AND username=?', (entry_id, username))
        conn.commit()
        log_event(username, 'cbt', 'goal_deleted', f"ID: {entry_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Entry deleted'}), 200
    except Exception as e:
        return handle_exception(e, 'delete_goal')

# Milestones CRUD
@app.route('/api/cbt/goals/<int:goal_id>/milestone', methods=['POST'])
def create_goal_milestone(goal_id):
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        milestone_title = data.get('milestone_title')
        milestone_description = data.get('milestone_description')
        target_date = data.get('target_date')
        is_completed = int(data.get('is_completed', 0))
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO goal_milestones (goal_id, username, milestone_title, milestone_description, target_date, is_completed) VALUES (?, ?, ?, ?, ?, ?)''',
            (goal_id, username, milestone_title, milestone_description, target_date, is_completed))
        conn.commit()
        log_event(username, 'cbt', 'goal_milestone_created', f"Goal ID: {goal_id}, Title: {milestone_title}")
        conn.close()
        return jsonify({'success': True, 'message': 'Milestone entry created'}), 201
    except Exception as e:
        return handle_exception(e, 'create_goal_milestone')

@app.route('/api/cbt/goals/<int:goal_id>/milestone', methods=['GET'])
def list_goal_milestones(goal_id):
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT * FROM goal_milestones WHERE goal_id=? AND username=? ORDER BY entry_timestamp DESC', (goal_id, username)).fetchall()
        conn.close()
        result = [dict(zip([c[0] for c in cur.description], row)) for row in rows]
        return jsonify({'entries': result}), 200
    except Exception as e:
        return handle_exception(e, 'list_goal_milestones')

# Check-ins CRUD
@app.route('/api/cbt/goals/<int:goal_id>/checkin', methods=['POST'])
def create_goal_checkin(goal_id):
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        progress_notes = data.get('progress_notes')
        obstacles = data.get('obstacles')
        next_steps = data.get('next_steps')
        motivation_level = data.get('motivation_level')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO goal_checkins (goal_id, username, progress_notes, obstacles, next_steps, motivation_level) VALUES (?, ?, ?, ?, ?, ?)''',
            (goal_id, username, progress_notes, obstacles, next_steps, motivation_level))
        conn.commit()
        log_event(username, 'cbt', 'goal_checkin_created', f"Goal ID: {goal_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Check-in entry created'}), 201
    except Exception as e:
        return handle_exception(e, 'create_goal_checkin')

@app.route('/api/cbt/goals/<int:goal_id>/checkin', methods=['GET'])
def list_goal_checkins(goal_id):
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT * FROM goal_checkins WHERE goal_id=? AND username=? ORDER BY checkin_timestamp DESC', (goal_id, username)).fetchall()
        conn.close()
        result = [dict(zip([c[0] for c in cur.description], row)) for row in rows]
        return jsonify({'entries': result}), 200
    except Exception as e:
        return handle_exception(e, 'list_goal_checkins')

# ========== AI MEMORY INTEGRATION: Goals ==========
def summarize_goals(username, limit=3):
    """Summarize recent goal activity for AI memory/context"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT goal_title, status, progress_percentage, entry_timestamp FROM goals WHERE username=? ORDER BY entry_timestamp DESC LIMIT ?', (username, limit)).fetchall()
        conn.close()
        if not rows:
            return None
        summary = []
        for r in rows:
            summary.append(f"{r[0]} ({r[1]}, {r[2]}%) on {r[3][:10]}")
        return "Recent goals: " + "; ".join(summary)
    except Exception:
        return None
# ================== CBT: VALUES CLARIFICATION ENDPOINTS ==================

@app.route('/api/cbt/values', methods=['POST'])
def create_value():
    """Create a new values clarification entry"""
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        required = ['value_name']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        value_name = data['value_name']
        value_description = data.get('value_description')
        importance_rating = data.get('importance_rating')
        current_alignment = data.get('current_alignment')
        life_area = data.get('life_area')
        related_goals = data.get('related_goals')
        is_active = int(data.get('is_active', 1))
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO values_clarification (username, value_name, value_description, importance_rating, current_alignment, life_area, related_goals, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (username, value_name, value_description, importance_rating, current_alignment, life_area, related_goals, is_active))
        conn.commit()
        log_event(username, 'cbt', 'value_created', f"Value: {value_name}")
        conn.close()
        return jsonify({'success': True, 'message': 'Value entry created'}), 201
    except Exception as e:
        return handle_exception(e, 'create_value')

@app.route('/api/cbt/values', methods=['GET'])
def list_values():
    """List all values clarification entries for the authenticated user"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT * FROM values_clarification WHERE username=? ORDER BY entry_timestamp DESC', (username,)).fetchall()
        conn.close()
        result = [dict(zip([c[0] for c in cur.description], row)) for row in rows]
        return jsonify({'entries': result}), 200
    except Exception as e:
        return handle_exception(e, 'list_values')

@app.route('/api/cbt/values/<int:entry_id>', methods=['GET'])
def get_value(entry_id):
    """Get a single values clarification entry by ID"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM values_clarification WHERE id=? AND username=?', (entry_id, username)).fetchone()
        conn.close()
        if not row:
            return jsonify({'error': 'Entry not found'}), 404
        result = dict(zip([c[0] for c in cur.description], row))
        return jsonify(result), 200
    except Exception as e:
        return handle_exception(e, 'get_value')

@app.route('/api/cbt/values/<int:entry_id>', methods=['PUT'])
def update_value(entry_id):
    """Update a values clarification entry"""
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM values_clarification WHERE id=? AND username=?', (entry_id, username)).fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Entry not found'}), 404
        fields = ['value_name', 'value_description', 'importance_rating', 'current_alignment', 'life_area', 'related_goals', 'is_active']
        updates = {k: data[k] for k in fields if k in data}
        set_clause = ', '.join([f"{k}=?" for k in updates.keys()])
        values = list(updates.values()) + [entry_id, username]
        cur.execute(f'UPDATE values_clarification SET {set_clause} WHERE id=? AND username=?', values)
        conn.commit()
        log_event(username, 'cbt', 'value_updated', f"ID: {entry_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Entry updated'}), 200
    except Exception as e:
        return handle_exception(e, 'update_value')

@app.route('/api/cbt/values/<int:entry_id>', methods=['DELETE'])
def delete_value(entry_id):
    """Delete a values clarification entry"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM values_clarification WHERE id=? AND username=?', (entry_id, username)).fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Entry not found'}), 404
        cur.execute('DELETE FROM values_clarification WHERE id=? AND username=?', (entry_id, username))
        conn.commit()
        log_event(username, 'cbt', 'value_deleted', f"ID: {entry_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Entry deleted'}), 200
    except Exception as e:
        return handle_exception(e, 'delete_value')

# ========== AI MEMORY INTEGRATION: Values Clarification ==========
def summarize_values_clarification(username, limit=3):
    """Summarize recent values clarification activity for AI memory/context"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT value_name, importance_rating, current_alignment, entry_timestamp FROM values_clarification WHERE username=? ORDER BY entry_timestamp DESC LIMIT ?', (username, limit)).fetchall()
        conn.close()
        if not rows:
            return None
        summary = []
        for r in rows:
            summary.append(f"{r[0]} (importance {r[1]}, align {r[2]}) on {r[3][:10]}")
        return "Recent values: " + "; ".join(summary)
    except Exception:
        return None
# ================== CBT: SELF-COMPASSION JOURNAL ENDPOINTS ==================

@app.route('/api/cbt/self-compassion', methods=['POST'])
def create_self_compassion():
    """Create a new self-compassion journal entry"""
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        difficult_situation = data.get('difficult_situation')
        self_critical_thoughts = data.get('self_critical_thoughts')
        common_humanity = data.get('common_humanity')
        kind_response = data.get('kind_response')
        self_care_action = data.get('self_care_action')
        mood_before = data.get('mood_before')
        mood_after = data.get('mood_after')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO self_compassion_journal (username, difficult_situation, self_critical_thoughts, common_humanity, kind_response, self_care_action, mood_before, mood_after) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (username, difficult_situation, self_critical_thoughts, common_humanity, kind_response, self_care_action, mood_before, mood_after))
        conn.commit()
        log_event(username, 'cbt', 'self_compassion_created', f"Situation: {difficult_situation}")
        conn.close()
        return jsonify({'success': True, 'message': 'Self-compassion journal entry created'}), 201
    except Exception as e:
        return handle_exception(e, 'create_self_compassion')

@app.route('/api/cbt/self-compassion', methods=['GET'])
def list_self_compassion():
    """List all self-compassion journal entries for the authenticated user"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT * FROM self_compassion_journal WHERE username=? ORDER BY entry_timestamp DESC', (username,)).fetchall()
        conn.close()
        result = [dict(zip([c[0] for c in cur.description], row)) for row in rows]
        return jsonify({'entries': result}), 200
    except Exception as e:
        return handle_exception(e, 'list_self_compassion')

@app.route('/api/cbt/self-compassion/<int:entry_id>', methods=['GET'])
def get_self_compassion(entry_id):
    """Get a single self-compassion journal entry by ID"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM self_compassion_journal WHERE id=? AND username=?', (entry_id, username)).fetchone()
        conn.close()
        if not row:
            return jsonify({'error': 'Entry not found'}), 404
        result = dict(zip([c[0] for c in cur.description], row))
        return jsonify(result), 200
    except Exception as e:
        return handle_exception(e, 'get_self_compassion')

@app.route('/api/cbt/self-compassion/<int:entry_id>', methods=['PUT'])
def update_self_compassion(entry_id):
    """Update a self-compassion journal entry"""
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM self_compassion_journal WHERE id=? AND username=?', (entry_id, username)).fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Entry not found'}), 404
        fields = ['difficult_situation', 'self_critical_thoughts', 'common_humanity', 'kind_response', 'self_care_action', 'mood_before', 'mood_after']
        updates = {k: data[k] for k in fields if k in data}
        set_clause = ', '.join([f"{k}=?" for k in updates.keys()])
        values = list(updates.values()) + [entry_id, username]
        cur.execute(f'UPDATE self_compassion_journal SET {set_clause} WHERE id=? AND username=?', values)
        conn.commit()
        log_event(username, 'cbt', 'self_compassion_updated', f"ID: {entry_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Entry updated'}), 200
    except Exception as e:
        return handle_exception(e, 'update_self_compassion')

@app.route('/api/cbt/self-compassion/<int:entry_id>', methods=['DELETE'])
def delete_self_compassion(entry_id):
    """Delete a self-compassion journal entry"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM self_compassion_journal WHERE id=? AND username=?', (entry_id, username)).fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Entry not found'}), 404
        cur.execute('DELETE FROM self_compassion_journal WHERE id=? AND username=?', (entry_id, username))
        conn.commit()
        log_event(username, 'cbt', 'self_compassion_deleted', f"ID: {entry_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Entry deleted'}), 200
    except Exception as e:
        return handle_exception(e, 'delete_self_compassion')

# ========== AI MEMORY INTEGRATION: Self-Compassion Journal ==========
def summarize_self_compassion(username, limit=3):
    """Summarize recent self-compassion journal activity for AI memory/context"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT difficult_situation, kind_response, mood_before, mood_after, entry_timestamp FROM self_compassion_journal WHERE username=? ORDER BY entry_timestamp DESC LIMIT ?', (username, limit)).fetchall()
        conn.close()
        if not rows:
            return None
        summary = []
        for r in rows:
            summary.append(f"{r[0]}: {r[1]} ({r[2]}→{r[3]}) on {r[4][:10]}")
        return "Recent self-compassion: " + "; ".join(summary)
    except Exception:
        return None
# ================== CBT: COPING CARDS ENDPOINTS ==================

@app.route('/api/cbt/coping-card', methods=['POST'])
def create_coping_card():
    """Create a new coping card entry"""
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        required = ['card_title']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        card_title = data['card_title']
        situation_trigger = data.get('situation_trigger')
        unhelpful_thought = data.get('unhelpful_thought')
        helpful_response = data.get('helpful_response')
        coping_strategies = data.get('coping_strategies')
        is_favorite = int(data.get('is_favorite', 0))
        times_used = int(data.get('times_used', 0))
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO coping_cards (username, card_title, situation_trigger, unhelpful_thought, helpful_response, coping_strategies, is_favorite, times_used) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (username, card_title, situation_trigger, unhelpful_thought, helpful_response, coping_strategies, is_favorite, times_used))
        conn.commit()
        log_event(username, 'cbt', 'coping_card_created', f"Title: {card_title}")
        conn.close()
        return jsonify({'success': True, 'message': 'Coping card entry created'}), 201
    except Exception as e:
        return handle_exception(e, 'create_coping_card')

@app.route('/api/cbt/coping-card', methods=['GET'])
def list_coping_cards():
    """List all coping card entries for the authenticated user"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT * FROM coping_cards WHERE username=? ORDER BY entry_timestamp DESC', (username,)).fetchall()
        conn.close()
        result = [dict(zip([c[0] for c in cur.description], row)) for row in rows]
        return jsonify({'entries': result}), 200
    except Exception as e:
        return handle_exception(e, 'list_coping_cards')

@app.route('/api/cbt/coping-card/<int:entry_id>', methods=['GET'])
def get_coping_card(entry_id):
    """Get a single coping card entry by ID"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM coping_cards WHERE id=? AND username=?', (entry_id, username)).fetchone()
        conn.close()
        if not row:
            return jsonify({'error': 'Entry not found'}), 404
        result = dict(zip([c[0] for c in cur.description], row))
        return jsonify(result), 200
    except Exception as e:
        return handle_exception(e, 'get_coping_card')

@app.route('/api/cbt/coping-card/<int:entry_id>', methods=['PUT'])
def update_coping_card(entry_id):
    """Update a coping card entry"""
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM coping_cards WHERE id=? AND username=?', (entry_id, username)).fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Entry not found'}), 404
        fields = ['card_title', 'situation_trigger', 'unhelpful_thought', 'helpful_response', 'coping_strategies', 'is_favorite', 'times_used']
        updates = {k: data[k] for k in fields if k in data}
        set_clause = ', '.join([f"{k}=?" for k in updates.keys()])
        values = list(updates.values()) + [entry_id, username]
        cur.execute(f'UPDATE coping_cards SET {set_clause} WHERE id=? AND username=?', values)
        conn.commit()
        log_event(username, 'cbt', 'coping_card_updated', f"ID: {entry_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Entry updated'}), 200
    except Exception as e:
        return handle_exception(e, 'update_coping_card')

@app.route('/api/cbt/coping-card/<int:entry_id>', methods=['DELETE'])
def delete_coping_card(entry_id):
    """Delete a coping card entry"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM coping_cards WHERE id=? AND username=?', (entry_id, username)).fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Entry not found'}), 404
        cur.execute('DELETE FROM coping_cards WHERE id=? AND username=?', (entry_id, username))
        conn.commit()
        log_event(username, 'cbt', 'coping_card_deleted', f"ID: {entry_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Entry deleted'}), 200
    except Exception as e:
        return handle_exception(e, 'delete_coping_card')

# ========== AI MEMORY INTEGRATION: Coping Cards ==========
def summarize_coping_cards(username, limit=3):
    """Summarize recent coping card activity for AI memory/context"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT card_title, helpful_response, times_used, entry_timestamp FROM coping_cards WHERE username=? ORDER BY entry_timestamp DESC LIMIT ?', (username, limit)).fetchall()
        conn.close()
        if not rows:
            return None
        summary = []
        for r in rows:
            summary.append(f"{r[0]}: {r[1]} (used {r[2]}x) on {r[3][:10]}")
        return "Recent coping cards: " + "; ".join(summary)
    except Exception:
        return None
# ================== CBT: PROBLEM-SOLVING WORKSHEET ENDPOINTS ==================

@app.route('/api/cbt/problem-solving', methods=['POST'])
def create_problem_solving():
    """Create a new problem-solving worksheet entry"""
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        required = ['problem_description']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        problem_description = data['problem_description']
        problem_importance = data.get('problem_importance')
        brainstormed_solutions = data.get('brainstormed_solutions')
        chosen_solution = data.get('chosen_solution')
        action_steps = data.get('action_steps')
        outcome = data.get('outcome')
        status = data.get('status', 'in_progress')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO problem_solving (username, problem_description, problem_importance, brainstormed_solutions, chosen_solution, action_steps, outcome, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (username, problem_description, problem_importance, brainstormed_solutions, chosen_solution, action_steps, outcome, status))
        conn.commit()
        log_event(username, 'cbt', 'problem_solving_created', f"Problem: {problem_description}")
        conn.close()
        return jsonify({'success': True, 'message': 'Problem-solving entry created'}), 201
    except Exception as e:
        return handle_exception(e, 'create_problem_solving')

@app.route('/api/cbt/problem-solving', methods=['GET'])
def list_problem_solving():
    """List all problem-solving worksheet entries for the authenticated user"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT * FROM problem_solving WHERE username=? ORDER BY entry_timestamp DESC', (username,)).fetchall()
        conn.close()
        result = [dict(zip([c[0] for c in cur.description], row)) for row in rows]
        return jsonify({'entries': result}), 200
    except Exception as e:
        return handle_exception(e, 'list_problem_solving')

@app.route('/api/cbt/problem-solving/<int:entry_id>', methods=['GET'])
def get_problem_solving(entry_id):
    """Get a single problem-solving worksheet entry by ID"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM problem_solving WHERE id=? AND username=?', (entry_id, username)).fetchone()
        conn.close()
        if not row:
            return jsonify({'error': 'Entry not found'}), 404
        result = dict(zip([c[0] for c in cur.description], row))
        return jsonify(result), 200
    except Exception as e:
        return handle_exception(e, 'get_problem_solving')

@app.route('/api/cbt/problem-solving/<int:entry_id>', methods=['PUT'])
def update_problem_solving(entry_id):
    """Update a problem-solving worksheet entry"""
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM problem_solving WHERE id=? AND username=?', (entry_id, username)).fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Entry not found'}), 404
        fields = ['problem_description', 'problem_importance', 'brainstormed_solutions', 'chosen_solution', 'action_steps', 'outcome', 'status']
        updates = {k: data[k] for k in fields if k in data}
        set_clause = ', '.join([f"{k}=?" for k in updates.keys()])
        values = list(updates.values()) + [entry_id, username]
        cur.execute(f'UPDATE problem_solving SET {set_clause} WHERE id=? AND username=?', values)
        conn.commit()
        log_event(username, 'cbt', 'problem_solving_updated', f"ID: {entry_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Entry updated'}), 200
    except Exception as e:
        return handle_exception(e, 'update_problem_solving')

@app.route('/api/cbt/problem-solving/<int:entry_id>', methods=['DELETE'])
def delete_problem_solving(entry_id):
    """Delete a problem-solving worksheet entry"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM problem_solving WHERE id=? AND username=?', (entry_id, username)).fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Entry not found'}), 404
        cur.execute('DELETE FROM problem_solving WHERE id=? AND username=?', (entry_id, username))
        conn.commit()
        log_event(username, 'cbt', 'problem_solving_deleted', f"ID: {entry_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Entry deleted'}), 200
    except Exception as e:
        return handle_exception(e, 'delete_problem_solving')

# ========== AI MEMORY INTEGRATION: Problem Solving ==========
def summarize_problem_solving(username, limit=3):
    """Summarize recent problem-solving worksheet activity for AI memory/context"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT problem_description, chosen_solution, outcome, status, entry_timestamp FROM problem_solving WHERE username=? ORDER BY entry_timestamp DESC LIMIT ?', (username, limit)).fetchall()
        conn.close()
        if not rows:
            return None
        summary = []
        for r in rows:
            summary.append(f"{r[0]}: {r[1]} → {r[2]} ({r[3]}) on {r[4][:10]}")
        return "Recent problem-solving: " + "; ".join(summary)
    except Exception:
        return None
# ================== CBT: EXPOSURE HIERARCHY ENDPOINTS ==================

@app.route('/api/cbt/exposure', methods=['POST'])
def create_exposure_hierarchy():
    """Create a new exposure hierarchy entry"""
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        required = ['fear_situation']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        fear_situation = data['fear_situation']
        initial_suds = data.get('initial_suds')
        target_suds = data.get('target_suds')
        hierarchy_rank = data.get('hierarchy_rank')
        status = data.get('status', 'not_started')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO exposure_hierarchy (username, fear_situation, initial_suds, target_suds, hierarchy_rank, status) VALUES (?, ?, ?, ?, ?, ?)''',
            (username, fear_situation, initial_suds, target_suds, hierarchy_rank, status))
        conn.commit()
        log_event(username, 'cbt', 'exposure_hierarchy_created', f"Situation: {fear_situation}")
        conn.close()
        return jsonify({'success': True, 'message': 'Exposure hierarchy entry created'}), 201
    except Exception as e:
        return handle_exception(e, 'create_exposure_hierarchy')

@app.route('/api/cbt/exposure', methods=['GET'])
def list_exposure_hierarchy():
    """List all exposure hierarchy entries for the authenticated user"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT * FROM exposure_hierarchy WHERE username=? ORDER BY hierarchy_rank ASC, entry_timestamp DESC', (username,)).fetchall()
        conn.close()
        result = [dict(zip([c[0] for c in cur.description], row)) for row in rows]
        return jsonify({'entries': result}), 200
    except Exception as e:
        return handle_exception(e, 'list_exposure_hierarchy')

@app.route('/api/cbt/exposure/<int:entry_id>', methods=['GET'])
def get_exposure_hierarchy(entry_id):
    """Get a single exposure hierarchy entry by ID"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM exposure_hierarchy WHERE id=? AND username=?', (entry_id, username)).fetchone()
        conn.close()
        if not row:
            return jsonify({'error': 'Entry not found'}), 404
        result = dict(zip([c[0] for c in cur.description], row))
        return jsonify(result), 200
    except Exception as e:
        return handle_exception(e, 'get_exposure_hierarchy')

@app.route('/api/cbt/exposure/<int:entry_id>', methods=['PUT'])
def update_exposure_hierarchy(entry_id):
    """Update an exposure hierarchy entry"""
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM exposure_hierarchy WHERE id=? AND username=?', (entry_id, username)).fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Entry not found'}), 404
        fields = ['fear_situation', 'initial_suds', 'target_suds', 'hierarchy_rank', 'status']
        updates = {k: data[k] for k in fields if k in data}
        set_clause = ', '.join([f"{k}=?" for k in updates.keys()])
        values = list(updates.values()) + [entry_id, username]
        cur.execute(f'UPDATE exposure_hierarchy SET {set_clause} WHERE id=? AND username=?', values)
        conn.commit()
        log_event(username, 'cbt', 'exposure_hierarchy_updated', f"ID: {entry_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Entry updated'}), 200
    except Exception as e:
        return handle_exception(e, 'update_exposure_hierarchy')

@app.route('/api/cbt/exposure/<int:entry_id>', methods=['DELETE'])
def delete_exposure_hierarchy(entry_id):
    """Delete an exposure hierarchy entry"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM exposure_hierarchy WHERE id=? AND username=?', (entry_id, username)).fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Entry not found'}), 404
        cur.execute('DELETE FROM exposure_hierarchy WHERE id=? AND username=?', (entry_id, username))
        conn.commit()
        log_event(username, 'cbt', 'exposure_hierarchy_deleted', f"ID: {entry_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Entry deleted'}), 200
    except Exception as e:
        return handle_exception(e, 'delete_exposure_hierarchy')

# Exposure Attempts CRUD
@app.route('/api/cbt/exposure/<int:exposure_id>/attempt', methods=['POST'])
def create_exposure_attempt(exposure_id):
    """Create a new exposure attempt for a hierarchy item"""
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        pre_suds = data.get('pre_suds')
        peak_suds = data.get('peak_suds')
        post_suds = data.get('post_suds')
        duration_minutes = data.get('duration_minutes')
        coping_strategies_used = data.get('coping_strategies_used')
        notes = data.get('notes')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO exposure_attempts (exposure_id, username, pre_suds, peak_suds, post_suds, duration_minutes, coping_strategies_used, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (exposure_id, username, pre_suds, peak_suds, post_suds, duration_minutes, coping_strategies_used, notes))
        conn.commit()
        log_event(username, 'cbt', 'exposure_attempt_created', f"Exposure ID: {exposure_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Exposure attempt entry created'}), 201
    except Exception as e:
        return handle_exception(e, 'create_exposure_attempt')

@app.route('/api/cbt/exposure/<int:exposure_id>/attempt', methods=['GET'])
def list_exposure_attempts(exposure_id):
    """List all exposure attempts for a hierarchy item"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT * FROM exposure_attempts WHERE exposure_id=? AND username=? ORDER BY attempt_timestamp DESC', (exposure_id, username)).fetchall()
        conn.close()
        result = [dict(zip([c[0] for c in cur.description], row)) for row in rows]
        return jsonify({'entries': result}), 200
    except Exception as e:
        return handle_exception(e, 'list_exposure_attempts')

# ========== AI MEMORY INTEGRATION: Exposure Hierarchy ==========
def summarize_exposure_hierarchy(username, limit=3):
    """Summarize recent exposure hierarchy activity for AI memory/context"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT fear_situation, status, initial_suds, target_suds, entry_timestamp FROM exposure_hierarchy WHERE username=? ORDER BY entry_timestamp DESC LIMIT ?', (username, limit)).fetchall()
        conn.close()
        if not rows:
            return None
        summary = []
        for r in rows:
            summary.append(f"{r[0]} ({r[1]}): {r[2]}→{r[3]} SUDS on {r[4][:10]}")
        return "Recent exposures: " + "; ".join(summary)
    except Exception:
        return None
# ================== CBT: CORE BELIEF WORKSHEET ENDPOINTS ==================

@app.route('/api/cbt/core-belief', methods=['POST'])
def create_core_belief():
    """Create a new core belief worksheet entry"""
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        required = ['old_belief']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        old_belief = data['old_belief']
        belief_origin = data.get('belief_origin')
        evidence_for = data.get('evidence_for')
        evidence_against = data.get('evidence_against')
        new_balanced_belief = data.get('new_balanced_belief')
        belief_strength_before = data.get('belief_strength_before')
        belief_strength_after = data.get('belief_strength_after')
        is_active = int(data.get('is_active', 1))
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO core_beliefs (username, old_belief, belief_origin, evidence_for, evidence_against, new_balanced_belief, belief_strength_before, belief_strength_after, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (username, old_belief, belief_origin, evidence_for, evidence_against, new_balanced_belief, belief_strength_before, belief_strength_after, is_active))
        conn.commit()
        log_event(username, 'cbt', 'core_belief_created', f"Old: {old_belief}")
        conn.close()
        return jsonify({'success': True, 'message': 'Core belief entry created'}), 201
    except Exception as e:
        return handle_exception(e, 'create_core_belief')

@app.route('/api/cbt/core-belief', methods=['GET'])
def list_core_beliefs():
    """List all core belief worksheet entries for the authenticated user"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT * FROM core_beliefs WHERE username=? ORDER BY entry_timestamp DESC', (username,)).fetchall()
        conn.close()
        result = [dict(zip([c[0] for c in cur.description], row)) for row in rows]
        return jsonify({'entries': result}), 200
    except Exception as e:
        return handle_exception(e, 'list_core_beliefs')

@app.route('/api/cbt/core-belief/<int:entry_id>', methods=['GET'])
def get_core_belief(entry_id):
    """Get a single core belief worksheet entry by ID"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM core_beliefs WHERE id=? AND username=?', (entry_id, username)).fetchone()
        conn.close()
        if not row:
            return jsonify({'error': 'Entry not found'}), 404
        result = dict(zip([c[0] for c in cur.description], row))
        return jsonify(result), 200
    except Exception as e:
        return handle_exception(e, 'get_core_belief')

@app.route('/api/cbt/core-belief/<int:entry_id>', methods=['PUT'])
def update_core_belief(entry_id):
    """Update a core belief worksheet entry"""
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM core_beliefs WHERE id=? AND username=?', (entry_id, username)).fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Entry not found'}), 404
        # Only update provided fields
        fields = ['old_belief', 'belief_origin', 'evidence_for', 'evidence_against', 'new_balanced_belief', 'belief_strength_before', 'belief_strength_after', 'is_active']
        updates = {k: data[k] for k in fields if k in data}
        set_clause = ', '.join([f"{k}=?" for k in updates.keys()])
        values = list(updates.values()) + [entry_id, username]
        cur.execute(f'UPDATE core_beliefs SET {set_clause} WHERE id=? AND username=?', values)
        conn.commit()
        log_event(username, 'cbt', 'core_belief_updated', f"ID: {entry_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Entry updated'}), 200
    except Exception as e:
        return handle_exception(e, 'update_core_belief')

@app.route('/api/cbt/core-belief/<int:entry_id>', methods=['DELETE'])
def delete_core_belief(entry_id):
    """Delete a core belief worksheet entry"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM core_beliefs WHERE id=? AND username=?', (entry_id, username)).fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Entry not found'}), 404
        cur.execute('DELETE FROM core_beliefs WHERE id=? AND username=?', (entry_id, username))
        conn.commit()
        log_event(username, 'cbt', 'core_belief_deleted', f"ID: {entry_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Entry deleted'}), 200
    except Exception as e:
        return handle_exception(e, 'delete_core_belief')

# ========== AI MEMORY INTEGRATION: Core Beliefs ==========
def summarize_core_beliefs(username, limit=3):
    """Summarize recent core belief worksheet activity for AI memory/context"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT old_belief, new_balanced_belief, belief_strength_before, belief_strength_after, entry_timestamp FROM core_beliefs WHERE username=? ORDER BY entry_timestamp DESC LIMIT ?', (username, limit)).fetchall()
        conn.close()
        if not rows:
            return None
        summary = []
        for r in rows:
            summary.append(f"Old: {r[0]}, New: {r[1]}, {r[2]}→{r[3]} on {r[4][:10]}")
        return "Recent core beliefs: " + "; ".join(summary)
    except Exception:
        return None
# ================== CBT: SLEEP DIARY ENDPOINTS ==================

@app.route('/api/cbt/sleep', methods=['POST'])
def create_sleep_diary():
    """Create a new sleep diary entry"""
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        required = ['sleep_date']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        sleep_date = data['sleep_date']
        bedtime = data.get('bedtime')
        wake_time = data.get('wake_time')
        time_to_fall_asleep = data.get('time_to_fall_asleep')
        times_woken = data.get('times_woken')
        total_sleep_hours = data.get('total_sleep_hours')
        sleep_quality = data.get('sleep_quality')
        dreams_nightmares = data.get('dreams_nightmares')
        factors_affecting = data.get('factors_affecting')
        morning_mood = data.get('morning_mood')
        notes = data.get('notes')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO sleep_diary (username, sleep_date, bedtime, wake_time, time_to_fall_asleep, times_woken, total_sleep_hours, sleep_quality, dreams_nightmares, factors_affecting, morning_mood, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (username, sleep_date, bedtime, wake_time, time_to_fall_asleep, times_woken, total_sleep_hours, sleep_quality, dreams_nightmares, factors_affecting, morning_mood, notes))
        conn.commit()
        log_event(username, 'cbt', 'sleep_diary_created', f"Date: {sleep_date}, Quality: {sleep_quality}")
        conn.close()
        return jsonify({'success': True, 'message': 'Sleep diary entry created'}), 201
    except Exception as e:
        return handle_exception(e, 'create_sleep_diary')

@app.route('/api/cbt/sleep', methods=['GET'])
def list_sleep_diary():
    """List all sleep diary entries for the authenticated user"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT * FROM sleep_diary WHERE username=? ORDER BY entry_timestamp DESC', (username,)).fetchall()
        conn.close()
        result = [dict(zip([c[0] for c in cur.description], row)) for row in rows]
        return jsonify({'entries': result}), 200
    except Exception as e:
        return handle_exception(e, 'list_sleep_diary')

@app.route('/api/cbt/sleep/<int:entry_id>', methods=['GET'])
def get_sleep_diary(entry_id):
    """Get a single sleep diary entry by ID"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM sleep_diary WHERE id=? AND username=?', (entry_id, username)).fetchone()
        conn.close()
        if not row:
            return jsonify({'error': 'Entry not found'}), 404
        result = dict(zip([c[0] for c in cur.description], row))
        return jsonify(result), 200
    except Exception as e:
        return handle_exception(e, 'get_sleep_diary')

@app.route('/api/cbt/sleep/<int:entry_id>', methods=['PUT'])
def update_sleep_diary(entry_id):
    """Update a sleep diary entry"""
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM sleep_diary WHERE id=? AND username=?', (entry_id, username)).fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Entry not found'}), 404
        # Only update provided fields
        fields = ['sleep_date', 'bedtime', 'wake_time', 'time_to_fall_asleep', 'times_woken', 'total_sleep_hours', 'sleep_quality', 'dreams_nightmares', 'factors_affecting', 'morning_mood', 'notes']
        updates = {k: data[k] for k in fields if k in data}
        set_clause = ', '.join([f"{k}=?" for k in updates.keys()])
        values = list(updates.values()) + [entry_id, username]
        cur.execute(f'UPDATE sleep_diary SET {set_clause} WHERE id=? AND username=?', values)
        conn.commit()
        log_event(username, 'cbt', 'sleep_diary_updated', f"ID: {entry_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Entry updated'}), 200
    except Exception as e:
        return handle_exception(e, 'update_sleep_diary')

@app.route('/api/cbt/sleep/<int:entry_id>', methods=['DELETE'])
def delete_sleep_diary(entry_id):
    """Delete a sleep diary entry"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM sleep_diary WHERE id=? AND username=?', (entry_id, username)).fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Entry not found'}), 404
        cur.execute('DELETE FROM sleep_diary WHERE id=? AND username=?', (entry_id, username))
        conn.commit()
        log_event(username, 'cbt', 'sleep_diary_deleted', f"ID: {entry_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Entry deleted'}), 200
    except Exception as e:
        return handle_exception(e, 'delete_sleep_diary')

# ========== AI MEMORY INTEGRATION: Sleep Diary ==========
def summarize_sleep_diary(username, limit=3):
    """Summarize recent sleep diary activity for AI memory/context"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT sleep_date, total_sleep_hours, sleep_quality, morning_mood, entry_timestamp FROM sleep_diary WHERE username=? ORDER BY entry_timestamp DESC LIMIT ?', (username, limit)).fetchall()
        conn.close()
        if not rows:
            return None
        summary = []
        for r in rows:
            summary.append(f"{r[0]}: {r[1]}h, quality {r[2]}, mood {r[3]}")
        return "Recent sleep diary: " + "; ".join(summary)
    except Exception:
        return None
# ================== CBT: RELAXATION TECHNIQUES ENDPOINTS ==================

@app.route('/api/cbt/relaxation', methods=['POST'])
def create_relaxation_technique():
    """Create a new relaxation technique entry"""
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        required = ['technique_type']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        technique_type = data['technique_type']
        duration_minutes = data.get('duration_minutes')
        effectiveness_rating = data.get('effectiveness_rating')
        body_scan_areas = data.get('body_scan_areas')
        notes = data.get('notes')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO relaxation_techniques (username, technique_type, duration_minutes, effectiveness_rating, body_scan_areas, notes) VALUES (?, ?, ?, ?, ?, ?)''',
            (username, technique_type, duration_minutes, effectiveness_rating, body_scan_areas, notes))
        conn.commit()
        log_event(username, 'cbt', 'relaxation_technique_created', f"Type: {technique_type}, Duration: {duration_minutes}")
        conn.close()
        return jsonify({'success': True, 'message': 'Relaxation technique entry created'}), 201
    except Exception as e:
        return handle_exception(e, 'create_relaxation_technique')

@app.route('/api/cbt/relaxation', methods=['GET'])
def list_relaxation_techniques():
    """List all relaxation technique entries for the authenticated user"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT * FROM relaxation_techniques WHERE username=? ORDER BY entry_timestamp DESC', (username,)).fetchall()
        conn.close()
        result = [dict(zip([c[0] for c in cur.description], row)) for row in rows]
        return jsonify({'entries': result}), 200
    except Exception as e:
        return handle_exception(e, 'list_relaxation_techniques')

@app.route('/api/cbt/relaxation/<int:entry_id>', methods=['GET'])
def get_relaxation_technique(entry_id):
    """Get a single relaxation technique entry by ID"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM relaxation_techniques WHERE id=? AND username=?', (entry_id, username)).fetchone()
        conn.close()
        if not row:
            return jsonify({'error': 'Entry not found'}), 404
        result = dict(zip([c[0] for c in cur.description], row))
        return jsonify(result), 200
    except Exception as e:
        return handle_exception(e, 'get_relaxation_technique')

@app.route('/api/cbt/relaxation/<int:entry_id>', methods=['PUT'])
def update_relaxation_technique(entry_id):
    """Update a relaxation technique entry"""
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM relaxation_techniques WHERE id=? AND username=?', (entry_id, username)).fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Entry not found'}), 404
        # Only update provided fields
        fields = ['technique_type', 'duration_minutes', 'effectiveness_rating', 'body_scan_areas', 'notes']
        updates = {k: data[k] for k in fields if k in data}
        set_clause = ', '.join([f"{k}=?" for k in updates.keys()])
        values = list(updates.values()) + [entry_id, username]
        cur.execute(f'UPDATE relaxation_techniques SET {set_clause} WHERE id=? AND username=?', values)
        conn.commit()
        log_event(username, 'cbt', 'relaxation_technique_updated', f"ID: {entry_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Entry updated'}), 200
    except Exception as e:
        return handle_exception(e, 'update_relaxation_technique')

@app.route('/api/cbt/relaxation/<int:entry_id>', methods=['DELETE'])
def delete_relaxation_technique(entry_id):
    """Delete a relaxation technique entry"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM relaxation_techniques WHERE id=? AND username=?', (entry_id, username)).fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Entry not found'}), 404
        cur.execute('DELETE FROM relaxation_techniques WHERE id=? AND username=?', (entry_id, username))
        conn.commit()
        log_event(username, 'cbt', 'relaxation_technique_deleted', f"ID: {entry_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Entry deleted'}), 200
    except Exception as e:
        return handle_exception(e, 'delete_relaxation_technique')

# ========== AI MEMORY INTEGRATION: Relaxation Techniques ==========
def summarize_relaxation_techniques(username, limit=3):
    """Summarize recent relaxation technique activity for AI memory/context"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT technique_type, duration_minutes, effectiveness_rating, entry_timestamp FROM relaxation_techniques WHERE username=? ORDER BY entry_timestamp DESC LIMIT ?', (username, limit)).fetchall()
        conn.close()
        if not rows:
            return None
        summary = []
        for r in rows:
            summary.append(f"{r[0]} ({r[1]}min, rating {r[2]}) on {r[3][:10]}")
        return "Recent relaxation techniques: " + "; ".join(summary)
    except Exception:
        return None

# Note: Duplicate imports and ensure_pet_table removed (already defined at top of file)

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

# ==================== CORS CONFIGURATION ====================
# Note: Flask app already initialized at top of file (line 58)
# Restrict CORS origins in production for security
# In DEBUG mode, allow all origins for local development
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '').split(',') if os.environ.get('ALLOWED_ORIGINS') else None

if DEBUG and not ALLOWED_ORIGINS:
    # Development mode: allow all origins
    CORS(app, supports_credentials=True)
else:
    # Production mode: restrict to specific origins
    production_origins = ALLOWED_ORIGINS or [
        'https://healing-space.org.uk',
        'https://www.healing-space.org.uk',
        'https://web-production-64594.up.railway.app'
    ]
    CORS(app, origins=production_origins, supports_credentials=True)

# ==================== SECURITY HEADERS ====================
@app.after_request
def add_security_headers(response):
    """PHASE 2C: Add comprehensive security headers to all responses"""
    # Prevent clickjacking attacks
    response.headers['X-Frame-Options'] = 'DENY'

    # Prevent MIME type sniffing (critical for security)
    response.headers['X-Content-Type-Options'] = 'nosniff'

    # Enable XSS filter in older browsers
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # Enforce HTTPS (only in production)
    if not DEBUG:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'

    # Referrer policy for privacy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    # Permissions policy (disable unnecessary features)
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=(), payment=(), usb=()'

    # Content Security Policy (comprehensive - Phase 2C)
    if not DEBUG:
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self' https://api.groq.com https://www.healing-space.org.uk; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )

    return response

# ==================== ERROR HANDLING HELPER ====================
def handle_exception(e, context: str = 'unknown'):
    """
    Log exception details internally and return a safe generic error response.
    Prevents leaking internal error details to clients.
    """
    # Log the actual error for debugging/monitoring
    error_id = secrets.token_hex(4)  # Short unique ID for support reference
    log_event('system', 'error', f'{context}_error', f'Error ID: {error_id}, Details: {str(e)}')
    print(f"[ERROR {error_id}] {context}: {str(e)}")  # Also print for server logs

    # Return generic error to client with reference ID
    return jsonify({
        'error': 'An unexpected error occurred. Please try again.',
        'error_id': error_id,
        'code': 'INTERNAL_ERROR'
    }), 500

# ==================== CONTENT MODERATION ====================
class ContentModerator:
    """Simple content moderation for community posts and replies"""

    # Words/phrases that should be blocked entirely
    BLOCKED_PATTERNS = [
        # Slurs and hate speech (add as needed)
        # Keeping minimal for now - expand based on needs
    ]

    # Words to filter/mask (replace with asterisks)
    FILTER_WORDS = []

    def __init__(self):
        pass

    def moderate(self, text):
        """
        Check text for inappropriate content.
        Returns dict with 'allowed', 'reason', 'filtered_text', 'flagged', 'flag_reason'.
        """
        if not text or not text.strip():
            return {
                'allowed': False,
                'reason': 'Empty message not allowed',
                'filtered_text': '',
                'flagged': False,
                'flag_reason': None
            }

        text = text.strip()

        # Check message length (reasonable limits)
        if len(text) > 2000:
            return {
                'allowed': False,
                'reason': 'Message too long (max 2000 characters)',
                'filtered_text': text[:2000],
                'flagged': False,
                'flag_reason': None
            }

        # Check for blocked patterns
        text_lower = text.lower()
        for pattern in self.BLOCKED_PATTERNS:
            if pattern.lower() in text_lower:
                return {
                    'allowed': False,
                    'reason': 'Message contains inappropriate content',
                    'filtered_text': '',
                    'flagged': True,
                    'flag_reason': 'Blocked content detected'
                }

        # Filter/mask certain words if needed
        filtered_text = text
        for word in self.FILTER_WORDS:
            # Case-insensitive replacement with asterisks
            import re
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            filtered_text = pattern.sub('*' * len(word), filtered_text)

        return {
            'allowed': True,
            'reason': None,
            'filtered_text': filtered_text,
            'flagged': False,
            'flag_reason': None
        }

# Create global moderator instance
content_moderator = ContentModerator()

# ==================== CSRF PROTECTION ====================
# CSRF Secret key for token generation
import secrets as stdlib_secrets
CSRF_SECRET = os.environ.get('CSRF_SECRET', stdlib_secrets.token_hex(32))

# Endpoints exempt from CSRF (login, registration, public endpoints)
CSRF_EXEMPT_ENDPOINTS = {
    'index', 'health_check', 'login', 'register_user', 'register_clinician',
    'forgot_password', 'confirm_password_reset', 'get_csrf_token',
    'list_clinicians',  # Public listing
    # Phase 3: Messaging endpoints (CSRF token validation handled via session auth)
    'send_message', 'get_inbox', 'get_conversation', 'mark_message_read', 'delete_message'
}

def generate_csrf_token():
    """Generate a CSRF token for the current session"""
    if 'csrf_token' not in g:
        g.csrf_token = stdlib_secrets.token_hex(32)
    return g.csrf_token

def validate_csrf_token(token):
    """Validate CSRF token from request"""
    if not token:
        return False
    # For API use, we validate the token format and presence
    # In production, you'd want to validate against stored session tokens
    return len(token) == 64 and token.isalnum()

# ================== PHASE 2C: CONTENT-TYPE VALIDATION ==================

@app.before_request
def validate_content_type():
    """PHASE 2C: Validate Content-Type for POST/PUT/PATCH requests"""
    # Skip validation for GET/DELETE requests
    if request.method in ('GET', 'DELETE', 'HEAD', 'OPTIONS'):
        return
    
    # Skip if no body
    if not request.data:
        return
    
    content_type = request.headers.get('Content-Type', '').lower()
    
    # Allow JSON requests only (or form data for file uploads)
    if not (content_type.startswith('application/json') or 
            content_type.startswith('multipart/form-data')):
        log_event('system', 'security', 'invalid_content_type', f'Content-Type: {content_type}, Endpoint: {request.endpoint}')
        return jsonify({'error': 'Invalid Content-Type. Only application/json is allowed.'}), 415

@app.before_request
def csrf_protect():
    """CSRF protection middleware for state-changing requests"""
    # Skip CSRF check for safe methods
    if request.method in ('GET', 'HEAD', 'OPTIONS'):
        return

    # Skip CSRF check for exempt endpoints
    if request.endpoint in CSRF_EXEMPT_ENDPOINTS:
        return

    # Skip CSRF in development mode if explicitly disabled
    if DEBUG and os.environ.get('DISABLE_CSRF', '').lower() in ('1', 'true', 'yes'):
        return

    # Check for CSRF token in header (preferred for APIs)
    csrf_token = request.headers.get('X-CSRF-Token') or request.headers.get('X-CSRFToken')

    # Also check in JSON body as fallback
    if not csrf_token and request.is_json:
        csrf_token = request.json.get('_csrf_token') if request.json else None

    # Validate token
    if not csrf_token or not validate_csrf_token(csrf_token):
        log_event('system', 'security', 'csrf_validation_failed', f'Endpoint: {request.endpoint}, IP: {request.remote_addr}')
        return jsonify({'error': 'CSRF token missing or invalid', 'code': 'CSRF_FAILED'}), 403

@app.route('/api/csrf-token', methods=['GET'])
def get_csrf_token():
    """Get a CSRF token for subsequent requests"""
    token = stdlib_secrets.token_hex(32)
    response = jsonify({'csrf_token': token})
    # Also set as cookie for double-submit pattern
    response.set_cookie('csrf_token', token, httponly=False, samesite='Strict', secure=not DEBUG)
    return response

# ==================== RATE LIMITING ====================
# In-memory rate limiter (for single-instance deployments)
# For production multi-instance, use Redis-based rate limiting
from collections import defaultdict
import threading

class RateLimiter:
    """Simple in-memory rate limiter with IP and user tracking"""

    def __init__(self):
        self.requests = defaultdict(list)  # key -> list of timestamps
        self.lock = threading.Lock()
        # Rate limit configurations: (max_requests, window_seconds)
        self.limits = {
            'login': (5, 60),           # 5 login attempts per minute
            'verify_code': (10, 60),    # 10 code verification attempts per minute (Phase 1D)
            'register': (3, 300),       # 3 registrations per 5 minutes
            'forgot_password': (3, 300), # 3 password resets per 5 minutes
            'ai_chat': (30, 60),        # 30 AI chat messages per minute
            'default': (60, 60),        # 60 requests per minute default
        }

    def is_allowed(self, key: str, limit_type: str = 'default') -> bool:
        """Check if request is allowed under rate limit"""
        max_requests, window = self.limits.get(limit_type, self.limits['default'])

        with self.lock:
            now = time.time()
            # Clean old entries
            self.requests[key] = [t for t in self.requests[key] if now - t < window]

            # Check limit
            if len(self.requests[key]) >= max_requests:
                return False

            # Record request
            self.requests[key].append(now)
            return True

    def get_wait_time(self, key: str, limit_type: str = 'default') -> int:
        """Get seconds until next allowed request"""
        max_requests, window = self.limits.get(limit_type, self.limits['default'])

        with self.lock:
            now = time.time()
            self.requests[key] = [t for t in self.requests[key] if now - t < window]

            if len(self.requests[key]) < max_requests:
                return 0

            oldest = min(self.requests[key])
            return int(window - (now - oldest)) + 1

    def cleanup(self):
        """Remove stale entries (call periodically)"""
        with self.lock:
            now = time.time()
            max_window = max(w for _, w in self.limits.values())
            keys_to_remove = []
            for key, timestamps in self.requests.items():
                self.requests[key] = [t for t in timestamps if now - t < max_window]
                if not self.requests[key]:
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                del self.requests[key]

rate_limiter = RateLimiter()

def check_rate_limit(limit_type: str = 'default'):
    """Decorator to apply rate limiting to endpoints"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Use IP address and optionally username for rate limiting
            ip = request.remote_addr or 'unknown'
            username = None

            # Try to get username from request
            if request.is_json and request.json:
                username = request.json.get('username')
            elif request.args:
                username = request.args.get('username')

            # Rate limit by IP
            ip_key = f"ip:{ip}:{limit_type}"
            if not rate_limiter.is_allowed(ip_key, limit_type):
                wait_time = rate_limiter.get_wait_time(ip_key, limit_type)
                log_event(username or ip, 'security', 'rate_limit_exceeded', f'{limit_type} from {ip}')
                return jsonify({
                    'error': f'Too many requests. Please wait {wait_time} seconds.',
                    'code': 'RATE_LIMITED',
                    'retry_after': wait_time
                }), 429

            # Also rate limit by username if available (prevents distributed attacks)
            if username:
                user_key = f"user:{username}:{limit_type}"
                if not rate_limiter.is_allowed(user_key, limit_type):
                    wait_time = rate_limiter.get_wait_time(user_key, limit_type)
                    log_event(username, 'security', 'rate_limit_exceeded', f'{limit_type} for user {username}')
                    return jsonify({
                        'error': f'Too many requests. Please wait {wait_time} seconds.',
                        'code': 'RATE_LIMITED',
                        'retry_after': wait_time
                    }), 429

            return f(*args, **kwargs)
        return wrapped
    return decorator

# Database path - use volume on Railway, local otherwise
def get_db_path():
    """Get database path - use Railway volume if available"""
    if os.path.exists('/app/data'):
        # Railway volume mounted
        return '/app/data/therapist_app.db'
    return 'therapist_app.db'

def get_pet_db_path():
    """Get pet game database path - use Railway volume if available"""
    if os.path.exists('/app/data'):
        return '/app/data/pet_game.db'
    return 'pet_game.db'

DB_PATH = get_db_path()
PET_DB_PATH = get_pet_db_path()

# Database connection helper for PostgreSQL
def get_db_connection(timeout=30.0):
    """Create a connection to PostgreSQL database
    
    Supports both:
    1. DATABASE_URL (Railway): postgresql://user:pass@host:port/db
    2. Individual env vars: DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    """
    try:
        # Check for Railway DATABASE_URL first
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            conn = psycopg2.connect(database_url)
        else:
            # Fall back to individual environment variables
            conn = psycopg2.connect(
                host=os.environ.get('DB_HOST', 'localhost'),
                port=os.environ.get('DB_PORT', '5432'),
                database=os.environ.get('DB_NAME', 'healing_space_test'),
                user=os.environ.get('DB_USER', 'healing_space'),
                password=os.environ.get('DB_PASSWORD', 'healing_space_dev_pass')
            )
        return conn
    except psycopg2.Error as e:
        print(f"Failed to connect to PostgreSQL database: {e}")
        raise

# Load secrets
secrets_manager = SecretsManager(debug=DEBUG)
GROQ_API_KEY = secrets_manager.get_secret("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
API_URL = os.environ.get("API_URL", "https://api.groq.com/openai/v1/chat/completions")
PIN_SALT = secrets_manager.get_secret("PIN_SALT") or os.environ.get("PIN_SALT") or 'dev_fallback_salt'

# Validate critical API key on startup
_groq_key_warning_shown = False
def validate_groq_api_key():
    """Validate GROQ_API_KEY is configured properly"""
    global _groq_key_warning_shown
    if not GROQ_API_KEY:
        if DEBUG:
            if not _groq_key_warning_shown:
                print("=" * 60)
                print("WARNING: GROQ_API_KEY not set!")
                print("AI therapy chat features will NOT work.")
                print("Get an API key from https://console.groq.com")
                print("Set: export GROQ_API_KEY=your_key_here")
                print("=" * 60)
                _groq_key_warning_shown = True
        else:
            # In production, this is a critical error
            raise RuntimeError(
                "CRITICAL: GROQ_API_KEY environment variable is required in production. "
                "AI therapy features cannot function without it. "
                "Get an API key from https://console.groq.com"
            )
        return False
    # Basic format validation (Groq keys start with 'gsk_')
    if not GROQ_API_KEY.startswith('gsk_'):
        print("WARNING: GROQ_API_KEY may be invalid (expected prefix 'gsk_')")
    return True

# Validate on module load (but don't crash in debug mode)
try:
    validate_groq_api_key()
except RuntimeError as e:
    if not DEBUG:
        raise

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


def validate_password_strength(password: str) -> tuple:
    """
    Validate password meets security requirements.
    Returns (is_valid: bool, error_message: str or None)

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if not password:
        return False, 'Password is required'

    if len(password) < 8:
        return False, 'Password must be at least 8 characters'

    if not any(c.islower() for c in password):
        return False, 'Password must contain at least one lowercase letter'

    if not any(c.isupper() for c in password):
        return False, 'Password must contain at least one uppercase letter'

    if not any(c.isdigit() for c in password):
        return False, 'Password must contain at least one number'

    special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
    if not any(c in special_chars for c in password):
        return False, 'Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)'

    # Check for common weak passwords
    weak_passwords = {'password', 'password1', '12345678', 'qwerty123', 'admin123'}
    if password.lower() in weak_passwords:
        return False, 'This password is too common. Please choose a stronger password.'

    return True, None


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

# Encryption/Decryption functions (avoid importing from main.py)
_cached_encryption_key = None
_encryption_key_warning_shown = False

def get_encryption_key():
    """
    Get encryption key from environment or secrets manager.
    SECURITY: Key MUST be provided via environment variable or secrets manager.
    File-based key storage is NOT supported for security reasons.
    """
    global _cached_encryption_key, _encryption_key_warning_shown

    # Return cached key if available (avoids repeated env lookups)
    if _cached_encryption_key:
        return _cached_encryption_key

    # Try secrets manager first, then environment variable
    key = secrets.get_secret("ENCRYPTION_KEY") or os.environ.get("ENCRYPTION_KEY")

    if not key:
        if DEBUG:
            # Development fallback - generate ephemeral key with warning
            from cryptography.fernet import Fernet
            key = Fernet.generate_key().decode()
            if not _encryption_key_warning_shown:
                print("=" * 60)
                print("WARNING: ENCRYPTION_KEY not set!")
                print("Using ephemeral key for development only.")
                print("ALL DATA WILL BE LOST when the app restarts!")
                print("Set ENCRYPTION_KEY environment variable for persistent data.")
                print("Generate key: python3 -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"")
                print("=" * 60)
                _encryption_key_warning_shown = True
                log_event('system', 'security', 'encryption_key_missing', 'Using ephemeral key in DEBUG mode')
        else:
            # PRODUCTION: Encryption key is REQUIRED
            raise RuntimeError(
                "CRITICAL: ENCRYPTION_KEY environment variable is required in production. "
                "Generate with: python3 -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )

    # Validate key format
    try:
        from cryptography.fernet import Fernet
        # Test that the key is valid Fernet format
        Fernet(key.encode() if isinstance(key, str) else key)
    except Exception as e:
        raise ValueError(f"Invalid ENCRYPTION_KEY format. Must be a valid Fernet key. Error: {e}")

    _cached_encryption_key = key
    return key

def encrypt_text(text: str) -> str:
    """Encrypt text using Fernet"""
    if not text:
        return ""
    try:
        from cryptography.fernet import Fernet
        key = get_encryption_key()
        f = Fernet(key.encode() if isinstance(key, str) else key)
        return f.encrypt(text.encode()).decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        return text  # Fallback to plaintext in debug mode

def decrypt_text(encrypted: str) -> str:
    """Decrypt text using Fernet"""
    if not encrypted:
        return ""
    try:
        from cryptography.fernet import Fernet
        key = get_encryption_key()
        f = Fernet(key.encode() if isinstance(key, str) else key)
        return f.decrypt(encrypted.encode()).decode()
    except Exception as e:
        # If decryption fails, might be plaintext
        return encrypted

def init_db():
    """Initialize database - tables should already exist in PostgreSQL from migration"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # PostgreSQL: Just verify the database is accessible
        # Tables are already created from migration (Step 3)
        cursor.execute("SELECT 1")
        
        conn.commit()
        conn.close()
        print("✓ Database connection verified")
        return True
        
    except psycopg2.Error as e:
        print(f"Database initialization error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False
    
    # Initialize pet database
    try:
        ensure_pet_table()
        print("Pet database initialized successfully")
    except Exception as e:
        print(f"Pet database initialization error: {e}")


def get_authenticated_username():
    """Get authenticated username from Flask session (SECURE - Phase 1A).
    
    PRIMARY: Uses Flask session (secure, server-side, httponly)
    FALLBACK: X-Username header/query param for dev/test only (DEBUG mode)
    
    Returns: username if authenticated, None otherwise
    """
    try:
        # PRIMARY: Use Flask session (secure, server-side)
        if 'username' in session and 'role' in session:
            username = session.get('username')
            role = session.get('role')
            
            # Verify user still exists in database (prevents stale sessions)
            conn = get_db_connection()
            cur = conn.cursor()
            result = cur.execute(
                "SELECT role FROM users WHERE username=? AND role=?",
                (username, role)
            ).fetchone()
            conn.close()
            
            if result:
                return username  # Session is valid
            else:
                # User doesn't exist or role mismatch - invalidate session
                session.clear()
                return None
        
        # FALLBACK: For development/testing with X-Username header (INSECURE)
        # This should NEVER be used in production - prefer session
        if DEBUG:
            fallback = request.headers.get('X-Username') or request.args.get('username')
            if fallback:
                print(f"⚠️  WARNING: Using insecure X-Username header for {fallback}. Only use in DEBUG mode.")
                return fallback
        
        return None
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return None

@app.route('/api/cbt/breathing', methods=['POST'])
def create_breathing_exercise():
    """Create a new breathing exercise entry"""
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        required = ['exercise_type']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        exercise_type = data['exercise_type']
        duration_seconds = data.get('duration_seconds')
        pre_anxiety_level = data.get('pre_anxiety_level')
        post_anxiety_level = data.get('post_anxiety_level')
        notes = data.get('notes')
        completed = int(data.get('completed', 1))
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO breathing_exercises (username, exercise_type, duration_seconds, pre_anxiety_level, post_anxiety_level, notes, completed) VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (username, exercise_type, duration_seconds, pre_anxiety_level, post_anxiety_level, notes, completed))
        conn.commit()
        log_event(username, 'cbt', 'breathing_exercise_created', f"Type: {exercise_type}, Duration: {duration_seconds}")
        conn.close()
        return jsonify({'success': True, 'message': 'Breathing exercise entry created'}), 201
    except Exception as e:
        return handle_exception(e, 'create_breathing_exercise')

@app.route('/api/cbt/breathing', methods=['GET'])
def list_breathing_exercises():
    """List all breathing exercise entries for the authenticated user"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT * FROM breathing_exercises WHERE username=? ORDER BY entry_timestamp DESC', (username,)).fetchall()
        conn.close()
        result = [dict(zip([c[0] for c in cur.description], row)) for row in rows]
        return jsonify({'entries': result}), 200
    except Exception as e:
        return handle_exception(e, 'list_breathing_exercises')

@app.route('/api/cbt/breathing/<int:entry_id>', methods=['GET'])
def get_breathing_exercise(entry_id):
    """Get a single breathing exercise entry by ID"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM breathing_exercises WHERE id=? AND username=?', (entry_id, username)).fetchone()
        conn.close()
        if not row:
            return jsonify({'error': 'Entry not found'}), 404
        result = dict(zip([c[0] for c in cur.description], row))
        return jsonify(result), 200
    except Exception as e:
        return handle_exception(e, 'get_breathing_exercise')

@app.route('/api/cbt/breathing/<int:entry_id>', methods=['PUT'])
def update_breathing_exercise(entry_id):
    """Update a breathing exercise entry"""
    try:
        data = request.json
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM breathing_exercises WHERE id=? AND username=?', (entry_id, username)).fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Entry not found'}), 404
        # Only update provided fields
        fields = ['exercise_type', 'duration_seconds', 'pre_anxiety_level', 'post_anxiety_level', 'notes', 'completed']
        updates = {k: data[k] for k in fields if k in data}
        set_clause = ', '.join([f"{k}=?" for k in updates.keys()])
        values = list(updates.values()) + [entry_id, username]
        cur.execute(f'UPDATE breathing_exercises SET {set_clause} WHERE id=? AND username=?', values)
        conn.commit()
        log_event(username, 'cbt', 'breathing_exercise_updated', f"ID: {entry_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Entry updated'}), 200
    except Exception as e:
        return handle_exception(e, 'update_breathing_exercise')

@app.route('/api/cbt/breathing/<int:entry_id>', methods=['DELETE'])
def delete_breathing_exercise(entry_id):
    """Delete a breathing exercise entry"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        cur = conn.cursor()
        row = cur.execute('SELECT * FROM breathing_exercises WHERE id=? AND username=?', (entry_id, username)).fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Entry not found'}), 404
        cur.execute('DELETE FROM breathing_exercises WHERE id=? AND username=?', (entry_id, username))
        conn.commit()
        log_event(username, 'cbt', 'breathing_exercise_deleted', f"ID: {entry_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Entry deleted'}), 200
    except Exception as e:
        return handle_exception(e, 'delete_breathing_exercise')

# ========== AI MEMORY INTEGRATION: Breathing Exercises ==========
def summarize_breathing_exercises(username, limit=3):
    """Summarize recent breathing exercise activity for AI memory/context"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        rows = cur.execute('SELECT exercise_type, duration_seconds, pre_anxiety_level, post_anxiety_level, entry_timestamp FROM breathing_exercises WHERE username=? ORDER BY entry_timestamp DESC LIMIT ?', (username, limit)).fetchall()
        conn.close()
        if not rows:
            return None
        summary = []
        for r in rows:
            summary.append(f"{r[0]} ({r[1]}s): {r[2]}→{r[3]} anxiety on {r[4][:10]}")
        return "Recent breathing exercises: " + "; ".join(summary)
    except Exception:
        return None

# Initialize database on startup
try:
    init_db()
except Exception as e:
    print(f"Database initialization: {e}")

# Initialize pet game database on startup
def init_pet_db():
    """Initialize pet game database with required table"""
    try:
        conn = get_pet_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pet (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                name TEXT, species TEXT, gender TEXT,
                hunger INTEGER DEFAULT 70, happiness INTEGER DEFAULT 70,
                energy INTEGER DEFAULT 70, hygiene INTEGER DEFAULT 80,
                coins INTEGER DEFAULT 0, xp INTEGER DEFAULT 0,
                stage TEXT DEFAULT 'Baby', adventure_end REAL DEFAULT 0,
                last_updated REAL, hat TEXT DEFAULT 'None',
                UNIQUE(username)
            )
        """)
        conn.commit()
        conn.close()
        print("Pet database initialized successfully")
    except Exception as e:
        print(f"Pet database initialization error: {e}")

try:
    init_pet_db()
except Exception as e:
    print(f"Pet database initialization: {e}")

@app.route('/')
def index():
    """Serve simple web interface"""
    return render_template('index.html')

@app.route('/api/admin/wipe')
def admin_wipe_page():
    """Serve admin database wipe page"""
    return render_template('admin-wipe.html')

@app.route('/api/debug/analytics/<clinician>', methods=['GET'])
def debug_analytics(clinician):
    """Phase 1C: Debug endpoint - PROTECTED (developer role only)"""
    try:
        # Phase 1C: Only allow developers to access debug endpoints
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verify user is a developer
        user_role = cur.execute(
            "SELECT role FROM users WHERE username=?",
            (username,)
        ).fetchone()
        
        if not user_role or user_role[0] != 'developer':
            conn.close()
            return jsonify({'error': 'Developer role required for debug endpoints'}), 403
        
        debug_info = {
            'clinician': clinician,
            'timestamp': datetime.now().isoformat()
        }
        
        # Check if clinician exists
        clinician_exists = cur.execute(
            "SELECT username, role FROM users WHERE username=?",
            (clinician,)
        ).fetchone()
        debug_info['clinician_exists'] = bool(clinician_exists)
        if clinician_exists:
            debug_info['clinician_role'] = clinician_exists[1]
        
        # Get approved patients
        patients = cur.execute("""
            SELECT u.username, u.role FROM users u
            JOIN patient_approvals pa ON u.username = pa.patient_username
            WHERE pa.clinician_username=? AND pa.status='approved'
        """, (clinician,)).fetchall()
        
        debug_info['total_patients'] = len(patients)
        debug_info['patients'] = [{'username': p[0], 'role': p[1]} for p in patients]
        
        # Get all approvals for this clinician
        all_approvals = cur.execute(
            "SELECT patient_username, status, request_date FROM patient_approvals WHERE clinician_username=?",
            (clinician,)
        ).fetchall()
        debug_info['all_approvals'] = [
            {'patient': a[0], 'status': a[1], 'date': a[2]} for a in all_approvals
        ]
        
        # If we have patients, get activity
        if patients:
            patient_usernames = [p[0] for p in patients]
            placeholders = ','.join(['?'] * len(patient_usernames))
            
            # Active patients
            active = cur.execute(f"""
                SELECT COUNT(DISTINCT username) FROM (
                    SELECT username FROM mood_logs 
                    WHERE username IN ({placeholders}) 
                    AND datetime(entrestamp) > datetime('now', '-7 days')
                    UNION
                    SELECT sender as username FROM chat_history 
                    WHERE sender IN ({placeholders}) 
                    AND datetime(timestamp) > datetime('now', '-7 days')
                )
            """, patient_usernames + patient_usernames).fetchone()[0]
            debug_info['active_patients'] = active
            
            # High risk
            high_risk = cur.execute(f"""
                SELECT COUNT(DISTINCT username) FROM alerts 
                WHERE username IN ({placeholders}) 
                AND (status IS NULL OR status != 'resolved')
            """, patient_usernames).fetchone()[0]
            debug_info['high_risk_count'] = high_risk
        
        conn.close()
        
        return jsonify(debug_info), 200
        
    except Exception as e:
        return handle_exception(e, 'debug_analytics')

@app.route('/diagnostic')
def diagnostic():
    """Diagnostic page to test JavaScript loading"""
    return render_template('diagnostic.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'healthy',
        'service': 'python-chat-bot Therapy API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/admin/wipe-database', methods=['POST'])
def admin_wipe_database():
    """ADMIN ONLY: Wipe all user data from database - requires secret key"""
    try:
        data = request.json
        admin_key = data.get('admin_key')
        
        # Check admin key (MUST be set via environment variable - no default)
        required_key = os.getenv('ADMIN_WIPE_KEY')

        if not required_key:
            return jsonify({'error': 'Admin wipe key not configured on server'}), 500

        if not admin_key or admin_key != required_key:
            return jsonify({'error': 'Unauthorized - invalid admin key'}), 403
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        print("🗑️  ADMIN: Wiping all user data from database...")
        
        tables_to_clear = [
            'users',
            'patient_approvals',
            'chat_history',
            'chat_sessions',
            'mood_logs',
            'alerts',
            'notifications',
            'clinical_scales',
            'clinician_notes',
            'cbt_records',
            'ai_memory',
            'appointments',
            'audit_logs',
            'verification_codes'
        ]
        
        results = {}
        for table in tables_to_clear:
            try:
                cur.execute(f"DELETE FROM {table}")
                count = cur.rowcount
                results[table] = f"{count} rows deleted"
                print(f"  ✓ Cleared {table}: {count} rows")
            except Exception as e:
                results[table] = f"Error: {str(e)}"
                print(f"  ⚠️  {table}: {e}")
        
        conn.commit()
        conn.close()
        
        log_event('ADMIN', 'api', 'database_wiped', 'All user data cleared')
        
        print("✅ ADMIN: Database wipe complete")
        
        return jsonify({
            'success': True,
            'message': 'Database wiped successfully',
            'results': results
        }), 200
        
    except Exception as e:
        print(f"❌ ADMIN: Database wipe error: {e}")
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/auth/send-verification', methods=['POST'])
def send_verification():
    """Send 2FA verification code during signup"""
    try:
        data = request.json
        identifier = data.get('identifier')  # email or phone
        method = data.get('method', 'email')  # 'email' or 'sms'
        
        if not identifier:
            return jsonify({'error': 'Email or phone number required'}), 400
        
        if method not in ['email', 'sms']:
            return jsonify({'error': 'Method must be email or sms'}), 400
        
        # Generate 6-digit code
        code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        
        # Store code in database with 10 minute expiration
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Clear old codes for this identifier
        cur.execute("DELETE FROM verification_codes WHERE identifier=? AND verified=0", (identifier,))
        
        # Insert new code
        expires_at = datetime.now() + timedelta(minutes=10)
        cur.execute(
            "INSERT INTO verification_codes (identifier, code, method, expires_at) VALUES (?, ?, ?, ?)",
            (identifier, code, method, expires_at)
        )
        conn.commit()
        conn.close()
        
        # Send code
        success = send_verification_code(identifier, code, method)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Verification code sent to {identifier} via {method}'
            }), 200
        else:
            return jsonify({
                'error': f'Failed to send verification code via {method}. Please try another method.'
            }), 500
            
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/auth/verify-code', methods=['POST'])
@check_rate_limit('verify_code')  # Phase 1D: Add rate limiting to prevent brute-force
def verify_code():
    """Verify 2FA code"""
    try:
        data = request.json
        identifier = data.get('identifier')
        code = data.get('code')
        
        if not identifier or not code:
            return jsonify({'error': 'Identifier and code required'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Find valid code
        result = cur.execute(
            "SELECT id, expires_at FROM verification_codes WHERE identifier=? AND code=? AND verified=0",
            (identifier, code)
        ).fetchone()
        
        if not result:
            conn.close()
            return jsonify({'error': 'Invalid verification code'}), 400
        
        code_id, expires_at = result
        
        # Check expiration
        if datetime.now() > datetime.fromisoformat(expires_at):
            conn.close()
            return jsonify({'error': 'Verification code expired. Please request a new one.'}), 400
        
        # Mark as verified
        cur.execute("UPDATE verification_codes SET verified=1 WHERE id=?", (code_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Code verified successfully'
        }), 200
        
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/auth/register', methods=['POST'])
@check_rate_limit('register')
def register():
    """Register new user - requires 2FA verification"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        pin = data.get('pin')
        email = data.get('email')
        phone = data.get('phone')
        full_name = data.get('full_name')
        dob = data.get('dob')
        verified_identifier = data.get('verified_identifier')  # The email or phone that was verified
        
        if not username or not password or not pin or not email or not phone:
            return jsonify({'error': 'All fields are required'}), 400
        
        # Check if email or phone was verified (if 2FA is enabled)
        if os.getenv('REQUIRE_2FA_SIGNUP', '0') == '1':
            if not verified_identifier:
                return jsonify({'error': 'Please verify your email or phone number first'}), 400
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check if verification exists and is valid
            verified = cur.execute(
                "SELECT id FROM verification_codes WHERE identifier=? AND verified=1 AND datetime(expires_at) > datetime('now')",
                (verified_identifier,)
            ).fetchone()
            
            conn.close()
            
            if not verified:
                return jsonify({'error': 'Verification expired or invalid. Please verify again.'}), 400
        conditions = data.get('conditions')
        clinician_id = data.get('clinician_id')  # Required for patients
        country = data.get('country', '')
        area = data.get('area', '')
        postcode = data.get('postcode', '')
        nhs_number = data.get('nhs_number', '')
        
        if not username or not password or not pin or not email or not phone:
            return jsonify({'error': 'All fields are required'}), 400
        
        if not country or not area:
            return jsonify({'error': 'Country and area are required'}), 400
        
        if not full_name:
            return jsonify({'error': 'Full name is required'}), 400
        
        if not dob:
            return jsonify({'error': 'Date of birth is required'}), 400
        
        if not conditions:
            return jsonify({'error': 'Medical conditions/diagnosis is required'}), 400

        # Validate password complexity using centralized function
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            return jsonify({'error': error_msg}), 400

        # Clinician is now optional
        if clinician_id:
            # Verify clinician exists if provided
            conn = get_db_connection()
            cur = conn.cursor()
            clinician = cur.execute(
                "SELECT username FROM users WHERE username=? AND role='clinician'",
                (clinician_id,)
            ).fetchone()
            
            if not clinician:
                conn.close()
                return jsonify({'error': 'Invalid clinician ID. Please select a valid clinician.'}), 400
        else:
            clinician = None
        
        conn = get_db_connection()
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
        
        # Hash credentials
        hashed_password = hash_password(password)
        hashed_pin = hash_pin(pin)
        
        # Create user with full profile information
        cur.execute("INSERT INTO users (username, password, pin, email, phone, full_name, dob, conditions, last_login, role, country, area, postcode, nhs_number, clinician_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                   (username, hashed_password, hashed_pin, email, phone, full_name, dob, conditions, datetime.now(), 'user', country, area, postcode, nhs_number, clinician_id))
        
        # Only create approval request if clinician is provided
        if clinician_id:
            # Create pending approval request
            cur.execute("INSERT INTO patient_approvals (patient_username, clinician_username, status) VALUES (?,?,?)",
                       (username, clinician_id, 'pending'))
            
            # Notify clinician of new patient request
            cur.execute("INSERT INTO notifications (recipient_username, message, notification_type) VALUES (?,?,?)",
                       (clinician_id, f'New patient request from {full_name} ({username})', 'patient_request'))
            
            # Notify patient that request is pending
            cur.execute("INSERT INTO notifications (recipient_username, message, notification_type) VALUES (?,?,?)",
                       (username, f'Your request to join {clinician_id} is pending approval', 'approval_pending'))
            
            log_msg = f'Registration via API, pending approval from clinician: {clinician_id}'
            success_msg = 'Account created! Your clinician will approve your request shortly.'
            pending = True
        else:
            # Notify patient that they can use the app independently
            cur.execute("INSERT INTO notifications (recipient_username, message, notification_type) VALUES (?,?,?)",
                       (username, 'Account created! You can start using Healing Space independently. You can connect with a clinician anytime.', 'account_created'))
            
            log_msg = 'Registration via API without clinician assignment'
            success_msg = 'Account created! You can start using Healing Space immediately.'
            pending = False
        
        conn.commit()
        conn.close()
        
        log_event(username, 'api', 'user_registered', log_msg)
        
        return jsonify({
            'success': True,
            'message': success_msg,
            'username': username,
            'pending_approval': pending
        }), 201
        
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/auth/login', methods=['POST'])
@check_rate_limit('login')
def login():
    """Authenticate user with 2FA PIN"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        pin = data.get('pin')  # Required for 2FA

        print(f"🔐 Login attempt for user: {username}")
        
        if not username or not password:
            print("❌ Missing username or password")
            return jsonify({'error': 'Username and password required'}), 400
        
        if not pin:
            print("❌ Missing PIN")
            return jsonify({'error': 'PIN required for 2FA authentication'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        user = cur.execute("SELECT username, password, role, pin, clinician_id FROM users WHERE username=?", (username,)).fetchone()
        
        if not user:
            print(f"❌ User not found: {username}")
            conn.close()
            return jsonify({'error': 'Invalid credentials'}), 401
        
        print(f"✓ User found: {username}, role: {user[2]}")
        
        # Verify password
        if not verify_password(user[1], password):
            print("❌ Password verification failed")
            conn.close()
            return jsonify({'error': 'Invalid credentials'}), 401
        
        print("✓ Password verified")
        
        # Verify PIN (2FA)
        stored_pin = user[3]
        if not check_pin(pin, stored_pin):
            print("❌ PIN verification failed")
            conn.close()
            return jsonify({'error': 'Invalid PIN'}), 401
        
        print("✓ PIN verified")
        
        role = user[2] or 'user'
        clinician_id = user[4]
        
        # Check disclaimer acceptance
        disclaimer_accepted = cur.execute(
            "SELECT disclaimer_accepted FROM users WHERE username=?",
            (username,)
        ).fetchone()[0]
        
        # Update last_login timestamp
        cur.execute(
            "UPDATE users SET last_login=datetime('now') WHERE username=?",
            (username,)
        )
        conn.commit()
        
        # Check approval status for patients
        approval_status = 'approved'
        clinician_name = None
        if role == 'user':
            approval = cur.execute(
                "SELECT status FROM patient_approvals WHERE patient_username=? ORDER BY request_date DESC LIMIT 1",
                (username,)
            ).fetchone()
            if approval:
                approval_status = approval[0]

            # Get clinician's name if assigned
            if clinician_id:
                clinician_info = cur.execute(
                    "SELECT username FROM users WHERE username=? AND role='clinician'",
                    (clinician_id,)
                ).fetchone()
                if clinician_info:
                    # Format clinician name nicely (capitalize, add Dr. prefix)
                    clinician_name = clinician_info[0]

        conn.close()
        
        log_event(username, 'api', 'user_login', 'Login via API with 2FA')
        
        # Set session after successful authentication (Phase 1A - SECURE)
        session.permanent = True
        session['username'] = username
        session['role'] = role
        session['clinician_id'] = clinician_id
        session['login_time'] = datetime.now().isoformat()
        
        # PHASE 2B: Generate CSRF token on successful login
        csrf_token = CSRFProtection.generate_csrf_token(username)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'username': username,
            'role': role,
            'approval_status': approval_status,
            'clinician_id': clinician_id,
            'clinician_name': clinician_name,
            'disclaimer_accepted': bool(disclaimer_accepted),
            'csrf_token': csrf_token  # NEW: Send CSRF token to client
        }), 200
        
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user and clear session"""
    try:
        username = get_authenticated_username()
        if username:
            log_event(username, 'api', 'user_logout', 'Logout via API')
        
        session.clear()
        return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
    except Exception as e:
        return handle_exception(e, 'logout')

def verify_clinician_patient_relationship(clinician_username, patient_username):
    """Phase 1B: Verify clinician is assigned to patient (FK validation).
    
    Returns: (is_valid, clinician_id)
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get clinician's ID
        clinician = cur.execute(
            "SELECT id FROM users WHERE username=? AND role='clinician'",
            (clinician_username,)
        ).fetchone()
        
        if not clinician:
            conn.close()
            return False, None
        
        clinician_id = clinician[0]
        
        # Check if clinician is assigned to patient
        patient = cur.execute(
            "SELECT clinician_id FROM users WHERE username=? AND role='user'",
            (patient_username,)
        ).fetchone()
        
        conn.close()
        
        if patient and patient[0] == clinician_id:
            return True, clinician_id
        
        return False, None
    except Exception as e:
        print(f"❌ FK validation error: {e}")
        return False, None

@app.route('/api/validate-session', methods=['POST'])
def validate_session():
    """Validate stored session data"""
    try:
        data = request.json
        username = data.get('username')
        role = data.get('role', 'user')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if user still exists and get their current role
        user = cur.execute(
            "SELECT username, role FROM users WHERE username=?",
            (username,)
        ).fetchone()
        
        conn.close()
        
        if not user:
            return jsonify({'error': 'Session invalid - user not found'}), 401
        
        # Verify role matches
        if user[1] != role:
            return jsonify({'error': 'Session invalid - role mismatch'}), 401
        
        return jsonify({
            'success': True,
            'message': 'Session valid',
            'username': username,
            'role': role
        }), 200
        
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/auth/forgot-password', methods=['POST'])
@check_rate_limit('forgot_password')
def forgot_password():
    """Send password reset email"""
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        
        print(f"📧 Password reset request for user: {username}, email: {email}")
        
        if not username or not email:
            print("❌ Missing username or email")
            return jsonify({'error': 'Username and email required'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verify user exists and email matches
        user = cur.execute(
            "SELECT email FROM users WHERE username=? AND email=?",
            (username, email)
        ).fetchone()
        
        if not user:
            print(f"⚠️  User/email combination not found (security: returning success anyway)")
            # Don't reveal if user exists for security
            conn.close()
            return jsonify({'success': True, 'message': 'If account exists, reset link sent'}), 200
        
        print(f"✓ User verified: {username}")
        
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
            email_sent = send_reset_email(email, username, reset_token)
            
            if email_sent:
                log_event(username, 'api', 'password_reset_requested', f'Reset requested for {email}')
                return jsonify({
                    'success': True,
                    'message': 'Password reset link sent to your email'
                }), 200
            else:
                # Email sending failed but token is stored
                log_event(username, 'api', 'password_reset_requested', f'Token created but email failed for {email}')
                return jsonify({
                    'success': True,
                    'message': 'Reset token created. Email service unavailable - please contact support with your username.',
                    'token': reset_token if DEBUG else None
                }), 200
                
        except Exception as email_error:
            # Email failed but token is stored - still allow reset via support
            print(f"Email error: {email_error}")
            log_event(username, 'api', 'password_reset_email_failed', str(email_error))
            return jsonify({
                'success': True,
                'message': 'Reset initiated. Please contact support if you don\'t receive an email.'
            }), 200

    except Exception as e:
        print(f"Password reset error: {e}")  # Server-side logging only
        return handle_exception(e, 'password_reset')

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
        msg['Subject'] = 'python-chat-bot - Password Reset'
        msg['From'] = from_email
        msg['To'] = to_email
        
        # Reset URL (use Railway URL or localhost)
        base_url = os.getenv('APP_URL', 'http://localhost:5000')
        reset_url = f"{base_url}/reset-password%stoken={reset_token}&username={username}"
        
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
            <p>Best regards,<br>python-chat-bot Team</p>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Password reset email sent to {to_email}")
        return True

    except Exception as e:
        print(f"❌ Error sending password reset email: {e}")
        return False


@app.route('/api/auth/confirm-reset', methods=['POST'])
def confirm_password_reset():
    """Complete password reset with token"""
    try:
        data = request.json
        username = data.get('username')
        token = data.get('token')
        new_password = data.get('new_password')

        if not username or not token or not new_password:
            return jsonify({'error': 'Username, token, and new password required'}), 400

        # Validate password strength using centralized function
        is_valid, error_msg = validate_password_strength(new_password)
        if not is_valid:
            return jsonify({'error': error_msg}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Verify token and expiry
        user = cur.execute(
            "SELECT reset_token, reset_token_expiry FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if not user or not user[0]:
            conn.close()
            return jsonify({'error': 'Invalid or expired reset token'}), 400

        stored_token = user[0]
        expiry_str = user[1]

        # Validate token matches
        if stored_token != token:
            conn.close()
            log_event(username, 'security', 'invalid_reset_token', 'Mismatched reset token attempted')
            return jsonify({'error': 'Invalid or expired reset token'}), 400

        # Validate expiry
        if expiry_str:
            try:
                expiry = datetime.strptime(expiry_str, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                expiry = datetime.strptime(expiry_str, '%Y-%m-%d %H:%M:%S')

            if datetime.now() > expiry:
                conn.close()
                return jsonify({'error': 'Reset token has expired. Please request a new one.'}), 400

        # Update password and clear reset token
        hashed_password = hash_password(new_password)
        cur.execute(
            "UPDATE users SET password=?, reset_token=NULL, reset_token_expiry=NULL WHERE username=?",
            (hashed_password, username)
        )

        # SECURITY: Invalidate all existing sessions for this user
        cur.execute("DELETE FROM sessions WHERE username=?", (username,))
        cur.execute("DELETE FROM chat_sessions WHERE username=?", (username,))

        conn.commit()
        conn.close()

        log_event(username, 'security', 'password_reset_completed', 'Password successfully reset, all sessions invalidated')

        return jsonify({
            'success': True,
            'message': 'Password has been reset successfully. Please log in with your new password.'
        }), 200

    except Exception as e:
        log_event('system', 'error', 'password_reset_error', str(e))
        print(f"Password reset confirmation error: {e}")
        return jsonify({'error': 'Password reset failed. Please try again.'}), 500


def send_verification_code(identifier, code, method='email'):
    """Send 2FA verification code via email or SMS"""
    try:
        if method == 'email':
            # Get SMTP credentials
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')
            from_email = os.getenv('FROM_EMAIL', smtp_user)
            
            if not smtp_user or not smtp_password:
                print("⚠️  SMTP not configured - skipping email verification")
                return False
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'python-chat-bot - Verification Code'
            msg['From'] = from_email
            msg['To'] = identifier
            
            html = f"""
            <html>
              <body>
                <h2>Welcome to python-chat-bot!</h2>
                <p>Your verification code is:</p>
                <h1 style="color: #667eea; font-size: 32px; letter-spacing: 5px;">{code}</h1>
                <p>This code expires in 10 minutes.</p>
                <p>If you didn't request this, please ignore this email.</p>
                <br>
                <p>Best regards,<br>python-chat-bot Team</p>
              </body>
            </html>
            """
            
            msg.attach(MIMEText(html, 'html'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Verification code sent to {identifier}")
            return True
            
        elif method == 'sms':
            # SMS via Twilio (requires TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER)
            try:
                from twilio.rest import Client
                
                account_sid = os.getenv('TWILIO_ACCOUNT_SID')
                auth_token = os.getenv('TWILIO_AUTH_TOKEN')
                from_phone = os.getenv('TWILIO_PHONE_NUMBER')
                
                if not account_sid or not auth_token or not from_phone:
                    print("⚠️  Twilio not configured - skipping SMS verification")
                    return False
                
                client = Client(account_sid, auth_token)
                message = client.messages.create(
                    body=f"Your python-chat-bot verification code is: {code}. Valid for 10 minutes.",
                    from_=from_phone,
                    to=identifier
                )
                
                print(f"✅ SMS verification code sent to {identifier}")
                return True
                
            except ImportError:
                print("⚠️  Twilio library not installed. Run: pip install twilio")
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ Error sending verification code: {e}")
        return False
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
        country = data.get('country', '')
        area = data.get('area', '')
        professional_id = data.get('professional_id', '')
        
        if not username or not password or not pin or not email or not phone:
            return jsonify({'error': 'All fields are required'}), 400
        
        if not country or not area:
            return jsonify({'error': 'Country and area are required'}), 400
        
        if not professional_id:
            return jsonify({'error': 'Professional ID number is required'}), 400

        # Validate password complexity using centralized function
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            return jsonify({'error': error_msg}), 400

        if len(pin) != 4 or not pin.isdigit():
            return jsonify({'error': 'PIN must be exactly 4 digits'}), 400
        
        hashed_password = hash_password(password)
        hashed_pin = hash_pin(pin)
        
        conn = get_db_connection()
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
            "INSERT INTO users (username, password, pin, role, full_name, email, phone, last_login, country, area, professional_id) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (username, hashed_password, hashed_pin, 'clinician', full_name, email, phone, datetime.now(), country, area, professional_id)
        )
        conn.commit()
        conn.close()
        
        log_event(username, 'api', 'clinician_registered', 'Clinician registration via API')
        
        return jsonify({'success': True, 'message': 'Clinician account created successfully'}), 201
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/auth/developer/register', methods=['POST'])
def developer_register():
    """Register single developer account (one-time setup)"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        pin = data.get('pin')
        registration_key = data.get('registration_key')

        # Verify secret key
        expected_key = os.getenv('DEVELOPER_REGISTRATION_KEY')
        if not expected_key or registration_key != expected_key:
            return jsonify({'error': 'Invalid registration key'}), 403

        # Check if developer already exists
        conn = get_db_connection()
        cur = conn.cursor()
        existing = cur.execute("SELECT username FROM users WHERE role='developer'").fetchone()
        if existing:
            conn.close()
            return jsonify({'error': 'Developer account already exists'}), 409

        # Validate password strength using centralized function (same as user/clinician registration)
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            return jsonify({'error': error_msg}), 400

        hashed_password = hash_password(password)
        hashed_pin = hash_pin(pin)

        # Create developer account
        cur.execute(
            "INSERT INTO users (username, password, pin, role, last_login) VALUES (?,?,?,?,?)",
            (username, hashed_password, hashed_pin, 'developer', datetime.now())
        )
        conn.commit()
        conn.close()

        log_event(username, 'api', 'developer_registered', 'Developer account created')
        return jsonify({'success': True, 'message': 'Developer account created'}), 201
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/auth/disclaimer/accept', methods=['POST'])
def accept_disclaimer():
    """Mark disclaimer as accepted for user"""
    try:
        data = request.json
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET disclaimer_accepted=1 WHERE username=?", (username,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# ========== DEVELOPER DASHBOARD ENDPOINTS ==========

@app.route('/api/developer/terminal/execute', methods=['POST'])
def execute_terminal():
    """Execute terminal command with restricted whitelist"""
    try:
        data = request.json
        username = data.get('username')
        command = data.get('command')

        # Verify developer role
        conn = get_db_connection()
        cur = conn.cursor()
        role = cur.execute("SELECT role FROM users WHERE username=?", (username,)).fetchone()

        if not role or role[0] != 'developer':
            conn.close()
            return jsonify({'error': 'Unauthorized - Developer access required'}), 403

        # SECURITY: Whitelist of allowed commands (no shell injection)
        import subprocess
        import shlex
        import time

        # Parse command safely
        try:
            cmd_parts = shlex.split(command)
        except ValueError as e:
            conn.close()
            return jsonify({'error': f'Invalid command syntax: {str(e)}'}), 400

        if not cmd_parts:
            conn.close()
            return jsonify({'error': 'Empty command'}), 400

        # Whitelist of allowed base commands (safe, read-only operations)
        ALLOWED_COMMANDS = {
            'ls', 'pwd', 'whoami', 'date', 'cat', 'head', 'tail', 'wc',
            'grep', 'find', 'echo', 'env', 'printenv', 'df', 'du', 'free',
            'uptime', 'ps', 'top', 'htop', 'pip', 'python', 'python3',
            'git', 'which', 'file', 'stat', 'uname', 'hostname'
        }

        base_cmd = cmd_parts[0]
        if base_cmd not in ALLOWED_COMMANDS:
            conn.close()
            return jsonify({
                'error': f'Command "{base_cmd}" not allowed. Allowed: {", ".join(sorted(ALLOWED_COMMANDS))}'
            }), 403

        # Block dangerous arguments
        BLOCKED_ARGS = {'--rm', '-rf', '--force', '--no-preserve-root', '>', '>>', '|', '&', ';', '`', '$(' }
        for arg in cmd_parts[1:]:
            for blocked in BLOCKED_ARGS:
                if blocked in arg:
                    conn.close()
                    return jsonify({'error': f'Argument contains blocked pattern: {blocked}'}), 403

        start_time = time.time()
        try:
            result = subprocess.run(
                cmd_parts,
                shell=False,  # SECURE: No shell injection possible
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.getcwd()
            )
            duration_ms = int((time.time() - start_time) * 1000)

            output = result.stdout + result.stderr
            exit_code = result.returncode

            # Log command
            cur.execute(
                "INSERT INTO dev_terminal_logs (username, command, output, exit_code, duration_ms) VALUES (?,?,?,?,?)",
                (username, command, output[:10000], exit_code, duration_ms)  # Truncate output to 10k chars
            )
            conn.commit()
            conn.close()

            return jsonify({
                'output': output,
                'exit_code': exit_code,
                'duration_ms': duration_ms
            }), 200

        except subprocess.TimeoutExpired:
            conn.close()
            return jsonify({'error': 'Command timed out (30s limit)'}), 408
        except Exception as e:
            conn.close()
            return handle_exception(e, request.endpoint or 'unknown')

    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/developer/ai/chat', methods=['POST'])
def developer_ai_chat():
    """Developer AI assistant"""
    try:
        data = request.json
        username = data.get('username')
        message = data.get('message')
        session_id = data.get('session_id', 'default')

        # Verify developer role
        conn = get_db_connection()
        cur = conn.cursor()
        role = cur.execute("SELECT role FROM users WHERE username=?", (username,)).fetchone()

        if not role or role[0] != 'developer':
            conn.close()
            return jsonify({'error': 'Unauthorized'}), 403

        # Get chat history
        history = cur.execute(
            "SELECT role, message FROM dev_ai_chats WHERE username=? AND session_id=? ORDER BY created_at DESC LIMIT 10",
            (username, session_id)
        ).fetchall()

        # Build conversation context
        messages = [
            {
                "role": "system",
                "content": """You are a technical assistant for the python-chat-bot platform developer. You help with:
- Debugging code issues in Python/Flask/JavaScript
- Writing and optimizing SQL queries
- Explaining system architecture and data flows
- Database schema questions
- API endpoint usage and troubleshooting
- Frontend UI development (HTML/CSS/JavaScript)
- Security best practices
- User support message drafting
- Performance optimization

You have full knowledge of the codebase and can provide specific advice. Be concise but thorough."""
            }
        ]

        for h in reversed(history):
            messages.append({"role": h[0], "content": h[1]})
        messages.append({"role": "user", "content": message})

        # Call Groq API
        groq_key = os.getenv('GROQ_API_KEY')
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={'Authorization': f'Bearer {groq_key}', 'Content-Type': 'application/json'},
            json={'model': 'llama-3.3-70b-versatile', 'messages': messages, 'max_tokens': 1000}
        )

        if response.status_code == 200:
            ai_response = response.json()['choices'][0]['message']['content']

            # Save to database
            cur.execute(
                "INSERT INTO dev_ai_chats (username, session_id, role, message) VALUES (?,?,?,?)",
                (username, session_id, 'user', message)
            )
            cur.execute(
                "INSERT INTO dev_ai_chats (username, session_id, role, message) VALUES (?,?,?,?)",
                (username, session_id, 'assistant', ai_response)
            )
            conn.commit()
            conn.close()

            return jsonify({'response': ai_response, 'session_id': session_id}), 200
        else:
            conn.close()
            return jsonify({'error': 'AI API error'}), 500

    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/developer/messages/send', methods=['POST'])
def send_dev_message():
    """Send message from developer/clinician/user to another user (uses new messages table - Phase 3)"""
    try:
        data = request.json
        from_username = data.get('from_username')
        to_username = data.get('to_username')
        message = data.get('message')
        subject = data.get('subject', '')

        # Validate required fields
        if not from_username or not from_username.strip():
            return jsonify({'error': 'from_username is required'}), 400
        if not to_username or not to_username.strip():
            return jsonify({'error': 'to_username is required'}), 400
        if not message or not message.strip():
            return jsonify({'error': 'message content is required'}), 400

        # Check sender exists and get role
        conn = get_db_connection()
        cur = conn.cursor()
        sender_user = cur.execute("SELECT role FROM users WHERE username=?", (from_username,)).fetchone()

        if not sender_user:
            conn.close()
            return jsonify({'error': 'Unauthorized'}), 403

        sender_role = sender_user[0]

        # Developer: can message anyone
        if sender_role == 'developer':
            if to_username == 'ALL':
                # Message all non-developer users
                users = cur.execute("SELECT username FROM users WHERE role != 'developer'").fetchall()
                for user in users:
                    recipient_username = user[0]
                    # Insert into messages table (new Phase 3 system)
                    cur.execute('''
                        INSERT INTO messages (sender_username, recipient_username, subject, content, sent_at)
                        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (from_username, recipient_username, subject if subject else None, message))
                    
                    # Send notification
                    send_notification(
                        recipient_username,
                        f"New message from {from_username}: {subject if subject else message[:50]}",
                        'dev_message'
                    )
            else:
                # Message single user
                recipient_user = cur.execute("SELECT username FROM users WHERE username=?", (to_username,)).fetchone()
                if not recipient_user:
                    conn.close()
                    return jsonify({'error': 'Recipient not found'}), 404
                
                cur.execute('''
                    INSERT INTO messages (sender_username, recipient_username, subject, content, sent_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (from_username, to_username, subject if subject else None, message))
                
                # Send notification
                send_notification(
                    to_username,
                    f"New message from {from_username}: {subject if subject else message[:50]}",
                    'dev_message'
                )
        
        # Clinician: can only message patients
        elif sender_role == 'clinician':
            recipient_user = cur.execute("SELECT role FROM users WHERE username=?", (to_username,)).fetchone()
            if not recipient_user or recipient_user[0] != 'user':
                conn.close()
                return jsonify({'error': 'Clinicians can only send messages to patients'}), 403
            
            cur.execute('''
                INSERT INTO messages (sender_username, recipient_username, subject, content, sent_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (from_username, to_username, subject if subject else None, message))
            
            # Send notification
            send_notification(
                to_username,
                f"New message from {from_username}: {subject if subject else message[:50]}",
                'dev_message'
            )
        
        # Patient: can only message developer
        elif sender_role == 'user':
            recipient_user = cur.execute("SELECT role FROM users WHERE username=?", (to_username,)).fetchone()
            if not recipient_user or recipient_user[0] != 'developer':
                conn.close()
                return jsonify({'error': 'Patients can only send messages to developers'}), 403
            
            cur.execute('''
                INSERT INTO messages (sender_username, recipient_username, subject, content, sent_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (from_username, to_username, subject if subject else None, message))
            
            # Send notification
            send_notification(
                to_username,
                f"New message from {from_username}: {subject if subject else message[:50]}",
                'dev_message'
            )
        
        else:
            conn.close()
            return jsonify({'error': 'Unauthorized'}), 403

        conn.commit()
        conn.close()

        return jsonify({'success': True}), 201

    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/developer/messages/list', methods=['GET'])
def list_dev_messages():
    """Get messages for current user (dev or patient/clinician)"""
    try:
        username = request.args.get('username')

        conn = get_db_connection()
        cur = conn.cursor()

        # Get role
        role = cur.execute("SELECT role FROM users WHERE username=?", (username,)).fetchone()

        if role and role[0] == 'developer':
            # Developer sees all messages they sent + replies
            messages = cur.execute("""
                SELECT id, from_username, to_username, message, message_type, read, parent_message_id, created_at
                FROM dev_messages
                WHERE from_username=? OR to_username=?
                ORDER BY created_at DESC
            """, (username, username)).fetchall()
        else:
            # Regular user sees messages to/from developer
            messages = cur.execute("""
                SELECT id, from_username, to_username, message, message_type, read, parent_message_id, created_at
                FROM dev_messages
                WHERE to_username=? OR from_username=?
                ORDER BY created_at DESC
            """, (username, username)).fetchall()

        conn.close()

        return jsonify({
            'messages': [
                {
                    'id': m[0],
                    'from_username': m[1],
                    'to_username': m[2],
                    'message': m[3],
                    'message_type': m[4],
                    'read': bool(m[5]),
                    'parent_message_id': m[6],
                    'created_at': m[7]
                }
                for m in messages
            ]
        }), 200

    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/developer/messages/reply', methods=['POST'])
def reply_dev_message():
    """Reply to a developer message"""
    try:
        data = request.json
        from_username = data.get('from_username')
        parent_message_id = data.get('parent_message_id')
        message = data.get('message')

        conn = get_db_connection()
        cur = conn.cursor()

        # Get original message to determine recipient
        original = cur.execute(
            "SELECT from_username, to_username FROM dev_messages WHERE id=?",
            (parent_message_id,)
        ).fetchone()

        if not original:
            conn.close()
            return jsonify({'error': 'Original message not found'}), 404

        # Determine who to send to (if user replies, send to developer; if dev replies, send to user)
        to_username = original[0] if original[1] == from_username else original[1]

        # Insert reply
        cur.execute(
            "INSERT INTO dev_messages (from_username, to_username, message, message_type, parent_message_id) VALUES (?,?,?,?,?)",
            (from_username, to_username, message, 'reply', parent_message_id)
        )
        conn.commit()
        conn.close()

        # Send notification (don't fail if this fails)
        try:
            send_notification(to_username, f"New reply from {from_username}", 'dev_message_reply')
        except:
            pass

        return jsonify({'success': True}), 200

    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/developer/stats', methods=['GET'])
def developer_stats():
    """Get system statistics"""
    try:
        username = request.args.get('username')

        # Verify developer role
        conn = get_db_connection()
        cur = conn.cursor()
        role = cur.execute("SELECT role FROM users WHERE username=?", (username,)).fetchone()

        if not role or role[0] != 'developer':
            conn.close()
            return jsonify({'error': 'Unauthorized'}), 403

        # Gather stats
        stats = {}
        stats['total_users'] = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        stats['total_patients'] = cur.execute("SELECT COUNT(*) FROM users WHERE role='user'").fetchone()[0]
        stats['total_clinicians'] = cur.execute("SELECT COUNT(*) FROM users WHERE role='clinician'").fetchone()[0]
        stats['total_developers'] = cur.execute("SELECT COUNT(*) FROM users WHERE role='developer'").fetchone()[0]
        stats['total_chats'] = cur.execute("SELECT COUNT(*) FROM chat_history").fetchone()[0]
        stats['total_mood_logs'] = cur.execute("SELECT COUNT(*) FROM mood_logs").fetchone()[0]
        stats['total_assessments'] = cur.execute("SELECT COUNT(*) FROM clinical_scales").fetchone()[0]

        # Database size
        db_size = os.path.getsize(DB_PATH) / (1024 * 1024)  # MB
        stats['database_size_mb'] = round(db_size, 2)

        conn.close()

        return jsonify(stats), 200

    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/developer/users/list', methods=['GET'])
def list_all_users():
    """List all users with filter"""
    try:
        username = request.args.get('username')
        role_filter = request.args.get('role', 'all')
        search = request.args.get('search', '')

        # Verify developer role
        conn = get_db_connection()
        cur = conn.cursor()
        role = cur.execute("SELECT role FROM users WHERE username=?", (username,)).fetchone()

        if not role or role[0] != 'developer':
            conn.close()
            return jsonify({'error': 'Unauthorized'}), 403

        # Build query (NO personal info like email for GDPR compliance)
        query = "SELECT username, role, last_login FROM users WHERE 1=1"
        params = []

        if role_filter != 'all':
            query += " AND role=?"
            params.append(role_filter)

        if search:
            query += " AND username LIKE ?"
            params.append(f'%{search}%')

        query += " ORDER BY last_login DESC"

        users = cur.execute(query, params).fetchall()
        conn.close()

        return jsonify({
            'users': [
                {
                    'username': u[0],
                    'role': u[1],
                    'last_login': u[2]
                }
                for u in users
            ]
        }), 200

    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/developer/users/delete', methods=['POST'])
def delete_user():
    """Delete a user account (GDPR-compliant deletion)"""
    try:
        data = request.json
        dev_username = data.get('username')  # Developer username
        target_username = data.get('target_username')  # User to delete

        # Verify developer role
        conn = get_db_connection()
        cur = conn.cursor()
        role = cur.execute("SELECT role FROM users WHERE username=?", (dev_username,)).fetchone()

        if not role or role[0] != 'developer':
            conn.close()
            return jsonify({'error': 'Unauthorized'}), 403

        # Prevent deleting developer account
        target_role = cur.execute("SELECT role FROM users WHERE username=?", (target_username,)).fetchone()
        if not target_role:
            conn.close()
            return jsonify({'error': 'User not found'}), 404

        if target_role[0] == 'developer':
            conn.close()
            return jsonify({'error': 'Cannot delete developer account'}), 403

        # Delete user and all associated data (GDPR right to erasure)
        # Delete chat_history by session first (chat_history doesn't have username column)
        cur.execute("DELETE FROM chat_history WHERE chat_session_id IN (SELECT id FROM chat_sessions WHERE username=?)", (target_username,))
        cur.execute("DELETE FROM chat_sessions WHERE username=?", (target_username,))
        cur.execute("DELETE FROM mood_logs WHERE username=?", (target_username,))
        cur.execute("DELETE FROM clinical_scales WHERE username=?", (target_username,))
        cur.execute("DELETE FROM gratitude_logs WHERE username=?", (target_username,))
        cur.execute("DELETE FROM cbt_records WHERE username=?", (target_username,))
        cur.execute("DELETE FROM safety_plans WHERE username=?", (target_username,))
        # Pet is in separate database, skip deletion
        cur.execute("DELETE FROM notifications WHERE recipient_username=?", (target_username,))
        cur.execute("DELETE FROM ai_memory WHERE username=?", (target_username,))
        cur.execute("DELETE FROM clinician_notes WHERE patient_username=?", (target_username,))
        cur.execute("DELETE FROM audit_logs WHERE username=? OR actor=?", (target_username, target_username))
        cur.execute("DELETE FROM alerts WHERE username=?", (target_username,))
        cur.execute("DELETE FROM appointments WHERE patient_username=? OR clinician_username=?", (target_username, target_username))
        cur.execute("DELETE FROM dev_messages WHERE from_username=? OR to_username=?", (target_username, target_username))
        cur.execute("DELETE FROM dev_ai_chats WHERE username=?", (target_username,))
        cur.execute("DELETE FROM community_posts WHERE username=?", (target_username,))
        cur.execute("DELETE FROM community_likes WHERE username=?", (target_username,))
        cur.execute("DELETE FROM community_replies WHERE username=?", (target_username,))
        cur.execute("DELETE FROM patient_approvals WHERE patient_username=? OR clinician_username=?", (target_username, target_username))
        cur.execute("DELETE FROM verification_codes WHERE identifier=?", (target_username,))
        cur.execute("DELETE FROM users WHERE username=?", (target_username,))

        conn.commit()
        conn.close()

        log_event(dev_username, 'api', 'user_deleted', f'Deleted user: {target_username}')
        return jsonify({'success': True, 'message': f'User {target_username} deleted successfully'}), 200

    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# ========== END DEVELOPER DASHBOARD ENDPOINTS ==========

@app.route('/api/clinicians/list', methods=['GET'])
def get_clinicians():
    """Get list of all clinicians for patient signup (with optional filtering)"""
    try:
        country = request.args.get('country', '')
        area = request.args.get('area', '')
        search = request.args.get('search', '')  # Search by username or full_name
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = "SELECT username, full_name, country, area FROM users WHERE role='clinician'"
        params = []
        
        if country:
            query += " AND LOWER(country) LIKE LOWER(?)"
            params.append(f"%{country}%")
        
        if area:
            query += " AND LOWER(area) LIKE LOWER(?)"
            params.append(f"%{area}%")
        
        if search:
            query += " AND (LOWER(username) LIKE LOWER(?) OR LOWER(full_name) LIKE LOWER(?))"
            params.append(f"%{search}%")
            params.append(f"%{search}%")
        
        query += " ORDER BY username"
        
        clinicians = cur.execute(query, params).fetchall()
        conn.close()
        
        return jsonify({
            'clinicians': [
                {
                    'username': c[0], 
                    'full_name': c[1] or c[0],
                    'country': c[2] or '',
                    'area': c[3] or ''
                }
                for c in clinicians
            ]
        }), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# === NOTIFICATIONS ===
@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Get notifications for user"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = get_db_connection()
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
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE notifications SET read=1 WHERE id=?", (notification_id,))
        conn.commit()
        conn.close()

        return jsonify({'success': True}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    """Delete a single notification"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM notifications WHERE id=?", (notification_id,))
        conn.commit()
        conn.close()

        return jsonify({'success': True}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/notifications/clear-read', methods=['POST'])
def clear_read_notifications():
    """Clear all read notifications for a user"""
    try:
        data = request.json
        username = data.get('username')

        if not username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM notifications WHERE recipient_username=? AND read=1", (username,))
        deleted_count = cur.rowcount
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'deleted': deleted_count}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# === PATIENT APPROVAL SYSTEM ===
@app.route('/api/approvals/pending', methods=['GET'])
def get_pending_approvals():
    """Get pending patient approval requests for clinician"""
    try:
        clinician = request.args.get('clinician')
        if not clinician:
            return jsonify({'error': 'Clinician username required'}), 400
        
        conn = get_db_connection()
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
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/approvals/<int:approval_id>/approve', methods=['POST'])
def approve_patient(approval_id):
    """Approve patient request"""
    try:
        conn = get_db_connection()
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

        # Clear any prior "approval_pending" notifications for this patient
        cur.execute(
            "UPDATE notifications SET read=1 WHERE recipient_username=? AND notification_type='approval_pending'",
            (patient_username,)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Patient approved successfully'}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/approvals/<int:approval_id>/reject', methods=['POST'])
def reject_patient(approval_id):
    """Reject patient request"""
    try:
        conn = get_db_connection()
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

        # Clear any prior "approval_pending" notifications for this patient when rejected
        cur.execute(
            "UPDATE notifications SET read=1 WHERE recipient_username=? AND notification_type='approval_pending'",
            (patient_username,)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Patient request rejected'}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

def update_ai_memory(username):
    """Update AI memory with recent user activity summary including clinician notes"""
    try:
        conn = get_db_connection()
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

        # Get CBT Dashboard tool entries
        recent_cbt_tools = cur.execute(
            "SELECT tool_type, mood_rating, notes, created_at FROM cbt_tool_entries WHERE username=? ORDER BY created_at DESC LIMIT 5",
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

        if recent_cbt_tools:
            # Format CBT tool names for readability
            tool_type_map = {
                'cognitive-distortions': 'Cognitive Distortions Quiz',
                'core-beliefs': 'Core Beliefs Worksheet',
                'thought-defusion': 'Thought Defusion Exercise',
                'if-then-coping': 'If-Then Coping Plan',
                'coping-skills': 'Coping Skills Selector',
                'self-compassion': 'Self-Compassion Letter',
                'problem-solving': 'Problem Solving Worksheet',
                'exposure-hierarchy': 'Exposure Hierarchy Builder',
                'relaxation-audio': 'Relaxation Audio',
                'urge-surfing': 'Urge Surfing Timer',
                'values-card': 'Values Card Sort',
                'strengths-inventory': 'Strengths Inventory',
                'sleep-hygiene': 'Sleep Hygiene Checklist',
                'safety-plan': 'Safety Plan Builder',
                'activity-scheduler': 'Activity Scheduler'
            }
            # Get unique tools used
            tools_used = list(set(t[0] for t in recent_cbt_tools))
            tool_names = [tool_type_map.get(t, t.replace('-', ' ').title()) for t in tools_used[:3]]
            memory_parts.append(f"CBT Tools used: {', '.join(tool_names)} ({len(recent_cbt_tools)} recent entries)")
            # Include latest mood rating if available
            latest_with_mood = next((t for t in recent_cbt_tools if t[1] is not None), None)
            if latest_with_mood:
                memory_parts.append(f"Latest CBT tool mood: {latest_with_mood[1]}/10")

        memory_summary = "; ".join(memory_parts) if memory_parts else "New user, no activity yet"
        
        # Update or insert memory
        cur.execute(
            "INSERT INTO ai_memory (username, memory_summary, last_updated) VALUES (?,?,?)",
            (username, memory_summary, datetime.now())
        )
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"AI memory update error: {e}")

def send_notification(username, message, notification_type='info'):
    """Helper function to send notification to user"""
    try:
        conn = get_db_connection()
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
        ensure_pet_table()
        conn = get_pet_db_connection()
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
@check_rate_limit('ai_chat')
def therapy_chat():
    """AI therapy chat endpoint (Phase 2A: Input validation added)"""
    try:
        data = request.json
        username = data.get('username')
        message = data.get('message')
        
        if not username or not message:
            return jsonify({'error': 'Username and message required'}), 400
        
        # PHASE 2A: Input validation
        message, msg_error = InputValidator.validate_message(message)
        if msg_error:
            return jsonify({'error': msg_error}), 400
        
        # Update AI memory before chat
        try:
            update_ai_memory(username)
        except Exception as mem_error:
            print(f"AI memory update error (non-critical): {mem_error}")
        
        # Get or create active chat session
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            active_session = cur.execute(
                "SELECT id FROM chat_sessions WHERE username=? AND is_active=1",
                (username,)
            ).fetchone()
            
            if not active_session:
                # Create default session
                cur.execute(
                    "INSERT INTO chat_sessions (username, session_name, is_active) VALUES (%s, 'Main Chat', 1) RETURNING id",
                    (username,)
                )
                conn.commit()
                chat_session_id = cur.fetchone()[0]
            else:
                chat_session_id = active_session[0]
        except Exception as session_error:
            conn.close()
            log_event(username, 'error', 'session_error', str(session_error))
            print(f"Session error: {session_error}")
            return jsonify({'error': 'Unable to create chat session. Please try again.', 'code': 'SESSION_ERROR'}), 500

        # Use TherapistAI class
        try:
            ai = TherapistAI(username)
        except Exception as ai_error:
            conn.close()
            log_event(username, 'error', 'ai_init_error', str(ai_error))
            print(f"AI initialization error: {ai_error}")
            return jsonify({'error': 'The AI service is temporarily unavailable. Please try again later.', 'code': 'AI_INIT_ERROR'}), 500
        
        # Get conversation history from current session
        try:
            history = cur.execute(
                "SELECT sender, message FROM chat_history WHERE chat_session_id=? ORDER BY timestamp DESC LIMIT 10",
                (chat_session_id,)
            ).fetchall()
        except Exception as hist_error:
            print(f"History fetch error: {hist_error}")
            history = []
        
        # Get AI memory to include in context
        try:
            memory = cur.execute(
                "SELECT memory_summary FROM ai_memory WHERE username=?",
                (username,)
            ).fetchone()
        except Exception as mem_error:
            print(f"Memory fetch error: {mem_error}")
            memory = None
        
        conn.close()
        
        # Get AI response using existing logic
        try:
            response = ai.get_response(message, history[::-1])
        except Exception as resp_error:
            log_event(username, 'error', 'ai_response_error', str(resp_error))
            print(f"AI response error: {resp_error}")
            return jsonify({
                'error': 'I apologize, but I am having trouble responding right now. Please try again.',
                'code': 'AI_RESPONSE_ERROR'
            }), 500
        
        # Save to chat history with session tracking
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get or create active session
        active_session = cur.execute(
            "SELECT id FROM chat_sessions WHERE username=? AND is_active=1",
            (username,)
        ).fetchone()
        
        if not active_session:
            cur.execute(
                "INSERT INTO chat_sessions (username, session_name, is_active) VALUES (?, 'Main Chat', 1)",
                (username,)
            )
            conn.commit()
            chat_session_id = cur.lastrowid
        else:
            chat_session_id = active_session[0]
        
        # Save messages with both session_id (for clinician access) and chat_session_id (for user organization)
        cur.execute("INSERT INTO chat_history (session_id, chat_session_id, sender, message) VALUES (?,?,?,?)",
                   (f"{username}_session", chat_session_id, "user", message))
        cur.execute("INSERT INTO chat_history (session_id, chat_session_id, sender, message) VALUES (?,?,?,?)",
                   (f"{username}_session", chat_session_id, "ai", response))
        
        # Update session last_active
        cur.execute(
            "UPDATE chat_sessions SET last_active=? WHERE id=?",
            (datetime.now(), chat_session_id)
        )
        
        conn.commit()
        conn.close()
        
        # Collect for training if user has consented
        try:
            if training_manager.check_user_consent(username):
                # Get user's mood context
                conn = get_db_connection()
                cur = conn.cursor()
                recent_mood = cur.execute(
                    "SELECT mood_val FROM mood_logs WHERE username=? ORDER BY entrestamp DESC LIMIT 1",
                    (username,)
                ).fetchone()
                conn.close()
                
                mood_context = recent_mood[0] if recent_mood else None
                
                # Collect conversation for training
                training_manager.collect_therapy_session(
                    username,
                    [
                        {'role': 'user', 'content': message},
                        {'role': 'ai', 'content': response}
                    ],
                    mood_context=mood_context
                )
                
                # Check if we should trigger background training (Railway only)
                try:
                    from training_config import get_training_config, IS_RAILWAY
                    config = get_training_config()
                    
                    if config['enable_auto_training'] and IS_RAILWAY:
                        # Check number of new messages since last training
                        conn = get_pet_db_connection()  # Use pet connection for now
                        cur = conn.cursor()
                        
                        # Get last trained ID from metrics file
                        import json
                        metrics_file = os.path.join(config['model_storage'], 'training_metrics.json')
                        last_trained_id = 0
                        if os.path.exists(metrics_file):
                            try:
                                with open(metrics_file, 'r') as f:
                                    metrics = json.load(f)
                                    last_trained_id = metrics.get('last_trained_id', 0)
                            except:
                                pass
                        
                        new_count = cur.execute(
                            "SELECT COUNT(*) FROM training_chats WHERE id > ?",
                            (last_trained_id,)
                        ).fetchone()[0]
                        conn.close()
                        
                        # Trigger training if threshold reached
                        if new_count >= config['auto_train_threshold']:
                            import threading
                            from ai_trainer import train_background_model
                            
                            def train_async():
                                print(f"🚀 Auto-triggering training ({new_count} new messages)...")
                                train_background_model(epochs=config['epochs'])
                            
                            thread = threading.Thread(target=train_async, daemon=True)
                            thread.start()
                            print(f"✅ Background training started ({new_count} new messages)")
                except Exception as e:
                    print(f"Auto-training check error: {e}")
                
        except Exception as e:
            # Don't break the chat if training collection fails
            print(f"Training data collection error: {e}")

        # Mark daily task as complete
        mark_daily_task_complete(username, 'therapy_session')

        log_event(username, 'api', 'therapy_chat', 'Chat message sent')

        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        # Log the actual error for debugging, but return a user-friendly message
        log_event('system', 'error', 'therapy_chat_error', str(e))
        print(f"Therapy chat error: {e}")
        return jsonify({
            'error': 'An unexpected error occurred. Please try again.',
            'code': 'UNEXPECTED_ERROR'
        }), 500

@app.route('/api/therapy/history', methods=['GET'])
def get_chat_history():
    """Get chat history for a user (optionally filtered by chat session)"""
    try:
        username = request.args.get('username')
        chat_session_id = request.args.get('chat_session_id')  # Optional: specific session
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        if chat_session_id:
            # Get history for specific chat session
            history = cur.execute(
                "SELECT sender, message, timestamp FROM chat_history WHERE chat_session_id=? ORDER BY timestamp ASC",
                (chat_session_id,)
            ).fetchall()
        else:
            # Get history from active session, or all history if no sessions exist yet
            active_session = cur.execute(
                "SELECT id FROM chat_sessions WHERE username=? AND is_active=1",
                (username,)
            ).fetchone()
            
            if active_session:
                history = cur.execute(
                    "SELECT sender, message, timestamp FROM chat_history WHERE chat_session_id=? ORDER BY timestamp ASC",
                    (active_session[0],)
                ).fetchall()
            else:
                # Backward compatibility: get all messages with old session_id
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
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/therapy/export', methods=['POST'])
def export_chat_history():
    """Export chat history with date range filter"""
    import csv
    import io
    from datetime import datetime
    
    try:
        data = request.json
        username = data.get('username')
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        export_format = data.get('format', 'txt')
        chat_session_id = data.get('chat_session_id')  # Optional: specific session
        
        if not username or not from_date or not to_date:
            return jsonify({'error': 'Username, from_date, and to_date required'}), 400
        
        # Convert dates to datetime objects
        from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
        to_datetime = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        if chat_session_id:
            # Export specific session
            history = cur.execute(
                """SELECT sender, message, timestamp FROM chat_history 
                   WHERE chat_session_id=? 
                   AND datetime(timestamp) BETWEEN datetime(?) AND datetime(?)
                   ORDER BY timestamp ASC""",
                (chat_session_id, from_datetime.isoformat(), to_datetime.isoformat())
            ).fetchall()
        else:
            # Export all sessions for this user
            history = cur.execute(
                """SELECT sender, message, timestamp FROM chat_history 
                   WHERE session_id=? 
                   AND datetime(timestamp) BETWEEN datetime(?) AND datetime(?)
                   ORDER BY timestamp ASC""",
                (f"{username}_session", from_datetime.isoformat(), to_datetime.isoformat())
            ).fetchall()
        
        conn.close()
        
        if export_format == 'json':
            # JSON export
            output = json.dumps([{
                'sender': h[0],
                'message': h[1],
                'timestamp': h[2]
            } for h in history], indent=2)
            
            return Response(
                output,
                mimetype='application/json',
                headers={'Content-Disposition': f'attachment; filename=chat_export_{from_date}_to_{to_date}.json'}
            )
        
        elif export_format == 'csv':
            # CSV export
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Sender', 'Message', 'Timestamp'])
            writer.writerows(history)
            
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=chat_export_{from_date}_to_{to_date}.csv'}
            )
        
        else:
            # Text export (default)
            output = f"Chat History Export for {username}\n"
            output += f"Date Range: {from_date} to {to_date}\n"
            output += "=" * 80 + "\n\n"
            
            for sender, message, timestamp in history:
                dt = datetime.fromisoformat(timestamp)
                formatted_time = dt.strftime('%Y-%m-%d %I:%M %p')
                output += f"[{formatted_time}] {sender.upper()}:\n"
                output += f"{message}\n\n"
            
            output += "=" * 80 + "\n"
            output += f"Total messages: {len(history)}\n"
            
            return Response(
                output,
                mimetype='text/plain',
                headers={'Content-Disposition': f'attachment; filename=chat_export_{from_date}_to_{to_date}.txt'}
            )
        
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/therapy/sessions', methods=['GET'])
def get_chat_sessions():
    """Get all chat sessions for a user"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create default session if none exist
        existing = cur.execute(
            "SELECT COUNT(*) FROM chat_sessions WHERE username=?",
            (username,)
        ).fetchone()[0]
        
        if existing == 0:
            cur.execute(
                "INSERT INTO chat_sessions (username, session_name, is_active) VALUES (?, ?, 1)",
                (username, "Main Chat")
            )
            conn.commit()
        
        sessions = cur.execute(
            """SELECT id, session_name, created_at, last_active, is_active,
               (SELECT COUNT(*) FROM chat_history WHERE chat_session_id = chat_sessions.id) as message_count
               FROM chat_sessions WHERE username=? ORDER BY last_active DESC""",
            (username,)
        ).fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'sessions': [{
                'id': s[0],
                'name': s[1],
                'created_at': s[2],
                'last_active': s[3],
                'is_active': s[4] == 1,
                'message_count': s[5]
            } for s in sessions]
        }), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/therapy/sessions', methods=['POST'])
def create_chat_session():
    """Create a new chat session"""
    try:
        data = request.json
        username = data.get('username')
        session_name = data.get('session_name', 'New Chat')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            # Deactivate all other sessions
            cur.execute("UPDATE chat_sessions SET is_active=0 WHERE username=?", (username,))
            
            # Create new session
            cur.execute(
                "INSERT INTO chat_sessions (username, session_name, is_active) VALUES (?, ?, 1)",
                (username, session_name)
            )
            session_id = cur.lastrowid
            conn.commit()
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'session_name': session_name
            }), 200
        except Exception as db_error:
            conn.rollback()
            raise db_error
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Create chat session error: {e}")
        return jsonify({'error': 'Failed to create chat session. Please try again.'}), 500

@app.route('/api/therapy/sessions/<int:session_id>', methods=['PUT'])
def update_chat_session(session_id):
    """Update chat session (rename or switch active)"""
    try:
        data = request.json
        username = data.get('username')
        session_name = data.get('session_name')
        make_active = data.get('make_active', False)
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verify session belongs to user
        owner = cur.execute(
            "SELECT username FROM chat_sessions WHERE id=?",
            (session_id,)
        ).fetchone()
        
        if not owner or owner[0] != username:
            conn.close()
            return jsonify({'error': 'Session not found or unauthorized'}), 404
        
        if session_name:
            cur.execute(
                "UPDATE chat_sessions SET session_name=? WHERE id=?",
                (session_name, session_id)
            )
        
        if make_active:
            # Deactivate all other sessions
            cur.execute("UPDATE chat_sessions SET is_active=0 WHERE username=?", (username,))
            # Activate this session
            cur.execute("UPDATE chat_sessions SET is_active=1, last_active=? WHERE id=?", 
                       (datetime.now(), session_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/therapy/sessions/<int:session_id>', methods=['DELETE'])
def delete_chat_session(session_id):
    """Delete a chat session and its messages"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verify session belongs to user
        owner = cur.execute(
            "SELECT username FROM chat_sessions WHERE id=?",
            (session_id,)
        ).fetchone()
        
        if not owner or owner[0] != username:
            conn.close()
            return jsonify({'error': 'Session not found or unauthorized'}), 404
        
        # Check if this is the only session
        session_count = cur.execute(
            "SELECT COUNT(*) FROM chat_sessions WHERE username=?",
            (username,)
        ).fetchone()[0]
        
        if session_count == 1:
            conn.close()
            return jsonify({'error': 'Cannot delete your only chat session'}), 400
        
        # Delete messages first (cascade)
        cur.execute("DELETE FROM chat_history WHERE chat_session_id=?", (session_id,))
        
        # Delete session
        cur.execute("DELETE FROM chat_sessions WHERE id=?", (session_id,))
        
        # If deleted session was active, activate the most recent one
        is_active = cur.execute(
            "SELECT is_active FROM chat_sessions WHERE username=? LIMIT 1",
            (username,)
        ).fetchone()
        
        if is_active and is_active[0] == 0:
            most_recent = cur.execute(
                "SELECT id FROM chat_sessions WHERE username=? ORDER BY last_active DESC LIMIT 1",
                (username,)
            ).fetchone()
            if most_recent:
                cur.execute("UPDATE chat_sessions SET is_active=1 WHERE id=?", (most_recent[0],))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

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
        conn = get_db_connection()
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
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/therapy/initialize', methods=['POST'])
def initialize_chat():
    """Initialize chat for new users - creates first AI interaction and memory bank"""
    try:
        data = request.json
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = get_db_connection()
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
            "INSERT INTO ai_memory (username, memory_summary, last_updated) VALUES (?,?,?)",
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
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/mood/log', methods=['POST'])
def log_mood():
    """Log mood entry with full tracking (Phase 2A: Input validation added)"""
    try:
        # SECURITY: Authenticate user via session
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.json
        mood_val = data.get('mood_val')
        sleep_val = data.get('sleep_val', 0)
        meds = data.get('meds', '')  # Now expects JSON array of {name, strength, quantity}
        notes = data.get('notes', '')
        water_pints = data.get('water_pints', 0)
        exercise_mins = data.get('exercise_mins', 0)
        outside_mins = data.get('outside_mins', 0)

        # INPUT VALIDATION
        if not username or mood_val is None:
            return jsonify({'error': 'Username and mood_val required'}), 400

        # PHASE 2A: Validate mood_val range (1-10)
        mood_val, mood_error = InputValidator.validate_mood(mood_val)
        if mood_error:
            return jsonify({'error': mood_error}), 400

        # PHASE 2A: Validate sleep_val (0-10 scale)
        if sleep_val is not None:
            sleep_val, sleep_error = InputValidator.validate_sleep(sleep_val)
            if sleep_error:
                return jsonify({'error': sleep_error}), 400
        else:
            sleep_val = 0

        # Validate exercise_mins (non-negative, max 1440 minutes = 24 hours)
        try:
            exercise_mins = int(exercise_mins) if exercise_mins else 0
            if exercise_mins < 0 or exercise_mins > 1440:
                return jsonify({'error': 'exercise_mins must be between 0 and 1440'}), 400
        except (ValueError, TypeError):
            exercise_mins = 0

        # Validate outside_mins (non-negative, max 1440 minutes)
        try:
            outside_mins = int(outside_mins) if outside_mins else 0
            if outside_mins < 0 or outside_mins > 1440:
                return jsonify({'error': 'outside_mins must be between 0 and 1440'}), 400
        except (ValueError, TypeError):
            outside_mins = 0

        # Validate water_pints (non-negative, max 20 pints)
        try:
            water_pints = float(water_pints) if water_pints else 0
            if water_pints < 0 or water_pints > 20:
                return jsonify({'error': 'water_pints must be between 0 and 20'}), 400
        except (ValueError, TypeError):
            water_pints = 0

        # Sanitize and limit notes length (prevent XSS and oversized input)
        if notes:
            notes = str(notes)[:2000]  # Max 2000 characters
            # Basic HTML sanitization (remove script tags)
            import re
            notes = re.sub(r'<script[^>]*>.*?</script>', '', notes, flags=re.IGNORECASE | re.DOTALL)
            notes = re.sub(r'<[^>]+>', '', notes)  # Remove all HTML tags

        conn = get_db_connection()
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

        # Mark daily task as complete
        mark_daily_task_complete(username, 'log_mood')

        log_event(username, 'api', 'mood_logged', f'Mood: {mood_val}')
        
        return jsonify({
            'success': True,
            'message': 'Mood logged successfully',
            'log_id': log_id
        }), 201
        
    except Exception as e:
        import traceback, logging
        tb = traceback.format_exc()
        logging.error(f"[log_mood] Exception: {e}\nTraceback:\n{tb}")
        print(f"[log_mood] Exception: {e}\nTraceback:\n{tb}")
        return jsonify({'error': f'Internal server error: {str(e)}', 'trace': tb}), 500

@app.route('/api/mood/history', methods=['GET'])
def mood_history():
    """Get mood history for user with all tracking data"""
    try:
        username = request.args.get('username')
        limit = request.args.get('limit', 30)
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = get_db_connection()
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
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/gratitude/log', methods=['POST'])
def log_gratitude():
    """Log gratitude entry - automatically updates AI memory"""
    try:
        data = request.json
        username = data.get('username')
        entry = data.get('entry')

        if not username or not entry:
            return jsonify({'error': 'Username and entry required'}), 400

        # INPUT VALIDATION: Length limits
        MAX_ENTRY_LENGTH = 1000
        if len(entry) > MAX_ENTRY_LENGTH:
            return jsonify({'error': f'Entry too long. Maximum {MAX_ENTRY_LENGTH} characters allowed.'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO gratitude_logs (username, entry) VALUES (?,?)", (username, entry))
        conn.commit()
        log_id = cur.lastrowid
        conn.close()
        
        # AUTO-UPDATE AI MEMORY
        update_ai_memory(username)
        
        # Reward pet for self-care activity
        reward_pet('gratitude')

        # Mark daily task as complete
        mark_daily_task_complete(username, 'practice_gratitude')

        log_event(username, 'api', 'gratitude_logged', 'Gratitude entry added, AI memory updated')
        
        return jsonify({
            'success': True,
            'message': 'Gratitude logged successfully',
            'log_id': log_id
        }), 201
        
    except Exception as e:
        import traceback, logging
        tb = traceback.format_exc()
        logging.error(f"[log_gratitude] Exception: {e}\nTraceback:\n{tb}")
        print(f"[log_gratitude] Exception: {e}\nTraceback:\n{tb}")
        return jsonify({'error': f'Internal server error: {str(e)}', 'trace': tb}), 500

# ========== CBT TOOLS API ENDPOINTS ==========

# === 1. BREATHING EXERCISES ===
@app.route('/api/cbt/breathing', methods=['GET'])
def get_breathing_exercises():
    """Get user's breathing exercise history"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        exercises = cur.execute(
            """SELECT id, exercise_type, duration_seconds, pre_anxiety_level,
                      post_anxiety_level, notes, completed, entry_timestamp
               FROM breathing_exercises WHERE username=?
               ORDER BY entry_timestamp DESC LIMIT 50""",
            (username,)
        ).fetchall()
        conn.close()

        return jsonify({
            'exercises': [{
                'id': e[0], 'exercise_type': e[1], 'duration_seconds': e[2],
                'pre_anxiety_level': e[3], 'post_anxiety_level': e[4],
                'notes': e[5], 'completed': bool(e[6]), 'timestamp': e[7]
            } for e in exercises]
        }), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/cbt/breathing', methods=['POST'])
def log_breathing_exercise():
    """Log a breathing exercise session"""
    try:
        data = request.json
        username = data.get('username')
        exercise_type = data.get('exercise_type')  # e.g., '4-7-8', 'box', 'diaphragmatic'
        duration_seconds = data.get('duration_seconds', 0)
        pre_anxiety = data.get('pre_anxiety_level')
        post_anxiety = data.get('post_anxiety_level')
        notes = data.get('notes', '')

        if not username or not exercise_type:
            return jsonify({'error': 'Username and exercise_type required'}), 400

        # Validate anxiety levels (1-10)
        if pre_anxiety and (pre_anxiety < 1 or pre_anxiety > 10):
            return jsonify({'error': 'Anxiety level must be between 1-10'}), 400
        if post_anxiety and (post_anxiety < 1 or post_anxiety > 10):
            return jsonify({'error': 'Anxiety level must be between 1-10'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO breathing_exercises
               (username, exercise_type, duration_seconds, pre_anxiety_level, post_anxiety_level, notes)
               VALUES (?,?,?,?,?,?)""",
            (username, exercise_type, duration_seconds, pre_anxiety, post_anxiety, notes[:500] if notes else None)
        )
        conn.commit()
        log_id = cur.lastrowid
        conn.close()

        update_ai_memory(username)
        reward_pet('breathing', 'cbt')

        # Mark daily task as complete
        mark_daily_task_complete(username, 'breathing_exercise')

        log_event(username, 'api', 'breathing_exercise', f'Completed {exercise_type} breathing exercise')

        return jsonify({'success': True, 'id': log_id}), 201
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# === 2. RELAXATION TECHNIQUES ===
@app.route('/api/cbt/relaxation', methods=['GET'])
def get_relaxation_sessions():
    """Get user's relaxation technique history"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        sessions = cur.execute(
            """SELECT id, technique_type, duration_minutes, effectiveness_rating,
                      body_scan_areas, notes, entry_timestamp
               FROM relaxation_techniques WHERE username=?
               ORDER BY entry_timestamp DESC LIMIT 50""",
            (username,)
        ).fetchall()
        conn.close()

        return jsonify({
            'sessions': [{
                'id': s[0], 'technique_type': s[1], 'duration_minutes': s[2],
                'effectiveness_rating': s[3], 'body_scan_areas': s[4],
                'notes': s[5], 'timestamp': s[6]
            } for s in sessions]
        }), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/cbt/relaxation', methods=['POST'])
def log_relaxation_session():
    """Log a relaxation technique session"""
    try:
        data = request.json
        username = data.get('username')
        technique_type = data.get('technique_type')  # e.g., 'pmr', 'body_scan', 'visualization', 'grounding'
        duration_minutes = data.get('duration_minutes', 0)
        effectiveness = data.get('effectiveness_rating')
        body_areas = data.get('body_scan_areas', '')
        notes = data.get('notes', '')

        if not username or not technique_type:
            return jsonify({'error': 'Username and technique_type required'}), 400

        if effectiveness and (effectiveness < 1 or effectiveness > 10):
            return jsonify({'error': 'Effectiveness rating must be between 1-10'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO relaxation_techniques
               (username, technique_type, duration_minutes, effectiveness_rating, body_scan_areas, notes)
               VALUES (?,?,?,?,?,?)""",
            (username, technique_type, duration_minutes, effectiveness, body_areas[:200] if body_areas else None, notes[:500] if notes else None)
        )
        conn.commit()
        log_id = cur.lastrowid
        conn.close()

        update_ai_memory(username)
        reward_pet('relaxation', 'cbt')
        log_event(username, 'api', 'relaxation_session', f'Completed {technique_type} relaxation')

        return jsonify({'success': True, 'id': log_id}), 201
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# === 3. SLEEP DIARY ===
@app.route('/api/cbt/sleep-diary', methods=['GET'])
def get_sleep_diary_list():
    """Get user's sleep diary entries"""
    try:
        username = request.args.get('username')
        days = request.args.get('days', 30, type=int)
        if not username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        entries = cur.execute(
            """SELECT id, sleep_date, bedtime, wake_time, time_to_fall_asleep,
                      times_woken, total_sleep_hours, sleep_quality, dreams_nightmares,
                      factors_affecting, morning_mood, notes, entry_timestamp
               FROM sleep_diary WHERE username=?
               ORDER BY sleep_date DESC LIMIT ?""",
            (username, days)
        ).fetchall()
        conn.close()

        return jsonify({
            'entries': [{
                'id': e[0], 'sleep_date': e[1], 'bedtime': e[2], 'wake_time': e[3],
                'time_to_fall_asleep': e[4], 'times_woken': e[5], 'total_sleep_hours': e[6],
                'sleep_quality': e[7], 'dreams_nightmares': e[8], 'factors_affecting': e[9],
                'morning_mood': e[10], 'notes': e[11], 'timestamp': e[12]
            } for e in entries]
        }), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/cbt/sleep-diary', methods=['POST'])
def log_sleep_diary():
    """Log a sleep diary entry"""
    try:
        data = request.json
        username = data.get('username')
        sleep_date = data.get('sleep_date')
        bedtime = data.get('bedtime')
        wake_time = data.get('wake_time')
        time_to_fall_asleep = data.get('time_to_fall_asleep')
        times_woken = data.get('times_woken', 0)
        total_sleep_hours = data.get('total_sleep_hours')
        sleep_quality = data.get('sleep_quality')
        dreams = data.get('dreams_nightmares', '')
        factors = data.get('factors_affecting', '')
        morning_mood = data.get('morning_mood')
        notes = data.get('notes', '')

        if not username or not sleep_date:
            return jsonify({'error': 'Username and sleep_date required'}), 400

        if sleep_quality and (sleep_quality < 1 or sleep_quality > 10):
            return jsonify({'error': 'Sleep quality must be between 1-10'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO sleep_diary
               (username, sleep_date, bedtime, wake_time, time_to_fall_asleep, times_woken,
                total_sleep_hours, sleep_quality, dreams_nightmares, factors_affecting, morning_mood, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (username, sleep_date, bedtime, wake_time, time_to_fall_asleep, times_woken,
             total_sleep_hours, sleep_quality, dreams[:500] if dreams else None,
             factors[:500] if factors else None, morning_mood, notes[:500] if notes else None)
        )
        conn.commit()
        log_id = cur.lastrowid
        conn.close()

        update_ai_memory(username)
        reward_pet('sleep_diary', 'cbt')
        log_event(username, 'api', 'sleep_diary', f'Logged sleep for {sleep_date}')

        return jsonify({'success': True, 'id': log_id}), 201
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# === 4. CORE BELIEF WORKSHEET ===
@app.route('/api/cbt/core-beliefs', methods=['GET'])
def get_core_beliefs():
    """Get user's core beliefs"""
    try:
        username = request.args.get('username')
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        if not username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        query = """SELECT id, old_belief, belief_origin, evidence_for, evidence_against,
                          new_balanced_belief, belief_strength_before, belief_strength_after,
                          is_active, entry_timestamp, last_reviewed
                   FROM core_beliefs WHERE username=?"""
        if active_only:
            query += " AND is_active=1"
        query += " ORDER BY entry_timestamp DESC"

        beliefs = cur.execute(query, (username,)).fetchall()
        conn.close()

        return jsonify({
            'beliefs': [{
                'id': b[0], 'old_belief': b[1], 'belief_origin': b[2],
                'evidence_for': b[3], 'evidence_against': b[4], 'new_balanced_belief': b[5],
                'belief_strength_before': b[6], 'belief_strength_after': b[7],
                'is_active': bool(b[8]), 'timestamp': b[9], 'last_reviewed': b[10]
            } for b in beliefs]
        }), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/cbt/core-beliefs', methods=['POST'])
def create_core_belief_alt():
    """Create a new core belief worksheet entry (alternate endpoint)"""
    try:
        data = request.json
        username = data.get('username')
        old_belief = data.get('old_belief')
        belief_origin = data.get('belief_origin', '')
        evidence_for = data.get('evidence_for', '')
        evidence_against = data.get('evidence_against', '')
        new_belief = data.get('new_balanced_belief', '')
        strength_before = data.get('belief_strength_before')
        strength_after = data.get('belief_strength_after')

        if not username or not old_belief:
            return jsonify({'error': 'Username and old_belief required'}), 400

        # Validate strength (0-100%)
        if strength_before and (strength_before < 0 or strength_before > 100):
            return jsonify({'error': 'Belief strength must be between 0-100'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO core_beliefs
               (username, old_belief, belief_origin, evidence_for, evidence_against,
                new_balanced_belief, belief_strength_before, belief_strength_after)
               VALUES (?,?,?,?,?,?,?,?)""",
            (username, old_belief[:500], belief_origin[:500] if belief_origin else None,
             evidence_for[:1000] if evidence_for else None, evidence_against[:1000] if evidence_against else None,
             new_belief[:500] if new_belief else None, strength_before, strength_after)
        )
        conn.commit()
        log_id = cur.lastrowid
        conn.close()

        update_ai_memory(username)
        reward_pet('core_belief', 'cbt')
        log_event(username, 'api', 'core_belief', 'Created core belief worksheet')

        return jsonify({'success': True, 'id': log_id}), 201
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# === 5. EXPOSURE HIERARCHY ===
# Note: update_core_belief duplicate removed (defined earlier at line ~1017)
@app.route('/api/cbt/exposure', methods=['GET'])
def get_exposure_hierarchy_list():
    """Get user's exposure hierarchy (list all)"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        exposures = cur.execute(
            """SELECT id, fear_situation, initial_suds, target_suds, hierarchy_rank, status, entry_timestamp
               FROM exposure_hierarchy WHERE username=?
               ORDER BY hierarchy_rank ASC""",
            (username,)
        ).fetchall()

        # Get attempts for each exposure
        result = []
        for exp in exposures:
            attempts = cur.execute(
                """SELECT id, pre_suds, peak_suds, post_suds, duration_minutes,
                          coping_strategies_used, notes, attempt_timestamp
                   FROM exposure_attempts WHERE exposure_id=? AND username=?
                   ORDER BY attempt_timestamp DESC""",
                (exp[0], username)
            ).fetchall()

            result.append({
                'id': exp[0], 'fear_situation': exp[1], 'initial_suds': exp[2],
                'target_suds': exp[3], 'hierarchy_rank': exp[4], 'status': exp[5],
                'timestamp': exp[6],
                'attempts': [{
                    'id': a[0], 'pre_suds': a[1], 'peak_suds': a[2], 'post_suds': a[3],
                    'duration_minutes': a[4], 'coping_strategies': a[5], 'notes': a[6],
                    'timestamp': a[7]
                } for a in attempts]
            })

        conn.close()
        return jsonify({'exposures': result}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/cbt/exposure', methods=['POST'])
def create_exposure_item():
    """Add an item to exposure hierarchy"""
    try:
        data = request.json
        username = data.get('username')
        fear_situation = data.get('fear_situation')
        initial_suds = data.get('initial_suds')  # Subjective Units of Distress Scale (0-100)
        target_suds = data.get('target_suds', 20)
        hierarchy_rank = data.get('hierarchy_rank')

        if not username or not fear_situation:
            return jsonify({'error': 'Username and fear_situation required'}), 400

        if initial_suds and (initial_suds < 0 or initial_suds > 100):
            return jsonify({'error': 'SUDS must be between 0-100'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO exposure_hierarchy
               (username, fear_situation, initial_suds, target_suds, hierarchy_rank)
               VALUES (?,?,?,?,?)""",
            (username, fear_situation[:500], initial_suds, target_suds, hierarchy_rank)
        )
        conn.commit()
        log_id = cur.lastrowid
        conn.close()

        update_ai_memory(username)
        log_event(username, 'api', 'exposure_hierarchy', 'Added exposure item')

        return jsonify({'success': True, 'id': log_id}), 201
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/cbt/exposure/<int:exposure_id>/attempt', methods=['POST'])
def log_exposure_attempt(exposure_id):
    """Log an exposure attempt"""
    try:
        data = request.json
        username = data.get('username')
        pre_suds = data.get('pre_suds')
        peak_suds = data.get('peak_suds')
        post_suds = data.get('post_suds')
        duration = data.get('duration_minutes')
        coping_strategies = data.get('coping_strategies_used', '')
        notes = data.get('notes', '')

        if not username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Verify exposure exists and belongs to user
        exposure = cur.execute(
            "SELECT id FROM exposure_hierarchy WHERE id=? AND username=?", (exposure_id, username)
        ).fetchone()
        if not exposure:
            conn.close()
            return jsonify({'error': 'Exposure item not found'}), 404

        cur.execute(
            """INSERT INTO exposure_attempts
               (exposure_id, username, pre_suds, peak_suds, post_suds, duration_minutes, coping_strategies_used, notes)
               VALUES (?,?,?,?,?,?,?,?)""",
            (exposure_id, username, pre_suds, peak_suds, post_suds, duration,
             coping_strategies[:500] if coping_strategies else None, notes[:500] if notes else None)
        )

        # Update exposure status if post_suds meets target
        if post_suds is not None:
            target = cur.execute("SELECT target_suds FROM exposure_hierarchy WHERE id=?", (exposure_id,)).fetchone()
            if target and post_suds <= target[0]:
                cur.execute("UPDATE exposure_hierarchy SET status='completed' WHERE id=?", (exposure_id,))
            else:
                cur.execute("UPDATE exposure_hierarchy SET status='in_progress' WHERE id=?", (exposure_id,))

        conn.commit()
        log_id = cur.lastrowid
        conn.close()

        update_ai_memory(username)
        reward_pet('exposure', 'cbt')
        log_event(username, 'api', 'exposure_attempt', f'Completed exposure attempt for item {exposure_id}')

        return jsonify({'success': True, 'id': log_id}), 201
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# === 6. PROBLEM-SOLVING WORKSHEET ===
@app.route('/api/cbt/problem-solving', methods=['GET'])
def get_problem_solving_list():
    """Get user's problem-solving worksheets (list all)"""
    try:
        username = request.args.get('username')
        status = request.args.get('status')  # 'in_progress', 'completed', or None for all
        if not username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        query = """SELECT id, problem_description, problem_importance, brainstormed_solutions,
                          chosen_solution, action_steps, outcome, status, entry_timestamp, completed_timestamp
                   FROM problem_solving WHERE username=?"""
        params = [username]
        if status:
            query += " AND status=?"
            params.append(status)
        query += " ORDER BY entry_timestamp DESC"

        problems = cur.execute(query, params).fetchall()
        conn.close()

        return jsonify({
            'problems': [{
                'id': p[0], 'problem_description': p[1], 'problem_importance': p[2],
                'brainstormed_solutions': p[3], 'chosen_solution': p[4], 'action_steps': p[5],
                'outcome': p[6], 'status': p[7], 'timestamp': p[8], 'completed_timestamp': p[9]
            } for p in problems]
        }), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# Note: update_problem_solving duplicate removed (defined earlier at line ~718)

# === 7. COPING CARDS ===
@app.route('/api/cbt/coping-cards', methods=['GET'])
def get_coping_cards():
    """Get user's coping cards"""
    try:
        username = request.args.get('username')
        favorites_only = request.args.get('favorites', 'false').lower() == 'true'
        if not username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        query = """SELECT id, card_title, situation_trigger, unhelpful_thought,
                          helpful_response, coping_strategies, is_favorite, times_used,
                          entry_timestamp, last_used
                   FROM coping_cards WHERE username=?"""
        if favorites_only:
            query += " AND is_favorite=1"
        query += " ORDER BY times_used DESC, entry_timestamp DESC"

        cards = cur.execute(query, (username,)).fetchall()
        conn.close()

        return jsonify({
            'cards': [{
                'id': c[0], 'card_title': c[1], 'situation_trigger': c[2],
                'unhelpful_thought': c[3], 'helpful_response': c[4],
                'coping_strategies': c[5], 'is_favorite': bool(c[6]),
                'times_used': c[7], 'timestamp': c[8], 'last_used': c[9]
            } for c in cards]
        }), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/cbt/coping-cards', methods=['POST'])
def create_coping_card_alt():
    """Create a new coping card (alternate endpoint)"""
    try:
        data = request.json
        username = data.get('username')
        title = data.get('card_title')
        trigger = data.get('situation_trigger', '')
        unhelpful = data.get('unhelpful_thought', '')
        helpful = data.get('helpful_response', '')
        strategies = data.get('coping_strategies', '')

        if not username or not title:
            return jsonify({'error': 'Username and card_title required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO coping_cards
               (username, card_title, situation_trigger, unhelpful_thought, helpful_response, coping_strategies)
               VALUES (?,?,?,?,?,?)""",
            (username, title[:100], trigger[:500] if trigger else None,
             unhelpful[:500] if unhelpful else None, helpful[:500] if helpful else None,
             strategies[:1000] if strategies else None)
        )
        conn.commit()
        log_id = cur.lastrowid
        conn.close()

        update_ai_memory(username)
        reward_pet('coping_card', 'cbt')
        log_event(username, 'api', 'coping_card', 'Created coping card')

        return jsonify({'success': True, 'id': log_id}), 201
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/cbt/coping-cards/<int:card_id>/use', methods=['POST'])
def use_coping_card(card_id):
    """Mark a coping card as used (increment counter)"""
    try:
        data = request.json
        username = data.get('username')

        if not username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Verify ownership and update
        result = cur.execute(
            """UPDATE coping_cards SET times_used = times_used + 1, last_used = CURRENT_TIMESTAMP
               WHERE id=? AND username=?""",
            (card_id, username)
        )

        if cur.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Card not found'}), 404

        conn.commit()
        conn.close()

        log_event(username, 'api', 'coping_card_used', f'Used coping card {card_id}')
        return jsonify({'success': True}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/cbt/coping-cards/<int:card_id>', methods=['PUT'])
def update_coping_card_alt(card_id):
    """Update a coping card (alternate endpoint)"""
    try:
        data = request.json
        username = data.get('username')

        if not username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        updates = []
        values = []
        for field in ['card_title', 'situation_trigger', 'unhelpful_thought',
                      'helpful_response', 'coping_strategies', 'is_favorite']:
            if field in data:
                updates.append(f"{field}=?")
                values.append(data[field])

        if updates:
            values.append(card_id)
            values.append(username)
            cur.execute(f"UPDATE coping_cards SET {', '.join(updates)} WHERE id=? AND username=?", values)
            conn.commit()

        conn.close()
        return jsonify({'success': True}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/cbt/coping-cards/<int:card_id>', methods=['DELETE'])
def delete_coping_card_alt(card_id):
    """Delete a coping card (alternate endpoint)"""
    try:
        data = request.json
        username = data.get('username')

        if not username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM coping_cards WHERE id=? AND username=?", (card_id, username))

        if cur.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Card not found'}), 404

        conn.commit()
        conn.close()

        log_event(username, 'api', 'coping_card_deleted', f'Deleted coping card {card_id}')
        return jsonify({'success': True}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# === 8. SELF-COMPASSION JOURNAL ===
@app.route('/api/cbt/self-compassion', methods=['GET'])
def get_self_compassion_entries():
    """Get user's self-compassion journal entries"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        entries = cur.execute(
            """SELECT id, difficult_situation, self_critical_thoughts, common_humanity,
                      kind_response, self_care_action, mood_before, mood_after, entry_timestamp
               FROM self_compassion_journal WHERE username=?
               ORDER BY entry_timestamp DESC LIMIT 50""",
            (username,)
        ).fetchall()
        conn.close()

        return jsonify({
            'entries': [{
                'id': e[0], 'difficult_situation': e[1], 'self_critical_thoughts': e[2],
                'common_humanity': e[3], 'kind_response': e[4], 'self_care_action': e[5],
                'mood_before': e[6], 'mood_after': e[7], 'timestamp': e[8]
            } for e in entries]
        }), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/cbt/self-compassion', methods=['POST'])
def log_self_compassion():
    """Log a self-compassion journal entry"""
    try:
        data = request.json
        username = data.get('username')
        situation = data.get('difficult_situation')
        critical_thoughts = data.get('self_critical_thoughts', '')
        common_humanity = data.get('common_humanity', '')
        kind_response = data.get('kind_response', '')
        self_care = data.get('self_care_action', '')
        mood_before = data.get('mood_before')
        mood_after = data.get('mood_after')

        if not username or not situation:
            return jsonify({'error': 'Username and difficult_situation required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO self_compassion_journal
               (username, difficult_situation, self_critical_thoughts, common_humanity,
                kind_response, self_care_action, mood_before, mood_after)
               VALUES (?,?,?,?,?,?,?,?)""",
            (username, situation[:1000], critical_thoughts[:1000] if critical_thoughts else None,
             common_humanity[:1000] if common_humanity else None, kind_response[:1000] if kind_response else None,
             self_care[:500] if self_care else None, mood_before, mood_after)
        )
        conn.commit()
        log_id = cur.lastrowid
        conn.close()

        update_ai_memory(username)
        reward_pet('self_compassion', 'cbt')
        log_event(username, 'api', 'self_compassion', 'Logged self-compassion journal entry')

        return jsonify({'success': True, 'id': log_id}), 201
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# === 9. VALUES CLARIFICATION ===
@app.route('/api/cbt/values', methods=['GET'])
def get_values():
    """Get user's values"""
    try:
        username = request.args.get('username')
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        if not username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        query = """SELECT id, value_name, value_description, importance_rating,
                          current_alignment, life_area, related_goals, is_active,
                          entry_timestamp, last_reviewed
                   FROM values_clarification WHERE username=?"""
        if active_only:
            query += " AND is_active=1"
        query += " ORDER BY importance_rating DESC"

        values = cur.execute(query, (username,)).fetchall()
        conn.close()

        return jsonify({
            'values': [{
                'id': v[0], 'value_name': v[1], 'value_description': v[2],
                'importance_rating': v[3], 'current_alignment': v[4],
                'life_area': v[5], 'related_goals': v[6], 'is_active': bool(v[7]),
                'timestamp': v[8], 'last_reviewed': v[9]
            } for v in values]
        }), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# Note: update_value duplicate removed (defined earlier at line ~335)

# === 10. GOAL SETTING AND TRACKING ===
@app.route('/api/cbt/goals', methods=['GET'])
def get_goals():
    """Get user's goals with milestones and check-ins"""
    try:
        username = request.args.get('username')
        status = request.args.get('status')  # 'active', 'completed', 'abandoned'
        if not username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        query = """SELECT id, goal_title, goal_description, goal_type, target_date,
                          related_value_id, status, progress_percentage, entry_timestamp, completed_timestamp
                   FROM goals WHERE username=?"""
        params = [username]
        if status:
            query += " AND status=?"
            params.append(status)
        query += " ORDER BY entry_timestamp DESC"

        goals = cur.execute(query, params).fetchall()

        result = []
        for goal in goals:
            # Get milestones
            milestones = cur.execute(
                """SELECT id, milestone_title, milestone_description, target_date,
                          is_completed, completed_timestamp, entry_timestamp
                   FROM goal_milestones WHERE goal_id=? AND username=?
                   ORDER BY target_date""",
                (goal[0], username)
            ).fetchall()

            # Get recent check-ins
            checkins = cur.execute(
                """SELECT id, progress_notes, obstacles, next_steps, motivation_level, checkin_timestamp
                   FROM goal_checkins WHERE goal_id=? AND username=?
                   ORDER BY checkin_timestamp DESC LIMIT 5""",
                (goal[0], username)
            ).fetchall()

            # Get related value name if exists
            value_name = None
            if goal[5]:
                value = cur.execute(
                    "SELECT value_name FROM values_clarification WHERE id=?", (goal[5],)
                ).fetchone()
                value_name = value[0] if value else None

            result.append({
                'id': goal[0], 'goal_title': goal[1], 'goal_description': goal[2],
                'goal_type': goal[3], 'target_date': goal[4], 'related_value_id': goal[5],
                'related_value_name': value_name, 'status': goal[6],
                'progress_percentage': goal[7], 'timestamp': goal[8], 'completed_timestamp': goal[9],
                'milestones': [{
                    'id': m[0], 'title': m[1], 'description': m[2], 'target_date': m[3],
                    'is_completed': bool(m[4]), 'completed_timestamp': m[5], 'timestamp': m[6]
                } for m in milestones],
                'checkins': [{
                    'id': c[0], 'progress_notes': c[1], 'obstacles': c[2],
                    'next_steps': c[3], 'motivation_level': c[4], 'timestamp': c[5]
                } for c in checkins]
            })

        conn.close()
        return jsonify({'goals': result}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# Note: update_goal duplicate removed (defined earlier at line ~130)

@app.route('/api/cbt/goals/<int:goal_id>/milestone', methods=['POST'])
def add_goal_milestone(goal_id):
    """Add a milestone to a goal"""
    try:
        data = request.json
        username = data.get('username')
        title = data.get('milestone_title')
        description = data.get('milestone_description', '')
        target_date = data.get('target_date')

        if not username or not title:
            return jsonify({'error': 'Username and milestone_title required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Verify goal ownership
        goal = cur.execute(
            "SELECT id FROM goals WHERE id=? AND username=?", (goal_id, username)
        ).fetchone()
        if not goal:
            conn.close()
            return jsonify({'error': 'Goal not found'}), 404

        cur.execute(
            """INSERT INTO goal_milestones
               (goal_id, username, milestone_title, milestone_description, target_date)
               VALUES (?,?,?,?,?)""",
            (goal_id, username, title[:200], description[:500] if description else None, target_date)
        )
        conn.commit()
        log_id = cur.lastrowid
        conn.close()

        log_event(username, 'api', 'milestone_added', f'Added milestone to goal {goal_id}')
        return jsonify({'success': True, 'id': log_id}), 201
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/cbt/goals/<int:goal_id>/milestone/<int:milestone_id>', methods=['PUT'])
def update_milestone(goal_id, milestone_id):
    """Update a milestone (including marking as complete)"""
    try:
        data = request.json
        username = data.get('username')

        if not username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        updates = []
        values = []
        for field in ['milestone_title', 'milestone_description', 'target_date', 'is_completed']:
            if field in data:
                updates.append(f"{field}=?")
                values.append(data[field])

        # Set completed_timestamp if marking as complete
        if data.get('is_completed'):
            updates.append("completed_timestamp=CURRENT_TIMESTAMP")

        if updates:
            values.append(milestone_id)
            values.append(goal_id)
            values.append(username)
            cur.execute(
                f"UPDATE goal_milestones SET {', '.join(updates)} WHERE id=? AND goal_id=? AND username=?",
                values
            )
            conn.commit()

            # Update goal progress based on completed milestones
            total = cur.execute(
                "SELECT COUNT(*) FROM goal_milestones WHERE goal_id=?", (goal_id,)
            ).fetchone()[0]
            completed = cur.execute(
                "SELECT COUNT(*) FROM goal_milestones WHERE goal_id=? AND is_completed=1", (goal_id,)
            ).fetchone()[0]

            if total > 0:
                progress = int((completed / total) * 100)
                cur.execute("UPDATE goals SET progress_percentage=? WHERE id=?", (progress, goal_id))
                conn.commit()

        conn.close()
        update_ai_memory(username)

        if data.get('is_completed'):
            reward_pet('milestone', 'cbt')
            log_event(username, 'api', 'milestone_completed', f'Completed milestone {milestone_id}')

        return jsonify({'success': True}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/cbt/goals/<int:goal_id>/checkin', methods=['POST'])
def add_goal_checkin(goal_id):
    """Add a check-in to a goal"""
    try:
        data = request.json
        username = data.get('username')
        progress_notes = data.get('progress_notes', '')
        obstacles = data.get('obstacles', '')
        next_steps = data.get('next_steps', '')
        motivation_level = data.get('motivation_level')

        if not username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Verify goal ownership
        goal = cur.execute(
            "SELECT id FROM goals WHERE id=? AND username=?", (goal_id, username)
        ).fetchone()
        if not goal:
            conn.close()
            return jsonify({'error': 'Goal not found'}), 404

        cur.execute(
            """INSERT INTO goal_checkins
               (goal_id, username, progress_notes, obstacles, next_steps, motivation_level)
               VALUES (?,?,?,?,?,?)""",
            (goal_id, username, progress_notes[:1000] if progress_notes else None,
             obstacles[:500] if obstacles else None, next_steps[:500] if next_steps else None,
             motivation_level)
        )
        conn.commit()
        log_id = cur.lastrowid
        conn.close()

        update_ai_memory(username)
        reward_pet('checkin', 'cbt')
        log_event(username, 'api', 'goal_checkin', f'Added check-in to goal {goal_id}')

        return jsonify({'success': True, 'id': log_id}), 201
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# === CBT TOOLS SUMMARY ENDPOINT ===
@app.route('/api/cbt/summary', methods=['GET'])
def get_cbt_summary():
    """Get a summary of all CBT tool usage for a user"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        summary = {}

        # Breathing exercises
        breathing = cur.execute(
            "SELECT COUNT(*), AVG(post_anxiety_level - pre_anxiety_level) FROM breathing_exercises WHERE username=?",
            (username,)
        ).fetchone()
        summary['breathing_exercises'] = {'total': breathing[0], 'avg_anxiety_reduction': round(breathing[1] or 0, 1)}

        # Relaxation techniques
        relaxation = cur.execute(
            "SELECT COUNT(*), AVG(effectiveness_rating) FROM relaxation_techniques WHERE username=?",
            (username,)
        ).fetchone()
        summary['relaxation_techniques'] = {'total': relaxation[0], 'avg_effectiveness': round(relaxation[1] or 0, 1)}

        # Sleep diary
        sleep = cur.execute(
            "SELECT COUNT(*), AVG(sleep_quality), AVG(total_sleep_hours) FROM sleep_diary WHERE username=?",
            (username,)
        ).fetchone()
        summary['sleep_diary'] = {'total': sleep[0], 'avg_quality': round(sleep[1] or 0, 1), 'avg_hours': round(sleep[2] or 0, 1)}

        # Core beliefs
        beliefs = cur.execute(
            "SELECT COUNT(*) FROM core_beliefs WHERE username=? AND is_active=1",
            (username,)
        ).fetchone()
        summary['core_beliefs'] = {'active': beliefs[0]}

        # Exposure hierarchy
        exposures = cur.execute(
            """SELECT COUNT(*), SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END)
               FROM exposure_hierarchy WHERE username=?""",
            (username,)
        ).fetchone()
        summary['exposure_hierarchy'] = {'total': exposures[0], 'completed': exposures[1] or 0}

        # Problem-solving
        problems = cur.execute(
            """SELECT COUNT(*), SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END)
               FROM problem_solving WHERE username=?""",
            (username,)
        ).fetchone()
        summary['problem_solving'] = {'total': problems[0], 'completed': problems[1] or 0}

        # Coping cards
        cards = cur.execute(
            "SELECT COUNT(*), SUM(times_used) FROM coping_cards WHERE username=?",
            (username,)
        ).fetchone()
        summary['coping_cards'] = {'total': cards[0], 'total_uses': cards[1] or 0}

        # Self-compassion
        compassion = cur.execute(
            "SELECT COUNT(*), AVG(mood_after - mood_before) FROM self_compassion_journal WHERE username=?",
            (username,)
        ).fetchone()
        summary['self_compassion'] = {'total': compassion[0], 'avg_mood_improvement': round(compassion[1] or 0, 1)}

        # Values
        values = cur.execute(
            "SELECT COUNT(*), AVG(current_alignment) FROM values_clarification WHERE username=? AND is_active=1",
            (username,)
        ).fetchone()
        summary['values'] = {'total': values[0], 'avg_alignment': round(values[1] or 0, 1)}

        # Goals
        goals = cur.execute(
            """SELECT COUNT(*), SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END), AVG(progress_percentage)
               FROM goals WHERE username=?""",
            (username,)
        ).fetchone()
        summary['goals'] = {'total': goals[0], 'completed': goals[1] or 0, 'avg_progress': round(goals[2] or 0, 1)}

        conn.close()
        return jsonify({'summary': summary}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/export/fhir', methods=['GET'])
def export_fhir():
    """Export user data in FHIR format"""
    try:
        username = request.args.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        # Use existing FHIR export function. Only sign if ENCRYPTION_KEY is available.
        sign = bool(getattr(fhir_export, 'ENCRYPTION_KEY', None))
        bundle = fhir_export.export_patient_fhir(username, sign_bundle=sign)
        
        log_event(username, 'api', 'fhir_export', 'FHIR data exported via API')
        
        return jsonify({
            'success': True,
            'bundle': json.loads(bundle)
        }), 200
        
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

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
        return handle_exception(e, request.endpoint or 'unknown')

# ===== PET GAME ENDPOINTS =====

def verify_pet_user(username):
    """SECURITY: Verify username exists in main database before allowing pet operations"""
    if not username:
        return False, "Username required"
    conn = get_db_connection()
    cur = conn.cursor()
    user = cur.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    if not user:
        return False, "User not found"
    return True, None

@app.route('/api/pet/status', methods=['GET'])
def pet_status():
    """Get pet status"""
    try:
        username = request.args.get('username')
        # SECURITY: Verify user exists
        valid, error = verify_pet_user(username)
        if not valid:
            return jsonify({'exists': False, 'error': error}), 200
        conn = get_pet_db_connection()
        cur = conn.cursor()
        ensure_pet_table()
        
        pet = cur.execute("SELECT * FROM pet WHERE username = ?", (username,)).fetchone()
        conn.close()
        if not pet:
            return jsonify({'exists': False, 'error': 'No pet found for user'}), 200
        return jsonify({
            'exists': True,
            'pet': {
                'name': pet[2], 'species': pet[3], 'gender': pet[4],
                'hunger': pet[5], 'happiness': pet[6], 'energy': pet[7],
                'hygiene': pet[8], 'coins': pet[9], 'xp': pet[10],
                'stage': pet[11], 'adventure_end': pet[12],
                'last_updated': pet[13], 'hat': pet[14]
            }
        }), 200
    except Exception as e:
        print(f"Pet status error: {e}")
        return jsonify({'exists': False, 'error': 'Unable to fetch pet status'}), 200

@app.route('/api/ai/trigger-training', methods=['POST'])
def trigger_background_training():
    """Manually trigger background training (admin only)"""
    try:
        data = request.json
        username = data.get('username')
        
        # Verify admin/clinician (you can adjust this check)
        conn = get_db_connection()
        cur = conn.cursor()
        user = cur.execute(
            "SELECT role FROM users WHERE username=?",
            (username,)
        ).fetchone()
        conn.close()
        
        if not user or user[0] != 'clinician':
            return jsonify({'error': 'Unauthorized - clinician access required'}), 403
        
        # Start training in background thread
        import threading
        from ai_trainer import train_background_model
        
        def train_async():
            print("🚀 Starting background training...")
            success = train_background_model(epochs=3)
            print(f"✅ Training completed: {success}")
        
        thread = threading.Thread(target=train_async, daemon=True)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Background training started. Check status in a few minutes.'
        }), 200
        
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/pet/create', methods=['POST'])
def pet_create():
    """Create new pet"""
    try:
        data = request.json
        username = data.get('username')
        name = data.get('name')
        species = data.get('species', 'Dog')
        gender = data.get('gender', 'Neutral')

        # SECURITY: Verify user exists
        valid, error = verify_pet_user(username)
        if not valid:
            return jsonify({'error': error}), 401

        if not name:
            return jsonify({'error': 'Pet name required'}), 400

        ensure_pet_table()
        conn = get_pet_db_connection()
        cur = conn.cursor()
        
        # Delete only THIS user's pet, not all pets
        cur.execute("DELETE FROM pet WHERE username = ?", (username,))
        cur.execute("""
            INSERT INTO pet (username, name, species, gender, hunger, happiness, energy, hygiene, 
                           coins, xp, stage, adventure_end, last_updated, hat)
            VALUES (?, ?, ?, ?, 70, 70, 70, 80, 0, 0, 'Baby', 0, ?, 'None')
        """, (username, name, species, gender, datetime.now().timestamp()))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Pet created!'}), 201
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/pet/feed', methods=['POST'])
def pet_feed():
    """Feed pet (from shop)"""
    try:
        data = request.json
        username = data.get('username')
        item_cost = data.get('cost', 10)

        # SECURITY: Verify user exists
        valid, error = verify_pet_user(username)
        if not valid:
            return jsonify({'error': error}), 401

        conn = get_pet_db_connection()
        cur = conn.cursor()
        pet = cur.execute("SELECT * FROM pet WHERE username = ?", (username,)).fetchone()
        
        if not pet:
            conn.close()
            return jsonify({'error': 'No pet found'}), 404
        
        coins = pet[9]
        if coins < item_cost:
            conn.close()
            return jsonify({'error': 'Not enough coins'}), 400
        
        # Update pet
        new_hunger = min(100, pet[5] + 30)
        new_coins = coins - item_cost
        cur.execute("UPDATE pet SET hunger=?, coins=? WHERE id=?", (new_hunger, new_coins, pet[0]))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'new_hunger': new_hunger, 'coins': new_coins}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/pet/reward', methods=['POST'])
def pet_reward():
    """Reward pet for user self-care actions - matches original desktop app logic"""
    try:
        # SECURITY: Authenticate user via session
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.json
        action = data.get('action')  # 'therapy', 'mood', 'gratitude', 'breathing', 'cbt', 'clinical'
        activity_type = data.get('activity_type')  # 'cbt', 'clinical', etc.

        # SECURITY: Verify user exists
        valid, error = verify_pet_user(username)
        if not valid:
            return jsonify({'success': False, 'message': error}), 200

        conn = get_pet_db_connection()
        cur = conn.cursor()
        pet_raw = cur.execute("SELECT * FROM pet WHERE username = ?", (username,)).fetchone()
        pet = normalize_pet_row(pet_raw)
        
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
        elif action == 'therapy':
            hap += 15
            hun += 5
        elif action == 'gratitude':
            hap += 8
        elif action == 'breathing':
            en += 10
            hap += 5
        elif action == 'cbt':
            hap += 12
            coin_gain += 5
        elif action == 'clinical':
            xp_gain += 10

        # Calculate new stats
        new_hunger = max(0, min(100, pet[5] + hun))
        new_happiness = max(0, min(100, pet[6] + hap))
        new_energy = max(0, min(100, pet[7] + en))
        new_hygiene = max(0, min(100, pet[8] + hyg))
        new_coins = pet[9] + coin_gain
        new_xp = pet[10] + xp_gain
        
        # Check evolution
        stage = pet[11]
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
            'evolved': stage != pet[11]
        }), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

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
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/pet/buy', methods=['POST'])
def pet_buy():
    """Purchase shop item"""
    try:
        data = request.json
        username = data.get('username')
        item_id = data.get('item_id')

        # SECURITY: Verify user exists
        valid, error = verify_pet_user(username)
        if not valid:
            return jsonify({'error': error}), 401

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
        
        conn = get_pet_db_connection()
        cur = conn.cursor()
        pet = cur.execute("SELECT * FROM pet WHERE username = ?", (username,)).fetchone()
        
        if not pet:
            conn.close()
            return jsonify({'error': 'No pet found'}), 404
        
        if pet[9] < item['cost']:
            conn.close()
            return jsonify({'error': 'Not enough coins'}), 400
        
        # Apply effect
        new_coins = pet[9] - item['cost']
        new_hunger = pet[5]
        new_happiness = pet[6]
        new_hat = pet[14] if len(pet) > 14 else 'None'
        
        if item['effect'] == 'hunger':
            new_hunger = min(100, pet[5] + item['value'])
        elif item['effect'] == 'multi':
            new_hunger = min(100, pet[5] + item['hunger'])
            new_happiness = min(100, pet[6] + item['happiness'])
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
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/pet/declutter', methods=['POST'])
def pet_declutter():
    """Declutter task - throw away worries"""
    try:
        # SECURITY: Authenticate user via session
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.json
        worries = data.get('worries', [])

        # SECURITY: Verify user exists
        valid, error = verify_pet_user(username)
        if not valid:
            return jsonify({'error': error}), 401

        if not worries or len(worries) == 0:
            return jsonify({'error': 'Please provide at least one worry'}), 400

        conn = get_pet_db_connection()
        cur = conn.cursor()
        pet_raw = cur.execute("SELECT * FROM pet WHERE username = ?", (username,)).fetchone()
        pet = normalize_pet_row(pet_raw)
        
        if not pet:
            conn.close()
            return jsonify({'error': 'No pet found'}), 404
        
        # Boost hygiene and happiness
        new_hygiene = min(100, pet[8] + 40)
        new_happiness = min(100, pet[6] + 5)
        new_xp = pet[10] + 15
        new_coins = pet[9] + 5
        
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
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/pet/adventure', methods=['POST'])
def pet_adventure():
    """Start adventure (30 min walk)"""
    try:
        data = request.json or {}
        username = data.get('username')

        # SECURITY: Verify user exists
        valid, error = verify_pet_user(username)
        if not valid:
            return jsonify({'error': error}), 401

        conn = get_pet_db_connection()
        cur = conn.cursor()
        pet_raw = cur.execute("SELECT * FROM pet WHERE username = ?", (username,)).fetchone()
        pet = normalize_pet_row(pet_raw)
        
        if not pet:
            conn.close()
            return jsonify({'error': 'No pet found'}), 404
        
        if pet[7] < 20:  # Energy check
            conn.close()
            return jsonify({'error': 'Pet is too tired for a walk!'}), 400
        
        # Set adventure end time (30 minutes from now)
        adventure_end = time.time() + (30 * 60)
        new_energy = pet[7] - 20
        
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
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/pet/check-return', methods=['POST'])
def pet_check_return():
    """Check if pet returned from adventure and give rewards"""
    try:
        # SECURITY: Authenticate user via session
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.json or {}

        # SECURITY: Verify user exists
        valid, error = verify_pet_user(username)
        if not valid:
            return jsonify({'error': error}), 401

        conn = get_pet_db_connection()
        cur = conn.cursor()
        pet_raw = cur.execute("SELECT * FROM pet WHERE username = ?", (username,)).fetchone()
        pet = normalize_pet_row(pet_raw)
        
        if not pet:
            conn.close()
            return jsonify({'error': 'No pet found'}), 404
        
        adventure_end = pet[12]
        
        if adventure_end > 0 and time.time() >= adventure_end:
            # Pet returned!
            import random
            bonus_coins = random.randint(10, 50)
            
            new_coins = pet[9] + bonus_coins
            new_xp = pet[10] + 20
            
            cur.execute(
                "UPDATE pet SET coins=?, xp=?, adventure_end=0, last_updated=? WHERE id=?",
                (new_coins, new_xp, time.time(), pet[0])
            )
            conn.commit()
            conn.close()
            
            return jsonify({
                'returned': True,
                'message': f'{pet[2]} returned with {bonus_coins} coins and a cool leaf! 🍃',
                'coins_earned': bonus_coins,
                'new_coins': new_coins
            }), 200
        else:
            conn.close()
            return jsonify({'returned': False}), 200
            
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/pet/apply-decay', methods=['POST'])
def pet_apply_decay():
    """Apply time-based stat decay"""
    try:
        # SECURITY: Authenticate user via session
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.json or {}

        # SECURITY: Verify user exists
        valid, error = verify_pet_user(username)
        if not valid:
            return jsonify({'error': error}), 401

        conn = get_pet_db_connection()
        cur = conn.cursor()
        pet_raw = cur.execute("SELECT * FROM pet WHERE username = ?", (username,)).fetchone()
        pet = normalize_pet_row(pet_raw)
        
        if not pet:
            conn.close()
            return jsonify({'error': 'No pet found'}), 404
        
        now = time.time()
        last_updated = pet[13]
        hours_passed = (now - last_updated) / 3600
        
        # Very gentle decay (user doesn't feel like they're neglecting pet)
        # 0.3 per hour = ~7 points per day, not overwhelming
        if hours_passed > 1.0:
            decay = int(hours_passed * 0.3)
            
            new_hunger = max(20, pet[5] - decay)
            new_energy = max(20, pet[7] - decay)
            new_hygiene = max(20, pet[8] - int(decay / 3))
            
            cur.execute(
                "UPDATE pet SET hunger=?, energy=?, hygiene=?, last_updated=? WHERE id=?",
                (new_hunger, new_energy, new_hygiene, now, pet[0])
            )
            conn.commit()
        
        conn.close()
        return jsonify({'success': True}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

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

        # INPUT VALIDATION: Length limits
        MAX_FIELD_LENGTH = 2000
        for field_name, field_value in [('situation', situation), ('thought', thought), ('evidence', evidence)]:
            if field_value and len(field_value) > MAX_FIELD_LENGTH:
                return jsonify({'error': f'{field_name.capitalize()} too long. Maximum {MAX_FIELD_LENGTH} characters allowed.'}), 400

        conn = get_db_connection()
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
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/cbt/records', methods=['GET'])
def get_cbt_records():
    """Get user's CBT thought records"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = get_db_connection()
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
        return handle_exception(e, request.endpoint or 'unknown')

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
        conn = get_db_connection()
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
        return handle_exception(e, request.endpoint or 'unknown')

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
        conn = get_db_connection()
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
        return handle_exception(e, request.endpoint or 'unknown')

# === COMMUNITY SUPPORT BOARD ===
@app.route('/api/community/posts', methods=['GET'])
def get_community_posts():
    """Get recent community posts with reaction counts and replies inline"""
    try:
        username = request.args.get('username', '')  # Optional - to check user's reactions
        category = request.args.get('category', '')  # Optional - filter by category (required for channel view)

        # Valid categories for reference
        VALID_CATEGORIES = [
            'anxiety', 'depression', 'relationships', 'intrusive-thoughts',
            'grief', 'work-stress', 'self-esteem', 'trauma', 'addiction',
            'sleep', 'motivation', 'general', 'celebration', 'question'
        ]

        conn = get_db_connection()
        cur = conn.cursor()

        # Build query with optional category filter - pinned posts first, then by timestamp
        if category and category in VALID_CATEGORIES:
            posts = cur.execute(
                "SELECT id, username, message, likes, entry_timestamp, category, is_pinned FROM community_posts WHERE category=? ORDER BY is_pinned DESC, entry_timestamp DESC LIMIT 100",
                (category,)
            ).fetchall()
            # Mark channel as read for this user
            if username:
                cur.execute(
                    "INSERT INTO community_channel_reads (username, channel, last_read) VALUES (?, ?, CURRENT_TIMESTAMP)",
                    (username, category)
                )
                conn.commit()
        else:
            posts = cur.execute(
                "SELECT id, username, message, likes, entry_timestamp, category, is_pinned FROM community_posts ORDER BY is_pinned DESC, entry_timestamp DESC LIMIT 100"
            ).fetchall()

        post_list = []
        for p in posts:
            post_id = p[0]

            # Get reaction counts by type
            reactions = cur.execute(
                "SELECT reaction_type, COUNT(*) FROM community_likes WHERE post_id=? GROUP BY reaction_type",
                (post_id,)
            ).fetchall()
            reaction_counts = {r[0]: r[1] for r in reactions}

            # Check which reactions current user has made
            user_reactions = []
            if username:
                user_reacts = cur.execute(
                    "SELECT reaction_type FROM community_likes WHERE post_id=? AND username=?",
                    (post_id, username)
                ).fetchall()
                user_reactions = [r[0] for r in user_reacts]

            # Get replies inline
            replies = cur.execute(
                "SELECT id, username, message, timestamp FROM community_replies WHERE post_id=? ORDER BY timestamp ASC",
                (post_id,)
            ).fetchall()
            reply_list = [
                {
                    'id': r[0],
                    'username': r[1],
                    'message': r[2],
                    'timestamp': r[3]
                } for r in replies
            ]

            post_list.append({
                'id': post_id,
                'username': p[1],
                'message': p[2],
                'likes': p[3] or 0,  # Total reactions (backwards compatible)
                'reactions': reaction_counts,  # Breakdown by type
                'user_reactions': user_reactions,  # What current user reacted with
                'timestamp': p[4],
                'category': p[5] or 'general',
                'is_pinned': bool(p[6]) if len(p) > 6 else False,
                'replies': reply_list,
                'reply_count': len(reply_list),
                'liked_by_user': 'like' in user_reactions  # Backwards compatible
            })

        conn.close()
        return jsonify({'posts': post_list, 'categories': VALID_CATEGORIES}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/community/channels', methods=['GET'])
def get_community_channels():
    """Get all channels with post counts and unread indicators"""
    try:
        username = request.args.get('username', '')

        VALID_CATEGORIES = [
            'anxiety', 'depression', 'relationships', 'intrusive-thoughts',
            'grief', 'work-stress', 'self-esteem', 'trauma', 'addiction',
            'sleep', 'motivation', 'general', 'celebration', 'question'
        ]

        CATEGORY_INFO = {
            'anxiety': {'emoji': '😰', 'name': 'Anxiety', 'description': 'Discuss anxiety and coping strategies'},
            'depression': {'emoji': '😔', 'name': 'Depression', 'description': 'Support for depression'},
            'relationships': {'emoji': '💑', 'name': 'Relationships', 'description': 'Relationship advice and support'},
            'intrusive-thoughts': {'emoji': '🧠', 'name': 'Intrusive Thoughts', 'description': 'Managing unwanted thoughts'},
            'grief': {'emoji': '💔', 'name': 'Grief & Loss', 'description': 'Coping with loss'},
            'work-stress': {'emoji': '💼', 'name': 'Work Stress', 'description': 'Workplace mental health'},
            'self-esteem': {'emoji': '🪞', 'name': 'Self-Esteem', 'description': 'Building confidence'},
            'trauma': {'emoji': '🩹', 'name': 'Trauma', 'description': 'Trauma support and healing'},
            'addiction': {'emoji': '🔗', 'name': 'Addiction', 'description': 'Recovery support'},
            'sleep': {'emoji': '😴', 'name': 'Sleep Issues', 'description': 'Better sleep habits'},
            'motivation': {'emoji': '⚡', 'name': 'Motivation', 'description': 'Finding motivation'},
            'general': {'emoji': '💬', 'name': 'General', 'description': 'General discussion'},
            'celebration': {'emoji': '🎉', 'name': 'Celebrations', 'description': 'Share your wins!'},
            'question': {'emoji': '❓', 'name': 'Questions', 'description': 'Ask the community'}
        }

        conn = get_db_connection()
        cur = conn.cursor()

        channels = []
        for cat in VALID_CATEGORIES:
            info = CATEGORY_INFO.get(cat, {'emoji': '💬', 'name': cat.title(), 'description': ''})

            # Get post count for this channel
            count = cur.execute(
                "SELECT COUNT(*) FROM community_posts WHERE category=?", (cat,)
            ).fetchone()[0]

            # Get latest post timestamp
            latest = cur.execute(
                "SELECT MAX(entry_timestamp) FROM community_posts WHERE category=?", (cat,)
            ).fetchone()[0]

            # Check for unread posts
            unread_count = 0
            if username and latest:
                last_read = cur.execute(
                    "SELECT last_read FROM community_channel_reads WHERE username=? AND channel=?",
                    (username, cat)
                ).fetchone()
                if last_read:
                    unread = cur.execute(
                        "SELECT COUNT(*) FROM community_posts WHERE category=? AND entry_timestamp > ?",
                        (cat, last_read[0])
                    ).fetchone()[0]
                    unread_count = unread
                else:
                    # Never visited - all posts are unread (max 10 shown)
                    unread_count = min(count, 10)

            channels.append({
                'id': cat,
                'emoji': info['emoji'],
                'name': info['name'],
                'description': info['description'],
                'post_count': count,
                'latest_post': latest,
                'unread_count': unread_count
            })

        conn.close()
        return jsonify({'channels': channels}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/community/post/<int:post_id>/pin', methods=['POST'])
def pin_community_post(post_id):
    """Pin or unpin a community post (clinicians only)"""
    try:
        data = request.json
        username = data.get('username')
        pin = data.get('pin', True)  # True to pin, False to unpin

        if not username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Check if user is a clinician
        user = cur.execute("SELECT role FROM users WHERE username=?", (username,)).fetchone()
        if not user or user[0] != 'clinician':
            conn.close()
            return jsonify({'error': 'Only clinicians can pin posts'}), 403

        # Update pin status
        cur.execute(
            "UPDATE community_posts SET is_pinned=? WHERE id=?",
            (1 if pin else 0, post_id)
        )
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'pinned': pin}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/community/post', methods=['POST'])
def create_community_post():
    """Create a new community post"""
    try:
        data = request.json
        username = data.get('username')
        message = data.get('message')
        category = data.get('category')

        # Valid categories
        VALID_CATEGORIES = [
            'anxiety', 'depression', 'relationships', 'intrusive-thoughts',
            'grief', 'work-stress', 'self-esteem', 'trauma', 'addiction',
            'sleep', 'motivation', 'general', 'celebration', 'question'
        ]

        if not username or not message:
            return jsonify({'error': 'Username and message required'}), 400

        if not category or category not in VALID_CATEGORIES:
            return jsonify({'error': 'Please select a valid category', 'valid_categories': VALID_CATEGORIES}), 400

        # INPUT VALIDATION: Length limits to prevent abuse
        MAX_POST_LENGTH = 2000
        if len(message) > MAX_POST_LENGTH:
            return jsonify({'error': f'Message too long. Maximum {MAX_POST_LENGTH} characters allowed.'}), 400

        if len(username) > 50:
            return jsonify({'error': 'Username and message required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO community_posts (username, message, category) VALUES (?,?,?)",
            (username, message, category)
        )
        conn.commit()
        conn.close()
        
        # AUTO-UPDATE AI MEMORY
        update_ai_memory(username)
        
        return jsonify({'success': True}), 201
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/community/post/<int:post_id>/react', methods=['POST'])
def react_to_post(post_id):
    """Add or remove a reaction to a community post"""
    try:
        data = request.json
        username = data.get('username')
        reaction_type = data.get('reaction', 'like')  # Default to 'like' for backwards compatibility

        # Valid reaction types
        VALID_REACTIONS = ['like', 'heart', 'hug', 'celebrate', 'support']

        if not username:
            return jsonify({'error': 'Username required'}), 400

        if reaction_type not in VALID_REACTIONS:
            return jsonify({'error': 'Invalid reaction type'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Check if user already has this reaction on this post
        existing_reaction = cur.execute(
            "SELECT 1 FROM community_likes WHERE post_id=? AND username=? AND reaction_type=?",
            (post_id, username, reaction_type)
        ).fetchone()

        if existing_reaction:
            # Remove reaction (toggle off)
            cur.execute(
                "DELETE FROM community_likes WHERE post_id=? AND username=? AND reaction_type=?",
                (post_id, username, reaction_type)
            )
            action = 'removed'
        else:
            # Add reaction
            cur.execute(
                "INSERT INTO community_likes (post_id, username, reaction_type) VALUES (?,?,?)",
                (post_id, username, reaction_type)
            )
            action = 'added'

        # Get updated reaction counts for this post
        reactions = cur.execute(
            "SELECT reaction_type, COUNT(*) FROM community_likes WHERE post_id=? GROUP BY reaction_type",
            (post_id,)
        ).fetchall()

        reaction_counts = {r[0]: r[1] for r in reactions}

        # Update total likes count (sum of all reactions) for backwards compatibility
        total_reactions = sum(reaction_counts.values())
        cur.execute("UPDATE community_posts SET likes=? WHERE id=?", (total_reactions, post_id))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'action': action,
            'reaction': reaction_type,
            'reactions': reaction_counts,
            'total': total_reactions
        }), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# Backwards compatible like endpoint
@app.route('/api/community/post/<int:post_id>/like', methods=['POST'])
def like_community_post(post_id):
    """Like or unlike a community post (backwards compatible - uses 'like' reaction)"""
    try:
        data = request.json
        username = data.get('username')

        if not username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Check if already liked
        existing_like = cur.execute(
            "SELECT 1 FROM community_likes WHERE post_id=? AND username=? AND reaction_type='like'",
            (post_id, username)
        ).fetchone()

        if existing_like:
            # Unlike - remove like
            cur.execute("DELETE FROM community_likes WHERE post_id=? AND username=? AND reaction_type='like'", (post_id, username))
        else:
            # Like - add like
            cur.execute("INSERT INTO community_likes (post_id, username, reaction_type) VALUES (?,?,'like')", (post_id, username))

        # Update total count
        total = cur.execute("SELECT COUNT(*) FROM community_likes WHERE post_id=?", (post_id,)).fetchone()[0]
        cur.execute("UPDATE community_posts SET likes=? WHERE id=?", (total, post_id))

        conn.commit()
        conn.close()

        return jsonify({'success': True}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/community/post/<int:post_id>', methods=['DELETE'])
def delete_community_post(post_id):
    """Delete a community post (only by author)"""
    try:
        data = request.json
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = get_db_connection()
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
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/community/post/<int:post_id>/reply', methods=['POST'])
def create_reply(post_id):
    """Create a reply to a community post with content moderation"""
    try:
        data = request.json
        username = data.get('username')
        message = data.get('message')

        if not username or not message:
            return jsonify({'error': 'Username and message required'}), 400

        # CONTENT MODERATION: Check reply before posting
        moderation_result = content_moderator.moderate(message)

        if not moderation_result['allowed']:
            log_event(username, 'community', 'reply_blocked', moderation_result['reason'])
            return jsonify({
                'error': moderation_result['reason'],
                'code': 'CONTENT_BLOCKED'
            }), 400

        sanitized_message = moderation_result['filtered_text']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO community_replies (post_id, username, message) VALUES (?,?,?)",
            (post_id, username, sanitized_message)
        )
        reply_id = cur.lastrowid

        # Flag for review if needed
        if moderation_result['flagged']:
            cur.execute(
                "INSERT INTO alerts (username, alert_type, details, status) VALUES (?,?,?,?)",
                (username, 'content_review', f"Reply {reply_id} to post {post_id}: {moderation_result['flag_reason']}", 'pending_review')
            )
            log_event(username, 'community', 'reply_flagged', moderation_result['flag_reason'])

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'reply_id': reply_id}), 201
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')


@app.route('/api/community/reply/<int:reply_id>', methods=['DELETE'])
def delete_reply(reply_id):
    """Delete a community reply (only by author)"""
    try:
        data = request.json
        username = data.get('username')

        if not username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Verify reply belongs to user
        reply = cur.execute(
            "SELECT username FROM community_replies WHERE id=?",
            (reply_id,)
        ).fetchone()

        if not reply:
            conn.close()
            return jsonify({'error': 'Reply not found'}), 404

        if reply[0] != username:
            conn.close()
            return jsonify({'error': 'You can only delete your own replies'}), 403

        # Delete the reply
        cur.execute("DELETE FROM community_replies WHERE id=?", (reply_id,))

        conn.commit()
        conn.close()

        return jsonify({'success': True}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')


@app.route('/api/community/post/<int:post_id>/report', methods=['POST'])
def report_community_post(post_id):
    """Report a community post for moderation review"""
    try:
        data = request.json
        reporter_username = data.get('username')
        reason = data.get('reason', 'No reason provided')

        if not reporter_username:
            return jsonify({'error': 'Username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Check if post exists
        post = cur.execute(
            "SELECT username, message FROM community_posts WHERE id=?",
            (post_id,)
        ).fetchone()

        if not post:
            conn.close()
            return jsonify({'error': 'Post not found'}), 404

        post_author = post[0]

        # Don't allow self-reporting
        if reporter_username == post_author:
            conn.close()
            return jsonify({'error': 'Cannot report your own post'}), 400

        # Check if already reported by this user
        existing_report = cur.execute(
            "SELECT id FROM alerts WHERE alert_type='post_report' AND details LIKE ? AND details LIKE ?",
            (f'%post_id:{post_id}%', f'%reporter:{reporter_username}%')
        ).fetchone()

        if existing_report:
            conn.close()
            return jsonify({'error': 'You have already reported this post'}), 409

        # Create report alert
        report_details = f"post_id:{post_id}|reporter:{reporter_username}|author:{post_author}|reason:{reason}"
        cur.execute(
            "INSERT INTO alerts (username, alert_type, details, status) VALUES (?,?,?,?)",
            (post_author, 'post_report', report_details, 'pending_review')
        )

        conn.commit()
        conn.close()

        log_event(reporter_username, 'community', 'post_reported', f"Reported post {post_id}: {reason}")

        return jsonify({
            'success': True,
            'message': 'Post has been reported for review'
        }), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')


@app.route('/api/community/post/<int:post_id>/replies', methods=['GET'])
def get_replies(post_id):
    """Get replies for a community post"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        replies = cur.execute(
            "SELECT id, username, message, timestamp FROM community_replies WHERE post_id=? ORDER BY timestamp ASC",
            (post_id,)
        ).fetchall()
        conn.close()

        return jsonify({'replies': [
            {
                'id': r[0],
                'username': r[1],
                'message': r[2],
                'timestamp': r[3]
            } for r in replies
        ]}), 200
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# === SAFETY PLAN ===
@app.route('/api/safety-plan', methods=['GET'])
def get_safety_plan():
    """Get user's safety plan"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = get_db_connection()
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
        return handle_exception(e, request.endpoint or 'unknown')

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
        
        conn = get_db_connection()
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
        return handle_exception(e, request.endpoint or 'unknown')

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
        
        conn = get_db_connection()
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
        for r in cur.execute("SELECT entrestamp, mood_val, sleep_val, meds, notes, sentiment, exercise_mins, outside_mins, water_pints FROM mood_logs WHERE username=? ORDER BY entrestamp DESC", (username,)).fetchall():
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
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/export/pdf', methods=['GET'])
def export_pdf():
    """Export user data as PDF report (patient personal wellness format)"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
        except ImportError:
            return jsonify({'error': 'PDF library not available. Please install reportlab.'}), 500
        
        import io
        from datetime import datetime
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=12,
            alignment=TA_CENTER
        )
        story.append(Paragraph(f"Personal Wellness Report", title_style))
        story.append(Paragraph(f"<i>{username}</i>", styles['Normal']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Mood Summary
        moods = cur.execute(
            "SELECT entrestamp, mood_val, sleep_val, meds, exercise_mins FROM mood_logs WHERE username=? ORDER BY entrestamp DESC LIMIT 15",
            (username,)
        ).fetchall()
        
        if moods:
            story.append(Paragraph("<b>Recent Mood & Wellness Tracking</b>", styles['Heading2']))
            mood_data = [['Date', 'Mood', 'Sleep (hrs)', 'Exercise (mins)', 'Medications']]
            for m in moods:
                date_str = m[0][:10] if m[0] else 'N/A'
                mood_data.append([
                    date_str,
                    f"{m[1]}/10" if m[1] else 'N/A',
                    f"{m[2]}" if m[2] else 'N/A',
                    f"{m[4]}" if m[4] else '0',
                    m[3] if m[3] else 'None'
                ])
            
            table = Table(mood_data, colWidths=[1.2*inch, 0.8*inch, 1*inch, 1.2*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(table)
            story.append(Spacer(1, 0.2*inch))
        
        # Gratitude entries
        gratitudes = cur.execute(
            "SELECT entry_timestamp, entry FROM gratitude_logs WHERE username=? ORDER BY entry_timestamp DESC LIMIT 10",
            (username,)
        ).fetchall()
        
        if gratitudes:
            story.append(Paragraph("<b>Gratitude Journal Highlights</b>", styles['Heading2']))
            for g in gratitudes:
                date_str = g[0][:10] if g[0] else 'N/A'
                story.append(Paragraph(f"<i>{date_str}:</i> {g[1]}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        conn.close()
        
        # Build PDF
        doc.build(story)
        
        pdf_data = buffer.getvalue()
        buffer.close()
        
        response = make_response(pdf_data)
        response.headers["Content-Disposition"] = f"attachment; filename={username}_wellness_report.pdf"
        response.headers["Content-Type"] = "application/pdf"
        return response
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# === PROGRESS INSIGHTS ===
@app.route('/api/insights', methods=['GET'])
def get_insights():
    """
    Generate AI-powered insights for a patient or clinician over a custom date range.
    Uses a descriptive prompt for the AI and includes all user data, conversations, and app interactions.
    - Clinician: professional, data-rich summary
    - Patient: narrative, empathetic summary

    SECURITY: Requires authentication - users can only view their own data,
    or clinicians can view their approved patients' data.
    """
    try:
        username = request.args.get('username')
        role = request.args.get('role', 'patient')  # 'clinician' or 'patient'
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        ai_prompt = request.args.get('prompt')  # The descriptive insights prompt
        requesting_user = request.args.get('requesting_user')  # Who is making this request

        if not username or not ai_prompt:
            return jsonify({'error': 'Username and prompt required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # SECURITY: Verify authorization
        if role == 'clinician':
            # Clinician must provide their username and be approved to view this patient
            clinician_username = request.args.get('clinician_username')
            if not clinician_username:
                conn.close()
                return jsonify({'error': 'Clinician username required for clinician role'}), 400

            # Verify clinician exists and has correct role
            clinician_check = cur.execute(
                "SELECT role FROM users WHERE username=?", (clinician_username,)
            ).fetchone()
            if not clinician_check or clinician_check[0] != 'clinician':
                conn.close()
                return jsonify({'error': 'Invalid clinician'}), 403

            # Verify clinician has approved access to this patient
            approval_check = cur.execute(
                "SELECT status FROM patient_approvals WHERE patient_username=? AND clinician_username=? AND status='approved'",
                (username, clinician_username)
            ).fetchone()
            if not approval_check:
                conn.close()
                return jsonify({'error': 'Clinician not authorized to view this patient'}), 403
        else:
            # Patient role - verify they're requesting their own data
            if requesting_user and requesting_user != username:
                # Check if requesting_user is a clinician with approval
                clinician_check = cur.execute(
                    "SELECT role FROM users WHERE username=?", (requesting_user,)
                ).fetchone()
                if clinician_check and clinician_check[0] == 'clinician':
                    approval_check = cur.execute(
                        "SELECT status FROM patient_approvals WHERE patient_username=? AND clinician_username=? AND status='approved'",
                        (username, requesting_user)
                    ).fetchone()
                    if not approval_check:
                        conn.close()
                        return jsonify({'error': 'Not authorized to view this data'}), 403
                else:
                    conn.close()
                    return jsonify({'error': 'Not authorized to view this data'}), 403

        # Build mood log query with date range
        mood_query = "SELECT mood_val, sleep_val, entrestamp, notes FROM mood_logs WHERE username=?"
        params = [username]
        if from_date:
            mood_query += " AND date(entrestamp) >= date(?)"
            params.append(from_date)
        if to_date:
            mood_query += " AND date(entrestamp) <= date(?)"
            params.append(to_date)
        mood_query += " ORDER BY entrestamp DESC"
        moods = cur.execute(mood_query, tuple(params)).fetchall()

        # Get chat history in date range
        chat_query = "SELECT sender, message, timestamp FROM chat_history WHERE session_id=?"
        chat_params = [f"{username}_session"]
        if from_date:
            chat_query += " AND date(timestamp) >= date(?)"
            chat_params.append(from_date)
        if to_date:
            chat_query += " AND date(timestamp) <= date(?)"
            chat_params.append(to_date)
        chat_query += " ORDER BY timestamp DESC"
        chat_history = cur.execute(chat_query, tuple(chat_params)).fetchall()

        # Get gratitude entries
        grat_query = "SELECT entry, entry_timestamp FROM gratitude_logs WHERE username=?"
        grat_params = [username]
        if from_date:
            grat_query += " AND date(entry_timestamp) >= date(?)"
            grat_params.append(from_date)
        if to_date:
            grat_query += " AND date(entry_timestamp) <= date(?)"
            grat_params.append(to_date)
        grat_query += " ORDER BY entry_timestamp DESC"
        gratitudes = cur.execute(grat_query, tuple(grat_params)).fetchall()

        # Get CBT records
        cbt_query = "SELECT situation, thought, evidence, entry_timestamp FROM cbt_records WHERE username=?"
        cbt_params = [username]
        if from_date:
            cbt_query += " AND date(entry_timestamp) >= date(?)"
            cbt_params.append(from_date)
        if to_date:
            cbt_query += " AND date(entry_timestamp) <= date(?)"
            cbt_params.append(to_date)
        cbt_query += " ORDER BY entry_timestamp DESC"
        cbt = cur.execute(cbt_query, tuple(cbt_params)).fetchall()

        # Get safety plan
        safety = cur.execute(
            "SELECT triggers, coping FROM safety_plans WHERE username=?", (username,)
        ).fetchone()

        conn.close()

        # Format data for AI
        mood_summary = [
            f"{m[2][:10]}: Mood {m[0]}/10, Sleep {m[1]}h, Notes: {m[3][:50] if m[3] else '-'}"
            for m in moods
        ]
        chat_summary = [
            f"{c[2][:16]} {c[0].upper()}: {c[1][:100]}"
            for c in chat_history
        ]
        gratitude_summary = [f"{g[1][:10]}: {g[0][:80]}" for g in gratitudes]
        cbt_summary = [
            f"{c[3][:10]}: Situation: {c[0][:40]}, Thought: {c[1][:40]}, Evidence: {c[2][:40]}"
            for c in cbt
        ]
        safety_summary = f"Triggers: {safety[0] if safety else 'None'}, Coping: {safety[1] if safety else 'None'}"

        # Compose maximally detailed AI input
        if role == 'clinician':
            ai_input = (
                f"You are a clinical psychologist generating a comprehensive, data-rich summary for another clinician. "
                f"Include all available patient data, highlight trends, risks, engagement, and make actionable recommendations. "
                f"Be specific, evidence-based, and reference all app activity.\n\n"
                f"PATIENT DATA ({from_date or 'start'} to {to_date or 'now'}):\n"
                f"- Mood Logs (up to 15):\n" + "\n".join(mood_summary[:15]) + "\n"
                f"- Chat History (user/AI, up to 10):\n" + "\n".join(chat_summary[:10]) + "\n"
                f"- Gratitude Entries (up to 5):\n" + "\n".join(gratitude_summary[:5]) + "\n"
                f"- CBT Records (up to 5):\n" + "\n".join(cbt_summary[:5]) + "\n"
                f"- Safety Plan: {safety_summary}\n"
                f"\nPlease analyze:\n"
                f"1. Overall clinical impression, referencing all data sources.\n"
                f"2. Key concerns, risk factors, and any safety issues.\n"
                f"3. Notable trends in mood, sleep, habits, and engagement.\n"
                f"4. Recommendations for clinical action or follow-up.\n"
                f"5. Progress in self-help activities (gratitude, CBT, etc).\n"
                f"6. Any missing data or areas needing further assessment.\n"
                f"Be thorough, concise, and professional."
            )
        else:
            ai_input = (
                f"You are a compassionate therapist writing a detailed, narrative insight for the patient. "
                f"Summarize all their app activity, highlight progress, strengths, and areas for growth. "
                f"Use an empathetic, encouraging tone.\n\n"
                f"YOUR DATA ({from_date or 'the beginning'} to {to_date or 'now'}):\n"
                f"- Mood logs: " + ", ".join([f"{m[0]}/10" for m in moods[:10]]) + "\n"
                f"- Sleep: " + ", ".join([f"{m[1]}h" for m in moods[:10]]) + "\n"
                f"- Recent gratitude: " + "; ".join([g[0][:60] for g in gratitudes[:5]]) + "\n"
                f"- CBT: " + "; ".join([c[1][:60] for c in cbt[:3]]) + "\n"
                f"- Safety plan: {safety_summary}\n"
                f"- Chat highlights: " + "; ".join([c[1][:80] for c in chat_history[:5]]) + "\n"
                f"\nPlease write a comprehensive, encouraging summary that:\n"
                f"1. Reflects on their progress and patterns.\n"
                f"2. Highlights strengths and positive changes.\n"
                f"3. Gently notes any risks or areas to focus on.\n"
                f"4. Offers practical, personalized suggestions.\n"
                f"5. Encourages continued engagement and self-care.\n"
                f"Make it easy to understand, supportive, and motivating."
            )

        # Call AI model (pseudo-code, replace with actual call)
        ai_response = TherapistAI(username).get_insight(ai_input)

        # Calculate avg_mood, avg_sleep, and trend safely
        # Always return numbers to prevent frontend .toFixed() errors
        if moods:
            avg_mood = sum(m[0] for m in moods if m[0] is not None) / max(1, len([m for m in moods if m[0] is not None]))
            avg_sleep = sum(m[1] or 0 for m in moods) / len(moods)
            trend = 'Improving' if len(moods) > 1 and moods[0][0] > moods[-1][0] else 'Stable'
        else:
            avg_mood = 0.0  # Return 0 instead of None for frontend compatibility
            avg_sleep = 0.0
            trend = 'No data'
        return jsonify({
            'insight': ai_response,
            'mood_data': [{'value': m[0], 'timestamp': m[2]} for m in moods],
            'sleep_data': [{'value': m[1], 'timestamp': m[2]} for m in moods],
            'avg_mood': avg_mood,
            'avg_sleep': avg_sleep,
            'trend': trend,
            'from_date': from_date,
            'to_date': to_date,
            'role': role
        }), 200

    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# === PROFESSIONAL DASHBOARD ===
@app.route('/api/professional/patients', methods=['GET'])
def get_patients():
    """Get list of all patients assigned to logged-in clinician.

    OPTIMIZED: Uses a single query with subqueries instead of N+1 pattern.
    Previously: 1 + 4*N queries (where N = number of patients)
    Now: 1 query (with subqueries executed once per patient in SQL)

    SECURITY: Uses session authentication and verifies clinician role.
    """
    try:
        # SECURITY: Get authenticated clinician from session (Phase 1A)
        clinician_username = get_authenticated_username()
        if not clinician_username:
            return jsonify({'error': 'Authentication required'}), 401

        conn = get_db_connection()
        cur = conn.cursor()

        # SECURITY: Verify the clinician exists and has the clinician role
        clinician_check = cur.execute(
            "SELECT role FROM users WHERE username=?", (clinician_username,)
        ).fetchone()

        if not clinician_check:
            conn.close()
            return jsonify({'error': 'Clinician not found'}), 404

        if clinician_check[0] != 'clinician':
            conn.close()
            return jsonify({'error': 'User is not a clinician'}), 403

        # OPTIMIZED: Single query with correlated subqueries
        # This is much more efficient than N+1 queries in application code
        patients = cur.execute("""
            SELECT
                u.username,
                u.last_login,
                -- 7-day mood average (correlated subquery)
                (SELECT AVG(mood_val)
                 FROM mood_logs ml
                 WHERE ml.username = u.username
                   AND ml.entrestamp > datetime('now', '-7 days')
                ) as avg_mood_7d,
                -- 7-day alert count (correlated subquery)
                (SELECT COUNT(*)
                 FROM alerts a
                 WHERE a.username = u.username
                   AND a.created_at > datetime('now', '-7 days')
                ) as alert_count_7d,
                -- Latest assessment info (using nested subqueries)
                (SELECT scale_name FROM clinical_scales cs
                 WHERE cs.username = u.username
                 ORDER BY entry_timestamp DESC LIMIT 1) as latest_scale_name,
                (SELECT score FROM clinical_scales cs
                 WHERE cs.username = u.username
                 ORDER BY entry_timestamp DESC LIMIT 1) as latest_scale_score,
                (SELECT severity FROM clinical_scales cs
                 WHERE cs.username = u.username
                 ORDER BY entry_timestamp DESC LIMIT 1) as latest_scale_severity,
                (SELECT entry_timestamp FROM clinical_scales cs
                 WHERE cs.username = u.username
                 ORDER BY entry_timestamp DESC LIMIT 1) as latest_scale_date
            FROM users u
            JOIN patient_approvals pa ON u.username = pa.patient_username
            WHERE u.role = 'user'
              AND pa.clinician_username = ?
              AND pa.status = 'approved'
            ORDER BY alert_count_7d DESC, u.username ASC
        """, (clinician_username,)).fetchall()

        # Build response from single query results
        patient_list = []
        for p in patients:
            username, last_login, avg_mood, alert_count, scale_name, scale_score, scale_severity, scale_date = p

            patient_list.append({
                'username': username,
                'avg_mood_7d': round(avg_mood, 1) if avg_mood else 0,
                'alert_count_7d': alert_count or 0,
                'last_login': last_login,
                'latest_assessment': {
                    'name': scale_name,
                    'score': scale_score,
                    'severity': scale_severity,
                    'date': scale_date
                } if scale_name else None
            })

        conn.close()
        return jsonify({'patients': patient_list}), 200
    except Exception as e:
        print(f"ERROR in get_patients: {str(e)}")
        import traceback
        traceback.print_exc()
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/professional/patient/<username>', methods=['GET'])
def get_patient_detail(username):
    """Phase 1B: Get detailed patient data with FK validation"""
    try:
        # SECURITY: Get authenticated clinician from session
        clinician_username = get_authenticated_username()
        if not clinician_username:
            return jsonify({'error': 'Authentication required'}), 401

        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verify user is a clinician
        clinician = cur.execute(
            "SELECT role FROM users WHERE username=?",
            (clinician_username,)
        ).fetchone()
        
        if not clinician or clinician[0] != 'clinician':
            conn.close()
            return jsonify({'error': 'Clinician role required'}), 403

        # Phase 1B: Verify clinician-patient relationship via FK
        is_valid, _ = verify_clinician_patient_relationship(clinician_username, username)
        if not is_valid:
            conn.close()
            return jsonify({'error': 'Unauthorized: Patient not assigned to clinician'}), 403

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
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/professional/ai-summary', methods=['POST'])
def generate_ai_summary():
    """Generate AI clinical summary for a patient"""
    try:
        data = request.json
        username = data.get('username')
        clinician_username = data.get('clinician_username')

        # Log incoming request for debugging
        print(f"[AI SUMMARY] Request: username={username}, clinician_username={clinician_username}")

        if not username:
            print("[AI SUMMARY] Error: Username required")
            return jsonify({'error': 'Username required'}), 400

        if not clinician_username:
            print("[AI SUMMARY] Error: Clinician username required")
            return jsonify({'error': 'Clinician username required'}), 400

        # Fetch patient data
        conn = get_db_connection()
        cur = conn.cursor()

        # SECURITY: Verify clinician has approved access to this patient
        approval = cur.execute(
            "SELECT status FROM patient_approvals WHERE clinician_username=? AND patient_username=? AND status='approved'",
            (clinician_username, username)
        ).fetchone()

        if not approval:
            conn.close()
            print(f"[AI SUMMARY] Error: Unauthorized access attempt by {clinician_username} for {username}")
            return jsonify({'error': 'Unauthorized: You do not have access to this patient'}), 403

        # Get profile info
        profile = cur.execute(
            "SELECT full_name, conditions FROM users WHERE username=?",
            (username,)
        ).fetchone()
        print(f"[AI SUMMARY] Profile: {profile}")

        # Get join date from first mood log (users table doesn't have created_at)
        join_date = None
        first_mood = cur.execute(
            "SELECT entrestamp FROM mood_logs WHERE username=? ORDER BY entrestamp ASC LIMIT 1",
            (username,)
        ).fetchone()
        if first_mood and first_mood[0]:
            join_date = first_mood[0]
        # Calculate days since join
        days_since_join = 30
        if join_date:
            try:
                join_dt = datetime.strptime(join_date, "%Y-%m-%d %H:%M:%S") if ":" in join_date else datetime.strptime(join_date, "%Y-%m-%d")
                days_since_join = max(1, (datetime.now() - join_dt).days)
            except Exception:
                days_since_join = 30
        # Get moods and alerts since join (or 30 days, whichever is less)
        moods = cur.execute(
            "SELECT mood_val, sleep_val, exercise_mins, outside_mins, water_pints, meds, notes, entrestamp FROM mood_logs WHERE username=? AND entrestamp >= datetime('now', ? || ' days') ORDER BY entrestamp DESC",
            (username, f"-{min(days_since_join,30)}"),
        ).fetchall() or []
        alerts = cur.execute(
            "SELECT alert_type, details, created_at FROM alerts WHERE username=? AND created_at >= datetime('now', ? || ' days') ORDER BY created_at DESC",
            (username, f"-{min(days_since_join,30)}"),
        ).fetchall() or []

        # Get latest assessments
        scales = cur.execute(
            "SELECT scale_name, score, severity FROM clinical_scales WHERE username=? ORDER BY entry_timestamp DESC LIMIT 5",
            (username,)
        ).fetchall() or []

        # Get recent therapy chat messages (sample themes)
        # Fix: Accept any session_id for this user (not just _session)
        chat_messages = cur.execute(
            "SELECT message FROM chat_history WHERE session_id LIKE ? AND sender='user' ORDER BY timestamp DESC LIMIT 10",
            (f"{username}_%",)
        ).fetchall() or []

        # Count total therapy sessions
        therapy_sessions_row = cur.execute(
            "SELECT COUNT(DISTINCT session_id) FROM chat_history WHERE session_id LIKE ?",
            (f"{username}_%",)
        ).fetchone()
        therapy_sessions = therapy_sessions_row[0] if therapy_sessions_row and len(therapy_sessions_row) > 0 else 0

        # Get gratitude entries
        gratitude = cur.execute(
            "SELECT entry FROM gratitude_logs WHERE username=? ORDER BY entry_timestamp DESC LIMIT 5",
            (username,)
        ).fetchall() or []

        # Get CBT exercises
        cbt_records = cur.execute(
            "SELECT situation, thought, evidence FROM cbt_records WHERE username=? ORDER BY entry_timestamp DESC LIMIT 5",
            (username,)
        ).fetchall() or []

        # Get clinician notes (especially highlighted ones)
        clinician_notes = cur.execute(
            "SELECT note_text, is_highlighted FROM clinician_notes WHERE patient_username=? ORDER BY created_at DESC LIMIT 5",
            (username,)
        ).fetchall() or []

        conn.close()
        # Log all intermediate results for debugging
        print(f"[AI SUMMARY] moods: {len(moods)}, alerts: {len(alerts)}, scales: {len(scales)}, chat_messages: {len(chat_messages)}, therapy_sessions: {therapy_sessions}, gratitude: {len(gratitude)}, cbt_records: {len(cbt_records)}, clinician_notes: {len(clinician_notes)}")
        
        # Build context for AI
        patient_name = profile[0] if profile and len(profile) > 0 and profile[0] else username
        conditions = profile[1] if profile and len(profile) > 1 and profile[1] else "Not specified"

        avg_mood = sum((m[0] or 0) for m in moods if m and len(m) > 0) / len(moods) if moods else 0
        avg_sleep = sum((m[1] or 0) for m in moods if m and len(m) > 1) / len(moods) if moods else 0
        avg_exercise = sum((m[2] or 0) for m in moods if m and len(m) > 2) / len(moods) if moods else 0
        avg_outside = sum((m[3] or 0) for m in moods if m and len(m) > 3) / len(moods) if moods else 0
        avg_water = sum((m[4] or 0) for m in moods if m and len(m) > 4) / len(moods) if moods else 0

        # Mood trend (recent vs older)
        if len(moods) >= 6:
            recent_mood = sum((m[0] or 0) for m in moods[:3] if m and len(m) > 0) / 3
            older_mood = sum((m[0] or 0) for m in moods[-3:] if m and len(m) > 0) / 3
            mood_trend = "improving" if recent_mood > older_mood else "declining" if recent_mood < older_mood else "stable"
        else:
            mood_trend = "insufficient data"
        
        alert_count = len(alerts)
        gratitude_count = len(gratitude)
        cbt_count = len(cbt_records)
        
        # Build prompt with comprehensive data
        window_desc = f"since joining ({days_since_join} days)" if days_since_join < 30 else "last 30 days"
        prompt = f"""You are an experienced clinical psychologist preparing a comprehensive patient review for a colleague. Generate a detailed, professional clinical summary with clear sections.

PATIENT INFORMATION:
- Name: {patient_name}
- Known Conditions: {conditions}
- Review Period: {window_desc}

QUANTITATIVE DATA:
- Average Mood Score: {avg_mood:.1f}/10 (Trend: {mood_trend})
- Average Sleep Duration: {avg_sleep:.1f} hours/night
- Average Daily Exercise: {avg_exercise:.1f} minutes
- Average Outdoor Time: {avg_outside:.1f} minutes
- Average Water Intake: {avg_water:.1f} pints
- Total Safety Alerts: {alert_count}
- Gratitude Journal Entries: {gratitude_count}
- CBT Exercises Completed: {cbt_count}
- Total Therapy Sessions: {therapy_sessions}

CLINICAL ASSESSMENTS:
{chr(10).join([f"- {s[0] or 'Unknown'}: Score {s[1] or 0} ({s[2] or 'unknown'} severity)" for s in scales]) if scales else "No formal assessments completed yet"}

THERAPY SESSION THEMES (Patient's expressed concerns):
{chr(10).join([f"- {(msg[0] or '')[:150]}" for msg in chat_messages[:7]]) if chat_messages else "No therapy sessions recorded"}

GRATITUDE PRACTICE ENTRIES:
{chr(10).join([f"- {(g[0] or '')[:100]}" for g in gratitude[:5]]) if gratitude else "Patient has not used gratitude journaling"}

CBT THOUGHT RECORDS:
{chr(10).join([f"- Situation: {(c[0] or '')[:80]} | Thought: {(c[1] or '')[:80]}" for c in cbt_records[:5]]) if cbt_records else "No CBT exercises completed"}

PREVIOUS CLINICIAN NOTES:
{chr(10).join([f"- {'[FLAGGED] ' if n[1] else ''}{(n[0] or '')[:150]}" for n in clinician_notes]) if clinician_notes else "No previous clinician notes"}

SAFETY ALERTS:
{chr(10).join([f"- [{a[0] or 'Alert'}] {a[1] or 'No details'}" for a in alerts[:5]]) if alerts else "No safety concerns flagged"}

---

Please provide a COMPREHENSIVE clinical summary with the following sections:

## 1. CLINICAL IMPRESSION
Provide an overall assessment of the patient's current mental health status, integrating all available data sources. Comment on presentation, engagement level, and general functioning.

## 2. MOOD & SLEEP ANALYSIS
Analyze the mood and sleep patterns in detail. Identify any concerning trends, correlations between mood and sleep, and compare to healthy baselines.

## 3. RISK ASSESSMENT
Evaluate any risk factors present including safety alerts, concerning themes in therapy, low mood patterns, or assessment results indicating elevated risk.

## 4. TREATMENT ENGAGEMENT
Assess the patient's engagement with therapeutic activities including therapy sessions, CBT exercises, gratitude practice, and self-care habits (exercise, hydration, outdoor time).

## 5. PROGRESS & STRENGTHS
Highlight positive developments, strengths, protective factors, and areas where the patient is making progress.

## 6. CLINICAL RECOMMENDATIONS
Provide specific, actionable recommendations for ongoing treatment including:
- Therapeutic focus areas
- Suggested interventions
- Monitoring priorities
- Any referral considerations

Be thorough, evidence-based, and clinically specific. Reference the actual data provided."""

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
                        "temperature": 0.4,
                        "max_tokens": 2000
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
    Patient has recorded {len(moods)} mood entries over the {window_desc} with an average mood rating of {avg_mood:.1f}/10. Mood trend appears {mood_trend}. {"⚠️ ALERT: " + str(alert_count) + " safety alerts have been triggered." if alert_count > 0 else "No safety alerts recorded."}

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
        import traceback
        print(f"AI SUMMARY ERROR: {str(e)}")
        traceback.print_exc()
        return handle_exception(e, request.endpoint or 'unknown')

# ===== CLINICIAN NOTES & PDF EXPORT =====
@app.route('/api/professional/notes', methods=['POST'])
@CSRFProtection.require_csrf  # PHASE 2B: CSRF protection
def create_clinician_note():
    """Create a note about a patient (Phase 2A: Input validation added)"""
    try:
        # SECURITY: Get authenticated clinician from session (Phase 1B)
        clinician_username = get_authenticated_username()
        if not clinician_username:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.json
        patient_username = data.get('patient_username')
        note_text = data.get('note_text')
        is_highlighted = data.get('is_highlighted', False)
        
        if not patient_username or not note_text:
            return jsonify({'error': 'Patient username and note text required'}), 400
        
        # PHASE 2A: Input validation
        note_text, note_error = InputValidator.validate_note(note_text)
        if note_error:
            return jsonify({'error': note_error}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()

        # Phase 1B: Verify clinician-patient relationship via FK
        is_valid, _ = verify_clinician_patient_relationship(clinician_username, patient_username)
        if not is_valid:
            conn.close()
            return jsonify({'error': 'Unauthorized: Patient not assigned to clinician'}), 403
        
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
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/professional/notes/<patient_username>', methods=['GET'])
def get_clinician_notes(patient_username):
    """Get all notes for a patient"""
    try:
        # SECURITY: Get authenticated clinician from session (Phase 1B)
        clinician_username = get_authenticated_username()
        if not clinician_username:
            return jsonify({'error': 'Authentication required'}), 401
        
        conn = get_db_connection()
        cur = conn.cursor()

        # Phase 1B: Verify clinician-patient relationship via FK
        is_valid, _ = verify_clinician_patient_relationship(clinician_username, patient_username)
        if not is_valid:
            conn.close()
            return jsonify({'error': 'Unauthorized: Patient not assigned to clinician'}), 403
        
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
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/professional/notes/<int:note_id>', methods=['DELETE'])
def delete_clinician_note(note_id):
    """Delete a clinician note"""
    try:
        # SECURITY: Get authenticated clinician from session (Phase 1A)
        clinician_username = get_authenticated_username()
        if not clinician_username:
            return jsonify({'error': 'Authentication required'}), 401
        
        conn = get_db_connection()
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
        return handle_exception(e, request.endpoint or 'unknown')

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

        conn = get_db_connection()
        cur = conn.cursor()

        # SECURITY: Verify clinician has approved access to this patient
        approval = cur.execute(
            "SELECT status FROM patient_approvals WHERE clinician_username=? AND patient_username=? AND status='approved'",
            (clinician_username, patient_username)
        ).fetchone()

        if not approval:
            conn.close()
            return jsonify({'error': 'Unauthorized: You do not have access to this patient'}), 403

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
    <p style="text-align: center; color: #999; font-size: 11px;">Confidential - Generated by python-chat-bot Therapy App for {clinician_username}</p>
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
        return handle_exception(e, request.endpoint or 'unknown')

# ===== ADMIN / TESTING ENDPOINTS =====
@app.route('/api/admin/reset-users', methods=['POST'])
def reset_all_users():
    """DANGER: Delete all users, approvals, and notifications (for testing only)"""
    try:
        # SECURITY: Block this endpoint in production unless explicitly enabled
        if os.environ.get('FLASK_ENV') == 'production' and not os.environ.get('ALLOW_ADMIN_RESET'):
            return jsonify({'error': 'This endpoint is disabled in production'}), 403

        data = request.json
        confirm = data.get('confirm')
        admin_username = data.get('admin_username')
        admin_password = data.get('admin_password')

        # SECURITY: Require admin authentication
        if not admin_username or not admin_password:
            return jsonify({'error': 'Admin credentials required'}), 401

        # Verify admin credentials and role
        conn = get_db_connection()
        cur = conn.cursor()

        admin = cur.execute(
            "SELECT password, role FROM users WHERE username=?",
            (admin_username,)
        ).fetchone()

        if not admin:
            conn.close()
            return jsonify({'error': 'Invalid admin credentials'}), 401

        # Verify password (using the same hashing as login)
        from werkzeug.security import check_password_hash
        if not check_password_hash(admin[0], admin_password):
            conn.close()
            return jsonify({'error': 'Invalid admin credentials'}), 401

        # Verify admin role
        if admin[1] != 'admin':
            conn.close()
            return jsonify({'error': 'Insufficient privileges: admin role required'}), 403

        # Require explicit confirmation
        if confirm != 'DELETE_ALL_USERS':
            conn.close()
            return jsonify({'error': 'Must provide confirm="DELETE_ALL_USERS" to proceed'}), 400

        # Log the admin action BEFORE deleting
        log_event(admin_username, 'admin', 'database_reset_initiated', 'Admin initiated full database reset')

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

        log_event(admin_username, 'admin', 'database_reset_completed', f'All users and data deleted. Users remaining: {user_count}')

        return jsonify({
            'success': True,
            'message': 'All users and related data deleted',
            'users_remaining': user_count,
            'approvals_remaining': approval_count
        }), 200

    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

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
        
        conn = get_db_connection()
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
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/mood/check-today', methods=['GET'])
def check_mood_today():
    """Check if user has logged mood today"""
    try:
        username = request.args.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = get_db_connection()
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
        return handle_exception(e, request.endpoint or 'unknown')

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
        return handle_exception(e, request.endpoint or 'unknown')

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
        return handle_exception(e, request.endpoint or 'unknown')

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
        return handle_exception(e, request.endpoint or 'unknown')

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
        return handle_exception(e, request.endpoint or 'unknown')

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
        return handle_exception(e, request.endpoint or 'unknown')

# ==================== APPOINTMENT CALENDAR ENDPOINTS ====================

@app.route('/api/appointments', methods=['GET', 'POST'])
def manage_appointments():
    """Get or create appointments"""
    try:
        if request.method == 'GET':
            # Get appointments for clinician or patient
            clinician_username = request.args.get('clinician')
            patient_username = request.args.get('patient')
            
            if not clinician_username and not patient_username:
                return jsonify({'error': 'Clinician or patient username required'}), 400
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            if clinician_username:
                # Get appointments for clinician (show last 30 days and future)
                appointments = cur.execute("""
                    SELECT id, patient_username, appointment_date, appointment_type, notes, 
                           pdf_generated, notification_sent, created_at, patient_acknowledged,
                           patient_response, patient_response_date, attendance_status, attendance_confirmed_by, attendance_confirmed_at
                    FROM appointments 
                    WHERE clinician_username=? AND appointment_date >= datetime('now', '-30 days')
                    ORDER BY appointment_date DESC
                """, (clinician_username,)).fetchall()
            else:
                # Get appointments for patient
                appointments = cur.execute("""
                    SELECT id, clinician_username, appointment_date, appointment_type, notes, 
                           pdf_generated, notification_sent, created_at, patient_acknowledged,
                           patient_response, patient_response_date, attendance_status, attendance_confirmed_by, attendance_confirmed_at
                    FROM appointments 
                    WHERE patient_username=? AND appointment_date >= datetime('now', '-7 days')
                    ORDER BY appointment_date ASC
                """, (patient_username,)).fetchall()
            
            conn.close()
            
            results = []
            for apt in appointments:
                result = {
                    'id': apt[0],
                    'appointment_date': apt[2],
                    'appointment_type': apt[3],
                    'notes': apt[4],
                    'pdf_generated': bool(apt[5]),
                    'notification_sent': bool(apt[6]),
                    'created_at': apt[7],
                    'patient_acknowledged': bool(apt[8]),
                    'patient_response': apt[9] or 'pending',
                    'patient_response_date': apt[10],
                    'attendance_status': apt[11] or 'scheduled',
                    'attendance_confirmed_by': apt[12],
                    'attendance_confirmed_at': apt[13]
                }
                
                if clinician_username:
                    result['patient_username'] = apt[1]
                else:
                    result['clinician_username'] = apt[1]
                
                results.append(result)
            
            return jsonify({'appointments': results}), 200
            
        elif request.method == 'POST':
            # Create new appointment
            data = request.json
            clinician = data.get('clinician_username')
            patient = data.get('patient_username')
            appt_date = data.get('appointment_date')
            notes = data.get('notes', '')
            
            if not all([clinician, patient, appt_date]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO appointments (clinician_username, patient_username, appointment_date, notes, patient_response)
                VALUES (?, ?, ?, ?, ?)
            """, (clinician, patient, appt_date, notes, 'pending'))
            appt_id = cur.lastrowid
            
            # Send notification to patient
            from datetime import datetime as dt
            appt_datetime = dt.fromisoformat(appt_date.replace('Z', '+00:00'))
            date_str = appt_datetime.strftime('%A, %d %B %Y at %H:%M')
            cur.execute("""
                INSERT INTO notifications (recipient_username, message, notification_type)
                VALUES (?, ?, ?)
            """, (patient, f'New appointment scheduled with {clinician} on {date_str}. Please view and respond in the Appointments tab.', 'appointment_new'))
            
            conn.commit()
            conn.close()
            
            log_event(clinician, 'clinician', 'appointment_booked', f'Booked with {patient}')
            
            return jsonify({
                'success': True,
                'appointment_id': appt_id,
                'message': 'Appointment created and patient notified'
            }), 201
            
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/appointments/<int:appointment_id>', methods=['DELETE'])
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get appointment details before deleting
        apt = cur.execute(
            "SELECT patient_username, clinician_username, appointment_date, appointment_time FROM appointments WHERE id=?",
            (appointment_id,)
        ).fetchone()
        
        if apt:
            patient_username, clinician_username, apt_date, apt_time = apt
            
            # Delete the appointment
            cur.execute("DELETE FROM appointments WHERE id=?", (appointment_id,))
            
            # Send notification to patient
            cur.execute(
                "INSERT INTO notifications (username, message, read) VALUES (?, ?, 0)",
                (patient_username, f"Your appointment on {apt_date} at {apt_time} with {clinician_username} has been cancelled.")
            )
            
            conn.commit()
            conn.close()
            
            return jsonify({'success': True, 'message': 'Appointment cancelled and patient notified'}), 200
        else:
            conn.close()
            return jsonify({'error': 'Appointment not found'}), 404
        
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/appointments/<int:appointment_id>/respond', methods=['POST'])
def respond_to_appointment(appointment_id):
    """Patient acknowledges and responds to appointment (accept/decline)"""
    try:
        data = request.json
        patient_username = data.get('patient_username')
        acknowledged = data.get('acknowledged', False)
        response = data.get('response')  # 'accepted' or 'declined'
        
        if not patient_username:
            return jsonify({'error': 'Patient username required'}), 400
        
        if not acknowledged:
            return jsonify({'error': 'You must acknowledge reading the appointment'}), 400
        
        if response not in ['accepted', 'declined']:
            return jsonify({'error': 'Response must be accepted or declined'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verify appointment belongs to patient
        apt = cur.execute(
            "SELECT clinician_username FROM appointments WHERE id=? AND patient_username=?",
            (appointment_id, patient_username)
        ).fetchone()
        
        if not apt:
            conn.close()
            return jsonify({'error': 'Appointment not found'}), 404
        
        # Update appointment
        cur.execute("""
            UPDATE appointments 
            SET patient_acknowledged=1, patient_response=?, patient_response_date=?
            WHERE id=?
        """, (response, datetime.now(), appointment_id))
        
        # Notify clinician
        clinician = apt[0]
        action = 'accepted' if response == 'accepted' else 'declined'
        cur.execute("""
            INSERT INTO notifications (recipient_username, message, notification_type)
            VALUES (?, ?, ?)
        """, (clinician, f'{patient_username} has {action} the appointment', 'appointment_response'))
        
        conn.commit()
        conn.close()
        
        log_event(patient_username, 'api', f'appointment_{action}', f'Appointment ID: {appointment_id}')
        
        return jsonify({
            'success': True,
            'message': f'Appointment {action} successfully'
        }), 200
        
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')


@app.route('/api/appointments/<int:appointment_id>/attendance', methods=['POST'])
def confirm_appointment_attendance(appointment_id):
    """Clinician confirms whether a patient attended an appointment"""
    try:
        data = request.json
        clinician_username = data.get('clinician_username')
        status = data.get('status')  # 'attended' or 'no_show' or 'missed'

        if not clinician_username or not status:
            return jsonify({'error': 'clinician_username and status are required'}), 400

        if status not in ['attended', 'no_show', 'missed']:
            return jsonify({'error': "status must be one of: 'attended', 'no_show', 'missed'"}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Verify appointment and clinician ownership
        apt = cur.execute(
            "SELECT patient_username, clinician_username FROM appointments WHERE id=?",
            (appointment_id,)
        ).fetchone()

        if not apt:
            conn.close()
            return jsonify({'error': 'Appointment not found'}), 404

        patient_username, owner = apt
        if owner != clinician_username:
            conn.close()
            return jsonify({'error': 'Clinician not authorised for this appointment'}), 403

        # Update attendance fields
        cur.execute(
            "UPDATE appointments SET attendance_status=?, attendance_confirmed_by=?, attendance_confirmed_at=? WHERE id=?",
            (status, clinician_username, datetime.now(), appointment_id)
        )

        # Notify patient of attendance status
        message = ''
        if status == 'attended':
            message = f'Your clinician {clinician_username} has confirmed you attended the appointment.'
        else:
            message = f'Your clinician {clinician_username} has marked the appointment as {status}.'

        cur.execute(
            "INSERT INTO notifications (recipient_username, message, notification_type) VALUES (?,?,?)",
            (patient_username, message, 'appointment_attendance')
        )

        conn.commit()
        conn.close()

        log_event(clinician_username, 'clinician', 'appointment_attendance_confirmed', f'Appointment {appointment_id} marked {status}')

        return jsonify({'success': True, 'message': f'Appointment marked {status}'}), 200

    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/patient/profile', methods=['GET', 'PUT'])
def patient_profile():
    """Get or update patient profile (About Me)"""
    try:
        username = request.args.get('username') if request.method == 'GET' else request.json.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        if request.method == 'GET':
            # Get profile
            profile = cur.execute("""
                SELECT full_name, dob, email, phone, conditions, clinician_id
                FROM users WHERE username=?
            """, (username,)).fetchone()
            
            if not profile:
                conn.close()
                return jsonify({'error': 'User not found'}), 404
            
            # Get statistics
            mood_count = cur.execute("SELECT COUNT(*) FROM mood_logs WHERE username=?", (username,)).fetchone()[0]
            grat_count = cur.execute("SELECT COUNT(*) FROM gratitude_logs WHERE username=?", (username,)).fetchone()[0]
            cbt_count = cur.execute("SELECT COUNT(*) FROM cbt_records WHERE username=?", (username,)).fetchone()[0]
            session_count = cur.execute("SELECT COUNT(*) FROM sessions WHERE username=?", (username,)).fetchone()[0]
            
            # Get clinician info if assigned
            clinician_info = None
            if profile[5]:  # clinician_id exists
                clinician = cur.execute("""
                    SELECT full_name, email FROM users WHERE username=? AND role='clinician'
                """, (profile[5],)).fetchone()
                if clinician:
                    try:
                        clinician_info = {
                            'name': decrypt_text(clinician[0]) if clinician[0] else profile[5],
                            'email': decrypt_text(clinician[1]) if clinician[1] else None
                        }
                    except:
                        clinician_info = {'name': profile[5], 'email': None}
            
            conn.close()
            
            return jsonify({
                'profile': {
                    'username': username,
                    'full_name': decrypt_text(profile[0]) if profile[0] else '',
                    'dob': decrypt_text(profile[1]) if profile[1] else '',
                    'email': decrypt_text(profile[2]) if profile[2] else '',
                    'phone': decrypt_text(profile[3]) if profile[3] else '',
                    'conditions': decrypt_text(profile[4]) if profile[4] else '',
                    'assigned_clinician': clinician_info['name'] if clinician_info else None,
                    'clinician_email': clinician_info['email'] if clinician_info else None
                },
                'stats': {
                    'mood_logs': mood_count,
                    'gratitude_entries': grat_count,
                    'cbt_entries': cbt_count,
                    'therapy_sessions': session_count
                }
            }), 200
            
        elif request.method == 'PUT':
            # Update profile
            data = request.json
            
            cur.execute("""
                UPDATE users SET full_name=?, dob=?, email=?, phone=?, conditions=?
                WHERE username=?
            """, (
                encrypt_text(data.get('full_name', '')),
                encrypt_text(data.get('dob', '')),
                encrypt_text(data.get('email', '')),
                encrypt_text(data.get('phone', '')),
                encrypt_text(data.get('conditions', '')),
                username
            ))
            conn.commit()
            conn.close()
            
            log_event(username, 'user', 'profile_updated', 'Updated via API')
            
            return jsonify({'success': True, 'message': 'Profile updated'}), 200
            
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# ==================== ANALYTICS ENDPOINTS ====================

@app.route('/api/analytics/dashboard', methods=['GET'])
def get_analytics_dashboard():
    """Get comprehensive analytics for clinician dashboard"""
    try:
        clinician = request.args.get('clinician')
        if not clinician:
            return jsonify({'error': 'Clinician username required'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get clinician's APPROVED patients from patient_approvals table
        patients = cur.execute("""
            SELECT u.username FROM users u
            JOIN patient_approvals pa ON u.username = pa.patient_username
            WHERE pa.clinician_username=? AND pa.status='approved'
        """, (clinician,)).fetchall()
        
        patient_usernames = [p[0] for p in patients]
        
        if not patient_usernames:
            conn.close()
            return jsonify({
                'total_patients': 0,
                'active_patients': 0,
                'high_risk_count': 0,
                'mood_trends': [],
                'engagement_data': [],
                'assessment_summary': {}
            }), 200
        
        # Total and active patients (logged in last 7 days)
        # Check last_login, mood_logs and chat_history for recent activity
        placeholders = ','.join(['?'] * len(patient_usernames))
        
        # Get active patients from last_login, mood logs or chat activity
        active = cur.execute(f"""
            SELECT COUNT(DISTINCT username) FROM (
                SELECT username FROM users
                WHERE username IN ({placeholders})
                AND datetime(last_login) > datetime('now', '-7 days')
                UNION
                SELECT username FROM mood_logs 
                WHERE username IN ({placeholders}) 
                AND datetime(entrestamp) > datetime('now', '-7 days')
                UNION
                SELECT sender as username FROM chat_history 
                WHERE sender IN ({placeholders}) 
                AND datetime(timestamp) > datetime('now', '-7 days')
            )
        """, patient_usernames + patient_usernames + patient_usernames).fetchone()[0]
        
        # High risk count (from alerts table - using status column)
        high_risk = cur.execute(f"""
            SELECT COUNT(DISTINCT username) FROM alerts 
            WHERE username IN ({placeholders}) 
            AND (status IS NULL OR status != 'resolved')
        """, patient_usernames).fetchone()[0]
        
        # Mood trends over last 30 days
        mood_data = cur.execute(f"""
            SELECT DATE(entrestamp) as date, AVG(mood_val) as avg_mood, COUNT(*) as count
            FROM mood_logs
            WHERE username IN ({placeholders})
            AND datetime(entrestamp) > datetime('now', '-30 days')
            GROUP BY DATE(entrestamp)
            ORDER BY date
        """, patient_usernames).fetchall()
        
        # Engagement metrics (recent activity per patient in last 7 days)
        engagement = cur.execute(f"""
            SELECT username, 
                   (SELECT COUNT(*) FROM mood_logs ml WHERE ml.username = u.username 
                    AND datetime(ml.entrestamp) > datetime('now', '-7 days')) as mood_count,
                   (SELECT MAX(entrestamp) FROM mood_logs ml WHERE ml.username = u.username) as last_active
            FROM users u
            WHERE u.username IN ({placeholders})
            ORDER BY mood_count DESC
        """, patient_usernames).fetchall()
        
        # Assessment score summary (latest PHQ-9 and GAD-7)
        assessment_summary = {
            'phq9': {'severe': 0, 'moderate': 0, 'mild': 0, 'minimal': 0},
            'gad7': {'severe': 0, 'moderate': 0, 'mild': 0, 'minimal': 0}
        }
        
        for username in patient_usernames:
            # Latest PHQ-9
            phq9 = cur.execute("""
                SELECT score FROM clinical_scales
                WHERE username=? AND scale_name='PHQ-9'
                ORDER BY entry_timestamp DESC LIMIT 1
            """, (username,)).fetchone()
            
            if phq9:
                score = phq9[0]
                if score >= 20:
                    assessment_summary['phq9']['severe'] += 1
                elif score >= 15:
                    assessment_summary['phq9']['moderate'] += 1
                elif score >= 10:
                    assessment_summary['phq9']['mild'] += 1
                else:
                    assessment_summary['phq9']['minimal'] += 1
            
            # Latest GAD-7
            gad7 = cur.execute("""
                SELECT score FROM clinical_scales
                WHERE username=? AND scale_name='GAD-7'
                ORDER BY entry_timestamp DESC LIMIT 1
            """, (username,)).fetchone()
            
            if gad7:
                score = gad7[0]
                if score >= 15:
                    assessment_summary['gad7']['severe'] += 1
                elif score >= 10:
                    assessment_summary['gad7']['moderate'] += 1
                elif score >= 5:
                    assessment_summary['gad7']['mild'] += 1
                else:
                    assessment_summary['gad7']['minimal'] += 1
        
        conn.close()
        
        return jsonify({
            'total_patients': len(patient_usernames),
            'active_patients': active,
            'high_risk_count': high_risk,
            'mood_trends': [
                {
                    'date': row[0],
                    'avg_mood': round(row[1], 1) if row[1] else 0,
                    'count': row[2]
                } for row in mood_data
            ],
            'engagement_data': [
                {
                    'username': row[0],
                    'session_count': row[1],  # Actually mood log count
                    'last_active': row[2] if row[2] else 'Never'
                } for row in engagement
            ],
            'assessment_summary': assessment_summary
        }), 200
        
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/analytics/active-patients', methods=['GET'])
def get_active_patients():
    """Get list of active patients with last activity timestamps"""
    try:
        clinician = request.args.get('clinician')
        if not clinician:
            return jsonify({'error': 'Clinician username required'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get clinician's approved patients
        patients = cur.execute("""
            SELECT u.username, u.full_name FROM users u
            JOIN patient_approvals pa ON u.username = pa.patient_username
            WHERE pa.clinician_username=? AND pa.status='approved'
        """, (clinician,)).fetchall()
        
        active_patients = []
        
        for patient in patients:
            username = patient[0]
            full_name = patient[1]
            
            # Get most recent activity from multiple sources
            last_login = cur.execute(
                "SELECT last_login FROM users WHERE username=?",
                (username,)
            ).fetchone()[0]
            
            last_mood = cur.execute(
                "SELECT MAX(entrestamp) FROM mood_logs WHERE username=?",
                (username,)
            ).fetchone()[0]
            
            last_chat = cur.execute(
                "SELECT MAX(timestamp) FROM chat_history WHERE sender=?",
                (username,)
            ).fetchone()[0]
            
            # Get the most recent activity
            activities = [
                ('login', last_login),
                ('mood_log', last_mood),
                ('chat', last_chat)
            ]
            
            # Filter out None and get most recent
            recent_activities = [(act_type, ts) for act_type, ts in activities if ts]
            if recent_activities:
                recent_activities.sort(key=lambda x: x[1], reverse=True)
                last_activity_type = recent_activities[0][0]
                last_activity_time = recent_activities[0][1]
                
                # Check if active in last 7 days
                seven_days_ago = cur.execute(
                    "SELECT datetime('now', '-7 days')"
                ).fetchone()[0]
                
                if last_activity_time > seven_days_ago:
                    active_patients.append({
                        'username': username,
                        'full_name': full_name,
                        'last_activity': last_activity_time,
                        'activity_type': last_activity_type
                    })
        
        # Sort by most recent activity
        active_patients.sort(key=lambda x: x['last_activity'], reverse=True)
        
        conn.close()
        
        return jsonify({
            'active_patients': active_patients,
            'total_active': len(active_patients)
        }), 200
        
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

@app.route('/api/analytics/patient/<username>', methods=['GET'])
def get_patient_analytics(username):
    """Phase 1B: Get detailed analytics for specific patient with FK validation"""
    try:
        # SECURITY: Get authenticated clinician from session
        clinician_username = get_authenticated_username()
        if not clinician_username:
            return jsonify({'error': 'Authentication required'}), 401

        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verify user is a clinician
        clinician = cur.execute(
            "SELECT role FROM users WHERE username=?",
            (clinician_username,)
        ).fetchone()
        
        if not clinician or clinician[0] != 'clinician':
            conn.close()
            return jsonify({'error': 'Clinician role required'}), 403

        # Phase 1B: Verify clinician-patient relationship via FK
        is_valid, _ = verify_clinician_patient_relationship(clinician_username, username)
        if not is_valid:
            conn.close()
            return jsonify({'error': 'Unauthorized: Patient not assigned to clinician'}), 403

        # Mood trend (last 90 days)
        mood_trend = cur.execute("""
            SELECT DATE(entrestamp) as date, mood_val, notes
            FROM mood_logs
            WHERE username=?
            AND datetime(entrestamp) > datetime('now', '-90 days')
            ORDER BY date
        """, (username,)).fetchall()
        
        # Assessment scores over time
        assessments = cur.execute("""
            SELECT scale_name, score, entry_timestamp
            FROM clinical_scales
            WHERE username=?
            ORDER BY entry_timestamp DESC
            LIMIT 20
        """, (username,)).fetchall()
        
        # Activity metrics
        activity = cur.execute("""
            SELECT 
                (SELECT COUNT(*) FROM sessions WHERE username=?) as total_sessions,
                (SELECT COUNT(*) FROM mood_logs WHERE username=?) as mood_logs,
                (SELECT COUNT(*) FROM gratitude_logs WHERE username=?) as gratitude_logs,
                (SELECT COUNT(*) FROM cbt_records WHERE username=?) as cbt_records,
                (SELECT MAX(created_at) FROM sessions WHERE username=?) as last_active
        """, (username, username, username, username, username)).fetchone()
        
        # Risk indicators
        risk_data = cur.execute("""
            SELECT COUNT(*) as alert_count, MAX(created_at) as last_alert
            FROM alerts
            WHERE username=? AND (status IS NULL OR status != 'resolved')
        """, (username,)).fetchone()

        # Upcoming appointments (next 30 days)
        upcoming = cur.execute("""
            SELECT id, clinician_username, appointment_date, appointment_type, notes, attendance_status, attendance_confirmed_by, attendance_confirmed_at
            FROM appointments
            WHERE patient_username=? AND datetime(appointment_date) >= datetime('now')
            ORDER BY datetime(appointment_date) ASC
            LIMIT 10
        """, (username,)).fetchall()

        # Recent past appointments (last 7 days) to allow clinicians to confirm attendance
        recent_past = cur.execute("""
            SELECT id, clinician_username, appointment_date, appointment_type, notes, attendance_status, attendance_confirmed_by, attendance_confirmed_at
            FROM appointments
            WHERE patient_username=? AND datetime(appointment_date) < datetime('now') AND datetime(appointment_date) >= datetime('now', '-7 days')
            ORDER BY datetime(appointment_date) DESC
            LIMIT 10
        """, (username,)).fetchall()
        
        conn.close()

        return jsonify({
            'mood_trend': [
                {'date': row[0], 'score': row[1], 'notes': row[2]}
                for row in mood_trend
            ],
            'assessments': [
                {'type': row[0], 'score': row[1], 'date': row[2]}
                for row in assessments
            ],
            'activity': {
                'total_sessions': activity[0] or 0,
                'mood_logs': activity[1] or 0,
                'gratitude_logs': activity[2] or 0,
                'cbt_records': activity[3] or 0,
                'last_active': activity[4]
            },
            'risk': {
                'active_alerts': risk_data[0] or 0,
                'last_alert': risk_data[1]
            }
            ,
            'upcoming_appointments': [
                {
                    'id': r[0],
                    'clinician_username': r[1],
                    'appointment_date': r[2],
                    'appointment_type': r[3],
                    'notes': r[4],
                    'attendance_status': r[5],
                    'attendance_confirmed_by': r[6],
                    'attendance_confirmed_at': r[7]
                } for r in upcoming
            ],
            'recent_past_appointments': [
                {
                    'id': r[0],
                    'clinician_username': r[1],
                    'appointment_date': r[2],
                    'appointment_type': r[3],
                    'notes': r[4],
                    'attendance_status': r[5],
                    'attendance_confirmed_by': r[6],
                    'attendance_confirmed_at': r[7]
                } for r in recent_past
            ]
        }), 200
        
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# ==================== REPORT GENERATOR ENDPOINTS ====================

@app.route('/api/reports/generate', methods=['POST'])
def generate_clinical_report():
    """Generate clinical report for patient"""
    try:
        data = request.json
        username = data.get('username')
        report_type = data.get('report_type')  # 'gp_referral', 'progress', 'discharge'
        clinician = data.get('clinician')

        if not all([username, report_type, clinician]):
            return jsonify({'error': 'Missing required fields'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # SECURITY: Verify clinician has approved access to this patient
        approval = cur.execute(
            "SELECT status FROM patient_approvals WHERE clinician_username=? AND patient_username=? AND status='approved'",
            (clinician, username)
        ).fetchone()

        if not approval:
            conn.close()
            return jsonify({'error': 'Unauthorized: You do not have access to this patient'}), 403

        # Get patient info
        patient = cur.execute("""
            SELECT full_name, dob, email, phone, conditions, created_at
            FROM users WHERE username=?
        """, (username,)).fetchone()

        if not patient:
            conn.close()
            return jsonify({'error': 'Patient not found'}), 404
        
        # Decrypt patient data
        full_name = decrypt_text(patient[0]) if patient[0] else username
        dob = decrypt_text(patient[1]) if patient[1] else 'Not provided'
        conditions = decrypt_text(patient[4]) if patient[4] else 'None recorded'
        
        # Get latest assessments
        phq9 = cur.execute("""
            SELECT score, entry_timestamp FROM clinical_scales
            WHERE username=? AND scale_name='PHQ-9'
            ORDER BY entry_timestamp DESC LIMIT 1
        """, (username,)).fetchone()
        
        gad7 = cur.execute("""
            SELECT score, entry_timestamp FROM clinical_scales
            WHERE username=? AND scale_name='GAD-7'
            ORDER BY entry_timestamp DESC LIMIT 1
        """, (username,)).fetchone()
        
        # Get clinician notes
        notes = cur.execute("""
            SELECT note_text, created_at, is_highlighted
            FROM clinician_notes
            WHERE patient_username=?
            ORDER BY created_at DESC
            LIMIT 10
        """, (username,)).fetchall()
        
        # Get mood average (using correct column names: mood_val and entrestamp)
        mood_avg = cur.execute("""
            SELECT AVG(mood_val) FROM mood_logs
            WHERE username=?
            AND datetime(entrestamp) > datetime('now', '-30 days')
        """, (username,)).fetchone()[0]
        
        conn.close()
        
        # Generate report content
        from datetime import datetime
        report_date = datetime.now().strftime('%d %B %Y')
        
        if report_type == 'gp_referral':
            report_content = f"""
REFERRAL LETTER TO GP

Date: {report_date}
Clinician: {clinician}

RE: {full_name}
DOB: {dob}
Patient ID: {username}

Dear Doctor,

I am writing to refer the above-named patient for your consideration and ongoing care.

PRESENTING CONCERNS:
{conditions}

ASSESSMENT FINDINGS:
- PHQ-9 Score: {phq9[0] if phq9 else 'Not completed'} ({phq9[1] if phq9 else ''})
- GAD-7 Score: {gad7[0] if gad7 else 'Not completed'} ({gad7[1] if gad7 else ''})
- Average Mood (30 days): {round(mood_avg, 1) if mood_avg else 'No data'}/10

CLINICAL NOTES:
"""
            for note in notes[:5]:
                report_content += f"- {note[1]}: {note[0]}\n"
            
            report_content += f"""

RECOMMENDATION:
Patient would benefit from continued monitoring and support for mental health concerns.

Yours sincerely,
{clinician}
Mental Health Clinician
"""
        
        elif report_type == 'progress':
            report_content = f"""
PROGRESS REPORT

Patient: {full_name}
DOB: {dob}
Report Date: {report_date}
Clinician: {clinician}

CURRENT STATUS:
- Recent PHQ-9: {phq9[0] if phq9 else 'Not completed'}
- Recent GAD-7: {gad7[0] if gad7 else 'Not completed'}
- Average Mood: {round(mood_avg, 1) if mood_avg else 'No data'}/10
- Medical History: {conditions}

PROGRESS NOTES:
"""
            for note in notes:
                marker = '[HIGHLIGHTED] ' if note[2] else ''
                report_content += f"{marker}{note[1]}: {note[0]}\n\n"
        
        elif report_type == 'discharge':
            report_content = f"""
DISCHARGE SUMMARY

Patient: {full_name}
DOB: {dob}
Discharge Date: {report_date}
Clinician: {clinician}

TREATMENT SUMMARY:
Patient has been under care from {patient[5]}.

FINAL ASSESSMENT:
- PHQ-9: {phq9[0] if phq9 else 'Not completed'}
- GAD-7: {gad7[0] if gad7 else 'Not completed'}
- Average Mood: {round(mood_avg, 1) if mood_avg else 'No data'}/10

DISCHARGE PLAN:
Patient discharged with recommendations for self-care and monitoring.

FOLLOW-UP RECOMMENDATIONS:
- Continue self-monitoring
- Contact GP if symptoms worsen
- Return to service if needed

{clinician}
Mental Health Clinician
"""
        
        log_event(clinician, 'clinician', 'report_generated', f'{report_type} for {username}')
        
        return jsonify({
            'success': True,
            'report_content': report_content,
            'report_type': report_type,
            'patient': username
        }), 200
        
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# ==================== SEARCH & FILTER ENDPOINTS ====================

@app.route('/api/patients/search', methods=['GET'])
def search_patients():
    """Search and filter patients"""
    try:
        clinician = request.args.get('clinician')
        search_query = request.args.get('q', '')
        filter_type = request.args.get('filter')  # 'high_risk', 'inactive', 'all'

        if not clinician:
            return jsonify({'error': 'Clinician username required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # SECURITY: Base query uses patient_approvals table to ensure proper authorization
        # Only return patients that the clinician has APPROVED access to
        query = """
            SELECT DISTINCT u.username, u.full_name, u.email, u.created_at,
                   (SELECT COUNT(*) FROM alerts WHERE username=u.username AND (status IS NULL OR status != 'resolved')) as alert_count,
                   (SELECT MAX(created_at) FROM sessions WHERE username=u.username) as last_active,
                   (SELECT score FROM clinical_scales WHERE username=u.username AND scale_name='PHQ-9' ORDER BY entry_timestamp DESC LIMIT 1) as phq9_score
            FROM users u
            JOIN patient_approvals pa ON u.username = pa.patient_username
            WHERE pa.clinician_username=? AND pa.status='approved' AND u.role='user'
        """
        params = [clinician]

        # Add search filter
        if search_query:
            query += " AND (u.username LIKE ? OR u.full_name LIKE ? OR u.email LIKE ?)"
            search_term = f'%{search_query}%'
            params.extend([search_term, search_term, search_term])

        # Add type filter
        if filter_type == 'high_risk':
            query += " AND (SELECT COUNT(*) FROM alerts WHERE username=u.username AND (status IS NULL OR status != 'resolved')) > 0"
        elif filter_type == 'inactive':
            query += " AND ((SELECT MAX(created_at) FROM sessions WHERE username=u.username) < datetime('now', '-7 days') OR (SELECT MAX(created_at) FROM sessions WHERE username=u.username) IS NULL)"

        query += " ORDER BY alert_count DESC, last_active DESC"

        patients = cur.execute(query, params).fetchall()
        conn.close()
        
        results = []
        for p in patients:
            full_name = decrypt_text(p[1]) if p[1] else p[0]
            email = decrypt_text(p[2]) if p[2] else ''
            
            results.append({
                'username': p[0],
                'full_name': full_name,
                'email': email,
                'created_at': p[3],
                'alert_count': p[4] or 0,
                'last_active': p[5],
                'phq9_score': p[6],
                'risk_level': 'high' if p[4] and p[4] > 0 else ('moderate' if p[6] and p[6] >= 15 else 'low')
            })
        
        return jsonify({
            'patients': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        return handle_exception(e, request.endpoint or 'unknown')

# ==================== HOME TAB ENDPOINTS ====================

@app.route('/api/home/data', methods=['GET'])
def get_home_data():
    """Get consolidated home tab data including welcome info, tasks, and streaks"""
    try:
        username = request.args.get('username') or get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401

        conn = get_db_connection()
        cur = conn.cursor()

        # Get last login
        user = cur.execute("SELECT last_login FROM users WHERE username=?", (username,)).fetchone()
        last_login = user[0] if user else None

        # Get today's completed tasks
        today = datetime.now().strftime('%Y-%m-%d')
        tasks = cur.execute(
            "SELECT task_type, completed_at FROM daily_tasks WHERE username=? AND task_date=? AND completed=1",
            (username, today)
        ).fetchall()

        # Get streak info
        streak = cur.execute(
            "SELECT current_streak, longest_streak, last_complete_date FROM daily_streaks WHERE username=?",
            (username,)
        ).fetchone()

        # Get pet info for quick display
        pet_conn = get_pet_db_connection()
        pet_cur = pet_conn.cursor()
        pet = pet_cur.execute("SELECT name, coins, xp, stage FROM pet WHERE username=?", (username,)).fetchone()
        pet_conn.close()

        conn.close()

        return jsonify({
            'success': True,
            'last_login': last_login,
            'daily_tasks': [{'task_type': t[0], 'completed_at': t[1]} for t in tasks],
            'streak': {
                'current': streak[0] if streak else 0,
                'longest': streak[1] if streak else 0,
                'last_complete': streak[2] if streak else None
            },
            'pet': {
                'name': pet[0] if pet else None,
                'coins': pet[1] if pet else 0,
                'xp': pet[2] if pet else 0,
                'stage': pet[3] if pet else None
            } if pet else None
        }), 200

    except Exception as e:
        return handle_exception(e, 'get_home_data')


@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback to developers"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.json
        category = data.get('category')
        message = data.get('message', '').strip()

        if not category or not message:
            return jsonify({'error': 'Category and message are required'}), 400

        if len(message) > 5000:
            return jsonify({'error': 'Message too long (max 5000 characters)'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Get user role
        user = cur.execute("SELECT role FROM users WHERE username=?", (username,)).fetchone()
        role = user[0] if user else 'user'

        cur.execute(
            "INSERT INTO feedback (username, role, category, message) VALUES (?, ?, ?, ?)",
            (username, role, category, message)
        )
        
        feedback_id = cur.lastrowid
        conn.commit()

        # Send notification to all developers
        try:
            developers = cur.execute("SELECT username FROM users WHERE role='developer'").fetchall()
            emoji = {'bug': '🐛', 'feature': '⭐', 'improvement': '📈', 'other': '💬'}.get(category, '📝')
            message_preview = message[:50] + '...' if len(message) > 50 else message
            
            for dev in developers:
                dev_username = dev[0]
                send_notification(
                    dev_username,
                    f"New {category.lower()}: {emoji} {message_preview} (from {username})",
                    'feedback_notification'
                )
        except Exception as notif_error:
            print(f"Failed to send developer notifications: {notif_error}")

        log_event(username, 'api', 'feedback_submitted', f'Category: {category}')
        conn.close()

        return jsonify({'success': True, 'message': 'Feedback submitted successfully'}), 201

    except Exception as e:
        return handle_exception(e, 'submit_feedback')


@app.route('/api/feedback', methods=['GET'])
def get_user_feedback():
    """Get feedback history for the authenticated user"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401

        conn = get_db_connection()
        cur = conn.cursor()

        feedback = cur.execute(
            "SELECT id, category, message, status, created_at FROM feedback WHERE username=? ORDER BY created_at DESC LIMIT 50",
            (username,)
        ).fetchall()

        conn.close()

        return jsonify({
            'success': True,
            'feedback': [
                {'id': f[0], 'category': f[1], 'message': f[2], 'status': f[3], 'created_at': f[4]}
                for f in feedback
            ]
        }), 200

    except Exception as e:
        return handle_exception(e, 'get_user_feedback')


@app.route('/api/daily-tasks/complete', methods=['POST'])
def complete_daily_task():
    """Mark a daily task as complete"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.json
        task_type = data.get('task_type')

        valid_tasks = ['log_mood', 'practice_gratitude', 'check_pet', 'breathing_exercise', 'therapy_session', 'read_resource']
        if not task_type or task_type not in valid_tasks:
            return jsonify({'error': f'Invalid task type. Must be one of: {", ".join(valid_tasks)}'}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')

        # Check if already completed today
        existing = cur.execute(
            "SELECT id FROM daily_tasks WHERE username=? AND task_type=? AND task_date=?",
            (username, task_type, today)
        ).fetchone()

        if existing:
            # Update existing record
            cur.execute(
                "UPDATE daily_tasks SET completed=1, completed_at=datetime('now') WHERE id=?",
                (existing[0],)
            )
        else:
            # Insert new record
            cur.execute(
                "INSERT INTO daily_tasks (username, task_type, completed, completed_at, task_date) VALUES (?, ?, 1, datetime('now'), ?)",
                (username, task_type, today)
            )

        # Check if all tasks completed today
        completed_count = cur.execute(
            "SELECT COUNT(DISTINCT task_type) FROM daily_tasks WHERE username=? AND task_date=? AND completed=1",
            (username, today)
        ).fetchone()[0]

        bonus_awarded = False
        if completed_count >= 6:  # All 6 tasks completed
            bonus_awarded = award_daily_completion_bonus(username, cur, today)

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'task_type': task_type,
            'completed_count': completed_count,
            'total_tasks': 6,
            'bonus_awarded': bonus_awarded
        }), 200

    except Exception as e:
        return handle_exception(e, 'complete_daily_task')


def award_daily_completion_bonus(username, cursor, today):
    """Award bonus for completing all daily tasks"""
    try:
        # Check streak record
        streak = cursor.execute(
            "SELECT current_streak, longest_streak, last_complete_date FROM daily_streaks WHERE username=?",
            (username,)
        ).fetchone()

        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        if streak:
            last_date = streak[2]

            if last_date == today:
                return False  # Already awarded today

            if last_date == yesterday:
                new_streak = streak[0] + 1
            else:
                new_streak = 1

            cursor.execute('''
                UPDATE daily_streaks
                SET current_streak=?, last_complete_date=?,
                    longest_streak=MAX(longest_streak, ?),
                    total_bonus_coins=total_bonus_coins+50,
                    total_bonus_xp=total_bonus_xp+100
                WHERE username=?
            ''', (new_streak, today, new_streak, username))
        else:
            cursor.execute('''
                INSERT INTO daily_streaks (username, current_streak, longest_streak, last_complete_date, total_bonus_coins, total_bonus_xp)
                VALUES (?, 1, 1, ?, 50, 100)
            ''', (username, today))

        # Award pet bonus (50 coins, 100 XP, +10 happiness)
        try:
            pet_conn = get_pet_db_connection()
            pet_cur = pet_conn.cursor()
            pet_cur.execute('''
                UPDATE pet SET coins=coins+50, xp=xp+100, happiness=MIN(100, happiness+10)
                WHERE id=?
            ''', (username,))
            pet_conn.commit()
            pet_conn.close()
        except Exception:
            pass  # Pet bonus is optional

        log_event(username, 'daily', 'daily_bonus_awarded', f'Streak updated, +50 coins, +100 XP')
        return True

    except Exception as e:
        print(f"Error awarding daily bonus: {e}")
        return False


@app.route('/api/daily-tasks/streak', methods=['GET'])
def get_daily_streak():
    """Get streak information for the authenticated user"""
    try:
        username = request.args.get('username') or get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401

        conn = get_db_connection()
        cur = conn.cursor()

        streak = cur.execute(
            "SELECT current_streak, longest_streak, last_complete_date, total_bonus_coins, total_bonus_xp FROM daily_streaks WHERE username=?",
            (username,)
        ).fetchone()

        conn.close()

        if streak:
            return jsonify({
                'success': True,
                'current_streak': streak[0],
                'longest_streak': streak[1],
                'last_complete_date': streak[2],
                'total_bonus_coins': streak[3],
                'total_bonus_xp': streak[4]
            }), 200
        else:
            return jsonify({
                'success': True,
                'current_streak': 0,
                'longest_streak': 0,
                'last_complete_date': None,
                'total_bonus_coins': 0,
                'total_bonus_xp': 0
            }), 200

    except Exception as e:
        return handle_exception(e, 'get_daily_streak')


def mark_daily_task_complete(username, task_type):
    """Helper function to mark a daily task as complete (called from other endpoints)"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')

        # Use INSERT OR REPLACE to handle duplicates
        cur.execute('''
            INSERT INTO daily_tasks (username, task_type, completed, completed_at, task_date)
            VALUES (?, ?, 1, datetime('now'), ?)
            ON CONFLICT(username, task_type, task_date) DO UPDATE SET completed=1, completed_at=datetime('now')
        ''', (username, task_type, today))

        # Check if all tasks completed
        completed_count = cur.execute(
            "SELECT COUNT(DISTINCT task_type) FROM daily_tasks WHERE username=? AND task_date=? AND completed=1",
            (username, today)
        ).fetchone()[0]

        if completed_count >= 6:
            award_daily_completion_bonus(username, cur, today)

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error marking daily task: {e}")
        return False


# ==================== CBT TOOLS DASHBOARD ENDPOINTS ====================

@app.route('/cbt_tools/components/<path:filename>')
def serve_cbt_tool_component(filename):
    """Serve CBT tool HTML component files"""
    try:
        # Security: only allow .html files from the components directory
        if not filename.endswith('.html'):
            return jsonify({'error': 'Invalid file type'}), 400

        # Sanitize filename to prevent directory traversal
        safe_filename = os.path.basename(filename)
        component_path = os.path.join(os.path.dirname(__file__), 'cbt_tools', 'components', safe_filename)

        if not os.path.exists(component_path):
            return jsonify({'error': f'Component not found: {safe_filename}'}), 404

        with open(component_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        return Response(html_content, mimetype='text/html')

    except Exception as e:
        print(f"Error serving CBT component: {e}")
        return jsonify({'error': 'Failed to load component'}), 500


@app.route('/api/cbt-tools/save', methods=['POST'])
def save_cbt_tool_entry():
    """Save CBT tool data entry"""
    try:
        username = get_authenticated_username()
        if not username:
            # Fall back to request data for compatibility
            username = request.json.get('username')

        if not username:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.json
        tool_type = data.get('tool_type')
        entry_data = json.dumps(data.get('data', {}))
        mood_rating = data.get('mood_rating')
        notes = data.get('notes', '')

        if not tool_type:
            return jsonify({'error': 'tool_type is required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Check if entry exists for this user and tool
        existing = cur.execute(
            "SELECT id FROM cbt_tool_entries WHERE username=? AND tool_type=?",
            (username, tool_type)
        ).fetchone()

        if existing:
            # Update existing entry
            cur.execute('''
                UPDATE cbt_tool_entries
                SET data=?, mood_rating=?, notes=?, updated_at=datetime('now')
                WHERE id=?
            ''', (entry_data, mood_rating, notes, existing[0]))
        else:
            # Insert new entry
            cur.execute('''
                INSERT INTO cbt_tool_entries (username, tool_type, data, mood_rating, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, tool_type, entry_data, mood_rating, notes))

        conn.commit()
        entry_id = existing[0] if existing else cur.lastrowid
        conn.close()

        # Update AI memory with CBT activity
        try:
            update_ai_memory(username)
        except Exception as e:
            print(f"AI memory update error (non-critical): {e}")

        # Reward pet for CBT activity
        try:
            reward_pet('cbt', 'cbt')
        except Exception as e:
            print(f"Pet reward error (non-critical): {e}")

        log_event(username, 'cbt', 'tool_saved', f'Tool: {tool_type}')

        return jsonify({'success': True, 'id': entry_id}), 200

    except Exception as e:
        return handle_exception(e, 'save_cbt_tool_entry')


@app.route('/api/cbt-tools/load', methods=['GET'])
def load_cbt_tool_entry():
    """Load saved CBT tool data"""
    try:
        username = request.args.get('username') or get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401

        tool_type = request.args.get('tool_type')
        if not tool_type:
            return jsonify({'error': 'tool_type is required'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        row = cur.execute('''
            SELECT id, data, mood_rating, notes, created_at, updated_at
            FROM cbt_tool_entries
            WHERE username=? AND tool_type=?
            ORDER BY updated_at DESC
            LIMIT 1
        ''', (username, tool_type)).fetchone()

        conn.close()

        if row:
            return jsonify({
                'success': True,
                'id': row[0],
                'data': json.loads(row[1]) if row[1] else {},
                'mood_rating': row[2],
                'notes': row[3],
                'created_at': row[4],
                'updated_at': row[5]
            }), 200
        else:
            return jsonify({'success': True, 'data': None}), 200

    except Exception as e:
        return handle_exception(e, 'load_cbt_tool_entry')


@app.route('/api/cbt-tools/history', methods=['GET'])
def get_cbt_tool_history():
    """Get history of CBT tool entries for a user"""
    try:
        username = request.args.get('username') or get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401

        tool_type = request.args.get('tool_type')  # Optional filter
        limit = int(request.args.get('limit', 20))

        conn = get_db_connection()
        cur = conn.cursor()

        if tool_type:
            rows = cur.execute('''
                SELECT id, tool_type, data, mood_rating, notes, created_at
                FROM cbt_tool_entries
                WHERE username=? AND tool_type=?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (username, tool_type, limit)).fetchall()
        else:
            rows = cur.execute('''
                SELECT id, tool_type, data, mood_rating, notes, created_at
                FROM cbt_tool_entries
                WHERE username=?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (username, limit)).fetchall()

        conn.close()

        entries = [{
            'id': r[0],
            'tool_type': r[1],
            'data': json.loads(r[2]) if r[2] else {},
            'mood_rating': r[3],
            'notes': r[4],
            'created_at': r[5]
        } for r in rows]

        return jsonify({'success': True, 'entries': entries}), 200

    except Exception as e:
        return handle_exception(e, 'get_cbt_tool_history')


# ======================= PHASE 3: INTERNAL MESSAGING SYSTEM =======================

@app.route('/api/messages/send', methods=['POST'])
def send_message():
    """Send a message to another user"""
    try:
        sender = get_authenticated_username()
        if not sender:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json() or {}
        recipient = data.get('recipient')
        subject = data.get('subject', '')
        content = data.get('content', '').strip()
        
        # Validation
        if not recipient or not isinstance(recipient, str):
            return jsonify({'error': 'Recipient is required'}), 400
        
        if not content:
            return jsonify({'error': 'Message content is required'}), 400
        
        if len(content) > 5000:
            return jsonify({'error': 'Message cannot exceed 5000 characters'}), 400
        
        if len(subject) > 100:
            return jsonify({'error': 'Subject cannot exceed 100 characters'}), 400
        
        if sender == recipient:
            return jsonify({'error': 'You cannot send messages to yourself'}), 400
        
        # Check recipient exists
        conn = get_db_connection()
        cur = conn.cursor()
        recipient_user = cur.execute('SELECT username, role FROM users WHERE username=?', (recipient,)).fetchone()
        
        if not recipient_user:
            conn.close()
            return jsonify({'error': 'Recipient not found'}), 404
        
        # Get sender role for permission check
        sender_user = cur.execute('SELECT role FROM users WHERE username=?', (sender,)).fetchone()
        sender_role = sender_user[0] if sender_user else 'user'
        recipient_role = recipient_user[1]
        
        # Role-based access control
        # Users cannot initiate messages to clinicians (but can reply)
        if sender_role == 'user' and recipient_role == 'clinician':
            conn.close()
            return jsonify({'error': 'Users may only reply to clinicians, not initiate contact'}), 403
        
        # Define allowed recipients for each role
        allowed_recipients = {
            'therapist': ['therapist', 'clinician', 'user', 'admin', 'developer'],
            'clinician': ['therapist', 'clinician', 'user', 'admin', 'developer'],
            'user': ['therapist', 'user', 'admin', 'developer'],  # NOT clinician
            'admin': ['therapist', 'clinician', 'user', 'admin', 'developer'],
            'developer': ['therapist', 'clinician', 'user', 'admin', 'developer']
        }
        
        if sender_role not in allowed_recipients or recipient_role not in allowed_recipients.get(sender_role, []):
            conn.close()
            return jsonify({'error': 'Permission denied for this message'}), 403
        
        # Insert message
        cur.execute('''
            INSERT INTO messages (sender_username, recipient_username, subject, content, sent_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (sender, recipient, subject if subject else None, content))
        
        message_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        # Log the action
        log_event(sender, 'messaging', 'message_sent', f'To: {recipient}')
        
        # Send notification to recipient
        send_notification(
            recipient,
            f"New message from {sender}: {subject if subject else content[:50]}",
            'dev_message'
        )
        
        return jsonify({
            'message_id': message_id,
            'status': 'sent',
            'recipient': recipient
        }), 201
    
    except Exception as e:
        return handle_exception(e, 'send_message')


@app.route('/api/messages/inbox', methods=['GET'])
def get_inbox():
    """Get user's message inbox with conversation previews"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        if page < 1:
            page = 1
        if limit < 1 or limit > 50:
            limit = 20
        
        offset = (page - 1) * limit
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get conversations (unique senders/recipients, excluding deleted messages)
        if unread_only:
            # Only show conversations with unread messages
            rows = cur.execute('''
                SELECT 
                    CASE WHEN sender_username = ? THEN recipient_username ELSE sender_username END as other_user,
                    (SELECT content FROM messages m2 
                     WHERE (m2.sender_username = messages.sender_username AND m2.recipient_username = messages.recipient_username
                            OR m2.sender_username = messages.recipient_username AND m2.recipient_username = messages.sender_username)
                     AND m2.deleted_at IS NULL
                     ORDER BY m2.sent_at DESC LIMIT 1) as last_message,
                    (SELECT sent_at FROM messages m2 
                     WHERE (m2.sender_username = messages.sender_username AND m2.recipient_username = messages.recipient_username
                            OR m2.sender_username = messages.recipient_username AND m2.recipient_username = messages.sender_username)
                     AND m2.deleted_at IS NULL
                     ORDER BY m2.sent_at DESC LIMIT 1) as last_message_time,
                    SUM(CASE WHEN recipient_username = ? AND is_read = 0 AND deleted_at IS NULL THEN 1 ELSE 0 END) as unread_count,
                    MAX(CASE WHEN sender_username != ? THEN 1 ELSE 0 END) as is_latest_from_them
                FROM messages
                WHERE (sender_username = ? OR recipient_username = ?)
                AND deleted_at IS NULL
                AND is_read = 0
                AND recipient_username = ?
                GROUP BY other_user
                ORDER BY last_message_time DESC
                LIMIT ? OFFSET ?
            ''', (username, username, username, username, username, username, limit, offset)).fetchall()
        else:
            # Show all conversations
            rows = cur.execute('''
                SELECT 
                    CASE WHEN sender_username = ? THEN recipient_username ELSE sender_username END as other_user,
                    (SELECT content FROM messages m2 
                     WHERE (m2.sender_username = messages.sender_username AND m2.recipient_username = messages.recipient_username
                            OR m2.sender_username = messages.recipient_username AND m2.recipient_username = messages.sender_username)
                     AND m2.deleted_at IS NULL
                     ORDER BY m2.sent_at DESC LIMIT 1) as last_message,
                    (SELECT sent_at FROM messages m2 
                     WHERE (m2.sender_username = messages.sender_username AND m2.recipient_username = messages.recipient_username
                            OR m2.sender_username = messages.recipient_username AND m2.recipient_username = messages.sender_username)
                     AND m2.deleted_at IS NULL
                     ORDER BY m2.sent_at DESC LIMIT 1) as last_message_time,
                    SUM(CASE WHEN recipient_username = ? AND is_read = 0 AND deleted_at IS NULL THEN 1 ELSE 0 END) as unread_count,
                    MAX(CASE WHEN sender_username != ? THEN 1 ELSE 0 END) as is_latest_from_them
                FROM messages
                WHERE (sender_username = ? OR recipient_username = ?)
                AND deleted_at IS NULL
                GROUP BY other_user
                ORDER BY last_message_time DESC
                LIMIT ? OFFSET ?
            ''', (username, username, username, username, username, limit, offset)).fetchall()
        
        # Get total unread count
        total_unread = cur.execute('''
            SELECT COUNT(*) FROM messages
            WHERE recipient_username = ? AND is_read = 0 AND deleted_at IS NULL
        ''', (username,)).fetchone()[0]
        
        # Get total conversation count
        total_conversations = cur.execute('''
            SELECT COUNT(DISTINCT 
                CASE WHEN sender_username = ? THEN recipient_username ELSE sender_username END
            ) FROM messages
            WHERE (sender_username = ? OR recipient_username = ?) AND deleted_at IS NULL
        ''', (username, username, username)).fetchone()[0]
        
        conn.close()
        
        conversations = [{
            'with_user': row[0],
            'last_message': row[1][:100] if row[1] else '',  # Preview first 100 chars
            'last_message_time': row[2],
            'unread_count': row[3] if row[3] else 0,
            'is_latest_from_them': bool(row[4]) if row[4] else False
        } for row in rows]
        
        return jsonify({
            'conversations': conversations,
            'total_unread': total_unread,
            'page': page,
            'page_size': limit,
            'total_conversations': total_conversations
        }), 200
    
    except Exception as e:
        return handle_exception(e, 'get_inbox')


@app.route('/api/messages/conversation/<recipient_username>', methods=['GET'])
def get_conversation(recipient_username):
    """Get full conversation history with a specific user"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        
        limit = int(request.args.get('limit', 50))
        if limit < 1 or limit > 200:
            limit = 50
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get conversation messages (both directions, ordered chronologically)
        rows = cur.execute('''
            SELECT id, sender_username, recipient_username, content, subject, is_read, read_at, sent_at
            FROM messages
            WHERE (sender_username = ? AND recipient_username = ?)
               OR (sender_username = ? AND recipient_username = ?)
            AND deleted_at IS NULL
            ORDER BY sent_at ASC
            LIMIT ?
        ''', (username, recipient_username, recipient_username, username, limit)).fetchall()
        
        # Mark all messages from recipient as read
        cur.execute('''
            UPDATE messages
            SET is_read = 1, read_at = CURRENT_TIMESTAMP
            WHERE sender_username = ? AND recipient_username = ? AND is_read = 0
        ''', (recipient_username, username))
        
        conn.commit()
        
        # Re-fetch messages to get updated is_read values
        rows = cur.execute('''
            SELECT id, sender_username, recipient_username, content, subject, is_read, read_at, sent_at
            FROM messages
            WHERE (sender_username = ? AND recipient_username = ?)
               OR (sender_username = ? AND recipient_username = ?)
            AND deleted_at IS NULL
            ORDER BY sent_at ASC
            LIMIT ?
        ''', (username, recipient_username, recipient_username, username, limit)).fetchall()
        
        conn.close()
        
        messages = [{
            'id': row[0],
            'sender': row[1],
            'recipient': row[2],
            'content': row[3],
            'subject': row[4],
            'is_read': bool(row[5]),
            'read_at': row[6],
            'sent_at': row[7]
        } for row in rows]
        
        return jsonify({
            'messages': messages,
            'participant_count': 2
        }), 200
    
    except Exception as e:
        return handle_exception(e, 'get_conversation')


@app.route('/api/messages/<int:message_id>/read', methods=['PATCH'])
def mark_message_read(message_id):
    """Mark a message as read"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check message exists and user is recipient
        message = cur.execute('''
            SELECT id, recipient_username FROM messages WHERE id = ?
        ''', (message_id,)).fetchone()
        
        if not message:
            conn.close()
            return jsonify({'error': 'Message not found'}), 404
        
        if message[1] != username:
            conn.close()
            return jsonify({'error': 'You are not the recipient of this message'}), 403
        
        # Mark as read
        cur.execute('''
            UPDATE messages
            SET is_read = 1, read_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (message_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message_id': message_id,
            'is_read': True,
            'read_at': datetime.now().isoformat() + 'Z'
        }), 200
    
    except Exception as e:
        return handle_exception(e, 'mark_message_read')


@app.route('/api/messages/sent', methods=['GET'])
def get_sent_messages():
    """Get messages sent by the authenticated user"""
    try:
        sender = get_authenticated_username()
        if not sender:
            return jsonify({'error': 'Authentication required'}), 401

        conn = get_db_connection()
        cur = conn.cursor()

        # Get sent messages (messages where user is sender)
        messages = cur.execute('''
            SELECT id, sender_username, recipient_username, subject, content, sent_at, is_read, read_at
            FROM messages 
            WHERE sender_username = ? AND is_deleted_by_sender = 0
            ORDER BY sent_at DESC
        ''', (sender,)).fetchall()

        conn.close()

        return jsonify({
            'success': True,
            'messages': [
                {
                    'id': m[0],
                    'sender': m[1],
                    'recipient': m[2],
                    'subject': m[3],
                    'content': m[4],
                    'sent_at': m[5],
                    'is_read': bool(m[6]),
                    'read_at': m[7]
                }
                for m in messages
            ]
        }), 200

    except Exception as e:
        return handle_exception(e, 'get_sent_messages')


@app.route('/api/feedback/all', methods=['GET'])
def get_all_feedback():
    """Get all feedback (developers only)"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401

        conn = get_db_connection()
        cur = conn.cursor()

        # Check if user is developer
        user_role = cur.execute('SELECT role FROM users WHERE username=?', (username,)).fetchone()
        if not user_role or user_role[0] != 'developer':
            conn.close()
            return jsonify({'error': 'Only developers can view all feedback'}), 403

        # Get all feedback
        feedback = cur.execute('''
            SELECT id, username, role, category, message, status, created_at 
            FROM feedback 
            ORDER BY created_at DESC 
            LIMIT 500
        ''').fetchall()

        conn.close()

        return jsonify({
            'success': True,
            'feedback_count': len(feedback),
            'feedback': [
                {
                    'id': f[0],
                    'username': f[1],
                    'user_role': f[2],
                    'category': f[3],
                    'message': f[4],
                    'status': f[5],
                    'created_at': f[6]
                }
                for f in feedback
            ]
        }), 200

    except Exception as e:
        return handle_exception(e, 'get_all_feedback')

@app.route('/api/feedback/<int:feedback_id>/status', methods=['PUT'])
def update_feedback_status(feedback_id):
    """Update feedback status (developers only)"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json() or {}
        new_status = data.get('status', '').strip()
        admin_notes = data.get('admin_notes', '').strip()

        # Validate status
        valid_statuses = ['pending', 'in_progress', 'resolved', 'wont_fix', 'duplicate']
        if not new_status or new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Valid options: {", ".join(valid_statuses)}'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Check if user is developer
        user_role = cur.execute('SELECT role FROM users WHERE username=?', (username,)).fetchone()
        if not user_role or user_role[0] != 'developer':
            conn.close()
            return jsonify({'error': 'Only developers can update feedback'}), 403

        # Get feedback to find who submitted it
        feedback = cur.execute('''
            SELECT username, category, message FROM feedback WHERE id=?
        ''', (feedback_id,)).fetchone()

        if not feedback:
            conn.close()
            return jsonify({'error': 'Feedback not found'}), 404

        feedback_submitter, category, message = feedback

        # Update feedback
        resolved_at = 'CURRENT_TIMESTAMP' if new_status == 'resolved' else 'NULL'
        cur.execute(f'''
            UPDATE feedback 
            SET status=?, admin_notes=?, resolved_at={resolved_at}
            WHERE id=?
        ''', (new_status, admin_notes, feedback_id))

        conn.commit()

        # Send notification to user who submitted feedback
        emoji = {'pending': '⏳', 'in_progress': '⚙️', 'resolved': '✅', 'wont_fix': '❌', 'duplicate': '📋'}.get(new_status, '📝')
        status_display = new_status.replace('_', ' ').title()
        send_notification(
            feedback_submitter,
            f"Your {category.lower()} has been updated: {emoji} {status_display}",
            'feedback_update'
        )

        # Log event
        try:
            log_event(username, 'developer', 'feedback_status_update', f'Feedback #{feedback_id} ({category}) → {new_status}')
        except:
            pass

        conn.close()

        return jsonify({
            'success': True,
            'message': f'Feedback status updated to {new_status}',
            'feedback_id': feedback_id
        }), 200

    except Exception as e:
        return handle_exception(e, 'update_feedback_status')

@app.route('/api/messages/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    """Soft delete a message (hide from user, not permanent)"""
    try:
        username = get_authenticated_username()
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check message exists and user is sender or recipient
        message = cur.execute('''
            SELECT id, sender_username, recipient_username, is_deleted_by_sender, is_deleted_by_recipient
            FROM messages WHERE id = ?
        ''', (message_id,)).fetchone()
        
        if not message:
            conn.close()
            return jsonify({'error': 'Message not found'}), 404
        
        msg_id, sender, recipient, deleted_by_sender, deleted_by_recipient = message
        
        if username not in (sender, recipient):
            conn.close()
            return jsonify({'error': 'You cannot delete this message'}), 403
        
        # Mark as deleted by this user
        if username == sender:
            cur.execute('''
                UPDATE messages SET is_deleted_by_sender = 1 WHERE id = ?
            ''', (message_id,))
        else:  # recipient
            cur.execute('''
                UPDATE messages SET is_deleted_by_recipient = 1 WHERE id = ?
            ''', (message_id,))
        
        # If both have marked deleted, hide the message permanently
        if (username == sender and deleted_by_recipient) or (username == recipient and deleted_by_sender):
            cur.execute('''
                UPDATE messages SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?
            ''', (message_id,))
        
        conn.commit()
        conn.close()
        
        log_event(username, 'messaging', 'message_deleted', f'Message ID: {message_id}')
        
        return '', 204  # No content response
    
    except Exception as e:
        return handle_exception(e, 'delete_message')


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

# ================== APP INITIALIZATION & STARTUP LOGGING ==================

def test_database_connection():
    """Test database connection on startup"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        conn.close()
        print("✅ Database connection: SUCCESSFUL")
        return True
    except Exception as e:
        print(f"❌ Database connection: FAILED - {e}")
        return False

# Initialize pet table
try:
    ensure_pet_table()
except Exception as e:
    print(f"⚠️  Pet table initialization failed: {e}")

# Log startup info
print("=" * 80)
print("🚀 HEALING SPACE UK - Flask API Starting")
print("=" * 80)
print(f"Environment: {'DEBUG MODE' if DEBUG else 'PRODUCTION'}")
print(f"Database URL configured: {bool(os.environ.get('DATABASE_URL'))}")
print(f"Using: {'Railway PostgreSQL' if os.environ.get('DATABASE_URL') else 'Local/env var PostgreSQL'}")

# Test database connection on startup
db_ready = test_database_connection()

# Check required secrets
groq_ready = bool(GROQ_API_KEY)
print(f"✅ GROQ API Key configured: {groq_ready}")
print(f"✅ SECRET_KEY configured: {bool(app.config.get('SECRET_KEY'))}")
print(f"✅ PIN_SALT configured: {bool(PIN_SALT)}")

# Print app summary
print(f"📊 API Routes: {len(app.url_map._rules)} routes registered")
print("=" * 80)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Starting on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=DEBUG)
