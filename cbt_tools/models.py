"""
CBT Tools Models - PostgreSQL Backend

Manages data models for Cognitive Behavioral Therapy tools.
Uses PostgreSQL for consistency with main application.
"""

import os
import psycopg2


def get_db_connection(timeout=30.0):
    """Get PostgreSQL connection for CBT tools"""
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        conn = psycopg2.connect(database_url, connect_timeout=timeout)
    else:
        host = os.environ.get('DB_HOST')
        database = os.environ.get('DB_NAME')
        user = os.environ.get('DB_USER')
        password = os.environ.get('DB_PASSWORD')
        
        if not all([host, database, user, password]):
            raise RuntimeError(
                "CRITICAL: Database credentials incomplete for CBT tools. "
                "Required env vars: DB_HOST, DB_NAME, DB_USER, DB_PASSWORD or DATABASE_URL"
            )
        
        conn = psycopg2.connect(
            host=host, database=database, user=user, password=password,
            connect_timeout=timeout
        )
    
    return conn


def init_cbt_tools_schema():
    """Initialize CBT tools tables in PostgreSQL"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Create cbt_tool_entries table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cbt_tool_entries (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL,
                tool_type TEXT NOT NULL,
                data TEXT NOT NULL,
                mood_rating INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster queries
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_cbt_tool_entries_username_tooltype 
            ON cbt_tool_entries(username, tool_type, updated_at DESC)
        """)
        
        conn.commit()
    finally:
        cur.close()
        conn.close()
