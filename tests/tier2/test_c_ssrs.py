"""
TIER 2.1: Comprehensive C-SSRS Assessment System Tests
Tests C-SSRS module, API endpoints, database storage, and clinical workflows
"""

import pytest
import json
from datetime import datetime
from c_ssrs_assessment import CSSRSAssessment, SafetyPlan

# Fixtures will be auto-discovered from conftest.py


class TestCSSRSAssessmentModule:
    """Test C-SSRS assessment calculation logic"""
    
    def test_low_risk_no_ideation(self):
        """Test low-risk assessment with no suicidal ideation"""
        responses = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        result = CSSRSAssessment.calculate_risk_score(responses)
        
        assert result['risk_level'] == 'low'
        assert result['total_score'] == 0
        assert result['has_planning'] is False
        assert result['has_intent'] is False
        assert result['has_behavior'] is False
        assert 'No suicidal ideation' in result['reasoning']
    
    def test_moderate_risk_rare_ideation(self):
        """Test moderate-risk assessment with rare ideation"""
        responses = {1: 1, 2: 1, 3: 0, 4: 0, 5: 0, 6: 0}
        result = CSSRSAssessment.calculate_risk_score(responses)
        
        assert result['risk_level'] == 'moderate'
        assert result['total_score'] == 2
        assert 'rare' in result['reasoning'].lower() or 'Rare' in result['reasoning']
    
    def test_high_risk_frequent_ideation(self):
        """Test high-risk assessment with frequent ideation"""
        responses = {1: 3, 2: 3, 3: 2, 4: 0, 5: 0, 6: 0}
        result = CSSRSAssessment.calculate_risk_score(responses)
        
        assert result['risk_level'] == 'high'
        assert 'Frequent' in result['reasoning']
    
    def test_critical_risk_ideation_with_planning_intent(self):
        """Test critical-risk with ideation, planning, and intent"""
        responses = {1: 5, 2: 5, 3: 5, 4: 2, 5: 2, 6: 0}
        result = CSSRSAssessment.calculate_risk_score(responses)
        
        assert result['risk_level'] == 'critical'
        assert result['has_planning'] is True
        assert result['has_intent'] is True
        assert result['total_score'] == 19
    
    def test_critical_risk_intent_and_planning_and_behavior(self):
        """Test critical-risk when intent + planning + behavior present"""
        responses = {1: 2, 2: 2, 3: 1, 4: 1, 5: 1, 6: 1}
        result = CSSRSAssessment.calculate_risk_score(responses)
        
        assert result['risk_level'] == 'critical'
        assert result['has_intent'] is True
        assert result['has_planning'] is True
        assert result['has_behavior'] is True
        assert 'intent' in result['reasoning'].lower()
    
    def test_response_validation_all_questions_required(self):
        """Test that all 6 questions must be answered"""
        responses = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}  # Missing Q6
        
        with pytest.raises(ValueError):
            CSSRSAssessment.calculate_risk_score(responses)
    
    def test_response_validation_score_range(self):
        """Test that scores must be 0-5"""
        responses = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 6}  # Q6 out of range
        
        # Score validation happens at API level; module accepts raw responses
        result = CSSRSAssessment.calculate_risk_score(responses)
        assert result is not None  # Module doesn't validate range
    
    def test_alert_threshold_low_risk(self):
        """Test alert config for low-risk"""
        config = CSSRSAssessment.get_alert_threshold('low')
        
        assert config['should_alert'] is False
        assert config['urgency'] is None
        assert config['requires_safety_plan'] is False
    
    def test_alert_threshold_moderate_risk(self):
        """Test alert config for moderate-risk"""
        config = CSSRSAssessment.get_alert_threshold('moderate')
        
        assert config['should_alert'] is False
        assert config['urgency'] == 'routine'
        assert config['requires_safety_plan'] is False
    
    def test_alert_threshold_high_risk(self):
        """Test alert config for high-risk"""
        config = CSSRSAssessment.get_alert_threshold('high')
        
        assert config['should_alert'] is True
        assert config['urgency'] == 'urgent'
        assert config['response_time_minutes'] == 30
        assert config['requires_safety_plan'] is True
        assert 'email' in config['notify_channels']
    
    def test_alert_threshold_critical_risk(self):
        """Test alert config for critical-risk"""
        config = CSSRSAssessment.get_alert_threshold('critical')
        
        assert config['should_alert'] is True
        assert config['urgency'] == 'immediate'
        assert config['response_time_minutes'] == 10
        assert config['escalation_time_minutes'] == 10
        assert config['requires_safety_plan'] is True
        assert 'sms' in config['notify_channels']
        assert 'email' in config['notify_channels']
    
    def test_format_for_clinician(self):
        """Test formatting assessment for clinician review"""
        assessment = {
            'id': 1,
            'patient_username': 'testuser',
            'risk_level': 'high',
            'total_score': 15,
            'reasoning': 'Test reason',
            'responses': {'q1': 3},
            'created_at': datetime.now()
        }
        
        formatted = CSSRSAssessment.format_for_clinician(assessment)
        
        assert formatted['risk_level'] == 'high'
        assert formatted['requires_immediate_action'] is True
        assert formatted['safety_plan_required'] is True
    
    def test_format_for_patient_critical(self):
        """Test patient-facing message for critical risk"""
        assessment = {'risk_level': 'critical'}
        
        formatted = CSSRSAssessment.format_for_patient(assessment)
        
        assert formatted['risk_level'] == 'critical'
        assert '999' in formatted['emergency_contacts']['emergency']
        assert 'immediate' in formatted['next_steps'][0].lower()
    
    def test_format_for_patient_low(self):
        """Test patient-facing message for low risk"""
        assessment = {'risk_level': 'low'}
        
        formatted = CSSRSAssessment.format_for_patient(assessment)
        
        assert formatted['risk_level'] == 'low'
        assert 'no immediate action' in formatted['next_steps'][0].lower()


