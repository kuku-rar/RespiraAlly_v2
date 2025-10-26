"""
Daily Log Repository Implementation
Infrastructure Layer - Clean Architecture

Concrete implementation of DailyLogRepository interface using SQLAlchemy.
This class handles all database interactions for DailyLog entities.
"""

from datetime import date
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.domain.repositories.daily_log_repository import DailyLogRepository
from respira_ally.infrastructure.database.models.daily_log import DailyLogModel


class DailyLogRepositoryImpl(DailyLogRepository):
    """
    SQLAlchemy implementation of DailyLogRepository

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

    async def create(self, daily_log: DailyLogModel) -> DailyLogModel:
        """Create a new daily log record"""
        self.db.add(daily_log)
        await self.db.commit()
        await self.db.refresh(daily_log)
        return daily_log

    async def get_by_id(self, log_id: UUID) -> DailyLogModel | None:
        """Retrieve daily log by log ID"""
        return await self.db.get(DailyLogModel, log_id)

    async def get_by_patient_and_date(
        self, patient_id: UUID, log_date: date
    ) -> DailyLogModel | None:
        """Retrieve daily log for specific patient and date"""
        query = select(DailyLogModel).where(
            and_(
                DailyLogModel.patient_id == patient_id,
                DailyLogModel.log_date == log_date,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_by_patient(
        self,
        patient_id: UUID,
        start_date: date | None = None,
        end_date: date | None = None,
        skip: int = 0,
        limit: int = 30,
    ) -> tuple[list[DailyLogModel], int]:
        """List daily logs for a specific patient"""
        conditions = [DailyLogModel.patient_id == patient_id]
        if start_date:
            conditions.append(DailyLogModel.log_date >= start_date)
        if end_date:
            conditions.append(DailyLogModel.log_date <= end_date)

        base_query = select(DailyLogModel).where(and_(*conditions))

        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Get paginated results
        query = base_query.offset(skip).limit(limit).order_by(DailyLogModel.log_date.desc())
        result = await self.db.execute(query)
        logs = list(result.scalars().all())

        return logs, total

    async def list_by_date_range(
        self,
        start_date: date,
        end_date: date,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[DailyLogModel], int]:
        """List all daily logs within a date range"""
        base_query = select(DailyLogModel).where(
            and_(
                DailyLogModel.log_date >= start_date,
                DailyLogModel.log_date <= end_date,
            )
        )

        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        query = (
            base_query.offset(skip)
            .limit(limit)
            .order_by(DailyLogModel.log_date.desc(), DailyLogModel.patient_id)
        )
        result = await self.db.execute(query)
        logs = list(result.scalars().all())

        return logs, total

    async def update(
        self,
        log_id: UUID,
        update_data: dict,
    ) -> DailyLogModel | None:
        """Update daily log information"""
        daily_log = await self.get_by_id(log_id)
        if not daily_log:
            return None

        for key, value in update_data.items():
            if value is not None and hasattr(daily_log, key):
                setattr(daily_log, key, value)

        await self.db.commit()
        await self.db.refresh(daily_log)
        return daily_log

    async def delete(self, log_id: UUID) -> bool:
        """Delete daily log record"""
        daily_log = await self.get_by_id(log_id)
        if not daily_log:
            return False

        await self.db.delete(daily_log)
        await self.db.commit()
        return True

    async def exists(self, log_id: UUID) -> bool:
        """Check if daily log exists"""
        query = select(func.count()).where(DailyLogModel.log_id == log_id)
        result = await self.db.execute(query)
        count = result.scalar()
        return count > 0

    async def count_by_patient(
        self,
        patient_id: UUID,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> int:
        """Count daily logs for a patient"""
        conditions = [DailyLogModel.patient_id == patient_id]
        if start_date:
            conditions.append(DailyLogModel.log_date >= start_date)
        if end_date:
            conditions.append(DailyLogModel.log_date <= end_date)

        query = select(func.count()).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_medication_adherence(
        self, patient_id: UUID, start_date: date, end_date: date
    ) -> float:
        """Calculate medication adherence rate for a patient"""
        total_query = select(func.count()).where(
            and_(
                DailyLogModel.patient_id == patient_id,
                DailyLogModel.log_date >= start_date,
                DailyLogModel.log_date <= end_date,
            )
        )
        total_result = await self.db.execute(total_query)
        total_logs = total_result.scalar() or 0

        if total_logs == 0:
            return 0.0

        taken_query = select(func.count()).where(
            and_(
                DailyLogModel.patient_id == patient_id,
                DailyLogModel.log_date >= start_date,
                DailyLogModel.log_date <= end_date,
                DailyLogModel.medication_taken == True,  # noqa: E712
            )
        )
        taken_result = await self.db.execute(taken_query)
        taken_logs = taken_result.scalar() or 0

        adherence_rate = (taken_logs / total_logs) * 100
        return round(adherence_rate, 2)

    async def get_latest_log(self, patient_id: UUID) -> DailyLogModel | None:
        """Get the most recent log for a patient"""
        query = (
            select(DailyLogModel)
            .where(DailyLogModel.patient_id == patient_id)
            .order_by(DailyLogModel.log_date.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_aggregated_statistics(
        self,
        patient_id: UUID,
        start_date: date,
        end_date: date,
    ) -> dict:
        """
        Calculate aggregated statistics using SQL (database-side computation)

        This method replaces the inefficient pattern of fetching 10000 records
        and computing statistics in Python memory.

        Performance Improvement:
        - Old: Fetch 10000 records × 200 bytes = 2MB memory + Python loops
        - New: Single SQL query returns aggregated result < 1KB
        - Speedup: ~100x faster

        Args:
            patient_id: Patient UUID
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            Dictionary with aggregated statistics:
            - total_logs: int
            - medication_taken_count: int
            - total_water_intake: int
            - avg_water_intake: float
            - total_exercise_minutes: int (sum of non-null values)
            - avg_exercise_minutes: float (average of non-null values)
            - exercise_log_count: int (count of non-null exercise entries)
            - mood_good: int
            - mood_neutral: int
            - mood_bad: int
        """
        from sqlalchemy import case

        query = select(
            # Basic counts
            func.count(DailyLogModel.log_id).label('total_logs'),
            func.count(
                case((DailyLogModel.medication_taken == True, 1))  # noqa: E712
            ).label('medication_taken_count'),

            # Water intake statistics
            func.sum(
                func.coalesce(DailyLogModel.water_intake_ml, 0)
            ).label('total_water_intake'),
            func.avg(DailyLogModel.water_intake_ml).label('avg_water_intake'),

            # Exercise statistics (only non-null values)
            func.sum(DailyLogModel.exercise_minutes).label('total_exercise_minutes'),
            func.avg(DailyLogModel.exercise_minutes).label('avg_exercise_minutes'),
            func.count(DailyLogModel.exercise_minutes).label('exercise_log_count'),

            # Mood distribution
            func.count(
                case((DailyLogModel.mood == 'GOOD', 1))
            ).label('mood_good'),
            func.count(
                case((DailyLogModel.mood == 'NEUTRAL', 1))
            ).label('mood_neutral'),
            func.count(
                case((DailyLogModel.mood == 'BAD', 1))
            ).label('mood_bad'),
        ).where(
            and_(
                DailyLogModel.patient_id == patient_id,
                DailyLogModel.log_date >= start_date,
                DailyLogModel.log_date <= end_date,
            )
        )

        result = await self.db.execute(query)
        row = result.one()

        return {
            'total_logs': row.total_logs or 0,
            'medication_taken_count': row.medication_taken_count or 0,
            'total_water_intake': row.total_water_intake or 0,
            'avg_water_intake': float(row.avg_water_intake or 0),
            'total_exercise_minutes': row.total_exercise_minutes or 0,
            'avg_exercise_minutes': float(row.avg_exercise_minutes or 0),
            'exercise_log_count': row.exercise_log_count or 0,
            'mood_good': row.mood_good or 0,
            'mood_neutral': row.mood_neutral or 0,
            'mood_bad': row.mood_bad or 0,
        }
