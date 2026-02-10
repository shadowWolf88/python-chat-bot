"""
Tests for Chat Export and Data Export endpoints.

Covers:
  - POST /api/therapy/export (chat history export in txt/json/csv)
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

import api
from tests.conftest import make_mock_db


# ==================== CHAT EXPORT (POST /api/therapy/export) ====================

class TestChatExport:
    """Tests for POST /api/therapy/export"""

    def test_export_txt_success(self, client, mock_db):
        """Text export returns plain text attachment."""
        now = datetime.now().isoformat()
        conn, cursor = mock_db([
            ('user', 'Hello', now),
            ('ai', 'Hi there', now),
        ])

        resp = client.post('/api/therapy/export', json={
            'username': 'test_patient',
            'from_date': '2026-01-01',
            'to_date': '2026-02-28',
            'format': 'txt',
        })

        assert resp.status_code == 200
        assert 'text/plain' in resp.content_type
        assert 'attachment' in resp.headers.get('Content-Disposition', '')

    def test_export_json_success(self, client, mock_db):
        """JSON export returns JSON attachment."""
        now = datetime.now().isoformat()
        conn, cursor = mock_db([
            ('user', 'Hello', now),
        ])

        resp = client.post('/api/therapy/export', json={
            'username': 'test_patient',
            'from_date': '2026-01-01',
            'to_date': '2026-02-28',
            'format': 'json',
        })

        assert resp.status_code == 200
        assert 'json' in resp.content_type

    def test_export_csv_success(self, client, mock_db):
        """CSV export returns CSV attachment."""
        now = datetime.now().isoformat()
        conn, cursor = mock_db([
            ('user', 'Hello', now),
        ])

        resp = client.post('/api/therapy/export', json={
            'username': 'test_patient',
            'from_date': '2026-01-01',
            'to_date': '2026-02-28',
            'format': 'csv',
        })

        assert resp.status_code == 200
        assert 'csv' in resp.content_type

    def test_export_missing_username(self, client, mock_db):
        """Missing username returns 400."""
        resp = client.post('/api/therapy/export', json={
            'from_date': '2026-01-01',
            'to_date': '2026-02-28',
        })
        assert resp.status_code == 400

    def test_export_missing_dates(self, client, mock_db):
        """Missing date range returns 400."""
        resp = client.post('/api/therapy/export', json={
            'username': 'test_patient',
        })
        assert resp.status_code == 400

    def test_export_empty_history(self, client, mock_db):
        """Empty history returns empty export."""
        conn, cursor = mock_db([])

        resp = client.post('/api/therapy/export', json={
            'username': 'test_patient',
            'from_date': '2026-01-01',
            'to_date': '2026-02-28',
            'format': 'json',
        })

        assert resp.status_code == 200

    def test_export_with_session_id(self, client, mock_db):
        """Export with specific chat_session_id works."""
        now = datetime.now().isoformat()
        conn, cursor = mock_db([
            ('user', 'Session msg', now),
        ])

        resp = client.post('/api/therapy/export', json={
            'username': 'test_patient',
            'from_date': '2026-01-01',
            'to_date': '2026-02-28',
            'format': 'txt',
            'chat_session_id': 5,
        })

        assert resp.status_code == 200
