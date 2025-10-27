"""
User Repository Implementation (Infrastructure Layer)
Concrete implementation of UserRepository interface using SQLAlchemy
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.core.schemas.auth import UserRole
from respira_ally.domain.repositories.user_repository import UserRepository
from respira_ally.infrastructure.database.models.user import UserModel


class UserRepositoryImpl(UserRepository):
    """
    SQLAlchemy implementation of UserRepository

    This class implements the repository pattern for user data access,
    providing concrete implementations of all UserRepository interface methods.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session

        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    async def find_by_id(self, user_id: UUID) -> UserModel | None:
        """
        Find user by UUID

        Args:
            user_id: User's UUID

        Returns:
            UserModel if found and not deleted, None otherwise
        """
        stmt = select(UserModel).where(
            UserModel.user_id == user_id,
            UserModel.deleted_at.is_(None),  # Exclude soft-deleted users
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_line_user_id(self, line_user_id: str) -> UserModel | None:
        """
        Find user by LINE User ID (Patient authentication)

        Args:
            line_user_id: LINE User ID

        Returns:
            UserModel if found and not deleted, None otherwise
        """
        stmt = select(UserModel).where(
            UserModel.line_user_id == line_user_id, UserModel.deleted_at.is_(None)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str) -> UserModel | None:
        """
        Find user by email (Therapist authentication)

        Args:
            email: User's email address

        Returns:
            UserModel if found and not deleted, None otherwise
        """
        stmt = select(UserModel).where(UserModel.email == email, UserModel.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_patient(self, line_user_id: str, display_name: str | None = None) -> UserModel:
        """
        Create a new patient user

        Args:
            line_user_id: LINE User ID
            display_name: Optional display name (not used in UserModel, for future profile creation)

        Returns:
            Created UserModel
        """
        user = UserModel(
            line_user_id=line_user_id,
            role=UserRole.PATIENT.value,
            email=None,  # Patients don't have email in UserModel
            hashed_password=None,  # Patients use LINE OAuth
        )

        self.db.add(user)
        await self.db.flush()  # Generate user_id
        await self.db.refresh(user)  # Refresh to get all server defaults

        return user

    async def create_therapist(self, email: str, password_hash: str, full_name: str) -> UserModel:
        """
        Create a new therapist user

        Args:
            email: Therapist email
            password_hash: Hashed password (bcrypt)
            full_name: Therapist full name (not used in UserModel, for future profile creation)

        Returns:
            Created UserModel
        """
        user = UserModel(
            email=email,
            hashed_password=password_hash,
            role=UserRole.THERAPIST.value,
            line_user_id=None,  # Therapists don't use LINE
        )

        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def update_last_login(self, user_id: UUID) -> None:
        """
        Update user's last login timestamp

        Note: Currently updates the 'updated_at' field since there's no
        dedicated 'last_login_at' field in the UserModel schema.

        Args:
            user_id: User's UUID
        """
        stmt = (
            update(UserModel)
            .where(UserModel.user_id == user_id)
            .values(updated_at=datetime.now(UTC))
        )
        await self.db.execute(stmt)
        await self.db.flush()

    async def is_active(self, user_id: UUID) -> bool:
        """
        Check if user account is active (not soft-deleted)

        Args:
            user_id: User's UUID

        Returns:
            True if active (deleted_at is NULL), False otherwise
        """
        stmt = select(UserModel.deleted_at).where(UserModel.user_id == user_id)
        result = await self.db.execute(stmt)
        deleted_at = result.scalar_one_or_none()

        # Active means deleted_at is None
        return deleted_at is None
