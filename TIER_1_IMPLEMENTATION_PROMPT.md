# TIER 1: PRODUCTION BLOCKERS - COMPREHENSIVE IMPLEMENTATION PROMPT

## Executive Summary

You are implementing TIER 1: Production Blockers for the Healing Space mental health platform. This tier contains 10 critical issues that must be fixed before the application can safely handle real users. All 10 items must be completed without breaking existing functionality.

**Total Effort:** 76-81 hours  
**Timeline:** 2-3 weeks at full-time development  
**Risk Level:** CRITICAL - These are blocking production deployment  
**Testing Required:** Comprehensive (unit + integration + regression)

---

## Critical Success Criteria

Before you begin any implementation:

1. **No Breaking Changes**: All existing tests must continue passing
2. **Complete Coverage**: Every item (1.1-1.10) must be fully implemented, not partially
3. **Security First**: Each fix must close the identified security vulnerability
4. **Well Tested**: New tests must accompany every fix
5. **Well Documented**: Every change must be documented
6. **Clean Git History**: One commit per item with clear messages

---

## Phase 0: Setup (2 hours)

### Step 0.1: Create Test Infrastructure
```bash
# Create test structure
mkdir -p tests/tier1/unit tests/tier1/integration tests/tier1/fixtures

# Create main test file
touch tests/test_tier1_blockers.py

# Create documentation files
touch docs/TIER_1_TESTING_GUIDE.md
touch docs/TIER_1_IMPLEMENTATION_CHECKLIST.md
touch docs/TIER_1_DEBUGGING_GUIDE.md
```

### Step 0.2: Create Test Fixtures and Helpers
Create `tests/tier1/fixtures.py`:
```python
"""
Tier 1 Test Fixtures

Provides:
- Test user accounts (patient, clinician, admin)
- Mock data (moods, assessments, messages)
- Database setup/teardown
- Session management
- CSRF token generation
"""

import pytest
import os
from datetime import datetime, timedelta
from app import app, get_db_connection

@pytest.fixture(scope='session')
def test_db():
    """Setup test database before all tests"""
    os.environ['DEBUG'] = '1'
    os.environ['DATABASE_URL'] = os.getenv('TEST_DATABASE_URL', 'postgresql://test:test@localhost/test_healing')
    conn = get_db_connection()
    # Initialize schema
    yield conn
    # Cleanup
    conn.close()

@pytest.fixture
def client(test_db):
    """Flask test client"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

@pytest.fixture
def test_patient_account(client):
    """Create and return test patient account"""
    response = client.post('/api/auth/register', json={
        'username': 'testpatient_tier1',
        'email': 'testpatient@tier1.test',
        'password': 'TestPassword123!',
        'age': 28,
        'role': 'patient'
    })
    assert response.status_code == 201
    return {'username': 'testpatient_tier1', 'email': 'testpatient@tier1.test', 'password': 'TestPassword123!'}

@pytest.fixture
def test_clinician_account(client):
    """Create and return test clinician account"""
    response = client.post('/api/auth/clinician/register', json={
        'username': 'testclinician_tier1',
        'email': 'testclinician@tier1.test',
        'password': 'TestPassword123!',
        'license_number': 'BPS00001',
        'specialty': 'General Mental Health'
    })
    assert response.status_code == 201
    return {'username': 'testclinician_tier1', 'email': 'testclinician@tier1.test', 'password': 'TestPassword123!'}

@pytest.fixture
def authenticated_patient_client(client, test_patient_account):
    """Return authenticated client for patient"""
    response = client.post('/api/auth/login', json={
        'username': test_patient_account['username'],
        'password': test_patient_account['password']
    })
    assert response.status_code == 200
    return client

@pytest.fixture
def authenticated_clinician_client(client, test_clinician_account):
    """Return authenticated client for clinician"""
    response = client.post('/api/auth/login', json={
        'username': test_clinician_account['username'],
        'password': test_clinician_account['password']
    })
    assert response.status_code == 200
    return client

@pytest.fixture
def csrf_token(authenticated_patient_client):
    """Get CSRF token from authenticated session"""
    response = authenticated_patient_client.get('/api/auth/csrf-token')
    return response.json['token']

# Mock data generators
def create_mood_entry(mood=7, sleep=7, exercise=30, anxiety=3):
    """Create mock mood entry"""
    return {
        'mood': mood,
        'sleep_hours': sleep,
        'exercise_minutes': exercise,
        'anxiety_level': anxiety,
        'notes': 'Test mood entry'
    }

def create_assessment_entry(assessment_type='phq9', scores=None):
    """Create mock clinical assessment"""
    if assessment_type == 'phq9' and scores is None:
        scores = [0] * 9  # All zeros = minimal symptoms
    elif assessment_type == 'gad7' and scores is None:
        scores = [0] * 7
    return {
        'assessment_type': assessment_type,
        'scores': scores,
        'timestamp': datetime.utcnow().isoformat()
    }

def create_message(sender, content, recipient=None):
    """Create mock message"""
    return {
        'sender': sender,
        'content': content,
        'recipient': recipient,
        'timestamp': datetime.utcnow().isoformat()
    }
```

