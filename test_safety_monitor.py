#!/usr/bin/env python3
"""
Test script for SafetyMonitor - Real-time Risk Detection
Tests all scenarios: green, amber, orange, red risks
"""

import sys
sys.path.insert(0, '/home/computer001/Documents/python chat bot')

from safety_monitor import SafetyMonitor, analyze_chat_message

def test_safety_monitor():
    monitor = SafetyMonitor()
    
    test_cases = [
        # (message, expected_risk_level, description)
        ("I'm feeling good today, thanks for asking!", "green", "Positive message"),
        ("Everything feels hopeless sometimes", "amber", "Hopelessness indicator"),
        ("I've been thinking a lot about ending it all", "orange", "Direct ideation"),
        ("I have a plan to kill myself tonight", "red", "Direct planning + imminent"),
        ("I'm not sure I want to be alive anymore", "orange", "Active suicidal ideation"),
        ("Just joking about ending things, lol", "green", "Denial/minimization"),
        ("Therapy is helping me find reasons to live", "green", "Protective factors"),
        ("I used to have suicidal thoughts but I'm better now", "amber", "Past tense"),
    ]
    
    print("=" * 70)
    print("SAFETY MONITOR TEST SUITE")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for message, expected_level, description in test_cases:
        result = analyze_chat_message(message)
        
        status = "✓ PASS" if result['risk_level'] == expected_level else "✗ FAIL"
        if result['risk_level'] == expected_level:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{status}: {description}")
        print(f"  Message: \"{message}\"")
        print(f"  Expected: {expected_level:8s} | Got: {result['risk_level']:8s}")
        print(f"  Score: {result['risk_score']:3d}/100 | Confidence: {result['confidence']:.1%}")
        if result['indicators']:
            print(f"  Indicators: {', '.join(result['indicators'])}")
        print(f"  Action Needed: {result['action_needed']} | Urgent: {result['urgent_action']}")
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 70)
    
    return failed == 0

if __name__ == '__main__':
    success = test_safety_monitor()
    sys.exit(0 if success else 1)
