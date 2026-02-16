"""
Tests for AI Memory System endpoints.

Covers:
  - POST /api/activity/log
  - GET  /api/activity/consent
  - POST /api/activity/consent
  - POST /api/ai/memory/update
  - GET  /api/ai/memory
  - POST /api/ai/patterns/detect
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

import api
from tests.conftest import make_mock_db


# ==================== ACTIVITY LOG (POST /api/activity/log) ====================

class TestActivityLog:
    """Tests for POST /api/activity/log"""

    def test_log_activity_success(self, auth_patient, mock_db):
        """Valid activity batch returns 200."""
        conn, cursor = mock_db({
            'SELECT activity_tracking_consent FROM users': [(1,)],  # consent given
            'INSERT INTO ai_activity_log': [],
        })
        client, _ = auth_patient

        resp = client.post('/api/activity/log', json={
            'activities': [
                {'activity_type': 'page_view', 'activity_detail': 'home_tab', 'session_id': 'abc'},
                {'activity_type': 'chat_sent', 'activity_detail': 'therapy', 'session_id': 'abc'},
            ],
        })

        data = resp.get_json()
        assert resp.status_code == 200
        assert data['success'] is True
        assert data['activities_logged'] == 2

    def test_log_activity_unauthenticated(self, unauth_client, mock_db):
        """Unauthenticated request returns 401."""
        resp = unauth_client.post('/api/activity/log', json={
            'activities': [{'activity_type': 'test'}],
        })
        assert resp.status_code == 401

    def test_log_activity_no_consent(self, auth_patient, mock_db):
        """Without GDPR consent, returns 403."""
        conn, cursor = mock_db({
            'SELECT activity_tracking_consent FROM users': [(0,)],  # no consent
        })
        client, _ = auth_patient

        resp = client.post('/api/activity/log', json={
            'activities': [{'activity_type': 'test'}],
        })
        assert resp.status_code == 403

    def test_log_activity_empty_list(self, auth_patient, mock_db):
        """Empty activities list returns 400."""
        conn, cursor = mock_db({
            'SELECT activity_tracking_consent FROM users': [(1,)],
        })
        client, _ = auth_patient

        resp = client.post('/api/activity/log', json={
            'activities': [],
        })
        assert resp.status_code == 400

    def test_log_activity_no_data(self, auth_patient, mock_db):
        """No JSON body returns 400."""
        conn, cursor = mock_db({
            'SELECT activity_tracking_consent FROM users': [(1,)],
        })
        client, _ = auth_patient

        resp = client.post('/api/activity/log',
                           data='',
                           content_type='application/json')
        assert resp.status_code in (400, 500)

    def test_log_activity_batch_cap(self, auth_patient, mock_db):
        """Activities capped at 50 per batch."""
        conn, cursor = mock_db({
            'SELECT activity_tracking_consent FROM users': [(1,)],
            'INSERT INTO ai_activity_log': [],
        })
        client, _ = auth_patient

        activities = [{'activity_type': f'type_{i}'} for i in range(60)]
        resp = client.post('/api/activity/log', json={'activities': activities})

        data = resp.get_json()
        assert resp.status_code == 200
        assert data['activities_logged'] <= 50


# ==================== ACTIVITY CONSENT ====================

class TestActivityConsent:
    """Tests for GET/POST /api/activity/consent"""

    def test_get_consent_status(self, auth_patient, mock_db):
        """Returns consent status for authenticated user."""
        conn, cursor = mock_db({
            'SELECT activity_tracking_consent FROM users': [(1,)],
        })
        client, _ = auth_patient

        resp = client.get('/api/activity/consent')
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['consent_given'] is True

    def test_get_consent_unauthenticated(self, unauth_client, mock_db):
        """Unauthenticated returns 401."""
        resp = unauth_client.get('/api/activity/consent')
        assert resp.status_code == 401

    def test_set_consent_grant(self, auth_patient, mock_db):
        """Granting consent returns success."""
        conn, cursor = mock_db({
            'UPDATE users': [],
        })
        client, _ = auth_patient

        with patch.object(api, 'log_event'):
            resp = client.post('/api/activity/consent', json={'consent': True})

        data = resp.get_json()
        assert resp.status_code == 200
        assert data['success'] is True
        assert data['activity_tracking_consent'] is True

    def test_set_consent_revoke(self, auth_patient, mock_db):
        """Revoking consent returns success."""
        conn, cursor = mock_db({
            'UPDATE users': [],
        })
        client, _ = auth_patient

        with patch.object(api, 'log_event'):
            resp = client.post('/api/activity/consent', json={'consent': False})

        data = resp.get_json()
        assert resp.status_code == 200
        assert data['activity_tracking_consent'] is False

    def test_set_consent_missing_field(self, auth_patient, mock_db):
        """Missing consent field returns 400."""
        client, _ = auth_patient
        resp = client.post('/api/activity/consent', json={})
        assert resp.status_code == 400

    def test_set_consent_unauthenticated(self, unauth_client, mock_db):
        """Unauthenticated returns 401."""
        resp = unauth_client.post('/api/activity/consent', json={'consent': True})
        assert resp.status_code == 401


# ==================== AI MEMORY UPDATE (POST /api/ai/memory/update) ====================

class TestAIMemoryUpdate:
    """Tests for POST /api/ai/memory/update"""

    def test_update_memory_success(self, auth_patient, mock_db):
        """Valid memory event returns 200."""
        conn, cursor = mock_db({
            'INSERT INTO ai_memory_events': [],
            'SELECT memory_version FROM ai_memory_core': [(3,)],
        })
        client, _ = auth_patient

        with patch.object(api, 'check_event_for_flags', return_value=[]), \
             patch.object(api, 'update_memory_core', return_value=True):
            resp = client.post('/api/ai/memory/update', json={
                'event_type': 'mood_logged',
                'event_data': {'mood': 7},
                'severity': 'normal',
            })

        data = resp.get_json()
        assert resp.status_code == 200
        assert data['success'] is True
        assert data['memory_updated'] is True

    def test_update_memory_unauthenticated(self, unauth_client, mock_db):
        """Unauthenticated returns 401."""
        resp = unauth_client.post('/api/ai/memory/update', json={
            'event_type': 'test',
        })
        assert resp.status_code == 401

    def test_update_memory_missing_event_type(self, auth_patient, mock_db):
        """Missing event_type returns 400."""
        client, _ = auth_patient
        resp = client.post('/api/ai/memory/update', json={
            'event_data': {},
        })
        assert resp.status_code == 400

    def test_update_memory_no_data(self, auth_patient, mock_db):
        """No JSON body returns 400."""
        client, _ = auth_patient
        resp = client.post('/api/ai/memory/update',
                           data='',
                           content_type='application/json')
        assert resp.status_code in (400, 500)


# ==================== GET AI MEMORY (GET /api/ai/memory) ====================

class TestGetAIMemory:
    """Tests for GET /api/ai/memory"""

    def test_get_memory_success(self, auth_patient, mock_db):
        """Returns memory for authenticated user."""
        client, _ = auth_patient

        with patch.object(api, 'fetch_user_memory', return_value={
            'memory_summary': 'Patient is progressing well',
            'flags': [],
            'recent_events': [],
        }):
            resp = client.get('/api/ai/memory')

        data = resp.get_json()
        assert resp.status_code == 200
        assert 'memory_summary' in data

    def test_get_memory_unauthenticated(self, unauth_client, mock_db):
        """Unauthenticated returns 401."""
        resp = unauth_client.get('/api/ai/memory')
        assert resp.status_code == 401


# ==================== PATTERN DETECTION (POST /api/ai/patterns/detect) ====================

class TestPatternDetection:
    """Tests for POST /api/ai/patterns/detect"""

    def test_detect_patterns_success(self, client, mock_db):
        """Pattern detection with active users returns 200."""
        conn, cursor = mock_db({
            'SELECT DISTINCT username FROM ai_activity_log': [('test_patient',)],
            'SELECT COUNT(DISTINCT DATE': [(5,), (4,)],
            'SELECT EXTRACT(HOUR': [(14, 100)],
            'SELECT DISTINCT EXTRACT': [(14,)],
            'SELECT message FROM chat_history': [('I feel ok',), ('Feeling better',), ('Not bad',)],
        })

        with patch.object(api, 'update_or_create_flag'), \
             patch.object(api, 'analyze_message_severity', return_value=2):
            resp = client.post('/api/ai/patterns/detect')

        data = resp.get_json()
        assert resp.status_code == 200
        assert data['success'] is True
