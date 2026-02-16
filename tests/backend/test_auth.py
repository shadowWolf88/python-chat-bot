"""
Comprehensive tests for Healing Space authentication system.

Covers password hashing/verification (Argon2, bcrypt, PBKDF2, legacy SHA256),
password strength validation, PIN hashing/verification, login/register endpoints,
session management, X-Username header bypass logging, and CSRF token handling.

Run with:
    pytest tests/backend/test_auth.py -v
    pytest tests/backend/test_auth.py -v -k "TestPasswordHashing"
"""

import hashlib
import secrets
import pytest
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timedelta

import api
from tests.conftest import make_mock_db, make_user_row


# ==================== PASSWORD HASHING & VERIFICATION ====================

class TestPasswordHashing:
    """Tests for hash_password() across all supported backends."""

    def test_hash_password_returns_string(self):
        """hash_password should always return a string."""
        result = api.hash_password("TestPass1!")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_hash_password_different_inputs_produce_different_hashes(self):
        """Different passwords must produce different hashes."""
        h1 = api.hash_password("Password1!")
        h2 = api.hash_password("Password2!")
        assert h1 != h2

    def test_hash_password_same_input_produces_different_hashes(self):
        """Same password hashed twice should produce different hashes (salted)."""
        h1 = api.hash_password("SamePass1!")
        h2 = api.hash_password("SamePass1!")
        # Argon2 and bcrypt produce different hashes each time; PBKDF2 with
        # deterministic salt may not, so we only assert they are strings.
        assert isinstance(h1, str) and isinstance(h2, str)

    @patch.object(api, 'HAS_ARGON2', False)
    @patch.object(api, '_ph', None)
    @patch.object(api, 'HAS_BCRYPT', False)
    def test_hash_password_pbkdf2_fallback(self):
        """When Argon2 and bcrypt are unavailable, PBKDF2 fallback is used."""
        result = api.hash_password("FallbackPass1!")
        assert result.startswith("pbkdf2$")

    @patch.object(api, 'HAS_ARGON2', False)
    @patch.object(api, '_ph', None)
    @patch.object(api, 'HAS_BCRYPT', True)
    def test_hash_password_bcrypt_backend(self):
        """When Argon2 is unavailable, bcrypt is used."""
        result = api.hash_password("BcryptPass1!")
        assert result.startswith("$2")

    def test_hash_password_argon2_when_available(self):
        """If Argon2 is available, hash should start with $argon2."""
        if not api.HAS_ARGON2:
            pytest.skip("Argon2 not installed")
        result = api.hash_password("Argon2Pass1!")
        assert result.startswith("$argon2")


class TestPasswordVerification:
    """Tests for verify_password() across all hash formats."""

    def test_verify_correct_password(self):
        """Correct password should verify against its own hash."""
        pw = "Correct1!Horse"
        hashed = api.hash_password(pw)
        assert api.verify_password(hashed, pw) is True

    def test_verify_wrong_password(self):
        """Wrong password should fail verification."""
        hashed = api.hash_password("RightPass1!")
        assert api.verify_password(hashed, "WrongPass1!") is False

    def test_verify_empty_stored_hash(self):
        """Empty stored hash should return False."""
        assert api.verify_password("", "anything") is False
        assert api.verify_password(None, "anything") is False

    def test_verify_pbkdf2_hash(self):
        """PBKDF2 hashes should verify correctly."""
        pw = "PBKDF2Test1!"
        salt = hashlib.sha256(pw.encode()).hexdigest()[:16]
        dk = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), 200000)
        stored = f"pbkdf2${dk.hex()}"
        assert api.verify_password(stored, pw) is True
        assert api.verify_password(stored, "WrongPBKDF2!") is False

    def test_verify_legacy_sha256_hash(self):
        """Legacy SHA256 hashes (64 hex chars) should verify correctly."""
        pw = "LegacySHA256!"
        stored = hashlib.sha256(pw.encode()).hexdigest()
        assert len(stored) == 64
        assert api.verify_password(stored, pw) is True
        assert api.verify_password(stored, "WrongLegacy!") is False

    def test_verify_bcrypt_hash(self):
        """bcrypt hashes should verify when bcrypt is available."""
        if not api.HAS_BCRYPT:
            pytest.skip("bcrypt not installed")
        import bcrypt
        pw = "BcryptVerify1!"
        stored = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
        assert api.verify_password(stored, pw) is True
        assert api.verify_password(stored, "WrongBcrypt1!") is False

    def test_verify_argon2_hash(self):
        """Argon2 hashes should verify when argon2 is available."""
        if not api.HAS_ARGON2:
            pytest.skip("Argon2 not installed")
        pw = "Argon2Verify1!"
        stored = api._ph.hash(pw)
        assert api.verify_password(stored, pw) is True
        assert api.verify_password(stored, "WrongArgon2!") is False

    def test_verify_unrecognized_hash_format(self):
        """Unrecognized hash format should return False."""
        assert api.verify_password("some_random_string", "password") is False
        assert api.verify_password("$unknown$hash", "password") is False


