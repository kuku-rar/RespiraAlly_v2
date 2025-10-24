"""
Exacerbation Service - COPD acute exacerbation management
Sprint 4: Risk Engine - Business logic for exacerbation tracking and statistics
"""

from datetime import date, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.core.schemas.exacerbation import (
    ExacerbationCreate,
    ExacerbationListResponse,
    ExacerbationResponse,
    ExacerbationStats,
    ExacerbationUpdate,
)
from respira_ally.infrastructure.database.models.exacerbation import ExacerbationModel
from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel


class ExacerbationService:
    """
    Exacerbation Service - COPD acute exacerbation management

    Responsibilities:
    - Create, read, update, delete exacerbation records
    - Calculate exacerbation statistics for GOLD ABE classification
    - Auto-update patient_profiles summary fields via database trigger
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_exacerbation(
        self, data: ExacerbationCreate, recorded_by: UUID
    ) -> ExacerbationResponse:
        """
        Create a new exacerbation record

        Args:
            data: ExacerbationCreate request data
            recorded_by: UUID of the user creating this record (therapist)

        Returns:
            ExacerbationResponse with created exacerbation details

        Raises:
            ValueError: If patient not found
        """
        # Verify patient exists
        patient = await self.db.get(PatientProfileModel, data.patient_id)
        if not patient:
            raise ValueError(f"Patient {data.patient_id} not found")

        # Create exacerbation record
        exacerbation = ExacerbationModel(
            patient_id=data.patient_id,
            onset_date=data.onset_date,
            severity=data.severity,
            required_hospitalization=data.required_hospitalization,
            hospitalization_days=data.hospitalization_days,
            required_antibiotics=data.required_antibiotics,
            required_steroids=data.required_steroids,
            symptoms=data.symptoms,
            notes=data.notes,
            recorded_date=date.today(),
            recorded_by=recorded_by,
        )

        self.db.add(exacerbation)
        await self.db.commit()
        await self.db.refresh(exacerbation)

        # Convert to response
        return self._to_response(exacerbation)

    async def get_exacerbation_by_id(self, exacerbation_id: UUID) -> ExacerbationResponse | None:
        """
        Get exacerbation record by ID

        Args:
            exacerbation_id: Exacerbation UUID

        Returns:
            ExacerbationResponse or None if not found
        """
        exacerbation = await self.db.get(ExacerbationModel, exacerbation_id)
        if not exacerbation:
            return None

        return self._to_response(exacerbation)

    async def list_patient_exacerbations(
        self,
        patient_id: UUID,
        page: int = 0,
        page_size: int = 20,
        start_date: date | None = None,
        end_date: date | None = None,
        severity: str | None = None,
    ) -> ExacerbationListResponse:
        """
        List exacerbations for a patient with filters and pagination

        Args:
            patient_id: Patient UUID
            page: Page number (0-indexed)
            page_size: Number of items per page
            start_date: Filter by onset_date >= start_date
            end_date: Filter by onset_date <= end_date
            severity: Filter by severity (MILD, MODERATE, SEVERE)

        Returns:
            ExacerbationListResponse with paginated results
        """
        # Build query
        query = select(ExacerbationModel).where(ExacerbationModel.patient_id == patient_id)

        # Apply filters
        if start_date:
            query = query.where(ExacerbationModel.onset_date >= start_date)
        if end_date:
            query = query.where(ExacerbationModel.onset_date <= end_date)
        if severity:
            query = query.where(ExacerbationModel.severity == severity)

        # Order by onset_date descending (newest first)
        query = query.order_by(ExacerbationModel.onset_date.desc())

        # Count total results
        count_query = select(func.count()).select_from(query.subquery())
        result = await self.db.execute(count_query)
        total = result.scalar_one()

        # Apply pagination
        query = query.offset(page * page_size).limit(page_size)

        # Execute query
        result = await self.db.execute(query)
        exacerbations = result.scalars().all()

        # Convert to response
        exacerbation_list = [self._to_response(e) for e in exacerbations]

        return ExacerbationListResponse(
            exacerbations=exacerbation_list,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,  # Ceiling division
        )

    async def update_exacerbation(
        self, exacerbation_id: UUID, data: ExacerbationUpdate
    ) -> ExacerbationResponse | None:
        """
        Update exacerbation record (partial update)

        Args:
            exacerbation_id: Exacerbation UUID
            data: ExacerbationUpdate with fields to update

        Returns:
            Updated ExacerbationResponse or None if not found
        """
        exacerbation = await self.db.get(ExacerbationModel, exacerbation_id)
        if not exacerbation:
            return None

        # Update fields (only if provided)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(exacerbation, field, value)

        # Update timestamp
        exacerbation.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(exacerbation)

        return self._to_response(exacerbation)

    async def delete_exacerbation(self, exacerbation_id: UUID) -> bool:
        """
        Delete exacerbation record

        Args:
            exacerbation_id: Exacerbation UUID

        Returns:
            True if deleted, False if not found
        """
        exacerbation = await self.db.get(ExacerbationModel, exacerbation_id)
        if not exacerbation:
            return False

        await self.db.delete(exacerbation)
        await self.db.commit()

        return True

    async def get_exacerbation_stats(self, patient_id: UUID) -> ExacerbationStats | None:
        """
        Get exacerbation statistics for a patient

        Args:
            patient_id: Patient UUID

        Returns:
            ExacerbationStats or None if patient not found
        """
        # Verify patient exists
        patient = await self.db.get(PatientProfileModel, patient_id)
        if not patient:
            return None

        # Calculate date 12 months ago
        twelve_months_ago = date.today() - timedelta(days=365)

        # Query all exacerbations
        stmt_all = select(func.count(ExacerbationModel.exacerbation_id)).where(
            ExacerbationModel.patient_id == patient_id
        )
        result = await self.db.execute(stmt_all)
        total_exacerbations = result.scalar_one()

        # Query last 12 months exacerbations
        stmt_12m = select(func.count(ExacerbationModel.exacerbation_id)).where(
            ExacerbationModel.patient_id == patient_id,
            ExacerbationModel.onset_date >= twelve_months_ago,
        )
        result = await self.db.execute(stmt_12m)
        exacerbations_last_12m = result.scalar_one()

        # Query last 12 months hospitalizations
        stmt_hosp = select(func.count(ExacerbationModel.exacerbation_id)).where(
            ExacerbationModel.patient_id == patient_id,
            ExacerbationModel.onset_date >= twelve_months_ago,
            ExacerbationModel.required_hospitalization == True,  # noqa: E712
        )
        result = await self.db.execute(stmt_hosp)
        hospitalizations_last_12m = result.scalar_one()

        # Query last exacerbation date
        stmt_last = (
            select(ExacerbationModel.onset_date)
            .where(ExacerbationModel.patient_id == patient_id)
            .order_by(ExacerbationModel.onset_date.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt_last)
        last_exacerbation_date = result.scalar_one_or_none()

        # Query last hospitalization date
        stmt_last_hosp = (
            select(ExacerbationModel.onset_date)
            .where(
                ExacerbationModel.patient_id == patient_id,
                ExacerbationModel.required_hospitalization == True,  # noqa: E712
            )
            .order_by(ExacerbationModel.onset_date.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt_last_hosp)
        last_hospitalization_date = result.scalar_one_or_none()

        # Query severity breakdown (last 12 months)
        stmt_mild = select(func.count(ExacerbationModel.exacerbation_id)).where(
            ExacerbationModel.patient_id == patient_id,
            ExacerbationModel.onset_date >= twelve_months_ago,
            ExacerbationModel.severity == "MILD",
        )
        result = await self.db.execute(stmt_mild)
        mild_count_12m = result.scalar_one()

        stmt_moderate = select(func.count(ExacerbationModel.exacerbation_id)).where(
            ExacerbationModel.patient_id == patient_id,
            ExacerbationModel.onset_date >= twelve_months_ago,
            ExacerbationModel.severity == "MODERATE",
        )
        result = await self.db.execute(stmt_moderate)
        moderate_count_12m = result.scalar_one()

        stmt_severe = select(func.count(ExacerbationModel.exacerbation_id)).where(
            ExacerbationModel.patient_id == patient_id,
            ExacerbationModel.onset_date >= twelve_months_ago,
            ExacerbationModel.severity == "SEVERE",
        )
        result = await self.db.execute(stmt_severe)
        severe_count_12m = result.scalar_one()

        return ExacerbationStats(
            patient_id=patient_id,
            total_exacerbations=total_exacerbations,
            exacerbations_last_12m=exacerbations_last_12m,
            hospitalizations_last_12m=hospitalizations_last_12m,
            last_exacerbation_date=last_exacerbation_date,
            last_hospitalization_date=last_hospitalization_date,
            mild_count_12m=mild_count_12m,
            moderate_count_12m=moderate_count_12m,
            severe_count_12m=severe_count_12m,
        )

    def _to_response(self, exacerbation: ExacerbationModel) -> ExacerbationResponse:
        """Convert ExacerbationModel to ExacerbationResponse"""
        return ExacerbationResponse(
            exacerbation_id=exacerbation.exacerbation_id,
            patient_id=exacerbation.patient_id,
            onset_date=exacerbation.onset_date,
            severity=exacerbation.severity,
            required_hospitalization=exacerbation.required_hospitalization,
            hospitalization_days=exacerbation.hospitalization_days,
            required_antibiotics=exacerbation.required_antibiotics,
            required_steroids=exacerbation.required_steroids,
            symptoms=exacerbation.symptoms,
            notes=exacerbation.notes,
            recorded_date=exacerbation.recorded_date,
            recorded_by=exacerbation.recorded_by,
            created_at=exacerbation.created_at.isoformat(),
            updated_at=exacerbation.updated_at.isoformat(),
        )
