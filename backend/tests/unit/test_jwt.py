"""
Unit Tests for JWT Token Management
Tests JWT token creation, verification, and utilities
"""

import time
from datetime import timedelta
from uuid import uuid4

import pytest
from jose import jwt

from respira_ally.core.exceptions.application_exceptions import UnauthorizedError
from respira_ally.core.schemas import UserRole
from respira_ally.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_token_expiration,
    is_token_expired,
    verify_token,
)


class TestJWTCreation:
    """Test JWT token creation functions"""

    def test_create_access_token_success(self):
        """Test creating a valid access token"""
        user_id = str(uuid4())
        data = {"sub": user_id, "role": UserRole.PATIENT.value}

        token = create_access_token(data)

        # Verify token is a string
        assert isinstance(token, str)
        assert len(token) > 0

        # Decode without verification to check payload
        payload = decode_token(token)
        assert payload["sub"] == user_id
        assert payload["role"] == UserRole.PATIENT.value
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_create_access_token_with_custom_expiration(self):
        """Test creating access token with custom expiration"""
        user_id = str(uuid4())
        data = {"sub": user_id, "role": UserRole.THERAPIST.value}
        custom_expires = timedelta(minutes=30)

        token = create_access_token(data, expires_delta=custom_expires)

        payload = decode_token(token)
        # Expiration should be approximately 30 minutes from now
        exp_time = get_token_expiration(token)
        assert exp_time is not None

    def test_create_refresh_token_success(self):
        """Test creating a valid refresh token"""
        user_id = str(uuid4())
        data = {"sub": user_id, "role": UserRole.PATIENT.value}

        token = create_refresh_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

        # Verify token type
        payload = decode_token(token)
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
        assert "exp" in payload

    def test_create_token_with_additional_claims(self):
        """Test creating token with additional custom claims"""
        user_id = str(uuid4())
        data = {
            "sub": user_id,
            "role": UserRole.THERAPIST.value,
            "email": "therapist@example.com",
            "department": "Pulmonology",
        }

        token = create_access_token(data)
        payload = decode_token(token)

        assert payload["sub"] == user_id
        assert payload["role"] == UserRole.THERAPIST.value
        assert payload["email"] == "therapist@example.com"
        assert payload["department"] == "Pulmonology"


class TestJWTVerification:
    """Test JWT token verification functions"""

    def test_verify_valid_access_token(self):
        """Test verifying a valid access token"""
        user_id = str(uuid4())
        data = {"sub": user_id, "role": UserRole.PATIENT.value}

        token = create_access_token(data)
        payload = verify_token(token, expected_type="access")

        assert payload["sub"] == user_id
        assert payload["role"] == UserRole.PATIENT.value
        assert payload["type"] == "access"

    def test_verify_valid_refresh_token(self):
        """Test verifying a valid refresh token"""
        user_id = str(uuid4())
        data = {"sub": user_id, "role": UserRole.THERAPIST.value}

        token = create_refresh_token(data)
        payload = verify_token(token, expected_type="refresh")

        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"

    def test_verify_token_wrong_type_fails(self):
        """Test that verifying token with wrong type raises error"""
        user_id = str(uuid4())
        data = {"sub": user_id, "role": UserRole.PATIENT.value}

        access_token = create_access_token(data)

        # Try to verify access token as refresh token
        with pytest.raises(UnauthorizedError) as exc_info:
            verify_token(access_token, expected_type="refresh")

        assert "Invalid token type" in str(exc_info.value)

    def test_verify_expired_token_fails(self):
        """Test that expired token raises UnauthorizedError"""
        user_id = str(uuid4())
        data = {"sub": user_id, "role": UserRole.PATIENT.value}

        # Create token with very short expiration (1 second)
        token = create_access_token(data, expires_delta=timedelta(seconds=1))

        # Wait for token to expire
        time.sleep(2)

        with pytest.raises(UnauthorizedError) as exc_info:
            verify_token(token)

        assert "expired" in str(exc_info.value).lower()

    def test_verify_invalid_signature_fails(self):
        """Test that token with invalid signature raises error"""
        user_id = str(uuid4())
        data = {"sub": user_id, "role": UserRole.PATIENT.value, "type": "access"}

        # Create token with wrong secret key
        invalid_token = jwt.encode(data, "wrong-secret-key", algorithm="HS256")

        with pytest.raises(UnauthorizedError) as exc_info:
            verify_token(invalid_token)

        assert "Invalid token" in str(exc_info.value)

    def test_verify_malformed_token_fails(self):
        """Test that malformed token raises error"""
        malformed_token = "this.is.not.a.valid.jwt"

        with pytest.raises(UnauthorizedError) as exc_info:
            verify_token(malformed_token)

        assert "Invalid token" in str(exc_info.value)


