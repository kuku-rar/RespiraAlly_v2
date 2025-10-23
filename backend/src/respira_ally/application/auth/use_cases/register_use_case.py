"""
Registration Use Case
Handles therapist registration (patients auto-register via LINE OAuth)
"""

from respira_ally.core.config import settings
from respira_ally.core.exceptions.application_exceptions import ConflictError, ValidationError
from respira_ally.core.schemas.auth import LoginResponse, UserInfo, UserRole
from respira_ally.core.security.jwt import create_access_token, create_refresh_token
from respira_ally.domain.repositories.user_repository import UserRepository

from .login_use_case import hash_password


class TherapistRegisterUseCase:
    """
    Therapist Registration Use Case

    Flow:
    1. Validate input (email, password, full_name)
    2. Check if email already exists
    3. Hash password
    4. Create therapist user
    5. Generate JWT tokens
    6. Return tokens + user info
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, email: str, password: str, full_name: str) -> LoginResponse:
        """
        Register a new therapist

        Args:
            email: Therapist email address
            password: Plain text password (min 8 characters)
            full_name: Therapist full name

        Returns:
            LoginResponse with tokens and user info

        Raises:
            ValidationError: If input validation fails
            ConflictError: If email already exists
        """
        # Validate input
        if not email or len(email) == 0:
            raise ValidationError(field="email", message="Email is required")

        if not password or len(password) < 8:
            raise ValidationError(
                field="password",
                message="Password must be at least 8 characters",
                value=len(password) if password else 0,
            )

        if not full_name or len(full_name) == 0:
            raise ValidationError(field="full_name", message="Full name is required")

        # Check if email already exists
        existing_user = await self.user_repository.find_by_email(email)

        if existing_user is not None:
            raise ConflictError(
                resource_type="User",
                conflict_field="email",
                value=email,
            )

        # Hash password
        hashed_password = hash_password(password)

        # Create therapist user
        user = await self.user_repository.create_therapist(
            email=email, password_hash=hashed_password, full_name=full_name
        )

        # Generate tokens
        token_payload = {"sub": str(user.user_id), "role": UserRole.THERAPIST.value}

        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(token_payload)

        # Build user info
        user_info = UserInfo(
            user_id=user.user_id,
            role=UserRole.THERAPIST,
            email=user.email,
            line_user_id=None,
            display_name=full_name,
            is_active=True,
            created_at=user.created_at,
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_info,
        )
