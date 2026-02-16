"""
Tests for Wins Board endpoints.

Covers:
  - POST /api/wins/log
  - GET  /api/wins/recent
  - GET  /api/wins/stats
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, date, timedelta

import api
from tests.conftest import make_mock_db


# ==================== LOG WIN (POST /api/wins/log) ====================

class TestLogWin:
    """Tests for POST /api/wins/log"""

    def test_log_win_success(self, auth_patient, mock_db):
        """Valid win log returns 201."""
        conn, cursor = mock_db({
            'INSERT INTO patient_wins': [(1,)],
            'INSERT INTO ai_memory_events': [],
        })
        client, _ = auth_patient

        with patch.object(api, 'update_ai_memory'), \
             patch.object(api, 'mark_daily_task_complete'), \
             patch.object(api, 'log_event'):
            resp = client.post('/api/wins/log', json={
                'win_type': 'self_care',
                'win_text': 'Took a relaxing bath',
            })

        data = resp.get_json()
        assert resp.status_code == 201
        assert data['success'] is True
        assert data['win_id'] == 1

    def test_log_win_unauthenticated(self, unauth_client, mock_db):
        """Unauthenticated request returns 401."""
        resp = unauth_client.post('/api/wins/log', json={
            'win_type': 'self_care',
            'win_text': 'Test win',
        })
        assert resp.status_code == 401

    def test_log_win_invalid_type(self, auth_patient, mock_db):
        """Invalid win_type returns 400."""
        client, _ = auth_patient
        resp = client.post('/api/wins/log', json={
            'win_type': 'invalid_type',
            'win_text': 'Test win',
        })
        assert resp.status_code == 400

    def test_log_win_empty_text(self, auth_patient, mock_db):
        """Empty win_text returns 400."""
        client, _ = auth_patient
        resp = client.post('/api/wins/log', json={
            'win_type': 'self_care',
            'win_text': '',
        })
        assert resp.status_code == 400

    def test_log_win_text_too_long(self, auth_patient, mock_db):
        """win_text over 500 chars returns 400."""
        client, _ = auth_patient
        resp = client.post('/api/wins/log', json={
            'win_type': 'self_care',
            'win_text': 'x' * 501,
        })
        assert resp.status_code == 400

    def test_log_win_all_valid_types(self, auth_patient, mock_db):
        """All valid win types are accepted."""
        valid_types = ['had_a_laugh', 'self_care', 'kept_promise', 'tried_new',
                       'stood_up', 'got_outside', 'helped_someone', 'custom']

        for wt in valid_types:
            conn, cursor = mock_db({
                'INSERT INTO patient_wins': [(1,)],
                'INSERT INTO ai_memory_events': [],
            })
            client, _ = auth_patient

            with patch.object(api, 'update_ai_memory'), \
                 patch.object(api, 'mark_daily_task_complete'), \
                 patch.object(api, 'log_event'):
                resp = client.post('/api/wins/log', json={
                    'win_type': wt,
                    'win_text': f'Test {wt}',
                })

            assert resp.status_code == 201, f"Failed for win_type: {wt}"


# ==================== RECENT WINS (GET /api/wins/recent) ====================

class TestRecentWins:
    """Tests for GET /api/wins/recent"""

    def test_get_recent_wins_success(self, auth_patient, mock_db):
        """Returns recent wins for authenticated user."""
        now = datetime.now().isoformat()
        conn, cursor = mock_db({
            'SELECT id, win_type, win_text, created_at FROM patient_wins': [
                (1, 'self_care', 'Took a walk', now),
                (2, 'had_a_laugh', 'Funny movie', now),
            ],
            'SELECT COUNT': [(10,), (3,)],  # total_count, this_week_count
        })
        client, _ = auth_patient

        resp = client.get('/api/wins/recent')
        data = resp.get_json()

        assert resp.status_code == 200
        assert len(data['wins']) == 2
        assert data['total_count'] == 10

    def test_get_recent_wins_unauthenticated(self, unauth_client, mock_db):
        """Unauthenticated request returns 401."""
        resp = unauth_client.get('/api/wins/recent')
        assert resp.status_code == 401

    def test_get_recent_wins_with_limit(self, auth_patient, mock_db):
        """Custom limit parameter is respected."""
        conn, cursor = mock_db({
            'SELECT id, win_type, win_text': [],
            'SELECT COUNT': [(0,), (0,)],
        })
        client, _ = auth_patient

        resp = client.get('/api/wins/recent?limit=5')
        assert resp.status_code == 200


# ==================== WINS STATS (GET /api/wins/stats) ====================

class TestWinsStats:
    """Tests for GET /api/wins/stats"""

    def test_get_stats_own(self, auth_patient, mock_db):
        """User can get their own win stats."""
        conn, cursor = mock_db({
            'SELECT COUNT': [(15,), (5,), (3,)],
            'SELECT win_type, COUNT': [('self_care', 8), ('had_a_laugh', 5)],
            'SELECT DISTINCT DATE': [(date.today(),), (date.today() - timedelta(days=1),)],
        })
        client, _ = auth_patient

        resp = client.get('/api/wins/stats')
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['total_wins'] == 15
        assert data['trend'] in ('improving', 'declining', 'stable')

    def test_get_stats_unauthenticated(self, unauth_client, mock_db):
        """Unauthenticated request returns 401."""
        resp = unauth_client.get('/api/wins/stats')
        assert resp.status_code == 401

    def test_get_stats_clinician_views_patient(self, auth_clinician, mock_db):
        """Clinician can view approved patient stats."""
        conn, cursor = mock_db({
            'SELECT role FROM users': [('clinician',)],
            'SELECT status FROM patient_approvals': [('approved',)],
            'SELECT COUNT': [(10,), (4,), (2,)],
            'SELECT win_type, COUNT': [('self_care', 6)],
            'SELECT DISTINCT DATE': [(date.today(),)],
        })
        client, _ = auth_clinician

        resp = client.get('/api/wins/stats?username=test_patient')
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['total_wins'] == 10

    def test_get_stats_unauthorized_for_other_user(self, auth_patient, mock_db):
        """Non-clinician cannot view another user's stats."""
        conn, cursor = mock_db({
            'SELECT role FROM users': [('user',)],  # not clinician
        })
        client, _ = auth_patient

        resp = client.get('/api/wins/stats?username=other_patient')
        assert resp.status_code == 403
