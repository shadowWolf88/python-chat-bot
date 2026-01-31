"""
Monitoring and observability setup with OpenTelemetry and Prometheus.
Provides metrics, distributed tracing, and structured logging.
"""
import os
import logging
import json
from datetime import datetime
from pythonjsonlogger import jsonlogger

# OpenTelemetry imports
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from prometheus_flask_exporter import PrometheusMetrics

# Service information
SERVICE_NAME = os.environ.get('SERVICE_NAME', 'therapy-chatbot')
SERVICE_VERSION = os.environ.get('SERVICE_VERSION', '1.0.0')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')


def setup_structured_logging():
    """Configure structured JSON logging for better log aggregation."""

    class CustomJsonFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record, record, message_dict):
            super().add_fields(log_record, record, message_dict)
            log_record['timestamp'] = datetime.utcnow().isoformat()
            log_record['service'] = SERVICE_NAME
            log_record['environment'] = ENVIRONMENT
            log_record['level'] = record.levelname

            # Add trace context if available
            span = trace.get_current_span()
            if span:
                ctx = span.get_span_context()
                if ctx.is_valid:
                    log_record['trace_id'] = format(ctx.trace_id, '032x')
                    log_record['span_id'] = format(ctx.span_id, '016x')

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Add JSON handler
    handler = logging.StreamHandler()
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    print(f"✓ Structured JSON logging configured for {SERVICE_NAME}")
    return logger


def setup_tracing():
    """Configure OpenTelemetry distributed tracing."""

    # Set up tracer provider
    tracer_provider = TracerProvider()
    trace.set_tracer_provider(tracer_provider)

    # Note: In production, you'd add exporters here
    # For example: Jaeger, Zipkin, or cloud-native solutions
    # tracer_provider.add_span_processor(
    #     BatchSpanProcessor(JaegerExporter(...))
    # )

    print(f"✓ OpenTelemetry tracing configured for {SERVICE_NAME}")
    return trace.get_tracer(__name__)


def setup_metrics():
    """Configure Prometheus metrics collection."""

    # Set up Prometheus metric reader
    reader = PrometheusMetricReader()
    meter_provider = MeterProvider(metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)

    print(f"✓ Prometheus metrics configured for {SERVICE_NAME}")
    return metrics.get_meter(__name__)


def init_monitoring(app):
    """
    Initialize comprehensive monitoring for Flask application.

    Args:
        app: Flask application instance

    Returns:
        dict with monitoring components
    """
    # Set up structured logging
    logger = setup_structured_logging()

    # Set up tracing
    tracer = setup_tracing()

    # Set up metrics
    meter = setup_metrics()

    # Instrument Flask application
    FlaskInstrumentor().instrument_app(app)

    # Instrument database connections
    try:
        Psycopg2Instrumentor().instrument()
        logger.info("PostgreSQL instrumentation enabled")
    except Exception as e:
        logger.warning(f"Could not instrument PostgreSQL: {e}")

    # Instrument Redis
    try:
        RedisInstrumentor().instrument()
        logger.info("Redis instrumentation enabled")
    except Exception as e:
        logger.warning(f"Could not instrument Redis: {e}")

    # Add Prometheus metrics exporter
    prometheus_metrics = PrometheusMetrics(app)

    # Add custom metrics
    prometheus_metrics.info('app_info', 'Application info',
                           version=SERVICE_VERSION,
                           environment=ENVIRONMENT)

    # Add health check endpoint with metrics
    @app.route('/metrics')
    def metrics_endpoint():
        """Prometheus metrics endpoint"""
        return prometheus_metrics.export()

    @app.route('/health')
    def health_check():
        """Health check endpoint with database connectivity check"""
        from database import health_check as db_health

        db_status = db_health()

        health_status = {
            "status": "healthy" if db_status["status"] == "healthy" else "unhealthy",
            "service": SERVICE_NAME,
            "version": SERVICE_VERSION,
            "environment": ENVIRONMENT,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "database": db_status
            }
        }

        status_code = 200 if health_status["status"] == "healthy" else 503
        return health_status, status_code

    logger.info(f"Monitoring initialized for {SERVICE_NAME} v{SERVICE_VERSION} ({ENVIRONMENT})")

    return {
        "logger": logger,
        "tracer": tracer,
        "meter": meter,
        "prometheus": prometheus_metrics
    }


# Custom metric helpers
def track_ai_request(model: str, tokens: int, duration_ms: float):
    """Track AI/LLM request metrics."""
    logger = logging.getLogger(__name__)
    logger.info(
        "AI request completed",
        extra={
            "model": model,
            "tokens": tokens,
            "duration_ms": duration_ms,
            "event_type": "ai_request"
        }
    )


def track_error(error_type: str, endpoint: str, details: str = None):
    """Track application errors."""
    logger = logging.getLogger(__name__)
    logger.error(
        f"Application error: {error_type}",
        extra={
            "error_type": error_type,
            "endpoint": endpoint,
            "details": details,
            "event_type": "error"
        }
    )


def track_user_action(action: str, user_id: str = None, metadata: dict = None):
    """Track user actions for analytics."""
    logger = logging.getLogger(__name__)
    logger.info(
        f"User action: {action}",
        extra={
            "action": action,
            "user_id": user_id,
            "metadata": metadata or {},
            "event_type": "user_action"
        }
    )
