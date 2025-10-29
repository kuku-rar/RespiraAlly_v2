"""
Initialize COPD Knowledge Base Table
Uses project's existing database connection and settings
"""
import asyncio
import sys
from pathlib import Path

# Add backend src to path
backend_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_path))

from sqlalchemy import text
from respira_ally.core.config import settings
from respira_ally.infrastructure.database.session import engine


async def init_copd_knowledge_base():
    """Initialize COPD knowledge base table with pgvector support"""

    async with engine.begin() as conn:
        # Get current schema
        schema = settings.get_db_schema()
        print(f"🔧 Initializing in schema: {schema}")

        # Enable pgvector extension (in public schema, only needs to run once)
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        print("✅ pgvector extension enabled")

        # Create simplified table (text-based search for now, will add vector later)
        await conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {schema}.copd_knowledge_base (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                category VARCHAR(128) NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                keywords VARCHAR(1024),
                notes TEXT,
                -- Simplified: use TEXT for now, will add vector column later
                search_text TEXT GENERATED ALWAYS AS (
                    question || ' ' || answer || ' ' || COALESCE(keywords, '')
                ) STORED,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
        """))
        print(f"✅ Table {schema}.copd_knowledge_base created (text-based search)")

        # Create full-text search index
        await conn.execute(text(f"""
            CREATE INDEX IF NOT EXISTS idx_copd_kb_search_text
                ON {schema}.copd_knowledge_base
                USING gin(to_tsvector('english', search_text));
        """))
        print("✅ Full-text search index created")

        # Create B-tree index for category
        await conn.execute(text(f"""
            CREATE INDEX IF NOT EXISTS idx_copd_kb_category
                ON {schema}.copd_knowledge_base (category);
        """))
        print("✅ Category index created")

        # Verify
        result = await conn.execute(text(f"SELECT COUNT(*) FROM {schema}.copd_knowledge_base;"))
        count = result.scalar()
        print(f"\n✅ Table ready! Current row count: {count}")

    await engine.dispose()


if __name__ == "__main__":
    print("=" * 60)
    print("COPD Knowledge Base Table Initialization")
    print("=" * 60)
    asyncio.run(init_copd_knowledge_base())
    print("\n✅ Initialization complete!")
