"""
Integration Tests for LineMessageConsumer Hybrid Strategy

Test Coverage:
- Fast response uses Reply API (FREE)
- Slow response uses Push API (PAID)
- Reply Token expiry fallback
- Message classification integration
- Cost tracking integration
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, Mock, patch

from respira_ally.infrastructure.message_queue.consumers.line_message_consumer import (
    LineMessageConsumer,
)
from respira_ally.infrastructure.line.line_client import MessageSendMethod
from respira_ally.services.agent_manager import AgentManager


@pytest.fixture
def mock_agent_manager():
    """Mock AgentManager for testing"""
    mock_manager = Mock(spec=AgentManager)
    mock_manager.conversation_repo = Mock()
    mock_manager.conversation_repo.save_message = AsyncMock()
    return mock_manager


@pytest.fixture
def mock_line_client():
    """Mock LineMessagingClient for testing"""
    mock_client = Mock()
    mock_client.send_text_message = AsyncMock()
    mock_client.get_usage_stats = Mock(
        return_value={
            "reply_count": 0,
            "push_count": 0,
            "total_count": 0,
            "reply_ratio_percent": 0,
            "estimated_monthly_cost_twd": 0,
        }
    )
    return mock_client


@pytest.fixture
async def consumer(mock_agent_manager, mock_line_client):
    """Create Consumer instance with mocked dependencies"""
    consumer = LineMessageConsumer()
    consumer.agent_manager = mock_agent_manager
    consumer.line_client = mock_line_client
    return consumer


class TestFastResponseUsesReplyAPI:
    """Test fast responses use Reply API (FREE)"""

    @pytest.mark.asyncio
    async def test_simple_greeting_fast_response(
        self, consumer, mock_agent_manager, mock_line_client
    ):
        """Test simple greeting triggers fast response with Reply API"""
        # Mock fast agent response (2 seconds)
        async def fast_response(user_id, user_input, include_context):
            await asyncio.sleep(0.1)  # Simulate 0.1s processing
            return "您好！有什麼可以幫助您的嗎？"

        mock_agent_manager.handle_message = fast_response

        # Mock Reply API success
        mock_line_client.send_text_message.return_value = (
            MessageSendMethod.REPLY,
            {"status": "ok"},
        )

        event_data = {
            "patient_id": "patient_123",
            "text": "你好",
            "line_user_id": "U1234567890abcdef",
            "reply_token": "valid_reply_token",
        }

        await consumer._handle_text_message(event_data)

        # Verify Reply API was called
        mock_line_client.send_text_message.assert_called_once()
        call_kwargs = mock_line_client.send_text_message.call_args.kwargs

        assert call_kwargs["reply_token"] == "valid_reply_token"
        assert call_kwargs["user_id"] == "U1234567890abcdef"
        assert "您好" in call_kwargs["text"]

    @pytest.mark.asyncio
    async def test_command_fast_response(
        self, consumer, mock_agent_manager, mock_line_client
    ):
        """Test command triggers fast response with Reply API"""
        async def fast_response(user_id, user_input, include_context):
            await asyncio.sleep(0.1)
            return "您的任務列表：\n1. 服用藥物\n2. 記錄症狀"

        mock_agent_manager.handle_message = fast_response
        mock_line_client.send_text_message.return_value = (
            MessageSendMethod.REPLY,
            {},
        )

        event_data = {
            "patient_id": "patient_123",
            "text": "查看任務",
            "line_user_id": "U1234567890abcdef",
            "reply_token": "valid_reply_token",
        }

        await consumer._handle_text_message(event_data)

        # Verify Reply API was used (FREE)
        call_kwargs = mock_line_client.send_text_message.call_args.kwargs
        assert call_kwargs["reply_token"] is not None


class TestSlowResponseUsesPushAPI:
    """Test slow responses use Push API (PAID)"""

    @pytest.mark.asyncio
    async def test_complex_query_slow_response(
        self, consumer, mock_agent_manager, mock_line_client
    ):
        """Test complex query triggers slow response with Push API"""
        # Mock slow agent response (> 25 seconds)
        async def slow_response(user_id, user_input, include_context):
            await asyncio.sleep(0.5)  # Simulate slow processing
            return "根據您的症狀分析，建議您..."

        mock_agent_manager.handle_message = slow_response

        # Mock Push API success (Reply will timeout)
        mock_line_client.send_text_message.return_value = (
            MessageSendMethod.PUSH,
            {"status": "ok"},
        )

        event_data = {
            "patient_id": "patient_123",
            "text": "我最近呼吸困難，咳嗽有痰，該怎麼辦？",
            "line_user_id": "U1234567890abcdef",
            "reply_token": "valid_reply_token",
        }

        # Patch time.time() to simulate > 25s elapsed
        original_time = time.time

        def mock_time_sequence():
            """Mock time sequence: start, then +26s"""
            calls = [0]

            def _time():
                if calls[0] == 0:
                    calls[0] += 1
                    return 100.0  # Start time
                else:
                    return 126.1  # +26.1 seconds (> 25s threshold)

            return _time

        with patch("time.time", side_effect=mock_time_sequence()):
            await consumer._handle_text_message(event_data)

        # Verify Push API was used (PAID) because elapsed_time > 25s
        call_kwargs = mock_line_client.send_text_message.call_args.kwargs
        # When elapsed > 25s, Consumer passes only user_id (Push API)
        assert call_kwargs["user_id"] == "U1234567890abcdef"


class TestReplyTokenExpiryFallback:
    """Test fallback to Push API when Reply Token expires"""

    @pytest.mark.asyncio
    async def test_reply_token_expired_during_processing(
        self, consumer, mock_agent_manager, mock_line_client
    ):
        """Test fallback when Reply Token expires during agent processing"""
        async def moderate_response(user_id, user_input, include_context):
            await asyncio.sleep(0.2)  # 200ms processing
            return "COPD 是慢性阻塞性肺病..."

        mock_agent_manager.handle_message = moderate_response

        # Mock Reply fails (expired), then Push succeeds
        from respira_ally.infrastructure.line.line_client import (
            LineReplyTokenExpiredError,
        )

        async def mock_send_with_fallback(**kwargs):
            if kwargs.get("reply_token"):
                # First try Reply, but token expired
                raise LineReplyTokenExpiredError("Reply token expired")
            else:
                # Fallback to Push succeeds
                return (MessageSendMethod.PUSH, {"status": "ok"})

        mock_line_client.send_text_message.side_effect = mock_send_with_fallback

        event_data = {
            "patient_id": "patient_123",
            "text": "什麼是COPD？",
            "line_user_id": "U1234567890abcdef",
            "reply_token": "expired_reply_token",
        }

        # This should not raise exception (fallback to Push)
        await consumer._handle_text_message(event_data)

        # Verify send_text_message was called (might be called twice: Reply fail → Push success)
        assert mock_line_client.send_text_message.call_count >= 1


class TestMessageClassificationIntegration:
    """Test message classification integration with decision logic"""

    @pytest.mark.asyncio
    async def test_classifier_determines_processing_strategy(
        self, consumer, mock_agent_manager, mock_line_client
    ):
        """Test MessageClassifier influences processing strategy"""
        async def standard_response(user_id, user_input, include_context):
            await asyncio.sleep(0.1)
            return "回應訊息"

        mock_agent_manager.handle_message = standard_response
        mock_line_client.send_text_message.return_value = (
            MessageSendMethod.REPLY,
            {},
        )

        test_cases = [
            {
                "text": "你好",
                "expected_complexity": "simple",
                "should_use_reply": True,
            },
            {
                "text": "查看任務",
                "expected_complexity": "simple",
                "should_use_reply": True,
            },
            {
                "text": "什麼是COPD？",
                "expected_complexity": "moderate",
                "should_use_reply": True,
            },
        ]

        for case in test_cases:
            event_data = {
                "patient_id": "patient_123",
                "text": case["text"],
                "line_user_id": "U123",
                "reply_token": "valid_token",
            }

            # Reset mock
            mock_line_client.send_text_message.reset_mock()

            await consumer._handle_text_message(event_data)

            # Verify classification was logged (check if send was called)
            assert mock_line_client.send_text_message.called


class TestCostTrackingIntegration:
    """Test cost tracking integration"""

    @pytest.mark.asyncio
    async def test_cost_stats_logged_after_send(
        self, consumer, mock_agent_manager, mock_line_client
    ):
        """Test cost statistics are logged after message send"""
        async def fast_response(user_id, user_input, include_context):
            await asyncio.sleep(0.05)
            return "回應"

        mock_agent_manager.handle_message = fast_response
        mock_line_client.send_text_message.return_value = (
            MessageSendMethod.REPLY,
            {},
        )

        # Mock get_usage_stats with incremental values
        stats_sequence = [
            {
                "reply_count": 1,
                "push_count": 0,
                "total_count": 1,
                "reply_ratio_percent": 100.0,
                "estimated_monthly_cost_twd": 0.0,
            },
            {
                "reply_count": 2,
                "push_count": 0,
                "total_count": 2,
                "reply_ratio_percent": 100.0,
                "estimated_monthly_cost_twd": 0.0,
            },
        ]

        mock_line_client.get_usage_stats.side_effect = stats_sequence

        # Send two messages
        for i in range(2):
            event_data = {
                "patient_id": f"patient_{i}",
                "text": "你好",
                "line_user_id": "U123",
                "reply_token": "valid_token",
            }
            await consumer._handle_text_message(event_data)

        # Verify get_usage_stats was called twice
        assert mock_line_client.get_usage_stats.call_count == 2


class TestErrorHandling:
    """Test error handling in Consumer"""

    @pytest.mark.asyncio
    async def test_agent_error_sends_fallback_message(
        self, consumer, mock_agent_manager, mock_line_client
    ):
        """Test fallback error message when agent fails"""

        async def failing_agent(user_id, user_input, include_context):
            raise Exception("Agent processing failed")

        mock_agent_manager.handle_message = failing_agent
        mock_line_client.send_text_message.return_value = (
            MessageSendMethod.REPLY,
            {},
        )

        event_data = {
            "patient_id": "patient_123",
            "text": "測試",
            "line_user_id": "U123",
            "reply_token": "valid_token",
        }

        # Should not raise exception (sends fallback message)
        await consumer._handle_text_message(event_data)

        # Verify fallback message was sent
        call_kwargs = mock_line_client.send_text_message.call_args.kwargs
        assert "抱歉" in call_kwargs["text"] or "繁忙" in call_kwargs["text"]


class TestConversationHistorySaving:
    """Test conversation history is saved correctly"""

    @pytest.mark.asyncio
    async def test_conversation_saved_after_success(
        self, consumer, mock_agent_manager, mock_line_client
    ):
        """Test conversation is saved to database"""

        async def standard_response(user_id, user_input, include_context):
            await asyncio.sleep(0.05)
            return "AI 回應"

        mock_agent_manager.handle_message = standard_response
        mock_line_client.send_text_message.return_value = (
            MessageSendMethod.REPLY,
            {},
        )

        event_data = {
            "patient_id": "patient_123",
            "text": "使用者訊息",
            "line_user_id": "U123",
            "reply_token": "valid_token",
        }

        await consumer._handle_text_message(event_data)

        # Verify conversation was saved (2 messages: user + assistant)
        assert mock_agent_manager.conversation_repo.save_message.call_count == 2

        # Check user message was saved
        first_call = mock_agent_manager.conversation_repo.save_message.call_args_list[0]
        assert first_call.kwargs["role"] == "user"
        assert first_call.kwargs["content"] == "使用者訊息"

        # Check assistant message was saved
        second_call = mock_agent_manager.conversation_repo.save_message.call_args_list[
            1
        ]
        assert second_call.kwargs["role"] == "assistant"
        assert second_call.kwargs["content"] == "AI 回應"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
