"""
Survey Context - API Router
Presentation Layer (Clean Architecture)

Endpoints:
- POST /surveys/cat - Submit CAT survey (patient)
- POST /surveys/mmrc - Submit mMRC survey (patient)
- GET /surveys/{response_id} - Get specific survey response
- GET /surveys/patient/{patient_id} - List all surveys for a patient
- GET /surveys/cat/patient/{patient_id}/latest - Get latest CAT survey
- GET /surveys/mmrc/patient/{patient_id}/latest - Get latest mMRC survey
- GET /surveys/cat/patient/{patient_id}/stats - Get CAT statistics
- GET /surveys/mmrc/patient/{patient_id}/stats - Get mMRC statistics
"""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from respira_ally.application.survey.survey_service import SurveyService
from respira_ally.core.dependencies import (
    get_current_patient,
    get_current_user,
    get_survey_service,
)
from respira_ally.core.schemas.auth import TokenData, UserRole
from respira_ally.core.schemas.survey import (
    CATSurveyCreate,
    SurveyListResponse,
    SurveyResponse,
    SurveyStats,
    mMRCSurveyCreate,
)

router = APIRouter()


# ============================================================================
# Submit Survey Endpoints
# ============================================================================


@router.post("/cat", response_model=SurveyResponse, status_code=status.HTTP_201_CREATED)
async def submit_cat_survey(
    data: CATSurveyCreate,
    service: Annotated[SurveyService, Depends(get_survey_service)],
    current_user: Annotated[TokenData, Depends(get_current_patient)],
):
    """
    Submit CAT (COPD Assessment Test) survey

    **Authorization**: Patient only

    **CAT Survey**:
    - 8 questions, each scored 0-5
    - Total score: 0-40
    - Severity levels: MILD (0-10), MODERATE (11-20), SEVERE (21-30), VERY_SEVERE (31-40)

    **Returns**:
    - 201: Survey submitted successfully
    - 400: Validation error
    - 403: Forbidden (can only submit for yourself)
    - 404: Patient not found
    """
    # Patients can only submit surveys for themselves
    if data.patient_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit surveys for yourself",
        )

    try:
        response = await service.submit_cat_survey(
            patient_id=data.patient_id,
            answers=data.answers,
        )
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/mmrc", response_model=SurveyResponse, status_code=status.HTTP_201_CREATED)
async def submit_mmrc_survey(
    data: mMRCSurveyCreate,
    service: Annotated[SurveyService, Depends(get_survey_service)],
    current_user: Annotated[TokenData, Depends(get_current_patient)],
):
    """
    Submit mMRC (Modified Medical Research Council) dyspnea survey

    **Authorization**: Patient only

    **mMRC Survey**:
    - Single question, grade 0-4
    - Grade 0: Only breathless with strenuous exercise
    - Grade 1: Short of breath when hurrying/walking uphill
    - Grade 2: Walks slower than peers or stops for breath
    - Grade 3: Stops for breath after 100m or few minutes
    - Grade 4: Too breathless to leave house or when dressing

    **Returns**:
    - 201: Survey submitted successfully
    - 400: Validation error
    - 403: Forbidden (can only submit for yourself)
    - 404: Patient not found
    """
    # Patients can only submit surveys for themselves
    if data.patient_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit surveys for yourself",
        )

    try:
        response = await service.submit_mmrc_survey(
            patient_id=data.patient_id,
            answers=data.answers,
        )
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ============================================================================
# Read Survey Endpoints
# ============================================================================


@router.get("/{response_id}", response_model=SurveyResponse)
async def get_survey(
    response_id: UUID,
    service: Annotated[SurveyService, Depends(get_survey_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
):
    """
    Get survey response by ID

    **Authorization**:
    - Therapists can view surveys of their patients
    - Patients can only view their own surveys

    **Returns**:
    - 200: Survey response information
    - 403: Access denied
    - 404: Survey not found
    """
    survey = await service.get_survey_by_id(response_id)
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey response not found",
        )

    # Permission check
    if current_user.role == UserRole.PATIENT:
        if survey.patient_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own surveys",
            )
    # TODO: Therapist permission check (verify patient belongs to therapist)

    return survey


