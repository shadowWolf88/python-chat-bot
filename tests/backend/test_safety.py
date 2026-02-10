"""
Tests for Safety & Risk Assessment endpoints in the Healing Space Flask app.

Covers:
- C-SSRS assessment (start, submit, history, detail, clinician-response, safety-plan)
- Safety check (real-time message scanning)
- Safety plan (get/save)
- Risk score, history, alerts, dashboard
- Clinical scales (PHQ-9, GAD-7)
"""

import json
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime, timedelta

import api


# ========================= HELPERS =========================

def _mock_db(cursor_results=None):
    """Create a mock DB connection + cursor pair.
    cursor_results: list of tuples for fetchone/fetchall, or None.
    """
    mock_cursor = MagicMock()
    mock_cursor.execute.return_value = mock_cursor
    mock_cursor.fetchone.return_value = cursor_results[0] if cursor_results else None
    mock_cursor.fetchall.return_value = cursor_results if cursor_results else []
    mock_cursor.rowcount = 1
    mock_cursor.description = [('col',)]

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    return mock_conn, mock_cursor


def _patch_db(mock_conn, mock_cursor):
    """Return a dict of patches for get_db_connection and get_wrapped_cursor."""
    return {
        'db': patch.object(api, 'get_db_connection', return_value=mock_conn),
        'cur': patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor),
    }


# ========================= C-SSRS: START =========================

class TestCSSRSStart:
    """POST /api/c-ssrs/start"""

    def test_start_assessment_authenticated(self, auth_patient):
        """Starting a C-SSRS assessment returns questions and assessment_id."""
        client, user = auth_patient
        mock_conn, mock_cursor = _mock_db()

        with _patch_db(mock_conn, mock_cursor)['db'], \
             _patch_db(mock_conn, mock_cursor)['cur'], \
             patch.object(api, 'CSSRSAssessment') as mock_cssrs, \
             patch.object(api, 'log_event'):
            mock_cssrs.QUESTIONS = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6']
            mock_cssrs.ANSWER_OPTIONS = [0, 1, 2, 3, 4, 5]

            resp = client.post('/api/c-ssrs/start',
                               json={'clinician_username': 'dr_test'},
                               content_type='application/json')
            data = resp.get_json()

            assert resp.status_code == 200
            assert 'assessment_id' in data
            assert 'questions' in data

    def test_start_assessment_unauthenticated(self, unauth_client):
        """Starting C-SSRS without auth returns 401."""
        with patch.object(api, 'CSSRSAssessment', True):
            resp = unauth_client.post('/api/c-ssrs/start',
                                      json={},
                                      content_type='application/json')
            assert resp.status_code == 401


# ========================= C-SSRS: SUBMIT =========================

class TestCSSRSSubmit:
    """POST /api/c-ssrs/submit"""

    def test_submit_valid_assessment(self, auth_patient):
        """Submitting valid C-SSRS responses returns risk level and assessment_id."""
        client, user = auth_patient
        mock_conn, mock_cursor = _mock_db([(1,)])

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor), \
             patch.object(api, 'CSSRSAssessment') as mock_cssrs, \
             patch.object(api, 'log_event'), \
             patch.object(api, 'send_email', return_value=None, create=True):

            mock_cssrs.calculate_risk_score.return_value = {
                'total_score': 8,
                'risk_level': 'moderate',
                'risk_category_score': 5,
                'reasoning': 'Moderate ideation present',
                'has_planning': False,
                'has_intent': False,
                'has_behavior': False
            }
            mock_cssrs.get_alert_threshold.return_value = {
                'should_alert': False,
                'requires_safety_plan': False,
                'response_time_minutes': 60
            }
            mock_cssrs.format_for_patient.return_value = {
                'message': 'Thank you for completing this assessment.',
                'next_steps': ['Continue therapy sessions'],
                'emergency_contacts': {'samaritans': '116 123'}
            }

            resp = client.post('/api/c-ssrs/submit', json={
                'q1': 2, 'q2': 1, 'q3': 1, 'q4': 0, 'q5': 0, 'q6': 0
            }, content_type='application/json')
            data = resp.get_json()

            assert resp.status_code == 201
            assert data['risk_level'] == 'moderate'
            assert data['total_score'] == 8
            assert 'assessment_id' in data

    def test_submit_without_auth(self, unauth_client):
        """C-SSRS submit without auth returns 401."""
        with patch.object(api, 'CSSRSAssessment', True):
            resp = unauth_client.post('/api/c-ssrs/submit',
                                      json={'q1': 0, 'q2': 0, 'q3': 0, 'q4': 0, 'q5': 0, 'q6': 0},
                                      content_type='application/json')
            assert resp.status_code == 401

    def test_submit_invalid_score_range(self, auth_patient):
        """C-SSRS response values outside 0-5 return 400."""
        client, user = auth_patient
        with patch.object(api, 'CSSRSAssessment', True):
            resp = client.post('/api/c-ssrs/submit', json={
                'q1': 9, 'q2': 0, 'q3': 0, 'q4': 0, 'q5': 0, 'q6': 0
            }, content_type='application/json')
            assert resp.status_code == 400

    def test_submit_no_data(self, auth_patient):
        """C-SSRS submit with empty body returns 400."""
        client, user = auth_patient
        with patch.object(api, 'CSSRSAssessment', True):
            resp = client.post('/api/c-ssrs/submit',
                               data='',
                               content_type='application/json')
            # Flask parses empty string as None json
            assert resp.status_code == 400