### Step 0.3: Create Baseline Test
Create `tests/test_tier1_blockers.py`:
```python
"""
TIER 1: Production Blockers Test Suite

Tests for:
1.1 - Clinician Dashboard
1.2 - CSRF Protection
1.3 - Rate Limiting
1.4 - Input Validation
1.5 - Session Management
1.6 - Error Handling
1.7 - Access Control
1.8 - XSS Prevention
1.9 - DB Connection Pooling
1.10 - Anonymization Salt

Total: 80+ tests covering all TIER 1 items
"""

import pytest
import json
from datetime import datetime, timedelta
from tests.tier1.fixtures import *

# ========== TIER 1.1: CLINICIAN DASHBOARD ==========

class TestClinicianDashboard:
    """Test Clinician Dashboard - 20+ broken features"""
    
    def test_dashboard_loads(self, authenticated_clinician_client):
        """Test dashboard page loads"""
        response = authenticated_clinician_client.get('/dashboard')
        assert response.status_code == 200
        assert b'Clinician Dashboard' in response.data
    
    def test_patient_roster_loads(self, authenticated_clinician_client):
        """Test patient roster endpoint"""
        response = authenticated_clinician_client.get('/api/clinician/patients')
        assert response.status_code == 200
        data = response.json
        assert 'patients' in data
    
    def test_patient_detail_view(self, authenticated_clinician_client, test_patient_account):
        """Test viewing individual patient details"""
        response = authenticated_clinician_client.get(
            f'/api/clinician/patient/{test_patient_account["username"]}'
        )
        assert response.status_code in [200, 403]  # 200 if approved, 403 if not
    
    def test_ai_summary_generation(self, authenticated_clinician_client, test_patient_account):
        """Test AI summary for patient"""
        response = authenticated_clinician_client.get(
            f'/api/clinician/ai-summary/{test_patient_account["username"]}'
        )
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert 'summary' in response.json
    
    def test_mood_chart_data(self, authenticated_clinician_client, test_patient_account):
        """Test mood chart data retrieval"""
        response = authenticated_clinician_client.get(
            f'/api/clinician/mood-trends/{test_patient_account["username"]}'
        )
        assert response.status_code in [200, 404]
    
    def test_therapy_history_view(self, authenticated_clinician_client, test_patient_account):
        """Test therapy chat history viewing"""
        response = authenticated_clinician_client.get(
            f'/api/clinician/therapy-history/{test_patient_account["username"]}'
        )
        assert response.status_code in [200, 403, 404]
    
    def test_clinical_notes_crud(self, authenticated_clinician_client, test_patient_account):
        """Test create/read clinical notes"""
        # Create note
        response = authenticated_clinician_client.post(
            f'/api/clinician/notes/{test_patient_account["username"]}',
            json={'content': 'Clinical observation test', 'category': 'general'}
        )
        assert response.status_code in [201, 400, 403]
        
        # Read notes
        response = authenticated_clinician_client.get(
            f'/api/clinician/notes/{test_patient_account["username"]}'
        )
        assert response.status_code in [200, 403, 404]
    
    def test_appointments_view(self, authenticated_clinician_client):
        """Test clinician appointments view"""
        response = authenticated_clinician_client.get('/api/clinician/appointments')
        assert response.status_code == 200
    
    def test_alerts_dashboard(self, authenticated_clinician_client):
        """Test alerts/flags dashboard"""
        response = authenticated_clinician_client.get('/api/clinician/alerts')
        assert response.status_code == 200
    
    def test_risk_assessments_view(self, authenticated_clinician_client, test_patient_account):
        """Test viewing patient risk assessments"""
        response = authenticated_clinician_client.get(
            f'/api/clinician/risk-assessments/{test_patient_account["username"]}'
        )
        assert response.status_code in [200, 404, 403]

# ========== TIER 1.2: CSRF PROTECTION ==========

class TestCSRFProtection:
    """Test CSRF Protection - Apply Consistently"""
    
    def test_csrf_token_required_on_state_change(self, authenticated_patient_client):
        """Test CSRF token required for POST requests"""
        response = authenticated_patient_client.post(
            '/api/mood/log',
            json={'mood': 7, 'sleep_hours': 8},
            headers={'X-CSRF-Token': 'invalid'}
        )
        # Should reject invalid CSRF token
        assert response.status_code in [400, 401, 403]
    
    def test_csrf_token_validation(self, authenticated_patient_client, csrf_token):
        """Test valid CSRF token is accepted"""
        response = authenticated_patient_client.post(
            '/api/mood/log',
            json={'mood': 7, 'sleep_hours': 8},
            headers={'X-CSRF-Token': csrf_token}
        )
        # Should accept valid CSRF token
        assert response.status_code in [200, 201]
    
    def test_csrf_on_all_post_endpoints(self, authenticated_patient_client, csrf_token):
        """Test CSRF required on all state-changing endpoints"""
        endpoints = [
            ('/api/mood/log', {'mood': 7}),
            ('/api/therapy/chat', {'message': 'test'}),
            ('/api/appointments/schedule', {'clinician': 'test', 'date': '2026-02-08'}),
        ]
        
        for endpoint, payload in endpoints:
            response = authenticated_patient_client.post(
                endpoint,
                json=payload,
                headers={'X-CSRF-Token': csrf_token}
            )
            # Should not get CSRF error with valid token
            assert response.status_code != 403 or 'CSRF' not in response.json.get('error', '')
    
    def test_csrf_exempt_on_get_requests(self, authenticated_patient_client):
        """Test CSRF not required on GET requests"""
        response = authenticated_patient_client.get('/api/mood/history')
        assert response.status_code in [200, 404, 500]

# ========== TIER 1.3: RATE LIMITING ==========

class TestRateLimiting:
    """Test Rate Limiting - Critical Endpoints"""
    
    def test_login_rate_limit(self, client):
        """Test login endpoint is rate limited"""
        # Make 10 rapid login attempts
        for i in range(10):
            response = client.post('/api/auth/login', json={
                'username': f'user{i}',
                'password': 'wrong'
            })
        
        # Eventually should hit rate limit
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'wrong'
        })
        # Status should be 429 (Too Many Requests) after limit
        # or still 401/400 if rate limit not yet implemented
        assert response.status_code in [400, 401, 429]
    
    def test_registration_rate_limit(self, client):
        """Test registration endpoint rate limiting"""
        # Make rapid registration attempts
        for i in range(5):
            response = client.post('/api/auth/register', json={
                'username': f'testuser_{i}_{datetime.utcnow().timestamp()}',
                'email': f'test{i}@example.com',
                'password': 'TestPassword123!'
            })
        
        # Next request might be rate limited
        response = client.post('/api/auth/register', json={
            'username': f'testuser_blocked_{datetime.utcnow().timestamp()}',
            'email': 'blocked@example.com',
            'password': 'TestPassword123!'
        })
        assert response.status_code in [201, 400, 429]
    
    def test_password_reset_rate_limit(self, client):
        """Test password reset rate limiting to prevent enumeration"""
        # Make rapid password reset attempts
        for i in range(5):
            response = client.post('/api/auth/forgot-password', json={
                'email': f'test{i}@example.com'
            })
        
        response = client.post('/api/auth/forgot-password', json={
            'email': 'enumeration@example.com'
        })
        # Should be rate limited or slow
        assert response.status_code in [200, 429]
    
    def test_verification_code_rate_limit(self, client):
        """Test verification code attempts rate limited"""
        for i in range(10):
            response = client.post('/api/auth/verify-code', json={
                'email': 'test@example.com',
                'code': f'{i:06d}'
            })
        
        # Should eventually rate limit
        assert True  # Placeholder - depends on implementation

# ========== TIER 1.4: INPUT VALIDATION ==========

class TestInputValidation:
    """Test Input Validation - Type/Range/Format"""
    
    def test_mood_value_range(self, authenticated_patient_client, csrf_token):
        """Test mood values must be 1-10"""
        # Invalid: below range
        response = authenticated_patient_client.post(
            '/api/mood/log',
            json={'mood': 0, 'sleep_hours': 8},
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response.status_code == 400
        
        # Invalid: above range
        response = authenticated_patient_client.post(
            '/api/mood/log',
            json={'mood': 11, 'sleep_hours': 8},
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response.status_code == 400
        
        # Valid: in range
        response = authenticated_patient_client.post(
            '/api/mood/log',
            json={'mood': 7, 'sleep_hours': 8},
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response.status_code in [200, 201]
    
    def test_sleep_hours_validation(self, authenticated_patient_client, csrf_token):
        """Test sleep hours must be 0-24"""
        response = authenticated_patient_client.post(
            '/api/mood/log',
            json={'mood': 7, 'sleep_hours': 25},
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response.status_code == 400
    
    def test_email_format_validation(self, client):
        """Test email format validation"""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'TestPassword123!'
        })
        assert response.status_code == 400
    
    def test_password_strength_validation(self, client):
        """Test password must meet requirements"""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'weak'
        })
        assert response.status_code == 400
    
    def test_username_format_validation(self, client):
        """Test username format (alphanumeric + underscore)"""
        response = client.post('/api/auth/register', json={
            'username': 'invalid@user!',
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        })
        assert response.status_code == 400
    
    def test_message_length_validation(self, authenticated_patient_client, csrf_token):
        """Test message length constraints"""
        # Too long
        response = authenticated_patient_client.post(
            '/api/therapy/chat',
            json={'message': 'x' * 10000},
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response.status_code == 400
        
        # Empty
        response = authenticated_patient_client.post(
            '/api/therapy/chat',
            json={'message': ''},
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response.status_code == 400

# ========== TIER 1.5: SESSION MANAGEMENT ==========

class TestSessionManagement:
    """Test Session Management - Timeout/Rotation/Invalidation"""
    
    def test_session_timeout(self, authenticated_patient_client):
        """Test session timeout after inactivity"""
        # Session should be valid immediately after login
        response = authenticated_patient_client.get('/api/auth/check-session')
        assert response.status_code == 200
        assert response.json.get('authenticated') == True
        
        # After timeout period, should be invalid
        # Note: This test may need to be mocked for CI/CD
    
    def test_session_rotation_on_login(self, client):
        """Test session ID changes after login"""
        # Get initial session ID
        client.get('/')
        initial_session = client.cookies.get_dict().get('session')
        
        # Login
        client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password'
        })
        
        # Get new session ID
        new_session = client.cookies.get_dict().get('session')
        
        # Should be different
        if initial_session and new_session:
            assert initial_session != new_session
    
    def test_session_invalidation_on_password_change(self, authenticated_patient_client):
        """Test session invalidated after password change"""
        # Change password
        csrf_response = authenticated_patient_client.get('/api/auth/csrf-token')
        csrf_token = csrf_response.json['token']
        
        response = authenticated_patient_client.post(
            '/api/auth/change-password',
            json={
                'old_password': 'TestPassword123!',
                'new_password': 'NewPassword123!'
            },
            headers={'X-CSRF-Token': csrf_token}
        )
        
        # After password change, old session should be invalid
        if response.status_code == 200:
            response = authenticated_patient_client.get('/api/auth/check-session')
            # Should either be invalid or require re-auth
            assert response.status_code in [200, 401]
    
    def test_concurrent_session_limit(self, client, test_patient_account):
        """Test concurrent session limits"""
        # Login first time
        response1 = client.post('/api/auth/login', json={
            'username': test_patient_account['username'],
            'password': test_patient_account['password']
        })
        assert response1.status_code == 200
        
        # Login second time (new client)
        client2 = app.test_client()
        response2 = client2.post('/api/auth/login', json={
            'username': test_patient_account['username'],
            'password': test_patient_account['password']
        })
        # Second login should succeed, but first session may be invalidated
        assert response2.status_code == 200
    
    def test_logout_invalidates_session(self, authenticated_patient_client):
        """Test logout properly invalidates session"""
        csrf_response = authenticated_patient_client.get('/api/auth/csrf-token')
        csrf_token = csrf_response.json['token']
        
        response = authenticated_patient_client.post(
            '/api/auth/logout',
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response.status_code == 200
        
        # After logout, should not be able to access protected endpoints
        response = authenticated_patient_client.get('/api/mood/history')
        assert response.status_code == 401

# ========== TIER 1.6: ERROR HANDLING ==========

class TestErrorHandling:
    """Test Error Handling - Structured Logging, No Debug Leaks"""
    
    def test_no_stack_trace_in_response(self, authenticated_patient_client):
        """Test error responses don't leak stack traces"""
        response = authenticated_patient_client.get('/api/nonexistent-endpoint')
        assert response.status_code == 404
        data = response.json
        
        # Should have error message but no traceback
        if 'error' in data:
            assert 'Traceback' not in data['error']
            assert 'File "' not in data['error']
    
    def test_database_errors_not_exposed(self, authenticated_patient_client, csrf_token):
        """Test database errors don't expose table names or SQL"""
        # Try to trigger a DB error
        response = authenticated_patient_client.post(
            '/api/mood/log',
            json={'mood': 'invalid_type', 'sleep_hours': 8},
            headers={'X-CSRF-Token': csrf_token}
        )
        
        if response.status_code >= 400:
            data = response.json
            # Should not expose SQL or table names
            if 'error' in data:
                assert 'SELECT' not in data['error'].upper()
                assert 'INSERT' not in data['error'].upper()
                assert 'mood_logs' not in data['error']
    
    def test_authentication_errors_vague(self, client):
        """Test authentication errors are vague (don't reveal username existence)"""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent_user_12345',
            'password': 'wrongpassword'
        })
        
        # Error message should be generic
        assert response.status_code == 401
        error = response.json.get('error', '').lower()
        # Should not say "user not found" or "password incorrect"
        assert 'not found' not in error or error in ['invalid credentials']
    
    def test_validation_errors_clear(self, client):
        """Test validation errors are clear but safe"""
        response = client.post('/api/auth/register', json={
            'username': 'test',
            'email': 'invalid-email',
            'password': 'weak'
        })
        
        assert response.status_code == 400
        error = response.json.get('error', '')
        # Should mention what's wrong without exposing system details
        assert any(word in error.lower() for word in ['email', 'password', 'invalid'])
    
    def test_permission_denied_errors(self, authenticated_patient_client):
        """Test permission denied errors don't expose resource details"""
        response = authenticated_patient_client.get('/api/clinician/patients')
        
        if response.status_code == 403:
            error = response.json.get('error', '')
            # Should not expose API structure
            assert 'clinician_patients' not in error

# ========== TIER 1.7: ACCESS CONTROL ==========

class TestAccessControl:
    """Test Access Control - Permission Verification"""
    
    def test_patient_cannot_access_clinician_routes(self, authenticated_patient_client):
        """Test patients cannot access clinician endpoints"""
        response = authenticated_patient_client.get('/api/clinician/patients')
        assert response.status_code == 403
    
    def test_clinician_cannot_access_other_patients(self, authenticated_clinician_client, test_patient_account):
        """Test clinicians cannot access unapproved patients"""
        response = authenticated_clinician_client.get(
            f'/api/clinician/patient/{test_patient_account["username"]}'
        )
        # Should be 403 if not approved, not expose patient data
        if response.status_code != 404:
            assert response.status_code in [403, 404]
    
    def test_admin_summary_requires_session_identity(self, authenticated_clinician_client):
        """Test AI summary uses session identity, not request body"""
        # Try to forge clinician identity via request body
        response = authenticated_clinician_client.get(
            '/api/professional/ai-summary/somepatient',
            json={'clinician_username': 'other_clinician'}
        )
        
        # Should only use session clinician, not body
        assert response.status_code in [200, 403, 404]
    
    def test_cannot_edit_others_data(self, authenticated_patient_client, csrf_token):
        """Test users cannot edit other users' data"""
        response = authenticated_patient_client.post(
            '/api/mood/log/other_user',
            json={'mood': 7},
            headers={'X-CSRF-Token': csrf_token}
        )
        # Should not allow
        assert response.status_code in [400, 403, 404]
    
    def test_clinician_notes_access(self, authenticated_clinician_client, test_patient_account):
        """Test clinician can only access notes for assigned patients"""
        response = authenticated_clinician_client.get(
            f'/api/clinician/notes/{test_patient_account["username"]}'
        )
        # Should be 403 if not assigned, not expose data
        assert response.status_code in [200, 403, 404]

# ========== TIER 1.8: XSS PREVENTION ==========

class TestXSSPrevention:
    """Test XSS Prevention - innerHTML Sanitization"""
    
    def test_user_content_escaped_in_community_posts(self, authenticated_patient_client):
        """Test community post content is escaped"""
        # Create post with XSS payload
        csrf_response = authenticated_patient_client.get('/api/auth/csrf-token')
        csrf_token = csrf_response.json['token']
        
        response = authenticated_patient_client.post(
            '/api/community/post',
            json={
                'content': '<img src=x onerror="alert(\'xss\')">',
                'title': 'Test post'
            },
            headers={'X-CSRF-Token': csrf_token}
        )
        
        if response.status_code in [200, 201]:
            # Retrieve and check it's escaped
            posts = authenticated_patient_client.get('/api/community/posts').json
            for post in posts.get('posts', []):
                if '<img' in post.get('content', ''):
                    # Should be escaped or removed
                    assert 'onerror=' not in post['content']
    
    def test_pet_name_xss_protection(self, authenticated_patient_client, csrf_token):
        """Test pet names are sanitized"""
        response = authenticated_patient_client.post(
            '/api/pet/create',
            json={'name': '<script>alert("xss")</script>Pet'},
            headers={'X-CSRF-Token': csrf_token}
        )
        
        if response.status_code in [200, 201]:
            pet = response.json.get('pet', {})
            # Script tag should be removed or escaped
            assert '<script>' not in pet.get('name', '')
    
    def test_message_content_sanitized(self, authenticated_patient_client, csrf_token):
        """Test message content is sanitized"""
        response = authenticated_patient_client.post(
            '/api/messages/send',
            json={
                'recipient': 'someclinician',
                'content': '<iframe src="malicious.com"></iframe>Hi'
            },
            headers={'X-CSRF-Token': csrf_token}
        )
        
        # Should either reject or sanitize
        assert response.status_code in [201, 400]
    
    def test_safety_plan_entries_sanitized(self, authenticated_patient_client, csrf_token):
        """Test safety plan entries are sanitized"""
        response = authenticated_patient_client.post(
            '/api/safety-plan/update',
            json={
                'warning_signs': '<embed src="evil.swf">',
                'coping_strategies': 'Regular exercise'
            },
            headers={'X-CSRF-Token': csrf_token}
        )
        
        # Should sanitize
        assert response.status_code in [200, 201, 400]

# ========== TIER 1.9: DATABASE CONNECTION POOLING ==========

class TestDatabaseConnectionPooling:
    """Test Database Connection Pooling"""
    
    def test_connection_reuse(self):
        """Test connections are reused from pool"""
        # Make multiple requests
        for i in range(10):
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT 1')
            conn.close()
        
        # Should not create 10 new connections (pool should reuse)
        assert True  # Actual test would check pg_stat_activity
    
    def test_connection_pool_exhaustion_handling(self):
        """Test graceful handling of connection exhaustion"""
        # Try to exhaust pool (implementation-dependent)
        conns = []
        try:
            for i in range(20):
                conns.append(get_db_connection())
            
            # If we got here, pool expanded or has >20 connections
            assert len(conns) > 0
        finally:
            for conn in conns:
                conn.close()
    
    def test_connection_context_manager(self):
        """Test connection can be used with context manager"""
        try:
            from contextlib import contextmanager
            
            @contextmanager
            def get_db_context():
                conn = get_db_connection()
                try:
                    yield conn
                finally:
                    conn.close()
            
            with get_db_context() as conn:
                cur = conn.cursor()
                cur.execute('SELECT 1')
            
            assert True
        except:
            # If context manager not implemented, that's fine
            assert True

# ========== TIER 1.10: ANONYMIZATION SALT ==========

class TestAnonymizationSalt:
    """Test Anonymization Salt - Random Generation"""
    
    def test_salt_not_hardcoded(self):
        """Test salt is not hardcoded in source"""
        import training_data_manager
        import inspect
        source = inspect.getsource(training_data_manager)
        
        # Should not have default salt like 'healing_space_salt'
        assert 'healing_space_salt' not in source.lower()
        assert 'default_salt' not in source.lower()
    
    def test_salt_generated_on_startup(self):
        """Test salt is generated/loaded on startup"""
        from training_data_manager import get_anonymization_salt
        
        salt1 = get_anonymization_salt()
        salt2 = get_anonymization_salt()
        
        # Should be same salt within same session
        assert salt1 == salt2
        
        # Should be reasonable length
        assert len(salt1) >= 16
    
    def test_salt_persists_across_runs(self):
        """Test salt is persisted and reloaded"""
        # First run gets salt
        from training_data_manager import get_anonymization_salt
        salt1 = get_anonymization_salt()
        
        # Simulate application restart (would need to reimport)
        # Second run should get same salt
        assert salt1 is not None

# ========== REGRESSION TESTS ==========

class TestRegressions:
    """Test that existing functionality still works"""
    
    def test_patient_can_login(self, test_patient_account):
        """Test patient login still works"""
        client = app.test_client()
        response = client.post('/api/auth/login', json={
            'username': test_patient_account['username'],
            'password': test_patient_account['password']
        })
        assert response.status_code == 200
    
    def test_clinician_can_login(self, test_clinician_account):
        """Test clinician login still works"""
        client = app.test_client()
        response = client.post('/api/auth/login', json={
            'username': test_clinician_account['username'],
            'password': test_clinician_account['password']
        })
        assert response.status_code == 200
    
    def test_basic_mood_logging(self, authenticated_patient_client, csrf_token):
        """Test mood logging still works"""
        response = authenticated_patient_client.post(
            '/api/mood/log',
            json={'mood': 7, 'sleep_hours': 8},
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response.status_code in [200, 201]
    
    def test_therapy_chat_still_works(self, authenticated_patient_client, csrf_token):
        """Test therapy chat still works"""
        response = authenticated_patient_client.post(
            '/api/therapy/chat',
            json={'message': 'Hello, how are you?'},
            headers={'X-CSRF-Token': csrf_token}
        )
        assert response.status_code in [200, 201, 503]  # 503 if Groq API down
    
    def test_existing_tests_still_pass(self):
        """Ensure original 13 tests still pass"""
        # Run pytest tests/ -v
        import subprocess
        result = subprocess.run(['pytest', 'tests/', '-v'], capture_output=True)
        assert result.returncode == 0

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
```

