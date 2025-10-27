"""
Task Repository Interface - Repository pattern contract for task persistence
Sprint 5: Task Management - Define repository contract following DDD

This interface defines the contract for task persistence operations.
Following Clean Architecture, this interface belongs to the domain layer,
while implementations belong to the infrastructure layer (Dependency Inversion).
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID

from respira_ally.domain.entities.task import Task, TaskPriority, TaskStatus, TaskType


class ITaskRepository(ABC):
    """
    Task Repository Interface - Define persistence contract

    Following Repository Pattern:
    - Interface in Domain Layer (this file)
    - Implementation in Infrastructure Layer (task_repository.py)
    - Dependency Inversion Principle (DIP) applied

    Business Rules:
    - All queries support filtering and pagination
    - Soft delete not supported (hard delete only)
    - Optimistic locking for concurrent updates (via updated_at)
    """

    @abstractmethod
    async def create(self, task: Task) -> Task:
        """
        Create a new task

        Args:
            task: Task entity to create

        Returns:
            Created task with generated task_id and timestamps
        """
        pass

    @abstractmethod
    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        """
        Get task by ID

        Args:
            task_id: Task UUID

        Returns:
            Task if found, None otherwise
        """
        pass

    @abstractmethod
    async def list_by_patient(
        self,
        patient_id: UUID,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        task_type: Optional[TaskType] = None,
        page: int = 0,
        page_size: int = 20,
    ) -> tuple[list[Task], int]:
        """
        List tasks for a specific patient with filtering and pagination

        Args:
            patient_id: Patient UUID
            status: Optional status filter
            priority: Optional priority filter
            task_type: Optional task type filter
            page: Page number (0-indexed)
            page_size: Number of items per page

        Returns:
            Tuple of (task list, total count)
        """
        pass

    @abstractmethod
    async def list_by_therapist(
        self,
        therapist_id: UUID,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        include_unassigned: bool = False,
        page: int = 0,
        page_size: int = 20,
    ) -> tuple[list[Task], int]:
        """
        List tasks assigned to a specific therapist with filtering

        Args:
            therapist_id: Therapist UUID
            status: Optional status filter
            priority: Optional priority filter
            include_unassigned: If True, include unassigned tasks
            page: Page number (0-indexed)
            page_size: Number of items per page

        Returns:
            Tuple of (task list, total count)
        """
        pass

    @abstractmethod
    async def list_by_alert(
        self,
        alert_id: UUID,
    ) -> list[Task]:
        """
        List all tasks related to a specific alert

        Args:
            alert_id: Alert UUID

        Returns:
            List of tasks related to the alert
        """
        pass

    @abstractmethod
    async def update(self, task: Task) -> Task:
        """
        Update existing task

        Args:
            task: Task entity with updated fields

        Returns:
            Updated task

        Raises:
            ValueError: If task not found
        """
        pass

    @abstractmethod
    async def delete(self, task_id: UUID) -> bool:
        """
        Delete task (hard delete)

        Args:
            task_id: Task UUID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def get_overdue_tasks(
        self,
        as_of: Optional[datetime] = None,
        therapist_id: Optional[UUID] = None,
    ) -> list[Task]:
        """
        Get all overdue tasks

        Args:
            as_of: Cutoff datetime (default: now)
            therapist_id: Optional filter by therapist

        Returns:
            List of overdue tasks (status != DONE/CANCELLED and due_date < as_of)
        """
        pass

    @abstractmethod
    async def get_task_statistics(
        self,
        therapist_id: Optional[UUID] = None,
        patient_id: Optional[UUID] = None,
    ) -> dict:
        """
        Get task statistics (counts by status, priority, etc.)

        Args:
            therapist_id: Optional filter by therapist
            patient_id: Optional filter by patient

        Returns:
            Dictionary with statistics:
            {
                "total": int,
                "by_status": {"TODO": int, "IN_PROGRESS": int, "DONE": int, "CANCELLED": int},
                "by_priority": {"CRITICAL": int, "HIGH": int, "MEDIUM": int, "LOW": int},
                "overdue_count": int,
            }
        """
        pass