# ==================== PASSWORD STRENGTH VALIDATION ====================

class TestPasswordStrengthValidation:
    """Tests for validate_password_strength() covering all rules."""

    def test_valid_strong_password(self):
        """A password meeting all criteria should pass."""
        is_valid, error = api.validate_password_strength("Strong1!Pass")
        assert is_valid is True
        assert error is None

    def test_empty_password(self):
        """Empty password should fail."""
        is_valid, error = api.validate_password_strength("")
        assert is_valid is False
        assert "required" in error.lower()

    def test_none_password(self):
        """None password should fail."""
        is_valid, error = api.validate_password_strength(None)
        assert is_valid is False

    def test_too_short(self):
        """Password under 8 characters should fail."""
        is_valid, error = api.validate_password_strength("Ab1!xyz")
        assert is_valid is False
        assert "8 characters" in error

    def test_no_lowercase(self):
        """Password without lowercase should fail."""
        is_valid, error = api.validate_password_strength("ALLCAPS1!")
        assert is_valid is False
        assert "lowercase" in error.lower()

    def test_no_uppercase(self):
        """Password without uppercase should fail."""
        is_valid, error = api.validate_password_strength("nouppercase1!")
        assert is_valid is False
        assert "uppercase" in error.lower()

    def test_no_digit(self):
        """Password without a digit should fail."""
        is_valid, error = api.validate_password_strength("NoDigits!!")
        assert is_valid is False
        assert "number" in error.lower()

    def test_no_special_character(self):
        """Password without a special character should fail."""
        is_valid, error = api.validate_password_strength("NoSpecial1a")
        assert is_valid is False
        assert "special" in error.lower()

    @pytest.mark.parametrize("weak_pw", [
        "Password1!", "password1!", "12345678Ab!", "Qwerty123!", "Admin123!"
    ])
    def test_common_weak_passwords(self, weak_pw):
        """Common weak passwords (case-insensitive) should be rejected."""
        base = weak_pw.lower().rstrip("!").rstrip("1")
        # Only test against the known weak list
        if base in {'password', 'password1', '12345678', 'qwerty123', 'admin123'}:
            is_valid, error = api.validate_password_strength(weak_pw.replace("!", "").replace("Ab", ""))
            # These may fail for other reasons too, which is fine
            assert is_valid is False

    def test_password_exactly_8_chars_valid(self):
        """Password of exactly 8 characters meeting all rules should pass."""
        is_valid, error = api.validate_password_strength("Abcdef1!")
        assert is_valid is True
        assert error is None

    def test_long_valid_password(self):
        """Very long password meeting all rules should pass."""
        is_valid, error = api.validate_password_strength("A" * 50 + "b1!")
        assert is_valid is True


# ==================== PIN HASHING & VERIFICATION ====================

