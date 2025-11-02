"""
Unit tests for DailyLog Entity

Tests cover:
- Invariant validation (TD-003.1)
- Domain Events publishing (TD-003.3)
- Business logic (medication adherence, hydration, exercise tracking)
- Factory methods (create)
- Daily health metrics tracking
"""

from datetime import date
from uuid import uuid4

import pytest

from respira_ally.domain.entities.daily_log import (
    DailyLog,
    DailyLogCreatedEvent,
    MedicationNotTakenEvent,
)
from respira_ally.domain.exceptions import BusinessRuleViolationError


class TestDailyLogCreation:
    """Test DailyLog creation and basic validation."""

    def test_create_daily_log_with_all_metrics(self):
        """Test creating daily log with all metrics filled."""
        log = DailyLog.create(
            patient_id=uuid4(),
            log_date=date.today(),
            medication_taken=True,
            water_intake_ml=2500,
            exercise_minutes=45,
            smoking_count=0,
            symptoms="Feeling well",
            mood="GOOD",
        )

        assert log.log_id is not None
        assert log.medication_taken is True
        assert log.water_intake_ml == 2500
        assert log.exercise_minutes == 45
        assert log.smoking_count == 0
        assert log.mood == "GOOD"

        # Check domain events (only DailyLogCreatedEvent)
        events = log.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], DailyLogCreatedEvent)

    def test_create_daily_log_medication_not_taken(self):
        """Test creating daily log when medication not taken."""
        log = DailyLog.create(
            patient_id=uuid4(),
            log_date=date.today(),
            medication_taken=False,  # Medication not taken
        )

        # Should trigger MedicationNotTakenEvent
        events = log.get_domain_events()
        assert len(events) == 2
        assert isinstance(events[0], DailyLogCreatedEvent)
        assert isinstance(events[1], MedicationNotTakenEvent)

    def test_create_daily_log_minimal(self):
        """Test creating daily log with minimal data."""
        patient_id = uuid4()
        log_date = date.today()

        log = DailyLog.create(
            patient_id=patient_id,
            log_date=log_date,
        )

        assert log.patient_id == patient_id
        assert log.log_date == log_date
        assert log.medication_taken is None
        assert log.water_intake_ml is None
        assert log.exercise_minutes is None
        assert log.smoking_count is None

    def test_water_intake_out_of_range_too_high(self):
        """Test that water intake > 10000 ml raises error."""
        with pytest.raises(BusinessRuleViolationError, match="Water intake must be 0-10000 ml"):
            DailyLog.create(
                patient_id=uuid4(),
                log_date=date.today(),
                water_intake_ml=15000,  # Invalid: > 10000
            )

    def test_water_intake_out_of_range_negative(self):
        """Test that negative water intake raises error."""
        with pytest.raises(BusinessRuleViolationError, match="Water intake must be 0-10000 ml"):
            DailyLog.create(
                patient_id=uuid4(),
                log_date=date.today(),
                water_intake_ml=-100,  # Invalid: < 0
            )

    def test_exercise_minutes_out_of_range_too_high(self):
        """Test that exercise > 480 minutes raises error."""
        with pytest.raises(BusinessRuleViolationError, match="Exercise duration must be 0-480 minutes"):
            DailyLog.create(
                patient_id=uuid4(),
                log_date=date.today(),
                exercise_minutes=500,  # Invalid: > 480 (8 hours)
            )

    def test_exercise_minutes_out_of_range_negative(self):
        """Test that negative exercise duration raises error."""
        with pytest.raises(BusinessRuleViolationError, match="Exercise duration must be 0-480 minutes"):
            DailyLog.create(
                patient_id=uuid4(),
                log_date=date.today(),
                exercise_minutes=-10,  # Invalid: < 0
            )

    def test_smoking_count_out_of_range_too_high(self):
        """Test that smoking count > 100 raises error."""
        with pytest.raises(BusinessRuleViolationError, match="Smoking count must be 0-100"):
            DailyLog.create(
                patient_id=uuid4(),
                log_date=date.today(),
                smoking_count=150,  # Invalid: > 100
            )

    def test_smoking_count_out_of_range_negative(self):
        """Test that negative smoking count raises error."""
        with pytest.raises(BusinessRuleViolationError, match="Smoking count must be 0-100"):
            DailyLog.create(
                patient_id=uuid4(),
                log_date=date.today(),
                smoking_count=-5,  # Invalid: < 0
            )

    def test_invalid_mood(self):
        """Test that invalid mood value raises error."""
        with pytest.raises(BusinessRuleViolationError, match="Mood must be one of"):
            DailyLog.create(
                patient_id=uuid4(),
                log_date=date.today(),
                mood="HAPPY",  # type: ignore - Invalid: not in (GOOD, NEUTRAL, BAD)
            )


