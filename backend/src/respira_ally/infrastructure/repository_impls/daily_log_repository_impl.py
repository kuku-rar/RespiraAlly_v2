"""
Daily Log Repository Implementation
Infrastructure Layer - Clean Architecture

Concrete implementation of DailyLogRepository interface using SQLAlchemy.
This class handles all database interactions for DailyLog entities.
"""
from datetime import date
from typing import Optional
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

    async def get_by_id(self, log_id: UUID) -> Optional[DailyLogModel]:
        """Retrieve daily log by log ID"""
        return await self.db.get(DailyLogModel, log_id)

    async def get_by_patient_and_date(
        self, patient_id: UUID, log_date: date
    ) -> Optional[DailyLogModel]:
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
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
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
        query = (
            base_query.offset(skip)
            .limit(limit)
            .order_by(DailyLogModel.log_date.desc())
        )
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
    ) -> Optional[DailyLogModel]:
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
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
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

    async def get_latest_log(self, patient_id: UUID) -> Optional[DailyLogModel]:
        """Get the most recent log for a patient"""
        query = (
            select(DailyLogModel)
            .where(DailyLogModel.patient_id == patient_id)
            .order_by(DailyLogModel.log_date.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
