"""
Event Log Model - System event tracking (replaces MongoDB)
"""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Index, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from respira_ally.infrastructure.database.session import Base


class EventLogModel(Base):
    """
    Event logs table - System event tracking using PostgreSQL JSONB
    
    Replaces MongoDB for event storage
    """
    __tablename__ = "event_logs"

    # Primary Key
    event_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()")
    )

    # Event Type
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Event type: LOGIN, LOGOUT, DATA_SUBMIT, API_CALL, etc."
    )

    # User/Entity ID (for filtering)
    entity_id: Mapped[UUID | None] = mapped_column(
        nullable=True,
        index=True,
        comment="Related user_id or patient_id"
    )

    # Event Payload (JSONB for flexibility)
    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
        comment="Event payload: {action, details, metadata, ...}"
    )

    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        index=True
    )

    # Indexes
    __table_args__ = (
        # Composite index for common queries (entity + timestamp)
        Index("idx_event_logs_entity_timestamp", "entity_id", "timestamp"),
        # Composite index for event type + timestamp
        Index("idx_event_logs_type_timestamp", "event_type", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<EventLog(event_id={self.event_id}, type={self.event_type}, timestamp={self.timestamp})>"
