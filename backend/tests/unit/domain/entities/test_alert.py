"""
Unit tests for Alert Entity

Tests cover:
- Invariant validation (TD-003.1)
- Domain Events publishing (TD-003.3)
- Business logic (acknowledge, resolve, criticality checks)
- Factory methods (create)
- State machine transitions (ACTIVE → ACKNOWLEDGED → RESOLVED)
"""

from datetime import datetime
from uuid import uuid4

import pytest

from respira_ally.domain.entities.alert import (
    Alert,
    AlertAcknowledgedEvent,
    AlertResolvedEvent,
    AlertSeverity,
    AlertStatus,
    AlertTriggeredEvent,
    AlertType,
)
from respira_ally.domain.exceptions import BusinessRuleViolationError


class TestAlertCreation:
    """Test Alert creation and basic validation."""

    def test_create_high_risk_alert(self):
        """Test creating a HIGH risk alert."""
        alert = Alert.create(
            patient_id=uuid4(),
            alert_type=AlertType.HIGH_RISK_DETECTED,
            severity=AlertSeverity.HIGH,
            title="High Risk Detected",
            message="Patient CAT score indicates high risk",
        )

        assert alert.alert_id is not None
        assert alert.alert_type == AlertType.HIGH_RISK_DETECTED
        assert alert.severity == AlertSeverity.HIGH
        assert alert.status == AlertStatus.ACTIVE
        assert alert.title == "High Risk Detected"
        assert alert.message == "Patient CAT score indicates high risk"
        assert alert.acknowledged_at is None
        assert alert.resolved_at is None

        # Check domain events
        events = alert.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], AlertTriggeredEvent)
        assert events[0].alert_id == alert.alert_id
        assert events[0].alert_type == AlertType.HIGH_RISK_DETECTED
        assert events[0].severity == AlertSeverity.HIGH

    def test_create_critical_alert_with_metadata(self):
        """Test creating a CRITICAL alert with metadata."""
        metadata = {
            "cat_score": 35,
            "mmrc_grade": 4,
            "gold_group": "E",
        }

        alert = Alert.create(
            patient_id=uuid4(),
            alert_type=AlertType.EXACERBATION_RISK,
            severity=AlertSeverity.CRITICAL,
            title="Critical Exacerbation Risk",
            message="Patient shows critical COPD exacerbation risk",
            alert_metadata=metadata,
        )

        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.alert_metadata == metadata

    def test_title_cannot_be_empty(self):
        """Test that title cannot be empty."""
        with pytest.raises(BusinessRuleViolationError, match="Alert title cannot be empty"):
            Alert(
                alert_id=uuid4(),
                patient_id=uuid4(),
                alert_type=AlertType.HIGH_RISK_DETECTED,
                severity=AlertSeverity.HIGH,
                status=AlertStatus.ACTIVE,
                title="",
                message="Test message",
            )

    def test_title_cannot_exceed_200_chars(self):
        """Test that title cannot exceed 200 characters."""
        long_title = "A" * 201

        with pytest.raises(
            BusinessRuleViolationError,
            match="Alert title cannot exceed 200 characters",
        ):
            Alert(
                alert_id=uuid4(),
                patient_id=uuid4(),
                alert_type=AlertType.HIGH_RISK_DETECTED,
                severity=AlertSeverity.HIGH,
                status=AlertStatus.ACTIVE,
                title=long_title,
                message="Test message",
            )

    def test_message_cannot_be_empty(self):
        """Test that message cannot be empty."""
        with pytest.raises(BusinessRuleViolationError, match="Alert message cannot be empty"):
            Alert(
                alert_id=uuid4(),
                patient_id=uuid4(),
                alert_type=AlertType.HIGH_RISK_DETECTED,
                severity=AlertSeverity.HIGH,
                status=AlertStatus.ACTIVE,
                title="Test Title",
                message="",
            )

    def test_enum_auto_conversion_from_string(self):
        """Test that enum strings are automatically converted to enums."""
        alert = Alert(
            alert_id=uuid4(),
            patient_id=uuid4(),
            alert_type="HIGH_RISK_DETECTED",  # type: ignore
            severity="CRITICAL",  # type: ignore
            status="ACTIVE",  # type: ignore
            title="Test Alert",
            message="Test message",
        )

        assert alert.alert_type == AlertType.HIGH_RISK_DETECTED
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.status == AlertStatus.ACTIVE
        assert isinstance(alert.alert_type, AlertType)
        assert isinstance(alert.severity, AlertSeverity)
        assert isinstance(alert.status, AlertStatus)


