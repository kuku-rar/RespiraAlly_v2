"""
Patient Context - API Router
Presentation Layer (Clean Architecture)

Endpoints:
- POST /patients - Create new patient (therapist only)
- GET /patients/{user_id} - Get patient details
- GET /patients - List patients with pagination (therapist only)
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.core.dependencies import get_current_therapist, get_current_user
from respira_ally.core.schemas.auth import TokenData, UserRole
from respira_ally.core.schemas.patient import (
    PatientCreate,
    PatientListResponse,
    PatientResponse,
)
from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
from respira_ally.infrastructure.database.models.therapist_profile import (
    TherapistProfileModel,
)
from respira_ally.infrastructure.database.models.user import UserModel
from respira_ally.infrastructure.database.session import get_db

router = APIRouter()


# ============================================================================
# Helper Functions
# ============================================================================


def _calculate_age(birth_date) -> int:
    """Calculate age from birth date"""
    from datetime import date

    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def _calculate_bmi(weight_kg, height_cm) -> float | None:
    """Calculate BMI from weight and height"""
    if not weight_kg or not height_cm:
        return None
    height_m = height_cm / 100.0
    bmi = float(weight_kg) / (height_m * height_m)
    return round(bmi, 1)


def _enrich_patient_response(patient: PatientProfileModel) -> dict:
    """Add computed fields to patient response"""
    patient_dict = {
        "user_id": patient.user_id,
        "name": patient.name,
        "birth_date": patient.birth_date,
        "gender": patient.gender,
        "therapist_id": patient.therapist_id,
        "height_cm": patient.height_cm,
        "weight_kg": patient.weight_kg,
        "phone": patient.contact_info.get("phone") if patient.contact_info else None,
        "age": _calculate_age(patient.birth_date),
        "bmi": _calculate_bmi(patient.weight_kg, patient.height_cm),
    }
    return patient_dict


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    data: PatientCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_therapist)],
):
    """
    Create new patient profile

    **Authorization**: Therapist only

    **Workflow**:
    1. Verify therapist exists
    2. Create user account with PATIENT role
    3. Create patient profile linked to therapist
    4. Return patient information

    **Returns**:
    - 201: Patient created successfully
    - 404: Therapist not found
    - 409: Patient already exists (if user_id conflicts)
    """
    # 1. Verify therapist exists (check User with THERAPIST role)
    # TODO: Once TherapistProfile is created during registration, use TherapistProfileModel
    therapist_user = await db.get(UserModel, data.therapist_id)
    if not therapist_user or therapist_user.role != "THERAPIST":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Therapist not found"
        )

    # 2. Create user account for patient
    # Generate a temporary LINE user ID (will be replaced when patient logs in via LINE)
    import secrets

    temp_line_id = f"temp_{secrets.token_hex(8)}"

    new_user = UserModel(
        line_user_id=temp_line_id,
        role="PATIENT",
        email=None,  # Patients don't have email (use LINE)
        hashed_password=None,  # No password for LINE users
    )
    db.add(new_user)
    await db.flush()  # Get user_id

    # 3. Create patient profile
    contact_info = {}
    if data.phone:
        contact_info["phone"] = data.phone

    new_patient = PatientProfileModel(
        user_id=new_user.user_id,
        therapist_id=data.therapist_id,
        name=data.name,
        birth_date=data.birth_date,
        gender=data.gender,
        height_cm=data.height_cm,
        weight_kg=data.weight_kg,
        contact_info=contact_info,
        medical_history={},  # Empty for now
    )
    db.add(new_patient)
    await db.commit()
    await db.refresh(new_patient)

    # 4. Return enriched response
    return PatientResponse(**_enrich_patient_response(new_patient))


@router.get("/{user_id}", response_model=PatientResponse)
async def get_patient(
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
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
    # Fetch patient
    patient = await db.get(PatientProfileModel, user_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )

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

    return PatientResponse(**_enrich_patient_response(patient))


@router.get("/", response_model=PatientListResponse)
async def list_patients(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_therapist)],
    page: int = Query(0, ge=0, description="Page number (0-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    List patients assigned to current therapist

    **Authorization**: Therapist only

    **Pagination**:
    - `page`: Page number (0-indexed)
    - `page_size`: Number of items per page (1-100, default 20)

    **Returns**:
    - 200: Paginated patient list
    """
    # Build query for therapist's patients
    base_query = select(PatientProfileModel).where(
        PatientProfileModel.therapist_id == current_user.user_id
    )

    # Get total count
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    offset = page * page_size
    query = base_query.offset(offset).limit(page_size).order_by(PatientProfileModel.name)

    result = await db.execute(query)
    patients = result.scalars().all()

    # Enrich patient responses
    items = [PatientResponse(**_enrich_patient_response(p)) for p in patients]

    return PatientListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_next=(offset + len(items)) < total,
    )
