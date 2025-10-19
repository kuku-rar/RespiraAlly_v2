"""
Domain Exceptions Module
Exports all domain layer exception classes
"""
from respira_ally.domain.exceptions.domain_exceptions import (
    AggregateInvariantViolationError,
    BusinessRuleViolationError,
    DomainException,
    EntityAlreadyExistsError,
    EntityNotFoundError,
    InvalidEntityStateError,
)

__all__ = [
    "DomainException",
    "EntityNotFoundError",
    "EntityAlreadyExistsError",
    "InvalidEntityStateError",
    "BusinessRuleViolationError",
    "AggregateInvariantViolationError",
]
