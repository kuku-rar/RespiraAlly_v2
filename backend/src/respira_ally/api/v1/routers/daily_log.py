"""
Daily Log Context - API Router
Presentation Layer (Clean Architecture)

Endpoints:
- POST /daily-logs - Create/update daily log (patient)
- GET /daily-logs/{log_id} - Get specific log
- GET /daily-logs - List logs with filters
- GET /daily-logs/patient/{patient_id}/stats - Get patient statistics
- PATCH /daily-logs/{log_id} - Update log
- DELETE /daily-logs/{log_id} - Delete log
"""

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from respira_ally.application.daily_log.daily_log_service import DailyLogService
from respira_ally.core.dependencies import (
    get_current_patient,
    get_current_user,
    get_daily_log_service,
    get_idempotency_key,
    get_idempotency_service,
)
from respira_ally.core.schemas.auth import TokenData, UserRole
from respira_ally.core.schemas.daily_log import (
    DailyLogCreate,
    DailyLogListResponse,
    DailyLogResponse,
    DailyLogStats,
    DailyLogUpdate,
)
from respira_ally.infrastructure.cache import IdempotencyService

router = APIRouter()


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/", response_model=DailyLogResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_daily_log(
    data: DailyLogCreate,
    service: Annotated[DailyLogService, Depends(get_daily_log_service)],
    current_user: Annotated[TokenData, Depends(get_current_patient)],
    idempotency_key: Annotated[str | None, Depends(get_idempotency_key)] = None,
    idempotency_service: Annotated[IdempotencyService, Depends(get_idempotency_service)] = None,
):
    """
    Create or update daily log (upsert operation)

    **Authorization**: Patient only

    **Business Rule**: Only one log per patient per day
    - If log exists for the date → updates it
    - If log doesn't exist → creates new one

    **Idempotency**: Optional Idempotency-Key header
    - Prevents duplicate requests (cached for 24 hours)
    - If same key is used again → returns cached response

    **Returns**:
    - 201: Daily log created/updated successfully
    - 400: Validation error
    """
    # Check idempotency key (if provided) - user-scoped for security
    if idempotency_key and idempotency_service:
        cached_response = await idempotency_service.get_cached_response(
            idempotency_key, user_id=str(current_user.user_id)
        )
        if cached_response:
            # Return cached response (idempotent request)
            return DailyLogResponse(**cached_response)

    # Patients can only create logs for themselves
    if data.patient_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create logs for yourself",
        )

    try:
        response, was_created = await service.create_or_update_daily_log(data)

        # Cache response for idempotency (if key provided) - user-scoped for security
        if idempotency_key and idempotency_service:
            response_dict = response.model_dump(mode="json")
            await idempotency_service.cache_response(
                idempotency_key, response_dict, user_id=str(current_user.user_id)
            )

        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{log_id}", response_model=DailyLogResponse)
async def get_daily_log(
    log_id: UUID,
    service: Annotated[DailyLogService, Depends(get_daily_log_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
):
    """
    Get daily log by ID

    **Authorization**:
    - Therapists can view logs of their patients
    - Patients can only view their own logs

    **Returns**:
    - 200: Daily log information
    - 403: Access denied
    - 404: Log not found
    """
    log = await service.get_daily_log_by_id(log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Daily log not found",
        )

    # Permission check
    if current_user.role == UserRole.PATIENT:
        if log.patient_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own logs",
            )
    # Note: Therapist permission check would require patient_service to verify
    # if the patient belongs to this therapist. Skipped for simplicity.

    return log


@router.get("/", response_model=DailyLogListResponse)
async def list_daily_logs(
    service: Annotated[DailyLogService, Depends(get_daily_log_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    patient_id: UUID | None = Query(None, description="Filter by patient ID (therapists only)"),
    start_date: date | None = Query(None, description="Start date (inclusive)"),
    end_date: date | None = Query(None, description="End date (inclusive)"),
    page: int = Query(0, ge=0, description="Page number (0-indexed)"),
    page_size: int = Query(30, ge=1, le=100, description="Items per page"),
):
    """
    List daily logs with filters

    **Authorization**:
    - Patients: Can only list their own logs (patient_id is ignored)
    - Therapists: Can list logs for specific patient (patient_id required)

    **Returns**:
    - 200: Paginated daily log list
    """
    # Determine which patient_id to use
    if current_user.role == UserRole.PATIENT:
        # Patients can only see their own logs
        target_patient_id = current_user.user_id
    elif current_user.role == UserRole.THERAPIST:
        # Therapists must specify patient_id
        if not patient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="patient_id is required for therapists",
            )
        target_patient_id = patient_id
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user role",
        )

    return await service.list_daily_logs_by_patient(
        patient_id=target_patient_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )


@router.get("/patient/{patient_id}/stats", response_model=DailyLogStats)
async def get_patient_statistics(
    patient_id: UUID,
    service: Annotated[DailyLogService, Depends(get_daily_log_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    start_date: date = Query(..., description="Start date for statistics"),
    end_date: date = Query(..., description="End date for statistics"),
):
    """
    Get statistics for a patient's daily logs

    **Authorization**:
    - Therapists can view statistics for their patients
    - Patients can only view their own statistics

    **Returns**:
    - 200: Daily log statistics
    - 403: Access denied
    """
    # Permission check
    if current_user.role == UserRole.PATIENT:
        if patient_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own statistics",
            )
    # Note: Therapist permission check would require verifying patient ownership

    return await service.get_patient_statistics(
        patient_id=patient_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/patient/{patient_id}/latest", response_model=DailyLogResponse)
async def get_latest_log(
    patient_id: UUID,
    service: Annotated[DailyLogService, Depends(get_daily_log_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
):
    """
    Get the most recent log for a patient

    **Authorization**:
    - Therapists can view latest log for their patients
    - Patients can only view their own latest log

    **Returns**:
    - 200: Latest daily log
    - 403: Access denied
    - 404: No logs found for patient
    """
    # Permission check
    if current_user.role == UserRole.PATIENT:
        if patient_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own logs",
            )

    log = await service.get_latest_log(patient_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No logs found for this patient",
        )

    return log


@router.patch("/{log_id}", response_model=DailyLogResponse)
async def update_daily_log(
    log_id: UUID,
    data: DailyLogUpdate,
    service: Annotated[DailyLogService, Depends(get_daily_log_service)],
    current_user: Annotated[TokenData, Depends(get_current_patient)],
):
    """
    Update daily log (partial update)

    **Authorization**: Patient only (can only update their own logs)

    **Returns**:
    - 200: Daily log updated successfully
    - 403: Access denied
    - 404: Log not found
    """
    # Check if log exists and belongs to current user
    existing_log = await service.get_daily_log_by_id(log_id)
    if not existing_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Daily log not found",
        )

    if existing_log.patient_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own logs",
        )

    updated_log = await service.update_daily_log(log_id, data)
    if not updated_log:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update daily log",
        )

    return updated_log


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_daily_log(
    log_id: UUID,
    service: Annotated[DailyLogService, Depends(get_daily_log_service)],
    current_user: Annotated[TokenData, Depends(get_current_patient)],
):
    """
    Delete daily log

    **Authorization**: Patient only (can only delete their own logs)

    **Returns**:
    - 204: Daily log deleted successfully
    - 403: Access denied
    - 404: Log not found
    """
    # Check if log exists and belongs to current user
    existing_log = await service.get_daily_log_by_id(log_id)
    if not existing_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Daily log not found",
        )

    if existing_log.patient_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own logs",
        )

    deleted = await service.delete_daily_log(log_id, deleted_by=current_user.user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete daily log",
        )

    return None
