"""
Patient Schemas
Pydantic models for Patient API endpoints
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Base Schemas
# ============================================================================

class PatientBase(BaseModel):
    """Base patient information (shared fields)"""
    name: str = Field(..., min_length=2, max_length=100, description="Patient full name")
    birth_date: date = Field(..., description="Date of birth")
    gender: Literal["MALE", "FEMALE", "OTHER"] | None = Field(None, description="Gender")


# ============================================================================
# Request Schemas
# ============================================================================

class PatientCreate(PatientBase):
    """
    Patient Creation Request
    Therapists create patient profiles and assign themselves
    """
    therapist_id: UUID = Field(..., description="Assigned therapist ID")

    # Optional fields for detailed profile
    height_cm: int | None = Field(None, ge=50, le=250, description="Height in cm")
    weight_kg: Decimal | None = Field(None, ge=20, le=300, description="Weight in kg")

    # Contact information (simplified for MVP)
    phone: str | None = Field(None, max_length=20, description="Contact phone number")


class PatientUpdate(BaseModel):
    """
    Patient Update Request
    All fields optional for partial updates
    """
    name: str | None = Field(None, min_length=2, max_length=100)
    birth_date: date | None = None
    gender: Literal["MALE", "FEMALE", "OTHER"] | None = None
    height_cm: int | None = Field(None, ge=50, le=250)
    weight_kg: Decimal | None = Field(None, ge=20, le=300)
    phone: str | None = Field(None, max_length=20)
    therapist_id: UUID | None = None


class PatientQueryFilters(BaseModel):
    """
    Patient Query Filters
    Optional filters for patient list endpoint
    """
    # Search
    search: str | None = Field(None, description="Search by name or phone (case-insensitive)")

    # Gender filter
    gender: Literal["MALE", "FEMALE", "OTHER"] | None = Field(None, description="Filter by gender")

    # BMI range filter
    min_bmi: Decimal | None = Field(None, ge=0, le=100, description="Minimum BMI")
    max_bmi: Decimal | None = Field(None, ge=0, le=100, description="Maximum BMI")

    # Age range filter
    min_age: int | None = Field(None, ge=0, le=150, description="Minimum age")
    max_age: int | None = Field(None, ge=0, le=150, description="Maximum age")

    # Sorting
    sort_by: Literal["name", "birth_date", "bmi", "created_at"] | None = Field(
        "created_at", description="Sort field (default: created_at)"
    )
    sort_order: Literal["asc", "desc"] | None = Field(
        "desc", description="Sort order (default: desc)"
    )


# ============================================================================
# Response Schemas
# ============================================================================

class PatientResponse(PatientBase):
    """
    Patient API Response
    Returns essential patient information
    """
    user_id: UUID = Field(..., description="Patient user ID (primary key)")
    therapist_id: UUID | None = Field(None, description="Assigned therapist ID")

    # Physical metrics
    height_cm: int | None = None
    weight_kg: Decimal | None = None

    # Contact info
    phone: str | None = None

    # Computed field (if available)
    bmi: Decimal | None = Field(None, description="Body Mass Index (computed)")
    age: int | None = Field(None, description="Age in years (computed)")

    model_config = ConfigDict(from_attributes=True)


class PatientListResponse(BaseModel):
    """
    Patient List Response (with pagination)
    """
    items: list[PatientResponse]
    total: int = Field(..., description="Total number of patients")
    page: int = Field(..., description="Current page (0-indexed)")
    page_size: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Has next page")


# ============================================================================
# Detailed Response (for future expansion)
# ============================================================================

class PatientDetailResponse(PatientResponse):
    """
    Detailed Patient Response
    Includes additional medical information (future use)
    """
    smoking_status: Literal["NEVER", "FORMER", "CURRENT"] | None = None
    smoking_years: int | None = None
    hospital_medical_record_number: str | None = None

    # Timestamps
    created_at: datetime | None = None
    updated_at: datetime | None = None
