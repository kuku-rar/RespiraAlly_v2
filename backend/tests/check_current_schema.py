"""Check current schema configuration and pgvector installation"""

import asyncio
import sys
from pathlib import Path

# Add src to path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root / "src"))

from respira_ally.infrastructure.database.session import AsyncSessionLocal
from respira_ally.core.config import settings
from sqlalchemy import text


async def check_schema_config():
    """Check schema configuration and pgvector installation"""
    print("=" * 70)
    print("SCHEMA CONFIGURATION CHECK")
    print("=" * 70)

    # Check environment configuration
    print(f"\n📋 Environment Configuration:")
    print(f"   ENVIRONMENT: {settings.ENVIRONMENT}")
    print(f"   DB_SCHEMA: {settings.DB_SCHEMA}")
    print(f"   get_db_schema(): {settings.get_db_schema()}")

    async with AsyncSessionLocal() as session:
        # Check current search_path
        result = await session.execute(text("SHOW search_path"))
        search_path = result.scalar()
        print(f"\n🔍 Current search_path: {search_path}")

        # Check current schema
        result = await session.execute(text("SELECT current_schema()"))
        current_schema = result.scalar()
        print(f"   Current schema: {current_schema}")

        # Check all schemas in database
        result = await session.execute(
            text(
                """
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            ORDER BY schema_name
        """
            )
        )
        schemas = [row[0] for row in result.fetchall()]
        print(f"\n📊 Available schemas: {', '.join(schemas)}")

        # Check pgvector installation in each schema
        print(f"\n🔬 pgvector installation status:")
        result = await session.execute(
            text(
                """
            SELECT n.nspname AS schema, t.typname AS type_name
            FROM pg_type t
            JOIN pg_namespace n ON t.typnamespace = n.oid
            WHERE t.typname = 'vector'
            ORDER BY n.nspname
        """
            )
        )
        vector_schemas = result.fetchall()

        if vector_schemas:
            for row in vector_schemas:
                marker = "✅" if row.schema == settings.get_db_schema() else "⚠️ "
                print(f"   {marker} vector type found in: {row.schema}")
        else:
            print("   ❌ vector type not found in any schema!")

        # Check pgvector extension
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
        extensions = result.fetchall()

        print(f"\n📦 pgvector extension:")
        if extensions:
            for row in extensions:
                marker = "✅" if row.schema == settings.get_db_schema() else "⚠️ "
                print(f"   {marker} Installed in schema: {row.schema}")
        else:
            print("   ❌ pgvector extension not found!")

        # Check if development schema has the extension
        expected_schema = settings.get_db_schema()
        has_vector_in_expected = any(
            row.schema == expected_schema for row in vector_schemas
        )

        print(f"\n" + "=" * 70)
        print("DIAGNOSIS")
        print("=" * 70)

        if has_vector_in_expected:
            print(f"✅ vector type is available in expected schema: {expected_schema}")
            print(f"   Should use: schema='{expected_schema}' for registration")
        else:
            print(f"⚠️  vector type NOT found in expected schema: {expected_schema}")
            if vector_schemas:
                actual_schema = vector_schemas[0].schema
                print(f"   Found in: {actual_schema}")
                print(f"\n💡 SOLUTION: Either:")
                print(f"   1. Reinstall pgvector in '{expected_schema}' schema:")
                print(f"      CREATE EXTENSION IF NOT EXISTS vector SCHEMA {expected_schema};")
                print(f"   2. Or use the schema where it's installed: '{actual_schema}'")
            else:
                print(f"   pgvector is not installed at all!")

        return has_vector_in_expected, expected_schema


if __name__ == "__main__":
    asyncio.run(check_schema_config())
