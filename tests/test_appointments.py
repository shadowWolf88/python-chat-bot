import sqlite3
import pytest
from datetime import datetime, timedelta, timezone

import sys
import pathlib

# Ensure repo root is on sys.path for imports
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import api


@pytest.fixture()
def client(tmp_path, monkeypatch):
    # Use a temporary DB for tests
    db_path = str(tmp_path / "test_therapist_app.db")
    monkeypatch.setattr(api, 'DB_PATH', db_path)
    # Ensure DB initialized
    api.init_db()
    app = api.app.test_client()
    yield app


def create_user(cur, username, role='user'):
    cur.execute("INSERT INTO users (username, password, role, last_login, full_name) VALUES (?,?,?,?,?)",
                (username, 'passhash', role, datetime.now(timezone.utc).isoformat(), username))


def test_analytics_includes_appointments(client):
    # Prepare DB with a patient, clinician and appointments
    conn = sqlite3.connect(api.DB_PATH)
    cur = conn.cursor()
    create_user(cur, 'patient1', 'user')
    create_user(cur, 'dr_smith', 'clinician')

    # upcoming appointment
    appt_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    cur.execute("INSERT INTO appointments (clinician_username, patient_username, appointment_date, notes, patient_response) VALUES (?,?,?,?,?)",
                ('dr_smith', 'patient1', appt_date, 'Follow-up', 'pending'))
    # past appointment
    past_date = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    cur.execute("INSERT INTO appointments (clinician_username, patient_username, appointment_date, notes, patient_response) VALUES (?,?,?,?,?)",
                ('dr_smith', 'patient1', past_date, 'Last session', 'accepted'))
    conn.commit()
    conn.close()

    resp = client.get(f"/api/analytics/patient/patient1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'upcoming_appointments' in data
    assert 'recent_past_appointments' in data
    assert any(a['clinician_username'] == 'dr_smith' for a in data['upcoming_appointments'])
    assert any(a['clinician_username'] == 'dr_smith' for a in data['recent_past_appointments'])


def test_attendance_endpoint_updates_db_and_notifications(client):
    conn = sqlite3.connect(api.DB_PATH)
    cur = conn.cursor()
    create_user(cur, 'patient2', 'user')
    create_user(cur, 'dr_jones', 'clinician')

    appt_date = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    cur.execute("INSERT INTO appointments (clinician_username, patient_username, appointment_date, notes) VALUES (?,?,?,?)",
                ('dr_jones', 'patient2', appt_date, 'Check-in'))
    appt_id = cur.lastrowid
    conn.commit()

    # Call attendance endpoint as clinician
    client_resp = client.post(f"/api/appointments/{appt_id}/attendance", json={
        'clinician_username': 'dr_jones',
        'status': 'attended'
    })
    assert client_resp.status_code == 200
    j = client_resp.get_json()
    assert j.get('success') is True

    # Verify appointment row updated
    r = cur.execute("SELECT attendance_status, attendance_confirmed_by, attendance_confirmed_at FROM appointments WHERE id=?", (appt_id,)).fetchone()
    assert r[0] == 'attended'
    assert r[1] == 'dr_jones'
    assert r[2] is not None

    # Verify notification created for patient
    note = cur.execute("SELECT recipient_username, message, notification_type FROM notifications WHERE recipient_username=? ORDER BY created_at DESC LIMIT 1", ('patient2',)).fetchone()
    assert note is not None
    assert note[0] == 'patient2'
    assert note[2] == 'appointment_attendance'

    conn.close()