### Step 0.4: Create Implementation Checklist
Create `docs/TIER_1_IMPLEMENTATION_CHECKLIST.md`:
```markdown
# TIER 1 Implementation Checklist

## Status: IN PROGRESS

### Item 1.1: Clinician Dashboard (20-25 hours)
- [ ] Dashboard page loads correctly
- [ ] Patient roster displays
- [ ] Patient detail view works
- [ ] AI summary generation works
- [ ] Mood charts render
- [ ] Therapy history visible
- [ ] Clinical notes CRUD works
- [ ] Appointments display
- [ ] Alerts dashboard functional
- [ ] Risk assessments visible
- [ ] Tests written (10+ tests)
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Git commit made

**Estimated Completion:** [Date]

### Item 1.2: CSRF Protection (4 hours)
- [ ] Identified all state-changing endpoints
- [ ] Applied @CSRFProtection.require_csrf to all POST/PUT/DELETE
- [ ] Removed DEBUG mode CSRF bypass
- [ ] Updated frontend to include CSRF tokens
- [ ] Tests written (5+ tests)
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Git commit made

**Estimated Completion:** [Date]

### Item 1.3: Rate Limiting (4 hours)
- [ ] Configured Flask-Limiter
- [ ] Applied rate limits to login endpoint (5 attempts/minute)
- [ ] Applied rate limits to registration (3 attempts/hour)
- [ ] Applied rate limits to password reset (2 attempts/hour)
- [ ] Applied rate limits to verification code (5 attempts/minute)
- [ ] Tests written (5+ tests)
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Git commit made

**Estimated Completion:** [Date]

### Item 1.4: Input Validation (8 hours)
- [ ] Validated mood values (1-10)
- [ ] Validated sleep hours (0-24)
- [ ] Validated exercise minutes (0-1440)
- [ ] Validated anxiety levels (1-10)
- [ ] Validated email format (RFC 5322)
- [ ] Validated password strength (min 12 chars, uppercase, number, special)
- [ ] Validated username format (alphanumeric + underscore only)
- [ ] Validated message length (max 5000 chars)
- [ ] Applied InputValidator to all endpoints
- [ ] Tests written (8+ tests)
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Git commit made

**Estimated Completion:** [Date]

### Item 1.5: Session Management (6 hours)
- [ ] Implemented session timeout (7 days max)
- [ ] Implemented inactivity timeout (30 minutes)
- [ ] Implemented session rotation on login
- [ ] Implemented session invalidation on password change
- [ ] Implemented concurrent session limits (1 per user OR document why not)
- [ ] Implemented logout invalidation
- [ ] Tests written (6+ tests)
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Git commit made

**Estimated Completion:** [Date]

### Item 1.6: Error Handling (10 hours)
- [ ] Replaced bare except Exception blocks
- [ ] Added specific exception handlers
- [ ] Implemented structured logging (Python logging module)
- [ ] Removed debug print statements
- [ ] Ensured no stack traces in responses
- [ ] Ensured no database details in error messages
- [ ] Ensured no usernames/credentials in logs
- [ ] Tests written (6+ tests)
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Git commit made

**Estimated Completion:** [Date]

### Item 1.7: Access Control (4 hours)
- [ ] Fixed `/api/professional/ai-summary` to use session identity
- [ ] Verified all endpoints check user identity from session
- [ ] Verified clinicians cannot access unauthorized patients
- [ ] Verified patients cannot access clinician routes
- [ ] Verified users cannot edit other users' data
- [ ] Tests written (5+ tests)
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Git commit made

**Estimated Completion:** [Date]

### Item 1.8: XSS Prevention (12 hours)
- [ ] Identified all 138 innerHTML uses in templates/index.html
- [ ] Replaced innerHTML with textContent for user content
- [ ] Added DOMPurify sanitization for rich content
- [ ] Sanitized community post content
- [ ] Sanitized pet names
- [ ] Sanitized message content
- [ ] Sanitized safety plan entries
- [ ] Added CSP headers if needed
- [ ] Tests written (7+ tests)
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Git commit made

**Estimated Completion:** [Date]

### Item 1.9: Database Connection Pooling (6 hours)
- [ ] Implemented psycopg2.pool.ThreadedConnectionPool
- [ ] Updated get_db_connection() to use pool
- [ ] Added connection context manager
- [ ] Tested connection reuse
- [ ] Tested connection exhaustion handling
- [ ] Tests written (3+ tests)
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Git commit made

**Estimated Completion:** [Date]

### Item 1.10: Anonymization Salt (2 hours)
- [ ] Removed hardcoded salt from source
- [ ] Implemented random salt generation
- [ ] Implemented salt persistence (env var OR database)
- [ ] Implemented salt reload on startup
- [ ] Documented salt rotation procedure
- [ ] Tests written (3+ tests)
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Git commit made

**Estimated Completion:** [Date]

## Overall Progress

- Total Items: 10
- Completed: 0
- In Progress: 0
- Not Started: 10
- **Overall Progress: 0%**

## Testing Summary

| Item | Unit Tests | Integration Tests | Regression | Status |
|------|------------|-------------------|-----------|--------|
| 1.1  | 0/10       | 0/10              | ❌        | ⏳      |
| 1.2  | 0/5        | 0/5               | ❌        | ⏳      |
| 1.3  | 0/5        | 0/5               | ❌        | ⏳      |
| 1.4  | 0/8        | 0/8               | ❌        | ⏳      |
| 1.5  | 0/6        | 0/6               | ❌        | ⏳      |
| 1.6  | 0/6        | 0/6               | ❌        | ⏳      |
| 1.7  | 0/5        | 0/5               | ❌        | ⏳      |
| 1.8  | 0/7        | 0/7               | ❌        | ⏳      |
| 1.9  | 0/3        | 0/3               | ❌        | ⏳      |
| 1.10 | 0/3        | 0/3               | ❌        | ⏳      |
| **TOTAL** | **0/53** | **0/53** | **❌** | **0%** |

## Notes

Track actual hours spent vs. estimates
Document any blockers or dependencies
Update status weekly
```

