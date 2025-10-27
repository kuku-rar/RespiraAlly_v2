"""
Alert Rule Engine - Domain Service
Sprint 4: Alert System - Business rules for risk-based alerts

This is the core business logic for evaluating patient risk and generating alerts.
Following Linus's principle: "Bad programmers worry about code. Good ones worry about data structures."

Data Structure:
- Input: RiskAssessmentModel (patient's current risk state)
- Output: List[AlertCreate] (alerts that should be triggered)
- Rules: 3 fixed rules defined in MVP (see DEBT-001)

TODO(DEBT-001): MVP uses 3 hard-coded rules.
Full implementation: database-driven configurable rule engine.
"""

import logging
from datetime import date, timedelta

from respira_ally.core.schemas.alert import AlertCreate, AlertSeverity, AlertType
from respira_ally.infrastructure.database.models.risk_assessment import RiskAssessmentModel

logger = logging.getLogger(__name__)


class AlertRuleEngine:
    """
    Alert Rule Engine - Evaluate patient risk and generate alerts

    MVP Strategy (DEBT-001):
    - 3 fixed rules hard-coded in this class
    - No database-driven rule configuration
    - No rule priority or conflict resolution

    Rules:
    1. GOLD Group E → HIGH_RISK_DETECTED (CRITICAL severity)
    2. CAT Score >= 20 → HIGH_RISK_DETECTED (HIGH severity)
    3. 3+ exacerbations in 12m → EXACERBATION_RISK (MEDIUM severity)

    Design Philosophy (Linus):
    "Good taste means eliminating special cases." - All rules follow same evaluation pattern.
    """

    def __init__(self):
        """
        Initialize rule engine

        TODO(DEBT-001): MVP has no dependencies.
        Full implementation: inject RuleRepository to load rules from database.
        """
        pass

    async def evaluate(
        self, risk_assessment: RiskAssessmentModel
    ) -> list[AlertCreate]:
        """
        Evaluate all rules against patient's risk assessment

        Args:
            risk_assessment: Patient's current risk assessment

        Returns:
            List of alerts to be created (can be empty if no rules triggered)

        Design Note:
            This method returns a LIST, not a single alert, because multiple rules
            can trigger simultaneously. This is good data structure design - it handles
            both 0 alerts and N alerts with the same code path (no special cases).
        """
        alerts: list[AlertCreate] = []

        # Rule 1: GOLD Group E Detection (Highest Risk)
        if self._is_gold_group_e(risk_assessment):
            alerts.append(self._create_gold_e_alert(risk_assessment))

        # Rule 2: High CAT Score (Severe Symptom Burden)
        if self._is_high_cat_score(risk_assessment):
            alerts.append(self._create_high_cat_alert(risk_assessment))

        # Rule 3: Frequent Exacerbations (High Exacerbation Risk)
        if self._is_frequent_exacerbations(risk_assessment):
            alerts.append(self._create_frequent_exacerbation_alert(risk_assessment))

        logger.info(
            f"Alert evaluation for patient {risk_assessment.patient_id}: "
            f"triggered {len(alerts)} alert(s)"
        )

        return alerts

    # ========================================================================
    # Rule Evaluation Methods (Private)
    # ========================================================================

    def _is_gold_group_e(self, risk_assessment: RiskAssessmentModel) -> bool:
        """
        Rule 1: GOLD Group E indicates highest risk patient

        GOLD ABE Classification:
        - Group E: Highest risk (≥2 exacerbations OR ≥1 hospitalization in 12m)

        Returns:
            True if patient is in GOLD Group E
        """
        return risk_assessment.gold_group == "E"

    def _is_high_cat_score(self, risk_assessment: RiskAssessmentModel) -> bool:
        """
        Rule 2: CAT Score >= 20 indicates high symptom burden

        CAT (COPD Assessment Test) Score Ranges:
        - 0-10: Low impact
        - 11-20: Medium impact
        - 21-30: High impact
        - 31-40: Very high impact

        Threshold: >= 20 (High or Very High impact)

        Returns:
            True if CAT score >= 20
        """
        return risk_assessment.cat_score is not None and risk_assessment.cat_score >= 20

    def _is_frequent_exacerbations(self, risk_assessment: RiskAssessmentModel) -> bool:
        """
        Rule 3: 3+ exacerbations in last 12 months indicates high exacerbation risk

        Clinical Rationale:
        - Frequent exacerbations (≥3/year) predict future exacerbations
        - Require intensive monitoring and intervention

        Returns:
            True if patient had 3+ exacerbations in last 12 months
        """
        # Check if patient had 3+ exacerbations in last 12 months
        # This data comes from patient_profiles.exacerbation_count_12m
        # which is auto-updated by database trigger when exacerbations are created
        return risk_assessment.exacerbation_count_12m >= 3

    # ========================================================================
    # Alert Creation Methods (Private)
    # ========================================================================

    def _create_gold_e_alert(self, risk_assessment: RiskAssessmentModel) -> AlertCreate:
        """
        Create alert for GOLD Group E detection

        Severity: CRITICAL (highest risk group)
        """
        # Get metadata from risk assessment
        metadata = {
            "gold_group": risk_assessment.gold_group,
            "cat_score": risk_assessment.cat_score,
            "mmrc_grade": risk_assessment.mmrc_grade,
            "exacerbation_count_12m": risk_assessment.exacerbation_count_12m,
            "hospitalization_count_12m": risk_assessment.hospitalization_count_12m,
            "rule": "GOLD_GROUP_E",
            "trigger_date": date.today().isoformat(),
        }

        # Build detailed message
        exacerb_text = f"{risk_assessment.exacerbation_count_12m} exacerbation(s)"
        hosp_text = f"{risk_assessment.hospitalization_count_12m} hospitalization(s)"
        message = (
            f"Patient classified as GOLD Group E (Highest Risk). "
            f"In the last 12 months: {exacerb_text}, {hosp_text}. "
            f"CAT Score: {risk_assessment.cat_score or 'N/A'}, "
            f"mMRC Grade: {risk_assessment.mmrc_grade or 'N/A'}. "
            f"Requires intensive monitoring and treatment optimization."
        )

        return AlertCreate(
            patient_id=risk_assessment.patient_id,
            alert_type=AlertType.HIGH_RISK_DETECTED,
            severity=AlertSeverity.CRITICAL,
            title="GOLD Group E - Highest Risk Patient",
            message=message,
            alert_metadata=metadata,
        )

    def _create_high_cat_alert(self, risk_assessment: RiskAssessmentModel) -> AlertCreate:
        """
        Create alert for high CAT score

        Severity: HIGH (severe symptom burden)
        """
        metadata = {
            "cat_score": risk_assessment.cat_score,
            "gold_group": risk_assessment.gold_group,
            "rule": "HIGH_CAT_SCORE",
            "trigger_date": date.today().isoformat(),
        }

        # CAT score interpretation
        if risk_assessment.cat_score >= 30:
            impact_level = "Very High"
        else:  # 20-29
            impact_level = "High"

        message = (
            f"Patient has {impact_level} symptom burden (CAT Score: {risk_assessment.cat_score}). "
            f"GOLD Group: {risk_assessment.gold_group or 'N/A'}. "
            f"Symptoms significantly affecting daily life. "
            f"Consider reassessing treatment plan and symptom management strategies."
        )

        return AlertCreate(
            patient_id=risk_assessment.patient_id,
            alert_type=AlertType.HIGH_RISK_DETECTED,
            severity=AlertSeverity.HIGH,
            title=f"High Symptom Burden (CAT: {risk_assessment.cat_score})",
            message=message,
            alert_metadata=metadata,
        )

    def _create_frequent_exacerbation_alert(
        self, risk_assessment: RiskAssessmentModel
    ) -> AlertCreate:
        """
        Create alert for frequent exacerbations

        Severity: MEDIUM (clinical concern, requires intervention)
        """
        metadata = {
            "exacerbation_count_12m": risk_assessment.exacerbation_count_12m,
            "hospitalization_count_12m": risk_assessment.hospitalization_count_12m,
            "gold_group": risk_assessment.gold_group,
            "rule": "FREQUENT_EXACERBATIONS",
            "trigger_date": date.today().isoformat(),
        }

        # Calculate average days between exacerbations
        if risk_assessment.exacerbation_count_12m > 0:
            avg_days = 365 / risk_assessment.exacerbation_count_12m
        else:
            avg_days = 365

        message = (
            f"Patient experienced {risk_assessment.exacerbation_count_12m} exacerbations "
            f"in the last 12 months (average: every {avg_days:.0f} days). "
            f"{risk_assessment.hospitalization_count_12m} required hospitalization. "
            f"Frequent exacerbations increase risk of lung function decline. "
            f"Review prevention strategies and medication adherence."
        )

        return AlertCreate(
            patient_id=risk_assessment.patient_id,
            alert_type=AlertType.EXACERBATION_RISK,
            severity=AlertSeverity.MEDIUM,
            title=f"Frequent Exacerbations ({risk_assessment.exacerbation_count_12m} in 12 months)",
            message=message,
            alert_metadata=metadata,
        )