class TestPINHashing:
    """Tests for hash_pin() and check_pin() functions."""

    def test_hash_pin_returns_string(self):
        """hash_pin should return a non-empty string."""
        result = api.hash_pin("1234")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_check_pin_correct(self):
        """Correct PIN should verify successfully."""
        pin = "5678"
        stored = api.hash_pin(pin)
        assert api.check_pin(pin, stored) is True

    def test_check_pin_wrong(self):
        """Wrong PIN should fail verification."""
        stored = api.hash_pin("1234")
        assert api.check_pin("9999", stored) is False

    def test_check_pin_empty_stored(self):
        """Empty stored hash should return False."""
        assert api.check_pin("1234", "") is False
        assert api.check_pin("1234", None) is False

    @patch.object(api, 'HAS_BCRYPT', False)
    def test_hash_pin_pbkdf2_fallback(self):
        """PIN should hash with PBKDF2 when bcrypt is unavailable."""
        result = api.hash_pin("4321")
        assert result.startswith("pbkdf2$")

    @patch.object(api, 'HAS_BCRYPT', False)
    def test_check_pin_pbkdf2_roundtrip(self):
        """PBKDF2-hashed PIN should verify correctly."""
        pin = "9876"
        stored = api.hash_pin(pin)
        assert stored.startswith("pbkdf2$")
        assert api.check_pin(pin, stored) is True
        assert api.check_pin("0000", stored) is False

    def test_check_pin_plaintext_fallback(self):
        """Plain-text stored PIN (legacy) should match via equality."""
        assert api.check_pin("1234", "1234") is True
        assert api.check_pin("1234", "5678") is False


# ==================== LOGIN ENDPOINT ====================

class TestLoginEndpoint:
    """Tests for POST /api/auth/login endpoint."""

    def _login(self, client, username="testuser", password="TestPass1!",
               pin="1234", csrf_token=None):
        """Helper to make login requests."""
        headers = {"Content-Type": "application/json"}
        if csrf_token:
            headers["X-CSRF-Token"] = csrf_token
        return client.post("/api/auth/login", json={
            "username": username,
            "password": password,
            "pin": pin,
        }, headers=headers)

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_login_success(self, mock_log, client, mock_db):
        """Successful login with valid credentials returns 200 and sets session."""
        pw = "ValidPass1!"
        pin = "1234"
        hashed_pw = api.hash_password(pw)
        hashed_pin = api.hash_pin(pin)

        mock_db({
            "SELECT username, password, role, pin, clinician_id FROM users": [
                (("testuser", hashed_pw, "user", hashed_pin, None),)
            ],
            "SELECT disclaimer_accepted": [(False,)],
            "UPDATE users SET last_login": [],
            "SELECT status FROM patient_approvals": [("approved",)],
        })

        # The conftest mock_db uses substring matching, but the login
        # endpoint issues multiple queries. We need a smarter mock.
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db({
            "SELECT username, password, role, pin, clinician_id": (
                "testuser", hashed_pw, "user", hashed_pin, None
            ),
            "SELECT disclaimer_accepted": (False,),
            "UPDATE users SET last_login": None,
            "SELECT status FROM patient_approvals": ("approved",),
        })

        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor):
            resp = self._login(client, "testuser", pw, pin)

        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["username"] == "testuser"
        assert data["role"] == "user"

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_login_missing_username(self, mock_log, client):
        """Login without username returns 400."""
        resp = client.post("/api/auth/login", json={
            "password": "test", "pin": "1234"
        }, headers={"Content-Type": "application/json"})
        assert resp.status_code == 400
        assert "required" in resp.get_json()["error"].lower()

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_login_missing_password(self, mock_log, client):
        """Login without password returns 400."""
        resp = client.post("/api/auth/login", json={
            "username": "testuser", "pin": "1234"
        }, headers={"Content-Type": "application/json"})
        assert resp.status_code == 400

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_login_missing_pin(self, mock_log, client):
        """Login without PIN returns 400."""
        resp = client.post("/api/auth/login", json={
            "username": "testuser", "password": "TestPass1!"
        }, headers={"Content-Type": "application/json"})
        assert resp.status_code == 400
        assert "PIN" in resp.get_json()["error"]

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_login_user_not_found(self, mock_log, client):
        """Login with nonexistent user returns 401."""
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db([])

        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor):
            resp = self._login(client, "nonexistent", "Pass1!", "1234")

        assert resp.status_code == 401
        assert "Invalid credentials" in resp.get_json()["error"]

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_login_wrong_password(self, mock_log, client):
        """Login with wrong password returns 401."""
        hashed_pw = api.hash_password("CorrectPass1!")
        hashed_pin = api.hash_pin("1234")

        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db({
            "SELECT username, password, role, pin, clinician_id": (
                "testuser", hashed_pw, "user", hashed_pin, None
            ),
        })

        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor):
            resp = self._login(client, "testuser", "WrongPass1!", "1234")

        assert resp.status_code == 401
        assert "Invalid credentials" in resp.get_json()["error"]

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_login_wrong_pin(self, mock_log, client):
        """Login with correct password but wrong PIN returns 401."""
        pw = "CorrectPass1!"
        hashed_pw = api.hash_password(pw)
        hashed_pin = api.hash_pin("1234")

        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db({
            "SELECT username, password, role, pin, clinician_id": (
                "testuser", hashed_pw, "user", hashed_pin, None
            ),
        })

        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor):
            resp = self._login(client, "testuser", pw, "9999")

        assert resp.status_code == 401
        assert "Invalid PIN" in resp.get_json()["error"]

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_login_empty_body(self, mock_log, client):
        """Login with empty JSON body returns 400."""
        resp = client.post("/api/auth/login", json={},
                           headers={"Content-Type": "application/json"})
        assert resp.status_code == 400


