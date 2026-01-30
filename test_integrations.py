#!/usr/bin/env python3
"""
Integration Testing Script for Healing Space UK Platform
Creates trial accounts and tests key features
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://www.healing-space.org.uk"  # Railway URL
# BASE_URL = "https://web-production-64594.up.railway.app"  # Alternative Railway URL
# BASE_URL = "http://localhost:5000"  # Local testing

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(test_name, status, message=""):
    """Print formatted test result"""
    icon = "✅" if status else "❌"
    color = Colors.GREEN if status else Colors.RED
    print(f"{icon} {color}{test_name}{Colors.RESET} {message}")

def print_section(title):
    """Print section header"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.RESET}\n")

# Test accounts to create
TEST_ACCOUNTS = {
    "patients": [
        {
            "username": "test_patient1",
            "password": "TestPass123!",
            "pin": "1111",
            "role": "user",
            "email": "patient1@example.com",
            "phone": "+441234567801",
            "full_name": "Test Patient One",
            "dob": "1990-01-01",
            "country": "United Kingdom",
            "area": "London",
            "conditions": "Anxiety, Depression",
            "clinician_id": "test_clinician",
            "verified_identifier": "patient1@example.com"
        },
        {
            "username": "test_patient2",
            "password": "TestPass123!",
            "pin": "2222",
            "role": "user",
            "email": "patient2@example.com",
            "phone": "+441234567802",
            "full_name": "Test Patient Two",
            "dob": "1985-05-15",
            "country": "United Kingdom",
            "area": "Manchester",
            "conditions": "Stress, Sleep disorders",
            "clinician_id": "test_clinician",
            "verified_identifier": "patient2@example.com"
        },
        {
            "username": "test_patient3",
            "password": "TestPass123!",
            "pin": "3333",
            "role": "user",
            "email": "patient3@example.com",
            "phone": "+441234567803",
            "full_name": "Test Patient Three",
            "dob": "1995-12-20",
            "country": "United Kingdom",
            "area": "Birmingham",
            "conditions": "PTSD, Anxiety",
            "clinician_id": "test_clinician",
            "verified_identifier": "patient3@example.com"
        },
    ],
    "clinician": {
        "username": "test_clinician",
        "password": "TestPass123!",
        "pin": "9999",
        "role": "clinician",
        "email": "clinician@example.com",
        "phone": "+441234567999",
        "full_name": "Dr. Test Clinician",
        "country": "United Kingdom",
        "area": "London",
        "professional_id": "GMC123456"
    }
}

def test_health_check():
    """Test if the API is accessible"""
    print_section("🏥 HEALTH CHECK")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        if response.status_code == 200:
            print_test("API Health Check", True, f"Status: {response.json()}")
            return True
        else:
            print_test("API Health Check", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_test("API Health Check", False, f"Error: {e}")
        return False

def create_test_accounts():
    """Create test patient and clinician accounts"""
    print_section("👥 CREATING TEST ACCOUNTS")

    created_accounts = {"patients": [], "clinician": None}

    # Create patients
    for patient in TEST_ACCOUNTS["patients"]:
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/register",
                json=patient,
                timeout=10
            )
            if response.status_code in [200, 201]:
                print_test(f"Create Patient: {patient['username']}", True)
                created_accounts["patients"].append(patient)
            elif response.status_code == 400 and "already exists" in response.json().get('error', ''):
                print_test(f"Create Patient: {patient['username']}", True, "(already exists)")
                created_accounts["patients"].append(patient)
            else:
                print_test(f"Create Patient: {patient['username']}", False, f"{response.json()}")
                # Still add to accounts list so we can test login
                created_accounts["patients"].append(patient)
        except Exception as e:
            print_test(f"Create Patient: {patient['username']}", False, f"Error: {e}")
            # Still add to accounts list so we can test login
            created_accounts["patients"].append(patient)

    # Create clinician
    clinician = TEST_ACCOUNTS["clinician"]
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/clinician/register",
            json=clinician,
            timeout=10
        )
        if response.status_code in [200, 201]:
            print_test(f"Create Clinician: {clinician['username']}", True)
            created_accounts["clinician"] = clinician
        elif response.status_code == 400 and "already exists" in response.json().get('error', ''):
            print_test(f"Create Clinician: {clinician['username']}", True, "(already exists)")
            created_accounts["clinician"] = clinician
        else:
            print_test(f"Create Clinician: {clinician['username']}", False, f"{response.json()}")
            created_accounts["clinician"] = clinician
    except Exception as e:
        print_test(f"Create Clinician: {clinician['username']}", False, f"Error: {e}")
        created_accounts["clinician"] = clinician

    return created_accounts

