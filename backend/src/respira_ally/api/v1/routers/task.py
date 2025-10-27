"""
Task Context - API Router
Presentation Layer (Clean Architecture)

Sprint 5: Task Management System - Therapist action items and assignments

Endpoints:
- POST /tasks/ - Create new task (manual)
- GET /tasks/{id} - Get task details
- PATCH /tasks/{id} - Update task
- DELETE /tasks/{id} - Delete task
- POST /tasks/{id}/assign - Assign task to therapist
- POST /tasks/{id}/start - Start task execution
- POST /tasks/{id}/complete - Complete task
- POST /tasks/{id}/cancel - Cancel task
- GET /patients/{patient_id}/tasks - List patient tasks
- GET /therapists/{therapist_id}/tasks - List therapist tasks
- GET /alerts/{alert_id}/tasks - List alert-related tasks
- GET /tasks/overdue - List overdue tasks
- GET /patients/{patient_id}/tasks/stats - Patient task statistics
- GET /therapists/{therapist_id}/tasks/stats - Therapist task statistics
"""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.application.task.task_service import TaskService
from respira_ally.core.authorization import can_access_patient, require_role
from respira_ally.core.dependencies import get_current_user
from respira_ally.core.schemas.auth import TokenData
from respira_ally.core.schemas.task import (
    TaskAssignRequest,
    TaskCancelRequest,
    TaskCreateRequest,
    TaskListResponse,
    TaskPriority,
    TaskResponse,
    TaskStatsResponse,
    TaskStatus,
    TaskType,
    TaskUpdateRequest,
)
from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
from respira_ally.infrastructure.database.models.therapist_profile import TherapistProfileModel
from respira_ally.infrastructure.database.session import get_db

router = APIRouter()


# ============================================================================
# Dependency: Task Service
# ============================================================================


def get_task_service(db: Annotated[AsyncSession, Depends(get_db)]) -> TaskService:
    """Dependency: Get TaskService instance"""
    return TaskService(db)