class TestAlertAcknowledgement:
    """Test Alert acknowledgement workflow."""

    def test_acknowledge_active_alert(self):
        """Test acknowledging an ACTIVE alert."""
        alert = Alert.create(
            patient_id=uuid4(),
            alert_type=AlertType.HIGH_RISK_DETECTED,
            severity=AlertSeverity.HIGH,
            title="High Risk",
            message="Patient at high risk",
        )
        alert.clear_domain_events()  # Clear creation event

        therapist_id = uuid4()
        alert.acknowledge(therapist_id)

        assert alert.status == AlertStatus.ACKNOWLEDGED
        assert alert.acknowledged_at is not None
        assert alert.acknowledged_by == therapist_id

        # Check domain events
        events = alert.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], AlertAcknowledgedEvent)
        assert events[0].alert_id == alert.alert_id
        assert events[0].acknowledged_by == therapist_id
        assert events[0].previous_status == AlertStatus.ACTIVE

    def test_cannot_acknowledge_already_acknowledged_alert(self):
        """Test that already ACKNOWLEDGED alert cannot be acknowledged again."""
        alert = Alert.create(
            patient_id=uuid4(),
            alert_type=AlertType.HIGH_RISK_DETECTED,
            severity=AlertSeverity.HIGH,
            title="High Risk",
            message="Patient at high risk",
        )

        alert.acknowledge(uuid4())

        with pytest.raises(
            BusinessRuleViolationError,
            match="Cannot acknowledge alert in ACKNOWLEDGED status",
        ):
            alert.acknowledge(uuid4())

    def test_cannot_acknowledge_resolved_alert(self):
        """Test that RESOLVED alert cannot be acknowledged."""
        alert = Alert.create(
            patient_id=uuid4(),
            alert_type=AlertType.HIGH_RISK_DETECTED,
            severity=AlertSeverity.HIGH,
            title="High Risk",
            message="Patient at high risk",
        )

        alert.resolve(uuid4(), "Resolved by treatment")

        with pytest.raises(
            BusinessRuleViolationError,
            match="Cannot acknowledge alert in RESOLVED status",
        ):
            alert.acknowledge(uuid4())


class TestAlertResolution:
    """Test Alert resolution workflow."""

    def test_resolve_active_alert(self):
        """Test resolving an ACTIVE alert."""
        alert = Alert.create(
            patient_id=uuid4(),
            alert_type=AlertType.HIGH_RISK_DETECTED,
            severity=AlertSeverity.HIGH,
            title="High Risk",
            message="Patient at high risk",
        )
        alert.clear_domain_events()

        therapist_id = uuid4()
        resolution_notes = "Patient condition improved after treatment"
        alert.resolve(therapist_id, resolution_notes)

        assert alert.status == AlertStatus.RESOLVED
        assert alert.resolved_at is not None
        assert alert.resolved_by == therapist_id
        assert alert.resolution_notes == resolution_notes

        # Check domain events
        events = alert.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], AlertResolvedEvent)
        assert events[0].alert_id == alert.alert_id
        assert events[0].resolved_by == therapist_id
        assert events[0].resolution_notes == resolution_notes
        assert events[0].previous_status == AlertStatus.ACTIVE

    def test_resolve_acknowledged_alert(self):
        """Test resolving an ACKNOWLEDGED alert."""
        alert = Alert.create(
            patient_id=uuid4(),
            alert_type=AlertType.HIGH_RISK_DETECTED,
            severity=AlertSeverity.HIGH,
            title="High Risk",
            message="Patient at high risk",
        )

        alert.acknowledge(uuid4())
        alert.clear_domain_events()

        therapist_id = uuid4()
        alert.resolve(therapist_id, "Resolved")

        assert alert.status == AlertStatus.RESOLVED

        # Check domain events
        events = alert.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], AlertResolvedEvent)
        assert events[0].previous_status == AlertStatus.ACKNOWLEDGED

    def test_resolve_without_notes(self):
        """Test resolving alert without resolution notes."""
        alert = Alert.create(
            patient_id=uuid4(),
            alert_type=AlertType.HIGH_RISK_DETECTED,
            severity=AlertSeverity.HIGH,
            title="High Risk",
            message="Patient at high risk",
        )

        therapist_id = uuid4()
        alert.resolve(therapist_id)

        assert alert.status == AlertStatus.RESOLVED
        assert alert.resolution_notes is None

    def test_cannot_resolve_already_resolved_alert(self):
        """Test that already RESOLVED alert cannot be resolved again."""
        alert = Alert.create(
            patient_id=uuid4(),
            alert_type=AlertType.HIGH_RISK_DETECTED,
            severity=AlertSeverity.HIGH,
            title="High Risk",
            message="Patient at high risk",
        )

        alert.resolve(uuid4(), "Resolved")

        with pytest.raises(BusinessRuleViolationError, match="Alert is already resolved"):
            alert.resolve(uuid4(), "Resolved again")


