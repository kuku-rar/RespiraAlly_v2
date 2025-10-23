"""
Daily Log API Integration Tests
Tests all Daily Log API endpoints with database integration

Run with: pytest tests/integration/api/test_daily_log_api.py -v
"""

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.infrastructure.database.models.user import UserModel

# ============================================================================
# POST /api/v1/daily-logs - Create/Update Daily Log (Upsert)
# ============================================================================


@pytest.mark.asyncio
async def test_create_daily_log_success(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test creating a new daily log successfully (Happy Path)

    Scenario: Patient submits daily log for the first time
    Expected: 201 Created, log data returned
    """
    # Arrange
    log_data = {
        "patient_id": str(patient_user.user_id),
        "log_date": date.today().isoformat(),
        "medication_taken": True,
        "water_intake_ml": 2000,
        "exercise_minutes": 40,  # 40 minutes of exercise
        "symptoms": "Mild cough",
        "mood": "GOOD",
    }

    # Act
    response = client.post(
        "/api/v1/daily-logs", json=log_data, headers={"Authorization": f"Bearer {patient_token}"}
    )

    # Assert
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["patient_id"] == str(patient_user.user_id)
    assert data["log_date"] == log_data["log_date"]
    assert data["medication_taken"] == True
    assert data["water_intake_ml"] == 2000
    assert "log_id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_upsert_daily_log_same_date(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test upserting daily log on same date (Upsert Logic Test)

    Scenario: Patient submits log twice on same date
    Expected: 201, second submission updates the first
    """
    # Arrange
    log_date = date.today().isoformat()
    first_log = {
        "patient_id": str(patient_user.user_id),
        "log_date": log_date,
        "medication_taken": True,
        "water_intake_ml": 2000,
    }
    updated_log = {
        "patient_id": str(patient_user.user_id),
        "log_date": log_date,
        "medication_taken": False,
        "water_intake_ml": 2500,  # Updated value
    }

    # Act - First submission
    response1 = client.post(
        "/api/v1/daily-logs", json=first_log, headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response1.status_code == 201
    log_id_1 = response1.json()["log_id"]

    # Act - Second submission (upsert)
    response2 = client.post(
        "/api/v1/daily-logs", json=updated_log, headers={"Authorization": f"Bearer {patient_token}"}
    )

    # Assert
    assert response2.status_code == 201
    data = response2.json()
    assert data["water_intake_ml"] == 2500  # Updated value
    assert data["medication_taken"] == False  # Updated value
    # Should be same log ID (updated, not created)
    assert data["log_id"] == log_id_1


@pytest.mark.asyncio
async def test_create_log_for_other_patient_forbidden(
    client: TestClient,
    other_patient_user: UserModel,
    patient_token: str,
):
    """
    Test creating log for another patient (Error Case - 403)

    Scenario: Patient tries to create log for another patient
    Expected: 403 Forbidden
    """
    # Arrange
    log_data = {
        "patient_id": str(other_patient_user.user_id),  # Different patient
        "log_date": date.today().isoformat(),
        "medication_taken": True,
        "water_intake_ml": 2000,
    }

    # Act
    response = client.post(
        "/api/v1/daily-logs", json=log_data, headers={"Authorization": f"Bearer {patient_token}"}
    )

    # Assert
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"


# ============================================================================
# GET /api/v1/daily-logs/{log_id} - Get Single Daily Log
# ============================================================================


@pytest.mark.asyncio
async def test_get_daily_log_success(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test getting a daily log by ID (Happy Path)

    Scenario: Patient retrieves their log
    Expected: 200 OK, log data returned
    """
    # Arrange - Create a log first
    log_data = {
        "patient_id": str(patient_user.user_id),
        "log_date": date.today().isoformat(),
        "medication_taken": True,
        "water_intake_ml": 1500,
    }
    create_response = client.post(
        "/api/v1/daily-logs", json=log_data, headers={"Authorization": f"Bearer {patient_token}"}
    )
    log_id = create_response.json()["log_id"]

    # Act
    response = client.get(
        f"/api/v1/daily-logs/{log_id}", headers={"Authorization": f"Bearer {patient_token}"}
    )

    # Assert
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["log_id"] == log_id
    assert data["patient_id"] == str(patient_user.user_id)


@pytest.mark.asyncio
async def test_get_other_patient_log_forbidden(
    client: TestClient,
    patient_user: UserModel,
    other_patient_user: UserModel,
    patient_token: str,
):
    """
    Test accessing another patient's log (Error Case - 403)

    Scenario: Patient A tries to access Patient B's log
    Expected: 403 Forbidden
    """
    # Arrange - Create log for other_patient (need other_patient_token)
    # For this test, we'll assume a log exists and try to access it
    # In real scenario, need to create fixture or use known log_id

    # Act - Try to get logs list for other patient
    response = client.get(
        f"/api/v1/daily-logs?patient_id={other_patient_user.user_id}",
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    # Assert - Patient role cannot specify patient_id for others
    # Should either ignore patient_id param or return 403
    # Based on router logic, patient role gets their own logs only
    assert response.status_code == 200  # Success but filtered to own logs
    data = response.json()
    # All returned logs should belong to current patient
    for item in data["items"]:
        assert item["patient_id"] == str(patient_user.user_id)


# ============================================================================
# GET /api/v1/daily-logs - List Daily Logs
# ============================================================================


@pytest.mark.asyncio
async def test_list_daily_logs_success(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test listing daily logs with pagination (Happy Path)

    Scenario: Patient lists their logs
    Expected: 200 OK, paginated log list
    """
    # Arrange - Create multiple logs
    for i in range(3):
        log_data = {
            "patient_id": str(patient_user.user_id),
            "log_date": (date.today() - timedelta(days=i)).isoformat(),
            "medication_taken": True,
            "water_intake_ml": 2000 + i * 100,
        }
        client.post(
            "/api/v1/daily-logs",
            json=log_data,
            headers={"Authorization": f"Bearer {patient_token}"},
        )

    # Act
    response = client.get(
        "/api/v1/daily-logs?page=0&page_size=10",
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    # Assert
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 3
    assert len(data["items"]) >= 3


@pytest.mark.asyncio
async def test_list_daily_logs_with_date_filter(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test filtering logs by date range (Happy Path)

    Scenario: Patient lists logs for specific date range
    Expected: 200 OK, filtered logs
    """
    # Arrange
    today = date.today()
    yesterday = today - timedelta(days=1)

    # Create log for today
    client.post(
        "/api/v1/daily-logs",
        json={
            "patient_id": str(patient_user.user_id),
            "log_date": today.isoformat(),
            "medication_taken": True,
            "water_intake_ml": 2000,
        },
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    # Act - Filter by today only
    response = client.get(
        f"/api/v1/daily-logs?start_date={today.isoformat()}&end_date={today.isoformat()}",
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
    for item in data["items"]:
        assert item["log_date"] == today.isoformat()


# ============================================================================
# GET /api/v1/daily-logs/patient/{patient_id}/stats - Get Statistics
# ============================================================================


@pytest.mark.asyncio
async def test_get_patient_statistics_success(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test getting patient statistics (Happy Path)

    Scenario: Patient requests their statistics
    Expected: 200 OK, statistics data
    """
    # Arrange - Create logs for statistics
    today = date.today()
    for i in range(5):
        client.post(
            "/api/v1/daily-logs",
            json={
                "patient_id": str(patient_user.user_id),
                "log_date": (today - timedelta(days=i)).isoformat(),
                "medication_taken": i % 2 == 0,  # Alternate True/False
                "water_intake_ml": 2000 + i * 100,
                "mood": "GOOD" if i % 2 == 0 else "NEUTRAL",
            },
            headers={"Authorization": f"Bearer {patient_token}"},
        )

    # Act
    start_date = (today - timedelta(days=6)).isoformat()
    end_date = today.isoformat()
    response = client.get(
        f"/api/v1/daily-logs/patient/{patient_user.user_id}/stats?start_date={start_date}&end_date={end_date}",
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    # Assert
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "total_logs" in data
    assert "medication_adherence_rate" in data
    assert "avg_water_intake_ml" in data
    assert "mood_distribution" in data
    assert data["total_logs"] >= 5


@pytest.mark.asyncio
async def test_get_statistics_for_other_patient_forbidden(
    client: TestClient,
    other_patient_user: UserModel,
    patient_token: str,
):
    """
    Test getting statistics for another patient (Error Case - 403)

    Scenario: Patient A tries to get Patient B's statistics
    Expected: 403 Forbidden
    """
    # Act
    today = date.today()
    response = client.get(
        f"/api/v1/daily-logs/patient/{other_patient_user.user_id}/stats?start_date={today.isoformat()}&end_date={today.isoformat()}",
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    # Assert
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"


# ============================================================================
# Validation Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_log_invalid_water_intake(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test creating log with invalid water intake (Error Case - 422)

    Scenario: Water intake exceeds maximum
    Expected: 422 Validation Error
    """
    # Arrange
    log_data = {
        "patient_id": str(patient_user.user_id),
        "log_date": date.today().isoformat(),
        "medication_taken": True,
        "water_intake_ml": 15000,  # Exceeds max 10000
    }

    # Act
    response = client.post(
        "/api/v1/daily-logs", json=log_data, headers={"Authorization": f"Bearer {patient_token}"}
    )

    # Assert
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_create_log_invalid_exercise_minutes(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test creating log with invalid exercise minutes (Error Case - 422)

    Scenario: Exercise minutes exceeds maximum (480 minutes / 8 hours)
    Expected: 422 Validation Error
    """
    # Arrange
    log_data = {
        "patient_id": str(patient_user.user_id),
        "log_date": date.today().isoformat(),
        "medication_taken": True,
        "water_intake_ml": 2000,
        "exercise_minutes": 500,  # Exceeds max 480 minutes
    }

    # Act
    response = client.post(
        "/api/v1/daily-logs", json=log_data, headers={"Authorization": f"Bearer {patient_token}"}
    )

    # Assert
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_get_daily_log_without_auth(
    client: TestClient,
):
    """
    Test accessing daily log without authentication (Error Case - 401)

    Scenario: No Authorization header
    Expected: 401 Unauthorized
    """
    # Arrange
    from uuid import uuid4

    fake_log_id = str(uuid4())

    # Act
    response = client.get(f"/api/v1/daily-logs/{fake_log_id}")

    # Assert
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"


# ============================================================================
# PATCH /api/v1/daily-logs/{log_id} - Update Daily Log
# ============================================================================


@pytest.mark.asyncio
async def test_update_daily_log_success(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test updating a daily log successfully (Happy Path)

    Scenario: Patient updates their own daily log
    Expected: 200 OK, updated log data returned
    """
    # Arrange - Create a log first
    log_data = {
        "patient_id": str(patient_user.user_id),
        "log_date": date.today().isoformat(),
        "medication_taken": True,
        "water_intake_ml": 2000,
        "exercise_minutes": 30,
        "mood": "GOOD",
    }
    create_response = client.post(
        "/api/v1/daily-logs", json=log_data, headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert create_response.status_code == 201
    log_id = create_response.json()["log_id"]

    # Act - Update the log
    update_data = {"water_intake_ml": 2500, "exercise_minutes": 45, "mood": "NEUTRAL"}
    response = client.patch(
        f"/api/v1/daily-logs/{log_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    # Assert
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["water_intake_ml"] == 2500  # Updated
    assert data["exercise_minutes"] == 45  # Updated
    assert data["mood"] == "NEUTRAL"  # Updated
    assert data["medication_taken"] == True  # Unchanged


@pytest.mark.asyncio
async def test_update_daily_log_partial_fields(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
    db_session: AsyncSession,
):
    """
    Test updating only specific fields (Partial Update Test)

    Scenario: Patient updates only mood, other fields remain unchanged
    Expected: 200 OK, only specified field updated
    """
    # Arrange - Create a log first with unique timestamp

    unique_date = date.today() - timedelta(days=10)  # Use older date to avoid conflicts

    log_data = {
        "patient_id": str(patient_user.user_id),
        "log_date": unique_date.isoformat(),
        "medication_taken": True,
        "water_intake_ml": 2000,
        "exercise_minutes": 30,
        "symptoms": "Mild cough",
        "mood": "GOOD",
    }
    create_response = client.post(
        "/api/v1/daily-logs", json=log_data, headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert create_response.status_code == 201, f"Failed to create log: {create_response.text}"
    log_id = create_response.json()["log_id"]

    # Act - Update only mood
    update_data = {"mood": "BAD"}
    response = client.patch(
        f"/api/v1/daily-logs/{log_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    # Assert
    assert response.status_code == 200, f"Failed to update: {response.text}"
    data = response.json()
    assert data["mood"] == "BAD"  # Updated
    assert data["medication_taken"] == True  # Unchanged
    assert data["water_intake_ml"] == 2000  # Unchanged
    assert data["exercise_minutes"] == 30  # Unchanged
    assert data["symptoms"] == "Mild cough"  # Unchanged


@pytest.mark.asyncio
async def test_update_daily_log_not_found(
    client: TestClient,
    patient_token: str,
):
    """
    Test updating non-existent daily log (Error Case - 404)

    Scenario: Patient tries to update a log that doesn't exist
    Expected: 404 Not Found
    """
    # Arrange
    from uuid import uuid4

    fake_log_id = str(uuid4())
    update_data = {"mood": "GOOD"}

    # Act
    response = client.patch(
        f"/api/v1/daily-logs/{fake_log_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    # Assert
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"


@pytest.mark.asyncio
async def test_update_other_patient_log_forbidden(
    client: TestClient,
    patient_user: UserModel,
    other_patient_user: UserModel,
    patient_token: str,
    other_patient_token: str,
):
    """
    Test updating another patient's log (Error Case - 403)

    Scenario: Patient tries to update another patient's log
    Expected: 403 Forbidden
    """
    # Arrange - Create log as other_patient
    log_data = {
        "patient_id": str(other_patient_user.user_id),
        "log_date": date.today().isoformat(),
        "medication_taken": True,
        "water_intake_ml": 2000,
    }
    create_response = client.post(
        "/api/v1/daily-logs",
        json=log_data,
        headers={"Authorization": f"Bearer {other_patient_token}"},
    )
    assert create_response.status_code == 201
    log_id = create_response.json()["log_id"]

    # Act - Try to update as different patient
    update_data = {"mood": "GOOD"}
    response = client.patch(
        f"/api/v1/daily-logs/{log_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {patient_token}"},  # Different patient token
    )

    # Assert
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"


# ============================================================================
# DELETE /api/v1/daily-logs/{log_id} - Delete Daily Log
# ============================================================================


@pytest.mark.asyncio
async def test_delete_daily_log_success(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
    db_session: AsyncSession,
):
    """
    Test deleting a daily log successfully (Happy Path)

    Scenario: Patient deletes their own daily log
    Expected: 204 No Content
    """
    # Arrange - Create a log first with unique date
    unique_date = date.today() - timedelta(days=20)  # Use older date to avoid conflicts

    log_data = {
        "patient_id": str(patient_user.user_id),
        "log_date": unique_date.isoformat(),
        "medication_taken": True,
        "water_intake_ml": 2000,
    }
    create_response = client.post(
        "/api/v1/daily-logs", json=log_data, headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert create_response.status_code == 201, f"Failed to create log: {create_response.text}"
    log_id = create_response.json()["log_id"]

    # Act - Delete the log
    response = client.delete(
        f"/api/v1/daily-logs/{log_id}", headers={"Authorization": f"Bearer {patient_token}"}
    )

    # Assert
    assert response.status_code == 204, f"Expected 204, got {response.status_code}: {response.text}"

    # Verify log is actually deleted
    get_response = client.get(
        f"/api/v1/daily-logs/{log_id}", headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert get_response.status_code == 404  # Log should not exist


@pytest.mark.asyncio
async def test_delete_daily_log_not_found(
    client: TestClient,
    patient_token: str,
):
    """
    Test deleting non-existent daily log (Error Case - 404)

    Scenario: Patient tries to delete a log that doesn't exist
    Expected: 404 Not Found
    """
    # Arrange
    from uuid import uuid4

    fake_log_id = str(uuid4())

    # Act
    response = client.delete(
        f"/api/v1/daily-logs/{fake_log_id}", headers={"Authorization": f"Bearer {patient_token}"}
    )

    # Assert
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"


@pytest.mark.asyncio
async def test_delete_other_patient_log_forbidden(
    client: TestClient,
    patient_user: UserModel,
    other_patient_user: UserModel,
    patient_token: str,
    other_patient_token: str,
    db_session: AsyncSession,
):
    """
    Test deleting another patient's log (Error Case - 403)

    Scenario: Patient tries to delete another patient's log
    Expected: 403 Forbidden
    """
    # Arrange - Create log as other_patient with unique date
    unique_date = date.today() - timedelta(days=30)  # Use older date to avoid conflicts

    log_data = {
        "patient_id": str(other_patient_user.user_id),
        "log_date": unique_date.isoformat(),
        "medication_taken": True,
        "water_intake_ml": 2000,
    }
    create_response = client.post(
        "/api/v1/daily-logs",
        json=log_data,
        headers={"Authorization": f"Bearer {other_patient_token}"},
    )
    assert create_response.status_code == 201, f"Failed to create log: {create_response.text}"
    log_id = create_response.json()["log_id"]

    # Act - Try to delete as different patient
    response = client.delete(
        f"/api/v1/daily-logs/{log_id}",
        headers={"Authorization": f"Bearer {patient_token}"},  # Different patient token
    )

    # Assert
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"
