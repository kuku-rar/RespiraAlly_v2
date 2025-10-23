"""
Login Lockout Service Unit Tests
Tests the Redis-based login lockout mechanism

Run with: pytest tests/unit/infrastructure/cache/test_login_lockout_service.py -v
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from respira_ally.infrastructure.cache.login_lockout_service import (
    LockoutPolicy,
    LoginLockoutService,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    mock = AsyncMock()
    return mock


@pytest.fixture
def lockout_service(mock_redis):
    """Create LoginLockoutService with mocked Redis"""
    return LoginLockoutService(redis_client=mock_redis)


@pytest.fixture
def custom_lockout_service(mock_redis):
    """Create LoginLockoutService with custom policies"""
    custom_policies = [
        LockoutPolicy(max_attempts=3, lockout_duration_minutes=5),
        LockoutPolicy(max_attempts=6, lockout_duration_minutes=10),
    ]
    return LoginLockoutService(redis_client=mock_redis, lockout_policies=custom_policies)


# ============================================================================
# Tests: is_locked_out
# ============================================================================


@pytest.mark.asyncio
async def test_is_locked_out_not_locked(lockout_service, mock_redis):
    """Test is_locked_out returns False when no lockout exists"""
    # Arrange
    mock_redis.get.return_value = None

    # Act
    is_locked, remaining = await lockout_service.is_locked_out("test@example.com")

    # Assert
    assert is_locked is False
    assert remaining is None
    mock_redis.get.assert_called_once_with("login:locked:test@example.com")


@pytest.mark.asyncio
async def test_is_locked_out_active_lockout(lockout_service, mock_redis):
    """Test is_locked_out returns True with remaining time for active lockout"""
    # Arrange
    future_time = datetime.now(UTC) + timedelta(minutes=10)
    future_timestamp = str(int(future_time.timestamp()))
    mock_redis.get.return_value = future_timestamp

    # Act
    is_locked, remaining = await lockout_service.is_locked_out("test@example.com")

    # Assert
    assert is_locked is True
    assert remaining is not None
    assert 0 < remaining <= 600  # Should be around 10 minutes (600 seconds)


@pytest.mark.asyncio
async def test_is_locked_out_expired_lockout(lockout_service, mock_redis):
    """Test is_locked_out cleans up expired lockout"""
    # Arrange
    past_time = datetime.now(UTC) - timedelta(minutes=5)
    past_timestamp = str(int(past_time.timestamp()))
    mock_redis.get.return_value = past_timestamp

    # Act
    is_locked, remaining = await lockout_service.is_locked_out("test@example.com")

    # Assert
    assert is_locked is False
    assert remaining is None
    mock_redis.delete.assert_called_once_with("login:locked:test@example.com")


# ============================================================================
# Tests: record_failed_attempt
# ============================================================================


@pytest.mark.asyncio
async def test_record_failed_attempt_first_failure(lockout_service, mock_redis):
    """Test recording first failed attempt sets TTL"""
    # Arrange
    mock_redis.incr.return_value = 1

    # Act
    is_locked, fail_count = await lockout_service.record_failed_attempt("test@example.com")

    # Assert
    assert is_locked is False
    assert fail_count == 1
    mock_redis.incr.assert_called_once_with("login:fail:test@example.com")
    mock_redis.expire.assert_called_once_with("login:fail:test@example.com", 3600)


@pytest.mark.asyncio
async def test_record_failed_attempt_triggers_lockout(lockout_service, mock_redis):
    """Test that 5th failed attempt triggers lockout"""
    # Arrange
    mock_redis.incr.return_value = 5

    # Act
    is_locked, fail_count = await lockout_service.record_failed_attempt("test@example.com")

    # Assert
    assert is_locked is True
    assert fail_count == 5
    mock_redis.setex.assert_called_once()

    # Verify lockout key and TTL
    call_args = mock_redis.setex.call_args
    assert call_args[0][0] == "login:locked:test@example.com"
    assert call_args[0][1] == 15 * 60  # 15 minutes in seconds


@pytest.mark.asyncio
async def test_record_failed_attempt_progressive_lockout(lockout_service, mock_redis):
    """Test progressive lockout (10th failure = 1 hour lockout)"""
    # Arrange
    mock_redis.incr.return_value = 10

    # Act
    is_locked, fail_count = await lockout_service.record_failed_attempt("test@example.com")

    # Assert
    assert is_locked is True
    assert fail_count == 10

    # Verify longer lockout duration
    call_args = mock_redis.setex.call_args
    assert call_args[0][1] == 60 * 60  # 1 hour in seconds


@pytest.mark.asyncio
async def test_record_failed_attempt_custom_policy(custom_lockout_service, mock_redis):
    """Test custom lockout policy"""
    # Arrange
    mock_redis.incr.return_value = 3

    # Act
    is_locked, fail_count = await custom_lockout_service.record_failed_attempt("test@example.com")

    # Assert
    assert is_locked is True
    assert fail_count == 3

    # Verify custom lockout duration (5 minutes)
    call_args = mock_redis.setex.call_args
    assert call_args[0][1] == 5 * 60


# ============================================================================
# Tests: clear_failed_attempts
# ============================================================================


@pytest.mark.asyncio
async def test_clear_failed_attempts_success(lockout_service, mock_redis):
    """Test successfully clearing failed attempts"""
    # Act
    result = await lockout_service.clear_failed_attempts("test@example.com")

    # Assert
    assert result is True
    assert mock_redis.delete.call_count == 2
    mock_redis.delete.assert_any_call("login:fail:test@example.com")
    mock_redis.delete.assert_any_call("login:locked:test@example.com")


# ============================================================================
# Tests: get_failed_attempt_count
# ============================================================================


@pytest.mark.asyncio
async def test_get_failed_attempt_count_zero(lockout_service, mock_redis):
    """Test getting count when no failures"""
    # Arrange
    mock_redis.get.return_value = None

    # Act
    count = await lockout_service.get_failed_attempt_count("test@example.com")

    # Assert
    assert count == 0


@pytest.mark.asyncio
async def test_get_failed_attempt_count_nonzero(lockout_service, mock_redis):
    """Test getting existing failure count"""
    # Arrange
    mock_redis.get.return_value = "3"

    # Act
    count = await lockout_service.get_failed_attempt_count("test@example.com")

    # Assert
    assert count == 3


# ============================================================================
# Tests: unlock_account
# ============================================================================


@pytest.mark.asyncio
async def test_unlock_account(lockout_service, mock_redis):
    """Test admin unlock function"""
    # Act
    result = await lockout_service.unlock_account("test@example.com")

    # Assert
    assert result is True
    assert mock_redis.delete.call_count == 2


# ============================================================================
# Tests: get_lockout_info
# ============================================================================


def test_get_lockout_info_no_lockout(lockout_service):
    """Test lockout info when no lockout triggered"""
    # Act
    info = lockout_service.get_lockout_info(3)

    # Assert
    assert info["current_fails"] == 3
    assert info["next_lockout_at"] == 5  # Next lockout at 5 failures
    assert info["next_lockout_duration"] == 15  # 15 minutes
    assert info["is_locked"] is False


def test_get_lockout_info_locked(lockout_service):
    """Test lockout info when account is locked"""
    # Act
    info = lockout_service.get_lockout_info(5)

    # Assert
    assert info["current_fails"] == 5
    assert info["next_lockout_at"] == 10  # Next escalation at 10 failures
    assert info["next_lockout_duration"] == 60  # 60 minutes
    assert info["is_locked"] is True


def test_get_lockout_info_max_lockout(lockout_service):
    """Test lockout info at maximum lockout level"""
    # Act
    info = lockout_service.get_lockout_info(25)

    # Assert
    assert info["current_fails"] == 25
    assert info["next_lockout_at"] is None  # No higher level
    assert info["next_lockout_duration"] is None
    assert info["is_locked"] is True


# ============================================================================
# Tests: Error Handling
# ============================================================================


@pytest.mark.asyncio
async def test_is_locked_out_redis_error(lockout_service, mock_redis):
    """Test is_locked_out handles Redis errors gracefully"""
    # Arrange
    mock_redis.get.side_effect = Exception("Redis connection error")

    # Act
    is_locked, remaining = await lockout_service.is_locked_out("test@example.com")

    # Assert - Should fail open (not locked) on error
    assert is_locked is False
    assert remaining is None


@pytest.mark.asyncio
async def test_record_failed_attempt_redis_error(lockout_service, mock_redis):
    """Test record_failed_attempt handles Redis errors"""
    # Arrange
    mock_redis.incr.side_effect = Exception("Redis connection error")

    # Act
    is_locked, fail_count = await lockout_service.record_failed_attempt("test@example.com")

    # Assert - Should fail open on error
    assert is_locked is False
    assert fail_count == 0


@pytest.mark.asyncio
async def test_clear_failed_attempts_redis_error(lockout_service, mock_redis):
    """Test clear_failed_attempts handles Redis errors"""
    # Arrange
    mock_redis.delete.side_effect = Exception("Redis connection error")

    # Act
    result = await lockout_service.clear_failed_attempts("test@example.com")

    # Assert
    assert result is False
