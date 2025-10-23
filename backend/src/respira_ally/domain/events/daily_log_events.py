"""
Daily Log Domain Events
Domain Layer - Event-Driven Architecture

Events published when daily log actions occur.
These events enable loose coupling between bounded contexts.
"""

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

# ============================================================================
# Base Event
# ============================================================================


class DomainEvent(BaseModel):
    """
    Base class for all domain events

    All domain events should inherit from this base class to ensure
    consistent structure and metadata.
    """

    event_id: str = Field(..., description="Unique event identifier")
    event_type: str = Field(..., description="Event type identifier")
    timestamp: datetime = Field(..., description="When the event occurred")
    aggregate_id: UUID = Field(..., description="ID of the aggregate that produced this event")

    class Config:
        frozen = True  # Events are immutable


# ============================================================================
# Daily Log Events
# ============================================================================


class DailyLogSubmittedEvent(DomainEvent):
    """
    Event published when a patient submits a daily log

    **Use Cases**:
    - Trigger adherence score calculation
    - Send encouragement notifications
    - Update therapist dashboard
    - Generate health trend analysis

    **Subscribers**:
    - NotificationService: Send encouragement message
    - AnalyticsService: Update adherence metrics
    - RiskAssessmentService: Check for health risks
    """

    event_type: Literal["daily_log.submitted"] = "daily_log.submitted"

    # Event data
    patient_id: UUID = Field(..., description="Patient who submitted the log")
    log_date: date = Field(..., description="Date of the log")
    medication_taken: bool = Field(..., description="Whether medication was taken")
    water_intake_ml: int = Field(..., description="Water intake in ml")
    exercise_minutes: int | None = Field(None, description="Exercise duration in minutes")
    symptoms: str | None = Field(None, description="Symptoms description")
    mood: Literal["GOOD", "NEUTRAL", "BAD"] | None = Field(None, description="Mood rating")

    # Metadata
    is_first_log_today: bool = Field(
        ..., description="Whether this is the first log submission today"
    )
    consecutive_days: int = Field(0, description="Number of consecutive days with logs")


class DailyLogUpdatedEvent(DomainEvent):
    """
    Event published when a daily log is updated

    **Use Cases**:
    - Track log modifications
    - Audit trail

    **Subscribers**:
    - AuditService: Log modification history
    """

    event_type: Literal["daily_log.updated"] = "daily_log.updated"

    # Event data
    patient_id: UUID
    log_date: date
    updated_fields: list[str] = Field(..., description="List of fields that were updated")


class DailyLogDeletedEvent(DomainEvent):
    """
    Event published when a daily log is deleted

    **Use Cases**:
    - Recalculate adherence scores
    - Audit trail

    **Subscribers**:
    - AnalyticsService: Recalculate metrics
    - AuditService: Log deletion
    """

    event_type: Literal["daily_log.deleted"] = "daily_log.deleted"

    # Event data
    patient_id: UUID
    log_date: date
    deleted_by: UUID = Field(..., description="User who deleted the log")


# ============================================================================
# Event Factory
# ============================================================================


def create_daily_log_submitted_event(
    log_id: UUID,
    patient_id: UUID,
    log_date: date,
    medication_taken: bool,
    water_intake_ml: int,
    exercise_minutes: int | None,
    symptoms: str | None,
    mood: str | None,
    is_first_log_today: bool = True,
    consecutive_days: int = 0,
) -> DailyLogSubmittedEvent:
    """
    Factory function to create DailyLogSubmittedEvent

    Args:
        log_id: Daily log ID
        patient_id: Patient who submitted
        log_date: Date of the log
        medication_taken: Whether medication was taken
        water_intake_ml: Water intake in ml
        exercise_minutes: Exercise duration in minutes
        symptoms: Symptoms description
        mood: Mood rating
        is_first_log_today: Whether this is first log today
        consecutive_days: Consecutive days with logs

    Returns:
        DailyLogSubmittedEvent instance
    """
    from uuid import uuid4

    return DailyLogSubmittedEvent(
        event_id=str(uuid4()),
        event_type="daily_log.submitted",
        timestamp=datetime.utcnow(),
        aggregate_id=log_id,
        patient_id=patient_id,
        log_date=log_date,
        medication_taken=medication_taken,
        water_intake_ml=water_intake_ml,
        exercise_minutes=exercise_minutes,
        symptoms=symptoms,
        mood=mood,
        is_first_log_today=is_first_log_today,
        consecutive_days=consecutive_days,
    )


def create_daily_log_updated_event(
    log_id: UUID,
    patient_id: UUID,
    log_date: date,
    updated_fields: list[str],
) -> DailyLogUpdatedEvent:
    """
    Factory function to create DailyLogUpdatedEvent

    Args:
        log_id: Daily log ID
        patient_id: Patient who owns the log
        log_date: Date of the log
        updated_fields: List of field names that were updated

    Returns:
        DailyLogUpdatedEvent instance
    """
    from uuid import uuid4

    return DailyLogUpdatedEvent(
        event_id=str(uuid4()),
        event_type="daily_log.updated",
        timestamp=datetime.utcnow(),
        aggregate_id=log_id,
        patient_id=patient_id,
        log_date=log_date,
        updated_fields=updated_fields,
    )


def create_daily_log_deleted_event(
    log_id: UUID,
    patient_id: UUID,
    log_date: date,
    deleted_by: UUID,
) -> DailyLogDeletedEvent:
    """
    Factory function to create DailyLogDeletedEvent

    Args:
        log_id: Daily log ID
        patient_id: Patient who owns the log
        log_date: Date of the log
        deleted_by: User ID who deleted the log

    Returns:
        DailyLogDeletedEvent instance
    """
    from uuid import uuid4

    return DailyLogDeletedEvent(
        event_id=str(uuid4()),
        event_type="daily_log.deleted",
        timestamp=datetime.utcnow(),
        aggregate_id=log_id,
        patient_id=patient_id,
        log_date=log_date,
        deleted_by=deleted_by,
    )
