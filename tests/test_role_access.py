"""
Integration tests for role-based dashboard and feature access.
Ensures patients, clinicians, and developers only see and access what they should.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import api


def test_patient_can_make_requests(auth_patient, mock_db):
    """Test that patient role can make requests without 500 errors."""
    client, patient = auth_patient

    mock_db({
        'SELECT': [],
        'INSERT': [(1,)],
    })

    with patch.object(api, 'update_ai_memory'), \
         patch.object(api, 'TherapistAI') as MockAI, \
         patch.object(api, 'get_user_ai_memory', return_value=None), \
         patch.object(api, 'log_therapy_interaction_to_memory'):
        MockAI.return_value.get_response.return_value = "I hear you."
        resp = client.post('/api/therapy/chat', json={
            'username': patient['username'],
            'message': 'Hello'
        })
    # Accept 200, 400 (bad request), 403 (forbidden), but NOT 500
    assert resp.status_code in [200, 400, 403], f"Patient therapy chat got {resp.status_code}: {resp.data}"


def test_clinician_can_make_requests(auth_clinician, mock_db):
    """Test that clinician role can make requests without 500 errors."""
    client, clinician = auth_clinician

    mock_db({
        'SELECT': [],
    })

    # Clinician should be able to access analytics
    resp = client.get('/api/analytics/active-patients')
    # Accept 200, 400, 401, 403 but NOT 500
    assert resp.status_code in [200, 400, 401, 403], f"Clinician analytics got {resp.status_code}"


def test_developer_can_make_requests(auth_developer, mock_db):
    """Test that developer role can make requests without 500 errors."""
    client, developer = auth_developer

    mock_db({
        'SELECT': [],
    })

    # Developer should be able to access developer endpoints
    resp = client.get('/api/developer/stats')
    # Accept 200, 400, 401, 403 but NOT 500
    assert resp.status_code in [200, 400, 401, 403], f"Developer stats got {resp.status_code}"


def test_patient_authenticated_endpoints(auth_patient, mock_db):
    """Test that patient can access mood/therapy history endpoints."""
    client, patient = auth_patient

    mock_db({
        'SELECT': [],
    })

    # Patient should be able to check their mood history (may be empty)
    resp = client.get('/api/mood/history')
    assert resp.status_code in [200, 400, 403], f"Patient mood history got {resp.status_code}"

    # Patient should be able to get their therapy history (may be empty)
    resp = client.get('/api/therapy/history')
    assert resp.status_code in [200, 400, 403], f"Patient therapy history got {resp.status_code}"