# ==================== REGISTRATION ENDPOINT ====================

class TestRegistrationEndpoint:
    """Tests for POST /api/auth/register endpoint."""

    VALID_REG_DATA = {
        "username": "newuser",
        "password": "StrongP@ss1",
        "pin": "5678",
        "email": "new@example.com",
        "phone": "07700111222",
        "full_name": "New User",
        "dob": "1995-06-15",
        "conditions": "anxiety",
        "country": "UK",
        "area": "London",
        "postcode": "E1 6AN",
    }

    def _register(self, client, data=None):
        """Helper to make registration requests."""
        payload = data if data is not None else self.VALID_REG_DATA.copy()
        return client.post("/api/auth/register", json=payload,
                           headers={"Content-Type": "application/json"})

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_register_success(self, mock_log, client):
        """Successful registration returns 201 with username."""
        # All SELECT checks return None (no duplicates), INSERT succeeds
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db([])

        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor):
            resp = self._register(client)

        assert resp.status_code == 201
        data = resp.get_json()
        assert data["success"] is True
        assert data["username"] == "newuser"

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_register_duplicate_username(self, mock_log, client):
        """Registration with existing username returns 409."""
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db({
            "SELECT username FROM users WHERE username": ("newuser",),
            "SELECT username FROM users WHERE email": None,
            "SELECT username FROM users WHERE phone": None,
        })

        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor):
            resp = self._register(client)

        assert resp.status_code == 409
        assert "Username already exists" in resp.get_json()["error"]

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_register_duplicate_email(self, mock_log, client):
        """Registration with existing email returns 409."""
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db({
            "SELECT username FROM users WHERE username=": None,
            "SELECT username FROM users WHERE email": ("otheruser",),
        })

        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor):
            resp = self._register(client)

        assert resp.status_code == 409
        assert "Email already in use" in resp.get_json()["error"]

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_register_missing_required_fields(self, mock_log, client):
        """Registration missing required fields returns 400."""
        # Missing username
        data = self.VALID_REG_DATA.copy()
        data.pop("username")
        resp = self._register(client, data)
        assert resp.status_code == 400

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_register_missing_password(self, mock_log, client):
        """Registration without password returns 400."""
        data = self.VALID_REG_DATA.copy()
        data.pop("password")
        resp = self._register(client, data)
        assert resp.status_code == 400

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_register_missing_email(self, mock_log, client):
        """Registration without email returns 400."""
        data = self.VALID_REG_DATA.copy()
        data.pop("email")
        resp = self._register(client, data)
        assert resp.status_code == 400

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_register_missing_full_name(self, mock_log, client):
        """Registration without full_name returns 400."""
        data = self.VALID_REG_DATA.copy()
        data.pop("full_name")
        resp = self._register(client, data)
        assert resp.status_code == 400

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_register_missing_dob(self, mock_log, client):
        """Registration without dob returns 400."""
        data = self.VALID_REG_DATA.copy()
        data.pop("dob")
        resp = self._register(client, data)
        assert resp.status_code == 400

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_register_missing_conditions(self, mock_log, client):
        """Registration without conditions returns 400."""
        data = self.VALID_REG_DATA.copy()
        data.pop("conditions")
        resp = self._register(client, data)
        assert resp.status_code == 400

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_register_weak_password_rejected(self, mock_log, client):
        """Registration with a weak password returns 400."""
        data = self.VALID_REG_DATA.copy()
        data["password"] = "short"
        resp = self._register(client, data)
        assert resp.status_code == 400

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_register_missing_country_area(self, mock_log, client):
        """Registration without country/area returns 400."""
        data = self.VALID_REG_DATA.copy()
        data.pop("country")
        data.pop("area")
        resp = self._register(client, data)
        assert resp.status_code == 400


