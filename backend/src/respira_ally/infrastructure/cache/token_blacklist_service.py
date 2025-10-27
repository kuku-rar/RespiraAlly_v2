"""
Token Blacklist Service
Manages JWT token revocation using Redis
"""

from datetime import UTC, datetime

from redis.asyncio import Redis

from respira_ally.core.security.jwt import decode_token, get_token_expiration
from respira_ally.infrastructure.cache.redis_client import RedisClient


class TokenBlacklistService:
    """
    Token Blacklist Service using Redis

    Features:
    - Add tokens to blacklist with automatic expiration
    - Check if token is blacklisted
    - Revoke all tokens for a specific user
    - Automatic cleanup via Redis TTL

    Redis Key Format:
    - blacklist:token:{token_jti} - Individual token blacklist
    - blacklist:user:{user_id}:revoke_before - User-level revocation timestamp
    """

    def __init__(self, redis_client: Redis | None = None):
        """
        Initialize Token Blacklist Service

        Args:
            redis_client: Optional Redis client (uses singleton if not provided)
        """
        self.redis = redis_client

    async def _get_redis(self) -> Redis:
        """Get Redis client instance"""
        if self.redis is None:
            return await RedisClient.get_client()
        return self.redis

    def _get_token_blacklist_key(self, token_jti: str) -> str:
        """Generate Redis key for token blacklist"""
        return f"blacklist:token:{token_jti}"

    def _get_user_revoke_key(self, user_id: str) -> str:
        """Generate Redis key for user-level token revocation"""
        return f"blacklist:user:{user_id}:revoke_before"

    async def add_to_blacklist(self, token: str, token_jti: str | None = None) -> bool:
        """
        Add a token to the blacklist

        Args:
            token: JWT token string
            token_jti: Optional JWT ID (will be extracted from token if not provided)

        Returns:
            True if successfully blacklisted, False otherwise

        Note:
            Token is automatically removed from blacklist after expiration
        """
        try:
            # Extract token expiration for TTL
            exp_time = get_token_expiration(token)
            if exp_time is None:
                # Token has no expiration, use default 30 days
                ttl = 30 * 24 * 60 * 60
            else:
                # Calculate remaining time until expiration
                now = datetime.now(UTC)
                ttl = int((exp_time - now).total_seconds())

                # If token is already expired, don't blacklist (no need)
                if ttl <= 0:
                    return False

            # Extract JTI from token if not provided
            if token_jti is None:
                payload = decode_token(token)
                token_jti = payload.get("jti", token[:32])  # Use token prefix if no JTI

            # Add to Redis with TTL
            redis = await self._get_redis()
            key = self._get_token_blacklist_key(token_jti)
            await redis.setex(key, ttl, "1")

            return True

        except Exception:
            # Log error in production
            return False

    async def is_blacklisted(self, token: str, user_id: str | None = None) -> bool:
        """
        Check if a token is blacklisted

        Checks both:
        1. Individual token blacklist (via JTI)
        2. User-level revocation (all tokens issued before a certain time)

        Args:
            token: JWT token string
            user_id: Optional user ID for user-level revocation check

        Returns:
            True if token is blacklisted, False otherwise
        """
        try:
            payload = decode_token(token)
            redis = await self._get_redis()

            # Check 1: Individual token blacklist
            token_jti = payload.get("jti")
            if token_jti:
                key = self._get_token_blacklist_key(token_jti)
                is_blacklisted = await redis.exists(key)
                if is_blacklisted:
                    return True

            # Check 2: User-level revocation
            if user_id:
                user_revoke_key = self._get_user_revoke_key(user_id)
                revoke_before_ts = await redis.get(user_revoke_key)

                if revoke_before_ts:
                    # Token issued time (iat)
                    token_iat = payload.get("iat")
                    if token_iat and int(revoke_before_ts) > token_iat:
                        return True

            return False

        except Exception:
            # On error, assume token is blacklisted (fail-safe)
            return True

    async def revoke_all_user_tokens(
        self, user_id: str, issued_before: datetime | None = None
    ) -> bool:
        """
        Revoke all tokens for a specific user

        This is useful for "logout from all devices" functionality.
        Tokens issued before the specified timestamp will be considered revoked.

        Args:
            user_id: User ID whose tokens should be revoked
            issued_before: Optional timestamp (defaults to now)

        Returns:
            True if successful, False otherwise
        """
        try:
            if issued_before is None:
                issued_before = datetime.now(UTC)

            # Store revocation timestamp (Unix epoch)
            revoke_timestamp = int(issued_before.timestamp())

            redis = await self._get_redis()
            key = self._get_user_revoke_key(user_id)

            # Store with 30-day TTL (max refresh token lifetime)
            await redis.setex(key, 30 * 24 * 60 * 60, str(revoke_timestamp))

            return True

        except Exception:
            return False

    async def remove_from_blacklist(self, token_jti: str) -> bool:
        """
        Remove a token from the blacklist

        This is rarely needed, but useful for admin actions or testing.

        Args:
            token_jti: JWT ID of the token to remove

        Returns:
            True if removed, False otherwise
        """
        try:
            redis = await self._get_redis()
            key = self._get_token_blacklist_key(token_jti)
            await redis.delete(key)
            return True

        except Exception:
            return False

    async def clear_user_revocation(self, user_id: str) -> bool:
        """
        Clear user-level token revocation

        This re-enables all previously revoked tokens for the user.
        Use with caution!

        Args:
            user_id: User ID whose revocation should be cleared

        Returns:
            True if cleared, False otherwise
        """
        try:
            redis = await self._get_redis()
            key = self._get_user_revoke_key(user_id)
            await redis.delete(key)
            return True

        except Exception:
            return False


# Singleton instance
token_blacklist_service = TokenBlacklistService()
