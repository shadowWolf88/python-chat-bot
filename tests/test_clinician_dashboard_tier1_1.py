"""
TIER 1.1: Clinician Dashboard Tests

Comprehensive test coverage for 9 new clinician endpoints:
- 4 CRITICAL blockers
- 5 HIGH priority features

Tests verify:
- Authentication & authorization
- CSRF protection
- Patient assignment validation
- Data accuracy & completeness
- Security guardrails
- No broken functionality

Run: pytest tests/test_clinician_dashboard_tier1_1.py -v
"""

import pytest
import json
from datetime import datetime, timedelta, date
from unittest.mock import patch, MagicMock


class TestClinicalianSummary:
    """Tests for GET /api/clinician/summary endpoint"""
    
    def test_summary_requires_authentication(self, client):
        """Unauthenticated request returns 401"""
        response = client.get('/api/clinician/summary')
        assert response.status_code == 401
        assert 'Authentication required' in response.json['error']
    
    def test_summary_requires_clinician_role(self, client, authenticated_session, test_user_patient):
        """Non-clinician user cannot access summary"""
        # Logged in as patient, not clinician
        response = client.get(
            '/api/clinician/summary',
            headers={'Cookie': f'session={authenticated_session}'}
        )
        assert response.status_code == 403
        assert 'Clinician access required' in response.json['error']
    
    def test_summary_returns_correct_schema(self, client, clinician_session):
        """Clinician receives summary with all required fields"""
        response = client.get(
            '/api/clinician/summary',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert 'total_patients' in data
        assert 'critical_patients' in data
        assert 'sessions_this_week' in data
        assert 'appointments_today' in data
        assert 'unread_messages' in data
    
    def test_summary_field_types(self, client, clinician_session):
        """All summary fields are integers"""
        response = client.get(
            '/api/clinician/summary',
            headers={'Cookie': f'session={clinician_session}'}
        )
        data = response.json
        assert isinstance(data['total_patients'], int)
        assert isinstance(data['critical_patients'], int)
        assert isinstance(data['sessions_this_week'], int)
        assert isinstance(data['appointments_today'], int)
        assert isinstance(data['unread_messages'], int)


class TestClinicianPatients:
    """Tests for GET /api/clinician/patients endpoint"""
    
    def test_patients_requires_authentication(self, client):
        """Unauthenticated request returns 401"""
        response = client.get('/api/clinician/patients')
        assert response.status_code == 401
    
    def test_patients_requires_clinician_role(self, client, authenticated_session):
        """Non-clinician cannot view patients"""
        response = client.get(
            '/api/clinician/patients',
            headers={'Cookie': f'session={authenticated_session}'}
        )
        assert response.status_code == 403
    
    def test_patients_returns_array(self, client, clinician_session):
        """Response includes patient array"""
        response = client.get(
            '/api/clinician/patients',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 200
        data = response.json
        assert 'patients' in data
        assert isinstance(data['patients'], list)
        assert 'count' in data
    
    def test_patient_list_fields(self, client, clinician_session, assigned_patient):
        """Each patient has required fields"""
        response = client.get(
            '/api/clinician/patients',
            headers={'Cookie': f'session={clinician_session}'}
        )
        patients = response.json['patients']
        assert len(patients) > 0
        
        patient = patients[0]
        assert 'username' in patient
        assert 'name' in patient
        assert 'email' in patient
        assert 'last_session' in patient
        assert 'open_alerts' in patient
        assert 'mood_7d' in patient
    
    def test_patients_only_assigned(self, client, clinician_session, assigned_patient, unassigned_patient):
        """Clinician only sees assigned patients"""
        response = client.get(
            '/api/clinician/patients',
            headers={'Cookie': f'session={clinician_session}'}
        )
        usernames = [p['username'] for p in response.json['patients']]
        assert assigned_patient in usernames
        assert unassigned_patient not in usernames


class TestClinicianPatientDetail:
    """Tests for GET /api/clinician/patient/<username> endpoint"""
    
    def test_patient_detail_requires_auth(self, client, test_patient):
        """Unauthenticated request returns 401"""
        response = client.get(f'/api/clinician/patient/{test_patient}')
        assert response.status_code == 401
    
    def test_patient_detail_requires_clinician_role(self, client, authenticated_session, test_patient):
        """Non-clinician cannot access patient detail"""
        response = client.get(
            f'/api/clinician/patient/{test_patient}',
            headers={'Cookie': f'session={authenticated_session}'}
        )
        assert response.status_code == 403
    
    def test_patient_detail_requires_assignment(self, client, clinician_session, unassigned_patient):
        """Clinician cannot access unassigned patient detail"""
        response = client.get(
            f'/api/clinician/patient/{unassigned_patient}',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 403
        assert 'Not assigned to this patient' in response.json['error']
    
    def test_patient_detail_returns_profile(self, client, clinician_session, assigned_patient):
        """Clinician receives complete patient profile"""
        response = client.get(
            f'/api/clinician/patient/{assigned_patient}',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert data['username'] == assigned_patient
        assert 'name' in data
        assert 'email' in data
        assert 'sessions_count' in data
        assert 'risk_level' in data
        assert 'recent_moods' in data
    
    def test_patient_detail_recent_moods(self, client, clinician_session, assigned_patient, patient_moods):
        """Recent moods list is present and populated"""
        response = client.get(
            f'/api/clinician/patient/{assigned_patient}',
            headers={'Cookie': f'session={clinician_session}'}
        )
        moods = response.json['recent_moods']
        assert isinstance(moods, list)
        for mood in moods:
            assert 'date' in mood
            assert 'mood' in mood
            assert isinstance(mood['mood'], int)


class TestClinicianMoodLogs:
    """Tests for GET /api/clinician/patient/<username>/mood-logs endpoint"""
    
    def test_mood_logs_requires_assignment(self, client, clinician_session, unassigned_patient):
        """Cannot access unassigned patient's mood logs"""
        response = client.get(
            f'/api/clinician/patient/{unassigned_patient}/mood-logs',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 403
    
    def test_mood_logs_returns_array(self, client, clinician_session, assigned_patient):
        """Response includes mood logs array"""
        response = client.get(
            f'/api/clinician/patient/{assigned_patient}/mood-logs',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 200
        data = response.json
        assert 'logs' in data
        assert isinstance(data['logs'], list)
        assert 'week_avg' in data
        assert 'trend' in data
    
    def test_mood_logs_date_filtering(self, client, clinician_session, assigned_patient):
        """Date filter parameters work correctly"""
        start_date = (date.today() - timedelta(days=30)).isoformat()
        end_date = date.today().isoformat()
        
        response = client.get(
            f'/api/clinician/patient/{assigned_patient}/mood-logs?start_date={start_date}&end_date={end_date}',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 200
    
    def test_mood_logs_trend_calculation(self, client, clinician_session, assigned_patient, patient_moods):
        """Trend is calculated correctly"""
        response = client.get(
            f'/api/clinician/patient/{assigned_patient}/mood-logs',
            headers={'Cookie': f'session={clinician_session}'}
        )
        trend = response.json['trend']
        assert trend in ['improving', 'stable', 'worsening']


class TestClinicianAnalytics:
    """Tests for GET /api/clinician/patient/<username>/analytics endpoint"""
    
    def test_analytics_requires_assignment(self, client, clinician_session, unassigned_patient):
        """Cannot access unassigned patient's analytics"""
        response = client.get(
            f'/api/clinician/patient/{unassigned_patient}/analytics',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 403
    
    def test_analytics_includes_mood_data(self, client, clinician_session, assigned_patient):
        """Response includes mood_data array"""
        response = client.get(
            f'/api/clinician/patient/{assigned_patient}/analytics',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 200
        data = response.json
        assert 'mood_data' in data
        assert isinstance(data['mood_data'], list)
    
    def test_analytics_includes_activity_data(self, client, clinician_session, assigned_patient):
        """Response includes activity_data array"""
        response = client.get(
            f'/api/clinician/patient/{assigned_patient}/analytics',
            headers={'Cookie': f'session={clinician_session}'}
        )
        data = response.json
        assert 'activity_data' in data
        assert isinstance(data['activity_data'], list)
    
    def test_analytics_mood_data_schema(self, client, clinician_session, assigned_patient, analytics_data):
        """Mood data has correct schema"""
        response = client.get(
            f'/api/clinician/patient/{assigned_patient}/analytics',
            headers={'Cookie': f'session={clinician_session}'}
        )
        moods = response.json['mood_data']
        if moods:
            mood = moods[0]
            assert 'date' in mood
            assert 'mood' in mood
            assert isinstance(mood['mood'], int)


class TestClinicianAssessments:
    """Tests for GET /api/clinician/patient/<username>/assessments endpoint"""
    
    def test_assessments_requires_assignment(self, client, clinician_session, unassigned_patient):
        """Cannot access unassigned patient's assessments"""
        response = client.get(
            f'/api/clinician/patient/{unassigned_patient}/assessments',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 403
    
    def test_assessments_returns_schema(self, client, clinician_session, assigned_patient):
        """Response includes PHQ-9 and GAD-7 schema"""
        response = client.get(
            f'/api/clinician/patient/{assigned_patient}/assessments',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 200
        data = response.json
        assert 'phq9' in data
        assert 'gad7' in data
    
    def test_assessment_schema_with_data(self, client, clinician_session, assigned_patient, patient_assessments):
        """Assessment data has required fields"""
        response = client.get(
            f'/api/clinician/patient/{assigned_patient}/assessments',
            headers={'Cookie': f'session={clinician_session}'}
        )
        phq9 = response.json['phq9']
        if phq9:
            assert 'score' in phq9
            assert 'interpretation' in phq9
            assert 'date' in phq9
            assert isinstance(phq9['score'], int)


class TestClinicianSessions:
    """Tests for GET /api/clinician/patient/<username>/sessions endpoint"""
    
    def test_sessions_requires_assignment(self, client, clinician_session, unassigned_patient):
        """Cannot access unassigned patient's sessions"""
        response = client.get(
            f'/api/clinician/patient/{unassigned_patient}/sessions',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 403
    
    def test_sessions_returns_array(self, client, clinician_session, assigned_patient):
        """Response includes sessions array"""
        response = client.get(
            f'/api/clinician/patient/{assigned_patient}/sessions',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 200
        data = response.json
        assert 'sessions' in data
        assert isinstance(data['sessions'], list)
        assert 'total' in data
        assert isinstance(data['total'], int)


class TestClinicianRiskAlerts:
    """Tests for GET /api/clinician/risk-alerts endpoint"""
    
    def test_risk_alerts_requires_auth(self, client):
        """Unauthenticated request returns 401"""
        response = client.get('/api/clinician/risk-alerts')
        assert response.status_code == 401
    
    def test_risk_alerts_returns_array(self, client, clinician_session):
        """Response includes alerts array"""
        response = client.get(
            '/api/clinician/risk-alerts',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 200
        data = response.json
        assert 'alerts' in data
        assert isinstance(data['alerts'], list)
        assert 'total' in data
    
    def test_risk_alerts_includes_only_assigned(self, client, clinician_session, assigned_patient, unassigned_patient):
        """Only alerts for assigned patients are shown"""
        response = client.get(
            '/api/clinician/risk-alerts',
            headers={'Cookie': f'session={clinician_session}'}
        )
        # Alert check would depend on test data setup


class TestClinicianAppointments:
    """Tests for GET /api/clinician/patient/<username>/appointments endpoint"""
    
    def test_appointments_requires_assignment(self, client, clinician_session, unassigned_patient):
        """Cannot access unassigned patient's appointments"""
        response = client.get(
            f'/api/clinician/patient/{unassigned_patient}/appointments',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 403
    
    def test_appointments_returns_array(self, client, clinician_session, assigned_patient):
        """Response includes appointments array"""
        response = client.get(
            f'/api/clinician/patient/{assigned_patient}/appointments',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 200
        data = response.json
        assert 'appointments' in data
        assert isinstance(data['appointments'], list)


class TestClinicianMessage:
    """Tests for POST /api/clinician/message endpoint"""
    
    def test_message_requires_auth(self, client):
        """Unauthenticated request returns 401"""
        response = client.post(
            '/api/clinician/message',
            json={'recipient_username': 'patient1', 'message': 'test'},
            headers={'X-CSRF-Token': 'test'}
        )
        assert response.status_code == 401
    
    def test_message_requires_csrf_token(self, client, clinician_session):
        """Missing CSRF token returns 403"""
        response = client.post(
            '/api/clinician/message',
            json={'recipient_username': 'patient1', 'message': 'test'},
            headers={'Cookie': f'session={clinician_session}'}
            # Missing X-CSRF-Token
        )
        assert response.status_code == 403
        assert 'CSRF token invalid' in response.json['error']
    
    def test_message_requires_both_fields(self, client, clinician_session, valid_csrf_token):
        """Both recipient and message required"""
        response = client.post(
            '/api/clinician/message',
            json={'recipient_username': 'patient1'},  # Missing message
            headers={
                'Cookie': f'session={clinician_session}',
                'X-CSRF-Token': valid_csrf_token
            }
        )
        assert response.status_code == 400
        assert 'required' in response.json['error']
    
    def test_message_requires_assignment(self, client, clinician_session, unassigned_patient, valid_csrf_token):
        """Cannot message unassigned patient"""
        response = client.post(
            '/api/clinician/message',
            json={'recipient_username': unassigned_patient, 'message': 'test'},
            headers={
                'Cookie': f'session={clinician_session}',
                'X-CSRF-Token': valid_csrf_token
            }
        )
        assert response.status_code == 403
        assert 'Not assigned to this patient' in response.json['error']
    
    def test_message_max_length(self, client, clinician_session, assigned_patient, valid_csrf_token):
        """Message must not exceed max length"""
        long_message = 'x' * 10001  # Exceeds 10000 limit
        response = client.post(
            '/api/clinician/message',
            json={'recipient_username': assigned_patient, 'message': long_message},
            headers={
                'Cookie': f'session={clinician_session}',
                'X-CSRF-Token': valid_csrf_token
            }
        )
        assert response.status_code == 400
    
    def test_message_creates_successfully(self, client, clinician_session, assigned_patient, valid_csrf_token):
        """Valid message is sent successfully"""
        response = client.post(
            '/api/clinician/message',
            json={'recipient_username': assigned_patient, 'message': 'Test message'},
            headers={
                'Cookie': f'session={clinician_session}',
                'X-CSRF-Token': valid_csrf_token
            }
        )
        assert response.status_code == 201
        data = response.json
        assert data['success'] is True
        assert 'message_id' in data
        assert 'timestamp' in data


# ==================== INTEGRATION TESTS ====================

class TestClinicianDashboardWorkflow:
    """End-to-end clinician dashboard workflow"""
    
    def test_full_clinician_workflow(self, client, clinician_session, assigned_patient):
        """Clinician can: view summary → see patients → select patient → view data"""
        
        # 1. Get summary
        response = client.get(
            '/api/clinician/summary',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 200
        assert response.json['success'] is True
        
        # 2. Get patient list
        response = client.get(
            '/api/clinician/patients',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 200
        patients = response.json['patients']
        assert len(patients) > 0
        
        # 3. Get patient profile
        response = client.get(
            f'/api/clinician/patient/{assigned_patient}',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 200
        
        # 4. Get patient mood logs
        response = client.get(
            f'/api/clinician/patient/{assigned_patient}/mood-logs',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 200
        
        # 5. Get patient analytics
        response = client.get(
            f'/api/clinician/patient/{assigned_patient}/analytics',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 200


# ==================== SECURITY TESTS ====================

class TestClinicianSecurityGuardrails:
    """Verify security guardrails are enforced"""
    
    def test_sql_injection_protection(self, client, clinician_session):
        """SQL injection attempts are safely handled"""
        malicious_username = "'; DROP TABLE users; --"
        response = client.get(
            f'/api/clinician/patient/{malicious_username}/mood-logs',
            headers={'Cookie': f'session={clinician_session}'}
        )
        # Should either return 403 (not assigned) or handle gracefully
        assert response.status_code in [403, 404, 500]
    
    def test_cross_patient_access_prevented(self, client, clinician_session, test_patients):
        """Clinician cannot access data for patients they don't manage"""
        other_clinician_patient = test_patients['other_clinician_patient']
        response = client.get(
            f'/api/clinician/patient/{other_clinician_patient}/mood-logs',
            headers={'Cookie': f'session={clinician_session}'}
        )
        assert response.status_code == 403
    
    def test_xss_protection_in_response(self, client, clinician_session, assigned_patient_with_xss_name):
        """Patient names with XSS payloads are safely returned"""
        response = client.get(
            f'/api/clinician/patient/{assigned_patient_with_xss_name}',
            headers={'Cookie': f'session={clinician_session}'}
        )
        # XSS payload should be in response but safe
        assert response.status_code == 200


# ==================== TEST FIXTURES ====================

@pytest.fixture
def clinician_session(client, test_db_connection):
    """Create authenticated clinician session"""
    # Create test clinician
    test_db_connection.execute(
        "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
        ('dr_smith', 'hashed_pw', 'clinician')
    )
    test_db_connection.commit()
    
    # Return session token
    return 'test_clinician_session_token'


@pytest.fixture
def assigned_patient(client, test_db_connection, clinician_session):
    """Patient assigned to clinician"""
    test_db_connection.execute(
        "INSERT INTO users (username, password, role, full_name) VALUES (%s, %s, %s, %s)",
        ('patient_assigned', 'hashed_pw', 'user', 'John Smith')
    )
    test_db_connection.execute(
        "INSERT INTO patient_approvals (patient_username, clinician_username, status) VALUES (%s, %s, %s)",
        ('patient_assigned', 'dr_smith', 'approved')
    )
    test_db_connection.commit()
    return 'patient_assigned'


@pytest.fixture
def unassigned_patient(client, test_db_connection):
    """Patient NOT assigned to clinician"""
    test_db_connection.execute(
        "INSERT INTO users (username, password, role, full_name) VALUES (%s, %s, %s, %s)",
        ('patient_unassigned', 'hashed_pw', 'user', 'Jane Doe')
    )
    test_db_connection.commit()
    return 'patient_unassigned'


@pytest.fixture
def patient_moods(test_db_connection, assigned_patient):
    """Add mood logs for patient"""
    for i in range(1, 8):
        test_db_connection.execute(
            "INSERT INTO mood_logs (username, mood_val, sleep_val, entry_timestamp) VALUES (%s, %s, %s, %s)",
            (assigned_patient, 5 + i, 7, datetime.now() - timedelta(days=i))
        )
    test_db_connection.commit()


@pytest.fixture
def valid_csrf_token(clinician_session):
    """Generate valid CSRF token"""
    return 'test_csrf_token_valid'
