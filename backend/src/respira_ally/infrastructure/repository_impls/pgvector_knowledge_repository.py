"""
PgVector Knowledge Repository Implementation
"""
from openai import AsyncOpenAI
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.core.config import settings
from respira_ally.domain.repositories.knowledge_repository import (
    KnowledgeRepository,
)
from respira_ally.domain.value_objects.knowledge import Document
from respira_ally.infrastructure.database.models.copd_knowledge_base import (
    COPDKnowledgeBaseModel,
)


class PgvectorKnowledgeRepository(KnowledgeRepository):
    """
    pgvector 知識庫檢索實現

    使用 OpenAI text-embedding-3-small 生成 embeddings
    使用 pgvector cosine similarity 進行語義搜尋
    """

    def __init__(self, db_session: AsyncSession):
        """
        Args:
            db_session: SQLAlchemy AsyncSession 實例
        """
        self.db = db_session
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_model = "text-embedding-3-small"  # 1536 dimensions

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
        # 1. 生成查詢的 embedding
        query_embedding = await self._generate_embedding(query)

        # 2. 構建 SQL 查詢
        # pgvector cosine similarity: <-> operator (距離越小越相似)
        # 轉換為分數: 1 - distance (分數越高越相似)
        stmt = select(
            COPDKnowledgeBaseModel,
            (1 - COPDKnowledgeBaseModel.embedding.cosine_distance(query_embedding)).label(
                "similarity_score"
            ),
        )

        # 可選的類別篩選
        if category:
            stmt = stmt.where(COPDKnowledgeBaseModel.category == category)

        # 按相似度排序，取前 K 個
        stmt = stmt.order_by(text("similarity_score DESC")).limit(top_k)

        # 3. 執行查詢
        result = await self.db.execute(stmt)
        rows = result.all()

        # 4. 轉換為 Document value objects
        documents = []
        for row in rows:
            kb_entry, score = row
            doc = Document(
                content=f"Q: {kb_entry.question}\n\nA: {kb_entry.answer}",
                metadata={
                    "id": str(kb_entry.id),
                    "category": kb_entry.category,
                    "keywords": kb_entry.keywords,
                    "notes": kb_entry.notes,
                },
                score=float(score),
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
