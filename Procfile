# Procfile for Railway deployment
# Railway runs the 'web' process by default
# For worker/beat, create separate services in Railway with custom start commands

# Web server - serves HTTP requests
web: python -m gunicorn api:app --workers 4 --threads 2 --timeout 120 --bind 0.0.0.0:$PORT

# Celery worker - add as separate Railway service with custom start command:
# celery -A celery_config.celery_app worker --loglevel=info --concurrency=4

# Celery beat - add as separate Railway service with custom start command:
# celery -A celery_config.celery_app beat --loglevel=info
