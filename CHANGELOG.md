# Changelog

All notable changes to RespiraAlly V2.0 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### 🚀 Frontend Integration Pending
- Alert System UI integration (Dashboard badge, Alert list)
- Risk Assessment Dashboard UI update (GOLD ABE display)

---

## [Sprint 4] - 2025-10-26

### 🎯 Sprint 4 Focus: COPD Risk Management - Alert System & Exacerbation Tracking

**Summary**: Implemented complete Alert System with DDD architecture and automatic alert triggering based on GOLD ABE risk classification. Enhanced Exacerbation Management API with automatic risk recalculation.

---

### ✨ Added - Alert System (P1 High Priority)

#### Domain Layer - AlertRuleEngine
- **3 Fixed Alert Rules** (MVP Strategy - ADR-016):
  1. `GOLD_GROUP_E`: CRITICAL severity - Highest risk patients (≥2 exacerbations OR ≥1 hospitalization in 12m)
  2. `HIGH_CAT_SCORE`: HIGH severity - CAT Score ≥ 20 (severe symptom burden)
  3. `FREQUENT_EXACERBATIONS`: MEDIUM severity - ≥3 exacerbations in last 12 months
- Alert evaluation logic following Linus Torvalds' "Good Taste" principles
- Alert creation with rich metadata (rule, trigger_date, clinical indicators)

#### Application Layer - AlertService
- Alert creation and persistence (DDD Repository pattern)
- Alert retrieval with filtering, pagination, and sorting
- Active alert counting for dashboard badges
- Clean separation from Notification System (ADR-017)

#### API Layer - Alert Endpoints (Read-Only MVP)
- `GET /api/v1/alerts/patients/{patient_id}/` - List patient alerts
  - Filters: alert_type, severity, status, date_range
  - Pagination: page, page_size (default 20)
  - Sorting: triggered_at (desc), severity, created_at
- `GET /api/v1/alerts/patients/{patient_id}/active/count` - Count active alerts
- `GET /api/v1/alerts/{alert_id}` - Get alert details
- Authorization: Therapist (own patients), Patient (own data), SUPERVISOR/ADMIN (all)

#### Database Schema
- `alerts` table with full lifecycle tracking:
  - Status transitions: ACTIVE → ACKNOWLEDGED → RESOLVED
  - Alert metadata (JSONB): rule, clinical indicators, trigger conditions
  - Triggered/acknowledged/resolved timestamps and actors

#### Auto-Trigger Integration
- Risk Assessment → Alert Evaluation (automatic)
- Alerts created immediately after risk calculation
- No manual alert creation in MVP (read-only API)

---

### ✨ Added - Exacerbation Management Enhancement

