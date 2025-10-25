"""
Database Migration Helper - Dual Schema Support
Runs Alembic migrations on both production and development schemas

Usage:
    # Migrate both schemas to latest
    uv run python scripts/migrate_schemas.py

    # Migrate specific schema
    uv run python scripts/migrate_schemas.py --schema production
    uv run python scripts/migrate_schemas.py --schema development

    # Downgrade
    uv run python scripts/migrate_schemas.py --down

Environment Variables:
    DATABASE_URL: PostgreSQL connection string (from .env)
    DB_SCHEMA: Target schema (default: both)
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Add backend src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv

# Load .env file
load_dotenv(Path(__file__).parent.parent / ".env")

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Import Base to get all models
from respira_ally.infrastructure.database.session import Base


async def run_migrations_for_schema(schema_name: str, database_url: str):
    """
    Run Alembic migrations for a specific schema

    This creates all tables defined in Base.metadata in the target schema
    """
    print(f"\n{'='*70}")
    print(f"🔄 Migrating schema: {schema_name}")
    print(f"{'='*70}")

    # Create async engine
    engine = create_async_engine(database_url, echo=False)

    try:
        async with engine.begin() as conn:
            # Set schema search path for this connection
            await conn.execute(text(f"SET search_path TO {schema_name}"))

            # Create all tables in this schema
            await conn.run_sync(Base.metadata.create_all)

            print(f"✅ Schema '{schema_name}' migrated successfully")

            # List created tables
            result = await conn.execute(text(
                f"""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = '{schema_name}'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
                """
            ))
            tables = result.fetchall()

            print(f"\n📋 Tables in '{schema_name}' schema ({len(tables)}):")
            for table in tables:
                print(f"   - {table[0]}")

    except Exception as e:
        print(f"❌ Error migrating schema '{schema_name}': {e}")
        raise
    finally:
        await engine.dispose()


async def main():
    """Main migration orchestrator"""
    parser = argparse.ArgumentParser(description="Migrate database schemas")
    parser.add_argument(
        "--schema",
        choices=["production", "development", "both"],
        default="both",
        help="Target schema to migrate (default: both)"
    )
    parser.add_argument(
        "--down",
        action="store_true",
        help="Downgrade (not implemented - use Alembic directly)"
    )

    args = parser.parse_args()

    if args.down:
        print("❌ Downgrade not supported by this script")
        print("   Use: uv run alembic downgrade -1")
        return 1

    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not set in environment")
        return 1

    print("🚀 RespiraAlly Database Schema Migration")
    print(f"📌 Database: {database_url.split('@')[1] if '@' in database_url else 'unknown'}")

    # Migrate selected schema(s)
    if args.schema == "both":
        await run_migrations_for_schema("production", database_url)
        await run_migrations_for_schema("development", database_url)
    else:
        await run_migrations_for_schema(args.schema, database_url)

    print(f"\n{'='*70}")
    print("✅ Migration Complete!")
    print(f"{'='*70}")
    print("\n📋 Next Steps:")
    print("   1. Verify schemas: docker exec respirally-postgres psql -U admin -d respirally_db -c '\\dn'")
    print("   2. Generate test data: uv run python scripts/generate_test_data.py")
    print("   3. Check tables: docker exec respirally-postgres psql -U admin -d respirally_db -c '\\dt development.*'")

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
