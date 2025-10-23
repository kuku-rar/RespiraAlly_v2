"""
FastAPI Dependencies
Authentication and authorization dependencies for route protection
"""

from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.core.exceptions.application_exceptions import ForbiddenError, UnauthorizedError
from respira_ally.core.schemas.auth import TokenData, UserRole
from respira_ally.core.security.jwt import verify_token
from respira_ally.infrastructure.cache.redis_client import get_redis
from respira_ally.infrastructure.cache.token_blacklist_service import token_blacklist_service
from respira_ally.infrastructure.database.session import get_db


def get_token_from_header(authorization: str | None = Header(None)) -> str:
    """
    Extract JWT token from Authorization header

    Args:
        authorization: Authorization header value (format: "Bearer <token>")

    Returns:
        Extracted token string

    Raises:
        UnauthorizedError: If header is missing or malformed
    """
    if not authorization:
        raise UnauthorizedError("Missing Authorization header")

    parts = authorization.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedError("Invalid Authorization header format. Expected: Bearer <token>")

    return parts[1]


async def get_current_user(token: Annotated[str, Depends(get_token_from_header)]) -> TokenData:
    """
    Get current authenticated user from JWT token

    This dependency:
    1. Extracts token from Authorization header
    2. Verifies token signature and expiration
    3. Checks if token is blacklisted
    4. Returns validated token data

    Args:
        token: JWT token from Authorization header

    Returns:
        TokenData with user_id and role

    Raises:
        UnauthorizedError: If token is invalid, expired, or blacklisted

    Usage:
        @router.get("/me")
        async def get_me(current_user: TokenData = Depends(get_current_user)):
            return {"user_id": current_user.user_id}
    """
    # Verify token signature and expiration
    payload = verify_token(token, expected_type="access")

    # Extract user information
    user_id_str = payload.get("sub")
    role_str = payload.get("role")

    if not user_id_str or not role_str:
        raise UnauthorizedError("Invalid token: missing user information")

    try:
        user_id = UUID(user_id_str)
        role = UserRole(role_str)
    except (ValueError, KeyError):
        raise UnauthorizedError("Invalid token: malformed user data")

    # Check if token is blacklisted
    is_blacklisted = await token_blacklist_service.is_blacklisted(token, user_id=user_id_str)
    if is_blacklisted:
        raise UnauthorizedError("Token has been revoked")

    return TokenData(user_id=user_id, role=role, token_type="access")


async def get_current_patient(
    current_user: Annotated[TokenData, Depends(get_current_user)],
) -> TokenData:
    """
    Require current user to be a patient

    Raises:
        ForbiddenError: If user is not a patient

    Usage:
        @router.get("/patients/me")
        async def get_patient_profile(patient: TokenData = Depends(get_current_patient)):
            return {"patient_id": patient.user_id}
    """
    if current_user.role != UserRole.PATIENT:
        raise ForbiddenError("This endpoint requires patient role")

    return current_user


async def get_current_therapist(
    current_user: Annotated[TokenData, Depends(get_current_user)],
) -> TokenData:
    """
    Require current user to be a therapist

    Raises:
        ForbiddenError: If user is not a therapist

    Usage:
        @router.get("/therapists/dashboard")
        async def therapist_dashboard(therapist: TokenData = Depends(get_current_therapist)):
            return {"therapist_id": therapist.user_id}
    """
    if current_user.role != UserRole.THERAPIST:
        raise ForbiddenError("This endpoint requires therapist role")

    return current_user


# Optional: Helper dependency for routes that allow both roles but need authentication
async def get_authenticated_user(
    current_user: Annotated[TokenData, Depends(get_current_user)],
) -> TokenData:
    """
    Require authentication but allow any role

    Usage:
        @router.get("/profile")
        async def get_profile(user: TokenData = Depends(get_authenticated_user)):
            # Works for both patients and therapists
            return {"user_id": user.user_id, "role": user.role}
    """
    return current_user


