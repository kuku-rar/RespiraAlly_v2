"""
Risk Assessment Schemas
Pydantic models for Risk Assessment API endpoints

Sprint 4: GOLD ABE Classification System
Supports COPD risk assessment based on CAT, mMRC, and exacerbation history
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# Type aliases
GoldGroup = Literal["A", "B", "E"]
RiskLevel = Literal["low", "medium", "high", "critical"]


# ============================================================================
# Risk Assessment Response Schemas
# ============================================================================


class RiskAssessmentResponse(BaseModel):
    """
    Complete Risk Assessment Response

    Returns full GOLD ABE classification results with all assessment data
    """

    model_config = ConfigDict(from_attributes=True)

    # Assessment ID
    assessment_id: UUID = Field(..., description="Unique assessment ID")
    patient_id: UUID = Field(..., description="Patient UUID")

    # Input Data
    cat_score: int = Field(..., ge=0, le=40, description="CAT (COPD Assessment Test) score (0-40)")
    mmrc_grade: int = Field(..., ge=0, le=4, description="mMRC dyspnea grade (0-4)")
    exacerbation_count_12m: int = Field(
        ..., ge=0, description="Number of exacerbations in last 12 months"
    )
    hospitalization_count_12m: int = Field(
        ..., ge=0, description="Number of hospitalizations in last 12 months"
    )

    # GOLD ABE Classification Result
    gold_group: GoldGroup = Field(
        ..., description="GOLD ABE group: A=low risk, B=medium risk, E=high risk"
    )

    # Backward Compatible Fields (Hybrid Strategy)
    risk_score: int | None = Field(
        None, ge=0, le=100, description="Legacy risk score (0-100) mapped from gold_group"
    )
    risk_level: RiskLevel | None = Field(
        None, description="Legacy risk level mapped from gold_group"
    )

    # Timestamps
    assessed_at: datetime = Field(..., description="Assessment timestamp (UTC)")
    created_at: datetime = Field(..., description="Record creation timestamp (UTC)")


class RiskAssessmentSummary(BaseModel):
    """
    Risk Assessment Summary (for patient list display)

    Lightweight version with essential risk information
    """

    model_config = ConfigDict(from_attributes=True)

    # GOLD ABE Classification
    gold_group: GoldGroup = Field(..., description="GOLD ABE group: A, B, or E")
    risk_level: RiskLevel = Field(..., description="Risk level: low, medium, high, critical")

    # Key Metrics
    cat_score: int = Field(..., description="Latest CAT score")
    mmrc_grade: int = Field(..., description="Latest mMRC grade")
    exacerbation_count_12m: int = Field(..., description="Exacerbations in last 12 months")

    # Timestamp
    assessed_at: datetime = Field(..., description="Assessment timestamp (UTC)")


# ============================================================================
# Risk Assessment Request Schemas
# ============================================================================


class RiskAssessmentCalculateRequest(BaseModel):
    """
    Calculate Risk Assessment Request

    Request body for triggering new risk assessment calculation
    (patient_id can also be provided via path parameter)
    """

    model_config = ConfigDict(from_attributes=True)

    patient_id: UUID = Field(..., description="Patient UUID to assess")


# ============================================================================
# Batch Risk Assessment Schemas (for Dashboard KPIs)
# ============================================================================


class PatientRiskSummary(BaseModel):
    """
    Patient Risk Summary (for Dashboard)

    Used in high-risk patient list and risk statistics
    """

    model_config = ConfigDict(from_attributes=True)

    patient_id: UUID = Field(..., description="Patient UUID")
    patient_name: str | None = Field(None, description="Patient full name")

    # Latest Risk Assessment
    gold_group: GoldGroup = Field(..., description="GOLD ABE group")
    risk_level: RiskLevel = Field(..., description="Risk level")
    risk_score: int = Field(..., description="Risk score (0-100)")

    # Risk Trend
    previous_gold_group: GoldGroup | None = Field(
        None, description="Previous GOLD group (for trend analysis)"
    )
    trend: Literal["improving", "stable", "worsening", "unknown"] | None = Field(
        None, description="Risk trend: improving, stable, worsening, or unknown"
    )

    # Key Metrics
    cat_score: int = Field(..., description="Latest CAT score")
    mmrc_grade: int = Field(..., description="Latest mMRC grade")
    exacerbation_count_12m: int = Field(..., description="Exacerbations in last 12 months")
    hospitalization_count_12m: int = Field(..., description="Hospitalizations in last 12 months")

    # Timestamp
    assessed_at: datetime = Field(..., description="Latest assessment timestamp")


class RiskStatistics(BaseModel):
    """
    Risk Statistics (for Dashboard)

    Aggregate statistics across all patients managed by therapist
    """

    model_config = ConfigDict(from_attributes=True)

    total_patients: int = Field(..., description="Total number of patients")

    # Risk Distribution
    low_risk_count: int = Field(..., description="Number of Group A patients")
    medium_risk_count: int = Field(..., description="Number of Group B patients")
    high_risk_count: int = Field(..., description="Number of Group E patients")
    not_assessed_count: int = Field(..., description="Number of patients without assessment")

    # Percentages
    low_risk_percentage: float = Field(..., description="Percentage of low-risk patients")
    medium_risk_percentage: float = Field(..., description="Percentage of medium-risk patients")
    high_risk_percentage: float = Field(..., description="Percentage of high-risk patients")

    # Trend Summary
    patients_worsening: int = Field(
        ..., description="Number of patients with worsening risk trend"
    )
    patients_improving: int = Field(..., description="Number of patients with improving risk trend")
