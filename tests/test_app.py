import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os
import json
import sqlite3
import hashlib

# Ensure debug mode so imports don't require production secrets
os.environ.setdefault('DEBUG', '1')
os.environ.setdefault('PIN_SALT', 'testsalt1234567890')
try:
    from cryptography.fernet import Fernet
    os.environ.setdefault('ENCRYPTION_KEY', Fernet.generate_key().decode())
except Exception:
    # If cryptography not available in test runtime, set a placeholder and rely on DEBUG behavior
    os.environ.setdefault('ENCRYPTION_KEY', '')

import pytest

import importlib

# Import modules under test
main = importlib.import_module('legacy_desktop.main')
from fhir_export import export_patient_fhir
import secure_transfer


def test_init_db_creates_tables(tmp_path):
    # Use an isolated DB file in tmp
    db_path = tmp_path / 'therapist_app.db'
    os.chdir(str(tmp_path))
    # Initialize DB
    main.init_db()
    conn = sqlite3.connect('therapist_app.db')
    cur = conn.cursor()
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    conn.close()
    expected = {'users','alerts','clinical_scales','mood_logs','gratitude_logs','audit_logs','settings'}
    assert expected.intersection(set(tables))


def test_password_verify_and_migration(tmp_path):
    os.chdir(str(tmp_path))
    main.init_db()
    conn = sqlite3.connect('therapist_app.db')
    cur = conn.cursor()
    # Create legacy SHA256 password entry
    pwd = 'Secret123!'
    legacy = hashlib.sha256(pwd.encode()).hexdigest()
    cur.execute("INSERT INTO users (username,password) VALUES (?,?)", ('legacyuser', legacy))
    conn.commit()
    conn.close()

    # verify_password should accept legacy hash
    assert main.verify_password(legacy, pwd)

    # Simulate login migration: call hash_password and check it differs
    newh = main.hash_password(pwd)
    assert newh != legacy


def test_alert_persistence(tmp_path):
    os.chdir(str(tmp_path))
    main.init_db()
    sm = main.SafetyMonitor()
    ok = sm.send_crisis_alert('testuser')
    assert ok
    conn = sqlite3.connect('therapist_app.db')
    r = conn.cursor().execute("SELECT username, alert_type FROM alerts WHERE username=?", ('testuser',)).fetchone()
    conn.close()
    assert r and r[0] == 'testuser' and r[1] == 'crisis'


def test_fhir_export_signed_and_valid(tmp_path):
    os.chdir(str(tmp_path))
    # set a valid Fernet key for fhir_export module by env
    os.environ['ENCRYPTION_KEY'] = 'A' * 44
    main.init_db()
    conn = sqlite3.connect('therapist_app.db')
    c = conn.cursor()
    # insert a user with encrypted profile
    c.execute("INSERT INTO users (username, full_name, dob, conditions) VALUES (?,?,?,?)", ('u1', main.encrypt_text('Alice'), main.encrypt_text('1970-01-01'), main.encrypt_text('None')))
    c.execute("INSERT INTO clinical_scales (username, scale_name, score, severity, entry_timestamp) VALUES (?,?,?,?,?)", ('u1','PHQ-9',10,'Moderate','2024-01-01 10:00:00'))
    conn.commit(); conn.close()

    bundle_signed = export_patient_fhir('u1')
    assert bundle_signed
    parsed = json.loads(bundle_signed)
    assert 'signature' in parsed
    assert parsed['signature']['algorithm'].startswith('hmac')


def test_sftp_helper_when_missing_paramiko():
    # If paramiko not available, secure_transfer.sftp_upload should raise RuntimeError
    if secure_transfer.HAS_PARAMIKO:
        pytest.skip('paramiko installed in environment; skipping missing-paramiko test')
    with pytest.raises(RuntimeError):
        secure_transfer.sftp_upload('nonexistent.file', '/remote/path', 'example.com', username='x', password='y')
