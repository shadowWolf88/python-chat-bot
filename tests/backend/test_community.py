"""
Tests for Community Forum endpoints.

Covers: GET /api/community/posts, GET /api/community/channels,
POST /api/community/post, POST /api/community/post/<id>/reply,
POST /api/community/post/<id>/like, POST /api/community/post/<id>/react,
POST /api/community/post/<id>/pin, DELETE /api/community/post/<id>,
POST /api/community/post/<id>/report, GET /api/community/post/<id>/replies,
DELETE /api/community/reply/<id>
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

import api


# ==================== HELPER: DB MOCK SETUP ====================

def _mock_db():
    """Return (mock_conn, mock_cursor) with patchers started."""
    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    mock_connection.close = MagicMock()
    mock_connection.commit = MagicMock()
    mock_connection.rollback = MagicMock()

    # Make cursor chainable: cur.execute(...).fetchall() / .fetchone()
    mock_cursor.execute.return_value = mock_cursor

    p1 = patch.object(api, 'get_db_connection', return_value=mock_connection)
    p2 = patch.object(api, 'get_wrapped_cursor', return_value=mock_cursor)
    return p1, p2, mock_connection, mock_cursor


# ==================== GET /api/community/posts ====================

class TestGetCommunityPosts:
    """Tests for listing community posts."""

    def test_get_posts_success(self, client):
        """Should return a list of posts with reactions and replies."""
        p1, p2, mock_conn, mock_cursor = _mock_db()

        now = datetime.now().isoformat()
        # First fetchall returns posts
        mock_cursor.fetchall.side_effect = [
            [(1, 'user1', 'Hello world', 5, now, 'general', 0)],  # posts
            [('like', 3), ('heart', 2)],  # reactions for post 1
            [],   # user_reactions
            [(10, 'user2', 'Nice post!', now)],  # replies for post 1
        ]
        mock_cursor.fetchone.return_value = None

        with p1, p2:
            resp = client.get('/api/community/posts')

        assert resp.status_code == 200
        data = resp.get_json()
        assert 'posts' in data
        assert 'categories' in data

    def test_get_posts_with_category_filter(self, client):
        """Should filter posts by category when provided."""
        p1, p2, mock_conn, mock_cursor = _mock_db()

        mock_cursor.fetchall.return_value = []
        mock_cursor.fetchone.return_value = None

        with p1, p2:
            resp = client.get('/api/community/posts?category=anxiety')

        assert resp.status_code == 200
        data = resp.get_json()
        assert 'posts' in data

    def test_get_posts_empty(self, client):
        """Should return empty list when no posts exist."""
        p1, p2, mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchall.return_value = []
        mock_cursor.fetchone.return_value = None

        with p1, p2:
            resp = client.get('/api/community/posts')

        assert resp.status_code == 200
        data = resp.get_json()
        assert data['posts'] == []


# ==================== GET /api/community/channels ====================

class TestGetCommunityChannels:
    """Tests for listing community channels."""

    def test_get_channels_success(self, client):
        """Should return all channels with post counts."""
        p1, p2, mock_conn, mock_cursor = _mock_db()

        # Each channel queries: COUNT(*), MAX(timestamp), possibly unread
        mock_cursor.fetchone.return_value = (0,)

        with p1, p2:
            resp = client.get('/api/community/channels')

        assert resp.status_code == 200
        data = resp.get_json()
        assert 'channels' in data
        assert len(data['channels']) == 14  # 14 valid categories


# ==================== POST /api/community/post ====================

class TestCreateCommunityPost:
    """Tests for creating a community post."""

    def test_create_post_success(self, client):
        """Should create a post and return 201."""
        p1, p2, mock_conn, mock_cursor = _mock_db()

        with p1, p2, patch.object(api, 'update_ai_memory'):
            resp = client.post('/api/community/post',
                               json={'username': 'test_patient',
                                     'message': 'Feeling better today!',
                                     'category': 'celebration'})

        assert resp.status_code == 201
        data = resp.get_json()
        assert data['success'] is True

    def test_create_post_missing_username(self, client):
        """Should return 400 when username is missing."""
        resp = client.post('/api/community/post',
                           json={'message': 'Hello', 'category': 'general'})
        assert resp.status_code == 400

    def test_create_post_missing_message(self, client):
        """Should return 400 when message is empty."""
        resp = client.post('/api/community/post',
                           json={'username': 'test_patient',
                                 'message': '',
                                 'category': 'general'})
        assert resp.status_code == 400

    def test_create_post_invalid_category(self, client):
        """Should return 400 for invalid category."""
        resp = client.post('/api/community/post',
                           json={'username': 'test_patient',
                                 'message': 'Hello',
                                 'category': 'invalid_cat'})
        assert resp.status_code == 400
        data = resp.get_json()
        assert 'valid_categories' in data

    def test_create_post_message_too_long(self, client):
        """Should return 400 when message exceeds 2000 chars."""
        resp = client.post('/api/community/post',
                           json={'username': 'test_patient',
                                 'message': 'x' * 2001,
                                 'category': 'general'})
        assert resp.status_code == 400


# ==================== POST /api/community/post/<id>/reply ====================

class TestCreateReply:
    """Tests for replying to a community post."""

    def test_reply_success(self, client):
        """Should create a reply and return 201."""
        p1, p2, mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = (42,)  # reply_id from RETURNING

        moderation_result = {
            'allowed': True,
            'flagged': False,
            'filtered_text': 'Great post!',
            'flag_reason': None
        }

        with p1, p2, \
             patch.object(api, 'content_moderator') as mock_mod, \
             patch.object(api, 'log_event'):
            mock_mod.moderate.return_value = moderation_result
            resp = client.post('/api/community/post/1/reply',
                               json={'username': 'test_patient',
                                     'message': 'Great post!'})

        assert resp.status_code == 201
        data = resp.get_json()
        assert data['success'] is True
        assert data['reply_id'] == 42

    def test_reply_missing_message(self, client):
        """Should return 400 when message is missing."""
        resp = client.post('/api/community/post/1/reply',
                           json={'username': 'test_patient', 'message': ''})
        assert resp.status_code == 400

    def test_reply_missing_username(self, client):
        """Should return 400 when username is missing."""
        resp = client.post('/api/community/post/1/reply',
                           json={'message': 'Hello'})
        assert resp.status_code == 400

    def test_reply_blocked_by_moderation(self, client):
        """Should return 400 when content moderation blocks the reply."""
        moderation_result = {
            'allowed': False,
            'flagged': False,
            'filtered_text': '',
            'reason': 'Content violates community guidelines'
        }

        with patch.object(api, 'content_moderator') as mock_mod, \
             patch.object(api, 'log_event'):
            mock_mod.moderate.return_value = moderation_result
            resp = client.post('/api/community/post/1/reply',
                               json={'username': 'test_patient',
                                     'message': 'Bad content here'})

        assert resp.status_code == 400
        data = resp.get_json()
        assert 'error' in data


# ==================== POST /api/community/post/<id>/like ====================

class TestLikePost:
    """Tests for liking/unliking a community post."""

    def test_like_post_success(self, client):
        """Should toggle like and return success."""
        p1, p2, mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.side_effect = [None, (1,)]  # no existing like, then count

        with p1, p2:
            resp = client.post('/api/community/post/1/like',
                               json={'username': 'test_patient'})

        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True

    def test_like_post_missing_username(self, client):
        """Should return 400 when username is missing."""
        resp = client.post('/api/community/post/1/like', json={})
        assert resp.status_code == 400


# ==================== POST /api/community/post/<id>/react ====================

class TestReactToPost:
    """Tests for adding reactions to a community post."""

    def test_react_success(self, client):
        """Should add a reaction and return updated counts."""
        p1, p2, mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = None  # no existing reaction
        mock_cursor.fetchall.return_value = [('heart', 1)]  # reaction counts

        with p1, p2:
            resp = client.post('/api/community/post/1/react',
                               json={'username': 'test_patient',
                                     'reaction': 'heart'})

        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert data['action'] == 'added'

    def test_react_toggle_off(self, client):
        """Should remove an existing reaction (toggle off)."""
        p1, p2, mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = (1,)  # existing reaction found
        mock_cursor.fetchall.return_value = []  # no reactions left

        with p1, p2:
            resp = client.post('/api/community/post/1/react',
                               json={'username': 'test_patient',
                                     'reaction': 'heart'})

        assert resp.status_code == 200
        data = resp.get_json()
        assert data['action'] == 'removed'

    def test_react_invalid_type(self, client):
        """Should return 400 for invalid reaction type."""
        resp = client.post('/api/community/post/1/react',
                           json={'username': 'test_patient',
                                 'reaction': 'angry'})
        assert resp.status_code == 400

    def test_react_missing_username(self, client):
        """Should return 400 when username is missing."""
        resp = client.post('/api/community/post/1/react',
                           json={'reaction': 'like'})
        assert resp.status_code == 400


# ==================== POST /api/community/post/<id>/pin ====================

class TestPinPost:
    """Tests for pinning/unpinning a community post."""

    def test_pin_post_clinician(self, client):
        """Clinician should be able to pin a post."""
        p1, p2, mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = ('clinician',)  # role check

        with p1, p2:
            resp = client.post('/api/community/post/1/pin',
                               json={'username': 'test_clinician', 'pin': True})

        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert data['pinned'] is True

    def test_pin_post_non_clinician_forbidden(self, client):
        """Non-clinician should be rejected with 403."""
        p1, p2, mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = ('user',)  # role check: regular user

        with p1, p2:
            resp = client.post('/api/community/post/1/pin',
                               json={'username': 'test_patient', 'pin': True})

        assert resp.status_code == 403

    def test_pin_post_missing_username(self, client):
        """Should return 400 when username is missing."""
        resp = client.post('/api/community/post/1/pin', json={'pin': True})
        assert resp.status_code == 400


# ==================== DELETE /api/community/post/<id> ====================

class TestDeletePost:
    """Tests for deleting a community post."""

    def test_delete_own_post(self, client):
        """Author should be able to delete their own post."""
        p1, p2, mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = ('test_patient',)  # post author

        with p1, p2:
            resp = client.delete('/api/community/post/1',
                                 json={'username': 'test_patient'})

        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True

    def test_delete_other_user_post_forbidden(self, client):
        """Should return 403 when trying to delete another user's post."""
        p1, p2, mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = ('other_user',)  # post author is different

        with p1, p2:
            resp = client.delete('/api/community/post/1',
                                 json={'username': 'test_patient'})

        assert resp.status_code == 403

    def test_delete_nonexistent_post(self, client):
        """Should return 404 when post does not exist."""
        p1, p2, mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = None

        with p1, p2:
            resp = client.delete('/api/community/post/999',
                                 json={'username': 'test_patient'})

        assert resp.status_code == 404

    def test_delete_post_missing_username(self, client):
        """Should return 400 when username is missing."""
        resp = client.delete('/api/community/post/1', json={})
        assert resp.status_code == 400


