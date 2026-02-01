# Production Deployment Guide

This guide covers deploying the therapy chatbot application to production with PostgreSQL, Redis, rate limiting, monitoring, and background job processing.

## 🚀 Quick Start

### 1. Add Production Dependencies

Already done! Check `requirements.txt` for these critical packages:
- `psycopg2-binary` - PostgreSQL driver
- `redis` - Redis client
- `celery` - Background job processing
- `flask-limiter` - Rate limiting
- `prometheus-flask-exporter` - Metrics
- `opentelemetry-*` - Distributed tracing
- `python-json-logger` - Structured logging

### 2. Environment Variables

Add these to your Railway project:

#### Required Variables

```bash
# PostgreSQL Database (Railway provides this automatically)
DATABASE_URL=postgresql://user:password@host:port/database

# Redis (add Redis plugin in Railway)
REDIS_URL=redis://default:password@host:port

# Application Settings
ENVIRONMENT=production
SERVICE_NAME=therapy-chatbot
SERVICE_VERSION=1.0.0

# Security
SECRET_KEY=<generate-strong-random-key>
PIN_SALT=<generate-strong-random-salt>

# CORS Settings
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# API Keys
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
```

#### Optional Variables

```bash
# SMTP for Email (optional - for background email tasks)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Debug (should be false in production)
DEBUG=false
```

### 3. Provision PostgreSQL on Railway

1. Go to your Railway project
2. Click "New" → "Database" → "PostgreSQL"
3. Railway will automatically set `DATABASE_URL` environment variable
4. The application will automatically use PostgreSQL when `DATABASE_URL` is set

### 4. Provision Redis on Railway

1. Go to your Railway project
2. Click "New" → "Database" → "Redis"
3. Railway will automatically set `REDIS_URL` environment variable
4. Redis is used for:
   - Rate limiting (distributed across instances)
   - Celery message broker
   - Celery result backend
   - Session storage (optional)

### 5. Integrate Production Components

The production components are already created in separate modules:
- `database.py` - Connection pooling
- `rate_limiting.py` - Rate limiting configuration
- `monitoring.py` - Observability setup
- `celery_config.py` - Background job configuration
- `celery_tasks.py` - Task definitions

To integrate into `api.py`, add the code from `integration_snippet.py` after line 63 (after `DEBUG = ...`).

### 6. Deploy to Railway

```bash
# Commit changes
git add .
git commit -m "Add production infrastructure: PostgreSQL, Redis, monitoring, Celery"
git push origin main

# Railway will automatically deploy
```

## 📊 Monitoring Endpoints

After deployment, these endpoints will be available:

- **`/health`** - Health check with database connectivity
- **`/metrics`** - Prometheus metrics for monitoring
- **`/api/*`** - All API endpoints with rate limiting

Example health check response:
```json
{
  "status": "healthy",
  "service": "therapy-chatbot",
  "version": "1.0.0",
  "environment": "production",
  "timestamp": "2026-01-31T16:00:00.000Z",
  "checks": {
    "database": {
      "status": "healthy",
      "type": "postgresql",
      "pool_size": 5
    }
  }
}
```

## 🔧 Background Jobs (Celery)

### Starting Celery Worker

Celery needs to run as a separate process. On Railway, add a new service:

1. Create `Procfile` in your project root:
```
web: gunicorn api:app
worker: celery -A celery_config.celery_app worker --loglevel=info
beat: celery -A celery_config.celery_app beat --loglevel=info
```

2. In Railway, you can run multiple processes by:
   - Deploying the same repo to multiple services
   - Set start command for each:
     - Web service: `gunicorn api:app`
     - Worker service: `celery -A celery_config.celery_app worker --loglevel=info`
     - Beat service: `celery -A celery_config.celery_app beat --loglevel=info`

### Available Background Tasks

The following Celery tasks are configured:

#### Periodic Tasks (Celery Beat)
- **`cleanup-old-sessions`** - Runs daily at 2 AM, removes sessions older than 30 days
- **`database-maintenance`** - Runs weekly (Sunday 3 AM), performs VACUUM/ANALYZE
- **`daily-analytics`** - Runs daily at 6 AM, generates analytics reports
- **`health-check`** - Runs every 5 minutes, monitors system health

#### On-Demand Tasks
- **`send_email`** - Async email sending with retry
- **`process_export`** - Background data export processing
- **`ai_background_task`** - AI processing for batch operations

### Using Background Tasks

