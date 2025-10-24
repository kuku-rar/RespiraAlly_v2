"""
KPI Service - Patient health metrics aggregation
Sprint 4: Dashboard KPI - Aggregate patient health metrics for dashboard display
"""

from datetime import date, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.application.risk.use_cases.calculate_risk_use_case import CalculateRiskUseCase
from respira_ally.core.schemas.kpi import PatientKPIResponse
from respira_ally.infrastructure.database.models.daily_log import DailyLogModel
from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
from respira_ally.infrastructure.database.models.survey_response import SurveyResponseModel


class KPIService:
    """
    KPI Service - Aggregate patient health metrics

    Aggregates metrics from multiple sources:
    - Adherence: medication, daily logs, surveys
    - Health: BMI, vitals from latest daily log
    - Risk: GOLD ABE classification (via RiskAssessmentModel)
    - Activity: log submission tracking
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.risk_calculator = CalculateRiskUseCase(db)

    async def get_patient_kpi(self, patient_id: UUID, refresh: bool = False) -> PatientKPIResponse:
        """
        Get comprehensive KPI metrics for a patient

        Args:
            patient_id: Patient UUID
            refresh: If True, force recalculate risk assessment

        Returns:
            PatientKPIResponse with aggregated metrics

        Raises:
            ValueError: If patient not found
        """
        # 1. Verify patient exists
        patient = await self.db.get(PatientProfileModel, patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")

        # 2. Get adherence metrics (last 30 days)
        adherence = await self._calculate_adherence_metrics(patient_id)

        # 3. Get latest health metrics from daily logs
        health = await self._get_latest_health_metrics(patient_id)

        # 4. Get latest survey scores
        surveys = await self._get_latest_survey_scores(patient_id)

        # 5. Get or calculate risk assessment
        if refresh:
            # Force recalculate
            try:
                risk_assessment = await self.risk_calculator.execute(patient_id)
            except ValueError:
                # No survey data available - skip risk assessment
                risk_assessment = None
        else:
            # Get latest assessment
            risk_assessment = await self.risk_calculator.get_latest_assessment(patient_id)

        # 6. Get activity tracking
        activity = await self._get_activity_tracking(patient_id)

        # 7. Build KPI response (Hybrid Strategy)
        return PatientKPIResponse(
            patient_id=patient_id,
            updated_at=datetime.utcnow().isoformat(),
            # Adherence
            medication_adherence_rate=adherence.get("medication"),
            log_submission_rate=adherence.get("log"),
            survey_completion_rate=adherence.get("survey"),
            # Health
            latest_bmi=health.get("bmi"),
            latest_spo2=health.get("spo2"),
            latest_heart_rate=health.get("heart_rate"),
            latest_systolic_bp=health.get("systolic_bp"),
            latest_diastolic_bp=health.get("diastolic_bp"),
            # Surveys
            latest_cat_score=surveys.get("cat_score"),
            latest_mmrc_score=surveys.get("mmrc_score"),
            # GOLD ABE Risk (Sprint 4)
            gold_group=risk_assessment.gold_group if risk_assessment else None,
            exacerbation_count_last_12m=patient.exacerbation_count_last_12m,
            hospitalization_count_last_12m=patient.hospitalization_count_last_12m,
            last_exacerbation_date=(
                patient.last_exacerbation_date.isoformat() if patient.last_exacerbation_date else None
            ),
            # Legacy Risk (Backward Compatible)
            risk_score=risk_assessment.risk_score if risk_assessment else None,
            risk_level=risk_assessment.risk_level if risk_assessment else None,
            # Activity
            last_log_date=activity.get("last_log_date"),
            days_since_last_log=activity.get("days_since_last_log"),
        )

    async def _calculate_adherence_metrics(self, patient_id: UUID) -> dict[str, float | None]:
        """Calculate adherence rates for last 30 days"""
        start_date = date.today() - timedelta(days=30)

        # Log submission rate (expected: 1 per day = 30 logs)
        stmt = select(func.count(DailyLogModel.log_id)).where(
            DailyLogModel.patient_id == patient_id,
            DailyLogModel.log_date >= start_date,
        )
        result = await self.db.execute(stmt)
        log_count = result.scalar_one()
        log_rate = (log_count / 30) * 100 if log_count else 0.0

        # Medication adherence rate (from daily logs)
        # Simplified: percentage of logs where medication_taken = True
        stmt = select(func.count(DailyLogModel.log_id)).where(
            DailyLogModel.patient_id == patient_id,
            DailyLogModel.log_date >= start_date,
            DailyLogModel.values["medication_taken"].astext.cast(bool) == True,  # noqa: E712
        )
        result = await self.db.execute(stmt)
        medication_count = result.scalar_one()
        medication_rate = (medication_count / log_count * 100) if log_count > 0 else None

        # Survey completion rate (expected: 1 CAT + 1 mMRC per month = 2)
        stmt = select(func.count(SurveyResponseModel.response_id)).where(
            SurveyResponseModel.patient_id == patient_id,
            SurveyResponseModel.submitted_at >= datetime.now() - timedelta(days=30),
        )
        result = await self.db.execute(stmt)
        survey_count = result.scalar_one()
        survey_rate = (survey_count / 2) * 100 if survey_count else 0.0

        return {
            "medication": medication_rate,
            "log": log_rate,
            "survey": min(survey_rate, 100.0),  # Cap at 100%
        }

    async def _get_latest_health_metrics(self, patient_id: UUID) -> dict[str, Any]:
        """Get latest health vitals from daily logs"""
        stmt = (
            select(DailyLogModel)
            .where(DailyLogModel.patient_id == patient_id)
            .order_by(DailyLogModel.log_date.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        latest_log = result.scalar_one_or_none()

        if not latest_log:
            return {}

        # Extract vitals from JSONB values
        values = latest_log.values or {}

        # Calculate BMI if height/weight available
        patient = await self.db.get(PatientProfileModel, patient_id)
        bmi = None
        if patient and patient.height_cm and patient.weight_kg:
            height_m = patient.height_cm / 100
            bmi = float(patient.weight_kg) / (height_m**2)

        return {
            "bmi": round(bmi, 1) if bmi else None,
            "spo2": values.get("spo2"),
            "heart_rate": values.get("heart_rate"),
            "systolic_bp": values.get("systolic_bp"),
            "diastolic_bp": values.get("diastolic_bp"),
        }

    async def _get_latest_survey_scores(self, patient_id: UUID) -> dict[str, int | None]:
        """Get latest CAT and mMRC scores"""
        # Latest CAT score
        stmt_cat = (
            select(SurveyResponseModel.total_score)
            .where(
                SurveyResponseModel.patient_id == patient_id,
                SurveyResponseModel.survey_type == "CAT",
            )
            .order_by(SurveyResponseModel.submitted_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt_cat)
        cat_score = result.scalar_one_or_none()

        # Latest mMRC score
        stmt_mmrc = (
            select(SurveyResponseModel.total_score)
            .where(
                SurveyResponseModel.patient_id == patient_id,
                SurveyResponseModel.survey_type == "mMRC",
            )
            .order_by(SurveyResponseModel.submitted_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt_mmrc)
        mmrc_score = result.scalar_one_or_none()

        return {
            "cat_score": cat_score,
            "mmrc_score": mmrc_score,
        }

    async def _get_activity_tracking(self, patient_id: UUID) -> dict[str, Any]:
        """Get last log date and days since"""
        stmt = (
            select(DailyLogModel.log_date)
            .where(DailyLogModel.patient_id == patient_id)
            .order_by(DailyLogModel.log_date.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        last_log_date = result.scalar_one_or_none()

        if not last_log_date:
            return {"last_log_date": None, "days_since_last_log": None}

        days_since = (date.today() - last_log_date).days

        return {
            "last_log_date": last_log_date.isoformat(),
            "days_since_last_log": days_since,
        }
