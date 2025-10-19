"""
User Model - Core authentication table
Supports both PATIENT (LINE OAuth) and THERAPIST (Email/Password) login
"""
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from respira_ally.infrastructure.database.session import Base

if TYPE_CHECKING:
    from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
    from respira_ally.infrastructure.database.models.therapist_profile import TherapistProfileModel


class UserModel(Base):
    """
    Users table - Core authentication entity

    Supports two authentication methods:
    - PATIENT: LINE OAuth (line_user_id)
    - THERAPIST: Email + Password (email + hashed_password)
    """
    __tablename__ = "users"

    # Primary Key
    user_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        server_default="gen_random_uuid()"
    )

    # Authentication Fields
    line_user_id: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        comment="LINE User ID for PATIENT login"
    )
    email: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        comment="Email for THERAPIST login"
    )
    hashed_password: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Bcrypt hashed password (null for LINE OAuth)"
    )

    # Role
    role: Mapped[str] = mapped_column(
        Enum("PATIENT", "THERAPIST", name="user_role_enum", create_type=True),
        nullable=False,
        comment="User role"
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
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Soft delete timestamp"
    )

    # Relationships
    patient_profile: Mapped["PatientProfileModel | None"] = relationship(
        "PatientProfileModel",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    therapist_profile: Mapped["TherapistProfileModel | None"] = relationship(
        "TherapistProfileModel",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        # At least one login method must be provided
        CheckConstraint(
            "line_user_id IS NOT NULL OR email IS NOT NULL",
            name="users_login_method_check"
        ),
        # PATIENT must have line_user_id
        CheckConstraint(
            "role != 'PATIENT' OR line_user_id IS NOT NULL",
            name="users_patient_line_check"
        ),
        # THERAPIST must have email
        CheckConstraint(
            "role != 'THERAPIST' OR email IS NOT NULL",
            name="users_therapist_email_check"
        ),
    )

    def __repr__(self) -> str:
        return f"<User(user_id={self.user_id}, role={self.role})>"
