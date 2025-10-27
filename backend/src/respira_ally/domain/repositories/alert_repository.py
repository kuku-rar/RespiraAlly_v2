"""
Alert Repository Interface
Domain Layer - Clean Architecture

This is the abstract repository interface that defines the contract
for alert data operations. The actual implementation is in the
Infrastructure Layer.

Sprint 4: Alert System MVP
TODO(DEBT-001): MVP provides read-only operations.
Full implementation: Add acknowledgment/resolution operations.
"""

from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from respira_ally.infrastructure.database.models.alert import AlertModel


class AlertRepository(ABC):
    """
    Abstract base class for Alert data access

    Following the Dependency Inversion Principle, the Domain Layer
    defines the interface, and the Infrastructure Layer implements it.

    MVP Operations (DEBT-001):
    - create: Create alerts (triggered by risk engine)
    - get_by_id: Get single alert
    - list_by_patient: List patient's alerts with filters
    - count_active_by_patient: Count active alerts

    Deferred Operations (Full Implementation):
    - acknowledge_alert
    - resolve_alert
    - update_status
    - get_analytics
    """

    @abstractmethod
    async def create(self, alert: AlertModel) -> AlertModel:
        """
        Create a new alert record

        Args:
            alert: AlertModel instance to persist

        Returns:
            AlertModel: The created alert with database-generated fields

        Note:
            In MVP, this is only called by risk assessment engine,
            not exposed via public API.
        """
        pass

    @abstractmethod
    async def get_by_id(self, alert_id: UUID) -> AlertModel | None:
        """
        Retrieve alert by ID

        Args:
            alert_id: Alert UUID

        Returns:
            AlertModel if found, None otherwise
        """
        pass

    @abstractmethod
    async def list_by_patient(
        self,
        patient_id: UUID,
        skip: int = 0,
        limit: int = 20,
        # Filters
        alert_type: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        sort_by: str = "triggered_at",
        sort_order: str = "desc",
    ) -> tuple[list[AlertModel], int]:
        """
        List alerts for a specific patient with filters and pagination

        Args:
            patient_id: Patient UUID
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            alert_type: Filter by alert type (RISK_GROUP_CHANGE, HIGH_RISK_DETECTED, EXACERBATION_RISK)
            severity: Filter by severity (LOW, MEDIUM, HIGH, CRITICAL)
            status: Filter by status (ACTIVE, ACKNOWLEDGED, RESOLVED)
            start_date: Filter by triggered_at >= start_date
            end_date: Filter by triggered_at <= end_date
            sort_by: Sort field (triggered_at, severity, created_at)
            sort_order: Sort order (asc, desc)

        Returns:
            Tuple of (list of alerts, total count)

        Design Note:
            Returns tuple (list, count) not a wrapper object.
            Linus principle: "Keep data structures simple and code will follow naturally."
        """
        pass

    @abstractmethod
    async def count_active_by_patient(self, patient_id: UUID) -> int:
        """
        Count active alerts for a patient

        Args:
            patient_id: Patient UUID

        Returns:
            Number of active (not acknowledged/resolved) alerts

        Use Case:
            Dashboard badge: "You have 3 active alerts"
        """
        pass

    @abstractmethod
    async def exists(self, alert_id: UUID) -> bool:
        """
        Check if alert exists

        Args:
            alert_id: Alert UUID

        Returns:
            True if alert exists, False otherwise
        """
        pass

    # ========================================================================
    # Future Operations (DEBT-001: Deferred to Full Implementation)
    # ========================================================================
    # These methods are not implemented in MVP but defined in interface
    # for future backward-compatible extension.

    # async def acknowledge_alert(self, alert_id: UUID, acknowledged_by: UUID) -> AlertModel | None:
    #     """Acknowledge alert (mark as seen by therapist)"""
    #     pass

    # async def resolve_alert(
    #     self, alert_id: UUID, resolved_by: UUID, notes: str
    # ) -> AlertModel | None:
    #     """Resolve alert (mark as handled with resolution notes)"""
    #     pass

    # async def update_status(
    #     self, alert_id: UUID, status: str
    # ) -> AlertModel | None:
    #     """Update alert status (ACTIVE ’ ACKNOWLEDGED ’ RESOLVED)"""
    #     pass