class TestJWTDecoding:
    """Test JWT token decoding functions"""

    def test_decode_valid_token(self):
        """Test decoding a valid token without verification"""
        user_id = str(uuid4())
        data = {"sub": user_id, "role": UserRole.PATIENT.value}

        token = create_access_token(data)
        payload = decode_token(token)

        assert payload["sub"] == user_id
        assert payload["role"] == UserRole.PATIENT.value

    def test_decode_expired_token_succeeds(self):
        """Test that decode_token can decode expired tokens (no verification)"""
        user_id = str(uuid4())
        data = {"sub": user_id, "role": UserRole.PATIENT.value}

        # Create expired token
        token = create_access_token(data, expires_delta=timedelta(seconds=1))
        time.sleep(2)

        # decode_token should still work (no verification)
        payload = decode_token(token)
        assert payload["sub"] == user_id

    def test_decode_malformed_token_fails(self):
        """Test that decoding malformed token raises error"""
        malformed_token = "not.a.jwt"

        with pytest.raises(UnauthorizedError) as exc_info:
            decode_token(malformed_token)

        assert "Invalid token format" in str(exc_info.value)


class TestJWTUtilities:
    """Test JWT utility functions"""

    def test_get_token_expiration(self):
        """Test getting token expiration datetime"""
        user_id = str(uuid4())
        data = {"sub": user_id, "role": UserRole.PATIENT.value}

        token = create_access_token(data)
        exp_time = get_token_expiration(token)

        assert exp_time is not None
        assert exp_time.tzinfo is not None  # Should have timezone

    def test_get_token_expiration_invalid_token_returns_none(self):
        """Test that invalid token returns None for expiration"""
        invalid_token = "invalid.jwt.token"

        exp_time = get_token_expiration(invalid_token)
        assert exp_time is None

    def test_is_token_expired_false_for_valid_token(self):
        """Test that valid token is not marked as expired"""
        user_id = str(uuid4())
        data = {"sub": user_id, "role": UserRole.PATIENT.value}

        token = create_access_token(data)
        assert is_token_expired(token) is False

    def test_is_token_expired_true_for_expired_token(self):
        """Test that expired token is marked as expired"""
        user_id = str(uuid4())
        data = {"sub": user_id, "role": UserRole.PATIENT.value}

        # Create token with very short expiration
        token = create_access_token(data, expires_delta=timedelta(seconds=1))

        # Wait for expiration
        time.sleep(2)

        assert is_token_expired(token) is True

    def test_is_token_expired_true_for_invalid_token(self):
        """Test that invalid token is marked as expired"""
        invalid_token = "invalid.jwt.token"
        assert is_token_expired(invalid_token) is True


class TestJWTSecurity:
    """Test JWT security features"""

    def test_token_algorithm_is_hs256(self):
        """Test that tokens use HS256 algorithm"""
        user_id = str(uuid4())
        data = {"sub": user_id, "role": UserRole.PATIENT.value}

        token = create_access_token(data)

        # Decode header to check algorithm
        unverified = jwt.get_unverified_header(token)
        assert unverified["alg"] == "HS256"

    def test_token_contains_iat_claim(self):
        """Test that tokens contain 'issued at' (iat) claim"""
        user_id = str(uuid4())
        data = {"sub": user_id, "role": UserRole.PATIENT.value}

        token = create_access_token(data)
        payload = decode_token(token)

        assert "iat" in payload
        assert isinstance(payload["iat"], int)

    def test_different_users_get_different_tokens(self):
        """Test that different users get different tokens"""
        user1_id = str(uuid4())
        user2_id = str(uuid4())

        data1 = {"sub": user1_id, "role": UserRole.PATIENT.value}
        data2 = {"sub": user2_id, "role": UserRole.PATIENT.value}

        token1 = create_access_token(data1)
        token2 = create_access_token(data2)

        assert token1 != token2

        payload1 = verify_token(token1)
        payload2 = verify_token(token2)

        assert payload1["sub"] == user1_id
        assert payload2["sub"] == user2_id
