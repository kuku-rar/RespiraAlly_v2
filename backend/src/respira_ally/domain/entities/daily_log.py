"""
Daily Log Domain Entity - Daily Health Tracking
Sprint 5: Task Management - Patient daily health metrics logging

This Entity represents the business logic and invariants for daily health tracking.
Following Clean Architecture and Linus "Good Taste" principles.

Business Rules (TD-003.1):
1. One log per patient per day (enforced by unique constraint)
2. Water intake: 0-10000 ml
3. Exercise: 0-480 minutes (max 8 hours)
4. Smoking: 0-100 cigarettes
5. Mood must be one of: GOOD, NEUTRAL, BAD

Domain Events (TD-003.3):
- DailyLogCreatedEvent: When daily log is created
- MedicationNotTakenEvent: When patient doesn't take medication

"Bad programmers worry about the code. Good programmers worry about data structures."
- Linus Torvalds
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Literal
from uuid import UUID, uuid4

from respira_ally.domain.events.base import DomainEvent
from respira_ally.domain.exceptions import BusinessRuleViolationError

# Type alias for mood enum
MoodType = Literal["GOOD", "NEUTRAL", "BAD"]


# ============================================================================
# Domain Events
# ============================================================================


@dataclass(frozen=True)
class DailyLogCreatedEvent(DomainEvent):
    """Emitted when a daily log is created"""

    log_id: UUID
    patient_id: UUID
    log_date: date
    medication_taken: bool | None
    water_intake_ml: int | None
    exercise_minutes: int | None
    smoking_count: int | None
    mood: MoodType | None
    created_at: datetime


@dataclass(frozen=True)
class MedicationNotTakenEvent(DomainEvent):
    """Emitted when patient doesn't take medication"""

    log_id: UUID
    patient_id: UUID
    log_date: date
    missed_at: datetime


