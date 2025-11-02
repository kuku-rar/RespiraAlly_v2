"""
Alert Domain Entity - Risk-based Alert System
Sprint 4: Alert System - Domain logic for alert lifecycle management

This Entity represents the business logic and invariants for alerts.
Following Clean Architecture and Linus "Good Taste" principles.

Business Rules (TD-003.1):
1. Status transitions: ACTIVE � ACKNOWLEDGED � RESOLVED (irreversible)
2. Cannot acknowledge/resolve an alert twice
3. Acknowledged/resolved timestamps must follow logical order
4. Only valid AlertType, AlertSeverity, AlertStatus allowed
5. Title (1-200 chars), message (non-empty) required

Domain Events (TD-003.3):
- AlertTriggeredEvent: When alert is created
- AlertAcknowledgedEvent: When therapist acknowledges
- AlertResolvedEvent: When alert is resolved
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from respira_ally.domain.events.base import DomainEvent
from respira_ally.domain.exceptions import BusinessRuleViolationError


# ============================================================================
# Alert Enums
# ============================================================================


class AlertType(str, Enum):
    """Alert types triggered by risk assessment engine"""

    RISK_GROUP_CHANGE = "RISK_GROUP_CHANGE"
    HIGH_RISK_DETECTED = "HIGH_RISK_DETECTED"
    EXACERBATION_RISK = "EXACERBATION_RISK"


class AlertSeverity(str, Enum):
    """Alert severity levels - determines priority and urgency"""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(str, Enum):
    """Alert lifecycle status - defines state machine"""

    ACTIVE = "ACTIVE"  # Initial state: alert triggered
    ACKNOWLEDGED = "ACKNOWLEDGED"  # Therapist has seen the alert
    RESOLVED = "RESOLVED"  # Alert has been addressed/resolved


# ============================================================================
# Domain Events
# ============================================================================


@dataclass(frozen=True)
class AlertTriggeredEvent(DomainEvent):
    """Emitted when an alert is triggered by the risk engine"""

    alert_id: UUID
    patient_id: UUID
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    triggered_at: datetime


@dataclass(frozen=True)
class AlertAcknowledgedEvent(DomainEvent):
    """Emitted when a therapist acknowledges an alert"""

    alert_id: UUID
    patient_id: UUID
    acknowledged_by: UUID
    acknowledged_at: datetime
    previous_status: AlertStatus


@dataclass(frozen=True)
class AlertResolvedEvent(DomainEvent):
    """Emitted when an alert is resolved"""

    alert_id: UUID
    patient_id: UUID
    resolved_by: UUID
    resolved_at: datetime
    resolution_notes: Optional[str]
    previous_status: AlertStatus


# ============================================================================
# Alert Entity
# ============================================================================


@dataclass
class Alert:
    """
    Alert Domain Entity - Represents risk-based alerts for patients

    Linus "Good Taste" Principles Applied:
    1. Eliminates special cases: State machine handles all transitions uniformly
    2. Single source of truth: Status determines allowed operations
    3. No nested complexity: Validation in __post_init__, business logic in methods
    4. Clear data structure: All state in simple fields, no hidden state

    Business Rules:
    - Cannot acknowledge ACKNOWLEDGED or RESOLVED alerts
    - Cannot resolve RESOLVED alerts
    - Timestamps must be logical: triggered < acknowledged < resolved
    - Domain events published for all state transitions
    """

    # Identifiers
    alert_id: UUID
    patient_id: UUID

    # Alert Classification
    alert_type: AlertType
    severity: AlertSeverity
    status: AlertStatus

    # Alert Content
    title: str
    message: str
    alert_metadata: Optional[dict] = None

    # Workflow Fields
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[UUID] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[UUID] = None
    resolution_notes: Optional[str] = None

    # Timestamps
    triggered_at: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain Events (not persisted)
    _domain_events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        """
        Validate invariants after initialization (TD-003.1)

        Linus "Good Taste": All validation in one place, no scattered checks.
        """
        # Validate alert_type
        if not isinstance(self.alert_type, AlertType):
            if isinstance(self.alert_type, str):
                try:
                    self.alert_type = AlertType(self.alert_type)
                except ValueError:
                    raise BusinessRuleViolationError(
                        f"Invalid alert_type. Must be one of {[t.value for t in AlertType]}"
                    )
            else:
                raise BusinessRuleViolationError("alert_type must be AlertType enum or string")

        # Validate severity
        if not isinstance(self.severity, AlertSeverity):
            if isinstance(self.severity, str):
                try:
                    self.severity = AlertSeverity(self.severity)
                except ValueError:
                    raise BusinessRuleViolationError(
                        f"Invalid severity. Must be one of {[s.value for s in AlertSeverity]}"
                    )
            else:
                raise BusinessRuleViolationError("severity must be AlertSeverity enum or string")

        # Validate status
        if not isinstance(self.status, AlertStatus):
            if isinstance(self.status, str):
                try:
                    self.status = AlertStatus(self.status)
                except ValueError:
                    raise BusinessRuleViolationError(
                        f"Invalid status. Must be one of {[s.value for s in AlertStatus]}"
                    )
            else:
                raise BusinessRuleViolationError("status must be AlertStatus enum or string")

        # Validate title
        if not self.title or not self.title.strip():
            raise BusinessRuleViolationError("Alert title cannot be empty")
        if len(self.title) > 200:
            raise BusinessRuleViolationError("Alert title cannot exceed 200 characters")

        # Validate message
        if not self.message or not self.message.strip():
            raise BusinessRuleViolationError("Alert message cannot be empty")

        # Validate workflow consistency
        self._validate_workflow_consistency()

    def _validate_workflow_consistency(self) -> None:
        """
        Validate consistency of workflow fields

        Business Rule: Timestamps and user IDs must match status
        """
        if self.status == AlertStatus.ACKNOWLEDGED:
            if not self.acknowledged_at:
                raise BusinessRuleViolationError(
                    "ACKNOWLEDGED status requires acknowledged_at timestamp"
                )
            if not self.acknowledged_by:
                raise BusinessRuleViolationError(
                    "ACKNOWLEDGED status requires acknowledged_by user ID"
                )

        if self.status == AlertStatus.RESOLVED:
            if not self.resolved_at:
                raise BusinessRuleViolationError("RESOLVED status requires resolved_at timestamp")
            if not self.resolved_by:
                raise BusinessRuleViolationError("RESOLVED status requires resolved_by user ID")

        # Validate timestamp order
        if self.acknowledged_at and self.acknowledged_at < self.triggered_at:
            raise BusinessRuleViolationError(
                "acknowledged_at cannot be earlier than triggered_at"
            )

        if self.resolved_at:
            if self.resolved_at < self.triggered_at:
                raise BusinessRuleViolationError("resolved_at cannot be earlier than triggered_at")
            if self.acknowledged_at and self.resolved_at < self.acknowledged_at:
                raise BusinessRuleViolationError(
                    "resolved_at cannot be earlier than acknowledged_at"
                )

    # ========================================================================
    # Business Logic Methods
    # ========================================================================

    def acknowledge(self, user_id: UUID) -> None:
        """
        Acknowledge this alert

        Business Rules:
        - Can only acknowledge ACTIVE alerts
        - Cannot acknowledge already ACKNOWLEDGED or RESOLVED alerts
        - Sets acknowledged_at, acknowledged_by, and updates status

        Args:
            user_id: UUID of the user (therapist) acknowledging this alert

        Raises:
            BusinessRuleViolationError: If alert cannot be acknowledged

        Publishes:
            AlertAcknowledgedEvent
        """
        if self.status != AlertStatus.ACTIVE:
            raise BusinessRuleViolationError(
                f"Cannot acknowledge alert in {self.status.value} status. "
                f"Only ACTIVE alerts can be acknowledged."
            )

        previous_status = self.status
        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_at = datetime.utcnow()
        self.acknowledged_by = user_id
        self.updated_at = datetime.utcnow()

        # Publish domain event (TD-003.3)
        self._add_domain_event(
            AlertAcknowledgedEvent(
                alert_id=self.alert_id,
                patient_id=self.patient_id,
                acknowledged_by=user_id,
                acknowledged_at=self.acknowledged_at,
                previous_status=previous_status,
            )
        )

    def resolve(self, user_id: UUID, resolution_notes: Optional[str] = None) -> None:
        """
        Resolve this alert

        Business Rules:
        - Can resolve ACTIVE or ACKNOWLEDGED alerts
        - Cannot resolve already RESOLVED alerts
        - Sets resolved_at, resolved_by, resolution_notes, and updates status

        Args:
            user_id: UUID of the user (therapist) resolving this alert
            resolution_notes: Optional notes about the resolution

        Raises:
            BusinessRuleViolationError: If alert cannot be resolved

        Publishes:
            AlertResolvedEvent
        """
        if self.status == AlertStatus.RESOLVED:
            raise BusinessRuleViolationError("Alert is already resolved")

        previous_status = self.status
        self.status = AlertStatus.RESOLVED
        self.resolved_at = datetime.utcnow()
        self.resolved_by = user_id
        self.resolution_notes = resolution_notes
        self.updated_at = datetime.utcnow()

        # Publish domain event (TD-003.3)
        self._add_domain_event(
            AlertResolvedEvent(
                alert_id=self.alert_id,
                patient_id=self.patient_id,
                resolved_by=user_id,
                resolved_at=self.resolved_at,
                resolution_notes=resolution_notes,
                previous_status=previous_status,
            )
        )

    def is_critical(self) -> bool:
        """Check if this alert has CRITICAL severity"""
        return self.severity == AlertSeverity.CRITICAL

    def is_active(self) -> bool:
        """Check if this alert is still active (not resolved)"""
        return self.status != AlertStatus.RESOLVED

    def requires_immediate_action(self) -> bool:
        """
        Check if alert requires immediate action

        Business Logic:
        - CRITICAL or HIGH severity AND still ACTIVE
        """
        return self.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH] and self.is_active()

    # ========================================================================
    # Domain Events Management (TD-003.3)
    # ========================================================================

    def _add_domain_event(self, event: DomainEvent) -> None:
        """Add domain event to internal list (not persisted)"""
        self._domain_events.append(event)

    def get_domain_events(self) -> list[DomainEvent]:
        """Get all domain events for Application Service to publish"""
        return self._domain_events.copy()

    def clear_domain_events(self) -> None:
        """Clear domain events after Application Service publishes them"""
        self._domain_events.clear()

    # ========================================================================
    # Factory Methods
    # ========================================================================

    @classmethod
    def create(
        cls,
        patient_id: UUID,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        message: str,
        alert_metadata: Optional[dict] = None,
    ) -> "Alert":
        """
        Factory method to create a new alert

        Automatically publishes AlertTriggeredEvent

        Linus "Good Taste": Factory eliminates special case initialization code.
        All alerts created through this method follow same pattern.
        """
        alert = cls(
            alert_id=uuid4(),
            patient_id=patient_id,
            alert_type=alert_type,
            severity=severity,
            status=AlertStatus.ACTIVE,
            title=title,
            message=message,
            alert_metadata=alert_metadata,
        )

        # Publish domain event (TD-003.3)
        alert._add_domain_event(
            AlertTriggeredEvent(
                alert_id=alert.alert_id,
                patient_id=patient_id,
                alert_type=alert_type,
                severity=severity,
                title=title,
                triggered_at=alert.triggered_at,
            )
        )

        return alert

    def __repr__(self) -> str:
        return (
            f"<Alert(id={self.alert_id}, "
            f"patient={self.patient_id}, "
            f"type={self.alert_type.value}, "
            f"severity={self.severity.value}, "
            f"status={self.status.value})>"
        )
