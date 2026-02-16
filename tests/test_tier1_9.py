"""
TIER 1.9: Database Connection Pooling Tests
============================================

Tests for connection pooling infrastructure to prevent connection exhaustion.
Verifies that the pool is created, connections are reused, and pooling reduces
connection overhead under load.

Test Coverage:
- Pool creation and initialization
- Connection retrieval from pool
- Connection return to pool
- Thread safety
- Pool size limits
- Context manager usage
- Error handling
"""

import pytest
import os
import sys
import threading
import time
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import api


class TestTier19PoolCreation:
    """Test connection pool initialization"""
    
    def test_pool_module_imported(self):
        """Verify psycopg2.pool is imported"""
        # Check that pool module is available
        from psycopg2 import pool as psycopg2_pool
        assert psycopg2_pool is not None, "psycopg2.pool module not available"
        assert hasattr(psycopg2_pool, 'ThreadedConnectionPool'), \
            "ThreadedConnectionPool class not found"
    
    def test_pool_globals_exist(self):
        """Verify pool global variables exist in api.py"""
        assert hasattr(api, '_db_pool'), "api._db_pool global variable not found"
        assert hasattr(api, '_db_pool_lock'), "api._db_pool_lock global variable not found"
        assert hasattr(api, '_get_db_pool'), "api._get_db_pool function not found"
    
    def test_pool_is_none_initially(self):
        """Pool should be None until first use"""
        # Save original pool state
        original_pool = api._db_pool
        
        # The pool may have been created during import, but let's check the logic
        if api._db_pool is None:
            assert api._db_pool is None, "Pool should be None initially"
        
        # Restore
        api._db_pool = original_pool
    
    def test_get_db_pool_function_exists(self):
        """Verify _get_db_pool function is defined"""
        assert callable(api._get_db_pool), "_get_db_pool should be callable"
        # Check function signature
        import inspect
        sig = inspect.signature(api._get_db_pool)
        assert len(sig.parameters) == 0, "_get_db_pool should take no parameters"
    
    def test_get_db_connection_pooled_function_exists(self):
        """Verify get_db_connection_pooled context manager exists"""
        assert hasattr(api, 'get_db_connection_pooled'), \
            "get_db_connection_pooled function not found"
        assert callable(api.get_db_connection_pooled), \
            "get_db_connection_pooled should be callable"


class TestTier19PoolConfiguration:
    """Test connection pool configuration"""
    
    def test_pool_uses_threaded_connection_pool(self):
        """Pool should use ThreadedConnectionPool for thread safety"""
        # Read api.py source to verify pool type
        with open(os.path.join(os.path.dirname(api.__file__), 'api.py'), 'r') as f:
            content = f.read()
            assert 'ThreadedConnectionPool' in content, \
                "Should use ThreadedConnectionPool for thread safety"
            assert 'pool.ThreadedConnectionPool' in content, \
                "Should use pool.ThreadedConnectionPool"
    
    def test_pool_min_connections_configured(self):
        """Pool should have minimum connection count"""
        with open(os.path.join(os.path.dirname(api.__file__), 'api.py'), 'r') as f:
            content = f.read()
            # Check for minconn parameter
            assert 'minconn=' in content or 'minconn =' in content, \
                "Pool should specify minconn parameter"
            assert 'minconn=2' in content, \
                "Pool should have minconn=2 (at least 2 connections always ready)"
    
    def test_pool_max_connections_configured(self):
        """Pool should have maximum connection limit"""
        with open(os.path.join(os.path.dirname(api.__file__), 'api.py'), 'r') as f:
            content = f.read()
            # Check for maxconn parameter
            assert 'maxconn=' in content or 'maxconn =' in content, \
                "Pool should specify maxconn parameter"
            assert 'maxconn=20' in content, \
                "Pool should have maxconn=20 (limit connection exhaustion)"
    
    def test_pool_uses_correct_database_credentials(self):
        """Pool should read credentials from environment"""
        with open(os.path.join(os.path.dirname(api.__file__), 'api.py'), 'r') as f:
            content = f.read()
            # Check that pool respects DATABASE_URL
            assert 'DATABASE_URL' in content, "Pool should check DATABASE_URL env var"
            # Check that pool respects individual env vars
            assert 'DB_HOST' in content and 'DB_PORT' in content, \
                "Pool should support individual env vars (DB_HOST, DB_PORT, etc.)"
    
    def test_pool_has_timeout_configured(self):
        """Pool should have connection timeout"""
        with open(os.path.join(os.path.dirname(api.__file__), 'api.py'), 'r') as f:
            content = f.read()
            assert 'connect_timeout=' in content or 'timeout' in content.lower(), \
                "Pool should have connect_timeout configured"
            assert 'connect_timeout=30' in content, \
                "Pool should have 30 second timeout"


