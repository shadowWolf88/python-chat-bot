# Setting Up Persistent Storage on Railway

This guide explains how to set up persistent storage for Healing Space UK on Railway, using either a Railway Volume (for SQLite) or PostgreSQL (recommended for production and scaling).

---

## Option 1: Railway Volume (for SQLite)

**Best for:** Pilots, small-scale trials, or when you want to keep using SQLite.

### Steps:
1. **Go to your Railway project dashboard.**
2. **Click the 'Add Plugin' button.**
3. **Select 'Volume'.**
   - Choose a mount path (e.g., `/data`).
   - Set the size (e.g., 1GB or more as needed).
4. **Update your environment variables:**
   - Set your SQLite DB path to the volume, e.g., `/data/therapist_app.db`.
   - In `api.py`, ensure the DB path logic uses the volume path if available.
5. **Redeploy your app.**
   - The database will now persist across deploys and restarts.

**Note:** Volumes are only available on paid Railway plans.

---

## Option 2: Railway PostgreSQL (Recommended)

**Best for:** Production, university pilots, or scaling beyond a few users.

### Steps:
1. **Go to your Railway project dashboard.**
2. **Click the 'Add Plugin' button.**
3. **Select 'PostgreSQL'.**
   - Railway will provision a managed PostgreSQL instance.
4. **Copy the `DATABASE_URL` provided by Railway.**
5. **Update your app to use PostgreSQL:**
   - Install `psycopg2` or `asyncpg` in your requirements.txt.
   - Update your database connection logic in `api.py` to use PostgreSQL if `DATABASE_URL` is set.
   - Migrate your SQLite schema/data to PostgreSQL (see below).
6. **Set the `DATABASE_URL` as an environment variable in Railway.**
7. **Redeploy your app.**

---

## Migrating Data from SQLite to PostgreSQL

1. Use a tool like `sqlite3` to export your data:
   ```sh
   sqlite3 therapist_app.db .dump > dump.sql
   ```
2. Use a tool like `pgloader` or `sqlalchemy` to import into PostgreSQL.
   - Or manually edit `dump.sql` for PostgreSQL compatibility and run:
   ```sh
   psql $DATABASE_URL -f dump.sql
   ```

---

## References
- Railway Volumes: https://docs.railway.app/develop/volumes
- Railway PostgreSQL: https://docs.railway.app/databases/postgresql
- Example migration: https://stackoverflow.com/questions/1038570/how-to-import-sqlite-database-into-postgresql

---

**Tip:** For production, always use PostgreSQL for reliability, backups, and scaling.
