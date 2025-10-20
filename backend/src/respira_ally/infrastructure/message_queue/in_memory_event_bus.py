"""
In-Memory Event Bus
Infrastructure Layer - Event-Driven Architecture

Simple in-memory event publisher for development and testing.
Events are logged but not persisted or sent to external message brokers.

For production, replace with RabbitMQ or Kafka implementation.
"""
import logging
from typing import Callable, Any

from respira_ally.domain.events.daily_log_events import DomainEvent
from respira_ally.infrastructure.message_queue.publishers.event_publisher import (
    EventPublisher,
    PublishError,
)

logger = logging.getLogger(__name__)


class InMemoryEventBus(EventPublisher):
    """
    In-memory event bus implementation

    **Features**:
    - Synchronous event handling within same process
    - Event handlers can be registered by event type
    - Useful for development, testing, and simple deployments
    - No external dependencies

    **Limitations**:
    - Events are not persisted
    - No retry mechanism
    - Not suitable for distributed systems
    - Events are lost if application crashes

    **Usage**:
    ```python
    event_bus = InMemoryEventBus()

    # Register handler
    async def handle_daily_log_submitted(event):
        print(f"Log submitted: {event.patient_id}")

    event_bus.subscribe("daily_log.submitted", handle_daily_log_submitted)

    # Publish event
    await event_bus.publish(event)
    ```
    """

    def __init__(self):
        """Initialize the in-memory event bus"""
        self._handlers: dict[str, list[Callable]] = {}
        self._published_events: list[DomainEvent] = []  # For testing/debugging
        logger.info("InMemoryEventBus initialized")

    def subscribe(self, event_type: str, handler: Callable[[DomainEvent], Any]) -> None:
        """
        Subscribe a handler to a specific event type

        Args:
            event_type: Event type to subscribe to (e.g., "daily_log.submitted")
            handler: Async function to handle the event
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        self._handlers[event_type].append(handler)
        logger.info(f"Subscribed handler to event type: {event_type}")

    async def publish(self, event: DomainEvent) -> None:
        """
        Publish a domain event and invoke all registered handlers

        Args:
            event: Domain event to publish

        Raises:
            PublishError: If event handling fails
        """
        try:
            # Store event for debugging
            self._published_events.append(event)

            # Log the event
            logger.info(
                f"Publishing event: {event.event_type} "
                f"(ID: {event.event_id}, Aggregate: {event.aggregate_id})"
            )

            # Get handlers for this event type
            handlers = self._handlers.get(event.event_type, [])

            if not handlers:
                logger.warning(f"No handlers registered for event type: {event.event_type}")
                return

            # Invoke all handlers
            for handler in handlers:
                try:
                    await handler(event)
                    logger.debug(f"Handler {handler.__name__} completed for {event.event_type}")
                except Exception as e:
                    # Log error but don't stop other handlers
                    logger.error(
                        f"Handler {handler.__name__} failed for {event.event_type}: {str(e)}",
                        exc_info=True
                    )
                    # In production, you might want to:
                    # - Send to dead letter queue
                    # - Trigger alert
                    # - Retry with exponential backoff

        except Exception as e:
            error_msg = f"Failed to publish event {event.event_type}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise PublishError(error_msg, event=event, original_error=e)

    async def publish_batch(self, events: list[DomainEvent]) -> None:
        """
        Publish multiple events in a batch

        Args:
            events: List of domain events to publish

        Note:
            For in-memory implementation, this just publishes events sequentially.
            Real message brokers might optimize batch publishing.
        """
        logger.info(f"Publishing batch of {len(events)} events")

        for event in events:
            await self.publish(event)

    async def close(self) -> None:
        """
        Close the event bus and release resources

        For in-memory implementation, this just clears handlers and logs.
        """
        logger.info("Closing InMemoryEventBus")
        self._handlers.clear()
        self._published_events.clear()

    # ========================================================================
    # Testing/Debugging Utilities
    # ========================================================================

    def get_published_events(self, event_type: str | None = None) -> list[DomainEvent]:
        """
        Get list of published events (for testing)

        Args:
            event_type: Optional filter by event type

        Returns:
            List of published events
        """
        if event_type:
            return [e for e in self._published_events if e.event_type == event_type]
        return self._published_events.copy()

    def clear_published_events(self) -> None:
        """Clear published events history (for testing)"""
        self._published_events.clear()

    def get_handler_count(self, event_type: str) -> int:
        """Get number of handlers registered for event type (for testing)"""
        return len(self._handlers.get(event_type, []))


# ============================================================================
# Global Instance (Singleton Pattern)
# ============================================================================

_event_bus_instance: InMemoryEventBus | None = None


def get_event_bus() -> InMemoryEventBus:
    """
    Get global event bus instance (singleton)

    Returns:
        InMemoryEventBus instance
    """
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = InMemoryEventBus()
    return _event_bus_instance


def reset_event_bus() -> None:
    """
    Reset global event bus instance (for testing)

    This allows tests to start with a clean slate.
    """
    global _event_bus_instance
    _event_bus_instance = None
