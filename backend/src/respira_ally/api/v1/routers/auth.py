"""
Auth Router - Authentication & Authorization API Endpoints
Presentation Layer (Clean Architecture)
"""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.application.auth.use_cases.login_use_case import (
    PatientLoginUseCase,
    TherapistLoginUseCase,
)
from respira_ally.application.auth.use_cases.logout_use_case import LogoutUseCase
from respira_ally.application.auth.use_cases.refresh_token_use_case import RefreshTokenUseCase
from respira_ally.application.auth.use_cases.register_use_case import TherapistRegisterUseCase
from respira_ally.core.dependencies import get_current_user, get_token_from_header
from respira_ally.core.schemas.auth import (
    LoginResponse,
    LogoutRequest,
    PatientLoginRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    TherapistLoginRequest,
    TherapistRegisterRequest,
    TokenData,
)
from respira_ally.infrastructure.cache.token_blacklist_service import token_blacklist_service
from respira_ally.infrastructure.database.session import get_db
from respira_ally.infrastructure.repositories.user_repository_impl import UserRepositoryImpl

router = APIRouter()


# ============================================================================
# Dependency Injection Functions
# ============================================================================


def get_user_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> UserRepositoryImpl:
    """
    Dependency to inject UserRepository implementation

    Args:
        db: Database session from FastAPI dependency

    Returns:
        UserRepositoryImpl instance
    """
    return UserRepositoryImpl(db)


def get_patient_login_use_case(
    user_repository: Annotated[UserRepositoryImpl, Depends(get_user_repository)],
) -> PatientLoginUseCase:
    """Dependency to inject PatientLoginUseCase"""
    return PatientLoginUseCase(user_repository)


def get_therapist_login_use_case(
    user_repository: Annotated[UserRepositoryImpl, Depends(get_user_repository)],
) -> TherapistLoginUseCase:
    """Dependency to inject TherapistLoginUseCase"""
    return TherapistLoginUseCase(user_repository)


def get_therapist_register_use_case(
    user_repository: Annotated[UserRepositoryImpl, Depends(get_user_repository)],
) -> TherapistRegisterUseCase:
    """Dependency to inject TherapistRegisterUseCase"""
    return TherapistRegisterUseCase(user_repository)


def get_logout_use_case() -> LogoutUseCase:
    """Dependency to inject LogoutUseCase"""
    return LogoutUseCase(token_blacklist_service)


def get_refresh_token_use_case() -> RefreshTokenUseCase:
    """Dependency to inject RefreshTokenUseCase"""
    return RefreshTokenUseCase(token_blacklist_service)


# ============================================================================
# Authentication Endpoints
# ============================================================================


@router.post(
    "/patient/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Patient Login (LINE OAuth)",
    description="""
    Patient login via LINE User ID.

    - Auto-registers new patients if LINE User ID not found
    - Returns JWT access & refresh tokens
    - Updates last login timestamp
    """,
    tags=["Authentication"],
)
async def patient_login(
    request: PatientLoginRequest,
    use_case: Annotated[PatientLoginUseCase, Depends(get_patient_login_use_case)],
) -> LoginResponse:
    """
    Patient login endpoint using LINE OAuth

    Args:
        request: PatientLoginRequest with line_user_id
        use_case: Injected PatientLoginUseCase

    Returns:
        LoginResponse with tokens and user info

    Raises:
        UnauthorizedError: If account is deactivated
    """
    return await use_case.execute(
        line_user_id=request.line_user_id, line_access_token=request.line_access_token
    )


@router.post(
    "/therapist/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Therapist Login (Email + Password)",
    description="""
    Therapist login via email and password.

    - Verifies email and bcrypt-hashed password
    - Returns JWT access & refresh tokens
    - Updates last login timestamp
    """,
    tags=["Authentication"],
)
async def therapist_login(
    request: TherapistLoginRequest,
    use_case: Annotated[TherapistLoginUseCase, Depends(get_therapist_login_use_case)],
) -> LoginResponse:
    """
    Therapist login endpoint using email/password

    Args:
        request: TherapistLoginRequest with email and password
        use_case: Injected TherapistLoginUseCase

    Returns:
        LoginResponse with tokens and user info

    Raises:
        UnauthorizedError: If credentials are invalid or account is deactivated
    """
    return await use_case.execute(email=request.email, password=request.password)


@router.post(
    "/therapist/register",
    response_model=LoginResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Therapist Registration",
    description="""
    Register a new therapist account.

    - Only therapists need manual registration (patients auto-register via LINE)
    - Email must be unique
    - Password must be at least 8 characters
    - Automatically logs in after registration
    """,
    tags=["Authentication"],
)
async def therapist_register(
    request: TherapistRegisterRequest,
    use_case: Annotated[TherapistRegisterUseCase, Depends(get_therapist_register_use_case)],
) -> LoginResponse:
    """
    Therapist registration endpoint

    Args:
        request: TherapistRegisterRequest with email, password, full_name
        use_case: Injected TherapistRegisterUseCase

    Returns:
        LoginResponse with tokens and user info (auto-login after registration)

    Raises:
        ConflictError: If email already exists
    """
    return await use_case.execute(
        email=request.email, password=request.password, full_name=request.full_name
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout (Revoke Token)",
    description="""
    Logout and revoke access token.

    - Adds current token to blacklist
    - Optional: Revoke all tokens for this user (logout from all devices)
    - Requires valid access token in Authorization header
    """,
    tags=["Authentication"],
)
async def logout(
    request: LogoutRequest,
    token: Annotated[str, Depends(get_token_from_header)],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    use_case: Annotated[LogoutUseCase, Depends(get_logout_use_case)],
) -> None:
    """
    Logout endpoint - revokes access token

    Args:
        request: LogoutRequest with optional revoke_all_tokens flag
        token: Raw JWT token extracted from Authorization header
        current_user: Current authenticated user from JWT (validates token)
        use_case: Injected LogoutUseCase

    Returns:
        None (204 No Content)
    """
    await use_case.execute(access_token=token, revoke_all_tokens=request.revoke_all_tokens)


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Access Token",
    description="""
    Refresh access token using refresh token.

    - Generates new access token
    - Optional: Rotate refresh token for enhanced security
    - Refresh token must not be blacklisted
    """,
    tags=["Authentication"],
)
async def refresh_token(
    request: RefreshTokenRequest,
    use_case: Annotated[RefreshTokenUseCase, Depends(get_refresh_token_use_case)],
) -> RefreshTokenResponse:
    """
    Token refresh endpoint

    Args:
        request: RefreshTokenRequest with refresh_token
        use_case: Injected RefreshTokenUseCase

    Returns:
        RefreshTokenResponse with new access token and optionally new refresh token

    Raises:
        UnauthorizedError: If refresh token is invalid, expired, or blacklisted
    """
    return await use_case.execute(
        refresh_token=request.refresh_token,
        rotate_refresh_token=False,  # Set to True for token rotation
    )
