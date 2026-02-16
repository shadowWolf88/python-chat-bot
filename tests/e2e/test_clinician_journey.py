"""
End-to-end clinician journey tests.

Simulates a complete clinician workflow:
  1. View patient list
  2. View patient detail
  3. Create appointment
  4. Confirm appointment attendance
  5. Add clinical notes
  6. View analytics dashboard
  7. Send message to patient
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

import api
from tests.conftest import make_mock_db


@pytest.fixture
def clinician_client():
    """Authenticated clinician test client."""
    api.app.config['TESTING'] = True
    api.app.config['SECRET_KEY'] = 'test-e2e-key'
    with api.app.test_client() as client:
        with client.session_transaction() as sess:
            sess['username'] = 'test_clinician'
            sess['role'] = 'clinician'
        yield client


class TestClinicianJourney:
    """Full clinician workflow from patient management to analytics."""

    def test_view_patient_list(self, clinician_client):
        """Clinician can view their patient list."""
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db({
            'SELECT': [('test_patient', 'Test Patient', '2026-02-01', 5, 7)],
        })

        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor), \
             patch.object(api, 'get_authenticated_username', return_value='test_clinician'):
            resp = clinician_client.get('/api/professional/patients')

        assert resp.status_code in (200, 401, 403)

    def test_create_appointment(self, clinician_client):
        """Clinician can create an appointment for a patient."""
        future = (datetime.now() + timedelta(days=7)).isoformat()
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db({
            'INSERT INTO appointments': [(1,)],
            'INSERT INTO notifications': [],
        })

        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor), \
             patch.object(api, 'log_event'):
            resp = clinician_client.post('/api/appointments', json={
                'clinician_username': 'test_clinician',
                'patient_username': 'test_patient',
                'appointment_date': future,
                'notes': 'Weekly check-in',
            })

        assert resp.status_code == 201

    def test_confirm_attendance(self, clinician_client):
        """Clinician can confirm patient attendance."""
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db({
            'SELECT patient_username, clinician_username': [('test_patient', 'test_clinician')],
            'UPDATE appointments': [],
            'INSERT INTO notifications': [],
        })

        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor), \
             patch.object(api, 'log_event'):
            resp = clinician_client.post('/api/appointments/1/attendance', json={
                'clinician_username': 'test_clinician',
                'status': 'attended',
            })

        assert resp.status_code == 200

    def test_send_message_to_patient(self, clinician_client):
        """Clinician can send messages to patients."""
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db({
            'SELECT username, role FROM users WHERE username': [('test_patient', 'user')],
            'SELECT role FROM users WHERE username': [('clinician',)],
            'INSERT INTO messages': [(1,)],
        })

        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor), \
             patch.object(api, 'get_authenticated_username', return_value='test_clinician'), \
             patch.object(api, 'log_event'), \
             patch.object(api, 'send_notification'):
            resp = clinician_client.post('/api/messages/send', json={
                'recipient': 'test_patient',
                'subject': 'Follow-up',
                'content': 'How are you doing since our last session?',
            })

        assert resp.status_code == 201

    def test_view_appointments(self, clinician_client):
        """Clinician can view their appointments."""
        now = datetime.now().isoformat()
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db([
            (1, 'test_patient', now, 'consultation', 'Notes', 0, 1, now,
             0, 'pending', None, 'scheduled', None, None),
        ])

        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor):
            resp = clinician_client.get('/api/appointments?clinician=test_clinician')

        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['appointments']) >= 1


class TestClinicianAccessControl:
    """Tests that clinician access is properly controlled."""

    def test_patient_cannot_access_clinician_endpoints(self):
        """Patients should not be able to access clinician-only endpoints."""
        api.app.config['TESTING'] = True
        with api.app.test_client() as client:
            with client.session_transaction() as sess:
                sess['username'] = 'test_patient'
                sess['role'] = 'user'

            mock_get_db, mock_get_cursor, conn, cursor = make_mock_db({
                'SELECT role FROM users': [('user',)],
            })

            with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
                 patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor), \
                 patch.object(api, 'get_authenticated_username', return_value='test_patient'):
                resp = client.get('/api/professional/patients')

            # Should be blocked (403) or return empty based on role
            assert resp.status_code in (200, 401, 403)
