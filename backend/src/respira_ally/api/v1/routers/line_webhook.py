"""
LINE Webhook Router
API Layer - LINE Bot Integration

Handles incoming webhook events from LINE platform.
Publishes events to RabbitMQ for async processing by Health Agents.
"""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from linebot.v3 import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import (
    AudioMessageContent,
    FollowEvent,
    MessageEvent,
    TextMessageContent,
    UnfollowEvent,
)
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.core.config import settings
from respira_ally.domain.events.line_message_events import (
    create_line_audio_message_received_event,
    create_line_text_message_received_event,
)
from respira_ally.domain.repositories.user_repository import UserRepository
from respira_ally.infrastructure.database.session import get_db
from respira_ally.infrastructure.message_queue.rabbitmq_event_publisher import (
    get_rabbitmq_publisher,
)
from respira_ally.infrastructure.repository_impls.user_repository_impl import (
    UserRepositoryImpl,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/line", tags=["LINE Webhook"])

# LINE Bot SDK Parser (verifies signature and parses events)
parser = WebhookParser(channel_secret=settings.LINE_CHANNEL_SECRET)


# ============================================================================
# Dependency Injection
# ============================================================================


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """Get user repository instance"""
    return UserRepositoryImpl(db_session=db)


# ============================================================================
# LINE Webhook Endpoint
# ============================================================================


@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
    summary="LINE Webhook Endpoint",
    description="""
    Receives webhook events from LINE platform.

    **Events Handled**:
    - TextMessage: Process with Health Agent via RabbitMQ
    - AudioMessage: Transcribe and process with Health Agent
    - FollowEvent: Welcome new users
    - UnfollowEvent: Log user unfollow

    **Flow**:
    1. Verify LINE signature (security)
    2. Parse webhook events
    3. Check user registration
    4. Publish event to RabbitMQ for async processing
    """,
)
async def webhook(
    request: Request,
    x_line_signature: Annotated[str, Header()],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> dict[str, str]:
    """
    LINE Webhook endpoint - receives and processes LINE events

    Args:
        request: FastAPI request object (contains raw body)
        x_line_signature: LINE signature header for verification
        user_repo: User repository for database access

    Returns:
        Success response

    Raises:
        HTTPException: If signature verification fails or event processing fails
    """
    # Step 1: Get raw body for signature verification
    body = await request.body()
    body_str = body.decode("utf-8")

    # Step 2: Verify signature and parse events
    try:
        events = parser.parse(body_str, x_line_signature)
    except InvalidSignatureError:
        logger.error("Invalid LINE signature - possible security threat")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature. Verify LINE Channel Secret configuration.",
        )

    # Step 3: Process each event
    for event in events:
        logger.info(f"Processing LINE event: {type(event).__name__}")

        try:
            if isinstance(event, MessageEvent):
                if isinstance(event.message, TextMessageContent):
                    await handle_text_message(event, user_repo)
                elif isinstance(event.message, AudioMessageContent):
                    await handle_audio_message(event, user_repo)
                else:
                    logger.info(f"Unsupported message type: {type(event.message).__name__}")

            elif isinstance(event, FollowEvent):
                await handle_follow_event(event, user_repo)

            elif isinstance(event, UnfollowEvent):
                await handle_unfollow_event(event, user_repo)

            else:
                logger.info(f"Unsupported event type: {type(event).__name__}")

        except Exception as e:
            # Log error but don't fail the entire webhook
            # LINE expects 200 OK even if individual events fail
            logger.error(f"Failed to process event {type(event).__name__}: {str(e)}", exc_info=True)

    return {"status": "ok"}


# ============================================================================
# Event Handlers
# ============================================================================


