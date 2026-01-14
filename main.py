import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, ttk, filedialog
from tkinter import colorchooser
import requests
import threading
import sqlite3
import hashlib
import uuid
import random
import csv
import json
import pyttsx3  
from datetime import datetime, timedelta
import edge_tts
import asyncio
import pygame 
from plyer import notification 
import os
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except Exception:
    def load_dotenv():
        return
    DOTENV_AVAILABLE = False
from pet_game import PetGame
from audit import log_event
from fhir_export import export_patient_fhir
from secure_transfer import sftp_upload
from secrets_manager import SecretsManager

# Load runtime mode
DEBUG = os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes')

# Password hashing: prefer Argon2, fallback to bcrypt, then PBKDF2
try:
    from argon2 import PasswordHasher
    _ph = PasswordHasher()
    HAS_ARGON2 = True
except Exception:
    _ph = None
    HAS_ARGON2 = False

# --- UX Patches: Ensure all CTkToplevels are front, bind <Escape> to close, and focus them
_orig_ctk_toplevel = ctk.CTkToplevel
def _ctk_toplevel_fixed(*args, **kwargs):
    t = _orig_ctk_toplevel(*args, **kwargs)
    try:
        t.attributes("-topmost", True)
    except Exception:
        pass
    try:
        t.transient(args[0] if args else None)
    except Exception:
        pass
    try:
        t.bind('<Escape>', lambda e: t.destroy())
        t.focus_force()
    except Exception:
        pass
    return t

ctk.CTkToplevel = _ctk_toplevel_fixed

# Ensure messageboxes appear on top by default (use root as parent)
_orig_showinfo = messagebox.showinfo
_orig_showerror = messagebox.showerror
_orig_askyesno = messagebox.askyesno
def _mb_parent_wrapper(fn):
    def wrapped(title, message, **kwargs):
        try:
            parent = kwargs.pop('parent', tk._default_root)
        except Exception:
            parent = None
        return fn(title, message, parent=parent, **kwargs)
    return wrapped

messagebox.showinfo = _mb_parent_wrapper(_orig_showinfo)
messagebox.showerror = _mb_parent_wrapper(_orig_showerror)
messagebox.askyesno = _mb_parent_wrapper(_orig_askyesno)

# bcrypt optional: provide safe fallback if not installed in environment
try:
    import bcrypt
    HAS_BCRYPT = True
except Exception:
    bcrypt = None
    HAS_BCRYPT = False
import hashlib as _hashlib

def hash_pin(pin: str) -> str:
    # Use PIN_SALT sourced from secrets manager or env (module-level PIN_SALT)
    if not PIN_SALT:
        import warnings
        warnings.warn('PIN_SALT not configured; using dev fallback salt')
    if HAS_BCRYPT:
        return bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()
    # fallback: PBKDF2 hex with a deploy-time salt
    salt_val = PIN_SALT or 'dev_fallback_salt'
    salt = _hashlib.sha256(salt_val.encode()).hexdigest()[:16]
    dk = _hashlib.pbkdf2_hmac('sha256', pin.encode(), salt.encode(), 100000)
    return f"pbkdf2${dk.hex()}"

def check_pin(pin: str, stored: str) -> bool:
    if not stored:
        return False
    if stored.startswith("$2") and HAS_BCRYPT:
        return bcrypt.checkpw(pin.encode(), stored.encode())
    if stored.startswith("pbkdf2$"):
        dk = stored.split("$", 1)[1]
        # Use module-level PIN_SALT sourced from secrets manager or env
        if not PIN_SALT and not DEBUG:
            return False
        salt_val = PIN_SALT or 'dev_fallback_salt'
        salt = _hashlib.sha256(salt_val.encode()).hexdigest()[:16]
        new = _hashlib.pbkdf2_hmac('sha256', pin.encode(), salt.encode(), 100000).hex()
        return new == dk
    # last resort: plaintext comparison (will be migrated)
    return pin == stored

# NEW LIBRARIES FOR SECURITY AND EXPORT
from cryptography.fernet import Fernet
from fpdf import FPDF

# --- MODERN THEMING ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- CONFIGURATION & ENCRYPTION ---
load_dotenv()
API_URL = os.environ.get("API_URL", "https://api.groq.com/openai/v1/chat/completions")

# Initialize secrets manager (will fallback to env if no external secrets backend configured)
secrets = SecretsManager(debug=DEBUG)

# Secrets: prefer secrets manager or environment variables. In production these MUST be provided.
# Primary lookup: standard name `GROQ_API_KEY` (env or vault)
GROQ_API_KEY = secrets.get_secret("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")

# Require API key in production
if not GROQ_API_KEY and not DEBUG:
    raise RuntimeError("GROQ_API_KEY is required. Set it in environment variables or secrets manager.")

_enc = secrets.get_secret("ENCRYPTION_KEY") or os.environ.get("ENCRYPTION_KEY")
# PIN_SALT is used for legacy PBKDF2 fallbacks; prefer providing a proper per-user Argon2 instead.
PIN_SALT = secrets.get_secret("PIN_SALT") or os.environ.get("PIN_SALT")
if not PIN_SALT:
    import warnings
    warnings.warn("PIN_SALT is not set; using development fallback salt. Set PIN_SALT in production.")
    PIN_SALT = os.environ.get('PIN_SALT') or 'dev_fallback_salt'

if _enc:
    ENCRYPTION_KEY = _enc.encode() if isinstance(_enc, str) else _enc
    cipher_suite = Fernet(ENCRYPTION_KEY)
else:
    # Do not raise at import time; allow the app to run without encryption available.
    ENCRYPTION_KEY = None
    cipher_suite = None
    if DEBUG:
        print("WARNING: ENCRYPTION_KEY not set; generating temporary key for DEBUG mode")
        ENCRYPTION_KEY = Fernet.generate_key()
        cipher_suite = Fernet(ENCRYPTION_KEY)

# Optional alert webhook for clinician notifications
ALERT_WEBHOOK_URL = os.environ.get('ALERT_WEBHOOK_URL', '')
SFTP_HOST = os.environ.get('SFTP_HOST', '')
SFTP_PORT = int(os.environ.get('SFTP_PORT', '22')) if os.environ.get('SFTP_PORT') else 22
SFTP_USER = os.environ.get('SFTP_USER', '')
SFTP_PASS = os.environ.get('SFTP_PASS', '')
SFTP_PKEY = os.environ.get('SFTP_PKEY_PATH', '')
SFTP_REMOTE_DIR = os.environ.get('SFTP_REMOTE_DIR', '/')


def encrypt_text(text):
    if not text: return ""
    if cipher_suite is None:
        # No encryption available; return plaintext (local/dev fallback)
        return text
    return cipher_suite.encrypt(text.encode()).decode()

def decrypt_text(text):
    if not text: return ""
    if cipher_suite is None:
        return text
    try:
        return cipher_suite.decrypt(text.encode()).decode()
    except Exception:
        return "[Decrypted Data - Error]"


# --- Password helpers (hash/verify) ---
def hash_password(password: str) -> str:
    if HAS_ARGON2 and _ph:
        return _ph.hash(password)
    if HAS_BCRYPT:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    # Fallback PBKDF2
    salt_val = PIN_SALT or ('dev_fallback_salt' if DEBUG else 'dev_fallback_salt')
    if not salt_val:
        import warnings
        warnings.warn('No PIN_SALT available; using dev fallback for password hashing')
    dk = _hashlib.pbkdf2_hmac('sha256', password.encode(), salt_val.encode(), 200000)
    return f"pbkdf2${dk.hex()}"

def verify_password(stored: str, password: str) -> bool:
    if not stored: return False
    try:
        if stored.startswith('$argon2'):
            if HAS_ARGON2 and _ph:
                return _ph.verify(stored, password)
            else:
                # Cannot verify Argon2 without library; log and fail safe
                import warnings
                warnings.warn('Argon2 hash found but argon2 library not available; cannot verify password')
                return False
    except Exception:
        pass
    try:
        if stored.startswith('$2') and HAS_BCRYPT:
            return bcrypt.checkpw(password.encode(), stored.encode())
    except Exception:
        pass
    if stored.startswith('pbkdf2$'):
        dk = stored.split('$', 1)[1]
        salt_val = PIN_SALT or ('dev_fallback_salt' if DEBUG else None)
        if not salt_val:
            return False
        new = _hashlib.pbkdf2_hmac('sha256', password.encode(), salt_val.encode(), 200000).hex()
        return new == dk
    # Legacy SHA256 hexdigest (migration path)
    if len(stored) == 64 and all(c in '0123456789abcdef' for c in stored.lower()):
        return _hashlib.sha256(password.encode()).hexdigest() == stored
    return False

# --- SAFETY RESOURCES ---
CRISIS_RESOURCES = """
*** IMPORTANT SAFETY NOTICE ***
If you are feeling overwhelmed and considering self-harm or ending your life, please reach out for help immediately. 

- UK: Call 999 or 111, or text SHOUT to 85258.
- USA/Canada: Call or text 988.
- International: Visit findahelpline.com
"""

# --- HELP & GUIDE TEXT ---
HELP_GUIDE_TEXT = """
HEALING SPACE - USER GUIDE

1. YOUR SELF-CARE PET 🐾
   - Purpose: Your companion reflects your wellbeing.
   - Earning Coins: Every time you perform a self-care action (Log mood, Journal, Therapy, Breathing), you earn 5 COINS.
   - Growth: Your pet gains XP for every action. 
     * 500 XP: Evolves to Child.
     * 1500 XP: Evolves to Adult.
   - Stats:
     * Hunger: Buy food in the Shop.
     * Happiness: Gratitude Journal & Grounding.
     * Energy: Taking Meds & Therapy.
     * Hygiene: Use the 'Declutter' game to clean the mind.

2. CLINICAL TOOLS 🩺
   - Mood Tracker: Log every 2 hours to track trends.
   - Therapy: Talk to the AI. It remembers your history.
   - Clinical Scales (PHQ-9): Take this assessment once every 2 weeks to track clinical progress.
   - PDF Export: Download your full medical report in "Progress Insights".

3. SAFETY
   - All data is encrypted.
   - Use the Panic Button in emergencies.
"""

