"""
Patient Context - API Router
Presentation Layer (Clean Architecture)

Endpoints:
- POST /patients - Create new patient (therapist only)
- GET /patients/{user_id} - Get patient details
- GET /patients - List patients with pagination and filters (therapist only)
- PATCH /patients/{user_id} - Update patient information (therapist only)
- DELETE /patients/{user_id} - Delete patient (therapist only)
"""

import secrets
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.application.patient.patient_service import PatientService
from respira_ally.core.dependencies import (
    get_current_therapist,
    get_current_user,
    get_patient_service,
)
from respira_ally.core.schemas.auth import TokenData, UserRole
from respira_ally.core.schemas.patient import (
    PatientCreate,
    PatientListResponse,
    PatientResponse,
    PatientUpdate,
)
from respira_ally.infrastructure.database.models.user import UserModel
from respira_ally.infrastructure.database.session import get_db

router = APIRouter()


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    data: PatientCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    patient_service: Annotated[PatientService, Depends(get_patient_service)],
    current_user: Annotated[TokenData, Depends(get_current_therapist)],
):
    """
    Create new patient profile

    **Authorization**: Therapist only

    **Workflow**:
    1. Verify therapist exists
    2. Create user account with PATIENT role
    3. Create patient profile linked to therapist (via PatientService)
    4. Return patient information

    **Returns**:
    - 201: Patient created successfully
    - 404: Therapist not found
    - 409: Patient already exists (if user_id conflicts)
    """
    # 1. Verify therapist exists
    therapist_user = await db.get(UserModel, data.therapist_id)
    if not therapist_user or therapist_user.role != "THERAPIST":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Therapist not found")

    # 2. Create user account for patient
    temp_line_id = f"temp_{secrets.token_hex(8)}"

    new_user = UserModel(
        line_user_id=temp_line_id,
        role="PATIENT",
        email=None,  # Patients don't have email (use LINE)
        hashed_password=None,  # No password for LINE users
    )
    db.add(new_user)
    await db.flush()  # Get user_id

    # 3. Create patient profile using PatientService
    try:
        patient_response = await patient_service.create_patient(
            data=data,
            user_model=new_user,
        )
        await db.commit()  # Commit the user and patient
        return patient_response
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create patient: {str(e)}",
        ) from e


