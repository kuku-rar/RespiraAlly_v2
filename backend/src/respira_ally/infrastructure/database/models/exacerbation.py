"""
Exacerbation Model - COPD acute exacerbation records
Sprint 4: Risk Engine - Track patient acute deterioration events
"""

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from respira_ally.infrastructure.database.session import Base

if TYPE_CHECKING:
    from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
    from respira_ally.infrastructure.database.models.user import UserModel


class ExacerbationModel(Base):
    """
    Exacerbations table - COPD acute exacerbation records

    Tracks patient acute deterioration events for GOLD ABE classification and risk assessment.
    Auto-updates patient_profiles summary fields via database trigger.
    """

    __tablename__ = "exacerbations"

    # Primary Key
    exacerbation_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, server_default=text("gen_random_uuid()")
    )

    # Foreign Keys
    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patient_profiles.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Exacerbation Information
    onset_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="Date of exacerbation onset"
    )
    severity: Mapped[str] = mapped_column(
        Enum("MILD", "MODERATE", "SEVERE", name="exacerbation_severity_enum", create_type=False),
        nullable=False,
        comment="Severity level: MILD/MODERATE/SEVERE",
    )

    # Treatment Information
    required_hospitalization: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("FALSE"), comment="Required hospitalization"
    )
    hospitalization_days: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Number of hospitalization days (if hospitalized)"
    )
    required_antibiotics: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("FALSE"), comment="Required antibiotics"
    )
    required_steroids: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("FALSE"), comment="Required steroids"
    )

    # Symptom Description
    symptoms: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Symptom description (e.g., increased cough, sputum)"
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Clinical notes")

    # Metadata
    recorded_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=text("CURRENT_DATE"),
        comment="Date when record was created (may be later than onset_date)",
    )
    recorded_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.user_id"), nullable=True, comment="User who recorded this exacerbation"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.utcnow,
    )

    # Relationships
    patient: Mapped["PatientProfileModel"] = relationship(
        "PatientProfileModel", foreign_keys=[patient_id]
    )
    recorder: Mapped["UserModel | None"] = relationship("UserModel", foreign_keys=[recorded_by])

    # Constraints
    __table_args__ = (
        # Hospitalization days must be > 0 if required_hospitalization = TRUE
        CheckConstraint(
            "(required_hospitalization = FALSE AND hospitalization_days IS NULL) OR "
            "(required_hospitalization = TRUE AND hospitalization_days > 0)",
            name="exacerbation_hospitalization_days_check",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Exacerbation(id={self.exacerbation_id}, "
            f"patient_id={self.patient_id}, "
            f"onset={self.onset_date}, "
            f"severity={self.severity})>"
        )
