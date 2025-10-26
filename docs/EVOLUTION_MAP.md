# Evolution Map: MVP → Full Implementation

> **Purpose**: 明確定義 MVP 到完整實作的演進路徑，確保技術債可追蹤、可執行、可驗證
> **Created**: 2025-10-26
> **Philosophy**: "Good programmers worry about data structures and their relationships." - Linus Torvalds

---

## Overview

This map defines the migration path from Sprint 4 MVP to Production-Ready Full Implementation. Each phase is designed to maintain **zero breaking changes** while progressively adding capabilities.

### Linus Principle: "Never Break Userspace"
> "We don't break userspace. Any change that causes existing programs to break is a bug, no matter how 'correct' the new behavior is."

**Applied to RespiraAlly**:
- All MVP APIs remain backward compatible
- New features added via **extension**, not replacement
- Database migrations are **additive only** (new columns/tables, never drop)
- Frontend components progressively enhanced, never rewritten

---

## Phase Map

```
MVP (Sprint 4)
    ↓
Phase 1: Notification Infrastructure (4-5h)
    ↓
Phase 2: Alert Workflow Enhancement (2-3h)
    ↓
Phase 3: Configurable Rules Engine (5-6h)
    ↓
Phase 4: Rich Alert Context (2-3h)
    ↓
Phase 5: Analytics & Optimization (8-10h)
    ↓
Production Ready
```

---

## Phase 0: MVP (Sprint 4) - Current State

### What We Have ✅
- GOLD ABE Risk Assessment API
- Exacerbation Management API with auto-risk-recalculation
- Alert System with 3 fixed rules
- Dashboard displaying alerts
- DDD architecture foundation

### What We Don't Have ❌
- Notification delivery (LINE/Email)
- Configurable alert rules
- Alert acknowledgment workflow
- Historical alert analytics

### Key Characteristics
- **Data Structure**: Clean separation of Risk Assessment → Alert → Notification (deferred)
- **Backward Compatibility**: All APIs use versioned endpoints (`/api/v1/`)
- **Extension Points**: DDD architecture allows adding new use cases without touching existing code

---

## Phase 1: Notification Infrastructure (4-5h)

### Goal
Enable real-time notifications to therapists via LINE and Email.

### Database Changes (Additive Only)
```sql
-- Add notification preferences to therapist_profiles
ALTER TABLE development.therapist_profiles
ADD COLUMN notification_preferences JSONB DEFAULT '{
  "line_enabled": true,
  "email_enabled": true,
  "alert_severity_threshold": "MEDIUM"
}'::jsonb;

-- Add notification delivery tracking
CREATE TABLE development.alert_notifications (
  notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alert_id UUID NOT NULL REFERENCES development.alerts(alert_id) ON DELETE CASCADE,
  channel TEXT NOT NULL, -- 'LINE', 'EMAIL', 'SMS'
  recipient_id UUID NOT NULL,
  sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  delivered_at TIMESTAMPTZ,
  read_at TIMESTAMPTZ,
  error_message TEXT,
  metadata JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_alert_notifications_alert_id ON development.alert_notifications(alert_id);
CREATE INDEX idx_alert_notifications_recipient ON development.alert_notifications(recipient_id);
```

### Code Changes
```python
# New: backend/src/respira_ally/infrastructure/notifications/notification_service.py
class NotificationService:
    """
    Multi-channel notification delivery service.

    TODO(DEBT-001): This service extends Alert System without modifying existing code.
    Follows Linus principle: "Bad programmers worry about code. Good ones worry about data structures."
    """
    async def send_alert_notification(self, alert: Alert, therapist: TherapistProfile) -> None:
        """Send notification via therapist's preferred channels"""
        pass

# Modified: backend/src/respira_ally/application/alert/alert_service.py
class AlertService:
    def __init__(self, db: AsyncSession, notification_service: NotificationService | None = None):
        # TODO(DEBT-001): Notification service is OPTIONAL for backward compatibility
        self.notification_service = notification_service

    async def create_alert(self, ...) -> Alert:
        alert = await self.repository.create(...)

        # TODO(DEBT-001): Notification is optional - existing code works without it
        if self.notification_service:
            await self.notification_service.send_alert_notification(alert, therapist)

        return alert
```

### Backward Compatibility Guarantee
- ✅ Existing Alert API endpoints unchanged
- ✅ Alert creation still works if NotificationService not injected
- ✅ No breaking changes to frontend Dashboard

### Validation Criteria
- [ ] Therapist receives LINE notification within 5 minutes of alert creation
- [ ] Email notification delivery rate > 95%
- [ ] Notification preferences can be updated via API
- [ ] Alert creation still works without NotificationService (backward compatible)

---

## Phase 2: Alert Workflow Enhancement (2-3h)

### Goal
Add alert acknowledgment and resolution tracking.

