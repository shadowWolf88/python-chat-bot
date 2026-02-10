"""
Shared pytest fixtures and configuration for Healing Space tests.
Provides Flask test client, mock database, authenticated sessions,
and test data factories for all user roles.

Usage:
    pytest tests/                    # Run all tests
    pytest tests/backend/            # Backend unit tests only
    pytest tests/integration/        # Integration tests only
    pytest tests/e2e/                # End-to-end journey tests
    pytest -x --tb=short             # Stop on first failure
    pytest --cov=api --cov-report=html  # With coverage
"""

import os
import sys
import json
import sqlite3
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime, timezone, timedelta

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Configure environment for testing BEFORE importing api
os.environ['DEBUG'] = '1'
os.environ['TESTING'] = '1'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5432'
os.environ['DB_NAME'] = 'healing_space_test'
os.environ['DB_USER'] = 'healing_space'
os.environ['DB_PASSWORD'] = 'healing_space_dev_pass'
os.environ['PIN_SALT'] = 'test_pin_salt_12345'
os.environ['SECRET_KEY'] = 'test_secret_key_do_not_use_in_production'

try:
    from cryptography.fernet import Fernet
    os.environ.setdefault('ENCRYPTION_KEY', Fernet.generate_key().decode())
except Exception:
    os.environ.setdefault('ENCRYPTION_KEY', 'dGVzdGtleQ==')

os.environ.setdefault('GROQ_API_KEY', 'test_groq_key_not_real')

import api


# ==================== MOCK DATABASE HELPERS ====================

class MockCursor:
    """Mock database cursor that returns configurable results."""

    def __init__(self, results=None):
        self._results = results or []
        self._result_index = 0
        self.lastrowid = 1
        self.rowcount = 1
        self.description = None

    def execute(self, query, params=None):
        self._last_query = query
        self._last_params = params
        return self

    def fetchone(self):
        if self._results and self._result_index < len(self._results):
            result = self._results[self._result_index]
            self._result_index += 1
            return result
        return None

    def fetchall(self):
        results = self._results[self._result_index:]
        self._result_index = len(self._results)
        return results

    def close(self):
        pass


class MockConnection:
    """Mock database connection."""

    def __init__(self, cursor=None):
        self._cursor = cursor or MockCursor()

    def cursor(self):
        return self._cursor

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


def make_mock_db(query_results=None):
    """
    Create a mock get_db_connection that returns predictable results.

    Args:
        query_results: list of tuples to return from fetchone/fetchall,
                       or a dict mapping query substrings to results.
    """
    if isinstance(query_results, dict):
        cursor = MockCursor()
        original_execute = cursor.execute

        def smart_execute(query, params=None):
            original_execute(query, params)
            for key, value in query_results.items():
                if key.lower() in query.lower():
                    cursor._results = value if isinstance(value, list) else [value]
                    cursor._result_index = 0
                    return cursor
            cursor._results = []
            cursor._result_index = 0
            return cursor

        cursor.execute = smart_execute
    else:
        cursor = MockCursor(query_results or [])

    conn = MockConnection(cursor)

    def mock_get_db():
        return conn

    def mock_get_cursor(conn):
        return cursor

    return mock_get_db, mock_get_cursor, conn, cursor


# ==================== FLASK TEST CLIENT ====================

@pytest.fixture
def app():
    """Create Flask application for testing."""
    api.app.config['TESTING'] = True
    api.app.config['SECRET_KEY'] = 'test-secret-key-for-sessions'
    api.app.config['WTF_CSRF_ENABLED'] = False
    return api.app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    with app.test_client() as test_client:
        yield test_client


# ==================== AUTHENTICATED SESSION FIXTURES ====================

@pytest.fixture
def auth_patient(client):
    """Flask test client with authenticated patient session.
    Returns (client, user_info_dict).
    Mocks get_authenticated_username to return 'test_patient'.
    CSRF validation is skipped in TESTING mode (see api.py).
    """
    with client.session_transaction() as sess:
        sess['username'] = 'test_patient'
        sess['role'] = 'user'

    with patch.object(api, 'get_authenticated_username', return_value='test_patient'):
        yield client, {
            'username': 'test_patient',
            'role': 'user',
            'full_name': 'Test Patient',
            'email': 'patient@test.com'
        }


@pytest.fixture
def auth_clinician(client):
    """Flask test client with authenticated clinician session."""
    with client.session_transaction() as sess:
        sess['username'] = 'test_clinician'
        sess['role'] = 'clinician'

    with patch.object(api, 'get_authenticated_username', return_value='test_clinician'):
        yield client, {
            'username': 'test_clinician',
            'role': 'clinician',
            'full_name': 'Dr. Test Clinician',
            'email': 'clinician@test.com'
        }


@pytest.fixture
def auth_developer(client):
    """Flask test client with authenticated developer session."""
    with client.session_transaction() as sess:
        sess['username'] = 'test_developer'
        sess['role'] = 'developer'

    with patch.object(api, 'get_authenticated_username', return_value='test_developer'):
        yield client, {
            'username': 'test_developer',
            'role': 'developer',
            'full_name': 'Dev User',
            'email': 'dev@test.com'
        }


@pytest.fixture
def unauth_client(client):
    """Flask test client with NO authentication (anonymous)."""
    with patch.object(api, 'get_authenticated_username', return_value=None):
        yield client


# ==================== MOCK DB FIXTURE ====================

@pytest.fixture
def mock_db():
    """
    Fixture that patches get_db_connection and get_wrapped_cursor.

    Usage:
        def test_something(auth_patient, mock_db):
            mock_db({'SELECT role': ('clinician',)})
            client, user = auth_patient
            resp = client.get('/api/some-endpoint')
    """
    patches = []

    def setup(query_results=None):
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db(query_results)
        p1 = patch.object(api, 'get_db_connection', side_effect=mock_get_db)
        p2 = patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor)
        patches.append(p1.start())
        patches.append(p2.start())
        return conn, cursor

    yield setup

    for p in patches:
        try:
            patch.stopall()
        except Exception:
            pass


