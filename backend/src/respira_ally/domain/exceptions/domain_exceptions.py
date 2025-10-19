"""
Domain Layer Exceptions
Pure business logic errors that occur in the Domain layer
"""


class DomainException(Exception):
    """Base exception for all domain layer errors"""

    def __init__(self, message: str = "A domain error occurred"):
        self.message = message
        super().__init__(self.message)


class EntityNotFoundError(DomainException):
    """Raised when a required entity is not found"""

    def __init__(self, entity_name: str, entity_id: str | int):
        self.entity_name = entity_name
        self.entity_id = entity_id
        message = f"{entity_name} with id '{entity_id}' not found"
        super().__init__(message)


class EntityAlreadyExistsError(DomainException):
    """Raised when attempting to create an entity that already exists"""

    def __init__(self, entity_name: str, identifier: str):
        self.entity_name = entity_name
        self.identifier = identifier
        message = f"{entity_name} with identifier '{identifier}' already exists"
        super().__init__(message)


class InvalidEntityStateError(DomainException):
    """Raised when an entity is in an invalid state for the requested operation"""

    def __init__(self, entity_name: str, reason: str):
        self.entity_name = entity_name
        self.reason = reason
        message = f"Invalid state for {entity_name}: {reason}"
        super().__init__(message)


class BusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated"""

    def __init__(self, rule_name: str, details: str = ""):
        self.rule_name = rule_name
        self.details = details
        message = f"Business rule violation: {rule_name}"
        if details:
            message += f" - {details}"
        super().__init__(message)


class AggregateInvariantViolationError(DomainException):
    """Raised when an aggregate invariant is violated"""

    def __init__(self, aggregate_name: str, invariant: str):
        self.aggregate_name = aggregate_name
        self.invariant = invariant
        message = f"Invariant violation in {aggregate_name}: {invariant}"
        super().__init__(message)
