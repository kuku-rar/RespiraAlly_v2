"""
Move pgvector extension from production schema to public schema

This is the CORRECT way to install pgvector - in the public schema
so all other schemas can use it without schema qualification.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root / "src"))

from respira_ally.infrastructure.database.session import AsyncSessionLocal
from sqlalchemy import text


async def move_pgvector_to_public():
    """Move pgvector to public schema"""
    print("=" * 70)
    print("PGVECTOR SCHEMA MIGRATION (ISSUE-001 FINAL FIX)")
    print("=" * 70)

    async with AsyncSessionLocal() as session:
        # Step 1: Check current installation
        result = await session.execute(
            text(
                """
            SELECT e.extname, n.nspname as schema
            FROM pg_extension e
            JOIN pg_namespace n ON e.extnamespace = n.oid
            WHERE e.extname = 'vector'
        """
            )
        )
        current = result.fetchone()

        if current:
            print(f"\n📋 Current: pgvector installed in '{current.schema}' schema")
        else:
            print("\n⚠️  pgvector not currently installed")

        # Step 2: Drop from current schema if exists
        if current and current.schema != "public":
            print(f"\n🔧 Removing pgvector from '{current.schema}' schema...")
            try:
                await session.execute(text("DROP EXTENSION IF NOT EXISTS vector CASCADE"))
                await session.commit()
                print(f"   ✅ Removed successfully")
            except Exception as e:
                print(f"   ⚠️  Warning: {e}")
                await session.rollback()

        # Step 3: Install in public schema
        print(f"\n🔧 Installing pgvector in 'public' schema...")
        try:
            await session.execute(text("CREATE EXTENSION IF NOT EXISTS vector SCHEMA public"))
            await session.commit()
            print(f"   ✅ Installed successfully in 'public' schema")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            await session.rollback()
            return False

        # Step 4: Verify installation
        result = await session.execute(
            text(
                """
            SELECT n.nspname AS schema, t.typname
            FROM pg_type t
            JOIN pg_namespace n ON t.typnamespace = n.oid
            WHERE t.typname = 'vector'
        """
            )
        )
        verify = result.fetchone()

        if verify and verify.schema == "public":
            print(f"\n✅ Verification: vector type now in '{verify.schema}' schema")
            print(f"\n🎉 ISSUE-001 COMPLETELY FIXED!")
            print(f"\nBenefits:")
            print(f"   ✅ No schema qualification needed in queries")
            print(f"   ✅ Works in development, production, and all schemas")
            print(f"   ✅ Standard PostgreSQL extension practice")
            return True
        else:
            print(f"\n❌ Verification failed")
            return False


if __name__ == "__main__":
    success = asyncio.run(move_pgvector_to_public())
    sys.exit(0 if success else 1)
