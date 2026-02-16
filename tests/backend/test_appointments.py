"""
Tests for Appointment System endpoints.

Covers:
  - GET  /api/appointments (clinician + patient views)
  - POST /api/appointments (create appointment)
  - DELETE /api/appointments/<id> (cancel)
  - POST /api/appointments/<id>/respond (patient accept/decline)
  - POST /api/appointments/<id>/attendance (clinician confirms)
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

import api
from tests.conftest import make_mock_db


# ==================== GET APPOINTMENTS ====================

class TestGetAppointments:
    """Tests for GET /api/appointments"""

    def test_get_clinician_appointments(self, client, mock_db):
        """Returns appointments for a clinician."""
        now = datetime.now().isoformat()
        conn, cursor = mock_db([
            (1, 'test_patient', now, 'consultation', 'Notes', 0, 1, now,
             0, 'pending', None, 'scheduled', None, None),
        ])

        resp = client.get('/api/appointments?clinician=test_clinician')
        data = resp.get_json()

        assert resp.status_code == 200
        assert len(data['appointments']) == 1
        assert data['appointments'][0]['patient_username'] == 'test_patient'

    def test_get_patient_appointments(self, client, mock_db):
        """Returns appointments for a patient."""
        now = datetime.now().isoformat()
        conn, cursor = mock_db([
            (1, 'test_clinician', now, 'check-up', '', 0, 1, now,
             0, 'pending', None, 'scheduled', None, None),
        ])

        resp = client.get('/api/appointments?patient=test_patient')
        data = resp.get_json()

        assert resp.status_code == 200
        assert len(data['appointments']) == 1
        assert data['appointments'][0]['clinician_username'] == 'test_clinician'

    def test_get_appointments_missing_params(self, client, mock_db):
        """No clinician or patient param returns 400."""
        resp = client.get('/api/appointments')
        assert resp.status_code == 400

    def test_get_appointments_empty(self, client, mock_db):
        """No appointments returns empty list."""
        conn, cursor = mock_db([])
        resp = client.get('/api/appointments?clinician=test_clinician')
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['appointments'] == []


# ==================== CREATE APPOINTMENT ====================

class TestCreateAppointment:
    """Tests for POST /api/appointments"""

    def test_create_appointment_success(self, client, mock_db):
        """Valid appointment creation returns 201."""
        future_date = (datetime.now() + timedelta(days=7)).isoformat()
        conn, cursor = mock_db({
            'INSERT INTO appointments': [(1,)],
            'INSERT INTO notifications': [],
        })

        with patch.object(api, 'log_event'):
            resp = client.post('/api/appointments', json={
                'clinician_username': 'test_clinician',
                'patient_username': 'test_patient',
                'appointment_date': future_date,
                'notes': 'Regular check-in',
            })

        data = resp.get_json()
        assert resp.status_code == 201
        assert data['success'] is True
        assert 'appointment_id' in data

    def test_create_appointment_missing_fields(self, client, mock_db):
        """Missing required fields returns 400."""
        resp = client.post('/api/appointments', json={
            'clinician_username': 'test_clinician',
        })
        assert resp.status_code == 400

    def test_create_appointment_missing_date(self, client, mock_db):
        """Missing appointment_date returns 400."""
        resp = client.post('/api/appointments', json={
            'clinician_username': 'test_clinician',
            'patient_username': 'test_patient',
        })
        assert resp.status_code == 400


# ==================== CANCEL APPOINTMENT ====================

class TestCancelAppointment:
    """Tests for DELETE /api/appointments/<id>"""

    def test_cancel_appointment_success(self, client, mock_db):
        """Cancelling existing appointment returns success."""
        conn, cursor = mock_db({
            'SELECT patient_username': [('test_patient', 'test_clinician', '2026-02-15', '14:00')],
            'DELETE FROM appointments': [],
            'INSERT INTO notifications': [],
        })

        resp = client.delete('/api/appointments/1')
        data = resp.get_json()

        assert resp.status_code == 200
        assert data['success'] is True

    def test_cancel_appointment_not_found(self, client, mock_db):
        """Cancelling non-existent appointment returns 404."""
        conn, cursor = mock_db({
            'SELECT patient_username': [],
        })

        resp = client.delete('/api/appointments/999')
        assert resp.status_code == 404


# ==================== RESPOND TO APPOINTMENT ====================

class TestRespondToAppointment:
    """Tests for POST /api/appointments/<id>/respond"""

    def test_accept_appointment(self, client, mock_db):
        """Patient accepting appointment returns success."""
        conn, cursor = mock_db({
            'SELECT clinician_username FROM appointments': [('test_clinician',)],
            'UPDATE appointments': [],
            'INSERT INTO notifications': [],
        })

        with patch.object(api, 'log_event'):
            resp = client.post('/api/appointments/1/respond', json={
                'patient_username': 'test_patient',
                'acknowledged': True,
                'response': 'accepted',
            })

        data = resp.get_json()
        assert resp.status_code == 200
        assert data['success'] is True

    def test_decline_appointment(self, client, mock_db):
        """Patient declining appointment returns success."""
        conn, cursor = mock_db({
            'SELECT clinician_username FROM appointments': [('test_clinician',)],
            'UPDATE appointments': [],
            'INSERT INTO notifications': [],
        })

        with patch.object(api, 'log_event'):
            resp = client.post('/api/appointments/1/respond', json={
                'patient_username': 'test_patient',
                'acknowledged': True,
                'response': 'declined',
            })

        assert resp.status_code == 200

    def test_respond_missing_username(self, client, mock_db):
        """Missing patient_username returns 400."""
        resp = client.post('/api/appointments/1/respond', json={
            'acknowledged': True,
            'response': 'accepted',
        })
        assert resp.status_code == 400

    def test_respond_not_acknowledged(self, client, mock_db):
        """Not acknowledged returns 400."""
        resp = client.post('/api/appointments/1/respond', json={
            'patient_username': 'test_patient',
            'acknowledged': False,
            'response': 'accepted',
        })
        assert resp.status_code == 400

    def test_respond_invalid_response(self, client, mock_db):
        """Invalid response value returns 400."""
        resp = client.post('/api/appointments/1/respond', json={
            'patient_username': 'test_patient',
            'acknowledged': True,
            'response': 'maybe',  # invalid
        })
        assert resp.status_code == 400

    def test_respond_appointment_not_found(self, client, mock_db):
        """Responding to non-existent appointment returns 404."""
        conn, cursor = mock_db({
            'SELECT clinician_username FROM appointments': [],
        })

        resp = client.post('/api/appointments/999/respond', json={
            'patient_username': 'test_patient',
            'acknowledged': True,
            'response': 'accepted',
        })
        assert resp.status_code == 404


# ==================== CONFIRM ATTENDANCE ====================

class TestConfirmAttendance:
    """Tests for POST /api/appointments/<id>/attendance"""

    def test_confirm_attended(self, client, mock_db):
        """Clinician confirms attendance returns success."""
        conn, cursor = mock_db({
            'SELECT patient_username, clinician_username FROM appointments': [('test_patient', 'test_clinician')],
            'UPDATE appointments': [],
            'INSERT INTO notifications': [],
        })

        with patch.object(api, 'log_event'):
            resp = client.post('/api/appointments/1/attendance', json={
                'clinician_username': 'test_clinician',
                'status': 'attended',
            })

        data = resp.get_json()
        assert resp.status_code == 200
        assert data['success'] is True

    def test_confirm_no_show(self, client, mock_db):
        """Marking no_show returns success."""
        conn, cursor = mock_db({
            'SELECT patient_username, clinician_username FROM appointments': [('test_patient', 'test_clinician')],
            'UPDATE appointments': [],
            'INSERT INTO notifications': [],
        })

        with patch.object(api, 'log_event'):
            resp = client.post('/api/appointments/1/attendance', json={
                'clinician_username': 'test_clinician',
                'status': 'no_show',
            })

        assert resp.status_code == 200

    def test_confirm_missing_fields(self, client, mock_db):
        """Missing required fields returns 400."""
        resp = client.post('/api/appointments/1/attendance', json={})
        assert resp.status_code == 400

    def test_confirm_invalid_status(self, client, mock_db):
        """Invalid status value returns 400."""
        resp = client.post('/api/appointments/1/attendance', json={
            'clinician_username': 'test_clinician',
            'status': 'late',  # invalid
        })
        assert resp.status_code == 400

    def test_confirm_wrong_clinician(self, client, mock_db):
        """Clinician not owning appointment returns 403."""
        conn, cursor = mock_db({
            'SELECT patient_username, clinician_username FROM appointments': [('test_patient', 'other_clinician')],
        })

        resp = client.post('/api/appointments/1/attendance', json={
            'clinician_username': 'test_clinician',
            'status': 'attended',
        })
        assert resp.status_code == 403

    def test_confirm_appointment_not_found(self, client, mock_db):
        """Non-existent appointment returns 404."""
        conn, cursor = mock_db({
            'SELECT patient_username, clinician_username FROM appointments': [],
        })

        resp = client.post('/api/appointments/999/attendance', json={
            'clinician_username': 'test_clinician',
            'status': 'attended',
        })
        assert resp.status_code == 404
