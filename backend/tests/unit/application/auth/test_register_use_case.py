"""
Unit Tests for Patient Registration Use Case
Tests PatientRegisterUseCase business logic
"""

from datetime import date, datetime, UTC
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

from respira_ally.application.auth.use_cases.register_use_case import PatientRegisterUseCase
from respira_ally.core.exceptions.application_exceptions import ConflictError, ValidationError
from respira_ally.core.schemas.auth import PatientRegisterRequest, UserRole
from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
from respira_ally.infrastructure.database.models.user import UserModel


@pytest.fixture
def mock_user_repository():
    """Mock UserRepository"""
    repo = AsyncMock()
    repo.find_by_line_user_id = AsyncMock(return_value=None)
    repo.create_patient = AsyncMock()
    return repo


@pytest.fixture
def mock_patient_repository():
    """Mock PatientRepository"""
    repo = AsyncMock()
    repo.create = AsyncMock()
    return repo


@pytest.fixture
def mock_db():
    """Mock AsyncSession"""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db


@pytest.fixture
def use_case(mock_user_repository, mock_patient_repository, mock_db):
    """PatientRegisterUseCase instance with mocked dependencies"""
    return PatientRegisterUseCase(mock_user_repository, mock_patient_repository, mock_db)


@pytest.fixture
def valid_request():
    """Valid PatientRegisterRequest with all fields"""
    return PatientRegisterRequest(
        line_user_id="U1234567890abcdef",
        line_display_name="Test Patient",
        line_picture_url="https://example.com/picture.jpg",
        full_name="王小明",
        date_of_birth=date(1980, 5, 15),
        gender="MALE",
        phone_number="0912345678",
        hospital_patient_id="WF2024001",
        height_cm=170,
        weight_kg=Decimal("70.5"),
        smoking_years=15,
        emergency_contact_name="王大明",
        emergency_contact_phone="0987654321",
    )


@pytest.fixture
def minimal_request():
    """PatientRegisterRequest with only required fields"""
    return PatientRegisterRequest(
        line_user_id="U1234567890abcdef",
        line_display_name=None,
        line_picture_url=None,
        full_name="王小明",
        date_of_birth=date(1980, 5, 15),
        gender="MALE",
        phone_number=None,
        hospital_patient_id=None,
        height_cm=None,
        weight_kg=None,
        smoking_years=None,
        emergency_contact_name=None,
        emergency_contact_phone=None,
    )


class TestPatientRegisterSuccess:
    """Test successful patient registration scenarios"""

    @pytest.mark.asyncio
    async def test_register_with_all_fields_success(
        self, use_case, valid_request, mock_user_repository, mock_db
    ):
        """Test successful registration with all fields"""
        # Arrange
        user_id = uuid4()
        mock_user = UserModel(
            user_id=user_id,
            line_user_id=valid_request.line_user_id,
            role=UserRole.PATIENT.value,
            email=None,
            hashed_password=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            deleted_at=None,
        )
        mock_user_repository.create_patient.return_value = mock_user

        # Mock JWT token creation
        with patch(
            "respira_ally.application.auth.use_cases.register_use_case.create_access_token"
        ) as mock_access, patch(
            "respira_ally.application.auth.use_cases.register_use_case.create_refresh_token"
        ) as mock_refresh:
            mock_access.return_value = "mock_access_token"
            mock_refresh.return_value = "mock_refresh_token"

            # Act
            response = await use_case.execute(valid_request)

        # Assert
        assert response.access_token == "mock_access_token"
        assert response.refresh_token == "mock_refresh_token"
        assert response.token_type == "bearer"
        assert response.user.user_id == user_id
        assert response.user.role == UserRole.PATIENT
        assert response.user.line_user_id == valid_request.line_user_id
        assert response.user.display_name == valid_request.full_name

        # Verify UserRepository.create_patient was called
        mock_user_repository.create_patient.assert_called_once_with(
            line_user_id=valid_request.line_user_id,
            display_name=valid_request.line_display_name,
        )

        # Verify PatientProfileModel was created
        mock_db.add.assert_called_once()
        added_profile = mock_db.add.call_args[0][0]
        assert isinstance(added_profile, PatientProfileModel)
        assert added_profile.user_id == user_id
        assert added_profile.name == valid_request.full_name
        assert added_profile.birth_date == valid_request.date_of_birth
        assert added_profile.gender == valid_request.gender
        assert added_profile.hospital_medical_record_number == valid_request.hospital_patient_id
        assert added_profile.height_cm == valid_request.height_cm
        assert added_profile.weight_kg == valid_request.weight_kg
        assert added_profile.smoking_years == valid_request.smoking_years
        assert added_profile.smoking_status == "CURRENT"  # smoking_years > 0

        # Verify emergency contact in contact_info
        assert "phone" in added_profile.contact_info
        assert added_profile.contact_info["phone"] == valid_request.phone_number
        assert "emergency_contact" in added_profile.contact_info
        assert added_profile.contact_info["emergency_contact"] == valid_request.emergency_contact_name
        assert "emergency_phone" in added_profile.contact_info
        assert added_profile.contact_info["emergency_phone"] == valid_request.emergency_contact_phone

        # Verify transaction
        mock_db.flush.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_with_minimal_fields_success(
        self, use_case, minimal_request, mock_user_repository, mock_db
    ):
        """Test successful registration with only required fields"""
        # Arrange
        user_id = uuid4()
        mock_user = UserModel(
            user_id=user_id,
            line_user_id=minimal_request.line_user_id,
            role=UserRole.PATIENT.value,
            email=None,
            hashed_password=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            deleted_at=None,
        )
        mock_user_repository.create_patient.return_value = mock_user

        with patch(
            "respira_ally.application.auth.use_cases.register_use_case.create_access_token"
        ) as mock_access, patch(
            "respira_ally.application.auth.use_cases.register_use_case.create_refresh_token"
        ) as mock_refresh:
            mock_access.return_value = "mock_access_token"
            mock_refresh.return_value = "mock_refresh_token"

            # Act
            response = await use_case.execute(minimal_request)

        # Assert
        assert response.access_token == "mock_access_token"
        assert response.user.user_id == user_id

        # Verify PatientProfileModel with minimal data
        added_profile = mock_db.add.call_args[0][0]
        assert added_profile.name == minimal_request.full_name
        assert added_profile.hospital_medical_record_number is None
        assert added_profile.height_cm is None
        assert added_profile.weight_kg is None
        assert added_profile.smoking_years is None
        assert added_profile.smoking_status is None
        assert added_profile.contact_info == {}  # Empty contact_info


