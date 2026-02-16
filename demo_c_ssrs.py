#!/usr/bin/env python3
"""
C-SSRS Assessment Demo
Shows the complete workflow from assessment start to safety planning
"""

import json
from c_ssrs_assessment import CSSRSAssessment, SafetyPlan

def demo_critical_risk_case():
    """Demo: Patient with CRITICAL suicide risk"""
    print("\n" + "="*70)
    print("DEMO SCENARIO: Patient with CRITICAL Suicide Risk")
    print("="*70)
    
    print("\n1️⃣  PATIENT STARTS ASSESSMENT")
    print("-" * 70)
    print("Questions presented to patient:")
    for q in CSSRSAssessment.QUESTIONS[:3]:  # Show first 3 questions
        print(f"   Q{q['id']}: {q['text']}")
    print("   ... (3 more questions)")
    
    print("\n2️⃣  PATIENT SUBMITS RESPONSES (High Risk)")
    print("-" * 70)
    responses = {
        1: 5,  # Daily ideation
        2: 5,  # Very frequent
        3: 5,  # Long duration
        4: 5,  # Has plan
        5: 5,  # Has intent
        6: 0   # No behavior
    }
    
    print("Patient Answers:")
    questions = CSSRSAssessment.QUESTIONS
    for qid, response_val in responses.items():
        q_text = next(q['text'] for q in questions if q['id'] == qid)
        answer = CSSRSAssessment.ANSWER_OPTIONS[response_val]
        print(f"   Q{qid}: {answer}")
    
    # Calculate risk
    result = CSSRSAssessment.calculate_risk_score(responses)
    
    print("\n3️⃣  RISK SCORE CALCULATED")
    print("-" * 70)
    print(f"Total Score: {result['total_score']}/30")
    print(f"Risk Level: {result['risk_level'].upper()}")
    print(f"Reasoning: {result['reasoning']}")
    print(f"\nRisk Factors Detected:")
    print(f"  ✓ Suicidal Planning: {result['has_planning']}")
    print(f"  ✓ Suicidal Intent: {result['has_intent']}")
    print(f"  ✓ Suicide Behavior: {result['has_behavior']}")
    
    # Check alert config
    alert_config = CSSRSAssessment.get_alert_threshold(result['risk_level'])
    
    print("\n4️⃣  ALERT SYSTEM TRIGGERED")
    print("-" * 70)
    print(f"Alert Sent: {alert_config['should_alert']}")
    print(f"Urgency: {alert_config['urgency']}")
    print(f"Response Time Required: {alert_config['response_time_minutes']} minutes")
    print(f"\nClinician Email Subject:")
    print(f"  [URGENT] Patient john_doe - C-SSRS Risk Assessment CRITICAL")
    
    print("\n5️⃣  PATIENT RECEIVES FEEDBACK")
    print("-" * 70)
    patient_view = CSSRSAssessment.format_for_patient(result)
    print(f"Patient Message: {patient_view['message']}")
    print(f"\nNext Steps:")
    for i, step in enumerate(patient_view['next_steps'], 1):
        print(f"  {i}. {step}")
    
    print("\n6️⃣  SAFETY PLANNING REQUIRED")
    print("-" * 70)
    print("Patient must complete safety plan with 6 sections:")
    for section in SafetyPlan.PLAN_SECTIONS:
        print(f"  • {section['title']}: {section['description']}")
    
    blank_plan = SafetyPlan.create_blank_plan("john_doe")
    print(f"\nSafety Plan Template Created for: {blank_plan['username']}")
    print(f"Sections to complete: {list(blank_plan['plan'].keys())}")
    
    print("\n7️⃣  CLINICIAN RECEIVES ALERT & RESPONDS")
    print("-" * 70)
    print("Clinician receives email notification")
    print("Clicks response link and selects action:")
    print("  ☐ Attempted phone contact")
    print("  ☐ Contacted emergency services")
    print("  ☑ Contacted family/emergency contact")
    print("  ☐ Documented in patient file")
    
    print("\nClinician Response Recorded:")
    print(f"  Action: emergency_contact")
    print(f"  Timestamp: 2024-02-07T14:35:00Z")
    print(f"  Response Time: 5 minutes (WITHIN 10-MINUTE WINDOW)")
    
    print("\n8️⃣  DATABASE RECORDS UPDATED")
    print("-" * 70)
    print("c_ssrs_assessments table:")
    print(f"  ✓ Assessment saved with all responses")
    print(f"  ✓ Risk level: CRITICAL")
    print(f"  ✓ Alert marked as sent")
    print(f"  ✓ Clinician response recorded")
    print(f"\nenhanced_safety_plans table:")
    print(f"  ✓ Safety plan created/updated")
    print(f"  ✓ Linked to patient username")
    print(f"\naudit_logs table:")
    print(f"  ✓ Assessment submitted: john_doe")
    print(f"  ✓ Clinician response: dr_smith")
    print(f"  ✓ Safety plan created: john_doe")
    
    print("\n" + "="*70)
    print("✅ CRITICAL RISK CASE MANAGED SUCCESSFULLY")
    print("="*70 + "\n")