# ==================== TEST USER FIXTURES ====================

@pytest.fixture
def test_patient():
    """Return test patient user info dict."""
    return {
        'username': 'test_patient',
        'role': 'user',
        'full_name': 'Test Patient',
        'email': 'patient@test.com'
    }


@pytest.fixture
def test_clinician():
    """Return test clinician user info dict."""
    return {
        'username': 'test_clinician',
        'role': 'clinician',
        'full_name': 'Dr. Test Clinician',
        'email': 'clinician@test.com'
    }


@pytest.fixture
def test_developer():
    """Return test developer user info dict."""
    return {
        'username': 'test_developer',
        'role': 'developer',
        'full_name': 'Dev User',
        'email': 'dev@test.com'
    }


@pytest.fixture
def authenticated_patient(auth_patient):
    """Alias for auth_patient for backward compatibility."""
    return auth_patient


@pytest.fixture
def authenticated_clinician(auth_clinician):
    """Alias for auth_clinician for backward compatibility."""
    return auth_clinician


@pytest.fixture
def authenticated_developer(auth_developer):
    """Alias for auth_developer for backward compatibility."""
    return auth_developer


# ==================== DATABASE FIXTURES ====================

@pytest.fixture
def tmp_db(tmp_path):
    """Create a temporary SQLite database for testing.
    
    Note: Modern tests should use PostgreSQL via conftest setup,
    but this fixture supports legacy tests that expect SQLite.
    """
    db_file = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_file))
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Create minimal schema for legacy tests
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            pin TEXT,
            created_at TIMESTAMP,
            full_name TEXT,
            dob TEXT,
            conditions TEXT,
            role TEXT,
            clinician_id TEXT,
            is_active INTEGER,
            email TEXT,
            phone TEXT,
            avatar_url TEXT,
            bio TEXT,
            country TEXT,
            city TEXT,
            postcode TEXT,
            emergency_contact TEXT,
            emergency_contact_phone TEXT
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            recipient TEXT,
            subject TEXT,
            content TEXT,
            is_read INTEGER,
            clinician_note TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            deleted_by_sender INTEGER,
            deleted_by_recipient INTEGER,
            marked_at TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clinician_username TEXT,
            patient_username TEXT,
            appointment_date TIMESTAMP,
            appointment_type TEXT,
            notes TEXT,
            patient_response INTEGER,
            patient_response_time TIMESTAMP,
            attended INTEGER,
            created_at TIMESTAMP,
            reminder_sent INTEGER,
            reminder_sent_time TIMESTAMP,
            duration_minutes INTEGER,
            status TEXT,
            video_link TEXT,
            location TEXT,
            outcome TEXT
        );
    """)
    conn.commit()
    
    yield str(db_file)
    
    conn.close()


# ==================== TEST DATA FACTORIES ====================

def make_user_row(username='test_patient', role='user', full_name='Test Patient',
                  email='patient@test.com', clinician_id=None):
    """Create a user row tuple matching SELECT * FROM users."""
    return (username, 'hashed_password', 'hashed_pin', datetime.now(),
            full_name, '1990-01-01', 'anxiety', role, clinician_id, 1,
            email, '07700000000', None, None, 'UK', 'London', 'SW1A 1AA', '', '')


def make_mood_row(mood=7, anxiety=3, sleep=8, username='test_patient'):
    """Create a mood_logs row tuple."""
    return (1, username, mood, anxiety, sleep, '', datetime.now(), None)


def make_message_row(msg_id=1, sender='test_patient', recipient='test_clinician',
                     subject='Test', content='Hello', is_read=0):
    """Create a messages row tuple."""
    return (msg_id, sender, recipient, subject, content, is_read,
            None, datetime.now(), None, 0, 0, datetime.now())


def make_appointment_row(appt_id=1, clinician='test_clinician', patient='test_patient'):
    """Create an appointments row tuple."""
    return (appt_id, clinician, patient, datetime.now() + timedelta(days=1),
            'consultation', '', 0, None, 0, datetime.now(), 0, None, None,
            'scheduled', None, None, None)


def make_community_post_row(post_id=1, username='test_patient', message='Hello community'):
    """Create a community_posts row tuple."""
    return (post_id, username, message, 0, datetime.now(), 'general', 0, None)


def make_notification_row(notif_id=1, recipient='test_patient', message='New notification'):
    """Create a notifications row tuple."""
    return (notif_id, recipient, message, 'info', 0, datetime.now())


def make_chat_session_row(session_id=1, username='test_patient', name='Session 1'):
    """Create a chat_sessions row tuple."""
    return (session_id, username, name, datetime.now(), datetime.now(), 1)


def make_pet_row(username='test_patient', pet_name='Buddy', happiness=80, energy=70):
    """Create a virtual pet row tuple."""
    return (username, pet_name, 'dog', 5, happiness, energy, 90, 50, 100, 0,
            datetime.now(), datetime.now())


# ==================== PYTEST CONFIGURATION ====================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "backend: Backend unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end journey tests")
    config.addinivalue_line("markers", "security: Security-focused tests")
    config.addinivalue_line("markers", "clinical: Clinical safety tests")
    config.addinivalue_line("markers", "slow: Tests that are slow to run")


def pytest_collection_modifyitems(config, items):
    """Auto-mark tests based on their location."""
    for item in items:
        if "/backend/" in str(item.fspath):
            item.add_marker(pytest.mark.backend)
        elif "/integration/" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "/e2e/" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
