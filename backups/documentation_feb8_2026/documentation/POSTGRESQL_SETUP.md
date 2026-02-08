# PostgreSQL Setup for Railway Deployment

## Overview
This guide explains how to migrate from SQLite to PostgreSQL for production deployment on Railway.

## Why PostgreSQL?
- **Persistence**: Railway's filesystem is ephemeral - files reset on each deploy
- **Scalability**: Better performance for multiple concurrent users
- **Production-ready**: Industry standard for web applications
- **Backups**: Railway provides automatic PostgreSQL backups

## Current Setup (SQLite)
The app currently uses SQLite with these database files:
- `therapist_app.db` - Main application database
- `pet_game.db` - Pet game state (separate database)

**Note**: These files are lost on every Railway deployment unless using volumes or PostgreSQL.

## Railway PostgreSQL Setup

### Step 1: Provision PostgreSQL Database

1. Go to your Railway project dashboard
2. Click "+ New" → "Database" → "Add PostgreSQL"
3. Railway will provision a PostgreSQL database and provide connection details

### Step 2: Get Connection Details

Railway automatically provides these environment variables:
```
DATABASE_URL - Full connection string
PGHOST - Database host
PGPORT - Database port (usually 5432)
PGUSER - Database username
PGPASSWORD - Database password
PGDATABASE - Database name
```

### Step 3: Update Code for PostgreSQL

Install required package:
```bash
pip install psycopg2-binary
```

Add to `requirements.txt`:
```
psycopg2-binary==2.9.9
```

### Step 4: Update Database Connection Code

Replace SQLite connections with PostgreSQL:

```python
import psycopg2
from psycopg2.extras import RealDictCursor

# Get connection
def get_db_connection():
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # PostgreSQL (production)
        return psycopg2.connect(database_url)
    else:
        # SQLite (local development)
        return sqlite3.connect('therapist_app.db')
```

### Step 5: Schema Differences

Key differences between SQLite and PostgreSQL:

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| Auto-increment | `INTEGER PRIMARY KEY AUTOINCREMENT` | `SERIAL PRIMARY KEY` |
| Boolean | `INTEGER DEFAULT 0` | `BOOLEAN DEFAULT FALSE` |
| Timestamp | `DATETIME` | `TIMESTAMP` |
| String placeholder | `?` | `%s` |

### Step 6: Migration Script

Create `migrate_to_postgres.py`:

```python
import sqlite3
import psycopg2
import os

def migrate_sqlite_to_postgres():
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('therapist_app.db')
    sqlite_cur = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    pg_cur = pg_conn.cursor()
    
    # Get all table names
    tables = sqlite_cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    
    for table in tables:
        table_name = table[0]
        
        # Get data
        rows = sqlite_cur.execute(f"SELECT * FROM {table_name}").fetchall()
        columns = [desc[0] for desc in sqlite_cur.description]
        
        # Insert into PostgreSQL
        if rows:
            placeholders = ','.join(['%s'] * len(columns))
            query = f"INSERT INTO {table_name} VALUES ({placeholders})"
            pg_cur.executemany(query, rows)
    
    pg_conn.commit()
    print("Migration complete!")
```

## Environment Variables Required

Add these to Railway:

```bash
# Database (automatically set by Railway PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Email (for password reset)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@healingspace.app

# App URL (for reset links)
APP_URL=https://your-app.railway.app

# Existing variables
GROQ_API_KEY=your-groq-key
ENCRYPTION_KEY=your-fernet-key
PIN_SALT=your-pin-salt
DEBUG=0
```

## Gmail SMTP Setup (for Password Reset)

1. Enable 2-Factor Authentication on your Gmail account
2. Go to Google Account → Security → App Passwords
3. Generate app password for "Mail"
4. Use generated password as `SMTP_PASSWORD`

## Alternative: Keep SQLite with Railway Volumes

If you prefer to keep SQLite:

1. Add volume in Railway dashboard
2. Mount volume to `/data`
3. Update code to use `/data/therapist_app.db`

**Pros**: Simple, no code changes
**Cons**: Not scalable, manual backup management

## Testing PostgreSQL Locally

Install PostgreSQL locally:
```bash
# macOS
brew install postgresql

# Ubuntu
sudo apt install postgresql

# Start PostgreSQL
pg_ctl -D /usr/local/var/postgres start

# Create database
createdb therapist_app
```

Set local environment:
```bash
export DATABASE_URL=postgresql://localhost/therapist_app
```

## Recommended Approach

1. **Development**: Use SQLite (simple, fast)
2. **Production**: Use PostgreSQL (reliable, scalable)
3. **Auto-detect** in code based on `DATABASE_URL` presence

## Current Status

✅ Email and phone fields added to registration
✅ Password reset API endpoint created
✅ Email sending functionality implemented
⚠️ **Still using SQLite** - works for now but data resets on deploy
📝 Migration to PostgreSQL recommended for production

## Next Steps

1. Provision PostgreSQL on Railway
2. Install `psycopg2-binary`
3. Update database connection code
4. Run migration script
5. Test thoroughly before deploying