### Database Changes (Additive Only)
```sql
-- Add workflow fields to alerts table
ALTER TABLE development.alerts
ADD COLUMN status TEXT NOT NULL DEFAULT 'ACTIVE',
ADD COLUMN acknowledged_at TIMESTAMPTZ,
ADD COLUMN acknowledged_by UUID REFERENCES development.users(user_id),
ADD COLUMN resolved_at TIMESTAMPTZ,
ADD COLUMN resolved_by UUID REFERENCES development.users(user_id),
ADD COLUMN resolution_notes TEXT;

-- Add check constraint for valid status values
ALTER TABLE development.alerts
ADD CONSTRAINT alerts_status_check
CHECK (status IN ('ACTIVE', 'ACKNOWLEDGED', 'RESOLVED', 'DISMISSED'));
```

### Code Changes
```python
# Modified: backend/src/respira_ally/domain/alert/alert.py
class Alert:
    """
    TODO(DEBT-001): Status field added as extension.
    Existing alerts automatically get status='ACTIVE' via DEFAULT.
    No breaking changes to existing code.
    """
    status: AlertStatus = AlertStatus.ACTIVE  # New field with default
    acknowledged_at: datetime | None = None
    acknowledged_by: UUID | None = None
    resolved_at: datetime | None = None
    resolution_notes: str | None = None

# New: backend/src/respira_ally/application/alert/use_cases/acknowledge_alert_use_case.py
class AcknowledgeAlertUseCase:
    """
    TODO(DEBT-001): New use case added without modifying existing AlertService.
    Follows Clean Architecture: new use cases are independent modules.
    """
    async def execute(self, alert_id: UUID, therapist_id: UUID) -> Alert:
        pass
```

### Backward Compatibility Guarantee
- ✅ Existing alerts get status='ACTIVE' automatically
- ✅ Old API responses unchanged (new fields optional)
- ✅ Frontend Dashboard continues to work without changes

### Validation Criteria
- [ ] Therapist can acknowledge alert from Dashboard
- [ ] Alert status transitions correctly (ACTIVE → ACKNOWLEDGED → RESOLVED)
- [ ] Resolution notes saved and displayed
- [ ] Old alerts (before migration) still display correctly

---

## Phase 3: Configurable Rules Engine (5-6h)

### Goal
Replace hard-coded alert rules with database-driven configurable rules.

### Database Changes (Additive Only)
```sql
-- Create alert_rules table
CREATE TABLE development.alert_rules (
  rule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  condition_expr JSONB NOT NULL, -- Rule DSL in JSON
  severity TEXT NOT NULL,
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  priority INTEGER NOT NULL DEFAULT 0,
  created_by UUID NOT NULL REFERENCES development.users(user_id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Migrate existing hard-coded rules to database
INSERT INTO development.alert_rules (name, condition_expr, severity, priority, created_by)
VALUES
  ('GOLD Group E',
   '{"type": "field_equals", "field": "gold_group", "value": "E"}'::jsonb,
   'HIGH', 100,
   (SELECT user_id FROM development.users WHERE role = 'SYSTEM' LIMIT 1)),
  ('High CAT Score',
   '{"type": "field_gte", "field": "cat_total_score", "value": 20}'::jsonb,
   'MEDIUM', 80,
   (SELECT user_id FROM development.users WHERE role = 'SYSTEM' LIMIT 1)),
  ('Frequent Exacerbations',
   '{"type": "field_gte", "field": "exacerbation_count_last_12m", "value": 3}'::jsonb,
   'MEDIUM', 70,
   (SELECT user_id FROM development.users WHERE role = 'SYSTEM' LIMIT 1));
```

### Code Changes
```python
# Modified: backend/src/respira_ally/domain/alert/alert_rule_engine.py
class AlertRuleEngine:
    """
    TODO(DEBT-001): Refactored from hard-coded rules to database-driven rules.
    Old behavior preserved: if no rules in DB, fall back to hard-coded rules.
    Ensures zero downtime during migration.
    """
    def __init__(self, rule_repository: IAlertRuleRepository):
        self.rule_repository = rule_repository

    async def evaluate(self, risk_assessment: RiskAssessment) -> List[Alert]:
        # Try database rules first
        rules = await self.rule_repository.get_enabled_rules()

        # TODO(DEBT-001): Fallback to hard-coded rules if DB empty (backward compatible)
        if not rules:
            rules = self._get_default_rules()

        return [rule.evaluate(risk_assessment) for rule in rules if rule.matches()]
```

### Backward Compatibility Guarantee
- ✅ If database rules empty, fall back to hard-coded rules
- ✅ Rule evaluation logic backward compatible
- ✅ Frontend Dashboard continues to work

### Validation Criteria
- [ ] Admin can create custom alert rules via UI
- [ ] Custom rules evaluate correctly
- [ ] Disabling a rule stops alert creation
- [ ] Rule priority affects alert order
- [ ] Migration from hard-coded rules is seamless

---

## Phase 4: Rich Alert Context (2-3h)

