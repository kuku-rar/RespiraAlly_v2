"""
Unit tests for RiskScore Entity

Tests cover:
- Invariant validation (TD-003.1)
- Domain Events publishing (TD-003.3)
- Business logic (GOLD group classification, risk assessment)
- Factory methods (create, create_with_group_change)
- GOLD ABE classification system (A, B, E groups)
"""

from datetime import datetime
from uuid import uuid4

import pytest

from respira_ally.domain.entities.risk_score import (
    GoldGroup,
    RiskAssessmentCreatedEvent,
    RiskGroupChangedEvent,
    RiskScore,
)
from respira_ally.domain.exceptions import BusinessRuleViolationError


class TestRiskScoreCreation:
    """Test RiskScore creation and basic validation."""

    def test_create_gold_group_a(self):
        """Test creating risk assessment with GOLD group A (low risk)."""
        assessment = RiskScore.create(
            patient_id=uuid4(),
            cat_score=5,
            mmrc_grade=0,
            exacerbation_count_12m=0,
            hospitalization_count_12m=0,
            gold_group=GoldGroup.A,
        )

        assert assessment.assessment_id is not None
        assert assessment.gold_group == GoldGroup.A
        assert assessment.cat_score == 5
        assert assessment.mmrc_grade == 0
        assert assessment.risk_score == 25  # Auto-calculated
        assert assessment.risk_level == "low"  # Auto-calculated

        # Check domain events
        events = assessment.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], RiskAssessmentCreatedEvent)
        assert events[0].gold_group == GoldGroup.A

    def test_create_gold_group_b(self):
        """Test creating risk assessment with GOLD group B (medium risk)."""
        assessment = RiskScore.create(
            patient_id=uuid4(),
            cat_score=15,
            mmrc_grade=1,
            exacerbation_count_12m=1,
            hospitalization_count_12m=0,
            gold_group=GoldGroup.B,
        )

        assert assessment.gold_group == GoldGroup.B
        assert assessment.risk_score == 50  # Auto-calculated
        assert assessment.risk_level == "medium"

    def test_create_gold_group_e(self):
        """Test creating risk assessment with GOLD group E (high risk)."""
        assessment = RiskScore.create(
            patient_id=uuid4(),
            cat_score=25,
            mmrc_grade=3,
            exacerbation_count_12m=2,
            hospitalization_count_12m=1,
            gold_group=GoldGroup.E,
        )

        assert assessment.gold_group == GoldGroup.E
        assert assessment.risk_score == 75  # Auto-calculated
        assert assessment.risk_level == "high"

    def test_cat_score_out_of_range(self):
        """Test that CAT score out of range (0-40) raises error."""
        with pytest.raises(BusinessRuleViolationError, match="CAT score must be 0-40"):
            RiskScore.create(
                patient_id=uuid4(),
                cat_score=50,  # Invalid: > 40
                mmrc_grade=2,
                exacerbation_count_12m=0,
                hospitalization_count_12m=0,
                gold_group=GoldGroup.B,
            )

    def test_mmrc_grade_out_of_range(self):
        """Test that mMRC grade out of range (0-4) raises error."""
        with pytest.raises(BusinessRuleViolationError, match="mMRC grade must be 0-4"):
            RiskScore.create(
                patient_id=uuid4(),
                cat_score=10,
                mmrc_grade=5,  # Invalid: > 4
                exacerbation_count_12m=0,
                hospitalization_count_12m=0,
                gold_group=GoldGroup.B,
            )

    def test_exacerbation_count_negative(self):
        """Test that negative exacerbation count raises error."""
        with pytest.raises(BusinessRuleViolationError, match="Exacerbation count cannot be negative"):
            RiskScore.create(
                patient_id=uuid4(),
                cat_score=10,
                mmrc_grade=2,
                exacerbation_count_12m=-1,  # Invalid: < 0
                hospitalization_count_12m=0,
                gold_group=GoldGroup.B,
            )

    def test_hospitalization_count_negative(self):
        """Test that negative hospitalization count raises error."""
        with pytest.raises(BusinessRuleViolationError, match="Hospitalization count cannot be negative"):
            RiskScore.create(
                patient_id=uuid4(),
                cat_score=10,
                mmrc_grade=2,
                exacerbation_count_12m=0,
                hospitalization_count_12m=-1,  # Invalid: < 0
                gold_group=GoldGroup.B,
            )

    def test_enum_auto_conversion_from_string(self):
        """Test that GOLD group string is automatically converted to GoldGroup enum."""
        assessment = RiskScore(
            assessment_id=uuid4(),
            patient_id=uuid4(),
            cat_score=10,
            mmrc_grade=2,
            exacerbation_count_12m=0,
            hospitalization_count_12m=0,
            gold_group="B",  # type: ignore
        )

        assert assessment.gold_group == GoldGroup.B
        assert isinstance(assessment.gold_group, GoldGroup)

    def test_invalid_gold_group_string_raises_error(self):
        """Test that invalid GOLD group string raises BusinessRuleViolationError."""
        with pytest.raises(BusinessRuleViolationError, match="Invalid gold_group"):
            RiskScore(
                assessment_id=uuid4(),
                patient_id=uuid4(),
                cat_score=10,
                mmrc_grade=2,
                exacerbation_count_12m=0,
                hospitalization_count_12m=0,
                gold_group="X",  # type: ignore
            )


