"""
Risk Assessment Model - GOLD 2011 ABE classification
Sprint 4: Risk Engine - COPD risk assessment based on GOLD ABE system
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from respira_ally.infrastructure.database.session import Base

if TYPE_CHECKING:
    from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel


class RiskAssessmentModel(Base):
    """
    Risk assessments table - GOLD 2011 ABE classification system

    Records COPD risk assessment results based on:
    - CAT score (COPD Assessment Test)
    - mMRC grade (Modified Medical Research Council dyspnea scale)
    - Exacerbation history

    GOLD ABE Classification:
    - Group A: CAT<10 AND mMRC<2 (low risk)
    - Group B: CAT>=10 OR mMRC>=2 (medium risk)
    - Group E: CAT>=10 AND mMRC>=2 (high risk)

    Includes legacy fields (risk_score, risk_level) for backward compatibility (Hybrid Strategy).
    """

    __tablename__ = "risk_assessments"

    # Primary Key
    assessment_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, server_default=text("gen_random_uuid()")
    )

    # Foreign Keys
    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patient_profiles.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Assessment Input Data
    cat_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="CAT (COPD Assessment Test) score (0-40)",
    )
    mmrc_grade: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="mMRC (Modified Medical Research Council) dyspnea grade (0-4)",
    )
    exacerbation_count_12m: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
        comment="Number of exacerbations in last 12 months",
    )
    hospitalization_count_12m: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
        comment="Number of hospitalizations in last 12 months",
    )

    # GOLD ABE Classification Result (Sprint 4)
    gold_group: Mapped[str] = mapped_column(
        Enum("A", "B", "E", name="gold_group_enum", create_type=False),
        nullable=False,
        comment="GOLD 2011 ABE group: A=low risk, B=medium risk, E=high risk",
    )

    # Backward Compatible Fields (Hybrid Strategy - ADR-014)
    # Mapped from gold_group: A→25/low, B→50/medium, E→75/high
    risk_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Legacy risk score (0-100) - mapped from gold_group for backward compatibility",
    )
    risk_level: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Legacy risk level - mapped from gold_group for backward compatibility",
    )

    # Timestamps
    assessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Assessment timestamp",
    )
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

    # Constraints
    __table_args__ = (
        # CAT score range: 0-40
        CheckConstraint(
            "cat_score >= 0 AND cat_score <= 40",
            name="risk_assessment_cat_score_check",
        ),
        # mMRC grade range: 0-4
        CheckConstraint(
            "mmrc_grade >= 0 AND mmrc_grade <= 4",
            name="risk_assessment_mmrc_grade_check",
        ),
        # Risk score range: 0-100 (if provided)
        CheckConstraint(
            "risk_score IS NULL OR (risk_score >= 0 AND risk_score <= 100)",
            name="risk_assessment_risk_score_check",
        ),
        # Risk level values
        CheckConstraint(
            "risk_level IS NULL OR risk_level IN ('low', 'medium', 'high', 'critical')",
            name="risk_assessment_risk_level_check",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<RiskAssessment(id={self.assessment_id}, "
            f"patient_id={self.patient_id}, "
            f"gold_group={self.gold_group}, "
            f"CAT={self.cat_score}, mMRC={self.mmrc_grade})>"
        )
