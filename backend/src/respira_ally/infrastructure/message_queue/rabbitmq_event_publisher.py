"""
RabbitMQ Event Publisher (Async)
Infrastructure Layer - Event-Driven Architecture

Production-ready async event publisher using RabbitMQ message broker with aio-pika.
Implements the EventPublisher interface with durable queues and persistent messages.
"""

import json
import logging
from typing import Any

import aio_pika
from aio_pika import DeliveryMode, ExchangeType, Message
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractQueue

from respira_ally.core.config import settings
from respira_ally.domain.events.daily_log_events import DomainEvent
from respira_ally.infrastructure.message_queue.publishers.event_publisher import (
    EventPublisher,
    PublishError,
)

logger = logging.getLogger(__name__)


class RabbitMQEventPublisher(EventPublisher):
    """
    Async RabbitMQ-based event publisher implementation

    **Features**:
    - Async/await support with aio-pika
    - Durable queues (survive broker restarts)
    - Persistent messages (survive broker crashes)
    - Automatic queue declaration
    - Connection pooling
    - JSON serialization with Pydantic support

    **Configuration**:
    Uses settings from core.config:
    - RABBITMQ_HOST
    - RABBITMQ_PORT
    - RABBITMQ_USER
    - RABBITMQ_PASSWORD

    **Usage**:
    ```python
    publisher = RabbitMQEventPublisher(queue_name="line_messages")
    await publisher.publish(event)
    await publisher.close()
    ```
    """

    def __init__(self, queue_name: str = "line_message_queue"):
        """
        Initialize RabbitMQ event publisher

        Args:
            queue_name: Queue name for events (default: line_message_queue)
        """
        self.queue_name = queue_name
        self.connection: AbstractConnection | None = None
        self.channel: AbstractChannel | None = None
        self.queue: AbstractQueue | None = None

        # Build connection URL
        self.connection_url = (
            f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@"
            f"{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
        )

        logger.info(
            f"RabbitMQEventPublisher initialized for queue: {queue_name} "
            f"(host: {settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT})"
        )

    async def _connect(self) -> None:
        """
        Establish async connection to RabbitMQ broker

        Raises:
            PublishError: If connection fails
        """
        try:
            if not self.connection or self.connection.is_closed:
                logger.debug("Establishing RabbitMQ connection...")

                # Establish connection
                self.connection = await aio_pika.connect_robust(
                    url=self.connection_url,
                    timeout=30,
                )

                # Create channel
                self.channel = await self.connection.channel()

                # Declare queue with durability
                self.queue = await self.channel.declare_queue(
                    name=self.queue_name,
                    durable=True,  # Survives broker restart
                    arguments={
                        "x-message-ttl": 86400000,  # Message TTL: 24 hours (ms)
                        "x-max-length": 100000,  # Max queue length: 100k messages
                    },
                )

                logger.info("RabbitMQ connection established successfully")

        except Exception as e:
            error_msg = f"Failed to connect to RabbitMQ at {settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise PublishError(error_msg, original_error=e) from e

    def _serialize_event(self, event: DomainEvent) -> str:
        """
        Serialize domain event to JSON string

        Args:
            event: Domain event to serialize

        Returns:
            JSON string representation

        Note:
            Uses Pydantic's model_dump_json() for consistent serialization
        """
        try:
            # Pydantic v2 method (supports datetime, UUID, etc.)
            return event.model_dump_json(exclude_none=True)
        except AttributeError:
            # Fallback for Pydantic v1
            return event.json(exclude_none=True)

    async def publish(self, event: DomainEvent) -> None:
        """
        Publish a domain event to RabbitMQ

        Args:
            event: Domain event to publish

        Raises:
            PublishError: If publishing fails
        """
        try:
            # Ensure connection is established
            await self._connect()

            # Serialize event to JSON
            message_body = self._serialize_event(event)

            # Create message
            message = Message(
                body=message_body.encode("utf-8"),
                delivery_mode=DeliveryMode.PERSISTENT,  # Persistent message
                content_type="application/json",
                content_encoding="utf-8",
                headers={
                    "event_type": event.event_type,
                    "event_id": event.event_id,
                    "timestamp": event.timestamp.isoformat(),
                },
            )

            # Publish to queue
            await self.channel.default_exchange.publish(
                message=message,
                routing_key=self.queue_name,
            )

            logger.info(
                f"Published event to RabbitMQ: {event.event_type} "
                f"(ID: {event.event_id}, Queue: {self.queue_name})"
            )

        except Exception as e:
            error_msg = f"Failed to publish event {event.event_type}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise PublishError(error_msg, event=event, original_error=e) from e

    async def publish_batch(self, events: list[DomainEvent]) -> None:
        """
        Publish multiple events in a batch

        Args:
            events: List of domain events to publish

        Note:
            Maintains a single connection for the entire batch for efficiency.
        """
        if not events:
            logger.warning("Attempted to publish empty batch")
            return

        logger.info(f"Publishing batch of {len(events)} events to RabbitMQ")

        try:
            # Ensure connection is established
            await self._connect()

            for event in events:
                message_body = self._serialize_event(event)

                message = Message(
                    body=message_body.encode("utf-8"),
                    delivery_mode=DeliveryMode.PERSISTENT,
                    content_type="application/json",
                    content_encoding="utf-8",
                    headers={
                        "event_type": event.event_type,
                        "event_id": event.event_id,
                        "timestamp": event.timestamp.isoformat(),
                    },
                )

                await self.channel.default_exchange.publish(
                    message=message,
                    routing_key=self.queue_name,
                )

                logger.debug(f"Batch published: {event.event_type} (ID: {event.event_id})")

            logger.info(f"Successfully published batch of {len(events)} events")

        except Exception as e:
            error_msg = f"Failed to publish batch of {len(events)} events: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise PublishError(error_msg, original_error=e) from e

    async def close(self) -> None:
        """
        Close the publisher and release resources

        Should be called during application shutdown.
        """
        logger.info("Closing RabbitMQ event publisher")
        try:
            if self.connection and not self.connection.is_closed:
                await self.connection.close()
                logger.debug("RabbitMQ connection closed")
        except Exception as e:
            logger.warning(f"Error closing RabbitMQ connection: {e}")
        finally:
            self.connection = None
            self.channel = None
            self.queue = None


# ============================================================================
# Singleton Instance (Dependency Injection)
# ============================================================================

_rabbitmq_publisher_instance: RabbitMQEventPublisher | None = None


def get_rabbitmq_publisher(queue_name: str = "line_message_queue") -> RabbitMQEventPublisher:
    """
    Get RabbitMQ event publisher instance (singleton)

    Args:
        queue_name: Queue name for events (default: line_message_queue)

    Returns:
        RabbitMQEventPublisher instance

    Note:
        For different queues, you may want to create separate instances
        or pass queue_name as a parameter to publish().
    """
    global _rabbitmq_publisher_instance
    if _rabbitmq_publisher_instance is None or _rabbitmq_publisher_instance.queue_name != queue_name:
        _rabbitmq_publisher_instance = RabbitMQEventPublisher(queue_name=queue_name)
    return _rabbitmq_publisher_instance


async def reset_rabbitmq_publisher() -> None:
    """
    Reset global publisher instance (for testing)

    This allows tests to start with a clean slate.
    """
    global _rabbitmq_publisher_instance
    if _rabbitmq_publisher_instance:
        await _rabbitmq_publisher_instance.close()
    _rabbitmq_publisher_instance = None
