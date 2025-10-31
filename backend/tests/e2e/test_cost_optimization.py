"""
E2E Tests for Cost Optimization

Test Coverage:
- Verify 85% Reply API usage target
- Simulate realistic message distribution
- Validate cost savings calculation
- Test under different load scenarios
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch

from respira_ally.infrastructure.line.line_client import (
    LineMessagingClient,
    MessageSendMethod,
)
from respira_ally.application.services.message_classifier import MessageClassifier


@pytest.fixture
def message_distribution():
    """
    Realistic message distribution based on user behavior analysis

    Distribution:
    - 40% Greetings (SIMPLE)
    - 30% Commands (SIMPLE)
    - 20% FAQ (MODERATE)
    - 10% Complex queries (COMPLEX)

    Expected Reply usage: 90% (SIMPLE + MODERATE)
    Expected Push usage: 10% (COMPLEX)
    """
    return {
        "greetings": [
            "你好",
            "嗨",
            "Hi",
            "早安",
            "午安",
            "晚安",
            "Hello",
        ]
        * 6,  # 42 messages (40%)
        "commands": [
            "查看任務",
            "檢視提醒",
            "顯示警報",
            "列出記錄",
            "查詢歷史",
        ]
        * 6,  # 30 messages (30%)
        "faqs": [
            "什麼是COPD？",
            "如何使用吸入器？",
            "為什麼需要用藥？",
            "慢阻肺症狀？",
        ]
        * 5,  # 20 messages (20%)
        "complex": [
            "我最近呼吸困難，咳嗽有痰，該怎麼辦？",
            "我的症狀持續惡化，需要調整藥物嗎？",
        ]
        * 5,  # 10 messages (10%)
    }


class TestCostOptimizationTarget:
    """Test cost optimization target: 85% Reply API usage"""

    @pytest.mark.asyncio
    async def test_realistic_message_distribution_achieves_85_percent_reply(
        self, message_distribution
    ):
        """
        Test realistic message distribution achieves 85%+ Reply usage

        Scenario:
        - 100 messages with realistic distribution
        - Fast agent processing (<5s for simple, <25s for moderate)
        - Target: >= 85% Reply API usage
        """
        client = LineMessagingClient(access_token="test_token")
        classifier = MessageClassifier()

        # Flatten all messages
        all_messages = (
            message_distribution["greetings"]
            + message_distribution["commands"]
            + message_distribution["faqs"]
            + message_distribution["complex"]
        )

        # Mock HTTP client
        async def mock_send(method, endpoint, json):
            await asyncio.sleep(0.001)  # Simulate network latency
            return Mock(status_code=200, json=lambda: {}, text="")

        # Track actual API usage
        reply_count = 0
        push_count = 0

        with patch.object(client._client, "request", new=AsyncMock()) as mock_request:
            mock_request.side_effect = mock_send

            for message in all_messages:
                # Classify message
                should_reply, _ = classifier.should_use_reply_api(message)

                # Simulate agent processing time
                complexity = classifier.classify_complexity(message)
                if complexity.value == "simple":
                    processing_time = 2.0  # Fast
                elif complexity.value == "moderate":
                    processing_time = 10.0  # Moderate
                else:
                    processing_time = 35.0  # Slow

                # Decision: Reply or Push?
                if should_reply and processing_time < 25:
                    # Use Reply API (FREE)
                    try:
                        await client.send_text_message(
                            text="回應",
                            reply_token="valid_token",
                            user_id="U123",
                        )
                        reply_count += 1
                    except:
                        # Fallback to Push
                        await client.send_text_message(text="回應", user_id="U123")
                        push_count += 1
                else:
                    # Use Push API (PAID)
                    await client.send_text_message(text="回應", user_id="U123")
                    push_count += 1

        # Verify cost optimization target
        total = reply_count + push_count
        reply_ratio = (reply_count / total) * 100 if total > 0 else 0

        assert reply_ratio >= 85.0, (
            f"Reply ratio {reply_ratio:.1f}% < 85% target. "
            f"Reply: {reply_count}, Push: {push_count}, Total: {total}"
        )

        # Verify cost savings
        push_cost = push_count * 0.4  # TWD per message
        assert push_cost <= 6.0, (  # Max 15 Push messages * 0.4 = 6 TWD
            f"Push cost {push_cost} TWD exceeds 6 TWD budget for 100 messages"
        )

    @pytest.mark.asyncio
    async def test_cost_calculation_accuracy(self):
        """Test cost calculation accuracy for different scenarios"""
        client = LineMessagingClient(access_token="test_token")

        async def mock_send(method, endpoint, json):
            return Mock(status_code=200, json=lambda: {}, text="")

        with patch.object(client._client, "request", new=AsyncMock()) as mock_request:
            mock_request.side_effect = mock_send

            # Scenario 1: 85% Reply, 15% Push
            for _ in range(85):
                await client.send_text_message(
                    text="測試", reply_token="token", user_id="U123"
                )

            for _ in range(15):
                await client.send_text_message(text="測試", user_id="U123")

            stats = client.get_usage_stats()
            assert stats["reply_ratio_percent"] == 85.0
            assert stats["estimated_monthly_cost_twd"] == 15 * 0.4  # 6 TWD


class TestScalabilityCostAnalysis:
    """Test cost analysis under different load scenarios"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "total_messages,expected_push_ratio,max_monthly_cost",
        [
            (100, 0.15, 6.0),  # 100 messages: 15% Push = 6 TWD
            (1000, 0.15, 60.0),  # 1000 messages: 15% Push = 60 TWD
            (10000, 0.15, 600.0),  # 10000 messages: 15% Push = 600 TWD
        ],
    )
    async def test_cost_scaling_with_message_volume(
        self, total_messages, expected_push_ratio, max_monthly_cost
    ):
        """Test cost scaling with increasing message volume"""
        client = LineMessagingClient(access_token="test_token")

        async def mock_send(method, endpoint, json):
            return Mock(status_code=200, json=lambda: {}, text="")

        with patch.object(client._client, "request", new=AsyncMock()) as mock_request:
            mock_request.side_effect = mock_send

            # Simulate 85% Reply, 15% Push
            reply_count = int(total_messages * 0.85)
            push_count = total_messages - reply_count

            # Send Reply messages
            for _ in range(reply_count):
                await client.send_text_message(
                    text="測試", reply_token="token", user_id="U123"
                )

            # Send Push messages
            for _ in range(push_count):
                await client.send_text_message(text="測試", user_id="U123")

            stats = client.get_usage_stats()

            # Verify ratio
            actual_ratio = stats["reply_ratio_percent"]
            assert (
                actual_ratio >= 80.0
            ), f"Reply ratio {actual_ratio}% < 80% minimum"

            # Verify cost
            actual_cost = stats["estimated_monthly_cost_twd"]
            assert actual_cost <= max_monthly_cost * 1.1, (  # Allow 10% margin
                f"Cost {actual_cost} TWD exceeds budget {max_monthly_cost} TWD"
            )


