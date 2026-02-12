"""
MessageService - Core messaging business logic
Handles all message operations following MVC pattern
Implements Phase 2 of comprehensive messaging system overhaul
"""

import psycopg2
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple, Any

class MessageService:
    """
    World-class messaging service with full feature set.
    Encapsulates all message-related business logic.
    """
    
    # Constants
    MESSAGE_TYPES = ['direct', 'group', 'system', 'broadcast']
    DELIVERY_STATUSES = ['draft', 'scheduled', 'sent', 'delivered', 'failed']
    CONVERSATION_TYPES = ['direct', 'group', 'thread']
    RECEIPT_TYPES = ['delivered', 'read', 'typing']
    NOTIFICATION_TYPES = ['in_app', 'email', 'push', 'digest']
    
    MAX_MESSAGE_LENGTH = 10000
    MAX_SUBJECT_LENGTH = 255
    MAX_TEMPLATE_NAME_LENGTH = 255
    MAX_SEARCH_QUERY_LENGTH = 200
    
    def __init__(self, conn, cur, username: str = None):
        """Initialize service with database connection and authenticated user"""
        self.conn = conn
        self.cur = cur
        self.username = username  # Current authenticated user
        self.now = datetime.now()
    
    # ==================== DIRECT MESSAGING ====================
    
    def send_direct_message(self, recipient_username: str, content: str, 
                           subject: str = None, attachments: List[Dict] = None) -> Dict[str, Any]:
        """
        Send a direct message from authenticated user to recipient.
        Creates conversation if needed, stores message, logs event.
        
        Returns: {message_id, conversation_id, status, sent_at}
        """
        if not self.username:
            raise ValueError("Authentication required")
        
        if not recipient_username or not content:
            raise ValueError("Recipient and content required")
        
        if len(content) > self.MAX_MESSAGE_LENGTH:
            raise ValueError(f"Message exceeds {self.MAX_MESSAGE_LENGTH} characters")
        
        # Check if recipient exists
        try:
            self.cur.execute(
                "SELECT username, role FROM users WHERE username=%s",
                (recipient_username,)
            )
            recipient = self.cur.fetchone()
        except Exception as e:
            raise ValueError(f"Database error checking recipient: {str(e)}")
        
        if not recipient:
            raise ValueError(f"Recipient '{recipient_username}' not found")
        
        # Prevent self-messaging
        if self.username == recipient_username:
            raise ValueError("Cannot send messages to yourself")
        
        # Get or create conversation
        try:
            conversation_id = self._get_or_create_conversation(
                type='direct',
                subject=subject,
                participants=[self.username, recipient_username]
            )
        except Exception as e:
            raise ValueError(f"Failed to create/get conversation: {str(e)}")
        
        if not conversation_id:
            raise ValueError("Failed to get conversation ID")
        
        # Insert message
        try:
            self.cur.execute("""
                INSERT INTO messages (
                    conversation_id, sender_username, recipient_username,
                    message_type, subject, content, sent_at, delivery_status
                ) VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, 'sent')
                RETURNING id, sent_at
            """, (conversation_id, self.username, recipient_username, 'direct', subject, content))
            
            result = self.cur.fetchone()
            if not result:
                raise ValueError("Message insert returned no result")
            
            message_id, sent_at = result[0], result[1]
        except Exception as e:
            raise ValueError(f"Failed to insert message: {str(e)}")
        
        # Update conversation's last_message_at
        try:
            self.cur.execute("""
                UPDATE conversations 
                SET last_message_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (conversation_id,))
            
            self.conn.commit()
        except Exception as e:
            raise ValueError(f"Failed to update conversation: {str(e)}")
        
        return {
            'message_id': message_id,
            'conversation_id': conversation_id,
            'recipient': recipient_username,
            'status': 'sent',
            'sent_at': sent_at.isoformat() if sent_at else None
        }
    
    def send_group_message(self, participant_usernames: List[str], content: str,
                          subject: str = None) -> Dict[str, Any]:
        """Send message to multiple recipients (group message)"""
        if not self.username or not participant_usernames or not content:
            raise ValueError("All parameters required")
        
        if len(content) > self.MAX_MESSAGE_LENGTH:
            raise ValueError(f"Message exceeds {self.MAX_MESSAGE_LENGTH} characters")
        
        # Validate all recipients exist
        placeholders = ','.join(['%s'] * len(participant_usernames))
        self.cur.execute(
            f"SELECT COUNT(*) FROM users WHERE username IN ({placeholders})",
            participant_usernames
        )
        count = self.cur.fetchone()[0]
        
        if count != len(participant_usernames):
            raise ValueError("One or more recipients not found")
        
        # Create group conversation
        conversation_id = self._get_or_create_conversation(
            type='group',
            subject=subject or 'Group Message',
            participants=[self.username] + participant_usernames
        )
        
        # Insert message
        self.cur.execute("""
            INSERT INTO messages (
                conversation_id, sender_username, recipient_username,
                message_type, subject, content, sent_at, delivery_status
            ) VALUES (%s, %s, NULL, %s, %s, %s, CURRENT_TIMESTAMP, 'sent')
            RETURNING id, sent_at
        """, (conversation_id, self.username, 'group', subject, content))
        
        result = self.cur.fetchone()
        message_id, sent_at = result[0], result[1]
        
        # Create notification for each recipient
        for participant in participant_usernames:
            self._create_notification(message_id, participant, 'in_app')
        
        self.conn.commit()
        
        return {
            'message_id': message_id,
            'conversation_id': conversation_id,
            'recipients': participant_usernames,
            'status': 'sent',
            'sent_at': sent_at.isoformat() if sent_at else None
        }
    
    def send_broadcast_message(self, content: str, subject: str = None,
                              recipient_filter: str = None) -> Dict[str, Any]:
        """
        Broadcast message from developer/admin to all/filtered users.
        recipient_filter: 'all', 'patients', 'clinicians', or username list
        """
        if not self.username:
            raise ValueError("Authentication required")
        
        # Verify sender is developer
        sender_role = self.cur.execute(
            "SELECT role FROM users WHERE username=%s",
            (self.username,)
        ).fetchone()
        
        if not sender_role or sender_role[0] != 'developer':
            raise ValueError("Only developers can broadcast")
        
        # Get recipient list based on filter
        if recipient_filter == 'patients':
            self.cur.execute("SELECT username FROM users WHERE role='user'")
        elif recipient_filter == 'clinicians':
            self.cur.execute("SELECT username FROM users WHERE role='clinician'")
        else:  # 'all'
            self.cur.execute("SELECT username FROM users WHERE role != 'developer'")
        
        recipients = [row[0] for row in self.cur.fetchall()]
        
        if not recipients:
            return {'message_id': None, 'recipients_count': 0, 'status': 'no_recipients'}
        
        # Create broadcast conversation
        conversation_id = self._get_or_create_conversation(
            type='group',
            subject=subject or 'System Broadcast',
            participants=recipients
        )
        
        # Insert broadcast message
        self.cur.execute("""
            INSERT INTO messages (
                conversation_id, sender_username, message_type,
                subject, content, sent_at, delivery_status
            ) VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, 'sent')
            RETURNING id, sent_at
        """, (conversation_id, self.username, 'broadcast', subject, content))
        
        result = self.cur.fetchone()
        message_id, sent_at = result[0], result[1]
        
        # Create notifications
        for recipient in recipients:
            self._create_notification(message_id, recipient, 'in_app')
        
        self.conn.commit()
        
        return {
            'message_id': message_id,
            'conversation_id': conversation_id,
            'recipients_count': len(recipients),
            'status': 'sent',
            'sent_at': sent_at.isoformat() if sent_at else None
        }
    
    # ==================== MESSAGE RETRIEVAL ====================
    
    def get_conversations_list(self, page: int = 1, limit: int = 20,
                               unread_only: bool = False) -> Dict[str, Any]:
        """Get user's conversation list with pagination"""
        if not self.username:
            raise ValueError("Authentication required")
        
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 20
        
        # Get distinct conversation partners
        self.cur.execute("""
            SELECT DISTINCT conversation_id
            FROM conversation_participants
            WHERE username = %s
            ORDER BY conversation_id DESC
        """, (self.username,))
        
        conv_ids = [row[0] for row in self.cur.fetchall()]
        
        conversations = []
        for conv_id in conv_ids:
            # Get latest message
            self.cur.execute("""
                SELECT sender_username, content, sent_at
                FROM messages
                WHERE conversation_id = %s AND deleted_at IS NULL
                ORDER BY sent_at DESC LIMIT 1
            """, (conv_id,))
            
            latest = self.cur.fetchone()
            
            # Get unread count
            self.cur.execute("""
                SELECT COUNT(*) FROM messages
                WHERE conversation_id = %s AND recipient_username = %s
                AND is_read = 0 AND deleted_at IS NULL
            """, (conv_id, self.username))
            unread_result = self.cur.fetchone()
            unread_count = unread_result[0] if unread_result else 0
            
            if unread_only and unread_count == 0:
                continue  # Skip read conversations
            
            # Get conversation details
            self.cur.execute("""
                SELECT subject, type, participant_count, last_message_at
                FROM conversations WHERE id = %s
            """, (conv_id,))
            conv_details = self.cur.fetchone()
            
            # Get the other participant(s) in this conversation
            self.cur.execute("""
                SELECT username FROM conversation_participants
                WHERE conversation_id = %s AND username != %s
                LIMIT 1
            """, (conv_id, self.username))
            other_user_result = self.cur.fetchone()
            other_user = other_user_result[0] if other_user_result else 'Unknown User'
            
            conversations.append({
                'conversation_id': conv_id,
                'with_user': other_user,  # ← KEY FIELD MISSING BEFORE
                'subject': conv_details[0] if conv_details else None,
                'type': conv_details[1] if conv_details else 'direct',
                'last_message': latest[1][:100] if latest else None,
                'last_sender': latest[0] if latest else None,
                'last_message_time': latest[2].isoformat() if latest else None,
                'unread_count': unread_count,
                'participant_count': conv_details[3] if conv_details else 2
            })
        
        # Sort by most recent
        conversations.sort(key=lambda x: x['last_message_time'] or '', reverse=True)
        
        # Paginate
        total = len(conversations)
        offset = (page - 1) * limit
        paginated = conversations[offset:offset + limit]
        
        return {
            'conversations': paginated,
            'total_conversations': total,
            'page': page,
            'page_size': limit,
            'total_pages': (total + limit - 1) // limit
        }
    
    def get_conversation_thread(self, conversation_id: int, limit: int = 50) -> Dict[str, Any]:
        """Get full conversation thread"""
        if not self.username:
            raise ValueError("Authentication required")
        
        if limit < 1 or limit > 500:
            limit = 50
        
        # Verify access
        access = self.cur.execute("""
            SELECT 1 FROM conversation_participants
            WHERE conversation_id = %s AND username = %s
        """, (conversation_id, self.username)).fetchone()
        
        if not access:
            raise ValueError("Access denied")
        
        # Get messages
        self.cur.execute("""
            SELECT id, sender_username, recipient_username, subject, content,
                   is_read, read_at, sent_at, message_type
            FROM messages
            WHERE conversation_id = %s AND deleted_at IS NULL
            ORDER BY sent_at ASC LIMIT %s
        """, (conversation_id, limit))
        
        messages = []
        for row in self.cur.fetchall():
            # Mark as read if recipient
            if row[2] == self.username and not row[5]:
                self.cur.execute("""
                    UPDATE messages SET is_read = 1, read_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (row[0],))
            
            messages.append({
                'id': row[0],
                'sender': row[1],
                'recipient': row[2],
                'subject': row[3],
                'content': row[4],
                'is_read': bool(row[5]),
                'read_at': row[6].isoformat() if row[6] else None,
                'sent_at': row[7].isoformat() if row[7] else None,
                'message_type': row[8]
            })
        
        self.conn.commit()
        
        return {
            'conversation_id': conversation_id,
            'messages': messages,
            'message_count': len(messages)
        }
    
    def get_sent_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get messages sent by the authenticated user"""
        if not self.username:
            return []
        
        if limit < 1 or limit > 1000:
            limit = 100
        
        # Get sent messages
        self.cur.execute("""
            SELECT id, recipient_username, subject, content, is_read, sent_at, 
                   message_type, conversation_id
            FROM messages
            WHERE sender_username = %s AND (is_deleted_by_sender = 0 OR is_deleted_by_sender IS NULL)
            ORDER BY sent_at DESC LIMIT %s
        """, (self.username, limit))
        
        messages = []
        for row in self.cur.fetchall():
            messages.append({
                'id': row[0],
                'recipient': row[1],
                'subject': row[2],
                'content': row[3],
                'is_read': bool(row[4]),
                'sent_at': row[5].isoformat() if row[5] else None,
                'message_type': row[6],
                'conversation_id': row[7]
            })
        
        return messages
    
    def search_messages(self, query: str, limit: int = 50) -> Dict[str, Any]:
        """Full-text search across user's messages"""
        if not self.username:
            raise ValueError("Authentication required")
        
        if not query or len(query) < 2:
            raise ValueError("Search query must be at least 2 characters")
        
        if len(query) > self.MAX_SEARCH_QUERY_LENGTH:
            raise ValueError(f"Search query exceeds {self.MAX_SEARCH_QUERY_LENGTH} characters")
        
        search_term = f"%{query}%"
        
        # Search in messages
        self.cur.execute("""
            SELECT id, conversation_id, sender_username, recipient_username,
                   subject, content, sent_at, is_read
            FROM messages
            WHERE (sender_username = %s OR recipient_username = %s)
            AND deleted_at IS NULL
            AND (content ILIKE %s OR subject ILIKE %s)
            ORDER BY sent_at DESC LIMIT %s
        """, (self.username, self.username, search_term, search_term, limit))
        
        results = []
        for row in self.cur.fetchall():
            results.append({
                'message_id': row[0],
                'conversation_id': row[1],
                'sender': row[2],
                'recipient': row[3],
                'subject': row[4],
                'content': row[5][:200] + '...' if len(row[5]) > 200 else row[5],
                'sent_at': row[6].isoformat() if row[6] else None,
                'is_read': bool(row[7])
            })
        
        return {
            'query': query,
            'results': results,
            'count': len(results)
        }
    
    # ==================== MESSAGE MANAGEMENT ====================
    
    def mark_message_read(self, message_id: int) -> Dict[str, Any]:
        """Mark message as read"""
        if not self.username:
            raise ValueError("Authentication required")
        
        # Verify user is recipient
        msg = self.cur.execute("""
            SELECT recipient_username FROM messages WHERE id = %s
        """, (message_id,)).fetchone()
        
        if not msg or msg[0] != self.username:
            raise ValueError("Access denied or message not found")
        
        self.cur.execute("""
            UPDATE messages
            SET is_read = 1, read_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (message_id,))
        
        self.conn.commit()
        
        return {
            'message_id': message_id,
            'is_read': True,
            'read_at': self.now.isoformat()
        }
    
    def archive_message(self, message_id: int) -> Dict[str, Any]:
        """Archive message (hide from view)"""
        if not self.username:
            raise ValueError("Authentication required")
        
        # Check access
        msg = self.cur.execute("""
            SELECT sender_username, recipient_username FROM messages WHERE id = %s
        """, (message_id,)).fetchone()
        
        if not msg or self.username not in (msg[0], msg[1]):
            raise ValueError("Access denied")
        
        # Mark as archived by user
        if self.username == msg[0]:
            self.cur.execute("""
                UPDATE messages SET is_archived_by_sender = TRUE WHERE id = %s
            """, (message_id,))
        else:
            self.cur.execute("""
                UPDATE messages SET is_archived_by_recipient = TRUE WHERE id = %s
            """, (message_id,))
        
        self.conn.commit()
        
        return {'message_id': message_id, 'archived': True}
    
    def delete_message(self, message_id: int) -> Dict[str, Any]:
        """Soft delete message (may be permanent if both users delete)"""
        if not self.username:
            raise ValueError("Authentication required")
        
        msg = self.cur.execute("""
            SELECT sender_username, recipient_username, is_deleted_by_sender, is_deleted_by_recipient
            FROM messages WHERE id = %s
        """, (message_id,)).fetchone()
        
        if not msg or self.username not in (msg[0], msg[1]):
            raise ValueError("Access denied")
        
        # Mark as deleted by user
        if self.username == msg[0]:
            self.cur.execute("""
                UPDATE messages SET is_deleted_by_sender = TRUE WHERE id = %s
            """, (message_id,))
            deleted_by_sender = True
            deleted_by_recipient = msg[3]
        else:
            self.cur.execute("""
                UPDATE messages SET is_deleted_by_recipient = TRUE WHERE id = %s
            """, (message_id,))
            deleted_by_sender = msg[2]
            deleted_by_recipient = True
        
        # If both users deleted, mark permanently deleted
        if deleted_by_sender and deleted_by_recipient:
            self.cur.execute("""
                UPDATE messages SET deleted_at = CURRENT_TIMESTAMP WHERE id = %s
            """, (message_id,))
        
        self.conn.commit()
        
        return {'message_id': message_id, 'deleted': True}
    
    # ==================== MESSAGE TEMPLATES ====================
    
    def create_template(self, name: str, content: str, category: str = None) -> Dict[str, Any]:
        """Create a message template (for clinicians)"""
        if not self.username:
            raise ValueError("Authentication required")
        
        if not name or not content:
            raise ValueError("Name and content required")
        
        if len(name) > self.MAX_TEMPLATE_NAME_LENGTH:
            raise ValueError(f"Template name exceeds {self.MAX_TEMPLATE_NAME_LENGTH} characters")
        
        if len(content) > self.MAX_MESSAGE_LENGTH:
            raise ValueError(f"Template content exceeds {self.MAX_MESSAGE_LENGTH} characters")
        
        # Check uniqueness
        existing = self.cur.execute("""
            SELECT id FROM message_templates
            WHERE creator_username = %s AND name = %s
        """, (self.username, name)).fetchone()
        
        if existing:
            raise ValueError("Template with this name already exists")
        
        # Create template
        self.cur.execute("""
            INSERT INTO message_templates (creator_username, name, content, category)
            VALUES (%s, %s, %s, %s)
            RETURNING id, created_at
        """, (self.username, name, content, category))
        
        result = self.cur.fetchone()
        template_id, created_at = result[0], result[1]
        
        self.conn.commit()
        
        return {
            'template_id': template_id,
            'name': name,
            'created_at': created_at.isoformat() if created_at else None
        }
    
    def get_templates(self) -> List[Dict[str, Any]]:
        """Get user's message templates"""
        if not self.username:
            raise ValueError("Authentication required")
        
        self.cur.execute("""
            SELECT id, name, content, category, usage_count, created_at
            FROM message_templates
            WHERE creator_username = %s
            ORDER BY usage_count DESC, created_at DESC
        """, (self.username,))
        
        templates = []
        for row in self.cur.fetchall():
            templates.append({
                'template_id': row[0],
                'name': row[1],
                'content': row[2],
                'category': row[3],
                'usage_count': row[4],
                'created_at': row[5].isoformat() if row[5] else None
            })
        
        return templates
    
    # ==================== MESSAGE SCHEDULING ====================
    
    def schedule_message(self, recipient_username: str, content: str,
                         scheduled_for: datetime, subject: str = None) -> Dict[str, Any]:
        """Schedule a message to be sent at a future time"""
        if not self.username:
            raise ValueError("Authentication required")
        
        if scheduled_for <= self.now:
            raise ValueError("Scheduled time must be in the future")
        
        if len(content) > self.MAX_MESSAGE_LENGTH:
            raise ValueError(f"Message exceeds {self.MAX_MESSAGE_LENGTH} characters")
        
        # Create conversation
        conversation_id = self._get_or_create_conversation(
            type='direct',
            subject=subject,
            participants=[self.username, recipient_username]
        )
        
        # Insert scheduled message
        self.cur.execute("""
            INSERT INTO messages (
                conversation_id, sender_username, recipient_username,
                message_type, subject, content, scheduled_for, delivery_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'scheduled')
            RETURNING id, scheduled_for
        """, (conversation_id, self.username, recipient_username, 'direct', subject, content, scheduled_for))
        
        result = self.cur.fetchone()
        message_id, scheduled = result[0], result[1]
        
        self.conn.commit()
        
        return {
            'message_id': message_id,
            'recipient': recipient_username,
            'scheduled_for': scheduled.isoformat() if scheduled else None,
            'status': 'scheduled'
        }
    
    def get_scheduled_messages(self) -> List[Dict[str, Any]]:
        """Get user's scheduled messages"""
        if not self.username:
            raise ValueError("Authentication required")
        
        self.cur.execute("""
            SELECT id, recipient_username, subject, content, scheduled_for
            FROM messages
            WHERE sender_username = %s AND delivery_status = 'scheduled'
            ORDER BY scheduled_for ASC
        """, (self.username,))
        
        messages = []
        for row in self.cur.fetchall():
            messages.append({
                'message_id': row[0],
                'recipient': row[1],
                'subject': row[2],
                'preview': row[3][:100] + '...' if len(row[3]) > 100 else row[3],
                'scheduled_for': row[4].isoformat() if row[4] else None
            })
        
        return messages
    
    # ==================== USER BLOCKING ====================
    
    def block_user(self, blocked_username: str, reason: str = None) -> Dict[str, Any]:
        """Block another user from sending messages"""
        if not self.username:
            raise ValueError("Authentication required")
        
        if self.username == blocked_username:
            raise ValueError("Cannot block yourself")
        
        # Check if already blocked
        existing = self.cur.execute("""
            SELECT id FROM blocked_users
            WHERE blocker_username = %s AND blocked_username = %s
        """, (self.username, blocked_username)).fetchone()
        
        if existing:
            raise ValueError("User already blocked")
        
        self.cur.execute("""
            INSERT INTO blocked_users (blocker_username, blocked_username, reason)
            VALUES (%s, %s, %s)
            RETURNING id, blocked_at
        """, (self.username, blocked_username, reason))
        
        result = self.cur.fetchone()
        block_id, blocked_at = result[0], result[1]
        
        self.conn.commit()
        
        return {
            'block_id': block_id,
            'blocked_user': blocked_username,
            'blocked_at': blocked_at.isoformat() if blocked_at else None
        }
    
    def unblock_user(self, blocked_username: str) -> Dict[str, Any]:
        """Unblock a user"""
        if not self.username:
            raise ValueError("Authentication required")
        
        self.cur.execute("""
            DELETE FROM blocked_users
            WHERE blocker_username = %s AND blocked_username = %s
            RETURNING 1
        """, (self.username, blocked_username))
        
        if not self.cur.fetchone():
            raise ValueError("User not in blocklist")
        
        self.conn.commit()
        
        return {'blocked_user': blocked_username, 'unblocked': True}
    
    def get_blocked_users(self) -> List[str]:
        """Get list of users this user has blocked"""
        if not self.username:
            raise ValueError("Authentication required")
        
        self.cur.execute("""
            SELECT blocked_username FROM blocked_users
            WHERE blocker_username = %s
            ORDER BY blocked_at DESC
        """, (self.username,))
        
        return [row[0] for row in self.cur.fetchall()]
    
    def is_user_blocked(self, other_username: str) -> bool:
        """Check if other user is blocked by current user"""
        if not self.username:
            return False
        
        result = self.cur.execute("""
            SELECT 1 FROM blocked_users
            WHERE blocker_username = %s AND blocked_username = %s
        """, (self.username, other_username)).fetchone()
        
        return result is not None
    
    # ==================== INTERNAL HELPERS ====================
    
    def _get_or_create_conversation(self, type: str, subject: str = None,
                                   participants: List[str] = None) -> int:
        """Get existing conversation or create new one"""
        participants = participants or []
        
        if type == 'direct' and len(participants) == 2:
            # Check for existing direct conversation
            p1, p2 = sorted(participants)
            try:
                self.cur.execute("""
                    SELECT c.id FROM conversations c
                    JOIN conversation_participants cp1 ON c.id = cp1.conversation_id
                    JOIN conversation_participants cp2 ON c.id = cp2.conversation_id
                    WHERE c.type = 'direct'
                    AND ((cp1.username = %s AND cp2.username = %s) OR (cp1.username = %s AND cp2.username = %s))
                    LIMIT 1
                """, (p1, p2, p2, p1))
                existing = self.cur.fetchone()
                
                if existing:
                    return existing[0]
            except Exception as e:
                # Log but continue to create new conversation
                pass
        
        # Create new conversation
        try:
            self.cur.execute("""
                INSERT INTO conversations (type, subject, created_by, participant_count)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (type, subject, self.username, len(participants)))
            
            result = self.cur.fetchone()
            if not result:
                raise ValueError("Conversation creation returned no result")
            
            conv_id = result[0]
        except Exception as e:
            raise ValueError(f"Failed to create conversation: {str(e)}")
        
        # Add participants
        try:
            for participant in participants:
                self.cur.execute("""
                    INSERT INTO conversation_participants (conversation_id, username)
                    VALUES (%s, %s)
                """, (conv_id, participant))
        except Exception as e:
            raise ValueError(f"Failed to add conversation participants: {str(e)}")
        
        return conv_id
    
    def _create_notification(self, message_id: int, recipient_username: str,
                            notification_type: str = 'in_app') -> None:
        """Create a notification for received message"""
        self.cur.execute("""
            INSERT INTO message_notifications (message_id, recipient_username, notification_type, sent_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
        """, (message_id, recipient_username, notification_type))
    
    def get_unread_count(self) -> int:
        """Get total unread message count for user"""
        if not self.username:
            return 0
        
        result = self.cur.execute("""
            SELECT COUNT(*) FROM messages
            WHERE recipient_username = %s AND is_read = 0 AND deleted_at IS NULL
        """, (self.username,)).fetchone()
        
        return result[0] if result else 0
    
    def get_conversation_unread_count(self, conversation_id: int) -> int:
        """Get unread count for specific conversation"""
        if not self.username:
            return 0
        
        result = self.cur.execute("""
            SELECT COUNT(*) FROM messages
            WHERE conversation_id = %s AND recipient_username = %s
            AND is_read = 0 AND deleted_at IS NULL
        """, (conversation_id, self.username)).fetchone()
        
        return result[0] if result else 0
