"""
JWT Token Management Module
Handles JWT token creation, verification, and decoding
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError

from respira_ally.core.config import settings
from respira_ally.core.exceptions.application_exceptions import UnauthorizedError


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token

    Args:
        data: Payload data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string

    Example:
        >>> token = create_access_token({"sub": "user_id", "role": "patient"})
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "iat": datetime.now(UTC), "type": "access"})

    # Encode token
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return encoded_jwt


def create_refresh_token(data: dict[str, Any]) -> str:
    """
    Create a JWT refresh token with longer expiration

    Args:
        data: Payload data to encode in the token

    Returns:
        Encoded JWT refresh token string

    Example:
        >>> refresh_token = create_refresh_token({"sub": "user_id"})
    """
    to_encode = data.copy()

    # Set longer expiration for refresh token
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "iat": datetime.now(UTC), "type": "refresh"})

    # Encode token
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode JWT token without verification (for debugging/logging)

    Args:
        token: JWT token string

    Returns:
        Decoded payload dictionary

    Raises:
        UnauthorizedError: If token format is invalid

    Warning:
        This function does NOT verify token signature or expiration.
        Use verify_token() for authentication.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_signature": False, "verify_exp": False},
        )
        return payload
    except JWTError as e:
        raise UnauthorizedError(f"Invalid token format: {str(e)}")


def verify_token(token: str, expected_type: str = "access") -> dict[str, Any]:
    """
    Verify JWT token signature and expiration

    Args:
        token: JWT token string
        expected_type: Expected token type ("access" or "refresh")

    Returns:
        Decoded and verified payload dictionary

    Raises:
        UnauthorizedError: If token is expired, invalid, or wrong type

    Example:
        >>> payload = verify_token(token, expected_type="access")
        >>> user_id = payload["sub"]
    """
    try:
        # Decode and verify token
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

        # Verify token type
        token_type = payload.get("type")
        if token_type != expected_type:
            raise UnauthorizedError(
                f"Invalid token type: expected '{expected_type}', got '{token_type}'"
            )

        return payload

    except ExpiredSignatureError:
        raise UnauthorizedError("Token has expired")

    except JWTError as e:
        raise UnauthorizedError(f"Invalid token: {str(e)}")


def get_token_expiration(token: str) -> datetime | None:
    """
    Get token expiration datetime without full verification

    Args:
        token: JWT token string

    Returns:
        Expiration datetime or None if not present
    """
    try:
        payload = decode_token(token)
        exp_timestamp = payload.get("exp")

        if exp_timestamp:
            return datetime.fromtimestamp(exp_timestamp, tz=UTC)

        return None

    except UnauthorizedError:
        return None


def is_token_expired(token: str) -> bool:
    """
    Check if token is expired

    Args:
        token: JWT token string

    Returns:
        True if expired, False otherwise
    """
    exp_time = get_token_expiration(token)

    if exp_time is None:
        return True

    return datetime.now(UTC) > exp_time
