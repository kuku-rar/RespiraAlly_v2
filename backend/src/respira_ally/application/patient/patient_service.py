"""
Patient Application Service
Application Layer - Clean Architecture

This service orchestrates patient-related use cases and business logic.
It uses Repository pattern for data access and encapsulates complex workflows.
"""
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from respira_ally.core.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse,
)
from respira_ally.domain.repositories.patient_repository import PatientRepository
from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
from respira_ally.infrastructure.database.models.user import UserModel


class PatientService:
    """
    Patient Application Service

    Responsibilities:
    - Orchestrate patient CRUD operations
    - Calculate derived fields (BMI, age)
    - Validate business rules
    - Coordinate with User creation
    """

    def __init__(self, patient_repository: PatientRepository):
        """
        Initialize service with repository dependency

        Args:
            patient_repository: Implementation of PatientRepository interface
        """
        self.patient_repo = patient_repository

    # ========================================================================
    # Helper Methods (Business Logic)
    # ========================================================================

    @staticmethod
    def calculate_age(birth_date: date) -> int:
        """
        Calculate age from birth date

        Args:
            birth_date: Patient's date of birth

        Returns:
            Age in years
        """
        today = date.today()
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age

    @staticmethod
    def calculate_bmi(weight_kg: Optional[Decimal], height_cm: Optional[int]) -> Optional[Decimal]:
        """
        Calculate Body Mass Index (BMI)

        Formula: BMI = weight(kg) / height(m)²

        Args:
            weight_kg: Weight in kilograms
            height_cm: Height in centimeters

        Returns:
            BMI value (rounded to 1 decimal) or None if data insufficient
        """
        if not weight_kg or not height_cm:
            return None

        height_m = Decimal(height_cm) / Decimal(100)
        bmi = weight_kg / (height_m * height_m)
        return round(bmi, 1)

    def enrich_patient_response(self, patient: PatientProfileModel) -> PatientResponse:
        """
        Convert PatientProfileModel to PatientResponse with computed fields

        Args:
            patient: PatientProfileModel from database

        Returns:
            PatientResponse with age and BMI calculated
        """
        # Extract phone from contact_info JSONB
        phone = None
        if patient.contact_info:
            phone = patient.contact_info.get("phone")

        return PatientResponse(
            user_id=patient.user_id,
            therapist_id=patient.therapist_id,
            name=patient.name,
            birth_date=patient.birth_date,
            gender=patient.gender,
            height_cm=patient.height_cm,
            weight_kg=patient.weight_kg,
            phone=phone,
            age=self.calculate_age(patient.birth_date),
            bmi=self.calculate_bmi(patient.weight_kg, patient.height_cm),
        )

    # ========================================================================
    # Create Operations
    # ========================================================================

    async def create_patient(
        self,
        data: PatientCreate,
        user_model: UserModel,
    ) -> PatientResponse:
        """
        Create a new patient profile

        Workflow:
        1. Prepare contact_info and medical_history JSON
        2. Create PatientProfileModel
        3. Persist using repository
        4. Return enriched response

        Args:
            data: Patient creation request
            user_model: Pre-created UserModel for this patient

        Returns:
            PatientResponse with computed fields

        Raises:
            IntegrityError: If patient with same user_id already exists
        """
        # Prepare JSONB fields
        contact_info = {}
        if data.phone:
            contact_info["phone"] = data.phone

        medical_history = {}  # Empty for now, will be populated later

        # Create PatientProfileModel
        patient = PatientProfileModel(
            user_id=user_model.user_id,
            therapist_id=data.therapist_id,
            name=data.name,
            birth_date=data.birth_date,
            gender=data.gender,
            height_cm=data.height_cm,
            weight_kg=data.weight_kg,
            contact_info=contact_info,
            medical_history=medical_history,
        )

        # Persist
        created_patient = await self.patient_repo.create(patient)

        # Return enriched response
        return self.enrich_patient_response(created_patient)

    # ========================================================================
    # Read Operations
    # ========================================================================

    async def get_patient_by_id(self, user_id: UUID) -> Optional[PatientResponse]:
        """
        Retrieve patient by user ID

        Args:
            user_id: Patient's user ID

        Returns:
            PatientResponse if found, None otherwise
        """
        patient = await self.patient_repo.get_by_id(user_id)
        if not patient:
            return None

        return self.enrich_patient_response(patient)

    async def list_patients_by_therapist(
        self,
        therapist_id: UUID,
        page: int = 0,
        page_size: int = 20,
        # Filters
        search: Optional[str] = None,
        gender: Optional[str] = None,
        min_bmi: Optional[float] = None,
        max_bmi: Optional[float] = None,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> PatientListResponse:
        """
        List patients assigned to a therapist (with pagination and filters)

        Args:
            therapist_id: Therapist's user ID
            page: Page number (0-indexed)
            page_size: Number of items per page
            search: Search by name or phone
            gender: Filter by gender
            min_bmi: Minimum BMI
            max_bmi: Maximum BMI
            min_age: Minimum age
            max_age: Maximum age
            sort_by: Sort field
            sort_order: Sort order

        Returns:
            PatientListResponse with items and pagination metadata
        """
        skip = page * page_size
        patients, total = await self.patient_repo.list_by_therapist(
            therapist_id=therapist_id,
            skip=skip,
            limit=page_size,
            search=search,
            gender=gender,
            min_bmi=min_bmi,
            max_bmi=max_bmi,
            min_age=min_age,
            max_age=max_age,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        # Enrich all patient responses
        items = [self.enrich_patient_response(p) for p in patients]

        return PatientListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_next=(skip + len(items)) < total,
        )

    async def patient_exists(self, user_id: UUID) -> bool:
        """
        Check if patient exists

        Args:
            user_id: Patient's user ID

        Returns:
            True if patient exists, False otherwise
        """
        return await self.patient_repo.exists(user_id)

    async def count_patients_by_therapist(self, therapist_id: UUID) -> int:
        """
        Count patients assigned to a therapist

        Args:
            therapist_id: Therapist's user ID

        Returns:
            Number of patients
        """
        return await self.patient_repo.count_by_therapist(therapist_id)

    # ========================================================================
    # Update Operations
    # ========================================================================

    async def update_patient(
        self,
        user_id: UUID,
        data: PatientUpdate,
    ) -> Optional[PatientResponse]:
        """
        Update patient information (partial update)

        Args:
            user_id: Patient's user ID
            data: Patient update request (all fields optional)

        Returns:
            Updated PatientResponse if patient found, None otherwise
        """
        # Convert Pydantic model to dict, excluding None values
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)

        # Handle phone update (stored in JSONB contact_info)
        if "phone" in update_data:
            phone = update_data.pop("phone")
            # Fetch current contact_info
            patient = await self.patient_repo.get_by_id(user_id)
            if patient:
                contact_info = patient.contact_info or {}
                contact_info["phone"] = phone
                update_data["contact_info"] = contact_info

        # Update using repository
        updated_patient = await self.patient_repo.update(user_id, update_data)
        if not updated_patient:
            return None

        return self.enrich_patient_response(updated_patient)

    # ========================================================================
    # Delete Operations
    # ========================================================================

    async def delete_patient(self, user_id: UUID) -> bool:
        """
        Delete patient record

        Args:
            user_id: Patient's user ID

        Returns:
            True if patient was deleted, False if not found

        Note:
            Currently performs hard delete. Consider soft delete
            for production (add deleted_at column).
        """
        return await self.patient_repo.delete(user_id)
