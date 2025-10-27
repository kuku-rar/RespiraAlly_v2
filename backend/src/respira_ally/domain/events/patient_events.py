"""
Patient Domain Events
Domain Layer - Event-Driven Architecture

Events published when patient actions occur.
These events enable loose coupling between bounded contexts.
"""

from datetime import date, datetime
from decimal import Decimal
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
# Patient Events
# ============================================================================


class PatientCreatedEvent(DomainEvent):
    """
    Event published when a new patient is created

    **Use Cases**:
    - Send welcome notification
    - Initialize patient dashboard
    - Create default settings

    **Subscribers**:
    - NotificationService: Send welcome message
    - AnalyticsService: Track patient registration
    """

    event_type: Literal["patient.created"] = "patient.created"

    # Event data
    therapist_id: UUID = Field(..., description="Assigned therapist ID")
    name: str = Field(..., description="Patient name")
    birth_date: date | None = Field(None, description="Patient birth date")
    gender: Literal["MALE", "FEMALE", "OTHER"] | None = Field(None, description="Patient gender")


class PatientUpdatedEvent(DomainEvent):
    """
    Event published when a patient profile is updated

    **Use Cases**:
    - Track profile modifications
    - Recalculate risk scores if BMI changes
    - Audit trail

    **Subscribers**:
    - AuditService: Log modification history
    - RiskAssessmentService: Recalculate if BMI changed
    """

    event_type: Literal["patient.updated"] = "patient.updated"

    # Event data
    therapist_id: UUID = Field(..., description="Assigned therapist ID")
    updated_fields: list[str] = Field(..., description="List of fields that were updated")
    bmi_changed: bool = Field(False, description="Whether BMI was affected (height/weight changed)")
    new_bmi: Decimal | None = Field(None, description="New BMI value if changed")


class PatientDeletedEvent(DomainEvent):
    """
    Event published when a patient is deleted

    **Use Cases**:
    - Clean up related data
    - Audit trail
    - Send notification to therapist

    **Subscribers**:
    - DataCleanupService: Remove related records
    - AuditService: Log deletion
    - NotificationService: Notify therapist
    """

    event_type: Literal["patient.deleted"] = "patient.deleted"

    # Event data
    therapist_id: UUID = Field(..., description="Assigned therapist ID")
    deleted_by: UUID = Field(..., description="User who deleted the patient")


# ============================================================================
# Event Factory
# ============================================================================


def create_patient_created_event(
    patient_id: UUID,
    therapist_id: UUID,
    name: str,
    birth_date: date | None = None,
    gender: Literal["MALE", "FEMALE", "OTHER"] | None = None,
) -> PatientCreatedEvent:
    """
    Factory function to create PatientCreatedEvent

    Args:
        patient_id: Patient user ID
        therapist_id: Assigned therapist ID
        name: Patient name
        birth_date: Patient birth date
        gender: Patient gender

    Returns:
        PatientCreatedEvent instance
    """
    from uuid import uuid4

    return PatientCreatedEvent(
        event_id=str(uuid4()),
        event_type="patient.created",
        timestamp=datetime.utcnow(),
        aggregate_id=patient_id,
        therapist_id=therapist_id,
        name=name,
        birth_date=birth_date,
        gender=gender,
    )


def create_patient_updated_event(
    patient_id: UUID,
    therapist_id: UUID,
    updated_fields: list[str],
    bmi_changed: bool = False,
    new_bmi: Decimal | None = None,
) -> PatientUpdatedEvent:
    """
    Factory function to create PatientUpdatedEvent

    Args:
        patient_id: Patient user ID
        therapist_id: Assigned therapist ID
        updated_fields: List of field names that were updated
        bmi_changed: Whether BMI was affected
        new_bmi: New BMI value if changed

    Returns:
        PatientUpdatedEvent instance
    """
    from uuid import uuid4

    return PatientUpdatedEvent(
        event_id=str(uuid4()),
        event_type="patient.updated",
        timestamp=datetime.utcnow(),
        aggregate_id=patient_id,
        therapist_id=therapist_id,
        updated_fields=updated_fields,
        bmi_changed=bmi_changed,
        new_bmi=new_bmi,
    )


def create_patient_deleted_event(
    patient_id: UUID,
    therapist_id: UUID,
    deleted_by: UUID,
) -> PatientDeletedEvent:
    """
    Factory function to create PatientDeletedEvent

    Args:
        patient_id: Patient user ID
        therapist_id: Assigned therapist ID
        deleted_by: User ID who deleted the patient

    Returns:
        PatientDeletedEvent instance
    """
    from uuid import uuid4

    return PatientDeletedEvent(
        event_id=str(uuid4()),
        event_type="patient.deleted",
        timestamp=datetime.utcnow(),
        aggregate_id=patient_id,
        therapist_id=therapist_id,
        deleted_by=deleted_by,
    )
