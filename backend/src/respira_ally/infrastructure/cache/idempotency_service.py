"""
Idempotency Service
Prevents duplicate API requests using Idempotency-Key header
"""
import json
from typing import Any
from datetime import timedelta

from redis.asyncio import Redis


class IdempotencyService:
    """
    Idempotency Service using Redis

    Features:
    - Store request responses by idempotency key
    - 24-hour TTL to prevent infinite growth
    - JSON serialization for complex responses

    Usage:
        service = IdempotencyService(redis)
        response = await service.get_cached_response("key-123")
        if response:
            return response  # Return cached
        else:
            result = await process_request()
            await service.cache_response("key-123", result)
    """

    def __init__(self, redis: Redis):
        self.redis = redis
        self.key_prefix = "idempotency:"
        self.ttl = timedelta(hours=24)

    def _make_key(self, idempotency_key: str, user_id: str | None = None) -> str:
        """Generate Redis key for idempotency key (user-scoped for security)"""
        if user_id:
            return f"{self.key_prefix}{user_id}:{idempotency_key}"
        return f"{self.key_prefix}{idempotency_key}"

    async def get_cached_response(
        self, idempotency_key: str, user_id: str | None = None
    ) -> dict[str, Any] | None:
        """
        Get cached response for idempotency key

        Args:
            idempotency_key: Client-provided idempotency key
            user_id: Optional user ID for user-scoped caching (security best practice)

        Returns:
            Cached response dict or None if not found
        """
        redis_key = self._make_key(idempotency_key, user_id)
        cached = await self.redis.get(redis_key)

        if cached is None:
            return None

        try:
            return json.loads(cached)
        except json.JSONDecodeError:
            # Invalid cached data, delete it
            await self.redis.delete(redis_key)
            return None

    async def cache_response(
        self, idempotency_key: str, response: dict[str, Any], user_id: str | None = None
    ) -> None:
        """
        Cache response for idempotency key

        Args:
            idempotency_key: Client-provided idempotency key
            response: Response data to cache (must be JSON-serializable)
            user_id: Optional user ID for user-scoped caching (security best practice)
        """
        redis_key = self._make_key(idempotency_key, user_id)
        response_json = json.dumps(response)

        await self.redis.setex(
            redis_key,
            self.ttl,
            response_json,
        )

    async def delete_cached_response(
        self, idempotency_key: str, user_id: str | None = None
    ) -> bool:
        """
        Delete cached response (for testing/cleanup)

        Args:
            idempotency_key: Client-provided idempotency key
            user_id: Optional user ID for user-scoped caching

        Returns:
            True if key was deleted, False if key didn't exist
        """
        redis_key = self._make_key(idempotency_key, user_id)
        result = await self.redis.delete(redis_key)
        return result > 0

    async def key_exists(self, idempotency_key: str, user_id: str | None = None) -> bool:
        """
        Check if idempotency key exists in cache

        Args:
            idempotency_key: Client-provided idempotency key
            user_id: Optional user ID for user-scoped caching

        Returns:
            True if key exists, False otherwise
        """
        redis_key = self._make_key(idempotency_key, user_id)
        return await self.redis.exists(redis_key) > 0
