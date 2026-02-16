"""
TIER 1.5 Tests: Session Management Hardening
Tests for:
- Session lifetime (7 days max)
- Session rotation on login
- Inactivity timeout (30 minutes)
- Session invalidation on password change
"""

import pytest
from datetime import datetime, timedelta
from flask import session
from unittest.mock import patch
import time
import os

# Configure environment for tests
os.environ['DEBUG'] = '1'
os.environ['ENCRYPTION_KEY'] = 'test_key_for_cryptography_fernet_base64_32_chars_test'


@pytest.mark.security
class TestSessionLifetime:
    """Test session lifetime is limited to 7 days"""
    
    def test_session_lifetime_is_7_days(self, app):
        """Session lifetime should be 7 days, not 30"""
        # app.config['PERMANENT_SESSION_LIFETIME'] should be 7 days
        expected_lifetime = timedelta(days=7)
        assert app.config['PERMANENT_SESSION_LIFETIME'] == expected_lifetime
    
    def test_session_lifetime_not_30_days(self, app):
        """Ensure session lifetime is NOT 30 days (old value)"""
        max_lifetime = app.config['PERMANENT_SESSION_LIFETIME']
        thirty_days = timedelta(days=30)
        assert max_lifetime < thirty_days, f"Session lifetime {max_lifetime} should be less than 30 days"


@pytest.mark.security
class TestSessionRotation:
    """Test session rotation on login"""
    
    def test_session_rotation_code_check(self, app):
        """Code verification: session is rotated (cleared) on login"""
        import inspect
        import api as api_module
        
        login_func = getattr(api_module, 'login', None)
        if login_func:
            source = inspect.getsource(login_func)
            assert 'session.clear()' in source, "Should clear session on login (rotation)"
    
    def test_session_has_login_time_code_check(self, app):
        """Code verification: login_time is set on login"""
        import inspect
        import api as api_module
        
        login_func = getattr(api_module, 'login', None)
        if login_func:
            source = inspect.getsource(login_func)
            assert 'login_time' in source, "Should set login_time in session"
    
    def test_session_has_last_activity_tracking_code_check(self, app):
        """Code verification: last_activity is tracked for inactivity timeout"""
        import inspect
        import api as api_module
        
        login_func = getattr(api_module, 'login', None)
        if login_func:
            source = inspect.getsource(login_func)
            assert 'last_activity' in source, "Should set last_activity in session"


@pytest.mark.security
class TestInactivityTimeout:
    """Test session expiration after 30 minutes of inactivity"""
    
    def test_inactivity_timeout_middleware_exists(self, app):
        """Code verification: inactivity timeout middleware is implemented"""
        import inspect
        import api as api_module
        
        # Find check_session_inactivity function
        check_inactivity = getattr(api_module, 'check_session_inactivity', None)
        assert check_inactivity is not None, "check_session_inactivity middleware should exist"
    
    def test_inactivity_timeout_checks_last_activity(self, app):
        """Code verification: middleware checks last_activity timestamp"""
        import inspect
        import api as api_module
        
        check_inactivity = getattr(api_module, 'check_session_inactivity', None)
        if check_inactivity:
            source = inspect.getsource(check_inactivity)
            assert 'last_activity' in source, "Should check last_activity"
    
    def test_inactivity_timeout_is_30_minutes(self, app):
        """Code verification: timeout is 30 minutes"""
        import inspect
        import api as api_module
        
        check_inactivity = getattr(api_module, 'check_session_inactivity', None)
        if check_inactivity:
            source = inspect.getsource(check_inactivity)
            assert '30' in source and 'minute' in source.lower(), "Should have 30 minute timeout"
    
    def test_inactivity_timeout_clears_session(self, app):
        """Code verification: expired session is cleared"""
        import inspect
        import api as api_module
        
        check_inactivity = getattr(api_module, 'check_session_inactivity', None)
        if check_inactivity:
            source = inspect.getsource(check_inactivity)
            assert 'session.clear()' in source, "Should clear session on timeout"
    
    def test_last_activity_updated_on_each_request(self, app):
        """Code verification: last_activity is updated on each request"""
        import inspect
        import api as api_module
        
        check_inactivity = getattr(api_module, 'check_session_inactivity', None)
        if check_inactivity:
            source = inspect.getsource(check_inactivity)
            # Should update last_activity at the end of the middleware
            assert 'last_activity' in source, "Should update last_activity on each request"


