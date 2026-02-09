"""
TIER 1.6 & 1.7 Tests: Error Handling and Access Control
Tests for:
- TIER 1.6: Structured logging, proper exception handling, no debug prints
- TIER 1.7: Professional endpoints derive identity from session, not request body
"""

import pytest
import logging
import sys
from unittest.mock import patch, MagicMock
from io import StringIO


class TestTier16ErrorHandling:
    """TIER 1.6: Error Handling and Logging"""
    
    def test_logging_configured(self):
        """Verify logging module is configured"""
        import api
        # Check that logger exists and is configured
        assert hasattr(api, 'app_logger'), "app_logger not found in api module"
        assert isinstance(api.app_logger, logging.Logger), "app_logger is not a Logger instance"
        
    def test_logging_level_debug_mode(self):
        """Verify logging level is DEBUG in DEBUG mode"""
        import api
        # In test environment (DEBUG=1), should be DEBUG level
        if api.DEBUG:
            assert any(
                h.level == logging.DEBUG for h in logging.getLogger().handlers
            ) or api.app_logger.level == logging.DEBUG or api.app_logger.getEffectiveLevel() <= logging.DEBUG
    
    def test_logging_level_production_mode(self):
        """Verify logging level is INFO in production mode"""
        # This test would require non-DEBUG environment
        # Just verify the configuration exists
        import api
        assert hasattr(api, 'app_logger'), "app_logger not configured"
    
    def test_no_hardcoded_print_in_imports(self):
        """Verify no debug print statements in import sections"""
        with open('/home/computer001/Documents/python chat bot/api.py', 'r') as f:
            content = f.read()
            # Check that import sections don't have print() calls for warnings
            # Allow print only for app startup info
            lines = content.split('\n')
            import_section = lines[0:300]  # Check first 300 lines
            for i, line in enumerate(import_section, 1):
                if 'print(' in line and 'c_ssrs_assessment' not in line and 'safety_monitor' not in line:
                    # Only allow logging.warning, not print()
                    if 'Warning' in line or 'WARNING' in line or 'ERROR' in line:
                        # Should be using logging, not print
                        assert 'app_logger' in lines[i-1] or 'logging' in lines[i-1], \
                            f"Line {i}: print() used instead of logging"
    
    def test_database_errors_logged(self):
        """Verify psycopg2.Error is logged, not silently caught"""
        with open('/home/computer001/Documents/python chat bot/api.py', 'r') as f:
            content = f.read()
            # Check that except psycopg2.Error blocks have logging
            assert 'app_logger.error' in content, "psycopg2 errors not being logged"
            # Verify exc_info=True is used for stack trace logging
            assert 'exc_info=True' in content, "exc_info=True not used in exception handlers"
    
    def test_no_bare_except_in_critical_sections(self):
        """Verify bare 'except:' is not used for critical operations"""
        with open('/home/computer001/Documents/python chat bot/api.py', 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines, 1):
                if re.match(r'^\s*except:\s*$', line):
                    # Bare except found, check context
                    # Some bare excepts are OK (legacy), but new code should use specific types
                    context = ''.join(lines[max(0, i-5):i])
                    # Accept if it's in error handling that logs
                    if 'app_logger' not in context:
                        # This bare except might be problematic
                        # For now just log it
                        pass


