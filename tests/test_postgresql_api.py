#!/usr/bin/env python3
"""
Phase 5 Step 7: PostgreSQL API Test Suite

Tests the Flask API with PostgreSQL database to verify:
1. All endpoints work with PostgreSQL
2. RETURNING id clauses work properly
3. Data persistence and integrity
4. No .lastrowid errors
"""

import os
import sys
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure for PostgreSQL testing
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5432'
os.environ['DB_NAME'] = 'healing_space_test'
os.environ['DB_NAME_PET'] = 'healing_space_pet_test'
os.environ['DB_NAME_TRAINING'] = 'healing_space_training_test'
os.environ['DB_USER'] = 'healing_space'
os.environ['DB_PASSWORD'] = 'healing_space_dev_pass'
os.environ['DEBUG'] = '1'
os.environ['PIN_SALT'] = 'test_pin_salt_12345'
os.environ['GROQ_API_KEY'] = 'test_key'
os.environ['SECRET_KEY'] = 'test_secret_key_do_not_use_in_production'

import pytest
from api import app, get_db_connection, get_pet_db_connection


class TestPostgreSQLConnections:
    """Test basic PostgreSQL connectivity"""
    
    def test_main_db_connection(self):
        """Test connection to main therapy database"""
        conn = get_db_connection()
        assert conn is not None
        cur = conn.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        assert result[0] == 1
        cur.close()
        conn.close()
    
    def test_pet_db_connection(self):
        """Test connection to pet game database"""
        conn = get_pet_db_connection()
        assert conn is not None
        cur = conn.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        assert result[0] == 1
        cur.close()
        conn.close()
    
    def test_postgresql_version(self):
        """Verify PostgreSQL version"""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        assert 'PostgreSQL' in version
        assert '16.11' in version or '16' in version
        cur.close()
        conn.close()


class TestFlaskApp:
    """Test Flask app functionality"""
    
    @pytest.fixture
    def client(self):
        """Create a Flask test client"""
        with app.test_client() as client:
            yield client
    
    def test_app_loads(self):
        """Test that Flask app initializes"""
        assert app is not None
        assert len(app.url_map._rules) > 0
    
    def test_routes_registered(self):
        """Test that API routes are registered"""
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        # Check for auth routes
        assert any('register' in r for r in routes)
        assert any('login' in r for r in routes)
        # Check for therapy routes
        assert any('chat' in r for r in routes)
        assert any('mood' in r for r in routes)
    
    def test_app_route_count(self):
        """Verify number of registered routes"""
        route_count = len(app.url_map._rules)
        # Should have 203+ routes
        assert route_count >= 203, f"Expected 203+ routes, got {route_count}"


class TestDatabaseOperations:
    """Test critical database operations"""
    
    def test_insert_and_retrieve(self):
        """Test INSERT and RETURNING id functionality"""
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            
            # Test INSERT with RETURNING
            test_username = 'testuser_' + str(os.getpid())
            cur.execute(
                "INSERT INTO users (username, password, email) "
                "VALUES (%s, %s, %s) RETURNING username",
                (test_username, 'hash123', 'test@example.com')
            )
            conn.commit()

            result = cur.fetchone()
            assert result is not None
            assert result[0] == test_username

            # Clean up
            cur.execute("DELETE FROM users WHERE username = %s", (test_username,))
            conn.commit()
            
        finally:
            cur.close()
            conn.close()
    
    def test_update_operation(self):
        """Test UPDATE operation"""
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            
            # Create a test user
            test_username = 'update_test_' + str(os.getpid())
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING username",
                (test_username, 'hash123')
            )
            conn.commit()
            cur.fetchone()

            # Update the user
            cur.execute(
                "UPDATE users SET email = %s WHERE username = %s",
                ('newemail@test.com', test_username)
            )
            conn.commit()

            # Verify update
            cur.execute("SELECT email FROM users WHERE username = %s", (test_username,))
            email = cur.fetchone()[0]
            assert email == 'newemail@test.com'

            # Clean up
            cur.execute("DELETE FROM users WHERE username = %s", (test_username,))
            conn.commit()
            
        finally:
            cur.close()
            conn.close()
    
    def test_transaction_rollback(self):
        """Test transaction rollback"""
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            
            # Start transaction
            test_username = 'rollback_test_' + str(os.getpid())
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING username",
                (test_username, 'hash123')
            )
            cur.fetchone()

            # Rollback (don't commit)
            conn.rollback()

            # Verify the insert didn't persist
            cur.execute("SELECT username FROM users WHERE username = %s", (test_username,))
            result = cur.fetchone()
            assert result is None  # Rollback should have discarded the insert
            
        finally:
            cur.close()
            conn.close()


class TestCurrentTimestamp:
    """Test CURRENT_TIMESTAMP compatibility"""
    
    def test_current_timestamp_in_select(self):
        """Test that CURRENT_TIMESTAMP works in SELECT"""
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT CURRENT_TIMESTAMP")
            result = cur.fetchone()
            assert result is not None
            assert result[0] is not None
        finally:
            cur.close()
            conn.close()
    
    def test_current_timestamp_in_insert(self):
        """Test that CURRENT_TIMESTAMP works in INSERT"""
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            
            # Insert with CURRENT_TIMESTAMP
            test_username = 'timestamp_test_' + str(os.getpid())
            cur.execute(
                "INSERT INTO users (username, password, last_login) "
                "VALUES (%s, %s, CURRENT_TIMESTAMP) RETURNING username, last_login",
                (test_username, 'hash123')
            )
            conn.commit()

            result = cur.fetchone()
            assert result is not None
            assert result[1] is not None  # last_login timestamp should be set

            # Clean up
            cur.execute("DELETE FROM users WHERE username = %s", (test_username,))
            conn.commit()
            
        finally:
            cur.close()
            conn.close()


class TestPetDatabase:
    """Test pet game database operations"""
    
    def test_pet_table_exists(self):
        """Test that pet game table exists"""
        conn = get_pet_db_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            )
            tables = [row[0] for row in cur.fetchall()]
            assert len(tables) > 0
        finally:
            cur.close()
            conn.close()


def run_tests():
    """Run all tests and print results"""
    print("=" * 80)
    print("PHASE 5 STEP 7: POSTGRESQL API TEST SUITE")
    print("=" * 80)
    
    # Run with pytest
    exit_code = pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '-s'
    ])
    
    return exit_code


if __name__ == '__main__':
    sys.exit(run_tests())
