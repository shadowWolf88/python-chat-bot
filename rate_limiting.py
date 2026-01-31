"""
Rate limiting configuration for API endpoints.
Uses Redis for distributed rate limiting in production.
"""
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis

# Redis configuration for rate limiting
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

# Initialize rate limiter
def init_rate_limiter(app):
    """
    Initialize Flask-Limiter with Redis backend.

    Args:
        app: Flask application instance

    Returns:
        Limiter instance
    """
    # Try to use Redis if available, fall back to memory storage
    try:
        redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
        redis_client.ping()  # Test connection
        storage_uri = REDIS_URL
        print(f"✓ Rate limiting using Redis: {REDIS_URL}")
    except Exception as e:
        print(f"⚠ Redis not available for rate limiting: {e}")
        print("  Using in-memory storage (not suitable for production)")
        storage_uri = "memory://"

    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=storage_uri,
        default_limits=["200 per day", "50 per hour"],
        # Custom headers
        headers_enabled=True,
        # Strategy for handling rate limit exceeded
        strategy="fixed-window",
        # Custom error message
        default_limits_exempt_when=lambda: False,
    )

    return limiter


# Rate limit configurations for different endpoint types
RATE_LIMITS = {
    # Authentication endpoints - strict limits
    "auth_login": "5 per minute",
    "auth_register": "3 per hour",
    "auth_password_reset": "3 per hour",

    # AI/Chat endpoints - moderate limits
    "ai_chat": "30 per minute",
    "ai_therapy": "20 per minute",

    # Data modification - moderate limits
    "data_write": "60 per minute",
    "data_delete": "30 per minute",

    # Read operations - higher limits
    "data_read": "120 per minute",

    # File uploads - strict limits
    "file_upload": "10 per hour",

    # Export operations - moderate limits
    "export": "20 per hour",

    # Health/status checks - very high limits
    "health": "300 per minute",
}


def get_rate_limit(endpoint_type: str) -> str:
    """
    Get rate limit configuration for an endpoint type.

    Args:
        endpoint_type: Type of endpoint (e.g., 'auth_login', 'ai_chat')

    Returns:
        Rate limit string (e.g., "5 per minute")
    """
    return RATE_LIMITS.get(endpoint_type, "60 per hour")