def demo_moderate_risk_case():
    """Demo: Patient with MODERATE risk"""
    print("\n" + "="*70)
    print("DEMO SCENARIO: Patient with MODERATE Suicide Risk")
    print("="*70)
    
    responses = {
        1: 2,  # Infrequent
        2: 2,  # Few days/month
        3: 1,  # Brief duration
        4: 0,  # No planning
        5: 0,  # No intent
        6: 0   # No behavior
    }
    
    result = CSSRSAssessment.calculate_risk_score(responses)
    
    print(f"\nTotal Score: {result['total_score']}/30")
    print(f"Risk Level: {result['risk_level'].upper()}")
    print(f"Reasoning: {result['reasoning']}")
    
    alert_config = CSSRSAssessment.get_alert_threshold(result['risk_level'])
    print(f"\nAlert Status: {'⚠️ ALERT' if alert_config['should_alert'] else '✓ No alert'}")
    
    patient_view = CSSRSAssessment.format_for_patient(result)
    print(f"\nPatient Message: {patient_view['message']}")
    print(f"\nSafety Plan Required: {alert_config['requires_safety_plan']}")
    print(f"(Routine clinician follow-up scheduled)")
    
    print("\n✅ MODERATE RISK CASE - Routine Management\n")


def demo_low_risk_case():
    """Demo: Patient with LOW risk"""
    print("\n" + "="*70)
    print("DEMO SCENARIO: Patient with LOW Suicide Risk")
    print("="*70)
    
    responses = {
        1: 0,  # No
        2: 0,  # N/A
        3: 0,  # N/A
        4: 0,  # No
        5: 0,  # No
        6: 0   # No
    }
    
    result = CSSRSAssessment.calculate_risk_score(responses)
    
    print(f"\nTotal Score: {result['total_score']}/30")
    print(f"Risk Level: {result['risk_level'].upper()}")
    print(f"Reasoning: {result['reasoning']}")
    
    alert_config = CSSRSAssessment.get_alert_threshold(result['risk_level'])
    print(f"\nAlert Status: {'⚠️ ALERT' if alert_config['should_alert'] else '✓ No alert'}")
    
    patient_view = CSSRSAssessment.format_for_patient(result)
    print(f"\nPatient Message: {patient_view['message']}")
    print(f"\nSafety Plan Required: {alert_config['requires_safety_plan']}")
    print(f"(Standard therapeutic care continues)")
    
    print("\n✅ LOW RISK CASE - Standard Care\n")


def print_system_summary():
    """Print technical system summary"""
    print("\n" + "="*70)
    print("C-SSRS SYSTEM SUMMARY")
    print("="*70)
    
    print(f"\n📊 Assessment Module:")
    print(f"   • Questions: {len(CSSRSAssessment.QUESTIONS)}")
    print(f"   • Answer scale: 0-5 per question")
    print(f"   • Max total score: {sum([5 for _ in range(6)])}")
    print(f"   • Risk levels: 4 (LOW, MODERATE, HIGH, CRITICAL)")
    
    print(f"\n🚨 Alert Configuration:")
    for level in ['low', 'moderate', 'high', 'critical']:
        config = CSSRSAssessment.get_alert_threshold(level)
        print(f"   • {level.upper()}: Alert={config['should_alert']}, " +
              f"Response={config['response_time_minutes']}min" if config['response_time_minutes'] else "N/A")
    
    print(f"\n📋 Safety Planning:")
    print(f"   • Sections: {len(SafetyPlan.PLAN_SECTIONS)}")
    for section in SafetyPlan.PLAN_SECTIONS:
        print(f"     - {section['title']}")
    
    print(f"\n🗄️ Database Tables:")
    print(f"   • c_ssrs_assessments (17 columns, 4 indexes)")
    print(f"   • enhanced_safety_plans (linked to users)")
    print(f"   • audit_logs (compliance tracking)")
    
    print(f"\n🔌 API Endpoints:")
    endpoints = [
        "POST /api/c-ssrs/start",
        "POST /api/c-ssrs/submit",
        "GET /api/c-ssrs/history",
        "GET /api/c-ssrs/<id>",
        "POST /api/c-ssrs/<id>/clinician-response",
        "POST /api/c-ssrs/<id>/safety-plan"
    ]
    for ep in endpoints:
        print(f"   • {ep}")
    
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "C-SSRS ASSESSMENT SYSTEM DEMO" + " "*20 + "║")
    print("║" + " "*25 + "Healing Space UK v1.0" + " "*22 + "║")
    print("╚" + "="*68 + "╝")
    
    # System summary
    print_system_summary()
    
    # Three demo scenarios
    demo_critical_risk_case()
    demo_moderate_risk_case()
    demo_low_risk_case()
    
    # Closing
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\nKey Features Demonstrated:")
    print("  ✅ 6-question standardized assessment")
    print("  ✅ Automatic risk stratification")
    print("  ✅ Clinician alert system with response tracking")
    print("  ✅ Safety planning for high-risk patients")
    print("  ✅ Full audit trail for UK regulation compliance")
    print("\nReady for deployment to Lincoln University Psychology Department!")
    print("="*70 + "\n")