# ==================== POST /api/community/post/<id>/report ====================

class TestReportPost:
    """Tests for reporting a community post."""

    def test_report_post_success(self, client):
        """Should report a post for review."""
        p1, p2, mock_conn, mock_cursor = _mock_db()
        # First fetchone: post exists (author, message)
        # Second fetchone: no existing report
        mock_cursor.fetchone.side_effect = [
            ('other_user', 'Bad post content'),  # post lookup
            None,  # no existing report
        ]

        with p1, p2, patch.object(api, 'log_event'):
            resp = client.post('/api/community/post/1/report',
                               json={'username': 'test_patient',
                                     'reason': 'Inappropriate content'})

        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True

    def test_report_own_post(self, client):
        """Should return 400 when reporting own post."""
        p1, p2, mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = ('test_patient', 'My post')

        with p1, p2:
            resp = client.post('/api/community/post/1/report',
                               json={'username': 'test_patient',
                                     'reason': 'Test'})

        assert resp.status_code == 400

    def test_report_nonexistent_post(self, client):
        """Should return 404 when post does not exist."""
        p1, p2, mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = None

        with p1, p2:
            resp = client.post('/api/community/post/999/report',
                               json={'username': 'test_patient',
                                     'reason': 'Spam'})

        assert resp.status_code == 404

    def test_report_already_reported(self, client):
        """Should return 409 when user already reported this post."""
        p1, p2, mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.side_effect = [
            ('other_user', 'Some post'),  # post exists
            (5,),  # existing report found
        ]

        with p1, p2:
            resp = client.post('/api/community/post/1/report',
                               json={'username': 'test_patient',
                                     'reason': 'Spam'})

        assert resp.status_code == 409


