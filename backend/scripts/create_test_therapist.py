"""
臨時腳本：創建測試 therapist 帳號
用於 Task Board UI 真實 API 測試

帳號資訊：
- Email: test@therapist.com
- Password: SecurePass123!
"""

import asyncio
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
from respira_ally.infrastructure.database.models.therapist_profile import TherapistProfileModel


async def create_test_therapist():
    """創建測試 therapist 帳號"""

    # Database connection
    database_url = "postgresql+asyncpg://admin:admin@localhost:15432/respirally_db"

    # Test account credentials
    email = "test@therapist.com"
    password = "SecurePass123!"

    # Create async engine
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # Check if user already exists
            result = await session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"✅ Test therapist already exists: {email}")
                print(f"   User ID: {existing_user.user_id}")
                print(f"   Password: {password}")
                return existing_user.user_id

            # Create therapist user
            hashed_password = hash_password(password)
            therapist_user = UserModel(
                email=email,
                hashed_password=hashed_password,
                role="THERAPIST",
                line_user_id=None,
            )

            session.add(therapist_user)
            await session.flush()

            # Create therapist profile
            therapist_profile = TherapistProfileModel(
                user_id=therapist_user.user_id,
                name="測試治療師",
                institution="測試醫院",
                license_number="TEST123456",
                specialties=["呼吸治療"],
            )

            session.add(therapist_profile)
            await session.commit()
            await session.refresh(therapist_user)

            print("\n✅ Test therapist created successfully!")
            print(f"   Email: {email}")
            print(f"   Password: {password}")
            print(f"   User ID: {therapist_user.user_id}")
            print(f"   Role: THERAPIST")

            return therapist_user.user_id

        except Exception as e:
            print(f"\n❌ Error creating test therapist: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    print("🔧 Creating test therapist account...")
    print("=" * 60)
    asyncio.run(create_test_therapist())
    print("=" * 60)
    print("✅ Done!")
