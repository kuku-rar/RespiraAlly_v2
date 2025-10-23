"""
Patient Profile Model - Patient-specific information
"""

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, Enum, ForeignKey, Integer, Numeric, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from respira_ally.infrastructure.database.session import Base

if TYPE_CHECKING:
    from respira_ally.infrastructure.database.models.therapist_profile import TherapistProfileModel
    from respira_ally.infrastructure.database.models.user import UserModel


class PatientProfileModel(Base):
    """
    Patient profiles table - Extended patient information

    Linked to users table (1:1 relationship for PATIENT role)
    """

    __tablename__ = "patient_profiles"

    # Primary Key (FK to users.user_id)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    )

    # Assigned Therapist (FK to therapist_profiles.user_id)
    therapist_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("therapist_profiles.user_id", ondelete="SET NULL"),
        nullable=True,
        comment="Assigned therapist for this patient",
    )

    # Basic Information
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str | None] = mapped_column(
        Enum("MALE", "FEMALE", "OTHER", name="gender_enum", create_type=True), nullable=True
    )

    # Hospital Integration
    hospital_medical_record_number: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Hospital medical record number (for integration)"
    )

    # Physical Metrics (for BMI calculation and risk assessment)
    height_cm: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Height in centimeters"
    )
    weight_kg: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 1), nullable=True, comment="Weight in kilograms"
    )

    # Smoking History (Critical COPD risk factor)
    smoking_status: Mapped[str | None] = mapped_column(
        Enum("NEVER", "FORMER", "CURRENT", name="smoking_status_enum", create_type=True),
        nullable=True,
        comment="Smoking status",
    )
    smoking_years: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Years of smoking"
    )

    # Extended Information (JSONB for flexibility)
    medical_history: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
        comment="Medical history: {copd_stage, comorbidities, medications, ...}",
    )
    contact_info: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
        comment="Contact info: {phone, address, emergency_contact, ...}",
    )

    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="patient_profile")
    therapist: Mapped["TherapistProfileModel | None"] = relationship(
        "TherapistProfileModel", back_populates="assigned_patients", foreign_keys=[therapist_id]
    )

    # Constraints
    __table_args__ = (
        # Age must be between 18-120 years
        CheckConstraint(
            "birth_date <= CURRENT_DATE - INTERVAL '18 years' AND "
            "birth_date >= CURRENT_DATE - INTERVAL '120 years'",
            name="patient_age_check",
        ),
        # Height range check
        CheckConstraint(
            "height_cm IS NULL OR (height_cm >= 50 AND height_cm <= 250)",
            name="patient_height_check",
        ),
        # Weight range check
        CheckConstraint(
            "weight_kg IS NULL OR (weight_kg >= 20 AND weight_kg <= 300)",
            name="patient_weight_check",
        ),
        # Smoking years range check
        CheckConstraint(
            "smoking_years IS NULL OR (smoking_years >= 0 AND smoking_years <= 100)",
            name="patient_smoking_years_range_check",
        ),
        # Smoking years cannot exceed age
        CheckConstraint(
            "smoking_years IS NULL OR "
            "smoking_years <= EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date))",
            name="patient_smoking_years_check",
        ),
        # Smoking status consistency
        CheckConstraint(
            "(smoking_status = 'NEVER' AND (smoking_years IS NULL OR smoking_years = 0)) OR "
            "(smoking_status IN ('FORMER', 'CURRENT') AND smoking_years > 0) OR "
            "(smoking_status IS NULL)",
            name="patient_smoking_consistency_check",
        ),
    )

    def __repr__(self) -> str:
        return f"<PatientProfile(user_id={self.user_id}, name={self.name})>"
