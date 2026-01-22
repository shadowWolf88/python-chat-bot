import os
import sys
import sqlite3
import json
from datetime import datetime

# Ensure project root is on sys.path for test discovery
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import api


def setup_tmp_db(tmp_path):
    db_path = str(tmp_path / "test_integration.db")
    api.DB_PATH = db_path
    if os.path.exists(db_path):
        os.remove(db_path)
    api.init_db()
    return db_path


def test_fhir_export_and_chat(tmp_path):
    db = setup_tmp_db(tmp_path)

    # Seed a user and some mood logs
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username,password,role,full_name) VALUES (?,?,?,?)", ('u_fhir', 'p', 'user', 'FHIR User'))
    cur.execute("INSERT INTO mood_logs (username, mood_val, sleep_val, meds, notes, entrestamp) VALUES (?,?,?,?,?,?)",
                ('u_fhir', 3, 7.5, 'none', 'feeling ok', datetime.now().isoformat()))
    conn.commit()
    conn.close()

    with api.app.test_client() as c:
        # FHIR export
        r = c.get('/api/export/fhir?username=u_fhir')
        assert r.status_code == 200
        data = r.get_json()
        assert data.get('success') is True
        assert 'bundle' in data

        # Chat: send a message and retrieve history
        r2 = c.post('/api/therapy/chat', json={'username': 'u_fhir', 'message': 'hello'})
        assert r2.status_code == 200
        jr = r2.get_json()
        assert jr.get('success') is True

        # Retrieve chat history
        h = c.get('/api/therapy/history?username=u_fhir')
        assert h.status_code == 200
        hj = h.get_json()
        assert hj.get('success') is True
        assert isinstance(hj.get('history'), list)
