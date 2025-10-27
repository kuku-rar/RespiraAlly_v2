"""
Registration Use Case
Handles both therapist and patient registration
"""

from datetime import date
from decimal import Decimal

from respira_ally.core.config import settings
from respira_ally.core.exceptions.application_exceptions import ConflictError, ValidationError
from respira_ally.core.schemas.auth import (
    LoginResponse,
    PatientRegisterRequest,
    UserInfo,
    UserRole,
)
from respira_ally.core.security.jwt import create_access_token, create_refresh_token
from respira_ally.domain.repositories.patient_repository import PatientRepository
from respira_ally.domain.repositories.user_repository import UserRepository
from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel

from .login_use_case import hash_password


class TherapistRegisterUseCase:
    """
    Therapist Registration Use Case

    Flow:
    1. Validate input (email, password, full_name)
    2. Check if email already exists
    3. Hash password
    4. Create therapist user
    5. Generate JWT tokens
    6. Return tokens + user info
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, email: str, password: str, full_name: str) -> LoginResponse:
        """
        Register a new therapist

        Args:
            email: Therapist email address
            password: Plain text password (min 8 characters)
            full_name: Therapist full name

        Returns:
            LoginResponse with tokens and user info

        Raises:
            ValidationError: If input validation fails
            ConflictError: If email already exists
        """
        # Validate input
        if not email or len(email) == 0:
            raise ValidationError(field="email", message="Email is required")

        if not password or len(password) < 8:
            raise ValidationError(
                field="password",
                message="Password must be at least 8 characters",
                value=len(password) if password else 0,
            )

        if not full_name or len(full_name) == 0:
            raise ValidationError(field="full_name", message="Full name is required")

        # Check if email already exists
        existing_user = await self.user_repository.find_by_email(email)

        if existing_user is not None:
            raise ConflictError(
                resource_type="User",
                conflict_field="email",
                value=email,
            )

        # Hash password
        hashed_password = hash_password(password)

        # Create therapist user
        user = await self.user_repository.create_therapist(
            email=email, password_hash=hashed_password, full_name=full_name
        )

        # Generate tokens
        token_payload = {"sub": str(user.user_id), "role": UserRole.THERAPIST.value}

        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(token_payload)

        # Build user info
        user_info = UserInfo(
            user_id=user.user_id,
            role=UserRole.THERAPIST,
            email=user.email,
            line_user_id=None,
            display_name=full_name,
            is_active=True,
            created_at=user.created_at,
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_info,
        )


class PatientRegisterUseCase:
    """
    Patient Initial Registration Use Case (LINE LIFF)

    Flow:
    1. Validate input (required: line_user_id, full_name, date_of_birth, gender)
    2. Check if LINE User ID already exists
    3. Determine smoking_status from smoking_years
    4. Build contact_info JSONB
    5. Create UserModel
    6. Create PatientProfileModel
    7. Commit transaction
    8. Generate JWT tokens
    9. Return tokens + user info

    Design Decision:
    - hospital_patient_id maps to hospital_medical_record_number in DB
    - smoking_years determines smoking_status:
      - None or 0 → NEVER
      - > 0 → CURRENT (default assumption for COPD patients)
    - emergency contact stored in contact_info JSONB
    """

    def __init__(
        self, user_repository: UserRepository, patient_repository: PatientRepository, db
    ):
        self.user_repository = user_repository
        self.patient_repository = patient_repository
        self.db = db

    async def execute(self, request: PatientRegisterRequest) -> LoginResponse:
        """
        Register a new patient with complete profile data

        Args:
            request: PatientRegisterRequest with all patient data

        Returns:
            LoginResponse with tokens and user info

        Raises:
            ValidationError: If input validation fails
            ConflictError: If LINE User ID already exists
        """
        # Validate required fields (Pydantic already validates types, but double-check)
        if not request.line_user_id or len(request.line_user_id) == 0:
            raise ValidationError(field="line_user_id", message="LINE User ID is required")

        if not request.full_name or len(request.full_name) < 2:
            raise ValidationError(
                field="full_name",
                message="Full name must be at least 2 characters",
            )

        # Check if LINE User ID already exists
        existing_user = await self.user_repository.find_by_line_user_id(request.line_user_id)

        if existing_user is not None:
            raise ConflictError(
                resource_type="Patient",
                conflict_field="line_user_id",
                value=request.line_user_id,
            )

        # Determine smoking_status from smoking_years
        smoking_status = None
        if request.smoking_years is not None:
            if request.smoking_years == 0:
                smoking_status = "NEVER"
            elif request.smoking_years > 0:
                # Default to CURRENT for COPD patients with smoking history
                smoking_status = "CURRENT"

        # Build contact_info JSONB
        contact_info = {}
        if request.phone_number:
            contact_info["phone"] = request.phone_number
        if request.emergency_contact_name:
            contact_info["emergency_contact"] = request.emergency_contact_name
        if request.emergency_contact_phone:
            contact_info["emergency_phone"] = request.emergency_contact_phone

        # Create UserModel (only flush, don't commit yet)
        user = await self.user_repository.create_patient(
            line_user_id=request.line_user_id,
            display_name=request.line_display_name,
        )

        # Create PatientProfileModel
        patient_profile = PatientProfileModel(
            user_id=user.user_id,
            therapist_id=None,  # Can be assigned later by admin/therapist
            name=request.full_name,
            birth_date=request.date_of_birth,
            gender=request.gender,
            hospital_medical_record_number=request.hospital_patient_id,  # Field mapping
            height_cm=request.height_cm,
            weight_kg=request.weight_kg,
            smoking_status=smoking_status,
            smoking_years=request.smoking_years,
            medical_history={},  # Empty for now, can be filled later
            contact_info=contact_info,
        )

        # Add and flush PatientProfileModel (don't commit yet)
        self.db.add(patient_profile)
        await self.db.flush()

        # Commit transaction (both UserModel and PatientProfileModel)
        await self.db.commit()
        await self.db.refresh(user)
        await self.db.refresh(patient_profile)

        # Generate tokens
        token_payload = {"sub": str(user.user_id), "role": UserRole.PATIENT.value}

        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(token_payload)

        # Build user info
        user_info = UserInfo(
            user_id=user.user_id,
            role=UserRole.PATIENT,
            email=None,
            line_user_id=user.line_user_id,
            display_name=request.full_name,  # Use full_name as display_name
            is_active=True,
            created_at=user.created_at,
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_info,
        )
