"""
Exacerbation Context - API Router
Presentation Layer (Clean Architecture)

Endpoints:
- POST /exacerbations - Create exacerbation record (therapist only)
- GET /exacerbations/{id} - Get exacerbation details
- GET /patients/{patient_id}/exacerbations - List patient exacerbations (with filters)
- GET /patients/{patient_id}/exacerbations/stats - Get exacerbation statistics
- PATCH /exacerbations/{id} - Update exacerbation record (therapist only)
- DELETE /exacerbations/{id} - Delete exacerbation record (therapist only)
"""

from datetime import date
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.application.exacerbation.exacerbation_service import ExacerbationService
from respira_ally.core.authorization import can_access_patient, can_modify_patient
from respira_ally.core.dependencies import get_current_therapist, get_current_user
from respira_ally.core.schemas.auth import TokenData, UserRole
from respira_ally.core.schemas.exacerbation import (
    ExacerbationCreate,
    ExacerbationListResponse,
    ExacerbationResponse,
    ExacerbationStats,
    ExacerbationUpdate,
)
from respira_ally.infrastructure.database.models.exacerbation import ExacerbationModel
from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
from respira_ally.infrastructure.database.session import get_db

router = APIRouter()


# ============================================================================
# Dependency: Exacerbation Service
# ============================================================================