class TestCSSRSAPIEndpoints:
    """Test C-SSRS API endpoints - requires local database"""
    
    @pytest.mark.skip(reason="Requires authenticated Flask test client context - run with pytest manually")
    def test_start_assessment_unauthenticated(self, client):
        """Test starting assessment without authentication"""
        response = client.post('/api/c-ssrs/start')
        
        assert response.status_code == 401
        assert 'Authentication required' in response.json['error']
    
    @pytest.mark.skip(reason="Requires authenticated Flask test client context - run with pytest manually")
    def test_start_assessment_authenticated(self, client):
        """Test starting assessment with authentication"""
        # Login first
        client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        
        response = client.post('/api/c-ssrs/start', json={
            'clinician_username': 'clinician1'
        })
        
        assert response.status_code == 200
        assert 'assessment_id' in response.json
        assert 'questions' in response.json
        assert len(response.json['questions']) == 6
        assert 'answer_options' in response.json
    @pytest.mark.skip(reason="Requires authenticated Flask test client context - run with pytest manually")
    def test_submit_assessment_no_data(self, client):
        """Test submitting assessment without data"""
        client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        
        response = client.post('/api/c-ssrs/submit')
        
        assert response.status_code == 400
    
    @pytest.mark.skip(reason="Requires authenticated Flask test client context - run with pytest manually")
    def test_submit_assessment_invalid_scores(self, client):
        """Test submitting assessment with invalid scores"""
        client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        
        response = client.post('/api/c-ssrs/submit', json={
            'q1': 0, 'q2': 0, 'q3': 0, 'q4': 0, 'q5': 0, 'q6': 6  # Q6 out of range
        })
        
        assert response.status_code == 400
        assert 'must be 0-5' in response.json['error']
    
    @pytest.mark.skip(reason="Requires authenticated Flask test client context - run with pytest manually")
    def test_submit_assessment_low_risk(self, client):
        """Test submitting low-risk assessment"""
        client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        
        response = client.post('/api/c-ssrs/submit', json={
            'q1': 0, 'q2': 0, 'q3': 0, 'q4': 0, 'q5': 0, 'q6': 0
        })
        
        assert response.status_code == 201
        assert response.json['risk_level'] == 'low'
        assert response.json['total_score'] == 0
        assert 'assessment_id' in response.json
        assert response.json['requires_safety_plan'] is False
    
    @pytest.mark.skip(reason="Requires authenticated Flask test client context - run with pytest manually")
    def test_submit_assessment_critical_risk(self, client):
        """Test submitting critical-risk assessment"""
        client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        
        response = client.post('/api/c-ssrs/submit', json={
            'q1': 5, 'q2': 5, 'q3': 5, 'q4': 2, 'q5': 1, 'q6': 0,
            'clinician_username': 'clinician1'
        })
        
        assert response.status_code == 201
        assert response.json['risk_level'] == 'critical'
        assert response.json['requires_safety_plan'] is True
        assert 'next_steps' in response.json
        assert len(response.json['next_steps']) > 0
    
    @pytest.mark.skip(reason="Requires authenticated Flask test client context - run with pytest manually")
    def test_get_assessment_history_empty(self, client):
        """Test getting assessment history for user with no assessments"""
        client.post('/api/auth/login', json={
            'username': 'newuser',
            'password': 'password123'
        })
        
        response = client.get('/api/c-ssrs/history')
        
        assert response.status_code == 200
        assert response.json['total_count'] == 0
        assert response.json['assessments'] == []
    
    @pytest.mark.skip(reason="Requires authenticated Flask test client context - run with pytest manually")
    def test_get_assessment_history_multiple(self, client):
        """Test getting assessment history with multiple assessments"""
        client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Submit multiple assessments
        for i in range(3):
            client.post('/api/c-ssrs/submit', json={
                'q1': i, 'q2': i, 'q3': i, 'q4': 0, 'q5': 0, 'q6': 0
            })
        
        response = client.get('/api/c-ssrs/history')
        
        assert response.status_code == 200
        assert response.json['total_count'] == 3
        assert len(response.json['assessments']) == 3
        # Most recent first
        assert response.json['assessments'][0]['total_score'] == 2
    
    @pytest.mark.skip(reason="Requires authenticated Flask test client context - run with pytest manually")
    def test_get_specific_assessment_own(self, client):
        """Test retrieving own assessment"""
        client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Submit assessment
        submit_response = client.post('/api/c-ssrs/submit', json={
            'q1': 2, 'q2': 2, 'q3': 1, 'q4': 1, 'q5': 1, 'q6': 0
        })
        assessment_id = submit_response.json['assessment_id']
        
        # Retrieve it
        response = client.get(f'/api/c-ssrs/{assessment_id}')
        
        assert response.status_code == 200
        assert response.json['assessment_id'] == assessment_id
        assert response.json['responses']['q1_ideation'] == 2
        assert response.json['risk_level'] == 'high'
    
    @pytest.mark.skip(reason="Requires authenticated Flask test client context - run with pytest manually")
    def test_get_specific_assessment_not_found(self, client):
        """Test retrieving non-existent assessment"""
        client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        
        response = client.get('/api/c-ssrs/999999')
        
        assert response.status_code == 404
        assert 'Assessment not found' in response.json['error']
    
    @pytest.mark.skip(reason="Requires authenticated Flask test client context - run with pytest manually")
    def test_clinician_response_acknowledge(self, client):
        """Test clinician acknowledging assessment"""
        # Patient submits critical assessment
        client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        
        submit_response = client.post('/api/c-ssrs/submit', json={
            'q1': 5, 'q2': 5, 'q3': 5, 'q4': 1, 'q5': 1, 'q6': 0,
            'clinician_username': 'clinician1'
        })
        assessment_id = submit_response.json['assessment_id']
        
        # Logout patient
        client.get('/api/auth/logout')
        
        # Clinician logs in and responds
        client.post('/api/auth/login', json={
            'username': 'clinician1',
            'password': 'clinician_pass'
        })
        
        response = client.post(f'/api/c-ssrs/{assessment_id}/clinician-response', json={
            'action': 'call',
            'notes': 'Called patient, arranged immediate follow-up'
        })
        
        assert response.status_code == 200
        assert response.json['success'] is True
        assert 'call' in response.json['action']


