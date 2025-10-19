"""
FastAPI Dependencies
Authentication and authorization dependencies for route protection
"""
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header

from respira_ally.core.exceptions.application_exceptions import ForbiddenError, UnauthorizedError
from respira_ally.core.schemas.auth import TokenData, UserRole
from respira_ally.core.security.jwt import verify_token
from respira_ally.infrastructure.cache.token_blacklist_service import token_blacklist_service


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
    current_user: Annotated[TokenData, Depends(get_current_user)]
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
    current_user: Annotated[TokenData, Depends(get_current_user)]
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
    current_user: Annotated[TokenData, Depends(get_current_user)]
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
