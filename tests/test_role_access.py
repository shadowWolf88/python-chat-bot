"""
Integration tests for role-based dashboard and feature access.
Ensures patients, clinicians, and developers only see and access what they should.
"""
import pytest
import requests

BASE_URL = "http://localhost:5000"

# Example test users (should exist in test DB or be created in setup)
USERS = {
    "patient": {"username": "test_patient", "password": "testpass", "pin": "1234"},
    "clinician": {"username": "test_clinician", "password": "testpass", "pin": "1234"},
    "developer": {"username": "test_dev", "password": "testpass", "pin": "1234"},
}

@pytest.mark.parametrize("role", ["patient", "clinician", "developer"])
def test_login_and_dashboard_access(role):
    creds = USERS[role]
    # Login
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": creds["username"],
        "password": creds["password"],
        "pin": creds["pin"]
    })
    assert resp.status_code == 200, f"Login failed for {role}: {resp.text}"
    data = resp.json()
    token = data.get("token")
    assert token, "No token returned"

    # Access dashboard endpoints
    headers = {"Authorization": f"Bearer {token}"}
    if role == "patient":
        # Patient should NOT see clinician or dev endpoints
        r = requests.get(f"{BASE_URL}/api/professional/dashboard", headers=headers)
        assert r.status_code == 403
        r = requests.get(f"{BASE_URL}/api/developer/dashboard", headers=headers)
        assert r.status_code == 403
        # Patient should see their own dashboard
        r = requests.get(f"{BASE_URL}/api/patient/dashboard", headers=headers)
        assert r.status_code == 200
    elif role == "clinician":
        # Clinician should see professional dashboard
        r = requests.get(f"{BASE_URL}/api/professional/dashboard", headers=headers)
        assert r.status_code == 200
        # Should not see dev dashboard
        r = requests.get(f"{BASE_URL}/api/developer/dashboard", headers=headers)
        assert r.status_code == 403
        # Should not see patient dashboard
        r = requests.get(f"{BASE_URL}/api/patient/dashboard", headers=headers)
        assert r.status_code == 403
    elif role == "developer":
        # Developer should see dev dashboard
        r = requests.get(f"{BASE_URL}/api/developer/dashboard", headers=headers)
        assert r.status_code == 200
        # Should not see clinician or patient dashboards
        r = requests.get(f"{BASE_URL}/api/professional/dashboard", headers=headers)
        assert r.status_code == 403
        r = requests.get(f"{BASE_URL}/api/patient/dashboard", headers=headers)
        assert r.status_code == 403

# Additional tests for feature access, tab visibility, and endpoint protection can be added here.
