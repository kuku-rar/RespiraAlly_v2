"""
COPD Knowledge Base Loader
Loads COPD_QA.xlsx data into PostgreSQL with OpenAI embeddings
"""
import asyncio
import sys
from pathlib import Path

import pandas as pd
from openai import AsyncOpenAI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from respira_ally.core.config import settings
from respira_ally.infrastructure.database.models.copd_knowledge_base import (
    COPDKnowledgeBaseModel,
)
from respira_ally.infrastructure.database.session import AsyncSessionLocal


async def generate_embedding(client: AsyncOpenAI, text: str) -> list[float]:
    """
    Generate OpenAI embedding for text

    Args:
        client: AsyncOpenAI client
        text: Text to embed

    Returns:
        1536-dimensional vector
    """
    response = await client.embeddings.create(
        model="text-embedding-3-small", input=text
    )
    return response.data[0].embedding


async def load_knowledge_base():
    """
    Load COPD_QA.xlsx into database with embeddings
    """
    # 1. Read Excel file
    excel_path = Path(__file__).parent.parent / "data" / "COPD_QA.xlsx"
    print(f"📖 Reading {excel_path}...")
    df = pd.read_excel(excel_path)
    print(f"✅ Loaded {len(df)} rows")

    # 2. Initialize OpenAI client
    openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    # 3. Connect to database
    async with AsyncSessionLocal() as session:
        # Clear existing data (optional - remove if you want to keep existing data)
        print("🗑️  Clearing existing knowledge base...")
        await session.execute(text("DELETE FROM copd_knowledge_base"))
        await session.commit()
        print("✅ Cleared")

        # 4. Process each row
        print(f"\n🔄 Processing {len(df)} entries...")
        for idx, row in df.iterrows():
            category = row["類別"]
            question = row["問題（Q）"]
            answer = row["回答（A）"]
            keywords = row["關鍵詞"] if pd.notna(row["關鍵詞"]) else None
            notes = (
                row["注意事項 / 補充說明"]
                if pd.notna(row["注意事項 / 補充說明"])
                else None
            )

            # Combine question and answer for embedding
            text_to_embed = f"Q: {question}\n\nA: {answer}"

            # Generate embedding
            print(f"  [{idx + 1}/{len(df)}] Generating embedding for: {question[:50]}...")
            embedding = await generate_embedding(openai_client, text_to_embed)

            # Create database entry
            kb_entry = COPDKnowledgeBaseModel(
                category=category,
                question=question,
                answer=answer,
                keywords=keywords,
                notes=notes,
                embedding=embedding,
            )

            session.add(kb_entry)

            # Commit in batches of 10 to avoid memory issues
            if (idx + 1) % 10 == 0:
                await session.commit()
                print(f"  ✅ Committed batch up to row {idx + 1}")

        # Final commit
        await session.commit()
        print(f"\n✅ Successfully loaded {len(df)} entries into knowledge base!")

        # 5. Verify insertion
        result = await session.execute(
            text("SELECT COUNT(*) FROM copd_knowledge_base")
        )
        count = result.scalar()
        print(f"📊 Total entries in database: {count}")

        # 6. Show sample categories
        result = await session.execute(
            text("SELECT DISTINCT category FROM copd_knowledge_base ORDER BY category")
        )
        categories = result.scalars().all()
        print(f"\n📂 Categories loaded:")
        for cat in categories:
            print(f"  - {cat}")


if __name__ == "__main__":
    print("🚀 Starting COPD Knowledge Base Loader...")
    print(f"🔧 Using OpenAI model: text-embedding-3-small (1536 dimensions)")
    print(f"🗄️  Database schema: {settings.get_db_schema()}\n")

    try:
        asyncio.run(load_knowledge_base())
        print("\n✨ Done!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
