"""
Alert Service - Application Layer
Sprint 4: Alert System - Business logic for alert management

This service coordinates between:
- Domain Layer: AlertRuleEngine (business rules)
- Infrastructure Layer: AlertRepository (data persistence)

MVP Responsibilities:
- Create alerts triggered by risk assessments
- Retrieve alerts for patients
- Count active alerts

TODO(DEBT-001): MVP is read-only (no acknowledgment/resolution).
Full implementation: Add workflow methods (acknowledge, resolve).
"""

import logging
from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.core.schemas.alert import AlertCreate, AlertListResponse, AlertResponse
from respira_ally.domain.repositories.alert_repository import AlertRepository
from respira_ally.domain.services.alert_rule_engine import AlertRuleEngine
from respira_ally.infrastructure.database.models.alert import AlertModel
from respira_ally.infrastructure.database.models.risk_assessment import RiskAssessmentModel
from respira_ally.infrastructure.repository_impls.alert_repository_impl import AlertRepositoryImpl

logger = logging.getLogger(__name__)


class AlertService:
    """
    Alert Service - Coordinate alert creation and retrieval

    Design Philosophy (Linus):
    "Good programmers worry about data structures and their relationships."

    Data Flow:
    1. Risk Assessment → AlertRuleEngine → List[AlertCreate]
    2. AlertCreate → AlertRepository → AlertModel (persisted)
    3. AlertModel → AlertResponse (API)

    This service is the "glue code" that coordinates these transformations.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize alert service

        Args:
            db: Database session (async)

        Design Note:
            Dependency injection via constructor. AlertRepository and AlertRuleEngine
            are created here (not injected) because they have no external dependencies.
            This is simpler than over-engineering with dependency injection containers.
        """
        self.db = db
        self.repository: AlertRepository = AlertRepositoryImpl(db)
        self.rule_engine = AlertRuleEngine()

    async def create_alerts_from_risk_assessment(
        self, risk_assessment: RiskAssessmentModel
    ) -> list[AlertResponse]:
        """
        Evaluate risk assessment and create alerts based on triggered rules

        This is the PRIMARY method called by CalculateRiskUseCase.

        Args:
            risk_assessment: Patient's current risk assessment

        Returns:
            List of created alerts (can be empty if no rules triggered)

        Design Note:
            Returns list of AlertResponse (not AlertCreate) because the alerts
            are already persisted. This avoids "half-created" state in the API layer.
        """
        # Step 1: Evaluate rules (Domain Logic)
        alert_creates = await self.rule_engine.evaluate(risk_assessment)

        if not alert_creates:
            logger.info(
                f"No alert rules triggered for patient {risk_assessment.patient_id}"
            )
            return []

        # Step 2: Persist alerts (Infrastructure)
        created_alerts: list[AlertModel] = []
        for alert_create in alert_creates:
            # Convert AlertCreate (schema) → AlertModel (database entity)
            alert_model = AlertModel(
                patient_id=alert_create.patient_id,
                alert_type=alert_create.alert_type.value,
                severity=alert_create.severity.value,
                title=alert_create.title,
                message=alert_create.message,
                alert_metadata=alert_create.alert_metadata,
                status="ACTIVE",  # All new alerts start as ACTIVE
            )

            alert = await self.repository.create(alert_model)
            created_alerts.append(alert)

        logger.info(
            f"Created {len(created_alerts)} alert(s) for patient {risk_assessment.patient_id}"
        )

        # Step 3: AUTO-GENERATE TASKS from alerts (Phase B4)
        from respira_ally.application.task.task_service import TaskService
        task_service = TaskService(self.db)
        tasks_created = 0
        for alert in created_alerts:
            try:
                await task_service.create_task_from_alert(alert, risk_assessment)
                tasks_created += 1
            except Exception as e:
                logger.error(f"Failed to auto-generate task for alert {alert.alert_id}: {e}", exc_info=True)
        if tasks_created > 0:
            logger.info(f"Auto-generated {tasks_created} task(s) for patient {risk_assessment.patient_id}")

        # Step 4: Convert to response schemas
        return [self._to_response(alert) for alert in created_alerts]

    async def get_alert_by_id(self, alert_id: UUID) -> AlertResponse | None:
        """
        Get single alert by ID

        Args:
            alert_id: Alert UUID

        Returns:
            AlertResponse if found, None otherwise
        """
        alert = await self.repository.get_by_id(alert_id)
        if not alert:
            return None

        return self._to_response(alert)

    async def list_patient_alerts(
        self,
        patient_id: UUID,
        page: int = 0,
        page_size: int = 20,
        # Filters
        alert_type: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        sort_by: str = "triggered_at",
        sort_order: str = "desc",
    ) -> AlertListResponse:
        """
        List alerts for a patient with filters and pagination

        Args:
            patient_id: Patient UUID
            page: Page number (0-indexed)
            page_size: Number of items per page
            alert_type: Filter by alert type
            severity: Filter by severity
            status: Filter by status
            start_date: Filter by triggered_at >= start_date
            end_date: Filter by triggered_at <= end_date
            sort_by: Sort field
            sort_order: Sort order (asc/desc)

        Returns:
            AlertListResponse with paginated results
        """
        # Get paginated results from repository
        alerts, total = await self.repository.list_by_patient(
            patient_id=patient_id,
            skip=page * page_size,
            limit=page_size,
            alert_type=alert_type,
            severity=severity,
            status=status,
            start_date=start_date,
            end_date=end_date,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        # Convert to response schemas
        alert_responses = [self._to_response(alert) for alert in alerts]

        return AlertListResponse(
            alerts=alert_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,  # Ceiling division
        )

    async def count_active_alerts(self, patient_id: UUID) -> int:
        """
        Count active alerts for a patient

        Args:
            patient_id: Patient UUID

        Returns:
            Number of active alerts

        Use Case:
            Dashboard badge: "You have 3 active alerts"
        """
        return await self.repository.count_active_by_patient(patient_id)

    def _to_response(self, alert: AlertModel) -> AlertResponse:
        """
        Convert AlertModel to AlertResponse

        Args:
            alert: Database model

        Returns:
            API response schema

        Design Note:
            Private method because this is an implementation detail.
            The conversion is simple data transformation, no business logic.
        """
        return AlertResponse(
            alert_id=alert.alert_id,
            patient_id=alert.patient_id,
            alert_type=alert.alert_type,
            severity=alert.severity,
            status=alert.status,
            title=alert.title,
            message=alert.message,
            alert_metadata=alert.alert_metadata,
            acknowledged_at=(
                alert.acknowledged_at.isoformat() if alert.acknowledged_at else None
            ),
            acknowledged_by=alert.acknowledged_by,
            resolved_at=alert.resolved_at.isoformat() if alert.resolved_at else None,
            resolved_by=alert.resolved_by,
            resolution_notes=alert.resolution_notes,
            triggered_at=alert.triggered_at.isoformat(),
            created_at=alert.created_at.isoformat(),
            updated_at=alert.updated_at.isoformat(),
        )