class SafetyMonitor:
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
    
    # NEW: Crisis Alert Simulation
    def send_crisis_alert(self, user_details):
        try:
            username = user_details if isinstance(user_details, str) else user_details.get('username')
            details = str(user_details)
            conn = sqlite3.connect("therapist_app.db")
            conn.execute("INSERT INTO alerts (username, alert_type, details) VALUES (?,?,?)", (username, 'crisis', details))
            conn.commit(); conn.close()
            log_event(username or 'unknown', 'system', 'crisis_alert_sent', details)
            print(f"!!! CRISIS ALERT !!! Persisted alert for {username}")
            # Send out webhook notification if configured
            try:
                if ALERT_WEBHOOK_URL:
                    payload = {"username": username, "alert_type": "crisis", "details": details}
                    requests.post(ALERT_WEBHOOK_URL, json=payload, timeout=5)
                    log_event(username or 'unknown', 'system', 'webhook_sent', ALERT_WEBHOOK_URL)
            except Exception as e:
                print(f"Webhook notify failed: {e}")
            return True
        except Exception as e:
            print(f"Crisis alert failed: {e}")
            return False

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("therapist_app.db")
    cursor = conn.cursor()
    
    # Updated table with last_login and personal bio fields
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
                       entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # NEW: Safety Plan and AI Memory Tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS safety_plans
                      (username TEXT PRIMARY KEY, triggers TEXT, coping TEXT, contacts TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS ai_memory 
                      (username TEXT PRIMARY KEY, memory_summary TEXT, last_updated DATETIME)''')
    
    # NEW: CBT Records table for full data tracking
    cursor.execute('''CREATE TABLE IF NOT EXISTS cbt_records 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, situation TEXT, thought TEXT, evidence TEXT, entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    # NEW: Clinical Scales (PHQ-9 etc)
    cursor.execute('''CREATE TABLE IF NOT EXISTS clinical_scales
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, scale_name TEXT, score INTEGER, severity TEXT, entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    # NEW: Community Posts (P2P Simulation)
    cursor.execute('''CREATE TABLE IF NOT EXISTS community_posts
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, message TEXT, likes INTEGER DEFAULT 0, entry_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    # Audit logs for tracking data access and exports
    cursor.execute('''CREATE TABLE IF NOT EXISTS audit_logs
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, actor TEXT, action TEXT, details TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    # Alerts table for crisis escalations and clinician triage
    cursor.execute('''CREATE TABLE IF NOT EXISTS alerts
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, alert_type TEXT, details TEXT, status TEXT DEFAULT 'open', created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Patient approval system - clinicians must approve patients who select them
    cursor.execute('''CREATE TABLE IF NOT EXISTS patient_approvals
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_username TEXT, clinician_username TEXT, 
                       status TEXT DEFAULT 'pending', request_date DATETIME DEFAULT CURRENT_TIMESTAMP, 
                       approval_date DATETIME)''')
    
    # Notifications for clinician-patient interactions
    cursor.execute('''CREATE TABLE IF NOT EXISTS notifications
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, recipient_username TEXT, message TEXT, 
                       notification_type TEXT, read INTEGER DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    # --- DATABASE REPAIR BLOCK ---
    cursor.execute("PRAGMA table_info(users)")
    user_columns = [column[1] for column in cursor.fetchall()]
    if "pin" not in user_columns:
        try: cursor.execute("ALTER TABLE users ADD COLUMN pin TEXT")
        except: pass
    if "last_login" not in user_columns:
        try: cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP")
        except: pass
    if "full_name" not in user_columns:
        try: cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
        except: pass
    if "dob" not in user_columns:
        try: cursor.execute("ALTER TABLE users ADD COLUMN dob TEXT")
        except: pass
    if "conditions" not in user_columns:
        try: cursor.execute("ALTER TABLE users ADD COLUMN conditions TEXT")
        except: pass
    if "role" not in user_columns:
        try: cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
        except: pass

    # Settings store for UI preferences
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
    # Ensure some defaults exist
    curconf = dict(cursor.execute("SELECT key, value FROM settings").fetchall())
    defaults = {"font_size":"12", "appearance_mode":"dark", "accent_color":"blue", "bg_color":"", "font_color":""}
    for k, v in defaults.items():
        if k not in curconf:
            try: cursor.execute("INSERT INTO settings (key, value) VALUES (?,?)", (k, v))
            except: pass

    cursor.execute("PRAGMA table_info(mood_logs)")
    mood_columns = [column[1] for column in cursor.fetchall()]
    new_cols = {"exercise_mins": "INTEGER", "outside_mins": "INTEGER", "water_pints": "REAL"}
    for col, ctype in new_cols.items():
        if col not in mood_columns:
            cursor.execute(f"ALTER TABLE mood_logs ADD COLUMN {col} {ctype} DEFAULT 0")

    cursor.execute("PRAGMA table_info(chat_history)")
    if not cursor.fetchall():
        cursor.execute('''CREATE TABLE chat_history 
                          (session_id TEXT, sender TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

class TherapistAI:
    def __init__(self, username=None):
        self.username = username
        self.headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    def get_memory(self):
        if not self.username: return ""
        conn = sqlite3.connect("therapist_app.db")
        # Fetch AI summary
        res = conn.cursor().execute("SELECT memory_summary FROM ai_memory WHERE username=?", (self.username,)).fetchone()
        
        # Fetch Core Patient Profile
        profile = conn.cursor().execute("SELECT full_name, dob, conditions FROM users WHERE username=?", (self.username,)).fetchone()
        conn.close()

        # Risk Monitoring Tab - list persisted alerts
        try:
            conn = sqlite3.connect("therapist_app.db")
            alerts = conn.cursor().execute("SELECT id, username, alert_type, details, status, created_at FROM alerts ORDER BY created_at DESC LIMIT 50").fetchall()
            conn.close()
        except Exception:
            alerts = []

        # If this TherapistAI instance has no UI context (created in background threads),
        # avoid creating UI widgets and instead return a plain-text summary for memory/context.
        if not hasattr(self, 'win') or not hasattr(self, 't_risk'):
            alerts_text = []
            for a in alerts:
                aid, au, atype, details, status, created = a
                summary = details if not details or len(details) < 180 else details[:180] + "..."
                alerts_text.append(f"{created} | {au} | {atype} | {status} | {summary}")
            alerts_block = "\n".join(alerts_text[:25])
            profile_context = ""
            if profile:
                profile_context = (f"PATIENT PROFILE: Name: {decrypt_text(profile[0])}, "
                                   f"DOB: {decrypt_text(profile[1])}, "
                                   f"Relevant History: {decrypt_text(profile[2])}.\n")
            ai_summary = decrypt_text(res[0]) if res else "New patient, no session history yet."
            if alerts_block:
                return profile_context + ai_summary + "\nRecent Alerts:\n" + alerts_block
            return profile_context + ai_summary
        
        profile_context = ""
        if profile:
            profile_context = (f"PATIENT PROFILE: Name: {decrypt_text(profile[0])}, "
                               f"DOB: {decrypt_text(profile[1])}, "
                               f"Relevant History: {decrypt_text(profile[2])}.\n")

        ai_summary = decrypt_text(res[0]) if res else "New patient, no session history yet."
        return profile_context + ai_summary

    def update_memory(self, user_text, ai_text):
        if not self.username: return
        # If no external API key is configured, use a simple local summary updater in DEBUG mode
        current_mem = self.get_memory()
        if not GROQ_API_KEY and DEBUG:
            # Simple concatenative memory update for local testing
            updated = (current_mem + "\n" if current_mem else "") + f"Last interaction summary: User: {user_text[:200]} | AI: {ai_text[:200]}"
            try:
                conn = sqlite3.connect("therapist_app.db")
                # ensure table exists (safe-guard if init_db wasn't run)
                conn.execute('''CREATE TABLE IF NOT EXISTS ai_memory (username TEXT PRIMARY KEY, memory_summary TEXT, last_updated DATETIME)''')
                conn.execute("INSERT OR REPLACE INTO ai_memory VALUES (?,?,?)", (self.username, encrypt_text(updated), datetime.now()))
                conn.commit(); conn.close()
            except: pass
            return

        prompt = f"Current Knowledge: {current_mem}\n\nRecent Interaction:\nUser: {user_text}\nAI: {ai_text}\n\nUpdate the clinical summary for long-term memory. Be concise. Use text wrapping."
        payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": "You are a memory manager. Update summaries of patient progress."}, {"role": "user", "content": prompt}]}
        try:
            r = requests.post(API_URL, headers=self.headers, json=payload, timeout=10)
            if r.status_code == 200:
                updated = r.json()['choices'][0]['message']['content'].strip()
                conn = sqlite3.connect("therapist_app.db")
                conn.execute("INSERT OR REPLACE INTO ai_memory VALUES (?,?,?)", (self.username, encrypt_text(updated), datetime.now()))
                conn.commit(); conn.close()
        except: pass

    def get_response(self, user_input, history):
        memory = self.get_memory()
        system_msg = f"You are a kind, professional therapist. Use reflective listening. Be empathetic and supportive. use CBT or talking therapy styles. Always use text wrapping. LONG TERM CONTEXT: {memory}"
        
        messages = [{"role": "system", "content": system_msg}]
        for h in history[-10:]:
            role = "user" if h[0] == "You" else "assistant"
            messages.append({"role": role, "content": h[1]})
        messages.append({"role": "user", "content": user_input})
        
        payload = {"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": 0.7, "max_tokens": 500}
        # If no API key is configured, provide a local deterministic fallback in DEBUG mode
        if not GROQ_API_KEY and DEBUG:
            # Simple reflective reply for offline testing
            snippet = user_input.strip()
            if len(snippet) > 200:
                snippet = snippet[:200] + '...'
            content = f"It sounds like you're saying: '{snippet}'. Can you tell me more about how that feels?"
            # Persist memory via the fallback updater
            try:
                threading.Thread(target=self.update_memory, args=(user_input, content)).start()
            except: pass
            return content

        try:
            response = requests.post(API_URL, headers=self.headers, json=payload, timeout=15)
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content'].strip()
                threading.Thread(target=self.update_memory, args=(user_input, content)).start()
                return content
            # Log the failure (best-effort) with truncated response body for diagnostics
            try:
                body = response.text
            except Exception:
                body = ''
            short = (body[:300] + '...') if len(body) > 300 else body
            try:
                log_event(self.username or 'unknown', 'system', 'api_error', f'status={response.status_code}, body={short}')
            except: pass
            return f"I'm having a bit of trouble thinking (Error {response.status_code})."
        except Exception as e:
            try:
                log_event(self.username or 'unknown', 'system', 'api_exception', str(e)[:300])
            except: pass
            return "My connection flickered. I'm still listening—what were you saying?"

    def analyze_sentiment(self, text):
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "system", "content": "Analyze mood. Return one word: Positive, Neutral, Anxious, or Sad."},
                         {"role": "user", "content": text}],
            "max_tokens": 10
        }
        try:
            r = requests.post(API_URL, headers=self.headers, json=payload, timeout=5)
            return r.json()['choices'][0]['message']['content'].strip() if r.status_code == 200 else "Neutral"
        except: return "Neutral"

    def analyze_progress(self, logs, gratitudes, cbt_data, safety_plan):
        log_summary = "--- MOOD & HABIT LOGS ---\n"
        for l in logs:
            log_summary += f"Date: {l[8]}, Mood: {l[0]}/10, Sleep: {l[1]}hr, Meds: {l[2]}, Sentiment: {l[4]}, Exercise: {l[5]}m, Outside: {l[6]}m, Water: {l[7]}pints.\n"
        
        log_summary += "\n--- GRATITUDE ENTRIES ---\n"
        for g in gratitudes:
            log_summary += f"{g[1]}: {g[0]}\n"
            
        log_summary += "\n--- CBT THOUGHT RECORDS ---\n"
        for c in cbt_data:
            log_summary += f"{c[3]}: Sit: {c[0]} | Thought: {c[1]} | Challenge: {c[2]}\n"

        log_summary += f"\n--- SAFETY PLAN CONFIG ---\nTriggers: {safety_plan[0]} | Coping: {safety_plan[1]}"
        
        prompt = f"As a wellness AI, analyze ALL these user data points and provide a holistic opinion on patterns, progress, and health suggestions. Be encouraging and concise. Use text wrapping:\n\n{log_summary}"
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "system", "content": "You are a professional health analyst. Provide concise, scannable advice based on cross-referenced data patterns. Use text wrapping."},
                         {"role": "user", "content": prompt}],
            "max_tokens": 1000
        }
        try:
            r = requests.post(API_URL, headers=self.headers, json=payload, timeout=25)
            return r.json()['choices'][0]['message']['content'].strip() if r.status_code == 200 else "Unable to analyze patterns right now."
        except: return "AI Analysis currently unavailable."