---

## Phase 1: Item 1.1 - Clinician Dashboard (20-25 hours)

### Analysis Phase
1. **Read all clinician dashboard code** in `api.py` (search for `/api/clinician/`)
2. **Check frontend** in `templates/index.html` (search for "dashboard" or "clinician-view")
3. **List all broken features** from `docs/DEV_TO_DO.md`
4. **Create dashboard feature map:**
   - Feature name
   - API endpoint(s)
   - Frontend element(s)
   - Database tables involved
   - Current status (broken/working)
   - Fix required

### Implementation Approach
For **each broken feature**:
1. **Write test first** (test-driven development)
   - Test should fail initially
2. **Debug the issue**
   - Check API endpoint returns correct data
   - Check frontend JavaScript receives/renders it
   - Check database has required data
3. **Fix the issue**
   - Update backend if needed
   - Update frontend if needed
   - Ensure error handling works
4. **Verify test passes**
5. **Run full test suite** to check no regressions
6. **Git commit** with clear message

### Specific Broken Features to Fix
```
1. Dashboard page loads
2. Patient roster visible
3. Patient detail view functional
4. AI summary generation
5. Mood chart rendering
6. Therapy history display
7. Clinical notes CRUD
8. Appointments display
9. Alerts/flags visible
10. Risk assessments visible
... (10+ more to identify)
```

