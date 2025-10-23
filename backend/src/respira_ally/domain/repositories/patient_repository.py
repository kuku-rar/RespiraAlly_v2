"""
Patient Repository Interface
Domain Layer - Clean Architecture

This is the abstract repository interface that defines the contract
for patient data operations. The actual implementation is in the
Infrastructure Layer.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel


class PatientRepository(ABC):
    """
    Abstract base class for Patient data access

    This interface defines all data operations for Patient entities.
    Following the Dependency Inversion Principle, the Domain Layer
    defines the interface, and the Infrastructure Layer implements it.
    """

    @abstractmethod
    async def create(self, patient: PatientProfileModel) -> PatientProfileModel:
        """
        Create a new patient record

        Args:
            patient: PatientProfileModel instance to persist

        Returns:
            PatientProfileModel: The created patient with database-generated fields

        Raises:
            IntegrityError: If patient with same user_id already exists
        """
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> PatientProfileModel | None:
        """
        Retrieve patient by user ID

        Args:
            user_id: Patient's user ID (primary key)

        Returns:
            PatientProfileModel if found, None otherwise
        """
        pass

    @abstractmethod
    async def list_by_therapist(
        self,
        therapist_id: UUID,
        skip: int = 0,
        limit: int = 20,
        # Filters
        search: str | None = None,
        gender: str | None = None,
        min_bmi: float | None = None,
        max_bmi: float | None = None,
        min_age: int | None = None,
        max_age: int | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[PatientProfileModel], int]:
        """
        List patients assigned to a specific therapist with filters

        Args:
            therapist_id: Therapist's user ID
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            search: Search by name or phone (case-insensitive)
            gender: Filter by gender (MALE, FEMALE, OTHER)
            min_bmi: Minimum BMI value
            max_bmi: Maximum BMI value
            min_age: Minimum age in years
            max_age: Maximum age in years
            sort_by: Sort field (name, birth_date, bmi, created_at)
            sort_order: Sort order (asc, desc)

        Returns:
            Tuple of (list of patients, total count)
        """
        pass

    @abstractmethod
    async def update(
        self,
        user_id: UUID,
        update_data: dict,
    ) -> PatientProfileModel | None:
        """
        Update patient information

        Args:
            user_id: Patient's user ID
            update_data: Dictionary of fields to update

        Returns:
            Updated PatientProfileModel if found, None otherwise

        Note:
            Only fields present in update_data will be modified
        """
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """
        Delete patient record (soft delete recommended)

        Args:
            user_id: Patient's user ID

        Returns:
            True if patient was deleted, False if not found

        Note:
            Consider implementing soft delete for data retention
        """
        pass

    @abstractmethod
    async def exists(self, user_id: UUID) -> bool:
        """
        Check if patient exists

        Args:
            user_id: Patient's user ID

        Returns:
            True if patient exists, False otherwise
        """
        pass

    @abstractmethod
    async def count_by_therapist(self, therapist_id: UUID) -> int:
        """
        Count patients assigned to a therapist

        Args:
            therapist_id: Therapist's user ID

        Returns:
            Number of patients assigned to this therapist
        """
        pass