class TestCostComparisonFullPushVsHybrid:
    """Compare costs: Full Push vs Hybrid Strategy"""

    @pytest.mark.asyncio
    async def test_cost_savings_vs_full_push(self):
        """
        Compare costs: Full Push vs Hybrid Strategy

        Scenario: 1000 messages/day × 30 days = 30,000 messages/month

        Full Push:
        - 30,000 × 0.4 TWD = 12,000 TWD/month

        Hybrid (85% Reply):
        - Reply: 25,500 (FREE)
        - Push: 4,500 × 0.4 = 1,800 TWD/month
        - Savings: 10,200 TWD/month (85%)
        """
        client = LineMessagingClient(access_token="test_token")

        async def mock_send(method, endpoint, json):
            return Mock(status_code=200, json=lambda: {}, text="")

        with patch.object(client._client, "request", new=AsyncMock()) as mock_request:
            mock_request.side_effect = mock_send

            # Simulate 30,000 messages with 85% Reply
            reply_count = 25_500
            push_count = 4_500

            # Send Reply messages (FREE)
            for _ in range(min(reply_count, 100)):  # Limit for test speed
                await client.send_text_message(
                    text="測試", reply_token="token", user_id="U123"
                )

            # Send Push messages (PAID)
            for _ in range(min(push_count, 100)):  # Limit for test speed
                await client.send_text_message(text="測試", user_id="U123")

            # Calculate projected monthly cost
            stats = client.get_usage_stats()
            total_sent = stats["total_count"]
            push_ratio = stats["push_count"] / total_sent if total_sent > 0 else 0

            # Project to monthly volume
            projected_monthly_push = 30_000 * push_ratio
            projected_monthly_cost = projected_monthly_push * 0.4

            # Full Push cost
            full_push_cost = 30_000 * 0.4  # 12,000 TWD

            # Calculate savings
            savings = full_push_cost - projected_monthly_cost
            savings_percent = (savings / full_push_cost) * 100

            assert savings_percent >= 80.0, (
                f"Savings {savings_percent:.1f}% < 80% target. "
                f"Hybrid: {projected_monthly_cost:.0f} TWD, "
                f"Full Push: {full_push_cost:.0f} TWD"
            )


