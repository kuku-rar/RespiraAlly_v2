"""
Event Publisher Interface
Infrastructure Layer - Event-Driven Architecture

Abstract interface for publishing domain events.
Implementations can use different message brokers (RabbitMQ, Kafka, etc.)
or in-memory event bus for testing.
"""
from abc import ABC, abstractmethod

from respira_ally.domain.events.daily_log_events import DomainEvent


class EventPublisher(ABC):
    """
    Abstract base class for event publishers

    Following the Dependency Inversion Principle, the infrastructure layer
    defines the interface, and concrete implementations can vary.
    """

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """
        Publish a domain event

        Args:
            event: Domain event to publish

        Raises:
            PublishError: If event publishing fails
        """
        pass

    @abstractmethod
    async def publish_batch(self, events: list[DomainEvent]) -> None:
        """
        Publish multiple domain events in a batch

        Args:
            events: List of domain events to publish

        Raises:
            PublishError: If batch publishing fails
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """
        Close the publisher and release resources

        Should be called during application shutdown.
        """
        pass


class PublishError(Exception):
    """Exception raised when event publishing fails"""

    def __init__(self, message: str, event: DomainEvent | None = None, original_error: Exception | None = None):
        self.message = message
        self.event = event
        self.original_error = original_error
        super().__init__(message)
