"""
LINE Message Domain Events
Domain Layer - Event-Driven Architecture

Events published when LINE messages are received.
These events enable async processing through RabbitMQ.
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from respira_ally.domain.events.daily_log_events import DomainEvent


# ============================================================================
# LINE Message Events
# ============================================================================


class LineTextMessageReceivedEvent(DomainEvent):
    """
    Event published when a text message is received from LINE

    **Use Cases**:
    - Process patient queries through Health Agent
    - Extract health information from natural language
    - Provide RAG-based health guidance

    **Subscribers**:
    - AgentService: Process message with CrewAI agents
    - ConversationService: Store conversation history
    """

    event_type: Literal["line.text_message.received"] = "line.text_message.received"

    # Event data
    patient_id: UUID = Field(..., description="Patient who sent the message")
    line_user_id: str = Field(..., description="LINE user ID (for reply)")
    message_id: str = Field(..., description="LINE message ID")
    text: str = Field(..., description="Message text content")
    reply_token: str = Field(..., description="LINE reply token for response")

    # Metadata
    received_at: datetime = Field(..., description="When the message was received")


class LineAudioMessageReceivedEvent(DomainEvent):
    """
    Event published when an audio message is received from LINE

    **Use Cases**:
    - Transcribe audio to text using Whisper
    - Process through Health Agent
    - Store audio for medical records

    **Subscribers**:
    - AudioProcessingService: Transcribe and process audio
    - AgentService: Process transcribed text
    - StorageService: Archive audio file
    """

    event_type: Literal["line.audio_message.received"] = "line.audio_message.received"

    # Event data
    patient_id: UUID = Field(..., description="Patient who sent the audio")
    line_user_id: str = Field(..., description="LINE user ID (for reply)")
    message_id: str = Field(..., description="LINE message ID")
    audio_url: str | None = Field(None, description="URL to audio file (if stored)")
    audio_data: bytes | None = Field(None, description="Raw audio data (if not stored)")
    duration_ms: int = Field(..., description="Audio duration in milliseconds")
    reply_token: str = Field(..., description="LINE reply token for response")

    # Metadata
    received_at: datetime = Field(..., description="When the audio was received")

    class Config:
        frozen = True
        arbitrary_types_allowed = True  # Allow bytes type


class LineMessageProcessedEvent(DomainEvent):
    """
    Event published when a LINE message has been processed by agents

    **Use Cases**:
    - Send response back to LINE
    - Log agent interaction
    - Track conversation metrics

    **Subscribers**:
    - LineService: Send response via LINE Bot API
    - AnalyticsService: Track agent performance
    """

    event_type: Literal["line.message.processed"] = "line.message.processed"

    # Event data
    patient_id: UUID = Field(..., description="Patient who sent the message")
    line_user_id: str = Field(..., description="LINE user ID")
    original_message_id: str = Field(..., description="Original LINE message ID")
    response_text: str = Field(..., description="Agent response text")
    reply_token: str | None = Field(None, description="LINE reply token (if available)")
    processing_time_ms: int = Field(..., description="Processing duration in milliseconds")

    # Agent metadata
    agent_type: Literal["guardrail", "health", "fallback"] = Field(
        ..., description="Which agent generated the response"
    )
    is_blocked: bool = Field(False, description="Whether content was blocked by guardrail")
    used_rag: bool = Field(False, description="Whether RAG was used in response")


# ============================================================================
# Event Factory Functions
# ============================================================================


def create_line_text_message_received_event(
    patient_id: UUID,
    line_user_id: str,
    message_id: str,
    text: str,
    reply_token: str,
) -> LineTextMessageReceivedEvent:
    """
    Factory function to create LineTextMessageReceivedEvent

    Args:
        patient_id: Patient UUID
        line_user_id: LINE user ID
        message_id: LINE message ID
        text: Message text content
        reply_token: LINE reply token

    Returns:
        LineTextMessageReceivedEvent instance
    """
    from uuid import uuid4

    now = datetime.utcnow()

    return LineTextMessageReceivedEvent(
        event_id=str(uuid4()),
        event_type="line.text_message.received",
        timestamp=now,
        aggregate_id=patient_id,  # Patient is the aggregate root
        patient_id=patient_id,
        line_user_id=line_user_id,
        message_id=message_id,
        text=text,
        reply_token=reply_token,
        received_at=now,
    )


def create_line_audio_message_received_event(
    patient_id: UUID,
    line_user_id: str,
    message_id: str,
    duration_ms: int,
    reply_token: str,
    audio_url: str | None = None,
    audio_data: bytes | None = None,
) -> LineAudioMessageReceivedEvent:
    """
    Factory function to create LineAudioMessageReceivedEvent

    Args:
        patient_id: Patient UUID
        line_user_id: LINE user ID
        message_id: LINE message ID
        duration_ms: Audio duration in milliseconds
        reply_token: LINE reply token
        audio_url: URL to stored audio (optional)
        audio_data: Raw audio bytes (optional)

    Returns:
        LineAudioMessageReceivedEvent instance
    """
    from uuid import uuid4

    now = datetime.utcnow()

    return LineAudioMessageReceivedEvent(
        event_id=str(uuid4()),
        event_type="line.audio_message.received",
        timestamp=now,
        aggregate_id=patient_id,
        patient_id=patient_id,
        line_user_id=line_user_id,
        message_id=message_id,
        audio_url=audio_url,
        audio_data=audio_data,
        duration_ms=duration_ms,
        reply_token=reply_token,
        received_at=now,
    )


def create_line_message_processed_event(
    patient_id: UUID,
    line_user_id: str,
    original_message_id: str,
    response_text: str,
    processing_time_ms: int,
    agent_type: Literal["guardrail", "health", "fallback"],
    reply_token: str | None = None,
    is_blocked: bool = False,
    used_rag: bool = False,
) -> LineMessageProcessedEvent:
    """
    Factory function to create LineMessageProcessedEvent

    Args:
        patient_id: Patient UUID
        line_user_id: LINE user ID
        original_message_id: Original LINE message ID
        response_text: Agent response
        processing_time_ms: Processing duration
        agent_type: Which agent processed the message
        reply_token: LINE reply token (if available)
        is_blocked: Whether content was blocked
        used_rag: Whether RAG was used

    Returns:
        LineMessageProcessedEvent instance
    """
    from uuid import uuid4

    return LineMessageProcessedEvent(
        event_id=str(uuid4()),
        event_type="line.message.processed",
        timestamp=datetime.utcnow(),
        aggregate_id=patient_id,
        patient_id=patient_id,
        line_user_id=line_user_id,
        original_message_id=original_message_id,
        response_text=response_text,
        reply_token=reply_token,
        processing_time_ms=processing_time_ms,
        agent_type=agent_type,
        is_blocked=is_blocked,
        used_rag=used_rag,
    )
