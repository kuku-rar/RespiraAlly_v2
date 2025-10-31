"""
Message Classifier - 判斷訊息是否需要 Agent 深度分析

Author: Claude Code
Created: 2025-10-31
Purpose: Optimize LINE Reply API usage by classifying message complexity
"""

import re
from enum import Enum
from typing import Optional


class MessageType(Enum):
    """訊息類型分類"""
    GREETING = "greeting"  # 問候語（"你好"、"早安"）
    FAQ = "faq"  # 常見問題（"如何使用"、"什麼是COPD"）
    COMMAND = "command"  # 指令（"查看任務"、"今日提醒"）
    COMPLEX_QUERY = "complex_query"  # 需要 Agent 推理的複雜問題
    UNKNOWN = "unknown"  # 未知類型


class MessageComplexity(Enum):
    """訊息複雜度"""
    SIMPLE = "simple"  # 可用 Reply API（< 5秒）
    MODERATE = "moderate"  # 可能用 Reply API（< 25秒）
    COMPLEX = "complex"  # 必須用 Push API（> 30秒）


class MessageClassifier:
    """訊息分類器 - 決定使用 Reply 或 Push API"""

    # 簡單問候語模式
    GREETING_PATTERNS = [
        r"^(你好|嗨|hi|hello|早安|午安|晚安|哈囉)[\s!！]*$",
    ]

    # FAQ 關鍵字
    FAQ_KEYWORDS = [
        "什麼是", "如何", "怎麼", "為什麼", "是什麼",
        "COPD", "慢阻肺", "肺部", "呼吸", "氧氣",
        "用藥", "吸入器", "症狀", "治療",
    ]

    # 指令關鍵字
    COMMAND_KEYWORDS = [
        "查看", "檢視", "顯示", "列出", "查詢",
        "任務", "提醒", "警報", "記錄", "歷史",
    ]

    def __init__(self):
        self._greeting_regex = re.compile(
            "|".join(self.GREETING_PATTERNS),
            re.IGNORECASE
        )

    def classify_message_type(self, text: str) -> MessageType:
        """分類訊息類型"""
        text_lower = text.strip().lower()

        # 1. 檢查是否為問候語
        if self._greeting_regex.match(text_lower):
            return MessageType.GREETING

        # 2. 檢查是否為指令
        if any(keyword in text_lower for keyword in self.COMMAND_KEYWORDS):
            return MessageType.COMMAND

        # 3. 檢查是否為 FAQ
        if any(keyword in text_lower for keyword in self.FAQ_KEYWORDS):
            return MessageType.FAQ

        # 4. 檢查長度（長文本通常需要深度分析）
        if len(text) > 100:
            return MessageType.COMPLEX_QUERY

        # 5. 預設為需要 Agent 處理的複雜查詢
        return MessageType.COMPLEX_QUERY

    def classify_complexity(self, text: str, message_type: Optional[MessageType] = None) -> MessageComplexity:
        """判斷訊息複雜度"""
        if message_type is None:
            message_type = self.classify_message_type(text)

        # 簡單類型：問候、簡單指令
        if message_type in [MessageType.GREETING, MessageType.COMMAND]:
            return MessageComplexity.SIMPLE

        # 中等複雜度：FAQ
        if message_type == MessageType.FAQ:
            return MessageComplexity.MODERATE

        # 複雜查詢：需要 Agent 推理
        return MessageComplexity.COMPLEX

    def should_use_reply_api(self, text: str) -> tuple[bool, str]:
        """
        決定是否可以使用 Reply API

        Returns:
            (should_use_reply, reason)
        """
        message_type = self.classify_message_type(text)
        complexity = self.classify_complexity(text, message_type)

        if complexity == MessageComplexity.SIMPLE:
            return True, f"Simple {message_type.value}, use Reply API (free)"

        if complexity == MessageComplexity.MODERATE:
            return True, f"Moderate {message_type.value}, try Reply API with 25s timeout"

        return False, f"Complex {message_type.value}, must use Push API"


# 使用範例
if __name__ == "__main__":
    classifier = MessageClassifier()

    test_messages = [
        "你好",
        "查看今天的任務",
        "什麼是COPD？",
        "我最近呼吸困難，而且咳嗽有痰，該怎麼辦？我已經用藥了但是效果不好...",
    ]

    for msg in test_messages:
        msg_type = classifier.classify_message_type(msg)
        complexity = classifier.classify_complexity(msg, msg_type)
        should_reply, reason = classifier.should_use_reply_api(msg)

        print(f"訊息: {msg}")
        print(f"  類型: {msg_type.value}")
        print(f"  複雜度: {complexity.value}")
        print(f"  決策: {reason}")
        print()
