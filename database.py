"""
Database connection pooling and management for production.
Supports both PostgreSQL (production) and SQLite (development).
"""
import os
import sqlite3
from contextlib import contextmanager
from typing import Optional
import logging

# Conditional imports for PostgreSQL
try:
    import psycopg2
    from psycopg2 import pool
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
USE_POSTGRES = bool(DATABASE_URL and HAS_POSTGRES)

# Connection pool for PostgreSQL
_pg_pool: Optional['pool.ThreadedConnectionPool'] = None


def init_db_pool(minconn=2, maxconn=20):
    """Initialize PostgreSQL connection pool."""
    global _pg_pool

    if not USE_POSTGRES:
        logger.info("PostgreSQL not configured, using SQLite for development")
        return

    if _pg_pool is not None:
        logger.warning("Database pool already initialized")
        return

    try:
        _pg_pool = pool.ThreadedConnectionPool(
            minconn=minconn,
            maxconn=maxconn,
            dsn=DATABASE_URL,
            cursor_factory=RealDictCursor
        )
        logger.info(f"PostgreSQL connection pool initialized (min={minconn}, max={maxconn})")
    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL pool: {e}")
        raise


def close_db_pool():
    """Close all connections in the pool."""
    global _pg_pool

    if _pg_pool is not None:
        _pg_pool.closeall()
        _pg_pool = None
        logger.info("PostgreSQL connection pool closed")


@contextmanager
def get_db_connection(db_path: Optional[str] = None):
    """
    Context manager for database connections.

    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(...)
            conn.commit()

    Args:
        db_path: Path to SQLite database (only used if PostgreSQL not configured)

    Yields:
        Database connection object
    """
    if USE_POSTGRES:
        # PostgreSQL: Get connection from pool
        if _pg_pool is None:
            init_db_pool()

        conn = _pg_pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            _pg_pool.putconn(conn)
    else:
        # SQLite: Create new connection
        if db_path is None:
            db_path = os.environ.get('DB_PATH', 'therapy_chat.db')

        conn = sqlite3.connect(db_path, timeout=30.0, check_same_thread=False)
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA busy_timeout=30000')
        conn.execute('PRAGMA synchronous=NORMAL')

        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()


def execute_query(query: str, params: tuple = (), db_path: Optional[str] = None, fetch_one=False, fetch_all=False):
    """
    Execute a database query with automatic connection handling.

    Args:
        query: SQL query to execute
        params: Query parameters
        db_path: SQLite database path (optional)
        fetch_one: Return single row
        fetch_all: Return all rows

    Returns:
        Query results or None
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)

        if fetch_one:
            return cursor.fetchone()
        elif fetch_all:
            return cursor.fetchall()

        return None


def get_db_type() -> str:
    """Get the current database type."""
    return "postgresql" if USE_POSTGRES else "sqlite"


def health_check() -> dict:
    """Check database connectivity and return status."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            if USE_POSTGRES:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                return {
                    "status": "healthy",
                    "type": "postgresql",
                    "version": version['version'] if isinstance(version, dict) else str(version),
                    "pool_size": len(_pg_pool._pool) if _pg_pool else 0
                }
            else:
                cursor.execute("SELECT sqlite_version();")
                version = cursor.fetchone()
                return {
                    "status": "healthy",
                    "type": "sqlite",
                    "version": version[0] if version else "unknown"
                }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "type": get_db_type(),
            "error": str(e)
        }
