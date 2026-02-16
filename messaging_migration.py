#!/usr/bin/env python3
"""
Messaging System Database Migration
Implements Sprint 1 of the comprehensive messaging system overhaul.
Creates 8 new tables with proper constraints, indexes, and foreign keys.
"""

import psycopg2
import os
from datetime import datetime

def get_db_connection():
    """Get PostgreSQL connection"""
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        return psycopg2.connect(database_url)
    else:
        return psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME', 'healing_space'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )

def run_migration():
    """Execute all database migrations"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🔄 Starting Messaging System Database Migration...")
        print("-" * 60)
        
        # 1. Create conversations table
        print("📋 Creating conversations table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                type VARCHAR(50) NOT NULL DEFAULT 'direct',
                    CHECK (type IN ('direct', 'group', 'thread')),
                subject VARCHAR(255),
                created_by VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_message_at TIMESTAMP,
                participant_count INTEGER DEFAULT 2,
                is_archived BOOLEAN DEFAULT FALSE,
                
                FOREIGN KEY (created_by) REFERENCES users(username) ON DELETE CASCADE,
                INDEX idx_created_at (created_at),
                INDEX idx_created_by (created_by)
            );
        """)
        print("   ✓ conversations table created")
        
        # 2. Create messages table (enhanced)
        print("📋 Creating messages table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                conversation_id INTEGER,
                sender_username VARCHAR(255) NOT NULL,
                recipient_username VARCHAR(255),
                message_type VARCHAR(50) NOT NULL DEFAULT 'direct',
                    CHECK (message_type IN ('direct', 'group', 'system', 'broadcast')),
                subject VARCHAR(255),
                content TEXT NOT NULL,
                
                -- Rich content support
                content_html TEXT,
                attachments JSONB,
                
                -- Status tracking
                is_read BOOLEAN DEFAULT FALSE,
                read_at TIMESTAMP,
                is_archived_by_sender BOOLEAN DEFAULT FALSE,
                is_archived_by_recipient BOOLEAN DEFAULT FALSE,
                
                -- Soft delete (per-user deletion)
                is_deleted_by_sender BOOLEAN DEFAULT FALSE,
                is_deleted_by_recipient BOOLEAN DEFAULT FALSE,
                deleted_at TIMESTAMP,
                
                -- Scheduling & delivery
                scheduled_for TIMESTAMP,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                delivery_status VARCHAR(50) DEFAULT 'sent',
                    CHECK (delivery_status IN ('draft', 'scheduled', 'sent', 'delivered', 'failed')),
                
                -- Metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
                FOREIGN KEY (sender_username) REFERENCES users(username) ON DELETE CASCADE,
                FOREIGN KEY (recipient_username) REFERENCES users(username) ON DELETE CASCADE,
                
                INDEX idx_sender_recipient (sender_username, recipient_username),
                INDEX idx_conversation (conversation_id),
                INDEX idx_sent_at (sent_at),
                INDEX idx_is_read (is_read),
                INDEX idx_delivery_status (delivery_status)
            );
        """)
        print("   ✓ messages table created")
        
        # 3. Create conversation_participants table
        print("📋 Creating conversation_participants table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_participants (
                id SERIAL PRIMARY KEY,
                conversation_id INTEGER NOT NULL,
                username VARCHAR(255) NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_read_at TIMESTAMP,
                is_muted BOOLEAN DEFAULT FALSE,
                
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE,
                UNIQUE (conversation_id, username),
                
                INDEX idx_conversation_id (conversation_id),
                INDEX idx_username (username)
            );
        """)
        print("   ✓ conversation_participants table created")
        
        # 4. Create message_receipts table
        print("📋 Creating message_receipts table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS message_receipts (
                id SERIAL PRIMARY KEY,
                message_id INTEGER NOT NULL,
                username VARCHAR(255) NOT NULL,
                receipt_type VARCHAR(50) NOT NULL,
                    CHECK (receipt_type IN ('delivered', 'read', 'typing')),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE,
                
                INDEX idx_message_id (message_id),
                INDEX idx_username (username),
                INDEX idx_receipt_type (receipt_type)
            );
        """)
        print("   ✓ message_receipts table created")
        
        # 5. Create message_templates table
        print("📋 Creating message_templates table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS message_templates (
                id SERIAL PRIMARY KEY,
                creator_username VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                category VARCHAR(100),
                is_public BOOLEAN DEFAULT FALSE,
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (creator_username) REFERENCES users(username) ON DELETE CASCADE,
                UNIQUE (creator_username, name),
                
                INDEX idx_creator_username (creator_username),
                INDEX idx_category (category),
                INDEX idx_is_public (is_public)
            );
        """)
        print("   ✓ message_templates table created")
        
        # 6. Create blocked_users table
        print("📋 Creating blocked_users table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blocked_users (
                id SERIAL PRIMARY KEY,
                blocker_username VARCHAR(255) NOT NULL,
                blocked_username VARCHAR(255) NOT NULL,
                reason VARCHAR(255),
                blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (blocker_username) REFERENCES users(username) ON DELETE CASCADE,
                FOREIGN KEY (blocked_username) REFERENCES users(username) ON DELETE CASCADE,
                UNIQUE (blocker_username, blocked_username),
                
                INDEX idx_blocker (blocker_username),
                INDEX idx_blocked (blocked_username)
            );
        """)
        print("   ✓ blocked_users table created")
        
        # 7. Create message_notifications table
        print("📋 Creating message_notifications table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS message_notifications (
                id SERIAL PRIMARY KEY,
                message_id INTEGER NOT NULL,
                recipient_username VARCHAR(255) NOT NULL,
                notification_type VARCHAR(50),
                    CHECK (notification_type IN ('in_app', 'email', 'push', 'digest')),
                sent_at TIMESTAMP,
                read_at TIMESTAMP,
                
                FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE,
                FOREIGN KEY (recipient_username) REFERENCES users(username) ON DELETE CASCADE,
                
                INDEX idx_message_id (message_id),
                INDEX idx_recipient (recipient_username),
                INDEX idx_notification_type (notification_type)
            );
        """)
        print("   ✓ message_notifications table created")
        
        # 8. Create message_search_index table (for full-text search optimization)
        print("📋 Creating message_search_index table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS message_search_index (
                id SERIAL PRIMARY KEY,
                message_id INTEGER NOT NULL,
                search_text TEXT,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE,
                UNIQUE (message_id),
                
                INDEX idx_message_id (message_id)
            );
        """)
        print("   ✓ message_search_index table created")
        
        # Commit all changes
        conn.commit()
        print("\n" + "=" * 60)
        print("✅ Messaging System Database Migration Complete!")
        print("=" * 60)
        print("\nTables Created:")
        print("  1. conversations - Threading and grouping")
        print("  2. messages - Core message storage")
        print("  3. conversation_participants - Group participation")
        print("  4. message_receipts - Read/delivery status")
        print("  5. message_templates - Clinician message templates")
        print("  6. blocked_users - User blocking")
        print("  7. message_notifications - Notification tracking")
        print("  8. message_search_index - Search optimization")
        print("\nReady for API endpoint implementation!")
        
    except psycopg2.Error as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    run_migration()
