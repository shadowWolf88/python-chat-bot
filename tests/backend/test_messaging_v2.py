"""
Tests for Internal Messaging System (Phase 3).

Covers:
  - POST /api/messages/send
  - GET  /api/messages/inbox
  - DELETE /api/messages/<id>
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

import api
from tests.conftest import make_mock_db


# ==================== SEND MESSAGE (POST /api/messages/send) ====================

class TestSendMessage:
    """Tests for POST /api/messages/send"""

    def test_send_message_success(self, auth_clinician, mock_db):
        """Clinician can send message to patient."""
        conn, cursor = mock_db({
            'SELECT username, role FROM users WHERE username': [('test_patient', 'user')],
            'SELECT role FROM users WHERE username': [('clinician',)],
            'INSERT INTO conversations': [(1,)],
            'INSERT INTO conversation_participants': [(1,)],
            'INSERT INTO messages': [(1, datetime.now())],
            'UPDATE conversations': [(1,)],
        })
        client, user = auth_clinician

        with patch.object(api, 'log_event'), \
             patch.object(api, 'send_notification'):
            resp = client.post('/api/messages/send', json={
                'recipient': 'test_patient',
                'subject': 'Check-in',
                'content': 'How are you feeling today?',
            })

        data = resp.get_json()
        assert resp.status_code == 201
        assert data['status'] == 'sent'
        assert data['recipient'] == 'test_patient'

    def test_send_message_unauthenticated(self, unauth_client, mock_db):
        """Unauthenticated request returns 401."""
        resp = unauth_client.post('/api/messages/send', json={
            'recipient': 'someone',
            'content': 'Hello',
        })
        assert resp.status_code == 401

    def test_send_message_missing_recipient(self, auth_patient, mock_db):
        """Missing recipient returns 400."""
        client, _ = auth_patient
        resp = client.post('/api/messages/send', json={
            'content': 'Hello',
        })
        assert resp.status_code == 400

    def test_send_message_missing_content(self, auth_patient, mock_db):
        """Missing content returns 400."""
        client, _ = auth_patient
        resp = client.post('/api/messages/send', json={
            'recipient': 'test_clinician',
        })
        assert resp.status_code == 400

    def test_send_message_content_too_long(self, auth_patient, mock_db):
        """Content exceeding 5000 chars returns 400."""
        client, _ = auth_patient
        resp = client.post('/api/messages/send', json={
            'recipient': 'test_clinician',
            'content': 'x' * 5001,
        })
        assert resp.status_code == 400

    def test_send_message_subject_too_long(self, auth_patient, mock_db):
        """Subject exceeding 100 chars returns 400."""
        client, _ = auth_patient
        resp = client.post('/api/messages/send', json={
            'recipient': 'test_clinician',
            'subject': 'x' * 101,
            'content': 'Valid content',
        })
        assert resp.status_code == 400

    def test_send_message_to_self(self, auth_patient, mock_db):
        """Sending message to yourself returns 400."""
        client, _ = auth_patient
        resp = client.post('/api/messages/send', json={
            'recipient': 'test_patient',
            'content': 'Talking to myself',
        })
        assert resp.status_code == 400

    def test_send_message_recipient_not_found(self, auth_patient, mock_db):
        """Non-existent recipient returns 400 (validation error)."""
        conn, cursor = mock_db({
            'SELECT username, role FROM users': [],  # no user found
        })
        client, _ = auth_patient

        resp = client.post('/api/messages/send', json={
            'recipient': 'nonexistent_user',
            'content': 'Hello',
        })
        assert resp.status_code == 400

    def test_user_can_message_clinician(self, auth_patient, mock_db):
        """Users can send messages to clinicians."""
        conn, cursor = mock_db({
            'SELECT username, role FROM users WHERE username': [('test_clinician', 'clinician')],
            'SELECT role FROM users WHERE username': [('user',)],
            'INSERT INTO conversations': [(1,)],
            'INSERT INTO conversation_participants': [(1,)],
            'INSERT INTO messages': [(1, datetime.now())],
            'UPDATE conversations': [(1,)],
        })
        client, _ = auth_patient

        with patch.object(api, 'log_event'), \
             patch.object(api, 'send_notification'):
            resp = client.post('/api/messages/send', json={
                'recipient': 'test_clinician',
                'content': 'Hi doc',
            })
        assert resp.status_code == 201


# ==================== INBOX (GET /api/messages/inbox) ====================

class TestInbox:
    """Tests for GET /api/messages/inbox"""

    def test_get_inbox_success(self, auth_patient, mock_db):
        """Authenticated user gets inbox."""
        conn, cursor = mock_db({
            'SELECT DISTINCT': [('test_clinician',)],
            'SELECT content, sent_at FROM messages': [('Hi there', datetime.now().isoformat())],
            'SELECT COUNT': [(2,)],
        })
        client, _ = auth_patient

        resp = client.get('/api/messages/inbox')
        data = resp.get_json()

        assert resp.status_code == 200

    def test_get_inbox_unauthenticated(self, unauth_client, mock_db):
        """Unauthenticated request returns 401."""
        resp = unauth_client.get('/api/messages/inbox')
        assert resp.status_code == 401
