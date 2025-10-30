"""
Test pgvector + asyncpg Type Registration Fix (ISSUE-001)

This test verifies that the pgvector type registration in session.py
correctly enables semantic search functionality.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path for imports
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root / "src"))

from respira_ally.infrastructure.database.session import AsyncSessionLocal, engine
from respira_ally.infrastructure.repository_impls.pgvector_knowledge_repository import (
    PgvectorKnowledgeRepository,
)


async def test_vector_type_registration():
    """
    Test that vector type is properly registered with asyncpg.

    This addresses ISSUE-001: asyncpg.exceptions.UndefinedObjectError
    """
    print("🧪 Testing pgvector + asyncpg type registration...\n")

    async with AsyncSessionLocal() as session:
        # Create knowledge repository
        repo = PgvectorKnowledgeRepository(session)

        # Test 1: Check if we can query categories (non-vector operation)
        print("✅ Test 1: Query categories (baseline test)")
        try:
            categories = await repo.get_all_categories()
            print(f"   Found {len(categories)} categories")
            print(f"   Sample categories: {categories[:3]}")
        except Exception as e:
            print(f"   ❌ FAILED: {type(e).__name__}: {e}")
            return False

        # Test 2: Semantic search (vector operation - the critical test)
        print("\n✅ Test 2: Semantic search with vector similarity (ISSUE-001 test)")
        try:
            query = "如何預防 COPD 惡化？"
            print(f"   Query: '{query}'")

            results = await repo.search(query=query, top_k=3)

            if not results:
                print("   ⚠️  No results found (might be empty knowledge base)")
                return False

            print(f"   ✅ Found {len(results)} results:")
            for i, doc in enumerate(results, 1):
                print(f"   {i}. Score: {doc.score:.4f}")
                print(f"      Category: {doc.metadata.get('category', 'N/A')}")
                # Show first 50 chars of content
                content_preview = doc.content[:50].replace("\n", " ")
                print(f"      Preview: {content_preview}...")

            print("\n🎉 Vector type registration SUCCESS!")
            print("   ISSUE-001 is RESOLVED ✅")
            return True

        except Exception as e:
            print(f"   ❌ FAILED: {type(e).__name__}: {e}")
            print("\n🔴 Vector type registration FAILED")
            print("   ISSUE-001 is NOT resolved ❌")
            return False


async def test_keyword_search_fallback():
    """
    Test keyword search as fallback (doesn't use vector type).
    """
    print("\n✅ Test 3: Keyword search fallback")

    async with AsyncSessionLocal() as session:
        repo = PgvectorKnowledgeRepository(session)

        try:
            keywords = ["COPD", "肺部"]
            results = await repo.search_by_keywords(keywords, top_k=3)

            print(f"   ✅ Found {len(results)} results using keywords: {keywords}")
            for i, doc in enumerate(results, 1):
                category = doc.metadata.get("category", "N/A")
                print(f"   {i}. Category: {category}")

            return True

        except Exception as e:
            print(f"   ❌ FAILED: {type(e).__name__}: {e}")
            return False


async def cleanup():
    """Clean up database connections."""
    print("\n🧹 Cleaning up...")
    await engine.dispose()
    print("   Database connections closed")


async def main():
    """Run all tests."""
    print("=" * 70)
    print("PGVECTOR + ASYNCPG COMPATIBILITY TEST (ISSUE-001)")
    print("=" * 70)

    try:
        # Test vector type registration (the critical fix)
        test1_passed = await test_vector_type_registration()

        # Test keyword fallback
        test2_passed = await test_keyword_search_fallback()

        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Vector type registration: {'✅ PASS' if test1_passed else '❌ FAIL'}")
        print(f"Keyword search fallback:  {'✅ PASS' if test2_passed else '❌ FAIL'}")

        if test1_passed:
            print("\n🎉 ISSUE-001 RESOLVED!")
            print("   pgvector + asyncpg type registration is working correctly.")
            print("   Semantic search is now fully functional.")
        else:
            print("\n⚠️  ISSUE-001 NOT RESOLVED")
            print("   Vector type registration failed.")
            print("   Please check the event listener in session.py")

        return test1_passed and test2_passed

    except Exception as e:
        print(f"\n❌ Unexpected error: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        await cleanup()


if __name__ == "__main__":
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Embedding generation may fail.")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'\n")

    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