@router.get("/{user_id}", response_model=PatientResponse)
async def get_patient(
    user_id: UUID,
    patient_service: Annotated[PatientService, Depends(get_patient_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
):
    """
    Get patient details by user ID

    **Authorization**:
    - Therapists can view their own patients
    - Patients can only view themselves

    **Returns**:
    - 200: Patient information
    - 403: Access denied (not your patient)
    - 404: Patient not found
    """
    # Fetch patient using service
    patient = await patient_service.get_patient_by_id(user_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # Permission check
    if current_user.role == UserRole.THERAPIST:
        # Therapist can only view their own patients
        if patient.therapist_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own patients",
            )
    elif current_user.role == UserRole.PATIENT:
        # Patient can only view themselves
        if patient.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own profile",
            )

    return patient


@router.get("/", response_model=PatientListResponse)
async def list_patients(
    patient_service: Annotated[PatientService, Depends(get_patient_service)],
    current_user: Annotated[TokenData, Depends(get_current_therapist)],
    # Pagination
    page: int = Query(0, ge=0, description="Page number (0-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    # Filters
    search: str | None = Query(None, description="Search by name or phone (case-insensitive)"),
    gender: Literal["MALE", "FEMALE", "OTHER"] | None = Query(None, description="Filter by gender"),
    min_bmi: Decimal | None = Query(None, ge=0, le=100, description="Minimum BMI"),
    max_bmi: Decimal | None = Query(None, ge=0, le=100, description="Maximum BMI"),
    min_age: int | None = Query(None, ge=0, le=150, description="Minimum age"),
    max_age: int | None = Query(None, ge=0, le=150, description="Maximum age"),
    # Sorting
    sort_by: Literal["name", "birth_date", "bmi", "created_at"] | None = Query(
        "created_at", description="Sort field"
    ),
    sort_order: Literal["asc", "desc"] | None = Query("desc", description="Sort order"),
):
    """
    List patients assigned to current therapist with filters

    **Authorization**: Therapist only

    **Pagination**:
    - `page`: Page number (0-indexed)
    - `page_size`: Number of items per page (1-100, default 20)

    **Filters**:
    - `search`: Search by name or phone (case-insensitive partial match)
    - `gender`: Filter by gender (MALE, FEMALE, OTHER)
    - `min_bmi`, `max_bmi`: BMI range filter
    - `min_age`, `max_age`: Age range filter

    **Sorting**:
    - `sort_by`: Sort field (name, birth_date, bmi, created_at)
    - `sort_order`: Sort order (asc, desc)

    **Examples**:
    - Search: `?search=王`
    - Filter by BMI: `?min_bmi=18.5&max_bmi=24`
    - Filter by age: `?min_age=60&max_age=80`
    - Sort: `?sort_by=name&sort_order=asc`

    **Returns**:
    - 200: Paginated patient list with applied filters
    """
    # Use PatientService for listing with filters
    return await patient_service.list_patients_by_therapist(
        therapist_id=current_user.user_id,
        page=page,
        page_size=page_size,
        search=search,
        gender=gender,
        min_bmi=float(min_bmi) if min_bmi is not None else None,
        max_bmi=float(max_bmi) if max_bmi is not None else None,
        min_age=min_age,
        max_age=max_age,
        sort_by=sort_by or "created_at",
        sort_order=sort_order or "desc",
    )


@router.patch("/{user_id}", response_model=PatientResponse)
async def update_patient(
    user_id: UUID,
    data: PatientUpdate,
    patient_service: Annotated[PatientService, Depends(get_patient_service)],
    current_user: Annotated[TokenData, Depends(get_current_therapist)],
):
    """
    Update patient information (partial update)

    **Authorization**: Therapist only (can only update their own patients)

    **Request Body**: All fields are optional (PATCH = partial update)

    **Returns**:
    - 200: Patient updated successfully
    - 403: Access denied (not your patient)
    - 404: Patient not found
    """
    # Check if patient exists
    existing_patient = await patient_service.get_patient_by_id(user_id)
    if not existing_patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # Permission check: Therapist can only update their own patients
    if existing_patient.therapist_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own patients",
        )

    # Update using service
    updated_patient = await patient_service.update_patient(
        user_id=user_id,
        data=data,
    )

    if not updated_patient:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update patient",
        )

    return updated_patient


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    user_id: UUID,
    patient_service: Annotated[PatientService, Depends(get_patient_service)],
    current_user: Annotated[TokenData, Depends(get_current_therapist)],
):
    """
    Delete patient record

    **Authorization**: Therapist only (can only delete their own patients)

    **Note**: Currently performs hard delete. Consider implementing
    soft delete for production (add deleted_at column).

    **Returns**:
    - 204: Patient deleted successfully
    - 403: Access denied (not your patient)
    - 404: Patient not found
    """
    # Check if patient exists
    existing_patient = await patient_service.get_patient_by_id(user_id)
    if not existing_patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # Permission check: Therapist can only delete their own patients
    if existing_patient.therapist_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own patients",
        )

    # Delete using service
    deleted = await patient_service.delete_patient(user_id, deleted_by=current_user.user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete patient",
        )

    # Return 204 No Content (no response body)
    return None


# ============================================================================
# Sprint 4: KPI Endpoints
# ============================================================================


@router.get("/{patient_id}/kpis", response_model=PatientKPIResponse)
async def get_patient_kpi(
    patient_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    refresh: bool = Query(False, description="Force recalculate risk assessment"),
):
    """
    Get patient KPI metrics for dashboard

    **Authorization**:
    - Therapists can view their own patients' KPIs
    - Patients can only view their own KPIs

    **Sprint 4**: Returns GOLD ABE classification + backward-compatible legacy risk fields

    **Query Parameters**:
    - `refresh`: If True, force recalculate risk assessment (default: False)

    **Returns**:
    - 200: Patient KPI metrics (Hybrid: GOLD ABE + Legacy)
    - 403: Access denied (not your patient)
    - 404: Patient not found

    **Response includes**:
    - Adherence metrics (medication, logs, surveys)
    - Health vitals (BMI, SpO2, BP, HR)
    - Survey scores (CAT, mMRC)
    - GOLD ABE risk (gold_group, exacerbation counts)
    - Legacy risk (risk_score, risk_level) - backward compatible
    - Activity tracking (last log date, days since)
    """
    from respira_ally.application.patient.kpi_service import KPIService
    from respira_ally.core.schemas.kpi import PatientKPIResponse

    # Check patient exists
    patient = await db.get(PatientProfileModel, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # Permission check
    if current_user.role == UserRole.THERAPIST:
        # Therapist can only view their own patients
        if patient.therapist_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view KPIs for your own patients",
            )
    elif current_user.role == UserRole.PATIENT:
        # Patient can only view themselves
        if patient_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own KPIs",
            )

    # Get KPI metrics using service
    kpi_service = KPIService(db)
    try:
        kpi_metrics = await kpi_service.get_patient_kpi(patient_id, refresh=refresh)
        return kpi_metrics
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
