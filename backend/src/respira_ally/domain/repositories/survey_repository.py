"""
Survey Repository Interface
Domain Layer - Clean Architecture

This is the abstract repository interface that defines the contract
for survey response data operations (CAT and mMRC surveys).
The actual implementation is in the Infrastructure Layer.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Literal
from uuid import UUID

from respira_ally.infrastructure.database.models.survey_response import SurveyResponseModel


class SurveyRepository(ABC):
    """
    Abstract base class for Survey Response data access

    This interface defines all data operations for Survey entities (CAT and mMRC).
    Following the Dependency Inversion Principle, the Domain Layer
    defines the interface, and the Infrastructure Layer implements it.
    """

    @abstractmethod
    async def create(self, survey_response: SurveyResponseModel) -> SurveyResponseModel:
        """
        Create a new survey response record

        Args:
            survey_response: SurveyResponseModel instance to persist

        Returns:
            SurveyResponseModel: The created survey response with database-generated fields

        Raises:
            IntegrityError: If database constraints are violated
        """
        pass

    @abstractmethod
    async def get_by_id(self, response_id: UUID) -> SurveyResponseModel | None:
        """
        Retrieve survey response by response ID

        Args:
            response_id: Survey response ID (primary key)

        Returns:
            SurveyResponseModel if found, None otherwise
        """
        pass

    @abstractmethod
    async def list_by_patient(
        self,
        patient_id: UUID,
        survey_type: Literal["CAT", "mMRC"] | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[SurveyResponseModel], int]:
        """
        List survey responses for a specific patient

        Args:
            patient_id: Patient's user ID
            survey_type: Optional filter by survey type ("CAT" or "mMRC")
            start_date: Optional start datetime (inclusive)
            end_date: Optional end datetime (inclusive)
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of survey responses, total count)
        """
        pass

    @abstractmethod
    async def get_latest_by_patient_and_type(
        self,
        patient_id: UUID,
        survey_type: Literal["CAT", "mMRC"],
    ) -> SurveyResponseModel | None:
        """
        Get the most recent survey response for a patient and survey type

        Args:
            patient_id: Patient's user ID
            survey_type: Survey type ("CAT" or "mMRC")

        Returns:
            Latest SurveyResponseModel if found, None otherwise
        """
        pass

    @abstractmethod
    async def count_by_patient(
        self,
        patient_id: UUID,
        survey_type: Literal["CAT", "mMRC"] | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        """
        Count survey responses for a patient

        Args:
            patient_id: Patient's user ID
            survey_type: Optional filter by survey type
            start_date: Optional start datetime filter
            end_date: Optional end datetime filter

        Returns:
            Number of survey responses
        """
        pass

    @abstractmethod
    async def exists(self, response_id: UUID) -> bool:
        """
        Check if survey response exists

        Args:
            response_id: Survey response ID

        Returns:
            True if response exists, False otherwise
        """
        pass

    @abstractmethod
    async def delete(self, response_id: UUID) -> bool:
        """
        Delete survey response record

        Args:
            response_id: Survey response ID

        Returns:
            True if response was deleted, False if not found
        """
        pass

    @abstractmethod
    async def get_average_score(
        self,
        patient_id: UUID,
        survey_type: Literal["CAT", "mMRC"],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> float | None:
        """
        Calculate average score for a patient and survey type

        Args:
            patient_id: Patient's user ID
            survey_type: Survey type ("CAT" or "mMRC")
            start_date: Optional start datetime filter
            end_date: Optional end datetime filter

        Returns:
            Average score as float, or None if no data
        """
        pass

    @abstractmethod
    async def get_score_trend(
        self,
        patient_id: UUID,
        survey_type: Literal["CAT", "mMRC"],
        days: int = 30,
    ) -> Literal["IMPROVING", "STABLE", "WORSENING", "INSUFFICIENT_DATA"]:
        """
        Analyze score trend for a patient

        Trend Definition:
        - IMPROVING: Scores are decreasing over time (better condition)
        - STABLE: Scores remain relatively constant
        - WORSENING: Scores are increasing over time (worse condition)
        - INSUFFICIENT_DATA: Less than 2 data points

        Args:
            patient_id: Patient's user ID
            survey_type: Survey type ("CAT" or "mMRC")
            days: Number of days to analyze (default 30)

        Returns:
            Trend indicator
        """
        pass

    @abstractmethod
    async def get_severity_distribution(
        self,
        patient_id: UUID,
        survey_type: Literal["CAT", "mMRC"],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict[str, int]:
        """
        Get distribution of severity levels for a patient

        Args:
            patient_id: Patient's user ID
            survey_type: Survey type ("CAT" or "mMRC")
            start_date: Optional start datetime filter
            end_date: Optional end datetime filter

        Returns:
            Dictionary with severity levels as keys and counts as values
            Example: {"MILD": 5, "MODERATE": 3, "SEVERE": 2, "VERY_SEVERE": 0}
        """
        pass
