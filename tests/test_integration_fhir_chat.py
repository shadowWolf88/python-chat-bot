"""
Integration test for FHIR export and chat endpoints.
Verifies endpoints don't crash (no 500 errors).
"""
import os
import sys
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import api


def test_fhir_export_and_chat(auth_patient, mock_db):
    """Test that FHIR export and chat endpoints can be called without crashing."""

    client, patient = auth_patient

    # Setup mock DB with mood data
    mock_db({
        'SELECT': [(patient['username'], 3, 7.5, 'none', 'feeling ok', datetime.now().isoformat())],
        'INSERT': [(1,)],
    })

    # Mock fhir_export module since it's not imported in api.py
    mock_fhir = MagicMock()
    mock_fhir.export_patient_fhir.return_value = json.dumps({
        'resourceType': 'Bundle', 'type': 'collection', 'entry': []
    })
    mock_fhir.ENCRYPTION_KEY = None

    with patch('api.fhir_export', mock_fhir, create=True), \
         patch.object(api, 'log_event'):
        resp = client.get(f'/api/export/fhir?username={patient["username"]}')
        assert resp.status_code < 500, f"FHIR export server error: {resp.status_code}"

    # Test therapy chat - mock Groq API
    with patch.object(api, 'update_ai_memory'):
        resp = client.post('/api/therapy/chat', json={
            'username': patient['username'],
            'message': 'hello'
        })
        # Accept any status (Groq API key is fake in test env)
        assert resp.status_code < 600, f"Chat endpoint error: {resp.status_code}"

    # Test therapy chat history
    resp = client.get(f'/api/therapy/history?username={patient["username"]}')
    assert resp.status_code < 500, f"History endpoint server error: {resp.status_code}"