@router.get("/patient/{patient_id}", response_model=SurveyListResponse)
async def list_patient_surveys(
    patient_id: UUID,
    service: Annotated[SurveyService, Depends(get_survey_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    survey_type: Literal["CAT", "mMRC"] | None = Query(None, description="Filter by survey type"),
    start_date: datetime | None = Query(None, description="Start datetime (inclusive)"),
    end_date: datetime | None = Query(None, description="End datetime (inclusive)"),
    page: int = Query(0, ge=0, description="Page number (0-indexed)"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
):
    """
    List survey responses for a patient

    **Authorization**:
    - Patients can only list their own surveys (patient_id must match)
    - Therapists can list surveys for their patients

    **Query Parameters**:
    - survey_type: Filter by "CAT" or "mMRC" (optional)
    - start_date: Filter surveys after this date (optional)
    - end_date: Filter surveys before this date (optional)
    - page: Page number (0-indexed)
    - page_size: Items per page (1-100)

    **Returns**:
    - 200: Paginated list of surveys
    - 403: Access denied
    """
    # Permission check
    if current_user.role == UserRole.PATIENT:
        if patient_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own surveys",
            )
    # TODO: Therapist permission check

    return await service.list_surveys(
        patient_id=patient_id,
        survey_type=survey_type,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )


@router.get("/cat/patient/{patient_id}/latest", response_model=SurveyResponse | None)
async def get_latest_cat_survey(
    patient_id: UUID,
    service: Annotated[SurveyService, Depends(get_survey_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
):
    """
    Get the latest CAT survey for a patient

    **Authorization**:
    - Patients can only get their own latest survey
    - Therapists can get latest survey for their patients

    **Returns**:
    - 200: Latest CAT survey (or null if none exists)
    - 403: Access denied
    """
    # Permission check
    if current_user.role == UserRole.PATIENT:
        if patient_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own surveys",
            )

    return await service.get_latest_survey(patient_id=patient_id, survey_type="CAT")


@router.get("/mmrc/patient/{patient_id}/latest", response_model=SurveyResponse | None)
async def get_latest_mmrc_survey(
    patient_id: UUID,
    service: Annotated[SurveyService, Depends(get_survey_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
):
    """
    Get the latest mMRC survey for a patient

    **Authorization**:
    - Patients can only get their own latest survey
    - Therapists can get latest survey for their patients

    **Returns**:
    - 200: Latest mMRC survey (or null if none exists)
    - 403: Access denied
    """
    # Permission check
    if current_user.role == UserRole.PATIENT:
        if patient_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own surveys",
            )

    return await service.get_latest_survey(patient_id=patient_id, survey_type="mMRC")


# ============================================================================
# Statistics Endpoints
# ============================================================================


@router.get("/cat/patient/{patient_id}/stats", response_model=SurveyStats)
async def get_cat_survey_stats(
    patient_id: UUID,
    service: Annotated[SurveyService, Depends(get_survey_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    start_date: datetime | None = Query(None, description="Start datetime filter"),
    end_date: datetime | None = Query(None, description="End datetime filter"),
):
    """
    Get CAT survey statistics for a patient

    **Authorization**:
    - Patients can only get their own stats
    - Therapists can get stats for their patients

    **Statistics Include**:
    - Total number of responses
    - Latest score and severity level
    - Average score over time
    - Trend analysis (IMPROVING, STABLE, WORSENING, INSUFFICIENT_DATA)
    - Date range of responses

    **Returns**:
    - 200: Survey statistics
    - 403: Access denied
    """
    # Permission check
    if current_user.role == UserRole.PATIENT:
        if patient_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own statistics",
            )

    return await service.get_survey_stats(
        patient_id=patient_id,
        survey_type="CAT",
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/mmrc/patient/{patient_id}/stats", response_model=SurveyStats)
async def get_mmrc_survey_stats(
    patient_id: UUID,
    service: Annotated[SurveyService, Depends(get_survey_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    start_date: datetime | None = Query(None, description="Start datetime filter"),
    end_date: datetime | None = Query(None, description="End datetime filter"),
):
    """
    Get mMRC survey statistics for a patient

    **Authorization**:
    - Patients can only get their own stats
    - Therapists can get stats for their patients

    **Statistics Include**:
    - Total number of responses
    - Latest grade and severity level
    - Average grade over time
    - Trend analysis (IMPROVING, STABLE, WORSENING, INSUFFICIENT_DATA)
    - Date range of responses

    **Returns**:
    - 200: Survey statistics
    - 403: Access denied
    """
    # Permission check
    if current_user.role == UserRole.PATIENT:
        if patient_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own statistics",
            )

    return await service.get_survey_stats(
        patient_id=patient_id,
        survey_type="mMRC",
        start_date=start_date,
        end_date=end_date,
    )
