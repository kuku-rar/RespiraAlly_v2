"""
Task Domain Entity - Task Management System
Sprint 5: Task Management - Define task domain logic and business rules

This Entity represents the business logic and invariants for task management.
Following Clean Architecture, this entity is independent of database implementation.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID


class TaskPriority(str, Enum):
    """Task Priority Levels - Based on Alert Severity and GOLD ABE classification"""

    CRITICAL = "CRITICAL"  # Alert: CRITICAL severity
    HIGH = "HIGH"  # Alert: HIGH severity or GOLD Group E
    MEDIUM = "MEDIUM"  # Alert: MEDIUM severity
    LOW = "LOW"  # Alert: LOW severity or routine tasks


class TaskStatus(str, Enum):
    """Task Status Lifecycle"""

    TODO = "TODO"  # Task created, not started
    IN_PROGRESS = "IN_PROGRESS"  # Task assigned and in progress
    DONE = "DONE"  # Task completed
    CANCELLED = "CANCELLED"  # Task cancelled


class TaskType(str, Enum):
    """Task Type - Auto-generated or Manual"""

    ALERT_TRIGGERED = "ALERT_TRIGGERED"  # Auto-generated from Alert
    MANUAL = "MANUAL"  # Manually created by therapist
    SCHEDULED = "SCHEDULED"  # Scheduled routine task


@dataclass
class Task:
    """
    Task Domain Entity - Represents therapist action items

    Business Rules:
    1. Cannot assign completed or cancelled tasks
    2. Can only start TODO tasks
    3. Can only complete IN_PROGRESS tasks
    4. Priority is calculated from Alert severity and GOLD group
    5. Related alerts cannot be deleted if task is active
    """

    task_id: UUID
    title: str
    description: Optional[str]
    priority: TaskPriority
    status: TaskStatus
    task_type: TaskType
    patient_id: UUID
    assigned_to: Optional[UUID]  # therapist_id
    related_alert_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    task_metadata: Optional[dict]  # Additional task context (GOLD group, scores, etc.)

    def assign_to(self, therapist_id: UUID) -> None:
        """
        Assign task to a therapist

        Business Rules:
        - Cannot assign completed or cancelled tasks
        - Auto-updates status to IN_PROGRESS if currently TODO

        Args:
            therapist_id: UUID of the therapist to assign to

        Raises:
            ValueError: If task is completed or cancelled
        """
        if self.status in [TaskStatus.DONE, TaskStatus.CANCELLED]:
            raise ValueError(f"Cannot assign {self.status.value} task")

        self.assigned_to = therapist_id
        if self.status == TaskStatus.TODO:
            self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()

    def start(self) -> None:
        """
        Start task execution

        Business Rules:
        - Can only start TODO tasks
        - Auto-assigns status to IN_PROGRESS

        Raises:
            ValueError: If task is not in TODO status
        """
        if self.status != TaskStatus.TODO:
            raise ValueError(f"Cannot start task in {self.status.value} status")

        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()

    def complete(self) -> None:
        """
        Complete task execution

        Business Rules:
        - Can only complete IN_PROGRESS tasks
        - Sets completed_at timestamp
        - Updates status to DONE

        Raises:
            ValueError: If task is not IN_PROGRESS
        """
        if self.status != TaskStatus.IN_PROGRESS:
            raise ValueError(f"Cannot complete task in {self.status.value} status")

        self.status = TaskStatus.DONE
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def cancel(self, reason: Optional[str] = None) -> None:
        """
        Cancel task

        Business Rules:
        - Can only cancel TODO or IN_PROGRESS tasks
        - Cannot cancel DONE tasks
        - Optionally store cancellation reason in metadata

        Args:
            reason: Optional cancellation reason

        Raises:
            ValueError: If task is already DONE
        """
        if self.status == TaskStatus.DONE:
            raise ValueError("Cannot cancel completed task")

        self.status = TaskStatus.CANCELLED
        if reason:
            if self.task_metadata is None:
                self.task_metadata = {}
            self.task_metadata["cancellation_reason"] = reason
        self.updated_at = datetime.utcnow()

    def is_overdue(self) -> bool:
        """
        Check if task is overdue

        Returns:
            True if task has due_date and is past due, False otherwise
        """
        if self.due_date is None:
            return False

        if self.status in [TaskStatus.DONE, TaskStatus.CANCELLED]:
            return False

        return datetime.utcnow() > self.due_date

    def __repr__(self) -> str:
        return (
            f"<Task(id={self.task_id}, "
            f"title={self.title}, "
            f"priority={self.priority.value}, "
            f"status={self.status.value})>"
        )
