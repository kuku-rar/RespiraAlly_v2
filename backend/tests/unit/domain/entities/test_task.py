"""
Unit tests for Task Entity

Tests cover:
- Invariant validation (TD-003.1)
- Domain Events publishing (TD-003.3)
- Business logic (assign, start, complete, cancel)
- Factory methods (create)
- State machine transitions (TODO → IN_PROGRESS → DONE/CANCELLED)
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from respira_ally.domain.entities.task import (
    Task,
    TaskAssignedEvent,
    TaskCancelledEvent,
    TaskCompletedEvent,
    TaskCreatedEvent,
    TaskPriority,
    TaskStartedEvent,
    TaskStatus,
    TaskType,
)
from respira_ally.domain.exceptions import BusinessRuleViolationError


class TestTaskCreation:
    """Test Task creation and basic validation."""

    def test_create_manual_task(self):
        """Test creating a manual task."""
        patient_id = uuid4()
        task = Task.create(
            patient_id=patient_id,
            title="Follow-up with patient",
            priority=TaskPriority.MEDIUM,
            task_type=TaskType.MANUAL,
            description="Check patient's breathing exercises",
        )

        assert task.task_id is not None
        assert task.patient_id == patient_id
        assert task.title == "Follow-up with patient"
        assert task.priority == TaskPriority.MEDIUM
        assert task.status == TaskStatus.TODO
        assert task.task_type == TaskType.MANUAL
        assert task.assigned_to is None

        # Check domain events
        events = task.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskCreatedEvent)
        assert events[0].task_id == task.task_id
        assert events[0].priority == TaskPriority.MEDIUM

    def test_create_alert_triggered_task(self):
        """Test creating an alert-triggered task."""
        patient_id = uuid4()
        alert_id = uuid4()
        therapist_id = uuid4()

        task = Task.create(
            patient_id=patient_id,
            title="Urgent: High Risk Alert",
            priority=TaskPriority.CRITICAL,
            task_type=TaskType.ALERT_TRIGGERED,
            assigned_to=therapist_id,
            related_alert_id=alert_id,
        )

        assert task.priority == TaskPriority.CRITICAL
        assert task.task_type == TaskType.ALERT_TRIGGERED
        assert task.assigned_to == therapist_id
        assert task.related_alert_id == alert_id

    def test_title_cannot_be_empty(self):
        """Test that title cannot be empty."""
        with pytest.raises(BusinessRuleViolationError, match="Task title cannot be empty"):
            Task.create(
                patient_id=uuid4(),
                title="",
                priority=TaskPriority.LOW,
                task_type=TaskType.MANUAL,
            )

    def test_title_cannot_exceed_200_chars(self):
        """Test that title cannot exceed 200 characters."""
        long_title = "A" * 201

        with pytest.raises(
            BusinessRuleViolationError,
            match="Task title cannot exceed 200 characters",
        ):
            Task.create(
                patient_id=uuid4(),
                title=long_title,
                priority=TaskPriority.LOW,
                task_type=TaskType.MANUAL,
            )

    def test_patient_id_required(self):
        """Test that patient_id is required."""
        with pytest.raises(BusinessRuleViolationError, match="patient_id is required"):
            Task(
                task_id=uuid4(),
                patient_id=None,  # type: ignore
                title="Test Task",
                priority=TaskPriority.LOW,
                status=TaskStatus.TODO,
                task_type=TaskType.MANUAL,
            )


class TestTaskAssignment:
    """Test Task assignment workflow."""

    def test_assign_todo_task(self):
        """Test assigning a TODO task."""
        task = Task.create(
            patient_id=uuid4(),
            title="Test Task",
            priority=TaskPriority.MEDIUM,
            task_type=TaskType.MANUAL,
        )
        task.clear_domain_events()

        therapist_id = uuid4()
        task.assign_to(therapist_id)

        assert task.assigned_to == therapist_id
        assert task.status == TaskStatus.IN_PROGRESS  # Auto-updated

        # Check domain events
        events = task.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskAssignedEvent)
        assert events[0].assigned_to == therapist_id
        assert events[0].previous_status == TaskStatus.TODO

    def test_reassign_in_progress_task(self):
        """Test reassigning an IN_PROGRESS task."""
        task = Task.create(
            patient_id=uuid4(),
            title="Test Task",
            priority=TaskPriority.MEDIUM,
            task_type=TaskType.MANUAL,
        )

        first_therapist = uuid4()
        task.assign_to(first_therapist)
        task.clear_domain_events()

        second_therapist = uuid4()
        task.assign_to(second_therapist)

        assert task.assigned_to == second_therapist
        assert task.status == TaskStatus.IN_PROGRESS

        # Check domain events
        events = task.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskAssignedEvent)
        assert events[0].previous_assignee == first_therapist
        assert events[0].assigned_to == second_therapist

    def test_cannot_assign_done_task(self):
        """Test that DONE task cannot be assigned."""
        task = Task.create(
            patient_id=uuid4(),
            title="Test Task",
            priority=TaskPriority.MEDIUM,
            task_type=TaskType.MANUAL,
        )

        task.start()
        task.complete()

        with pytest.raises(
            BusinessRuleViolationError,
            match="Cannot assign DONE task",
        ):
            task.assign_to(uuid4())

    def test_cannot_assign_cancelled_task(self):
        """Test that CANCELLED task cannot be assigned."""
        task = Task.create(
            patient_id=uuid4(),
            title="Test Task",
            priority=TaskPriority.MEDIUM,
            task_type=TaskType.MANUAL,
        )

        task.cancel()

        with pytest.raises(
            BusinessRuleViolationError,
            match="Cannot assign CANCELLED task",
        ):
            task.assign_to(uuid4())


class TestTaskLifecycle:
    """Test Task lifecycle methods."""

    def test_start_task(self):
        """Test starting a TODO task."""
        task = Task.create(
            patient_id=uuid4(),
            title="Test Task",
            priority=TaskPriority.MEDIUM,
            task_type=TaskType.MANUAL,
        )
        task.clear_domain_events()

        task.start()

        assert task.status == TaskStatus.IN_PROGRESS

        # Check domain events
        events = task.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskStartedEvent)

    def test_cannot_start_in_progress_task(self):
        """Test that IN_PROGRESS task cannot be started again."""
        task = Task.create(
            patient_id=uuid4(),
            title="Test Task",
            priority=TaskPriority.MEDIUM,
            task_type=TaskType.MANUAL,
        )

        task.start()

        with pytest.raises(
            BusinessRuleViolationError,
            match="Cannot start task in IN_PROGRESS status",
        ):
            task.start()

    def test_complete_task(self):
        """Test completing an IN_PROGRESS task."""
        task = Task.create(
            patient_id=uuid4(),
            title="Test Task",
            priority=TaskPriority.MEDIUM,
            task_type=TaskType.MANUAL,
        )

        task.start()
        task.clear_domain_events()

        task.complete()

        assert task.status == TaskStatus.DONE
        assert task.completed_at is not None

        # Check domain events
        events = task.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskCompletedEvent)

    def test_cannot_complete_todo_task(self):
        """Test that TODO task cannot be completed directly."""
        task = Task.create(
            patient_id=uuid4(),
            title="Test Task",
            priority=TaskPriority.MEDIUM,
            task_type=TaskType.MANUAL,
        )

        with pytest.raises(
            BusinessRuleViolationError,
            match="Cannot complete task in TODO status",
        ):
            task.complete()

    def test_cancel_todo_task(self):
        """Test cancelling a TODO task."""
        task = Task.create(
            patient_id=uuid4(),
            title="Test Task",
            priority=TaskPriority.MEDIUM,
            task_type=TaskType.MANUAL,
        )
        task.clear_domain_events()

        task.cancel("No longer needed")

        assert task.status == TaskStatus.CANCELLED
        assert task.task_metadata is not None
        assert task.task_metadata["cancellation_reason"] == "No longer needed"

        # Check domain events
        events = task.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskCancelledEvent)
        assert events[0].cancellation_reason == "No longer needed"
        assert events[0].previous_status == TaskStatus.TODO

    def test_cancel_in_progress_task(self):
        """Test cancelling an IN_PROGRESS task."""
        task = Task.create(
            patient_id=uuid4(),
            title="Test Task",
            priority=TaskPriority.MEDIUM,
            task_type=TaskType.MANUAL,
        )

        task.start()
        task.clear_domain_events()

        task.cancel("Patient condition improved")

        assert task.status == TaskStatus.CANCELLED

        # Check domain events
        events = task.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskCancelledEvent)
        assert events[0].previous_status == TaskStatus.IN_PROGRESS

    def test_cannot_cancel_done_task(self):
        """Test that DONE task cannot be cancelled."""
        task = Task.create(
            patient_id=uuid4(),
            title="Test Task",
            priority=TaskPriority.MEDIUM,
            task_type=TaskType.MANUAL,
        )

        task.start()
        task.complete()

        with pytest.raises(BusinessRuleViolationError, match="Cannot cancel completed task"):
            task.cancel()


class TestTaskBusinessLogic:
    """Test Task business logic methods."""

    def test_is_overdue_with_past_due_date(self):
        """Test is_overdue() with past due date."""
        task = Task.create(
            patient_id=uuid4(),
            title="Test Task",
            priority=TaskPriority.MEDIUM,
            task_type=TaskType.MANUAL,
            due_date=datetime.utcnow() - timedelta(days=1),
        )

        assert task.is_overdue()

    def test_is_overdue_with_future_due_date(self):
        """Test is_overdue() with future due date."""
        task = Task.create(
            patient_id=uuid4(),
            title="Test Task",
            priority=TaskPriority.MEDIUM,
            task_type=TaskType.MANUAL,
            due_date=datetime.utcnow() + timedelta(days=1),
        )

        assert not task.is_overdue()

    def test_is_overdue_without_due_date(self):
        """Test is_overdue() without due date."""
        task = Task.create(
            patient_id=uuid4(),
            title="Test Task",
            priority=TaskPriority.MEDIUM,
            task_type=TaskType.MANUAL,
        )

        assert not task.is_overdue()

    def test_is_overdue_for_done_task(self):
        """Test is_overdue() for DONE task."""
        task = Task.create(
            patient_id=uuid4(),
            title="Test Task",
            priority=TaskPriority.MEDIUM,
            task_type=TaskType.MANUAL,
            due_date=datetime.utcnow() - timedelta(days=1),
        )

        task.start()
        task.complete()

        assert not task.is_overdue()  # Completed tasks are not overdue


class TestTaskDomainEvents:
    """Test Task domain events management."""

    def test_get_domain_events_returns_copy(self):
        """Test that get_domain_events() returns a copy."""
        task = Task.create(
            patient_id=uuid4(),
            title="Test Task",
            priority=TaskPriority.MEDIUM,
            task_type=TaskType.MANUAL,
        )

        events1 = task.get_domain_events()
        events2 = task.get_domain_events()

        assert events1 is not events2
        assert events1 == events2

    def test_clear_domain_events(self):
        """Test clearing domain events."""
        task = Task.create(
            patient_id=uuid4(),
            title="Test Task",
            priority=TaskPriority.MEDIUM,
            task_type=TaskType.MANUAL,
        )

        assert len(task.get_domain_events()) == 1

        task.clear_domain_events()

        assert len(task.get_domain_events()) == 0
