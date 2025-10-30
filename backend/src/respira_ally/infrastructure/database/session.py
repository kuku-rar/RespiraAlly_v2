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

# ISSUE-001 FIX: Include production schema in search_path for pgvector types
# Since pgvector is installed in production schema, we need it in search_path
# Order: current_schema (development/production), production (for vector type), public
_search_path_schemas = [_schema]
if _schema != "production":
    _search_path_schemas.append("production")  # Add production for pgvector
_search_path_schemas.append("public")  # Always include public
_search_path = ", ".join(_search_path_schemas)

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
            # ISSUE-001: Include production schema for pgvector types
            "search_path": _search_path
        }
    },
)


# ============================================================================
# pgvector Type Registration Helper (ISSUE-001 FIX)
# ============================================================================
# NOTE: This helper function is used by repositories that need pgvector support
# Called once per repository initialization to register the vector type
# ============================================================================


async def register_pgvector_type(session: AsyncSession) -> None:
    """
    Register pgvector 'vector' type with asyncpg for the current session.

    ISSUE-001 FIX: asyncpg doesn't auto-discover custom PostgreSQL types.
    This function must be called before executing any queries with vector operations.

    The function automatically detects which schema contains the vector type.

    Args:
        session: SQLAlchemy AsyncSession
    """
    from sqlalchemy import text
    from pgvector.asyncpg import register_vector

    # Step 1: Find which schema contains the vector type
    result = await session.execute(
        text(
            """
        SELECT n.nspname AS schema
        FROM pg_type t
        JOIN pg_namespace n ON t.typnamespace = n.oid
        WHERE t.typname = 'vector'
        LIMIT 1
    """
        )
    )
    row = result.fetchone()

    if not row:
        raise RuntimeError(
            "pgvector extension not found. "
            "Please install it with: CREATE EXTENSION IF NOT EXISTS vector;"
        )

    vector_schema = row.schema

    # Step 2: Get the raw asyncpg connection
    raw_connection = await session.connection()

    # Access the actual asyncpg connection through sync_connection
    # We need to unwrap: AsyncConnection -> sync_connection -> driver.connection -> asyncpg.Connection
    def get_driver_conn(sync_conn):
        # sync_conn.connection is AsyncAdapt_asyncpg_connection
        # We need to get its _connection attribute which is the real asyncpg.Connection
        adapted_conn = sync_conn.connection
        # The actual asyncpg connection is in _connection attribute
        return adapted_conn._connection

    # Get the asyncpg connection object
    driver_conn = await raw_connection.run_sync(get_driver_conn)

    # Step 3: Register the vector type with the correct schema
    await register_vector(driver_conn, schema=vector_schema)

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
