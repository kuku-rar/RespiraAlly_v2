"""
Therapist Profile Model - Therapist-specific information
"""
from typing import TYPE_CHECKING, List
from uuid import UUID

from sqlalchemy import ForeignKey, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from respira_ally.infrastructure.database.session import Base

if TYPE_CHECKING:
    from respira_ally.infrastructure.database.models.user import UserModel
    from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel


class TherapistProfileModel(Base):
    """
    Therapist profiles table - Extended therapist information
    
    Linked to users table (1:1 relationship for THERAPIST role)
    """
    __tablename__ = "therapist_profiles"

    # Primary Key (FK to users.user_id)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True
    )

    # Basic Information
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    institution: Mapped[str] = mapped_column(String(200), nullable=False)
    license_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="Professional license number"
    )

    # Specialties (JSONB for flexibility)
    specialties: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb"),
        comment="List of specialties: [\"Respiratory\", \"ICU\", ...]"
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="therapist_profile"
    )
    assigned_patients: Mapped[List["PatientProfileModel"]] = relationship(
        "PatientProfileModel",
        back_populates="therapist",
        foreign_keys="PatientProfileModel.therapist_id"
    )

    def __repr__(self) -> str:
        return f"<TherapistProfile(user_id={self.user_id}, name={self.name})>"
