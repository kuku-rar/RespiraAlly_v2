"""
Daily Log Repository Interface
Domain Layer - Clean Architecture

This is the abstract repository interface that defines the contract
for daily log data operations. The actual implementation is in the
Infrastructure Layer.
"""

from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from respira_ally.infrastructure.database.models.daily_log import DailyLogModel


class DailyLogRepository(ABC):
    """
    Abstract base class for Daily Log data access

    This interface defines all data operations for DailyLog entities.
    Following the Dependency Inversion Principle, the Domain Layer
    defines the interface, and the Infrastructure Layer implements it.
    """

    @abstractmethod
    async def create(self, daily_log: DailyLogModel) -> DailyLogModel:
        """
        Create a new daily log record

        Args:
            daily_log: DailyLogModel instance to persist

        Returns:
            DailyLogModel: The created daily log with database-generated fields

        Raises:
            IntegrityError: If log for same patient and date already exists
        """
        pass

    @abstractmethod
    async def get_by_id(self, log_id: UUID) -> DailyLogModel | None:
        """
        Retrieve daily log by log ID

        Args:
            log_id: Daily log ID (primary key)

        Returns:
            DailyLogModel if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_patient_and_date(
        self, patient_id: UUID, log_date: date
    ) -> DailyLogModel | None:
        """
        Retrieve daily log for specific patient and date

        Args:
            patient_id: Patient's user ID
            log_date: Log date

        Returns:
            DailyLogModel if found, None otherwise
        """
        pass

    @abstractmethod
    async def list_by_patient(
        self,
        patient_id: UUID,
        start_date: date | None = None,
        end_date: date | None = None,
        skip: int = 0,
        limit: int = 30,
    ) -> tuple[list[DailyLogModel], int]:
        """
        List daily logs for a specific patient

        Args:
            patient_id: Patient's user ID
            start_date: Optional start date (inclusive)
            end_date: Optional end date (inclusive)
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of daily logs, total count)
        """
        pass

    @abstractmethod
    async def list_by_date_range(
        self,
        start_date: date,
        end_date: date,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[DailyLogModel], int]:
        """
        List all daily logs within a date range (for therapist overview)

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of daily logs, total count)
        """
        pass

    @abstractmethod
    async def update(
        self,
        log_id: UUID,
        update_data: dict,
    ) -> DailyLogModel | None:
        """
        Update daily log information

        Args:
            log_id: Daily log ID
            update_data: Dictionary of fields to update

        Returns:
            Updated DailyLogModel if found, None otherwise

        Note:
            Only fields present in update_data will be modified
        """
        pass

    @abstractmethod
    async def delete(self, log_id: UUID) -> bool:
        """
        Delete daily log record

        Args:
            log_id: Daily log ID

        Returns:
            True if log was deleted, False if not found
        """
        pass

    @abstractmethod
    async def exists(self, log_id: UUID) -> bool:
        """
        Check if daily log exists

        Args:
            log_id: Daily log ID

        Returns:
            True if log exists, False otherwise
        """
        pass

    @abstractmethod
    async def count_by_patient(
        self,
        patient_id: UUID,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> int:
        """
        Count daily logs for a patient

        Args:
            patient_id: Patient's user ID
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Number of logs
        """
        pass

    @abstractmethod
    async def get_medication_adherence(
        self, patient_id: UUID, start_date: date, end_date: date
    ) -> float:
        """
        Calculate medication adherence rate for a patient

        Args:
            patient_id: Patient's user ID
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            Adherence rate as percentage (0-100)
        """
        pass

    @abstractmethod
    async def get_latest_log(self, patient_id: UUID) -> DailyLogModel | None:
        """
        Get the most recent log for a patient

        Args:
            patient_id: Patient's user ID

        Returns:
            Latest DailyLogModel if found, None otherwise
        """
        pass