# ========================= C-SSRS: HISTORY =========================

class TestCSSRSHistory:
    """GET /api/c-ssrs/history"""

    def test_get_history_authenticated(self, auth_patient):
        """Patient can retrieve their C-SSRS history."""
        client, user = auth_patient
        mock_conn, mock_cursor = _mock_db([
            (1, 'moderate', 8, 'Moderate ideation', datetime(2026, 1, 15)),
            (2, 'low', 2, 'Minimal risk', datetime(2026, 2, 1)),
        ])

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor):
            resp = client.get('/api/c-ssrs/history')
            data = resp.get_json()

            assert resp.status_code == 200
            assert 'assessments' in data
            assert data['total_count'] == 2

    def test_get_history_unauthenticated(self, unauth_client):
        """History without auth returns 401."""
        resp = unauth_client.get('/api/c-ssrs/history')
        assert resp.status_code == 401


# ========================= C-SSRS: GET SPECIFIC =========================

class TestCSSRSGetSpecific:
    """GET /api/c-ssrs/<id>"""

    def test_get_existing_assessment(self, auth_patient):
        """Get specific assessment by ID returns full detail."""
        client, user = auth_patient
        row = (1, 'test_patient', 'dr_test',
               2, 1, 1, 0, 0, 0,
               8, 'moderate', 'Moderate ideation present',
               False, False, False,
               None, None, datetime(2026, 1, 15))
        mock_conn, mock_cursor = _mock_db([row])

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor):
            resp = client.get('/api/c-ssrs/1')
            data = resp.get_json()

            assert resp.status_code == 200
            assert data['assessment_id'] == 1
            assert data['risk_level'] == 'moderate'
            assert 'responses' in data

    def test_get_nonexistent_assessment(self, auth_patient):
        """Get assessment that does not exist returns 404."""
        client, user = auth_patient
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = None

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor):
            resp = client.get('/api/c-ssrs/99999')
            assert resp.status_code == 404


# ========================= C-SSRS: CLINICIAN RESPONSE =========================

class TestCSSRSClinicianResponse:
    """POST /api/c-ssrs/<id>/clinician-response"""

    def test_clinician_respond(self, auth_clinician):
        """Clinician can respond to a C-SSRS assessment."""
        client, user = auth_clinician
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.rowcount = 1

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor), \
             patch.object(api, 'log_event'):
            resp = client.post('/api/c-ssrs/1/clinician-response', json={
                'action': 'call',
                'notes': 'Called patient, no immediate danger'
            }, content_type='application/json')
            data = resp.get_json()

            assert resp.status_code == 200
            assert data['success'] is True
            assert data['action'] == 'call'

    def test_clinician_respond_not_assigned(self, auth_clinician):
        """Clinician responding to unassigned assessment returns 404."""
        client, user = auth_clinician
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.rowcount = 0

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor), \
             patch.object(api, 'log_event'):
            resp = client.post('/api/c-ssrs/999/clinician-response', json={
                'action': 'documented',
                'notes': 'N/A'
            }, content_type='application/json')
            assert resp.status_code == 404


