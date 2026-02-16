"""
Tests for InputValidator and CSRFProtection classes in api.py.

Covers text validation, message/note validation, integer/range validation,
mood/sleep/anxiety validators, title/username validation, CSRF token
generation, validation, expiry, and the require_csrf decorator.
"""

import pytest
from unittest.mock import patch, MagicMock

import api
from api import InputValidator, CSRFProtection


# ==================== InputValidator.validate_text ====================


class TestValidateText:
    """Tests for InputValidator.validate_text static method."""

    def test_valid_text(self):
        result, error = InputValidator.validate_text("hello world")
        assert result == "hello world"
        assert error is None

    def test_valid_text_strips_whitespace(self):
        result, error = InputValidator.validate_text("  hello  ")
        assert result == "hello"
        assert error is None

    def test_none_returns_error(self):
        result, error = InputValidator.validate_text(None)
        assert result is None
        assert "cannot be None" in error

    def test_empty_string_too_short(self):
        result, error = InputValidator.validate_text("")
        assert result is None
        assert "at least 1 character" in error

    def test_whitespace_only_too_short(self):
        result, error = InputValidator.validate_text("   ")
        assert result is None
        assert "at least 1 character" in error

    def test_too_long(self):
        long_text = "a" * 1001
        result, error = InputValidator.validate_text(long_text, max_length=1000)
        assert result is None
        assert "cannot exceed 1000 characters" in error

    def test_exact_max_length(self):
        text = "a" * 1000
        result, error = InputValidator.validate_text(text, max_length=1000)
        assert result == text
        assert error is None

    def test_custom_field_name_in_error(self):
        result, error = InputValidator.validate_text(None, field_name="bio")
        assert "bio" in error

    def test_custom_min_length(self):
        result, error = InputValidator.validate_text("ab", min_length=5, field_name="name")
        assert result is None
        assert "at least 5 character" in error

    def test_non_string_converted(self):
        result, error = InputValidator.validate_text(12345, max_length=100)
        assert result == "12345"
        assert error is None


# ==================== InputValidator.validate_message ====================


class TestValidateMessage:
    """Tests for InputValidator.validate_message."""

    def test_valid_message(self):
        result, error = InputValidator.validate_message("I feel good today")
        assert result == "I feel good today"
        assert error is None

    def test_none_message(self):
        result, error = InputValidator.validate_message(None)
        assert result is None
        assert "required" in error

    def test_empty_string(self):
        result, error = InputValidator.validate_message("")
        assert result is None
        assert "required" in error

    def test_non_string_integer(self):
        result, error = InputValidator.validate_message(42)
        assert result is None
        assert "must be a string" in error

    def test_too_long_message(self):
        long_msg = "x" * 10001
        result, error = InputValidator.validate_message(long_msg)
        assert result is None
        assert "cannot exceed" in error

    def test_max_length_message(self):
        msg = "y" * 10000
        result, error = InputValidator.validate_message(msg)
        assert result == msg
        assert error is None


# ==================== InputValidator.validate_note ====================


class TestValidateNote:
    """Tests for InputValidator.validate_note."""

    def test_valid_note(self):
        result, error = InputValidator.validate_note("Patient shows improvement")
        assert result == "Patient shows improvement"
        assert error is None

    def test_none_note(self):
        result, error = InputValidator.validate_note(None)
        assert result is None
        assert "required" in error

    def test_empty_note(self):
        result, error = InputValidator.validate_note("")
        assert result is None
        assert "required" in error

    def test_non_string_note(self):
        result, error = InputValidator.validate_note(123)
        assert result is None
        assert "must be a string" in error

    def test_too_long_note(self):
        long_note = "z" * 50001
        result, error = InputValidator.validate_note(long_note)
        assert result is None
        assert "cannot exceed" in error

    def test_max_length_note(self):
        note = "a" * 50000
        result, error = InputValidator.validate_note(note)
        assert result == note
        assert error is None


# ==================== InputValidator.validate_integer ====================


class TestValidateInteger:
    """Tests for InputValidator.validate_integer."""

    def test_valid_integer(self):
        result, error = InputValidator.validate_integer(5, min_val=1, max_val=10)
        assert result == 5
        assert error is None

    def test_string_integer(self):
        result, error = InputValidator.validate_integer("7", min_val=1, max_val=10)
        assert result == 7
        assert error is None

    def test_below_min(self):
        result, error = InputValidator.validate_integer(0, min_val=1, max_val=10)
        assert result is None
        assert "at least 1" in error

    def test_above_max(self):
        result, error = InputValidator.validate_integer(11, min_val=1, max_val=10)
        assert result is None
        assert "cannot exceed 10" in error

    def test_non_integer_string(self):
        result, error = InputValidator.validate_integer("abc")
        assert result is None
        assert "must be an integer" in error

    def test_none_value(self):
        result, error = InputValidator.validate_integer(None)
        assert result is None
        assert "must be an integer" in error

    def test_no_range_limits(self):
        result, error = InputValidator.validate_integer(999)
        assert result == 999
        assert error is None

    def test_custom_field_name(self):
        result, error = InputValidator.validate_integer("abc", field_name="score")
        assert "score" in error


