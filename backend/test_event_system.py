"""
Test Event Publishing System
Test script to verify the event publishing system works correctly
"""
import asyncio
from datetime import date
from uuid import uuid4

from src.respira_ally.domain.events.daily_log_events import (
    create_daily_log_submitted_event,
    DailyLogSubmittedEvent,
)
from src.respira_ally.infrastructure.message_queue.in_memory_event_bus import (
    get_event_bus,
)


# ============================================================================
# Test Handler
# ============================================================================


async def test_handler(event: DailyLogSubmittedEvent):
    """Test event handler that prints event details"""
    print(f"✅ Event received: {event.event_type}")
    print(f"   - Event ID: {event.event_id}")
    print(f"   - Patient ID: {event.patient_id}")
    print(f"   - Log Date: {event.log_date}")
    print(f"   - Medication Taken: {event.medication_taken}")
    print(f"   - Water Intake: {event.water_intake_ml}ml")
    print(f"   - First Log Today: {event.is_first_log_today}")
    print(f"   - Consecutive Days: {event.consecutive_days}")


# ============================================================================
# Test Execution
# ============================================================================


async def test_event_publishing():
    """Test event publishing and subscription"""
    print("=" * 70)
    print("Testing Event Publishing System")
    print("=" * 70)

    # 1. Get event bus instance
    event_bus = get_event_bus()
    print("\n✅ Step 1: Event bus initialized")

    # 2. Subscribe handler
    event_bus.subscribe("daily_log.submitted", test_handler)
    print("✅ Step 2: Handler subscribed to 'daily_log.submitted'")

    # 3. Create and publish test event
    test_event = create_daily_log_submitted_event(
        log_id=uuid4(),
        patient_id=uuid4(),
        log_date=date.today(),
        medication_taken=True,
        water_intake_ml=2000,
        steps_count=8000,
        symptoms="輕微咳嗽",
        mood="GOOD",
        is_first_log_today=True,
        consecutive_days=5,
    )
    print("\n✅ Step 3: Test event created")

    # 4. Publish event
    print("\n📤 Publishing event...")
    await event_bus.publish(test_event)

    # 5. Verify event was published
    published_events = event_bus.get_published_events()
    print(f"\n✅ Step 4: Event published successfully!")
    print(f"   Total events published: {len(published_events)}")

    # 6. Verify event details
    assert len(published_events) == 1, "Should have 1 event published"
    published_event = published_events[0]
    assert published_event.event_type == "daily_log.submitted"
    assert published_event.patient_id == test_event.patient_id
    assert published_event.medication_taken is True
    assert published_event.water_intake_ml == 2000

    print("\n✅ Step 5: All assertions passed!")

    # 7. Test batch publishing
    print("\n" + "=" * 70)
    print("Testing Batch Publishing")
    print("=" * 70)

    event_bus.clear_published_events()  # Clear previous events

    batch_events = [
        create_daily_log_submitted_event(
            log_id=uuid4(),
            patient_id=uuid4(),
            log_date=date.today(),
            medication_taken=True,
            water_intake_ml=1500,
            steps_count=None,
            symptoms=None,
            mood="NEUTRAL",
            is_first_log_today=True,
            consecutive_days=i,
        )
        for i in range(3)
    ]

    print(f"\n📤 Publishing batch of {len(batch_events)} events...")
    await event_bus.publish_batch(batch_events)

    published_events = event_bus.get_published_events()
    print(f"✅ Batch published successfully!")
    print(f"   Total events in batch: {len(published_events)}")

    assert len(published_events) == 3, "Should have 3 events published"

    print("\n" + "=" * 70)
    print("🎉 All tests passed! Event publishing system works correctly.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_event_publishing())