### Goal
Add structured metadata and clinical recommendations to alerts.

### Database Changes (Additive Only)
```sql
-- Enhance alerts.metadata with structured schema
ALTER TABLE development.alerts
ADD COLUMN recommendations JSONB;

-- Example structured metadata
UPDATE development.alerts
SET metadata = jsonb_set(
  metadata,
  '{patient_context}',
  jsonb_build_object(
    'recent_exacerbations', (SELECT COUNT(*) FROM development.exacerbations WHERE ...),
    'medication_adherence', 0.85,
    'last_visit_date', '2025-09-01'
  )
);
```

### Code Changes
```python
# New: backend/src/respira_ally/core/schemas/alert.py
class AlertMetadata(BaseModel):
    """
    TODO(DEBT-001): Structured metadata schema.
    Replaces generic dict with typed model.
    """
    patient_context: PatientContext
    risk_factors: List[RiskFactor]
    severity_justification: str

class ClinicalRecommendation(BaseModel):
    """AI-generated clinical recommendations"""
    recommendation_type: str
    description: str
    priority: int

# Modified: backend/src/respira_ally/domain/alert/alert.py
class Alert:
    metadata: AlertMetadata  # TODO(DEBT-001): Was dict, now structured
    recommendations: List[ClinicalRecommendation] = []
```

### Backward Compatibility Guarantee
- ✅ Old alerts with dict metadata still work (use Pydantic validator)
- ✅ Recommendations optional (empty list if not generated)

### Validation Criteria
- [ ] New alerts include structured metadata
- [ ] Clinical recommendations displayed in Dashboard
- [ ] Old alerts (with dict metadata) still render correctly

---

## Phase 5: Analytics & Optimization (8-10h)

### Goal
Add alert analytics, performance monitoring, and false positive detection.

### Database Changes
```sql
CREATE TABLE development.alert_analytics (
  analytics_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alert_id UUID NOT NULL REFERENCES development.alerts(alert_id),
  false_positive BOOLEAN,
  feedback_by UUID REFERENCES development.users(user_id),
  feedback_notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Code Changes
```python
# New: backend/src/respira_ally/application/analytics/alert_analytics_service.py
class AlertAnalyticsService:
    async def calculate_precision(self) -> float:
        """Calculate alert precision (true positives / total alerts)"""
        pass

    async def detect_false_positives(self) -> List[Alert]:
        """Find alerts dismissed by therapists (potential false positives)"""
        pass
```

---

## Zero-Downtime Migration Strategy

### Linus Philosophy: "Data structures, not code"
> "I will, in fact, claim that the difference between a bad programmer and a good one is whether he considers his code or his data structures more important."

### Our Approach
1. **Database migrations are ALWAYS additive** (ADD COLUMN, CREATE TABLE, never DROP)
2. **API versioning** (`/api/v1/`, `/api/v2/`) for breaking changes
3. **Feature flags** for gradual rollout
4. **Backward-compatible defaults** (new fields have sensible defaults)

### Example: Alert Workflow Migration
```python
# BEFORE (MVP)
class Alert:
    alert_id: UUID
    patient_id: UUID
    alert_type: str
    severity: str
    metadata: dict

# AFTER (Phase 2) - Zero Breaking Changes
class Alert:
    alert_id: UUID
    patient_id: UUID
    alert_type: str
    severity: str
    metadata: dict

    # NEW FIELDS with defaults - existing code doesn't break
    status: AlertStatus = AlertStatus.ACTIVE
    acknowledged_at: datetime | None = None
    acknowledged_by: UUID | None = None
```

---

## Validation Gates

Each phase must pass these gates before moving to next phase:

### Technical Gates
- [ ] All existing tests pass (zero regression)
- [ ] New tests added for new features (coverage > 80%)
- [ ] API backward compatibility verified
- [ ] Database migration tested on staging data

### Business Gates
- [ ] Feature validated with therapist feedback
- [ ] Performance metrics within acceptable range (API < 200ms)
- [ ] False positive rate < 10%

---

## Estimated Total Migration Cost

| Phase | Effort | Dependencies |
|-------|--------|-------------|
| Phase 1: Notifications | 4-5h | LINE API integration |
| Phase 2: Workflow | 2-3h | Phase 1 |
| Phase 3: Configurable Rules | 5-6h | None (can be parallel) |
| Phase 4: Rich Context | 2-3h | Phase 3 |
| Phase 5: Analytics | 8-10h | All previous phases |
| **Total** | **21-27h** | **~3-4 sprints** |

---

## Related Documents
- [Technical Debt Registry](./technical_debt/REGISTRY.md)
- [DEBT-001: Alert MVP](./technical_debt/DEBT-001-alert-mvp.md)
- [ADR-017: Alert MVP Strategy](./architecture/adr/ADR-017-alert-mvp-strategy.md)
- [ADR-018: Notification Deferred](./architecture/adr/ADR-018-notification-deferred.md)