# ==================== InputValidator.validate_mood ====================


class TestValidateMood:
    """Tests for InputValidator.validate_mood (1-10 range)."""

    def test_valid_mood_min(self):
        result, error = InputValidator.validate_mood(1)
        assert result == 1
        assert error is None

    def test_valid_mood_max(self):
        result, error = InputValidator.validate_mood(10)
        assert result == 10
        assert error is None

    def test_mood_below_range(self):
        result, error = InputValidator.validate_mood(0)
        assert result is None
        assert "at least 1" in error

    def test_mood_above_range(self):
        result, error = InputValidator.validate_mood(11)
        assert result is None
        assert "cannot exceed 10" in error


# ==================== InputValidator.validate_sleep ====================


class TestValidateSleep:
    """Tests for InputValidator.validate_sleep (0-10 range)."""

    def test_valid_sleep_min(self):
        result, error = InputValidator.validate_sleep(0)
        assert result == 0
        assert error is None

    def test_valid_sleep_max(self):
        result, error = InputValidator.validate_sleep(10)
        assert result == 10
        assert error is None

    def test_sleep_below_range(self):
        result, error = InputValidator.validate_sleep(-1)
        assert result is None
        assert "at least 0" in error

    def test_sleep_above_range(self):
        result, error = InputValidator.validate_sleep(11)
        assert result is None
        assert "cannot exceed 10" in error


# ==================== InputValidator.validate_anxiety ====================


class TestValidateAnxiety:
    """Tests for InputValidator.validate_anxiety (0-10 range)."""

    def test_valid_anxiety_min(self):
        result, error = InputValidator.validate_anxiety(0)
        assert result == 0
        assert error is None

    def test_valid_anxiety_max(self):
        result, error = InputValidator.validate_anxiety(10)
        assert result == 10
        assert error is None

    def test_anxiety_below_range(self):
        result, error = InputValidator.validate_anxiety(-1)
        assert result is None
        assert "at least 0" in error

    def test_anxiety_above_range(self):
        result, error = InputValidator.validate_anxiety(11)
        assert result is None
        assert "cannot exceed 10" in error


# ==================== InputValidator.validate_title ====================


class TestValidateTitle:
    """Tests for InputValidator.validate_title."""

    def test_valid_title(self):
        result, error = InputValidator.validate_title("My Journal Entry")
        assert result == "My Journal Entry"
        assert error is None

    def test_empty_title(self):
        result, error = InputValidator.validate_title("")
        assert result is None
        assert "required" in error

    def test_none_title(self):
        result, error = InputValidator.validate_title(None)
        assert result is None
        assert "required" in error

    def test_too_long_title(self):
        long_title = "t" * 501
        result, error = InputValidator.validate_title(long_title)
        assert result is None
        assert "cannot exceed" in error

    def test_max_length_title(self):
        title = "t" * 500
        result, error = InputValidator.validate_title(title)
        assert result == title
        assert error is None

    def test_non_string_title(self):
        result, error = InputValidator.validate_title(999)
        assert result is None
        assert "must be a string" in error


# ==================== InputValidator.validate_username ====================


class TestValidateUsername:
    """Tests for InputValidator.validate_username."""

    def test_valid_username(self):
        result, error = InputValidator.validate_username("john_doe")
        assert result == "john_doe"
        assert error is None

    def test_too_short_username(self):
        result, error = InputValidator.validate_username("ab")
        assert result is None
        assert "at least 3 character" in error

    def test_too_long_username(self):
        long_name = "u" * 101
        result, error = InputValidator.validate_username(long_name)
        assert result is None
        assert "cannot exceed" in error

    def test_none_username(self):
        result, error = InputValidator.validate_username(None)
        assert result is None
        assert "required" in error

    def test_empty_username(self):
        result, error = InputValidator.validate_username("")
        assert result is None
        assert "required" in error

    def test_min_length_username(self):
        result, error = InputValidator.validate_username("abc")
        assert result == "abc"
        assert error is None

    def test_non_string_username(self):
        result, error = InputValidator.validate_username(42)
        assert result is None
        assert "must be a string" in error


# ==================== CSRFProtection.generate_csrf_token ====================


class TestCSRFGenerateToken:
    """Tests for CSRFProtection.generate_csrf_token."""

    def test_generates_token_string(self, app):
        with app.test_request_context():
            from flask import session
            token = CSRFProtection.generate_csrf_token("testuser")
            assert isinstance(token, str)
            assert len(token) > 20  # url-safe base64 of 32 bytes

    def test_stores_token_in_session(self, app):
        with app.test_request_context():
            from flask import session
            token = CSRFProtection.generate_csrf_token("testuser")
            token_data = session.get("csrf_token_testuser")
            assert token_data is not None
            assert token_data["token"] == token
            assert token_data["attempts"] == 0
            assert "created_at" in token_data

    def test_different_users_get_different_tokens(self, app):
        with app.test_request_context():
            token1 = CSRFProtection.generate_csrf_token("user_a")
            token2 = CSRFProtection.generate_csrf_token("user_b")
            assert token1 != token2