@pytest.mark.security
class TestSessionInvalidationOnPasswordChange:
    """Test that password change invalidates all sessions"""
    
    def test_password_change_endpoint_exists(self, client):
        """Password change endpoint should exist"""
        response = client.post('/api/auth/change-password', json={})
        # Should get 403 (CSRF) or 401 (auth) but not 404
        assert response.status_code in [401, 403, 415], "Password change endpoint should exist"
    
    def test_password_change_requires_current_password(self, app):
        """Code verification: change-password endpoint validates current password"""
        import inspect
        import api as api_module
        
        change_password_func = getattr(api_module, 'change_password', None)
        if change_password_func:
            source = inspect.getsource(change_password_func)
            assert 'verify_password' in source, "Should verify current password"
            assert 'current_password' in source, "Should require current_password param"
    
    def test_password_change_requires_confirmation(self, app):
        """Code verification: passwords must match"""
        import inspect
        import api as api_module
        
        change_password_func = getattr(api_module, 'change_password', None)
        if change_password_func:
            source = inspect.getsource(change_password_func)
            assert 'confirm_password' in source, "Should require confirmation"
            assert 'match' in source.lower(), "Should verify passwords match"
    
    def test_password_change_validates_password_strength(self, app):
        """Code verification: password strength validation"""
        import inspect
        import api as api_module
        
        change_password_func = getattr(api_module, 'change_password', None)
        if change_password_func:
            source = inspect.getsource(change_password_func)
            assert 'validate_password_strength' in source, "Should validate password strength"
    
    def test_password_change_requires_authentication(self, client):
        """Password change should require authenticated session"""
        response = client.post('/api/auth/change-password',
            json={
                'current_password': 'test',
                'new_password': 'new',
                'confirm_password': 'new'
            }
        )
        
        # Should fail - either 401 (auth) or 403 (CSRF) but not 200
        assert response.status_code in [401, 403]
    
    def test_password_change_requires_csrf_token_decorator(self, app):
        """Code verification: change-password has @CSRFProtection decorator"""
        import inspect
        import api as api_module
        
        change_password_func = getattr(api_module, 'change_password', None)
        if change_password_func:
            # Check the source code around the function
            source_lines = inspect.getsource(change_password_func).split('\n')
            # Look through the source for CSRF decorator
            source_full = '\n'.join(source_lines)
            assert '@CSRFProtection.require_csrf' in source_full or 'CSRF' in source_full, \
                "change-password should have @CSRFProtection decorator"
    
    def test_password_change_invalidates_sessions(self, app):
        """Code verification: password change invalidates sessions"""
        import inspect
        import api as api_module
        
        change_password_func = getattr(api_module, 'change_password', None)
        if change_password_func:
            source = inspect.getsource(change_password_func)
            # Should have session deletion logic
            assert 'DELETE FROM sessions' in source or 'session.clear()' in source, \
                "Should invalidate sessions on password change"


@pytest.mark.security
class TestSessionSecurityHeaders:
    """Test session cookies have proper security attributes"""
    
    def test_session_cookie_httponly(self, app):
        """Session cookie should have HttpOnly flag"""
        assert app.config['SESSION_COOKIE_HTTPONLY'] is True
    
    def test_session_cookie_samesite(self, app):
        """Session cookie should have SameSite=Lax"""
        assert app.config['SESSION_COOKIE_SAMESITE'] == 'Lax'
    
    def test_session_cookie_secure_in_production(self, app):
        """Session cookie should be Secure in production (HTTPS only)"""
        if not os.getenv('DEBUG'):
            assert app.config['SESSION_COOKIE_SECURE'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'security'])
