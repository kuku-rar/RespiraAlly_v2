"""
Redis Conversation Repository Implementation
"""
import json
from datetime import datetime
from uuid import UUID

from redis.asyncio import Redis

from respira_ally.domain.repositories.conversation_repository import (
    ConversationRepository,
)
from respira_ally.domain.value_objects.conversation import Message, MessageRole


class RedisConversationRepository(ConversationRepository):
    """
    Redis 對話歷史存儲實現

    數據結構：
    - Key: "conv:{user_id}"
    - Type: List (LPUSH/LRANGE)
    - TTL: 300 seconds (5 minutes)
    """

    def __init__(self, redis_client: Redis, ttl: int = 300):
        """
        Args:
            redis_client: Redis 客戶端實例
            ttl: 對話歷史過期時間（秒），預設5分鐘
        """
        self.redis = redis_client
        self.ttl = ttl

    def _get_key(self, user_id: UUID | str) -> str:
        """生成 Redis key"""
        return f"conv:{str(user_id)}"

    async def get_history(
        self, user_id: UUID | str, limit: int = 10
    ) -> list[Message]:
        """
        獲取用戶對話歷史

        從 Redis List 中取最後 N 條訊息（LRANGE -limit -1）
        """
        key = self._get_key(user_id)
        messages_json = await self.redis.lrange(key, -limit, -1)

        messages = []
        for msg_json in messages_json:
            msg_dict = json.loads(msg_json)
            messages.append(Message.from_dict(msg_dict))

        return messages

    async def save_message(self, user_id: UUID | str, message: Message) -> None:
        """
        保存訊息到對話歷史

        使用 RPUSH 追加到列表尾部，並更新 TTL
        """
        key = self._get_key(user_id)
        msg_json = json.dumps(message.to_dict())

        # 追加訊息並設置過期時間
        await self.redis.rpush(key, msg_json)
        await self.redis.expire(key, self.ttl)

    async def clear_history(self, user_id: UUID | str) -> None:
        """清除對話歷史"""
        key = self._get_key(user_id)
        await self.redis.delete(key)

    async def get_history_as_openai_messages(
        self, user_id: UUID | str, limit: int = 10
    ) -> list[dict]:
        """
        獲取對話歷史並轉換為 OpenAI Chat API 格式

        Returns:
            [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
        """
        messages = await self.get_history(user_id, limit)
        return [msg.to_openai_format() for msg in messages]

    async def save_user_message(self, user_id: UUID | str, content: str) -> None:
        """
        便捷方法：保存用戶訊息

        Args:
            user_id: 用戶 ID
            content: 訊息內容
        """
        message = Message(
            role=MessageRole.USER, content=content, timestamp=datetime.utcnow()
        )
        await self.save_message(user_id, message)

    async def save_assistant_message(
        self, user_id: UUID | str, content: str
    ) -> None:
        """
        便捷方法：保存助手回覆

        Args:
            user_id: 用戶 ID
            content: 回覆內容
        """
        message = Message(
            role=MessageRole.ASSISTANT, content=content, timestamp=datetime.utcnow()
        )
        await self.save_message(user_id, message)
