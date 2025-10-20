"""
Login Use Cases
Handles user authentication for both Patient (LINE) and Therapist (Email/Password)
"""
from passlib.context import CryptContext

from respira_ally.core.config import settings
from respira_ally.core.exceptions.application_exceptions import (
    UnauthorizedError,
    ValidationError,
)
from respira_ally.core.schemas.auth import LoginResponse, UserInfo, UserRole
from respira_ally.core.security.jwt import create_access_token, create_refresh_token
from respira_ally.domain.repositories.user_repository import UserRepository
from respira_ally.infrastructure.cache.login_lockout_service import login_lockout_service

# Password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PatientLoginUseCase:
    """
    Patient Login Use Case (LINE OAuth Authentication)

    Flow:
    1. Verify LINE User ID (optional: verify LINE access token with LINE API)
    2. Find or create patient user
    3. Update last login timestamp
    4. Generate JWT tokens
    5. Return tokens + user info
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(
        self, line_user_id: str, line_access_token: str | None = None
    ) -> LoginResponse:
        """
        Authenticate patient via LINE User ID

        Args:
            line_user_id: LINE User ID
            line_access_token: Optional LINE access token for verification

        Returns:
            LoginResponse with tokens and user info

        Raises:
            ValidationError: If LINE User ID is invalid
            UnauthorizedError: If LINE verification fails
        """
        # Validate input
        if not line_user_id or len(line_user_id) == 0:
            raise ValidationError(field="line_user_id", message="LINE User ID is required")

        # TODO: Optional LINE API verification
        # if line_access_token:
        #     await self._verify_line_token(line_user_id, line_access_token)

        # Find existing patient or create new one
        user = await self.user_repository.find_by_line_user_id(line_user_id)

        if user is None:
            # Auto-register new patient (LINE OAuth flow)
            user = await self.user_repository.create_patient(
                line_user_id=line_user_id, display_name=None
            )

        # Check if user account is active
        if user.deleted_at is not None:
            raise UnauthorizedError("Account has been deactivated")

        # Update last login
        await self.user_repository.update_last_login(user.user_id)

        # Generate tokens
        token_payload = {"sub": str(user.user_id), "role": UserRole.PATIENT.value}

        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(token_payload)

        # Build user info
        user_info = UserInfo(
            user_id=user.user_id,
            role=UserRole.PATIENT,
            email=None,
            line_user_id=user.line_user_id,
            display_name=None,  # TODO: Fetch from patient_profile
            is_active=user.deleted_at is None,
            created_at=user.created_at,
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_info,
        )


class TherapistLoginUseCase:
    """
    Therapist Login Use Case (Email + Password Authentication)

    Flow:
    1. Find therapist by email
    2. Verify password (bcrypt)
    3. Check account status
    4. Update last login
    5. Generate JWT tokens
    6. Return tokens + user info
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, email: str, password: str) -> LoginResponse:
        """
        Authenticate therapist via email and password

        Args:
            email: Therapist email address
            password: Plain text password

        Returns:
            LoginResponse with tokens and user info

        Raises:
            ValidationError: If email or password is invalid
            UnauthorizedError: If credentials are incorrect or account is locked
        """
        # Validate input
        if not email or len(email) == 0:
            raise ValidationError(field="email", message="Email is required")

        if not password or len(password) < 8:
            raise ValidationError(
                field="password", message="Password must be at least 8 characters"
            )

        # Check if account is locked out
        is_locked, remaining_seconds = await login_lockout_service.is_locked_out(email)
        if is_locked:
            remaining_minutes = (remaining_seconds or 0) // 60 + 1
            raise UnauthorizedError(
                f"Account temporarily locked due to multiple failed login attempts. "
                f"Please try again in {remaining_minutes} minutes."
            )

        # Find therapist by email
        user = await self.user_repository.find_by_email(email)

        if user is None:
            # Record failed attempt even if user doesn't exist (prevent user enumeration timing attacks)
            await login_lockout_service.record_failed_attempt(email)
            raise UnauthorizedError("Invalid email or password")

        # Verify role
        if user.role != "THERAPIST":
            await login_lockout_service.record_failed_attempt(email)
            raise UnauthorizedError("Invalid email or password")

        # Verify password
        if not user.hashed_password:
            await login_lockout_service.record_failed_attempt(email)
            raise UnauthorizedError("Invalid account configuration")

        if not pwd_context.verify(password, user.hashed_password):
            # Record failed attempt and check if now locked
            is_now_locked, fail_count = await login_lockout_service.record_failed_attempt(email)

            if is_now_locked:
                # Account just got locked
                lockout_info = login_lockout_service.get_lockout_info(fail_count)
                lockout_duration = lockout_info.get("next_lockout_duration", 15)
                raise UnauthorizedError(
                    f"Too many failed login attempts. Account locked for {lockout_duration} minutes."
                )

            raise UnauthorizedError("Invalid email or password")

        # Check if account is active
        if user.deleted_at is not None:
            raise UnauthorizedError("Account has been deactivated")

        # ✅ Successful login - Clear failed attempts
        await login_lockout_service.clear_failed_attempts(email)

        # Update last login
        await self.user_repository.update_last_login(user.user_id)

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
            display_name=None,  # TODO: Fetch from therapist_profile
            is_active=user.deleted_at is None,
            created_at=user.created_at,
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_info,
        )


# Helper functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)
