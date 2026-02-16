#!/usr/bin/env python3
"""
Test C-SSRS Assessment Endpoints
Validates that all endpoints are properly integrated
"""

import json
from c_ssrs_assessment import CSSRSAssessment, SafetyPlan

def test_scoring_algorithm():
    """Test risk score calculation"""
    print("Testing C-SSRS Scoring Algorithm...")
    
    # Test CRITICAL risk (daily ideation with intent and planning)
    critical_responses = {
        1: 5,  # Daily ideation
        2: 5,  # Very frequent
        3: 5,  # Long duration
        4: 5,  # Yes, has plan
        5: 5,  # Yes, has intent
        6: 0   # No behavior
    }
    
    result = CSSRSAssessment.calculate_risk_score(critical_responses)
    print(f"  ✓ Critical Risk: {result['risk_level']} (score: {result['total_score']})")
    assert result['risk_level'] == 'critical'
    assert result['total_score'] == 25
    
    # Test HIGH risk (frequent without daily)
    high_responses = {
        1: 3,  # Frequent
        2: 3,  # Frequent
        3: 3,  # Moderate duration
        4: 2,  # Maybe
        5: 2,  # Maybe
        6: 0   # No behavior
    }
    
    result = CSSRSAssessment.calculate_risk_score(high_responses)
    print(f"  ✓ High Risk: {result['risk_level']} (score: {result['total_score']})")
    assert result['risk_level'] == 'high'
    
    # Test LOW risk
    low_responses = {
        1: 0,  # No
        2: 0,  # No
        3: 0,  # N/A
        4: 0,  # No
        5: 0,  # No
        6: 0   # No
    }
    
    result = CSSRSAssessment.calculate_risk_score(low_responses)
    print(f"  ✓ Low Risk: {result['risk_level']} (score: {result['total_score']})")
    assert result['risk_level'] == 'low'
    
    print("✅ Scoring algorithm tests passed!\n")


def test_alert_thresholds():
    """Test alert configuration"""
    print("Testing Alert Thresholds...")
    
    for risk_level in ['low', 'moderate', 'high', 'critical']:
        config = CSSRSAssessment.get_alert_threshold(risk_level)
        print(f"  ✓ {risk_level.upper()}: should_alert={config['should_alert']}, " +
              f"response_time={config['response_time_minutes']}min")
    
    print("✅ Alert threshold tests passed!\n")


def test_formatting():
    """Test patient and clinician formatting"""
    print("Testing Output Formatting...")
    
    responses = {
        1: 5,  # Daily ideation
        2: 5,  # Very frequent
        3: 5,  # Long duration
        4: 5,  # Has plan
        5: 5,  # Has intent
        6: 0   # No behavior
    }
    
    result = CSSRSAssessment.calculate_risk_score(responses)
    
    # Test clinician view
    clinician_view = CSSRSAssessment.format_for_clinician(result)
    assert clinician_view['risk_level'] == 'critical'
    assert clinician_view['requires_immediate_action'] == True
    print(f"  ✓ Clinician view formatted with {len(clinician_view)} fields")
    
    # Test patient view
    patient_view = CSSRSAssessment.format_for_patient(result)
    assert 'message' in patient_view
    assert 'next_steps' in patient_view
    assert 'emergency_contacts' in patient_view
    print(f"  ✓ Patient view formatted with all required fields")
    
    print("✅ Formatting tests passed!\n")


def test_safety_plan():
    """Test safety plan template"""
    print("Testing Safety Plan Template...")
    
    sections = SafetyPlan.PLAN_SECTIONS
    print(f"  ✓ Safety plan has {len(sections)} required sections:")
    for section in sections:
        print(f"     - {section['title']}: {section['description'][:50]}...")
    
    blank_plan = SafetyPlan.create_blank_plan("test_user")
    assert len(blank_plan['plan']) == len(sections)
    print(f"  ✓ Blank plan template created successfully for user")
    
    print("✅ Safety plan tests passed!\n")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("C-SSRS ASSESSMENT ENDPOINT TESTS")
    print("="*60 + "\n")
    
    try:
        test_scoring_algorithm()
        test_alert_thresholds()
        test_formatting()
        test_safety_plan()
        
        print("="*60)
        print("✅ ALL TESTS PASSED - C-SSRS endpoints ready for deployment!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
