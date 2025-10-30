"""Check the actual type of the embedding column"""

import asyncio
import sys
from pathlib import Path

# Add src to path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root / "src"))

from respira_ally.infrastructure.database.session import AsyncSessionLocal
from respira_ally.core.config import settings
from sqlalchemy import text


async def check_embedding_column():
    """Check the embedding column type definition"""
    print("=" * 70)
    print("EMBEDDING COLUMN TYPE CHECK")
    print("=" * 70)

    schema = settings.get_db_schema()
    print(f"\nTarget schema: {schema}\n")

    async with AsyncSessionLocal() as session:
        # Check column definition
        result = await session.execute(
            text(
                """
            SELECT
                column_name,
                udt_schema,
                udt_name,
                data_type
            FROM information_schema.columns
            WHERE table_schema = :schema
              AND table_name = 'copd_knowledge_base'
              AND column_name = 'embedding'
        """
            ),
            {"schema": schema},
        )
        row = result.fetchone()

        if row:
            print(f"Column: {row.column_name}")
            print(f"Data type: {row.data_type}")
            print(f"UDT Schema: {row.udt_schema}")
            print(f"UDT Name: {row.udt_name}")

            full_type = f"{row.udt_schema}.{row.udt_name}" if row.udt_schema else row.udt_name
            print(f"\n✅ Full type: {full_type}")
        else:
            print(f"❌ embedding column not found in {schema}.copd_knowledge_base")


if __name__ == "__main__":
    asyncio.run(check_embedding_column())