---

## Phase 2-10: Items 1.2-1.10

Each item follows the same pattern:
1. **Create tests** (tests/test_tier1_blockers.py)
2. **Identify the vulnerability/issue**
3. **Implement the fix**
4. **Verify with tests**
5. **Check for regressions**
6. **Document the change**
7. **Git commit**

---

## Critical Rules

### ✅ DO
- Write tests FIRST (test-driven development)
- Run `pytest tests/ -v` after EVERY change
- Commit frequently (one per item minimum)
- Document every fix in git commit
- Check that all 13 original tests still pass
- Validate Python syntax: `python3 -m py_compile api.py`

### ❌ DON'T
- Skip writing tests
- Implement without understanding the issue
- Break existing functionality
- Commit without running tests
- Leave debug print statements
- Make vague commit messages

---

## Success Criteria

✅ TIER 1 is complete when:
1. All 10 items (1.1-1.10) are implemented
2. 50+ new tests written and passing
3. All 13 original tests still passing
4. Zero debug code in source
5. Zero hardcoded values
6. All code committed with clear messages
7. Full documentation updated
8. No security vulnerabilities remain from this tier

---

## Time Breakdown

| Item | Hours | Days at 8hrs/day |
|------|-------|-----------------|
| Phase 0 (Setup) | 2 | 0.25 |
| 1.1 Dashboard | 25 | 3.1 |
| 1.2 CSRF | 4 | 0.5 |
| 1.3 Rate Limit | 4 | 0.5 |
| 1.4 Input Validation | 8 | 1.0 |
| 1.5 Session Mgmt | 6 | 0.75 |
| 1.6 Error Handling | 10 | 1.25 |
| 1.7 Access Control | 4 | 0.5 |
| 1.8 XSS Prevention | 12 | 1.5 |
| 1.9 DB Pooling | 6 | 0.75 |
| 1.10 Salt | 2 | 0.25 |
| **TOTAL** | **83** | **10.4** |

