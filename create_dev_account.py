#!/usr/bin/env python3
"""
Create a developer account for the Developer Dashboard
"""

import os
import sys

# Set DEBUG mode to avoid production checks
os.environ['DEBUG'] = '1'

# Add current directory to path to import api.py
sys.path.insert(0, os.getcwd())

from api import get_db_connection, hash_password, hash_pin
from datetime import datetime

def create_developer_account():
    """Create a developer account"""
    
    username = "dev_admin"
    password = "DevAdmin123!"
    pin = "1234"
    
    print("=" * 60)
    print("🔐 Creating Developer Account")
    print("=" * 60)
    
    try:
        # Hash credentials
        print(f"Hashing password... ", end="", flush=True)
        hashed_password = hash_password(password)
        print("✓")
        
        print(f"Hashing PIN... ", end="", flush=True)
        hashed_pin = hash_pin(pin)
        print("✓")
        
        # Connect to database
        print(f"Connecting to database... ", end="", flush=True)
        conn = get_db_connection()
        cur = conn.cursor()
        print("✓")
        
        # Check if account already exists
        print(f"Checking if account exists... ", end="", flush=True)
        cur.execute("SELECT username FROM users WHERE username = %s", (username,))
        existing = cur.fetchone()
        
        if existing:
            print("exists already")
            print(f"\n❌ Account '{username}' already exists!")
            print(f"   If you want to reset it, delete it first:")
            print(f"   DELETE FROM users WHERE username = '{username}';")
            conn.close()
            return False
        
        print("✓ (available)")
        
        # Create account
        print(f"Creating account... ", end="", flush=True)
        cur.execute("""
            INSERT INTO users (username, password, pin, role, last_login)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, hashed_password, hashed_pin, 'developer', datetime.now()))
        
        conn.commit()
        print("✓")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Developer Account Created Successfully!")
        print("=" * 60)
        print(f"\nLogin Credentials:")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        print(f"  PIN:      {pin}")
        print(f"\nAccess Dashboard:")
        print(f"  http://localhost:5000/api/developer/dashboard")
        print("\n" + "=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_developer_account()
    sys.exit(0 if success else 1)
