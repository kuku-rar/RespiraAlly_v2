"""
COPD Knowledge Base Model - RAG Vector Store
Stores COPD Q&A data with embeddings for semantic search using pgvector
"""

from datetime import datetime
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from respira_ally.core.config import settings
from respira_ally.infrastructure.database.session import Base


class COPDKnowledgeBaseModel(Base):
    """
    COPD Knowledge Base table - Vector store for RAG

    Stores structured COPD Q&A knowledge with embeddings for semantic search.
    Based on COPD_QA.xlsx data structure.
    """

    __tablename__ = "copd_knowledge_base"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, server_default=text("gen_random_uuid()")
    )

    # Content Fields (from COPD_QA.xlsx)
    category: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="類別 (e.g., 生活品質與運動, 藥物治療)"
    )
    question: Mapped[str] = mapped_column(
        Text, nullable=False, comment="問題（Q）- COPD 相關問題"
    )
    answer: Mapped[str] = mapped_column(
        Text, nullable=False, comment="回答（A）- 專業回答內容"
    )
    keywords: Mapped[str | None] = mapped_column(
        String(1024), nullable=True, comment="關鍵詞 - 搜尋標籤"
    )
    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="注意事項 / 補充說明"
    )

    # Vector Field for RAG (OpenAI text-embedding-3-small: 1536 dimensions)
    # Using pgvector for semantic search
    embedding: Mapped[Vector] = mapped_column(
        Vector(1536), nullable=False, comment="Question+Answer combined embedding vector"
    )

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.utcnow,
    )

    # Indexes for efficient search
    __table_args__ = (
        # HNSW index for cosine similarity search (pgvector)
        Index(
            "idx_copd_kb_embedding_cosine",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        # B-tree index for category filtering
        Index("idx_copd_kb_category", "category"),
        # Schema configuration
        {"schema": settings.get_db_schema()},
    )

    def __repr__(self) -> str:
        return f"<COPDKnowledgeBase(id={self.id}, category={self.category}, question={self.question[:50]}...)>"