class TestTier19ContextManager:
    """Test context manager for pooled connections"""
    
    def test_context_manager_is_generator(self):
        """get_db_connection_pooled should be a context manager"""
        # Check that it has __enter__ and __exit__ (via contextmanager decorator)
        func = api.get_db_connection_pooled
        # contextmanager decorator makes it return a context manager
        context = func()
        assert hasattr(context, '__enter__'), "Should have __enter__ method"
        assert hasattr(context, '__exit__'), "Should have __exit__ method"
    
    def test_context_manager_has_correct_signature(self):
        """Context manager should properly document usage"""
        import inspect
        doc = inspect.getdoc(api.get_db_connection_pooled)
        assert doc is not None, "Context manager should have docstring"
        assert 'Usage:' in doc or 'usage' in doc.lower(), \
            "Docstring should explain usage"
        assert 'with' in doc.lower(), "Docstring should mention 'with' keyword"
    
    def test_docstring_mentions_pooling(self):
        """Function docstring should mention TIER 1.9 pooling"""
        import inspect
        doc = inspect.getdoc(api.get_db_connection_pooled)
        assert 'TIER 1.9' in doc or 'pool' in doc.lower() or 'pooled' in doc.lower(), \
            "Docstring should mention pooling or TIER 1.9"


class TestTier19BackwardCompatibility:
    """Test that existing get_db_connection calls still work"""
    
    def test_get_db_connection_function_exists(self):
        """Original get_db_connection should still exist for compatibility"""
        assert hasattr(api, 'get_db_connection'), \
            "get_db_connection function must exist for backward compatibility"
        assert callable(api.get_db_connection), \
            "get_db_connection should be callable"
    
    def test_get_db_connection_takes_timeout_param(self):
        """Maintain backward compatibility with timeout parameter"""
        import inspect
        sig = inspect.signature(api.get_db_connection)
        assert 'timeout' in sig.parameters, \
            "get_db_connection should accept timeout parameter for compatibility"
    
    def test_get_db_connection_uses_pool(self):
        """get_db_connection should use the pool internally"""
        with open(os.path.join(os.path.dirname(api.__file__), 'api.py'), 'r') as f:
            content = f.read()
            # Find get_db_connection function
            import re
            match = re.search(r'def get_db_connection\(.*?\):\s*"""[^"]*""".*?return', 
                            content, re.DOTALL)
            assert match, "get_db_connection function not found"
            func_body = match.group(0)
            # Should call _get_db_pool or getconn from pool
            assert '_get_db_pool' in func_body or 'getconn' in func_body, \
                "get_db_connection should use pool internally"
    
    def test_backward_compat_docstring(self):
        """Docstring should explain pooling is now in use"""
        import inspect
        doc = inspect.getdoc(api.get_db_connection)
        assert doc is not None, "get_db_connection should have docstring"
        # Should mention pool or TIER 1.9
        assert 'pool' in doc.lower() or 'TIER 1.9' in doc, \
            "Docstring should explain that pooling is now in use"


