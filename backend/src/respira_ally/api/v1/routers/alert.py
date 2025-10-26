"""
Alert Context - API Router
Presentation Layer (Clean Architecture)

Sprint 4: Alert System MVP - Read-only API

Endpoints (MVP):
- GET /alerts/{id} - Get alert details
- GET /patients/{patient_id}/alerts - List patient alerts (with filters)
- GET /patients/{patient_id}/alerts/active/count - Count active alerts

TODO(DEBT-001): MVP is read-only. Alerts are created automatically by risk assessment engine.
No POST /alerts endpoint in MVP.

Full Implementation (Future):
- POST /alerts/{id}/acknowledge - Mark alert as acknowledged
- POST /alerts/{id}/resolve - Resolve alert with notes
- GET /alerts/stats - Alert analytics dashboard
"""

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.application.alert.alert_service import AlertService
from respira_ally.core.authorization import can_access_patient
from respira_ally.core.dependencies import get_current_user
from respira_ally.core.schemas.alert import AlertListResponse, AlertResponse
from respira_ally.core.schemas.auth import TokenData
from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
from respira_ally.infrastructure.database.session import get_db

router = APIRouter()


# ============================================================================
# Dependency: Alert Service
# ============================================================================


def get_alert_service(db: Annotated[AsyncSession, Depends(get_db)]) -> AlertService:
    """Dependency: Get AlertService instance"""
    return AlertService(db)


# ============================================================================
# Endpoints
# ============================================================================


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert_by_id(
    alert_id: UUID,
    alert_service: Annotated[AlertService, Depends(get_alert_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get alert details by ID

    **Authorization**: User must have permission to access the patient

    **Returns**:
    - 200: Alert details
    - 403: Access denied (not your patient)
    - 404: Alert not found
    """
    # Get alert
    alert = await alert_service.get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    # Verify user has permission to access this patient's data
    patient = await db.get(PatientProfileModel, alert.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    if not can_access_patient(current_user, patient.user_id, patient.therapist_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this alert",
        )

    return alert


@router.get("/patients/{patient_id}/", response_model=AlertListResponse)
async def list_patient_alerts(
    patient_id: UUID,
    alert_service: Annotated[AlertService, Depends(get_alert_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    # Pagination
    page: Annotated[int, Query(ge=0)] = 0,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    # Filters
    alert_type: Annotated[str | None, Query()] = None,
    severity: Annotated[str | None, Query()] = None,
    alert_status: Annotated[str | None, Query()] = None,
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    # Sorting
    sort_by: Annotated[str, Query()] = "triggered_at",
    sort_order: Annotated[str, Query(pattern="^(asc|desc)$")] = "desc",
):
    """
    List alerts for a specific patient with filters and pagination

    **Authorization**: User must have permission to access the patient

    **Query Parameters**:
    - `page`: Page number (0-indexed), default=0
    - `page_size`: Items per page (1-100), default=20
    - `alert_type`: Filter by alert type (RISK_GROUP_CHANGE, HIGH_RISK_DETECTED, EXACERBATION_RISK)
    - `severity`: Filter by severity (LOW, MEDIUM, HIGH, CRITICAL)
    - `alert_status`: Filter by status (ACTIVE, ACKNOWLEDGED, RESOLVED)
    - `start_date`: Filter by triggered_at >= start_date (YYYY-MM-DD)
    - `end_date`: Filter by triggered_at <= end_date (YYYY-MM-DD)
    - `sort_by`: Sort field (triggered_at, severity, created_at), default=triggered_at
    - `sort_order`: Sort order (asc, desc), default=desc

    **Returns**:
    - 200: Paginated alert list
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
            detail="You do not have permission to access this patient's alerts",
        )

    # Get alerts with filters
    alerts = await alert_service.list_patient_alerts(
        patient_id=patient_id,
        page=page,
        page_size=page_size,
        alert_type=alert_type,
        severity=severity,
        status=alert_status,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return alerts


@router.get("/patients/{patient_id}/active/count", response_model=int)
async def count_active_alerts(
    patient_id: UUID,
    alert_service: Annotated[AlertService, Depends(get_alert_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Count active alerts for a patient

    **Authorization**: User must have permission to access the patient

    **Use Case**: Dashboard badge - "You have 3 active alerts"

    **Returns**:
    - 200: Number of active alerts (integer)
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
            detail="You do not have permission to access this patient's data",
        )

    # Get active alert count
    count = await alert_service.count_active_alerts(patient_id)
    return count
