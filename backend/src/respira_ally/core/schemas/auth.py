"""
Authentication Schemas
Pydantic models for JWT authentication and authorization
"""
from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """User role enumeration"""
    PATIENT = "patient"
    THERAPIST = "therapist"


# ============================================================================
# JWT Token Schemas
# ============================================================================

class TokenPayload(BaseModel):
    """
    JWT Token Payload Schema
    Represents the decoded content of a JWT token
    """
    sub: str = Field(..., description="Subject (user_id)")
    role: UserRole = Field(..., description="User role (patient or therapist)")
    type: Literal["access", "refresh"] = Field(..., description="Token type")
    exp: int = Field(..., description="Expiration timestamp (Unix epoch)")
    iat: int = Field(..., description="Issued at timestamp (Unix epoch)")

    # Optional fields for enhanced security
    jti: str | None = Field(None, description="JWT ID for token revocation")
    scope: list[str] | None = Field(None, description="Token scopes/permissions")


class TokenData(BaseModel):
    """
    Validated Token Data
    Used after token verification and validation
    """
    user_id: UUID = Field(..., description="User UUID")
    role: UserRole = Field(..., description="User role")
    token_type: Literal["access", "refresh"] = Field(..., description="Token type")


class TokenResponse(BaseModel):
    """
    Token Response Schema
    API response containing access and refresh tokens
    """
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
    expires_in: int = Field(..., description="Access token expiration in seconds")
    refresh_expires_in: int = Field(..., description="Refresh token expiration in seconds")


# ============================================================================
# Login Request/Response Schemas
# ============================================================================

class PatientLoginRequest(BaseModel):
    """
    Patient Login Request (LINE Authentication)
    Patients authenticate via LINE LIFF using LINE User ID
    """
    line_user_id: str = Field(..., min_length=1, max_length=100, description="LINE User ID")
    line_access_token: str | None = Field(
        None, description="LINE access token for profile verification (optional)"
    )


class TherapistLoginRequest(BaseModel):
    """
    Therapist Login Request (Email + Password)
    Therapists authenticate via traditional email/password
    """
    email: EmailStr = Field(..., description="Therapist email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password")


class UserInfo(BaseModel):
    """
    User Information included in login response
    """
    user_id: UUID = Field(..., description="User UUID")
    role: UserRole = Field(..., description="User role")
    email: EmailStr | None = Field(None, description="Email (therapist only)")
    line_user_id: str | None = Field(None, description="LINE User ID (patient only)")
    display_name: str | None = Field(None, description="Display name")
    is_active: bool = Field(..., description="Account active status")
    created_at: datetime = Field(..., description="Account creation timestamp")


class LoginResponse(BaseModel):
    """
    Login Response Schema
    Contains tokens and basic user information
    """
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
    expires_in: int = Field(..., description="Access token expiration in seconds")
    user: UserInfo = Field(..., description="User information")


# ============================================================================
# Token Refresh Schemas
# ============================================================================

class RefreshTokenRequest(BaseModel):
    """
    Refresh Token Request
    Used to obtain a new access token using a refresh token
    """
    refresh_token: str = Field(..., description="JWT refresh token")


class RefreshTokenResponse(BaseModel):
    """
    Refresh Token Response
    Contains new access token and optionally a new refresh token
    """
    access_token: str = Field(..., description="New JWT access token")
    refresh_token: str | None = Field(
        None, description="New refresh token (if rotation is enabled)"
    )
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
    expires_in: int = Field(..., description="Access token expiration in seconds")


# ============================================================================
# Logout Schema
# ============================================================================

class LogoutRequest(BaseModel):
    """
    Logout Request
    Used to invalidate tokens (add to blacklist)
    """
    revoke_all_tokens: bool = Field(
        default=False, description="Revoke all tokens for this user (logout from all devices)"
    )
