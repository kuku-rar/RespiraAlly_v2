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
    auth,
    daily_log,
    notification,
    patient,
    rag,
    risk,
    survey,
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


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events"""
    # Startup
    print("🚀 Starting RespiraAlly V2.0...")
    print(f"📋 Environment: {settings.ENVIRONMENT}")
    print(
        f"🗄️  Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'N/A'}"
    )

    yield

    # Shutdown
    print("🛑 Shutting down RespiraAlly V2.0...")
    await engine.dispose()


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


# Include API Routers (7 Bounded Contexts)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(patient.router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(daily_log.router, prefix="/api/v1/daily-logs", tags=["Daily Logs"])
app.include_router(survey.router, prefix="/api/v1/surveys", tags=["Surveys"])
app.include_router(risk.router, prefix="/api/v1/risk", tags=["Risk"])
app.include_router(rag.router, prefix="/api/v1/rag", tags=["RAG"])
app.include_router(notification.router, prefix="/api/v1/notifications", tags=["Notifications"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "respira_ally.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
