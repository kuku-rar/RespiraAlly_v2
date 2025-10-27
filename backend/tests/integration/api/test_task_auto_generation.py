"""
Task Auto-Generation Integration Tests (Phase B5)
Tests the Alert → Task automatic generation workflow

Features tested:
1. Auto-generate tasks from alerts triggered by risk assessments
2. Task priority calculation from alert severity
3. Auto-assignment to patient's therapist
4. Task status transitions
5. Error resilience (task generation failure doesn't break alert creation)

Run with: pytest tests/integration/api/test_task_auto_generation.py -v
"""

from datetime import date
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from respira_ally.infrastructure.database.models.alert import AlertModel
from respira_ally.infrastructure.database.models.daily_log import DailyLogModel
from respira_ally.infrastructure.database.models.patient_profile import PatientProfileModel
from respira_ally.infrastructure.database.models.risk_assessment import RiskAssessmentModel
from respira_ally.infrastructure.database.models.task import TaskModel
from respira_ally.infrastructure.database.models.user import UserModel


# ============================================================================
# Test: Alert → Task Auto-Generation Workflow
# ============================================================================


@pytest.mark.asyncio
async def test_auto_generate_task_from_high_risk_alert(
    client: TestClient,
    therapist_user: UserModel,
    patient_user: UserModel,
    patient_token: str,
    db_session: AsyncSession,
):
    """
    Test auto-generating task when high-risk alert is created

    Scenario: Patient logs worsening symptoms → Risk assessment → High-risk alert → Auto-generate task
    Expected: Task created automatically, assigned to therapist, with CRITICAL priority
    """
    # Arrange: Get patient profile and verify therapist assignment
    patient_profile = await db_session.get(PatientProfileModel, patient_user.user_id)
    assert patient_profile is not None
    assert patient_profile.therapist_id == therapist_user.user_id

    # Count existing tasks and alerts
    tasks_before = (await db_session.execute(
        select(TaskModel).where(TaskModel.patient_id == patient_user.user_id)
    )).scalars().all()
    alerts_before = (await db_session.execute(
        select(AlertModel).where(AlertModel.patient_id == patient_user.user_id)
    )).scalars().all()

    # Act: Create daily log with high-risk symptoms
    daily_log_data = {
        "log_date": date.today().isoformat(),
        "symptom_severity": 4,  # High severity
        "breathlessness_score": 4,  # Severe breathlessness
        "cough_frequency": 4,  # Frequent cough
        "sputum_color": "GREEN",  # Warning sign
        "activity_level": 1,  # Very limited activity
        "medication_adherence": 2,  # Poor adherence
        "notes": "Feeling very unwell, hard to breathe",
    }

    response = client.post(
        "/api/v1/daily-logs",
        json=daily_log_data,
        headers={"Authorization": f"Bearer {patient_token}"},
    )

    # Assert: Daily log created successfully
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

    # Verify: New alert created
    alerts_after = (await db_session.execute(
        select(AlertModel).where(AlertModel.patient_id == patient_user.user_id)
    )).scalars().all()
    new_alerts = [a for a in alerts_after if a not in alerts_before]
    assert len(new_alerts) > 0, "Expected at least one new alert to be created"

    # Verify: New task auto-generated
    tasks_after = (await db_session.execute(
        select(TaskModel).where(TaskModel.patient_id == patient_user.user_id)
    )).scalars().all()
    new_tasks = [t for t in tasks_after if t not in tasks_before]
    assert len(new_tasks) > 0, "Expected at least one new task to be auto-generated"

    # Verify: Task properties
    task = new_tasks[0]
    assert task.patient_id == patient_user.user_id
    assert task.assigned_to == therapist_user.user_id, "Task should be assigned to therapist"
    assert task.status == "IN_PROGRESS", "Task should be IN_PROGRESS when assigned"
    assert task.task_type == "ALERT_TRIGGERED"
    assert task.related_alert_id is not None, "Task should reference the alert"
    assert task.task_metadata is not None
    assert task.task_metadata.get("auto_generated") is True
    assert "alert_id" in task.task_metadata
    assert "priority_reason" in task.task_metadata


