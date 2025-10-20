"""
Patient Repository Integration Tests
Tests the PatientRepositoryImpl with real database operations

Run with: pytest tests/integration/database/test_patient_repository.py -v
"""
import pytest
from datetime import date
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.infrastructure.repositories.patient_repository_impl import (
    PatientRepositoryImpl,
)
from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
from respira_ally.infrastructure.database.models.user import UserModel


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
async def therapist_user(db_session: AsyncSession) -> UserModel:
    """Create a therapist user for testing"""
    therapist = UserModel(
        line_user_id=f"therapist_{uuid4().hex[:8]}",
        role="THERAPIST",
        email=f"therapist_{uuid4().hex[:8]}@test.com",
        hashed_password="hashed_password_123",
    )
    db_session.add(therapist)
    await db_session.commit()
    await db_session.refresh(therapist)
    return therapist


@pytest.fixture
async def patient_repository(db_session: AsyncSession) -> PatientRepositoryImpl:
    """Create PatientRepository instance"""
    return PatientRepositoryImpl(db_session)


@pytest.fixture
def sample_patient_data(therapist_user: UserModel) -> dict:
    """Sample patient data for testing"""
    return {
        "user_id": uuid4(),
        "therapist_id": therapist_user.user_id,
        "name": ",fÅ£",
        "birth_date": date(1970, 1, 1),
        "gender": "MALE",
        "height_cm": 170,
        "weight_kg": Decimal("70.5"),
        "contact_info": {"phone": "0912345678"},
        "medical_history": {},
    }


# ============================================================================
# Tests: Create Operations
# ============================================================================

@pytest.mark.asyncio
async def test_create_patient_success(
    patient_repository: PatientRepositoryImpl,
    sample_patient_data: dict,
):
    """Test successfully creating a new patient"""
    # Arrange
    patient = PatientProfileModel(**sample_patient_data)

    # Act
    created = await patient_repository.create(patient)

    # Assert
    assert created.user_id == sample_patient_data["user_id"]
    assert created.name == sample_patient_data["name"]
    assert created.therapist_id == sample_patient_data["therapist_id"]
    assert created.birth_date == sample_patient_data["birth_date"]
    assert created.gender == sample_patient_data["gender"]


@pytest.mark.asyncio
async def test_create_patient_with_minimal_data(
    patient_repository: PatientRepositoryImpl,
    therapist_user: UserModel,
):
    """Test creating patient with only required fields"""
    # Arrange
    patient = PatientProfileModel(
        user_id=uuid4(),
        therapist_id=therapist_user.user_id,
        name="u!Å£",
        birth_date=date(1980, 5, 15),
        contact_info={},
        medical_history={},
    )

    # Act
    created = await patient_repository.create(patient)

    # Assert
    assert created.name == "u!Å£"
    assert created.height_cm is None
    assert created.weight_kg is None
    assert created.gender is None


# ============================================================================
# Tests: Read Operations
# ============================================================================

@pytest.mark.asyncio
async def test_get_by_id_exists(
    patient_repository: PatientRepositoryImpl,
    sample_patient_data: dict,
):
    """Test retrieving existing patient by ID"""
    # Arrange
    patient = PatientProfileModel(**sample_patient_data)
    await patient_repository.create(patient)

    # Act
    retrieved = await patient_repository.get_by_id(sample_patient_data["user_id"])

    # Assert
    assert retrieved is not None
    assert retrieved.user_id == sample_patient_data["user_id"]
    assert retrieved.name == sample_patient_data["name"]


@pytest.mark.asyncio
async def test_get_by_id_not_found(
    patient_repository: PatientRepositoryImpl,
):
    """Test retrieving non-existent patient returns None"""
    # Act
    retrieved = await patient_repository.get_by_id(uuid4())

    # Assert
    assert retrieved is None


@pytest.mark.asyncio
async def test_exists_true(
    patient_repository: PatientRepositoryImpl,
    sample_patient_data: dict,
):
    """Test exists() returns True for existing patient"""
    # Arrange
    patient = PatientProfileModel(**sample_patient_data)
    await patient_repository.create(patient)

    # Act
    exists = await patient_repository.exists(sample_patient_data["user_id"])

    # Assert
    assert exists is True


@pytest.mark.asyncio
async def test_exists_false(
    patient_repository: PatientRepositoryImpl,
):
    """Test exists() returns False for non-existent patient"""
    # Act
    exists = await patient_repository.exists(uuid4())

    # Assert
    assert exists is False


# ============================================================================
# Tests: List Operations
# ============================================================================

@pytest.mark.asyncio
async def test_list_by_therapist_empty(
    patient_repository: PatientRepositoryImpl,
    therapist_user: UserModel,
):
    """Test listing patients when therapist has no patients"""
    # Act
    patients, total = await patient_repository.list_by_therapist(
        therapist_id=therapist_user.user_id
    )

    # Assert
    assert len(patients) == 0
    assert total == 0


