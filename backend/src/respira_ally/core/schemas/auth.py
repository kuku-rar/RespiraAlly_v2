"""
Authentication Schemas
Pydantic models for JWT authentication and authorization
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """
    User role enumeration with hierarchical permissions

    Role Hierarchy (lowest to highest):
    - PATIENT: Can only access their own data (read-only for profiles)
    - THERAPIST: Can access and modify their assigned patients' data
    - SUPERVISOR: Can access and modify ALL patients' data (MVP mode)
    - ADMIN: Full system access (future: user management, system config)

    Design Decision: ADR-015 - RBAC Extension for MVP Flexibility
    """

    PATIENT = "PATIENT"
    THERAPIST = "THERAPIST"
    SUPERVISOR = "SUPERVISOR"  # MVP: Can access all patients
    ADMIN = "ADMIN"  # Future: Full system administration


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


# ============================================================================
# Registration Schemas
# ============================================================================


class TherapistRegisterRequest(BaseModel):
    """
    Therapist Registration Request
    Patients auto-register via LINE, so only therapists need manual registration
    """

    email: EmailStr = Field(..., description="Therapist email address")
    password: str = Field(
        ..., min_length=8, max_length=128, description="Password (min 8 characters)"
    )
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")


class PatientRegisterRequest(BaseModel):
    """
    Patient Initial Registration Request (LINE LIFF)

    This schema is used when a patient completes their initial registration via LINE LIFF.
    It includes all necessary fields for patient profile creation, including optional hospital
    medical record number (hospital_patient_id), health metrics, and emergency contact information.

    Design Decision:
    - Patients register with complete profile data in one step (not auto-register with minimal data)
    - hospital_patient_id maps to database field hospital_medical_record_number
    - Returns JWT tokens upon successful registration for immediate login
    """

    # LINE Authentication Data
    line_user_id: str = Field(
        ..., min_length=1, max_length=100, description="LINE User ID (unique identifier)"
    )
    line_display_name: str | None = Field(
        None, max_length=100, description="LINE display name (optional)"
    )
    line_picture_url: str | None = Field(
        None, max_length=255, description="LINE profile picture URL (optional)"
    )

    # Required Basic Information
    full_name: str = Field(..., min_length=2, max_length=100, description="Patient full name")
    date_of_birth: date = Field(..., description="Date of birth (YYYY-MM-DD)")
    gender: Literal["MALE", "FEMALE", "OTHER"] = Field(..., description="Gender")

    # Optional Contact Information
    phone_number: str | None = Field(None, max_length=20, description="Contact phone number")

    # Optional Hospital Integration
    hospital_patient_id: str | None = Field(
        None,
        max_length=50,
        description="Hospital medical record number (maps to hospital_medical_record_number in DB)",
    )

    # Optional Health Metrics
    height_cm: int | None = Field(
        None, ge=100, le=250, description="Height in centimeters (100-250 cm)"
    )
    weight_kg: Decimal | None = Field(
        None, ge=30, le=200, description="Weight in kilograms (30-200 kg)"
    )
    smoking_years: int | None = Field(
        None, ge=0, le=80, description="Years of smoking (0-80 years, 0 if never smoked)"
    )

    # Optional Emergency Contact
    emergency_contact_name: str | None = Field(
        None, max_length=100, description="Emergency contact person name"
    )
    emergency_contact_phone: str | None = Field(
        None, max_length=20, description="Emergency contact phone number"
    )
