"""
Calculate Risk Use Case - GOLD ABE Classification Engine
Sprint 4: Risk Engine - Core business logic for COPD risk assessment
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
from respira_ally.infrastructure.database.models.risk_assessment import RiskAssessmentModel
from respira_ally.infrastructure.database.models.survey_response import SurveyResponseModel

# Type aliases
GoldGroup = Literal["A", "B", "E"]
RiskLevel = Literal["low", "medium", "high", "critical"]


class GoldAbeClassificationEngine:
    """
    GOLD 2011 ABE Classification Engine

    Classification Logic:
    - Group A (Low Risk): CAT<10 AND mMRC<2
    - Group B (Medium Risk): CAT>=10 OR mMRC>=2 (but not both)
    - Group E (High Risk): CAT>=10 AND mMRC>=2

    Hybrid Strategy Mapping (Backward Compatibility):
    - A ’ risk_score: 25, risk_level: 'low'
    - B ’ risk_score: 50, risk_level: 'medium'
    - E ’ risk_score: 75, risk_level: 'high'

    ADR References: ADR-013 v2.0 (GOLD ABE), ADR-014 (Hybrid Strategy)
    """

    @staticmethod
    def classify_gold_group(cat_score: int, mmrc_grade: int) -> GoldGroup:
        """
        Classify patient into GOLD ABE group based on CAT and mMRC scores

        Args:
            cat_score: CAT (COPD Assessment Test) score (0-40)
            mmrc_grade: mMRC (Modified Medical Research Council) grade (0-4)

        Returns:
            GOLD ABE group: 'A', 'B', or 'E'

        Raises:
            ValueError: If scores are out of valid range
        """
        # Input validation
        if not (0 <= cat_score <= 40):
            raise ValueError(f"CAT score must be 0-40, got {cat_score}")
        if not (0 <= mmrc_grade <= 4):
            raise ValueError(f"mMRC grade must be 0-4, got {mmrc_grade}")

        # GOLD ABE Classification Logic
        high_symptoms_cat = cat_score >= 10
        high_symptoms_mmrc = mmrc_grade >= 2

        if high_symptoms_cat and high_symptoms_mmrc:
            return "E"  # High risk: Both CAT>=10 AND mMRC>=2
        elif high_symptoms_cat or high_symptoms_mmrc:
            return "B"  # Medium risk: Either CAT>=10 OR mMRC>=2
        else:
            return "A"  # Low risk: CAT<10 AND mMRC<2

    @staticmethod
    def map_to_legacy_risk(gold_group: GoldGroup) -> tuple[int, RiskLevel]:
        """
        Map GOLD ABE group to legacy risk_score and risk_level

        Hybrid Strategy for backward compatibility (ADR-014)

        Args:
            gold_group: GOLD ABE group ('A', 'B', or 'E')

        Returns:
            Tuple of (risk_score, risk_level)
        """
        mapping = {
            "A": (25, "low"),
            "B": (50, "medium"),
            "E": (75, "high"),
        }
        return mapping[gold_group]


class CalculateRiskUseCase:
    """
    Calculate Risk Use Case - Perform GOLD ABE risk assessment for a patient

    Workflow:
    1. Retrieve latest CAT and mMRC survey scores
    2. Retrieve exacerbation history from patient profile
    3. Classify into GOLD ABE group
    4. Map to legacy risk score/level (backward compatibility)
    5. Save risk assessment record
    6. Return assessment result
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.classifier = GoldAbeClassificationEngine()

    async def execute(self, patient_id: UUID) -> RiskAssessmentModel:
        """
        Execute risk assessment for a patient

        Args:
            patient_id: Patient UUID

        Returns:
            RiskAssessmentModel: Created risk assessment record

        Raises:
            ValueError: If patient not found or missing required survey data
        """
        # Step 1: Verify patient exists and get exacerbation summary
        stmt_patient = select(PatientProfileModel).where(PatientProfileModel.user_id == patient_id)
        result = await self.db.execute(stmt_patient)
        patient = result.scalar_one_or_none()

        if not patient:
            raise ValueError(f"Patient {patient_id} not found")

        # Step 2: Get latest CAT score
        stmt_cat = (
            select(SurveyResponseModel)
            .where(
                SurveyResponseModel.patient_id == patient_id,
                SurveyResponseModel.survey_type == "CAT",
            )
            .order_by(SurveyResponseModel.submitted_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt_cat)
        latest_cat = result.scalar_one_or_none()

        if not latest_cat:
            raise ValueError(f"Patient {patient_id} has no CAT survey responses")

        cat_score = latest_cat.total_score

        # Step 3: Get latest mMRC grade
        stmt_mmrc = (
            select(SurveyResponseModel)
            .where(
                SurveyResponseModel.patient_id == patient_id,
                SurveyResponseModel.survey_type == "mMRC",
            )
            .order_by(SurveyResponseModel.submitted_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt_mmrc)
        latest_mmrc = result.scalar_one_or_none()

        if not latest_mmrc:
            raise ValueError(f"Patient {patient_id} has no mMRC survey responses")

        mmrc_grade = latest_mmrc.total_score

        # Step 4: Get exacerbation counts (from patient profile - auto-updated by trigger)
        exacerbation_count_12m = patient.exacerbation_count_last_12m
        hospitalization_count_12m = patient.hospitalization_count_last_12m

        # Step 5: Classify GOLD ABE group
        gold_group = self.classifier.classify_gold_group(cat_score, mmrc_grade)

        # Step 6: Map to legacy risk score/level (Hybrid Strategy)
        risk_score, risk_level = self.classifier.map_to_legacy_risk(gold_group)

        # Step 7: Create risk assessment record
        assessment = RiskAssessmentModel(
            patient_id=patient_id,
            cat_score=cat_score,
            mmrc_grade=mmrc_grade,
            exacerbation_count_12m=exacerbation_count_12m,
            hospitalization_count_12m=hospitalization_count_12m,
            gold_group=gold_group,
            risk_score=risk_score,
            risk_level=risk_level,
            assessed_at=datetime.utcnow(),
        )

        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)

        return assessment

    async def get_latest_assessment(self, patient_id: UUID) -> RiskAssessmentModel | None:
        """
        Get latest risk assessment for a patient

        Args:
            patient_id: Patient UUID

        Returns:
            Latest RiskAssessmentModel or None if not found
        """
        stmt = (
            select(RiskAssessmentModel)
            .where(RiskAssessmentModel.patient_id == patient_id)
            .order_by(RiskAssessmentModel.assessed_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
