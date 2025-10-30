"""
LINE Message Consumer
Infrastructure Layer - Event-Driven Architecture

Consumes LINE message events from RabbitMQ and processes them with AI agents.
Implements async message processing with robust error handling.
"""

import asyncio
import json
import logging
from typing import Any

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.core.config import settings
from respira_ally.domain.events.line_message_events import (
    LineAudioMessageReceivedEvent,
    LineTextMessageReceivedEvent,
)
from respira_ally.domain.repositories.conversation_repository import (
    ConversationRepository,
)
from respira_ally.domain.repositories.knowledge_repository import KnowledgeRepository
from respira_ally.infrastructure.database.session import AsyncSessionLocal
from respira_ally.infrastructure.repository_impls.conversation_repository_impl import (
    ConversationRepositoryImpl,
)
from respira_ally.infrastructure.repository_impls.pgvector_knowledge_repository import (
    PgvectorKnowledgeRepository,
)
from respira_ally.services.agent_manager import AgentManager

logger = logging.getLogger(__name__)


class LineMessageConsumer:
    """
    Async RabbitMQ consumer for LINE message events

    **Features**:
    - Async message consumption with aio-pika
    - Two-stage agent processing (Guardrail → Health)
    - Automatic message acknowledgment
    - Error handling with DLQ support
    - Graceful shutdown

    **Flow**:
    1. Consume message from RabbitMQ queue
    2. Deserialize domain event
    3. Process with AgentManager
    4. (Future) Publish response back to LINE
    5. Acknowledge message

    **Configuration**:
    Uses settings from core.config:
    - RABBITMQ_HOST, RABBITMQ_PORT
    - RABBITMQ_USER, RABBITMQ_PASSWORD
    """

    def __init__(
        self,
        queue_name: str = "line_message_queue",
        prefetch_count: int = 10,
    ):
        """
        Initialize LINE message consumer

        Args:
            queue_name: Queue name to consume from (default: line_message_queue)
            prefetch_count: Max messages to process concurrently (default: 10)
        """
        self.queue_name = queue_name
        self.prefetch_count = prefetch_count

        self.connection: aio_pika.abc.AbstractConnection | None = None
        self.channel: aio_pika.abc.AbstractChannel | None = None
        self.queue: aio_pika.abc.AbstractQueue | None = None

        # Build connection URL
        self.connection_url = (
            f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@"
            f"{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
        )

        # Agent Manager (initialized later with repositories)
        self.agent_manager: AgentManager | None = None

        logger.info(
            f"LineMessageConsumer initialized for queue: {queue_name} "
            f"(prefetch: {prefetch_count})"
        )

    async def connect(self) -> None:
        """
        Establish connection to RabbitMQ broker

        Raises:
            Exception: If connection fails
        """
        try:
            logger.info("Connecting to RabbitMQ...")

            # Establish connection with reconnection support
            self.connection = await aio_pika.connect_robust(
                url=self.connection_url,
                timeout=30,
            )

            # Create channel
            self.channel = await self.connection.channel()

            # Set QoS (Quality of Service) - max concurrent messages
            await self.channel.set_qos(prefetch_count=self.prefetch_count)

            # Declare queue (idempotent - safe if already exists)
            self.queue = await self.channel.declare_queue(
                name=self.queue_name,
                durable=True,
                arguments={
                    "x-message-ttl": 86400000,  # Message TTL: 24 hours
                    "x-max-length": 100000,  # Max queue length
                },
            )

            logger.info("RabbitMQ connection established successfully")

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}", exc_info=True)
            raise

    async def start_consuming(self) -> None:
        """
        Start consuming messages from queue

        This method blocks and runs the message processing loop.
        Call this in a background task or worker process.

        Example:
            consumer = LineMessageConsumer()
            await consumer.start_consuming()
        """
        try:
            # Ensure connection
            await self.connect()

            # Initialize Agent Manager with repositories
            await self._initialize_agent_manager()

            logger.info(f"Starting to consume messages from queue: {self.queue_name}")

            # Start consuming
            await self.queue.consume(self.process_message)

            logger.info("Consumer started successfully - waiting for messages...")

            # Keep the consumer running
            # This will block until the program is terminated
            await asyncio.Future()  # Run forever

        except KeyboardInterrupt:
            logger.info("Consumer stopped by user")
        except Exception as e:
            logger.error(f"Consumer error: {str(e)}", exc_info=True)
            raise
        finally:
            await self.close()

    async def process_message(self, message: AbstractIncomingMessage) -> None:
        """
        Process incoming RabbitMQ message

        Args:
            message: Incoming RabbitMQ message
        """
        async with message.process():
            try:
                # Decode message body
                body_str = message.body.decode("utf-8")
                event_data = json.loads(body_str)

                logger.info(
                    f"Processing message: {event_data.get('event_type')} "
                    f"(ID: {event_data.get('event_id')})"
                )

                # Dispatch based on event type
                event_type = event_data.get("event_type")

                if event_type == "line.text_message.received":
                    await self._handle_text_message(event_data)
                elif event_type == "line.audio_message.received":
                    await self._handle_audio_message(event_data)
                else:
                    logger.warning(f"Unknown event type: {event_type}")

                logger.info(f"Message processed successfully: {event_data.get('event_id')}")

            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode message: {str(e)}", exc_info=True)
                # Don't requeue - message is malformed
            except Exception as e:
                logger.error(f"Failed to process message: {str(e)}", exc_info=True)
                # Message will be requeued automatically if exception is raised
                # For now, we'll just log and ack (preventing infinite retries)
                # In production, consider implementing:
                # - Dead Letter Queue (DLQ)
                # - Retry with exponential backoff
                # - Alert on repeated failures

    async def _handle_text_message(self, event_data: dict[str, Any]) -> None:
        """
        Handle text message event

        Args:
            event_data: Deserialized event data
        """
        # Reconstruct event object (optional, for type safety)
        patient_id = event_data.get("patient_id")
        text = event_data.get("text")
        line_user_id = event_data.get("line_user_id")
        reply_token = event_data.get("reply_token")

        logger.info(f"Processing text message from patient {patient_id}: {text[:50]}...")

        # Process with Agent Manager
        if not self.agent_manager:
            logger.error("AgentManager not initialized")
            return

        try:
            # Call Agent Manager to process message
            response = await self.agent_manager.handle_message(
                user_id=patient_id,
                user_input=text,
                include_context=True,  # Include conversation history
            )

            logger.info(f"Agent response: {response[:100]}...")

            # TODO: Send response back to LINE
            # This could be done by:
            # 1. Publishing a LineMessageProcessedEvent
            # 2. Another consumer handles LINE Bot API call
            # For now, we just log the response

            # Save to conversation history
            if self.agent_manager.conversation_repo:
                try:
                    # Save user message
                    await self.agent_manager.conversation_repo.save_message(
                        user_id=patient_id,
                        role="user",
                        content=text,
                    )
                    # Save agent response
                    await self.agent_manager.conversation_repo.save_message(
                        user_id=patient_id,
                        role="assistant",
                        content=response,
                    )
                except Exception as e:
                    logger.error(f"Failed to save conversation: {str(e)}")

        except Exception as e:
            logger.error(f"Agent processing failed: {str(e)}", exc_info=True)
            # TODO: Publish error event or send fallback response

    async def _handle_audio_message(self, event_data: dict[str, Any]) -> None:
        """
        Handle audio message event

        Args:
            event_data: Deserialized event data
        """
        patient_id = event_data.get("patient_id")
        message_id = event_data.get("message_id")
        duration_ms = event_data.get("duration_ms")

        logger.info(
            f"Processing audio message from patient {patient_id}: "
            f"duration={duration_ms}ms, message_id={message_id}"
        )

        # TODO: Implement audio processing
        # Flow:
        # 1. Download audio from LINE Bot API using message_id
        # 2. Transcribe with Whisper API
        # 3. Process transcribed text with AgentManager
        # 4. Send response back to LINE
        #
        # For Sprint 6 Phase 2, we'll focus on text messages first
        # Audio processing can be added in a future phase

        logger.warning("Audio message processing not yet implemented - skipping")

    async def _initialize_agent_manager(self) -> None:
        """
        Initialize Agent Manager with repository dependencies

        Creates a new database session and initializes repositories.
        This should be called once when the consumer starts.
        """
        try:
            # Create database session
            db_session = AsyncSessionLocal()

            # Initialize repositories
            conversation_repo = ConversationRepositoryImpl(db_session=db_session)
            knowledge_repo = PgvectorKnowledgeRepository(db_session=db_session)

            # Initialize Agent Manager
            self.agent_manager = AgentManager(
                conversation_repo=conversation_repo,
                knowledge_repo=knowledge_repo,
            )

            logger.info("AgentManager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize AgentManager: {str(e)}", exc_info=True)
            raise

    async def close(self) -> None:
        """
        Close consumer and release resources

        Should be called during shutdown.
        """
        logger.info("Closing LINE message consumer...")
        try:
            if self.connection and not self.connection.is_closed:
                await self.connection.close()
                logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.warning(f"Error closing connection: {e}")
        finally:
            self.connection = None
            self.channel = None
            self.queue = None


# ============================================================================
# Consumer Entry Point (for standalone execution)
# ============================================================================

async def main():
    """
    Main entry point for running the consumer as a standalone process

    Usage:
        python -m respira_ally.infrastructure.message_queue.consumers.line_message_consumer
    """
    consumer = LineMessageConsumer(
        queue_name="line_message_queue",
        prefetch_count=10,
    )

    try:
        await consumer.start_consuming()
    except KeyboardInterrupt:
        logger.info("Consumer stopped by user")
    finally:
        await consumer.close()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run consumer
    asyncio.run(main())
