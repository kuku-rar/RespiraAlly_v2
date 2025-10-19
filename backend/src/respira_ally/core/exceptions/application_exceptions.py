"""
Application Layer Exceptions
Use case and application service errors
"""
from typing import Any


class ApplicationException(Exception):
    """Base exception for all application layer errors"""

    def __init__(self, message: str = "An application error occurred"):
        self.message = message
        super().__init__(self.message)


class ValidationError(ApplicationException):
    """Raised when input validation fails"""

    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.value = value
        error_msg = f"Validation error for field '{field}': {message}"
        if value is not None:
            error_msg += f" (received: {value})"
        super().__init__(error_msg)


class ResourceNotFoundError(ApplicationException):
    """Raised when a requested resource is not found"""

    def __init__(self, resource_type: str, resource_id: str | int | None = None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        message = f"{resource_type} not found"
        if resource_id:
            message += f" (id: {resource_id})"
        super().__init__(message)


class UnauthorizedError(ApplicationException):
    """Raised when authentication fails or is missing"""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message)


class ForbiddenError(ApplicationException):
    """Raised when the user lacks permission for the requested operation"""

    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message)


class ConflictError(ApplicationException):
    """Raised when a resource conflict occurs (e.g., duplicate email)"""

    def __init__(self, resource_type: str, conflict_field: str, value: Any):
        self.resource_type = resource_type
        self.conflict_field = conflict_field
        self.value = value
        message = f"{resource_type} conflict: {conflict_field} '{value}' already exists"
        super().__init__(message)


class ExternalServiceError(ApplicationException):
    """Raised when an external service (LINE, OpenAI, etc.) fails"""

    def __init__(self, service_name: str, reason: str):
        self.service_name = service_name
        self.reason = reason
        message = f"External service '{service_name}' error: {reason}"
        super().__init__(message)


class InvalidOperationError(ApplicationException):
    """Raised when an operation is invalid in the current context"""

    def __init__(self, operation: str, reason: str):
        self.operation = operation
        self.reason = reason
        message = f"Invalid operation '{operation}': {reason}"
        super().__init__(message)