# ==================== GET /api/community/post/<id>/replies ====================

class TestGetReplies:
    """Tests for getting replies to a post."""

    def test_get_replies_success(self, client):
        """Should return replies for a post."""
        p1, p2, mock_conn, mock_cursor = _mock_db()
        now = datetime.now().isoformat()
        mock_cursor.fetchall.return_value = [
            (1, 'user1', 'First reply', now),
            (2, 'user2', 'Second reply', now),
        ]

        with p1, p2:
            resp = client.get('/api/community/post/1/replies')

        assert resp.status_code == 200
        data = resp.get_json()
        assert 'replies' in data
        assert len(data['replies']) == 2

    def test_get_replies_empty(self, client):
        """Should return empty list for post with no replies."""
        p1, p2, mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchall.return_value = []

        with p1, p2:
            resp = client.get('/api/community/post/1/replies')

        assert resp.status_code == 200
        data = resp.get_json()
        assert data['replies'] == []


# ==================== DELETE /api/community/reply/<id> ====================

class TestDeleteReply:
    """Tests for deleting a reply."""

    def test_delete_own_reply(self, client):
        """Author should be able to delete their own reply."""
        p1, p2, mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = ('test_patient',)

        with p1, p2:
            resp = client.delete('/api/community/reply/1',
                                 json={'username': 'test_patient'})

        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True

    def test_delete_other_user_reply_forbidden(self, client):
        """Should return 403 when deleting another user's reply."""
        p1, p2, mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = ('other_user',)

        with p1, p2:
            resp = client.delete('/api/community/reply/1',
                                 json={'username': 'test_patient'})

        assert resp.status_code == 403

    def test_delete_nonexistent_reply(self, client):
        """Should return 404 when reply does not exist."""
        p1, p2, mock_conn, mock_cursor = _mock_db()
        mock_cursor.fetchone.return_value = None

        with p1, p2:
            resp = client.delete('/api/community/reply/999',
                                 json={'username': 'test_patient'})

        assert resp.status_code == 404

    def test_delete_reply_missing_username(self, client):
        """Should return 400 when username is missing."""
        resp = client.delete('/api/community/reply/1', json={})
        assert resp.status_code == 400
