"""
HTTP Exception Handlers
FastAPI global exception handlers for consistent error responses
"""

from datetime import UTC, datetime
from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

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
from respira_ally.domain.exceptions.domain_exceptions import (
    AggregateInvariantViolationError,
    BusinessRuleViolationError,
    DomainException,
    EntityAlreadyExistsError,
    EntityNotFoundError,
    InvalidEntityStateError,
)


def create_error_response(
    error_type: str,
    message: str,
    status_code: int,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    """
    Create a standardized error response

    Response format:
    {
        "error": {
            "type": "ValidationError",
            "message": "Validation failed for field 'email'",
            "timestamp": "2025-10-20T03:00:00.000Z",
            "details": {...}  # Optional
        }
    }
    """
    error_content = {
        "error": {
            "type": error_type,
            "message": message,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    }

    if details:
        error_content["error"]["details"] = details

    return JSONResponse(status_code=status_code, content=error_content)


# ============================================================================
# Application Layer Exception Handlers
# ============================================================================


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle application validation errors (business logic validation)"""
    return create_error_response(
        error_type="ValidationError",
        message=exc.message,
        status_code=status.HTTP_400_BAD_REQUEST,
        details={"field": exc.field, "value": exc.value},
    )


async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError) -> JSONResponse:
    """Handle resource not found errors"""
    return create_error_response(
        error_type="ResourceNotFoundError",
        message=exc.message,
        status_code=status.HTTP_404_NOT_FOUND,
        details={"resource_type": exc.resource_type, "resource_id": exc.resource_id},
    )


async def unauthorized_error_handler(request: Request, exc: UnauthorizedError) -> JSONResponse:
    """Handle authentication errors"""
    return create_error_response(
        error_type="UnauthorizedError",
        message=exc.message,
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


async def forbidden_error_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
    """Handle authorization errors"""
    return create_error_response(
        error_type="ForbiddenError",
        message=exc.message,
        status_code=status.HTTP_403_FORBIDDEN,
    )


async def conflict_error_handler(request: Request, exc: ConflictError) -> JSONResponse:
    """Handle resource conflict errors"""
    return create_error_response(
        error_type="ConflictError",
        message=exc.message,
        status_code=status.HTTP_409_CONFLICT,
        details={
            "resource_type": exc.resource_type,
            "conflict_field": exc.conflict_field,
            "value": exc.value,
        },
    )


async def external_service_error_handler(
    request: Request, exc: ExternalServiceError
) -> JSONResponse:
    """Handle external service errors"""
    return create_error_response(
        error_type="ExternalServiceError",
        message=exc.message,
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        details={"service_name": exc.service_name, "reason": exc.reason},
    )


async def invalid_operation_error_handler(
    request: Request, exc: InvalidOperationError
) -> JSONResponse:
    """Handle invalid operation errors"""
    return create_error_response(
        error_type="InvalidOperationError",
        message=exc.message,
        status_code=status.HTTP_400_BAD_REQUEST,
        details={"operation": exc.operation, "reason": exc.reason},
    )


async def application_exception_handler(
    request: Request, exc: ApplicationException
) -> JSONResponse:
    """Generic handler for all application exceptions"""
    return create_error_response(
        error_type="ApplicationError",
        message=exc.message,
        status_code=status.HTTP_400_BAD_REQUEST,
    )


# ============================================================================
# Domain Layer Exception Handlers
# ============================================================================


async def entity_not_found_handler(request: Request, exc: EntityNotFoundError) -> JSONResponse:
    """Handle domain entity not found errors"""
    return create_error_response(
        error_type="EntityNotFoundError",
        message=exc.message,
        status_code=status.HTTP_404_NOT_FOUND,
        details={"entity_name": exc.entity_name, "entity_id": str(exc.entity_id)},
    )


async def entity_already_exists_handler(
    request: Request, exc: EntityAlreadyExistsError
) -> JSONResponse:
    """Handle domain entity already exists errors"""
    return create_error_response(
        error_type="EntityAlreadyExistsError",
        message=exc.message,
        status_code=status.HTTP_409_CONFLICT,
        details={"entity_name": exc.entity_name, "identifier": exc.identifier},
    )


async def invalid_entity_state_handler(
    request: Request, exc: InvalidEntityStateError
) -> JSONResponse:
    """Handle invalid entity state errors"""
    return create_error_response(
        error_type="InvalidEntityStateError",
        message=exc.message,
        status_code=status.HTTP_400_BAD_REQUEST,
        details={"entity_name": exc.entity_name, "reason": exc.reason},
    )


async def business_rule_violation_handler(
    request: Request, exc: BusinessRuleViolationError
) -> JSONResponse:
    """Handle business rule violation errors"""
    return create_error_response(
        error_type="BusinessRuleViolationError",
        message=exc.message,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={"rule_name": exc.rule_name, "details": exc.details},
    )


async def aggregate_invariant_violation_handler(
    request: Request, exc: AggregateInvariantViolationError
) -> JSONResponse:
    """Handle aggregate invariant violation errors"""
    return create_error_response(
        error_type="AggregateInvariantViolationError",
        message=exc.message,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={"aggregate_name": exc.aggregate_name, "invariant": exc.invariant},
    )


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """Generic handler for all domain exceptions"""
    return create_error_response(
        error_type="DomainError",
        message=exc.message,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


# ============================================================================
# FastAPI Built-in Exception Handlers
# ============================================================================


async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle FastAPI/Pydantic request validation errors
    This is for HTTP layer validation (e.g., invalid JSON, missing required fields)
    """
    errors = exc.errors()
    formatted_errors = []

    for error in errors:
        formatted_errors.append(
            {
                "field": " -> ".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    return create_error_response(
        error_type="RequestValidationError",
        message="Request validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={"errors": formatted_errors},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all handler for unhandled exceptions
    In production, this should log the error and return a generic message
    """
    # TODO: Add structured logging here
    print(f"[ERROR] Unhandled exception: {exc.__class__.__name__}: {str(exc)}")

    # In production, don't expose internal error details
    return create_error_response(
        error_type="InternalServerError",
        message="An unexpected error occurred. Please try again later.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
