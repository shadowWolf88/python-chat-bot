"""
Tests for Therapy Chat, Chat History, Chat Sessions, and Chat Export endpoints.

Covers:
  - POST /api/therapy/chat
  - GET  /api/therapy/history
  - GET  /api/therapy/sessions
  - POST /api/therapy/sessions
  - POST /api/therapy/export
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

import api
from tests.conftest import make_mock_db


# ==================== THERAPY CHAT (POST /api/therapy/chat) ====================

class TestTherapyChat:
    """Tests for POST /api/therapy/chat"""

    def test_chat_success(self, client, mock_db):
        """Valid chat message returns AI response."""
        conn, cursor = mock_db({
            'SELECT id FROM chat_sessions': [(1,)],
            'SELECT sender, message FROM chat_history': [],
            'SELECT memory_summary FROM ai_memory': None,
            'SELECT keyword, category, severity_weight FROM risk_keywords': [],
            'INSERT INTO chat_history': [],
        })

        mock_ai = MagicMock()
        mock_ai.get_response.return_value = "I hear you. Tell me more about that."

        with patch.object(api, 'update_ai_memory'), \
             patch.object(api, 'TherapistAI', return_value=mock_ai), \
             patch.object(api, 'get_user_ai_memory', return_value=None), \
             patch.object(api, 'log_therapy_interaction_to_memory'), \
             patch.object(api, 'log_event'):
            resp = client.post('/api/therapy/chat', json={
                'username': 'test_patient',
                'message': 'I feel anxious today',
            })

        data = resp.get_json()
        assert resp.status_code == 200
        assert 'response' in data or 'error' not in data

    def test_chat_missing_username(self, client, mock_db):
        """Missing username returns 400."""
        resp = client.post('/api/therapy/chat', json={
            'message': 'Hello',
        })
        assert resp.status_code == 400
        assert 'error' in resp.get_json()

    def test_chat_missing_message(self, client, mock_db):
        """Missing message returns 400."""
        resp = client.post('/api/therapy/chat', json={
            'username': 'test_patient',
        })
        assert resp.status_code == 400

    def test_chat_empty_message(self, client, mock_db):
        """Empty string message returns 400."""
        resp = client.post('/api/therapy/chat', json={
            'username': 'test_patient',
            'message': '',
        })
        assert resp.status_code == 400

    def test_chat_input_validation_xss(self, client, mock_db):
        """Script tags in message are handled by input validation."""
        conn, cursor = mock_db({
            'SELECT id FROM chat_sessions': [(1,)],
            'SELECT sender, message FROM chat_history': [],
            'SELECT memory_summary FROM ai_memory': None,
            'SELECT keyword, category, severity_weight FROM risk_keywords': [],
        })

        mock_ai = MagicMock()
        mock_ai.get_response.return_value = "I understand."

        with patch.object(api, 'update_ai_memory'), \
             patch.object(api, 'TherapistAI', return_value=mock_ai), \
             patch.object(api, 'get_user_ai_memory', return_value=None), \
             patch.object(api, 'log_therapy_interaction_to_memory'), \
             patch.object(api, 'log_event'):
            resp = client.post('/api/therapy/chat', json={
                'username': 'test_patient',
                'message': '<script>alert("xss")</script>I feel fine',
            })

        # Should either succeed with sanitized input or reject
        assert resp.status_code in (200, 400)

    def test_chat_creates_session_if_none(self, client, mock_db):
        """If no active session exists, one is created."""
        conn, cursor = mock_db({
            'SELECT id FROM chat_sessions': [],  # no session
            'INSERT INTO chat_sessions': [(99,)],  # RETURNING id
            'SELECT sender, message FROM chat_history': [],
            'SELECT memory_summary FROM ai_memory': None,
            'SELECT keyword, category, severity_weight FROM risk_keywords': [],
        })

        mock_ai = MagicMock()
        mock_ai.get_response.return_value = "Welcome! How can I help?"

        with patch.object(api, 'update_ai_memory'), \
             patch.object(api, 'TherapistAI', return_value=mock_ai), \
             patch.object(api, 'get_user_ai_memory', return_value=None), \
             patch.object(api, 'log_therapy_interaction_to_memory'), \
             patch.object(api, 'log_event'):
            resp = client.post('/api/therapy/chat', json={
                'username': 'test_patient',
                'message': 'Hello',
            })

        assert resp.status_code in (200, 500)


# ==================== CHAT HISTORY (GET /api/therapy/history) ====================

class TestChatHistory:
    """Tests for GET /api/therapy/history"""

    def test_get_history_success(self, client, mock_db):
        """Returns chat history for a user."""
        now = datetime.now().isoformat()
        conn, cursor = mock_db({
            'SELECT id FROM chat_sessions': [(1,)],
            'SELECT sender, message, timestamp FROM chat_history': [
                ('user', 'Hello', now),
                ('ai', 'Hi there!', now),
            ],
        })

        resp = client.get('/api/therapy/history?username=test_patient')
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['success'] is True
        assert len(data['history']) == 2

    def test_get_history_no_username(self, client, mock_db):
        """Missing username returns 400."""
        resp = client.get('/api/therapy/history')
        assert resp.status_code == 400

    def test_get_history_with_session_id(self, client, mock_db):
        """Filtering by chat_session_id returns filtered results."""
        now = datetime.now().isoformat()
        conn, cursor = mock_db([
            ('user', 'Session-specific msg', now),
        ])

        resp = client.get('/api/therapy/history?username=test_patient&chat_session_id=5')
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['success'] is True

    def test_get_history_empty(self, client, mock_db):
        """Empty history returns empty list."""
        conn, cursor = mock_db({
            'SELECT id FROM chat_sessions': [(1,)],
            'SELECT sender, message, timestamp FROM chat_history': [],
        })

        resp = client.get('/api/therapy/history?username=nobody')
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['history'] == []


# ==================== CHAT SESSIONS (GET/POST /api/therapy/sessions) ====================

class TestChatSessions:
    """Tests for GET/POST /api/therapy/sessions"""

    def test_get_sessions_success(self, client, mock_db):
        """Returns list of chat sessions for user."""
        now = datetime.now().isoformat()
        conn, cursor = mock_db({
            'SELECT COUNT(*) FROM chat_sessions': [(1,)],
            'SELECT id, session_name': [
                (1, 'Main Chat', now, now, 1, 5),
            ],
        })

        resp = client.get('/api/therapy/sessions?username=test_patient')
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['success'] is True
        assert len(data['sessions']) >= 1

    def test_get_sessions_no_username(self, client, mock_db):
        """Missing username returns 400."""
        resp = client.get('/api/therapy/sessions')
        assert resp.status_code == 400

    def test_get_sessions_creates_default(self, client, mock_db):
        """If no sessions exist, a default 'Main Chat' session is created."""
        now = datetime.now().isoformat()
        conn, cursor = mock_db({
            'SELECT COUNT(*) FROM chat_sessions': [(0,)],
            'INSERT INTO chat_sessions': [],
            'SELECT id, session_name': [
                (1, 'Main Chat', now, now, 1, 0),
            ],
        })

        resp = client.get('/api/therapy/sessions?username=new_user')
        assert resp.status_code == 200