```python
# In your api.py endpoints
from celery_tasks import send_email, process_export

@app.route('/api/export', methods=['POST'])
def trigger_export():
    # Queue background task
    task = process_export.delay(
        user_id=current_user,
        export_type='fhir',
        format='json'
    )

    return jsonify({
        'task_id': task.id,
        'status': 'processing'
    })
```

## 🛡️ Rate Limiting

Rate limiting is automatically applied to all endpoints. Current limits:

| Endpoint Type | Rate Limit |
|--------------|------------|
| Authentication | 5 per minute |
| Registration | 3 per hour |
| AI Chat | 30 per minute |
| Data Writes | 60 per minute |
| Data Reads | 120 per minute |
| File Uploads | 10 per hour |

### Applying Custom Rate Limits

```python
from rate_limiting import get_rate_limit

@app.route('/api/chat', methods=['POST'])
@limiter.limit(get_rate_limit('ai_chat'))
def chat_endpoint():
    # Your code here
    pass
```

### Rate Limit Headers

Responses include these headers:
- `X-RateLimit-Limit` - Request limit
- `X-RateLimit-Remaining` - Remaining requests
- `X-RateLimit-Reset` - Reset timestamp

## 📈 Observability

### Structured Logging

All logs are output in JSON format for easy parsing:

```json
{
  "timestamp": "2026-01-31T16:00:00.000Z",
  "level": "INFO",
  "service": "therapy-chatbot",
  "environment": "production",
  "message": "Request completed",
  "trace_id": "abc123...",
  "span_id": "def456...",
  "user_id": "user123",
  "duration_ms": 45
}
```

### Metrics Collection

Prometheus metrics are collected automatically:
- HTTP request duration
- Request count by endpoint
- Error rates
- Database connection pool stats
- Custom application metrics

Access metrics at: `https://your-app.railway.app/metrics`

### Distributed Tracing

OpenTelemetry automatically traces:
- HTTP requests
- Database queries
- Redis operations
- Celery tasks

Each request gets a unique `trace_id` for end-to-end tracking.

## 🗄️ Database Migration

### Migrating from SQLite to PostgreSQL

The application automatically uses PostgreSQL when `DATABASE_URL` is set. To migrate existing data:

1. Export data from SQLite:
```bash
python scripts/export_sqlite_data.py
```

2. Import to PostgreSQL:
```bash
python scripts/import_to_postgres.py
```

(Note: These scripts need to be created based on your schema)

### Connection Pooling

PostgreSQL uses connection pooling (2-20 connections):
- Improves performance under load
- Handles concurrent requests efficiently
- Automatic connection recycling

SQLite (dev mode) uses direct connections with WAL mode enabled.

## 🔍 Health Monitoring

### Monitoring System Health

```bash
# Check health endpoint
curl https://your-app.railway.app/health

# Check metrics
curl https://your-app.railway.app/metrics
```

### Setting Up Alerts

Configure Railway notifications or external monitoring:
- **Uptime Robot** - Monitor `/health` endpoint
- **Prometheus + Grafana** - Scrape `/metrics` endpoint
- **Sentry** - Error tracking (add to requirements.txt)

## 🐛 Troubleshooting

### Common Issues

**1. "No module named 'psycopg2'"**
- Fixed! Added `psycopg2-binary` to requirements.txt

**2. Rate limiting not working**
- Ensure `REDIS_URL` is set
- Check Redis connection in logs

**3. Database connection errors**
- Verify `DATABASE_URL` is correct
- Check PostgreSQL is provisioned
- Review connection pool logs

**4. Celery tasks not running**
- Ensure worker process is running
- Check Redis connection
- Verify `REDIS_URL` environment variable

### Debug Mode

To enable debug mode (NOT for production):
```bash
DEBUG=true
```

## 🎯 Next Steps

1. ✅ Fixed deployment error (added psycopg2)
2. ✅ Added database connection pooling
3. ✅ Configured rate limiting
4. ✅ Set up monitoring and observability
5. ✅ Configured background job processing
6. ⏳ Integrate components into api.py
7. ⏳ Test deployment on Railway
8. ⏳ Set up Celery worker processes
9. ⏳ Configure log aggregation (optional)
10. ⏳ Set up uptime monitoring

## 📚 Additional Resources

- [Railway PostgreSQL Docs](https://docs.railway.app/databases/postgresql)
- [Railway Redis Docs](https://docs.railway.app/databases/redis)
- [Celery Documentation](https://docs.celeryq.dev/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [Prometheus Flask Exporter](https://github.com/rycus86/prometheus_flask_exporter)

---

**Need Help?** Check the logs in Railway dashboard for detailed error messages.
