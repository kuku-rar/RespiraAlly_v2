"""
Prometheus Metrics Middleware

Provides HTTP metrics collection for FastAPI applications:
- Request duration (histogram)
- Request count (counter)
- Error count (counter by status code)
- Active requests (gauge)
- Database query metrics
"""

import time
from typing import Callable

from fastapi import Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse


# ============================================================================
# Metric Definitions
# ============================================================================

# HTTP Request Duration (latency) - histogram with buckets for different response times
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint", "status_code"],
    buckets=(
        0.005,
        0.01,
        0.025,
        0.05,
        0.075,
        0.1,
        0.25,
        0.5,
        0.75,
        1.0,
        2.5,
        5.0,
        7.5,
        10.0,
    ),  # Buckets: 5ms to 10s
)

# HTTP Request Count - counter for total requests
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

# HTTP Errors - counter for HTTP errors (4xx, 5xx)
http_errors_total = Counter(
    "http_errors_total",
    "Total HTTP errors",
    ["method", "endpoint", "status_code", "error_type"],
)

# Active Requests - gauge for current active requests
http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "HTTP requests currently being processed",
    ["method", "endpoint"],
)

# Database Connection Pool - gauge for connection pool status
db_connection_pool_size = Gauge(
    "db_connection_pool_size",
    "Database connection pool size",
    ["pool_name"],
)

db_connection_pool_in_use = Gauge(
    "db_connection_pool_in_use",
    "Database connections currently in use",
    ["pool_name"],
)


# ============================================================================
# Prometheus Metrics Middleware
# ============================================================================


class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware to collect HTTP metrics for Prometheus.

    Metrics collected:
    - http_request_duration_seconds: Request latency histogram
    - http_requests_total: Total request counter
    - http_errors_total: Error counter (4xx, 5xx)
    - http_requests_in_progress: Active requests gauge

    Linus "Good Taste" Principles Applied:
    1. Eliminates special cases - treats all endpoints uniformly
    2. Single source of truth - all HTTP metrics in one place
    3. No nested if-else - clean path-based logic
    4. Minimal complexity - tracks what matters, nothing more
    """

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process HTTP request and collect metrics"""

        # Extract request metadata
        method = request.method
        endpoint = self._get_endpoint(request)

        # Skip metrics endpoint to avoid recursion
        if endpoint == "/metrics":
            return await call_next(request)

        # Track active requests
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()

        # Measure request duration
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)
            status_code = response.status_code

            # Record duration
            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=method, endpoint=endpoint, status_code=status_code
            ).observe(duration)

            # Count request
            http_requests_total.labels(
                method=method, endpoint=endpoint, status_code=status_code
            ).inc()

            # Count errors (4xx, 5xx)
            if status_code >= 400:
                error_type = self._get_error_type(status_code)
                http_errors_total.labels(
                    method=method, endpoint=endpoint, status_code=status_code, error_type=error_type
                ).inc()

            return response

        except Exception as e:
            # Handle exceptions and record as 500 errors
            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=method, endpoint=endpoint, status_code=500
            ).observe(duration)

            http_requests_total.labels(method=method, endpoint=endpoint, status_code=500).inc()

            http_errors_total.labels(
                method=method, endpoint=endpoint, status_code=500, error_type="server_error"
            ).inc()

            raise  # Re-raise exception for proper error handling

        finally:
            # Always decrement active requests
            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()

    @staticmethod
    def _get_endpoint(request: Request) -> str:
        """
        Extract endpoint path from request.

        Applies "Good Taste" - normalizes paths to avoid metric explosion
        from dynamic path parameters (e.g., /api/v1/patients/{id})
        """
        # Use matched route if available (FastAPI routes)
        if hasattr(request, "scope") and "route" in request.scope:
            route = request.scope.get("route")
            if route and hasattr(route, "path"):
                return route.path

        # Fallback to raw path
        return request.url.path

    @staticmethod
    def _get_error_type(status_code: int) -> str:
        """
        Categorize HTTP status codes into error types.

        Good Taste: Eliminates complex if-else chains with simple range checks
        """
        if 400 <= status_code < 500:
            return "client_error"
        if 500 <= status_code < 600:
            return "server_error"
        return "unknown"


# ============================================================================
# Metrics Endpoint
# ============================================================================


async def metrics_endpoint() -> StarletteResponse:
    """
    Expose Prometheus metrics endpoint.

    Returns metrics in Prometheus exposition format.
    Endpoint: GET /metrics

    Linus "Good Taste": Simple, single-purpose function.
    No special cases, no complexity. Just does its job.
    """
    metrics_data = generate_latest(REGISTRY)
    return StarletteResponse(content=metrics_data, media_type=CONTENT_TYPE_LATEST)
