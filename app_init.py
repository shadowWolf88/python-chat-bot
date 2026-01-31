"""
Application initialization with production-ready components.
Integrates database pooling, rate limiting, monitoring, and background jobs.
"""
import os
import logging
from flask import Flask
from flask_cors import CORS

# Import our production components
from database import init_db_pool, close_db_pool
from rate_limiting import init_rate_limiter
from monitoring import init_monitoring


def create_app(app_instance=None):
    """
    Initialize Flask application with production-ready components.

    Args:
        app_instance: Existing Flask app instance (optional)

    Returns:
        Configured Flask app
    """
    if app_instance is None:
        app = Flask(__name__, static_folder='static', template_folder='templates')
    else:
        app = app_instance

    # Configuration
    DEBUG = os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes')
    app.config['DEBUG'] = DEBUG
    app.config['ENV'] = 'production' if not DEBUG else 'development'

    # CORS configuration
    CORS(app, resources={
        r"/api/*": {
            "origins": os.environ.get('CORS_ORIGINS', '*').split(','),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["X-RateLimit-Limit", "X-RateLimit-Remaining"],
            "supports_credentials": True
        }
    })

    # Initialize database connection pool
    try:
        init_db_pool(minconn=2, maxconn=20)
        logging.info("Database connection pool initialized")
    except Exception as e:
        logging.warning(f"Database pool initialization failed: {e}")

    # Initialize rate limiting
    try:
        limiter = init_rate_limiter(app)
        app.limiter = limiter
        logging.info("Rate limiting initialized")
    except Exception as e:
        logging.error(f"Rate limiting initialization failed: {e}")
        app.limiter = None

    # Initialize monitoring and observability
    try:
        monitoring = init_monitoring(app)
        app.monitoring = monitoring
        logging.info("Monitoring and observability initialized")
    except Exception as e:
        logging.error(f"Monitoring initialization failed: {e}")
        app.monitoring = None

    # Register cleanup handler
    @app.teardown_appcontext
    def cleanup(exception=None):
        """Cleanup resources on app context teardown."""
        pass  # Connection pool handles cleanup automatically

    # Register shutdown handler
    import atexit

    @atexit.register
    def shutdown():
        """Cleanup on application shutdown."""
        close_db_pool()
        logging.info("Application shutdown complete")

    return app


def configure_production_server(app):
    """
    Additional configuration for production deployment.

    Args:
        app: Flask application instance
    """
    # Security headers
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        # Don't send server version
        response.headers.pop('Server', None)

        return response

    # Request ID middleware
    @app.before_request
    def add_request_id():
        """Add unique request ID for tracking."""
        import uuid
        from flask import g
        g.request_id = str(uuid.uuid4())

    logging.info("Production server configuration applied")
