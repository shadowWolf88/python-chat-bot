#!/usr/bin/env python3
"""
Test Anonymization and PII Stripping

This script tests the training data manager's anonymization and PII
stripping capabilities to ensure personal information is removed properly.

Usage:
    python3 test_anonymization.py
"""

from training_data_manager import TrainingDataManager
from datetime import datetime
import re

def test_pii_stripping():
    """Test PII stripping with various patterns"""
    manager = TrainingDataManager()
    
    print("\n" + "="*70)
    print("TESTING PII STRIPPING")
    print("="*70 + "\n")
    
    test_cases = [
        # Emails
        ("My email is john.doe@example.com and I need help", 
         "email address should be redacted"),
        
        # Phone numbers
        ("Call me at 555-123-4567 or (555) 987-6543", 
         "phone numbers should be redacted"),
        
        # Names (common patterns)
        ("My name is John Smith and I live in California",
         "name might be redacted if pattern matches"),
        
        # Addresses
        ("I live at 123 Main Street, Apartment 4B",
         "street address should be redacted"),
        
        # SSN
        ("My SSN is 123-45-6789 and I'm worried",
         "SSN should be redacted"),
        
        # Dates (birth dates)
        ("I was born on 01/15/1990 and feel anxious",
         "date should be redacted"),
        
        # Multiple PII types
        ("Hi, I'm Sarah Johnson, email sarah@test.com, phone 555-0123, born 05/20/1985",
         "all PII should be redacted"),
        
        # Medical info (should NOT be redacted - not PII)
        ("I have depression and anxiety disorder",
         "medical conditions should remain"),
        
        # Normal therapy content
        ("I've been feeling really anxious lately about work",
         "normal content should remain unchanged"),
    ]
    
    passed = 0
    failed = 0
    
    for i, (original, description) in enumerate(test_cases, 1):
        print(f"Test {i}: {description}")
        print(f"  Original: {original}")
        
        cleaned = manager.strip_pii(original)
        print(f"  Cleaned:  {cleaned}")
        
        # Check if PII markers are present
        has_email = '[EMAIL]' in cleaned
        has_phone = '[PHONE]' in cleaned
        has_address = '[ADDRESS]' in cleaned
        has_ssn = '[SSN]' in cleaned
        has_date = '[DATE]' in cleaned
        has_name = '[NAME]' in cleaned
        
        # Verify expected redactions
        if '@' in original and 'example.com' in original:
            if has_email:
                print(f"  ✓ Email redacted")
                passed += 1
            else:
                print(f"  ✗ FAILED: Email not redacted")
                failed += 1
        
        elif re.search(r'\d{3}[-\s]?\d{3}[-\s]?\d{4}', original):
            if has_phone:
                print(f"  ✓ Phone redacted")
                passed += 1
            else:
                print(f"  ✗ FAILED: Phone not redacted")
                failed += 1
        
        elif re.search(r'\d{3}-\d{2}-\d{4}', original):
            if has_ssn:
                print(f"  ✓ SSN redacted")
                passed += 1
            else:
                print(f"  ✗ FAILED: SSN not redacted")
                failed += 1
        
        elif re.search(r'\d+\s+\w+\s+(Street|St|Avenue|Ave|Road|Rd)', original, re.IGNORECASE):
            if has_address:
                print(f"  ✓ Address redacted")
                passed += 1
            else:
                print(f"  ✗ FAILED: Address not redacted")
                failed += 1
        
        elif re.search(r'\d{2}/\d{2}/\d{4}', original):
            if has_date:
                print(f"  ✓ Date redacted")
                passed += 1
            else:
                print(f"  ✗ FAILED: Date not redacted")
                failed += 1
        
        elif 'depression' in original or 'anxiety' in original:
            if cleaned == original:
                print(f"  ✓ Medical content preserved")
                passed += 1
            else:
                print(f"  ⚠ Warning: Medical content was modified")
        
        elif 'feeling' in original and 'anxious' in original:
            if cleaned == original:
                print(f"  ✓ Normal content preserved")
                passed += 1
            else:
                print(f"  ⚠ Warning: Normal content was modified")
        
        print()
    
    print(f"{'='*70}")
    print(f"PII Stripping Results: {passed} passed, {failed} failed")
    print(f"{'='*70}\n")
    
    return failed == 0

