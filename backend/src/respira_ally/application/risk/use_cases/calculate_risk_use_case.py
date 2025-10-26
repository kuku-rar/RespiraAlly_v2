"""
Calculate Risk Use Case - Orchestrate COPD Risk Assessment
Sprint 4: Risk Engine - Application layer orchestration

This Use Case is responsible for:
1. Gathering data from infrastructure (database queries)
2. Delegating business logic to Domain Service (RiskAssessmentService)
3. Persisting results to database
4. Triggering side effects (alert creation)

Following Clean Architecture:
- Application Layer: Orchestration and coordination
- Domain Layer: Business logic and rules (RiskAssessmentService)
- Infrastructure Layer: Database access

Sprint 4 P1: Auto-trigger Alert creation after risk assessment
"""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.domain.repositories.patient_repository import PatientRepository
from respira_ally.domain.services.risk_assessment_service import (
    RiskAssessmentInput,
    RiskAssessmentService,
)
from respira_ally.infrastructure.database.models.risk_assessment import RiskAssessmentModel
from respira_ally.infrastructure.database.models.survey_response import SurveyResponseModel

logger = logging.getLogger(__name__)


class CalculateRiskUseCase:
    """
    Calculate Risk Use Case - Orchestrate COPD risk assessment

    Refactored Architecture (DDD):
    - Application Layer (this class): Data gathering + orchestration
    - Domain Layer (RiskAssessmentService): Pure business logic

    Workflow:
    1. Retrieve latest CAT and mMRC survey scores (Infrastructure)
    2. Retrieve exacerbation history from patient profile (Infrastructure)
    3. Delegate risk calculation to Domain Service (Domain)
    4. Persist risk assessment record (Infrastructure)
    5. Trigger alert creation (Side effect)
    6. Return assessment result

    Design Note (Linus):
        "Bad programmers worry about the code. Good programmers worry about
        data structures and their relationships."

        This Use Case is now THIN - it just gathers data, delegates to
        domain service, and saves results. No business logic here.
    """

    def __init__(self, db_session: AsyncSession, patient_repository: PatientRepository):
        """
        Initialize Use Case with dependencies

        Args:
            db_session: Database session for data access
            patient_repository: Patient repository for accessing patient data
        """
        self.db = db_session
        self.patient_repo = patient_repository
        self.risk_service = RiskAssessmentService()

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
        patient = await self.patient_repo.get_by_id(patient_id)

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

        # Step 5: Delegate risk calculation to Domain Service
        # This is where Clean Architecture shines - business logic is separate from orchestration
        input_data = RiskAssessmentInput(
            cat_score=cat_score,
            mmrc_grade=mmrc_grade,
            exacerbation_count_12m=exacerbation_count_12m,
            hospitalization_count_12m=hospitalization_count_12m,
        )

        risk_result = self.risk_service.calculate_risk(input_data)

        # Step 6: Create risk assessment record (persistence)
        # Map Domain Service result to database model
        assessment = RiskAssessmentModel(
            patient_id=patient_id,
            cat_score=cat_score,
            mmrc_grade=mmrc_grade,
            exacerbation_count_12m=exacerbation_count_12m,
            hospitalization_count_12m=hospitalization_count_12m,
            gold_group=risk_result.gold_group,
            risk_score=risk_result.risk_score,
            risk_level=risk_result.risk_level,
            assessed_at=datetime.utcnow(),
        )

        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)

        # Sprint 4 P1: Auto-trigger Alert creation
        # TODO(DEBT-001): Alerts are created automatically after risk assessment
        await self._create_alerts_if_needed(assessment)

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

    async def _create_alerts_if_needed(self, assessment: RiskAssessmentModel) -> None:
        """
        Auto-trigger Alert creation after risk assessment

        Sprint 4 P1 Requirement: Automatically create alerts when risk assessment
        triggers alert rules (GOLD Group E, High CAT Score, Frequent Exacerbations).

        Args:
            assessment: The newly created risk assessment

        Design Note (Linus):
            This method is PRIVATE (_create_alerts_if_needed) because alert creation
            is an implementation detail of risk assessment. The public API (execute())
            remains clean - callers don't need to know about alerts.

            "Good taste means hiding complexity, not exposing it."

        Error Handling:
            Errors are logged but not raised - alert creation failure should NOT
            block risk assessment. Risk assessment is the primary operation.
        """
        try:
            # Import here to avoid circular dependency
            # (AlertService imports RiskAssessmentModel, CalculateRiskUseCase imports AlertService)
            from respira_ally.application.alert.alert_service import AlertService

            alert_service = AlertService(self.db)

            # Create alerts based on risk assessment rules
            created_alerts = await alert_service.create_alerts_from_risk_assessment(assessment)

            if created_alerts:
                logger.info(
                    f"Created {len(created_alerts)} alert(s) for patient {assessment.patient_id} "
                    f"after risk assessment (GOLD: {assessment.gold_group})"
                )
            else:
                logger.debug(
                    f"No alerts triggered for patient {assessment.patient_id} "
                    f"(GOLD: {assessment.gold_group})"
                )

        except Exception as e:
            # Alert creation failure should not block risk assessment
            logger.error(
                f"Failed to create alerts for patient {assessment.patient_id} "
                f"after risk assessment: {e}",
                exc_info=True,
            )