# ========================= C-SSRS: SAFETY PLAN =========================

class TestCSSRSSafetyPlan:
    """POST /api/c-ssrs/<id>/safety-plan"""

    def test_submit_safety_plan_high_risk(self, auth_patient):
        """Patient can submit a safety plan for a high-risk assessment."""
        client, user = auth_patient
        mock_conn, mock_cursor = _mock_db()
        # First fetchone: assessment exists with high risk; second: no existing safety plan
        mock_cursor.fetchone.side_effect = [
            (1, 'high'),   # assessment row
            None,          # no existing safety plan
            None,          # RETURNING id (insert)
        ]

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor), \
             patch.object(api, 'SafetyPlan', True), \
             patch.object(api, 'log_event'):
            resp = client.post('/api/c-ssrs/1/safety-plan', json={
                'warning_signs': ['Feeling hopeless', 'Withdrawing'],
                'internal_coping': ['Deep breathing', 'Journaling'],
                'distraction_people': ['Friend A', 'Family member'],
                'people_for_help': ['Partner', 'Therapist'],
                'professionals': ['GP: 01onal', 'Crisis team'],
                'means_safety': ['Remove items']
            }, content_type='application/json')

            assert resp.status_code in (200, 201)

    def test_submit_safety_plan_not_found(self, auth_patient):
        """Safety plan for non-existent assessment returns 404."""
        client, user = auth_patient
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = None

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor), \
             patch.object(api, 'SafetyPlan', True), \
             patch.object(api, 'log_event'):
            resp = client.post('/api/c-ssrs/999/safety-plan', json={
                'warning_signs': ['test']
            }, content_type='application/json')
            assert resp.status_code == 404


# ========================= SAFETY CHECK =========================

class TestSafetyCheck:
    """POST /api/safety/check"""

    def test_safety_check_safe_message(self, auth_patient):
        """A safe message returns is_high_risk=False."""
        client, user = auth_patient

        with patch.object(api, 'SafetyMonitor') as MockMonitor, \
             patch.object(api, 'log_event'):
            instance = MockMonitor.return_value
            instance.is_high_risk.return_value = False

            resp = client.post('/api/safety/check', json={
                'text': 'I am feeling a bit down today but managing.',
                'username': 'test_patient'
            }, content_type='application/json')
            data = resp.get_json()

            assert resp.status_code == 200
            assert data['is_high_risk'] is False
            assert data['crisis_resources'] is None

    def test_safety_check_crisis_message(self, auth_patient):
        """A crisis-related message returns is_high_risk=True with crisis resources."""
        client, user = auth_patient

        with patch.object(api, 'SafetyMonitor') as MockMonitor, \
             patch.object(api, 'log_event'):
            instance = MockMonitor.return_value
            instance.is_high_risk.return_value = True

            resp = client.post('/api/safety/check', json={
                'text': 'I want to end it all',
                'username': 'test_patient'
            }, content_type='application/json')
            data = resp.get_json()

            assert resp.status_code == 200
            assert data['is_high_risk'] is True
            assert data['crisis_resources'] is not None
            instance.send_crisis_alert.assert_called_once_with('test_patient')

    def test_safety_check_no_text(self, auth_patient):
        """Safety check without text returns 400."""
        client, user = auth_patient
        resp = client.post('/api/safety/check', json={
            'username': 'test_patient'
        }, content_type='application/json')
        assert resp.status_code == 400


# ========================= SAFETY PLAN (GET/SAVE) =========================