class TestRiskScoreGroupChange:
    """Test RiskScore GOLD group change workflow."""

    def test_create_with_group_change_no_previous(self):
        """Test creating assessment without previous group (first assessment)."""
        assessment = RiskScore.create_with_group_change(
            patient_id=uuid4(),
            cat_score=5,
            mmrc_grade=0,
            exacerbation_count_12m=0,
            hospitalization_count_12m=0,
            gold_group=GoldGroup.A,
            previous_gold_group=None,  # First assessment
        )

        # Should only have RiskAssessmentCreatedEvent
        events = assessment.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], RiskAssessmentCreatedEvent)

    def test_create_with_group_change_from_a_to_b(self):
        """Test creating assessment with group change from A to B."""
        assessment = RiskScore.create_with_group_change(
            patient_id=uuid4(),
            cat_score=15,
            mmrc_grade=2,
            exacerbation_count_12m=0,
            hospitalization_count_12m=0,
            gold_group=GoldGroup.B,
            previous_gold_group=GoldGroup.A,
        )

        # Should have both events
        events = assessment.get_domain_events()
        assert len(events) == 2
        assert isinstance(events[0], RiskAssessmentCreatedEvent)
        assert isinstance(events[1], RiskGroupChangedEvent)
        assert events[1].previous_gold_group == GoldGroup.A
        assert events[1].new_gold_group == GoldGroup.B

    def test_create_with_group_change_from_b_to_e(self):
        """Test creating assessment with group change from B to E (deterioration)."""
        assessment = RiskScore.create_with_group_change(
            patient_id=uuid4(),
            cat_score=25,
            mmrc_grade=3,
            exacerbation_count_12m=2,
            hospitalization_count_12m=1,
            gold_group=GoldGroup.E,
            previous_gold_group=GoldGroup.B,
        )

        events = assessment.get_domain_events()
        assert len(events) == 2
        assert isinstance(events[1], RiskGroupChangedEvent)
        assert events[1].previous_gold_group == GoldGroup.B
        assert events[1].new_gold_group == GoldGroup.E

    def test_create_with_same_group_no_change_event(self):
        """Test that same GOLD group doesn't trigger RiskGroupChangedEvent."""
        assessment = RiskScore.create_with_group_change(
            patient_id=uuid4(),
            cat_score=10,
            mmrc_grade=2,
            exacerbation_count_12m=0,
            hospitalization_count_12m=0,
            gold_group=GoldGroup.B,
            previous_gold_group=GoldGroup.B,  # Same group
        )

        # Should only have RiskAssessmentCreatedEvent
        events = assessment.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], RiskAssessmentCreatedEvent)


