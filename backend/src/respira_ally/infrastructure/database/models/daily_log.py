"""
Daily Log Model - Patient daily health tracking
"""
from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from respira_ally.infrastructure.database.session import Base

if TYPE_CHECKING:
    from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel


class DailyLogModel(Base):
    """
    Daily logs table - Patient daily health tracking
    
    One log per patient per day
    """
    __tablename__ = "daily_logs"

    # Primary Key
    log_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()")
    )

    # Foreign Keys
    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patient_profiles.user_id", ondelete="CASCADE"),
        nullable=False
    )

    # Log Date
    log_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Health Metrics (all nullable for flexible tracking)
    medication_taken: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        comment="Whether medication was taken (NULL = not recorded)"
    )
    water_intake_ml: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Daily water intake in milliliters (NULL = not recorded)"
    )
    exercise_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Daily exercise duration in minutes (replaces steps_count)"
    )
    smoking_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Number of cigarettes smoked (COPD risk factor)"
    )

    # Symptoms & Mood
    symptoms: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Reported symptoms"
    )
    mood: Mapped[str | None] = mapped_column(
        Enum("GOOD", "NEUTRAL", "BAD", name="mood_enum", create_type=True),
        nullable=True,
        comment="Patient mood"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.utcnow
    )

    # Relationships
    patient: Mapped["PatientProfileModel"] = relationship(
        "PatientProfileModel",
        foreign_keys=[patient_id]
    )

    # Constraints
    __table_args__ = (
        # One log per patient per day
        UniqueConstraint("patient_id", "log_date", name="daily_logs_unique_per_day"),
        # Water intake range (nullable)
        CheckConstraint(
            "water_intake_ml IS NULL OR (water_intake_ml >= 0 AND water_intake_ml <= 10000)",
            name="daily_logs_water_intake_check"
        ),
        # Exercise duration range (0-480 minutes = 8 hours max)
        CheckConstraint(
            "exercise_minutes IS NULL OR (exercise_minutes >= 0 AND exercise_minutes <= 480)",
            name="daily_logs_exercise_minutes_check"
        ),
        # Smoking count range (0-100 cigarettes/day)
        CheckConstraint(
            "smoking_count IS NULL OR (smoking_count >= 0 AND smoking_count <= 100)",
            name="daily_logs_smoking_count_check"
        ),
    )

    def __repr__(self) -> str:
        return f"<DailyLog(log_id={self.log_id}, patient_id={self.patient_id}, date={self.log_date})>"
