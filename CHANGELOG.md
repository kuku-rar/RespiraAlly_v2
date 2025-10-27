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

### ✨ 新增功能 - 任務管理系統（後端完成）

**領域層 (Domain Layer)**：
- Task Entity 完整生命週期管理（TODO → IN_PROGRESS → DONE/CANCELLED）
  - 位置：`backend/src/respira_ally/domain/entities/task.py`
  - 業務方法：`assign_to()`、`start()`、`complete()`、`cancel()`

**應用層 (Application Layer)**：
- TaskService 完整 CRUD 操作
  - 位置：`backend/src/respira_ally/application/task/task_service.py`
- TaskPriorityCalculator 智能優先級分配
  - 位置：`backend/src/respira_ally/domain/services/task_priority_calculator.py`
  - 規則：CRITICAL Alert → CRITICAL Task，HIGH Alert + GOLD E → CRITICAL Task

**基礎設施層 (Infrastructure Layer)**：
- ITaskRepository 介面與 TaskRepositoryImpl 實作
  - 介面：`backend/src/respira_ally/domain/repositories/i_task_repository.py`
  - 實作：`backend/src/respira_ally/infrastructure/repository_impls/task_repository_impl.py`
  - 功能：分頁、過濾（狀態、優先級）、排序

**API 端點**（共 13 個）：
- `POST /api/v1/tasks` - 創建任務（手動 + 自動）
- `GET /api/v1/tasks/patients/{patient_id}` - 列出病患任務
- `GET /api/v1/tasks/therapists/{therapist_id}` - 列出治療師任務
- `GET /api/v1/tasks/{task_id}` - 取得任務詳情
- `PATCH /api/v1/tasks/{task_id}` - 更新任務
- `POST /api/v1/tasks/{task_id}/start` - 開始任務
- `POST /api/v1/tasks/{task_id}/complete` - 完成任務
- `POST /api/v1/tasks/{task_id}/cancel` - 取消任務
- `POST /api/v1/tasks/{task_id}/assign` - 分配任務
- `DELETE /api/v1/tasks/{task_id}` - 刪除任務
- 另外 3 個工作流程端點

**自動生成工作流程**：
- Alert → Task 自動創建
  - 整合點：`backend/src/respira_ally/application/alert/alert_service.py`
  - 觸發條件：Alert severity >= HIGH
  - 自動分配：任務自動分配給病患的主治療師

### ✨ 新增功能 - 告警系統 UI（前端完成）

**React 元件**：
- AlertList 元件（分頁與過濾功能）
  - 位置：`frontend/dashboard/src/features/alerts/components/AlertList.tsx`
  - 測試覆蓋率：90%

- AlertDetailModal 詳細告警資訊
  - 位置：`frontend/dashboard/src/features/alerts/components/AlertDetailModal.tsx`
  - 測試覆蓋率：100%

- AlertBadge 自動更新（30 秒間隔）
  - 位置：`frontend/dashboard/src/features/alerts/components/AlertBadge.tsx`
  - 功能：即時未讀計數、按嚴重程度顯示顏色

**整合**：
- Dashboard 整合 Alert 元件
- 病患詳細頁面整合
- GOLD ABE 風險等級顯示

### ✅ 測試

**後端整合測試**：
- 12 個測試案例涵蓋任務自動生成工作流程（641 行程式碼）
  - 檔案：`backend/tests/integration/api/test_task_auto_generation.py`
  - 覆蓋範圍：Alert 創建 → Task 生成 → 優先級計算
  - 場景：CRITICAL/HIGH/MEDIUM 告警、GOLD E 升級

**前端 E2E 測試**：
- Phase 1：真實 API 測試（通過）
- Phase 2：Mock 模式測試（82% 通過率，2 個失敗由於 Mock 資料問題）
  - 工具：Playwright
  - 覆蓋範圍：告警列表、詳情 Modal、Badge 互動

### 🐛 已知問題

**P0 - 關鍵（阻擋部署）**：
- 🚨 Mock 資料 Patient ID 不一致
  - 影響：AlertBadge 和 AlertList 在病患詳細頁面失效
  - 根本原因：patient_id 在不同 Mock 資料來源間不一致
  - 位置：`frontend/dashboard/mocks/` 目錄
  - 預估修復時間：1 小時
  - 狀態：⚠️ 待修復

### 📊 指標

**Sprint 5 完成度**：
- 時程：2025-10-27（1 天衝刺）
- 完成工時：39.5 小時
  - 任務管理後端：24h
  - 告警 UI：11.5h
  - E2E 測試：4h
- 專案整體完成度：87%（95.5h / 115.5h）

**API 覆蓋率**：
- 任務管理：13 個端點
- 告警系統：8 個端點（來自 Sprint 4）
- 總計：21 個核心 API 端點

**測試覆蓋率**：
- 後端整合測試：12 個案例（任務自動生成）
- 前端 E2E 測試：Phase 1 + Phase 2（82% 通過率）
- 前端單元測試：90-100% 覆蓋 Alert 元件

### 📚 文件

- 更新 PARALLEL_DEVELOPMENT_PLAN.md 包含 Sprint 5 完成狀態
- 更新 WBS (16-1_wbs_development_plan_sprint4-8.md) 包含任務管理詳細資訊
- 新增關鍵問題追蹤（P0/P1/P2 優先級）

### 🏗️ 架構

**Clean Architecture 合規性**：
- Task Entity 採用領域驅動設計（DDD）
- 資料存取採用 Repository 模式
- 依賴反轉（ITaskRepository 介面）
- 清晰分層：Domain → Application → Infrastructure → API

**整合點**：
- Alert Service → Task Service（自動生成）
- Task API → Frontend（即將推出的 Task Board UI）
- Patient-Therapist 關係 → 任務分配

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
