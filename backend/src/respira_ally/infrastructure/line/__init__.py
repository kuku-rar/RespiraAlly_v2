"""
LINE Messaging API Infrastructure

This module provides LINE Bot integration with intelligent cost optimization.

Key Components:
- LineMessagingClient: Hybrid Reply + Push API client
- Automatic cost tracking and optimization
- Reply API prioritization (FREE)
- Push API fallback (PAID)

Usage:
    from respira_ally.infrastructure.line import LineMessagingClient

    client = LineMessagingClient(access_token="YOUR_TOKEN")
    method, response = await client.send_text_message(
        text="Hello",
        reply_token="REPLY_TOKEN",  # If available
        user_id="U1234567890",      # For Push API fallback
    )

Cost Optimization:
    The client automatically optimizes costs by:
    1. Trying Reply API first (FREE, < 30s)
    2. Falling back to Push API if needed (PAID)
    3. Tracking usage statistics for monitoring
"""

from respira_ally.infrastructure.line.line_client import (
    LineMessagingClient,
    LineAPIError,
    LineReplyTokenExpiredError,
    LineRateLimitError,
    MessageSendMethod,
)

__all__ = [
    "LineMessagingClient",
    "LineAPIError",
    "LineReplyTokenExpiredError",
    "LineRateLimitError",
    "MessageSendMethod",
]
