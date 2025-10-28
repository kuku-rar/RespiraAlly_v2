# Changelog

All notable changes to RespiraAlly V2.0 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### 🐛 Fixed (2025-10-28)
- **P0 Critical**: Fixed PostgreSQL enum schema mismatch for Task model
  - Root cause: Alembic migration created enum types without schema specification
  - Solution: Aligned database columns and SQLAlchemy model to use `development` schema enums
  - Files modified: `backend/src/respira_ally/infrastructure/database/models/task.py`
  - Impact: Task Board drag-and-drop now fully functional, status updates persist to database
  - Verification: ✅ E2E tested with Playwright, API returns 200 OK, database updates confirmed

### 🚀 Sprint 6 Planning
- Task Board UI: Kanban board with drag-and-drop functionality ✅ **COMPLETED**
- Notification System MVP: Design and implementation
- Alert Lifecycle Management: Acknowledge/Resolve endpoints
- Technical Debt: Database-driven rule engine (DEBT-001)

---

## [Archived]

**Sprint 5 (2025-10-27)**: Task Management System + Alert UI
- 詳細內容已歸檔至：`docs/dev_logs/CHANGELOG_20251027.md`（繁體中文版本）

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
