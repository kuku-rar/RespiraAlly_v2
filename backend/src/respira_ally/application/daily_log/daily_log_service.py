"""
Daily Log Application Service
Application Layer - Clean Architecture

This service orchestrates daily log-related use cases and business logic.
It uses Repository pattern for data access and encapsulates complex workflows.
"""
import logging
from datetime import date
from typing import Optional
from uuid import UUID

from respira_ally.core.schemas.daily_log import (
    DailyLogCreate,
    DailyLogUpdate,
    DailyLogResponse,
    DailyLogListResponse,
    DailyLogStats,
)
from respira_ally.domain.events.daily_log_events import (
    create_daily_log_submitted_event,
    create_daily_log_updated_event,
    create_daily_log_deleted_event,
)
from respira_ally.domain.repositories.daily_log_repository import DailyLogRepository
from respira_ally.infrastructure.database.models.daily_log import DailyLogModel
from respira_ally.infrastructure.message_queue.publishers.event_publisher import EventPublisher

logger = logging.getLogger(__name__)


class DailyLogService:
    """
    Daily Log Application Service

    Responsibilities:
    - Orchestrate daily log CRUD operations
    - Calculate adherence and statistics
    - Validate business rules (one log per day)
    - Coordinate with event publishing
    """

    def __init__(
        self,
        daily_log_repository: DailyLogRepository,
        event_publisher: Optional[EventPublisher] = None,
    ):
        """
        Initialize service with repository and event publisher

        Args:
            daily_log_repository: Implementation of DailyLogRepository interface
            event_publisher: Optional event publisher for domain events
        """
        self.daily_log_repo = daily_log_repository
        self.event_publisher = event_publisher

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def to_response(self, daily_log: DailyLogModel) -> DailyLogResponse:
        """
        Convert DailyLogModel to DailyLogResponse

        Args:
            daily_log: DailyLogModel from database

        Returns:
            DailyLogResponse
        """
        return DailyLogResponse(
            log_id=daily_log.log_id,
            patient_id=daily_log.patient_id,
            log_date=daily_log.log_date,
            medication_taken=daily_log.medication_taken,
            water_intake_ml=daily_log.water_intake_ml,
            exercise_minutes=daily_log.exercise_minutes,
            symptoms=daily_log.symptoms,
            mood=daily_log.mood,
            created_at=daily_log.created_at,
            updated_at=daily_log.updated_at,
        )

    # ========================================================================
    # Create Operations
    # ========================================================================

    async def create_daily_log(self, data: DailyLogCreate) -> DailyLogResponse:
        """
        Create a new daily log

        Business Rule: Only one log per patient per day
        If log already exists for the date, raises ValueError

        Args:
            data: Daily log creation request

        Returns:
            DailyLogResponse

        Raises:
            ValueError: If log already exists for this date
        """
        # Check if log already exists for this date
        existing_log = await self.daily_log_repo.get_by_patient_and_date(
            patient_id=data.patient_id,
            log_date=data.log_date,
        )

        if existing_log:
            raise ValueError(
                f"Daily log already exists for patient {data.patient_id} on {data.log_date}"
            )

        # Create new log
        daily_log = DailyLogModel(
            patient_id=data.patient_id,
            log_date=data.log_date,
            medication_taken=data.medication_taken,
            water_intake_ml=data.water_intake_ml,
            exercise_minutes=data.exercise_minutes,
            symptoms=data.symptoms,
            mood=data.mood,
        )

        created_log = await self.daily_log_repo.create(daily_log)
        return self.to_response(created_log)

    async def create_or_update_daily_log(
        self, data: DailyLogCreate
    ) -> tuple[DailyLogResponse, bool]:
        """
        Create a new daily log or update existing one

        Args:
            data: Daily log creation/update request

        Returns:
            Tuple of (DailyLogResponse, was_created)
            - was_created: True if new log was created, False if updated
        """
        # Check if log already exists
        existing_log = await self.daily_log_repo.get_by_patient_and_date(
            patient_id=data.patient_id,
            log_date=data.log_date,
        )

        if existing_log:
            # Update existing log
            update_data = data.model_dump(exclude={"patient_id", "log_date"})
            updated_log = await self.daily_log_repo.update(
                log_id=existing_log.log_id,
                update_data=update_data,
            )
            response = self.to_response(updated_log)

            # Publish event (for updated log)
            await self._publish_daily_log_event(
                log_id=updated_log.log_id,
                patient_id=updated_log.patient_id,
                log_date=updated_log.log_date,
                medication_taken=updated_log.medication_taken,
                water_intake_ml=updated_log.water_intake_ml,
                exercise_minutes=updated_log.exercise_minutes,
                symptoms=updated_log.symptoms,
                mood=updated_log.mood,
                is_first_log_today=False,  # It's an update
            )

            return response, False
        else:
            # Create new log
            response = await self.create_daily_log(data)

            # Publish event (for new log)
            await self._publish_daily_log_event(
                log_id=response.log_id,
                patient_id=response.patient_id,
                log_date=response.log_date,
                medication_taken=response.medication_taken,
                water_intake_ml=response.water_intake_ml,
                exercise_minutes=response.exercise_minutes,
                symptoms=response.symptoms,
                mood=response.mood,
                is_first_log_today=True,  # It's a new log
            )

            return response, True

    async def _publish_daily_log_event(
        self,
        log_id: UUID,
        patient_id: UUID,
        log_date: date,
        medication_taken: bool,
        water_intake_ml: int,
        exercise_minutes: int | None,
        symptoms: str | None,
        mood: str | None,
        is_first_log_today: bool,
    ) -> None:
        """
        Publish daily log submitted event

        Args:
            log_id: Log ID
            patient_id: Patient ID
            log_date: Log date
            medication_taken: Whether medication was taken
            water_intake_ml: Water intake in ml
            exercise_minutes: Exercise duration in minutes
            symptoms: Symptoms description
            mood: Mood rating
            is_first_log_today: Whether this is first log today
        """
        if self.event_publisher is None:
            logger.warning("Event publisher not configured, skipping event publication")
            return

        try:
            # TODO: Calculate consecutive_days from repository
            # For now, use 0 as placeholder
            consecutive_days = 0

            # Create and publish event
            event = create_daily_log_submitted_event(
                log_id=log_id,
                patient_id=patient_id,
                log_date=log_date,
                medication_taken=medication_taken,
                water_intake_ml=water_intake_ml,
                exercise_minutes=exercise_minutes,
                symptoms=symptoms,
                mood=mood,
                is_first_log_today=is_first_log_today,
                consecutive_days=consecutive_days,
            )

            await self.event_publisher.publish(event)
            logger.info(f"Published daily_log.submitted event for log {log_id}")

        except Exception as e:
            # Log error but don't fail the request
            # In production, you might want to retry or send to DLQ
            logger.error(
                f"Failed to publish daily_log.submitted event for log {log_id}: {str(e)}",
                exc_info=True
            )

    async def _publish_daily_log_updated_event(
        self,
        log_id: UUID,
        patient_id: UUID,
        log_date: date,
        updated_fields: list[str],
    ) -> None:
        """
        Publish daily log updated event

        Args:
            log_id: Log ID
            patient_id: Patient ID
            log_date: Log date
            updated_fields: List of fields that were updated
        """
        if self.event_publisher is None:
            logger.warning("Event publisher not configured, skipping event publication")
            return

        try:
            # Create and publish event
            event = create_daily_log_updated_event(
                log_id=log_id,
                patient_id=patient_id,
                log_date=log_date,
                updated_fields=updated_fields,
            )

            await self.event_publisher.publish(event)
            logger.info(f"Published daily_log.updated event for log {log_id} (fields: {', '.join(updated_fields)})")

        except Exception as e:
            # Log error but don't fail the request
            logger.error(
                f"Failed to publish daily_log.updated event for log {log_id}: {str(e)}",
                exc_info=True
            )

    async def _publish_daily_log_deleted_event(
        self,
        log_id: UUID,
        patient_id: UUID,
        log_date: date,
        deleted_by: UUID,
    ) -> None:
        """
        Publish daily log deleted event

        Args:
            log_id: Log ID
            patient_id: Patient ID
            log_date: Log date
            deleted_by: User ID who deleted the log
        """
        if self.event_publisher is None:
            logger.warning("Event publisher not configured, skipping event publication")
            return

        try:
            # Create and publish event
            event = create_daily_log_deleted_event(
                log_id=log_id,
                patient_id=patient_id,
                log_date=log_date,
                deleted_by=deleted_by,
            )

            await self.event_publisher.publish(event)
            logger.info(f"Published daily_log.deleted event for log {log_id}")

        except Exception as e:
            # Log error but don't fail the request
            logger.error(
                f"Failed to publish daily_log.deleted event for log {log_id}: {str(e)}",
                exc_info=True
            )

    # ========================================================================
    # Read Operations
    # ========================================================================

    async def get_daily_log_by_id(self, log_id: UUID) -> Optional[DailyLogResponse]:
        """
        Retrieve daily log by log ID

        Args:
            log_id: Daily log ID

        Returns:
            DailyLogResponse if found, None otherwise
        """
        daily_log = await self.daily_log_repo.get_by_id(log_id)
        if not daily_log:
            return None

        return self.to_response(daily_log)

    async def get_daily_log_by_patient_and_date(
        self, patient_id: UUID, log_date: date
    ) -> Optional[DailyLogResponse]:
        """
        Retrieve daily log for specific patient and date

        Args:
            patient_id: Patient's user ID
            log_date: Log date

        Returns:
            DailyLogResponse if found, None otherwise
        """
        daily_log = await self.daily_log_repo.get_by_patient_and_date(
            patient_id=patient_id, log_date=log_date
        )
        if not daily_log:
            return None

        return self.to_response(daily_log)

    async def list_daily_logs_by_patient(
        self,
        patient_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 0,
        page_size: int = 30,
    ) -> DailyLogListResponse:
        """
        List daily logs for a patient (with pagination)

        Args:
            patient_id: Patient's user ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            page: Page number (0-indexed)
            page_size: Number of items per page

        Returns:
            DailyLogListResponse with items and pagination metadata
        """
        skip = page * page_size
        logs, total = await self.daily_log_repo.list_by_patient(
            patient_id=patient_id,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=page_size,
        )

        items = [self.to_response(log) for log in logs]

        return DailyLogListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_next=(skip + len(items)) < total,
        )

    async def get_latest_log(self, patient_id: UUID) -> Optional[DailyLogResponse]:
        """
        Get the most recent log for a patient

        Args:
            patient_id: Patient's user ID

        Returns:
            Latest DailyLogResponse if found, None otherwise
        """
        daily_log = await self.daily_log_repo.get_latest_log(patient_id)
        if not daily_log:
            return None

        return self.to_response(daily_log)

    # ========================================================================
    # Update Operations
    # ========================================================================

    async def update_daily_log(
        self, log_id: UUID, data: DailyLogUpdate
    ) -> Optional[DailyLogResponse]:
        """
        Update daily log information (partial update)

        Args:
            log_id: Daily log ID
            data: Daily log update request (all fields optional)

        Returns:
            Updated DailyLogResponse if found, None otherwise
        """
        # Convert Pydantic model to dict, excluding None values
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)

        # Update using repository
        updated_log = await self.daily_log_repo.update(log_id, update_data)
        if not updated_log:
            return None

        # Publish DailyLogUpdated event
        await self._publish_daily_log_updated_event(
            log_id=updated_log.log_id,
            patient_id=updated_log.patient_id,
            log_date=updated_log.log_date,
            updated_fields=list(update_data.keys()),
        )

        return self.to_response(updated_log)

    # ========================================================================
    # Delete Operations
    # ========================================================================

    async def delete_daily_log(self, log_id: UUID, deleted_by: UUID) -> bool:
        """
        Delete daily log record

        Args:
            log_id: Daily log ID
            deleted_by: User ID who is deleting the log

        Returns:
            True if log was deleted, False if not found
        """
        # Get log info before deleting (for event publishing)
        log = await self.daily_log_repo.get_by_id(log_id)
        if not log:
            return False

        # Delete the log
        deleted = await self.daily_log_repo.delete(log_id)
        if not deleted:
            return False

        # Publish DailyLogDeleted event
        await self._publish_daily_log_deleted_event(
            log_id=log_id,
            patient_id=log.patient_id,
            log_date=log.log_date,
            deleted_by=deleted_by,
        )

        return True

    # ========================================================================
    # Statistics & Analytics
    # ========================================================================

    async def get_patient_statistics(
        self,
        patient_id: UUID,
        start_date: date,
        end_date: date,
    ) -> DailyLogStats:
        """
        Calculate statistics for a patient's daily logs

        Args:
            patient_id: Patient's user ID
            start_date: Start date for statistics
            end_date: End date for statistics

        Returns:
            DailyLogStats with aggregated data
        """
        # Get all logs in date range
        logs, total = await self.daily_log_repo.list_by_patient(
            patient_id=patient_id,
            start_date=start_date,
            end_date=end_date,
            skip=0,
            limit=10000,  # Get all logs for statistics
        )

        if total == 0:
            return DailyLogStats(
                total_logs=0,
                medication_adherence_rate=0.0,
                avg_water_intake_ml=0.0,
                avg_exercise_minutes=None,
                mood_distribution={"GOOD": 0, "NEUTRAL": 0, "BAD": 0},
                date_range={"start": start_date, "end": end_date},
            )

        # Calculate medication adherence
        adherence_rate = await self.daily_log_repo.get_medication_adherence(
            patient_id=patient_id,
            start_date=start_date,
            end_date=end_date,
        )

        # Calculate average water intake
        total_water = sum(log.water_intake_ml for log in logs)
        avg_water = total_water / total

        # Calculate average exercise minutes (excluding None values)
        exercise_logs = [log.exercise_minutes for log in logs if log.exercise_minutes is not None]
        avg_exercise = sum(exercise_logs) / len(exercise_logs) if exercise_logs else None

        # Mood distribution
        mood_distribution = {"GOOD": 0, "NEUTRAL": 0, "BAD": 0}
        for log in logs:
            if log.mood:
                mood_distribution[log.mood] = mood_distribution.get(log.mood, 0) + 1

        return DailyLogStats(
            total_logs=total,
            medication_adherence_rate=adherence_rate,
            avg_water_intake_ml=round(avg_water, 2),
            avg_exercise_minutes=round(avg_exercise, 2) if avg_exercise else None,
            mood_distribution=mood_distribution,
            date_range={"start": start_date, "end": end_date},
        )
