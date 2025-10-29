"""
Conversation Value Objects - 對話相關值對象
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """訊息角色"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass(frozen=True)
class Message:
    """
    訊息值對象 (Immutable)

    用於表示對話中的單一訊息
    """

    role: MessageRole
    content: str
    timestamp: datetime

    def to_dict(self) -> dict:
        """轉換為字典格式（用於 JSON 序列化）"""
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """從字典創建 Message"""
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )

    def to_openai_format(self) -> dict:
        """轉換為 OpenAI Chat API 格式"""
        return {"role": self.role.value, "content": self.content}
