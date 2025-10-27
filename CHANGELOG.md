# Changelog

All notable changes to RespiraAlly V2.0 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### 🚀 Sprint 6 Planning
- Task Board UI: Kanban board with drag-and-drop functionality
- Notification System MVP: Design and implementation
- Alert Lifecycle Management: Acknowledge/Resolve endpoints
- Technical Debt: Database-driven rule engine (DEBT-001)

---

## [2.0.0-sprint5] - 2025-10-27

### ✨ Added - Task Management System (Backend Complete)

**Domain Layer**:
- Task Entity with full lifecycle management (TODO → IN_PROGRESS → DONE/CANCELLED)
  - Location: `backend/src/respira_ally/domain/entities/task.py`
  - Business methods: `assign_to()`, `start()`, `complete()`, `cancel()`

**Application Layer**:
- TaskService with complete CRUD operations
  - Location: `backend/src/respira_ally/application/task/task_service.py`
- TaskPriorityCalculator for intelligent priority assignment
  - Location: `backend/src/respira_ally/domain/services/task_priority_calculator.py`
  - Rules: CRITICAL Alert → CRITICAL Task, HIGH Alert + GOLD E → CRITICAL Task

**Infrastructure Layer**:
- ITaskRepository interface and TaskRepositoryImpl
  - Interface: `backend/src/respira_ally/domain/repositories/i_task_repository.py`
  - Implementation: `backend/src/respira_ally/infrastructure/repository_impls/task_repository_impl.py`
  - Features: Pagination, filtering (status, priority), sorting

**API Endpoints** (13 total):
- `POST /api/v1/tasks` - Create task (manual + auto)
- `GET /api/v1/tasks/patients/{patient_id}` - List patient tasks
- `GET /api/v1/tasks/therapists/{therapist_id}` - List therapist tasks
- `GET /api/v1/tasks/{task_id}` - Get task details
- `PATCH /api/v1/tasks/{task_id}` - Update task
- `POST /api/v1/tasks/{task_id}/start` - Start task
- `POST /api/v1/tasks/{task_id}/complete` - Complete task
- `POST /api/v1/tasks/{task_id}/cancel` - Cancel task
- `POST /api/v1/tasks/{task_id}/assign` - Assign task
- `DELETE /api/v1/tasks/{task_id}` - Delete task
- Plus 3 more workflow endpoints

**Auto-Generation Workflow**:
- Alert → Task automatic creation
  - Integration point: `backend/src/respira_ally/application/alert/alert_service.py`
  - Trigger condition: Alert severity >= HIGH
  - Auto-assignment: Task assigned to patient's primary therapist

### ✨ Added - Alert System UI (Frontend Complete)

**React Components**:
- AlertList component with pagination and filtering
  - Location: `frontend/dashboard/src/features/alerts/components/AlertList.tsx`
  - Test coverage: 90%

- AlertDetailModal for detailed alert information
  - Location: `frontend/dashboard/src/features/alerts/components/AlertDetailModal.tsx`
  - Test coverage: 100%

- AlertBadge with auto-refresh (30-second interval)
  - Location: `frontend/dashboard/src/features/alerts/components/AlertBadge.tsx`
  - Features: Real-time unread count, color-coded by severity

**Integration**:
- Dashboard integration with Alert components
- Patient detail page integration
- GOLD ABE risk level display

### ✅ Testing

**Backend Integration Tests**:
- 12 test cases for Task auto-generation workflow (641 lines)
  - File: `backend/tests/integration/api/test_task_auto_generation.py`
  - Coverage: Alert creation → Task generation → Priority calculation
  - Scenarios: CRITICAL/HIGH/MEDIUM alerts, GOLD E escalation

**Frontend E2E Tests**:
- Phase 1: Real API testing (passed)
- Phase 2: Mock mode testing (82% pass rate, 2 failures due to Mock Data issue)
  - Tool: Playwright
  - Coverage: Alert list, detail modal, badge interactions

### 🐛 Known Issues

**P0 - Critical (Blocks Deployment)**:
- 🚨 Mock Data Patient ID Mismatch
  - Impact: AlertBadge and AlertList fail on patient detail page
  - Root cause: Inconsistent patient_id across mock data sources
  - Location: `frontend/dashboard/mocks/` directory
  - Estimated fix: 1 hour
  - Status: ⚠️ Pending fix

### 📊 Metrics

**Sprint 5 Completion**:
- Duration: 2025-10-27 (1 day sprint)
- Work completed: 39.5 hours
  - Task Management Backend: 24h
  - Alert UI: 11.5h
  - E2E Testing: 4h
- Overall project completion: 87% (95.5h / 115.5h)

**API Coverage**:
- Task Management: 13 endpoints
- Alert System: 8 endpoints (from Sprint 4)
- Total: 21 core API endpoints

**Test Coverage**:
- Backend integration tests: 12 cases (Task auto-generation)
- Frontend E2E tests: Phase 1 + Phase 2 (82% pass rate)
- Frontend unit tests: 90-100% coverage for Alert components

### 📚 Documentation

- Updated PARALLEL_DEVELOPMENT_PLAN.md with Sprint 5 completion status
- Updated WBS (16-1_wbs_development_plan_sprint4-8.md) with Task Management details
- Added critical issues tracking (P0/P1/P2 priorities)

### 🏗️ Architecture

**Clean Architecture Compliance**:
- Domain-driven design (DDD) for Task entity
- Repository pattern for data access
- Dependency inversion (ITaskRepository interface)
- Clear separation: Domain → Application → Infrastructure → API

**Integration Points**:
- Alert Service → Task Service (auto-generation)
- Task API → Frontend (upcoming Task Board UI)
- Patient-Therapist relationship → Task assignment

---

## [Archived]

**Sprint 4 (2025-10-26)**: Alert System MVP + Exacerbation Management API
- 詳細內容已歸檔至：`docs/dev_logs/CHANGELOG_20251026.md`（繁體中文版本）

**Sprint 3 (2025-10-22)**: Risk Assessment API with GOLD ABE Classification
**Sprint 2 (2025-10-15)**: Authentication System, Database Setup
**Sprint 1 (2025-10-08)**: Project Initialization, Architecture Design

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
