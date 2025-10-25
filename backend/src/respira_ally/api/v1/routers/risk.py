"""
Risk Context - API Router
Presentation Layer (Clean Architecture)

Sprint 4: GOLD ABE Risk Assessment API
Endpoints for calculating and retrieving COPD risk assessments
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.application.risk.use_cases.calculate_risk_use_case import CalculateRiskUseCase
from respira_ally.core.authorization import can_access_patient
from respira_ally.core.dependencies import get_current_user
from respira_ally.core.schemas.auth import TokenData
from respira_ally.application.risk.schemas.risk_schemas import (
    RiskAssessmentResponse,
    RiskAssessmentCalculateRequest,
)
from respira_ally.infrastructure.database.session import get_db

router = APIRouter()


# ============================================================================
# Dependencies
# ============================================================================


def get_risk_use_case(db: Annotated[AsyncSession, Depends(get_db)]) -> CalculateRiskUseCase:
    """Dependency: Get CalculateRiskUseCase instance"""
    return CalculateRiskUseCase(db_session=db)


# ============================================================================
# Endpoints
# ============================================================================


@router.post(
    "/assessments/calculate",
    response_model=RiskAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def calculate_risk_assessment(
    request: RiskAssessmentCalculateRequest,
    risk_use_case: Annotated[CalculateRiskUseCase, Depends(get_risk_use_case)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
):
    """
    Calculate GOLD ABE Risk Assessment

    **Authorization**:
    - Therapists can calculate for their patients
    - Patients can calculate for themselves

    **Workflow**:
    1. Verify patient exists
    2. Retrieve latest CAT and mMRC survey scores
    3. Retrieve exacerbation history from patient profile
    4. Classify into GOLD ABE group (A/B/E)
    5. Map to legacy risk score/level (backward compatibility)
    6. Save risk assessment record
    7. Return assessment result

    **Requirements**:
    - Patient must have completed CAT survey (0-40)
    - Patient must have completed mMRC survey (0-4)
    - Exacerbation history auto-retrieved from patient profile

    **GOLD ABE Classification**:
    - Group A: CAT<10 AND mMRC<2 (low risk) → risk_score=25, risk_level='low'
    - Group B: CAT>=10 OR mMRC>=2 (medium risk) → risk_score=50, risk_level='medium'
    - Group E: CAT>=10 AND mMRC>=2 (high risk) → risk_score=75, risk_level='high'

    **Returns**:
    - 201: Risk assessment created successfully
    - 400: Missing required survey data (CAT or mMRC)
    - 403: Access denied (not your patient)
    - 404: Patient not found

    **Example Request**:
    ```json
    {
      "patient_id": "550e8400-e29b-41d4-a716-446655440000"
    }
    ```

    **Example Response**:
    ```json
    {
      "assessment_id": "660e8400-e29b-41d4-a716-446655440001",
      "patient_id": "550e8400-e29b-41d4-a716-446655440000",
      "cat_score": 15,
      "mmrc_grade": 2,
      "exacerbation_count_12m": 1,
      "hospitalization_count_12m": 0,
      "gold_group": "E",
      "risk_score": 75,
      "risk_level": "high",
      "assessed_at": "2025-10-26T10:30:00Z",
      "created_at": "2025-10-26T10:30:00Z"
    }
    ```
    """
    patient_id = request.patient_id

    # Permission check: Only patient themselves or their therapist can calculate risk
    # Note: can_access_patient() will check if current_user is the patient or their therapist
    # We'll retrieve patient data from risk_use_case.execute() which will validate patient exists
    # For now, we'll rely on the use case to validate patient existence
    # After retrieving the assessment, we'll check permissions

    try:
        # Execute risk calculation (validates patient, surveys, etc.)
        assessment = await risk_use_case.execute(patient_id)

        # Permission check after assessment (we now know patient exists and have therapist_id)
        # Note: The assessment.patient relationship contains therapist_id
        if not can_access_patient(
            current_user, patient_id, assessment.patient.therapist_id if assessment.patient else None
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to calculate risk for this patient",
            )

        return assessment

    except ValueError as e:
        # Handle missing patient or survey data errors
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg,
            ) from e
        elif "no CAT" in error_msg or "no mMRC" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            ) from e
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Risk calculation failed: {error_msg}",
            ) from e


@router.get(
    "/patients/{patient_id}",
    response_model=RiskAssessmentResponse,
)
async def get_latest_risk_assessment(
    patient_id: UUID,
    risk_use_case: Annotated[CalculateRiskUseCase, Depends(get_risk_use_case)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
):
    """
    Get Latest Risk Assessment for Patient

    **Authorization**:
    - Therapists can view their patients' risk assessments
    - Patients can view their own risk assessment

    **Returns**:
    - 200: Latest risk assessment
    - 403: Access denied (not your patient)
    - 404: Patient not found or no assessment exists

    **Response Fields**:
    - `gold_group`: GOLD ABE group (A, B, E)
    - `risk_level`: Mapped risk level (low, medium, high)
    - `risk_score`: Mapped risk score (25, 50, 75)
    - `cat_score`: CAT score used in assessment
    - `mmrc_grade`: mMRC grade used in assessment
    - `exacerbation_count_12m`: Exacerbations in last 12 months
    - `hospitalization_count_12m`: Hospitalizations in last 12 months
    - `assessed_at`: Assessment timestamp (UTC)

    **Example Response**:
    ```json
    {
      "assessment_id": "660e8400-e29b-41d4-a716-446655440001",
      "patient_id": "550e8400-e29b-41d4-a716-446655440000",
      "cat_score": 15,
      "mmrc_grade": 2,
      "exacerbation_count_12m": 1,
      "hospitalization_count_12m": 0,
      "gold_group": "E",
      "risk_score": 75,
      "risk_level": "high",
      "assessed_at": "2025-10-26T10:30:00Z",
      "created_at": "2025-10-26T10:30:00Z"
    }
    ```
    """
    # Retrieve latest risk assessment
    assessment = await risk_use_case.get_latest_assessment(patient_id)

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No risk assessment found for patient {patient_id}",
        )

    # Permission check
    if not can_access_patient(
        current_user, patient_id, assessment.patient.therapist_id if assessment.patient else None
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this patient's risk assessment",
        )

    return assessment
