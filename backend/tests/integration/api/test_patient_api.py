"""
Patient API Integration Tests
Tests all Patient API endpoints with database integration

Run with: pytest tests/integration/api/test_patient_api.py -v
"""

from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.infrastructure.database.models.user import UserModel

# ============================================================================
# POST /api/v1/patients - Create Patient
# ============================================================================


@pytest.mark.asyncio
async def test_create_patient_success(
    client: TestClient,
    therapist_user: UserModel,
    therapist_token: str,
    db_session: AsyncSession,
):
    """
    Test creating a new patient successfully (Happy Path)

    Scenario: Therapist creates a new patient
    Expected: 201 Created, patient data returned
    """
    # Arrange
    patient_data = {
        "name": "John Doe",
        "birth_date": "1960-05-15",
        "gender": "MALE",
        "therapist_id": str(therapist_user.user_id),
        "height_cm": 175,
        "weight_kg": 80.5,
        "phone": "0912345678",
    }

    # Act
    response = client.post(
        "/api/v1/patients",
        json=patient_data,
        headers={"Authorization": f"Bearer {therapist_token}"},
    )

    # Assert
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["gender"] == "MALE"
    assert data["therapist_id"] == str(therapist_user.user_id)
    assert "user_id" in data
    assert UUID(data["user_id"])  # Valid UUID


@pytest.mark.asyncio
async def test_create_patient_as_patient_forbidden(
    client: TestClient,
    therapist_user: UserModel,
    patient_token: str,
):
    """
    Test creating patient as patient role (Error Case - 403)

    Scenario: Patient tries to create another patient
    Expected: 403 Forbidden
    """
    # Arrange
    patient_data = {
        "name": "Jane Doe",
        "birth_date": "1970-01-01",
        "gender": "FEMALE",
        "therapist_id": str(therapist_user.user_id),
    }

    # Act
    response = client.post(
        "/api/v1/patients", json=patient_data, headers={"Authorization": f"Bearer {patient_token}"}
    )

    # Assert
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    assert "Therapist" in response.json()["detail"] or "therapist" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_patient_invalid_therapist(
    client: TestClient,
    therapist_token: str,
):
    """
    Test creating patient with invalid therapist ID (Error Case - 404)

    Scenario: Create patient with non-existent therapist
    Expected: 404 Not Found
    """
    # Arrange
    from uuid import uuid4

    invalid_therapist_id = str(uuid4())
    patient_data = {
        "name": "Test Patient",
        "birth_date": "1980-10-20",
        "gender": "OTHER",
        "therapist_id": invalid_therapist_id,
    }

    # Act
    response = client.post(
        "/api/v1/patients",
        json=patient_data,
        headers={"Authorization": f"Bearer {therapist_token}"},
    )

    # Assert
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    assert "Therapist not found" in response.json()["detail"]


# ============================================================================
# GET /api/v1/patients/{user_id} - Get Single Patient
# ============================================================================


@pytest.mark.asyncio
async def test_get_patient_as_therapist_success(
    client: TestClient,
    patient_user: UserModel,
    therapist_token: str,
):
    """
    Test therapist getting their own patient (Happy Path)

    Scenario: Therapist retrieves patient details
    Expected: 200 OK, patient data returned
    """
    # Act
    response = client.get(
        f"/api/v1/patients/{patient_user.user_id}",
        headers={"Authorization": f"Bearer {therapist_token}"},
    )

    # Assert
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["user_id"] == str(patient_user.user_id)
    assert data["name"] == "Test Patient"


