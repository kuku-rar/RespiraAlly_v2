"""
Patient Repository Implementation
Infrastructure Layer - Clean Architecture

Concrete implementation of PatientRepository interface using SQLAlchemy.
This class handles all database interactions for Patient entities.
"""

from datetime import date
from uuid import UUID

from sqlalchemy import and_, case, cast, extract, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.types import Float

from respira_ally.domain.repositories.patient_repository import PatientRepository
from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel


class PatientRepositoryImpl(PatientRepository):
    """
    SQLAlchemy implementation of PatientRepository

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

    async def create(self, patient: PatientProfileModel) -> PatientProfileModel:
        """
        Create a new patient record

        Args:
            patient: PatientProfileModel instance to persist

        Returns:
            The created patient with database-generated fields

        Raises:
            IntegrityError: If patient with same user_id already exists
        """
        self.db.add(patient)
        await self.db.commit()
        await self.db.refresh(patient)
        return patient

    async def get_by_id(self, user_id: UUID) -> PatientProfileModel | None:
        """
        Retrieve patient by user ID

        Args:
            user_id: Patient's user ID (primary key)

        Returns:
            PatientProfileModel if found, None otherwise
        """
        return await self.db.get(PatientProfileModel, user_id)

    async def list_by_therapist(
        self,
        therapist_id: UUID,
        skip: int = 0,
        limit: int = 20,
        # Filters
        search: str | None = None,
        gender: str | None = None,
        min_bmi: float | None = None,
        max_bmi: float | None = None,
        min_age: int | None = None,
        max_age: int | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[PatientProfileModel], int]:
        """
        List patients assigned to a specific therapist with filters

        Args:
            therapist_id: Therapist's user ID
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            search: Search by name or phone (case-insensitive)
            gender: Filter by gender
            min_bmi: Minimum BMI value
            max_bmi: Maximum BMI value
            min_age: Minimum age in years
            max_age: Maximum age in years
            sort_by: Sort field
            sort_order: Sort order (asc/desc)

        Returns:
            Tuple of (list of patients, total count)
        """
        # Build base query conditions
        conditions = [PatientProfileModel.therapist_id == therapist_id]

        # 1. Search filter (name or phone, case-insensitive)
        if search:
            search_pattern = f"%{search}%"
            conditions.append(
                or_(
                    PatientProfileModel.name.ilike(search_pattern),
                    PatientProfileModel.contact_info["phone"].astext.ilike(search_pattern),
                )
            )

        # 2. Gender filter
        if gender:
            conditions.append(PatientProfileModel.gender == gender)

        # 3. Age range filter (calculate age from birth_date)
        if min_age is not None or max_age is not None:
            current_year = date.today().year
            current_month = date.today().month
            current_day = date.today().day

            # Calculate age = current_year - birth_year
            # Adjust if birthday hasn't occurred this year
            age_expression = (
                current_year
                - extract("year", PatientProfileModel.birth_date)
                - case(
                    (
                        or_(
                            extract("month", PatientProfileModel.birth_date) > current_month,
                            and_(
                                extract("month", PatientProfileModel.birth_date) == current_month,
                                extract("day", PatientProfileModel.birth_date) > current_day,
                            ),
                        ),
                        1,
                    ),
                    else_=0,
                )
            )

            if min_age is not None:
                conditions.append(age_expression >= min_age)
            if max_age is not None:
                conditions.append(age_expression <= max_age)

        # 4. BMI range filter
        # BMI = weight_kg / (height_cm / 100) ^ 2
        if min_bmi is not None or max_bmi is not None:
            # Calculate BMI: weight / (height/100)^2
            bmi_expression = cast(
                PatientProfileModel.weight_kg / func.pow(PatientProfileModel.height_cm / 100.0, 2),
                Float,
            )

            # Only filter patients with valid height and weight
            conditions.append(PatientProfileModel.height_cm.isnot(None))
            conditions.append(PatientProfileModel.weight_kg.isnot(None))
            conditions.append(PatientProfileModel.height_cm > 0)

            if min_bmi is not None:
                conditions.append(bmi_expression >= min_bmi)
            if max_bmi is not None:
                conditions.append(bmi_expression <= max_bmi)

        # Build base query with all conditions
        base_query = select(PatientProfileModel).where(and_(*conditions))

        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # 5. Apply sorting
        if sort_by == "name":
            order_column = PatientProfileModel.name
        elif sort_by == "birth_date":
            order_column = PatientProfileModel.birth_date
        elif sort_by == "bmi":
            # Sort by calculated BMI
            order_column = cast(
                PatientProfileModel.weight_kg / func.pow(PatientProfileModel.height_cm / 100.0, 2),
                Float,
            )
        else:  # default: created_at
            order_column = PatientProfileModel.created_at

        # Apply sort order
        if sort_order == "asc":
            order_clause = order_column.asc()
        else:
            order_clause = order_column.desc()

        # Get paginated results
        query = base_query.offset(skip).limit(limit).order_by(order_clause)
        result = await self.db.execute(query)
        patients = list(result.scalars().all())

        return patients, total

    async def update(
        self,
        user_id: UUID,
        update_data: dict,
    ) -> PatientProfileModel | None:
        """
        Update patient information

        Args:
            user_id: Patient's user ID
            update_data: Dictionary of fields to update

        Returns:
            Updated PatientProfileModel if found, None otherwise

        Note:
            Only fields present in update_data will be modified.
            Empty dict or dict with None values will not modify anything.
        """
        # Fetch the patient
        patient = await self.get_by_id(user_id)
        if not patient:
            return None

        # Update only provided fields (exclude None values)
        for key, value in update_data.items():
            if value is not None and hasattr(patient, key):
                setattr(patient, key, value)

        await self.db.commit()
        await self.db.refresh(patient)
        return patient

    async def delete(self, user_id: UUID) -> bool:
        """
        Delete patient record (hard delete)

        Args:
            user_id: Patient's user ID

        Returns:
            True if patient was deleted, False if not found

        Note:
            Currently implements hard delete. Consider soft delete
            for production (add 'deleted_at' column and filter queries).
        """
        patient = await self.get_by_id(user_id)
        if not patient:
            return False

        await self.db.delete(patient)
        await self.db.commit()
        return True

    async def exists(self, user_id: UUID) -> bool:
        """
        Check if patient exists

        Args:
            user_id: Patient's user ID

        Returns:
            True if patient exists, False otherwise
        """
        query = select(func.count()).where(PatientProfileModel.user_id == user_id)
        result = await self.db.execute(query)
        count = result.scalar()
        return count > 0

    async def count_by_therapist(self, therapist_id: UUID) -> int:
        """
        Count patients assigned to a therapist

        Args:
            therapist_id: Therapist's user ID

        Returns:
            Number of patients assigned to this therapist
        """
        query = select(func.count()).where(PatientProfileModel.therapist_id == therapist_id)
        result = await self.db.execute(query)
        return result.scalar() or 0