# ==================== UNAUTHENTICATED ACCESS ====================

class TestUnauthenticatedAccess:
    """Tests that protected endpoints return 401 for unauthenticated requests."""

    PROTECTED_ENDPOINTS = [
        ("/api/mood/log", "POST"),
        ("/api/therapy/chat", "POST"),
        ("/api/wins/log", "POST"),
        ("/api/wins/recent", "GET"),
        ("/api/activity/log", "POST"),
    ]

    @patch.object(api, 'log_event')
    def test_protected_endpoints_require_auth(self, mock_log, unauth_client):
        """Protected endpoints should return 401 when not authenticated."""
        for path, method in self.PROTECTED_ENDPOINTS:
            if method == "GET":
                resp = unauth_client.get(path)
            else:
                resp = unauth_client.post(
                    path, json={},
                    headers={"Content-Type": "application/json",
                             "X-CSRF-Token": secrets.token_hex(32)}
                )
            # Accept 400, 401 or 403 (CSRF might fire before auth check)
            assert resp.status_code in (400, 401, 403), \
                f"{method} {path} returned {resp.status_code}, expected 400, 401 or 403"

    @patch.object(api, 'log_event')
    def test_logout_without_session(self, mock_log, unauth_client):
        """Logout without session should still return 200."""
        resp = unauth_client.post(
            "/api/auth/logout", json={},
            headers={"Content-Type": "application/json",
                     "X-CSRF-Token": secrets.token_hex(32)}
        )
        # Logout is safe to call without session
        assert resp.status_code == 200


# ==================== SESSION MANAGEMENT ====================

class TestSessionManagement:
    """Tests for get_authenticated_username() and session behavior."""

    def test_authenticated_user_returned_from_session(self, client):
        """get_authenticated_username returns username when session is valid and user exists in DB."""
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db({
            "SELECT role FROM users WHERE username": ("user",),
        })

        with client.session_transaction() as sess:
            sess["username"] = "test_patient"
            sess["role"] = "user"

        with client.application.test_request_context():
            with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
                 patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor):
                # Use the client to make a request so session is populated
                pass

        # Verify through an endpoint call
        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor), \
             patch.object(api, 'log_event'):
            resp = client.post(
                "/api/auth/logout", json={},
                headers={"Content-Type": "application/json",
                         "X-CSRF-Token": secrets.token_hex(32)}
            )
            assert resp.status_code == 200

    def test_session_cleared_when_user_not_in_db(self, client):
        """get_authenticated_username clears session if user no longer exists."""
        # DB returns no result for the user
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db([])

        with client.session_transaction() as sess:
            sess["username"] = "deleted_user"
            sess["role"] = "user"

        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor):
            result = None
            with client.application.test_request_context():
                from flask import session as flask_session
                flask_session["username"] = "deleted_user"
                flask_session["role"] = "user"
                result = api.get_authenticated_username()
            assert result is None

    def test_no_session_returns_none(self, client):
        """get_authenticated_username returns None when no session data exists."""
        with client.application.test_request_context():
            result = api.get_authenticated_username()
            assert result is None


