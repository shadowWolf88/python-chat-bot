#!/usr/bin/env python3
"""Diagnose pet table and creation issues"""

import os
import sys
import psycopg2
from datetime import datetime

# Get database URL
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)

print("=" * 60)
print("PET TABLE DIAGNOSTIC")
print("=" * 60)

try:
    conn = psycopg2.connect(database_url)
    cur = conn.cursor()
    
    # 1. Check if pet table exists
    print("\n1. Checking if 'pet' table exists...")
    cur.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'pet'
        )
    """)
    exists = cur.fetchone()[0]
    print(f"   Pet table exists: {exists}")
    
    if exists:
        # 2. Get table structure
        print("\n2. Pet table structure:")
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'pet'
            ORDER BY ordinal_position
        """)
        for row in cur.fetchall():
            print(f"   {row[0]}: {row[1]} (nullable={row[2]}, default={row[3]})")
        
        # 3. Check for constraints
        print("\n3. Table constraints:")
        cur.execute("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints
            WHERE table_name = 'pet'
        """)
        for row in cur.fetchall():
            print(f"   {row[0]}: {row[1]}")
        
        # 4. Try to insert test pet
        print("\n4. Testing pet insertion:")
        try:
            username = "test_user_" + str(int(datetime.now().timestamp()))
            cur.execute("""
                INSERT INTO pet (username, name, species, gender, hunger, happiness, energy, hygiene, 
                               coins, xp, stage, adventure_end, last_updated, hat)
                VALUES (%s, %s, %s, %s, 70, 70, 70, 80, 0, 0, 'Baby', 0, %s, 'None')
            """, (username, "TestPet", "Dog", "Male", datetime.now().timestamp()))
            conn.commit()
            print(f"   ✓ Successfully inserted pet for {username}")
            
            # Verify it was inserted
            cur.execute("SELECT * FROM pet WHERE username = %s", (username,))
            pet = cur.fetchone()
            if pet:
                print(f"   ✓ Pet verified in database: {pet[1]} (id={pet[0]}, name={pet[2]})")
            
            # Clean up
            cur.execute("DELETE FROM pet WHERE username = %s", (username,))
            conn.commit()
            print(f"   ✓ Cleaned up test pet")
            
        except Exception as e:
            print(f"   ✗ Error inserting pet: {e}")
            import traceback
            traceback.print_exc()
    
    else:
        print("   ✗ Pet table does NOT exist!")
        print("\n   Creating pet table...")
        cur.execute("""
            CREATE TABLE pet (
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
        print("   ✓ Pet table created!")
    
    # 5. Count existing pets
    print("\n5. Pet count:")
    cur.execute("SELECT COUNT(*) FROM pet")
    count = cur.fetchone()[0]
    print(f"   Total pets in database: {count}")
    
    # 6. Check for duplicate usernames
    print("\n6. Checking for duplicate usernames:")
    cur.execute("""
        SELECT username, COUNT(*) as cnt
        FROM pet
        GROUP BY username
        HAVING COUNT(*) > 1
    """)
    dups = cur.fetchall()
    if dups:
        print(f"   ✗ Found {len(dups)} duplicate usernames:")
        for dup in dups:
            print(f"      {dup[0]}: {dup[1]} pets")
    else:
        print("   ✓ No duplicate usernames")
    
    conn.close()
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