class TestRiskScoreBusinessLogic:
    """Test RiskScore business logic methods."""

    def test_is_high_risk_for_group_e(self):
        """Test is_high_risk() for GOLD group E."""
        assessment = RiskScore.create(
            patient_id=uuid4(),
            cat_score=25,
            mmrc_grade=3,
            exacerbation_count_12m=2,
            hospitalization_count_12m=1,
            gold_group=GoldGroup.E,
        )

        assert assessment.is_high_risk()

    def test_is_high_risk_for_group_a(self):
        """Test is_high_risk() for GOLD group A."""
        assessment = RiskScore.create(
            patient_id=uuid4(),
            cat_score=5,
            mmrc_grade=0,
            exacerbation_count_12m=0,
            hospitalization_count_12m=0,
            gold_group=GoldGroup.A,
        )

        assert not assessment.is_high_risk()

    def test_requires_intervention_for_group_e(self):
        """Test requires_intervention() for GOLD group E."""
        assessment = RiskScore.create(
            patient_id=uuid4(),
            cat_score=25,
            mmrc_grade=3,
            exacerbation_count_12m=2,
            hospitalization_count_12m=1,
            gold_group=GoldGroup.E,
        )

        assert assessment.requires_intervention()

    def test_requires_intervention_for_group_b_frequent_exacerbations(self):
        """Test requires_intervention() for Group B with frequent exacerbations."""
        assessment = RiskScore.create(
            patient_id=uuid4(),
            cat_score=10,
            mmrc_grade=1,
            exacerbation_count_12m=2,  # >= 2 exacerbations
            hospitalization_count_12m=0,
            gold_group=GoldGroup.B,
        )

        assert assessment.requires_intervention()

    def test_requires_intervention_for_group_b_low_exacerbations(self):
        """Test requires_intervention() for Group B with low exacerbations."""
        assessment = RiskScore.create(
            patient_id=uuid4(),
            cat_score=10,
            mmrc_grade=1,
            exacerbation_count_12m=1,  # < 2 exacerbations
            hospitalization_count_12m=0,
            gold_group=GoldGroup.B,
        )

        assert not assessment.requires_intervention()

    def test_get_symptom_burden_low(self):
        """Test get_symptom_burden() for CAT < 10 (low)."""
        assessment = RiskScore.create(
            patient_id=uuid4(),
            cat_score=5,
            mmrc_grade=0,
            exacerbation_count_12m=0,
            hospitalization_count_12m=0,
            gold_group=GoldGroup.A,
        )

        assert assessment.get_symptom_burden() == "low"

    def test_get_symptom_burden_high(self):
        """Test get_symptom_burden() for CAT >= 10 (high)."""
        assessment = RiskScore.create(
            patient_id=uuid4(),
            cat_score=10,
            mmrc_grade=2,
            exacerbation_count_12m=0,
            hospitalization_count_12m=0,
            gold_group=GoldGroup.B,
        )

        assert assessment.get_symptom_burden() == "high"


class TestRiskScoreDomainEvents:
    """Test RiskScore domain events management."""

    def test_get_domain_events_returns_copy(self):
        """Test that get_domain_events() returns a copy, not the original list."""
        assessment = RiskScore.create(
            patient_id=uuid4(),
            cat_score=10,
            mmrc_grade=2,
            exacerbation_count_12m=0,
            hospitalization_count_12m=0,
            gold_group=GoldGroup.B,
        )

        events1 = assessment.get_domain_events()
        events2 = assessment.get_domain_events()

        assert events1 is not events2
        assert events1 == events2

    def test_clear_domain_events(self):
        """Test clearing domain events."""
        assessment = RiskScore.create(
            patient_id=uuid4(),
            cat_score=10,
            mmrc_grade=2,
            exacerbation_count_12m=0,
            hospitalization_count_12m=0,
            gold_group=GoldGroup.B,
        )

        assert len(assessment.get_domain_events()) == 1

        assessment.clear_domain_events()

        assert len(assessment.get_domain_events()) == 0
