"""
Knowledge Repository Interface - COPD 知識庫檢索接口
"""
from abc import ABC, abstractmethod

from respira_ally.domain.value_objects.knowledge import Document


class KnowledgeRepository(ABC):
    """
    COPD 知識庫檢索接口 (DDD Repository Pattern)

    職責：
    - 提供語義相似度搜尋（RAG）
    - 支援類別篩選
    - 返回相關的 COPD 知識文檔
    """

    @abstractmethod
    async def search(
        self, query: str, top_k: int = 3, category: str | None = None
    ) -> list[Document]:
        """
        語義相似度搜尋

        Args:
            query: 搜尋查詢文本
            top_k: 返回最相關的前 K 個文檔（預設3個）
            category: 可選的類別篩選（如 "生活品質與運動", "藥物治療"）

        Returns:
            相關文檔列表（按相似度分數排序，最相關的在前）
        """
        pass

    @abstractmethod
    async def search_by_keywords(
        self, keywords: list[str], top_k: int = 3
    ) -> list[Document]:
        """
        關鍵詞搜尋

        Args:
            keywords: 關鍵詞列表
            top_k: 返回最相關的前 K 個文檔

        Returns:
            相關文檔列表
        """
        pass

    @abstractmethod
    async def get_all_categories(self) -> list[str]:
        """
        獲取所有知識庫類別

        Returns:
            類別列表（去重排序）
        """
        pass
