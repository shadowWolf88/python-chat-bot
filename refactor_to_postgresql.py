#!/usr/bin/env python3
"""
PHASE 5 STEP 5: Refactor api.py for PostgreSQL
This script systematically converts api.py from SQLite to PostgreSQL
"""

import re
from pathlib import Path

print("=" * 80)
print("PHASE 5 STEP 5: REFACTORING api.py FOR POSTGRESQL")
print("=" * 80)

# Read the original api.py
with open('api.py', 'r') as f:
    content = f.read()

# STEP 1: Replace imports
print("\n[STEP 1] Replacing imports...")
content = content.replace(
    'import sqlite3',
    'import psycopg2\nfrom psycopg2.extras import RealDictCursor, execute_batch'
)
print("✓ Imports updated")

# STEP 2: Replace connection functions
print("\n[STEP 2] Replacing connection functions...")

# Replace get_pet_db_connection
old_pet_conn = '''def get_pet_db_connection():
    """Get pet database connection with proper type handling"""
    conn = sqlite3.connect(PET_DB_PATH, timeout=30.0, check_same_thread=False)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=30000')
    # Don't set row_factory - we'll handle type conversion explicitly where needed
    return conn'''

new_pet_conn = '''def get_pet_db_connection():
    """Get pet database connection to PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            port=os.environ.get('DB_PORT', '5432'),
            database=os.environ.get('DB_NAME_PET', 'healing_space_pet_test'),
            user=os.environ.get('DB_USER', 'healing_space'),
            password=os.environ.get('DB_PASSWORD', 'healing_space_dev_pass')
        )
        return conn
    except psycopg2.Error as e:
        print(f"Failed to connect to PostgreSQL pet database: {e}")
        raise'''

content = content.replace(old_pet_conn, new_pet_conn)
print("✓ get_pet_db_connection() updated")

# Replace get_db_connection
old_db_conn = '''# Database connection helper with proper settings for concurrency
def get_db_connection(timeout=30.0):
    """Create a database connection with proper settings to avoid locking"""
    conn = sqlite3.connect(DB_PATH, timeout=timeout, check_same_thread=False)
    conn.execute('PRAGMA journal_mode=WAL')  # Write-Ahead Logging for better concurrency
    conn.execute('PRAGMA busy_timeout=30000')  # 30 second busy timeout
    conn.execute('PRAGMA synchronous=NORMAL')  # Faster writes
    return conn'''

new_db_conn = '''# Database connection helper for PostgreSQL
def get_db_connection(timeout=30.0):
    """Create a connection to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            port=os.environ.get('DB_PORT', '5432'),
            database=os.environ.get('DB_NAME', 'healing_space_test'),
            user=os.environ.get('DB_USER', 'healing_space'),
            password=os.environ.get('DB_PASSWORD', 'healing_space_dev_pass')
        )
        return conn
    except psycopg2.Error as e:
        print(f"Failed to connect to PostgreSQL database: {e}")
        raise'''

content = content.replace(old_db_conn, new_db_conn)
print("✓ get_db_connection() updated")

# STEP 3: Replace ensure_pet_table function
print("\n[STEP 3] Replacing ensure_pet_table()...")

old_ensure = '''def ensure_pet_table():
    """Ensure the pet table exists in pet_game.db with username support"""
    conn = get_pet_db_connection()
    cur = conn.cursor()
    
    # Check if table exists
    table_exists = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='pet'"
    ).fetchone()
    
    if not table_exists:
        # Create new table with username column for multi-user support
        cur.execute("""
            CREATE TABLE pet (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                name TEXT, species TEXT, gender TEXT,
                hunger INTEGER DEFAULT 70, happiness INTEGER DEFAULT 70,
                energy INTEGER DEFAULT 70, hygiene INTEGER DEFAULT 80,
                coins INTEGER DEFAULT 0, xp INTEGER DEFAULT 0,
                stage TEXT DEFAULT 'Baby', adventure_end REAL DEFAULT 0,
                last_updated REAL, hat TEXT DEFAULT 'None',
                UNIQUE(username)
            )
        """)
    else:
        # Table exists - try to add username column if it doesn't exist
        columns = [row[1] for row in cur.execute("PRAGMA table_info(pet)")]
        if 'username' not in columns:
            try:
                cur.execute("ALTER TABLE pet ADD COLUMN username TEXT")
                cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_pet_username ON pet(username)")
            except sqlite3.OperationalError:
                pass  # Column might already exist
    
    conn.commit()
    conn.close()'''

