"""
RiskScore Domain Entity - COPD Risk Assessment
Sprint 4: Risk Engine - GOLD ABE Classification System

This Entity represents the business logic and invariants for COPD risk assessment.
Following Clean Architecture and Linus "Good Taste" principles.

Business Rules (TD-003.1):
1. CAT score must be 0-40
2. mMRC grade must be 0-4
3. gold_group must be A, B, or E
4. Risk score (if provided) must be 0-100
5. Exacerbation/hospitalization counts must be >= 0

Domain Events (TD-003.3):
- RiskAssessmentCreatedEvent: When assessment is created
- RiskGroupChangedEvent: When GOLD group changes
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Literal, Optional
from uuid import UUID, uuid4

from respira_ally.domain.events.base import DomainEvent
from respira_ally.domain.exceptions import BusinessRuleViolationError


# ============================================================================
# Risk Enums
# ============================================================================


class GoldGroup(str, Enum):
    """GOLD ABE Classification Groups"""

    A = "A"  # Low risk: CAT<10 AND mMRC<2
    B = "B"  # Medium risk: CAT>=10 OR mMRC>=2
    E = "E"  # High risk: CAT>=10 AND mMRC>=2 (with exacerbations)


RiskLevel = Literal["low", "medium", "high", "critical"]


# ============================================================================
# Domain Events
# ============================================================================


@dataclass(frozen=True)
class RiskAssessmentCreatedEvent(DomainEvent):
    """Emitted when a risk assessment is created"""

    assessment_id: UUID
    patient_id: UUID
    gold_group: GoldGroup
    cat_score: int
    mmrc_grade: int
    assessed_at: datetime


@dataclass(frozen=True)
class RiskGroupChangedEvent(DomainEvent):
    """Emitted when GOLD group changes from previous assessment"""

    assessment_id: UUID
    patient_id: UUID
    previous_gold_group: GoldGroup
    new_gold_group: GoldGroup
    changed_at: datetime


# ============================================================================
# RiskScore Entity
# ============================================================================


@dataclass
class RiskScore:
    """
    RiskScore Domain Entity - COPD Risk Assessment

    Linus "Good Taste" Principles Applied:
    1. Simple data structure - GOLD ABE classification drives everything
    2. No special cases - All validation in __post_init__
    3. Single source of truth - gold_group determines risk_level/risk_score
    4. Clear invariants - Ranges enforced at domain level

    Business Rules:
    - CAT score: 0-40 (COPD Assessment Test)
    - mMRC grade: 0-4 (Modified Medical Research Council)
    - GOLD group: A (low), B (medium), E (high)
    - Risk score mapping: A→25, B→50, E→75
    - Domain events published for creation and GOLD group changes
    """

    # Identifiers
    assessment_id: UUID
    patient_id: UUID

    # Assessment Input Data
    cat_score: int
    mmrc_grade: int
    exacerbation_count_12m: int
    hospitalization_count_12m: int

    # GOLD ABE Classification Result
    gold_group: GoldGroup

    # Backward Compatible Fields (Hybrid Strategy)
    risk_score: Optional[int] = None
    risk_level: Optional[RiskLevel] = None

    # Timestamps
    assessed_at: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain Events (not persisted)
    _domain_events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        """
        Validate invariants after initialization (TD-003.1)

        Linus "Good Taste": All validation in one place, no scattered checks.
        """
        # Validate gold_group enum
        if not isinstance(self.gold_group, GoldGroup):
            if isinstance(self.gold_group, str):
                try:
                    self.gold_group = GoldGroup(self.gold_group)
                except ValueError:
                    raise BusinessRuleViolationError(
                        f"Invalid gold_group. Must be one of {[g.value for g in GoldGroup]}"
                    )
            else:
                raise BusinessRuleViolationError("gold_group must be GoldGroup enum or string")

        # Validate CAT score (0-40)
        if not 0 <= self.cat_score <= 40:
            raise BusinessRuleViolationError(
                f"CAT score must be 0-40, got {self.cat_score}"
            )

        # Validate mMRC grade (0-4)
        if not 0 <= self.mmrc_grade <= 4:
            raise BusinessRuleViolationError(
                f"mMRC grade must be 0-4, got {self.mmrc_grade}"
            )

        # Validate exacerbation count (>= 0)
        if self.exacerbation_count_12m < 0:
            raise BusinessRuleViolationError(
                f"Exacerbation count cannot be negative, got {self.exacerbation_count_12m}"
            )

        # Validate hospitalization count (>= 0)
        if self.hospitalization_count_12m < 0:
            raise BusinessRuleViolationError(
                f"Hospitalization count cannot be negative, got {self.hospitalization_count_12m}"
            )

        # Validate risk_score (0-100 if provided)
        if self.risk_score is not None and not 0 <= self.risk_score <= 100:
            raise BusinessRuleViolationError(
                f"Risk score must be 0-100, got {self.risk_score}"
            )

        # Auto-calculate legacy fields if not provided (Hybrid Strategy)
        if self.risk_score is None:
            self.risk_score = self._calculate_risk_score_from_gold_group()

        if self.risk_level is None:
            self.risk_level = self._calculate_risk_level_from_gold_group()

    def _calculate_risk_score_from_gold_group(self) -> int:
        """Map GOLD group to legacy risk score (0-100)"""
        mapping = {
            GoldGroup.A: 25,   # Low risk
            GoldGroup.B: 50,   # Medium risk
            GoldGroup.E: 75,   # High risk
        }
        return mapping[self.gold_group]

    def _calculate_risk_level_from_gold_group(self) -> RiskLevel:
        """Map GOLD group to legacy risk level"""
        mapping = {
            GoldGroup.A: "low",
            GoldGroup.B: "medium",
            GoldGroup.E: "high",
        }
        return mapping[self.gold_group]

    # ========================================================================
    # Business Logic Methods
    # ========================================================================

    def is_high_risk(self) -> bool:
        """Check if patient is in high-risk GOLD group E"""
        return self.gold_group == GoldGroup.E

    def requires_intervention(self) -> bool:
        """
        Check if assessment requires clinical intervention

        Business Logic:
        - Group E always requires intervention
        - Group B with frequent exacerbations (>=2) requires intervention
        """
        if self.gold_group == GoldGroup.E:
            return True

        if self.gold_group == GoldGroup.B and self.exacerbation_count_12m >= 2:
            return True

        return False

    def get_symptom_burden(self) -> Literal["low", "high"]:
        """
        Get symptom burden level based on CAT score

        Business Logic:
        - CAT < 10: Low symptom burden
        - CAT >= 10: High symptom burden
        """
        return "low" if self.cat_score < 10 else "high"

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
        cat_score: int,
        mmrc_grade: int,
        exacerbation_count_12m: int,
        hospitalization_count_12m: int,
        gold_group: GoldGroup,
    ) -> "RiskScore":
        """
        Factory method to create a new risk assessment

        Automatically publishes RiskAssessmentCreatedEvent

        Linus "Good Taste": Factory eliminates special case initialization code.
        All assessments created through this method follow same pattern.

        Args:
            patient_id: UUID of the patient
            cat_score: CAT score (0-40)
            mmrc_grade: mMRC grade (0-4)
            exacerbation_count_12m: Number of exacerbations in last 12 months
            hospitalization_count_12m: Number of hospitalizations in last 12 months
            gold_group: GOLD ABE group (A, B, or E)

        Returns:
            New RiskScore instance with RiskAssessmentCreatedEvent published
        """
        assessment = cls(
            assessment_id=uuid4(),
            patient_id=patient_id,
            cat_score=cat_score,
            mmrc_grade=mmrc_grade,
            exacerbation_count_12m=exacerbation_count_12m,
            hospitalization_count_12m=hospitalization_count_12m,
            gold_group=gold_group,
        )

        # Publish domain event (TD-003.3)
        assessment._add_domain_event(
            RiskAssessmentCreatedEvent(
                assessment_id=assessment.assessment_id,
                patient_id=patient_id,
                gold_group=gold_group,
                cat_score=cat_score,
                mmrc_grade=mmrc_grade,
                assessed_at=assessment.assessed_at,
            )
        )

        return assessment

    @classmethod
    def create_with_group_change(
        cls,
        patient_id: UUID,
        cat_score: int,
        mmrc_grade: int,
        exacerbation_count_12m: int,
        hospitalization_count_12m: int,
        gold_group: GoldGroup,
        previous_gold_group: Optional[GoldGroup] = None,
    ) -> "RiskScore":
        """
        Factory method to create assessment with potential GOLD group change

        Publishes RiskGroupChangedEvent if previous group differs from new group

        Args:
            patient_id: UUID of the patient
            cat_score: CAT score (0-40)
            mmrc_grade: mMRC grade (0-4)
            exacerbation_count_12m: Number of exacerbations in last 12 months
            hospitalization_count_12m: Number of hospitalizations in last 12 months
            gold_group: New GOLD ABE group
            previous_gold_group: Previous GOLD group (if exists)

        Returns:
            New RiskScore instance with appropriate events published
        """
        assessment = cls.create(
            patient_id=patient_id,
            cat_score=cat_score,
            mmrc_grade=mmrc_grade,
            exacerbation_count_12m=exacerbation_count_12m,
            hospitalization_count_12m=hospitalization_count_12m,
            gold_group=gold_group,
        )

        # Publish RiskGroupChangedEvent if group changed
        if previous_gold_group and previous_gold_group != gold_group:
            assessment._add_domain_event(
                RiskGroupChangedEvent(
                    assessment_id=assessment.assessment_id,
                    patient_id=patient_id,
                    previous_gold_group=previous_gold_group,
                    new_gold_group=gold_group,
                    changed_at=assessment.assessed_at,
                )
            )

        return assessment

    def __repr__(self) -> str:
        return (
            f"<RiskScore(id={self.assessment_id}, "
            f"patient={self.patient_id}, "
            f"gold_group={self.gold_group.value}, "
            f"CAT={self.cat_score}, mMRC={self.mmrc_grade})>"
        )