# ============================================================================
# Application Services Dependencies
# ============================================================================


async def get_patient_service(db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Dependency injection for PatientService

    Provides PatientService instance with PatientRepository injected.

    Args:
        db: Database session from FastAPI dependency

    Returns:
        PatientService instance

    Usage:
        @router.post("/patients")
        async def create_patient(
            patient_service: Annotated[PatientService, Depends(get_patient_service)]
        ):
            return await patient_service.create_patient(...)
    """
    from respira_ally.application.patient.patient_service import PatientService
    from respira_ally.infrastructure.repository_impls.patient_repository_impl import (
        PatientRepositoryImpl,
    )

    patient_repo = PatientRepositoryImpl(db)
    return PatientService(patient_repo)


async def get_daily_log_service(db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Dependency injection for DailyLogService

    Provides DailyLogService instance with DailyLogRepository and EventPublisher injected.

    Args:
        db: Database session from FastAPI dependency

    Returns:
        DailyLogService instance

    Usage:
        @router.post("/daily-logs")
        async def create_log(
            service: Annotated[DailyLogService, Depends(get_daily_log_service)]
        ):
            return await service.create_daily_log(...)
    """
    from respira_ally.application.daily_log.daily_log_service import DailyLogService
    from respira_ally.infrastructure.message_queue.in_memory_event_bus import get_event_bus
    from respira_ally.infrastructure.repository_impls.daily_log_repository_impl import (
        DailyLogRepositoryImpl,
    )

    daily_log_repo = DailyLogRepositoryImpl(db)
    event_publisher = get_event_bus()  # Use in-memory event bus for now

    return DailyLogService(daily_log_repo, event_publisher)


def get_idempotency_key(
    idempotency_key: str | None = Header(None, alias="Idempotency-Key")
) -> str | None:
    """
    Extract Idempotency-Key from request header (optional)

    Args:
        idempotency_key: Idempotency-Key header value (UUID recommended)

    Returns:
        Idempotency key string or None if not provided

    Usage:
        @router.post("/resource")
        async def create_resource(
            key: Annotated[str | None, Depends(get_idempotency_key)]
        ):
            if key:
                # Handle idempotency
                ...
    """
    return idempotency_key


async def get_idempotency_service(redis: Annotated[Any, Depends(get_redis)]):
    """
    Dependency injection for IdempotencyService

    Provides IdempotencyService instance with Redis client injected.

    Args:
        redis: Redis client from FastAPI dependency

    Returns:
        IdempotencyService instance

    Usage:
        @router.post("/resource")
        async def create_resource(
            idempotency: Annotated[IdempotencyService, Depends(get_idempotency_service)],
            key: Annotated[str | None, Depends(get_idempotency_key)]
        ):
            if key:
                cached = await idempotency.get_cached_response(key)
                if cached:
                    return cached
    """
    from respira_ally.infrastructure.cache import IdempotencyService

    return IdempotencyService(redis)


async def get_survey_service(db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Dependency injection for SurveyService

    Provides SurveyService instance with Survey and Patient repositories injected.

    Args:
        db: Database session from FastAPI dependency

    Returns:
        SurveyService instance

    Usage:
        @router.post("/surveys/cat")
        async def submit_cat(
            service: Annotated[SurveyService, Depends(get_survey_service)]
        ):
            return await service.submit_cat_survey(...)
    """
    from respira_ally.application.survey.survey_service import SurveyService
    from respira_ally.infrastructure.repository_impls.patient_repository_impl import (
        PatientRepositoryImpl,
    )
    from respira_ally.infrastructure.repository_impls.survey_repository_impl import (
        SurveyRepositoryImpl,
    )

    survey_repo = SurveyRepositoryImpl(db)
    patient_repo = PatientRepositoryImpl(db)

    return SurveyService(survey_repo, patient_repo)
