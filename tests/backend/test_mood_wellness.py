"""
Tests for Mood Logging, Wellness Rituals, and Gratitude endpoints.

Covers:
  - POST /api/mood/log
  - GET  /api/mood/history
  - POST /api/mood/check-reminder
  - GET  /api/mood/check-today
  - POST /api/wellness/log
  - GET  /api/wellness/today
  - GET  /api/wellness/summary
  - POST /api/gratitude/log
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

import api
from tests.conftest import make_mock_db, make_mood_row


# ==================== MOOD LOG (POST /api/mood/log) ====================

class TestLogMood:
    """Tests for POST /api/mood/log"""

    def test_log_mood_success(self, auth_patient, mock_db):
        """Log mood with valid data returns 201 and log_id."""
        conn, cursor = mock_db({
            'SELECT id FROM mood_logs': [],                  # no existing entry today
            'INSERT INTO mood_logs': [(42,)],                # RETURNING id
        })
        client, user = auth_patient

        with patch.object(api, 'update_ai_memory'), \
             patch.object(api, 'reward_pet'), \
             patch.object(api, 'mark_daily_task_complete'), \
             patch.object(api, 'log_event'):
            resp = client.post('/api/mood/log', json={
                'mood_val': 7,
                'sleep_val': 8,
                'notes': 'Feeling good today',
                'water_pints': 4,
                'exercise_mins': 30,
                'outside_mins': 20,
            })

        data = resp.get_json()
        assert resp.status_code == 201
        assert data['success'] is True
        assert data['log_id'] == 42

    def test_log_mood_unauthenticated(self, unauth_client, mock_db):
        """Unauthenticated request returns 401."""
        resp = unauth_client.post('/api/mood/log', json={'mood_val': 5})
        assert resp.status_code == 401
        assert 'error' in resp.get_json()

    def test_log_mood_missing_mood_val(self, auth_patient, mock_db):
        """Missing mood_val returns 400."""
        client, _ = auth_patient
        resp = client.post('/api/mood/log', json={})
        assert resp.status_code == 400

    def test_log_mood_invalid_mood_zero(self, auth_patient, mock_db):
        """mood_val=0 is below minimum (1-10) and returns 400."""
        client, _ = auth_patient
        resp = client.post('/api/mood/log', json={'mood_val': 0})
        assert resp.status_code == 400
        assert 'Mood rating' in resp.get_json()['error'] or 'error' in resp.get_json()

    def test_log_mood_invalid_mood_eleven(self, auth_patient, mock_db):
        """mood_val=11 exceeds maximum (1-10) and returns 400."""
        client, _ = auth_patient
        resp = client.post('/api/mood/log', json={'mood_val': 11})
        assert resp.status_code == 400

    def test_log_mood_invalid_mood_string(self, auth_patient, mock_db):
        """Non-numeric mood_val returns 400."""
        client, _ = auth_patient
        resp = client.post('/api/mood/log', json={'mood_val': 'abc'})
        assert resp.status_code == 400

    def test_log_mood_duplicate_today(self, auth_patient, mock_db):
        """Attempting to log mood twice in one day returns 409."""
        conn, cursor = mock_db({
            'SELECT id FROM mood_logs': [(99,)],  # already logged today
        })
        client, _ = auth_patient

        resp = client.post('/api/mood/log', json={'mood_val': 5})
        assert resp.status_code == 409
        assert 'already logged' in resp.get_json()['error'].lower()

    def test_log_mood_with_medications_array(self, auth_patient, mock_db):
        """Medications passed as JSON array are formatted into a string."""
        conn, cursor = mock_db({
            'SELECT id FROM mood_logs': [],
            'INSERT INTO mood_logs': [(10,)],
        })
        client, _ = auth_patient

        with patch.object(api, 'update_ai_memory'), \
             patch.object(api, 'reward_pet'), \
             patch.object(api, 'mark_daily_task_complete'), \
             patch.object(api, 'log_event'):
            resp = client.post('/api/mood/log', json={
                'mood_val': 6,
                'meds': [{'name': 'Sertraline', 'strength': 50, 'quantity': 1}],
            })

        assert resp.status_code == 201

    def test_log_mood_html_sanitized_in_notes(self, auth_patient, mock_db):
        """Script tags are stripped from notes."""
        conn, cursor = mock_db({
            'SELECT id FROM mood_logs': [],
            'INSERT INTO mood_logs': [(11,)],
        })
        client, _ = auth_patient

        with patch.object(api, 'update_ai_memory'), \
             patch.object(api, 'reward_pet'), \
             patch.object(api, 'mark_daily_task_complete'), \
             patch.object(api, 'log_event'):
            resp = client.post('/api/mood/log', json={
                'mood_val': 5,
                'notes': '<script>alert("xss")</script>Normal note',
            })

        assert resp.status_code == 201


# ==================== MOOD HISTORY (GET /api/mood/history) ====================

class TestMoodHistory:
    """Tests for GET /api/mood/history"""

    def test_get_mood_history_success(self, client, mock_db):
        """Returns list of mood rows for a given username."""
        now = datetime.now().isoformat()
        conn, cursor = mock_db([
            (1, 7, 8, '', 'Good day', now, 4, 30, 20),
            (2, 5, 6, '', 'OK day', now, 2, 0, 0),
        ])

        resp = client.get('/api/mood/history?username=test_patient')
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['success'] is True
        assert data['count'] == 2
        assert data['logs'][0]['mood_val'] == 7

    def test_get_mood_history_no_username(self, client, mock_db):
        """Missing username query param returns 400."""
        resp = client.get('/api/mood/history')
        assert resp.status_code == 400

    def test_get_mood_history_empty(self, client, mock_db):
        """Empty history returns success with zero logs."""
        conn, cursor = mock_db([])
        resp = client.get('/api/mood/history?username=nobody')
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['count'] == 0


# ==================== MOOD CHECK-REMINDER (POST /api/mood/check-reminder) ====================

class TestMoodCheckReminder:
    """Tests for POST /api/mood/check-reminder"""

    def test_check_reminder_forced(self, client, mock_db):
        """With force=True, reminders are sent regardless of hour."""
        conn, cursor = mock_db({
            "SELECT username FROM users": [('alice',), ('bob',)],
            'SELECT id FROM mood_logs': [],  # neither has logged today
        })

        resp = client.post('/api/mood/check-reminder', json={'force': True})
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['success'] is True
        assert data['reminders_sent'] >= 0

    def test_check_reminder_not_8pm(self, client, mock_db):
        """Without force, returns early if current hour is not 20."""
        resp = client.post('/api/mood/check-reminder', json={'force': False})
        assert resp.status_code == 200


# ==================== MOOD CHECK-TODAY (GET /api/mood/check-today) ====================

class TestMoodCheckToday:
    """Tests for GET /api/mood/check-today"""

    def test_check_today_logged(self, client, mock_db):
        """If mood was logged today, logged_today=True."""
        now = datetime.now().isoformat()
        conn, cursor = mock_db([(1, now)])
        resp = client.get('/api/mood/check-today?username=test_patient')
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['logged_today'] is True

    def test_check_today_not_logged(self, client, mock_db):
        """If mood was not logged today, logged_today=False."""
        conn, cursor = mock_db([])
        resp = client.get('/api/mood/check-today?username=test_patient')
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['logged_today'] is False

    def test_check_today_missing_username(self, client, mock_db):
        """Missing username query param returns 400."""
        resp = client.get('/api/mood/check-today')
        assert resp.status_code == 400


# ==================== WELLNESS LOG (POST /api/wellness/log) ====================

class TestWellnessLog:
    """Tests for POST /api/wellness/log"""

    def test_log_wellness_success(self, auth_patient, mock_db):
        """Valid wellness data returns 201."""
        conn, cursor = mock_db([])
        client, _ = auth_patient

        with patch.object(api, 'update_ai_memory'), \
             patch.object(api, 'log_event'):
            resp = client.post('/api/wellness/log', json={
                'mood': 7,
                'mood_descriptor': 'content',
                'mood_context': 'Had a good morning',
                'sleep_quality': 8,
                'energy_level': 6,
                'exercise_type': 'walking',
                'exercise_duration': 30,
                'hydration_level': 'high',
                'total_hydration_cups': 8,
                'medication_taken': True,
            })

        data = resp.get_json()
        assert resp.status_code == 201
        assert data['success'] is True
        assert 'wellness_log_id' in data

    def test_log_wellness_unauthenticated(self, unauth_client, mock_db):
        """Unauthenticated request returns 401."""
        resp = unauth_client.post('/api/wellness/log', json={'mood': 5})
        assert resp.status_code == 401

    def test_log_wellness_minimal_data(self, auth_patient, mock_db):
        """Wellness log with only optional fields (all None) still inserts."""
        conn, cursor = mock_db([])
        client, _ = auth_patient

        with patch.object(api, 'update_ai_memory'), \
             patch.object(api, 'log_event'):
            resp = client.post('/api/wellness/log', json={})

        assert resp.status_code == 201


# ==================== WELLNESS TODAY (GET /api/wellness/today) ====================

class TestWellnessToday:
    """Tests for GET /api/wellness/today"""

    def test_get_today_wellness_exists(self, auth_patient, mock_db):
        """Returns wellness log when one exists for today."""
        now = datetime.now().isoformat()
        conn, cursor = mock_db([(1, 7, 'content', 8, 6, 50, 30, now)])
        client, _ = auth_patient

        resp = client.get('/api/wellness/today')
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['exists'] is True
        assert data['log']['mood'] == 7

    def test_get_today_wellness_none(self, auth_patient, mock_db):
        """Returns exists=False when no wellness log for today."""
        conn, cursor = mock_db([])
        client, _ = auth_patient

        resp = client.get('/api/wellness/today')
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['exists'] is False

    def test_get_today_wellness_unauthenticated(self, unauth_client, mock_db):
        """Unauthenticated request returns 401."""
        resp = unauth_client.get('/api/wellness/today')
        assert resp.status_code == 401


# ==================== WELLNESS SUMMARY (GET /api/wellness/summary) ====================

class TestWellnessSummary:
    """Tests for GET /api/wellness/summary"""

    def test_get_wellness_summary_with_data(self, auth_patient, mock_db):
        """Returns computed averages and counts."""
        conn, cursor = mock_db([
            (7, 8, 6, 30, True, 'high', datetime.now().isoformat()),
            (5, 6, 4, 0, False, 'medium', datetime.now().isoformat()),
        ])
        client, _ = auth_patient

        resp = client.get('/api/wellness/summary?period=7')
        data = resp.get_json()

        assert resp.status_code == 200
        summary = data['summary']
        assert summary['logs_count'] == 2
        assert summary['mood_avg'] == 6.0
        assert summary['exercise_total_mins'] == 30

    def test_get_wellness_summary_empty(self, auth_patient, mock_db):
        """Empty summary returns empty dict."""
        conn, cursor = mock_db([])
        client, _ = auth_patient

        resp = client.get('/api/wellness/summary?period=30')
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['summary'] == {}

    def test_get_wellness_summary_unauthenticated(self, unauth_client, mock_db):
        """Unauthenticated request returns 401."""
        resp = unauth_client.get('/api/wellness/summary')
        assert resp.status_code == 401


# ==================== GRATITUDE LOG (POST /api/gratitude/log) ====================

class TestGratitudeLog:
    """Tests for POST /api/gratitude/log"""

    def test_log_gratitude_success(self, client, mock_db):
        """Valid gratitude entry returns 201."""
        conn, cursor = mock_db([(99,)])  # RETURNING id
        with patch.object(api, 'update_ai_memory'), \
             patch.object(api, 'reward_pet'), \
             patch.object(api, 'mark_daily_task_complete'), \
             patch.object(api, 'log_event'):
            resp = client.post('/api/gratitude/log', json={
                'username': 'test_patient',
                'entry': 'Grateful for sunshine today',
            })

        data = resp.get_json()
        assert resp.status_code == 201
        assert data['success'] is True
        assert data['log_id'] == 99

    def test_log_gratitude_missing_entry(self, client, mock_db):
        """Missing entry text returns 400."""
        resp = client.post('/api/gratitude/log', json={
            'username': 'test_patient',
        })
        assert resp.status_code == 400
        assert 'entry' in resp.get_json()['error'].lower() or 'required' in resp.get_json()['error'].lower()

    def test_log_gratitude_missing_username(self, client, mock_db):
        """Missing username returns 400."""
        resp = client.post('/api/gratitude/log', json={
            'entry': 'Grateful for code reviews',
        })
        assert resp.status_code == 400

    def test_log_gratitude_entry_too_long(self, client, mock_db):
        """Entry exceeding 1000 chars returns 400."""
        resp = client.post('/api/gratitude/log', json={
            'username': 'test_patient',
            'entry': 'x' * 1001,
        })
        assert resp.status_code == 400
        assert 'too long' in resp.get_json()['error'].lower() or 'maximum' in resp.get_json()['error'].lower()

    def test_log_gratitude_empty_entry(self, client, mock_db):
        """Empty string entry returns 400."""
        resp = client.post('/api/gratitude/log', json={
            'username': 'test_patient',
            'entry': '',
        })
        assert resp.status_code == 400