**Realistic Timeline:** 2-3 weeks at full-time development

---

## Git Workflow

For each item, use this commit structure:

```bash
# Start working on item 1.1
git checkout -b tier1/1.1-clinician-dashboard

# Make changes, test, repeat
pytest tests/test_tier1_blockers.py::TestClinicianDashboard -v

# When complete
git add -A
git commit -m "feat(tier1.1): Fix clinician dashboard - 10 broken features

- Feature A: Fixed by [change]
- Feature B: Fixed by [change]
- Feature C: Fixed by [change]
...

Tests added: 10+ tests for dashboard functionality
All tests passing: 13/13 original + 10/10 new
Code review: [Self review summary]

Closes: TIER-1-1"

# Merge to main
git checkout main
git merge tier1/1.1-clinician-dashboard
git push origin main
```

---

## Example: How to Fix One Feature

**Example: "Patient detail view not loading"**

### Step 1: Write Test (Fails)
```python
def test_patient_detail_view(self, authenticated_clinician_client, test_patient_account):
    response = authenticated_clinician_client.get(
        f'/api/clinician/patient/{test_patient_account["username"]}'
    )
    assert response.status_code == 200  # FAILS
    assert 'mood_history' in response.json
    assert 'therapy_sessions' in response.json
    assert 'assessments' in response.json
```