# ==================== CSRFProtection.validate_csrf_token ====================


class TestCSRFValidateToken:
    """Tests for CSRFProtection.validate_csrf_token."""

    def test_valid_token(self, app):
        with app.test_request_context():
            token = CSRFProtection.generate_csrf_token("testuser")
            is_valid, msg = CSRFProtection.validate_csrf_token("testuser", token)
            assert is_valid is True
            assert "valid" in msg.lower()

    def test_invalid_token(self, app):
        with app.test_request_context():
            CSRFProtection.generate_csrf_token("testuser")
            is_valid, msg = CSRFProtection.validate_csrf_token("testuser", "wrong_token")
            assert is_valid is False
            assert "invalid" in msg.lower()

    def test_missing_token_none(self, app):
        with app.test_request_context():
            CSRFProtection.generate_csrf_token("testuser")
            is_valid, msg = CSRFProtection.validate_csrf_token("testuser", None)
            assert is_valid is False
            assert "missing" in msg.lower()

    def test_missing_username(self, app):
        with app.test_request_context():
            is_valid, msg = CSRFProtection.validate_csrf_token(None, "some_token")
            assert is_valid is False
            assert "missing" in msg.lower()

    def test_no_token_in_session(self, app):
        with app.test_request_context():
            is_valid, msg = CSRFProtection.validate_csrf_token("unknown_user", "tok")
            assert is_valid is False
            assert "no csrf token in session" in msg.lower()

    def test_token_consumed_after_use(self, app):
        with app.test_request_context():
            from flask import session
            token = CSRFProtection.generate_csrf_token("testuser")
            CSRFProtection.validate_csrf_token("testuser", token)
            # Token should be removed from session after successful validation
            assert session.get("csrf_token_testuser") is None

    def test_too_many_attempts(self, app):
        with app.test_request_context():
            from flask import session
            token = CSRFProtection.generate_csrf_token("testuser")
            # Manually set attempts to 10 so next call triggers the limit
            session["csrf_token_testuser"]["attempts"] = 10
            is_valid, msg = CSRFProtection.validate_csrf_token("testuser", "bad")
            assert is_valid is False
            assert "too many times" in msg.lower()
            # Token data should be removed
            assert session.get("csrf_token_testuser") is None


# ==================== CSRFProtection.require_csrf decorator ====================


class TestRequireCSRFDecorator:
    """Tests for the require_csrf decorator behaviour via existing Flask routes."""

    def test_get_request_allowed_without_token(self, client):
        """GET requests should pass through without CSRF check."""
        resp = client.get("/api/csrf-token")
        assert resp.status_code == 200

    def test_post_requires_auth_when_csrf_enforced(self, unauth_client):
        """POST to a CSRF-protected route without auth returns 401 or 403."""
        with patch.dict('os.environ', {'TESTING': '0'}):
            resp = unauth_client.post("/api/mood/log", json={
                'username': 'test',
                'mood': 5,
            })
            # Without auth, CSRF decorator returns 401; other checks may return 400/403
            assert resp.status_code in (400, 401, 403)

    def test_post_bypasses_csrf_in_testing_mode(self, auth_patient, mock_db):
        """In TESTING mode, POST without CSRF token is allowed."""
        client, patient = auth_patient
        mock_db({
            'SELECT': [],
            'INSERT': [(1,)],
        })
        with patch.object(api, 'update_ai_memory'), \
             patch.object(api, 'reward_pet'), \
             patch.object(api, 'mark_daily_task_complete'), \
             patch.object(api, 'log_event'):
            resp = client.post("/api/mood/log", json={
                'username': patient['username'],
                'mood': 5,
                'sleep': 7,
                'anxiety': 3,
            })
        # Should pass CSRF check (bypassed in TESTING mode)
        assert resp.status_code in (200, 201, 400)

    def test_post_with_invalid_token_returns_error(self, unauth_client):
        """POST with an invalid CSRF token returns 401 or 403 (when TESTING is off)."""
        with patch.dict('os.environ', {'TESTING': '0'}), \
             patch.object(api, 'log_event'):
            resp = unauth_client.post("/api/mood/log", json={
                'username': 'test_patient',
                'mood': 5,
            }, headers={"X-CSRF-Token": "totally_wrong_token"})
            # Should fail auth or CSRF validation
            assert resp.status_code in (400, 401, 403)

    def test_csrf_token_generation_works(self, client):
        """CSRF token endpoint generates valid tokens."""
        resp = client.get("/api/csrf-token")
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'csrf_token' in data
        assert len(data['csrf_token']) == 64
