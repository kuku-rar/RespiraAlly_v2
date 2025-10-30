"""
PgVector Knowledge Repository Implementation
"""
from openai import AsyncOpenAI
from pgvector.sqlalchemy import Vector
from sqlalchemy import cast, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.core.config import settings
from respira_ally.domain.repositories.knowledge_repository import (
    KnowledgeRepository,
)
from respira_ally.domain.value_objects.knowledge import Document
from respira_ally.infrastructure.database.models.copd_knowledge_base import (
    COPDKnowledgeBaseModel,
)
from respira_ally.infrastructure.database.session import register_pgvector_type


class PgvectorKnowledgeRepository(KnowledgeRepository):
    """
    pgvector 知識庫檢索實現

    使用 OpenAI text-embedding-3-small 生成 embeddings
    使用 pgvector cosine similarity 進行語義搜尋

    ISSUE-001 FIX: 自動註冊 pgvector 類型以支援 asyncpg
    """

    def __init__(self, db_session: AsyncSession):
        """
        Args:
            db_session: SQLAlchemy AsyncSession 實例
        """
        self.db = db_session
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_model = "text-embedding-3-small"  # 1536 dimensions
        self._vector_type_registered = False  # ISSUE-001: Track registration status

    async def _ensure_vector_type_registered(self):
        """
        確保 pgvector 類型已註冊（ISSUE-001 修復）

        只會執行一次，之後會快取註冊狀態並記錄 vector schema
        """
        if not self._vector_type_registered:
            # Register the vector type
            await register_pgvector_type(self.db)

            # Get the schema where vector type exists
            from sqlalchemy import text

            result = await self.db.execute(
                text(
                    """
                SELECT n.nspname AS schema
                FROM pg_type t
                JOIN pg_namespace n ON t.typnamespace = n.oid
                WHERE t.typname = 'vector'
                LIMIT 1
            """
                )
            )
            row = result.fetchone()
            self._vector_schema = row.schema if row else "public"
            self._vector_type_registered = True

    async def _generate_embedding(self, text: str) -> list[float]:
        """
        使用 OpenAI API 生成文本 embedding

        Args:
            text: 要嵌入的文本

        Returns:
            1536 維度的向量
        """
        response = await self.openai_client.embeddings.create(
            model=self.embedding_model, input=text
        )
        return response.data[0].embedding

    async def search(
        self, query: str, top_k: int = 3, category: str | None = None
    ) -> list[Document]:
        """
        語義相似度搜尋

        使用 pgvector 的 cosine similarity (<->) 進行向量搜尋

        Args:
            query: 搜尋查詢文本
            top_k: 返回最相關的前 K 個文檔（預設3個）
            category: 可選的類別篩選

        Returns:
            相關文檔列表（按相似度分數排序，最相關的在前）
        """
        # 0. ISSUE-001 FIX: 確保 pgvector 類型已註冊
        await self._ensure_vector_type_registered()

        # 1. 生成查詢的 embedding
        query_embedding = await self._generate_embedding(query)

        # 2. 使用原生 SQL 進行 pgvector 查詢
        # 將 embedding 轉為字串格式供 PostgreSQL 使用
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

        # 獲取當前 schema
        schema = settings.get_db_schema()

        # ISSUE-001 FIX: 使用 pgvector 的操作符和函數（不需要 schema 限定）
        # asyncpg 已註冊 vector 類型，可直接使用操作符
        # 使用字串替換而非參數綁定來處理 vector 類型
        if category:
            query_sql = text(f"""
                SELECT
                    id, category, question, answer, keywords, notes,
                    embedding, created_at, updated_at,
                    1 - (embedding <=> '{embedding_str}'::vector) AS similarity_score
                FROM {schema}.copd_knowledge_base
                WHERE category = :category
                ORDER BY similarity_score DESC
                LIMIT :limit
            """)
            params = {"category": category, "limit": top_k}
        else:
            query_sql = text(f"""
                SELECT
                    id, category, question, answer, keywords, notes,
                    embedding, created_at, updated_at,
                    1 - (embedding <=> '{embedding_str}'::vector) AS similarity_score
                FROM {schema}.copd_knowledge_base
                ORDER BY similarity_score DESC
                LIMIT :limit
            """)
            params = {"limit": top_k}

        # 3. 執行查詢
        result = await self.db.execute(query_sql, params)
        rows = result.fetchall()

        # 4. 轉換為 Document value objects
        documents = []
        for row in rows:
            # 原生 SQL 返回的是 Row 對象，使用索引或列名訪問
            doc = Document(
                content=f"Q: {row.question}\n\nA: {row.answer}",
                metadata={
                    "id": str(row.id),
                    "category": row.category,
                    "keywords": row.keywords,
                    "notes": row.notes,
                },
                score=float(row.similarity_score),
            )
            documents.append(doc)

        return documents

    async def search_by_keywords(
        self, keywords: list[str], top_k: int = 3
    ) -> list[Document]:
        """
        關鍵詞搜尋

        使用 LIKE 模糊搜尋 keywords 欄位和 question 欄位

        Args:
            keywords: 關鍵詞列表
            top_k: 返回最相關的前 K 個文檔

        Returns:
            相關文檔列表
        """
        if not keywords:
            return []

        # 構建 OR 條件：任一關鍵詞匹配即可
        from sqlalchemy import or_

        conditions = []
        for keyword in keywords:
            # 搜尋 keywords 欄位
            conditions.append(
                COPDKnowledgeBaseModel.keywords.ilike(f"%{keyword}%")
            )
            # 搜尋 question 欄位
            conditions.append(
                COPDKnowledgeBaseModel.question.ilike(f"%{keyword}%")
            )

        # 使用 OR 連接所有條件
        stmt = (
            select(COPDKnowledgeBaseModel)
            .where(or_(*conditions))
            .limit(top_k)
        )

        result = await self.db.execute(stmt)
        kb_entries = result.scalars().all()

        # 轉換為 Document value objects
        documents = []
        for kb_entry in kb_entries:
            doc = Document(
                content=f"Q: {kb_entry.question}\n\nA: {kb_entry.answer}",
                metadata={
                    "id": str(kb_entry.id),
                    "category": kb_entry.category,
                    "keywords": kb_entry.keywords,
                    "notes": kb_entry.notes,
                },
                score=1.0,  # 關鍵詞搜尋沒有相似度分數，預設 1.0
            )
            documents.append(doc)

        return documents

    async def get_all_categories(self) -> list[str]:
        """
        獲取所有知識庫類別

        Returns:
            類別列表（去重排序）
        """
        stmt = select(COPDKnowledgeBaseModel.category).distinct()
        result = await self.db.execute(stmt)
        categories = result.scalars().all()

        # 排序並返回
        return sorted(categories)
