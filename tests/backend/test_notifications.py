"""
Tests for Notification System endpoints.

Covers:
  - GET  /api/notifications
  - POST /api/notifications/<id>/read
  - DELETE /api/notifications/<id>
  - POST /api/notifications/clear-read
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

import api
from tests.conftest import make_mock_db


# ==================== GET NOTIFICATIONS ====================

class TestGetNotifications:
    """Tests for GET /api/notifications"""

    def test_get_notifications_success(self, client, mock_db):
        """Returns notifications for a user."""
        now = datetime.now().isoformat()
        conn, cursor = mock_db([
            (1, 'New appointment scheduled', 'appointment', 0, now),
            (2, 'Mood logged successfully', 'info', 1, now),
        ])

        resp = client.get('/api/notifications?username=test_patient')
        data = resp.get_json()

        assert resp.status_code == 200
        assert len(data['notifications']) == 2
        assert data['notifications'][0]['id'] == 1
        assert data['notifications'][0]['read'] is False
        assert data['notifications'][1]['read'] is True

    def test_get_notifications_no_username(self, client, mock_db):
        """Missing username returns 400."""
        resp = client.get('/api/notifications')
        assert resp.status_code == 400

    def test_get_notifications_empty(self, client, mock_db):
        """No notifications returns empty list."""
        conn, cursor = mock_db([])
        resp = client.get('/api/notifications?username=test_patient')
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['notifications'] == []


# ==================== MARK NOTIFICATION READ ====================

class TestMarkNotificationRead:
    """Tests for POST /api/notifications/<id>/read"""

    def test_mark_read_success(self, client, mock_db):
        """Marking notification as read returns success."""
        conn, cursor = mock_db([])

        resp = client.post('/api/notifications/1/read')
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['success'] is True


# ==================== DELETE NOTIFICATION ====================

class TestDeleteNotification:
    """Tests for DELETE /api/notifications/<id>"""

    def test_delete_notification_success(self, client, mock_db):
        """Deleting a notification returns success."""
        conn, cursor = mock_db([])

        resp = client.delete('/api/notifications/1')
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['success'] is True


# ==================== CLEAR READ NOTIFICATIONS ====================

class TestClearReadNotifications:
    """Tests for POST /api/notifications/clear-read"""

    def test_clear_read_success(self, client, mock_db):
        """Clearing read notifications returns deleted count."""
        conn, cursor = mock_db([])
        # Mock rowcount for deleted rows
        cursor.rowcount = 3

        resp = client.post('/api/notifications/clear-read', json={
            'username': 'test_patient',
        })
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['success'] is True
        assert 'deleted' in data

    def test_clear_read_missing_username(self, client, mock_db):
        """Missing username returns 400."""
        resp = client.post('/api/notifications/clear-read', json={})
        assert resp.status_code == 400