@pytest.mark.asyncio
async def test_task_priority_calculation_from_alert_severity(
    client: TestClient,
    therapist_user: UserModel,
    patient_user: UserModel,
    db_session: AsyncSession,
):
    """
    Test priority calculation: Alert severity → Task priority mapping

    Scenario: Create alerts with different severities, verify task priorities
    Expected: CRITICAL alert → CRITICAL task, HIGH alert → HIGH task, etc.
    """
    from respira_ally.application.alert.alert_service import AlertService
    from respira_ally.application.task.task_service import TaskService

    # Arrange: Services
    alert_service = AlertService(db_session)
    task_service = TaskService(db_session)

    # Create risk assessment (prerequisite)
    risk_assessment = RiskAssessmentModel(
        patient_id=patient_user.user_id,
        gold_group="B",
        cat_score=15,
        mmrc_score=2,
        exacerbation_risk="MEDIUM",
    )
    db_session.add(risk_assessment)
    await db_session.commit()
    await db_session.refresh(risk_assessment)

    # Test cases: severity → expected priority
    test_cases = [
        ("CRITICAL", "CRITICAL"),
        ("HIGH", "HIGH"),
        ("MEDIUM", "MEDIUM"),
        ("LOW", "LOW"),
    ]

    for alert_severity, expected_priority in test_cases:
        # Act: Create alert manually
        alert = AlertModel(
            patient_id=patient_user.user_id,
            alert_type="RISK_GROUP_CHANGE",
            severity=alert_severity,
            title=f"Test {alert_severity} severity alert",
            message=f"Testing {alert_severity} → {expected_priority} priority mapping",
            status="ACTIVE",
        )
        db_session.add(alert)
        await db_session.commit()
        await db_session.refresh(alert)

        # Act: Auto-generate task
        task_response = await task_service.create_task_from_alert(alert, risk_assessment)

        # Assert: Priority matches
        assert task_response.priority == expected_priority, \
            f"Alert severity {alert_severity} should map to task priority {expected_priority}, got {task_response.priority}"


@pytest.mark.asyncio
async def test_gold_group_e_priority_upgrade(
    client: TestClient,
    therapist_user: UserModel,
    patient_user: UserModel,
    db_session: AsyncSession,
):
    """
    Test priority upgrade for GOLD Group E patients

    Business Rule: GOLD Group E patients → upgrade LOW/MEDIUM to HIGH
    Scenario: Create MEDIUM severity alert for GOLD E patient
    Expected: Task priority upgraded to HIGH
    """
    from respira_ally.application.alert.alert_service import AlertService
    from respira_ally.application.task.task_service import TaskService

    # Arrange: Services
    alert_service = AlertService(db_session)
    task_service = TaskService(db_session)

    # Create risk assessment with GOLD Group E (highest risk)
    risk_assessment = RiskAssessmentModel(
        patient_id=patient_user.user_id,
        gold_group="E",  # Highest risk group
        cat_score=25,
        mmrc_score=4,
        exacerbation_risk="HIGH",
    )
    db_session.add(risk_assessment)
    await db_session.commit()
    await db_session.refresh(risk_assessment)

    # Act: Create MEDIUM severity alert
    alert = AlertModel(
        patient_id=patient_user.user_id,
        alert_type="RISK_GROUP_CHANGE",
        severity="MEDIUM",  # Base priority: MEDIUM
        title="GOLD Group E patient alert",
        message="Testing priority upgrade for highest-risk patients",
        status="ACTIVE",
    )
    db_session.add(alert)
    await db_session.commit()
    await db_session.refresh(alert)

    # Act: Auto-generate task
    task_response = await task_service.create_task_from_alert(alert, risk_assessment)

    # Assert: Priority upgraded to HIGH
    assert task_response.priority == "HIGH", \
        "GOLD Group E patient should upgrade MEDIUM alert to HIGH priority task"
    assert "GOLD Group E" in task_response.task_metadata["priority_reason"], \
        "Priority reason should mention GOLD Group E"


