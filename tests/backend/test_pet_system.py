"""
Tests for Virtual Pet System endpoints.

Covers:
  - GET  /api/pet/status
  - POST /api/pet/create
  - POST /api/pet/feed
  - POST /api/pet/reward
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import time

import api
from tests.conftest import make_mock_db


# ==================== PET STATUS (GET /api/pet/status) ====================

class TestPetStatus:
    """Tests for GET /api/pet/status"""

    def test_pet_status_exists(self, client, mock_db):
        """Returns pet data when pet exists."""
        now = time.time()
        conn, cursor = mock_db({
            'SELECT username FROM users': [('test_patient',)],
            'SELECT * FROM pet': [(1, 'test_patient', 'Buddy', 'Dog', 'Male',
                                    80, 75, 60, 90, 50, 100, 'Child', 0, now, 'None')],
        })

        with patch.object(api, 'get_pet_db_connection', return_value=conn), \
             patch.object(api, 'ensure_pet_table'):
            resp = client.get('/api/pet/status?username=test_patient')

        data = resp.get_json()
        assert resp.status_code == 200
        assert data['exists'] is True
        assert data['pet']['name'] == 'Buddy'
        assert data['pet']['species'] == 'Dog'

    def test_pet_status_no_pet(self, client, mock_db):
        """Returns exists=False when no pet found."""
        conn, cursor = mock_db({
            'SELECT username FROM users': [('test_patient',)],
            'SELECT * FROM pet': [],
        })

        with patch.object(api, 'get_pet_db_connection', return_value=conn), \
             patch.object(api, 'ensure_pet_table'):
            resp = client.get('/api/pet/status?username=test_patient')

        data = resp.get_json()
        assert resp.status_code == 200
        assert data['exists'] is False

    def test_pet_status_no_username(self, client, mock_db):
        """Missing username returns exists=False with error."""
        conn, cursor = mock_db({
            'SELECT username FROM users': [],
        })

        resp = client.get('/api/pet/status')
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['exists'] is False

    def test_pet_status_user_not_found(self, client, mock_db):
        """Non-existent user returns exists=False."""
        conn, cursor = mock_db({
            'SELECT username FROM users': [],
        })

        resp = client.get('/api/pet/status?username=nobody')
        data = resp.get_json()
        assert resp.status_code == 200
        assert data['exists'] is False


# ==================== PET CREATE (POST /api/pet/create) ====================

class TestPetCreate:
    """Tests for POST /api/pet/create"""

    def test_create_pet_success(self, client, mock_db):
        """Valid pet creation returns 201."""
        conn, cursor = mock_db({
            'SELECT username FROM users': [('test_patient',)],
            'INSERT INTO pet': [],
        })

        with patch.object(api, 'get_pet_db_connection', return_value=conn), \
             patch.object(api, 'ensure_pet_table'):
            resp = client.post('/api/pet/create', json={
                'username': 'test_patient',
                'name': 'Buddy',
                'species': 'Dog',
                'gender': 'Male',
            })

        data = resp.get_json()
        assert resp.status_code == 201
        assert data['success'] is True

    def test_create_pet_missing_name(self, client, mock_db):
        """Missing pet name returns 400."""
        conn, cursor = mock_db({
            'SELECT username FROM users': [('test_patient',)],
        })

        resp = client.post('/api/pet/create', json={
            'username': 'test_patient',
        })
        assert resp.status_code == 400

    def test_create_pet_user_not_found(self, client, mock_db):
        """Non-existent user returns 401."""
        conn, cursor = mock_db({
            'SELECT username FROM users': [],
        })

        resp = client.post('/api/pet/create', json={
            'username': 'nobody',
            'name': 'Buddy',
        })
        assert resp.status_code == 401


# ==================== PET FEED (POST /api/pet/feed) ====================

class TestPetFeed:
    """Tests for POST /api/pet/feed"""

    def test_feed_pet_success(self, client, mock_db):
        """Feeding pet with enough coins succeeds."""
        now = time.time()
        conn, cursor = mock_db({
            'SELECT username FROM users': [('test_patient',)],
            'SELECT * FROM pet': [(1, 'test_patient', 'Buddy', 'Dog', 'Male',
                                    50, 75, 60, 90, 100, 50, 'Baby', 0, now, 'None')],
            'UPDATE pet': [],
        })

        with patch.object(api, 'get_pet_db_connection', return_value=conn):
            resp = client.post('/api/pet/feed', json={
                'username': 'test_patient',
                'cost': 10,
            })

        data = resp.get_json()
        assert resp.status_code == 200
        assert data['success'] is True
        assert data['new_hunger'] == 80  # 50 + 30
        assert data['coins'] == 90  # 100 - 10

    def test_feed_pet_not_enough_coins(self, client, mock_db):
        """Feeding pet without enough coins returns 400."""
        now = time.time()
        conn, cursor = mock_db({
            'SELECT username FROM users': [('test_patient',)],
            'SELECT * FROM pet': [(1, 'test_patient', 'Buddy', 'Dog', 'Male',
                                    50, 75, 60, 90, 5, 50, 'Baby', 0, now, 'None')],
        })

        with patch.object(api, 'get_pet_db_connection', return_value=conn):
            resp = client.post('/api/pet/feed', json={
                'username': 'test_patient',
                'cost': 10,
            })

        assert resp.status_code == 400
        assert 'coins' in resp.get_json()['error'].lower()

    def test_feed_pet_no_pet(self, client, mock_db):
        """Feeding non-existent pet returns 404."""
        conn, cursor = mock_db({
            'SELECT username FROM users': [('test_patient',)],
            'SELECT * FROM pet': [],
        })

        with patch.object(api, 'get_pet_db_connection', return_value=conn):
            resp = client.post('/api/pet/feed', json={
                'username': 'test_patient',
                'cost': 10,
            })

        assert resp.status_code == 404


# ==================== PET REWARD (POST /api/pet/reward) ====================

class TestPetReward:
    """Tests for POST /api/pet/reward"""

    def test_reward_pet_unauthenticated(self, unauth_client, mock_db):
        """Unauthenticated request returns 401."""
        resp = unauth_client.post('/api/pet/reward', json={
            'action': 'mood',
        })
        assert resp.status_code == 401

    def test_reward_pet_user_not_found(self, auth_patient, mock_db):
        """Non-existent user pet returns gracefully."""
        conn, cursor = mock_db({
            'SELECT username FROM users': [],
        })
        client, _ = auth_patient

        resp = client.post('/api/pet/reward', json={
            'action': 'mood',
        })
        # Returns 200 with success=False when user not found for pet
        assert resp.status_code == 200