class TestSafetyPlan:
    """GET/POST /api/safety-plan"""

    def test_get_safety_plan_exists(self, auth_patient):
        """Returns safety plan data when one exists."""
        client, user = auth_patient
        plan_row = ('Isolation', 'Deep breathing', 'Friend A: 07700000000', 'GP: 01onal')
        mock_conn, mock_cursor = _mock_db([plan_row])

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor):
            resp = client.get('/api/safety-plan?username=test_patient')
            data = resp.get_json()

            assert resp.status_code == 200
            assert data['triggers'] == 'Isolation'
            assert data['coping_strategies'] == 'Deep breathing'

    def test_get_safety_plan_empty(self, auth_patient):
        """Returns empty fields when no safety plan exists."""
        client, user = auth_patient
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = None

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor):
            resp = client.get('/api/safety-plan?username=test_patient')
            data = resp.get_json()

            assert resp.status_code == 200
            assert data['triggers'] == ''

    def test_get_safety_plan_no_username(self, auth_patient):
        """Safety plan GET without username returns 400."""
        client, user = auth_patient
        resp = client.get('/api/safety-plan')
        assert resp.status_code == 400

    def test_save_safety_plan_new(self, auth_patient):
        """Saving a new safety plan succeeds."""
        client, user = auth_patient
        mock_conn, mock_cursor = _mock_db()
        # first fetchone: no existing plan
        mock_cursor.fetchone.return_value = None

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor), \
             patch.object(api, 'update_ai_memory'):
            resp = client.post('/api/safety-plan', json={
                'username': 'test_patient',
                'triggers': 'Isolation, loneliness',
                'coping_strategies': 'Walk outside, call friend',
                'support_contacts': 'Friend: 07700000000',
                'professional_contacts': 'GP: 01onal'
            }, content_type='application/json')
            data = resp.get_json()

            assert resp.status_code == 201
            assert data['success'] is True

    def test_save_safety_plan_update_existing(self, auth_patient):
        """Updating an existing safety plan succeeds."""
        client, user = auth_patient
        mock_conn, mock_cursor = _mock_db()
        # first fetchone: existing plan found
        mock_cursor.fetchone.return_value = ('test_patient',)

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor), \
             patch.object(api, 'update_ai_memory'):
            resp = client.post('/api/safety-plan', json={
                'username': 'test_patient',
                'triggers': 'Updated triggers',
                'coping_strategies': 'Updated strategies'
            }, content_type='application/json')

            assert resp.status_code == 201

    def test_save_safety_plan_no_username(self, auth_patient):
        """Saving safety plan without username returns 400."""
        client, user = auth_patient
        resp = client.post('/api/safety-plan', json={
            'triggers': 'Something'
        }, content_type='application/json')
        assert resp.status_code == 400


# ========================= RISK SCORE =========================

class TestRiskScore:
    """GET /api/risk/score/<username>"""

    def test_get_own_risk_score(self, auth_patient):
        """Patient can view their own risk score."""
        client, user = auth_patient
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = ('user',)  # role lookup

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor), \
             patch.object(api, 'RiskScoringEngine') as mock_engine, \
             patch.object(api, 'log_event'):
            mock_engine.calculate_risk_score.return_value = {
                'risk_score': 35,
                'risk_level': 'moderate',
                'factors': ['elevated mood scores']
            }

            resp = client.get('/api/risk/score/test_patient')
            data = resp.get_json()

            assert resp.status_code == 200
            assert data['success'] is True
            assert data['risk_score'] == 35

    def test_get_risk_score_unauthorized(self, auth_patient):
        """Patient cannot view another patient's risk score."""
        client, user = auth_patient
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = ('user',)  # role is 'user', not clinician

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor):
            resp = client.get('/api/risk/score/other_patient')
            assert resp.status_code == 403

    def test_get_risk_score_unauthenticated(self, unauth_client):
        """Risk score without auth returns 401."""
        resp = unauth_client.get('/api/risk/score/test_patient')
        assert resp.status_code == 401


# ========================= RISK HISTORY =========================

class TestRiskHistory:
    """GET /api/risk/history/<username>"""

    def test_clinician_gets_risk_history(self, auth_clinician):
        """Clinician can view patient risk history."""
        client, user = auth_clinician
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = ('clinician',)
        mock_cursor.fetchall.return_value = [
            (1, 45, 'moderate', 0.3, 0.1, 0.2, 0.1, 20, 15, 10,
             '["mood decline"]', datetime(2026, 1, 15), 'system'),
        ]

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor):
            resp = client.get('/api/risk/history/test_patient')
            data = resp.get_json()

            assert resp.status_code == 200
            assert data['success'] is True
            assert len(data['history']) == 1
            assert data['total_assessments'] == 1

    def test_patient_cannot_view_risk_history(self, auth_patient):
        """Patient (non-clinician) cannot access risk history endpoint."""
        client, user = auth_patient
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = ('user',)  # role = user

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor):
            resp = client.get('/api/risk/history/test_patient')
            assert resp.status_code == 403


