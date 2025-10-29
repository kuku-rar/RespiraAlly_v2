"""
COPD Knowledge RAG Tool - pgvector Semantic Search

使用 pgvector + OpenAI embeddings 進行 COPD 知識檢索
"""

import os
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from respira_ally.core.config import settings
from respira_ally.domain.repositories.knowledge_repository import KnowledgeRepository
from respira_ally.infrastructure.database.session import AsyncSessionLocal
from respira_ally.infrastructure.repository_impls.pgvector_knowledge_repository import (
    PgvectorKnowledgeRepository,
)


class COPDKnowledgeInput(BaseModel):
    """COPDKnowledgeTool 輸入參數"""

    query: str = Field(..., description="用戶的問題或查詢")
    top_k: int = Field(default=3, description="返回最相關的前 K 個文檔")


class COPDKnowledgeTool(BaseTool):
    """
    COPD 知識檢索工具（RAG）

    使用語義搜索從 COPD 知識庫中找到最相關的 Q&A
    """

    name: str = "search_copd_knowledge"
    description: str = (
        "從 COPD 知識庫中搜尋相關資訊。當需要客觀的健康知識"
        "（疾病概念、症狀、風險、就醫時機、生活衛教等）時使用此工具。"
        "返回最相關的 Q&A 內容。"
    )
    args_schema: Type[BaseModel] = COPDKnowledgeInput

    def _run(self, query: str, top_k: int = 3) -> str:
        """
        執行知識檢索

        Args:
            query: 用戶查詢
            top_k: 返回前 K 個最相關文檔

        Returns:
            格式化的知識檢索結果
        """
        try:
            # 使用 asyncio.run 在同步環境中執行異步代碼
            import asyncio

            return asyncio.run(self._async_search(query, top_k))

        except Exception as e:
            print(f"[COPDKnowledgeTool Error] {e}")
            return (
                "❌ 知識檢索失敗：無法連接到知識庫。\n"
                "請稍後再試，或直接詢問您的問題。"
            )

    async def _async_search(self, query: str, top_k: int) -> str:
        """
        異步執行知識檢索

        Args:
            query: 用戶查詢
            top_k: 返回前 K 個最相關文檔

        Returns:
            格式化的知識檢索結果
        """
        async with AsyncSessionLocal() as session:
            repository: KnowledgeRepository = PgvectorKnowledgeRepository(session)

            # 語義搜索
            documents = await repository.search(query=query, top_k=top_k)

            if not documents:
                return (
                    "📚 知識庫中沒有找到相關資訊。\n"
                    "您可以諮詢醫療專業人員以獲得更準確的建議。"
                )

            # 格式化結果
            result_parts = ["📚 COPD 知識庫檢索結果：\n"]

            for i, doc in enumerate(documents, 1):
                # 相似度分數轉為百分比
                score_pct = doc.score * 100

                result_parts.append(f"\n【結果 {i}】（相似度：{score_pct:.1f}%）")
                result_parts.append(f"類別：{doc.category or '未分類'}")
                result_parts.append(f"\n{doc.content}")

                # 如果有關鍵詞，也顯示
                if doc.keywords:
                    result_parts.append(f"\n🔖 關鍵詞：{doc.keywords}")

                # 如果有注意事項，也顯示
                if doc.metadata.get("notes"):
                    result_parts.append(f"\n⚠️ 注意事項：{doc.metadata['notes']}")

                result_parts.append("\n" + "-" * 50)

            # 添加使用說明
            result_parts.append(
                "\n💡 使用提示："
                "\n- 請根據以上資料理解重點，再用自己的話回覆用戶"
                "\n- 如果資料與用戶問題不完全相符，可以適當調整或補充"
                "\n- 請避免直接複製貼上，保持對話的自然性"
            )

            return "\n".join(result_parts)
