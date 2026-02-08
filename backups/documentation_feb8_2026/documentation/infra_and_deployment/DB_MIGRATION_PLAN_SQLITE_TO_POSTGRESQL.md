# Database Migration Plan: SQLite to PostgreSQL on Railway

## Overview
This document provides a comprehensive, step-by-step plan to migrate the Healing Space app's databases from SQLite to PostgreSQL, deploying on Railway. It covers preparation, schema conversion, data migration, codebase updates, testing, deployment, and post-migration validation. All steps are detailed for reliability, security, and minimal downtime.

---

## 1. Preparation

### 1.1. Audit Current Databases
- Identify all SQLite databases in use:
  - therapist_app.db
  - pet_game.db
  - ai_training_data.db
- Document all tables, columns, indexes, constraints, triggers, and relationships.
- Export current schema definitions for reference.

### 1.2. Backup & Version Control
- Create fresh backups of all SQLite databases (see backups/ folder).
- Store backups securely and verify integrity.
- Tag current codebase in git for rollback.

### 1.3. Railway Account & Project Setup
- Create/verify Railway account.
- Create a new Railway project for PostgreSQL.
- Note connection credentials (host, port, user, password, database name).
- Set up environment variables in Railway for DB connection.

---

## 2. Schema Migration

### 2.1. Convert SQLite Schema to PostgreSQL
- Use tools like `sqlite3`, `pgloader`, or manual conversion.
- Address differences:
  - Data types (e.g., INTEGER → SERIAL, TEXT → VARCHAR)
  - AUTOINCREMENT → SERIAL/IDENTITY
  - Boolean types
  - Default values and constraints
  - Indexes and foreign keys
  - Triggers (rewrite in PL/pgSQL if needed)
- Create PostgreSQL-compatible CREATE TABLE scripts for all databases.

### 2.2. Create PostgreSQL Databases & Schemas
- On Railway, create one PostgreSQL database (or multiple if needed).
- Apply CREATE TABLE scripts using `psql` or Railway's SQL console.
- Verify schema matches original intent.

---

## 3. Data Migration

### 3.1. Export Data from SQLite
- For each database:
  - Use `sqlite3 dbname .dump` or CSV export for each table.
  - Clean dumps to remove SQLite-specific syntax.

### 3.2. Import Data to PostgreSQL
- Use `pgloader`, `psql`, or custom Python scripts to import data.
- Address:
  - Data type conversions
  - NULL/empty values
  - Encoding issues
  - Foreign key integrity
- Validate row counts and sample data in PostgreSQL.

### 3.3. Large Data & GDPR
- For large tables, batch imports to avoid timeouts.
- For ai_training_data.db, ensure GDPR compliance and anonymization is preserved.

---

## 4. Codebase Refactoring

### 4.1. Update Database Connection Logic
- Replace SQLite connection code with PostgreSQL (e.g., use `psycopg2` or `SQLAlchemy`).
- Update connection strings to use Railway environment variables.
- Refactor DB initialization and migration logic in `api.py` and related modules.

### 4.2. Update SQL Queries
- Review all raw SQL queries for compatibility:
  - Parameter placeholders (`?` → `%s`)
  - LIMIT/OFFSET syntax
  - UPSERT/ON CONFLICT
  - Transaction handling
- Update ORM models if using SQLAlchemy.

### 4.3. Update DB Utility Scripts
- Refactor backup, export, and migration scripts for PostgreSQL.
- Update test setup to use PostgreSQL (local or Railway dev DB).

---

## 5. Testing & Validation

### 5.1. Local Testing
- Set up a local PostgreSQL instance for dev/testing.
- Run all unit and integration tests against PostgreSQL.
- Validate:
  - Data integrity
  - App functionality
  - Performance

### 5.2. Staging on Railway
- Deploy app to Railway with PostgreSQL.
- Test all endpoints and workflows.
- Monitor logs for errors and slow queries.

### 5.3. Security & Compliance
- Verify encryption, password hashing, and GDPR logic.
- Test backup and restore procedures.
- Validate audit logging and crisis alerting.

---

## 6. Deployment

### 6.1. Final Data Sync
- Schedule downtime or maintenance window.
- Freeze writes to SQLite databases.
- Perform final data export/import to PostgreSQL.
- Verify data consistency.

### 6.2. Switch Production
- Update Railway environment variables to point app to PostgreSQL.
- Deploy updated codebase.
- Monitor for errors and performance issues.

---

## 7. Post-Migration Tasks

### 7.1. Monitoring & Maintenance
- Set up Railway monitoring and alerts for DB health.
- Schedule regular backups of PostgreSQL.
- Document new backup/restore procedures.

### 7.2. Documentation & Training
- Update developer and ops documentation.
- Train team on PostgreSQL usage and Railway workflows.

### 7.3. Decommission Old SQLite
- Archive old SQLite backups securely.
- Remove SQLite DB files from production.
- Update codebase to remove SQLite dependencies.

---

## 8. Rollback Plan
- Keep SQLite backups and codebase tag for rollback.
- Document steps to revert to SQLite if needed.
- Test rollback procedure before migration.

---

## 9. Checklist Summary
- [ ] Audit and backup SQLite DBs
- [ ] Set up Railway PostgreSQL
- [ ] Convert and apply schema
- [ ] Migrate data
- [ ] Refactor codebase
- [ ] Test thoroughly
- [ ] Deploy and monitor
- [ ] Document and train
- [ ] Archive SQLite
- [ ] Prepare rollback

---

## References
- Railway docs: https://docs.railway.app/guides/postgres
- pgloader: https://pgloader.io/
- psycopg2: https://www.psycopg.org/docs/
- SQLAlchemy: https://docs.sqlalchemy.org/

---

**End of Migration Plan**
