"""
Shared pytest fixtures and configuration for Healing Space tests.
Provides common test client setup, database fixtures, and test data factories.

Configuration: Uses PostgreSQL by default for API tests. 
Set DB_TYPE=sqlite to use SQLite for legacy desktop tests.
"""

import os
import sys
import sqlite3
import pytest
from datetime import datetime, timezone

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Configure for PostgreSQL testing by default
os.environ.setdefault('DEBUG', '1')
os.environ.setdefault('DB_HOST', 'localhost')
os.environ.setdefault('DB_PORT', '5432')
os.environ.setdefault('DB_NAME', 'healing_space_test')
os.environ.setdefault('DB_NAME_PET', 'healing_space_pet_test')
os.environ.setdefault('DB_NAME_TRAINING', 'healing_space_training_test')
os.environ.setdefault('DB_USER', 'healing_space')
os.environ.setdefault('DB_PASSWORD', 'healing_space_dev_pass')
os.environ.setdefault('PIN_SALT', 'test_pin_salt_12345')
os.environ.setdefault('GROQ_API_KEY', 'test_key')
os.environ.setdefault('SECRET_KEY', 'test_secret_key_do_not_use_in_production')

import api


@pytest.fixture
def tmp_db(tmp_path):
    """Create a temporary database for test isolation."""
    db_path = str(tmp_path / "test_app.db")
    # Set environment variable and API path
    os.environ['DATABASE_URL'] = f"sqlite:///{db_path}"
    api.DB_PATH = db_path
    
    # Initialize database schema
    api.init_db()
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def client(monkeypatch):
    """Create Flask test client with PostgreSQL database."""
    # Enable debug mode for tests and set secret key for sessions
    api.app.config['TESTING'] = True
    api.app.config['SECRET_KEY'] = 'test-secret-key-for-sessions'
    
    with api.app.test_client() as test_client:
        yield test_client


@pytest.fixture
def test_patient(tmp_db):
    """Create a test patient user in the database."""
    conn = sqlite3.connect(tmp_db)
    cur = conn.cursor()
    
    # Use same password hashing as api.py
    from hashlib import pbkdf2_hmac
    hashed = pbkdf2_hmac('sha256', b'testpass', b'salt', 100000).hex()
    
    cur.execute(
        "INSERT INTO users (username, password, role, full_name) "
        "VALUES (?, ?, ?, ?)",
        ('test_patient', hashed, 'user', 'Test Patient')
    )
    conn.commit()
    conn.close()
    
    return {'username': 'test_patient', 'password': 'testpass', 'role': 'user'}


@pytest.fixture
def test_clinician(tmp_db):
    """Create a test clinician user in the database."""
    conn = sqlite3.connect(tmp_db)
    cur = conn.cursor()
    
    from hashlib import pbkdf2_hmac
    hashed = pbkdf2_hmac('sha256', b'testpass', b'salt', 100000).hex()
    
    cur.execute(
        "INSERT INTO users (username, password, role, full_name) "
        "VALUES (?, ?, ?, ?)",
        ('test_clinician', hashed, 'clinician', 'Dr. Test')
    )
    conn.commit()
    conn.close()
    
    return {'username': 'test_clinician', 'password': 'testpass', 'role': 'clinician'}


@pytest.fixture
def test_developer(tmp_db):
    """Create a test developer user in the database."""
    conn = sqlite3.connect(tmp_db)
    cur = conn.cursor()
    
    from hashlib import pbkdf2_hmac
    hashed = pbkdf2_hmac('sha256', b'testpass', b'salt', 100000).hex()
    
    cur.execute(
        "INSERT INTO users (username, password, role, full_name) "
        "VALUES (?, ?, ?, ?)",
        ('test_dev', hashed, 'developer', 'Dev User')
    )
    conn.commit()
    conn.close()
    
    return {'username': 'test_dev', 'password': 'testpass', 'role': 'developer'}


@pytest.fixture
def authenticated_patient(client, test_patient):
    """Create authenticated patient session and return client with session."""
    # In Flask test client, we can set session directly
    with client.session_transaction() as sess:
        sess['username'] = test_patient['username']
        sess['role'] = test_patient['role']
    
    return client, test_patient


@pytest.fixture
def authenticated_clinician(client, test_clinician):
    """Create authenticated clinician session and return client with session."""
    with client.session_transaction() as sess:
        sess['username'] = test_clinician['username']
        sess['role'] = test_clinician['role']
    
    return client, test_clinician


@pytest.fixture
def authenticated_developer(client, test_developer):
    """Create authenticated developer session and return client with session."""
    with client.session_transaction() as sess:
        sess['username'] = test_developer['username']
        sess['role'] = test_developer['role']
    
    return client, test_developer
