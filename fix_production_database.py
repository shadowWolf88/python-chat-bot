#!/usr/bin/env python3
"""
Production Database Schema Fix Script
Date: 2026-02-05

This script applies schema fixes to the production database to resolve:
1. mood_logs entrestamp column issues
2. daily_tasks UNIQUE constraint missing
3. pet table ID auto-increment

IMPORTANT: Test on staging/backup environment first!
"""
import psycopg2
import os
import sys

def verify_and_fix_mood_logs(cur):
    """Verify and fix mood_logs table schema"""
    print("\n1. Checking mood_logs table...")

    # Check if table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'mood_logs'
        )
    """)
    if not cur.fetchone()[0]:
        print("   ✗ mood_logs table does not exist!")
        print("   → You need to run the full schema creation first")
        return False

    # Check for entrestamp column
    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'mood_logs'
        AND column_name IN ('entrestamp', 'entry_timestamp')
    """)
    columns = [row[0] for row in cur.fetchall()]

    if 'entrestamp' in columns:
        print("   ✓ entrestamp column exists")
        return True
    elif 'entry_timestamp' in columns:
        print("   ⚠ Found entry_timestamp instead of entrestamp")
        print("   → Renaming column...")
        cur.execute("ALTER TABLE mood_logs RENAME COLUMN entry_timestamp TO entrestamp")
        print("   ✓ Renamed to entrestamp")
        return True
    else:
        print("   ✗ No timestamp column found!")
        print("   → Adding entrestamp column...")
        cur.execute("ALTER TABLE mood_logs ADD COLUMN entrestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        print("   ✓ Added entrestamp column")
        return True

def verify_and_fix_daily_tasks(cur):
    """Verify and fix daily_tasks UNIQUE constraint"""
    print("\n2. Checking daily_tasks table...")

    # Check for UNIQUE constraint
    cur.execute("""
        SELECT COUNT(*) FROM information_schema.table_constraints
        WHERE table_name = 'daily_tasks'
        AND constraint_type = 'UNIQUE'
    """)
    constraint_count = cur.fetchone()[0]

    if constraint_count > 0:
        print("   ✓ UNIQUE constraint exists")
        return True
    else:
        print("   ⚠ UNIQUE constraint missing")
        print("   → Adding constraint...")
        cur.execute("""
            ALTER TABLE daily_tasks
            ADD CONSTRAINT daily_tasks_username_task_type_task_date_key
            UNIQUE (username, task_type, task_date)
        """)
        print("   ✓ Added UNIQUE constraint")
        return True

def verify_and_fix_pet_table(cur):
    """Verify and fix pet table ID auto-increment"""
    print("\n3. Checking pet table...")

    # Check if id has auto-increment
    cur.execute("""
        SELECT column_default FROM information_schema.columns
        WHERE table_name = 'pet' AND column_name = 'id'
    """)
    result = cur.fetchone()
    if not result:
        print("   ✗ pet table or id column does not exist!")
        return False

    default_value = result[0]
    if default_value and 'nextval' in str(default_value):
        print("   ✓ ID column has auto-increment")
        return True
    else:
        print("   ⚠ ID column missing auto-increment")
        print("   → Applying fix...")

        # Drop and recreate with sequence
        cur.execute("ALTER TABLE pet DROP CONSTRAINT IF EXISTS pet_pkey")
        cur.execute("CREATE SEQUENCE IF NOT EXISTS pet_id_seq")
        cur.execute("ALTER TABLE pet ALTER COLUMN id SET DEFAULT nextval('pet_id_seq')")
        cur.execute("ALTER SEQUENCE pet_id_seq OWNED BY pet.id")
        cur.execute("SELECT setval('pet_id_seq', COALESCE((SELECT MAX(id) FROM pet), 0) + 1, false)")
        cur.execute("ALTER TABLE pet ADD PRIMARY KEY (id)")

        print("   ✓ ID column now has auto-increment")
        return True

def main():
    print("=" * 70)
    print("Production Database Schema Fix Script")
    print("=" * 70)

    # Get database URL from environment or .env file
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        # Try to read from .env file
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith('DATABASE_URL='):
                        database_url = line.split('=', 1)[1].strip()
                        break

    if not database_url:
        print("\n✗ ERROR: DATABASE_URL not found in environment or .env file!")
        print("Please set it to your production database connection string.")
        print("\nExample:")
        print("  export DATABASE_URL='postgresql://user:pass@host:port/dbname'")
        sys.exit(1)

    print(f"\nConnecting to database...")
    print(f"URL: {database_url.split('@')[1] if '@' in database_url else '***'}")

    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = False
        cur = conn.cursor()
        print("✓ Connected successfully!")

        # Run fixes
        results = []
        results.append(verify_and_fix_mood_logs(cur))
        results.append(verify_and_fix_daily_tasks(cur))
        results.append(verify_and_fix_pet_table(cur))

        # Ask for confirmation before committing
        print("\n" + "=" * 70)
        print("Review the changes above.")
        response = input("Do you want to COMMIT these changes? (yes/no): ")

        if response.lower() in ['yes', 'y']:
            conn.commit()
            print("\n✓ All changes committed successfully!")
        else:
            conn.rollback()
            print("\n✗ Changes rolled back (not applied)")
            sys.exit(0)

        # Final verification
        print("\n" + "=" * 70)
        print("Final Verification")
        print("=" * 70)

        # Verify mood_logs
        cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'mood_logs' AND column_name = 'entrestamp'
        """)
        if cur.fetchone():
            print("✓ mood_logs.entrestamp exists")
        else:
            print("✗ mood_logs.entrestamp MISSING")

        # Verify daily_tasks constraint
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.table_constraints
            WHERE table_name = 'daily_tasks' AND constraint_type = 'UNIQUE'
        """)
        if cur.fetchone()[0] > 0:
            print("✓ daily_tasks UNIQUE constraint exists")
        else:
            print("✗ daily_tasks UNIQUE constraint MISSING")

        # Verify pet id
        cur.execute("""
            SELECT column_default FROM information_schema.columns
            WHERE table_name = 'pet' AND column_name = 'id'
        """)
        default = cur.fetchone()[0]
        if default and 'nextval' in str(default):
            print("✓ pet.id has auto-increment")
        else:
            print("✗ pet.id auto-increment MISSING")

        cur.close()
        conn.close()

        print("\n" + "=" * 70)
        print("Schema fixes completed!")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Test the application to verify fixes work")
        print("2. Monitor logs for any remaining errors")
        print("3. Create a backup of the fixed database")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)

if __name__ == '__main__':
    main()
