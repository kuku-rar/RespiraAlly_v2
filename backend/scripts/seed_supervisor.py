"""
Seed SUPERVISOR user for MVP testing

ADR-015: RBAC Extension for MVP Flexibility

This script creates a SUPERVISOR user with email/password authentication.
SUPERVISOR role can access ALL patients' data (unrestricted access for MVP testing).

Usage:
    uv run python scripts/seed_supervisor.py

Environment Variables:
    - DATABASE_URL: PostgreSQL connection string (default: from .env)
    - SUPERVISOR_EMAIL: SUPERVISOR email (default: supervisor@respiraally.com)
    - SUPERVISOR_PASSWORD: SUPERVISOR password (default: supervisor123)
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load .env file
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from respira_ally.application.auth.use_cases.login_use_case import hash_password
from respira_ally.infrastructure.database.models.user import UserModel


async def seed_supervisor():
    """Create SUPERVISOR user for MVP testing"""

    # Get database URL from environment
    database_url = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://admin:admin@localhost:15432/respirally_db"
    )

    # SUPERVISOR credentials (can be overridden via environment variables)
    email = os.getenv("SUPERVISOR_EMAIL", "supervisor@respiraally.com")
    password = os.getenv("SUPERVISOR_PASSWORD", "supervisor123")

    # Create async engine
    engine = create_async_engine(database_url, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # Check if SUPERVISOR user already exists
            result = await session.execute(
                select(UserModel).where(
                    UserModel.email == email, UserModel.role == "SUPERVISOR"
                )
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"✅ SUPERVISOR user already exists: {email}")
                print(f"   User ID: {existing_user.user_id}")
                return

            # Create SUPERVISOR user
            hashed_password = hash_password(password)
            supervisor_user = UserModel(
                email=email,
                hashed_password=hashed_password,
                role="SUPERVISOR",
                line_user_id=None,  # SUPERVISOR uses email/password, not LINE
            )

            session.add(supervisor_user)
            await session.commit()
            await session.refresh(supervisor_user)

            print("\n✅ SUPERVISOR user created successfully!")
            print(f"   Email: {email}")
            print(f"   Password: {password}")
            print(f"   User ID: {supervisor_user.user_id}")
            print(f"   Role: SUPERVISOR")
            print(
                "\n⚠️  IMPORTANT: This user has unrestricted access to ALL patients' data (MVP mode)"
            )
            print("   Change the password in production!")

        except Exception as e:
            print(f"\n❌ Error creating SUPERVISOR user: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    print("🔧 Seeding SUPERVISOR user for MVP testing...")
    print("=" * 60)
    asyncio.run(seed_supervisor())
    print("=" * 60)
    print("✅ Seed complete!")