class TestAlertBusinessLogic:
    """Test Alert business logic methods."""

    def test_is_critical(self):
        """Test is_critical() method."""
        critical_alert = Alert.create(
            patient_id=uuid4(),
            alert_type=AlertType.EXACERBATION_RISK,
            severity=AlertSeverity.CRITICAL,
            title="Critical Alert",
            message="Critical message",
        )

        high_alert = Alert.create(
            patient_id=uuid4(),
            alert_type=AlertType.HIGH_RISK_DETECTED,
            severity=AlertSeverity.HIGH,
            title="High Alert",
            message="High message",
        )

        assert critical_alert.is_critical()
        assert not high_alert.is_critical()

    def test_is_active(self):
        """Test is_active() method."""
        alert = Alert.create(
            patient_id=uuid4(),
            alert_type=AlertType.HIGH_RISK_DETECTED,
            severity=AlertSeverity.HIGH,
            title="High Risk",
            message="Patient at high risk",
        )

        assert alert.is_active()

        alert.resolve(uuid4())

        assert not alert.is_active()

    def test_requires_immediate_action_for_critical(self):
        """Test requires_immediate_action() for CRITICAL alert."""
        critical_alert = Alert.create(
            patient_id=uuid4(),
            alert_type=AlertType.EXACERBATION_RISK,
            severity=AlertSeverity.CRITICAL,
            title="Critical Alert",
            message="Critical message",
        )

        assert critical_alert.requires_immediate_action()

        critical_alert.resolve(uuid4())

        assert not critical_alert.requires_immediate_action()

    def test_requires_immediate_action_for_high(self):
        """Test requires_immediate_action() for HIGH alert."""
        high_alert = Alert.create(
            patient_id=uuid4(),
            alert_type=AlertType.HIGH_RISK_DETECTED,
            severity=AlertSeverity.HIGH,
            title="High Alert",
            message="High message",
        )

        assert high_alert.requires_immediate_action()

    def test_requires_immediate_action_for_medium(self):
        """Test requires_immediate_action() for MEDIUM alert."""
        medium_alert = Alert.create(
            patient_id=uuid4(),
            alert_type=AlertType.RISK_GROUP_CHANGE,
            severity=AlertSeverity.MEDIUM,
            title="Medium Alert",
            message="Medium message",
        )

        assert not medium_alert.requires_immediate_action()


class TestAlertDomainEvents:
    """Test Alert domain events management."""

    def test_get_domain_events_returns_copy(self):
        """Test that get_domain_events() returns a copy."""
        alert = Alert.create(
            patient_id=uuid4(),
            alert_type=AlertType.HIGH_RISK_DETECTED,
            severity=AlertSeverity.HIGH,
            title="High Risk",
            message="Patient at high risk",
        )

        events1 = alert.get_domain_events()
        events2 = alert.get_domain_events()

        assert events1 is not events2
        assert events1 == events2

    def test_clear_domain_events(self):
        """Test clearing domain events."""
        alert = Alert.create(
            patient_id=uuid4(),
            alert_type=AlertType.HIGH_RISK_DETECTED,
            severity=AlertSeverity.HIGH,
            title="High Risk",
            message="Patient at high risk",
        )

        assert len(alert.get_domain_events()) == 1

        alert.clear_domain_events()

        assert len(alert.get_domain_events()) == 0
