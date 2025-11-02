"""
RespiraAlly V2.0 - FastAPI Application Entry Point

Modular Monolith Architecture with Clean Architecture principles
Based on 7 Bounded Contexts (DDD Strategic Design)
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from respira_ally.api.v1.routers import (
    alert,
    auth,
    daily_log,
    exacerbation,
    line_webhook,
    notification,
    patient,
    rag,
    risk,
    survey,
    task,
)
from respira_ally.core.config import settings
from respira_ally.core.exceptions.application_exceptions import (
    ApplicationException,
    ConflictError,
    ExternalServiceError,
    ForbiddenError,
    InvalidOperationError,
    ResourceNotFoundError,
    UnauthorizedError,
    ValidationError,
)
from respira_ally.core.exceptions.http_exceptions import (
    aggregate_invariant_violation_handler,
    application_exception_handler,
    business_rule_violation_handler,
    conflict_error_handler,
    domain_exception_handler,
    entity_already_exists_handler,
    entity_not_found_handler,
    external_service_error_handler,
    forbidden_error_handler,
    generic_exception_handler,
    invalid_entity_state_handler,
    invalid_operation_error_handler,
    request_validation_error_handler,
    resource_not_found_handler,
    unauthorized_error_handler,
    validation_error_handler,
)
from respira_ally.domain.exceptions.domain_exceptions import (
    AggregateInvariantViolationError,
    BusinessRuleViolationError,
    DomainException,
    EntityAlreadyExistsError,
    EntityNotFoundError,
    InvalidEntityStateError,
)
from respira_ally.infrastructure.database.session import engine
from respira_ally.infrastructure.observability import (
    CorrelationIDMiddleware,
    PrometheusMetricsMiddleware,
    configure_structlog,
    get_logger,
    metrics_endpoint,
)

# Configure structured logging (Observability Phase 2)
configure_structlog()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events"""
    # Startup
    logger.info(
        "application_starting",
        version="2.0.0",
        environment=settings.ENVIRONMENT,
        database=settings.DATABASE_URL.split("@")[1] if "@" in settings.DATABASE_URL else "N/A",
    )

    yield

    # Shutdown
    logger.info("application_shutting_down")
    await engine.dispose()
    logger.info("database_connections_disposed")


app = FastAPI(
    title="RespiraAlly V2.0 API",
    description="COPD Patient Healthcare Platform - Modular Monolith with Clean Architecture",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Observability Middleware (Phase 1 & 2)
# Note: Order matters! Correlation ID should be outermost to track entire request
app.add_middleware(CorrelationIDMiddleware)  # Phase 2: Request tracing
app.add_middleware(PrometheusMetricsMiddleware)  # Phase 1: Metrics collection


# ============================================================================
# Global Exception Handlers
# ============================================================================
# Register exception handlers in order of specificity (most specific first)

# Application Layer Exceptions
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(ResourceNotFoundError, resource_not_found_handler)
app.add_exception_handler(UnauthorizedError, unauthorized_error_handler)
app.add_exception_handler(ForbiddenError, forbidden_error_handler)
app.add_exception_handler(ConflictError, conflict_error_handler)
app.add_exception_handler(ExternalServiceError, external_service_error_handler)
app.add_exception_handler(InvalidOperationError, invalid_operation_error_handler)
app.add_exception_handler(ApplicationException, application_exception_handler)

# Domain Layer Exceptions
app.add_exception_handler(EntityNotFoundError, entity_not_found_handler)
app.add_exception_handler(EntityAlreadyExistsError, entity_already_exists_handler)
app.add_exception_handler(InvalidEntityStateError, invalid_entity_state_handler)
app.add_exception_handler(BusinessRuleViolationError, business_rule_violation_handler)
app.add_exception_handler(AggregateInvariantViolationError, aggregate_invariant_violation_handler)
app.add_exception_handler(DomainException, domain_exception_handler)

# FastAPI Built-in Exceptions
app.add_exception_handler(RequestValidationError, request_validation_error_handler)

# Catch-all for unhandled exceptions
app.add_exception_handler(Exception, generic_exception_handler)


# Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> JSONResponse:
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "version": "2.0.0",
            "environment": settings.ENVIRONMENT,
        }
    )


# Prometheus Metrics Endpoint (Observability Phase 1)
@app.get("/metrics", tags=["Observability"])
async def get_metrics():
    """
    Prometheus metrics endpoint.

    Returns application metrics in Prometheus exposition format:
    - http_request_duration_seconds: Request latency histogram
    - http_requests_total: Total request counter
    - http_errors_total: Error counter (4xx, 5xx)
    - http_requests_in_progress: Active requests gauge
    """
    return await metrics_endpoint()


# Include API Routers (7 Bounded Contexts + Sprint 4: Exacerbation + Alert + Sprint 5: Task + Sprint 6: LINE)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(patient.router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(daily_log.router, prefix="/api/v1/daily-logs", tags=["Daily Logs"])
app.include_router(survey.router, prefix="/api/v1/surveys", tags=["Surveys"])
app.include_router(risk.router, prefix="/api/v1/risk", tags=["Risk"])
app.include_router(rag.router, prefix="/api/v1/rag", tags=["RAG"])
app.include_router(notification.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(exacerbation.router, prefix="/api/v1/exacerbations", tags=["Exacerbations"])
app.include_router(alert.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(task.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(line_webhook.router, prefix="/api/v1", tags=["LINE"])


if __name__ == "__main__":
    import uvicorn

    # Security: Bind to 0.0.0.0 only in production (container environment)
    # Development: Bind to 127.0.0.1 (localhost only) for security
    host = "0.0.0.0" if settings.ENVIRONMENT == "production" else "127.0.0.1"

    uvicorn.run(
        "respira_ally.main:app",
        host=host,
        port=8000,
        reload=True,
        log_level="info",
    )
