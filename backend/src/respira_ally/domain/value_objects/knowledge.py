"""
Knowledge Value Objects - 知識庫相關值對象
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    """
    知識文檔值對象 (Immutable)

    用於表示從知識庫檢索的文檔
    """

    content: str
    metadata: dict
    score: float  # 相似度分數 (0-1, 越高越相似)

    def __post_init__(self):
        """驗證數據有效性"""
        if not 0 <= self.score <= 1:
            raise ValueError(f"Score must be between 0 and 1, got {self.score}")

    @property
    def category(self) -> str | None:
        """從 metadata 取得類別"""
        return self.metadata.get("category")

    @property
    def keywords(self) -> str | None:
        """從 metadata 取得關鍵詞"""
        return self.metadata.get("keywords")

    def to_context_string(self) -> str:
        """
        轉換為可用於 LLM context 的字串

        Returns:
            格式化的知識內容字串
        """
        parts = [self.content]

        if self.category:
            parts.append(f"[類別: {self.category}]")

        if self.keywords:
            parts.append(f"[關鍵詞: {self.keywords}]")

        return "\n".join(parts)
