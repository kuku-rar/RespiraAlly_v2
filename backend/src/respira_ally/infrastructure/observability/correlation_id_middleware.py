"""
Correlation ID Middleware for Request Tracing

Automatically assigns a unique correlation ID to each HTTP request, enabling
request tracing across all logs, metrics, and distributed services.

Benefits:
- Track a single request through all service layers
- Correlate logs from different modules
- Debug production issues by filtering on correlation_id
- Identify slow requests and error chains

Linus "Good Taste" Principles:
1. Every request gets an ID - no special cases
2. ID flows automatically through context - no manual passing
3. Works seamlessly with structured logging
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .logging_config import bind_context, clear_context, get_logger

logger = get_logger(__name__)


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to assign and propagate correlation IDs for each HTTP request.

    Flow:
    1. Request arrives → Generate or extract correlation ID
    2. Bind ID to logging context → All logs include it automatically
    3. Add ID to response headers → Client can track requests
    4. Clear context after response → No leakage to next request

    Linus "Good Taste":
    - Eliminates manual ID passing (auto-propagates via context)
    - Single middleware handles all requests uniformly
    - No special cases for different endpoints
    """

    CORRELATION_ID_HEADER = "X-Correlation-ID"

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with correlation ID.

        Good Taste: Simple, linear flow. No nested if-else chains.
        """

        # Step 1: Get or generate correlation ID
        correlation_id = self._get_or_generate_correlation_id(request)

        # Step 2: Bind to logging context (all logs will now include it)
        bind_context(
            correlation_id=correlation_id,
            method=request.method,
            path=request.url.path,
        )

        # Step 3: Log request start
        start_time = time.time()
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
        )

        try:
            # Step 4: Process request
            response = await call_next(request)

            # Step 5: Log request completion
            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            # Step 6: Add correlation ID to response headers
            response.headers[self.CORRELATION_ID_HEADER] = correlation_id

            return response

        except Exception as e:
            # Log exception with full context
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "request_failed",
                error_type=type(e).__name__,
                error_message=str(e),
                duration_ms=round(duration_ms, 2),
                exc_info=True,  # Include stack trace
            )
            raise  # Re-raise for FastAPI error handlers

        finally:
            # Step 7: Always clear context to avoid leakage
            clear_context()

    def _get_or_generate_correlation_id(self, request: Request) -> str:
        """
        Extract correlation ID from request header or generate new one.

        Supports distributed tracing:
        - If upstream service sends correlation ID, reuse it
        - Otherwise, generate new UUID

        Good Taste: Simple logic, no complex branching.
        """
        # Try to extract from header
        correlation_id = request.headers.get(self.CORRELATION_ID_HEADER)

        # Generate new UUID if not present
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        return correlation_id
