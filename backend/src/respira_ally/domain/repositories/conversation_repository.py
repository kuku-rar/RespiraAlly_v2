"""
Conversation Repository Interface - 對話歷史存儲接口
"""
from abc import ABC, abstractmethod
from uuid import UUID

from respira_ally.domain.value_objects.conversation import Message


class ConversationRepository(ABC):
    """
    對話歷史存儲接口 (DDD Repository Pattern)

    職責：
    - 管理用戶對話歷史（5分鐘 session）
    - 提供歷史消息檢索
    - 支援多輪對話上下文
    """

    @abstractmethod
    async def get_history(
        self, user_id: UUID | str, limit: int = 10
    ) -> list[Message]:
        """
        獲取用戶對話歷史

        Args:
            user_id: 用戶 ID
            limit: 最多返回的訊息數量（預設10條）

        Returns:
            訊息列表（按時間正序排列，最舊的在前）
        """
        pass

    @abstractmethod
    async def save_message(self, user_id: UUID | str, message: Message) -> None:
        """
        保存單一訊息到對話歷史

        Args:
            user_id: 用戶 ID
            message: 訊息值對象
        """
        pass

    @abstractmethod
    async def clear_history(self, user_id: UUID | str) -> None:
        """
        清除用戶對話歷史

        Args:
            user_id: 用戶 ID
        """
        pass

    @abstractmethod
    async def get_history_as_openai_messages(
        self, user_id: UUID | str, limit: int = 10
    ) -> list[dict]:
        """
        獲取對話歷史並轉換為 OpenAI Chat API 格式

        Args:
            user_id: 用戶 ID
            limit: 最多返回的訊息數量

        Returns:
            OpenAI 格式的訊息列表 [{"role": "user", "content": "..."}, ...]
        """
        pass
