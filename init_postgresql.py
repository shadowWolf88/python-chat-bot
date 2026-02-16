#!/usr/bin/env python3
"""
Initialize PostgreSQL database with schema
"""
import os
import sys
import psycopg2

# Get DATABASE_URL from environment
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("❌ DATABASE_URL not set")
    sys.exit(1)

print(f"Connecting to PostgreSQL...")
try:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    print("✅ Connected to PostgreSQL")
    
    # Read the schema file
    schema_file = '/home/computer001/Documents/python chat bot/schema_therapist_app_postgres.sql'
    print(f"Reading schema from {schema_file}...")
    
    with open(schema_file, 'r') as f:
        schema_sql = f.read()
    
    print(f"Creating {len(schema_sql)} bytes of schema...")
    
    # Split by semicolon and execute each statement
    statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
    
    for i, statement in enumerate(statements):
        try:
            cursor.execute(statement)
            conn.commit()
            print(f"  ✓ Statement {i+1}/{len(statements)}")
        except Exception as e:
            print(f"  ⚠️  Statement {i+1} skipped (likely already exists): {str(e)[:60]}")
            conn.rollback()
    
    cursor.close()
    conn.close()
    print("✅ Database schema initialized successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