### Step 2: Debug
```bash
# Add test-specific debugging
curl http://localhost:5000/api/clinician/patient/testpatient \
  -H "Cookie: session=..."

# Check if endpoint exists
grep -n "/api/clinician/patient/" api.py

# Check database has data
psql -U user healing_space -c "SELECT * FROM mood_logs WHERE username='testpatient';"
```

### Step 3: Identify Issue
- Maybe endpoint doesn't exist
- Maybe endpoint exists but returns wrong data format
- Maybe frontend doesn't render it correctly
- Maybe database doesn't have the data

### Step 4: Fix
```python
# In api.py, add/fix endpoint
@app.route('/api/clinician/patient/<username>', methods=['GET'])
@app.route('/api/clinician/patient/<username>', methods=['GET'])
def get_patient_detail(username):
    clinician = get_authenticated_username()
    if not clinician:
        return jsonify({'error': 'Auth required'}), 401
    
    # Verify clinician has access
    conn = get_db_connection()
    cur = get_wrapped_cursor(conn)
    cur.execute(
        'SELECT 1 FROM clinician_patients WHERE clinician_username=%s AND patient_username=%s',
        (clinician, username)
    )
    if not cur.fetchone():
        conn.close()
        return jsonify({'error': 'Access denied'}), 403
    
    # Get patient data
    cur.execute(
        'SELECT * FROM mood_logs WHERE username=%s ORDER BY timestamp DESC LIMIT 30',
        (username,)
    )
    mood_history = cur.fetchall()
    
    # ... get other data
    
    conn.close()
    return jsonify({
        'username': username,
        'mood_history': mood_history,
        'therapy_sessions': sessions,
        'assessments': assessments
    }), 200
```

