# 🚀 PHASE 5: Database Migration - SQLite to PostgreSQL

## Overview
This phase transitions the Healing Space application from SQLite to PostgreSQL, enabling production-scale reliability, performance, and concurrent user support on Railway.

**Status:** Starting  
**Estimated Duration:** 8-10 hours  
**Savepoint:** commit 84a8be1  
**Previous Phase:** Phase 4 (Database Integrity - COMPLETE ✅)

---

## 🎯 Objectives

1. **Schema Conversion:** SQLite → PostgreSQL (data type mappings, constraints)
2. **Data Migration:** Move all data from 3 SQLite databases to PostgreSQL
3. **Code Refactoring:** Update connection logic, queries, and test setup
4. **Local Validation:** Test against PostgreSQL before production
5. **Railway Deployment:** Deploy with PostgreSQL backend
6. **Post-Migration:** Monitoring, documentation, rollback plan

---

## 📋 Step-by-Step Implementation

### **STEP 1: Audit & Backup SQLite Databases** ⏳ IN PROGRESS

**Deliverables:**
- [ ] Fresh backups of all 3 SQLite databases
- [ ] Schema export documents
- [ ] Database audit report

**Actions:**  *

```bash
# 1. Create fresh backups
mkdir -p backups/pre_migration_$(date +%Y%m%d)
cp therapist_app.db backups/pre_migration_$(date +%Y%m%d)/
cp legacy_desktop/pet_game.db backups/pre_migration_$(date +%Y%m%d)/
cp ai_training_data.db backups/pre_migration_$(date +%Y%m%d)/

# 2. Export schema for each database
sqlite3 therapist_app.db .schema > schema_therapist_app.sql
sqlite3 legacy_desktop/pet_game.db .schema > schema_pet_game.sql
sqlite3 ai_training_data.db .schema > schema_ai_training_data.sql

# 3. Count tables and rows for audit
echo "=== DATABASE AUDIT ===" && \
sqlite3 therapist_app.db "SELECT count(*) FROM sqlite_master WHERE type='table';" && \
sqlite3 therapist_app.db "SELECT name, (SELECT count(*) FROM pragma_table_info(name)) as cols FROM sqlite_master WHERE type='table' ORDER BY name;" 
```

**Key Databases:**
- `therapist_app.db` - Main application (users, messages, feedback, appointments, clinical data)
- `pet_game.db` - Gamification (pet state, progression)
- `ai_training_data.db` - GDPR-compliant anonymized training data

---

### **STEP 2: Set Up Local PostgreSQL** ⏳ TODO

**Deliverables:**
- [ ] PostgreSQL 14+ installed locally
- [ ] Test database created
- [ ] psycopg2 installed in virtualenv

**Actions:**

```bash
# 1. Install PostgreSQL (macOS)
brew install postgresql@14

# 2. Start PostgreSQL
brew services start postgresql@14

# 3. Create test databases
createdb healing_space_test
createdb healing_space_pet_test
createdb healing_space_training_test

# 4. Install Python driver
pip install psycopg2-binary sqlalchemy

# 5. Verify connection
psql -U $(whoami) healing_space_test -c "SELECT version();"
```

---

### **STEP 3: Schema Conversion** ⏳ TODO

**Key Conversions:**

| SQLite | PostgreSQL | Notes |
|--------|-----------|-------|
| INTEGER PRIMARY KEY | SERIAL or BIGSERIAL | Auto-increment |
| AUTOINCREMENT | Serial default | Not needed in PG |
| TEXT | VARCHAR or TEXT | Unlimited TEXT in PG |
| DATETIME | TIMESTAMP | With timezone support |
| BLOB | BYTEA | Binary data |
| BOOLEAN | BOOLEAN | Native support |
| CREATE TABLE IF NOT EXISTS | CREATE TABLE IF NOT EXISTS | Compatible |

**Actions:**

1. Create `postgres_schema.py` - Automated schema generator
2. Generate CREATE TABLE scripts for all 3 databases
3. Handle constraint differences:
   - Foreign keys: Syntax identical ✅
   - Check constraints: Syntax identical ✅
   - Indexes: Syntax identical ✅
   - Triggers: Rewrite in PL/pgSQL if needed

**Sample Conversion:**
```sql
-- SQLite
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    email TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    role TEXT DEFAULT 'user',
    FOREIGN KEY(admin_id) REFERENCES users(username)
);

-- PostgreSQL
CREATE TABLE users (
    username VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role VARCHAR(50) DEFAULT 'user',
    FOREIGN KEY(admin_id) REFERENCES users(username)
);
```

---

### **STEP 4: Data Migration** ⏳ TODO

**Approach:**
- Use Python script with psycopg2
- Batch import (1000 rows at a time)
- Preserve foreign key relationships
- Handle NULL/empty values correctly
- Verify row counts before/after

**Actions:**