@dataclass
class DailyLog:
    """
    Daily Log Entity - Patient daily health tracking

    Linus "Good Taste" Principles Applied:
    1. Simple data structure - All health metrics in one place
    2. No special cases - All validations in __post_init__
    3. Single source of truth - One log per patient per day
    4. Clear invariants - Ranges enforced at domain level

    Business Rules:
    - One log per patient per day (enforced by unique constraint)
    - Water intake: 0-10000 ml
    - Exercise: 0-480 minutes (max 8 hours)
    - Smoking: 0-100 cigarettes
    - Medication not taken triggers MedicationNotTakenEvent
    - Domain events published for creation
    """

    # Identifiers
    patient_id: UUID
    log_date: date

    # Health Metrics (nullable for flexible tracking)
    medication_taken: bool | None = None
    water_intake_ml: int | None = None
    exercise_minutes: int | None = None
    smoking_count: int | None = None

    # Symptoms & Mood
    symptoms: str | None = None
    mood: MoodType | None = None

    # Metadata
    log_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain Events (not persisted)
    _domain_events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        """
        Validate invariants after initialization (TD-003.1)

        Linus "Good Taste": All validation in one place, no scattered checks.
        """
        # Water intake validation (0-10000 ml)
        if self.water_intake_ml is not None:
            if not (0 <= self.water_intake_ml <= 10000):
                raise BusinessRuleViolationError(
                    f"Water intake must be 0-10000 ml, got {self.water_intake_ml}"
                )

        # Exercise duration validation (0-480 minutes)
        if self.exercise_minutes is not None:
            if not (0 <= self.exercise_minutes <= 480):
                raise BusinessRuleViolationError(
                    f"Exercise duration must be 0-480 minutes, got {self.exercise_minutes}"
                )

        # Smoking count validation (0-100 cigarettes)
        if self.smoking_count is not None:
            if not (0 <= self.smoking_count <= 100):
                raise BusinessRuleViolationError(
                    f"Smoking count must be 0-100, got {self.smoking_count}"
                )

        # Mood validation
        if self.mood is not None:
            valid_moods: list[MoodType] = ["GOOD", "NEUTRAL", "BAD"]
            if self.mood not in valid_moods:
                raise BusinessRuleViolationError(
                    f"Mood must be one of {valid_moods}, got {self.mood}"
                )

    # ========================================================================
    # Business Logic Methods
    # ========================================================================

    def is_medication_adherent(self) -> bool:
        """
        Check if patient took medication

        Returns:
            True if medication was taken, False otherwise
        """
        return self.medication_taken if self.medication_taken is not None else False

    def has_symptoms(self) -> bool:
        """Check if patient reported any symptoms"""
        return bool(self.symptoms and self.symptoms.strip())

    def is_well_hydrated(self, threshold_ml: int = 2000) -> bool:
        """
        Check if patient is well hydrated

        Args:
            threshold_ml: Minimum water intake for good hydration (default: 2000ml)

        Returns:
            True if water intake >= threshold, False otherwise
        """
        if self.water_intake_ml is None:
            return False
        return self.water_intake_ml >= threshold_ml

    def has_exercised(self, min_minutes: int = 30) -> bool:
        """
        Check if patient exercised adequately

        Args:
            min_minutes: Minimum exercise duration (default: 30 minutes)

        Returns:
            True if exercise >= threshold, False otherwise
        """
        if self.exercise_minutes is None:
            return False
        return self.exercise_minutes >= min_minutes

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
        log_date: date,
        medication_taken: bool | None = None,
        water_intake_ml: int | None = None,
        exercise_minutes: int | None = None,
        smoking_count: int | None = None,
        symptoms: str | None = None,
        mood: MoodType | None = None,
    ) -> "DailyLog":
        """
        Factory method to create a new daily log

        Automatically publishes DailyLogCreatedEvent
        Publishes MedicationNotTakenEvent if medication_taken = False

        Linus "Good Taste": Factory eliminates special case initialization code.
        All daily logs created through this method follow same pattern.

        Args:
            patient_id: UUID of the patient
            log_date: Date of the log entry
            medication_taken: Whether medication was taken (None = not recorded)
            water_intake_ml: Water intake in ml (0-10000)
            exercise_minutes: Exercise duration in minutes (0-480)
            smoking_count: Number of cigarettes smoked (0-100)
            symptoms: Free text symptoms description
            mood: Patient mood (GOOD, NEUTRAL, BAD)

        Returns:
            New DailyLog instance with appropriate events published
        """
        daily_log = cls(
            patient_id=patient_id,
            log_date=log_date,
            medication_taken=medication_taken,
            water_intake_ml=water_intake_ml,
            exercise_minutes=exercise_minutes,
            smoking_count=smoking_count,
            symptoms=symptoms,
            mood=mood,
        )

        # Publish DailyLogCreatedEvent (TD-003.3)
        daily_log._add_domain_event(
            DailyLogCreatedEvent(
                log_id=daily_log.log_id,
                patient_id=patient_id,
                log_date=log_date,
                medication_taken=medication_taken,
                water_intake_ml=water_intake_ml,
                exercise_minutes=exercise_minutes,
                smoking_count=smoking_count,
                mood=mood,
                created_at=daily_log.created_at,
            )
        )

        # Publish MedicationNotTakenEvent if medication not taken (TD-003.3)
        if medication_taken is False:
            daily_log._add_domain_event(
                MedicationNotTakenEvent(
                    log_id=daily_log.log_id,
                    patient_id=patient_id,
                    log_date=log_date,
                    missed_at=daily_log.created_at,
                )
            )

        return daily_log

    def __str__(self) -> str:
        """Human-readable representation"""
        return f"DailyLog(patient={self.patient_id}, date={self.log_date}, medication={self.medication_taken})"

    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return (
            f"<DailyLog(log_id={self.log_id}, "
            f"patient_id={self.patient_id}, "
            f"log_date={self.log_date}, "
            f"medication_taken={self.medication_taken})>"
        )
