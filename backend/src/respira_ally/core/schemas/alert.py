"""
Alert Schemas
Pydantic models for Alert System API endpoints

Sprint 4: Alert System - Risk-based alert and notification system
MVP Strategy: Read-only API (alerts created automatically by risk engine)
"""

from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Alert Enums
# ============================================================================


class AlertType(str, Enum):
    """
    Alert types triggered by risk assessment engine

    TODO(DEBT-001): MVP uses 3 fixed types.
    Full implementation: extensible alert type system from database.
    """

    RISK_GROUP_CHANGE = "RISK_GROUP_CHANGE"  # GOLD group change detected
    HIGH_RISK_DETECTED = "HIGH_RISK_DETECTED"  # High risk (Group E) detected
    EXACERBATION_RISK = "EXACERBATION_RISK"  # Exacerbation risk detected


class AlertSeverity(str, Enum):
    """Alert severity levels"""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(str, Enum):
    """
    Alert lifecycle status

    TODO(DEBT-001): MVP only uses ACTIVE status.
    Full implementation: ACKNOWLEDGED, RESOLVED status transitions.
    """

    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


# ============================================================================
# Alert Request Schemas (Internal Use Only)
# ============================================================================


class AlertCreate(BaseModel):
    """
    Internal schema for creating alerts (not exposed via API)

    TODO(DEBT-001): MVP - Alerts are ONLY created by risk assessment engine.
    No POST /api/v1/alerts/ endpoint in MVP.
    Full implementation: Allow therapists to manually create alerts.
    """

    model_config = ConfigDict(from_attributes=True)

    # Required fields
    patient_id: UUID = Field(..., description="Patient UUID")
    alert_type: AlertType = Field(..., description="Alert type")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    title: str = Field(..., max_length=200, description="Alert title (short description)")
    message: str = Field(..., description="Alert detailed message")

    # Optional metadata
    alert_metadata: dict | None = Field(
        None,
        description="JSON metadata (e.g., {old_group: 'A', new_group: 'E', trigger_reason: '...'})",
    )


# ============================================================================
# Alert Response Schemas
# ============================================================================


class AlertResponse(BaseModel):
    """
    Alert response schema for API endpoints

    MVP: Read-only fields
    Full implementation: Add acknowledgment/resolution actions
    """

    model_config = ConfigDict(from_attributes=True)

    # Core fields
    alert_id: UUID = Field(..., description="Alert UUID")
    patient_id: UUID = Field(..., description="Patient UUID")
    alert_type: AlertType = Field(..., description="Alert type")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    status: AlertStatus = Field(..., description="Alert status")

    # Alert content
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert detailed message")
    alert_metadata: dict | None = Field(None, description="Additional alert metadata (JSON)")

    # Workflow fields (for future use)
    # TODO(DEBT-001): MVP doesn't use these fields, but they're in the database
    acknowledged_at: str | None = Field(None, description="Acknowledgement timestamp (ISO 8601)")
    acknowledged_by: UUID | None = Field(None, description="User who acknowledged this alert")
    resolved_at: str | None = Field(None, description="Resolution timestamp (ISO 8601)")
    resolved_by: UUID | None = Field(None, description="User who resolved this alert")
    resolution_notes: str | None = Field(None, description="Resolution notes")

    # Timestamps
    triggered_at: str = Field(..., description="Alert trigger timestamp (ISO 8601)")
    created_at: str = Field(..., description="Creation timestamp (ISO 8601)")
    updated_at: str = Field(..., description="Last update timestamp (ISO 8601)")


class AlertListResponse(BaseModel):
    """
    Paginated alert list response

    Used for GET /api/v1/alerts/patients/{patient_id}/ endpoint
    """

    model_config = ConfigDict(from_attributes=True)

    alerts: list[AlertResponse] = Field(..., description="List of alerts")
    total: int = Field(..., description="Total number of alerts matching filters")
    page: int = Field(..., description="Current page number (0-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


# ============================================================================
# Alert Statistics Schemas (Future Use)
# ============================================================================


class AlertStats(BaseModel):
    """
    Alert statistics for a patient

    TODO(DEBT-001): Not implemented in MVP.
    Full implementation: Alert analytics dashboard for therapists.
    """

    model_config = ConfigDict(from_attributes=True)

    patient_id: UUID
    total_alerts: int = Field(..., description="Total alerts all-time")
    active_alerts: int = Field(..., description="Currently active alerts")
    acknowledged_alerts: int = Field(..., description="Acknowledged but unresolved alerts")
    resolved_alerts: int = Field(..., description="Resolved alerts")

    # Severity breakdown
    critical_count: int = Field(0, description="Number of CRITICAL severity alerts")
    high_count: int = Field(0, description="Number of HIGH severity alerts")
    medium_count: int = Field(0, description="Number of MEDIUM severity alerts")
    low_count: int = Field(0, description="Number of LOW severity alerts")

    # Last alert
    last_alert_date: datetime | None = Field(None, description="Last alert triggered date")
    last_alert_type: AlertType | None = Field(None, description="Last alert type")
