"""
Task Domain Entity - Task Management System
Sprint 5: Task Management - Define task domain logic and business rules

This Entity represents the business logic and invariants for task management.
Following Clean Architecture and Linus "Good Taste" principles.

Business Rules (TD-003.1):
1. Cannot assign completed or cancelled tasks
2. Can only start TODO tasks
3. Can only complete IN_PROGRESS tasks
4. Priority is calculated from Alert severity and GOLD group
5. Related alerts cannot be deleted if task is active
6. Title must be 1-200 chars, non-empty
7. patient_id is required

Domain Events (TD-003.3):
- TaskCreatedEvent: When task is created
- TaskAssignedEvent: When task is assigned to therapist
- TaskStartedEvent: When task execution starts
- TaskCompletedEvent: When task is completed
- TaskCancelledEvent: When task is cancelled
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from respira_ally.domain.events.base import DomainEvent
from respira_ally.domain.exceptions import BusinessRuleViolationError


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


# ============================================================================
# Domain Events
# ============================================================================


@dataclass(frozen=True)
class TaskCreatedEvent(DomainEvent):
    """Emitted when a task is created"""

    task_id: UUID
    patient_id: UUID
    title: str
    priority: TaskPriority
    task_type: TaskType
    assigned_to: Optional[UUID]
    related_alert_id: Optional[UUID]
    created_at: datetime


@dataclass(frozen=True)
class TaskAssignedEvent(DomainEvent):
    """Emitted when a task is assigned to a therapist"""

    task_id: UUID
    patient_id: UUID
    assigned_to: UUID
    assigned_at: datetime
    previous_assignee: Optional[UUID]
    previous_status: TaskStatus


@dataclass(frozen=True)
class TaskStartedEvent(DomainEvent):
    """Emitted when task execution starts"""

    task_id: UUID
    patient_id: UUID
    started_at: datetime
    assigned_to: Optional[UUID]


@dataclass(frozen=True)
class TaskCompletedEvent(DomainEvent):
    """Emitted when a task is completed"""

    task_id: UUID
    patient_id: UUID
    completed_at: datetime
    assigned_to: Optional[UUID]


@dataclass(frozen=True)
class TaskCancelledEvent(DomainEvent):
    """Emitted when a task is cancelled"""

    task_id: UUID
    patient_id: UUID
    cancelled_at: datetime
    cancellation_reason: Optional[str]
    previous_status: TaskStatus


# ============================================================================
# Task Entity
# ============================================================================


@dataclass
class Task:
    """
    Task Domain Entity - Represents therapist action items

    Linus "Good Taste" Principles Applied:
    1. State machine handles all transitions uniformly - no special cases
    2. Single source of truth: Status determines allowed operations
    3. Validation in __post_init__, business logic in methods
    4. Clear data structure: All state in simple fields, no hidden state

    Business Rules:
    - Cannot assign completed or cancelled tasks
    - Can only start TODO tasks
    - Can only complete IN_PROGRESS tasks
    - Title must be 1-200 chars, non-empty
    - patient_id is required
    - Domain events published for all state transitions
    """

    # Identifiers
    task_id: UUID
    patient_id: UUID

    # Task Classification
    title: str
    description: Optional[str]
    priority: TaskPriority
    status: TaskStatus
    task_type: TaskType

    # Assignment & Relations
    assigned_to: Optional[UUID] = None  # therapist_id
    related_alert_id: Optional[UUID] = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Metadata
    task_metadata: Optional[dict] = None  # Additional task context (GOLD group, scores, etc.)

    # Domain Events (not persisted)
    _domain_events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        """
        Validate invariants after initialization (TD-003.1)

        Linus "Good Taste": All validation in one place, no scattered checks.
        """
        # Validate priority enum
        if not isinstance(self.priority, TaskPriority):
            if isinstance(self.priority, str):
                try:
                    self.priority = TaskPriority(self.priority)
                except ValueError:
                    raise BusinessRuleViolationError(
                        f"Invalid priority. Must be one of {[p.value for p in TaskPriority]}"
                    )
            else:
                raise BusinessRuleViolationError("priority must be TaskPriority enum or string")

        # Validate status enum
        if not isinstance(self.status, TaskStatus):
            if isinstance(self.status, str):
                try:
                    self.status = TaskStatus(self.status)
                except ValueError:
                    raise BusinessRuleViolationError(
                        f"Invalid status. Must be one of {[s.value for s in TaskStatus]}"
                    )
            else:
                raise BusinessRuleViolationError("status must be TaskStatus enum or string")

        # Validate task_type enum
        if not isinstance(self.task_type, TaskType):
            if isinstance(self.task_type, str):
                try:
                    self.task_type = TaskType(self.task_type)
                except ValueError:
                    raise BusinessRuleViolationError(
                        f"Invalid task_type. Must be one of {[t.value for t in TaskType]}"
                    )
            else:
                raise BusinessRuleViolationError("task_type must be TaskType enum or string")

        # Validate title
        if not self.title or not self.title.strip():
            raise BusinessRuleViolationError("Task title cannot be empty")
        if len(self.title) > 200:
            raise BusinessRuleViolationError("Task title cannot exceed 200 characters")

        # Validate patient_id is not None
        if self.patient_id is None:
            raise BusinessRuleViolationError("patient_id is required")

        # Validate workflow consistency
        self._validate_workflow_consistency()

    def _validate_workflow_consistency(self) -> None:
        """
        Validate consistency of workflow fields

        Business Rule: Timestamps and status must match
        """
        # Validate completed_at matches DONE status
        if self.status == TaskStatus.DONE:
            if not self.completed_at:
                raise BusinessRuleViolationError("DONE status requires completed_at timestamp")

        # Validate completed_at is not set for non-DONE tasks
        if self.status != TaskStatus.DONE and self.completed_at:
            raise BusinessRuleViolationError(
                "completed_at should only be set for DONE tasks"
            )

        # Validate timestamp order
        if self.completed_at and self.completed_at < self.created_at:
            raise BusinessRuleViolationError("completed_at cannot be earlier than created_at")

        if self.due_date and self.due_date < self.created_at:
            raise BusinessRuleViolationError("due_date cannot be earlier than created_at")

    # ========================================================================
    # Business Logic Methods
    # ========================================================================

    def assign_to(self, therapist_id: UUID) -> None:
        """
        Assign task to a therapist

        Business Rules:
        - Cannot assign completed or cancelled tasks
        - Auto-updates status to IN_PROGRESS if currently TODO

        Args:
            therapist_id: UUID of the therapist to assign to

        Raises:
            BusinessRuleViolationError: If task is completed or cancelled

        Publishes:
            TaskAssignedEvent
        """
        if self.status in [TaskStatus.DONE, TaskStatus.CANCELLED]:
            raise BusinessRuleViolationError(
                f"Cannot assign {self.status.value} task. "
                f"Only TODO or IN_PROGRESS tasks can be reassigned."
            )

        previous_assignee = self.assigned_to
        previous_status = self.status

        self.assigned_to = therapist_id
        if self.status == TaskStatus.TODO:
            self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()

        # Publish domain event (TD-003.3)
        self._add_domain_event(
            TaskAssignedEvent(
                task_id=self.task_id,
                patient_id=self.patient_id,
                assigned_to=therapist_id,
                assigned_at=self.updated_at,
                previous_assignee=previous_assignee,
                previous_status=previous_status,
            )
        )

    def start(self) -> None:
        """
        Start task execution

        Business Rules:
        - Can only start TODO tasks
        - Auto-assigns status to IN_PROGRESS

        Raises:
            BusinessRuleViolationError: If task is not in TODO status

        Publishes:
            TaskStartedEvent
        """
        if self.status != TaskStatus.TODO:
            raise BusinessRuleViolationError(
                f"Cannot start task in {self.status.value} status. "
                f"Only TODO tasks can be started."
            )

        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()

        # Publish domain event (TD-003.3)
        self._add_domain_event(
            TaskStartedEvent(
                task_id=self.task_id,
                patient_id=self.patient_id,
                started_at=self.updated_at,
                assigned_to=self.assigned_to,
            )
        )

    def complete(self) -> None:
        """
        Complete task execution

        Business Rules:
        - Can only complete IN_PROGRESS tasks
        - Sets completed_at timestamp
        - Updates status to DONE

        Raises:
            BusinessRuleViolationError: If task is not IN_PROGRESS

        Publishes:
            TaskCompletedEvent
        """
        if self.status != TaskStatus.IN_PROGRESS:
            raise BusinessRuleViolationError(
                f"Cannot complete task in {self.status.value} status. "
                f"Only IN_PROGRESS tasks can be completed."
            )

        self.status = TaskStatus.DONE
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        # Publish domain event (TD-003.3)
        self._add_domain_event(
            TaskCompletedEvent(
                task_id=self.task_id,
                patient_id=self.patient_id,
                completed_at=self.completed_at,
                assigned_to=self.assigned_to,
            )
        )

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
            BusinessRuleViolationError: If task is already DONE

        Publishes:
            TaskCancelledEvent
        """
        if self.status == TaskStatus.DONE:
            raise BusinessRuleViolationError(
                "Cannot cancel completed task. "
                "Only TODO or IN_PROGRESS tasks can be cancelled."
            )

        previous_status = self.status
        self.status = TaskStatus.CANCELLED
        if reason:
            if self.task_metadata is None:
                self.task_metadata = {}
            self.task_metadata["cancellation_reason"] = reason
        self.updated_at = datetime.utcnow()

        # Publish domain event (TD-003.3)
        self._add_domain_event(
            TaskCancelledEvent(
                task_id=self.task_id,
                patient_id=self.patient_id,
                cancelled_at=self.updated_at,
                cancellation_reason=reason,
                previous_status=previous_status,
            )
        )

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

    # ========================================================================
    # Domain Events Management (TD-003.3)
    # ========================================================================

    def _add_domain_event(self, event: DomainEvent) -> None:
        """Add domain event to internal list (not persisted)"""
        self._domain_events.append(event)

    def get_domain_events(self) -> list[DomainEvent]:
        """Get all domain events for Application Service to publish"""
        return self._domain_events.copy()

    def clear_domain_events(self) -> None:
        """Clear domain events after Application Service publishes them"""
        self._domain_events.clear()

    # ========================================================================
    # Factory Methods
    # ========================================================================

    @classmethod
    def create(
        cls,
        patient_id: UUID,
        title: str,
        priority: TaskPriority,
        task_type: TaskType,
        description: Optional[str] = None,
        assigned_to: Optional[UUID] = None,
        related_alert_id: Optional[UUID] = None,
        due_date: Optional[datetime] = None,
        task_metadata: Optional[dict] = None,
    ) -> "Task":
        """
        Factory method to create a new task

        Automatically publishes TaskCreatedEvent

        Linus "Good Taste": Factory eliminates special case initialization code.
        All tasks created through this method follow same pattern.

        Args:
            patient_id: UUID of the patient this task is for
            title: Task title (1-200 chars)
            priority: Task priority level
            task_type: Task type (ALERT_TRIGGERED, MANUAL, SCHEDULED)
            description: Optional task description
            assigned_to: Optional UUID of therapist to assign to
            related_alert_id: Optional UUID of related alert
            due_date: Optional due date for task completion
            task_metadata: Optional additional task context

        Returns:
            New Task instance with TaskCreatedEvent published
        """
        task = cls(
            task_id=uuid4(),
            patient_id=patient_id,
            title=title,
            description=description,
            priority=priority,
            status=TaskStatus.TODO,
            task_type=task_type,
            assigned_to=assigned_to,
            related_alert_id=related_alert_id,
            due_date=due_date,
            task_metadata=task_metadata,
        )

        # Publish domain event (TD-003.3)
        task._add_domain_event(
            TaskCreatedEvent(
                task_id=task.task_id,
                patient_id=patient_id,
                title=title,
                priority=priority,
                task_type=task_type,
                assigned_to=assigned_to,
                related_alert_id=related_alert_id,
                created_at=task.created_at,
            )
        )

        return task

    def __repr__(self) -> str:
        return (
            f"<Task(id={self.task_id}, "
            f"title={self.title}, "
            f"priority={self.priority.value}, "
            f"status={self.status.value})>"
        )
