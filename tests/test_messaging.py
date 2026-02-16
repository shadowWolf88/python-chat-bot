"""
Tests for Phase 3: Internal Messaging System endpoints
Comprehensive tests for all messaging functionality.
Uses mock_db fixture (no SQLite) since the API uses PostgreSQL.
"""
import pytest
import json
from datetime import datetime


class TestMessagingSend:
    """Tests for POST /api/messages/send endpoint"""

    def test_send_message_to_other_user(self, auth_patient, mock_db):
        """Test user can send message to another user"""
        client, patient = auth_patient

        # Mock: recipient exists as 'user' role, sender exists as 'user' role
        mock_db({
            'SELECT username, role FROM users': ('other_patient', 'user'),
            'SELECT role FROM users': ('user',),
            'INSERT INTO messages': (1,),
        })

        response = client.post('/api/messages/send',
            json={
                'recipient': 'other_patient',
                'subject': 'Check-in',
                'content': 'I am feeling better today'
            })

        assert response.status_code == 201
        data = response.get_json()
        assert 'message_id' in data
        assert data['status'] == 'sent'
        assert data['recipient'] == 'other_patient'

    def test_send_message_missing_content(self, auth_patient):
        """Test that empty content is rejected"""
        client, patient = auth_patient

        response = client.post('/api/messages/send',
            json={
                'recipient': 'someone',
                'content': ''
            })

        assert response.status_code == 400
        data = response.get_json()
        assert 'content' in data['error'].lower()

    def test_send_message_to_self(self, auth_patient):
        """Test that users cannot message themselves"""
        client, patient = auth_patient

        response = client.post('/api/messages/send',
            json={
                'recipient': patient['username'],
                'content': 'Hello myself'
            })

        assert response.status_code == 400
        assert 'yourself' in response.get_json()['error'].lower()

    def test_send_message_content_too_long(self, auth_patient):
        """Test that content over 5000 chars is rejected"""
        client, patient = auth_patient

        response = client.post('/api/messages/send',
            json={
                'recipient': 'someone',
                'content': 'x' * 5001
            })

        assert response.status_code == 400
        assert '5000' in response.get_json()['error']

    def test_send_message_no_recipient(self, auth_patient):
        """Test that missing recipient is rejected"""
        client, patient = auth_patient

        response = client.post('/api/messages/send',
            json={
                'content': 'Hello'
            })

        assert response.status_code == 400
        assert 'recipient' in response.get_json()['error'].lower()


class TestMessagingInbox:
    """Tests for GET /api/messages/inbox endpoint"""

    def test_get_empty_inbox(self, auth_patient, mock_db):
        """Test that new user has empty inbox"""
        client, patient = auth_patient

        mock_db({
            'SELECT DISTINCT': [],
            'SELECT COUNT': [(0,)],
        })

        response = client.get('/api/messages/inbox')

        assert response.status_code == 200
        data = response.get_json()
        assert data['conversations'] == []
        assert data['total_unread'] == 0
        assert data['total_conversations'] == 0

    def test_inbox_pagination(self, auth_patient, mock_db):
        """Test inbox pagination works"""
        client, patient = auth_patient

        mock_db({
            'SELECT DISTINCT': [],
            'SELECT COUNT': [(0,)],
        })

        response = client.get('/api/messages/inbox?page=2&limit=10')

        assert response.status_code == 200
        data = response.get_json()
        assert data['page'] == 2
        assert data['page_size'] == 10


class TestMessagingConversation:
    """Tests for GET /api/messages/conversation/<username> endpoint"""

    def test_get_empty_conversation(self, auth_patient, mock_db):
        """Test getting conversation with no messages"""
        client, patient = auth_patient

        mock_db({
            'SELECT': [],
            'UPDATE': None,
        })

        response = client.get('/api/messages/conversation/test_clinician')

        assert response.status_code == 200
        data = response.get_json()
        assert data['messages'] == []


class TestMarkAsRead:
    """Tests for PATCH /api/messages/<id>/read endpoint"""

    def test_mark_nonexistent_as_read(self, auth_patient, mock_db):
        """Test marking nonexistent message as read"""
        client, patient = auth_patient

        mock_db({
            'SELECT': None,
        })

        response = client.patch('/api/messages/99999/read')

        assert response.status_code == 404


class TestDeleteMessage:
    """Tests for DELETE /api/messages/<id> endpoint"""

    def test_delete_nonexistent_message(self, auth_patient, mock_db):
        """Test deleting nonexistent message"""
        client, patient = auth_patient

        mock_db({
            'SELECT': None,
        })

        response = client.delete('/api/messages/99999')

        assert response.status_code == 404


class TestMessagesSentEndpoint:
    """Tests for GET /api/messages/sent endpoint"""

    def test_get_sent_messages(self, auth_patient, mock_db):
        """Test retrieving all messages sent by user"""
        client, patient = auth_patient

        mock_db({
            'SELECT': [
                (1, patient['username'], 'recipient_user', 'Test Subject',
                 'Test message content', datetime.now().isoformat(), 0, None),
            ],
        })

        response = client.get('/api/messages/sent')
        assert response.status_code == 200


class TestFeedbackAllEndpoint:
    """Tests for GET /api/feedback/all endpoint"""

    def test_patient_cannot_view_all_feedback(self, auth_patient, mock_db):
        """Test that patients cannot view all feedback (forbidden)"""
        client, patient = auth_patient

        mock_db({
            'SELECT role': ('user',),
        })

        response = client.get('/api/feedback/all')
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