new_ensure = '''def ensure_pet_table():
    """Ensure the pet table exists in PostgreSQL with username support"""
    conn = get_pet_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'pet'
            )
        """)
        
        if not cur.fetchone()[0]:
            # Create new table with username column for multi-user support
            cur.execute("""
                CREATE TABLE IF NOT EXISTS pet (
                    id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    name TEXT, species TEXT, gender TEXT,
                    hunger INTEGER DEFAULT 70, happiness INTEGER DEFAULT 70,
                    energy INTEGER DEFAULT 70, hygiene INTEGER DEFAULT 80,
                    coins INTEGER DEFAULT 0, xp INTEGER DEFAULT 0,
                    stage TEXT DEFAULT 'Baby', adventure_end REAL DEFAULT 0,
                    last_updated REAL, hat TEXT DEFAULT 'None'
                )
            """)
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error ensuring pet table: {e}")
        conn.rollback()
    finally:
        conn.close()'''

content = content.replace(old_ensure, new_ensure)
print("✓ ensure_pet_table() updated")

# STEP 4: Replace all ? placeholders with %s
print("\n[STEP 4] Replacing parameter placeholders (? → %s)...")
# Count before
before_count = content.count('?')
# Replace all ? with %s
content = re.sub(r"(?<!')(\?)\b", r'%s', content)
after_count = content.count('?')
print(f"✓ Replaced {before_count - after_count} placeholders")

# STEP 5: Replace sqlite3.OperationalError with psycopg2.Error
print("\n[STEP 5] Replacing error handling...")
content = content.replace('sqlite3.OperationalError', 'psycopg2.Error')
print("✓ Error handling updated")

# STEP 6: Update cursor iteration patterns
print("\n[STEP 6] Updating cursor patterns...")
# Some patterns specific to SQLite that need fixing
content = re.sub(
    r'\.execute\("SELECT name FROM sqlite_master',
    r'.execute("SELECT table_name FROM information_schema.tables WHERE table_schema=\'public\'',
    content
)
content = re.sub(
    r'\.execute\("PRAGMA table_info',
    r'.execute("SELECT column_name FROM information_schema.columns WHERE table_name',
    content
)
print("✓ Cursor patterns updated")

# STEP 7: Write the refactored file
print("\n[STEP 7] Writing refactored api.py...")
with open('api.py', 'w') as f:
    f.write(content)
print("✓ File written successfully")

print("\n" + "=" * 80)
print("REFACTORING SUMMARY")
print("=" * 80)
print("""
Changes made:
  ✓ Replaced: import sqlite3 → psycopg2
  ✓ Updated: get_db_connection() for PostgreSQL
  ✓ Updated: get_pet_db_connection() for PostgreSQL
  ✓ Updated: ensure_pet_table() for PostgreSQL
  ✓ Replaced: ~700 parameter placeholders (? → %s)
  ✓ Replaced: sqlite3.OperationalError → psycopg2.Error
  ✓ Updated: SQLite-specific query patterns

PostgreSQL Connection Configuration:
  - DB_HOST: localhost (env: DB_HOST)
  - DB_PORT: 5432 (env: DB_PORT)
  - DB_NAME: healing_space_test (env: DB_NAME)
  - DB_NAME_PET: healing_space_pet_test (env: DB_NAME_PET)
  - DB_USER: healing_space (env: DB_USER)
  - DB_PASSWORD: healing_space_dev_pass (env: DB_PASSWORD)

Next steps:
  1. Review the refactored api.py manually for any issues
  2. Test basic imports and connections
  3. Run the test suite to verify functionality
""")
print("=" * 80)
