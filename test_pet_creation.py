#!/usr/bin/env python3
"""
Simple pet creation test script
Usage: python test_pet_creation.py
"""
import requests
import json
import sys

# Test configuration
API_URL = "http://localhost:5000"  # Change if your API is hosted elsewhere
TEST_USERNAME = "testuser123"
TEST_PET_NAME = "Fluffy"

def test_pet_creation():
    """Test creating a pet"""
    print(f"🧪 Testing pet creation for user: {TEST_USERNAME}")
    print(f"📍 API URL: {API_URL}")
    
    # Step 1: Create/register user account first
    print("\n1️⃣ Creating user account...")
    try:
        response = requests.post(f"{API_URL}/api/register", json={
            'username': TEST_USERNAME,
            'email': f'{TEST_USERNAME}@test.com',
            'password': 'Test123!@#'
        }, timeout=5)
        if response.status_code == 201:
            print(f"   ✓ User created: {response.json()}")
        elif response.status_code == 409:
            print(f"   ℹ️ User already exists: {response.json()}")
        else:
            print(f"   ✗ Failed to create user: {response.status_code} {response.json()}")
            return False
    except Exception as e:
        print(f"   ✗ Error creating user: {e}")
        return False
    
    # Step 2: Login to get session
    print("\n2️⃣ Logging in...")
    try:
        response = requests.post(f"{API_URL}/api/login", json={
            'username': TEST_USERNAME,
            'password': 'Test123!@#'
        }, timeout=5)
        if response.status_code == 200:
            print(f"   ✓ Logged in successfully")
        else:
            print(f"   ✗ Login failed: {response.status_code} {response.json()}")
            return False
    except Exception as e:
        print(f"   ✗ Error logging in: {e}")
        return False
    
    # Step 3: Create pet
    print("\n3️⃣ Creating pet...")
    try:
        response = requests.post(f"{API_URL}/api/pet/create", json={
            'username': TEST_USERNAME,
            'name': TEST_PET_NAME,
            'species': 'Dog',
            'gender': 'Male'
        }, timeout=5)
        if response.status_code == 201:
            print(f"   ✓ Pet created: {response.json()}")
        else:
            print(f"   ✗ Failed to create pet: {response.status_code}")
            print(f"      Response: {response.json()}")
            return False
    except Exception as e:
        print(f"   ✗ Error creating pet: {e}")
        return False
    
    # Step 4: Get pet status
    print("\n4️⃣ Checking pet status...")
    try:
        response = requests.get(f"{API_URL}/api/pet/status", 
                              params={'username': TEST_USERNAME}, 
                              timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('exists'):
                print(f"   ✓ Pet found: {data['pet']}")
                return True
            else:
                print(f"   ✗ Pet not found in database!")
                print(f"      Response: {data}")
                return False
        else:
            print(f"   ✗ Failed to get pet status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error getting pet status: {e}")
        return False

if __name__ == '__main__':
    success = test_pet_creation()
    print("\n" + "="*50)
    if success:
        print("✅ Pet creation test PASSED!")
        sys.exit(0)
    else:
        print("❌ Pet creation test FAILED!")
        print("\nPlease check:")
        print("1. Is the API server running? (python3 api.py)")
        print("2. Is PostgreSQL running?")
        print("3. Check the server logs for [PET CREATE] messages")
        sys.exit(1)