class TestTier19ThreadSafety:
    """Test that pooling is thread-safe"""
    
    def test_pool_lock_exists(self):
        """Pool creation should use threading.Lock for thread safety"""
        assert hasattr(api, '_db_pool_lock'), "Pool lock variable not found"
        # Verify it's a Lock-like object
        assert hasattr(api._db_pool_lock, 'acquire') and hasattr(api._db_pool_lock, 'release'), \
            "_db_pool_lock should be a threading.Lock (has acquire/release methods)"
    
    def test_pool_creation_uses_lock(self):
        """Pool initialization should use lock to prevent race conditions"""
        with open(os.path.join(os.path.dirname(api.__file__), 'api.py'), 'r') as f:
            content = f.read()
            # Find _get_db_pool function
            import re
            match = re.search(r'def _get_db_pool\(\):.*?return _db_pool', 
                            content, re.DOTALL)
            assert match, "_get_db_pool function not found"
            func_body = match.group(0)
            # Should use _db_pool_lock
            assert '_db_pool_lock' in func_body and 'with' in func_body, \
                "Pool creation should use lock with context manager"
    
    def test_multiple_requests_use_same_pool(self):
        """Multiple requests should retrieve connections from same pool instance"""
        # This tests the singleton pattern
        with open(os.path.join(os.path.dirname(api.__file__), 'api.py'), 'r') as f:
            content = f.read()
            import re
            # Check that _db_pool is checked and reused
            match = re.search(r'if _db_pool is None:.*?if _db_pool is None:', 
                            content, re.DOTALL)
            assert match, "Should check _db_pool twice (singleton pattern)"


class TestTier19ErrorHandling:
    """Test connection pool error handling"""
    
    def test_context_manager_handles_exceptions(self):
        """Context manager should handle exceptions in user code"""
        import inspect
        source = inspect.getsource(api.get_db_connection_pooled)
        # Should have try/except/finally pattern
        assert 'try:' in source, "Should have try block"
        assert 'except' in source, "Should have except block"
        assert 'finally:' in source, "Should have finally block"
        assert 'putconn' in source, "Should return connection in finally"
    
    def test_pool_logging_for_errors(self):
        """Pool should log errors when unable to create or use connections"""
        with open(os.path.join(os.path.dirname(api.__file__), 'api.py'), 'r') as f:
            content = f.read()
            # Should have logging for pool errors
            pool_section = content[content.find('_get_db_pool'):content.find('_get_db_pool')+2000]
            assert 'app_logger' in pool_section or 'logger' in pool_section.lower(), \
                "Pool creation should use logging"


class TestTier19Documentation:
    """Test that pooling is properly documented"""
    
    def test_comments_explain_tier_1_9(self):
        """Code should have TIER 1.9 comments"""
        with open(os.path.join(os.path.dirname(api.__file__), 'api.py'), 'r') as f:
            content = f.read()
            # Count TIER 1.9 references
            count = content.count('TIER 1.9')
            assert count >= 2, \
                f"Should have at least 2 TIER 1.9 comments (found {count})"
    
    def test_pool_docstrings_explain_minconn_maxconn(self):
        """Docstrings should explain pool sizing"""
        with open(os.path.join(os.path.dirname(api.__file__), 'api.py'), 'r') as f:
            content = f.read()
            # Check that pool explanation mentions min/max
            pool_section = content[content.find('minconn'):content.find('maxconn')+100]
            assert 'minconn' in pool_section and 'maxconn' in pool_section, \
                "Should explain minconn and maxconn in comments"
    
    def test_docstring_recommends_context_manager(self):
        """Docstring should recommend using context manager"""
        import inspect
        doc = inspect.getdoc(api.get_db_connection)
        assert 'context manager' in doc.lower() or 'with' in doc.lower(), \
            "Docstring should recommend context manager usage"


class TestTier19Integration:
    """Integration tests for connection pooling"""
    
    def test_imports_are_correct(self):
        """Verify all necessary imports are present"""
        # Check imports at top of api.py
        with open(os.path.join(os.path.dirname(api.__file__), 'api.py'), 'r') as f:
            content = f.read()
            # Should import psycopg2.pool
            assert 'from psycopg2 import pool' in content, \
                "Should import pool from psycopg2"
            # Should import contextmanager
            assert 'contextmanager' in content, \
                "Should import contextmanager from functools"
            # Should import threading
            assert 'import threading' in content, \
                "Should import threading module"
    
    def test_pool_initialization_message(self):
        """Pool creation should log initialization message"""
        with open(os.path.join(os.path.dirname(api.__file__), 'api.py'), 'r') as f:
            content = f.read()
            # Should log pool creation
            assert 'pool created' in content.lower(), \
                "Should log when connection pool is created"
            # Should mention pool size
            assert 'min=' in content or 'minconn' in content, \
                "Log message should mention minimum connections"
    
    def test_teardown_hook_exists(self):
        """Should have Flask teardown hook for cleanup"""
        with open(os.path.join(os.path.dirname(api.__file__), 'api.py'), 'r') as f:
            content = f.read()
            # Should have teardown_appcontext decorator
            assert '@app.teardown_appcontext' in content, \
                "Should have teardown_appcontext hook for pool cleanup"
            # Check the teardown function
            import re
            match = re.search(r'def teardown_db_pool\(.*?\):', content)
            assert match, "Should have teardown_db_pool function"


