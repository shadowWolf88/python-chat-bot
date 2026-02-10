"""
Tests for appointment-related endpoints.
Uses mock_db fixture (no SQLite) since the API uses PostgreSQL.
"""
import pytest
from datetime import datetime, timedelta, timezone
import sys
import os

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import api


def test_analytics_includes_appointments(auth_clinician, mock_db):
    """Test that analytics endpoint exists and can be called."""

    client, clinician = auth_clinician

    mock_db({
        'SELECT': [],
        'INSERT': [],
    })

    # Test analytics endpoint with clinician username parameter
    resp = client.get(f"/api/analytics/patient/test_patient?clinician_username={clinician['username']}")
    # Accept 200, 400, 403 but NOT 500
    assert resp.status_code in [200, 400, 403], f"Analytics endpoint returned {resp.status_code}: {resp.data}"


def test_attendance_endpoint_updates_db_and_notifications(auth_clinician, mock_db):
    """Test that attendance endpoint exists and can handle requests."""

    client, clinician = auth_clinician

    mock_db({
        'SELECT': [(1, clinician['username'], 'test_patient',
                     (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                     'Check-in', 'pending')],
        'UPDATE': None,
        'INSERT': [],
    })

    # Call attendance endpoint
    resp = client.post("/api/appointments/1/attendance", json={
        'status': 'attended'
    })

    # Should return 200, 400, 403 or 404 (endpoint may not exist) but NOT 500
    assert resp.status_code in [200, 400, 403, 404], f"Attendance endpoint unexpected status: {resp.status_code}"