def get_exacerbation_service(db: Annotated[AsyncSession, Depends(get_db)]) -> ExacerbationService:
    """Dependency: Get ExacerbationService instance"""
    return ExacerbationService(db)


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/", response_model=ExacerbationResponse, status_code=status.HTTP_201_CREATED)
async def create_exacerbation(
    data: ExacerbationCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    exacerbation_service: Annotated[ExacerbationService, Depends(get_exacerbation_service)],
    current_user: Annotated[TokenData, Depends(get_current_therapist)],
):
    """
    Create new exacerbation record

    **Authorization**: Therapist only

    **Workflow**:
    1. Verify therapist has permission to access this patient
    2. Create exacerbation record
    3. Auto-update patient_profiles summary fields (via database trigger)
    4. Return exacerbation details

    **Returns**:
    - 201: Exacerbation created successfully
    - 403: Access denied (not your patient)
    - 404: Patient not found
    """
    # Verify patient exists and therapist has permission
    patient = await db.get(PatientProfileModel, data.patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # Permission check using centralized authorization helper
    if not can_modify_patient(current_user, patient.therapist_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create exacerbation records for this patient",
        )

    # Create exacerbation record
    try:
        exacerbation = await exacerbation_service.create_exacerbation(
            data=data, recorded_by=current_user.user_id
        )
        return exacerbation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/{exacerbation_id}", response_model=ExacerbationResponse)
async def get_exacerbation(
    exacerbation_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    exacerbation_service: Annotated[ExacerbationService, Depends(get_exacerbation_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
):
    """
    Get exacerbation details by ID

    **Authorization**:
    - Therapists can view exacerbations for their own patients
    - Patients can view their own exacerbations

    **Returns**:
    - 200: Exacerbation details
    - 403: Access denied (not your exacerbation)
    - 404: Exacerbation not found
    """
    # Fetch exacerbation
    exacerbation_response = await exacerbation_service.get_exacerbation_by_id(exacerbation_id)
    if not exacerbation_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exacerbation not found"
        )

    # Verify patient exists for permission check
    patient = await db.get(PatientProfileModel, exacerbation_response.patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # Permission check using centralized authorization helper
    if not can_access_patient(
        current_user, exacerbation_response.patient_id, patient.therapist_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this exacerbation record",
        )

    return exacerbation_response


@router.get("/patients/{patient_id}/", response_model=ExacerbationListResponse)
async def list_patient_exacerbations(
    patient_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    exacerbation_service: Annotated[ExacerbationService, Depends(get_exacerbation_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    # Pagination
    page: int = Query(0, ge=0, description="Page number (0-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    # Filters
    start_date: date | None = Query(None, description="Filter by onset_date >= start_date"),
    end_date: date | None = Query(None, description="Filter by onset_date <= end_date"),
    severity: Literal["MILD", "MODERATE", "SEVERE"] | None = Query(
        None, description="Filter by severity"
    ),
):
    """
    List exacerbations for a patient with filters and pagination

    **Authorization**:
    - Therapists can view exacerbations for their own patients
    - Patients can view their own exacerbations

    **Filters**:
    - `start_date`: Filter by onset_date >= start_date (YYYY-MM-DD)
    - `end_date`: Filter by onset_date <= end_date (YYYY-MM-DD)
    - `severity`: Filter by severity (MILD, MODERATE, SEVERE)

    **Examples**:
    - Last 12 months: `?start_date=2024-01-01`
    - Severe exacerbations: `?severity=SEVERE`
    - Date range: `?start_date=2024-01-01&end_date=2024-12-31`

    **Returns**:
    - 200: Paginated exacerbation list with filters applied
    - 403: Access denied (not your patient)
    - 404: Patient not found
    """
    # Verify patient exists
    patient = await db.get(PatientProfileModel, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # Permission check using centralized authorization helper
    if not can_access_patient(current_user, patient_id, patient.therapist_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this patient's exacerbation records",
        )

    # List exacerbations with filters
    exacerbations = await exacerbation_service.list_patient_exacerbations(
        patient_id=patient_id,
        page=page,
        page_size=page_size,
        start_date=start_date,
        end_date=end_date,
        severity=severity,
    )

    return exacerbations


@router.get("/patients/{patient_id}/stats", response_model=ExacerbationStats)
async def get_exacerbation_stats(
    patient_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    exacerbation_service: Annotated[ExacerbationService, Depends(get_exacerbation_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
):
    """
    Get exacerbation statistics for a patient

    **Authorization**:
    - Therapists can view stats for their own patients
    - Patients can view their own stats

    **Returns**:
    - 200: Exacerbation statistics (total, last 12m, severity breakdown)
    - 403: Access denied (not your patient)
    - 404: Patient not found
    """
    # Verify patient exists
    patient = await db.get(PatientProfileModel, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # Permission check using centralized authorization helper
    if not can_access_patient(current_user, patient_id, patient.therapist_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this patient's exacerbation statistics",
        )

    # Get stats
    stats = await exacerbation_service.get_exacerbation_stats(patient_id)
    if not stats:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    return stats


@router.patch("/{exacerbation_id}", response_model=ExacerbationResponse)
async def update_exacerbation(
    exacerbation_id: UUID,
    data: ExacerbationUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    exacerbation_service: Annotated[ExacerbationService, Depends(get_exacerbation_service)],
    current_user: Annotated[TokenData, Depends(get_current_therapist)],
):
    """
    Update exacerbation record (partial update)

    **Authorization**: Therapist only (can only update records for their own patients)

    **Request Body**: All fields are optional (PATCH = partial update)

    **Returns**:
    - 200: Exacerbation updated successfully
    - 403: Access denied (not your patient)
    - 404: Exacerbation not found
    """
    # Fetch existing exacerbation
    existing = await exacerbation_service.get_exacerbation_by_id(exacerbation_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exacerbation not found"
        )

    # Verify patient exists and therapist has permission
    patient = await db.get(PatientProfileModel, existing.patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # Permission check using centralized authorization helper
    if not can_modify_patient(current_user, patient.therapist_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this exacerbation record",
        )

    # Update exacerbation
    updated = await exacerbation_service.update_exacerbation(exacerbation_id, data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update exacerbation",
        )

    return updated


@router.delete("/{exacerbation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exacerbation(
    exacerbation_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    exacerbation_service: Annotated[ExacerbationService, Depends(get_exacerbation_service)],
    current_user: Annotated[TokenData, Depends(get_current_therapist)],
):
    """
    Delete exacerbation record

    **Authorization**: Therapist only (can only delete records for their own patients)

    **Note**: Currently performs hard delete. Consider implementing soft delete for
    production (add deleted_at column).

    **Returns**:
    - 204: Exacerbation deleted successfully
    - 403: Access denied (not your patient)
    - 404: Exacerbation not found
    """
    # Fetch existing exacerbation
    existing = await exacerbation_service.get_exacerbation_by_id(exacerbation_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exacerbation not found"
        )

    # Verify patient exists and therapist has permission
    patient = await db.get(PatientProfileModel, existing.patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # Permission check using centralized authorization helper
    if not can_modify_patient(current_user, patient.therapist_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this exacerbation record",
        )

    # Delete exacerbation
    deleted = await exacerbation_service.delete_exacerbation(exacerbation_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete exacerbation",
        )

    # Return 204 No Content (no response body)
    return None
