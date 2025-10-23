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
