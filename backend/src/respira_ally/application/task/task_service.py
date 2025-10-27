"""
Task Service - Application Layer
Sprint 5: Task Management System - Business logic for task management

This service coordinates between:
- Domain Layer: Task entity (business rules and state transitions)
- Infrastructure Layer: TaskRepository (data persistence)

Responsibilities:
- Create and manage tasks (CRUD operations)
- Handle task state transitions (start, complete, cancel, assign)
- Retrieve tasks with filtering and pagination
- Calculate task statistics

Design Philosophy (Linus):
"Good programmers worry about data structures and their relationships."

Data Flow:
1. Request (API) → TaskService → Repository → Database
2. Database → Repository → Task Entity → TaskService → Response (API)
"""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.core.schemas.task import (
    TaskListResponse,
    TaskPriority,
    TaskResponse,
    TaskStatsResponse,
    TaskStatus,
    TaskType,
)
from respira_ally.domain.entities.task import Task
from respira_ally.domain.repositories.i_task_repository import ITaskRepository
from respira_ally.infrastructure.repository_impls.task_repository_impl import TaskRepositoryImpl

logger = logging.getLogger(__name__)


class TaskService:
    """
    Task Service - Coordinate task creation, updates, and retrieval

    Design Note:
        Dependency injection via constructor. TaskRepository is created here
        because it has no external dependencies. This is simpler than
        over-engineering with dependency injection containers.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize task service

        Args:
            db: Database session (async)
        """
        self.db = db
        self.repository: ITaskRepository = TaskRepositoryImpl(db)

    async def create_task(
        self,
        patient_id: UUID,
        title: str,
        priority: TaskPriority,
        task_type: TaskType,
        description: Optional[str] = None,
        assigned_to: Optional[UUID] = None,
        related_alert_id: Optional[UUID] = None,
        due_date: Optional[datetime] = None,
        task_metadata: Optional[dict] = None,
        created_by: Optional[UUID] = None,
    ) -> TaskResponse:
        """
        Create a new task

        Args:
            patient_id: Patient UUID
            title: Task title
            priority: Task priority level
            task_type: Task type (ALERT_TRIGGERED, MANUAL, SCHEDULED)
            description: Optional task description
            assigned_to: Optional therapist UUID to assign to
            related_alert_id: Optional related alert UUID
            due_date: Optional due date
            task_metadata: Optional additional context
            created_by: Optional creator user UUID

        Returns:
            TaskResponse with created task details
        """
        # Create Task entity
        now = datetime.utcnow()
        task = Task(
            task_id=uuid4(),
            patient_id=patient_id,
            title=title,
            description=description,
            priority=priority,
            status=TaskStatus.TODO if assigned_to is None else TaskStatus.IN_PROGRESS,
            task_type=task_type,
            assigned_to=assigned_to,
            related_alert_id=related_alert_id,
            due_date=due_date,
            completed_at=None,
            task_metadata=task_metadata or {},
            created_at=now,
            updated_at=now,
        )

        # Persist to database
        created_task = await self.repository.create(task)

        logger.info(
            f"Created task {created_task.task_id} for patient {patient_id} "
            f"(priority: {priority.value}, type: {task_type.value})"
        )

        return self._to_response(created_task)

    async def get_task_by_id(self, task_id: UUID) -> Optional[TaskResponse]:
        """
        Get single task by ID

        Args:
            task_id: Task UUID

        Returns:
            TaskResponse if found, None otherwise
        """
        task = await self.repository.get_by_id(task_id)
        if not task:
            return None

        return self._to_response(task)

    async def update_task(
        self,
        task_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[TaskPriority] = None,
        assigned_to: Optional[UUID] = None,
        due_date: Optional[datetime] = None,
        task_metadata: Optional[dict] = None,
    ) -> Optional[TaskResponse]:
        """
        Update task details (partial update)

        Args:
            task_id: Task UUID
            title: Optional new title
            description: Optional new description
            priority: Optional new priority
            assigned_to: Optional new assigned therapist
            due_date: Optional new due date
            task_metadata: Optional new metadata

        Returns:
            TaskResponse with updated task, or None if task not found
        """
        task = await self.repository.get_by_id(task_id)
        if not task:
            return None

        # Update fields if provided
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if priority is not None:
            task.priority = priority
        if assigned_to is not None:
            task.assigned_to = assigned_to
        if due_date is not None:
            task.due_date = due_date
        if task_metadata is not None:
            task.task_metadata = task_metadata

        task.updated_at = datetime.utcnow()

        # Persist changes
        updated_task = await self.repository.update(task)

        logger.info(f"Updated task {task_id}")

        return self._to_response(updated_task)

    async def delete_task(self, task_id: UUID) -> bool:
        """
        Delete a task

        Args:
            task_id: Task UUID

        Returns:
            True if deleted, False if task not found
        """
        success = await self.repository.delete(task_id)

        if success:
            logger.info(f"Deleted task {task_id}")

        return success

    # ============================================================================
    # Task State Transitions
    # ============================================================================

    async def assign_task(self, task_id: UUID, therapist_id: UUID) -> Optional[TaskResponse]:
        """
        Assign task to a therapist

        Business Rules (from Task entity):
        - Cannot assign completed or cancelled tasks
        - Auto-updates status to IN_PROGRESS if currently TODO

        Args:
            task_id: Task UUID
            therapist_id: Therapist UUID to assign to

        Returns:
            TaskResponse with updated task, or None if task not found

        Raises:
            ValueError: If task is completed or cancelled
        """
        task = await self.repository.get_by_id(task_id)
        if not task:
            return None

        # Use domain logic for assignment
        task.assign_to(therapist_id)

        # Persist changes
        updated_task = await self.repository.update(task)

        logger.info(f"Assigned task {task_id} to therapist {therapist_id}")

        return self._to_response(updated_task)

    async def start_task(self, task_id: UUID) -> Optional[TaskResponse]:
        """
        Start task execution

        Business Rules (from Task entity):
        - Can only start TODO tasks
        - Auto-assigns status to IN_PROGRESS

        Args:
            task_id: Task UUID

        Returns:
            TaskResponse with updated task, or None if task not found

        Raises:
            ValueError: If task is not in TODO status
        """
        task = await self.repository.get_by_id(task_id)
        if not task:
            return None

        # Use domain logic for state transition
        task.start()

        # Persist changes
        updated_task = await self.repository.update(task)

        logger.info(f"Started task {task_id}")

        return self._to_response(updated_task)

    async def complete_task(self, task_id: UUID) -> Optional[TaskResponse]:
        """
        Complete task execution

        Business Rules (from Task entity):
        - Can only complete IN_PROGRESS tasks
        - Sets completed_at timestamp
        - Updates status to DONE

        Args:
            task_id: Task UUID

        Returns:
            TaskResponse with updated task, or None if task not found

        Raises:
            ValueError: If task is not IN_PROGRESS
        """
        task = await self.repository.get_by_id(task_id)
        if not task:
            return None

        # Use domain logic for state transition
        task.complete()

        # Persist changes
        updated_task = await self.repository.update(task)

        logger.info(f"Completed task {task_id}")

        return self._to_response(updated_task)

    async def cancel_task(
        self, task_id: UUID, reason: Optional[str] = None
    ) -> Optional[TaskResponse]:
        """
        Cancel task

        Business Rules (from Task entity):
        - Can only cancel TODO or IN_PROGRESS tasks
        - Cannot cancel DONE tasks
        - Optionally store cancellation reason in metadata

        Args:
            task_id: Task UUID
            reason: Optional cancellation reason

        Returns:
            TaskResponse with updated task, or None if task not found

        Raises:
            ValueError: If task is already DONE
        """
        task = await self.repository.get_by_id(task_id)
        if not task:
            return None

        # Use domain logic for cancellation
        task.cancel(reason)

        # Persist changes
        updated_task = await self.repository.update(task)

        logger.info(f"Cancelled task {task_id}" + (f" (reason: {reason})" if reason else ""))

        return self._to_response(updated_task)

    # ============================================================================
    # Task Queries
    # ============================================================================

    async def list_patient_tasks(
        self,
        patient_id: UUID,
        page: int = 0,
        page_size: int = 20,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        task_type: Optional[TaskType] = None,
    ) -> TaskListResponse:
        """
        List tasks for a patient with filters and pagination

        Args:
            patient_id: Patient UUID
            page: Page number (0-indexed)
            page_size: Number of items per page
            status: Optional filter by status
            priority: Optional filter by priority
            task_type: Optional filter by task type

        Returns:
            TaskListResponse with paginated results
        """
        tasks, total = await self.repository.list_by_patient(
            patient_id=patient_id,
            page=page,
            page_size=page_size,
            status=status,
            priority=priority,
            task_type=task_type,
        )

        # Convert to response schemas
        task_responses = [self._to_response(task) for task in tasks]

        return TaskListResponse(
            tasks=task_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,  # Ceiling division
        )

    async def list_therapist_tasks(
        self,
        therapist_id: UUID,
        page: int = 0,
        page_size: int = 20,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
    ) -> TaskListResponse:
        """
        List tasks assigned to a therapist with filters and pagination

        Args:
            therapist_id: Therapist UUID
            page: Page number (0-indexed)
            page_size: Number of items per page
            status: Optional filter by status
            priority: Optional filter by priority

        Returns:
            TaskListResponse with paginated results
        """
        tasks, total = await self.repository.list_by_therapist(
            therapist_id=therapist_id,
            page=page,
            page_size=page_size,
            status=status,
            priority=priority,
        )

        # Convert to response schemas
        task_responses = [self._to_response(task) for task in tasks]

        return TaskListResponse(
            tasks=task_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
        )

    async def list_alert_tasks(self, alert_id: UUID) -> list[TaskResponse]:
        """
        List all tasks related to a specific alert

        Args:
            alert_id: Alert UUID

        Returns:
            List of TaskResponse objects
        """
        tasks = await self.repository.list_by_alert(alert_id)

        return [self._to_response(task) for task in tasks]

    async def get_overdue_tasks(
        self, patient_id: Optional[UUID] = None, therapist_id: Optional[UUID] = None
    ) -> list[TaskResponse]:
        """
        Get overdue tasks (optional filtering by patient or therapist)

        Args:
            patient_id: Optional patient UUID filter
            therapist_id: Optional therapist UUID filter

        Returns:
            List of overdue TaskResponse objects
        """
        tasks = await self.repository.get_overdue_tasks(
            patient_id=patient_id, therapist_id=therapist_id
        )

        return [self._to_response(task) for task in tasks]

    # ============================================================================
    # Task Statistics
    # ============================================================================

    async def get_patient_task_stats(self, patient_id: UUID) -> TaskStatsResponse:
        """
        Get task statistics for a patient

        Args:
            patient_id: Patient UUID

        Returns:
            TaskStatsResponse with status and priority breakdown
        """
        stats = await self.repository.get_task_statistics(patient_id=patient_id)

        return TaskStatsResponse(
            patient_id=patient_id,
            therapist_id=None,
            total_tasks=stats["total_tasks"],
            todo_count=stats["status_breakdown"].get("TODO", 0),
            in_progress_count=stats["status_breakdown"].get("IN_PROGRESS", 0),
            done_count=stats["status_breakdown"].get("DONE", 0),
            cancelled_count=stats["status_breakdown"].get("CANCELLED", 0),
            critical_count=stats["priority_breakdown"].get("CRITICAL", 0),
            high_count=stats["priority_breakdown"].get("HIGH", 0),
            medium_count=stats["priority_breakdown"].get("MEDIUM", 0),
            low_count=stats["priority_breakdown"].get("LOW", 0),
            overdue_count=stats["overdue_count"],
            last_task_date=stats.get("last_task_date"),
            last_task_title=stats.get("last_task_title"),
        )

    async def get_therapist_task_stats(self, therapist_id: UUID) -> TaskStatsResponse:
        """
        Get task statistics for a therapist

        Args:
            therapist_id: Therapist UUID

        Returns:
            TaskStatsResponse with status and priority breakdown
        """
        stats = await self.repository.get_task_statistics(therapist_id=therapist_id)

        return TaskStatsResponse(
            patient_id=None,
            therapist_id=therapist_id,
            total_tasks=stats["total_tasks"],
            todo_count=stats["status_breakdown"].get("TODO", 0),
            in_progress_count=stats["status_breakdown"].get("IN_PROGRESS", 0),
            done_count=stats["status_breakdown"].get("DONE", 0),
            cancelled_count=stats["status_breakdown"].get("CANCELLED", 0),
            critical_count=stats["priority_breakdown"].get("CRITICAL", 0),
            high_count=stats["priority_breakdown"].get("HIGH", 0),
            medium_count=stats["priority_breakdown"].get("MEDIUM", 0),
            low_count=stats["priority_breakdown"].get("LOW", 0),
            overdue_count=stats["overdue_count"],
            last_task_date=stats.get("last_task_date"),
            last_task_title=stats.get("last_task_title"),
        )

    # ============================================================================
    # Private Helper Methods
    # ============================================================================

    def _to_response(self, task: Task) -> TaskResponse:
        """
        Convert Task entity to TaskResponse schema

        Args:
            task: Task domain entity

        Returns:
            TaskResponse API schema

        Design Note:
            Private method because this is an implementation detail.
            The conversion is simple data transformation, no business logic.
        """
        return TaskResponse(
            task_id=task.task_id,
            patient_id=task.patient_id,
            title=task.title,
            description=task.description,
            task_type=task.task_type,
            priority=task.priority,
            status=task.status,
            assigned_to=task.assigned_to,
            related_alert_id=task.related_alert_id,
            task_metadata=task.task_metadata,
            due_date=task.due_date.isoformat() if task.due_date else None,
            completed_at=task.completed_at.isoformat() if task.completed_at else None,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
            is_overdue=task.is_overdue(),
        )
