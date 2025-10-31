"""
Unit Tests for LineMessagingClient

Test Coverage:
- Reply API success (FREE)
- Push API success (PAID)
- Hybrid strategy (Reply → Push fallback)
- Error handling (expired token, rate limit, API errors)
- Cost tracking
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx

from respira_ally.infrastructure.line.line_client import (
    LineMessagingClient,
    LineAPIError,
    LineReplyTokenExpiredError,
    LineRateLimitError,
    MessageSendMethod,
)


@pytest.fixture
def line_client():
    """Create LineMessagingClient instance for testing"""
    return LineMessagingClient(access_token="test_access_token")


@pytest.fixture
def mock_httpx_response():
    """Create mock httpx.Response"""

    def _create_mock(status_code: int, json_data: dict = None, headers: dict = None):
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = status_code
        mock_response.json.return_value = json_data or {}
        mock_response.text = "mock response"
        mock_response.headers = headers or {}
        return mock_response

    return _create_mock


class TestReplyAPISuccess:
    """Test Reply API success scenarios (FREE)"""

    @pytest.mark.asyncio
    async def test_reply_message_success(self, line_client, mock_httpx_response):
        """Test successful Reply API call"""
        mock_response = mock_httpx_response(200, {"status": "ok"})

        with patch.object(
            line_client._client, "request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            result = await line_client.reply_message(
                reply_token="test_reply_token", text="測試訊息"
            )

            assert result["status"] == "ok"
            mock_request.assert_called_once()
            call_kwargs = mock_request.call_args.kwargs
            assert call_kwargs["json"]["replyToken"] == "test_reply_token"
            assert call_kwargs["json"]["messages"][0]["text"] == "測試訊息"

    @pytest.mark.asyncio
    async def test_send_text_message_with_reply_token(
        self, line_client, mock_httpx_response
    ):
        """Test hybrid strategy - uses Reply API when token available"""
        mock_response = mock_httpx_response(200, {})

        with patch.object(
            line_client._client, "request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            method, result = await line_client.send_text_message(
                text="測試",
                reply_token="valid_token",
                user_id="U1234567890abcdef",
            )

            assert method == MessageSendMethod.REPLY  # Should use FREE Reply API
            assert line_client._reply_count == 1
            assert line_client._push_count == 0


class TestPushAPISuccess:
    """Test Push API success scenarios (PAID)"""

    @pytest.mark.asyncio
    async def test_push_text_message_success(self, line_client, mock_httpx_response):
        """Test successful Push API call"""
        mock_response = mock_httpx_response(200, {"status": "ok"})

        with patch.object(
            line_client._client, "request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            result = await line_client.push_text_message(
                user_id="U1234567890abcdef", text="測試訊息"
            )

            assert result["status"] == "ok"
            call_kwargs = mock_request.call_args.kwargs
            assert call_kwargs["json"]["to"] == "U1234567890abcdef"
            assert call_kwargs["json"]["messages"][0]["text"] == "測試訊息"

    @pytest.mark.asyncio
    async def test_send_text_message_without_reply_token(
        self, line_client, mock_httpx_response
    ):
        """Test hybrid strategy - uses Push API when no reply token"""
        mock_response = mock_httpx_response(200, {})

        with patch.object(
            line_client._client, "request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            method, result = await line_client.send_text_message(
                text="測試", user_id="U1234567890abcdef"
            )

            assert method == MessageSendMethod.PUSH  # Should use PAID Push API
            assert line_client._reply_count == 0
            assert line_client._push_count == 1


class TestHybridStrategyFallback:
    """Test hybrid strategy - Reply → Push fallback"""

    @pytest.mark.asyncio
    async def test_fallback_to_push_when_reply_token_expired(
        self, line_client, mock_httpx_response
    ):
        """Test fallback to Push API when Reply Token expires"""
        # First call (Reply API) returns expired token error
        reply_error_response = mock_httpx_response(
            400, {"message": "Invalid reply token"}
        )
        # Second call (Push API) succeeds
        push_success_response = mock_httpx_response(200, {"status": "ok"})

        with patch.object(
            line_client._client, "request", new_callable=AsyncMock
        ) as mock_request:
            # Mock two calls: Reply fails, Push succeeds
            mock_request.side_effect = [reply_error_response, push_success_response]

            method, result = await line_client.send_text_message(
                text="測試",
                reply_token="expired_token",
                user_id="U1234567890abcdef",
            )

            # Should fallback to Push API (PAID)
            assert method == MessageSendMethod.PUSH
            assert line_client._reply_count == 0  # Reply failed
            assert line_client._push_count == 1  # Push succeeded
            assert mock_request.call_count == 2  # Two API calls


class TestErrorHandling:
    """Test error handling scenarios"""

    @pytest.mark.asyncio
    async def test_reply_token_expired_error(self, line_client, mock_httpx_response):
        """Test LineReplyTokenExpiredError is raised"""
        mock_response = mock_httpx_response(
            400, {"message": "Invalid reply token"}
        )

        with patch.object(
            line_client._client, "request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            with pytest.raises(LineReplyTokenExpiredError):
                await line_client.reply_message(
                    reply_token="expired_token", text="測試"
                )

    @pytest.mark.asyncio
    async def test_rate_limit_error(self, line_client, mock_httpx_response):
        """Test LineRateLimitError is raised"""
        mock_response = mock_httpx_response(
            429, {"message": "Rate limit exceeded"}, headers={"Retry-After": "60"}
        )

        with patch.object(
            line_client._client, "request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            with pytest.raises(LineRateLimitError) as exc_info:
                await line_client.push_text_message(
                    user_id="U1234567890abcdef", text="測試"
                )

            assert exc_info.value.retry_after == 60

    @pytest.mark.asyncio
    async def test_generic_api_error(self, line_client, mock_httpx_response):
        """Test generic LineAPIError is raised"""
        mock_response = mock_httpx_response(500, {"message": "Internal server error"})

        with patch.object(
            line_client._client, "request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            with pytest.raises(LineAPIError):
                await line_client.push_text_message(
                    user_id="U1234567890abcdef", text="測試"
                )

    @pytest.mark.asyncio
    async def test_timeout_error_with_retry(self, line_client):
        """Test timeout error with retry mechanism"""
        with patch.object(
            line_client._client, "request", new_callable=AsyncMock
        ) as mock_request:
            # Mock timeout error for all retries
            mock_request.side_effect = httpx.TimeoutException("Request timeout")

            with pytest.raises(LineAPIError) as exc_info:
                await line_client.push_text_message(
                    user_id="U1234567890abcdef", text="測試"
                )

            # Should retry max_retries times (default 3)
            assert mock_request.call_count == line_client.max_retries
            assert "timeout" in str(exc_info.value).lower()


class TestInputValidation:
    """Test input validation"""

    @pytest.mark.asyncio
    async def test_invalid_user_id(self, line_client):
        """Test invalid user_id raises ValueError"""
        with pytest.raises(ValueError, match="Invalid LINE user_id"):
            await line_client.push_text_message(user_id="invalid_id", text="測試")

    @pytest.mark.asyncio
    async def test_text_too_long(self, line_client):
        """Test text > 5000 chars raises ValueError"""
        long_text = "a" * 5001
        with pytest.raises(ValueError, match="Text too long"):
            await line_client.push_text_message(
                user_id="U1234567890abcdef", text=long_text
            )

    @pytest.mark.asyncio
    async def test_missing_reply_token_and_user_id(self, line_client):
        """Test missing both reply_token and user_id raises ValueError"""
        with pytest.raises(
            ValueError, match="Must provide either reply_token or user_id"
        ):
            await line_client.send_text_message(text="測試")


class TestCostTracking:
    """Test cost tracking functionality"""

    @pytest.mark.asyncio
    async def test_cost_stats_initial_state(self, line_client):
        """Test initial cost statistics"""
        stats = line_client.get_usage_stats()

        assert stats["reply_count"] == 0
        assert stats["push_count"] == 0
        assert stats["total_count"] == 0
        assert stats["reply_ratio_percent"] == 0
        assert stats["estimated_monthly_cost_twd"] == 0

    @pytest.mark.asyncio
    async def test_cost_stats_after_mixed_usage(
        self, line_client, mock_httpx_response
    ):
        """Test cost statistics after mixed Reply and Push usage"""
        mock_response = mock_httpx_response(200, {})

        with patch.object(
            line_client._client, "request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            # 8 Reply API calls (FREE)
            for _ in range(8):
                await line_client.send_text_message(
                    text="測試", reply_token="valid_token", user_id="U123"
                )

            # 2 Push API calls (PAID)
            for _ in range(2):
                await line_client.send_text_message(text="測試", user_id="U123")

            stats = line_client.get_usage_stats()

            assert stats["reply_count"] == 8
            assert stats["push_count"] == 2
            assert stats["total_count"] == 10
            assert stats["reply_ratio_percent"] == 80.0  # 8/10 = 80%
            assert stats["estimated_monthly_cost_twd"] == 0.8  # 2 * 0.4 = 0.8 TWD

    @pytest.mark.asyncio
    async def test_cost_optimization_target_85_percent(
        self, line_client, mock_httpx_response
    ):
        """Test cost optimization target: 85% Reply usage"""
        mock_response = mock_httpx_response(200, {})

        with patch.object(
            line_client._client, "request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_response

            # Simulate 85% Reply, 15% Push
            for _ in range(85):
                await line_client.send_text_message(
                    text="測試", reply_token="valid_token", user_id="U123"
                )

            for _ in range(15):
                await line_client.send_text_message(text="測試", user_id="U123")

            stats = line_client.get_usage_stats()

            assert stats["reply_ratio_percent"] == 85.0
            assert stats["push_count"] == 15
            # 15 * 0.4 = 6 TWD for 100 messages
            assert stats["estimated_monthly_cost_twd"] == 6.0


class TestRetryMechanism:
    """Test retry mechanism with exponential backoff"""

    @pytest.mark.asyncio
    async def test_retry_on_timeout_then_success(
        self, line_client, mock_httpx_response
    ):
        """Test retry succeeds on second attempt"""
        success_response = mock_httpx_response(200, {"status": "ok"})

        with patch.object(
            line_client._client, "request", new_callable=AsyncMock
        ) as mock_request:
            # First call fails, second succeeds
            mock_request.side_effect = [
                httpx.TimeoutException("timeout"),
                success_response,
            ]

            result = await line_client.push_text_message(
                user_id="U1234567890abcdef", text="測試"
            )

            assert result["status"] == "ok"
            assert mock_request.call_count == 2  # Retried once


@pytest.mark.asyncio
async def test_client_close(line_client):
    """Test client cleanup"""
    with patch.object(
        line_client._client, "aclose", new_callable=AsyncMock
    ) as mock_close:
        await line_client.close()
        mock_close.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
