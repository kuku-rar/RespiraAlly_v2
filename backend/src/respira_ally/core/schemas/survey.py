"""
Survey Schemas - CAT and mMRC questionnaire schemas
Pydantic models for Survey API endpoints
"""
from datetime import datetime
from typing import Dict, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================================================
# CAT (COPD Assessment Test) Schemas
# ============================================================================

class CATSurveyAnswers(BaseModel):
    """
    CAT Survey Answers (8 questions, each 0-5 points)

    CAT evaluates COPD impact on daily life across 8 dimensions:
    1. Cough frequency
    2. Mucus in chest
    3. Chest tightness
    4. Breathlessness going uphill/stairs
    5. Activity limitations at home
    6. Confidence leaving home
    7. Sleep quality
    8. Energy level

    Each question: 0 (best) to 5 (worst)
    """
    q1_cough: int = Field(..., ge=0, le=5, description="咳嗽頻率 (0=從不咳嗽, 5=總是咳嗽)")
    q2_mucus: int = Field(..., ge=0, le=5, description="胸部有痰 (0=完全沒有, 5=充滿痰液)")
    q3_chest_tightness: int = Field(..., ge=0, le=5, description="胸部緊繃感 (0=完全不緊, 5=非常緊)")
    q4_breathlessness_stairs: int = Field(..., ge=0, le=5, description="爬坡/樓梯時喘不過氣 (0=不會, 5=非常喘)")
    q5_activity_limitation: int = Field(..., ge=0, le=5, description="居家活動受限 (0=無限制, 5=非常受限)")
    q6_confidence_leaving_home: int = Field(..., ge=0, le=5, description="外出信心 (0=很有信心, 5=完全沒信心)")
    q7_sleep_quality: int = Field(..., ge=0, le=5, description="睡眠品質 (0=睡得很好, 5=睡不好)")
    q8_energy_level: int = Field(..., ge=0, le=5, description="精力充沛程度 (0=充滿精力, 5=完全沒精力)")

    @field_validator('*')
    @classmethod
    def validate_score_range(cls, v: int) -> int:
        """Validate each answer is within 0-5 range"""
        if not (0 <= v <= 5):
            raise ValueError("CAT answer must be between 0 and 5")
        return v


class CATSurveyCreate(BaseModel):
    """CAT Survey submission request"""
    patient_id: UUID = Field(..., description="Patient user ID")
    answers: CATSurveyAnswers = Field(..., description="CAT survey answers (8 questions)")


# ============================================================================
# mMRC (Modified Medical Research Council) Schemas
# ============================================================================

class mMRCSurveyAnswers(BaseModel):
    """
    mMRC Dyspnea Scale Answer (single question, 5 grades)

    Measures breathlessness severity:
    - Grade 0: Only breathless with strenuous exercise
    - Grade 1: Short of breath when hurrying on level or walking up slight hill
    - Grade 2: Walks slower than people of same age on level, or stops for breath
    - Grade 3: Stops for breath after walking 100 meters or a few minutes on level
    - Grade 4: Too breathless to leave house or breathless when dressing/undressing
    """
    grade: int = Field(..., ge=0, le=4, description="mMRC dyspnea grade (0=best, 4=worst)")

    @field_validator('grade')
    @classmethod
    def validate_grade_range(cls, v: int) -> int:
        """Validate grade is within 0-4 range"""
        if not (0 <= v <= 4):
            raise ValueError("mMRC grade must be between 0 and 4")
        return v


class mMRCSurveyCreate(BaseModel):
    """mMRC Survey submission request"""
    patient_id: UUID = Field(..., description="Patient user ID")
    answers: mMRCSurveyAnswers = Field(..., description="mMRC dyspnea grade")


# ============================================================================
# Common Response Schemas
# ============================================================================

class SurveyResponse(BaseModel):
    """
    Survey response (both CAT and mMRC)
    """
    response_id: UUID = Field(..., description="Unique response ID")
    survey_type: Literal["CAT", "mMRC"] = Field(..., description="Survey type")
    patient_id: UUID = Field(..., description="Patient user ID")
    answers: Dict[str, int] = Field(..., description="Survey answers as JSON")
    total_score: int = Field(..., description="Calculated total score")
    severity_level: Literal["MILD", "MODERATE", "SEVERE", "VERY_SEVERE"] | None = Field(
        None, description="Calculated severity level (CAT only)"
    )
    submitted_at: datetime = Field(..., description="Submission timestamp")

    model_config = ConfigDict(from_attributes=True)


class SurveyListResponse(BaseModel):
    """Survey list response (with pagination)"""
    items: list[SurveyResponse]
    total: int = Field(..., description="Total number of surveys")
    page: int = Field(..., description="Current page (0-indexed)")
    page_size: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Has next page")


# ============================================================================
# Statistics Schemas
# ============================================================================

class SurveyStats(BaseModel):
    """
    Survey statistics for a patient
    """
    survey_type: Literal["CAT", "mMRC"]
    total_responses: int = Field(..., description="Total number of responses")
    latest_score: int | None = Field(None, description="Most recent score")
    latest_severity: Literal["MILD", "MODERATE", "SEVERE", "VERY_SEVERE"] | None = Field(
        None, description="Most recent severity level (CAT only)"
    )
    avg_score: float | None = Field(None, description="Average score over time")
    trend: Literal["IMPROVING", "STABLE", "WORSENING", "INSUFFICIENT_DATA"] = Field(
        ..., description="Score trend over time"
    )
    date_range: dict = Field(..., description="Date range of responses")