# ========================= RISK ALERTS =========================

class TestRiskAlerts:
    """GET /api/risk/alerts"""

    def test_clinician_gets_alerts(self, auth_clinician):
        """Clinician can retrieve active risk alerts."""
        client, user = auth_clinician
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = ('clinician',)
        mock_cursor.fetchall.return_value = [
            (1, 'patient1', 'test_clinician', 'automated', 'high',
             'Elevated risk detected', 'PHQ-9 score increased', 'system', 0.85,
             65, False, None, None, None, False, None, datetime(2026, 2, 1), 'Patient One'),
        ]

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor):
            resp = client.get('/api/risk/alerts')
            data = resp.get_json()

            assert resp.status_code == 200
            assert data['success'] is True
            assert data['total'] == 1
            assert data['alerts'][0]['severity'] == 'high'

    def test_patient_cannot_get_alerts(self, auth_patient):
        """Patient role cannot access risk alerts."""
        client, user = auth_patient
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = ('user',)

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor):
            resp = client.get('/api/risk/alerts')
            assert resp.status_code == 403


# ========================= CREATE RISK ALERT =========================

class TestCreateRiskAlert:
    """POST /api/risk/alert"""

    def test_clinician_creates_alert(self, auth_clinician):
        """Clinician can create a manual risk alert."""
        client, user = auth_clinician
        mock_conn, mock_cursor = _mock_db()
        # First fetchone: role lookup; second: RETURNING id
        mock_cursor.fetchone.side_effect = [('clinician',), (42,)]

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor), \
             patch.object(api, 'log_event'):
            resp = client.post('/api/risk/alert', json={
                'patient_username': 'test_patient',
                'severity': 'high',
                'title': 'Observed distress in session',
                'details': 'Patient appeared highly agitated'
            }, content_type='application/json')
            data = resp.get_json()

            assert resp.status_code == 201
            assert data['success'] is True
            assert data['alert_id'] == 42

    def test_create_alert_missing_fields(self, auth_clinician):
        """Create alert without required fields returns 400."""
        client, user = auth_clinician
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = ('clinician',)

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor):
            resp = client.post('/api/risk/alert', json={
                'severity': 'high'
                # Missing patient_username and title
            }, content_type='application/json')
            assert resp.status_code == 400

    def test_create_alert_invalid_severity(self, auth_clinician):
        """Create alert with invalid severity returns 400."""
        client, user = auth_clinician
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = ('clinician',)

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor):
            resp = client.post('/api/risk/alert', json={
                'patient_username': 'test_patient',
                'severity': 'extreme',  # invalid
                'title': 'Test'
            }, content_type='application/json')
            assert resp.status_code == 400


# ========================= ACKNOWLEDGE RISK ALERT =========================

class TestAcknowledgeRiskAlert:
    """PATCH /api/risk/alert/<id>/acknowledge"""

    def test_acknowledge_alert(self, auth_clinician):
        """Clinician can acknowledge an unacknowledged alert."""
        client, user = auth_clinician
        mock_conn, mock_cursor = _mock_db()
        # First fetchone: role; second: alert (id, acknowledged=False)
        mock_cursor.fetchone.side_effect = [('clinician',), (1, False)]

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor), \
             patch.object(api, 'log_event'):
            resp = client.patch('/api/risk/alert/1/acknowledge', json={})
            data = resp.get_json()

            assert resp.status_code == 200
            assert data['success'] is True

    def test_acknowledge_already_acknowledged(self, auth_clinician):
        """Acknowledging an already-acknowledged alert returns 400."""
        client, user = auth_clinician
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.side_effect = [('clinician',), (1, True)]

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor):
            resp = client.patch('/api/risk/alert/1/acknowledge', json={})
            assert resp.status_code == 400

    def test_acknowledge_nonexistent_alert(self, auth_clinician):
        """Acknowledging non-existent alert returns 404."""
        client, user = auth_clinician
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.side_effect = [('clinician',), None]

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor):
            resp = client.patch('/api/risk/alert/999/acknowledge', json={})
            assert resp.status_code == 404