class TestRealisticUserJourney:
    """Test realistic user journey scenarios"""

    @pytest.mark.asyncio
    async def test_typical_patient_daily_interaction(self):
        """
        Test typical patient daily interaction pattern

        Morning:
        1. "早安" → Reply (FREE)
        2. "查看任務" → Reply (FREE)

        Afternoon:
        3. "記錄症狀完成" → Reply (FREE)
        4. "什麼是COPD急性發作？" → Reply (FREE, FAQ)

        Evening:
        5. "我今天呼吸特別困難..." → Push (PAID, Complex)

        Expected: 4/5 = 80% Reply (meets target)
        """
        client = LineMessagingClient(access_token="test_token")
        classifier = MessageClassifier()

        async def mock_send(method, endpoint, json):
            return Mock(status_code=200, json=lambda: {}, text="")

        with patch.object(client._client, "request", new=AsyncMock()) as mock_request:
            mock_request.side_effect = mock_send

            daily_messages = [
                ("早安", True, 2.0),  # Greeting, fast
                ("查看任務", True, 3.0),  # Command, fast
                ("記錄症狀完成", True, 2.5),  # Command, fast
                ("什麼是COPD急性發作？", True, 15.0),  # FAQ, moderate
                ("我今天呼吸特別困難，咳嗽加劇...", False, 35.0),  # Complex, slow
            ]

            for text, should_reply, processing_time in daily_messages:
                if should_reply and processing_time < 25:
                    await client.send_text_message(
                        text="回應", reply_token="token", user_id="U123"
                    )
                else:
                    await client.send_text_message(text="回應", user_id="U123")

            stats = client.get_usage_stats()
            reply_ratio = stats["reply_ratio_percent"]

            assert reply_ratio >= 75.0, (  # Allow 75% for 5 messages
                f"Daily interaction Reply ratio {reply_ratio:.1f}% < 75%"
            )


class TestCostMonitoringMetrics:
    """Test cost monitoring metrics"""

    @pytest.mark.asyncio
    async def test_usage_stats_accuracy(self):
        """Test usage statistics are accurate"""
        client = LineMessagingClient(access_token="test_token")

        async def mock_send(method, endpoint, json):
            return Mock(status_code=200, json=lambda: {}, text="")

        with patch.object(client._client, "request", new=AsyncMock()) as mock_request:
            mock_request.side_effect = mock_send

            # Send known quantities
            for _ in range(17):  # 17 Reply (FREE)
                await client.send_text_message(
                    text="測試", reply_token="token", user_id="U123"
                )

            for _ in range(3):  # 3 Push (PAID)
                await client.send_text_message(text="測試", user_id="U123")

            stats = client.get_usage_stats()

            # Verify accuracy
            assert stats["reply_count"] == 17
            assert stats["push_count"] == 3
            assert stats["total_count"] == 20
            assert stats["reply_ratio_percent"] == 85.0  # 17/20 = 85%
            assert stats["estimated_monthly_cost_twd"] == 3 * 0.4  # 1.2 TWD


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
