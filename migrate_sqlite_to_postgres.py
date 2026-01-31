"""
Migration script to copy data from SQLite to PostgreSQL for Healing Space app.
- Reads from therapist_app.db (SQLite)
- Writes to PostgreSQL using DATABASE_URL
- Migrates all tables and data
- Requires psycopg2-binary and sqlite3

Usage:
  1. Set DATABASE_URL env var to your Railway Postgres URL.
  2. Place this script in project root.
  3. Run: python migrate_sqlite_to_postgres.py
"""
import os
import sqlite3
import psycopg2
from psycopg2.extras import execute_values
from urllib.parse import urlparse

def get_sqlite_connection(sqlite_path):
    return sqlite3.connect(sqlite_path)

def get_postgres_connection():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL env var not set!")
    result = urlparse(url)
    return psycopg2.connect(
        dbname=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port,
        sslmode='require'
    )

def get_table_names(sqlite_conn):
    cur = sqlite_conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    return [row[0] for row in cur.fetchall()]

def get_table_schema(sqlite_conn, table):
    cur = sqlite_conn.cursor()
    cur.execute(f"PRAGMA table_info({table});")
    return [(row[1], row[2]) for row in cur.fetchall()]

def fetch_all_rows(sqlite_conn, table):
    cur = sqlite_conn.cursor()
    cur.execute(f"SELECT * FROM {table};")
    return cur.fetchall()

def migrate_table(sqlite_conn, pg_conn, table):
    schema = get_table_schema(sqlite_conn, table)
    columns = [col for col, _ in schema]
    rows = fetch_all_rows(sqlite_conn, table)
    if not rows:
        print(f"Skipping {table}: no data.")
        return
    placeholders = ','.join(['%s'] * len(columns))
    insert_sql = f'INSERT INTO {table} ({', '.join(columns)}) VALUES %s ON CONFLICT DO NOTHING'
    with pg_conn.cursor() as cur:
        try:
            execute_values(cur, insert_sql, rows)
            pg_conn.commit()
            print(f"Migrated {len(rows)} rows to {table}.")
        except Exception as e:
            print(f"Error migrating {table}: {e}")
            pg_conn.rollback()

def main():
    sqlite_path = 'therapist_app.db'
    sqlite_conn = get_sqlite_connection(sqlite_path)
    pg_conn = get_postgres_connection()
    tables = get_table_names(sqlite_conn)
    print(f"Found tables: {tables}")
    for table in tables:
        migrate_table(sqlite_conn, pg_conn, table)
    sqlite_conn.close()
    pg_conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    main()
