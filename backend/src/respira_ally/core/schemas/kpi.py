"""
KPI Schemas
Pydantic models for Patient KPI API endpoints

Sprint 4: Risk Engine & Dashboard KPI
Based on frontend TypeScript interface: PatientKPI
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ============================================================================
# KPI Response Schemas
# ============================================================================


class PatientKPIResponse(BaseModel):
    """
    Patient KPI Response - Dashboard health metrics

    Includes:
    - Adherence metrics (medication, log submission, surveys)
    - Health metrics (BMI, SpO2, heart rate, blood pressure)
    - Survey scores (CAT, mMRC)
    - GOLD ABE risk assessment
    - Legacy risk fields (backward compatibility)
    - Activity tracking

    Hybrid Strategy (ADR-014): Returns both GOLD ABE and legacy risk fields
    """

    model_config = ConfigDict(from_attributes=True)

    # Identity
    patient_id: UUID = Field(..., description="Patient UUID")
    updated_at: str = Field(..., description="Last update timestamp (ISO 8601)")

    # Adherence Metrics (0-100 percentage)
    medication_adherence_rate: float | None = Field(
        None, ge=0, le=100, description="Medication adherence rate (%)"
    )
    log_submission_rate: float | None = Field(
        None, ge=0, le=100, description="Daily log submission rate (%)"
    )
    survey_completion_rate: float | None = Field(
        None, ge=0, le=100, description="Survey completion rate (%)"
    )

    # Health Metrics
    latest_bmi: float | None = Field(None, description="Latest BMI value")
    latest_spo2: int | None = Field(None, ge=0, le=100, description="Latest SpO2 (%)")
    latest_heart_rate: int | None = Field(None, ge=0, le=300, description="Latest heart rate (bpm)")
    latest_systolic_bp: int | None = Field(
        None, ge=0, le=300, description="Latest systolic blood pressure (mmHg)"
    )
    latest_diastolic_bp: int | None = Field(
        None, ge=0, le=200, description="Latest diastolic blood pressure (mmHg)"
    )

    # Survey Scores
    latest_cat_score: int | None = Field(
        None, ge=0, le=40, description="Latest CAT score (COPD Assessment Test)"
    )
    latest_mmrc_score: int | None = Field(
        None, ge=0, le=4, description="Latest mMRC score (dyspnea scale)"
    )

    # GOLD ABE Risk Assessment (Sprint 4)
    gold_group: Literal["A", "B", "E"] | None = Field(
        None, description="GOLD 2011 ABE classification (A=low, B=medium, E=high)"
    )
    exacerbation_count_last_12m: int | None = Field(
        None, description="Number of exacerbations in last 12 months"
    )
    hospitalization_count_last_12m: int | None = Field(
        None, description="Number of hospitalizations in last 12 months"
    )
    last_exacerbation_date: str | None = Field(
        None, description="Last exacerbation date (YYYY-MM-DD)"
    )

    # Legacy Risk Fields (Hybrid Strategy - Backward Compatible)
    # Deprecated in Sprint 4 - Prefer using gold_group
    risk_score: int | None = Field(
        None,
        ge=0,
        le=100,
        description="Legacy risk score (0-100) - Mapped from gold_group",
    )
    risk_level: Literal["low", "medium", "high", "critical"] | None = Field(
        None, description="Legacy risk level - Mapped from gold_group"
    )

    # Activity Tracking
    last_log_date: str | None = Field(None, description="Last daily log date (YYYY-MM-DD)")
    days_since_last_log: int | None = Field(None, description="Days since last log submission")


# ============================================================================
# Risk Assessment Schemas
# ============================================================================


class RiskAssessmentResponse(BaseModel):
    """Risk assessment result"""

    model_config = ConfigDict(from_attributes=True)

    assessment_id: UUID
    patient_id: UUID
    cat_score: int = Field(..., ge=0, le=40)
    mmrc_grade: int = Field(..., ge=0, le=4)
    exacerbation_count_12m: int
    hospitalization_count_12m: int
    gold_group: Literal["A", "B", "E"]
    risk_score: int | None = Field(None, ge=0, le=100)
    risk_level: Literal["low", "medium", "high", "critical"] | None
    assessed_at: datetime