@pytest.mark.asyncio
async def test_high_risk_detected_priority_escalation(
    client: TestClient,
    therapist_user: UserModel,
    patient_user: UserModel,
    db_session: AsyncSession,
):
    """
    Test priority escalation for HIGH_RISK_DETECTED alert type

    Business Rule: HIGH_RISK_DETECTED alert → always CRITICAL priority
    Scenario: Create HIGH severity HIGH_RISK_DETECTED alert
    Expected: Task priority escalated to CRITICAL
    """
    from respira_ally.application.alert.alert_service import AlertService
    from respira_ally.application.task.task_service import TaskService

    # Arrange: Services
    alert_service = AlertService(db_session)
    task_service = TaskService(db_session)

    # Create risk assessment
    risk_assessment = RiskAssessmentModel(
        patient_id=patient_user.user_id,
        gold_group="C",
        cat_score=20,
        mmrc_score=3,
        exacerbation_risk="HIGH",
    )
    db_session.add(risk_assessment)
    await db_session.commit()
    await db_session.refresh(risk_assessment)

    # Act: Create HIGH_RISK_DETECTED alert with HIGH severity
    alert = AlertModel(
        patient_id=patient_user.user_id,
        alert_type="HIGH_RISK_DETECTED",  # Special alert type
        severity="HIGH",  # Base priority: HIGH
        title="High risk detected",
        message="Patient showing signs of acute exacerbation",
        status="ACTIVE",
    )
    db_session.add(alert)
    await db_session.commit()
    await db_session.refresh(alert)

    # Act: Auto-generate task
    task_response = await task_service.create_task_from_alert(alert, risk_assessment)

    # Assert: Priority escalated to CRITICAL
    assert task_response.priority == "CRITICAL", \
        "HIGH_RISK_DETECTED alert should always escalate to CRITICAL priority"
    assert "High risk detected" in task_response.task_metadata["priority_reason"], \
        "Priority reason should mention high risk alert type"


@pytest.mark.asyncio
async def test_task_without_therapist_assignment(
    client: TestClient,
    patient_user: UserModel,
    db_session: AsyncSession,
):
    """
    Test task creation when patient has no assigned therapist

    Scenario: Patient without therapist triggers alert
    Expected: Task created with status=TODO (unassigned)
    """
    from respira_ally.application.alert.alert_service import AlertService
    from respira_ally.application.task.task_service import TaskService

    # Arrange: Remove therapist assignment
    patient_profile = await db_session.get(PatientProfileModel, patient_user.user_id)
    patient_profile.therapist_id = None
    await db_session.commit()

    # Arrange: Services
    alert_service = AlertService(db_session)
    task_service = TaskService(db_session)

    # Create risk assessment
    risk_assessment = RiskAssessmentModel(
        patient_id=patient_user.user_id,
        gold_group="A",
        cat_score=8,
        mmrc_score=1,
        exacerbation_risk="LOW",
    )
    db_session.add(risk_assessment)
    await db_session.commit()
    await db_session.refresh(risk_assessment)

    # Act: Create alert
    alert = AlertModel(
        patient_id=patient_user.user_id,
        alert_type="RISK_GROUP_CHANGE",
        severity="MEDIUM",
        title="Unassigned patient alert",
        message="Testing task creation without therapist",
        status="ACTIVE",
    )
    db_session.add(alert)
    await db_session.commit()
    await db_session.refresh(alert)

    # Act: Auto-generate task
    task_response = await task_service.create_task_from_alert(alert, risk_assessment)

    # Assert: Task created but unassigned
    assert task_response.assigned_to is None, "Task should not be assigned"
    assert task_response.status == "TODO", "Unassigned task should have TODO status"


