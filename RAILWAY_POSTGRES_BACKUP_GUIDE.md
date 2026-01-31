# Railway PostgreSQL Backup Guide

## Automated Backups (Railway Platform)
- Railway automatically snapshots your Postgres database daily (see Railway dashboard > Postgres plugin > Backups tab).
- You can restore from these snapshots at any time.

## Manual Backup (pg_dump)
1. Install `pg_dump` (part of PostgreSQL client tools).
2. Get your `DATABASE_URL` from Railway (Postgres plugin > Connect > PostgreSQL URL).
3. Run this command to create a backup:

```
PGPASSWORD=yourpassword pg_dump -h yourhost -U youruser -d yourdb -p yourport -F c -b -v -f backup_file.dump
```
- Replace values from your `DATABASE_URL`.
- Example:
  - Host: `yourhost`
  - User: `youruser`
  - DB: `yourdb`
  - Port: `yourport`
  - Password: `yourpassword`

## Restore Backup
```
PGPASSWORD=yourpassword pg_restore -h yourhost -U youruser -d yourdb -p yourport -v backup_file.dump
```

## Tips
- Never commit backups to git.
- Store backups securely (offsite/cloud).
- Test restores regularly.

---
For more, see: https://docs.railway.app/databases/postgresql#backups
