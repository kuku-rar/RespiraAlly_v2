"""
Survey Repository Implementation
Infrastructure Layer - Clean Architecture

Concrete implementation of SurveyRepository interface using SQLAlchemy.
This class handles all database interactions for Survey Response entities.
"""

from datetime import datetime, timedelta
from typing import Literal
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.domain.repositories.survey_repository import SurveyRepository
from respira_ally.infrastructure.database.models.survey_response import SurveyResponseModel


class SurveyRepositoryImpl(SurveyRepository):
    """
    SQLAlchemy implementation of SurveyRepository

    Uses async SQLAlchemy session for database operations.
    All methods are async to support FastAPI's async endpoints.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session

        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    async def create(self, survey_response: SurveyResponseModel) -> SurveyResponseModel:
        """Create a new survey response record"""
        self.db.add(survey_response)
        await self.db.commit()
        await self.db.refresh(survey_response)
        return survey_response

    async def get_by_id(self, response_id: UUID) -> SurveyResponseModel | None:
        """Retrieve survey response by response ID"""
        return await self.db.get(SurveyResponseModel, response_id)

    async def list_by_patient(
        self,
        patient_id: UUID,
        survey_type: Literal["CAT", "mMRC"] | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[SurveyResponseModel], int]:
        """List survey responses for a specific patient"""
        conditions = [SurveyResponseModel.patient_id == patient_id]

        if survey_type:
            conditions.append(SurveyResponseModel.survey_type == survey_type)
        if start_date:
            conditions.append(SurveyResponseModel.submitted_at >= start_date)
        if end_date:
            conditions.append(SurveyResponseModel.submitted_at <= end_date)

        base_query = select(SurveyResponseModel).where(and_(*conditions))

        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Get paginated results
        query = (
            base_query.offset(skip).limit(limit).order_by(SurveyResponseModel.submitted_at.desc())
        )
        result = await self.db.execute(query)
        responses = list(result.scalars().all())

        return responses, total

    async def get_latest_by_patient_and_type(
        self,
        patient_id: UUID,
        survey_type: Literal["CAT", "mMRC"],
    ) -> SurveyResponseModel | None:
        """Get the most recent survey response for a patient and survey type"""
        query = (
            select(SurveyResponseModel)
            .where(
                and_(
                    SurveyResponseModel.patient_id == patient_id,
                    SurveyResponseModel.survey_type == survey_type,
                )
            )
            .order_by(SurveyResponseModel.submitted_at.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def count_by_patient(
        self,
        patient_id: UUID,
        survey_type: Literal["CAT", "mMRC"] | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        """Count survey responses for a patient"""
        conditions = [SurveyResponseModel.patient_id == patient_id]

        if survey_type:
            conditions.append(SurveyResponseModel.survey_type == survey_type)
        if start_date:
            conditions.append(SurveyResponseModel.submitted_at >= start_date)
        if end_date:
            conditions.append(SurveyResponseModel.submitted_at <= end_date)

        query = select(func.count()).select_from(SurveyResponseModel).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def exists(self, response_id: UUID) -> bool:
        """Check if survey response exists"""
        query = (
            select(func.count())
            .select_from(SurveyResponseModel)
            .where(SurveyResponseModel.response_id == response_id)
        )
        result = await self.db.execute(query)
        count = result.scalar() or 0
        return count > 0

    async def delete(self, response_id: UUID) -> bool:
        """Delete survey response record"""
        survey_response = await self.get_by_id(response_id)
        if survey_response:
            await self.db.delete(survey_response)
            await self.db.commit()
            return True
        return False

    async def get_average_score(
        self,
        patient_id: UUID,
        survey_type: Literal["CAT", "mMRC"],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> float | None:
        """Calculate average score for a patient and survey type"""
        conditions = [
            SurveyResponseModel.patient_id == patient_id,
            SurveyResponseModel.survey_type == survey_type,
        ]

        if start_date:
            conditions.append(SurveyResponseModel.submitted_at >= start_date)
        if end_date:
            conditions.append(SurveyResponseModel.submitted_at <= end_date)

        query = (
            select(func.avg(SurveyResponseModel.total_score))
            .select_from(SurveyResponseModel)
            .where(and_(*conditions))
        )
        result = await self.db.execute(query)
        avg_score = result.scalar()

        return float(avg_score) if avg_score is not None else None

    async def get_score_trend(
        self,
        patient_id: UUID,
        survey_type: Literal["CAT", "mMRC"],
        days: int = 30,
    ) -> Literal["IMPROVING", "STABLE", "WORSENING", "INSUFFICIENT_DATA"]:
        """
        Analyze score trend for a patient

        Algorithm:
        - Get all responses in the last N days
        - Compare first half average vs second half average
        - IMPROVING: second half < first half (score decreasing = improving)
        - WORSENING: second half > first half (score increasing = worsening)
        - STABLE: similar scores
        - INSUFFICIENT_DATA: less than 2 responses
        """
        start_date = datetime.now() - timedelta(days=days)

        query = (
            select(SurveyResponseModel)
            .where(
                and_(
                    SurveyResponseModel.patient_id == patient_id,
                    SurveyResponseModel.survey_type == survey_type,
                    SurveyResponseModel.submitted_at >= start_date,
                )
            )
            .order_by(SurveyResponseModel.submitted_at.asc())
        )
        result = await self.db.execute(query)
        responses = list(result.scalars().all())

        if len(responses) < 2:
            return "INSUFFICIENT_DATA"

        # Split into two halves and compare
        midpoint = len(responses) // 2
        first_half = responses[:midpoint]
        second_half = responses[midpoint:]

        first_avg = sum(r.total_score for r in first_half) / len(first_half)
        second_avg = sum(r.total_score for r in second_half) / len(second_half)

        # Threshold for significant change (10% for CAT, 1 point for mMRC)
        threshold = 4.0 if survey_type == "CAT" else 1.0

        if second_avg < first_avg - threshold:
            return "IMPROVING"
        elif second_avg > first_avg + threshold:
            return "WORSENING"
        else:
            return "STABLE"

    async def get_severity_distribution(
        self,
        patient_id: UUID,
        survey_type: Literal["CAT", "mMRC"],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict[str, int]:
        """Get distribution of severity levels for a patient"""
        conditions = [
            SurveyResponseModel.patient_id == patient_id,
            SurveyResponseModel.survey_type == survey_type,
        ]

        if start_date:
            conditions.append(SurveyResponseModel.submitted_at >= start_date)
        if end_date:
            conditions.append(SurveyResponseModel.submitted_at <= end_date)

        query = (
            select(
                SurveyResponseModel.severity_level,
                func.count(SurveyResponseModel.response_id).label("count"),
            )
            .where(and_(*conditions))
            .group_by(SurveyResponseModel.severity_level)
        )
        result = await self.db.execute(query)
        rows = result.all()

        # Initialize with all severity levels
        distribution = {
            "MILD": 0,
            "MODERATE": 0,
            "SEVERE": 0,
            "VERY_SEVERE": 0,
        }

        # Fill in actual counts
        for severity_level, count in rows:
            if severity_level:
                distribution[severity_level] = count

        return distribution