@pytest.mark.asyncio
async def test_task_metadata_completeness(
    client: TestClient,
    therapist_user: UserModel,
    patient_user: UserModel,
    db_session: AsyncSession,
):
    """
    Test task metadata contains all required information

    Scenario: Generate task from alert with risk assessment
    Expected: Task metadata includes alert info, risk data, priority reason
    """
    from respira_ally.application.alert.alert_service import AlertService
    from respira_ally.application.task.task_service import TaskService

    # Arrange: Services
    alert_service = AlertService(db_session)
    task_service = TaskService(db_session)

    # Create comprehensive risk assessment
    risk_assessment = RiskAssessmentModel(
        patient_id=patient_user.user_id,
        gold_group="D",
        cat_score=22,
        mmrc_score=3,
        exacerbation_risk="HIGH",
    )
    db_session.add(risk_assessment)
    await db_session.commit()
    await db_session.refresh(risk_assessment)

    # Act: Create alert with metadata
    alert_metadata = {
        "trigger": "daily_log",
        "symptom_severity": 3,
        "breathlessness_score": 3,
    }
    alert = AlertModel(
        patient_id=patient_user.user_id,
        alert_type="EXACERBATION_RISK",
        severity="HIGH",
        title="Exacerbation risk detected",
        message="Patient symptoms worsening",
        alert_metadata=alert_metadata,
        status="ACTIVE",
    )
    db_session.add(alert)
    await db_session.commit()
    await db_session.refresh(alert)

    # Act: Auto-generate task
    task_response = await task_service.create_task_from_alert(alert, risk_assessment)

    # Assert: Complete metadata
    metadata = task_response.task_metadata
    assert metadata is not None

    # Required fields
    assert "alert_id" in metadata
    assert "alert_type" in metadata
    assert metadata["alert_type"] == "EXACERBATION_RISK"
    assert "alert_severity" in metadata
    assert metadata["alert_severity"] == "HIGH"
    assert "auto_generated" in metadata
    assert metadata["auto_generated"] is True
    assert "priority_reason" in metadata

    # Risk assessment fields
    assert "gold_group" in metadata
    assert metadata["gold_group"] == "D"
    assert "cat_score" in metadata
    assert metadata["cat_score"] == 22
    assert "mmrc_score" in metadata
    assert metadata["mmrc_score"] == 3

    # Alert metadata propagation
    assert "alert_metadata" in metadata
    assert metadata["alert_metadata"]["trigger"] == "daily_log"


# ============================================================================
# Test: Error Resilience
# ============================================================================


@pytest.mark.asyncio
async def test_alert_creation_succeeds_despite_task_generation_failure(
    client: TestClient,
    therapist_user: UserModel,
    patient_user: UserModel,
    db_session: AsyncSession,
    monkeypatch,
):
    """
    Test error resilience: Alert creation succeeds even if task generation fails

    Business Rule: Task generation is supplementary, should not break alert workflow
    Scenario: Simulate task generation failure
    Expected: Alert created successfully, task generation logged as error
    """
    from respira_ally.application.alert.alert_service import AlertService
    from respira_ally.application.task.task_service import TaskService

    # Arrange: Services
    alert_service = AlertService(db_session)

    # Mock task creation to fail
    original_create = TaskService.create_task_from_alert

    async def failing_create_task(*args, **kwargs):
        raise Exception("Simulated task generation failure")

    monkeypatch.setattr(TaskService, "create_task_from_alert", failing_create_task)

    # Create risk assessment
    risk_assessment = RiskAssessmentModel(
        patient_id=patient_user.user_id,
        gold_group="B",
        cat_score=12,
        mmrc_score=2,
        exacerbation_risk="MEDIUM",
    )
    db_session.add(risk_assessment)
    await db_session.commit()
    await db_session.refresh(risk_assessment)

    # Count existing alerts
    alerts_before = (await db_session.execute(
        select(AlertModel).where(AlertModel.patient_id == patient_user.user_id)
    )).scalars().all()

    # Act: Create alerts (should succeed despite task generation failure)
    alerts_created = await alert_service.create_alerts_from_risk_assessment(risk_assessment)

    # Assert: Alerts created successfully
    assert len(alerts_created) > 0, "Alerts should be created despite task generation failure"

    # Verify: Alert exists in database
    alerts_after = (await db_session.execute(
        select(AlertModel).where(AlertModel.patient_id == patient_user.user_id)
    )).scalars().all()
    assert len(alerts_after) > len(alerts_before), "New alerts should exist in database"


