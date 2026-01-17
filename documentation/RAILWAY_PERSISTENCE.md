# Railway Database Persistence

## Problem
Railway's filesystem is **ephemeral** - it gets wiped on every deployment. Your SQLite database is deleted each time you push code.

## Solution 1: Railway Volume (Recommended for SQLite)

### Step 1: Create Volume
1. Go to https://railway.app
2. Open your project
3. Click on your service
4. Go to **"Data"** tab (or **"Volumes"**)
5. Click **"New Volume"**
6. Configure:
   - **Mount Path**: `/app/data`
   - **Name**: `therapist-db-volume`
   - **Size**: 1 GB (free tier)
7. Click **"Add Volume"**

### Step 2: Verify Code Changes
The code has been updated to automatically use the volume path:
- Volume path: `/app/data/therapist_app.db`
- Local path: `therapist_app.db`

### Step 3: Deploy
```bash
git add -A
git commit -m "Add Railway volume support for database persistence"
git push origin main
```

### Step 4: Verify Persistence
1. Deploy and create test accounts
2. Push another commit
3. Verify accounts still exist after deployment

## Solution 2: PostgreSQL (Recommended for Production)

See [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md) for migration guide.

### Why PostgreSQL?
- ✅ Native Railway integration
- ✅ Automatic backups
- ✅ Better performance at scale
- ✅ No volume setup needed
- ✅ Free tier available

### Quick PostgreSQL Setup
1. Railway Dashboard → Add → Database → PostgreSQL
2. Copy `DATABASE_URL` from PostgreSQL service
3. Update code to use PostgreSQL (requires SQLAlchemy or psycopg2)
4. Migrate data from SQLite

## Current Setup

The app now uses:
```python
def get_db_path():
    if os.path.exists('/app/data'):  # Railway volume
        return '/app/data/therapist_app.db'
    return 'therapist_app.db'  # Local development
```

All database connections use `DB_PATH` variable.

## Troubleshooting

### Volume Not Mounting
- Check Railway logs: `railway logs`
- Verify mount path is exactly `/app/data`
- Restart deployment after adding volume

### Database Still Resetting
- Ensure volume is attached to correct service
- Check that `DB_PATH` is used in all queries
- Verify volume shows in Railway dashboard

### Permission Errors
```bash
# Railway needs write permissions
# Add to Dockerfile if using custom image:
RUN mkdir -p /app/data && chmod 777 /app/data
```

## Backup Strategy

Even with volumes, **always backup**:

```bash
# Download database from Railway
railway run sqlite3 /app/data/therapist_app.db ".backup backup.db"

# Or use automated backups endpoint
curl -X POST https://your-app.railway.app/api/admin/backup
```

## Cost Considerations

| Storage     | Free Tier | Paid Tier    |
|-------------|-----------|--------------|
| Volume      | 1 GB      | $0.25/GB/mo  |
| PostgreSQL  | 1 GB      | $0.01/GB/mo  |

PostgreSQL is cheaper and more reliable for production.
