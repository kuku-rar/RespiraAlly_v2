"""
Daily Log Schemas
Pydantic models for Daily Log API endpoints
"""
from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Base Schemas
# ============================================================================

class DailyLogBase(BaseModel):
    """Base daily log information (shared fields)"""
    log_date: date = Field(..., description="Date of the log entry")
    medication_taken: bool = Field(..., description="Whether medication was taken")
    water_intake_ml: int = Field(..., ge=0, le=10000, description="Water intake in milliliters")
    steps_count: int | None = Field(None, ge=0, le=100000, description="Daily step count")
    symptoms: str | None = Field(None, max_length=500, description="Reported symptoms")
    mood: Literal["GOOD", "NEUTRAL", "BAD"] | None = Field(None, description="Patient mood")


# ============================================================================
# Request Schemas
# ============================================================================

class DailyLogCreate(DailyLogBase):
    """
    Daily Log Creation Request
    Patients submit daily health logs via LIFF
    """
    patient_id: UUID = Field(..., description="Patient user ID")


class DailyLogUpdate(BaseModel):
    """
    Daily Log Update Request
    All fields optional for partial updates
    """
    medication_taken: bool | None = None
    water_intake_ml: int | None = Field(None, ge=0, le=10000)
    steps_count: int | None = Field(None, ge=0, le=100000)
    symptoms: str | None = Field(None, max_length=500)
    mood: Literal["GOOD", "NEUTRAL", "BAD"] | None = None


# ============================================================================
# Response Schemas
# ============================================================================

class DailyLogResponse(DailyLogBase):
    """
    Daily Log API Response
    Returns complete daily log information
    """
    log_id: UUID = Field(..., description="Unique log ID")
    patient_id: UUID = Field(..., description="Patient user ID")
    created_at: datetime = Field(..., description="Log creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class DailyLogListResponse(BaseModel):
    """
    Daily Log List Response (with pagination)
    """
    items: list[DailyLogResponse]
    total: int = Field(..., description="Total number of logs")
    page: int = Field(..., description="Current page (0-indexed)")
    page_size: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Has next page")


# ============================================================================
# Query Schemas
# ============================================================================

class DailyLogQuery(BaseModel):
    """
    Query parameters for filtering daily logs
    """
    patient_id: UUID | None = Field(None, description="Filter by patient ID")
    start_date: date | None = Field(None, description="Filter logs from this date (inclusive)")
    end_date: date | None = Field(None, description="Filter logs until this date (inclusive)")
    mood: Literal["GOOD", "NEUTRAL", "BAD"] | None = Field(None, description="Filter by mood")
    medication_taken: bool | None = Field(None, description="Filter by medication compliance")


# ============================================================================
# Statistics Schemas
# ============================================================================

class DailyLogStats(BaseModel):
    """
    Daily log statistics for a patient
    """
    total_logs: int = Field(..., description="Total number of logs")
    medication_adherence_rate: float = Field(..., ge=0, le=100, description="Medication adherence percentage")
    avg_water_intake_ml: float = Field(..., description="Average daily water intake")
    avg_steps_count: float | None = Field(None, description="Average daily steps")
    mood_distribution: dict[str, int] = Field(..., description="Count of each mood type")
    date_range: dict[str, date] = Field(..., description="Start and end dates of logs")
