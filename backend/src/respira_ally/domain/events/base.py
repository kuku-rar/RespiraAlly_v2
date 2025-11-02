"""
Base Domain Event Definition

Provides a simple base class/protocol for domain events.
Can be used with both dataclass and Pydantic BaseModel implementations.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class DomainEvent(Protocol):
    """
    Base protocol for all domain events
    
    This allows both dataclass and Pydantic implementations
    to be used interchangeably as domain events.
    
    Linus "Good Taste": Simple interface, no complex inheritance.
    """
    pass
