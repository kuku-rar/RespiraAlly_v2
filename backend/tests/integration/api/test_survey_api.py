"""
Survey API Integration Tests
Tests all Survey API endpoints (CAT and mMRC) with database integration

Run with: pytest tests/integration/api/test_survey_api.py -v
"""


import pytest
from fastapi.testclient import TestClient

from respira_ally.infrastructure.database.models.user import UserModel

# ============================================================================
# POST /api/v1/surveys/cat - Submit CAT Survey
# ============================================================================


@pytest.mark.asyncio
async def test_submit_cat_survey_success(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test submitting a CAT survey successfully (Happy Path)

    Scenario: Patient submits CAT survey for the first time
    Expected: 201 Created, survey data with calculated score and severity
    """
    # Arrange - CAT survey with total score = 15 (MODERATE)
    survey_data = {
        "patient_id": str(patient_user.user_id),
        "answers": {
            "q1_cough": 2,
            "q2_mucus": 2,
            "q3_chest_tightness": 2,
            "q4_breathlessness_stairs": 2,
            "q5_activity_limitation": 2,
            "q6_confidence_leaving_home": 2,
            "q7_sleep_quality": 2,
            "q8_energy_level": 1,
        },
    }

    # Act
    response = client.post(
        "/api/v1/surveys/cat",
        json=survey_data,
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    # Assert
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["patient_id"] == str(patient_user.user_id)
    assert data["survey_type"] == "CAT"
    assert data["total_score"] == 15
    assert data["severity_level"] == "MODERATE"
    assert "response_id" in data
    assert "submitted_at" in data


@pytest.mark.asyncio
async def test_submit_cat_survey_mild_severity(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test CAT survey with MILD severity (score 0-10)
    """
    survey_data = {
        "patient_id": str(patient_user.user_id),
        "answers": {
            "q1_cough": 1,
            "q2_mucus": 1,
            "q3_chest_tightness": 1,
            "q4_breathlessness_stairs": 1,
            "q5_activity_limitation": 1,
            "q6_confidence_leaving_home": 1,
            "q7_sleep_quality": 1,
            "q8_energy_level": 1,
        },
    }

    response = client.post(
        "/api/v1/surveys/cat",
        json=survey_data,
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["total_score"] == 8
    assert data["severity_level"] == "MILD"


@pytest.mark.asyncio
async def test_submit_cat_survey_very_severe(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test CAT survey with VERY_SEVERE severity (score 31-40)
    """
    survey_data = {
        "patient_id": str(patient_user.user_id),
        "answers": {
            "q1_cough": 5,
            "q2_mucus": 5,
            "q3_chest_tightness": 5,
            "q4_breathlessness_stairs": 5,
            "q5_activity_limitation": 4,
            "q6_confidence_leaving_home": 4,
            "q7_sleep_quality": 4,
            "q8_energy_level": 4,
        },
    }

    response = client.post(
        "/api/v1/surveys/cat",
        json=survey_data,
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["total_score"] == 36
    assert data["severity_level"] == "VERY_SEVERE"


@pytest.mark.asyncio
async def test_submit_cat_survey_invalid_score(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test CAT survey with invalid score (out of range)
    Expected: 422 Validation Error
    """
    survey_data = {
        "patient_id": str(patient_user.user_id),
        "answers": {
            "q1_cough": 6,  # Invalid: should be 0-5
            "q2_mucus": 2,
            "q3_chest_tightness": 2,
            "q4_breathlessness_stairs": 2,
            "q5_activity_limitation": 2,
            "q6_confidence_leaving_home": 2,
            "q7_sleep_quality": 2,
            "q8_energy_level": 2,
        },
    }

    response = client.post(
        "/api/v1/surveys/cat",
        json=survey_data,
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_submit_cat_survey_wrong_patient(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test submitting survey for another patient (Security Test)
    Expected: 403 Forbidden
    """
    survey_data = {
        "patient_id": "00000000-0000-0000-0000-000000000000",  # Different patient
        "answers": {
            "q1_cough": 2,
            "q2_mucus": 2,
            "q3_chest_tightness": 2,
            "q4_breathlessness_stairs": 2,
            "q5_activity_limitation": 2,
            "q6_confidence_leaving_home": 2,
            "q7_sleep_quality": 2,
            "q8_energy_level": 2,
        },
    }

    response = client.post(
        "/api/v1/surveys/cat",
        json=survey_data,
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == 403


# ============================================================================
# POST /api/v1/surveys/mmrc - Submit mMRC Survey
# ============================================================================


@pytest.mark.asyncio
async def test_submit_mmrc_survey_success(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test submitting an mMRC survey successfully
    """
    survey_data = {"patient_id": str(patient_user.user_id), "answers": {"grade": 2}}

    response = client.post(
        "/api/v1/surveys/mmrc",
        json=survey_data,
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["patient_id"] == str(patient_user.user_id)
    assert data["survey_type"] == "mMRC"
    assert data["total_score"] == 2
    assert data["severity_level"] == "MODERATE"


@pytest.mark.asyncio
async def test_submit_mmrc_survey_all_grades(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test all mMRC grades (0-4) and their severity mapping
    """
    grade_to_severity = {
        0: "MILD",
        1: "MILD",
        2: "MODERATE",
        3: "SEVERE",
        4: "VERY_SEVERE",
    }

    for grade, expected_severity in grade_to_severity.items():
        survey_data = {"patient_id": str(patient_user.user_id), "answers": {"grade": grade}}

        response = client.post(
            "/api/v1/surveys/mmrc",
            json=survey_data,
            headers={"Authorization": f"Bearer {patient_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["total_score"] == grade
        assert data["severity_level"] == expected_severity


@pytest.mark.asyncio
async def test_submit_mmrc_survey_invalid_grade(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test mMRC survey with invalid grade (out of range 0-4)
    Expected: 422 Validation Error
    """
    survey_data = {
        "patient_id": str(patient_user.user_id),
        "answers": {"grade": 5},  # Invalid: should be 0-4
    }

    response = client.post(
        "/api/v1/surveys/mmrc",
        json=survey_data,
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == 422


# ============================================================================
# GET /api/v1/surveys/{response_id} - Get Survey by ID
# ============================================================================


@pytest.mark.asyncio
async def test_get_survey_by_id_success(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test getting a survey by ID
    """
    # First, create a survey
    survey_data = {
        "patient_id": str(patient_user.user_id),
        "answers": {
            "q1_cough": 2,
            "q2_mucus": 2,
            "q3_chest_tightness": 2,
            "q4_breathlessness_stairs": 2,
            "q5_activity_limitation": 2,
            "q6_confidence_leaving_home": 2,
            "q7_sleep_quality": 2,
            "q8_energy_level": 2,
        },
    }

    create_response = client.post(
        "/api/v1/surveys/cat",
        json=survey_data,
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert create_response.status_code == 201
    response_id = create_response.json()["response_id"]

    # Now, get the survey
    response = client.get(
        f"/api/v1/surveys/{response_id}", headers={"Authorization": f"Bearer {patient_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["response_id"] == response_id
    assert data["survey_type"] == "CAT"


@pytest.mark.asyncio
async def test_get_survey_not_found(
    client: TestClient,
    patient_token: str,
):
    """
    Test getting a non-existent survey
    Expected: 404 Not Found
    """
    response = client.get(
        "/api/v1/surveys/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == 404


# ============================================================================
# GET /api/v1/surveys/patient/{patient_id} - List Patient Surveys
# ============================================================================


@pytest.mark.asyncio
async def test_list_patient_surveys(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test listing all surveys for a patient
    """
    # Create 2 CAT surveys and 1 mMRC survey
    cat_data = {
        "patient_id": str(patient_user.user_id),
        "answers": {
            "q1_cough": 2,
            "q2_mucus": 2,
            "q3_chest_tightness": 2,
            "q4_breathlessness_stairs": 2,
            "q5_activity_limitation": 2,
            "q6_confidence_leaving_home": 2,
            "q7_sleep_quality": 2,
            "q8_energy_level": 2,
        },
    }
    mmrc_data = {"patient_id": str(patient_user.user_id), "answers": {"grade": 2}}

    client.post(
        "/api/v1/surveys/cat", json=cat_data, headers={"Authorization": f"Bearer {patient_token}"}
    )
    client.post(
        "/api/v1/surveys/cat", json=cat_data, headers={"Authorization": f"Bearer {patient_token}"}
    )
    client.post(
        "/api/v1/surveys/mmrc", json=mmrc_data, headers={"Authorization": f"Bearer {patient_token}"}
    )

    # List all surveys
    response = client.get(
        f"/api/v1/surveys/patient/{patient_user.user_id}",
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3
    assert len(data["items"]) >= 3


@pytest.mark.asyncio
async def test_list_patient_surveys_filter_by_type(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test listing surveys filtered by survey type
    """
    # Create surveys
    cat_data = {
        "patient_id": str(patient_user.user_id),
        "answers": {
            "q1_cough": 2,
            "q2_mucus": 2,
            "q3_chest_tightness": 2,
            "q4_breathlessness_stairs": 2,
            "q5_activity_limitation": 2,
            "q6_confidence_leaving_home": 2,
            "q7_sleep_quality": 2,
            "q8_energy_level": 2,
        },
    }
    mmrc_data = {"patient_id": str(patient_user.user_id), "answers": {"grade": 2}}

    client.post(
        "/api/v1/surveys/cat", json=cat_data, headers={"Authorization": f"Bearer {patient_token}"}
    )
    client.post(
        "/api/v1/surveys/mmrc", json=mmrc_data, headers={"Authorization": f"Bearer {patient_token}"}
    )

    # Filter by CAT
    response = client.get(
        f"/api/v1/surveys/patient/{patient_user.user_id}?survey_type=CAT",
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert all(item["survey_type"] == "CAT" for item in data["items"])


# ============================================================================
# GET /api/v1/surveys/cat/patient/{patient_id}/latest - Latest CAT
# ============================================================================


@pytest.mark.asyncio
async def test_get_latest_cat_survey(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test getting the latest CAT survey for a patient
    """
    # Create a CAT survey
    survey_data = {
        "patient_id": str(patient_user.user_id),
        "answers": {
            "q1_cough": 3,
            "q2_mucus": 3,
            "q3_chest_tightness": 3,
            "q4_breathlessness_stairs": 3,
            "q5_activity_limitation": 3,
            "q6_confidence_leaving_home": 3,
            "q7_sleep_quality": 3,
            "q8_energy_level": 3,
        },
    }

    client.post(
        "/api/v1/surveys/cat",
        json=survey_data,
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    # Get latest
    response = client.get(
        f"/api/v1/surveys/cat/patient/{patient_user.user_id}/latest",
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["survey_type"] == "CAT"
    assert data["total_score"] == 24


# ============================================================================
# GET /api/v1/surveys/cat/patient/{patient_id}/stats - CAT Statistics
# ============================================================================


@pytest.mark.asyncio
async def test_get_cat_survey_stats(
    client: TestClient,
    patient_user: UserModel,
    patient_token: str,
):
    """
    Test getting CAT survey statistics
    """
    # Create multiple CAT surveys
    for score in [10, 15, 20]:
        survey_data = {
            "patient_id": str(patient_user.user_id),
            "answers": {
                f"q{i+1}_{'cough' if i == 0 else 'mucus' if i == 1 else 'chest_tightness' if i == 2 else 'breathlessness_stairs' if i == 3 else 'activity_limitation' if i == 4 else 'confidence_leaving_home' if i == 5 else 'sleep_quality' if i == 6 else 'energy_level'}": score
                // 8
                + (1 if i < score % 8 else 0)
                for i in range(8)
            },
        }
        client.post(
            "/api/v1/surveys/cat",
            json=survey_data,
            headers={"Authorization": f"Bearer {patient_token}"},
        )

    # Get statistics
    response = client.get(
        f"/api/v1/surveys/cat/patient/{patient_user.user_id}/stats",
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["survey_type"] == "CAT"
    assert data["total_responses"] >= 3
    assert "avg_score" in data
    assert "trend" in data
    assert data["trend"] in ["IMPROVING", "STABLE", "WORSENING", "INSUFFICIENT_DATA"]


# ============================================================================
# Authorization Tests
# ============================================================================


@pytest.mark.asyncio
async def test_submit_cat_without_auth(client: TestClient):
    """
    Test submitting CAT survey without authentication
    Expected: 401 Unauthorized
    """
    survey_data = {
        "patient_id": "00000000-0000-0000-0000-000000000000",
        "answers": {
            "q1_cough": 2,
            "q2_mucus": 2,
            "q3_chest_tightness": 2,
            "q4_breathlessness_stairs": 2,
            "q5_activity_limitation": 2,
            "q6_confidence_leaving_home": 2,
            "q7_sleep_quality": 2,
            "q8_energy_level": 2,
        },
    }

    response = client.post("/api/v1/surveys/cat", json=survey_data)
    assert response.status_code == 401
