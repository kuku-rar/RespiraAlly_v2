"""
Task Model - Task Management System
Sprint 5: Task Management - Track therapist action items and assignments

This model represents the database schema for task management.
Tasks are auto-generated from alerts or manually created by therapists.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from respira_ally.infrastructure.database.session import Base

if TYPE_CHECKING:
    from respira_ally.infrastructure.database.models.alert import AlertModel
    from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
    from respira_ally.infrastructure.database.models.therapist_profile import TherapistProfileModel
    from respira_ally.infrastructure.database.models.user import UserModel


class TaskModel(Base):
    """
    Tasks table - Therapist action items and task management

    Task Types:
    - ALERT_TRIGGERED: Auto-generated from Alert
    - MANUAL: Manually created by therapist
    - SCHEDULED: Scheduled routine task

    Task Priorities: CRITICAL, HIGH, MEDIUM, LOW
    Task Statuses: TODO, IN_PROGRESS, DONE, CANCELLED

    Priority Calculation Logic:
    - CRITICAL: Alert severity = CRITICAL
    - HIGH: Alert severity = HIGH or GOLD Group E
    - MEDIUM: Alert severity = MEDIUM
    - LOW: Alert severity = LOW or routine tasks
    """

    __tablename__ = "tasks"
    __table_args__ = {"schema": "development"}

    # Primary Key
    task_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, server_default=text("gen_random_uuid()")
    )

    # Foreign Keys
    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patient_profiles.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Patient this task is related to",
    )
    assigned_to: Mapped[UUID | None] = mapped_column(
        ForeignKey("therapist_profiles.user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Therapist assigned to this task",
    )
    related_alert_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("alerts.alert_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Alert that triggered this task (if applicable)",
    )
    created_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
        comment="User who created this task (for manual tasks)",
    )

    # Task Information
    title: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="Task title (short description)"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Detailed task description and action items"
    )

    # Task Classification
    task_type: Mapped[str] = mapped_column(
        Enum(
            "ALERT_TRIGGERED",
            "MANUAL",
            "SCHEDULED",
            name="task_type_enum",
            create_type=True,
        ),
        nullable=False,
        comment="Task type: ALERT_TRIGGERED/MANUAL/SCHEDULED",
    )
    priority: Mapped[str] = mapped_column(
        Enum(
            "CRITICAL",
            "HIGH",
            "MEDIUM",
            "LOW",
            name="task_priority_enum",
            create_type=True,
        ),
        nullable=False,
        comment="Task priority: CRITICAL/HIGH/MEDIUM/LOW",
    )
    status: Mapped[str] = mapped_column(
        Enum(
            "TODO",
            "IN_PROGRESS",
            "DONE",
            "CANCELLED",
            name="task_status_enum",
            create_type=True,
        ),
        nullable=False,
        server_default=text("'TODO'"),
        comment="Task status: TODO/IN_PROGRESS/DONE/CANCELLED",
    )

    # Task Metadata (JSON format)
    task_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="JSON metadata: {gold_group: 'E', cat_score: 25, reason: '...', cancellation_reason: '...'}",
    )

    # Timestamps
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Task due date (if applicable)",
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Task completion timestamp"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Task creation timestamp",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.utcnow,
        comment="Task last update timestamp",
    )

    # Relationships
    patient: Mapped["PatientProfileModel"] = relationship(
        "PatientProfileModel", foreign_keys=[patient_id], back_populates="tasks"
    )
    therapist: Mapped["TherapistProfileModel | None"] = relationship(
        "TherapistProfileModel", foreign_keys=[assigned_to], back_populates="assigned_tasks"
    )
    related_alert: Mapped["AlertModel | None"] = relationship(
        "AlertModel", foreign_keys=[related_alert_id], back_populates="tasks"
    )
    creator: Mapped["UserModel | None"] = relationship(
        "UserModel", foreign_keys=[created_by]
    )

    def __repr__(self) -> str:
        return (
            f"<Task(id={self.task_id}, "
            f"title={self.title}, "
            f"priority={self.priority}, "
            f"status={self.status})>"
        )
