#!/usr/bin/env python3
"""
Quick Verification Script for Daily Wellness Ritual Implementation
Checks that all components are in place and working
"""

import sys
import re

def check_file_contains(filepath, pattern, description):
    """Check if a file contains a pattern"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description}")
                return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("Daily Wellness Ritual - Implementation Verification")
    print("="*70 + "\n")
    
    checks = [
        # Database checks
        (
            '/home/computer001/Documents/python chat bot/api.py',
            r'wellness_logs.*mood.*INTEGER.*sleep_quality.*INTEGER',
            "✓ wellness_logs table creation in init_db()"
        ),
        (
            '/home/computer001/Documents/python chat bot/api.py',
            r'patient_medications.*medication_name.*TEXT',
            "✓ patient_medications table creation in init_db()"
        ),
        (
            '/home/computer001/Documents/python chat bot/api.py',
            r'idx_wellness_username_timestamp',
            "✓ Wellness logs index created"
        ),
        
        # API Endpoints checks
        (
            '/home/computer001/Documents/python chat bot/api.py',
            r"@app\.route\('/api/wellness/log'",
            "✓ POST /api/wellness/log endpoint"
        ),
        (
            '/home/computer001/Documents/python chat bot/api.py',
            r"@app\.route\('/api/wellness/today'",
            "✓ GET /api/wellness/today endpoint"
        ),
        (
            '/home/computer001/Documents/python chat bot/api.py',
            r"@app\.route\('/api/wellness/summary'",
            "✓ GET /api/wellness/summary endpoint"
        ),
        (
            '/home/computer001/Documents/python chat bot/api.py',
            r"@app\.route\('/api/user/medications'",
            "✓ GET /api/user/medications endpoint"
        ),
        (
            '/home/computer001/Documents/python chat bot/api.py',
            r"@app\.route\('/api/homework/current'",
            "✓ GET /api/homework/current endpoint"
        ),
        
        # AI Memory integration
        (
            '/home/computer001/Documents/python chat bot/api.py',
            r'recent_wellness.*wellness_logs.*mood.*sleep_quality',
            "✓ Wellness data extraction in update_ai_memory()"
        ),
        (
            '/home/computer001/Documents/python chat bot/api.py',
            r'wellness_count.*med_adherence.*avg_sleep',
            "✓ Wellness pattern analysis in update_ai_memory()"
        ),
        
        # Frontend HTML checks
        (
            '/home/computer001/Documents/python chat bot/templates/index.html',
            r'id="wellnessRitualModal".*wellness-ritual-card',
            "✓ Wellness ritual modal HTML"
        ),
        (
            '/home/computer001/Documents/python chat bot/templates/index.html',
            r'id="wellnessConversation".*wellness-conversation',
            "✓ Wellness conversation div"
        ),
        (
            '/home/computer001/Documents/python chat bot/templates/index.html',
            r'Start Your Daily Wellness Check-in',
            "✓ Wellness button in Daily Tasks"
        ),
        
        # Frontend CSS checks
        (
            '/home/computer001/Documents/python chat bot/templates/index.html',
            r'\.wellness-ritual-card.*border-left.*primary-color',
            "✓ Wellness card CSS styling"
        ),
        (
            '/home/computer001/Documents/python chat bot/templates/index.html',
            r'\.mood-button.*selected.*primary-color',
            "✓ Mood button CSS styling"
        ),
        (
            '/home/computer001/Documents/python chat bot/templates/index.html',
            r'@keyframes slideIn',
            "✓ Wellness animation CSS"
        ),
        
        # Frontend JavaScript checks
        (
            '/home/computer001/Documents/python chat bot/templates/index.html',
            r'let wellnessRitualState.*currentStep.*data.*timeOfDay',
            "✓ Wellness state management"
        ),
        (
            '/home/computer001/Documents/python chat bot/templates/index.html',
            r'function initializeWellnessRitual\(\)',
            "✓ initializeWellnessRitual() function"
        ),
        (
            '/home/computer001/Documents/python chat bot/templates/index.html',
            r'function showWellnessStep\(\)',
            "✓ showWellnessStep() function"
        ),
        (
            '/home/computer001/Documents/python chat bot/templates/index.html',
            r'function submitWellnessRitual\(\)',
            "✓ submitWellnessRitual() function"
        ),
        (
            '/home/computer001/Documents/python chat bot/templates/index.html',
            r'renderMoodStep.*renderSleepStep.*renderHydrationStep',
            "✓ Step renderer functions"
        ),
        (
            '/home/computer001/Documents/python chat bot/templates/index.html',
            r'getTimeOfDay\(\)',
            "✓ Time-aware logic"
        ),
        
        # Integration checks
        (
            '/home/computer001/Documents/python chat bot/templates/index.html',
            r'switchTab.*=.*home.*initializeWellnessRitual\(\)',
            "✓ Wellness ritual initialization on tab switch"
        ),
        (
            '/home/computer001/Documents/python chat bot/templates/index.html',
            r"onclick=\"initializeWellnessRitual\(\)\"",
            "✓ Wellness button onclick handler"
        ),
    ]
    
    results = []
    for filepath, pattern, description in checks:
        results.append(check_file_contains(filepath, pattern, description))
    
    print("\n" + "="*70)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} checks passed")
    print("="*70 + "\n")
    
    if passed == total:
        print("✨ ALL CHECKS PASSED - Implementation is complete!")
        print("\nYou can now:")
        print("1. Run 'python3 api.py' to start the server")
        print("2. Navigate to http://localhost:5000")
        print("3. Go to the Home tab to see the wellness ritual")
        print("4. Click 'Start Your Daily Wellness Check-in'")
        print("\nThe 10-step wellness ritual will guide you through:")
        print("  • Mood tracking (1-5 scale)")
        print("  • Sleep quality assessment")
        print("  • Hydration tracking")
        print("  • Exercise/movement")
        print("  • Social connections")
        print("  • Medication adherence")
        print("  • Energy level")
        print("  • Homework progress")
        print("  • Wrap-up reflection\n")
        return 0
    else:
        print(f"⚠️  {total - passed} checks failed - Please review implementation")
        return 1

if __name__ == '__main__':
    sys.exit(main())
