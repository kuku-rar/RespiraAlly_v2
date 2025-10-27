"""
Task Priority Calculator - Domain Service
Sprint 5: Task Management System - Calculate task priority from alerts

Design Philosophy (Linus):
"Good programmers worry about data structures and their relationships."

This service calculates Task priority based on Alert severity and Risk Assessment data.
It implements business rules for priority determination.

Business Rules:
1. Direct Mapping: Alert severity → Task priority (CRITICAL, HIGH, MEDIUM, LOW)
2. Special Rule: GOLD Group E → Task priority ≥ HIGH (regardless of alert severity)
3. Special Rule: HIGH_RISK_DETECTED → Task priority = CRITICAL

Design Note:
    This is a pure function (no side effects, no database access).
    All logic is deterministic based on input data.
"""

import logging
from typing import Optional

from respira_ally.core.schemas.task import TaskPriority
from respira_ally.infrastructure.database.models.alert import AlertModel
from respira_ally.infrastructure.database.models.risk_assessment import RiskAssessmentModel

logger = logging.getLogger(__name__)


class TaskPriorityCalculator:
    """
    Calculate Task priority from Alert and Risk Assessment data

    Design Philosophy:
    - Simple, deterministic mapping
    - No special cases (eliminate if/else where possible)
    - Priority rules encoded as data, not code
    """

    # Priority Mapping: Alert severity → Task priority
    _SEVERITY_TO_PRIORITY = {
        "CRITICAL": TaskPriority.CRITICAL,
        "HIGH": TaskPriority.HIGH,
        "MEDIUM": TaskPriority.MEDIUM,
        "LOW": TaskPriority.LOW,
    }

    def calculate(
        self,
        alert: AlertModel,
        risk_assessment: Optional[RiskAssessmentModel] = None,
    ) -> TaskPriority:
        """
        Calculate Task priority from Alert and Risk Assessment

        Args:
            alert: Alert that triggered task creation
            risk_assessment: Optional risk assessment (for GOLD group check)

        Returns:
            TaskPriority enum value

        Business Rules Applied:
        1. Direct mapping from alert severity
        2. If GOLD Group E detected → upgrade to at least HIGH
        3. If HIGH_RISK_DETECTED alert type → upgrade to CRITICAL

        Design Note:
            Using dictionary lookup instead of if/else chain.
            This is "good taste" - no special cases, just data transformation.
        """
        # Rule 1: Direct mapping from alert severity
        base_priority = self._SEVERITY_TO_PRIORITY.get(
            alert.severity, TaskPriority.MEDIUM  # Default fallback
        )

        # Rule 2: GOLD Group E → upgrade to HIGH
        if risk_assessment and self._is_gold_group_e(risk_assessment):
            if base_priority in [TaskPriority.LOW, TaskPriority.MEDIUM]:
                logger.info(
                    f"Upgrading task priority to HIGH for GOLD Group E patient {alert.patient_id}"
                )
                base_priority = TaskPriority.HIGH

        # Rule 3: HIGH_RISK_DETECTED alert → upgrade to CRITICAL
        if alert.alert_type == "HIGH_RISK_DETECTED":
            if base_priority != TaskPriority.CRITICAL:
                logger.info(
                    f"Upgrading task priority to CRITICAL for HIGH_RISK_DETECTED alert {alert.alert_id}"
                )
                base_priority = TaskPriority.CRITICAL

        return base_priority

    def _is_gold_group_e(self, risk_assessment: RiskAssessmentModel) -> bool:
        """
        Check if patient is GOLD Group E (highest risk)

        Args:
            risk_assessment: Risk assessment to check

        Returns:
            True if GOLD Group E, False otherwise

        Design Note:
            Private method because this is an implementation detail.
            Encapsulates GOLD group check logic.
        """
        return risk_assessment.gold_group == "E"

    def get_priority_reason(
        self,
        alert: AlertModel,
        final_priority: TaskPriority,
        risk_assessment: Optional[RiskAssessmentModel] = None,
    ) -> str:
        """
        Generate human-readable explanation for priority determination

        Args:
            alert: Alert that triggered task creation
            final_priority: Final calculated priority
            risk_assessment: Optional risk assessment

        Returns:
            String explaining priority reasoning

        Design Note:
            Useful for task metadata and debugging.
            Helps therapists understand why a task has specific priority.
        """
        base_priority = self._SEVERITY_TO_PRIORITY.get(alert.severity, TaskPriority.MEDIUM)

        reasons = [f"Alert severity: {alert.severity}"]

        if risk_assessment and self._is_gold_group_e(risk_assessment):
            reasons.append("Patient is GOLD Group E (highest risk)")

        if alert.alert_type == "HIGH_RISK_DETECTED":
            reasons.append("High risk detected alert")

        if final_priority != base_priority:
            reasons.append(f"Priority upgraded from {base_priority.value} to {final_priority.value}")

        return " | ".join(reasons)