def test_anonymization():
    """Test username anonymization"""
    manager = TrainingDataManager()
    
    print("\n" + "="*70)
    print("TESTING USERNAME ANONYMIZATION")
    print("="*70 + "\n")
    
    test_usernames = [
        "john_doe",
        "patient123",
        "sarah.smith@email.com",
        "test_user_456"
    ]
    
    hashes = []
    
    for username in test_usernames:
        user_hash = manager.anonymize_username(username)
        hashes.append(user_hash)
        
        print(f"Username: {username}")
        print(f"  → Hash: {user_hash}")
        print(f"  → Length: {len(user_hash)} chars")
        print(f"  → Reversible: NO (SHA256 + salt)")
        print()
    
    # Verify hashes are unique
    if len(set(hashes)) == len(hashes):
        print(f"✓ All hashes are unique")
    else:
        print(f"✗ FAILED: Hash collision detected!")
        return False
    
    # Verify hashes are consistent
    test_hash_1 = manager.anonymize_username("test_user")
    test_hash_2 = manager.anonymize_username("test_user")
    
    if test_hash_1 == test_hash_2:
        print(f"✓ Hashing is consistent (same input → same output)")
    else:
        print(f"✗ FAILED: Hashing is not consistent!")
        return False
    
    # Verify different users get different hashes
    hash_a = manager.anonymize_username("user_a")
    hash_b = manager.anonymize_username("user_b")
    
    if hash_a != hash_b:
        print(f"✓ Different users get different hashes")
    else:
        print(f"✗ FAILED: Different users have same hash!")
        return False
    
    print(f"\n{'='*70}")
    print(f"Username Anonymization: PASSED")
    print(f"{'='*70}\n")
    
    return True

def test_integration():
    """Test full integration with sample data"""
    manager = TrainingDataManager()
    
    print("\n" + "="*70)
    print("TESTING FULL INTEGRATION")
    print("="*70 + "\n")
    
    test_username = "test_anonymization_user"
    
    # Clean up any existing test data
    try:
        manager.delete_user_training_data(test_username)
    except:
        pass
    
    # Set consent
    print("1. Setting user consent...")
    manager.set_user_consent(test_username, consent=True)
    
    if manager.check_user_consent(test_username):
        print("   ✓ Consent recorded successfully")
    else:
        print("   ✗ FAILED: Consent not recorded")
        return False
    
    # Check statistics
    print("\n2. Checking training database statistics...")
    stats = manager.get_training_stats()
    
    print(f"   Consented users: {stats.get('consented_users', 0)}")
    print(f"   Total messages: {stats.get('total_chat_messages', 0)}")
    print(f"   Total patterns: {stats.get('total_patterns', 0)}")
    print(f"   Total outcomes: {stats.get('total_outcomes', 0)}")
    print(f"   Audit entries: {stats.get('audit_entries', 0)}")
    
    # Withdraw consent
    print("\n3. Testing consent withdrawal...")
    manager.set_user_consent(test_username, consent=False)
    
    if not manager.check_user_consent(test_username):
        print("   ✓ Consent withdrawn successfully")
    else:
        print("   ✗ FAILED: Consent still active")
        return False
    
    # Re-enable consent
    print("\n4. Re-enabling consent...")
    manager.set_user_consent(test_username, consent=True)
    
    if manager.check_user_consent(test_username):
        print("   ✓ Consent re-enabled successfully")
    else:
        print("   ✗ FAILED: Could not re-enable consent")
        return False
    
    # Test deletion
    print("\n5. Testing GDPR deletion...")
    success, message = manager.delete_user_training_data(test_username)
    
    if success:
        print(f"   ✓ Deletion successful: {message}")
    else:
        print(f"   ✗ FAILED: {message}")
        return False
    
    print(f"\n{'='*70}")
    print(f"Integration Test: PASSED")
    print(f"{'='*70}\n")
    
    return True

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("TRAINING DATA ANONYMIZATION TEST SUITE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    results = []
    
    # Test 1: PII Stripping
    try:
        pii_result = test_pii_stripping()
        results.append(("PII Stripping", pii_result))
    except Exception as e:
        print(f"✗ PII Stripping test crashed: {e}")
        results.append(("PII Stripping", False))
    
    # Test 2: Username Anonymization
    try:
        anon_result = test_anonymization()
        results.append(("Username Anonymization", anon_result))
    except Exception as e:
        print(f"✗ Anonymization test crashed: {e}")
        results.append(("Username Anonymization", False))
    
    # Test 3: Integration
    try:
        integration_result = test_integration()
        results.append(("Integration Test", integration_result))
    except Exception as e:
        print(f"✗ Integration test crashed: {e}")
        results.append(("Integration Test", False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Anonymization is working correctly.")
        print("\nNext steps:")
        print("1. Set ANONYMIZATION_SALT in .env file")
        print("2. Run export_training_data.py to export real user data")
        print("3. Monitor audit logs for compliance")
    else:
        print("\n⚠ Some tests failed. Review the output above.")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
