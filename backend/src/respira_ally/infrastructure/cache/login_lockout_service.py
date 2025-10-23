"""
Login Lockout Service
Prevents brute-force attacks using Redis-based rate limiting

Strategy:
- Track failed login attempts per email/identifier
- Progressive lockout: more failures = longer lockout period
- Automatic cleanup via Redis TTL
- Clear counters on successful login
"""

from datetime import UTC, datetime, timedelta
from typing import NamedTuple

from redis.asyncio import Redis

from respira_ally.infrastructure.cache.redis_client import RedisClient


class LockoutPolicy(NamedTuple):
    """
    Lockout policy configuration

    Attributes:
        max_attempts: Maximum allowed failed attempts before lockout
        lockout_duration_minutes: Duration of lockout in minutes
    """

    max_attempts: int
    lockout_duration_minutes: int


# Default lockout policies (progressive)
DEFAULT_LOCKOUT_POLICIES = [
    LockoutPolicy(max_attempts=5, lockout_duration_minutes=15),  # 5 failures → 15 min
    LockoutPolicy(max_attempts=10, lockout_duration_minutes=60),  # 10 failures → 1 hour
    LockoutPolicy(max_attempts=20, lockout_duration_minutes=240),  # 20 failures → 4 hours
]


class LoginLockoutService:
    """
    Login Lockout Service using Redis

    Features:
    - Track failed login attempts with automatic expiration
    - Progressive lockout: longer lockout for repeated failures
    - Check if identifier (email) is currently locked out
    - Clear failed attempts on successful login
    - Admin override to unlock accounts

    Redis Key Format:
    - login:fail:{identifier} - Failed attempt counter with TTL
    - login:locked:{identifier} - Lockout expiration timestamp
    """

    def __init__(
        self,
        redis_client: Redis | None = None,
        lockout_policies: list[LockoutPolicy] | None = None,
    ):
        """
        Initialize Login Lockout Service

        Args:
            redis_client: Optional Redis client (uses singleton if not provided)
            lockout_policies: Optional custom lockout policies (uses defaults if not provided)
        """
        self.redis = redis_client
        self.lockout_policies = lockout_policies or DEFAULT_LOCKOUT_POLICIES

    async def _get_redis(self) -> Redis:
        """Get Redis client instance"""
        if self.redis is None:
            return await RedisClient.get_client()
        return self.redis

    def _get_fail_count_key(self, identifier: str) -> str:
        """Generate Redis key for failed attempt counter"""
        return f"login:fail:{identifier}"

    def _get_locked_key(self, identifier: str) -> str:
        """Generate Redis key for lockout status"""
        return f"login:locked:{identifier}"

    def _determine_lockout_duration(self, fail_count: int) -> int | None:
        """
        Determine lockout duration based on fail count

        Args:
            fail_count: Number of failed attempts

        Returns:
            Lockout duration in minutes, or None if no lockout needed
        """
        # Find the appropriate policy (highest threshold not exceeded)
        applicable_policy = None
        for policy in sorted(self.lockout_policies, key=lambda p: p.max_attempts):
            if fail_count >= policy.max_attempts:
                applicable_policy = policy

        return applicable_policy.lockout_duration_minutes if applicable_policy else None

    async def is_locked_out(self, identifier: str) -> tuple[bool, int | None]:
        """
        Check if identifier is currently locked out

        Args:
            identifier: Email or user identifier to check

        Returns:
            Tuple of (is_locked, remaining_seconds)
            - is_locked: True if currently locked out
            - remaining_seconds: Seconds until lockout expires (None if not locked)
        """
        try:
            redis = await self._get_redis()
            locked_key = self._get_locked_key(identifier)

            # Get lockout expiration timestamp
            locked_until_ts = await redis.get(locked_key)
            if not locked_until_ts:
                return False, None

            # Check if lockout has expired
            locked_until = datetime.fromtimestamp(int(locked_until_ts), tz=UTC)
            now = datetime.now(UTC)

            if now >= locked_until:
                # Lockout expired, clean up
                await redis.delete(locked_key)
                return False, None

            # Still locked
            remaining_seconds = int((locked_until - now).total_seconds())
            return True, remaining_seconds

        except Exception:
            # On error, assume not locked (fail-open for availability)
            return False, None

    async def record_failed_attempt(self, identifier: str) -> tuple[bool, int]:
        """
        Record a failed login attempt

        Args:
            identifier: Email or user identifier

        Returns:
            Tuple of (is_now_locked, fail_count)
            - is_now_locked: True if this failure triggered a lockout
            - fail_count: Total number of failed attempts
        """
        try:
            redis = await self._get_redis()
            fail_count_key = self._get_fail_count_key(identifier)

            # Increment failure counter
            fail_count = await redis.incr(fail_count_key)

            # Set TTL on first failure (counter expires after 1 hour of no activity)
            if fail_count == 1:
                await redis.expire(fail_count_key, 3600)  # 1 hour

            # Check if lockout should be triggered
            lockout_duration_minutes = self._determine_lockout_duration(fail_count)

            if lockout_duration_minutes:
                # Trigger lockout
                locked_key = self._get_locked_key(identifier)
                locked_until = datetime.now(UTC) + timedelta(minutes=lockout_duration_minutes)
                locked_until_ts = int(locked_until.timestamp())

                # Store lockout expiration with TTL
                lockout_ttl = lockout_duration_minutes * 60
                await redis.setex(locked_key, lockout_ttl, str(locked_until_ts))

                return True, fail_count

            return False, fail_count

        except Exception:
            # On error, don't lock out (fail-open)
            return False, 0

    async def clear_failed_attempts(self, identifier: str) -> bool:
        """
        Clear failed attempt counter (called on successful login)

        Args:
            identifier: Email or user identifier

        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            redis = await self._get_redis()
            fail_count_key = self._get_fail_count_key(identifier)
            locked_key = self._get_locked_key(identifier)

            # Delete both counter and lockout status
            await redis.delete(fail_count_key)
            await redis.delete(locked_key)

            return True

        except Exception:
            return False

    async def get_failed_attempt_count(self, identifier: str) -> int:
        """
        Get current failed attempt count for identifier

        Args:
            identifier: Email or user identifier

        Returns:
            Number of failed attempts
        """
        try:
            redis = await self._get_redis()
            fail_count_key = self._get_fail_count_key(identifier)

            count = await redis.get(fail_count_key)
            return int(count) if count else 0

        except Exception:
            return 0

    async def unlock_account(self, identifier: str) -> bool:
        """
        Admin function: Manually unlock an account

        This removes both the lockout status and failed attempt counter.

        Args:
            identifier: Email or user identifier to unlock

        Returns:
            True if unlocked successfully, False otherwise
        """
        return await self.clear_failed_attempts(identifier)

    def get_lockout_info(self, fail_count: int) -> dict:
        """
        Get lockout policy information for a given fail count

        Args:
            fail_count: Number of failed attempts

        Returns:
            Dictionary with lockout information:
            - current_fails: Current fail count
            - next_lockout_at: Failures needed to trigger next lockout
            - next_lockout_duration: Duration of next lockout in minutes
            - is_locked: Whether currently locked (based on fail count)
        """
        # Find next applicable policy
        next_policy = None
        current_locked = False

        for policy in sorted(self.lockout_policies, key=lambda p: p.max_attempts):
            if fail_count >= policy.max_attempts:
                current_locked = True
            elif not next_policy:
                next_policy = policy

        return {
            "current_fails": fail_count,
            "next_lockout_at": next_policy.max_attempts if next_policy else None,
            "next_lockout_duration": (
                next_policy.lockout_duration_minutes if next_policy else None
            ),
            "is_locked": current_locked,
        }


# Singleton instance
login_lockout_service = LoginLockoutService()