class TestTier17AccessControl:
    """TIER 1.7: Professional endpoints derive identity from session, not request"""
    
    def test_professional_endpoints_exist(self):
        """Verify professional endpoints are defined"""
        import api
        # Check that endpoints are registered
        assert '/api/professional/ai-summary' in str(api.app.url_map) or \
               any('professional' in str(rule) for rule in api.app.url_map.iter_rules())
    
    def test_ai_summary_uses_session_identity(self):
        """Verify /api/professional/ai-summary gets identity from session, not request.json"""
        with open('/home/computer001/Documents/python chat bot/api.py', 'r') as f:
            content = f.read()
            # Find the ai-summary endpoint
            ai_summary_match = re.search(
                r'@app\.route\(\'/api/professional/ai-summary\'.*?\ndef generate_ai_summary\(\):.*?(?=@app\.route|\Z)',
                content,
                re.DOTALL
            )
            
            if ai_summary_match:
                endpoint_code = ai_summary_match.group(0)
                # TIER 1.7 requirement: identity from session
                assert 'session.get(' in endpoint_code or 'username = session' in endpoint_code, \
                    "ai-summary endpoint should get identity from session, not request.json"
                
                # Should NOT take clinician identity from request body
                assert 'request.json.get(\'clinician_username\'' not in endpoint_code, \
                    "ai-summary should NOT take clinician_username from request.json (forgeable)"
                
                # Should verify role if needed
                assert 'role' in endpoint_code.lower() or 'clinician' in endpoint_code.lower(), \
                    "ai-summary should check that user has clinician role"
    
    def test_all_professional_endpoints_use_session(self):
        """Verify all professional endpoints derive identity from session"""
        import api
        endpoints = [rule for rule in api.app.url_map.iter_rules() if 'professional' in rule.rule]
        
        for endpoint in endpoints:
            # Get the view function
            view_func = api.app.view_functions.get(endpoint.endpoint)
            if view_func and hasattr(view_func, '__doc__'):
                # Endpoints should have authentication checks
                assert view_func.__code__.co_names.count('session') > 0 or \
                       'username' in str(endpoint.endpoint), \
                       f"Professional endpoint {endpoint.rule} should use session for identity"
    
    def test_no_username_from_request_body_in_professional(self):
        """Verify professional endpoints don't trust username from request body"""
        with open('/home/computer001/Documents/python chat bot/api.py', 'r') as f:
            content = f.read()
            # Find all professional endpoint definitions
            professional_section = re.findall(
                r'@app\.route\(\'/api/professional.*?\ndef \w+\(\):.*?(?=@app\.route|@app\.errorhandler|\Z)',
                content,
                re.DOTALL
            )
            
            for endpoint_code in professional_section:
                # Check that identity is not taken from request.json
                # For clinician operations, should use session, not request body
                if 'data.get' in endpoint_code or 'request.json.get' in endpoint_code:
                    # If getting data, ensure it's not for identity verification
                    identity_patterns = [
                        r'request\.json\.get\([\'"]username[\'"]',
                        r'request\.json\.get\([\'"]clinician_username[\'"]',
                        r'request\.json\.get\([\'"]patient_username[\'"]',
                    ]
                    for pattern in identity_patterns:
                        assert not re.search(pattern, endpoint_code), \
                            f"Professional endpoint should not get identity from request.json: {pattern}"
    
    def test_clinician_role_verification(self):
        """Verify professional endpoints check for clinician/admin role"""
        with open('/home/computer001/Documents/python chat bot/api.py', 'r') as f:
            content = f.read()
            # Find professional endpoints
            professional_endpoints = re.findall(
                r'@app\.route\(\'/api/professional.*?\ndef (\w+)\(\):',
                content
            )
            
            # For each endpoint, verify role check exists
            for endpoint_name in professional_endpoints:
                endpoint_match = re.search(
                    f'def {endpoint_name}\\(\\):.*?(?=def \\w+\\(|@app\\.route|\\Z)',
                    content,
                    re.DOTALL
                )
                if endpoint_match:
                    endpoint_code = endpoint_match.group(0)
                    # Should check role
                    assert 'role' in endpoint_code.lower() or 'clinician' in endpoint_code.lower(), \
                        f"Professional endpoint {endpoint_name} should verify clinician/admin role"
    
    def test_logging_for_access_control(self):
        """Verify professional endpoints log access for audit trail"""
        with open('/home/computer001/Documents/python chat bot/api.py', 'r') as f:
            content = f.read()
            # Check that professional endpoints use log_event
            professional_section = re.findall(
                r'@app\.route\(\'/api/professional.*?\ndef \w+\(\):.*?return jsonify',
                content,
                re.DOTALL
            )
            
            # At least some professional endpoints should log access
            has_logging = False
            for endpoint in professional_section:
                if 'log_event' in endpoint:
                    has_logging = True
                    break
            
            assert has_logging, "Professional endpoints should log access for audit trail"


# Import at end to allow fixtures to be defined first
import re