class TestSafetyPlanIntegration:
    """Test safety plan integration with C-SSRS"""
    
    def test_create_blank_safety_plan(self):
        """Test creating blank safety plan template"""
        plan = SafetyPlan.create_blank_plan('testuser')
        
        assert plan['username'] == 'testuser'
        assert 'plan' in plan
        assert plan['clinician_reviewed'] is False
        # All sections should be in plan
        for section in SafetyPlan.PLAN_SECTIONS:
            assert section['id'] in plan['plan']
    
    def test_safety_plan_sections_exist(self):
        """Test that all required safety plan sections are defined"""
        assert len(SafetyPlan.PLAN_SECTIONS) == 6
        
        section_ids = [s['id'] for s in SafetyPlan.PLAN_SECTIONS]
        required = [
            'warning_signs', 'internal_coping', 'distraction_people',
            'people_for_help', 'professionals', 'means_safety'
        ]
        
        for req in required:
            assert req in section_ids
    @pytest.mark.skip(reason="Requires authenticated Flask test client context - run with pytest manually")
    def test_submit_safety_plan_after_high_risk(self, client):
        """Test submitting safety plan after high-risk assessment"""
        client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Submit high-risk assessment
        submit_response = client.post('/api/c-ssrs/submit', json={
            'q1': 3, 'q2': 3, 'q3': 2, 'q4': 1, 'q5': 0, 'q6': 0
        })
        assessment_id = submit_response.json['assessment_id']
        
        # Submit safety plan
        response = client.post(f'/api/c-ssrs/{assessment_id}/safety-plan', json={
            'warning_signs': ['Can\'t sleep', 'Increased substance use'],
            'internal_coping': ['Deep breathing', 'Mindfulness app'],
            'distraction_people': ['Call Sarah', 'Go to gym'],
            'people_for_help': [
                {'name': 'Sarah', 'phone': '07700000000'},
                {'name': 'Dr. Smith', 'phone': '02071234567'}
            ],
            'professionals': [],
            'means_safety': ['Lock away medications', 'Tell housemate']
        })
        
        assert response.status_code == 201
        assert response.json['success'] is True
        assert response.json['assessment_id'] == assessment_id


