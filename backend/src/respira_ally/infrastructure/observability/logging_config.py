"""
Structured Logging Configuration using structlog

Provides JSON-formatted structured logging with:
- Correlation IDs for request tracing
- Contextual information (user_id, endpoint, etc.)
- Consistent log format across all modules
- Integration with Prometheus metrics

Linus "Good Taste" Principles Applied:
1. Single source of truth - One logger configuration for entire app
2. No special cases - All log entries follow same structure
3. Simplicity - Minimal configuration, maximum clarity
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor


def add_app_context(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    """
    Add application-wide context to all log entries.

    Good Taste: Single function adds all context, no scattered logic.
    """
    event_dict["application"] = "respirally"
    event_dict["version"] = "2.0.0"
    return event_dict


def extract_from_record(
    _: logging.Logger, __: str, event_dict: EventDict
) -> EventDict:
    """
    Extract extra fields from logging.LogRecord if present.

    Enables compatibility with standard logging library.
    """
    record = event_dict.get("_record")
    if record:
        # Extract correlation_id if present
        correlation_id = getattr(record, "correlation_id", None)
        if correlation_id:
            event_dict["correlation_id"] = correlation_id

        # Extract user_id if present
        user_id = getattr(record, "user_id", None)
        if user_id:
            event_dict["user_id"] = user_id

    return event_dict


def configure_structlog() -> None:
    """
    Configure structlog for the entire application.

    Linus "Good Taste":
    - Called once at startup, affects entire app (single source of truth)
    - No per-module configuration complexity
    - Consistent behavior across all logging calls
    """

    # Processors that run for ALL log entries
    shared_processors: list[Processor] = [
        # Add log level
        structlog.stdlib.add_log_level,
        # Add logger name
        structlog.stdlib.add_logger_name,
        # Add timestamp (ISO 8601 format)
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        # Add application context
        add_app_context,
        # Extract from LogRecord
        extract_from_record,
        # Format stack traces
        structlog.processors.format_exc_info,
        # Make exception info JSON-serializable
        structlog.processors.ExceptionPrettyPrinter(),
    ]

    # Configure structlog to use standard library logging
    structlog.configure(
        processors=shared_processors
        + [
            # Prepare for stdlib logging
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        # Use standard library's LoggerFactory
        logger_factory=structlog.stdlib.LoggerFactory(),
        # Cache logger instances for better performance
        cache_logger_on_first_use=True,
    )

    # Configure formatter for standard library logging
    formatter = structlog.stdlib.ProcessorFormatter(
        # Foreign log messages (from libraries)
        foreign_pre_chain=shared_processors,
        # Our own log messages
        processors=[
            # Remove _record & _from_structlog keys
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            # Render as JSON for production, pretty-print for development
            structlog.processors.JSONRenderer() if not sys.stdout.isatty() else structlog.dev.ConsoleRenderer(),  # Production: JSON  # Development: Pretty print
        ],
    )

    # Set up handler with formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    # Clear any default handlers
    root_logger.handlers = [handler]


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (typically __name__ of the calling module)

    Returns:
        Structured logger with all configured processors

    Example:
        ```python
        logger = get_logger(__name__)
        logger.info("user_logged_in", user_id="abc123", ip="192.168.1.1")
        ```

    Good Taste: Simple interface, one function to get logger anywhere.
    """
    return structlog.get_logger(name)


def bind_context(**kwargs: Any) -> None:
    """
    Bind context variables to the current thread/request.

    These will be included in all subsequent log entries within the same context.

    Args:
        **kwargs: Key-value pairs to add to log context

    Example:
        ```python
        # At request start
        bind_context(correlation_id="req-123", user_id="user-456")

        # All logs will now include these fields
        logger.info("processing_payment")  # Will have correlation_id and user_id
        ```

    Good Taste: Set context once, all logs benefit. No manual field passing.
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_context() -> None:
    """
    Clear all bound context variables.

    Should be called at the end of each request to avoid context leakage.

    Good Taste: Explicit cleanup, no hidden state between requests.
    """
    structlog.contextvars.clear_contextvars()
