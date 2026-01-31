"""
Celery background tasks for async processing.
"""
import logging
from datetime import datetime, timedelta
from celery_config import celery_app
from database import get_db_connection, get_db_type
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def send_email(self, to_email: str, subject: str, body: str, html: bool = False):
    """
    Send email asynchronously.

    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body
        html: Whether body is HTML
    """
    try:
        import os
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        smtp_user = os.environ.get('SMTP_USER')
        smtp_password = os.environ.get('SMTP_PASSWORD')

        if not smtp_user or not smtp_password:
            logger.error("SMTP credentials not configured")
            return False

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = to_email

        if html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_app.task
def cleanup_old_sessions():
    """Clean up expired sessions and old data."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Delete sessions older than 30 days
            cutoff_date = (datetime.now() - timedelta(days=30)).timestamp()

            if get_db_type() == "postgresql":
                cursor.execute(
                    "DELETE FROM sessions WHERE last_activity < %s",
                    (cutoff_date,)
                )
            else:
                cursor.execute(
                    "DELETE FROM sessions WHERE last_activity < ?",
                    (cutoff_date,)
                )

            deleted_count = cursor.rowcount
            logger.info(f"Cleaned up {deleted_count} old sessions")
            return {"deleted_sessions": deleted_count}

    except Exception as e:
        logger.error(f"Failed to cleanup sessions: {e}")
        return {"error": str(e)}


@celery_app.task
def database_maintenance():
    """Perform database maintenance tasks."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            if get_db_type() == "postgresql":
                # Run VACUUM ANALYZE for PostgreSQL
                conn.set_isolation_level(0)  # Required for VACUUM
                cursor.execute("VACUUM ANALYZE;")
                logger.info("PostgreSQL VACUUM ANALYZE completed")
            else:
                # SQLite optimization
                cursor.execute("VACUUM;")
                cursor.execute("ANALYZE;")
                logger.info("SQLite VACUUM and ANALYZE completed")

            return {"status": "success"}

    except Exception as e:
        logger.error(f"Database maintenance failed: {e}")
        return {"error": str(e)}


@celery_app.task
def generate_daily_analytics():
    """Generate daily analytics report."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Get yesterday's date
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

            # Count daily active users, messages, etc.
            # This is a placeholder - customize based on your schema
            analytics = {
                "date": yesterday,
                "generated_at": datetime.now().isoformat(),
            }

            logger.info(f"Daily analytics generated for {yesterday}")
            return analytics

    except Exception as e:
        logger.error(f"Failed to generate analytics: {e}")
        return {"error": str(e)}


@celery_app.task
def system_health_check():
    """Periodic system health check."""
    try:
        from database import health_check

        db_health = health_check()

        health_status = {
            "timestamp": datetime.now().isoformat(),
            "database": db_health,
        }

        if db_health["status"] != "healthy":
            logger.error(f"Health check failed: {health_status}")
        else:
            logger.info("System health check passed")

        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"error": str(e)}


@celery_app.task(bind=True, max_retries=3)
def process_export(self, user_id: str, export_type: str, format: str = 'json'):
    """
    Process data export in background.

    Args:
        user_id: User requesting export
        export_type: Type of data to export
        format: Export format (json, csv, pdf)
    """
    try:
        logger.info(f"Processing {export_type} export for user {user_id}")

        # This is a placeholder - implement based on your export logic
        # For example, generate FHIR export, PDF reports, etc.

        result = {
            "user_id": user_id,
            "export_type": export_type,
            "format": format,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }

        # Send email notification when export is ready
        # send_email.delay(
        #     user_email,
        #     "Your export is ready",
        #     f"Your {export_type} export has been completed."
        # )

        return result

    except Exception as e:
        logger.error(f"Export processing failed: {e}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_app.task
def ai_background_task(prompt: str, user_id: str = None):
    """
    Process AI requests in background for non-interactive use cases.

    Args:
        prompt: AI prompt
        user_id: User ID for tracking
    """
    try:
        # This is a placeholder - implement your AI processing logic
        logger.info(f"Processing AI task for user {user_id}")

        # Add your Groq API or other AI processing here

        return {
            "status": "completed",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"AI background task failed: {e}")
        return {"error": str(e)}
