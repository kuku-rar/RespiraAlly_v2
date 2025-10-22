"""
Survey Application Service
Application Layer - Clean Architecture

This service orchestrates survey-related use cases (CAT and mMRC) and business logic.
It uses Repository pattern for data access and encapsulates complex workflows.
"""
import logging
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from respira_ally.application.survey.use_cases.submit_cat_survey_use_case import (
    SubmitCATSurveyUseCase,
)
from respira_ally.application.survey.use_cases.submit_mmrc_survey_use_case import (
    SubmitMmrcSurveyUseCase,
)
from respira_ally.core.schemas.survey import (
    CATSurveyAnswers,
    mMRCSurveyAnswers,
    SurveyResponse,
    SurveyListResponse,
    SurveyStats,
)
from respira_ally.domain.repositories.patient_repository import PatientRepository
from respira_ally.domain.repositories.survey_repository import SurveyRepository
from respira_ally.infrastructure.database.models.survey_response import SurveyResponseModel

logger = logging.getLogger(__name__)


class SurveyService:
    """
    Survey Application Service

    Responsibilities:
    - Orchestrate CAT and mMRC survey submissions
    - Retrieve survey history and statistics
    - Calculate trends and analytics
    - Coordinate with event publishing (future)
    """

    def __init__(
        self,
        survey_repository: SurveyRepository,
        patient_repository: PatientRepository,
    ):
        """
        Initialize service with repositories

        Args:
            survey_repository: Implementation of SurveyRepository interface
            patient_repository: Implementation of PatientRepository interface
        """
        self.survey_repo = survey_repository
        self.patient_repo = patient_repository

        # Initialize use cases
        self.submit_cat_use_case = SubmitCATSurveyUseCase(
            survey_repository=survey_repository,
            patient_repository=patient_repository,
        )
        self.submit_mmrc_use_case = SubmitMmrcSurveyUseCase(
            survey_repository=survey_repository,
            patient_repository=patient_repository,
        )

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def to_response(self, survey: SurveyResponseModel) -> SurveyResponse:
        """
        Convert SurveyResponseModel to SurveyResponse

        Args:
            survey: SurveyResponseModel from database

        Returns:
            SurveyResponse
        """
        return SurveyResponse(
            response_id=survey.response_id,
            survey_type=survey.survey_type,
            patient_id=survey.patient_id,
            answers=survey.answers,
            total_score=survey.total_score,
            severity_level=survey.severity_level,
            submitted_at=survey.submitted_at,
        )

    # ========================================================================
    # Submit Operations
    # ========================================================================

    async def submit_cat_survey(
        self, patient_id: UUID, answers: CATSurveyAnswers
    ) -> SurveyResponse:
        """
        Submit a CAT survey

        Args:
            patient_id: Patient's user ID
            answers: CAT survey answers

        Returns:
            SurveyResponse with calculated score and severity
        """
        return await self.submit_cat_use_case.execute(patient_id, answers)

    async def submit_mmrc_survey(
        self, patient_id: UUID, answers: mMRCSurveyAnswers
    ) -> SurveyResponse:
        """
        Submit an mMRC survey

        Args:
            patient_id: Patient's user ID
            answers: mMRC survey answers

        Returns:
            SurveyResponse with validated grade and severity
        """
        return await self.submit_mmrc_use_case.execute(patient_id, answers)

    # ========================================================================
    # Read Operations
    # ========================================================================

    async def get_survey_by_id(self, response_id: UUID) -> Optional[SurveyResponse]:
        """
        Get a survey response by ID

        Args:
            response_id: Survey response ID

        Returns:
            SurveyResponse if found, None otherwise
        """
        survey = await self.survey_repo.get_by_id(response_id)
        return self.to_response(survey) if survey else None

    async def list_surveys(
        self,
        patient_id: UUID,
        survey_type: Optional[Literal["CAT", "mMRC"]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 0,
        page_size: int = 50,
    ) -> SurveyListResponse:
        """
        List survey responses for a patient

        Args:
            patient_id: Patient's user ID
            survey_type: Optional filter by survey type
            start_date: Optional start datetime
            end_date: Optional end datetime
            page: Page number (0-indexed)
            page_size: Items per page

        Returns:
            SurveyListResponse with paginated results
        """
        skip = page * page_size
        surveys, total = await self.survey_repo.list_by_patient(
            patient_id=patient_id,
            survey_type=survey_type,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=page_size,
        )

        items = [self.to_response(survey) for survey in surveys]
        has_next = (skip + len(items)) < total

        return SurveyListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_next=has_next,
        )

    async def get_latest_survey(
        self,
        patient_id: UUID,
        survey_type: Literal["CAT", "mMRC"],
    ) -> Optional[SurveyResponse]:
        """
        Get the latest survey response for a patient and survey type

        Args:
            patient_id: Patient's user ID
            survey_type: Survey type

        Returns:
            Latest SurveyResponse if found, None otherwise
        """
        survey = await self.survey_repo.get_latest_by_patient_and_type(
            patient_id=patient_id,
            survey_type=survey_type,
        )
        return self.to_response(survey) if survey else None

    # ========================================================================
    # Statistics & Analytics
    # ========================================================================

    async def get_survey_stats(
        self,
        patient_id: UUID,
        survey_type: Literal["CAT", "mMRC"],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> SurveyStats:
        """
        Get survey statistics for a patient

        Args:
            patient_id: Patient's user ID
            survey_type: Survey type
            start_date: Optional start datetime
            end_date: Optional end datetime

        Returns:
            SurveyStats with analytics
        """
        # Get total responses count
        total_responses = await self.survey_repo.count_by_patient(
            patient_id=patient_id,
            survey_type=survey_type,
            start_date=start_date,
            end_date=end_date,
        )

        # Get latest survey
        latest_survey = await self.get_latest_survey(patient_id, survey_type)

        # Get average score
        avg_score = await self.survey_repo.get_average_score(
            patient_id=patient_id,
            survey_type=survey_type,
            start_date=start_date,
            end_date=end_date,
        )

        # Get score trend
        trend = await self.survey_repo.get_score_trend(
            patient_id=patient_id,
            survey_type=survey_type,
            days=30,
        )

        # Get date range
        surveys, _ = await self.survey_repo.list_by_patient(
            patient_id=patient_id,
            survey_type=survey_type,
            start_date=start_date,
            end_date=end_date,
            skip=0,
            limit=1000,  # Get all for date range calculation
        )

        date_range = {}
        if surveys:
            dates = [s.submitted_at for s in surveys]
            date_range = {
                "earliest": min(dates).isoformat(),
                "latest": max(dates).isoformat(),
            }

        return SurveyStats(
            survey_type=survey_type,
            total_responses=total_responses,
            latest_score=latest_survey.total_score if latest_survey else None,
            latest_severity=latest_survey.severity_level if latest_survey else None,
            avg_score=avg_score,
            trend=trend,
            date_range=date_range,
        )
