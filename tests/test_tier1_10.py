"""
TIER 1.10 Tests: Anonymization Salt Hardening
Tests for:
- TIER 1.10: Remove hardcoded salt, use environment variable
- Auto-generation in DEBUG mode
- Fail-closed in production mode
- Proper validation
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock
import secrets

# Project root for portable file paths
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class TestTier110AnonymizationSalt:
    """TIER 1.10: Anonymization Salt Security"""
    
    def test_get_anonymization_salt_from_env(self):
        """Verify salt is read from ANONYMIZATION_SALT environment variable"""
        from training_data_manager import get_anonymization_salt
        
        test_salt = secrets.token_hex(32)
        with patch.dict(os.environ, {'ANONYMIZATION_SALT': test_salt, 'DEBUG': '0'}):
            salt = get_anonymization_salt()
            assert salt == test_salt, "Salt should come from environment variable"
    
    def test_get_anonymization_salt_autogenerate_debug(self):
        """Verify salt is auto-generated in DEBUG mode if not set"""
        from training_data_manager import get_anonymization_salt
        
        # Remove ANONYMIZATION_SALT and set DEBUG=1
        env = {k: v for k, v in os.environ.items() if k != 'ANONYMIZATION_SALT'}
        env['DEBUG'] = '1'
        
        with patch.dict(os.environ, env, clear=False):
            salt = get_anonymization_salt()
            # Should return a 64-character hex string (32 bytes)
            assert len(salt) >= 32, f"Generated salt too short: {len(salt)}"
            # Should be valid hex
            try:
                int(salt, 16)
            except ValueError:
                pytest.fail("Generated salt is not valid hex")
    
    def test_get_anonymization_salt_fail_closed_production(self):
        """Verify RuntimeError in production if ANONYMIZATION_SALT not set"""
        from training_data_manager import get_anonymization_salt
        
        # Remove ANONYMIZATION_SALT and set DEBUG=0 (production)
        env = {k: v for k, v in os.environ.items() if k != 'ANONYMIZATION_SALT'}
        env['DEBUG'] = '0'
        
        with patch.dict(os.environ, env, clear=False):
            with pytest.raises(RuntimeError) as excinfo:
                get_anonymization_salt()
            
            assert "CRITICAL" in str(excinfo.value), "Should raise RuntimeError for missing salt"
            assert "production" in str(excinfo.value).lower()
    
    def test_get_anonymization_salt_validates_length(self):
        """Verify salt must be 32+ characters"""
        from training_data_manager import get_anonymization_salt
        
        # Set a short salt
        with patch.dict(os.environ, {'ANONYMIZATION_SALT': 'short', 'DEBUG': '0'}):
            with pytest.raises(ValueError) as excinfo:
                get_anonymization_salt()
            
            assert "too short" in str(excinfo.value).lower()
    
    def test_anonymize_username_uses_env_salt(self):
        """Verify anonymize_username uses environment salt"""
        from training_data_manager import TrainingDataManager
        
        manager = TrainingDataManager()
        test_salt = secrets.token_hex(32)
        
        with patch.dict(os.environ, {'ANONYMIZATION_SALT': test_salt, 'DEBUG': '0'}):
            # Same username with same salt should produce same hash
            hash1 = manager.anonymize_username('testuser')
            hash2 = manager.anonymize_username('testuser')
            
            assert hash1 == hash2, "Same username should produce same hash with same salt"
            assert len(hash1) == 16, "Hash should be 16 characters (first 16 of SHA256)"
    
    def test_anonymize_username_different_with_different_salt(self):
        """Verify different salts produce different hashes for same username"""
        from training_data_manager import TrainingDataManager
        
        manager = TrainingDataManager()
        salt1 = secrets.token_hex(32)
        salt2 = secrets.token_hex(32)
        
        with patch.dict(os.environ, {'ANONYMIZATION_SALT': salt1, 'DEBUG': '0'}):
            hash1 = manager.anonymize_username('testuser')
        
        with patch.dict(os.environ, {'ANONYMIZATION_SALT': salt2, 'DEBUG': '0'}):
            hash2 = manager.anonymize_username('testuser')
        
        assert hash1 != hash2, "Different salts should produce different hashes"
    
    def test_no_hardcoded_salt_in_source(self):
        """Verify no hardcoded default salt in source code"""
        with open(os.path.join(ROOT, 'training_data_manager.py'), 'r') as f:
            content = f.read()
            # Should NOT contain the old hardcoded default
            assert "default_salt_change_in_production" not in content, \
                "Hardcoded default salt should not be in source code"
            # Should NOT have a literal string like 'default_salt' or similar
            assert "'default_salt" not in content, "No hardcoded default_salt should be present"
    
    def test_env_example_documents_salt(self):
        """Verify .env.example documents ANONYMIZATION_SALT requirement"""
        with open(os.path.join(ROOT, '.env.example'), 'r') as f:
            content = f.read()
            assert 'ANONYMIZATION_SALT' in content, ".env.example should document ANONYMIZATION_SALT"
            assert 'TIER 1.10' in content or 'anonymization salt' in content.lower(), \
                ".env.example should explain anonymization salt purpose"
    
    def test_salt_used_in_anonymization_logic(self):
        """Verify salt is actually used in SHA256 hash"""
        import hashlib
        from training_data_manager import get_anonymization_salt
        
        test_salt = secrets.token_hex(32)
        with patch.dict(os.environ, {'ANONYMIZATION_SALT': test_salt, 'DEBUG': '0'}):
            salt = get_anonymization_salt()
            
            # Manually compute what hash should be
            username = 'testuser'
            expected_hash = hashlib.sha256(f"{username}{salt}".encode()).hexdigest()[:16]
            
            # Create manager and anonymize
            from training_data_manager import TrainingDataManager
            manager = TrainingDataManager()
            actual_hash = manager.anonymize_username(username)
            
            assert actual_hash == expected_hash, "Hash should use salt in computation"
    
    def test_salt_affects_all_anonymization(self):
        """Verify salt is used for all anonymization operations"""
        from training_data_manager import TrainingDataManager
        
        # Check that anonymize_username method exists and uses salt
        manager = TrainingDataManager()
        
        salt1 = secrets.token_hex(32)
        salt2 = secrets.token_hex(32)
        
        with patch.dict(os.environ, {'ANONYMIZATION_SALT': salt1, 'DEBUG': '0'}):
            anon1 = manager.anonymize_username('user123')
        
        with patch.dict(os.environ, {'ANONYMIZATION_SALT': salt2, 'DEBUG': '0'}):
            anon2 = manager.anonymize_username('user123')
        
        # Different salts must produce different results
        assert anon1 != anon2, "Salt must affect anonymization output"
    
    def test_salt_generation_format(self):
        """Verify auto-generated salt meets security requirements"""
        from training_data_manager import get_anonymization_salt
        
        # Generate in DEBUG mode
        with patch.dict(os.environ, {'DEBUG': '1'}, clear=False):
            env = {k: v for k, v in os.environ.items() if k != 'ANONYMIZATION_SALT'}
            env['DEBUG'] = '1'
            
            with patch.dict(os.environ, env, clear=False):
                salt = get_anonymization_salt()
                
                # Should be at least 32 chars (16 bytes hex)
                assert len(salt) >= 32, "Generated salt must be at least 32 characters"
                
                # Should be valid hex
                try:
                    int(salt, 16)
                except ValueError:
                    pytest.fail("Generated salt must be valid hex string")
                
                # Should use secrets module (random enough for crypto)
                # Just verify it's reasonably random by checking it's not all same char
                assert len(set(salt)) > 5, "Salt should have good entropy"


class TestTier110Integration:
    """Integration tests for TIER 1.10 anonymization"""
    
    def test_manager_initialization_with_salt(self):
        """Verify TrainingDataManager works with environment salt"""
        from training_data_manager import TrainingDataManager
        
        test_salt = secrets.token_hex(32)
        with patch.dict(os.environ, {'ANONYMIZATION_SALT': test_salt, 'DEBUG': '0'}):
            manager = TrainingDataManager()
            
            # Should be able to anonymize usernames
            anon = manager.anonymize_username('patient123')
            assert anon is not None
            assert len(anon) == 16
    
    def test_salt_validation_on_init(self):
        """Verify salt is validated when getting anonymization salt"""
        from training_data_manager import get_anonymization_salt
        
        # Invalid salt (too short)
        with patch.dict(os.environ, {'ANONYMIZATION_SALT': 'x' * 10, 'DEBUG': '0'}):
            with pytest.raises(ValueError):
                get_anonymization_salt()
    
    def test_reproducible_anonymization_with_same_salt(self):
        """Verify same salt produces deterministic hashes"""
        from training_data_manager import TrainingDataManager
        
        manager = TrainingDataManager()
        test_salt = secrets.token_hex(32)
        
        with patch.dict(os.environ, {'ANONYMIZATION_SALT': test_salt, 'DEBUG': '0'}):
            # Same username should always produce same hash
            hashes = [manager.anonymize_username('alice') for _ in range(5)]
            assert len(set(hashes)) == 1, "Same username should always produce same hash"


# Import at end to ensure fixtures are defined
import os
