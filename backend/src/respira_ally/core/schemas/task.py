"""
Task Schemas
Pydantic models for Task Management System API endpoints

Sprint 5: Task Management System - Therapist action items and assignments
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Task Enums (mirrored from Domain Entity)
# ============================================================================


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
# Task Request Schemas
# ============================================================================


class TaskCreateRequest(BaseModel):
    """
    Request schema for creating a new task (POST /api/v1/tasks/)

    Therapists can manually create tasks for patients.
    """

    model_config = ConfigDict(from_attributes=True)

    # Required fields
    patient_id: UUID = Field(..., description="Patient UUID")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    priority: TaskPriority = Field(..., description="Task priority level")
    task_type: TaskType = Field(
        default=TaskType.MANUAL, description="Task type (defaults to MANUAL)"
    )

    # Optional fields
    description: Optional[str] = Field(None, description="Detailed task description")
    assigned_to: Optional[UUID] = Field(None, description="Therapist UUID to assign to")
    related_alert_id: Optional[UUID] = Field(
        None, description="Related alert ID (if triggered by alert)"
    )
    due_date: Optional[datetime] = Field(None, description="Task due date (ISO 8601)")
    task_metadata: Optional[dict] = Field(
        None, description="Additional task context (GOLD group, scores, etc.)"
    )


class TaskUpdateRequest(BaseModel):
    """
    Request schema for updating an existing task (PATCH /api/v1/tasks/{id})

    Therapists can update task details, assignment, and metadata.
    Status transitions should use dedicated endpoints (/start, /complete, /cancel).
    """

    model_config = ConfigDict(from_attributes=True)

    # All fields optional for partial updates
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None)
    priority: Optional[TaskPriority] = Field(None)
    assigned_to: Optional[UUID] = Field(None, description="Reassign to different therapist")
    due_date: Optional[datetime] = Field(None)
    task_metadata: Optional[dict] = Field(None)


class TaskAssignRequest(BaseModel):
    """
    Request schema for assigning a task to a therapist (POST /api/v1/tasks/{id}/assign)
    """

    model_config = ConfigDict(from_attributes=True)

    therapist_id: UUID = Field(..., description="Therapist UUID to assign to")


class TaskCancelRequest(BaseModel):
    """
    Request schema for cancelling a task (POST /api/v1/tasks/{id}/cancel)
    """

    model_config = ConfigDict(from_attributes=True)

    reason: Optional[str] = Field(None, description="Cancellation reason")


# ============================================================================
# Task Response Schemas
# ============================================================================


class TaskResponse(BaseModel):
    """
    Task response schema for API endpoints

    Represents a single task with all details.
    """

    model_config = ConfigDict(from_attributes=True)

    # Core fields
    task_id: UUID = Field(..., description="Task UUID")
    patient_id: UUID = Field(..., description="Patient UUID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")

    # Classification
    task_type: TaskType = Field(..., description="Task type")
    priority: TaskPriority = Field(..., description="Task priority level")
    status: TaskStatus = Field(..., description="Task status")

    # Assignment and relationships
    assigned_to: Optional[UUID] = Field(None, description="Assigned therapist UUID")
    related_alert_id: Optional[UUID] = Field(None, description="Related alert UUID")

    # Metadata
    task_metadata: Optional[dict] = Field(None, description="Additional task context")

    # Timestamps
    due_date: Optional[str] = Field(None, description="Due date (ISO 8601)")
    completed_at: Optional[str] = Field(None, description="Completion timestamp (ISO 8601)")
    created_at: str = Field(..., description="Creation timestamp (ISO 8601)")
    updated_at: str = Field(..., description="Last update timestamp (ISO 8601)")

    # Computed fields
    is_overdue: bool = Field(..., description="Whether task is overdue")


class TaskListResponse(BaseModel):
    """
    Paginated task list response

    Used for GET /api/v1/patients/{patient_id}/tasks endpoint
    """

    model_config = ConfigDict(from_attributes=True)

    tasks: list[TaskResponse] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks matching filters")
    page: int = Field(..., description="Current page number (0-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


# ============================================================================
# Task Statistics Schemas
# ============================================================================


class TaskStatsResponse(BaseModel):
    """
    Task statistics for a patient or therapist

    Provides overview of task distribution and completion metrics.
    """

    model_config = ConfigDict(from_attributes=True)

    # Scope identifiers
    patient_id: Optional[UUID] = Field(None, description="Patient UUID (if patient stats)")
    therapist_id: Optional[UUID] = Field(None, description="Therapist UUID (if therapist stats)")

    # Status breakdown
    total_tasks: int = Field(..., description="Total tasks")
    todo_count: int = Field(..., description="TODO tasks")
    in_progress_count: int = Field(..., description="IN_PROGRESS tasks")
    done_count: int = Field(..., description="DONE tasks")
    cancelled_count: int = Field(..., description="CANCELLED tasks")

    # Priority breakdown
    critical_count: int = Field(0, description="CRITICAL priority tasks")
    high_count: int = Field(0, description="HIGH priority tasks")
    medium_count: int = Field(0, description="MEDIUM priority tasks")
    low_count: int = Field(0, description="LOW priority tasks")

    # Overdue tasks
    overdue_count: int = Field(0, description="Overdue tasks")

    # Last activity
    last_task_date: Optional[datetime] = Field(None, description="Last task created date")
    last_task_title: Optional[str] = Field(None, description="Last task title")