class TestDailyLogBusinessLogic:
    """Test DailyLog business logic methods."""

    def test_is_medication_adherent_true(self):
        """Test is_medication_adherent() when medication taken."""
        log = DailyLog.create(
            patient_id=uuid4(),
            log_date=date.today(),
            medication_taken=True,
        )

        assert log.is_medication_adherent()

    def test_is_medication_adherent_false(self):
        """Test is_medication_adherent() when medication not taken."""
        log = DailyLog.create(
            patient_id=uuid4(),
            log_date=date.today(),
            medication_taken=False,
        )

        assert not log.is_medication_adherent()

    def test_is_medication_adherent_not_recorded(self):
        """Test is_medication_adherent() when medication not recorded."""
        log = DailyLog.create(
            patient_id=uuid4(),
            log_date=date.today(),
            medication_taken=None,
        )

        assert not log.is_medication_adherent()

    def test_has_symptoms_true(self):
        """Test has_symptoms() when symptoms recorded."""
        log = DailyLog.create(
            patient_id=uuid4(),
            log_date=date.today(),
            symptoms="Cough and shortness of breath",
        )

        assert log.has_symptoms()

    def test_has_symptoms_false(self):
        """Test has_symptoms() when no symptoms recorded."""
        log = DailyLog.create(
            patient_id=uuid4(),
            log_date=date.today(),
            symptoms=None,
        )

        assert not log.has_symptoms()

    def test_has_symptoms_empty_string(self):
        """Test has_symptoms() with empty string."""
        log = DailyLog.create(
            patient_id=uuid4(),
            log_date=date.today(),
            symptoms="   ",  # Whitespace only
        )

        assert not log.has_symptoms()

    def test_is_well_hydrated_true(self):
        """Test is_well_hydrated() when water intake >= threshold."""
        log = DailyLog.create(
            patient_id=uuid4(),
            log_date=date.today(),
            water_intake_ml=2500,
        )

        assert log.is_well_hydrated(threshold_ml=2000)

    def test_is_well_hydrated_false(self):
        """Test is_well_hydrated() when water intake < threshold."""
        log = DailyLog.create(
            patient_id=uuid4(),
            log_date=date.today(),
            water_intake_ml=1500,
        )

        assert not log.is_well_hydrated(threshold_ml=2000)

    def test_is_well_hydrated_not_recorded(self):
        """Test is_well_hydrated() when water intake not recorded."""
        log = DailyLog.create(
            patient_id=uuid4(),
            log_date=date.today(),
            water_intake_ml=None,
        )

        assert not log.is_well_hydrated()

    def test_has_exercised_true(self):
        """Test has_exercised() when exercise >= threshold."""
        log = DailyLog.create(
            patient_id=uuid4(),
            log_date=date.today(),
            exercise_minutes=45,
        )

        assert log.has_exercised(min_minutes=30)

    def test_has_exercised_false(self):
        """Test has_exercised() when exercise < threshold."""
        log = DailyLog.create(
            patient_id=uuid4(),
            log_date=date.today(),
            exercise_minutes=20,
        )

        assert not log.has_exercised(min_minutes=30)

    def test_has_exercised_not_recorded(self):
        """Test has_exercised() when exercise not recorded."""
        log = DailyLog.create(
            patient_id=uuid4(),
            log_date=date.today(),
            exercise_minutes=None,
        )

        assert not log.has_exercised()


class TestDailyLogDomainEvents:
    """Test DailyLog domain events management."""

    def test_get_domain_events_returns_copy(self):
        """Test that get_domain_events() returns a copy, not the original list."""
        log = DailyLog.create(
            patient_id=uuid4(),
            log_date=date.today(),
        )

        events1 = log.get_domain_events()
        events2 = log.get_domain_events()

        assert events1 is not events2
        assert events1 == events2

    def test_clear_domain_events(self):
        """Test clearing domain events."""
        log = DailyLog.create(
            patient_id=uuid4(),
            log_date=date.today(),
        )

        assert len(log.get_domain_events()) == 1

        log.clear_domain_events()

        assert len(log.get_domain_events()) == 0

    def test_medication_not_taken_event_triggered(self):
        """Test that MedicationNotTakenEvent is triggered when medication_taken = False."""
        patient_id = uuid4()
        log_date = date.today()

        log = DailyLog.create(
            patient_id=patient_id,
            log_date=log_date,
            medication_taken=False,
        )

        events = log.get_domain_events()
        assert len(events) == 2

        # First event: DailyLogCreatedEvent
        assert isinstance(events[0], DailyLogCreatedEvent)

        # Second event: MedicationNotTakenEvent
        assert isinstance(events[1], MedicationNotTakenEvent)
        assert events[1].patient_id == patient_id
        assert events[1].log_date == log_date

    def test_medication_taken_no_extra_event(self):
        """Test that no MedicationNotTakenEvent when medication_taken = True."""
        log = DailyLog.create(
            patient_id=uuid4(),
            log_date=date.today(),
            medication_taken=True,
        )

        events = log.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], DailyLogCreatedEvent)
