"""
Alert Model - Risk-based alert and notification system
Sprint 4: Alert System - Track and manage patient risk alerts
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from respira_ally.infrastructure.database.session import Base

if TYPE_CHECKING:
    from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
    from respira_ally.infrastructure.database.models.user import UserModel


class AlertModel(Base):
    """
    Alerts table - Risk-based alert and notification system

    Alert Types:
    - RISK_GROUP_CHANGE: GOLD group change detected
    - HIGH_RISK_DETECTED: High risk (Group E) detected
    - EXACERBATION_RISK: Exacerbation risk detected

    Alert Severities: LOW, MEDIUM, HIGH, CRITICAL
    Alert Statuses: ACTIVE, ACKNOWLEDGED, RESOLVED
    """

    __tablename__ = "alerts"

    # Primary Key
    alert_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, server_default=text("gen_random_uuid()")
    )

    # Foreign Keys
    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patient_profiles.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Alert Information
    alert_type: Mapped[str] = mapped_column(
        Enum(
            "RISK_GROUP_CHANGE",
            "HIGH_RISK_DETECTED",
            "EXACERBATION_RISK",
            name="alert_type_enum",
            create_type=False,
        ),
        nullable=False,
        comment="Alert type",
    )
    severity: Mapped[str] = mapped_column(
        Enum(
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL",
            name="alert_severity_enum",
            create_type=False,
        ),
        nullable=False,
        comment="Alert severity level",
    )
    title: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="Alert title (short description)"
    )
    message: Mapped[str] = mapped_column(Text, nullable=False, comment="Alert detailed message")

    # Alert Status
    status: Mapped[str] = mapped_column(
        Enum(
            "ACTIVE",
            "ACKNOWLEDGED",
            "RESOLVED",
            name="alert_status_enum",
            create_type=False,
        ),
        nullable=False,
        server_default=text("'ACTIVE'"),
        comment="Alert status: ACTIVE/ACKNOWLEDGED/RESOLVED",
    )

    # Related Data (JSON format)
    alert_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="JSON metadata: {old_group: 'A', new_group: 'E', trigger_reason: '...'}",
    )

    # Processing Information
    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Acknowledgement timestamp"
    )
    acknowledged_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=True,
        comment="User who acknowledged this alert",
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Resolution timestamp"
    )
    resolved_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=True,
        comment="User who resolved this alert",
    )
    resolution_notes: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Resolution notes"
    )

    # Timestamps
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Alert trigger timestamp",
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
    acknowledger: Mapped["UserModel | None"] = relationship(
        "UserModel", foreign_keys=[acknowledged_by]
    )
    resolver: Mapped["UserModel | None"] = relationship("UserModel", foreign_keys=[resolved_by])

    def __repr__(self) -> str:
        return (
            f"<Alert(id={self.alert_id}, "
            f"type={self.alert_type}, "
            f"severity={self.severity}, "
            f"status={self.status})>"
        )
