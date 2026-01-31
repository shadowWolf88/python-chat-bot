"""
Celery configuration for background job processing.
Handles async tasks like email sending, data processing, and scheduled jobs.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Redis URL for Celery broker and result backend
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

# Initialize Celery
celery_app = Celery(
    'therapy_chatbot',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['celery_tasks']  # Import task modules
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,

    # Task result settings
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        'master_name': 'mymaster',
        'visibility_timeout': 3600,
    },

    # Task execution settings
    task_acks_late=True,  # Acknowledge task after completion
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,  # One task at a time
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks

    # Retry settings
    task_default_retry_delay=60,  # Retry after 60 seconds
    task_max_retries=3,

    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,

    # Beat schedule for periodic tasks
    beat_schedule={
        # Cleanup old sessions every night at 2 AM
        'cleanup-old-sessions': {
            'task': 'celery_tasks.cleanup_old_sessions',
            'schedule': crontab(hour=2, minute=0),
        },
        # Database maintenance every Sunday at 3 AM
        'database-maintenance': {
            'task': 'celery_tasks.database_maintenance',
            'schedule': crontab(hour=3, minute=0, day_of_week=0),
        },
        # Generate daily analytics report at 6 AM
        'daily-analytics': {
            'task': 'celery_tasks.generate_daily_analytics',
            'schedule': crontab(hour=6, minute=0),
        },
        # Check system health every 5 minutes
        'health-check': {
            'task': 'celery_tasks.system_health_check',
            'schedule': 300.0,  # Every 5 minutes
        },
    },
)

# Task routes (optional - for task-specific queues)
celery_app.conf.task_routes = {
    'celery_tasks.send_email': {'queue': 'email'},
    'celery_tasks.process_export': {'queue': 'exports'},
    'celery_tasks.ai_background_task': {'queue': 'ai'},
}

print(f"✓ Celery configured with broker: {REDIS_URL}")