async def handle_text_message(event: MessageEvent, user_repo: UserRepository) -> None:
    """
    Handle incoming text message from LINE

    Flow:
    1. Find user by LINE user ID
    2. Check if user is registered
    3. Create domain event
    4. Publish to RabbitMQ for async agent processing

    Args:
        event: LINE MessageEvent
        user_repo: User repository
    """
    line_user_id = event.source.user_id
    message_id = event.message.id
    text = event.message.text
    reply_token = event.reply_token

    logger.info(f"Text message from {line_user_id}: {text[:50]}...")

    # Find user in database
    user = await user_repo.find_by_line_user_id(line_user_id)

    if not user:
        logger.warning(f"Unregistered user {line_user_id} sent message - ignoring")
        # TODO: Reply with registration prompt
        # This requires LINE Bot API client implementation
        return

    if user.role != "PATIENT":
        logger.warning(f"Non-patient user {user.user_id} sent message via LINE")
        return

    # Create domain event
    event_obj = create_line_text_message_received_event(
        patient_id=user.user_id,
        line_user_id=line_user_id,
        message_id=message_id,
        text=text,
        reply_token=reply_token,
    )

    # Publish to RabbitMQ
    publisher = get_rabbitmq_publisher(queue_name="line_message_queue")
    try:
        await publisher.publish(event_obj)
        logger.info(f"Published text message event to RabbitMQ: {event_obj.event_id}")
    except Exception as e:
        logger.error(f"Failed to publish text message event: {str(e)}", exc_info=True)
        raise


async def handle_audio_message(event: MessageEvent, user_repo: UserRepository) -> None:
    """
    Handle incoming audio message from LINE

    Flow:
    1. Find user by LINE user ID
    2. Check if user is registered
    3. Download audio from LINE (future: implement LINE Bot API client)
    4. Create domain event with audio data
    5. Publish to RabbitMQ for transcription and agent processing

    Args:
        event: LINE MessageEvent
        user_repo: User repository
    """
    line_user_id = event.source.user_id
    message_id = event.message.id
    duration_ms = event.message.duration
    reply_token = event.reply_token

    logger.info(f"Audio message from {line_user_id}: duration={duration_ms}ms")

    # Find user in database
    user = await user_repo.find_by_line_user_id(line_user_id)

    if not user:
        logger.warning(f"Unregistered user {line_user_id} sent audio - ignoring")
        return

    if user.role != "PATIENT":
        logger.warning(f"Non-patient user {user.user_id} sent audio via LINE")
        return

    # TODO: Download audio from LINE Bot API
    # For now, we'll just pass the message_id and let the consumer handle download
    # This requires implementing LINE Bot API client with MessagingApiBlob

    # Create domain event
    event_obj = create_line_audio_message_received_event(
        patient_id=user.user_id,
        line_user_id=line_user_id,
        message_id=message_id,
        duration_ms=duration_ms,
        reply_token=reply_token,
        audio_url=None,  # Consumer will download from LINE using message_id
        audio_data=None,
    )

    # Publish to RabbitMQ
    publisher = get_rabbitmq_publisher(queue_name="line_message_queue")
    try:
        await publisher.publish(event_obj)
        logger.info(f"Published audio message event to RabbitMQ: {event_obj.event_id}")
    except Exception as e:
        logger.error(f"Failed to publish audio message event: {str(e)}", exc_info=True)
        raise


async def handle_follow_event(event: FollowEvent, user_repo: UserRepository) -> None:
    """
    Handle user follow (add friend) event

    Flow:
    1. Check if user exists in database
    2. If exists: Log re-follow
    3. If not exists: Log potential new user (registration handled elsewhere)
    4. Future: Send welcome message via LINE Bot API

    Args:
        event: LINE FollowEvent
        user_repo: User repository
    """
    line_user_id = event.source.user_id
    reply_token = event.reply_token

    logger.info(f"User followed bot: {line_user_id}")

    user = await user_repo.find_by_line_user_id(line_user_id)

    if user:
        logger.info(f"Existing user {user.user_id} re-followed the bot")
    else:
        logger.info(f"New LINE user {line_user_id} followed - awaiting registration")

    # TODO: Send welcome message using LINE Bot API
    # This requires implementing LINE Messaging API client
    # Example: line_bot_api.reply_message(reply_token, TextMessage(text="歡迎使用 RespiraAlly!"))


async def handle_unfollow_event(event: UnfollowEvent, user_repo: UserRepository) -> None:
    """
    Handle user unfollow (block/unfriend) event

    Flow:
    1. Find user in database
    2. Log unfollow event
    3. Future: Update user status or trigger retention workflow

    Args:
        event: LINE UnfollowEvent
        user_repo: User repository
    """
    line_user_id = event.source.user_id

    logger.info(f"User unfollowed bot: {line_user_id}")

    user = await user_repo.find_by_line_user_id(line_user_id)

    if user:
        logger.info(f"User {user.user_id} unfollowed/blocked the bot")
        # TODO: Consider soft-delete or status update
    else:
        logger.warning(f"Unknown user {line_user_id} unfollowed")
