"""
Unit Tests for Daily Log Schema Validators
Tests Pydantic field validators for data accuracy
"""
import pytest
from datetime import date, timedelta
from uuid import uuid4

from respira_ally.core.schemas.daily_log import DailyLogCreate, DailyLogUpdate
from pydantic import ValidationError


# ============================================================================
# log_date Validator Tests
# ============================================================================

def test_log_date_valid_today():
    """Test log_date accepts today's date"""
    data = {
        "log_date": date.today(),
        "patient_id": uuid4(),
        "medication_taken": True,
        "water_intake_ml": 2000,
    }
    log = DailyLogCreate(**data)
    assert log.log_date == date.today()


def test_log_date_valid_yesterday():
    """Test log_date accepts yesterday's date"""
    yesterday = date.today() - timedelta(days=1)
    data = {
        "log_date": yesterday,
        "patient_id": uuid4(),
        "medication_taken": True,
        "water_intake_ml": 2000,
    }
    log = DailyLogCreate(**data)
    assert log.log_date == yesterday


def test_log_date_valid_one_year_ago():
    """Test log_date accepts date 365 days ago (boundary)"""
    one_year_ago = date.today() - timedelta(days=365)
    data = {
        "log_date": one_year_ago,
        "patient_id": uuid4(),
        "medication_taken": True,
        "water_intake_ml": 2000,
    }
    log = DailyLogCreate(**data)
    assert log.log_date == one_year_ago


def test_log_date_reject_future():
    """Test log_date rejects future dates"""
    tomorrow = date.today() + timedelta(days=1)
    data = {
        "log_date": tomorrow,
        "patient_id": uuid4(),
        "medication_taken": True,
        "water_intake_ml": 2000,
    }
    with pytest.raises(ValidationError) as exc_info:
        DailyLogCreate(**data)

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("log_date",)
    assert "cannot be in the future" in errors[0]["msg"]


def test_log_date_reject_too_old():
    """Test log_date rejects dates older than 365 days"""
    too_old = date.today() - timedelta(days=366)
    data = {
        "log_date": too_old,
        "patient_id": uuid4(),
        "medication_taken": True,
        "water_intake_ml": 2000,
    }
    with pytest.raises(ValidationError) as exc_info:
        DailyLogCreate(**data)

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("log_date",)
    assert "older than 365 days" in errors[0]["msg"]


# ============================================================================
# water_intake_ml Validator Tests
# ============================================================================

def test_water_intake_valid_normal():
    """Test water_intake_ml accepts normal values (500-5000ml)"""
    for amount in [500, 2000, 3000, 5000]:
        data = {
            "log_date": date.today(),
            "patient_id": uuid4(),
            "medication_taken": True,
            "water_intake_ml": amount,
        }
        log = DailyLogCreate(**data)
        assert log.water_intake_ml == amount


def test_water_intake_valid_low_warning():
    """Test water_intake_ml accepts low values but should trigger warning"""
    data = {
        "log_date": date.today(),
        "patient_id": uuid4(),
        "medication_taken": True,
        "water_intake_ml": 300,  # Low but valid
    }
    log = DailyLogCreate(**data)
    assert log.water_intake_ml == 300
    # Note: In production, this should trigger a warning notification


def test_water_intake_valid_high_warning():
    """Test water_intake_ml accepts high values but should trigger warning"""
    data = {
        "log_date": date.today(),
        "patient_id": uuid4(),
        "medication_taken": True,
        "water_intake_ml": 7000,  # High but valid
    }
    log = DailyLogCreate(**data)
    assert log.water_intake_ml == 7000
    # Note: In production, this should trigger a warning notification


def test_water_intake_reject_negative():
    """Test water_intake_ml rejects negative values"""
    data = {
        "log_date": date.today(),
        "patient_id": uuid4(),
        "medication_taken": True,
        "water_intake_ml": -100,
    }
    with pytest.raises(ValidationError) as exc_info:
        DailyLogCreate(**data)

    errors = exc_info.value.errors()
    assert any(e["loc"] == ("water_intake_ml",) for e in errors)


def test_water_intake_reject_excessive():
    """Test water_intake_ml rejects values > 10000ml"""
    data = {
        "log_date": date.today(),
        "patient_id": uuid4(),
        "medication_taken": True,
        "water_intake_ml": 15000,
    }
    with pytest.raises(ValidationError) as exc_info:
        DailyLogCreate(**data)

    errors = exc_info.value.errors()
    assert any(e["loc"] == ("water_intake_ml",) for e in errors)


# ============================================================================
# steps_count Validator Tests
# ============================================================================

def test_steps_count_valid_normal():
    """Test steps_count accepts normal values (1000-30000)"""
    for steps in [1000, 5000, 10000, 20000, 30000]:
        data = {
            "log_date": date.today(),
            "patient_id": uuid4(),
            "medication_taken": True,
            "water_intake_ml": 2000,
            "steps_count": steps,
        }
        log = DailyLogCreate(**data)
        assert log.steps_count == steps


