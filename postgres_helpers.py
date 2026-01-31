import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Helper to get Postgres connection from env

def get_postgres_conn():
    url = os.environ.get('DATABASE_URL')
    if not url:
        raise RuntimeError('DATABASE_URL environment variable not set')
    return psycopg2.connect(url, cursor_factory=RealDictCursor)

# Example usage:
# with get_postgres_conn() as conn:
#     with conn.cursor() as cur:
#         cur.execute('SELECT 1')
#         print(cur.fetchone())
