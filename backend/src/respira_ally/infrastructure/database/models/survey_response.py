"""
Survey Response Model - CAT and mMRC questionnaire responses
"""
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from respira_ally.infrastructure.database.session import Base

if TYPE_CHECKING:
    from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel


class SurveyResponseModel(Base):
    """
    Survey responses table - CAT and mMRC questionnaire responses
    """
    __tablename__ = "survey_responses"

    # Primary Key
    response_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()")
    )

    # Survey Type
    survey_type: Mapped[str] = mapped_column(
        Enum("CAT", "mMRC", name="survey_type_enum", create_type=True),
        nullable=False,
        comment="Survey type: CAT (COPD Assessment Test) or mMRC (Modified Medical Research Council)"
    )

    # Foreign Keys
    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patient_profiles.user_id", ondelete="CASCADE"),
        nullable=False
    )

    # Survey Data
    answers: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="Survey answers: {q1: 2, q2: 3, ...}"
    )
    total_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Total calculated score"
    )
    severity_level: Mapped[str | None] = mapped_column(
        Enum("MILD", "MODERATE", "SEVERE", "VERY_SEVERE", name="severity_level_enum", create_type=True),
        nullable=True,
        comment="Calculated severity level"
    )

    # Timestamp
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )

    # Relationships
    patient: Mapped["PatientProfileModel"] = relationship(
        "PatientProfileModel",
        foreign_keys=[patient_id]
    )

    # Constraints
    __table_args__ = (
        # Total score must be non-negative
        CheckConstraint(
            "total_score >= 0",
            name="survey_total_score_check"
        ),
    )

    def __repr__(self) -> str:
        return f"<SurveyResponse(response_id={self.response_id}, type={self.survey_type}, score={self.total_score})>"
