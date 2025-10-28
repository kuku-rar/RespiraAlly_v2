"""
Database Session Management
SQLAlchemy 2.0+ with async support
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from respira_ally.core.config import settings


# SQLAlchemy Base Model
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""

    pass


# ============================================================================
# SINGLE SOURCE OF TRUTH for Schema Selection
# ============================================================================
# Intelligent schema selection with flexible configuration:
#
# 📋 Priority Order:
# 1. DB_SCHEMA env var (explicit) → Docker deployment, full control
# 2. ENVIRONMENT env var (auto-derive) → Local development, convenient
#
# 🔧 Usage Examples:
# - Local dev: ENVIRONMENT=development → schema=development
# - Docker dev: DB_SCHEMA=development → schema=development (explicit)
# - Docker prod: DB_SCHEMA=production → schema=production (explicit)
#
# 🎯 Benefits:
# - Local: Just set ENVIRONMENT, schema auto-derived
# - Docker: Explicit DB_SCHEMA for clear separation
# - Single control point: settings.get_db_schema()
# ============================================================================

# Get schema using intelligent fallback
_schema = settings.get_db_schema()

# Async Engine with schema-aware connection
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args={
        "server_settings": {
            # CRITICAL: This sets PostgreSQL's search_path for ALL queries
            # Format: "schema1, schema2, ..." (searches in order)
            # We prioritize our target schema, fallback to public for extensions
            "search_path": f"{_schema}, public"
        }
    },
)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI endpoints to get database session

    Usage:
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
