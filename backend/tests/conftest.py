"""
Pytest Configuration and Fixtures
Shared fixtures for all tests
"""

import asyncio
from collections.abc import AsyncGenerator
from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from respira_ally.application.auth.use_cases import hash_password
from respira_ally.core.security.jwt import create_access_token
from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
from respira_ally.infrastructure.database.models.therapist_profile import TherapistProfileModel
from respira_ally.infrastructure.database.models.user import UserModel
from respira_ally.infrastructure.database.session import Base
from respira_ally.main import app

# ============================================================================
# Test Database Configuration
# ============================================================================

TEST_DATABASE_URL = "postgresql+asyncpg://admin:admin@localhost:15432/respirally_db"


# ============================================================================
# Async Event Loop Fixture
# ============================================================================


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Database Fixtures
# ============================================================================


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test

    This fixture:
    1. Creates all tables
    2. Yields a session for the test
    3. Rolls back all changes after test
    4. Drops all tables
    """
    # Create async engine
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,  # Disable connection pooling for tests
    )

    # Create all tables (use CASCADE for DROP)
    async with engine.begin() as conn:
        # Use raw SQL with CASCADE to avoid enum type dependency issues
        await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Create session
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    # Drop all tables after test (use CASCADE)
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))

    await engine.dispose()


# ============================================================================
# FastAPI Test Client Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    """
    Create async HTTP client for FastAPI with overridden database dependency

    This ensures the client uses the same test database session as the tests,
    providing proper test isolation and data visibility.

    IMPORTANT: Uses AsyncClient (not TestClient) to avoid event loop conflicts
    """
    from httpx import ASGITransport

    from respira_ally.infrastructure.database.session import get_db

    async def override_get_db():
        """Override get_db dependency to use test db_session"""
        yield db_session

    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    # Use AsyncClient with ASGITransport for async testing
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client

    # Clean up override
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client():
    """
    Create async HTTP client for FastAPI (without database override)

    Use for async tests that don't need database override
    """
    from httpx import ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# ============================================================================
# User Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def therapist_user(db_session: AsyncSession) -> UserModel:
    """Create a therapist user for testing"""
    user = UserModel(
        line_user_id=f"therapist_{uuid4().hex[:8]}",
        role="THERAPIST",
        email="therapist@test.com",
        hashed_password=hash_password("SecurePass123!"),
    )
    db_session.add(user)
    await db_session.flush()

    # Create therapist profile
    therapist_profile = TherapistProfileModel(
        user_id=user.user_id,
        name="Dr. Test Therapist",
        institution="Test Hospital",
        license_number="LIC123456",
    )
    db_session.add(therapist_profile)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest_asyncio.fixture
async def patient_user(db_session: AsyncSession, therapist_user: UserModel) -> UserModel:
    """Create a patient user for testing"""
    user = UserModel(
        line_user_id=f"patient_{uuid4().hex[:8]}",
        role="PATIENT",
        email=None,
        hashed_password=None,
    )
    db_session.add(user)
    await db_session.flush()

    # Create patient profile
    patient_profile = PatientProfileModel(
        user_id=user.user_id,
        therapist_id=therapist_user.user_id,
        name="Test Patient",
        birth_date=date(1970, 1, 1),
        gender="MALE",
        height_cm=170,
        weight_kg=Decimal("70.5"),
        contact_info={},
        medical_history={},
    )
    db_session.add(patient_profile)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest_asyncio.fixture
async def other_patient_user(db_session: AsyncSession, therapist_user: UserModel) -> UserModel:
    """Create another patient user for permission testing"""
    user = UserModel(
        line_user_id=f"patient_{uuid4().hex[:8]}",
        role="PATIENT",
        email=None,
        hashed_password=None,
    )
    db_session.add(user)
    await db_session.flush()

    # Create patient profile with different therapist
    other_therapist = UserModel(
        line_user_id=f"therapist_{uuid4().hex[:8]}",
        role="THERAPIST",
        email="other_therapist@test.com",
        hashed_password=hash_password("SecurePass123!"),
    )
    db_session.add(other_therapist)
    await db_session.flush()

    other_therapist_profile = TherapistProfileModel(
        user_id=other_therapist.user_id,
        name="Dr. Other Therapist",
        institution="萬芳醫院",
        license_number="LIC789012",
        specialties=["胸腔內科"],
    )
    db_session.add(other_therapist_profile)
    await db_session.flush()

    patient_profile = PatientProfileModel(
        user_id=user.user_id,
        therapist_id=other_therapist.user_id,
        name="Other Patient",
        birth_date=date(1980, 5, 15),
        gender="FEMALE",
        height_cm=160,
        weight_kg=Decimal("55.0"),
        contact_info={},
        medical_history={},
    )
    db_session.add(patient_profile)
    await db_session.commit()
    await db_session.refresh(user)

    return user


# ============================================================================
# JWT Token Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def therapist_token(therapist_user: UserModel) -> str:
    """Create JWT token for therapist user"""
    return create_access_token({"sub": str(therapist_user.user_id), "role": "THERAPIST"})


@pytest_asyncio.fixture
async def patient_token(patient_user: UserModel) -> str:
    """Create JWT token for patient user"""
    return create_access_token({"sub": str(patient_user.user_id), "role": "PATIENT"})


@pytest_asyncio.fixture
async def other_patient_token(other_patient_user: UserModel) -> str:
    """Create JWT token for other patient user (for permission testing)"""
    return create_access_token({"sub": str(other_patient_user.user_id), "role": "PATIENT"})


# ============================================================================
# Common Fixtures
# ============================================================================


@pytest.fixture
def sample_email():
    """Sample email for testing"""
    return "test@example.com"


@pytest.fixture
def sample_password():
    """Sample password for testing"""
    return "SecurePass123!"
