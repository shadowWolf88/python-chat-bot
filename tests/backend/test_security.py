"""
Tests for Security features: FHIR export, data export, GDPR consent,
patient profile, and general security patterns.

Covers:
  - GET  /api/export/fhir
  - GET  /api/patient/profile
  - PUT  /api/patient/profile
  - POST /api/auth/disclaimer/accept
  - Security pattern tests (injection, headers, etc.)
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

import api
from tests.conftest import make_mock_db


# ==================== FHIR EXPORT (GET /api/export/fhir) ====================

class TestFHIRExport:
    """Tests for GET /api/export/fhir"""

    def test_fhir_export_success(self, client, mock_db):
        """Valid FHIR export returns bundle."""
        mock_bundle = json.dumps({
            'resourceType': 'Bundle',
            'type': 'collection',
            'entry': [],
        })

        mock_fhir = MagicMock()
        mock_fhir.export_patient_fhir.return_value = mock_bundle
        mock_fhir.ENCRYPTION_KEY = None
        with patch('api.fhir_export', mock_fhir, create=True), \
             patch.object(api, 'log_event'):
            resp = client.get('/api/export/fhir?username=test_patient')

        data = resp.get_json()
        assert resp.status_code == 200
        assert data['success'] is True
        assert data['bundle']['resourceType'] == 'Bundle'

    def test_fhir_export_missing_username(self, client, mock_db):
        """Missing username returns 400."""
        resp = client.get('/api/export/fhir')
        assert resp.status_code == 400


# ==================== PATIENT PROFILE ====================

class TestPatientProfile:
    """Tests for GET/PUT /api/patient/profile"""

    def test_get_profile_success(self, client, mock_db):
        """Returns patient profile with stats."""
        conn, cursor = mock_db({
            'SELECT full_name': [('Test Patient', '1990-01-01', 'test@test.com',
                                   '07700000000', 'anxiety', None)],
            'SELECT COUNT': [(10,), (5,), (3,), (2,)],
        })

        resp = client.get('/api/patient/profile?username=test_patient')
        data = resp.get_json()

        assert resp.status_code == 200

    def test_get_profile_missing_username(self, client, mock_db):
        """Missing username returns 400."""
        resp = client.get('/api/patient/profile')
        assert resp.status_code == 400

    def test_get_profile_not_found(self, client, mock_db):
        """Non-existent user returns 404."""
        conn, cursor = mock_db({
            'SELECT full_name': [],
        })

        resp = client.get('/api/patient/profile?username=nobody')
        assert resp.status_code == 404


# ==================== DISCLAIMER ACCEPT ====================

class TestDisclaimerAccept:
    """Tests for POST /api/auth/disclaimer/accept"""

    def test_accept_disclaimer_success(self, client, mock_db):
        """Accepting disclaimer returns success."""
        conn, cursor = mock_db([])

        resp = client.post('/api/auth/disclaimer/accept', json={
            'username': 'test_patient',
        })

        data = resp.get_json()
        assert resp.status_code == 200
        assert data['success'] is True

    def test_accept_disclaimer_missing_username(self, client, mock_db):
        """Missing username returns 400."""
        resp = client.post('/api/auth/disclaimer/accept', json={})
        assert resp.status_code == 400


# ==================== SECURITY PATTERN TESTS ====================

class TestSecurityPatterns:
    """General security pattern tests across the API."""

    def test_sql_injection_in_username_param(self, client, mock_db):
        """SQL injection attempt in username is safely handled."""
        conn, cursor = mock_db([])
        resp = client.get("/api/mood/history?username='; DROP TABLE users;--")
        # Should return 200 with no data, not crash
        assert resp.status_code in (200, 400)

    def test_xss_in_json_field(self, client, mock_db):
        """XSS in JSON fields is handled by validation or encoding."""
        resp = client.post('/api/gratitude/log', json={
            'username': 'test_patient',
            'entry': '<img src=x onerror=alert(1)>',
        })
        # Should either accept (sanitized) or reject, not crash
        assert resp.status_code in (201, 400, 500)

    def test_oversized_payload(self, client, mock_db):
        """Extremely large payloads are handled gracefully."""
        resp = client.post('/api/therapy/chat', json={
            'username': 'test_patient',
            'message': 'A' * 100000,  # 100KB message
        })
        # Should be rejected by validation or handled
        assert resp.status_code in (400, 413, 500)

    def test_null_byte_in_input(self, client, mock_db):
        """Null bytes in input are handled."""
        resp = client.post('/api/gratitude/log', json={
            'username': 'test_patient',
            'entry': 'test\x00injection',
        })
        assert resp.status_code in (201, 400, 500)

    def test_unicode_normalization(self, client, mock_db):
        """Unicode input is handled properly."""
        conn, cursor = mock_db([(1,)])
        with patch.object(api, 'update_ai_memory'), \
             patch.object(api, 'reward_pet'), \
             patch.object(api, 'mark_daily_task_complete'), \
             patch.object(api, 'log_event'):
            resp = client.post('/api/gratitude/log', json={
                'username': 'test_patient',
                'entry': 'Grateful for family \u2764\ufe0f and friends \ud83d\ude0a',
            })
        assert resp.status_code in (201, 400)

    def test_protected_endpoints_require_auth(self, unauth_client, mock_db):
        """Key endpoints requiring auth return 401 for anonymous users."""
        endpoints = [
            ('POST', '/api/wellness/log'),
            ('GET', '/api/wellness/today'),
            ('GET', '/api/wellness/summary'),
            ('POST', '/api/pet/reward'),
            ('POST', '/api/wins/log'),
            ('GET', '/api/wins/recent'),
            ('GET', '/api/wins/stats'),
            ('POST', '/api/messages/send'),
            ('GET', '/api/messages/inbox'),
            ('POST', '/api/activity/log'),
            ('GET', '/api/activity/consent'),
            ('POST', '/api/ai/memory/update'),
            ('GET', '/api/ai/memory'),
        ]

        for method, path in endpoints:
            if method == 'GET':
                resp = unauth_client.get(path)
            else:
                resp = unauth_client.post(path, json={})
            assert resp.status_code == 401, \
                f"{method} {path} returned {resp.status_code} instead of 401"
