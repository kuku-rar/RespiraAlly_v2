# DEBT-001: Alert System MVP Simplification

## Metadata
- **ID**: DEBT-001
- **Component**: Alert System
- **Impact**: 🟡 Medium (10-15h refactor)
- **Status**: 🟡 Active (being tracked)
- **Created**: 2025-10-26
- **Related ADR**: ADR-017 (Alert MVP Strategy), ADR-018 (Notification Deferred)

## Context

為了在 Sprint 4 時限內交付 P1 功能，Alert System 採用 MVP 簡化策略：
- **Time Budget**: 12h (vs 30h for full implementation)
- **Goal**: 驗證 GOLD ABE risk assessment 能否有效識別高風險患者
- **Trade-off**: 犧牲配置靈活性和通知機制，優先驗證核心風險評估邏輯

## MVP Simplifications

### 1. Fixed Alert Rules (vs Configurable Rule Engine)
**MVP**:
```python
# Hard-coded rules in AlertRuleEngine
RULE_GOLD_E = "GOLD Group E - Highest Risk"
RULE_HIGH_CAT = "CAT Score >= 20 (High Symptom Burden)"
RULE_FREQUENT_EXACERBATIONS = "3+ exacerbations in last 12 months"
```

**Full Implementation**:
```python
# Configurable rules from database
class AlertRule(BaseModel):
    rule_id: UUID
    name: str
    condition_expr: str  # JSON-based rule DSL
    severity: AlertSeverity
    enabled: bool
    priority: int

# Rule Builder UI for therapists to create custom rules
```

**Refactor Cost**: 5-6h
- Implement Rule DSL (JSON-based condition expressions)
- Create AlertRuleModel + RuleRepository
- Build Rule evaluation engine
- Admin UI for rule management

---

### 2. No Notification Delivery (vs Multi-Channel Notifications)
**MVP**:
```python
# TODO(DEBT-001): Notification mechanism deferred
# Alerts created in database but not delivered to therapists
# Therapists must check Dashboard manually
```

**Full Implementation**:
```python
# Multi-channel notification system
class NotificationService:
    async def send_line_notification(alert: Alert) -> None
    async def send_email_notification(alert: Alert) -> None
    async def send_sms_notification(alert: Alert) -> None

# Notification preferences per therapist
class TherapistNotificationPreferences:
    line_enabled: bool
    email_enabled: bool
    sms_enabled: bool
    alert_severity_threshold: AlertSeverity
```

**Refactor Cost**: 4-5h
- Integrate LINE Messaging API
- Integrate Email service (SendGrid/SES)
- Create NotificationService
- Add notification preferences to TherapistProfile

---

### 3. Simplified Alert Metadata (vs Rich Context)
**MVP**:
```python
class Alert:
    alert_type: str  # Simple string
    metadata: dict   # Minimal data
```

**Full Implementation**:
```python
class Alert:
    alert_type: AlertType  # Enum with rich typing
    metadata: AlertMetadata  # Structured schema
    context: AlertContext  # Patient history snapshot
    recommendations: List[ClinicalRecommendation]  # AI-generated suggestions
```

**Refactor Cost**: 2-3h
- Define AlertMetadata schemas
- Add clinical recommendation generator
- Integrate with patient history service

---

### 4. No Alert Acknowledgment Workflow (vs Full Lifecycle)
**MVP**:
```python
# Alerts created with status = "ACTIVE"
# No acknowledgment or resolution tracking
```

**Full Implementation**:
```python
class Alert:
    status: AlertStatus  # ACTIVE, ACKNOWLEDGED, RESOLVED, DISMISSED
    acknowledged_at: datetime | None
    acknowledged_by: UUID | None
    resolved_at: datetime | None
    resolution_notes: str | None

# Alert lifecycle methods
async def acknowledge_alert(alert_id: UUID, therapist_id: UUID)
async def resolve_alert(alert_id: UUID, notes: str)
async def dismiss_alert(alert_id: UUID, reason: str)
```

**Refactor Cost**: 2-3h
- Add workflow state machine
- Implement acknowledgment endpoints
- Add resolution tracking

---

## Total Refactor Cost: 13-17h

## Migration Path (from Evolution Map)

### Phase 1: Enable Notification Delivery (4-5h)
1. Integrate LINE Messaging API
2. Create NotificationService
3. Add therapist notification preferences
4. Test end-to-end notification flow

### Phase 2: Implement Alert Workflow (2-3h)
1. Add acknowledgment/resolution fields to AlertModel
2. Create acknowledgment endpoints
3. Update Dashboard to show alert lifecycle

### Phase 3: Configurable Rules (5-6h)
1. Design Rule DSL
2. Create Rule management API
3. Build Admin UI for rule creation
4. Migrate hard-coded rules to database

### Phase 4: Rich Alert Context (2-3h)
1. Define structured metadata schemas
2. Add clinical recommendation generator
3. Integrate patient history context

---

## Validation Criteria (MVP → Full)

### MVP Success Metrics
- ✅ Alerts created successfully for high-risk patients
- ✅ Alert rules correctly evaluate risk assessments
- ✅ Dashboard displays alerts to therapists
- ✅ No false positives (precision > 90%)

### Full Implementation Success Metrics
- ✅ Therapists receive LINE notifications within 5 minutes
- ✅ Email notifications have 90% open rate
- ✅ Custom rules can be created without code changes
- ✅ Alert acknowledgment rate > 95%
- ✅ Alert resolution time < 24h average

---

## Code Locations

### MVP Implementation
- Domain: `backend/src/respira_ally/domain/alert/alert_rule_engine.py`
- Repository: `backend/src/respira_ally/infrastructure/repositories/alert_repository_impl.py`
- Service: `backend/src/respira_ally/application/alert/alert_service.py`
- API: `backend/src/respira_ally/api/v1/routers/alert.py`

### Full Implementation (Future)
- Notification: `backend/src/respira_ally/infrastructure/notifications/` (to be created)
- Rule Management: `backend/src/respira_ally/domain/alert/rule_engine/` (to be created)
- Admin UI: `frontend/src/pages/admin/alert-rules/` (to be created)

---

## Related ADRs
- [ADR-017](../architecture/adr/ADR-017-alert-mvp-strategy.md): Alert MVP Strategy
- [ADR-018](../architecture/adr/ADR-018-notification-deferred.md): Notification Mechanism Deferred to Post-MVP
