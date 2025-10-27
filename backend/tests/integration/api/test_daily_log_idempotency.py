"""
Daily Log API Idempotency Tests
Tests Idempotency-Key header support for POST /daily-logs

Run with: pytest tests/integration/api/test_daily_log_idempotency.py -v
"""

from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.infrastructure.database.models.user import UserModel

# ============================================================================
# POST /api/v1/daily-logs - Idempotency Tests
# ============================================================================


@pytest.mark.asyncio
async def test_idempotency_key_returns_cached_response(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test Idempotency-Key returns cached response on duplicate request

    Scenario:
    1. Send POST with Idempotency-Key: "test-key-123"
    2. Send same POST with same key
    3. Should return cached response (same log_id)

    Expected: Both responses identical (idempotent)
    """
    # Prepare data
    idempotency_key = str(uuid4())
    data = {
        "patient_id": str(patient_user.user_id),
        "log_date": date.today().isoformat(),
        "medication_taken": True,
        "water_intake_ml": 2000,
        "steps_count": 5000,
    }

    # First request
    response1 = client.post(
        "/api/v1/daily-logs/",
        json=data,
        headers={
            "Authorization": f"Bearer {patient_token}",
            "Idempotency-Key": idempotency_key,
        },
    )

    assert (
        response1.status_code == 201
    ), f"Expected 201, got {response1.status_code}: {response1.text}"
    log1 = response1.json()

    # Second request with SAME idempotency key
    response2 = client.post(
        "/api/v1/daily-logs/",
        json=data,
        headers={
            "Authorization": f"Bearer {patient_token}",
            "Idempotency-Key": idempotency_key,
        },
    )

    assert response2.status_code == 201
    log2 = response2.json()

    # Verify responses are identical (idempotent)
    assert log1["log_id"] == log2["log_id"], "Idempotent requests should return same log_id"
    assert log1["created_at"] == log2["created_at"], "Created timestamp should match"
    assert log1["water_intake_ml"] == log2["water_intake_ml"]


@pytest.mark.asyncio
async def test_different_idempotency_keys_create_different_responses(
    client: TestClient,
    db_session: AsyncSession,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test different Idempotency-Key values create different responses

    Scenario:
    1. Send POST with Idempotency-Key: "key-1"
    2. Send POST with Idempotency-Key: "key-2"
    3. Should create different cached responses

    Expected: Different keys → different responses (normal behavior)
    Note: Same date will UPDATE the log (upsert behavior)
    """
    today = date.today().isoformat()

    # First request with key-1
    data1 = {
        "patient_id": str(patient_user.user_id),
        "log_date": today,
        "medication_taken": True,
        "water_intake_ml": 2000,
    }
    response1 = client.post(
        "/api/v1/daily-logs/",
        json=data1,
        headers={
            "Authorization": f"Bearer {patient_token}",
            "Idempotency-Key": "key-1",
        },
    )
    assert response1.status_code == 201
    log1 = response1.json()

    # Second request with key-2 (different key, same date → will update)
    data2 = {
        "patient_id": str(patient_user.user_id),
        "log_date": today,
        "medication_taken": False,
        "water_intake_ml": 3000,  # Different value
    }
    response2 = client.post(
        "/api/v1/daily-logs/",
        json=data2,
        headers={
            "Authorization": f"Bearer {patient_token}",
            "Idempotency-Key": "key-2",
        },
    )
    assert response2.status_code == 201
    log2 = response2.json()

    # Verify: Same log (upsert), but cached responses differ
    assert log1["log_id"] == log2["log_id"], "Same date → same log (upsert)"
    assert log2["water_intake_ml"] == 3000, "Should reflect updated value"


@pytest.mark.asyncio
async def test_no_idempotency_key_allows_normal_upsert(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test request without Idempotency-Key works normally

    Scenario: Send POST without Idempotency-Key header
    Expected: Normal upsert behavior (no caching)
    """
    data = {
        "patient_id": str(patient_user.user_id),
        "log_date": date.today().isoformat(),
        "medication_taken": True,
        "water_intake_ml": 2000,
    }

    # First request (no idempotency key)
    response1 = client.post(
        "/api/v1/daily-logs/",
        json=data,
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert response1.status_code == 201
    log1_id = response1.json()["log_id"]

    # Second request (no idempotency key, same date)
    data["water_intake_ml"] = 3000
    response2 = client.post(
        "/api/v1/daily-logs/",
        json=data,
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert response2.status_code == 201
    log2 = response2.json()

    # Verify: Same log updated (upsert)
    assert log2["log_id"] == log1_id, "Same date → same log"
    assert log2["water_intake_ml"] == 3000, "Should show updated value"


@pytest.mark.asyncio
async def test_idempotency_key_with_validation_error(
    client: TestClient,
    db_session: AsyncSession,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test Idempotency-Key with validation error

    Scenario: Send invalid data with Idempotency-Key
    Expected: Error response (should NOT be cached)
    """
    idempotency_key = str(uuid4())
    invalid_data = {
        "patient_id": str(patient_user.user_id),
        "log_date": "2030-01-01",  # Future date (invalid)
        "medication_taken": True,
        "water_intake_ml": 2000,
    }

    # First request (should fail validation)
    response1 = client.post(
        "/api/v1/daily-logs/",
        json=invalid_data,
        headers={
            "Authorization": f"Bearer {patient_token}",
            "Idempotency-Key": idempotency_key,
        },
    )
    assert response1.status_code == 422, "Future date should fail validation"

    # Second request with same key (should also fail, not return cached error)
    response2 = client.post(
        "/api/v1/daily-logs/",
        json=invalid_data,
        headers={
            "Authorization": f"Bearer {patient_token}",
            "Idempotency-Key": idempotency_key,
        },
    )
    assert response2.status_code == 422, "Should fail validation again (errors not cached)"


@pytest.mark.asyncio
async def test_idempotency_key_respects_authorization(
    client: TestClient,
    patient_user: UserModel,
    other_patient_user: UserModel,
    patient_token: str,
    other_patient_token: str,
):
    """
    Test Idempotency-Key respects authorization (user-scoped)

    Scenario:
    1. Patient A creates log with idempotency key
    2. Patient B uses SAME idempotency key
    3. Should create separate cached responses (user-scoped security)

    Expected: Idempotency is user-scoped - different users with same key create different logs
    """
    idempotency_key = str(uuid4())
    today = date.today().isoformat()

    # Patient A creates log
    data_a = {
        "patient_id": str(patient_user.user_id),
        "log_date": today,
        "medication_taken": True,
        "water_intake_ml": 2000,
    }
    response_a = client.post(
        "/api/v1/daily-logs/",
        json=data_a,
        headers={
            "Authorization": f"Bearer {patient_token}",
            "Idempotency-Key": idempotency_key,
        },
    )
    assert response_a.status_code == 201
    log_a = response_a.json()

    # Patient B creates log with SAME idempotency key (should work - user-scoped)
    data_b = {
        "patient_id": str(other_patient_user.user_id),
        "log_date": today,
        "medication_taken": False,
        "water_intake_ml": 1500,
    }
    response_b = client.post(
        "/api/v1/daily-logs/",
        json=data_b,
        headers={
            "Authorization": f"Bearer {other_patient_token}",
            "Idempotency-Key": idempotency_key,
        },
    )
    assert response_b.status_code == 201
    log_b = response_b.json()

    # Verify: Different logs created (user-scoped idempotency - SECURITY FIX)
    assert log_a["log_id"] != log_b["log_id"], "Different users should create different logs"
    assert log_a["patient_id"] == str(patient_user.user_id), "Patient A's log belongs to A"
    assert log_b["patient_id"] == str(other_patient_user.user_id), "Patient B's log belongs to B"
    assert log_a["water_intake_ml"] == 2000, "Patient A's data is correct"
    assert log_b["water_intake_ml"] == 1500, "Patient B's data is correct"