# --- NEW: CLINICIAN DASHBOARD ---
class ProfessionalDashboard:
    def __init__(self, parent):
        self.win = ctk.CTkToplevel(parent)
        self.win.title("Clinician Dashboard (Confidential)")
        self.win.geometry("900x700")
        
        # Tabs
        self.tabview = ctk.CTkTabview(self.win)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.t_overview = self.tabview.add("Patient Overview")
        self.t_scales = self.tabview.add("Clinical Scales")
        self.t_risk = self.tabview.add("Risk Monitoring")
        
        self._load_data()

    def _load_data(self):
        conn = sqlite3.connect("therapist_app.db")
        users = conn.cursor().execute("SELECT username, full_name, last_login, conditions FROM users").fetchall()
        
        # Patient Overview Tab
        ctk.CTkLabel(self.t_overview, text="Registered Patients", font=("Arial", 20, "bold")).pack(pady=10)
        scroll = ctk.CTkScrollableFrame(self.t_overview)
        scroll.pack(fill="both", expand=True)
        
        for u in users:
            f = ctk.CTkFrame(scroll)
            f.pack(fill="x", pady=5, padx=5)
            name = decrypt_text(u[1])
            cond = decrypt_text(u[3])
            ctk.CTkLabel(f, text=f"User: {u[0]} | Name: {name}", font=("Arial", 12, "bold")).pack(side="left", padx=10)
            ctk.CTkLabel(f, text=f"Last Login: {u[2]}", font=("Arial", 10)).pack(side="right", padx=10)
            ctk.CTkLabel(f, text=f"History: {cond[:50]}...", font=("Arial", 10, "italic")).pack(side="left", padx=20)

        # Scales Tab
        ctk.CTkLabel(self.t_scales, text="PHQ-9 / GAD-7 Results", font=("Arial", 20, "bold")).pack(pady=10)
        scales = conn.cursor().execute("SELECT username, scale_name, score, severity, entry_timestamp FROM clinical_scales ORDER BY entry_timestamp DESC").fetchall()
        s_scroll = ctk.CTkScrollableFrame(self.t_scales)
        s_scroll.pack(fill="both", expand=True)
        
        for s in scales:
            f = ctk.CTkFrame(s_scroll)
            f.pack(fill="x", pady=5, padx=5)
            col = "#e74c3c" if "Severe" in s[3] else "#2ecc71"
            ctk.CTkLabel(f, text=f"{s[0]}: {s[1]}", font=("Arial", 12, "bold")).pack(side="left", padx=10)
            ctk.CTkLabel(f, text=f"Score: {s[2]} ({s[3]})", text_color=col, font=("Arial", 12, "bold")).pack(side="left", padx=10)
            ctk.CTkLabel(f, text=s[4], font=("Arial", 10)).pack(side="right", padx=10)
            
        conn.close()

# --- ENHANCED CLINICAL SCALES ---
class ClinicalScales:
    def __init__(self, parent, username):
        self.parent = parent
        self.username = username
        self.win = ctk.CTkToplevel(parent)
        self.win.title("Clinical Assessments")
        self.win.geometry("550x750")
        
        # Selection for different scales
        self.tabview = ctk.CTkTabview(self.win)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.t_phq = self.tabview.add("PHQ-9 (Depression)")
        self.t_gad = self.tabview.add("GAD-7 (Anxiety)")
        
        self._setup_phq9()
        self._setup_gad7()

    def _setup_phq9(self):
        questions = [
            "Little interest or pleasure in doing things",
            "Feeling down, depressed, or hopeless",
            "Trouble falling or staying asleep, or sleeping too much",
            "Feeling tired or having little energy",
            "Poor appetite or overeating",
            "Feeling bad about yourself",
            "Trouble concentrating on things",
            "Moving/speaking slowly OR being fidgety",
            "Thoughts that you would be better off dead"
        ]
        self.phq_vars = self._render_questions(self.t_phq, questions)
        ctk.CTkButton(self.t_phq, text="Submit PHQ-9", command=lambda: self.calculate("PHQ-9", self.phq_vars)).pack(pady=10)

    def _setup_gad7(self):
        questions = [
            "Feeling nervous, anxious, or on edge",
            "Not being able to stop or control worrying",
            "Worrying too much about different things",
            "Trouble relaxing",
            "Being so restless that it is hard to sit still",
            "Becoming easily annoyed or irritable",
            "Feeling afraid, as if something awful might happen"
        ]
        self.gad_vars = self._render_questions(self.t_gad, questions)
        ctk.CTkButton(self.t_gad, text="Submit GAD-7", command=lambda: self.calculate("GAD-7", self.gad_vars)).pack(pady=10)

    def _render_questions(self, parent, questions):
        vars_list = []
        scroll = ctk.CTkScrollableFrame(parent)
        scroll.pack(fill="both", expand=True, padx=5, pady=5)
        for q in questions:
            f = ctk.CTkFrame(scroll)
            f.pack(fill="x", pady=5)
            ctk.CTkLabel(f, text=q, wraplength=400, justify="left").pack(anchor="w")
            v = tk.IntVar(value=0)
            vars_list.append(v)
            opts = [("Not at all", 0), ("Several days", 1), ("> Half days", 2), ("Nearly every day", 3)]
            for text, val in opts:
                ctk.CTkRadioButton(f, text=text, variable=v, value=val).pack(side="left", padx=5)
        return vars_list

    def calculate(self, scale_name, vars_list):
        score = sum(v.get() for v in vars_list)
        
        # Calculate Severity logic
        if scale_name == "PHQ-9":
            thresholds = [(20, "Severe"), (15, "Moderately Severe"), (10, "Moderate"), (5, "Mild"), (0, "Minimal")]
        else: # GAD-7
            thresholds = [(15, "Severe"), (10, "Moderate"), (5, "Mild"), (0, "Minimal")]
        
        severity = next(label for limit, label in thresholds if score >= limit)
        
        conn = sqlite3.connect("therapist_app.db")
        conn.execute("INSERT INTO clinical_scales (username, scale_name, score, severity) VALUES (?,?,?,?)",
                     (self.username, scale_name, score, severity))
        conn.commit(); conn.close()
        
        messagebox.showinfo("Result", f"{scale_name} Score: {score}\nSeverity: {severity}")


