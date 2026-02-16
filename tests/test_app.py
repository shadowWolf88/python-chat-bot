import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os
import json
import sqlite3
import hashlib

# Ensure debug mode so imports don't require production secrets
os.environ.setdefault('DEBUG', '1')
os.environ.setdefault('PIN_SALT', 'testsalt1234567890')
try:
    from cryptography.fernet import Fernet
    os.environ.setdefault('ENCRYPTION_KEY', Fernet.generate_key().decode())
except Exception:
    # If cryptography not available in test runtime, set a placeholder and rely on DEBUG behavior
    os.environ.setdefault('ENCRYPTION_KEY', '')

import pytest

# Web-only platform: removed legacy desktop imports
import secure_transfer


def test_sftp_helper_when_missing_paramiko():
    # If paramiko not available, secure_transfer.sftp_upload should raise RuntimeError
    if secure_transfer.HAS_PARAMIKO:
        pytest.skip('paramiko installed in environment; skipping missing-paramiko test')
    with pytest.raises(RuntimeError):
        secure_transfer.sftp_upload('nonexistent.file', '/remote/path', 'example.com', username='x', password='y')
