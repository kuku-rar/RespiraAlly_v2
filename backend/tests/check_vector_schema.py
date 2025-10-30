"""Check which schema the pgvector extension is installed in"""

import asyncio
import sys
from pathlib import Path

# Add src to path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root / "src"))

from respira_ally.infrastructure.database.session import AsyncSessionLocal
from sqlalchemy import text


async def check_vector_schema():
    """Query the database to find the vector type schema"""
    print("🔍 Checking pgvector installation...\n")

    async with AsyncSessionLocal() as session:
        # Check if vector type exists and in which schema
        result = await session.execute(
            text(
                """
            SELECT n.nspname AS schema, t.typname AS type_name
            FROM pg_type t
            JOIN pg_namespace n ON t.typnamespace = n.oid
            WHERE t.typname = 'vector'
        """
            )
        )
        rows = result.fetchall()

        if not rows:
            print("❌ Vector type not found in database!")
            print("   pgvector extension might not be installed.")
            return None

        for row in rows:
            print(f"✅ Found vector type in schema: {row.schema}")

        # Check pgvector extension
        result = await session.execute(
            text(
                """
            SELECT extname, nspname
            FROM pg_extension e
            JOIN pg_namespace n ON e.extnamespace = n.oid
            WHERE extname = 'vector'
        """
            )
        )
        ext_rows = result.fetchall()

        if ext_rows:
            for row in ext_rows:
                print(f"✅ pgvector extension installed in schema: {row.nspname}")
        else:
            print("⚠️  pgvector extension not found (might be installed differently)")

        return rows[0].schema if rows else None


if __name__ == "__main__":
    schema = asyncio.run(check_vector_schema())
    if schema:
        print(f"\n📝 Recommendation: Use schema='{schema}' when registering vector type")