# --- MAIN APP CLASS ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Healing Space - AI Integrated Therapist")
        self.geometry("600x950")
        
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 155) 
        except:
            self.engine = None
            print("Speech engine could not initialize.")

        self.pet_manager = None # INTEGRATION: Pet manager holder
        self.safety = SafetyMonitor()
        self.current_user = None
        self.current_session_id = None
        self.added_meds = []
        self.last_ai_message = "" 
        self.ui_settings = {}

        init_db()
        self.load_ui_settings()
        self.apply_ui_settings()
        self.show_disclaimer()
        self.check_remembered_user()
        self.start_notification_timer()
        # Start backup scheduler
        try:
            threading.Thread(target=self._backup_scheduler, daemon=True).start()
        except Exception:
            pass

    def _backup_scheduler(self):
        # Simple daily backup + symmetric encryption using same ENCRYPTION_KEY
        import shutil, time
        backups_dir = os.path.join(os.getcwd(), 'backups')
        os.makedirs(backups_dir, exist_ok=True)
        while True:
            try:
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                src = os.path.join(os.getcwd(), 'therapist_app.db')
                tmp = os.path.join(backups_dir, f'therapist_app_{ts}.db')
                shutil.copy2(src, tmp)
                # Encrypt file if cipher available, otherwise write plaintext backup with .bak
                with open(tmp, 'rb') as f: data = f.read()
                if cipher_suite is None:
                    # No encryption configured; write plaintext fallback and warn
                    with open(tmp + '.bak', 'wb') as f: f.write(data)
                    os.remove(tmp)
                    log_event(None, 'system', 'backup_unencrypted', f'Unencrypted backup created: {tmp}.bak')
                    print('Warning: ENCRYPTION_KEY not configured; created unencrypted backup', tmp + '.bak')
                else:
                    enc = cipher_suite.encrypt(data)
                    with open(tmp + '.enc', 'wb') as f: f.write(enc)
                    os.remove(tmp)
                    log_event(None, 'system', 'backup', f'Backup created: {tmp}.enc')
                # Keep last 7 backups
                files = sorted([f for f in os.listdir(backups_dir) if f.endswith('.enc')])
                while len(files) > 7:
                    old = files.pop(0)
                    try: os.remove(os.path.join(backups_dir, old))
                    except: pass
            except Exception as e:
                print('Backup error:', e)
            time.sleep(24*3600)

    # --- UI Settings management ---
    def load_ui_settings(self):
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        rows = cur.execute("SELECT key, value FROM settings").fetchall()
        conn.close()
        self.ui_settings = {k: v for k, v in rows}

    def save_ui_setting(self, key, value):
        conn = sqlite3.connect("therapist_app.db")
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, str(value)))
        conn.commit(); conn.close()
        self.ui_settings[key] = str(value)

    def apply_ui_settings(self):
        # Appearance
        mode = self.ui_settings.get('appearance_mode', 'dark')
        try: ctk.set_appearance_mode(mode.capitalize())
        except: pass
        accent = self.ui_settings.get('accent_color', 'blue')
        try: ctk.set_default_color_theme(accent)
        except: pass

        # Background & font colors
        bg = self.ui_settings.get('bg_color', '')
        fcol = self.ui_settings.get('font_color', '')
        if bg:
            try: self.configure(bg=bg)
            except: pass

        # Font sizes: attempt to apply to all existing widgets
        try:
            base = int(self.ui_settings.get('font_size', '12'))
        except:
            base = 12

        wraplen = int(min(800, self.winfo_screenwidth() * 0.7))

        def _apply_recursive(w):
            for c in w.winfo_children():
                try:
                    # CTk widgets accept 'font' as CTkFont or tuple
                    c.configure(font=ctk.CTkFont(size=base))
                except Exception:
                    try: c.configure(font=("Arial", base))
                    except Exception: pass
                try:
                    c.configure(wraplength=wraplen)
                except Exception:
                    pass
                try:
                    if fcol:
                        c.configure(text_color=fcol)
                except Exception:
                    pass
                _apply_recursive(c)

        try: _apply_recursive(self)
        except Exception:
            pass

    def check_remembered_user(self):
        conn = sqlite3.connect("therapist_app.db")
        user = conn.cursor().execute("SELECT username FROM users ORDER BY last_login DESC LIMIT 1").fetchone()
        conn.close()
        if user:
            self.setup_quick_login_ui(user[0])
        else:
            self.setup_login_ui()

    def setup_quick_login_ui(self, username):
        self.clear_screen()
        frame = ctk.CTkFrame(self, corner_radius=20)
        frame.pack(pady=60, padx=60, fill="both", expand=True)
        ctk.CTkLabel(frame, text="Healing Space", font=ctk.CTkFont(size=32, weight="bold"), text_color="#3498db", wraplength=400).pack(pady=(40, 20))
        
        user_btn = ctk.CTkButton(frame, text=username, font=ctk.CTkFont(size=22, weight="bold"), height=80, width=250, 
                                 command=lambda: self.quick_pin_login(username))
        user_btn.pack(pady=20)
        
        ctk.CTkLabel(frame, text="Click your name to enter PIN", font=("Segoe UI", 12, "italic")).pack(pady=5)
        
        ctk.CTkButton(frame, text="Switch Account", fg_color="transparent", text_color="gray", border_width=0, 
                     command=self.setup_login_ui).pack(pady=20)

    def quick_pin_login(self, username):
        pin = simpledialog.askstring("Security", f"Enter PIN for {username}:", show='*')
        if pin:
            conn = sqlite3.connect("therapist_app.db")
            res = conn.cursor().execute("SELECT pin FROM users WHERE username=?", (username,)).fetchone()
            if res:
                stored = res[0]
                try:
                    if check_pin(pin, stored):
                        # if stored is plaintext, migrate to hashed form
                        if not (stored.startswith("$2") or stored.startswith("pbkdf2$")):
                            conn.cursor().execute("UPDATE users SET pin=? WHERE username=?", (hash_pin(pin), username))
                        conn.cursor().execute("UPDATE users SET last_login = ? WHERE username = ?", (datetime.now(), username))
                        conn.commit(); conn.close()
                        self.current_user = username
                        log_event(username, "user", "login", "Quick PIN login successful")
                        self.setup_menu_ui()
                        return
                except Exception:
                    pass
            conn.close()
            messagebox.showerror("Error", "Incorrect PIN")

    def toggle_theme(self):
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")

    def start_notification_timer(self):
        def notify_loop():
            while True:
                threading.Event().wait(7200) # 2 Hours
                if self.current_user:
                    try:
                        notification.notify(title="Healing Space", message="It's time for your 2-hour mood check-in!", timeout=10)
                    except: pass
        threading.Thread(target=notify_loop, daemon=True).start()

    def speak_last_message(self):
        if not self.last_ai_message:
            return
        async def amain():
            communicate = edge_tts.Communicate(self.last_ai_message, "en-GB-SoniaNeural")
            await communicate.save("speech.mp3")
            pygame.mixer.init()
            pygame.mixer.music.load("speech.mp3")
            pygame.mixer.music.play() 
        threading.Thread(target=lambda: asyncio.run(amain())).start()

    def show_disclaimer(self):
        disclaimer_text = ("WELCOME TO HEALING SPACE\n\nThis app does not give or replace medical advice.\n\n"
                           "If in danger, call 999 (UK), 988 (USA/CA).")
        messagebox.showinfo("Safety Acknowledgment", disclaimer_text)

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    def setup_login_ui(self):
        self.clear_screen()
        # Admin / Clinician Access Button
        ctk.CTkButton(self, text="Admin / Clinician", width=100, fg_color="transparent", text_color="gray", command=self.admin_login).pack(anchor="ne", padx=10, pady=10)

        frame = ctk.CTkFrame(self, corner_radius=20)
        frame.pack(pady=20, padx=60, fill="both", expand=True)
        ctk.CTkLabel(frame, text="Healing Space", font=ctk.CTkFont(size=32, weight="bold"), text_color="#3498db", wraplength=400).pack(pady=(40, 10))
        self.u_entry = ctk.CTkEntry(frame, placeholder_text="Username", width=250, height=45)
        self.u_entry.pack(pady=10)
        self.u_entry.focus_set()
        self.p_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=250, height=45)
        self.p_entry.pack(pady=10)
        
        ctk.CTkButton(frame, text="Login", command=self.login, width=250, height=45).pack(pady=20)
        ctk.CTkButton(frame, text="Create Account", command=self.setup_signup_ui, fg_color="transparent", border_width=2, text_color="#2ecc71", border_color="#2ecc71").pack()
        
        # Shortcut for login
        self.bind('<Return>', lambda event: self.login())

    def admin_login(self):
        # Prefer clinician account authentication (users.role = 'clinician')
        uname = simpledialog.askstring("Clinician Access", "Clinician Username:")
        if not uname:
            return
        pw = simpledialog.askstring("Clinician Access", "Password:", show="*")
        if not pw:
            return

        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        row = cur.execute("SELECT password, role FROM users WHERE username=?", (uname,)).fetchone()
        conn.close()
        if row and row[1] == 'clinician' and verify_password(row[0], pw):
            log_event(uname, 'clinician', 'login', 'Clinician dashboard accessed')
            ProfessionalDashboard(self)
            return

        # Fallback: admin password sourced from secrets manager (only allowed in DEBUG/local mode)
        admin_pw = secrets.get_secret("ADMIN_PASSWORD") or os.environ.get("ADMIN_PASSWORD")
        if DEBUG and admin_pw and pw == admin_pw:
            ProfessionalDashboard(self)
            return

        messagebox.showerror("Access Denied", "Incorrect credentials or not a clinician account")

    def setup_signup_ui(self):
        self.clear_screen()
        scroll = ctk.CTkScrollableFrame(self, corner_radius=20)
        scroll.pack(pady=40, padx=40, fill="both", expand=True)
        
        ctk.CTkLabel(scroll, text="Join Healing Space", font=ctk.CTkFont(size=24, weight="bold"), text_color="#2ecc71").pack(pady=20)
        
        self.su_name = ctk.CTkEntry(scroll, placeholder_text="Full Name", width=300, height=40); self.su_name.pack(pady=10)
        self.su_name.focus_set()
        self.su_dob = ctk.CTkEntry(scroll, placeholder_text="Date of Birth (DD/MM/YYYY)", width=300, height=40); self.su_dob.pack(pady=10)
        self.su_user = ctk.CTkEntry(scroll, placeholder_text="Choose Username", width=300, height=40); self.su_user.pack(pady=10)
        self.su_pass = ctk.CTkEntry(scroll, placeholder_text="Password", show="*", width=300, height=40); self.su_pass.pack(pady=10)
        
        ctk.CTkLabel(scroll, text="Relevant Medical/Health History:", font=("Arial", 12)).pack(pady=(10, 0))
        self.su_cond = ctk.CTkTextbox(scroll, height=100, width=300, wrap="word"); self.su_cond.pack(pady=10)
        
        ctk.CTkButton(scroll, text="Register Account", command=self.signup_process, width=300, height=50, fg_color="#2ecc71").pack(pady=20)
        ctk.CTkButton(scroll, text="Back to Login", command=self.setup_login_ui, fg_color="transparent").pack()
        
        self.bind('<Return>', lambda event: self.signup_process())

    def signup_process(self):
        user = self.su_user.get()
        full_name = self.su_name.get()
        dob = self.su_dob.get()
        conds = self.su_cond.get("1.0", "end-1c")
        
        if not user or not full_name or not dob:
            messagebox.showerror("Error", "Please fill in Name, DOB, and Username.")
            return

        pw_raw = self.su_pass.get()
        pw = hash_password(pw_raw)
        pin = simpledialog.askstring("Set PIN", "Create a 4-digit security PIN:", show='*')
        
        if not pin or len(pin) != 4:
            messagebox.showerror("Error", "Please enter a 4-digit PIN")
            return

        try:
            # Hash PIN (bcrypt if available, otherwise PBKDF2) before storing
            hashed_pin = hash_pin(pin)
            conn = sqlite3.connect("therapist_app.db")
            conn.cursor().execute('''INSERT INTO users 
                (username, password, pin, last_login, full_name, dob, conditions) 
                VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                (user, pw, hashed_pin, datetime.now(), encrypt_text(full_name), encrypt_text(dob), encrypt_text(conds)))
            conn.commit(); conn.close()
            log_event(user, "system", "signup", "Account created")
            messagebox.showinfo("Success", "Account created! You can now login.")
            self.unbind('<Return>')
            self.setup_login_ui()
        except Exception as e:
            messagebox.showerror("Error", "Username already exists or Database error.")

    def login(self):
        user = getattr(self, 'u_entry', None)
        pw = getattr(self, 'p_entry', None)
        if user is None or pw is None:
            messagebox.showerror("Error", "Login fields unavailable.")
            return
        username = user.get().strip()
        password = pw.get()
        if not username or not password:
            messagebox.showerror("Error", "Enter username and password.")
            return

        # Verify password and support migration from legacy SHA256
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        row = cur.execute("SELECT password, pin FROM users WHERE username=?", (username,)).fetchone()
        if not row:
            conn.close()
            messagebox.showerror("Login Failed", "No such user")
            return

        stored_pw = row[0]
        try:
            if verify_password(stored_pw, password):
                # If stored_pw looks like legacy SHA256, migrate to stronger hash
                if len(stored_pw) == 64 and all(c in '0123456789abcdef' for c in stored_pw.lower()):
                    try:
                        new_h = hash_password(password)
                        cur.execute("UPDATE users SET password=? WHERE username=?", (new_h, username))
                    except Exception:
                        pass

                cur.execute("UPDATE users SET last_login=? WHERE username=?", (datetime.now(), username))
                conn.commit()
                conn.close()
                self.current_user = username
                log_event(username, 'user', 'login', 'Password login successful')
                self.setup_menu_ui()
                return
        except Exception:
            pass

        conn.close()
        messagebox.showerror("Login Failed", "Incorrect username or password")

    def setup_menu_ui(self):
        self.clear_screen()
        ctk.CTkSwitch(self, text="Light/Dark Mode", command=self.toggle_theme).pack(pady=10, padx=20, anchor="ne")
        ctk.CTkLabel(self, text=f"Welcome, {self.current_user}", font=ctk.CTkFont(size=24, weight="bold"), wraplength=500).pack(pady=10)
        
        p_frame = ctk.CTkFrame(self, fg_color="#e74c3c", corner_radius=10)
        p_frame.pack(pady=5, padx=40, fill="x")
        ctk.CTkButton(p_frame, text="🆘 PANIC BUTTON", fg_color="transparent", font=("Arial", 16, "bold"), command=self.trigger_panic).pack(pady=5)
        ctk.CTkButton(p_frame, text="Edit Safety Plan", fg_color="transparent", font=("Arial", 10), command=self.open_safety_plan_editor).pack()

        container = ctk.CTkFrame(self, corner_radius=15)
        container.pack(pady=10, padx=40, fill="x")
        
        # NEW HELP GUIDE BUTTON
        ctk.CTkButton(container, text="❓ Help & Guide", command=self.open_help_guide, fg_color="#7f8c8d", height=45).pack(pady=5, padx=20, fill="x")

        ctk.CTkButton(container,text="🐾 Self-Care Pet",command=self.open_pet_game,    fg_color="#16a085",    height=45).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(container, text="💬 New Conversation", command=self.create_new_session, fg_color="#2ecc71", hover_color="#27ae60", height=45).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(container, text="🧘 Coping Toolbox", command=self.open_coping_window, fg_color="#9b59b6", hover_color="#8e44ad", height=45).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(container, text="👥 Community Support", command=self.open_community, fg_color="#8e44ad", height=45).pack(pady=5, padx=20, fill="x") 
        
        # UPDATED CLINICAL SCALES BUTTON (WITH CHECK)
        ctk.CTkButton(container, text="📋 Clinical Scales", command=self.check_clinical_access, fg_color="#34495e", height=45).pack(pady=5, padx=20, fill="x")
        
        ctk.CTkButton(container, text="📊 Mood Tracker", command=self.open_mood_tracker, fg_color="#e67e22", hover_color="#d35400", height=45).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(container, text="📈 Progress Insights & PDF", command=self.show_insights, fg_color="#3498db", height=45).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(container, text="⚙️ Settings", command=self.open_settings, fg_color="#95a5a6", height=45).pack(pady=5, padx=20, fill="x")
        
        ctk.CTkLabel(self, text="Recent Sessions:", font=("Segoe UI", 12, "italic"), wraplength=500).pack(pady=10)
        conn = sqlite3.connect("therapist_app.db")
        sessions = conn.cursor().execute("SELECT session_id, title FROM sessions WHERE username=? ORDER BY created_at DESC LIMIT 3", (self.current_user,)).fetchall()
        conn.close()
        for sid, title in sessions:
            f = ctk.CTkFrame(self, corner_radius=10)
            f.pack(pady=2, padx=40, fill="x")
            ctk.CTkButton(f, text=title, command=lambda s=sid: self.load_session(s), fg_color="#34495e", anchor="w").pack(side="left", fill="x", expand=True, padx=5)
            ctk.CTkButton(f, text="✖", width=35, fg_color="#e74c3c", command=lambda s=sid: self.delete_session(s)).pack(side="right", padx=5)
        ctk.CTkButton(self, text="Logout", command=self.check_remembered_user, fg_color="transparent", text_color="#e74c3c", border_width=1).pack(pady=20)

    # --- NEW: Help Guide ---
    def open_help_guide(self):
        h_win = ctk.CTkToplevel(self)
        h_win.title("Help & Guide")
        h_win.geometry("500x600")
        
        text_area = scrolledtext.ScrolledText(h_win, wrap="word", width=50, height=30, font=("Arial", 12))
        text_area.pack(pady=20, padx=20, fill="both", expand=True)
        text_area.insert("end", HELP_GUIDE_TEXT)
        text_area.configure(state='disabled') # Read only

    def open_settings(self):
        s = ctk.CTkToplevel(self)
        s.title("Settings")
        s.geometry("480x420")
        # Read current settings
        font_size = int(self.ui_settings.get('font_size', '12'))
        appearance = self.ui_settings.get('appearance_mode', 'dark')
        accent = self.ui_settings.get('accent_color', 'blue')
        bg = self.ui_settings.get('bg_color', '')
        fcol = self.ui_settings.get('font_color', '')

        ctk.CTkLabel(s, text="Appearance & Fonts", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        fs_frame = ctk.CTkFrame(s); fs_frame.pack(pady=6, padx=10, fill="x")
        ctk.CTkLabel(fs_frame, text="Base Font Size:").pack(side="left", padx=6)
        size_var = tk.IntVar(value=font_size)
        ctk.CTkSlider(fs_frame, from_=8, to=28, number_of_steps=20, variable=size_var).pack(side="left", padx=6, fill="x", expand=True)

        mode_frame = ctk.CTkFrame(s); mode_frame.pack(pady=6, padx=10, fill="x")
        ctk.CTkLabel(mode_frame, text="Theme Mode:").pack(side="left", padx=6)
        mode_var = tk.StringVar(value=appearance)
        ctk.CTkOptionMenu(mode_frame, values=["dark", "light"], variable=mode_var).pack(side="left", padx=6)

        accent_frame = ctk.CTkFrame(s); accent_frame.pack(pady=6, padx=10, fill="x")
        ctk.CTkLabel(accent_frame, text="Accent Color:").pack(side="left", padx=6)
        accent_var = tk.StringVar(value=accent)
        ctk.CTkOptionMenu(accent_frame, values=["blue","green","purple","dark-blue","red"], variable=accent_var).pack(side="left", padx=6)

        color_frame = ctk.CTkFrame(s); color_frame.pack(pady=6, padx=10, fill="x")
        ctk.CTkLabel(color_frame, text="Background Color:").pack(side="left", padx=6)
        bg_btn = ctk.CTkButton(color_frame, text="Choose", command=lambda: pick_color('bg'))
        bg_btn.pack(side="left", padx=6)
        ctk.CTkLabel(color_frame, text="Font Color:").pack(side="left", padx=6)
        f_btn = ctk.CTkButton(color_frame, text="Choose", command=lambda: pick_color('font'))
        f_btn.pack(side="left", padx=6)

        def pick_color(which):
            col = colorchooser.askcolor()[1]
            if not col: return
            if which == 'bg':
                self.save_ui_setting('bg_color', col)
            else:
                self.save_ui_setting('font_color', col)

        def apply_and_close():
            self.save_ui_setting('font_size', int(size_var.get()))
            self.save_ui_setting('appearance_mode', mode_var.get())
            self.save_ui_setting('accent_color', accent_var.get())
            self.load_ui_settings(); self.apply_ui_settings()
            messagebox.showinfo("Settings", "Applied. Some windows may refresh to apply fonts.")
            s.destroy()

        ctk.CTkButton(s, text="Apply", command=apply_and_close, fg_color="#2ecc71").pack(pady=14)

        # --- Clinician Provisioning ---
        ctk.CTkLabel(s, text="Clinician Provisioning", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(8,4))
        cp_frame = ctk.CTkFrame(s); cp_frame.pack(pady=4, padx=10, fill="x")
        ctk.CTkLabel(cp_frame, text="New Clinician Username:").grid(row=0, column=0, padx=6, pady=4, sticky="w")
        new_user = ctk.CTkEntry(cp_frame); new_user.grid(row=0, column=1, padx=6, pady=4)
        ctk.CTkLabel(cp_frame, text="Password:").grid(row=1, column=0, padx=6, pady=4, sticky="w")
        new_pass = ctk.CTkEntry(cp_frame, show='*'); new_pass.grid(row=1, column=1, padx=6, pady=4)

        def create_clinician():
            u = new_user.get().strip(); p = new_pass.get()
            if not u or not p:
                messagebox.showerror("Error", "Enter username and password")
                return
            h = hashlib.sha256(p.encode()).hexdigest()
            conn = sqlite3.connect('therapist_app.db')
            try:
                conn.execute("INSERT OR REPLACE INTO users (username,password,role,last_login) VALUES (?,?,?,?)", (u, h, 'clinician', datetime.now()))
                conn.commit()
                messagebox.showinfo("Clinician", f"Created clinician {u}")
                log_event(u, 'system', 'create_clinician', f'Provisioned by {self.current_user or "system"}')
            except Exception as e:
                messagebox.showerror("Error", f"Could not create clinician: {e}")
            finally:
                conn.close()

        ctk.CTkButton(s, text="Create Clinician", command=create_clinician, fg_color="#2980b9").pack(pady=8)

    # --- NEW: Clinical Access Check ---
    def check_clinical_access(self):
        conn = sqlite3.connect("therapist_app.db")
        last = conn.cursor().execute(
            "SELECT entry_timestamp FROM clinical_scales WHERE username=? ORDER BY entry_timestamp DESC LIMIT 1", 
            (self.current_user,)
        ).fetchone()
        conn.close()

        if last:
            try:
                # Handle potential variation in timestamp format
                try:
                    last_date = datetime.strptime(last[0], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    last_date = datetime.strptime(last[0], '%Y-%m-%d %H:%M:%S.%f')
                
                days_since = (datetime.now() - last_date).days
                if days_since < 14:
                    wait_days = 14 - days_since
                    messagebox.showinfo("Clinical Access", f"You completed an assessment {days_since} days ago.\n\nTo ensure accurate tracking, please wait {wait_days} more days.")
                    return
            except Exception as e:
                print(f"Date error: {e}")
                # Fallback: Allow access if error parsing date
        
        # If no previous record OR > 14 days, allow
        ClinicalScales(self, self.current_user)

    # --- NEW: Community Support (Simulated P2P) ---
    def open_community(self):
        c_win = ctk.CTkToplevel(self)
        c_win.title("Community Support Board")
        c_win.geometry("500x600")
        
        ctk.CTkLabel(c_win, text="Community Messages", font=("Arial", 20, "bold")).pack(pady=10)
        ctk.CTkLabel(c_win, text="Share encouragement with others anonymously.", font=("Arial", 10, "italic")).pack()
        
        scroll = ctk.CTkScrollableFrame(c_win)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        def refresh():
            for w in scroll.winfo_children(): w.destroy()
            conn = sqlite3.connect("therapist_app.db")
            posts = conn.cursor().execute("SELECT username, message, likes FROM community_posts ORDER BY entry_timestamp DESC LIMIT 20").fetchall()
            conn.close()
            for p in posts:
                f = ctk.CTkFrame(scroll)
                f.pack(fill="x", pady=5)
                # Obfuscate username for privacy
                u_display = p[0][:2] + "***" 
                ctk.CTkLabel(f, text=u_display, text_color="#3498db", font=("Arial", 10, "bold")).pack(anchor="w", padx=5)
                ctk.CTkLabel(f, text=p[1], wraplength=400, justify="left").pack(anchor="w", padx=5)
                ctk.CTkLabel(f, text=f"❤️ {p[2]}", font=("Arial", 10)).pack(anchor="e", padx=5)

        entry = ctk.CTkEntry(c_win, placeholder_text="Write something kind...")
        entry.pack(fill="x", padx=10, pady=5)
        
        def post():
            if not entry.get(): return
            conn = sqlite3.connect("therapist_app.db")
            conn.execute("INSERT INTO community_posts (username, message) VALUES (?,?)", (self.current_user, entry.get()))
            conn.commit(); conn.close()
            entry.delete(0, 'end')
            refresh()
            
        ctk.CTkButton(c_win, text="Post Message", command=post).pack(pady=10)
        refresh()

    def open_safety_plan_editor(self):
        win = ctk.CTkToplevel(self); win.title("My Safety Plan"); win.geometry("500x600")
        win.bind('<Escape>', lambda e: win.destroy())
        ctk.CTkLabel(win, text="Safety Plan", font=("Arial", 20, "bold")).pack(pady=20)
        
        t_ent = ctk.CTkEntry(win, placeholder_text="My Triggers (e.g. darkness, loud noise)..."); t_ent.pack(pady=10, padx=20, fill="x")
        t_ent.focus_set()
        c_ent = ctk.CTkEntry(win, placeholder_text="Internal Coping (e.g. music, tea)..."); c_ent.pack(pady=10, padx=20, fill="x")
        co_ent = ctk.CTkEntry(win, placeholder_text="Professional Contacts/Friends..."); co_ent.pack(pady=10, padx=20, fill="x")

        def save_plan():
            conn = sqlite3.connect("therapist_app.db")
            conn.execute("INSERT OR REPLACE INTO safety_plans VALUES (?,?,?,?)", (self.current_user, t_ent.get(), c_ent.get(), co_ent.get()))
            conn.commit(); conn.close(); win.destroy()
            messagebox.showinfo("Saved", "Your safety plan is updated.")

        ctk.CTkButton(win, text="Save Plan", command=save_plan).pack(pady=20)
        win.bind('<Return>', lambda e: save_plan())

    def open_sleep_hygiene(self):
        win = ctk.CTkToplevel(self); win.title("Sleep Wind-Down"); win.geometry("400x500")
        win.bind('<Escape>', lambda e: win.destroy())
        ctk.CTkLabel(win, text="Digital Sunset Checklist", font=("Arial", 18, "bold")).pack(pady=20)
        tasks = ["Lights Dimmed", "Phone on Do Not Disturb", "No Screens for 30 mins", "Gratitude Recorded", "Deep Breathing Done"]
        for t in tasks:
            ctk.CTkCheckBox(win, text=t).pack(pady=10, padx=40, anchor="w")

    def open_gratitude_journal(self):
        g_win = ctk.CTkToplevel(self); g_win.title("Gratitude Journal"); g_win.geometry("500x650")
        g_win.bind('<Escape>', lambda e: g_win.destroy())
        ctk.CTkLabel(g_win, text="What are you grateful for?", font=("Arial", 18, "bold")).pack(pady=15)
        entry = ctk.CTkTextbox(g_win, height=100, wrap="word"); entry.pack(pady=10, padx=20, fill="x")
        entry.focus_set()
        def save_gratitude():
            txt = entry.get("1.0", "end-1c")
            if txt.strip():
                enc_txt = encrypt_text(txt)
                conn = sqlite3.connect("therapist_app.db")
                conn.cursor().execute("INSERT INTO gratitude_logs (username, entry) VALUES (?,?)", (self.current_user, enc_txt))
                conn.commit(); conn.close()
                if self.pet_manager: self.pet_manager.reward("diary") # INTEGRATION: Reward Pet
                messagebox.showinfo("Saved", "Focusing on the good helps the mind heal. (+5 Coins)")
                g_win.destroy()
        ctk.CTkButton(g_win, text="Save Entry (Encrypted)", command=save_gratitude, fg_color="#1abc9c").pack(pady=10)
        
        scroll = ctk.CTkScrollableFrame(g_win); scroll.pack(fill="both", expand=True, padx=20, pady=20)
        conn = sqlite3.connect("therapist_app.db")
        logs = conn.cursor().execute("SELECT entry, entry_timestamp FROM gratitude_logs WHERE username=? ORDER BY entry_timestamp DESC", (self.current_user,)).fetchall()
        conn.close()
        for log in logs:
            dec_log = decrypt_text(log[0])
            ctk.CTkLabel(scroll, text=f"{log[1][:10]}: {dec_log}", wraplength=400, justify="left", font=("Segoe UI", 11)).pack(pady=5, anchor="w")

    def trigger_panic(self):
        # NEW: Send automated alert simulation
        self.safety.send_crisis_alert(self.current_user)
        log_event(self.current_user, "system", "crisis_alert", "Panic button pressed; crisis alert sent")
        
        p = ctk.CTkToplevel(self); p.title("EMERGENCY HELP"); p.geometry("400x500")
        p.bind('<Escape>', lambda e: p.destroy())
        ctk.CTkLabel(p, text="YOU ARE NOT ALONE", font=("Arial", 20, "bold"), text_color="#e74c3c", wraplength=350).pack(pady=20)
        conn = sqlite3.connect("therapist_app.db")
        plan = conn.cursor().execute("SELECT triggers, coping, contacts FROM safety_plans WHERE username=?", (self.current_user,)).fetchone()
        conn.close()
        if plan:
            ctk.CTkLabel(p, text=f"My Coping: {plan[1]}", font=("Arial", 14), wraplength=350).pack(pady=5)
            ctk.CTkLabel(p, text=f"Call: {plan[2]}", font=("Arial", 14, "bold"), text_color="#3498db").pack(pady=5)
        
        ctk.CTkLabel(p, text="Alert Sent to Professional Contacts", text_color="red", font=("Arial", 10, "bold")).pack(pady=5)
        ctk.CTkLabel(p, text=CRISIS_RESOURCES, justify="left", wraplength=350).pack(pady=10)
        ctk.CTkButton(p, text="Start Grounding Exercise", command=self.grounding_exercise).pack(pady=20)

    def open_mood_tracker(self):
        m_win = ctk.CTkToplevel(self); m_win.title("Mood, Habits & Meds"); m_win.geometry("620x950")
        m_win.bind('<Escape>', lambda e: m_win.destroy())
        entry_card = ctk.CTkScrollableFrame(m_win, corner_radius=15); entry_card.pack(pady=20, padx=20, fill="both", expand=True)
        mood_label = ctk.CTkLabel(entry_card, text="Mood: 5/10", font=("Arial", 14, "bold")); mood_label.pack(pady=(10,0))
        mood_s = ctk.CTkSlider(entry_card, from_=1, to=10, number_of_steps=9, command=lambda v: mood_label.configure(text=f"Mood: {int(v)}/10"))
        mood_s.set(5); mood_s.pack(pady=5)
        sleep_label = ctk.CTkLabel(entry_card, text="Sleep: 7.0 Hours", font=("Arial", 14, "bold")); sleep_label.pack(pady=(10,0))
        sleep_s = ctk.CTkSlider(entry_card, from_=0, to=15, number_of_steps=30, command=lambda v: sleep_label.configure(text=f"Sleep: {round(float(v), 1)} Hours"))
        sleep_s.set(7); sleep_s.pack(pady=5)
        ctk.CTkLabel(entry_card, text="Daily Quantities", font=("Arial", 14, "bold"), wraplength=500).pack(pady=10)
        h_frame = ctk.CTkFrame(entry_card, fg_color="transparent"); h_frame.pack(pady=5)
        ctk.CTkLabel(h_frame, text="Water (Pints):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        water_ent = ctk.CTkEntry(h_frame, width=60); water_ent.insert(0, "0"); water_ent.grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(h_frame, text="Exercise (Mins):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ex_ent = ctk.CTkEntry(h_frame, width=60); ex_ent.insert(0, "0"); ex_ent.grid(row=1, column=1, padx=5, pady=5)
        ctk.CTkLabel(h_frame, text="Outdoors (Mins):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        out_ent = ctk.CTkEntry(h_frame, width=60); out_ent.insert(0, "0"); out_ent.grid(row=2, column=1, padx=5, pady=5)
        self.added_meds = []
        med_frame = ctk.CTkFrame(entry_card, fg_color="transparent"); med_frame.pack(pady=10)
        m_name = ctk.CTkEntry(med_frame, placeholder_text="Med Name", width=120); m_name.pack(side="left", padx=2)
        m_str = ctk.CTkEntry(med_frame, placeholder_text="Str (mg)", width=90); m_str.pack(side="left", padx=2)
        m_qty = ctk.CTkEntry(med_frame, placeholder_text="Qty", width=40); m_qty.pack(side="left", padx=2)
        med_list_disp = ctk.CTkFrame(entry_card, height=60); med_list_disp.pack(pady=5, padx=20, fill="x")
        def add_m():
            if m_name.get():
                txt = f"{m_name.get()} {m_str.get()} (x{m_qty.get() or '1'})"
                self.added_meds.append(txt)
                row = ctk.CTkFrame(med_list_disp, fg_color="transparent"); row.pack(fill="x")
                ctk.CTkLabel(row, text=txt, wraplength=300).pack(side="left")
                ctk.CTkButton(row, text="X", width=30, fg_color="#c0392b", command=lambda r=row, t=txt: [r.destroy(), self.added_meds.remove(t)]).pack(side="right")
                m_name.delete(0, 'end'); m_str.delete(0, 'end'); m_qty.delete(0, 'end')
        ctk.CTkButton(med_frame, text="+", width=40, command=add_m).pack(side="left", padx=5)
        ctk.CTkLabel(entry_card, text="Journal Notes", wraplength=500).pack()
        notes_box = ctk.CTkTextbox(entry_card, height=80, wrap="word"); notes_box.pack(pady=10, padx=20, fill="x")
        def save():
            text_content = notes_box.get("1.0", "end-1c")
            enc_notes = encrypt_text(text_content)
            sentiment = TherapistAI().analyze_sentiment(text_content) if len(text_content) > 5 else "Neutral"
            try:
                w_val, e_val, o_val = float(water_ent.get() or 0), int(ex_ent.get() or 0), int(out_ent.get() or 0)
            except:
                messagebox.showerror("Error", "Enter valid numbers."); return
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conn = sqlite3.connect("therapist_app.db")
            conn.cursor().execute('''INSERT INTO mood_logs (username, mood_val, sleep_val, meds, notes, sentiment, exercise_mins, outside_mins, water_pints, entry_timestamp) VALUES (?,?,?,?,?,?,?,?,?,?)''', (self.current_user, int(mood_s.get()), sleep_s.get(), ", ".join(self.added_meds), enc_notes, sentiment, e_val, o_val, w_val, now))
            conn.commit(); conn.close()
            if self.pet_manager: self.pet_manager.reward("medication") # INTEGRATION: Reward Pet
            messagebox.showinfo("Saved", f"Log saved! (+5 Coins) Detected Mood: {sentiment}")
            m_win.destroy(); self.open_mood_tracker()
        ctk.CTkButton(entry_card, text="Save Entry", fg_color="#2ecc71", command=save).pack(pady=10)
        ctk.CTkButton(entry_card, text="📥 Export Data (CSV)", fg_color="#34495e", command=self.export_data).pack(pady=5)
        ctk.CTkButton(entry_card, text="⚠️ Reset Mood History", fg_color="#e74c3c", command=lambda: self.reset_history(m_win)).pack(pady=5)
        self.draw_graphs(entry_card)

    def reset_history(self, window_to_close):
        confirm = messagebox.askyesno("Confirm Reset", "Are you sure you want to permanently delete ALL logs?")
        if confirm:
            conn = sqlite3.connect("therapist_app.db")
            conn.cursor().execute("DELETE FROM mood_logs WHERE username=?", (self.current_user,))
            conn.commit(); conn.close()
            messagebox.showinfo("Reset Successful", "All mood history has been cleared.")
            window_to_close.destroy(); self.open_mood_tracker()

    # --- UPDATED PDF EXPORT (Inside App class) ---
    def export_data_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="Healing Space - Clinical Progress Report", ln=True, align='C')
        
        conn = sqlite3.connect("therapist_app.db")
        # Include basic profile (decrypted) at top
        cursor = conn.cursor()
        profile = cursor.execute("SELECT full_name, dob, conditions FROM users WHERE username=?", (self.current_user,)).fetchone()
        if profile:
            try:
                full_name = decrypt_text(profile[0])
            except: full_name = "(Unable to decrypt)"
            try:
                dob = decrypt_text(profile[1])
            except: dob = "(Unable to decrypt)"
            try:
                cond = decrypt_text(profile[2])
            except: cond = "(Unable to decrypt)"
            pdf.set_font("Arial", size=11)
            pdf.multi_cell(0, 6, txt=f"User: {self.current_user} | Name: {full_name} | DOB: {dob}")
            pdf.multi_cell(0, 6, txt=f"Relevant History: {cond}")
            pdf.ln(3)

        # 1. Clinical Assessments Section
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="Clinical Assessments (PHQ-9 & GAD-7)", ln=True)
        pdf.set_font("Arial", size=11)
        scales = cursor.execute("SELECT scale_name, score, severity, entry_timestamp FROM clinical_scales WHERE username=? ORDER BY entry_timestamp DESC", (self.current_user,)).fetchall()
        for s in scales:
            line = f"[{s[3]}] {s[0]}: Score {s[1]} ({s[2]})"
            pdf.multi_cell(0, 6, txt=line)

        # 2. Mood & Health Summary
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="Mood & Habit History", ln=True)
        pdf.set_font("Arial", size=11)
        moods = cursor.execute("SELECT mood_val, sleep_val, meds, notes, entry_timestamp FROM mood_logs WHERE username=? ORDER BY entry_timestamp DESC", (self.current_user,)).fetchall()
        for m in moods:
            notes = decrypt_text(m[3]) if m[3] else ""
            line = f"Date: {m[4]} | Mood: {m[0]}/10 | Sleep: {m[1]}hrs | Meds: {m[2]}"
            pdf.multi_cell(0, 6, txt=line)
            if notes:
                pdf.multi_cell(0, 6, txt=f"Notes: {notes}")

        # 3. Gratitude Entries
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="Gratitude Journal Entries", ln=True)
        pdf.set_font("Arial", size=11)
        grats = cursor.execute("SELECT entry, entry_timestamp FROM gratitude_logs WHERE username=? ORDER BY entry_timestamp DESC", (self.current_user,)).fetchall()
        for g in grats:
            try: text = decrypt_text(g[0])
            except: text = "(Unable to decrypt)"
            pdf.multi_cell(0, 6, txt=f"[{g[1]}] {text}")

        # 4. CBT records
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "CBT Records", ln=True)
        pdf.set_font("Arial", size=11)
        cbt = cursor.execute("SELECT situation, thought, evidence, entry_timestamp FROM cbt_records WHERE username=? ORDER BY entry_timestamp DESC", (self.current_user,)).fetchall()
        for c in cbt:
            sit = decrypt_text(c[0]) if c[0] else ""
            thought = decrypt_text(c[1]) if c[1] else ""
            evidence = decrypt_text(c[2]) if c[2] else ""
            pdf.multi_cell(0, 6, txt=f"[{c[3]}] Situation: {sit}")
            pdf.multi_cell(0, 6, txt=f"Thought: {thought}")
            pdf.multi_cell(0, 6, txt=f"Evidence: {evidence}")
            pdf.multi_cell(0, 6, txt='---')

        # 5. AI Memory Summary (if present)
        mem = cursor.execute("SELECT memory_summary, last_updated FROM ai_memory WHERE username=?", (self.current_user,)).fetchone()
        if mem:
            try: memtxt = decrypt_text(mem[0])
            except: memtxt = "(Unable to decrypt)"
            pdf.ln(3)
            pdf.set_font("Arial", 'B', 14); pdf.cell(200, 8, txt="AI Memory Summary", ln=True)
            pdf.set_font("Arial", size=11); pdf.multi_cell(0, 6, txt=memtxt)

        conn.close()
        path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if path:
            pdf.output(path)
            messagebox.showinfo("Success", "Clinical report exported successfully.")

    def export_data(self):
        """Export core user data to a single CSV file with clear sections."""
        if not self.current_user:
            messagebox.showerror("Error", "No user selected to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not path: return
        conn = sqlite3.connect("therapist_app.db")
        cur = conn.cursor()
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Profile
            writer.writerow(["USER PROFILE"])
            prof = cur.execute("SELECT full_name, dob, conditions FROM users WHERE username=?", (self.current_user,)).fetchone()
            if prof:
                writer.writerow(["username", self.current_user])
                writer.writerow(["full_name", decrypt_text(prof[0])])
                writer.writerow(["dob", decrypt_text(prof[1])])
                writer.writerow(["conditions", decrypt_text(prof[2])])
            writer.writerow([])

            # Mood logs
            writer.writerow(["MOOD_LOGS"])
            writer.writerow(["timestamp", "mood_val", "sleep_val", "meds", "notes", "sentiment", "exercise_mins", "outside_mins", "water_pints"])
            for r in cur.execute("SELECT entry_timestamp, mood_val, sleep_val, meds, notes, sentiment, exercise_mins, outside_mins, water_pints FROM mood_logs WHERE username=? ORDER BY entry_timestamp DESC", (self.current_user,)).fetchall():
                notes = decrypt_text(r[4]) if r[4] else ""
                writer.writerow([r[0], r[1], r[2], r[3], notes, r[5], r[6], r[7], r[8]])
            writer.writerow([])

            # Gratitude
            writer.writerow(["GRATITUDE_LOGS"])
            writer.writerow(["timestamp", "entry"])
            for r in cur.execute("SELECT entry_timestamp, entry FROM gratitude_logs WHERE username=? ORDER BY entry_timestamp DESC", (self.current_user,)).fetchall():
                writer.writerow([r[0], decrypt_text(r[1])])
            writer.writerow([])

            # CBT
            writer.writerow(["CBT_RECORDS"])
            writer.writerow(["timestamp", "situation", "thought", "evidence"])
            for r in cur.execute("SELECT entry_timestamp, situation, thought, evidence FROM cbt_records WHERE username=? ORDER BY entry_timestamp DESC", (self.current_user,)).fetchall():
                writer.writerow([r[0], decrypt_text(r[1]), decrypt_text(r[2]), decrypt_text(r[3])])
            writer.writerow([])

            # Clinical Scales
            writer.writerow(["CLINICAL_SCALES"])
            writer.writerow(["timestamp", "scale_name", "score", "severity"])
            for r in cur.execute("SELECT entry_timestamp, scale_name, score, severity FROM clinical_scales WHERE username=? ORDER BY entry_timestamp DESC", (self.current_user,)).fetchall():
                writer.writerow([r[0], r[1], r[2], r[3]])

        conn.close()
        messagebox.showinfo("Export", f"Data exported to {path}")
    def draw_graphs(self, parent):
        conn = sqlite3.connect("therapist_app.db")
        data = conn.cursor().execute("SELECT mood_val, sleep_val, entry_timestamp FROM mood_logs WHERE username=? ORDER BY entry_timestamp DESC LIMIT 7", (self.current_user,)).fetchall()
        conn.close()
        if len(data) < 2: return
        data.reverse()
        self.create_chart(parent, "Mood Trend (1-10)", [d[0] for d in data], [d[2] for d in data], 10, "#3498db")
        self.create_chart(parent, "Sleep Trend (Hours)", [d[1] for d in data], [d[2] for d in data], 15, "#f1c40f")

    def create_chart(self, parent, title, values, stamps, max_y, color):
        ctk.CTkLabel(parent, text=title, wraplength=500).pack()
        canvas = tk.Canvas(parent, width=500, height=150, bg="#1e1e1e", highlightthickness=0); canvas.pack(pady=5)
        points = []
        for i, v in enumerate(values):
            x = 50 + (i * 65); y = 130 - (v * (100 / max_y))
            points.append((x, y))
            canvas.create_oval(x-2, y-2, x+2, y+2, fill=color)
            ts = datetime.strptime(stamps[i], '%Y-%m-%d %H:%M:%S').strftime("%d/%m")
            canvas.create_text(x, 145, text=ts, fill="gray", font=("Arial", 7))
        if len(points) > 1: canvas.create_line(points, fill=color, width=2)

    def show_insights(self):
        win = ctk.CTkToplevel(self); win.title("AI Progress Analysis"); win.geometry("600x850")
        win.bind('<Escape>', lambda e: win.destroy())
        scroll = ctk.CTkScrollableFrame(win); scroll.pack(fill="both", expand=True, padx=10, pady=10)
        conn = sqlite3.connect("therapist_app.db")
        logs = conn.cursor().execute("SELECT mood_val, sleep_val, meds, notes, sentiment, exercise_mins, outside_mins, water_pints, entry_timestamp FROM mood_logs WHERE username=? ORDER BY entry_timestamp DESC LIMIT 10", (self.current_user,)).fetchall()
        grats = conn.cursor().execute("SELECT entry, entry_timestamp FROM gratitude_logs WHERE username=? ORDER BY entry_timestamp DESC LIMIT 10", (self.current_user,)).fetchall()
        cbt = conn.cursor().execute("SELECT situation, thought, evidence, entry_timestamp FROM cbt_records WHERE username=? ORDER BY entry_timestamp DESC LIMIT 10", (self.current_user,)).fetchall()
        plan = conn.cursor().execute("SELECT triggers, coping FROM safety_plans WHERE username=?", (self.current_user,)).fetchone() or ("None", "None")
        conn.close()
        
        if len(logs) < 1:
            ctk.CTkLabel(scroll, text="Log data to see insights!", wraplength=500).pack(pady=50); return

        ctk.CTkButton(scroll, text="📄 Generate ALL-DATA PDF Report", fg_color="#e67e22", command=lambda: self.generate_pdf_report(logs, grats, cbt, plan)).pack(pady=10)
        ctk.CTkLabel(scroll, text="Visual Consistency (Last 7 Logs)", font=("Arial", 16, "bold"), wraplength=550).pack(pady=10)
        self.draw_habit_chart(scroll, logs[:7])
        ctk.CTkLabel(scroll, text="AI Holistic Progress Opinion", font=("Arial", 16, "bold"), text_color="#3498db", wraplength=550).pack(pady=20)
        insight_box = ctk.CTkLabel(scroll, text="AI is synthesizing all records...", font=("Arial", 12), wraplength=550, justify="left"); insight_box.pack(pady=10, padx=20)
        
        def get_ai_opinion():
            processed_logs = [[l[0], l[1], l[2], decrypt_text(l[3]), l[4], l[5], l[6], l[7], l[8]] for l in logs]
            processed_grats = [[decrypt_text(g[0]), g[1]] for g in grats]
            processed_cbt = [[decrypt_text(c[0]), decrypt_text(c[1]), decrypt_text(c[2]), c[3]] for c in cbt]
            opinion = TherapistAI(self.current_user).analyze_progress(processed_logs, processed_grats, processed_cbt, plan)
            try:
                insight_box.configure(text=opinion)
            except Exception:
                # widget may have been destroyed; ignore
                pass
        threading.Thread(target=get_ai_opinion).start()

    def generate_pdf_report(self, logs, grats, cbt, plan):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not file_path: return
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt=f"Full Wellness Portfolio: {self.current_user}", ln=True, align='C')
        pdf.ln(5)
        
        # Safety Plan Section
        pdf.set_font("Arial", 'B', 12); pdf.cell(200, 10, txt="1. Safety Plan", ln=True)
        pdf.set_font("Arial", size=10); pdf.multi_cell(0, 5, txt=f"Triggers: {plan[0]}\nCoping: {plan[1]}")
        pdf.ln(5)

        # Mood Logs Section
        pdf.set_font("Arial", 'B', 12); pdf.cell(200, 10, txt="2. Mood & Health History", ln=True)
        pdf.set_font("Arial", size=9)
        for l in logs[:10]:
            pdf.cell(200, 7, txt=f"[{l[8]}] Mood: {l[0]}/10 | Sleep: {l[1]}h | Meds: {l[2]}", ln=True)
            pdf.multi_cell(0, 5, txt=f"Notes: {decrypt_text(l[3])}")
            pdf.ln(2)

        # Gratitude Section
        pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.cell(200, 10, txt="3. Gratitude Journal", ln=True)
        pdf.set_font("Arial", size=9)
        for g in grats[:10]:
            pdf.multi_cell(0, 5, txt=f"[{g[1]}]: {decrypt_text(g[0])}")
            pdf.ln(2)

        # CBT Section
        pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.cell(200, 10, txt="4. CBT Thought Challenges", ln=True)
        for c in cbt[:10]:
            pdf.set_font("Arial", 'I', 9); pdf.cell(0, 5, txt=f"Entry Date: {c[3]}", ln=True)
            pdf.set_font("Arial", size=9)
            pdf.multi_cell(0, 5, txt=f"Situation: {decrypt_text(c[0])}\nThought: {decrypt_text(c[1])}\nEvidence: {decrypt_text(c[2])}")
            pdf.ln(3)
        
        # Clinical Scales Section (NEW)
        pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.cell(200, 10, txt="5. Clinical Assessment History (PHQ-9)", ln=True)
        pdf.set_font("Arial", size=9)
        conn = sqlite3.connect("therapist_app.db")
        scales = conn.cursor().execute("SELECT entry_timestamp, score, severity FROM clinical_scales WHERE username=? ORDER BY entry_timestamp DESC LIMIT 10", (self.current_user,)).fetchall()
        conn.close()
        if not scales:
            pdf.cell(0, 5, txt="No clinical assessments recorded yet.", ln=True)
        for s in scales:
            pdf.cell(0, 5, txt=f"Date: {s[0]} | Score: {s[1]} | Result: {s[2]}", ln=True)

        pdf.output(file_path)
        try:
            messagebox.showinfo("Success", "Consolidated PDF Report Exported (Includes Clinical Scales).")
        except Exception:
            # If the UI is closing or unavailable, avoid crashing.
            pass

    def draw_habit_chart(self, parent, logs):
        canvas = tk.Canvas(parent, width=500, height=200, bg="#1a1a1a", highlightthickness=0); canvas.pack(pady=10)
        for i, l in enumerate(reversed(logs)):
            x_base = 60 + (i * 60)
            canvas.create_rectangle(x_base, 180, x_base+10, 180-(l[0]*15), fill="#3498db") 
            canvas.create_rectangle(x_base+12, 180, x_base+22, 180-(l[7]*10), fill="#1abc9c") 
            ex_h = min(l[5], 60); canvas.create_rectangle(x_base+24, 180, x_base+34, 180-(ex_h), fill="#9b59b6") 
            ts = datetime.strptime(l[8], '%Y-%m-%d %H:%M:%S').strftime("%d/%m")
            canvas.create_text(x_base+15, 190, text=ts, fill="white", font=("Arial", 8))

    def open_coping_window(self):
        win = ctk.CTkToplevel(self); win.title("Coping Toolbox"); win.geometry("400x550")
        win.bind('<Escape>', lambda e: win.destroy())
        ctk.CTkLabel(win, text="Exercises", font=("Arial", 18, "bold"), wraplength=350).pack(pady=20)
        ctk.CTkButton(win, text="Box Breathing", command=self.box_breathing, height=45).pack(pady=10, padx=40, fill="x")
        ctk.CTkButton(win, text="5-4-3-2-1 Grounding", command=self.grounding_exercise, height=45).pack(pady=10, padx=40, fill="x")
        ctk.CTkButton(win, text="CBT Thought Record", command=self.open_cbt_tool, height=45, fg_color="#34495e").pack(pady=10, padx=40, fill="x")
        ctk.CTkButton(win, text="Affirmation ✨", command=lambda: messagebox.showinfo("Affirmation", random.choice(["I am resilient.", "My feelings are valid.", "I am worthy."])), height=45).pack(pady=10, padx=40, fill="x")

    def open_cbt_tool(self):
        c = ctk.CTkToplevel(self); c.title("CBT Record"); c.geometry("500x600")
        c.bind('<Escape>', lambda e: c.destroy())
        ctk.CTkLabel(c, text="Challenge Negative Thoughts", font=("Arial", 16, "bold"), wraplength=450).pack(pady=15)
        q1 = ctk.CTkEntry(c, placeholder_text="The Situation..."); q1.pack(pady=10, fill="x", padx=20)
        q1.focus_set()
        q2 = ctk.CTkEntry(c, placeholder_text="The Negative Thought..."); q2.pack(pady=10, fill="x", padx=20)
        q3 = ctk.CTkTextbox(c, height=100, wrap="word"); q3.insert("0.0", "Evidence against this thought..."); q3.pack(pady=10, fill="x", padx=20)
        
        def save_cbt():
            conn = sqlite3.connect("therapist_app.db")
            conn.execute("INSERT INTO cbt_records (username, situation, thought, evidence) VALUES (?,?,?,?)", 
                         (self.current_user, encrypt_text(q1.get()), encrypt_text(q2.get()), encrypt_text(q3.get("1.0", "end-1c"))))
            conn.commit(); conn.close()
            messagebox.showinfo("CBT", "Thought recorded and added to progress tracking.")
            c.destroy()

        ctk.CTkButton(c, text="Save Reflection", command=save_cbt).pack(pady=20)
        c.bind('<Return>', lambda e: save_cbt())

    def box_breathing(self):
        bb = ctk.CTkToplevel(self); bb.title("Box Breathing"); bb.geometry("300x450")
        bb.bind('<Escape>', lambda e: bb.destroy())
        inst = ctk.CTkLabel(bb, text="Prepare...", font=("Arial", 20), wraplength=250); inst.pack(pady=20)
        timer = ctk.CTkLabel(bb, text="4", font=("Arial", 30), text_color="#3498db"); timer.pack()
        cv = tk.Canvas(bb, width=200, height=200, bg="#2c3e50", highlightthickness=0); cv.pack(pady=20)
        rect = cv.create_rectangle(80, 80, 120, 120, fill="#3498db")
        def update_t(s):
            if bb.winfo_exists():
                timer.configure(text=str(s))
                if s > 1: bb.after(1000, lambda: update_t(s-1))
        def anim(phase=0):
            if not bb.winfo_exists(): return
            update_t(4)
            if phase == 0:
                inst.configure(text="Inhale...")
                for i in range(40): bb.after(i*100, lambda i=i: cv.coords(rect, 100-(20+i*2), 100-(20+i*2), 100+(20+i*2), 100+(20+i*2)))
                bb.after(4000, lambda: anim(1))
            elif phase == 1: inst.configure(text="Hold..."); bb.after(4000, lambda: anim(2))
            elif phase == 2:
                inst.configure(text="Exhale...")
                for i in range(40): bb.after(i*100, lambda i=i: cv.coords(rect, 20+(i*2), 20+(i*2), 180-(i*2), 180-(i*2)))
                bb.after(4000, lambda: anim(3))
            else: inst.configure(text="Hold..."); bb.after(4000, lambda: anim(0))
        anim()

    def grounding_exercise(self):
        g_win = ctk.CTkToplevel(self); g_win.title("Grounding"); g_win.geometry("400x350")
        g_win.bind('<Escape>', lambda e: g_win.destroy())
        steps = [("SEE", 5), ("TOUCH", 4), ("HEAR", 3), ("SMELL", 2), ("TASTE", 1)]
        self.idx, self.cnt = 0, 0
        lbl = ctk.CTkLabel(g_win, text="", font=("Arial", 14), wraplength=350); lbl.pack(pady=20)
        ent = ctk.CTkEntry(g_win, width=250); ent.pack(pady=10)
        ent.focus_set()
        def proceed():
            if not ent.get(): return
            self.cnt += 1
            if self.cnt < steps[self.idx][1]: update_ui()
            else:
                self.cnt = 0; self.idx += 1
                if self.idx < len(steps): update_ui()
                else: 
                    if self.pet_manager: self.pet_manager.reward("grounding") # INTEGRATION: Reward Pet
                    messagebox.showinfo("Done", "Exercise complete. (+5 Coins)"); g_win.destroy()
        def update_ui():
            lbl.configure(text=f"Name {steps[self.idx][1]} things you can {steps[self.idx][0]}.\n({self.cnt}/{steps[self.idx][1]})")
            ent.delete(0, 'end')
        ctk.CTkButton(g_win, text="Submit", command=proceed).pack(pady=10)
        g_win.bind('<Return>', lambda e: proceed())
        update_ui()

    def create_new_session(self):
        t = simpledialog.askstring("Session", "Title:") or "New Chat"
        sid = str(uuid.uuid4())
        conn = sqlite3.connect("therapist_app.db")
        conn.cursor().execute("INSERT INTO sessions (session_id, username, title) VALUES (?,?,?)", (sid, self.current_user, t))
        conn.commit(); conn.close(); self.load_session(sid)

    def load_session(self, sid):
        self.current_session_id = sid
        self.clear_screen()
        ctk.CTkButton(self, text="⬅ Back", command=self.setup_menu_ui).pack(pady=5, padx=10, anchor="nw")
        self.chat_area = scrolledtext.ScrolledText(self, wrap="word", bg="#1e1e1e", fg="white", font=("Arial", 12))
        self.chat_area.pack(pady=10, padx=20, fill="both", expand=True)
        conn = sqlite3.connect("therapist_app.db")
        history = conn.cursor().execute("SELECT sender, message FROM chat_history WHERE session_id=? ORDER BY timestamp", (sid,)).fetchall()
        for s, m in history:
            self.chat_area.insert("end", f"{s}: {m}\n\n")
        conn.close()
        input_frame = ctk.CTkFrame(self); input_frame.pack(pady=10, padx=20, fill="x")
        self.user_input = ctk.CTkEntry(input_frame, placeholder_text="Type here...", height=40)
        self.user_input.pack(side="left", fill="x", expand=True, padx=5)
        self.user_input.focus_set()
        ctk.CTkButton(input_frame, text="Send", width=80, command=self.send_message).pack(side="right")
        ctk.CTkButton(self, text="🔊 Listen to AI", command=self.speak_last_message).pack(pady=5)
        
        # Shortcut for sending chat
        self.bind('<Return>', lambda event: self.send_message())

    def send_message(self):
        msg = self.user_input.get()
        if not msg: return
        self.chat_area.insert("end", f"You: {msg}\n\n")
        self.user_input.delete(0, 'end')
        if self.safety.is_high_risk(msg): self.trigger_panic()
        def ai_thread():
            conn = sqlite3.connect("therapist_app.db")
            hist = conn.cursor().execute("SELECT sender, message FROM chat_history WHERE session_id=?", (self.current_session_id,)).fetchall()
            resp = TherapistAI(self.current_user).get_response(msg, hist)
            self.last_ai_message = resp
            conn.execute("INSERT INTO chat_history (session_id, sender, message) VALUES (?,?,?)", (self.current_session_id, "You", msg))
            conn.execute("INSERT INTO chat_history (session_id, sender, message) VALUES (?,?,?)", (self.current_session_id, "AI", resp))
            conn.commit(); conn.close()
            # Audit chat exchange (truncate large AI text)
            try:
                log_event(self.current_user, "AI", "chat_exchange", f"User: {msg[:200]} | AI: {resp[:200]}")
            except: pass
            if self.pet_manager: self.pet_manager.reward("therapy") # INTEGRATION: Reward Pet
            self.chat_area.insert("end", f"AI: {resp}\n\n"); self.chat_area.see("end")
        threading.Thread(target=ai_thread).start()

    def delete_session(self, sid):
        if messagebox.askyesno("Delete", "Permanently delete this session?"):
            conn = sqlite3.connect("therapist_app.db")
            conn.cursor().execute("DELETE FROM sessions WHERE session_id=?", (sid,))
            conn.cursor().execute("DELETE FROM chat_history WHERE session_id=?", (sid,))
            conn.commit(); conn.close(); self.setup_menu_ui()
            
    def open_pet_game(self):
        if not self.current_user:
            return
        if self.pet_manager is None:
            self.pet_manager = PetGame(self, self.current_user)
        else:
            self.pet_manager.show_window()
  

if __name__ == "__main__":
    app = App()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        # Graceful shutdown on Ctrl-C from terminal
        try:
            app.destroy()
        except Exception:
            pass
        print("Interrupted, exiting.")
        import sys
        sys.exit(0)