# ============================================================================
# Test: Task Title and Description Generation
# ============================================================================


@pytest.mark.asyncio
async def test_task_title_generation_by_alert_type(
    client: TestClient,
    therapist_user: UserModel,
    patient_user: UserModel,
    db_session: AsyncSession,
):
    """
    Test task title generation based on alert type

    Scenario: Create alerts with different types
    Expected: Task title matches alert type template
    """
    from respira_ally.application.task.task_service import TaskService

    # Arrange: Service
    task_service = TaskService(db_session)

    # Create risk assessment
    risk_assessment = RiskAssessmentModel(
        patient_id=patient_user.user_id,
        gold_group="C",
        cat_score=18,
        mmrc_score=2,
        exacerbation_risk="MEDIUM",
    )
    db_session.add(risk_assessment)
    await db_session.commit()
    await db_session.refresh(risk_assessment)

    # Test cases: alert_type → expected title substring
    test_cases = [
        ("RISK_GROUP_CHANGE", "GOLD 風險分組變化"),
        ("HIGH_RISK_DETECTED", "高風險患者"),
        ("EXACERBATION_RISK", "急性惡化風險"),
    ]

    for alert_type, expected_title_part in test_cases:
        # Act: Create alert
        alert = AlertModel(
            patient_id=patient_user.user_id,
            alert_type=alert_type,
            severity="MEDIUM",
            title=f"Test {alert_type}",
            message=f"Testing {alert_type}",
            status="ACTIVE",
        )
        db_session.add(alert)
        await db_session.commit()
        await db_session.refresh(alert)

        # Act: Generate task
        task_response = await task_service.create_task_from_alert(alert, risk_assessment)

        # Assert: Title matches template
        assert expected_title_part in task_response.title, \
            f"Task title for {alert_type} should contain '{expected_title_part}', got '{task_response.title}'"


@pytest.mark.asyncio
async def test_task_description_includes_action_items(
    client: TestClient,
    therapist_user: UserModel,
    patient_user: UserModel,
    db_session: AsyncSession,
):
    """
    Test task description includes actionable items

    Scenario: Generate task from alert
    Expected: Description includes risk info and suggested actions
    """
    from respira_ally.application.task.task_service import TaskService

    # Arrange: Service
    task_service = TaskService(db_session)

    # Create risk assessment
    risk_assessment = RiskAssessmentModel(
        patient_id=patient_user.user_id,
        gold_group="D",
        cat_score=20,
        mmrc_score=3,
        exacerbation_risk="HIGH",
    )
    db_session.add(risk_assessment)
    await db_session.commit()
    await db_session.refresh(risk_assessment)

    # Act: Create alert
    alert = AlertModel(
        patient_id=patient_user.user_id,
        alert_type="EXACERBATION_RISK",
        severity="HIGH",
        title="High exacerbation risk",
        message="Patient showing multiple warning signs",
        status="ACTIVE",
    )
    db_session.add(alert)
    await db_session.commit()
    await db_session.refresh(alert)

    # Act: Generate task
    task_response = await task_service.create_task_from_alert(alert, risk_assessment)

    # Assert: Description includes key elements
    description = task_response.description
    assert "系統自動生成任務" in description
    assert "警報類型" in description
    assert "EXACERBATION_RISK" in description
    assert "警報嚴重程度" in description
    assert "HIGH" in description
    assert "風險評估資訊" in description
    assert "GOLD 分組" in description
    assert "建議行動" in description
    assert "檢查患者最新健康數據" in description
    assert "聯繫患者" in description