1. Create `migrate_data.py` script:
   - Connect to SQLite (source)
   - Connect to PostgreSQL (target)
   - Table-by-table transfer
   - Error logging & recovery
   - Row count validation

2. Test with small dataset first
3. Run full migration with logging

---

### **STEP 5: Refactor api.py for PostgreSQL** ⏳ TODO

**Current (SQLite):**
```python
import sqlite3
conn = sqlite3.connect("therapist_app.db", timeout=30.0)
cur = conn.cursor()
cur.execute("SELECT * FROM users WHERE username=?", (username,))
```

**New (PostgreSQL):**
```python
import psycopg2
import psycopg2.extras
conn = psycopg2.connect(
    host=os.environ.get('DB_HOST'),
    port=os.environ.get('DB_PORT', 5432),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASS'),
    database=os.environ.get('DB_NAME')
)
cur = conn.cursor()
cur.execute("SELECT * FROM users WHERE username=%s", (username,))
```

**Changes Required:**
- [ ] Replace `sqlite3` imports with `psycopg2`
- [ ] Update connection logic (environment variables)
- [ ] Replace `?` placeholders with `%s`
- [ ] Update `lastrowid` to `RETURNING` clause
- [ ] Handle transactions properly

---

### **STEP 6: Update SQL Queries** ⏳ TODO

**Parameter Placeholders:**
- SQLite: `?`
- PostgreSQL: `%s`

**UPSERT Syntax:**
```sql
-- SQLite
INSERT OR REPLACE INTO users (username, password) VALUES (?, ?)

-- PostgreSQL
INSERT INTO users (username, password) VALUES (%s, %s)
ON CONFLICT (username) DO UPDATE SET password=EXCLUDED.password
```

**Auto-increment:**
```sql
-- SQLite
INSERT INTO messages (...) VALUES (...)
lastrowid = cursor.lastrowid

-- PostgreSQL
INSERT INTO messages (...) VALUES (...) RETURNING id
id = cursor.fetchone()[0]
```

**Batch Operations:**
```python
# Use psycopg2.extras.execute_batch for performance
from psycopg2.extras import execute_batch
execute_batch(cur, 
    "INSERT INTO feedback (username, category, message) VALUES (%s, %s, %s)",
    data_list,
    page_size=1000
)
```

---

### **STEP 7: Testing** ⏳ TODO

**Local Testing:**
1. Run full test suite against PostgreSQL
2. Verify all 24 tests pass
3. Test performance (query speed, connection pooling)
4. Test connection recovery/retry logic

**Pre-Migration Checks:**
```bash
# 1. Run tests
GROQ_API_KEY="..." pytest tests/ -v

# 2. Check row counts (must match)
psql healing_space_test -c "SELECT COUNT(*) FROM users;"
sqlite3 therapist_app.db "SELECT COUNT(*) FROM users;"

# 3. Validate data integrity
# - Check foreign key relationships
# - Verify no NULL in NOT NULL columns
# - Sample data comparison
```

---

### **STEP 8: Railway Deployment** ⏳ TODO

**Railway Setup:**
1. Create PostgreSQL database on Railway
2. Note connection string from Railway dashboard
3. Set environment variables:
   ```
   DB_TYPE=postgresql
   DB_HOST=containers-us-west-...
   DB_PORT=5432
   DB_USER=postgres
   DB_PASS=...
   DB_NAME=railway
   ```
4. Deploy app with updated code
5. Monitor logs for errors

---

## 🛠️ Tools & Files

| File | Purpose |
|------|---------|
| `migrate_data.py` | Main migration script (TO CREATE) |
| `postgres_schema.py` | Schema generator (TO CREATE) |
| `api.py` | Connection refactoring (TO UPDATE) |
| `requirements.txt` | Add psycopg2 (TO UPDATE) |
| `tests/` | Run against PostgreSQL (TO UPDATE) |
| Backups | Pre-migration safety net |

---

## ✅ Rollback Plan

If migration fails:
1. Revert to savepoint 84a8be1
2. Restore SQLite databases from backups
3. Update environment variables back to SQLite
4. Deploy previous version
5. Post-mortem: Identify issues

---

## 📊 Success Criteria

- ✅ All 24 tests passing against PostgreSQL
- ✅ Row counts match (before/after)
- ✅ No data loss
- ✅ App runs on Railway with PostgreSQL
- ✅ Performance acceptable (queries < 100ms)
- ✅ Backup/restore procedures documented
- ✅ Monitoring alerts set up

---

## 📝 Environment Variables (Railway)

```
DB_TYPE=postgresql
DB_HOST=...railway.app
DB_PORT=5432
DB_USER=postgres
DB_PASS=...
DB_NAME=railway
DB_SSLMODE=require
```

---

**Phase 5 Kickoff:** February 4, 2026  
**Savepoint:** 84a8be1  
**Next Checkpoint:** After Step 2 (Local PostgreSQL ready)

