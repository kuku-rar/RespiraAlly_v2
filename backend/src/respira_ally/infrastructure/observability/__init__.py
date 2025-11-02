"""
Observability Infrastructure

Provides metrics, logging, and tracing capabilities for monitoring application health
and performance.

Components:
- Prometheus Metrics: HTTP request metrics, error rates, latency
- Structured Logging: JSON-formatted logs with correlation IDs
- Correlation ID Middleware: Request tracing across services
"""

from .correlation_id_middleware import CorrelationIDMiddleware
from .logging_config import (
    bind_context,
    clear_context,
    configure_structlog,
    get_logger,
)
from .prometheus_metrics import PrometheusMetricsMiddleware, metrics_endpoint

__all__ = [
    # Metrics
    "PrometheusMetricsMiddleware",
    "metrics_endpoint",
    # Logging
    "configure_structlog",
    "get_logger",
    "bind_context",
    "clear_context",
    # Middleware
    "CorrelationIDMiddleware",
]