@pytest.mark.asyncio
async def test_list_by_therapist_multiple_patients(
    patient_repository: PatientRepositoryImpl,
    therapist_user: UserModel,
):
    """Test listing multiple patients for a therapist"""
    # Arrange - Create 3 patients
    for i in range(3):
        patient = PatientProfileModel(
            user_id=uuid4(),
            therapist_id=therapist_user.user_id,
            name=f"Å£{i+1}",
            birth_date=date(1970 + i, 1, 1),
            contact_info={},
            medical_history={},
        )
        await patient_repository.create(patient)

    # Act
    patients, total = await patient_repository.list_by_therapist(
        therapist_id=therapist_user.user_id
    )

    # Assert
    assert len(patients) == 3
    assert total == 3
    # Verify ordering by name
    assert patients[0].name == "Å£1"
    assert patients[1].name == "Å£2"
    assert patients[2].name == "Å£3"


@pytest.mark.asyncio
async def test_list_by_therapist_pagination(
    patient_repository: PatientRepositoryImpl,
    therapist_user: UserModel,
):
    """Test pagination in list_by_therapist"""
    # Arrange - Create 5 patients
    for i in range(5):
        patient = PatientProfileModel(
            user_id=uuid4(),
            therapist_id=therapist_user.user_id,
            name=f"Å£{i+1:02d}",
            birth_date=date(1970, 1, 1),
            contact_info={},
            medical_history={},
        )
        await patient_repository.create(patient)

    # Act - Get first page (2 items)
    page1_patients, total = await patient_repository.list_by_therapist(
        therapist_id=therapist_user.user_id,
        skip=0,
        limit=2,
    )

    # Act - Get second page (2 items)
    page2_patients, _ = await patient_repository.list_by_therapist(
        therapist_id=therapist_user.user_id,
        skip=2,
        limit=2,
    )

    # Assert
    assert total == 5
    assert len(page1_patients) == 2
    assert len(page2_patients) == 2
    assert page1_patients[0].user_id != page2_patients[0].user_id


@pytest.mark.asyncio
async def test_count_by_therapist(
    patient_repository: PatientRepositoryImpl,
    therapist_user: UserModel,
):
    """Test counting patients assigned to a therapist"""
    # Arrange - Create 3 patients
    for i in range(3):
        patient = PatientProfileModel(
            user_id=uuid4(),
            therapist_id=therapist_user.user_id,
            name=f"Å£{i+1}",
            birth_date=date(1970, 1, 1),
            contact_info={},
            medical_history={},
        )
        await patient_repository.create(patient)

    # Act
    count = await patient_repository.count_by_therapist(therapist_user.user_id)

    # Assert
    assert count == 3


# ============================================================================
# Tests: Update Operations
# ============================================================================

@pytest.mark.asyncio
async def test_update_patient_success(
    patient_repository: PatientRepositoryImpl,
    sample_patient_data: dict,
):
    """Test successfully updating patient information"""
    # Arrange
    patient = PatientProfileModel(**sample_patient_data)
    await patient_repository.create(patient)

    # Act
    update_data = {
        "name": "ô°Œ„W",
        "height_cm": 175,
        "weight_kg": Decimal("75.0"),
    }
    updated = await patient_repository.update(
        user_id=sample_patient_data["user_id"],
        update_data=update_data,
    )

    # Assert
    assert updated is not None
    assert updated.name == "ô°Œ„W"
    assert updated.height_cm == 175
    assert updated.weight_kg == Decimal("75.0")
    # Unchanged fields
    assert updated.birth_date == sample_patient_data["birth_date"]
    assert updated.gender == sample_patient_data["gender"]


@pytest.mark.asyncio
async def test_update_patient_partial(
    patient_repository: PatientRepositoryImpl,
    sample_patient_data: dict,
):
    """Test partial update (only one field)"""
    # Arrange
    patient = PatientProfileModel(**sample_patient_data)
    await patient_repository.create(patient)

    # Act
    updated = await patient_repository.update(
        user_id=sample_patient_data["user_id"],
        update_data={"name": "ê9W"},
    )

    # Assert
    assert updated.name == "ê9W"
    assert updated.height_cm == sample_patient_data["height_cm"]
    assert updated.weight_kg == sample_patient_data["weight_kg"]


@pytest.mark.asyncio
async def test_update_patient_not_found(
    patient_repository: PatientRepositoryImpl,
):
    """Test updating non-existent patient returns None"""
    # Act
    updated = await patient_repository.update(
        user_id=uuid4(),
        update_data={"name": "X(„Å£"},
    )

    # Assert
    assert updated is None


# ============================================================================
# Tests: Delete Operations
# ============================================================================

@pytest.mark.asyncio
async def test_delete_patient_success(
    patient_repository: PatientRepositoryImpl,
    sample_patient_data: dict,
):
    """Test successfully deleting a patient"""
    # Arrange
    patient = PatientProfileModel(**sample_patient_data)
    await patient_repository.create(patient)

    # Act
    deleted = await patient_repository.delete(sample_patient_data["user_id"])

    # Assert
    assert deleted is True
    # Verify patient is really deleted
    retrieved = await patient_repository.get_by_id(sample_patient_data["user_id"])
    assert retrieved is None


@pytest.mark.asyncio
async def test_delete_patient_not_found(
    patient_repository: PatientRepositoryImpl,
):
    """Test deleting non-existent patient returns False"""
    # Act
    deleted = await patient_repository.delete(uuid4())

    # Assert
    assert deleted is False
