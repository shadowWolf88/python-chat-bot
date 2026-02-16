#!/usr/bin/env python3
"""
Test script to verify /api/insights endpoint works with proper authentication.
Run this after starting the Flask server to confirm the fix works.
"""

import requests
import json
import sys
from urllib.parse import quote

BASE_URL = "http://localhost:5000"
SESSION = requests.Session()

def test_authentication_check():
    """Test that unauthenticated requests are rejected"""
    print("\n🔍 Test 1: Unauthenticated request should fail")
    
    # Try to access insights without being logged in
    url = f"{BASE_URL}/api/insights?username=testpatient&prompt=test&role=patient"
    response = requests.get(url)
    
    if response.status_code == 401:
        print("✅ PASS: Unauthenticated request correctly rejected with 401")
        return True
    else:
        print(f"❌ FAIL: Expected 401, got {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_patient_own_data():
    """Test that patient can view their own insights"""
    print("\n🔍 Test 2: Authenticated patient viewing own insights")
    
    # First, login as patient
    login_data = {
        'username': 'testpatient',
        'password': 'password123',
        'pin': '1234'
    }
    
    # Try to login
    response = SESSION.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        print("   ✓ Login successful")
        
        # Now try to get insights
        prompt = quote("Generate a summary")
        url = f"{BASE_URL}/api/insights?username=testpatient&prompt={prompt}&role=patient"
        
        response = SESSION.get(url)
        
        if response.status_code in [200, 400]:  # 200 for success, 400 if no data
            print(f"✅ PASS: Patient can access own insights (status: {response.status_code})")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response keys: {list(data.keys())}")
            return True
        else:
            print(f"❌ FAIL: Expected 200 or 400, got {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    else:
        print(f"❌ SKIP: Could not login (no test user)")
        return None

def test_patient_other_data():
    """Test that patient cannot view other patient's data"""
    print("\n🔍 Test 3: Patient viewing other patient's data should fail")
    
    # Session should still have the testpatient login
    prompt = quote("Generate a summary")
    url = f"{BASE_URL}/api/insights?username=otherpatient&prompt={prompt}&role=patient"
    
    response = SESSION.get(url)
    
    if response.status_code == 403:
        print("✅ PASS: Patient correctly denied access to other patient's data (403)")
        return True
    elif response.status_code == 401:
        print("⚠️  SKIP: Not authenticated (no session)")
        return None
    else:
        print(f"❌ FAIL: Expected 403 or 401, got {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def main():
    print("=" * 60)
    print("Testing /api/insights Authentication Fix")
    print("=" * 60)
    
    print("\n📋 Assuming Flask server is running on http://localhost:5000")
    print("   Note: These tests check authentication, not functionality")
    
    results = []
    
    results.append(("Unauthenticated rejection", test_authentication_check()))
    results.append(("Patient own data access", test_patient_own_data()))
    results.append(("Patient other data denial", test_patient_other_data()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r is True)
    failed = sum(1 for _, r in results if r is False)
    skipped = sum(1 for _, r in results if r is None)
    
    for test_name, result in results:
        status = "✅ PASS" if result is True else "❌ FAIL" if result is False else "⏭️  SKIP"
        print(f"{status}: {test_name}")
    
    print("\n" + "-" * 60)
    print(f"Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 All critical tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed - check /api/insights implementation")
        return 1

if __name__ == "__main__":
    sys.exit(main())
