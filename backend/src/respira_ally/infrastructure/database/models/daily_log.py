"""
Daily Log Model - Patient daily health tracking
"""
from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
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
        server_default="gen_random_uuid()"
    )

    # Foreign Keys
    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patient_profiles.user_id", ondelete="CASCADE"),
        nullable=False
    )

    # Log Date
    log_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Health Metrics
    medication_taken: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false"
    )
    water_intake_ml: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Daily water intake in milliliters"
    )
    steps_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Daily step count"
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
        server_default="CURRENT_TIMESTAMP"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
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
        # Water intake range
        CheckConstraint(
            "water_intake_ml >= 0 AND water_intake_ml <= 10000",
            name="daily_logs_water_intake_check"
        ),
        # Steps count range
        CheckConstraint(
            "steps_count IS NULL OR (steps_count >= 0 AND steps_count <= 100000)",
            name="daily_logs_steps_count_check"
        ),
    )

    def __repr__(self) -> str:
        return f"<DailyLog(log_id={self.log_id}, patient_id={self.patient_id}, date={self.log_date})>"
