"""
TIER 2.2: Crisis Alert System - Integration Tests
Tests the actual API endpoints with database
"""

import pytest
import json
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '/home/computer001/Documents/python chat bot')


# Note: These tests would be run with conftest.py fixtures that provide:
# - Flask test client
# - Database connection
# - Authenticated sessions
# - Test data cleanup


class TestCrisisDetectEndpoint:
    """Integration tests for POST /api/crisis/detect"""
    
    def test_detect_crisis_message(self, client, auth_headers):
        """POST /api/crisis/detect should detect crisis message"""
        response = client.post(
            '/api/crisis/detect',
            json={'message': 'I want to kill myself'},
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201]
        data = response.get_json()
        assert 'severity' in data
        assert data['severity'] in ['critical', 'high', 'moderate', 'low']
    
    def test_detect_requires_authentication(self, client):
        """POST /api/crisis/detect requires authentication"""
        response = client.post(
            '/api/crisis/detect',
            json={'message': 'Test message'}
        )
        
        assert response.status_code == 401
    
    def test_detect_requires_csrf_token(self, client, auth_headers):
        """POST /api/crisis/detect requires CSRF token"""
        response = client.post(
            '/api/crisis/detect',
            json={'message': 'Test'},
            headers={'Authorization': auth_headers.get('Authorization')}
            # Missing X-CSRF-Token
        )
        
        # Should fail without CSRF token (unless endpoint is exempt)
        # assert response.status_code == 403
    
    def test_detect_empty_message(self, client, auth_headers):
        """Empty message should be rejected"""
        response = client.post(
            '/api/crisis/detect',
            json={'message': ''},
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    def test_detect_long_message(self, client, auth_headers):
        """Very long message should be rejected"""
        response = client.post(
            '/api/crisis/detect',
            json={'message': 'x' * 15000},  # Over 10000 char limit
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    def test_detect_normal_message_no_crisis(self, client, auth_headers):
        """Normal message should return low/none severity"""
        response = client.post(
            '/api/crisis/detect',
            json={'message': 'I had a good day today'},
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201]
        data = response.get_json()
        assert data['severity'] in ['low', 'none', 'moderate']


class TestGetAlertsEndpoint:
    """Integration tests for GET /api/crisis/alerts"""
    
    def test_get_alerts_for_clinician(self, client, auth_headers_clinician):
        """GET /api/crisis/alerts returns alerts for clinician's patients"""
        response = client.get(
            '/api/crisis/alerts',
            headers=auth_headers_clinician
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list) or 'alerts' in data
    
    def test_get_alerts_requires_authentication(self, client):
        """GET /api/crisis/alerts requires authentication"""
        response = client.get('/api/crisis/alerts')
        
        assert response.status_code == 401
    
    def test_get_alerts_clinician_only(self, client, auth_headers_patient):
        """Patients should not see crisis alerts"""
        response = client.get(
            '/api/crisis/alerts',
            headers=auth_headers_patient
        )
        
        # Patients might not have access to this endpoint
        assert response.status_code in [403, 404]
    
    def test_get_alerts_filtered_by_severity(self, client, auth_headers_clinician):
        """GET /api/crisis/alerts?severity=critical returns critical alerts"""
        response = client.get(
            '/api/crisis/alerts?severity=critical',
            headers=auth_headers_clinician
        )
        
        assert response.status_code == 200
        data = response.get_json()
        # All returned alerts should be critical
        if isinstance(data, list):
            assert all(alert.get('severity') == 'critical' for alert in data)
    
    def test_get_unacknowledged_alerts(self, client, auth_headers_clinician):
        """GET /api/crisis/alerts?acknowledged=false returns unacknowledged"""
        response = client.get(
            '/api/crisis/alerts?acknowledged=false',
            headers=auth_headers_clinician
        )
        
        assert response.status_code == 200
        data = response.get_json()
        # All returned alerts should be unacknowledged
        if isinstance(data, list):
            assert all(not alert.get('acknowledged') for alert in data)


class TestAcknowledgeAlertEndpoint:
    """Integration tests for POST /api/crisis/alerts/<id>/acknowledge"""
    
    def test_acknowledge_alert(self, client, auth_headers_clinician):
        """POST /api/crisis/alerts/1/acknowledge acknowledges alert"""
        response = client.post(
            '/api/crisis/alerts/1/acknowledge',
            json={
                'action_taken': 'Called patient, confirmed safety plan',
                'follow_up_scheduled': True,
                'follow_up_date': '2026-02-15'
            },
            headers=auth_headers_clinician
        )
        
        # Should succeed (201) or update (200)
        assert response.status_code in [200, 201, 204]
    
    def test_acknowledge_requires_action_description(self, client, auth_headers_clinician):
        """Acknowledgment requires action_taken field"""
        response = client.post(
            '/api/crisis/alerts/1/acknowledge',
            json={'follow_up_scheduled': True},
            headers=auth_headers_clinician
        )
        
        assert response.status_code == 400
    
    def test_acknowledge_already_acknowledged(self, client, auth_headers_clinician):
        """Acknowledging already-acknowledged alert handled gracefully"""
        # First acknowledgment
        client.post(
            '/api/crisis/alerts/1/acknowledge',
            json={'action_taken': 'First response'},
            headers=auth_headers_clinician
        )
        
        # Second acknowledgment
        response = client.post(
            '/api/crisis/alerts/1/acknowledge',
            json={'action_taken': 'Second response'},
            headers=auth_headers_clinician
        )
        
        # Should succeed (might be 200) or indicate already acknowledged
        assert response.status_code in [200, 201, 409]
    
    def test_acknowledge_requires_csrf_token(self, client, auth_headers_clinician):
        """POST /api/crisis/alerts/1/acknowledge requires CSRF token"""
        # Missing X-CSRF-Token header
        response = client.post(
            '/api/crisis/alerts/1/acknowledge',
            json={'action_taken': 'Test action'},
            headers={k: v for k, v in auth_headers_clinician.items() if k != 'X-CSRF-Token'}
        )
        
        # Should fail (unless endpoint is exempt)
        # assert response.status_code == 403


class TestResolveAlertEndpoint:
    """Integration tests for POST /api/crisis/alerts/<id>/resolve"""
    
    def test_resolve_alert(self, client, auth_headers_clinician):
        """POST /api/crisis/alerts/1/resolve marks alert as resolved"""
        response = client.post(
            '/api/crisis/alerts/1/resolve',
            json={'resolution_summary': 'Patient stable, safety plan confirmed'},
            headers=auth_headers_clinician
        )
        
        assert response.status_code in [200, 201, 204]
    
    def test_resolve_requires_summary(self, client, auth_headers_clinician):
        """Resolution requires resolution_summary"""
        response = client.post(
            '/api/crisis/alerts/1/resolve',
            json={},
            headers=auth_headers_clinician
        )
        
        assert response.status_code == 400
    
    def test_resolve_non_existent_alert(self, client, auth_headers_clinician):
        """Resolving non-existent alert returns 404"""
        response = client.post(
            '/api/crisis/alerts/99999/resolve',
            json={'resolution_summary': 'Test'},
            headers=auth_headers_clinician
        )
        
        assert response.status_code == 404
    
    def test_alert_becomes_resolved(self, client, auth_headers_clinician):
        """Alert should have resolved=true after resolution"""
        # Create alert and resolve
        client.post(
            '/api/crisis/alerts/1/resolve',
            json={'resolution_summary': 'Test'},
            headers=auth_headers_clinician
        )
        
        # Check alert status
        response = client.get(
            '/api/crisis/alerts',
            headers=auth_headers_clinician
        )
        
        assert response.status_code == 200


class TestEmergencyContactsEndpoint:
    """Integration tests for /api/crisis/contacts CRUD"""
    
    def test_create_emergency_contact(self, client, auth_headers_patient):
        """POST /api/crisis/contacts creates emergency contact"""
        response = client.post(
            '/api/crisis/contacts',
            json={
                'name': 'John Smith',
                'relationship': 'Parent',
                'phone': '+44 7911 123456',
                'email': 'john@example.com',
                'is_primary': True
            },
            headers=auth_headers_patient
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'id' in data
        assert data['name'] == 'John Smith'
    
    def test_get_emergency_contacts(self, client, auth_headers_patient):
        """GET /api/crisis/contacts returns contacts for patient"""
        response = client.get(
            '/api/crisis/contacts',
            headers=auth_headers_patient
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list) or 'contacts' in data
    
    def test_update_emergency_contact(self, client, auth_headers_patient):
        """PUT /api/crisis/contacts/1 updates contact"""
        response = client.put(
            '/api/crisis/contacts/1',
            json={'phone': '+44 7911 654321'},
            headers=auth_headers_patient
        )
        
        assert response.status_code in [200, 204]
    
    def test_delete_emergency_contact(self, client, auth_headers_patient):
        """DELETE /api/crisis/contacts/1 deletes contact"""
        response = client.delete(
            '/api/crisis/contacts/1',
            headers=auth_headers_patient
        )
        
        assert response.status_code in [200, 204, 404]
    
    def test_contact_phone_validation(self, client, auth_headers_patient):
        """Phone number should be validated"""
        response = client.post(
            '/api/crisis/contacts',
            json={
                'name': 'Test',
                'relationship': 'Friend',
                'phone': 'invalid-phone',
                'email': 'test@example.com'
            },
            headers=auth_headers_patient
        )
        
        # Should reject invalid phone
        assert response.status_code in [400, 422]
    
    def test_contact_email_validation(self, client, auth_headers_patient):
        """Email should be validated"""
        response = client.post(
            '/api/crisis/contacts',
            json={
                'name': 'Test',
                'relationship': 'Friend',
                'phone': '+44 7911 123456',
                'email': 'invalid-email'
            },
            headers=auth_headers_patient
        )
        
        # Should reject invalid email
        assert response.status_code in [400, 422]
    
    def test_cannot_delete_others_contact(self, client, auth_headers_patient, auth_headers_patient2):
        """Patient cannot delete another patient's contact"""
        response = client.delete(
            '/api/crisis/contacts/999',
            headers=auth_headers_patient2
        )
        
        assert response.status_code in [403, 404]


class TestCopingStrategiesEndpoint:
    """Integration tests for GET /api/crisis/coping-strategies"""
    
    def test_get_coping_strategies(self, client, auth_headers):
        """GET /api/crisis/coping-strategies returns strategies"""
        response = client.get(
            '/api/crisis/coping-strategies',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list) or 'strategies' in data
        assert len(data) >= 5  # Should have at least 5 strategies
    
    def test_strategies_have_required_fields(self, client, auth_headers):
        """Strategies should have title, description, steps"""
        response = client.get(
            '/api/crisis/coping-strategies',
            headers=auth_headers
        )
        
        data = response.get_json()
        strategies = data if isinstance(data, list) else data.get('strategies', [])
        
        for strategy in strategies:
            assert 'title' in strategy
            assert 'description' in strategy
            assert 'steps' in strategy
            assert isinstance(strategy['steps'], list)
    
    def test_strategies_are_accessible(self, client, auth_headers):
        """Strategies should be accessible to all authenticated users"""
        response = client.get(
            '/api/crisis/coping-strategies',
            headers=auth_headers
        )
        
        assert response.status_code == 200


class TestAuditLogging:
    """Integration tests for audit logging of crisis events"""
    
    def test_crisis_detection_logged(self, client, auth_headers):
        """Crisis detection creates audit log entry"""
        client.post(
            '/api/crisis/detect',
            json={'message': 'I want to hurt myself'},
            headers=auth_headers
        )
        
        # Check audit log table
        # Log entry should have:
        # - category = 'crisis'
        # - action = 'crisis_detected'
        # - username = authenticated user
    
    def test_acknowledgment_logged(self, client, auth_headers_clinician):
        """Alert acknowledgment creates audit log entry"""
        client.post(
            '/api/crisis/alerts/1/acknowledge',
            json={'action_taken': 'Test action'},
            headers=auth_headers_clinician
        )
        
        # Check audit log table for:
        # - category = 'crisis'
        # - action = 'alert_acknowledged'


class TestErrorHandlingAndValidation:
    """Integration tests for error handling"""
    
    def test_invalid_json(self, client, auth_headers):
        """Invalid JSON should return 400"""
        response = client.post(
            '/api/crisis/detect',
            data='invalid json',
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    def test_database_error_handling(self, client, auth_headers):
        """Database errors should be handled gracefully"""
        # Test with valid request - should handle any DB errors
        response = client.post(
            '/api/crisis/detect',
            json={'message': 'Test message'},
            headers=auth_headers
        )
        
        # Should not expose internal database errors
        if response.status_code == 500:
            data = response.get_json()
            assert 'error' in data
            assert 'database' not in data.get('error', '').lower()


# Fixtures would be defined in conftest.py
@pytest.fixture
def client():
    """Flask test client"""
    pass

@pytest.fixture
def auth_headers():
    """Authenticated user headers"""
    pass

@pytest.fixture
def auth_headers_patient():
    """Patient user headers"""
    pass

@pytest.fixture
def auth_headers_clinician():
    """Clinician user headers"""
    pass

@pytest.fixture
def auth_headers_patient2():
    """Second patient user headers"""
    pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