# ========================= RESOLVE RISK ALERT =========================

class TestResolveRiskAlert:
    """PATCH /api/risk/alert/<id>/resolve"""

    def test_resolve_alert(self, auth_clinician):
        """Clinician can resolve an alert with action notes."""
        client, user = auth_clinician
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.side_effect = [('clinician',), (1, False)]

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor), \
             patch.object(api, 'log_event'):
            resp = client.patch('/api/risk/alert/1/resolve', json={
                'action_taken': 'Contacted patient and arranged emergency session'
            }, content_type='application/json')
            data = resp.get_json()

            assert resp.status_code == 200
            assert data['success'] is True

    def test_resolve_alert_already_resolved(self, auth_clinician):
        """Resolving an already-resolved alert returns 400."""
        client, user = auth_clinician
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.side_effect = [('clinician',), (1, True)]

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor):
            resp = client.patch('/api/risk/alert/1/resolve', json={
                'action_taken': 'N/A'
            }, content_type='application/json')
            assert resp.status_code == 400

    def test_resolve_alert_missing_action(self, auth_clinician):
        """Resolving without action_taken returns 400."""
        client, user = auth_clinician
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.side_effect = [('clinician',), (1, False)]

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor):
            resp = client.patch('/api/risk/alert/1/resolve', json={
                'action_taken': ''
            }, content_type='application/json')
            assert resp.status_code == 400


# ========================= RISK DASHBOARD =========================

class TestRiskDashboard:
    """GET /api/risk/dashboard"""

    def test_clinician_dashboard(self, auth_clinician):
        """Clinician gets risk dashboard with patient summary."""
        client, user = auth_clinician
        mock_conn, mock_cursor = _mock_db()
        # 1) role lookup → ('clinician',)
        # 2-3) per-patient risk lookups → None (no assessment)
        # 4) unreviewed count → (0,) (fetchone()[0] used)
        mock_cursor.fetchone.side_effect = [('clinician',), None, None, (0,)] + [None] * 6
        mock_cursor.fetchall.side_effect = [
            # patient_approvals query
            [('patient1', 'Patient One'), ('patient2', 'Patient Two')],
            # recent alerts
            [],
        ]

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor):
            resp = client.get('/api/risk/dashboard')
            data = resp.get_json()

            assert resp.status_code == 200
            assert data['success'] is True

    def test_patient_cannot_access_dashboard(self, auth_patient):
        """Patient role cannot access risk dashboard."""
        client, user = auth_patient
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = ('user',)

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor):
            resp = client.get('/api/risk/dashboard')
            assert resp.status_code == 403

    def test_dashboard_unauthenticated(self, unauth_client):
        """Unauthenticated access to dashboard returns 401."""
        resp = unauth_client.get('/api/risk/dashboard')
        assert resp.status_code == 401


# ========================= PHQ-9 =========================

