"""
Survey Domain Events
Domain Layer - Event-Driven Architecture

Events published when survey actions occur (CAT and mMRC).
These events enable loose coupling between bounded contexts.
"""

from datetime import datetime
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
# Survey Events
# ============================================================================


class SurveySubmittedEvent(DomainEvent):
    """
    Event published when a patient submits a survey (CAT or mMRC)

    **Use Cases**:
    - Trigger risk assessment if score indicates worsening
    - Send alerts to therapist for concerning scores
    - Update patient health dashboard
    - Generate trend analysis
    - Track disease progression

    **Subscribers**:
    - RiskAssessmentService: Evaluate if score indicates health risk
    - NotificationService: Alert therapist for SEVERE/VERY_SEVERE scores
    - AnalyticsService: Update patient health metrics
    - ReportingService: Generate COPD progression reports
    """

    event_type: Literal["survey.submitted"] = "survey.submitted"

    # Event data
    patient_id: UUID = Field(..., description="Patient who submitted the survey")
    survey_type: Literal["CAT", "mMRC"] = Field(..., description="Type of survey (CAT or mMRC)")
    total_score: int = Field(..., description="Calculated total score")
    severity_level: Literal["MILD", "MODERATE", "SEVERE", "VERY_SEVERE"] = Field(
        ..., description="Calculated severity level"
    )

    # Metadata
    is_first_survey: bool = Field(
        False, description="Whether this is the first survey of this type"
    )
    previous_score: int | None = Field(None, description="Previous survey score (if exists)")
    score_change: int | None = Field(
        None, description="Change from previous score (positive = worsening)"
    )
    is_concerning: bool = Field(
        False, description="Whether score indicates concerning health status"
    )


class SurveyUpdatedEvent(DomainEvent):
    """
    Event published when a survey response is updated

    **Use Cases**:
    - Track survey modifications
    - Audit trail
    - Recalculate risk scores if score changed

    **Subscribers**:
    - AuditService: Log modification history
    - RiskAssessmentService: Recalculate risk if score changed
    """

    event_type: Literal["survey.updated"] = "survey.updated"

    # Event data
    patient_id: UUID
    survey_type: Literal["CAT", "mMRC"]
    old_score: int = Field(..., description="Score before update")
    new_score: int = Field(..., description="Score after update")
    updated_fields: list[str] = Field(..., description="List of fields that were updated")


class SurveyDeletedEvent(DomainEvent):
    """
    Event published when a survey response is deleted

    **Use Cases**:
    - Recalculate statistics and trends
    - Audit trail

    **Subscribers**:
    - AnalyticsService: Recalculate patient metrics
    - AuditService: Log deletion
    """

    event_type: Literal["survey.deleted"] = "survey.deleted"

    # Event data
    patient_id: UUID
    survey_type: Literal["CAT", "mMRC"]
    deleted_score: int
    deleted_by: UUID = Field(..., description="User who deleted the survey")


# ============================================================================
# Event Factory
# ============================================================================


def create_survey_submitted_event(
    response_id: UUID,
    patient_id: UUID,
    survey_type: Literal["CAT", "mMRC"],
    total_score: int,
    severity_level: Literal["MILD", "MODERATE", "SEVERE", "VERY_SEVERE"],
    is_first_survey: bool = False,
    previous_score: int | None = None,
    score_change: int | None = None,
) -> SurveySubmittedEvent:
    """
    Factory function to create SurveySubmittedEvent

    Args:
        response_id: Survey response ID
        patient_id: Patient who submitted
        survey_type: Type of survey (CAT or mMRC)
        total_score: Calculated total score
        severity_level: Calculated severity level
        is_first_survey: Whether this is first survey of this type
        previous_score: Previous survey score (if exists)
        score_change: Change from previous score

    Returns:
        SurveySubmittedEvent instance
    """
    from uuid import uuid4

    # Determine if score is concerning (SEVERE or VERY_SEVERE)
    is_concerning = severity_level in ("SEVERE", "VERY_SEVERE")

    # Or if there's a significant worsening (score increased by 5+ for CAT, 2+ for mMRC)
    if score_change is not None:
        threshold = 5 if survey_type == "CAT" else 2
        if score_change >= threshold:
            is_concerning = True

    return SurveySubmittedEvent(
        event_id=str(uuid4()),
        event_type="survey.submitted",
        timestamp=datetime.utcnow(),
        aggregate_id=response_id,
        patient_id=patient_id,
        survey_type=survey_type,
        total_score=total_score,
        severity_level=severity_level,
        is_first_survey=is_first_survey,
        previous_score=previous_score,
        score_change=score_change,
        is_concerning=is_concerning,
    )


def create_survey_updated_event(
    response_id: UUID,
    patient_id: UUID,
    survey_type: Literal["CAT", "mMRC"],
    old_score: int,
    new_score: int,
    updated_fields: list[str],
) -> SurveyUpdatedEvent:
    """
    Factory function to create SurveyUpdatedEvent

    Args:
        response_id: Survey response ID
        patient_id: Patient who owns the survey
        survey_type: Type of survey
        old_score: Score before update
        new_score: Score after update
        updated_fields: List of field names that were updated

    Returns:
        SurveyUpdatedEvent instance
    """
    from uuid import uuid4

    return SurveyUpdatedEvent(
        event_id=str(uuid4()),
        event_type="survey.updated",
        timestamp=datetime.utcnow(),
        aggregate_id=response_id,
        patient_id=patient_id,
        survey_type=survey_type,
        old_score=old_score,
        new_score=new_score,
        updated_fields=updated_fields,
    )


def create_survey_deleted_event(
    response_id: UUID,
    patient_id: UUID,
    survey_type: Literal["CAT", "mMRC"],
    deleted_score: int,
    deleted_by: UUID,
) -> SurveyDeletedEvent:
    """
    Factory function to create SurveyDeletedEvent

    Args:
        response_id: Survey response ID
        patient_id: Patient who owns the survey
        survey_type: Type of survey
        deleted_score: Score of deleted survey
        deleted_by: User ID who deleted the survey

    Returns:
        SurveyDeletedEvent instance
    """
    from uuid import uuid4

    return SurveyDeletedEvent(
        event_id=str(uuid4()),
        event_type="survey.deleted",
        timestamp=datetime.utcnow(),
        aggregate_id=response_id,
        patient_id=patient_id,
        survey_type=survey_type,
        deleted_score=deleted_score,
        deleted_by=deleted_by,
    )