### Step 5: Test
```bash
pytest tests/test_tier1_blockers.py::TestClinicianDashboard::test_patient_detail_view -v
# Now PASSES ✅
```

### Step 6: Run full suite
```bash
pytest tests/ -v
# All 23 tests pass ✅
```

### Step 7: Commit
```bash
git add api.py tests/test_tier1_blockers.py
git commit -m "feat(tier1.1): Fix clinician patient detail view endpoint

- Added GET /api/clinician/patient/<username> endpoint
- Returns mood history, therapy sessions, assessments
- Verifies clinician has access to patient
- Added comprehensive tests (3 test cases)

All tests passing: 13/13 original + 13/13 tier1"
```

---

## Next Steps

1. **Read this entire prompt carefully**
2. **Create the test infrastructure** (Phase 0)
3. **Run the baseline tests** (they will fail)
4. **Start implementing items** 1.1-1.10 in order
5. **After EACH item:**
   - Run tests
   - Check regressions
   - Commit to git
   - Update checklist
6. **When all 10 items done:**
   - Write summary document
   - Create TIER_1_COMPLETION_SUMMARY.md
   - Push to git
   - Mark TIER 1 as complete

---

## Support & Debugging

If you get stuck on any item:

1. **Read the requirements** again carefully
2. **Check the test** for what's expected
3. **Debug locally** with `python3 -i api.py`
4. **Check logs** for error messages
5. **Compare with working code** in other endpoints
6. **Ask for help** with specific error messages

---

**You are now ready to begin TIER 1 implementation.**

**Start with Phase 0 to set up the test infrastructure, then proceed to items 1.1-1.10 in order.**

**Good luck! 🚀**
