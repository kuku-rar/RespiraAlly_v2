"""
Redis Client Management
Provides Redis connection pool and async client
"""

from collections.abc import AsyncGenerator

import redis.asyncio as redis
from redis.asyncio import Redis

from respira_ally.core.config import settings


class RedisClient:
    """
    Redis Client Manager with connection pooling

    Features:
    - Async Redis client using redis-py
    - Connection pooling for performance
    - Auto-reconnection on connection loss
    - Support for both standalone and cluster modes
    """

    _pool: redis.ConnectionPool | None = None
    _client: Redis | None = None

    @classmethod
    async def get_pool(cls) -> redis.ConnectionPool:
        """Get or create Redis connection pool"""
        if cls._pool is None:
            cls._pool = redis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                decode_responses=True,
                max_connections=20,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30,
            )
        return cls._pool

    @classmethod
    async def get_client(cls) -> Redis:
        """Get or create Redis client"""
        if cls._client is None:
            pool = await cls.get_pool()
            cls._client = redis.Redis(connection_pool=pool)
        return cls._client

    @classmethod
    async def close(cls) -> None:
        """Close Redis connection pool"""
        if cls._client:
            await cls._client.close()
            cls._client = None

        if cls._pool:
            await cls._pool.disconnect()
            cls._pool = None

    @classmethod
    async def ping(cls) -> bool:
        """
        Health check: Ping Redis server

        Returns:
            True if Redis is reachable, False otherwise
        """
        try:
            client = await cls.get_client()
            return await client.ping()
        except Exception:
            return False


async def get_redis() -> AsyncGenerator[Redis, None]:
    """
    FastAPI dependency for Redis client

    Usage:
        @router.get("/")
        async def endpoint(redis: Redis = Depends(get_redis)):
            await redis.set("key", "value")

    Yields:
        Redis client instance
    """
    client = await RedisClient.get_client()
    try:
        yield client
    finally:
        # Connection is managed by the pool, no need to close here
        pass


# Singleton instance for direct access
redis_client = RedisClient()
