"""
SurveyResponse Domain Entity - CAT and mMRC Survey Management
Sprint 4: Risk Engine - Survey response data for COPD assessment

This Entity represents the business logic and invariants for survey responses.
Following Clean Architecture and Linus "Good Taste" principles.

Business Rules (TD-003.1):
1. Survey type must be: CAT or mMRC
2. Total score must be >= 0
3. For CAT: score range 0-40, 8 questions
4. For mMRC: grade range 0-4, single question
5. Severity level: MILD, MODERATE, SEVERE, VERY_SEVERE
6. Answers must be non-empty dict

Domain Events (TD-003.3):
- SurveySubmittedEvent: When survey is submitted
- HighSeveritySurveyEvent: When survey shows SEVERE/VERY_SEVERE severity

"Bad programmers worry about the code. Good programmers worry about data structures."
- Linus Torvalds
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from respira_ally.domain.events.base import DomainEvent
from respira_ally.domain.exceptions import BusinessRuleViolationError


# ============================================================================
# Survey Enums
# ============================================================================


SurveyType = Literal["CAT", "mMRC"]
SeverityLevel = Literal["MILD", "MODERATE", "SEVERE", "VERY_SEVERE"]


# ============================================================================
# Domain Events
# ============================================================================


@dataclass(frozen=True)
class SurveySubmittedEvent(DomainEvent):
    """Emitted when a patient submits a survey (CAT or mMRC)"""

    response_id: UUID
    patient_id: UUID
    survey_type: SurveyType
    total_score: int
    severity_level: SeverityLevel
    is_first_survey: bool
    previous_score: int | None
    score_change: int | None
    is_concerning: bool
    submitted_at: datetime


@dataclass(frozen=True)
class HighSeveritySurveyEvent(DomainEvent):
    """Emitted when survey shows SEVERE or VERY_SEVERE severity"""

    response_id: UUID
    patient_id: UUID
    survey_type: SurveyType
    total_score: int
    severity_level: SeverityLevel
    submitted_at: datetime


# ============================================================================
# SurveyResponse Entity
# ============================================================================


@dataclass
class SurveyResponse:
    """
    SurveyResponse Domain Entity - CAT and mMRC survey responses

    Linus "Good Taste" Principles Applied:
    1. Simple data structure - Survey data in JSONB answers dict
    2. No special cases - Same structure for CAT and mMRC
    3. Single source of truth - survey_type determines validation rules
    4. Clear invariants - Score ranges enforced based on type

    Business Rules:
    - CAT: 8 questions, score 0-40, severity thresholds
    - mMRC: 1 question, grade 0-4 (same as score)
    - Total score must be non-negative
    - Severity auto-calculated from score
    - Domain events published for submission and high severity
    """

    # Identifiers
    response_id: UUID
    patient_id: UUID

    # Survey Data
    survey_type: SurveyType
    answers: dict  # JSONB: {"q1": 2, "q2": 3, ...}
    total_score: int
    severity_level: SeverityLevel | None = None

    # Timestamps
    submitted_at: datetime = field(default_factory=datetime.utcnow)

    # Domain Events (not persisted)
    _domain_events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        """
        Validate invariants after initialization (TD-003.1)

        Linus "Good Taste": All validation in one place, no scattered checks.
        """
        # Validate survey_type
        valid_survey_types: list[SurveyType] = ["CAT", "mMRC"]
        if self.survey_type not in valid_survey_types:
            raise BusinessRuleViolationError(
                f"Survey type must be one of {valid_survey_types}, got {self.survey_type}"
            )

        # Validate total_score is non-negative
        if self.total_score < 0:
            raise BusinessRuleViolationError(
                f"Total score must be >= 0, got {self.total_score}"
            )

        # Validate score range based on survey type
        if self.survey_type == "CAT":
            if not 0 <= self.total_score <= 40:
                raise BusinessRuleViolationError(
                    f"CAT score must be 0-40, got {self.total_score}"
                )
        elif self.survey_type == "mMRC":
            if not 0 <= self.total_score <= 4:
                raise BusinessRuleViolationError(
                    f"mMRC grade must be 0-4, got {self.total_score}"
                )

        # Validate answers is non-empty dict
        if not isinstance(self.answers, dict) or not self.answers:
            raise BusinessRuleViolationError("Answers must be non-empty dict")

        # Validate severity_level if provided
        if self.severity_level is not None:
            valid_severity: list[SeverityLevel] = [
                "MILD",
                "MODERATE",
                "SEVERE",
                "VERY_SEVERE",
            ]
            if self.severity_level not in valid_severity:
                raise BusinessRuleViolationError(
                    f"Severity level must be one of {valid_severity}, got {self.severity_level}"
                )

    # ========================================================================
    # Business Logic Methods
    # ========================================================================

    def calculate_severity(self) -> SeverityLevel:
        """
        Calculate severity level based on survey type and score

        Business Logic:
        - CAT: 0-9 MILD, 10-19 MODERATE, 20-29 SEVERE, 30-40 VERY_SEVERE
        - mMRC: 0-1 MILD, 2 MODERATE, 3 SEVERE, 4 VERY_SEVERE

        Returns:
            Severity level based on score
        """
        if self.survey_type == "CAT":
            if self.total_score < 10:
                return "MILD"
            elif self.total_score < 20:
                return "MODERATE"
            elif self.total_score < 30:
                return "SEVERE"
            else:
                return "VERY_SEVERE"
        else:  # mMRC
            if self.total_score <= 1:
                return "MILD"
            elif self.total_score == 2:
                return "MODERATE"
            elif self.total_score == 3:
                return "SEVERE"
            else:  # 4
                return "VERY_SEVERE"

    def is_concerning(self) -> bool:
        """
        Check if survey result is concerning (SEVERE or VERY_SEVERE)

        Returns:
            True if severity is SEVERE or VERY_SEVERE
        """
        if self.severity_level is None:
            severity = self.calculate_severity()
        else:
            severity = self.severity_level

        return severity in ("SEVERE", "VERY_SEVERE")

    def has_significant_change(self, previous_score: int | None, threshold: int = 5) -> bool:
        """
        Check if score changed significantly from previous survey

        Args:
            previous_score: Previous survey score (None if first survey)
            threshold: Minimum change to be considered significant (default: 5 for CAT, 2 for mMRC)

        Returns:
            True if score changed by >= threshold
        """
        if previous_score is None:
            return False

        # Adjust threshold based on survey type
        if self.survey_type == "mMRC":
            threshold = 2

        score_change = abs(self.total_score - previous_score)
        return score_change >= threshold

    # ========================================================================
    # Domain Events Management (TD-003.3)
    # ========================================================================

    def _add_domain_event(self, event: DomainEvent) -> None:
        """Add domain event to internal list (not persisted)"""
        self._domain_events.append(event)

    def get_domain_events(self) -> list[DomainEvent]:
        """Get all domain events for Application Service to publish"""
        return self._domain_events.copy()

    def clear_domain_events(self) -> None:
        """Clear domain events after Application Service publishes them"""
        self._domain_events.clear()

    # ========================================================================
    # Factory Methods
    # ========================================================================

    @classmethod
    def create(
        cls,
        patient_id: UUID,
        survey_type: SurveyType,
        answers: dict,
        total_score: int,
        is_first_survey: bool = False,
        previous_score: int | None = None,
    ) -> "SurveyResponse":
        """
        Factory method to create a new survey response

        Automatically:
        - Calculates severity level
        - Publishes SurveySubmittedEvent
        - Publishes HighSeveritySurveyEvent if concerning

        Linus "Good Taste": Factory eliminates special case initialization code.
        All survey responses created through this method follow same pattern.

        Args:
            patient_id: UUID of the patient
            survey_type: Type of survey (CAT or mMRC)
            answers: Survey answers dict (e.g., {"q1": 2, "q2": 3})
            total_score: Calculated total score
            is_first_survey: Whether this is first survey of this type
            previous_score: Previous survey score (if exists)

        Returns:
            New SurveyResponse instance with appropriate events published
        """
        # Create survey response
        survey_response = cls(
            response_id=uuid4(),
            patient_id=patient_id,
            survey_type=survey_type,
            answers=answers,
            total_score=total_score,
        )

        # Auto-calculate severity
        severity = survey_response.calculate_severity()
        survey_response.severity_level = severity

        # Calculate score change
        score_change = None
        if previous_score is not None:
            score_change = total_score - previous_score

        # Determine if concerning
        is_concerning = survey_response.is_concerning()

        # Publish SurveySubmittedEvent (TD-003.3)
        survey_response._add_domain_event(
            SurveySubmittedEvent(
                response_id=survey_response.response_id,
                patient_id=patient_id,
                survey_type=survey_type,
                total_score=total_score,
                severity_level=severity,
                is_first_survey=is_first_survey,
                previous_score=previous_score,
                score_change=score_change,
                is_concerning=is_concerning,
                submitted_at=survey_response.submitted_at,
            )
        )

        # Publish HighSeveritySurveyEvent if concerning (TD-003.3)
        if is_concerning:
            survey_response._add_domain_event(
                HighSeveritySurveyEvent(
                    response_id=survey_response.response_id,
                    patient_id=patient_id,
                    survey_type=survey_type,
                    total_score=total_score,
                    severity_level=severity,
                    submitted_at=survey_response.submitted_at,
                )
            )

        return survey_response

    def __repr__(self) -> str:
        return (
            f"<SurveyResponse(id={self.response_id}, "
            f"type={self.survey_type}, "
            f"score={self.total_score}, "
            f"severity={self.severity_level})>"
        )
