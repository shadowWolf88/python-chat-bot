import psycopg2
import os
from datetime import datetime

def log_event(username, actor, action, details=None):
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cur = conn.cursor()
        cur.execute("INSERT INTO audit_logs (username, actor, action, details, timestamp) VALUES (%s,%s,%s,%s,%s)",
                     (username, actor, action, details or "", datetime.now()))
        conn.commit()
        conn.close()
    except Exception:
        # Best-effort logging; avoid crashing app if audit fails
        pass