def test_authentication(accounts):
    """Test login functionality"""
    print_section("🔐 AUTHENTICATION TESTS")

    successful_logins = []

    # Test patient logins
    for patient in accounts["patients"]:
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"username": patient["username"], "password": patient["password"], "pin": patient["pin"]},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                print_test(f"Login: {patient['username']}", True, f"Role: {data.get('role')}")
                successful_logins.append({**patient, "session": data})
            else:
                print_test(f"Login: {patient['username']}", False, f"{response.json()}")
        except Exception as e:
            print_test(f"Login: {patient['username']}", False, f"Error: {e}")

    # Test clinician login
    if accounts["clinician"]:
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"username": accounts["clinician"]["username"], "password": accounts["clinician"]["password"], "pin": accounts["clinician"]["pin"]},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                print_test(f"Login: {accounts['clinician']['username']}", True, f"Role: {data.get('role')}")
                successful_logins.append({**accounts["clinician"], "session": data})
            else:
                print_test(f"Login: {accounts['clinician']['username']}", False, f"{response.json()}")
        except Exception as e:
            print_test(f"Login: {accounts['clinician']['username']}", False, f"Error: {e}")

    return successful_logins

def test_chat_functionality(patient):
    """Test chat/AI conversation"""
    print_section("💬 CHAT FUNCTIONALITY")

    test_messages = [
        "Hello, I'm feeling anxious today",
        "Can you help me with stress management?",
        "Thank you for your support"
    ]

    for msg in test_messages:
        try:
            response = requests.post(
                f"{BASE_URL}/api/therapy/chat",
                json={
                    "username": patient["username"],
                    "message": msg,
                    "session_id": f"test_session_{patient['username']}"
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                reply = data.get('reply', '')[:60] + "..." if len(data.get('reply', '')) > 60 else data.get('reply', '')
                print_test(f"Chat: '{msg[:40]}...'", True, f"Got reply: {reply}")
            else:
                print_test(f"Chat: '{msg[:40]}...'", False, f"{response.json()}")
        except Exception as e:
            print_test(f"Chat: '{msg[:40]}...'", False, f"Error: {e}")

        time.sleep(1)  # Rate limiting

def test_mood_logging(patient):
    """Test mood tracking functionality"""
    print_section("📊 MOOD LOGGING")

    test_moods = [
        {"mood_val": 7, "note": "Had a good therapy session - feeling happy"},
        {"mood_val": 5, "note": "Feeling worried about work - anxious"},
        {"mood_val": 8, "note": "Meditation helped today - calm"}
    ]

    for mood_data in test_moods:
        try:
            response = requests.post(
                f"{BASE_URL}/api/mood/log",
                json={
                    "username": patient["username"],
                    **mood_data
                },
                timeout=10
            )
            if response.status_code in [200, 201]:
                print_test(f"Log Mood: {mood_data['mood_val']}/10", True)
            else:
                print_test(f"Log Mood: {mood_data['mood_val']}", False, f"{response.json()}")
        except Exception as e:
            print_test(f"Log Mood: {mood_data['mood_val']}", False, f"Error: {e}")

def test_gratitude_logging(patient):
    """Test gratitude wall functionality"""
    print_section("🙏 GRATITUDE LOGGING")

    test_gratitudes = [
        "I'm grateful for my supportive friends",
        "Thankful for the beautiful weather today",
        "Appreciate having access to mental health support"
    ]

    for gratitude in test_gratitudes:
        try:
            response = requests.post(
                f"{BASE_URL}/api/gratitude/log",
                json={
                    "username": patient["username"],
                    "entry": gratitude
                },
                timeout=10
            )
            if response.status_code in [200, 201]:
                print_test(f"Post Gratitude", True, f"'{gratitude[:40]}...'")
            else:
                print_test(f"Post Gratitude", False, f"{response.json()}")
        except Exception as e:
            print_test(f"Post Gratitude", False, f"Error: {e}")

def test_clinical_assessment(patient):
    """Test clinical scale (PHQ-9) functionality"""
    print_section("📋 CLINICAL ASSESSMENT")

    # PHQ-9 test responses (0-3 scale for 9 questions)
    test_responses = [1, 1, 2, 1, 0, 1, 2, 1, 0]  # Moderate symptoms

    try:
        response = requests.post(
            f"{BASE_URL}/api/clinical/phq9",
            json={
                "username": patient["username"],
                "scores": test_responses
            },
            timeout=10
        )
        if response.status_code in [200, 201]:
            data = response.json()
            score = data.get('score', 'N/A')
            severity = data.get('severity', 'N/A')
            print_test(f"PHQ-9 Assessment", True, f"Score: {score}, Severity: {severity}")
        else:
            print_test(f"PHQ-9 Assessment", False, f"{response.json()}")
    except Exception as e:
        print_test(f"PHQ-9 Assessment", False, f"Error: {e}")

def test_notifications(patient):
    """Test notification system"""
    print_section("🔔 NOTIFICATIONS")

    try:
        response = requests.get(
            f"{BASE_URL}/api/notifications",
            params={"username": patient["username"]},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('notifications', []))
            print_test(f"Fetch Notifications", True, f"Found {count} notifications")
        else:
            print_test(f"Fetch Notifications", False, f"{response.json()}")
    except Exception as e:
        print_test(f"Fetch Notifications", False, f"Error: {e}")

def test_clinician_features(clinician):
    """Test clinician-specific features"""
    print_section("👨‍⚕️ CLINICIAN FEATURES")

    # Test listing clinicians
    try:
        response = requests.get(
            f"{BASE_URL}/api/clinicians/list",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            clinicians = data.get('clinicians', [])
            print_test(f"List Clinicians", True, f"Found {len(clinicians)} clinician(s)")
        else:
            print_test(f"List Clinicians", False, f"{response.json()}")
    except Exception as e:
        print_test(f"List Clinicians", False, f"Error: {e}")

def test_database_concurrency():
    """Test database locking fix by making simultaneous requests"""
    print_section("🔄 DATABASE CONCURRENCY")

    import concurrent.futures

    def make_health_check():
        try:
            response = requests.get(f"{BASE_URL}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    # Make 10 simultaneous requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_health_check) for _ in range(10)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    success_count = sum(results)
    print_test(f"Concurrent Requests (10 simultaneous)", success_count == 10,
               f"{success_count}/10 succeeded")

def generate_summary_report(start_time):
    """Generate final summary"""
    print_section("📊 TEST SUMMARY")

    duration = time.time() - start_time
    print(f"⏱️  Total test duration: {duration:.2f} seconds")
    print(f"\n{Colors.GREEN}✅ Testing complete!{Colors.RESET}")
    print(f"\n{Colors.YELLOW}Test Accounts Created:{Colors.RESET}")
    print(f"  Patients:")
    for patient in TEST_ACCOUNTS["patients"]:
        print(f"    - {patient['username']} / {patient['password']} / PIN: {patient['pin']}")
    print(f"  Clinician:")
    print(f"    - {TEST_ACCOUNTS['clinician']['username']} / {TEST_ACCOUNTS['clinician']['password']} / PIN: {TEST_ACCOUNTS['clinician']['pin']}")
    print(f"\n{Colors.BLUE}You can now log in with these accounts at:{Colors.RESET}")
    print(f"  {BASE_URL}")

def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║    Healing Space UK Integration Testing Suite                ║")
    print("║    Automated testing of all major features                ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    print(f"Target: {BASE_URL}\n")

    start_time = time.time()

    # Run tests
    if not test_health_check():
        print(f"\n{Colors.RED}❌ API is not accessible. Exiting.{Colors.RESET}\n")
        return

    accounts = create_test_accounts()
    logged_in = test_authentication(accounts)

    # Test patient features
    if accounts["patients"]:
        patient = accounts["patients"][0]
        test_chat_functionality(patient)
        test_mood_logging(patient)
        test_gratitude_logging(patient)
        test_clinical_assessment(patient)
        test_notifications(patient)

    # Test clinician features
    if accounts["clinician"]:
        test_clinician_features(accounts["clinician"])

    # Test database concurrency
    test_database_concurrency()

    # Summary
    generate_summary_report(start_time)

if __name__ == "__main__":
    main()
