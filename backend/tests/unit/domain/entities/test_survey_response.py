"""
Unit tests for SurveyResponse Entity

Tests cover:
- Invariant validation (TD-003.1)
- Domain Events publishing (TD-003.3)
- Business logic (severity calculation, concerning checks)
- Factory methods (create)
- CAT and mMRC survey types
"""

from uuid import uuid4

import pytest

from respira_ally.domain.entities.survey_response import (
    HighSeveritySurveyEvent,
    SurveyResponse,
    SurveySubmittedEvent,
)
from respira_ally.domain.exceptions import BusinessRuleViolationError


class TestSurveyResponseCreation:
    """Test SurveyResponse creation and validation."""

    def test_create_cat_survey_mild(self):
        """Test creating CAT survey with MILD severity."""
        survey = SurveyResponse.create(
            patient_id=uuid4(),
            survey_type="CAT",
            answers={"q1": 1, "q2": 1, "q3": 1, "q4": 1, "q5": 1, "q6": 1, "q7": 1, "q8": 1},
            total_score=8,
            is_first_survey=True,
        )

        assert survey.survey_type == "CAT"
        assert survey.total_score == 8
        assert survey.severity_level == "MILD"
        assert len(survey.get_domain_events()) == 1
        assert isinstance(survey.get_domain_events()[0], SurveySubmittedEvent)

    def test_create_cat_survey_severe(self):
        """Test creating CAT survey with SEVERE severity."""
        survey = SurveyResponse.create(
            patient_id=uuid4(),
            survey_type="CAT",
            answers={"q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 3, "q6": 3, "q7": 3, "q8": 4},
            total_score=25,
            previous_score=8,
        )

        assert survey.severity_level == "SEVERE"
        events = survey.get_domain_events()
        assert len(events) == 2
        assert isinstance(events[0], SurveySubmittedEvent)
        assert isinstance(events[1], HighSeveritySurveyEvent)

    def test_create_mmrc_survey(self):
        """Test creating mMRC survey."""
        survey = SurveyResponse.create(
            patient_id=uuid4(),
            survey_type="mMRC",
            answers={"grade": 2},
            total_score=2,
        )

        assert survey.survey_type == "mMRC"
        assert survey.severity_level == "MODERATE"

    def test_invalid_survey_type(self):
        """Test invalid survey type raises error."""
        with pytest.raises(BusinessRuleViolationError, match="Survey type must be one of"):
            SurveyResponse.create(
                patient_id=uuid4(),
                survey_type="INVALID",  # type: ignore
                answers={"q1": 1},
                total_score=10,
            )

    def test_cat_score_out_of_range(self):
        """Test CAT score out of range raises error."""
        with pytest.raises(BusinessRuleViolationError, match="CAT score must be 0-40"):
            SurveyResponse.create(
                patient_id=uuid4(),
                survey_type="CAT",
                answers={"q1": 1},
                total_score=50,
            )

    def test_mmrc_grade_out_of_range(self):
        """Test mMRC grade out of range raises error."""
        with pytest.raises(BusinessRuleViolationError, match="mMRC grade must be 0-4"):
            SurveyResponse.create(
                patient_id=uuid4(),
                survey_type="mMRC",
                answers={"grade": 1},
                total_score=5,
            )


class TestSurveyResponseBusinessLogic:
    """Test SurveyResponse business logic methods."""

    def test_is_concerning_for_severe(self):
        """Test is_concerning() for SEVERE severity."""
        survey = SurveyResponse.create(
            patient_id=uuid4(),
            survey_type="CAT",
            answers={"q1": 3, "q2": 3, "q3": 3, "q4": 3, "q5": 3, "q6": 2, "q7": 2, "q8": 2},
            total_score=23,
        )

        assert survey.is_concerning()

    def test_is_concerning_for_mild(self):
        """Test is_concerning() for MILD severity."""
        survey = SurveyResponse.create(
            patient_id=uuid4(),
            survey_type="CAT",
            answers={"q1": 1, "q2": 1, "q3": 1, "q4": 1, "q5": 1, "q6": 1, "q7": 1, "q8": 1},
            total_score=8,
        )

        assert not survey.is_concerning()

    def test_has_significant_change(self):
        """Test has_significant_change() method."""
        survey = SurveyResponse.create(
            patient_id=uuid4(),
            survey_type="CAT",
            answers={"q1": 2, "q2": 2, "q3": 2, "q4": 2, "q5": 2, "q6": 2, "q7": 2, "q8": 2},
            total_score=16,
        )

        assert survey.has_significant_change(previous_score=8, threshold=5)
        assert not survey.has_significant_change(previous_score=14, threshold=5)