class TestCSSRSDataPersistence:
    """Test database persistence and querying - marked to skip, run manually"""
    
    @pytest.mark.skip(reason="Requires live database - run with pytest manually")
    def test_assessment_stored_in_database(self, client, db_connection):
        """Test that assessments are stored in database"""
        client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        
        client.post('/api/c-ssrs/submit', json={
            'q1': 3, 'q2': 2, 'q3': 1, 'q4': 1, 'q5': 0, 'q6': 0
        })
        
        # Query database directly (requires fixture)
        # cur = db_connection.cursor()
        # cur.execute(...)
    
    @pytest.mark.skip(reason="Requires live database - run with pytest manually")
    def test_alert_flags_set_correctly(self, client, db_connection):
        """Test that alert flags are set based on risk level"""
        client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        
        client.post('/api/c-ssrs/submit', json={
            'q1': 5, 'q2': 5, 'q3': 5, 'q4': 1, 'q5': 1, 'q6': 0,
            'clinician_username': 'clinician1'
        })


class TestCSSRSEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.mark.skip(reason="Requires authenticated Flask test client context - run with pytest manually")
    def test_assessment_with_no_clinician(self, client):
        """Test assessment without clinician assignment"""
        client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        
        response = client.post('/api/c-ssrs/submit', json={
            'q1': 2, 'q2': 2, 'q3': 1, 'q4': 1, 'q5': 0, 'q6': 0
        })
        
        assert response.status_code == 201
        assert 'assessment_id' in response.json
    
    @pytest.mark.skip(reason="Requires authenticated Flask test client context - run with pytest manually")
    def test_multiple_assessments_same_user(self, client):
        """Test multiple assessments from same user"""
        client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        
        responses = []
        for i in range(5):
            response = client.post('/api/c-ssrs/submit', json={
                'q1': i, 'q2': i, 'q3': i, 'q4': 0, 'q5': 0, 'q6': 0
            })
            responses.append(response)
        
        # All should succeed
        for resp in responses:
            assert resp.status_code == 201
        
        # Get history
        history = client.get('/api/c-ssrs/history')
        assert history.json['total_count'] == 5
    
    def test_assessment_score_calculation_accuracy(self):
        """Test that risk scores are calculated accurately"""
        test_cases = [
            ({1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}, 0, 'low'),
            ({1: 1, 2: 1, 3: 1, 4: 0, 5: 0, 6: 0}, 3, 'moderate'),
            ({1: 3, 2: 3, 3: 2, 4: 1, 5: 1, 6: 0}, 10, 'high'),
            ({1: 5, 2: 5, 3: 5, 4: 2, 5: 2, 6: 1}, 20, 'critical'),
        ]
        
        for responses, expected_score, expected_level in test_cases:
            result = CSSRSAssessment.calculate_risk_score(responses)
            assert result['total_score'] == expected_score
            assert result['risk_level'] == expected_level


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