@pytest.mark.asyncio
async def test_get_patient_as_self_success(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test patient getting their own profile (Happy Path)

    Scenario: Patient retrieves own details
    Expected: 200 OK, patient data returned
    """
    # Act
    response = client.get(
        f"/api/v1/patients/{patient_user.user_id}",
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    # Assert
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["user_id"] == str(patient_user.user_id)


@pytest.mark.asyncio
async def test_get_other_patient_forbidden(
    client: TestClient,
    other_patient_user: UserModel,
    patient_token: str,
):
    """
    Test patient getting another patient's profile (Error Case - 403)

    Scenario: Patient tries to access another patient's data
    Expected: 403 Forbidden
    """
    # Act
    response = client.get(
        f"/api/v1/patients/{other_patient_user.user_id}",
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    # Assert
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"


@pytest.mark.asyncio
async def test_get_patient_not_found(
    client: TestClient,
    therapist_token: str,
):
    """
    Test getting non-existent patient (Error Case - 404)

    Scenario: Request patient with invalid ID
    Expected: 404 Not Found
    """
    # Arrange
    from uuid import uuid4

    invalid_id = str(uuid4())

    # Act
    response = client.get(
        f"/api/v1/patients/{invalid_id}", headers={"Authorization": f"Bearer {therapist_token}"}
    )

    # Assert
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"


# ============================================================================
# GET /api/v1/patients - List Patients
# ============================================================================


@pytest.mark.asyncio
async def test_list_patients_success(
    client: TestClient,
    patient_user: UserModel,
    therapist_token: str,
):
    """
    Test listing patients with pagination (Happy Path)

    Scenario: Therapist lists their patients
    Expected: 200 OK, paginated patient list
    """
    # Act
    response = client.get(
        "/api/v1/patients?page=0&page_size=20",
        headers={"Authorization": f"Bearer {therapist_token}"},
    )

    # Assert
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert data["total"] >= 1  # At least the patient_user fixture
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_list_patients_with_pagination(
    client: TestClient,
    therapist_token: str,
):
    """
    Test pagination parameters work correctly (Happy Path)

    Scenario: Request specific page size
    Expected: 200 OK, correct page size returned
    """
    # Act
    response = client.get(
        "/api/v1/patients?page=0&page_size=5",
        headers={"Authorization": f"Bearer {therapist_token}"},
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 0
    assert data["page_size"] == 5
    assert len(data["items"]) <= 5


@pytest.mark.asyncio
async def test_list_patients_with_search(
    client: TestClient,
    patient_user: UserModel,
    therapist_token: str,
):
    """
    Test search functionality (Happy Path)

    Scenario: Search patients by name
    Expected: 200 OK, filtered results
    """
    # Act
    response = client.get(
        "/api/v1/patients?search=Test", headers={"Authorization": f"Bearer {therapist_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    # Verify search results contain "Test"
    for item in data["items"]:
        assert "Test" in item["name"] or "test" in item["name"].lower()


@pytest.mark.asyncio
async def test_list_patients_as_patient_forbidden(
    client: TestClient,
    patient_token: str,
):
    """
    Test patient role cannot list all patients (Error Case - 403)

    Scenario: Patient tries to list patients
    Expected: 403 Forbidden
    """
    # Act
    response = client.get("/api/v1/patients", headers={"Authorization": f"Bearer {patient_token}"})

    # Assert
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"


# ============================================================================
# Edge Cases & Validation Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_patient_invalid_birth_date(
    client: TestClient,
    therapist_user: UserModel,
    therapist_token: str,
):
    """
    Test creating patient with invalid birth date (Error Case - 422)

    Scenario: Birth date in future
    Expected: 422 Validation Error
    """
    # Arrange
    patient_data = {
        "name": "Future Baby",
        "birth_date": "2030-01-01",  # Future date
        "gender": "MALE",
        "therapist_id": str(therapist_user.user_id),
    }

    # Act
    response = client.post(
        "/api/v1/patients",
        json=patient_data,
        headers={"Authorization": f"Bearer {therapist_token}"},
    )

    # Assert
    assert response.status_code in [422, 400], f"Expected 422 or 400, got {response.status_code}"


@pytest.mark.asyncio
async def test_create_patient_invalid_height(
    client: TestClient,
    therapist_user: UserModel,
    therapist_token: str,
):
    """
    Test creating patient with invalid height (Error Case - 422)

    Scenario: Height out of valid range
    Expected: 422 Validation Error
    """
    # Arrange
    patient_data = {
        "name": "Tall Giant",
        "birth_date": "1990-01-01",
        "gender": "MALE",
        "therapist_id": str(therapist_user.user_id),
        "height_cm": 300,  # Too tall (max 250)
    }

    # Act
    response = client.post(
        "/api/v1/patients",
        json=patient_data,
        headers={"Authorization": f"Bearer {therapist_token}"},
    )

    # Assert
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_get_patient_without_auth(client: TestClient, patient_user: UserModel):
    """
    Test accessing patient without authentication (Error Case - 401)

    Scenario: No Authorization header
    Expected: 401 Unauthorized
    """
    # Act
    response = client.get(f"/api/v1/patients/{patient_user.user_id}")

    # Assert
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
