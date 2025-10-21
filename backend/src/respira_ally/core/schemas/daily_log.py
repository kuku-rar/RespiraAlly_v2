"""
Daily Log Schemas
Pydantic models for Daily Log API endpoints
"""
from datetime import date, datetime, timedelta
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ============================================================================
# Base Schemas
# ============================================================================

class DailyLogBase(BaseModel):
    """Base daily log information (all fields optional except log_date)"""
    log_date: date = Field(..., description="Date of the log entry (ONLY required field)")
    medication_taken: bool | None = Field(None, description="Whether medication was taken (NULL = not recorded)")
    water_intake_ml: int | None = Field(None, ge=0, le=10000, description="Water intake in milliliters (NULL = not recorded)")
    exercise_minutes: int | None = Field(None, ge=0, le=480, description="Exercise duration in minutes (0-480, max 8 hours)")
    smoking_count: int | None = Field(None, ge=0, le=100, description="Number of cigarettes smoked (COPD risk factor)")
    symptoms: str | None = Field(None, max_length=500, description="Reported symptoms")
    mood: Literal["GOOD", "NEUTRAL", "BAD"] | None = Field(None, description="Patient mood")

    @field_validator("log_date")
    @classmethod
    def validate_log_date(cls, v: date) -> date:
        """
        Validate log date is not in the future and within reasonable past range

        Rules:
        - Cannot be future date
        - Cannot be older than 365 days
        """
        today = date.today()

        if v > today:
            raise ValueError("Log date cannot be in the future")

        oldest_allowed = today - timedelta(days=365)
        if v < oldest_allowed:
            raise ValueError("Log date cannot be older than 365 days")

        return v

    @field_validator("water_intake_ml")
    @classmethod
    def validate_water_intake(cls, v: int | None) -> int | None:
        """
        Validate water intake for COPD patients

        Warning ranges:
        - <500ml: Dehydration risk (COPD patients need adequate hydration)
        - >5000ml: Excessive intake (normal: 2000-3000ml)
        """
        if v is None:
            return v

        if v < 500:
            # Note: This is a warning, not an error. We allow the value but log it.
            # In production, this could trigger a notification to therapist
            pass
        elif v > 5000:
            # Similarly, high intake is allowed but should be monitored
            pass

        return v

    @field_validator("exercise_minutes")
    @classmethod
    def validate_exercise_minutes(cls, v: int | None) -> int | None:
        """
        Validate exercise duration for COPD patients

        Warning ranges:
        - <10 minutes: Insufficient activity (COPD patients need regular exercise)
        - >120 minutes: Excessive activity (may strain COPD patients)

        Recommended: 30-60 minutes of moderate exercise daily
        """
        if v is None:
            return v

        if v < 10:
            # Low activity warning
            pass
        elif v > 120:
            # High activity warning (potential over-exertion)
            pass

        return v

    @field_validator("smoking_count")
    @classmethod
    def validate_smoking_count(cls, v: int | None) -> int | None:
        """
        Validate smoking count (CRITICAL for COPD management)

        ANY smoking is a risk factor for COPD progression!

        Alert ranges:
        - ≥1 cigarette: Should trigger therapist notification for cessation support
        - ≥10 cigarettes: High-risk behavior, immediate intervention needed
        """
        if v is None:
            return v

        if v >= 1:
            # CRITICAL: Any smoking should alert therapist
            # In production, this should trigger immediate notification
            pass

        return v

    @field_validator("symptoms")
    @classmethod
    def validate_symptoms(cls, v: str | None) -> str | None:
        """
        Validate symptoms and check for critical keywords

        Critical keywords that should alert therapist:
        - "無法呼吸", "不能呼吸", "呼吸困難"
        - "胸痛", "胸悶"
        - "暈倒", "昏倒", "失去意識"
        - "咳血", "吐血"
        """
        if v is None:
            return v

        critical_keywords = [
            "無法呼吸", "不能呼吸", "呼吸困難", "喘不過氣",
            "胸痛", "胸悶", "心臟痛",
            "暈倒", "昏倒", "失去意識", "昏迷",
            "咳血", "吐血", "血痰"
        ]

        v_lower = v.lower()
        for keyword in critical_keywords:
            if keyword.lower() in v_lower:
                # In production, this should trigger immediate alert to therapist
                # For now, we just validate the data is stored
                pass

        return v


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
    exercise_minutes: int | None = Field(None, ge=0, le=480)
    smoking_count: int | None = Field(None, ge=0, le=100)
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
    avg_water_intake_ml: float | None = Field(None, description="Average daily water intake (NULL if no data)")
    avg_exercise_minutes: float | None = Field(None, description="Average daily exercise duration in minutes")
    avg_smoking_count: float | None = Field(None, description="Average daily cigarette count (COPD risk tracking)")
    mood_distribution: dict[str, int] = Field(..., description="Count of each mood type")
    date_range: dict[str, date] = Field(..., description="Start and end dates of logs")