class TestPHQ9:
    """POST /api/clinical/phq9"""

    def test_submit_phq9_valid(self, auth_patient):
        """Valid PHQ-9 submission returns score and severity."""
        client, user = auth_patient
        mock_conn, mock_cursor = _mock_db()
        # 1) last_assessment (None = no prior)
        # 2) clinician lookup
        mock_cursor.fetchone.side_effect = [None, ('dr_clinician',)]

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor), \
             patch.object(api, 'send_notification'), \
             patch.object(api, 'update_ai_memory'), \
             patch.object(api, 'reward_pet'):
            resp = client.post('/api/clinical/phq9', json={
                'username': 'test_patient',
                'scores': [1, 2, 1, 0, 1, 2, 1, 0, 1]  # total = 9
            }, content_type='application/json')
            data = resp.get_json()

            assert resp.status_code == 201
            assert data['score'] == 9
            assert data['severity'] == 'Mild'

    def test_submit_phq9_severe(self, auth_patient):
        """PHQ-9 with high scores returns Severe severity."""
        client, user = auth_patient
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.side_effect = [None, ('dr_clinician',)]

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor), \
             patch.object(api, 'send_notification'), \
             patch.object(api, 'update_ai_memory'), \
             patch.object(api, 'reward_pet'):
            resp = client.post('/api/clinical/phq9', json={
                'username': 'test_patient',
                'scores': [3, 3, 3, 3, 3, 3, 3, 3, 3]  # total = 27
            }, content_type='application/json')
            data = resp.get_json()

            assert resp.status_code == 201
            assert data['severity'] == 'Severe'

    def test_submit_phq9_wrong_count(self, auth_patient):
        """PHQ-9 with wrong number of scores returns 400."""
        client, user = auth_patient
        resp = client.post('/api/clinical/phq9', json={
            'username': 'test_patient',
            'scores': [1, 2, 3]  # only 3, need 9
        }, content_type='application/json')
        assert resp.status_code == 400

    def test_submit_phq9_no_username(self, auth_patient):
        """PHQ-9 without username returns 400."""
        client, user = auth_patient
        resp = client.post('/api/clinical/phq9', json={
            'scores': [0] * 9
        }, content_type='application/json')
        assert resp.status_code == 400

    def test_submit_phq9_too_soon(self, auth_patient):
        """PHQ-9 submitted within 14 days returns 400."""
        client, user = auth_patient
        mock_conn, mock_cursor = _mock_db()
        # Last assessment was 5 days ago
        recent_date = (datetime.now() - timedelta(days=5)).isoformat()
        mock_cursor.fetchone.return_value = (recent_date,)

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor):
            resp = client.post('/api/clinical/phq9', json={
                'username': 'test_patient',
                'scores': [0] * 9
            }, content_type='application/json')
            assert resp.status_code == 400
            assert 'fortnight' in resp.get_json()['error'].lower() or 'wait' in resp.get_json()['error'].lower()


# ========================= GAD-7 =========================

class TestGAD7:
    """POST /api/clinical/gad7"""

    def test_submit_gad7_valid(self, auth_patient):
        """Valid GAD-7 submission returns score and severity."""
        client, user = auth_patient
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.side_effect = [None, ('dr_clinician',)]

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor), \
             patch.object(api, 'send_notification'), \
             patch.object(api, 'update_ai_memory'), \
             patch.object(api, 'reward_pet'):
            resp = client.post('/api/clinical/gad7', json={
                'username': 'test_patient',
                'scores': [2, 1, 2, 1, 2, 1, 2]  # total = 11
            }, content_type='application/json')
            data = resp.get_json()

            assert resp.status_code == 201
            assert data['score'] == 11
            assert data['severity'] == 'Moderate'

    def test_submit_gad7_minimal(self, auth_patient):
        """GAD-7 with minimal scores returns Minimal severity."""
        client, user = auth_patient
        mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.side_effect = [None, None]

        with patch.object(api, 'get_db_connection', return_value=mock_conn), \
             patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor), \
             patch.object(api, 'send_notification'), \
             patch.object(api, 'update_ai_memory'), \
             patch.object(api, 'reward_pet'):
            resp = client.post('/api/clinical/gad7', json={
                'username': 'test_patient',
                'scores': [0, 0, 1, 0, 0, 0, 0]  # total = 1
            }, content_type='application/json')
            data = resp.get_json()

            assert resp.status_code == 201
            assert data['severity'] == 'Minimal'

    def test_submit_gad7_wrong_count(self, auth_patient):
        """GAD-7 with wrong number of scores returns 400."""
        client, user = auth_patient
        resp = client.post('/api/clinical/gad7', json={
            'username': 'test_patient',
            'scores': [1, 2]  # only 2, need 7
        }, content_type='application/json')
        assert resp.status_code == 400

    def test_submit_gad7_no_auth_no_username(self, unauth_client):
        """GAD-7 without auth or username returns 400 (username check first)."""
        resp = unauth_client.post('/api/clinical/gad7', json={
            'scores': [0] * 7
        }, content_type='application/json')
        # The endpoint checks for username in the JSON body, not session auth
        assert resp.status_code == 400
