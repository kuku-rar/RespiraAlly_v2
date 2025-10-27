"""
User Repository Interface (Domain Layer)
Defines contracts for user data access operations
"""

from abc import ABC, abstractmethod
from uuid import UUID

from respira_ally.infrastructure.database.models.user import UserModel


class UserRepository(ABC):
    """
    User Repository Interface

    This interface defines contracts for user-related data operations.
    Implementation is in infrastructure layer (dependency inversion).
    """

    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> UserModel | None:
        """
        Find user by UUID

        Args:
            user_id: User's UUID

        Returns:
            User object if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_by_line_user_id(self, line_user_id: str) -> UserModel | None:
        """
        Find user by LINE User ID (Patient authentication)

        Args:
            line_user_id: LINE User ID

        Returns:
            User object if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> UserModel | None:
        """
        Find user by email (Therapist authentication)

        Args:
            email: User's email address

        Returns:
            User object if found, None otherwise
        """
        pass

    @abstractmethod
    async def create_patient(self, line_user_id: str, display_name: str | None = None) -> UserModel:
        """
        Create a new patient user

        Args:
            line_user_id: LINE User ID
            display_name: Optional display name

        Returns:
            Created User object
        """
        pass

    @abstractmethod
    async def create_therapist(self, email: str, password_hash: str, full_name: str) -> UserModel:
        """
        Create a new therapist user

        Args:
            email: Therapist email
            password_hash: Hashed password (bcrypt)
            full_name: Therapist full name

        Returns:
            Created User object
        """
        pass

    @abstractmethod
    async def update_last_login(self, user_id: UUID) -> None:
        """
        Update user's last login timestamp

        Args:
            user_id: User's UUID
        """
        pass

    @abstractmethod
    async def is_active(self, user_id: UUID) -> bool:
        """
        Check if user account is active

        Args:
            user_id: User's UUID

        Returns:
            True if active, False otherwise
        """
        pass
