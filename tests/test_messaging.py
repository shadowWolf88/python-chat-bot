"""
Tests for Phase 3: Internal Messaging System endpoints
Comprehensive tests for all messaging functionality
"""
import pytest
import json


class TestMessagingSend:
    """Tests for POST /api/messages/send endpoint"""
    
    def test_send_message_to_other_user(self, authenticated_patient, tmp_db):
        """Test user can send message to another user"""
        import sqlite3
        from hashlib import pbkdf2_hmac
        
        client, patient = authenticated_patient
        
        # Create another patient to send to
        conn = sqlite3.connect(tmp_db)
        cur = conn.cursor()
        hashed = pbkdf2_hmac('sha256', b'pass', b'salt', 100000).hex()
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('other_patient', hashed, 'user')
        )
        conn.commit()
        conn.close()
        
        # Send message
        response = client.post('/api/messages/send',
            json={
                'recipient': 'other_patient',
                'subject': 'Check-in',
                'content': 'I am feeling better today'
            })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'message_id' in data
        assert data['status'] == 'sent'
        assert data['recipient'] == 'other_patient'
    
    def test_send_message_missing_content(self, authenticated_patient):
        """Test that empty content is rejected"""
        client, patient = authenticated_patient
        
        response = client.post('/api/messages/send',
            json={
                'recipient': 'someone',
                'content': ''
            })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'content' in data['error'].lower()
    
    def test_send_message_to_self(self, authenticated_patient):
        """Test that users cannot message themselves"""
        client, patient = authenticated_patient
        
        response = client.post('/api/messages/send',
            json={
                'recipient': patient['username'],
                'content': 'Hello myself'
            })
        
        assert response.status_code == 400
        assert 'yourself' in response.get_json()['error'].lower()
    
    def test_send_message_content_too_long(self, authenticated_patient):
        """Test that content over 5000 chars is rejected"""
        client, patient = authenticated_patient
        
        response = client.post('/api/messages/send',
            json={
                'recipient': 'someone',
                'content': 'x' * 5001
            })
        
        assert response.status_code == 400
        assert '5000' in response.get_json()['error']
    
    def test_send_message_no_recipient(self, authenticated_patient):
        """Test that missing recipient is rejected"""
        client, patient = authenticated_patient
        
        response = client.post('/api/messages/send',
            json={
                'content': 'Hello'
            })
        
        assert response.status_code == 400
        assert 'recipient' in response.get_json()['error'].lower()


class TestMessagingInbox:
    """Tests for GET /api/messages/inbox endpoint"""
    
    def test_get_empty_inbox(self, authenticated_patient):
        """Test that new user has empty inbox"""
        client, patient = authenticated_patient
        
        response = client.get('/api/messages/inbox')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['conversations'] == []
        assert data['total_unread'] == 0
        assert data['total_conversations'] == 0
    
    def test_get_inbox_with_messages(self, authenticated_patient, tmp_db):
        """Test inbox shows conversation previews"""
        import sqlite3
        from hashlib import pbkdf2_hmac
        
        client_p, patient = authenticated_patient
        
        # Create another patient to send messages
        conn = sqlite3.connect(tmp_db)
        cur = conn.cursor()
        hashed = pbkdf2_hmac('sha256', b'pass', b'salt', 100000).hex()
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('friend_user', hashed, 'user')
        )
        conn.commit()
        conn.close()
        
        # Create session for friend
        with authenticated_patient[0].session_transaction() as sess:
            # Temporarily send message from friend
            pass
        
        # Create a direct database insert since friend needs to send message
        conn = sqlite3.connect(tmp_db)
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO messages (sender_username, recipient_username, content, sent_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', ('friend_user', patient['username'], 'How are you feeling?'))
        conn.commit()
        conn.close()
        
        # Check patient's inbox
        response = client_p.get('/api/messages/inbox')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['conversations']) == 1
        assert data['conversations'][0]['with_user'] == 'friend_user'
        assert 'feeling' in data['conversations'][0]['last_message']
        assert data['conversations'][0]['unread_count'] == 1
        assert data['total_unread'] == 1
    
    def test_inbox_pagination(self, authenticated_patient):
        """Test inbox pagination works"""
        client, patient = authenticated_patient
        
        response = client.get('/api/messages/inbox?page=2&limit=10')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['page'] == 2
        assert data['page_size'] == 10


