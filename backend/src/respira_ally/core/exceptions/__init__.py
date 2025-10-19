"""
Core Exceptions Module
Exports all exception classes and handlers
"""
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
    create_error_response,
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

__all__ = [
    # Application Exceptions
    "ApplicationException",
    "ValidationError",
    "ResourceNotFoundError",
    "UnauthorizedError",
    "ForbiddenError",
    "ConflictError",
    "ExternalServiceError",
    "InvalidOperationError",
    # Exception Handlers
    "validation_error_handler",
    "resource_not_found_handler",
    "unauthorized_error_handler",
    "forbidden_error_handler",
    "conflict_error_handler",
    "external_service_error_handler",
    "invalid_operation_error_handler",
    "application_exception_handler",
    "entity_not_found_handler",
    "entity_already_exists_handler",
    "invalid_entity_state_handler",
    "business_rule_violation_handler",
    "aggregate_invariant_violation_handler",
    "domain_exception_handler",
    "request_validation_error_handler",
    "generic_exception_handler",
    # Utilities
    "create_error_response",
]