class TestSmokingStatusDetermination:
    """Test automatic smoking_status determination from smoking_years"""

    @pytest.mark.asyncio
    async def test_smoking_years_zero_sets_never(
        self, use_case, minimal_request, mock_user_repository, mock_db
    ):
        """Test smoking_years = 0 → smoking_status = NEVER"""
        # Arrange
        request = minimal_request.model_copy(update={"smoking_years": 0})
        user_id = uuid4()
        mock_user = UserModel(
            user_id=user_id,
            line_user_id=request.line_user_id,
            role=UserRole.PATIENT.value,
            email=None,
            hashed_password=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            deleted_at=None,
        )
        mock_user_repository.create_patient.return_value = mock_user

        with patch(
            "respira_ally.application.auth.use_cases.register_use_case.create_access_token"
        ) as mock_access, patch(
            "respira_ally.application.auth.use_cases.register_use_case.create_refresh_token"
        ) as mock_refresh:
            mock_access.return_value = "mock_access_token"
            mock_refresh.return_value = "mock_refresh_token"

            # Act
            await use_case.execute(request)

        # Assert
        added_profile = mock_db.add.call_args[0][0]
        assert added_profile.smoking_years == 0
        assert added_profile.smoking_status == "NEVER"

    @pytest.mark.asyncio
    async def test_smoking_years_positive_sets_current(
        self, use_case, minimal_request, mock_user_repository, mock_db
    ):
        """Test smoking_years > 0 → smoking_status = CURRENT"""
        # Arrange
        request = minimal_request.model_copy(update={"smoking_years": 20})
        user_id = uuid4()
        mock_user = UserModel(
            user_id=user_id,
            line_user_id=request.line_user_id,
            role=UserRole.PATIENT.value,
            email=None,
            hashed_password=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            deleted_at=None,
        )
        mock_user_repository.create_patient.return_value = mock_user

        with patch(
            "respira_ally.application.auth.use_cases.register_use_case.create_access_token"
        ) as mock_access, patch(
            "respira_ally.application.auth.use_cases.register_use_case.create_refresh_token"
        ) as mock_refresh:
            mock_access.return_value = "mock_access_token"
            mock_refresh.return_value = "mock_refresh_token"

            # Act
            await use_case.execute(request)

        # Assert
        added_profile = mock_db.add.call_args[0][0]
        assert added_profile.smoking_years == 20
        assert added_profile.smoking_status == "CURRENT"

    @pytest.mark.asyncio
    async def test_smoking_years_none_sets_none(
        self, use_case, minimal_request, mock_user_repository, mock_db
    ):
        """Test smoking_years = None → smoking_status = None"""
        # Arrange
        user_id = uuid4()
        mock_user = UserModel(
            user_id=user_id,
            line_user_id=minimal_request.line_user_id,
            role=UserRole.PATIENT.value,
            email=None,
            hashed_password=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            deleted_at=None,
        )
        mock_user_repository.create_patient.return_value = mock_user

        with patch(
            "respira_ally.application.auth.use_cases.register_use_case.create_access_token"
        ) as mock_access, patch(
            "respira_ally.application.auth.use_cases.register_use_case.create_refresh_token"
        ) as mock_refresh:
            mock_access.return_value = "mock_access_token"
            mock_refresh.return_value = "mock_refresh_token"

            # Act
            await use_case.execute(minimal_request)

        # Assert
        added_profile = mock_db.add.call_args[0][0]
        assert added_profile.smoking_years is None
        assert added_profile.smoking_status is None


