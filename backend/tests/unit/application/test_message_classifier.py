"""
Unit Tests for MessageClassifier

Test Coverage:
- Message type classification (GREETING, COMMAND, FAQ, COMPLEX_QUERY)
- Complexity classification (SIMPLE, MODERATE, COMPLEX)
- Reply API decision logic
"""

import pytest
from respira_ally.application.services.message_classifier import (
    MessageClassifier,
    MessageType,
    MessageComplexity,
)


class TestMessageTypeClassification:
    """Test message type classification logic"""

    @pytest.fixture
    def classifier(self):
        return MessageClassifier()

    def test_classify_greeting_simple(self, classifier):
        """Test simple greeting detection"""
        greetings = ["你好", "嗨", "Hi", "Hello", "早安", "午安", "晚安"]
        for greeting in greetings:
            result = classifier.classify_message_type(greeting)
            assert result == MessageType.GREETING, f"Failed for: {greeting}"

    def test_classify_greeting_with_punctuation(self, classifier):
        """Test greeting with punctuation"""
        assert classifier.classify_message_type("你好！") == MessageType.GREETING
        assert classifier.classify_message_type("Hi!") == MessageType.GREETING

    def test_classify_command(self, classifier):
        """Test command keyword detection"""
        commands = [
            "查看任務",
            "檢視提醒",
            "顯示警報",
            "列出記錄",
            "查詢歷史",
        ]
        for cmd in commands:
            result = classifier.classify_message_type(cmd)
            assert result == MessageType.COMMAND, f"Failed for: {cmd}"

    def test_classify_faq(self, classifier):
        """Test FAQ keyword detection"""
        faqs = [
            "什麼是COPD？",
            "如何使用吸入器？",
            "為什麼需要用藥？",
            "慢阻肺是什麼？",
            "COPD症狀有哪些？",
        ]
        for faq in faqs:
            result = classifier.classify_message_type(faq)
            assert result == MessageType.FAQ, f"Failed for: {faq}"

    def test_classify_complex_query_long_text(self, classifier):
        """Test long text as complex query"""
        long_text = "我最近呼吸困難，而且咳嗽有痰，晚上睡覺也很不舒服，該怎麼辦？" * 3
        result = classifier.classify_message_type(long_text)
        assert result == MessageType.COMPLEX_QUERY

    def test_classify_complex_query_default(self, classifier):
        """Test default classification as complex query"""
        result = classifier.classify_message_type("這是一個沒有關鍵字的訊息")
        assert result == MessageType.COMPLEX_QUERY


class TestComplexityClassification:
    """Test complexity classification logic"""

    @pytest.fixture
    def classifier(self):
        return MessageClassifier()

    def test_complexity_greeting_is_simple(self, classifier):
        """Test greeting complexity is SIMPLE"""
        result = classifier.classify_complexity("你好")
        assert result == MessageComplexity.SIMPLE

    def test_complexity_command_is_simple(self, classifier):
        """Test command complexity is SIMPLE"""
        result = classifier.classify_complexity("查看任務")
        assert result == MessageComplexity.SIMPLE

    def test_complexity_faq_is_moderate(self, classifier):
        """Test FAQ complexity is MODERATE"""
        result = classifier.classify_complexity("什麼是COPD？")
        assert result == MessageComplexity.MODERATE

    def test_complexity_complex_query_is_complex(self, classifier):
        """Test complex query complexity is COMPLEX"""
        long_text = "我最近呼吸困難，咳嗽有痰..." * 3
        result = classifier.classify_complexity(long_text)
        assert result == MessageComplexity.COMPLEX


class TestReplyAPIDecision:
    """Test Reply API decision logic"""

    @pytest.fixture
    def classifier(self):
        return MessageClassifier()

    def test_should_use_reply_for_greeting(self, classifier):
        """Test greeting should use Reply API"""
        should_reply, reason = classifier.should_use_reply_api("你好")
        assert should_reply is True
        assert "Simple" in reason
        assert "greeting" in reason.lower()

    def test_should_use_reply_for_command(self, classifier):
        """Test command should use Reply API"""
        should_reply, reason = classifier.should_use_reply_api("查看任務")
        assert should_reply is True
        assert "Simple" in reason

    def test_should_use_reply_for_faq(self, classifier):
        """Test FAQ should try Reply API (moderate)"""
        should_reply, reason = classifier.should_use_reply_api("什麼是COPD？")
        assert should_reply is True
        assert "Moderate" in reason

    def test_should_use_push_for_complex_query(self, classifier):
        """Test complex query should use Push API"""
        complex_text = "我最近呼吸困難，咳嗽有痰，晚上睡不好..." * 3
        should_reply, reason = classifier.should_use_reply_api(complex_text)
        assert should_reply is False
        assert "Complex" in reason
        assert "Push" in reason

    @pytest.mark.parametrize(
        "text,expected_reply",
        [
            ("你好", True),
            ("Hi", True),
            ("查看任務", True),
            ("什麼是COPD", True),
            ("我最近呼吸困難，咳嗽有痰，該怎麼辦？我已經用藥了但效果不好...", False),
        ],
    )
    def test_reply_decision_parametrized(self, classifier, text, expected_reply):
        """Parametrized test for Reply API decision"""
        should_reply, _ = classifier.should_use_reply_api(text)
        assert should_reply == expected_reply


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    @pytest.fixture
    def classifier(self):
        return MessageClassifier()

    def test_empty_string(self, classifier):
        """Test empty string classification"""
        result = classifier.classify_message_type("")
        assert result == MessageType.COMPLEX_QUERY  # Default

    def test_whitespace_only(self, classifier):
        """Test whitespace-only string"""
        result = classifier.classify_message_type("   ")
        assert result == MessageType.COMPLEX_QUERY

    def test_mixed_case_greeting(self, classifier):
        """Test case-insensitive greeting"""
        assert classifier.classify_message_type("HELLO") == MessageType.GREETING
        assert classifier.classify_message_type("HeLLo") == MessageType.GREETING

    def test_boundary_length_100_chars(self, classifier):
        """Test boundary at 100 characters"""
        text_99 = "a" * 99
        text_100 = "a" * 100
        text_101 = "a" * 101

        # All should be COMPLEX_QUERY (no keywords)
        assert classifier.classify_message_type(text_99) == MessageType.COMPLEX_QUERY
        assert classifier.classify_message_type(text_100) == MessageType.COMPLEX_QUERY
        assert classifier.classify_message_type(text_101) == MessageType.COMPLEX_QUERY


# Performance test (optional)
class TestPerformance:
    """Test performance of classifier"""

    @pytest.fixture
    def classifier(self):
        return MessageClassifier()

    def test_classify_performance_1000_messages(self, classifier):
        """Test classification performance with 1000 messages"""
        import time

        messages = ["你好"] * 500 + ["查看任務"] * 300 + ["什麼是COPD"] * 200

        start = time.time()
        for msg in messages:
            classifier.classify_message_type(msg)
        elapsed = time.time() - start

        # Should complete in < 1 second
        assert elapsed < 1.0, f"Classification took {elapsed:.2f}s for 1000 messages"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
