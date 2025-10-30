"""
End-to-End Test for LINE → RabbitMQ → Agent Flow
Tests the complete integration from LINE webhook to agent response.
"""

import asyncio
import json
import sys
from pathlib import Path
from uuid import uuid4

# Add src to path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root / "src"))

from respira_ally.domain.events.line_message_events import (
    create_line_text_message_received_event,
)
from respira_ally.infrastructure.message_queue.rabbitmq_event_publisher import (
    get_rabbitmq_publisher,
)


async def test_publish_line_message():
    """
    Test publishing a LINE text message event to RabbitMQ

    This simulates what the LINE webhook does when a message is received.
    """
    print("=" * 70)
    print("E2E TEST: LINE → RabbitMQ → Agent Flow")
    print("=" * 70)

    # Step 1: Create a test event
    print("\n📝 Step 1: Creating test LINE message event...")

    test_patient_id = uuid4()
    test_line_user_id = "U1234567890abcdef"
    test_message_id = str(uuid4())
    test_text = "我最近咳嗽很嚴重，該怎麼辦？"
    test_reply_token = "test_reply_token_123"

    event = create_line_text_message_received_event(
        patient_id=test_patient_id,
        line_user_id=test_line_user_id,
        message_id=test_message_id,
        text=test_text,
        reply_token=test_reply_token,
    )

    print(f"   ✅ Event created:")
    print(f"      - Event ID: {event.event_id}")
    print(f"      - Event Type: {event.event_type}")
    print(f"      - Patient ID: {event.patient_id}")
    print(f"      - Text: {event.text}")

    # Step 2: Publish to RabbitMQ
    print("\n📤 Step 2: Publishing event to RabbitMQ...")

    try:
        publisher = get_rabbitmq_publisher(queue_name="line_message_queue")
        await publisher.publish(event)
        print(f"   ✅ Event published to queue: line_message_queue")
    except Exception as e:
        print(f"   ❌ Failed to publish: {e}")
        return False

    # Step 3: Verify event serialization
    print("\n🔍 Step 3: Verifying event serialization...")

    event_json = event.model_dump_json(exclude_none=True)
    event_dict = json.loads(event_json)

    print(f"   ✅ Event serialized successfully:")
    print(f"      - JSON length: {len(event_json)} bytes")
    print(f"      - Keys: {list(event_dict.keys())}")

    # Step 4: Instructions for manual testing
    print("\n" + "=" * 70)
    print("📋 MANUAL TESTING STEPS")
    print("=" * 70)
    print("\n1. Start the RabbitMQ consumer in another terminal:")
    print("   ```")
    print("   python -m respira_ally.infrastructure.message_queue.consumers.line_message_consumer")
    print("   ```")
    print("\n2. Monitor the consumer logs for message processing")
    print("\n3. Expected flow:")
    print("   - Consumer receives the message")
    print("   - Guardrail agent checks the message")
    print("   - Health agent generates response")
    print("   - Response is logged (LINE API integration pending)")
    print("\n4. Check consumer logs for:")
    print(f"   - Processing message: {event.event_type}")
    print(f"   - Processing text message from patient {test_patient_id}")
    print(f"   - Agent response: [健康建議內容]")

    print("\n" + "=" * 70)
    print("✅ TEST COMPLETED")
    print("=" * 70)
    print("\nNote: This test only verifies publishing.")
    print("Run the consumer manually to test the complete E2E flow.")

    return True


async def test_multiple_messages():
    """
    Test publishing multiple messages to verify consumer handles load
    """
    print("\n" + "=" * 70)
    print("LOAD TEST: Multiple Messages")
    print("=" * 70)

    test_messages = [
        "我的血氧濃度是 92%，這正常嗎？",
        "COPD 患者可以運動嗎？",
        "我應該什麼時候去看醫生？",
        "如何使用吸入器？",
        "我感覺呼吸困難，該怎麼辦？",
    ]

    publisher = get_rabbitmq_publisher(queue_name="line_message_queue")

    print(f"\n📤 Publishing {len(test_messages)} test messages...")

    for i, text in enumerate(test_messages, 1):
        event = create_line_text_message_received_event(
            patient_id=uuid4(),
            line_user_id=f"U{i:016d}",
            message_id=str(uuid4()),
            text=text,
            reply_token=f"token_{i}",
        )

        try:
            await publisher.publish(event)
            print(f"   ✅ Message {i}/{len(test_messages)}: {text[:30]}...")
        except Exception as e:
            print(f"   ❌ Failed to publish message {i}: {e}")

    print(f"\n✅ Published {len(test_messages)} messages to queue")
    print("Monitor consumer logs to see agent responses")


if __name__ == "__main__":
    print("\nRespiraAlly LINE Integration E2E Test")
    print("=" * 70)

    # Run tests
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(test_publish_line_message())

    if success:
        # Ask if user wants to run load test
        print("\n" + "=" * 70)
        response = input("\nRun load test with multiple messages? (y/N): ")
        if response.lower() == "y":
            loop.run_until_complete(test_multiple_messages())

    sys.exit(0 if success else 1)
