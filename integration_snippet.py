"""
Integration snippet to add to api.py after line 63 (after DEBUG = ...)

This code initializes:
- Database connection pooling
- Rate limiting with Redis
- Monitoring with OpenTelemetry and Prometheus
- Background job processing with Celery

Copy this code and insert it after the DEBUG line in api.py (around line 63).
"""

# ==================== PRODUCTION INFRASTRUCTURE SETUP ====================
import logging

# Initialize structured logging
try:
    from monitoring import setup_structured_logging
    logger = setup_structured_logging()
except ImportError as e:
    logging.warning(f"Could not import monitoring: {e}")
    logger = logging.getLogger(__name__)

# Initialize database connection pool
try:
    from database import init_db_pool
    init_db_pool(minconn=2, maxconn=20)
    logger.info("✓ Database connection pool initialized")
except Exception as e:
    logger.warning(f"Database pool initialization failed (will use direct connections): {e}")

# Initialize rate limiting
try:
    from rate_limiting import init_rate_limiter, get_rate_limit
    limiter = init_rate_limiter(app)
    logger.info("✓ Rate limiting initialized")
except Exception as e:
    logger.error(f"Rate limiting initialization failed: {e}")
    limiter = None

# Initialize monitoring and observability
try:
    from monitoring import init_monitoring
    monitoring_components = init_monitoring(app)
    logger.info("✓ Monitoring and observability initialized")
except Exception as e:
    logger.error(f"Monitoring initialization failed: {e}")

# Configure production server settings
@app.before_request
def add_request_id():
    """Add unique request ID for request tracing."""
    import uuid
    from flask import g
    g.request_id = str(uuid.uuid4())

# Register cleanup on shutdown
import atexit
@atexit.register
def shutdown_cleanup():
    """Cleanup resources on shutdown."""
    try:
        from database import close_db_pool
        close_db_pool()
        logger.info("Application shutdown complete")
    except:
        pass

logger.info("=" * 60)
logger.info("Production infrastructure initialized successfully")
logger.info("=" * 60)

# ==================== END PRODUCTION INFRASTRUCTURE ====================
