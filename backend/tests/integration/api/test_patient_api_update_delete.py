"""
Patient API Integration Tests - Update & Delete
Tests PATCH and DELETE endpoints for Patient API

Run with: pytest tests/integration/api/test_patient_api_update_delete.py -v
"""

import pytest
from fastapi.testclient import TestClient

from respira_ally.infrastructure.database.models.user import UserModel

# ============================================================================
# PATCH /api/v1/patients/{id} - Update Patient
# ============================================================================


@pytest.mark.asyncio
async def test_update_patient_success(
    client: TestClient,
    therapist_user: UserModel,
    patient_user: UserModel,
    therapist_token: str,
):
    """
    Test updating patient information successfully (Happy Path)

    Scenario: Therapist updates their own patient's weight
    Expected: 200 OK, patient data updated with new BMI

    Note: patient_user fixture already has a patient profile created
    """
    # Update data (patient_user already has a profile)
    update_data = {"weight_kg": 75.5, "phone": "0912345678"}

    # Act
    response = client.patch(
        f"/api/v1/patients/{patient_user.user_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {therapist_token}"},
    )

    # Assert
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert float(data["weight_kg"]) == 75.5  # API returns Decimal as string
    assert data["phone"] == "0912345678"
    assert data["bmi"] is not None  # BMI should be recalculated


@pytest.mark.asyncio
async def test_update_patient_partial_fields(
    client: TestClient,
    therapist_user: UserModel,
    patient_user: UserModel,
    therapist_token: str,
):
    """
    Test PATCH partial update (only name field)

    Scenario: Therapist updates only the patient's name
    Expected: 200 OK, only name changed, other fields unchanged

    Note: patient_user fixture already has a patient profile created
    """
    # Update only name (patient_user already has a profile)
    update_data = {"name": "New Name"}

    # Act
    response = client.patch(
        f"/api/v1/patients/{patient_user.user_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {therapist_token}"},
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert float(data["weight_kg"]) == 70.5  # Unchanged (from fixture)
    assert data["height_cm"] == 170  # Unchanged (from fixture)


@pytest.mark.asyncio
async def test_update_patient_forbidden(
    client: TestClient,
    therapist_user: UserModel,
    other_patient_user: UserModel,
    therapist_token: str,
):
    """
    Test updating another therapist's patient (Error Case - 403)

    Scenario: Therapist tries to update patient assigned to another therapist
    Expected: 403 Forbidden
    """
    # Act - Try to update other therapist's patient
    update_data = {"weight_kg": 80.0}
    response = client.patch(
        f"/api/v1/patients/{other_patient_user.user_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {therapist_token}"},
    )

    # Assert
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    assert "own patients" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_patient_not_found(
    client: TestClient,
    therapist_user: UserModel,
    therapist_token: str,
):
    """
    Test updating non-existent patient (Error Case - 404)

    Scenario: Patient ID does not exist
    Expected: 404 Not Found
    """
    # Act
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    update_data = {"weight_kg": 80.0}
    response = client.patch(
        f"/api/v1/patients/{fake_uuid}",
        json=update_data,
        headers={"Authorization": f"Bearer {therapist_token}"},
    )

    # Assert
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"


@pytest.mark.asyncio
async def test_update_patient_without_auth(
    client: TestClient,
    patient_user: UserModel,
):
    """
    Test updating patient without authentication (Error Case - 401)

    Scenario: No Authorization header
    Expected: 401 Unauthorized
    """
    # Act
    update_data = {"weight_kg": 80.0}
    response = client.patch(f"/api/v1/patients/{patient_user.user_id}", json=update_data)

    # Assert
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"


# ============================================================================
# DELETE /api/v1/patients/{id} - Delete Patient
# ============================================================================


@pytest.mark.asyncio
async def test_delete_patient_success(
    client: TestClient,
    patient_user: UserModel,
    therapist_token: str,
):
    """
    Test deleting patient successfully (Happy Path)

    Scenario: Therapist deletes their own patient
    Expected: 204 No Content

    Note: patient_user fixture already has a patient profile created
    """
    # Act (patient_user already has a profile)
    response = client.delete(
        f"/api/v1/patients/{patient_user.user_id}",
        headers={"Authorization": f"Bearer {therapist_token}"},
    )

    # Assert
    assert response.status_code == 204, f"Expected 204, got {response.status_code}"

    # Verify patient is deleted (subsequent GET should fail)
    get_response = client.get(
        f"/api/v1/patients/{patient_user.user_id}",
        headers={"Authorization": f"Bearer {therapist_token}"},
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_patient_forbidden(
    client: TestClient,
    therapist_user: UserModel,
    other_patient_user: UserModel,
    therapist_token: str,
):
    """
    Test deleting another therapist's patient (Error Case - 403)

    Scenario: Therapist tries to delete patient assigned to another therapist
    Expected: 403 Forbidden
    """
    # Act
    response = client.delete(
        f"/api/v1/patients/{other_patient_user.user_id}",
        headers={"Authorization": f"Bearer {therapist_token}"},
    )

    # Assert
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    assert "own patients" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_patient_not_found(
    client: TestClient,
    therapist_token: str,
):
    """
    Test deleting non-existent patient (Error Case - 404)

    Scenario: Patient ID does not exist
    Expected: 404 Not Found
    """
    # Act
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.delete(
        f"/api/v1/patients/{fake_uuid}", headers={"Authorization": f"Bearer {therapist_token}"}
    )

    # Assert
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"


@pytest.mark.asyncio
async def test_delete_patient_without_auth(
    client: TestClient,
    patient_user: UserModel,
):
    """
    Test deleting patient without authentication (Error Case - 401)

    Scenario: No Authorization header
    Expected: 401 Unauthorized
    """
    # Act
    response = client.delete(f"/api/v1/patients/{patient_user.user_id}")

    # Assert
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
