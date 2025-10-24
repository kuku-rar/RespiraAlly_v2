"""
Exacerbation Schemas
Pydantic models for Exacerbation Management API endpoints

Sprint 4: Risk Engine & Exacerbation Tracking
Supports GOLD ABE classification and patient risk assessment
"""

from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Exacerbation Request Schemas
# ============================================================================


class ExacerbationCreate(BaseModel):
    """
    Create exacerbation record request

    Therapists record patient acute exacerbation events for risk assessment.
    Auto-updates patient_profiles summary fields (exacerbation_count_last_12m, etc.)
    """

    model_config = ConfigDict(from_attributes=True)

    # Required fields
    patient_id: UUID = Field(..., description="Patient UUID")
    onset_date: date = Field(..., description="Date of exacerbation onset (YYYY-MM-DD)")
    severity: Literal["MILD", "MODERATE", "SEVERE"] = Field(
        ..., description="Severity level: MILD, MODERATE, or SEVERE"
    )

    # Treatment information
    required_hospitalization: bool = Field(
        False, description="Whether hospitalization was required"
    )
    hospitalization_days: int | None = Field(
        None, ge=1, description="Number of hospitalization days (required if hospitalized)"
    )
    required_antibiotics: bool = Field(False, description="Whether antibiotics were required")
    required_steroids: bool = Field(False, description="Whether steroids were required")

    # Optional symptom description
    symptoms: str | None = Field(
        None, max_length=2000, description="Symptom description (e.g., increased cough, sputum)"
    )
    notes: str | None = Field(None, max_length=5000, description="Clinical notes")

    # Validation: hospitalization_days must be > 0 if required_hospitalization = True
    def model_post_init(self, __context):
        if self.required_hospitalization and not self.hospitalization_days:
            raise ValueError("hospitalization_days is required when required_hospitalization is True")
        if not self.required_hospitalization and self.hospitalization_days:
            raise ValueError(
                "hospitalization_days should be None when required_hospitalization is False"
            )


class ExacerbationUpdate(BaseModel):
    """
    Update exacerbation record request (partial update)

    All fields are optional (PATCH semantics)
    """

    model_config = ConfigDict(from_attributes=True)

    onset_date: date | None = Field(None, description="Date of exacerbation onset (YYYY-MM-DD)")
    severity: Literal["MILD", "MODERATE", "SEVERE"] | None = Field(
        None, description="Severity level: MILD, MODERATE, or SEVERE"
    )

    # Treatment information
    required_hospitalization: bool | None = Field(
        None, description="Whether hospitalization was required"
    )
    hospitalization_days: int | None = Field(
        None, ge=1, description="Number of hospitalization days"
    )
    required_antibiotics: bool | None = Field(None, description="Whether antibiotics were required")
    required_steroids: bool | None = Field(None, description="Whether steroids were required")

    # Optional symptom description
    symptoms: str | None = Field(
        None, max_length=2000, description="Symptom description (e.g., increased cough, sputum)"
    )
    notes: str | None = Field(None, max_length=5000, description="Clinical notes")


# ============================================================================
# Exacerbation Response Schemas
# ============================================================================


class ExacerbationResponse(BaseModel):
    """
    Exacerbation record response

    Returns exacerbation details with metadata
    """

    model_config = ConfigDict(from_attributes=True)

    exacerbation_id: UUID
    patient_id: UUID
    onset_date: date
    severity: Literal["MILD", "MODERATE", "SEVERE"]

    # Treatment information
    required_hospitalization: bool
    hospitalization_days: int | None
    required_antibiotics: bool
    required_steroids: bool

    # Symptom description
    symptoms: str | None
    notes: str | None

    # Metadata
    recorded_date: date
    recorded_by: UUID | None

    # Timestamps
    created_at: str  # ISO 8601 format
    updated_at: str  # ISO 8601 format


class ExacerbationListResponse(BaseModel):
    """
    Exacerbation list response with pagination

    Returns paginated list of exacerbations for a patient
    """

    model_config = ConfigDict(from_attributes=True)

    exacerbations: list[ExacerbationResponse] = Field(
        ..., description="List of exacerbation records"
    )
    total: int = Field(..., description="Total number of exacerbations for this patient")
    page: int = Field(..., description="Current page number (0-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


# ============================================================================
# Exacerbation Statistics Schemas
# ============================================================================


class ExacerbationStats(BaseModel):
    """
    Exacerbation statistics for a patient

    Summary metrics for GOLD ABE classification
    """

    model_config = ConfigDict(from_attributes=True)

    patient_id: UUID
    total_exacerbations: int = Field(..., description="Total exacerbations (all time)")
    exacerbations_last_12m: int = Field(..., description="Exacerbations in last 12 months")
    hospitalizations_last_12m: int = Field(..., description="Hospitalizations in last 12 months")
    last_exacerbation_date: date | None = Field(..., description="Date of last exacerbation")
    last_hospitalization_date: date | None = Field(..., description="Date of last hospitalization")

    # Severity breakdown (last 12 months)
    mild_count_12m: int = Field(..., description="Mild exacerbations in last 12 months")
    moderate_count_12m: int = Field(..., description="Moderate exacerbations in last 12 months")
    severe_count_12m: int = Field(..., description="Severe exacerbations in last 12 months")
