"""
Simple test for vector type registration only
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root / "src"))

from respira_ally.infrastructure.database.session import AsyncSessionLocal, register_pgvector_type
from sqlalchemy import text


async def test_registration():
    """Test if vector type registration works"""
    print("=" * 70)
    print("VECTOR TYPE REGISTRATION TEST")
    print("=" * 70)

    async with AsyncSessionLocal() as session:
        # Step 1: Register vector type
        print("\n🔧 Registering vector type...")
        try:
            await register_pgvector_type(session)
            print("   ✅ Registration completed")
        except Exception as e:
            print(f"   ❌ Registration failed: {e}")
            return False

        # Step 2: Test simple vector cast
        print("\n🧪 Testing vector type cast...")
        try:
            result = await session.execute(
                text("SELECT '[1,2,3]'::vector AS test_vector")
            )
            row = result.fetchone()
            print(f"   ✅ Vector cast successful: {row.test_vector}")
        except Exception as e:
            print(f"   ❌ Vector cast failed: {type(e).__name__}: {e}")
            return False

        # Step 3: Test vector operator (<=>)
        print("\n🧪 Testing vector cosine distance operator...")
        try:
            result = await session.execute(
                text("SELECT '[1,2,3]'::vector <=> '[3,2,1]'::vector AS distance")
            )
            row = result.fetchone()
            print(f"   ✅ Operator successful: distance = {row.distance}")
        except Exception as e:
            print(f"   ❌ Operator failed: {type(e).__name__}: {e}")
            return False

        print("\n🎉 ALL TESTS PASSED!")
        print("   Vector type registration is working correctly")
        return True


if __name__ == "__main__":
    success = asyncio.run(test_registration())
    sys.exit(0 if success else 1)
