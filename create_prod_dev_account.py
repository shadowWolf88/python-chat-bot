#!/usr/bin/env python3
"""
Create developer account in PRODUCTION database
This script is only for use with the production DATABASE_URL from Railway
"""

import os
import sys
import psycopg2
from datetime import datetime
import hashlib

# Password hashing (mimics api.py)
try:
    from argon2 import PasswordHasher
    _ph = PasswordHasher()
    HAS_ARGON2 = True
except Exception:
    _ph = None
    HAS_ARGON2 = False

try:
    import bcrypt
    HAS_BCRYPT = True
except Exception:
    bcrypt = None
    HAS_BCRYPT = False

def hash_password(password: str) -> str:
    """Hash password using Argon2 > bcrypt > PBKDF2 fallback"""
    if HAS_ARGON2 and _ph:
        return _ph.hash(password)
    if HAS_BCRYPT:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    # Fallback PBKDF2
    salt = hashlib.sha256(password.encode()).hexdigest()[:16]
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 200000)
    return f"pbkdf2${dk.hex()}"

def hash_pin(pin: str, pin_salt='dev_fallback_salt') -> str:
    """Hash PIN using bcrypt or PBKDF2"""
    if HAS_BCRYPT:
        return bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()
    salt = hashlib.sha256(pin_salt.encode()).hexdigest()[:16]
    dk = hashlib.pbkdf2_hmac('sha256', pin.encode(), salt.encode(), 100000)
    return f"pbkdf2${dk.hex()}"

def create_production_dev_account():
    """Create dev_admin account in production database"""
    
    username = "dev_admin"
    password = "DevAdmin123!"
    pin = "1234"
    
    print("=" * 70)
    print("🔐 Creating Developer Account in PRODUCTION Database")
    print("=" * 70)
    
    # Get production DATABASE_URL from environment
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("\n❌ ERROR: DATABASE_URL environment variable not set!")
        print("\nTo create account in production:")
        print("1. Get your Railway DATABASE_URL from the environment variables")
        print("2. Set it: export DATABASE_URL='postgresql://user:pass@host:port/db'")
        print("3. Run this script again")
        print("\nTo find your Railway DATABASE_URL:")
        print("   - Go to your Railway project dashboard")
        print("   - Click on the PostgreSQL plugin")
        print("   - Copy the DATABASE_PUBLIC_URL")
        return False
    
    # Verify it's a production/Railway URL
    if 'localhost' in database_url or '127.0.0.1' in database_url:
        print("\n⚠️  WARNING: DATABASE_URL appears to be LOCAL, not production!")
        print(f"   URL: {database_url}")
        response = input("\nContinue anyway? (type 'yes' to confirm): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return False
    
    try:
        # Hash credentials
        print(f"\n⏳ Hashing password... ", end="", flush=True)
        hashed_password = hash_password(password)
        print("✓")
        
        print(f"⏳ Hashing PIN... ", end="", flush=True)
        hashed_pin = hash_pin(pin)
        print("✓")
        
        # Connect to PRODUCTION database
        print(f"⏳ Connecting to production database... ", end="", flush=True)
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        print("✓")
        
        # Check if account already exists
        print(f"⏳ Checking if account exists... ", end="", flush=True)
        cur.execute("SELECT username FROM users WHERE username = %s", (username,))
        existing = cur.fetchone()
        
        if existing:
            print("exists")
            print(f"\n⚠️  Account '{username}' already exists in production!")
            print(f"\nOptions:")
            print(f"  1. Reset password: Update credentials and restart")
            print(f"  2. Keep existing: Use current credentials")
            print(f"  3. Delete and recreate: DELETE FROM users WHERE username = '{username}';")
            
            update_response = input("\nDo you want to update the password? (yes/no): ")
            
            if update_response.lower() == 'yes':
                print(f"\n⏳ Updating password and PIN... ", end="", flush=True)
                cur.execute(
                    "UPDATE users SET password = %s, pin = %s WHERE username = %s",
                    (hashed_password, hashed_pin, username)
                )
                conn.commit()
                print("✓")
            else:
                print("\nKeeping existing credentials.")
                conn.close()
                return True
        else:
            # Create new account
            print("✓ (available)")
            print(f"⏳ Creating account in production... ", end="", flush=True)
            cur.execute("""
                INSERT INTO users (username, password, pin, role, last_login)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, hashed_password, hashed_pin, 'developer', datetime.now()))
            
            conn.commit()
            print("✓")
        
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ Developer Account Ready in Production!")
        print("=" * 70)
        print(f"\nLogin Credentials:")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        print(f"  PIN:      {pin}")
        print(f"\nAccess Production Dashboard:")
        print(f"  https://www.healing-space.org.uk/api/developer/dashboard")
        print(f"  (or: https://web-production-64594.up.railway.app/api/developer/dashboard)")
        print(f"\n1. Open the URL above")
        print(f"2. Enter username: {username}")
        print(f"3. Enter password: {password}")
        print(f"4. Enter PIN: {pin}")
        print(f"5. Click Login")
        print("\n" + "=" * 70)
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Database Connection Error:")
        print(f"   {str(e)}")
        print(f"\nVerify your DATABASE_URL is correct:")
        print(f"   Format: postgresql://user:pass@host:port/database")
        print(f"\nCheck Railway dashboard for the correct URL.")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_production_dev_account()
    sys.exit(0 if success else 1)