# ============================================================================
# CRUD Endpoints
# ============================================================================


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: TaskCreateRequest,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Create a new task (manual creation by therapist)

    **Authorization**: THERAPIST role required

    **Request Body**: TaskCreateRequest
    - patient_id: Patient UUID
    - title: Task title (1-200 chars)
    - priority: CRITICAL | HIGH | MEDIUM | LOW
    - task_type: MANUAL | SCHEDULED (defaults to MANUAL)
    - description: Optional task description
    - assigned_to: Optional therapist UUID
    - related_alert_id: Optional related alert UUID
    - due_date: Optional due date (ISO 8601)
    - task_metadata: Optional additional context

    **Returns**:
    - 201: Task created successfully
    - 403: Access denied (not a therapist or cannot access patient)
    - 404: Patient not found
    """
    # Verify THERAPIST role
    require_role(current_user, "THERAPIST")

    # Verify patient exists and therapist has access
    patient = await db.get(PatientProfileModel, request.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    if not can_access_patient(current_user, patient.user_id, patient.therapist_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create tasks for this patient",
        )

    # Create task
    task = await task_service.create_task(
        patient_id=request.patient_id,
        title=request.title,
        priority=request.priority,
        task_type=request.task_type,
        description=request.description,
        assigned_to=request.assigned_to,
        related_alert_id=request.related_alert_id,
        due_date=request.due_date,
        task_metadata=request.task_metadata,
        created_by=current_user.sub,
    )

    return task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(
    task_id: UUID,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get task details by ID

    **Authorization**: User must have permission to access the task's patient

    **Returns**:
    - 200: Task details
    - 403: Access denied (not your patient)
    - 404: Task not found
    """
    # Get task
    task = await task_service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Verify user has permission to access this patient's data
    patient = await db.get(PatientProfileModel, task.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    if not can_access_patient(current_user, patient.user_id, patient.therapist_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this task",
        )

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    request: TaskUpdateRequest,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Update task details (partial update)

    **Authorization**: THERAPIST role required, must have access to patient

    **Request Body**: TaskUpdateRequest (all fields optional)
    - title: New task title
    - description: New description
    - priority: New priority
    - assigned_to: Reassign to different therapist
    - due_date: New due date
    - task_metadata: New metadata

    **Note**: Use dedicated endpoints for status transitions (/start, /complete, /cancel)

    **Returns**:
    - 200: Task updated successfully
    - 403: Access denied (not a therapist or cannot access patient)
    - 404: Task not found
    """
    # Verify THERAPIST role
    require_role(current_user, "THERAPIST")

    # Get task to verify access
    task = await task_service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Verify patient access
    patient = await db.get(PatientProfileModel, task.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    if not can_access_patient(current_user, patient.user_id, patient.therapist_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this task",
        )

    # Update task
    updated_task = await task_service.update_task(
        task_id=task_id,
        title=request.title,
        description=request.description,
        priority=request.priority,
        assigned_to=request.assigned_to,
        due_date=request.due_date,
        task_metadata=request.task_metadata,
    )

    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Delete a task

    **Authorization**: THERAPIST role required, must have access to patient

    **Returns**:
    - 204: Task deleted successfully
    - 403: Access denied (not a therapist or cannot access patient)
    - 404: Task not found
    """
    # Verify THERAPIST role
    require_role(current_user, "THERAPIST")

    # Get task to verify access
    task = await task_service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Verify patient access
    patient = await db.get(PatientProfileModel, task.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    if not can_access_patient(current_user, patient.user_id, patient.therapist_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this task",
        )

    # Delete task
    await task_service.delete_task(task_id)

    return None


# ============================================================================
# Task State Transition Endpoints
# ============================================================================


@router.post("/{task_id}/assign", response_model=TaskResponse)
async def assign_task(
    task_id: UUID,
    request: TaskAssignRequest,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Assign task to a therapist

    **Authorization**: THERAPIST role required

    **Business Rules**:
    - Cannot assign completed or cancelled tasks
    - Auto-updates status to IN_PROGRESS if currently TODO

    **Returns**:
    - 200: Task assigned successfully
    - 400: Invalid state transition (task is DONE or CANCELLED)
    - 403: Access denied
    - 404: Task or therapist not found
    """
    # Verify THERAPIST role
    require_role(current_user, "THERAPIST")

    # Get task
    task = await task_service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Verify therapist exists
    therapist = await db.get(TherapistProfileModel, request.therapist_id)
    if not therapist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Therapist not found",
        )

    # Assign task
    try:
        updated_task = await task_service.assign_task(task_id, request.therapist_id)
        return updated_task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{task_id}/start", response_model=TaskResponse)
async def start_task(
    task_id: UUID,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Start task execution

    **Authorization**: User must be the assigned therapist or have patient access

    **Business Rules**:
    - Can only start TODO tasks
    - Auto-updates status to IN_PROGRESS

    **Returns**:
    - 200: Task started successfully
    - 400: Invalid state transition (task is not TODO)
    - 403: Access denied
    - 404: Task not found
    """
    # Get task
    task = await task_service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Verify authorization
    patient = await db.get(PatientProfileModel, task.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    if not can_access_patient(current_user, patient.user_id, patient.therapist_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to start this task",
        )

    # Start task
    try:
        updated_task = await task_service.start_task(task_id)
        return updated_task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: UUID,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Complete task execution

    **Authorization**: User must be the assigned therapist or have patient access

    **Business Rules**:
    - Can only complete IN_PROGRESS tasks
    - Sets completed_at timestamp
    - Updates status to DONE

    **Returns**:
    - 200: Task completed successfully
    - 400: Invalid state transition (task is not IN_PROGRESS)
    - 403: Access denied
    - 404: Task not found
    """
    # Get task
    task = await task_service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Verify authorization
    patient = await db.get(PatientProfileModel, task.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    if not can_access_patient(current_user, patient.user_id, patient.therapist_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to complete this task",
        )

    # Complete task
    try:
        updated_task = await task_service.complete_task(task_id)
        return updated_task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{task_id}/cancel", response_model=TaskResponse)
async def cancel_task(
    task_id: UUID,
    request: TaskCancelRequest,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Cancel task

    **Authorization**: THERAPIST role required

    **Business Rules**:
    - Can only cancel TODO or IN_PROGRESS tasks
    - Cannot cancel DONE tasks
    - Optionally store cancellation reason in metadata

    **Returns**:
    - 200: Task cancelled successfully
    - 400: Invalid state transition (task is DONE)
    - 403: Access denied
    - 404: Task not found
    """
    # Verify THERAPIST role
    require_role(current_user, "THERAPIST")

    # Get task
    task = await task_service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Verify authorization
    patient = await db.get(PatientProfileModel, task.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    if not can_access_patient(current_user, patient.user_id, patient.therapist_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to cancel this task",
        )

    # Cancel task
    try:
        updated_task = await task_service.cancel_task(task_id, request.reason)
        return updated_task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ============================================================================
# Query Endpoints
# ============================================================================


@router.get("/patients/{patient_id}/", response_model=TaskListResponse)
async def list_patient_tasks(
    patient_id: UUID,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    # Pagination
    page: Annotated[int, Query(ge=0)] = 0,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    # Filters
    task_status: Annotated[Optional[TaskStatus], Query()] = None,
    priority: Annotated[Optional[TaskPriority], Query()] = None,
    task_type: Annotated[Optional[TaskType], Query()] = None,
):
    """
    List tasks for a specific patient with filters and pagination

    **Authorization**: User must have permission to access the patient

    **Query Parameters**:
    - `page`: Page number (0-indexed), default=0
    - `page_size`: Items per page (1-100), default=20
    - `task_status`: Filter by status (TODO, IN_PROGRESS, DONE, CANCELLED)
    - `priority`: Filter by priority (CRITICAL, HIGH, MEDIUM, LOW)
    - `task_type`: Filter by type (ALERT_TRIGGERED, MANUAL, SCHEDULED)

    **Returns**:
    - 200: Paginated task list
    - 403: Access denied (not your patient)
    - 404: Patient not found
    """
    # Verify patient exists and user has permission
    patient = await db.get(PatientProfileModel, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    if not can_access_patient(current_user, patient.user_id, patient.therapist_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this patient's tasks",
        )

    # Get tasks with filters
    tasks = await task_service.list_patient_tasks(
        patient_id=patient_id,
        page=page,
        page_size=page_size,
        status=task_status,
        priority=priority,
        task_type=task_type,
    )

    return tasks


@router.get("/therapists/{therapist_id}/", response_model=TaskListResponse)
async def list_therapist_tasks(
    therapist_id: UUID,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    # Pagination
    page: Annotated[int, Query(ge=0)] = 0,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    # Filters
    task_status: Annotated[Optional[TaskStatus], Query()] = None,
    priority: Annotated[Optional[TaskPriority], Query()] = None,
):
    """
    List tasks assigned to a specific therapist with filters and pagination

    **Authorization**: THERAPIST role required, can only view own tasks

    **Query Parameters**:
    - `page`: Page number (0-indexed), default=0
    - `page_size`: Items per page (1-100), default=20
    - `task_status`: Filter by status (TODO, IN_PROGRESS, DONE, CANCELLED)
    - `priority`: Filter by priority (CRITICAL, HIGH, MEDIUM, LOW)

    **Returns**:
    - 200: Paginated task list
    - 403: Access denied (not your tasks)
    - 404: Therapist not found
    """
    # Verify THERAPIST role
    require_role(current_user, "THERAPIST")

    # Verify therapist exists
    therapist = await db.get(TherapistProfileModel, therapist_id)
    if not therapist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Therapist not found",
        )

    # Verify accessing own tasks
    if str(therapist_id) != current_user.sub:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own tasks",
        )

    # Get tasks with filters
    tasks = await task_service.list_therapist_tasks(
        therapist_id=therapist_id,
        page=page,
        page_size=page_size,
        status=task_status,
        priority=priority,
    )

    return tasks


@router.get("/alerts/{alert_id}/", response_model=list[TaskResponse])
async def list_alert_tasks(
    alert_id: UUID,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
):
    """
    List all tasks related to a specific alert

    **Authorization**: User must have permission to access the alert's patient

    **Returns**:
    - 200: List of tasks
    - 403: Access denied
    - 404: Alert not found
    """
    # Get tasks
    tasks = await task_service.list_alert_tasks(alert_id)

    # TODO: Add authorization check via alert's patient

    return tasks


@router.get("/overdue/", response_model=list[TaskResponse])
async def list_overdue_tasks(
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    patient_id: Annotated[Optional[UUID], Query()] = None,
    therapist_id: Annotated[Optional[UUID], Query()] = None,
):
    """
    List overdue tasks (optional filtering by patient or therapist)

    **Authorization**: THERAPIST role required

    **Query Parameters**:
    - `patient_id`: Optional filter by patient
    - `therapist_id`: Optional filter by therapist

    **Returns**:
    - 200: List of overdue tasks
    - 403: Access denied
    """
    # Verify THERAPIST role
    require_role(current_user, "THERAPIST")

    # Get overdue tasks
    tasks = await task_service.get_overdue_tasks(
        patient_id=patient_id, therapist_id=therapist_id
    )

    return tasks


# ============================================================================
# Statistics Endpoints
# ============================================================================


@router.get("/patients/{patient_id}/stats", response_model=TaskStatsResponse)
async def get_patient_task_stats(
    patient_id: UUID,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get task statistics for a patient

    **Authorization**: User must have permission to access the patient

    **Returns**:
    - 200: Task statistics (status/priority breakdown, overdue count)
    - 403: Access denied
    - 404: Patient not found
    """
    # Verify patient exists and user has permission
    patient = await db.get(PatientProfileModel, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    if not can_access_patient(current_user, patient.user_id, patient.therapist_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this patient's task statistics",
        )

    # Get statistics
    stats = await task_service.get_patient_task_stats(patient_id)

    return stats


@router.get("/therapists/{therapist_id}/stats", response_model=TaskStatsResponse)
async def get_therapist_task_stats(
    therapist_id: UUID,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get task statistics for a therapist

    **Authorization**: THERAPIST role required, can only view own stats

    **Returns**:
    - 200: Task statistics (status/priority breakdown, overdue count)
    - 403: Access denied
    - 404: Therapist not found
    """
    # Verify THERAPIST role
    require_role(current_user, "THERAPIST")

    # Verify therapist exists
    therapist = await db.get(TherapistProfileModel, therapist_id)
    if not therapist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Therapist not found",
        )

    # Verify accessing own stats
    if str(therapist_id) != current_user.sub:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own task statistics",
        )

    # Get statistics
    stats = await task_service.get_therapist_task_stats(therapist_id)

    return stats