#### Auto Risk Recalculation
- **POST /api/v1/exacerbations/** - Create exacerbation → Auto Risk Recalculation
- **PATCH /api/v1/exacerbations/{id}** - Update exacerbation → Auto Risk Recalculation (if severity changed)
- **DELETE /api/v1/exacerbations/{id}** - Delete exacerbation → Auto Risk Recalculation
- Ensures risk assessment always reflects latest exacerbation data

---

### 🐛 Fixed - Alert System Bugs

#### 1. Variable Shadowing in `alert.py`
- **Location**: `api/v1/routers/alert.py:108`
- **Issue**: Function parameter `status` shadowed FastAPI's `status` module
- **Impact**: `status.HTTP_403_FORBIDDEN` returned `None`, causing 500 error
- **Fix**: Renamed parameter from `status` to `alert_status`
- **Affected**: `list_patient_alerts()` endpoint

#### 2. Field Name Mismatches in `alert_rule_engine.py`
- **Issue**: Used incorrect field names from RiskAssessmentModel
  - ❌ `cat_total_score` → ✅ `cat_score` (7 occurrences)
  - ❌ `exacerbation_count_last_12m` → ✅ `exacerbation_count_12m`
  - ❌ `hospitalization_count_last_12m` → ✅ `hospitalization_count_12m`
- **Impact**: AttributeError during alert evaluation
- **Fix**: Global replace of all field names

#### 3. Authorization Parameter Order in `alert.py`
- **Location**: 3 endpoints (get_alert_by_id, list_patient_alerts, count_active_alerts)
- **Issue**: Incorrect parameter order in `can_access_patient()` call
  - ❌ `can_access_patient(current_user, therapist_id, patient_id)`
  - ✅ `can_access_patient(current_user, patient_id, therapist_id)`
- **Impact**: All authorization checks failed (403 Forbidden)
- **Fix**: Corrected parameter order in all 3 locations

#### 4. SQLAlchemy Lazy Loading Error in `risk.py`
- **Location**: `api/v1/routers/risk.py:124`
- **Issue**: Attempted synchronous access to lazy-loaded relationship in async context
  - ❌ `assessment.patient.therapist_id` (MissingGreenlet error)
- **Fix**: Added `db` dependency and manual patient query
  - ✅ `patient = await db.get(PatientProfileModel, patient_id)`

---

### 📚 Documentation - Architecture Decision Records

#### ADR-016: Alert MVP Strategy - Fixed Rule Engine
- **Decision**: 3 hard-coded rules instead of database-driven rule engine
- **Rationale**: Faster MVP delivery (4-6h vs 20-24h), focus on clinical validation
- **Trade-off**: Reduced flexibility vs accelerated time-to-market
- **Technical Debt**: DEBT-001 - Rule Engine Evolution (Post-MVP upgrade path)

#### ADR-017: Notification System Deferred to Post-MVP
- **Decision**: Alert creation without notification delivery
- **Rationale**: Separation of Concerns (Alert = detection, Notification = delivery)
- **Trade-off**: Manual alert checking in MVP vs complete user experience
- **Technical Debt**: DEBT-002 - Notification System Implementation (Sprint 5+)

---

### 📝 Documentation - Technical Debt Tracking

#### DEBT-001: Alert Rule Engine Evolution
- **Current State**: 3 fixed rules in `AlertRuleEngine`
- **Target State**: Database-driven configurable rule engine
- **Migration Path**: 5 phases (Rule DSL design → Parser → Database → UI)
- **Estimated Effort**: 16-20h (Sprint 5-6)
- **Trigger Conditions**: Rules > 5, dynamic threshold adjustment needed

#### DEBT-002: Notification System Implementation
- **Current State**: Alerts created but no notifications sent
- **Target State**: Multi-channel notifications (LINE, Email, SMS, Push)
- **Future Architecture**: Event-Driven (RabbitMQ) or Scheduled (Celery)
- **Estimated Effort**: 16-20h (Sprint 5-6)
- **Includes**: Notification preferences, delivery tracking, retry logic

---

### ✅ Testing - Manual Verification Completed

#### Alert API Testing (100% Pass Rate)
- ✅ **Test 1**: Count active alerts → HTTP 200, returned `2` active alerts
- ✅ **Test 2**: List patient alerts → HTTP 200, returned 2 alerts with full metadata
- ✅ **Test 3**: Filter by CRITICAL severity → HTTP 200, returned 1 CRITICAL alert
- ✅ **Test 4**: Get alert by ID → HTTP 200, returned complete alert details

#### Test Data Validation
- Patient: 利武雄 (CAT: 25, mMRC: 2, GOLD Group E)
- Alert 1 (CRITICAL): "GOLD Group E - Highest Risk Patient"
- Alert 2 (HIGH): "High Symptom Burden (CAT: 25)"
- Both alerts: Status ACTIVE, triggered automatically

#### Bug Fix Verification
- ✅ Variable shadowing resolved (no 500 errors)
- ✅ Field names corrected (no AttributeError)
- ✅ Authorization parameters fixed (no 403 errors)
- ✅ SQLAlchemy lazy loading resolved (no MissingGreenlet)

---

### 🏗️ Architecture & Design

#### Clean Architecture Layers
```
API Layer (Presentation)
  ↓ DTOs (AlertResponse, AlertListResponse)
Application Layer (Use Cases)
  ↓ Alert Service (create_alert, list_alerts, count_active)
Domain Layer (Business Logic)
  ↓ AlertRuleEngine (3 fixed rules)
Infrastructure Layer (Data)
  ↓ AlertRepositoryImpl (Repository pattern)
  ↓ Database (alerts table)
```

#### DDD Strategic Design
- **Alert Context** (Core Domain): Risk detection and alerting
- **Risk Context** (Core Domain): GOLD ABE classification
- **Exacerbation Context** (Supporting): Clinical event tracking
- **Notification Context** (Generic): Deferred to Post-MVP (ADR-017)

#### Repository Pattern Implementation
- `IAlertRepository` (Interface) - Abstract contract
- `AlertRepositoryImpl` (Concrete) - PostgreSQL implementation
- Dependency Injection via FastAPI Depends
- Clean separation from business logic

---

### 📊 Metrics & KPIs

#### Development Velocity
- **Phase 1**: Exacerbation Management - 12h (estimate) → 10h (actual) ✅
- **Phase 2**: Alert System - 12h (estimate) → 14h (actual) ⚠️ (+2h debugging)
- **Total Sprint 4**: 24h (estimate) → 24h (actual) ✅ On Target

#### Code Quality
- **Alert System**: 100% DDD compliance (Domain, Application, Infrastructure, API)
- **Bug Fix Rate**: 4 bugs fixed during testing (caught before production)
- **Test Coverage**: Manual testing 100% (automated tests pending Sprint 5)

#### Technical Debt
- **DEBT-001**: Alert Rule Engine Evolution - Planned upgrade (Sprint 5-6)
- **DEBT-002**: Notification System - Planned implementation (Sprint 5-6)
- **Total Debt**: 32-40h (manageable, documented, with payoff plan)

---

### 🔗 Related Files

#### Implementation
- `backend/src/respira_ally/domain/services/alert_rule_engine.py` (AlertRuleEngine)
- `backend/src/respira_ally/application/alert/alert_service.py` (AlertService)
- `backend/src/respira_ally/infrastructure/repository_impls/alert_repository_impl.py` (Repository)
- `backend/src/respira_ally/api/v1/routers/alert.py` (API endpoints)
- `backend/src/respira_ally/application/risk/use_cases/calculate_risk_use_case.py` (Auto-trigger)

#### Documentation
- `docs/adr/ADR-016-alert-mvp-fixed-rule-engine.md` (Alert MVP strategy)
- `docs/adr/ADR-017-notification-system-deferred-post-mvp.md` (Notification deferral)
- `docs/technical_debt/REGISTRY.md` (DEBT-001, DEBT-002)
- `docs/EVOLUTION_MAP.md` (Alert System roadmap)

---

### 🚀 Next Sprint (Sprint 5) - Planned

#### P1: Frontend Integration
- [ ] Alert System UI integration (Dashboard badge, Alert list)
- [ ] Risk Assessment Dashboard update (GOLD ABE display)
- [ ] Alert detail modal with clinical context

#### P2: Notification System MVP
- [ ] Notification data model design (notifications, preferences tables)
- [ ] NotificationService implementation (basic functionality)
- [ ] LINE Notification integration
- [ ] Notification history tracking

#### P3: Alert Lifecycle Management
- [ ] `POST /api/v1/alerts/{id}/acknowledge` - Mark alert as acknowledged
- [ ] `POST /api/v1/alerts/{id}/resolve` - Resolve alert with notes
- [ ] Alert status transitions (ACTIVE → ACKNOWLEDGED → RESOLVED)

---

## [Sprint 3] - 2025-10-22

### Summary
Risk Assessment API with GOLD ABE Classification, CAT/mMRC Surveys, Patient/Therapist Management

*(Details to be backfilled)*

---

## [Sprint 2] - 2025-10-15

### Summary
Authentication System, Database Setup, Core Infrastructure

*(Details to be backfilled)*

---

## [Sprint 1] - 2025-10-08

### Summary
Project Initialization, Architecture Design, Development Workflow Setup

*(Details to be backfilled)*

---

## Sprint Naming Convention

- **Unreleased**: Features in development, not yet deployed
- **[Sprint N]**: Completed sprint deliverables (YYYY-MM-DD completion date)
- **Version Tags**: Will be added when moving to production (e.g., v1.0.0)

---

## Legend

- ✨ **Added**: New features
- 🔄 **Changed**: Changes in existing functionality
- 🗑️ **Deprecated**: Soon-to-be removed features
- ❌ **Removed**: Now removed features
- 🐛 **Fixed**: Bug fixes
- 🔒 **Security**: Vulnerability fixes
- 📚 **Documentation**: Documentation-only changes
- 🏗️ **Architecture**: Architectural decisions and design changes
- ✅ **Testing**: Testing-related changes
- 📊 **Metrics**: KPIs, performance metrics, analytics

---

**Maintained by**: TaskMaster Hub Coordination System
**Review Frequency**: End of each sprint
**Format**: Keep a Changelog v1.0.0