class TestFieldMapping:
    """Test correct field mapping (e.g., hospital_patient_id → hospital_medical_record_number)"""

    @pytest.mark.asyncio
    async def test_hospital_patient_id_mapping(
        self, use_case, minimal_request, mock_user_repository, mock_db
    ):
        """Test hospital_patient_id correctly maps to hospital_medical_record_number"""
        # Arrange
        request = minimal_request.model_copy(update={"hospital_patient_id": "WF2024999"})
        user_id = uuid4()
        mock_user = UserModel(
            user_id=user_id,
            line_user_id=request.line_user_id,
            role=UserRole.PATIENT.value,
            email=None,
            hashed_password=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            deleted_at=None,
        )
        mock_user_repository.create_patient.return_value = mock_user

        with patch(
            "respira_ally.application.auth.use_cases.register_use_case.create_access_token"
        ) as mock_access, patch(
            "respira_ally.application.auth.use_cases.register_use_case.create_refresh_token"
        ) as mock_refresh:
            mock_access.return_value = "mock_access_token"
            mock_refresh.return_value = "mock_refresh_token"

            # Act
            await use_case.execute(request)

        # Assert
        added_profile = mock_db.add.call_args[0][0]
        assert added_profile.hospital_medical_record_number == "WF2024999"

    @pytest.mark.asyncio
    async def test_emergency_contact_stored_in_jsonb(
        self, use_case, minimal_request, mock_user_repository, mock_db
    ):
        """Test emergency contact fields are correctly stored in contact_info JSONB"""
        # Arrange
        request = minimal_request.model_copy(
            update={
                "phone_number": "0912345678",
                "emergency_contact_name": "緊急聯絡人",
                "emergency_contact_phone": "0987654321",
            }
        )
        user_id = uuid4()
        mock_user = UserModel(
            user_id=user_id,
            line_user_id=request.line_user_id,
            role=UserRole.PATIENT.value,
            email=None,
            hashed_password=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            deleted_at=None,
        )
        mock_user_repository.create_patient.return_value = mock_user

        with patch(
            "respira_ally.application.auth.use_cases.register_use_case.create_access_token"
        ) as mock_access, patch(
            "respira_ally.application.auth.use_cases.register_use_case.create_refresh_token"
        ) as mock_refresh:
            mock_access.return_value = "mock_access_token"
            mock_refresh.return_value = "mock_refresh_token"

            # Act
            await use_case.execute(request)

        # Assert
        added_profile = mock_db.add.call_args[0][0]
        assert added_profile.contact_info["phone"] == "0912345678"
        assert added_profile.contact_info["emergency_contact"] == "緊急聯絡人"
        assert added_profile.contact_info["emergency_phone"] == "0987654321"


class TestValidationErrors:
    """Test validation error scenarios"""

    @pytest.mark.asyncio
    async def test_empty_line_user_id_raises_validation_error(self, use_case, minimal_request):
        """Test empty line_user_id raises ValidationError"""
        # Arrange
        request = minimal_request.model_copy(update={"line_user_id": ""})

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await use_case.execute(request)

        assert exc_info.value.field == "line_user_id"
        assert "required" in exc_info.value.message.lower()

    @pytest.mark.asyncio
    async def test_short_full_name_raises_validation_error(self, use_case, minimal_request):
        """Test full_name < 2 characters raises ValidationError"""
        # Arrange
        request = minimal_request.model_copy(update={"full_name": "A"})

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await use_case.execute(request)

        assert exc_info.value.field == "full_name"
        assert "at least 2 characters" in exc_info.value.message


class TestConflictErrors:
    """Test conflict error scenarios"""

    @pytest.mark.asyncio
    async def test_existing_line_user_id_raises_conflict_error(
        self, use_case, minimal_request, mock_user_repository
    ):
        """Test existing LINE User ID raises ConflictError"""
        # Arrange
        existing_user = UserModel(
            user_id=uuid4(),
            line_user_id=minimal_request.line_user_id,
            role=UserRole.PATIENT.value,
            email=None,
            hashed_password=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            deleted_at=None,
        )
        mock_user_repository.find_by_line_user_id.return_value = existing_user

        # Act & Assert
        with pytest.raises(ConflictError) as exc_info:
            await use_case.execute(minimal_request)

        assert exc_info.value.resource_type == "Patient"
        assert exc_info.value.conflict_field == "line_user_id"
        assert exc_info.value.value == minimal_request.line_user_id