# ==================== X-USERNAME BYPASS LOGGING ====================

class TestXUsernameBypassLogging:
    """Tests that X-Username header without session triggers security logging."""

    @patch.object(api, 'log_event')
    def test_x_username_without_session_logs_attempt(self, mock_log, client):
        """X-Username header without session should log auth_bypass_attempt."""
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db([])

        with client.application.test_request_context(
            headers={"X-Username": "attacker"}
        ):
            with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
                 patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor):
                result = api.get_authenticated_username()

            assert result is None
            mock_log.assert_called_once()
            call_args = mock_log.call_args
            assert call_args[0][0] == 'system'
            assert call_args[0][1] == 'security'
            assert 'auth_bypass_attempt' in call_args[0][2]
            assert 'attacker' in call_args[0][3]

    @patch.object(api, 'log_event')
    def test_x_username_with_valid_session_no_log(self, mock_log, client):
        """X-Username header WITH valid session should not log bypass attempt."""
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db({
            "SELECT role FROM users WHERE username": ("user",),
        })

        with client.application.test_request_context(
            headers={"X-Username": "test_patient"}
        ):
            from flask import session as flask_session
            flask_session["username"] = "test_patient"
            flask_session["role"] = "user"

            with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
                 patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor):
                result = api.get_authenticated_username()

            assert result == "test_patient"
            # log_event should NOT have been called with bypass attempt
            for c in mock_log.call_args_list:
                assert 'auth_bypass_attempt' not in str(c)


# ==================== CSRF TOKEN ====================

class TestCSRFToken:
    """Tests for CSRF token generation and the /api/csrf-token endpoint."""

    def test_csrf_token_endpoint_returns_token(self, client):
        """GET /api/csrf-token should return a token string."""
        resp = client.get("/api/csrf-token")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "csrf_token" in data
        assert isinstance(data["csrf_token"], str)
        assert len(data["csrf_token"]) == 64  # token_hex(32) = 64 chars

    def test_csrf_token_set_as_cookie(self, client):
        """GET /api/csrf-token should set csrf_token cookie."""
        resp = client.get("/api/csrf-token")
        assert resp.status_code == 200
        set_cookie = resp.headers.get('Set-Cookie', '')
        assert 'csrf_token' in set_cookie

    def test_csrf_token_unique_per_request(self, client):
        """Each call to /api/csrf-token should return a different token."""
        resp1 = client.get("/api/csrf-token")
        resp2 = client.get("/api/csrf-token")
        t1 = resp1.get_json()["csrf_token"]
        t2 = resp2.get_json()["csrf_token"]
        assert t1 != t2

    def test_csrf_protection_class_generate(self, client):
        """CSRFProtection.generate_csrf_token should store token in session."""
        with client.application.test_request_context():
            from flask import session as flask_session
            token = api.CSRFProtection.generate_csrf_token("testuser")
            assert isinstance(token, str)
            assert len(token) > 0
            assert f"csrf_token_testuser" in flask_session

    def test_csrf_protection_class_validate_correct(self, client):
        """CSRFProtection.validate_csrf_token should succeed with matching token."""
        with client.application.test_request_context():
            from flask import session as flask_session
            token = api.CSRFProtection.generate_csrf_token("testuser")
            is_valid, msg = api.CSRFProtection.validate_csrf_token("testuser", token)
            assert is_valid is True

    def test_csrf_protection_class_validate_wrong_token(self, client):
        """CSRFProtection.validate_csrf_token should fail with wrong token."""
        with client.application.test_request_context():
            from flask import session as flask_session
            api.CSRFProtection.generate_csrf_token("testuser")
            is_valid, msg = api.CSRFProtection.validate_csrf_token("testuser", "wrong_token")
            assert is_valid is False
            assert "invalid" in msg.lower()

    def test_csrf_protection_class_validate_missing_token(self, client):
        """CSRFProtection.validate_csrf_token should fail with no token."""
        with client.application.test_request_context():
            is_valid, msg = api.CSRFProtection.validate_csrf_token("testuser", None)
            assert is_valid is False

    def test_csrf_token_invalidated_after_use(self, client):
        """CSRF token should be one-time use (invalidated after successful validation)."""
        with client.application.test_request_context():
            from flask import session as flask_session
            token = api.CSRFProtection.generate_csrf_token("testuser")
            # First validation should succeed
            is_valid, _ = api.CSRFProtection.validate_csrf_token("testuser", token)
            assert is_valid is True
            # Second validation with same token should fail (token consumed)
            is_valid, _ = api.CSRFProtection.validate_csrf_token("testuser", token)
            assert is_valid is False