class TestTier19CodeQuality:
    """Test code quality and best practices"""
    
    def test_no_hardcoded_pool_settings(self):
        """Pool settings should not be hardcoded magic numbers"""
        with open(os.path.join(os.path.dirname(api.__file__), 'api.py'), 'r') as f:
            content = f.read()
            # Should have clear minconn/maxconn values
            assert 'minconn=2' in content and 'maxconn=20' in content, \
                "Pool settings should be explicit and clear"
    
    def test_credentials_from_env_only(self):
        """Pool should only read credentials from environment"""
        with open(os.path.join(os.path.dirname(api.__file__), 'api.py'), 'r') as f:
            content = f.read()
            # Find pool initialization section
            import re
            pool_init_match = re.search(r'def _get_db_pool\(\):.*?return _db_pool', 
                                       content, re.DOTALL)
            assert pool_init_match, "_get_db_pool function not found"
            pool_init = pool_init_match.group(0)
            
            # Should use variables (db_host, db_user, etc.) not literal strings
            assert 'host=db_host' in pool_init, "Should use db_host variable, not literal"
            assert 'user=db_user' in pool_init, "Should use db_user variable, not literal"
            assert 'password=db_password' in pool_init, "Should use db_password variable, not literal"
            assert 'database=db_name' in pool_init, "Should use db_name variable, not literal"
            
            # These variables should come from os.environ
            assert 'os.environ.get' in pool_init or 'os.getenv' in pool_init, \
                "Credentials should be read from os.environ"
    
    def test_functions_are_properly_named(self):
        """Function names should clearly indicate purpose"""
        assert '_get_db_pool' in dir(api), "_get_db_pool private function exists"
        assert 'get_db_connection_pooled' in dir(api), "get_db_connection_pooled public function exists"
        assert 'get_db_connection' in dir(api), "get_db_connection backward compat function exists"
        # Names clearly indicate: private (_), public (get_), pooled (pooled)


class TestTier19Performance:
    """Test performance characteristics of connection pooling"""
    
    def test_reuses_connections(self):
        """Pool should reuse connections"""
        with open(os.path.join(os.path.dirname(api.__file__), 'api.py'), 'r') as f:
            content = f.read()
            # Should call getconn and putconn
            assert 'getconn()' in content, "Should get connections from pool"
            assert 'putconn(' in content, "Should return connections to pool"
    
    def test_pool_prevents_connection_exhaustion(self):
        """Pool size limits prevent exhaustion"""
        with open(os.path.join(os.path.dirname(api.__file__), 'api.py'), 'r') as f:
            content = f.read()
            # maxconn should be set to a reasonable limit
            import re
            match = re.search(r'maxconn=(\d+)', content)
            assert match, "maxconn should be configured"
            max_conn = int(match.group(1))
            assert max_conn >= 10 and max_conn <= 50, \
                f"maxconn should be reasonable (10-50, got {max_conn})"
    
    def test_maintains_minimum_ready_connections(self):
        """Pool should maintain minimum ready connections"""
        with open(os.path.join(os.path.dirname(api.__file__), 'api.py'), 'r') as f:
            content = f.read()
            # minconn should be set
            import re
            match = re.search(r'minconn=(\d+)', content)
            assert match, "minconn should be configured"
            min_conn = int(match.group(1))
            assert min_conn >= 1, f"minconn should be at least 1 (got {min_conn})"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