def test_steps_count_valid_none():
    """Test steps_count accepts None (optional field)"""
    data = {
        "log_date": date.today(),
        "patient_id": uuid4(),
        "medication_taken": True,
        "water_intake_ml": 2000,
        "steps_count": None,
    }
    log = DailyLogCreate(**data)
    assert log.steps_count is None


def test_steps_count_valid_low_warning():
    """Test steps_count accepts low values but should trigger warning"""
    data = {
        "log_date": date.today(),
        "patient_id": uuid4(),
        "medication_taken": True,
        "water_intake_ml": 2000,
        "steps_count": 500,  # Low but valid
    }
    log = DailyLogCreate(**data)
    assert log.steps_count == 500
    # Note: In production, this should trigger a low activity warning


def test_steps_count_valid_high_warning():
    """Test steps_count accepts high values but should trigger warning"""
    data = {
        "log_date": date.today(),
        "patient_id": uuid4(),
        "medication_taken": True,
        "water_intake_ml": 2000,
        "steps_count": 40000,  # High but valid
    }
    log = DailyLogCreate(**data)
    assert log.steps_count == 40000
    # Note: In production, this should trigger an excessive activity warning


def test_steps_count_reject_excessive():
    """Test steps_count rejects values > 50000"""
    data = {
        "log_date": date.today(),
        "patient_id": uuid4(),
        "medication_taken": True,
        "water_intake_ml": 2000,
        "steps_count": 60000,  # Exceeds max
    }
    with pytest.raises(ValidationError) as exc_info:
        DailyLogCreate(**data)

    errors = exc_info.value.errors()
    assert any(e["loc"] == ("steps_count",) for e in errors)


def test_steps_count_reject_negative():
    """Test steps_count rejects negative values"""
    data = {
        "log_date": date.today(),
        "patient_id": uuid4(),
        "medication_taken": True,
        "water_intake_ml": 2000,
        "steps_count": -100,
    }
    with pytest.raises(ValidationError) as exc_info:
        DailyLogCreate(**data)

    errors = exc_info.value.errors()
    assert any(e["loc"] == ("steps_count",) for e in errors)


# ============================================================================
# symptoms Validator Tests
# ============================================================================

def test_symptoms_valid_normal():
    """Test symptoms accepts normal symptom descriptions"""
    normal_symptoms = [
        "輕微咳嗽",
        "有點疲倦",
        "今天感覺還不錯",
        "沒什麼特別症狀",
    ]
    for symptom in normal_symptoms:
        data = {
            "log_date": date.today(),
            "patient_id": uuid4(),
            "medication_taken": True,
            "water_intake_ml": 2000,
            "symptoms": symptom,
        }
        log = DailyLogCreate(**data)
        assert log.symptoms == symptom


def test_symptoms_valid_none():
    """Test symptoms accepts None"""
    data = {
        "log_date": date.today(),
        "patient_id": uuid4(),
        "medication_taken": True,
        "water_intake_ml": 2000,
        "symptoms": None,
    }
    log = DailyLogCreate(**data)
    assert log.symptoms is None


def test_symptoms_critical_keywords_stored():
    """Test critical symptoms are stored (should trigger alerts)"""
    critical_symptoms = [
        "無法呼吸，很難受",
        "胸痛，需要休息",
        "今天有點暈倒",
        "咳血了，很擔心",
    ]
    for symptom in critical_symptoms:
        data = {
            "log_date": date.today(),
            "patient_id": uuid4(),
            "medication_taken": True,
            "water_intake_ml": 2000,
            "symptoms": symptom,
        }
        log = DailyLogCreate(**data)
        assert log.symptoms == symptom
        # Note: In production, this should trigger immediate therapist alert


def test_symptoms_reject_too_long():
    """Test symptoms rejects strings longer than 500 characters"""
    too_long = "很長的症狀描述" * 100  # > 500 chars
    data = {
        "log_date": date.today(),
        "patient_id": uuid4(),
        "medication_taken": True,
        "water_intake_ml": 2000,
        "symptoms": too_long,
    }
    with pytest.raises(ValidationError) as exc_info:
        DailyLogCreate(**data)

    errors = exc_info.value.errors()
    assert any(e["loc"] == ("symptoms",) for e in errors)


# ============================================================================
# DailyLogUpdate Validator Tests
# ============================================================================

def test_update_steps_count_max_50000():
    """Test DailyLogUpdate enforces max 50000 steps"""
    data = {"steps_count": 60000}
    with pytest.raises(ValidationError) as exc_info:
        DailyLogUpdate(**data)

    errors = exc_info.value.errors()
    assert any(e["loc"] == ("steps_count",) for e in errors)


def test_update_all_fields_optional():
    """Test DailyLogUpdate allows all fields to be None"""
    data = {}
    update = DailyLogUpdate(**data)
    assert update.medication_taken is None
    assert update.water_intake_ml is None
    assert update.steps_count is None
    assert update.symptoms is None
    assert update.mood is None