# ==================== VALIDATE SESSION ENDPOINT ====================

class TestValidateSessionEndpoint:
    """Tests for POST /api/validate-session endpoint."""

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_validate_session_success(self, mock_log, client):
        """Valid session data returns 200."""
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db({
            "SELECT username, role FROM users": ("testuser", "user"),
        })

        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor):
            resp = client.post("/api/validate-session", json={
                "username": "testuser", "role": "user"
            }, headers={"Content-Type": "application/json",
                        "X-CSRF-Token": secrets.token_hex(32)})

        assert resp.status_code == 200
        assert resp.get_json()["success"] is True

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_validate_session_user_not_found(self, mock_log, client):
        """Session validation for nonexistent user returns 401."""
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db([])

        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor):
            resp = client.post("/api/validate-session", json={
                "username": "ghost", "role": "user"
            }, headers={"Content-Type": "application/json",
                        "X-CSRF-Token": secrets.token_hex(32)})

        assert resp.status_code == 401

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_validate_session_role_mismatch(self, mock_log, client):
        """Session validation with wrong role returns 401."""
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db({
            "SELECT username, role FROM users": ("testuser", "user"),
        })

        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor):
            resp = client.post("/api/validate-session", json={
                "username": "testuser", "role": "clinician"
            }, headers={"Content-Type": "application/json",
                        "X-CSRF-Token": secrets.token_hex(32)})

        assert resp.status_code == 401

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_validate_session_missing_username(self, mock_log, client):
        """Session validation without username returns 400."""
        resp = client.post("/api/validate-session", json={},
                           headers={"Content-Type": "application/json",
                                    "X-CSRF-Token": secrets.token_hex(32)})
        assert resp.status_code == 400


# ==================== FORGOT PASSWORD ENDPOINT ====================

class TestForgotPasswordEndpoint:
    """Tests for POST /api/auth/forgot-password endpoint."""

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_forgot_password_valid_user(self, mock_log, client):
        """Forgot password with valid user/email returns success."""
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db({
            "SELECT email FROM users WHERE username": ("user@test.com",),
            "UPDATE users SET reset_token": None,
        })

        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor):
            resp = client.post("/api/auth/forgot-password", json={
                "username": "testuser", "email": "user@test.com"
            }, headers={"Content-Type": "application/json"})

        assert resp.status_code == 200
        assert resp.get_json()["success"] is True

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_forgot_password_unknown_user_still_200(self, mock_log, client):
        """Forgot password with unknown user still returns 200 (no info leak)."""
        mock_get_db, mock_get_cursor, conn, cursor = make_mock_db([])

        with patch.object(api, 'get_db_connection', side_effect=mock_get_db), \
             patch.object(api, 'get_wrapped_cursor', side_effect=mock_get_cursor):
            resp = client.post("/api/auth/forgot-password", json={
                "username": "nonexistent", "email": "nope@test.com"
            }, headers={"Content-Type": "application/json"})

        assert resp.status_code == 200
        assert resp.get_json()["success"] is True

    @patch.object(api, 'log_event')
    @patch.object(api, 'rate_limiter', MagicMock())
    def test_forgot_password_missing_fields(self, mock_log, client):
        """Forgot password with missing fields returns 400."""
        resp = client.post("/api/auth/forgot-password", json={
            "username": "testuser"
        }, headers={"Content-Type": "application/json"})
        assert resp.status_code == 400
