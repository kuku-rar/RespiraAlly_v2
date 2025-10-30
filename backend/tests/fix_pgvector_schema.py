"""
Fix pgvector schema installation

Install pgvector extension in the development schema
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root / "src"))

from respira_ally.infrastructure.database.session import AsyncSessionLocal
from respira_ally.core.config import settings
from sqlalchemy import text


async def install_pgvector_in_development():
    """Install pgvector extension in development schema"""
    print("=" * 70)
    print("PGVECTOR SCHEMA FIX (ISSUE-001)")
    print("=" * 70)

    target_schema = settings.get_db_schema()
    print(f"\n📋 Target schema: {target_schema}")

    async with AsyncSessionLocal() as session:
        # Check if already installed
        result = await session.execute(
            text(
                """
            SELECT n.nspname AS schema
            FROM pg_type t
            JOIN pg_namespace n ON t.typnamespace = n.oid
            WHERE t.typname = 'vector' AND n.nspname = :schema
        """
            ),
            {"schema": target_schema},
        )
        existing = result.fetchone()

        if existing:
            print(f"✅ pgvector already installed in '{target_schema}' schema")
            return True

        print(f"\n🔧 Installing pgvector extension in '{target_schema}' schema...")

        try:
            # Create extension in target schema
            await session.execute(
                text(f"CREATE EXTENSION IF NOT EXISTS vector SCHEMA {target_schema}")
            )
            await session.commit()

            print(f"✅ pgvector extension installed successfully in '{target_schema}'!")

            # Verify installation
            result = await session.execute(
                text(
                    """
                SELECT n.nspname AS schema, t.typname
                FROM pg_type t
                JOIN pg_namespace n ON t.typnamespace = n.oid
                WHERE t.typname = 'vector' AND n.nspname = :schema
            """
                ),
                {"schema": target_schema},
            )
            verify = result.fetchone()

            if verify:
                print(f"✅ Verification: vector type found in '{verify.schema}' schema")
                print(f"\n🎉 ISSUE-001 FIX COMPLETE!")
                print(f"   pgvector is now available in the correct schema")
                return True
            else:
                print(f"❌ Verification failed: vector type not found")
                return False

        except Exception as e:
            print(f"❌ Installation failed: {type(e).__name__}: {e}")
            print(f"\n💡 You may need superuser privileges to install extensions.")
            print(f"   Try running manually:")
            print(f"   CREATE EXTENSION IF NOT EXISTS vector SCHEMA {target_schema};")
            return False


if __name__ == "__main__":
    success = asyncio.run(install_pgvector_in_development())
    sys.exit(0 if success else 1)
