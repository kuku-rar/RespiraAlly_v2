"""
Auth API Integration Tests
Tests all Authentication & Authorization API endpoints

Run with: pytest tests/integration/api/test_auth_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.infrastructure.database.models.user import UserModel

# ============================================================================
# POST /api/v1/auth/therapist/register - Therapist Registration
# ============================================================================


@pytest.mark.asyncio
async def test_therapist_register_success(
    client: TestClient,
    db_session: AsyncSession,
):
    """
    Test therapist registration success (Happy Path)

    Scenario: New therapist registers with valid data
    Expected: 201 Created, tokens returned
    """
    # Arrange
    register_data = {
        "email": "new.therapist@test.com",
        "password": "SecurePass123!",
        "full_name": "Dr. New Therapist",
    }

    # Act
    response = client.post("/api/v1/auth/therapist/register", json=register_data)

    # Assert
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "new.therapist@test.com"
    assert data["user"]["role"] == "THERAPIST"


@pytest.mark.asyncio
async def test_therapist_register_duplicate_email(
    client: TestClient,
    therapist_user: UserModel,
):
    """
    Test therapist registration with duplicate email (Error Case - 409)

    Scenario: Register with existing email
    Expected: 409 Conflict
    """
    # Arrange
    register_data = {
        "email": therapist_user.email,  # Existing email
        "password": "AnotherPass123!",
        "full_name": "Dr. Duplicate",
    }

    # Act
    response = client.post("/api/v1/auth/therapist/register", json=register_data)

    # Assert
    assert response.status_code == 409, f"Expected 409, got {response.status_code}"


@pytest.mark.asyncio
async def test_therapist_register_weak_password(
    client: TestClient,
):
    """
    Test therapist registration with weak password (Error Case - 422)

    Scenario: Register with password < 8 characters
    Expected: 422 Validation Error
    """
    # Arrange
    register_data = {
        "email": "weak@test.com",
        "password": "123",  # Too short
        "full_name": "Dr. Weak",
    }

    # Act
    response = client.post("/api/v1/auth/therapist/register", json=register_data)

    # Assert
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


# ============================================================================
# POST /api/v1/auth/therapist/login - Therapist Login
# ============================================================================


@pytest.mark.asyncio
async def test_therapist_login_success(
    client: TestClient,
    therapist_user: UserModel,
):
    """
    Test therapist login with valid credentials (Happy Path)

    Scenario: Therapist logs in with correct email and password
    Expected: 200 OK, tokens returned
    """
    # Arrange
    login_data = {"email": therapist_user.email, "password": "SecurePass123!"}  # From fixture

    # Act
    response = client.post("/api/v1/auth/therapist/login", json=login_data)

    # Assert
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == therapist_user.email
    assert data["user"]["role"] == "THERAPIST"


@pytest.mark.asyncio
async def test_therapist_login_invalid_password(
    client: TestClient,
    therapist_user: UserModel,
):
    """
    Test therapist login with wrong password (Error Case - 401)

    Scenario: Therapist enters incorrect password
    Expected: 401 Unauthorized
    """
    # Arrange
    login_data = {"email": therapist_user.email, "password": "WrongPassword123!"}

    # Act
    response = client.post("/api/v1/auth/therapist/login", json=login_data)

    # Assert
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"


@pytest.mark.asyncio
async def test_therapist_login_invalid_email(
    client: TestClient,
):
    """
    Test therapist login with non-existent email (Error Case - 401)

    Scenario: Login with email not in database
    Expected: 401 Unauthorized
    """
    # Arrange
    login_data = {"email": "nonexistent@test.com", "password": "SomePassword123!"}

    # Act
    response = client.post("/api/v1/auth/therapist/login", json=login_data)

    # Assert
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"


# ============================================================================
# POST /api/v1/auth/patient/login - Patient Login (LINE OAuth)
# ============================================================================


@pytest.mark.asyncio
async def test_patient_login_success(
    client: TestClient,
    patient_user: UserModel,
):
    """
    Test patient login with LINE user ID (Happy Path)

    Scenario: Patient logs in with LINE OAuth
    Expected: 200 OK, tokens returned
    """
    # Arrange
    login_data = {
        "line_user_id": patient_user.line_user_id,
        "line_access_token": "mock_line_token",  # Mock token
    }

    # Act
    response = client.post("/api/v1/auth/patient/login", json=login_data)

    # Assert
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["role"] == "PATIENT"


@pytest.mark.asyncio
async def test_patient_login_auto_register(
    client: TestClient,
):
    """
    Test patient auto-registration on first login (Happy Path)

    Scenario: New LINE user logs in for first time
    Expected: 200 OK, new user created, tokens returned
    """
    # Arrange
    login_data = {"line_user_id": "new_line_user_12345", "line_access_token": "mock_line_token"}

    # Act
    response = client.post("/api/v1/auth/patient/login", json=login_data)

    # Assert
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "PATIENT"


# ============================================================================
# POST /api/v1/auth/patient/register - Patient Initial Registration
# ============================================================================


@pytest.mark.asyncio
async def test_patient_register_success_with_all_fields(
    client: TestClient,
):
    """
    Test patient registration with all fields (Happy Path)

    Scenario: New patient completes registration via LINE LIFF with full data
    Expected: 201 Created, tokens returned, patient profile created
    """
    # Arrange
    from datetime import date
    from decimal import Decimal

    register_data = {
        "line_user_id": "U_new_patient_123456",
        "line_display_name": "測試病患",
        "line_picture_url": "https://example.com/picture.jpg",
        "full_name": "王小明",
        "date_of_birth": "1980-05-15",
        "gender": "MALE",
        "phone_number": "0912345678",
        "hospital_patient_id": "WF2024001",
        "height_cm": 170,
        "weight_kg": "70.5",
        "smoking_years": 15,
        "emergency_contact_name": "王大明",
        "emergency_contact_phone": "0987654321",
    }

    # Act
    response = client.post("/api/v1/auth/patient/register", json=register_data)

    # Assert
    assert (
        response.status_code == 201
    ), f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()

    # Verify tokens
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    # Verify user info
    assert data["user"]["role"] == "PATIENT"
    assert data["user"]["line_user_id"] == "U_new_patient_123456"
    assert data["user"]["display_name"] == "王小明"


@pytest.mark.asyncio
async def test_patient_register_success_with_minimal_fields(
    client: TestClient,
):
    """
    Test patient registration with only required fields (Happy Path)

    Scenario: Patient registers with minimal data
    Expected: 201 Created, tokens returned
    """
    # Arrange
    register_data = {
        "line_user_id": "U_minimal_patient_789",
        "full_name": "陳小華",
        "date_of_birth": "1990-03-20",
        "gender": "FEMALE",
    }

    # Act
    response = client.post("/api/v1/auth/patient/register", json=register_data)

    # Assert
    assert (
        response.status_code == 201
    ), f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()

    # Verify tokens
    assert "access_token" in data
    assert "refresh_token" in data

    # Verify user info
    assert data["user"]["role"] == "PATIENT"
    assert data["user"]["display_name"] == "陳小華"


@pytest.mark.asyncio
async def test_patient_register_duplicate_line_user_id(
    client: TestClient,
    patient_user: UserModel,
):
    """
    Test patient registration with duplicate LINE User ID (Error Case - 409)

    Scenario: Register with existing LINE User ID
    Expected: 409 Conflict
    """
    # Arrange
    register_data = {
        "line_user_id": patient_user.line_user_id,  # Existing LINE User ID
        "full_name": "重複病患",
        "date_of_birth": "1985-08-10",
        "gender": "MALE",
    }

    # Act
    response = client.post("/api/v1/auth/patient/register", json=register_data)

    # Assert
    assert response.status_code == 409, f"Expected 409, got {response.status_code}: {response.text}"


@pytest.mark.asyncio
async def test_patient_register_missing_required_fields(
    client: TestClient,
):
    """
    Test patient registration with missing required fields (Error Case - 422)

    Scenario: Register without required fields (full_name, date_of_birth, gender)
    Expected: 422 Validation Error
    """
    # Arrange - Missing full_name
    register_data = {
        "line_user_id": "U_invalid_patient_001",
        "date_of_birth": "1985-08-10",
        "gender": "MALE",
    }

    # Act
    response = client.post("/api/v1/auth/patient/register", json=register_data)

    # Assert
    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"


@pytest.mark.asyncio
async def test_patient_register_invalid_name_too_short(
    client: TestClient,
):
    """
    Test patient registration with name < 2 characters (Error Case - 422)

    Scenario: Register with too short name
    Expected: 422 Validation Error
    """
    # Arrange
    register_data = {
        "line_user_id": "U_short_name_patient",
        "full_name": "A",  # Too short (< 2 characters)
        "date_of_birth": "1985-08-10",
        "gender": "MALE",
    }

    # Act
    response = client.post("/api/v1/auth/patient/register", json=register_data)

    # Assert
    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"


@pytest.mark.asyncio
async def test_patient_register_smoking_status_determination(
    client: TestClient,
    db_session: AsyncSession,
):
    """
    Test smoking_status is correctly determined from smoking_years (Business Logic)

    Scenario: Register with smoking_years = 15
    Expected: 201 Created, smoking_status = "CURRENT"
    """
    # Arrange
    register_data = {
        "line_user_id": "U_smoker_patient_555",
        "full_name": "吸菸病患",
        "date_of_birth": "1970-01-15",
        "gender": "MALE",
        "smoking_years": 15,
    }

    # Act
    response = client.post("/api/v1/auth/patient/register", json=register_data)

    # Assert
    assert (
        response.status_code == 201
    ), f"Expected 201, got {response.status_code}: {response.text}"

    # Verify smoking_status in database (requires querying PatientProfileModel)
    from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
    from sqlalchemy import select

    result = await db_session.execute(
        select(PatientProfileModel).where(PatientProfileModel.name == "吸菸病患")
    )
    patient_profile = result.scalars().first()

    assert patient_profile is not None
    assert patient_profile.smoking_years == 15
    assert patient_profile.smoking_status == "CURRENT"


@pytest.mark.asyncio
async def test_patient_register_field_mapping_hospital_id(
    client: TestClient,
    db_session: AsyncSession,
):
    """
    Test hospital_patient_id correctly maps to hospital_medical_record_number

    Scenario: Register with hospital_patient_id
    Expected: 201 Created, field correctly stored in database
    """
    # Arrange
    register_data = {
        "line_user_id": "U_hospital_patient_999",
        "full_name": "醫院病患",
        "date_of_birth": "1978-12-05",
        "gender": "FEMALE",
        "hospital_patient_id": "WF2024999",
    }

    # Act
    response = client.post("/api/v1/auth/patient/register", json=register_data)

    # Assert
    assert (
        response.status_code == 201
    ), f"Expected 201, got {response.status_code}: {response.text}"

    # Verify field mapping in database
    from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
    from sqlalchemy import select

    result = await db_session.execute(
        select(PatientProfileModel).where(PatientProfileModel.name == "醫院病患")
    )
    patient_profile = result.scalars().first()

    assert patient_profile is not None
    assert patient_profile.hospital_medical_record_number == "WF2024999"


@pytest.mark.asyncio
async def test_patient_register_emergency_contact_jsonb(
    client: TestClient,
    db_session: AsyncSession,
):
    """
    Test emergency contact info is correctly stored in contact_info JSONB

    Scenario: Register with emergency contact information
    Expected: 201 Created, contact_info JSONB contains all fields
    """
    # Arrange
    register_data = {
        "line_user_id": "U_emergency_contact_patient",
        "full_name": "緊急聯絡病患",
        "date_of_birth": "1982-07-20",
        "gender": "OTHER",
        "phone_number": "0912345678",
        "emergency_contact_name": "緊急聯絡人",
        "emergency_contact_phone": "0987654321",
    }

    # Act
    response = client.post("/api/v1/auth/patient/register", json=register_data)

    # Assert
    assert (
        response.status_code == 201
    ), f"Expected 201, got {response.status_code}: {response.text}"

    # Verify contact_info JSONB in database
    from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
    from sqlalchemy import select

    result = await db_session.execute(
        select(PatientProfileModel).where(PatientProfileModel.name == "緊急聯絡病患")
    )
    patient_profile = result.scalars().first()

    assert patient_profile is not None
    assert patient_profile.contact_info["phone"] == "0912345678"
    assert patient_profile.contact_info["emergency_contact"] == "緊急聯絡人"
    assert patient_profile.contact_info["emergency_phone"] == "0987654321"


# ============================================================================
# POST /api/v1/auth/logout - Logout
# ============================================================================


@pytest.mark.asyncio
async def test_logout_success(
    client: TestClient,
    therapist_token: str,
):
    """
    Test logout with valid token (Happy Path)

    Scenario: User logs out, token gets blacklisted
    Expected: 204 No Content
    """
    # Arrange
    logout_data = {"revoke_all_tokens": False}

    # Act
    response = client.post(
        "/api/v1/auth/logout",
        json=logout_data,
        headers={"Authorization": f"Bearer {therapist_token}"},
    )

    # Assert
    assert response.status_code == 204, f"Expected 204, got {response.status_code}"


@pytest.mark.asyncio
async def test_logout_revoke_all_tokens(
    client: TestClient,
    therapist_token: str,
):
    """
    Test logout from all devices (Happy Path)

    Scenario: User logs out from all devices
    Expected: 204 No Content, all tokens revoked
    """
    # Arrange
    logout_data = {"revoke_all_tokens": True}

    # Act
    response = client.post(
        "/api/v1/auth/logout",
        json=logout_data,
        headers={"Authorization": f"Bearer {therapist_token}"},
    )

    # Assert
    assert response.status_code == 204, f"Expected 204, got {response.status_code}"


@pytest.mark.asyncio
async def test_logout_without_auth(
    client: TestClient,
):
    """
    Test logout without authentication (Error Case - 401)

    Scenario: Logout request without Authorization header
    Expected: 401 Unauthorized
    """
    # Arrange
    logout_data = {"revoke_all_tokens": False}

    # Act
    response = client.post("/api/v1/auth/logout", json=logout_data)

    # Assert
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"


@pytest.mark.asyncio
async def test_access_after_logout(
    client: TestClient,
    therapist_user: UserModel,
):
    """
    Test accessing protected endpoint after logout (Error Case - 401)

    Scenario: Use token after logout
    Expected: 401 Unauthorized (token blacklisted)
    """
    # Arrange - Login first
    login_response = client.post(
        "/api/v1/auth/therapist/login",
        json={"email": therapist_user.email, "password": "SecurePass123!"},
    )
    token = login_response.json()["access_token"]

    # Logout
    client.post(
        "/api/v1/auth/logout",
        json={"revoke_all_tokens": False},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Act - Try to access protected endpoint
    response = client.get("/api/v1/patients", headers={"Authorization": f"Bearer {token}"})

    # Assert
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"


# ============================================================================
# POST /api/v1/auth/refresh - Token Refresh
# ============================================================================


@pytest.mark.asyncio
async def test_refresh_token_success(
    client: TestClient,
    therapist_user: UserModel,
):
    """
    Test refreshing access token (Happy Path)

    Scenario: User refreshes expired access token
    Expected: 200 OK, new access token returned
    """
    # Arrange - Login to get refresh token
    login_response = client.post(
        "/api/v1/auth/therapist/login",
        json={"email": therapist_user.email, "password": "SecurePass123!"},
    )
    refresh_token = login_response.json()["refresh_token"]

    # Act
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})

    # Assert
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_with_invalid_token(
    client: TestClient,
):
    """
    Test refreshing with invalid token (Error Case - 401)

    Scenario: Use fake refresh token
    Expected: 401 Unauthorized
    """
    # Arrange
    fake_refresh_token = "fake.refresh.token"

    # Act
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": fake_refresh_token})

    # Assert
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"


@pytest.mark.asyncio
async def test_refresh_with_access_token(
    client: TestClient,
    therapist_token: str,
):
    """
    Test refreshing with access token instead of refresh token (Error Case - 401)

    Scenario: Use wrong token type
    Expected: 401 Unauthorized (wrong token type)
    """
    # Act
    response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": therapist_token}  # Wrong token type
    )

    # Assert
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"


# ============================================================================
# Edge Cases & Security Tests
# ============================================================================


@pytest.mark.asyncio
async def test_login_with_expired_token(
    client: TestClient,
):
    """
    Test accessing API with expired token (Error Case - 401)

    Scenario: Token has expired
    Expected: 401 Unauthorized
    """
    # Arrange - Create expired token
    from datetime import timedelta

    from respira_ally.core.security.jwt import create_access_token

    expired_token = create_access_token(
        {"sub": "test_user", "role": "THERAPIST"},
        expires_delta=timedelta(seconds=-1),  # Already expired
    )

    # Act
    response = client.get("/api/v1/patients", headers={"Authorization": f"Bearer {expired_token}"})

    # Assert
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"


@pytest.mark.asyncio
async def test_malformed_authorization_header(
    client: TestClient,
):
    """
    Test malformed Authorization header (Error Case - 401)

    Scenario: Wrong header format
    Expected: 401 Unauthorized
    """
    # Act - Missing "Bearer" prefix
    response = client.get("/api/v1/patients", headers={"Authorization": "InvalidTokenFormat"})

    # Assert
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
