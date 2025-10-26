"""
Daily Log Domain Entity
Domain Layer - Clean Architecture

Pure domain entity with NO infrastructure dependencies.
This is what Linus would approve: simple data structures, clear business rules.

"Bad programmers worry about the code. Good programmers worry about data structures."
- Linus Torvalds
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Literal
from uuid import UUID, uuid4

# Type alias for mood enum
MoodType = Literal["GOOD", "NEUTRAL", "BAD"]


@dataclass
class DailyLog:
    """
    Daily Log Entity - Patient daily health tracking

    Pure domain entity with business logic and validation.
    No ORM, no database, no infrastructure.

    Business Rules:
    - One log per patient per day (enforced by unique constraint)
    - Water intake: 0-10000 ml
    - Exercise: 0-480 minutes (max 8 hours)
    - Smoking: 0-100 cigarettes

    Design Philosophy:
    - Immutable after creation (use copy/replace for updates)
    - All validations in __post_init__
    - No setters - modifications create new instances
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

    def __post_init__(self) -> None:
        """
        Validate business rules after initialization

        "Talk is cheap. Show me the code."
        This is where we enforce domain constraints.
        """
        # Water intake validation
        if self.water_intake_ml is not None:
            if not (0 <= self.water_intake_ml <= 10000):
                raise ValueError(
                    f"Water intake must be 0-10000 ml, got {self.water_intake_ml}"
                )

        # Exercise duration validation
        if self.exercise_minutes is not None:
            if not (0 <= self.exercise_minutes <= 480):
                raise ValueError(
                    f"Exercise duration must be 0-480 minutes, got {self.exercise_minutes}"
                )

        # Smoking count validation
        if self.smoking_count is not None:
            if not (0 <= self.smoking_count <= 100):
                raise ValueError(
                    f"Smoking count must be 0-100, got {self.smoking_count}"
                )

        # Mood validation
        if self.mood is not None:
            valid_moods = ["GOOD", "NEUTRAL", "BAD"]
            if self.mood not in valid_moods:
                raise ValueError(
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

    def __str__(self) -> str:
        """Human-readable representation"""
        return f"DailyLog(patient={self.patient_id}, date={self.log_date}, medication={self.medication_taken})"

    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return (
            f"DailyLog(log_id={self.log_id}, patient_id={self.patient_id}, "
            f"log_date={self.log_date}, medication_taken={self.medication_taken})"
        )