class TestMessagingConversation:
    """Tests for GET /api/messages/conversation/<username> endpoint"""
    
    def test_get_empty_conversation(self, authenticated_patient, test_clinician):
        """Test getting conversation with no messages"""
        client, patient = authenticated_patient
        
        response = client.get(f'/api/messages/conversation/{test_clinician["username"]}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['messages'] == []
        assert data['participant_count'] == 2
    
    def test_get_conversation_with_messages(self, authenticated_patient, tmp_db):
        """Test retrieving full conversation history"""
        import sqlite3
        from hashlib import pbkdf2_hmac
        
        client_p, patient = authenticated_patient
        
        # Create another user
        conn = sqlite3.connect(tmp_db)
        cur = conn.cursor()
        hashed = pbkdf2_hmac('sha256', b'pass', b'salt', 100000).hex()
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('chat_friend', hashed, 'user')
        )
        conn.commit()
        conn.close()
        
        # Insert messages directly in database
        conn = sqlite3.connect(tmp_db)
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO messages (sender_username, recipient_username, content, sent_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', ('chat_friend', patient['username'], 'How are you today?'))
        cur.execute('''
            INSERT INTO messages (sender_username, recipient_username, content, sent_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (patient['username'], 'chat_friend', 'Doing well, thanks!'))
        conn.commit()
        conn.close()
        
        # Get conversation from patient's side
        response = client_p.get(f'/api/messages/conversation/chat_friend')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['messages']) == 2
        # Messages should contain both content items
        contents = [msg['content'] for msg in data['messages']]
        assert 'How are you today?' in contents
        assert 'Doing well, thanks!' in contents
    
    def test_conversation_marks_messages_as_read(self, authenticated_patient, tmp_db):
        """Test that getting conversation marks messages as read"""
        import sqlite3
        from hashlib import pbkdf2_hmac
        
        client_p, patient = authenticated_patient
        
        # Create another user
        conn = sqlite3.connect(tmp_db)
        cur = conn.cursor()
        hashed = pbkdf2_hmac('sha256', b'pass', b'salt', 100000).hex()
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('mark_read_friend', hashed, 'user')
        )
        conn.commit()
        conn.close()
        
        # Insert unread message
        conn = sqlite3.connect(tmp_db)
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO messages (sender_username, recipient_username, content, sent_at, is_read)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, 0)
        ''', ('mark_read_friend', patient['username'], 'Check this out'))
        conn.commit()
        conn.close()
        
        # Get conversation (should auto-mark as read)
        response = client_p.get(f'/api/messages/conversation/mark_read_friend')
        
        assert response.status_code == 200
        messages = response.get_json()['messages']
        assert len(messages) == 1
        assert messages[0]['is_read'] == True


class TestMarkAsRead:
    """Tests for PATCH /api/messages/<id>/read endpoint"""
    
    def test_mark_as_read(self, authenticated_patient, tmp_db):
        """Test marking a message as read"""
        import sqlite3
        from hashlib import pbkdf2_hmac
        
        client_p, patient = authenticated_patient
        
        # Create another user
        conn = sqlite3.connect(tmp_db)
        cur = conn.cursor()
        hashed = pbkdf2_hmac('sha256', b'pass', b'salt', 100000).hex()
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('mark_friend', hashed, 'user')
        )
        conn.commit()
        conn.close()
        
        # Insert unread message
        conn = sqlite3.connect(tmp_db)
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO messages (sender_username, recipient_username, content, sent_at, is_read)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, 0)
        ''', ('mark_friend', patient['username'], 'Test message'))
        msg_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        # Mark as read
        response = client_p.patch(f'/api/messages/{msg_id}/read')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message_id'] == msg_id
        assert data['is_read'] == True
        assert 'read_at' in data
    
    def test_mark_nonexistent_as_read(self, authenticated_patient):
        """Test marking nonexistent message as read"""
        client, patient = authenticated_patient
        
        response = client.patch('/api/messages/99999/read')
        
        assert response.status_code == 404


class TestDeleteMessage:
    """Tests for DELETE /api/messages/<id> endpoint"""
    
    def test_soft_delete_message(self, authenticated_patient, authenticated_clinician):
        """Test soft deleting a message"""
        client_p, patient = authenticated_patient
        client_c, clinician = authenticated_clinician
        
        # Send message
        send_response = client_c.post('/api/messages/send',
            json={
                'recipient': patient['username'],
                'content': 'To be deleted'
            })
        
        message_id = send_response.get_json()['message_id']
        
        # Delete
        response = client_p.delete(f'/api/messages/{message_id}')
        
        assert response.status_code == 204
    
    def test_delete_nonexistent_message(self, authenticated_patient):
        """Test deleting nonexistent message"""
        client, patient = authenticated_patient
        
        response = client.delete('/api/messages/99999')
        
        assert response.status_code == 404
    
    def test_message_hidden_when_both_delete(self, authenticated_patient, authenticated_clinician):
        """Test that message hidden when both sender and recipient delete it"""
        client_p, patient = authenticated_patient
        client_c, clinician = authenticated_clinician
        
        # Send message
        send_response = client_c.post('/api/messages/send',
            json={
                'recipient': patient['username'],
                'content': 'Delete me'
            })
        
        message_id = send_response.get_json()['message_id']
        
        # Patient deletes
        client_p.delete(f'/api/messages/{message_id}')
        
        # Clinician deletes
        client_c.delete(f'/api/messages/{message_id}')
        
        # Message should not appear in conversation
        response = client_p.get(f'/api/messages/conversation/{clinician["username"]}')
        
        data = response.get_json()
        assert len(data['messages']) == 0


class TestMessagingIntegration:
    """Integration tests for full messaging workflows"""
    
    def test_full_conversation_flow(self, authenticated_patient, tmp_db):
        """Test complete messaging flow: send, receive, read, reply"""
        import sqlite3
        from hashlib import pbkdf2_hmac
        
        client_p, patient = authenticated_patient
        
        # Create another user
        conn = sqlite3.connect(tmp_db)
        cur = conn.cursor()
        hashed = pbkdf2_hmac('sha256', b'pass', b'salt', 100000).hex()
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('flow_friend', hashed, 'user')
        )
        conn.commit()
        conn.close()
        
        # 1. Friend sends first message
        conn = sqlite3.connect(tmp_db)
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO messages (sender_username, recipient_username, subject, content, sent_at, is_read)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, 0)
        ''', ('flow_friend', patient['username'], 'Initial check-in', 'How are you today?'))
        conn.commit()
        conn.close()
        
        # 2. Patient sees unread in inbox
        inbox = client_p.get('/api/messages/inbox')
        assert inbox.status_code == 200
        inbox_data = inbox.get_json()
        assert inbox_data['total_unread'] == 1
        assert inbox_data['conversations'][0]['with_user'] == 'flow_friend'
        
        # 3. Patient gets conversation (auto-reads)
        conv = client_p.get(f'/api/messages/conversation/flow_friend')
        assert conv.status_code == 200
        msgs = conv.get_json()['messages']
        assert len(msgs) == 1
        assert msgs[0]['is_read'] == True
        
        # 4. Patient replies
        reply = client_p.post('/api/messages/send',
            json={
                'recipient': 'flow_friend',
                'content': 'I am feeling much better today'
            })
        assert reply.status_code == 201
        
        # 5. Check conversation has both messages
        final_conv = client_p.get(f'/api/messages/conversation/flow_friend')
        final_msgs = final_conv.get_json()['messages']
        assert len(final_msgs) == 2
        # Verify both messages are present
        contents = [msg['content'] for msg in final_msgs]
        assert 'How are you today?' in contents
        assert 'I am feeling much better today' in contents
