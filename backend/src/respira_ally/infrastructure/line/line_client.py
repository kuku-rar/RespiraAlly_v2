"""
LINE Messaging API Client - Hybrid Reply + Push Strategy

Author: Claude Code
Created: 2025-10-31
Purpose: Optimize cost by prioritizing Reply API (free) over Push API (paid)

Key Features:
- Reply API for fast responses (< 30s, FREE)
- Push API fallback for slow responses (> 30s, PAID)
- Automatic token expiry detection
- Rate limiting and retry mechanism
"""

import asyncio
import time
from typing import Any, Optional
from enum import Enum

import httpx
import structlog

logger = structlog.get_logger()


class LineAPIError(Exception):
    """LINE API 錯誤基類"""
    pass


class LineReplyTokenExpiredError(LineAPIError):
    """Reply Token 已過期"""
    pass


class LineRateLimitError(LineAPIError):
    """達到 LINE API 限流"""
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded, retry after {retry_after}s")


class MessageSendMethod(Enum):
    """訊息發送方式"""
    REPLY = "reply"  # 免費，但需在30秒內
    PUSH = "push"  # 付費，無時間限制


class LineMessagingClient:
    """
    LINE Messaging API 客戶端 - 智能混合策略

    Cost Optimization Strategy:
    1. Try Reply API first (FREE) if reply_token available and < 30s
    2. Fallback to Push API (PAID) if reply_token expired or > 30s
    3. Track usage metrics for cost monitoring
    """

    def __init__(
        self,
        access_token: str,
        base_url: str = "https://api.line.me/v2/bot",
        timeout: float = 10.0,
        max_retries: int = 3,
    ):
        self.access_token = access_token
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries

        # HTTP Client with connection pooling
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        )

        # Cost tracking
        self._reply_count = 0
        self._push_count = 0

    async def send_text_message(
        self,
        text: str,
        reply_token: Optional[str] = None,
        user_id: Optional[str] = None,
        notification_disabled: bool = False,
    ) -> tuple[MessageSendMethod, dict[str, Any]]:
        """
        智能發送訊息 - 優先使用 Reply API（免費）

        Args:
            text: 訊息內容
            reply_token: Reply Token（如果有的話）
            user_id: LINE 使用者 ID（Reply Token 失效時使用）
            notification_disabled: 是否禁用通知

        Returns:
            (send_method, response) - 實際使用的發送方式和 API 回應

        Raises:
            ValueError: 如果 reply_token 和 user_id 都沒有提供
            LineAPIError: LINE API 錯誤
        """
        if not reply_token and not user_id:
            raise ValueError("Must provide either reply_token or user_id")

        # Strategy: Try Reply API first (FREE)
        if reply_token:
            try:
                response = await self.reply_message(
                    reply_token=reply_token,
                    text=text,
                    notification_disabled=notification_disabled,
                )
                self._reply_count += 1
                logger.info(
                    "✅ Message sent via Reply API (FREE)",
                    method="reply",
                    reply_count=self._reply_count,
                )
                return MessageSendMethod.REPLY, response

            except LineReplyTokenExpiredError:
                logger.warning(
                    "⚠️ Reply token expired, fallback to Push API (PAID)",
                    reply_token=reply_token[:10] + "...",
                )
                # Fallback to Push API below

        # Fallback: Use Push API (PAID)
        if not user_id:
            raise ValueError("user_id required for Push API fallback")

        response = await self.push_text_message(
            user_id=user_id,
            text=text,
            notification_disabled=notification_disabled,
        )
        self._push_count += 1
        logger.info(
            "💰 Message sent via Push API (PAID)",
            method="push",
            push_count=self._push_count,
            cost_ratio=f"{self._push_count}/{self._reply_count + self._push_count}",
        )
        return MessageSendMethod.PUSH, response

    async def reply_message(
        self,
        reply_token: str,
        text: str,
        notification_disabled: bool = False,
    ) -> dict[str, Any]:
        """
        使用 Reply API 發送訊息（免費，但需在30秒內）

        Args:
            reply_token: Reply Token from webhook
            text: 訊息內容
            notification_disabled: 是否禁用通知

        Returns:
            LINE API 回應

        Raises:
            LineReplyTokenExpiredError: Reply Token 已過期
            LineAPIError: 其他 LINE API 錯誤
        """
        if len(text) > 5000:
            raise ValueError(f"Text too long: {len(text)} > 5000 chars")

        payload = {
            "replyToken": reply_token,
            "messages": [{"type": "text", "text": text}],
            "notificationDisabled": notification_disabled,
        }

        try:
            return await self._send_with_retry(
                method="POST",
                endpoint="/message/reply",
                json=payload,
            )
        except LineAPIError as e:
            # Check if error is due to expired token
            if "invalid reply token" in str(e).lower():
                raise LineReplyTokenExpiredError(f"Reply token expired: {reply_token[:10]}...")
            raise

    async def push_text_message(
        self,
        user_id: str,
        text: str,
        notification_disabled: bool = False,
    ) -> dict[str, Any]:
        """
        使用 Push API 發送訊息（付費，無時間限制）

        Args:
            user_id: LINE 使用者 ID
            text: 訊息內容
            notification_disabled: 是否禁用通知

        Returns:
            LINE API 回應

        Raises:
            ValueError: 無效的參數
            LineAPIError: LINE API 錯誤
        """
        if not user_id.startswith("U"):
            raise ValueError(f"Invalid LINE user_id: {user_id}")

        if len(text) > 5000:
            raise ValueError(f"Text too long: {len(text)} > 5000 chars")

        payload = {
            "to": user_id,
            "messages": [{"type": "text", "text": text}],
            "notificationDisabled": notification_disabled,
        }

        return await self._send_with_retry(
            method="POST",
            endpoint="/message/push",
            json=payload,
        )

    async def _send_with_retry(
        self,
        method: str,
        endpoint: str,
        json: dict[str, Any],
    ) -> dict[str, Any]:
        """發送 HTTP 請求（含重試機制）"""
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                response = await self._client.request(method, endpoint, json=json)

                # Success
                if response.status_code == 200:
                    return response.json() if response.text else {}

                # Handle error responses
                await self._handle_error_response(response, attempt)

            except httpx.TimeoutException as e:
                last_exception = e
                logger.warning(
                    f"⏱️ Request timeout (attempt {attempt + 1}/{self.max_retries})",
                    endpoint=endpoint,
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise LineAPIError(f"Request timeout after {self.max_retries} retries")

            except Exception as e:
                last_exception = e
                logger.error(f"❌ Unexpected error: {e}", endpoint=endpoint)
                raise LineAPIError(f"Unexpected error: {e}")

        raise LineAPIError(f"Max retries exceeded: {last_exception}")

    async def _handle_error_response(self, response: httpx.Response, attempt: int):
        """處理 LINE API 錯誤回應"""
        status = response.status_code
        body = response.json() if response.text else {}
        error_message = body.get("message", "Unknown error")

        # Rate limiting (429)
        if status == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            logger.warning(
                f"⚠️ Rate limit hit (attempt {attempt + 1})",
                retry_after=retry_after,
            )
            raise LineRateLimitError(retry_after)

        # Invalid reply token (400)
        if status == 400 and "invalid reply token" in error_message.lower():
            raise LineReplyTokenExpiredError(error_message)

        # Other errors
        error = LineAPIError(
            f"LINE API error: {status} - {error_message}"
        )
        logger.error(
            f"❌ LINE API error",
            status=status,
            message=error_message,
            body=body,
        )
        raise error

    async def close(self):
        """關閉 HTTP 客戶端"""
        await self._client.aclose()

    def get_usage_stats(self) -> dict[str, Any]:
        """取得使用統計（用於成本監控）"""
        total = self._reply_count + self._push_count
        reply_ratio = (self._reply_count / total * 100) if total > 0 else 0

        return {
            "reply_count": self._reply_count,
            "push_count": self._push_count,
            "total_count": total,
            "reply_ratio_percent": round(reply_ratio, 2),
            "estimated_monthly_cost_twd": self._push_count * 0.4,  # 假設 0.4 TWD/條
        }


# 使用範例
async def main():
    client = LineMessagingClient(access_token="YOUR_CHANNEL_ACCESS_TOKEN")

    # 情境1: 快速回應（使用 Reply API - 免費）
    method, response = await client.send_text_message(
        text="您好！請問有什麼可以幫助您的？",
        reply_token="REPLY_TOKEN_FROM_WEBHOOK",
        user_id="U1234567890abcdef",  # Fallback user_id
    )
    print(f"Sent via {method.value}: {response}")

    # 情境2: Reply Token 過期（自動降級到 Push API - 付費）
    method, response = await client.send_text_message(
        text="您的提醒已設定成功！",
        reply_token="EXPIRED_TOKEN",
        user_id="U1234567890abcdef",
    )
    print(f"Sent via {method.value}: {response}")

    # 查看成本統計
    stats = client.get_usage_stats()
    print(f"Usage stats: {stats}")

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
