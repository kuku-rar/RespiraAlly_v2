# Changelog

All notable changes to the RespiraAlly V2.0 project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### 待完成 (Pending)
- Dashboard 手動 UI 測試（風險篩選功能驗證）
- 完整 GOLD ABE 分類引擎實作

---

## [2.0.0-sprint4.1.6] - 2025-10-25

### ✅ 新增 (Added)
- **風險計算工具模組** (`frontend/dashboard/lib/utils/risk.ts`, 88 lines)
  - `calculateRiskLevel()`: 基於 exacerbation history 的簡化風險計算
  - `getRiskLevelLabel()`: 中文風險等級標籤 (低風險/中風險/高風險/緊急)
  - `getRiskLevelColor()`: Tailwind CSS 樣式類別（綠/黃/橙/紅色系）
  - `getRiskLevelEmoji()`: Emoji 指示器 (✅/⚠️/🔶/🚨)
- **測試報告文檔** (`docs/test_reports/sprint4-dashboard-risk-filter-test.md`)
  - 完整測試計劃與測試案例定義
  - 實作檢核清單與技術總結
  - 預期測試結果與手動測試指引

### 🎯 功能 (Features)
- **Dashboard 風險等級顯示**:
  - PatientTable 新增「風險等級」欄位
  - 彩色 badge 顯示 (emoji + 標籤 + 邊框)
  - 風險等級自動計算（基於 exacerbation_count 和 hospitalization_count）
- **風險等級標準** (快速驗證版):
  - CRITICAL (緊急): ≥3 次急性惡化 OR ≥2 次住院
  - HIGH (高風險): ≥2 次急性惡化 OR ≥1 次住院
  - MEDIUM (中風險): 1 次急性惡化
  - LOW (低風險): 0 次急性惡化
- **既有篩選功能驗證**:
  - PatientFilters 已支持風險等級篩選（下拉選單）
  - 排序功能包含「風險等級（高→低）」選項
  - 篩選條件變更時自動重置到第一頁

### 🔧 修復 (Fixed)
- **Frontend Build 錯誤修復** (`frontend/dashboard/providers/QueryProvider.tsx`)
  - 問題: `@tanstack/react-query-devtools` 在 production build 找不到模組
  - 根本原因: devtools 套件在 devDependencies，但直接導入導致 production bundling 失敗
  - 解決方案: 實作 lazy loading + 條件導入 (process.env.NODE_ENV === 'development')
  - 結果: ✅ Build 成功，所有 7 頁面生成

### 🗄️ 資料庫 (Database)
- **Migration 005 完整執行** (7 個步驟完成)
  - **Step 1-2**: 建立 5 個 ENUM 類型 + index
    - `gold_group_enum`: GOLD ABE 分組 (A, B, E)
    - `exacerbation_severity_enum`: 急性惡化嚴重程度
    - `alert_type_enum`, `alert_severity_enum`, `alert_status_enum`: 預警系統
  - **Step 3**: 建立 `exacerbations` 資料表（急性惡化事件記錄）
  - **Step 4-5**: 建立 `risk_assessments` 和 `alerts` 資料表
  - **Step 6**: 建立 trigger function `update_patient_exacerbation_summary()`
  - **Step 7**: 建立 view `patient_risk_summary`（風險摘要視圖）
  - **特殊處理**: patient_profiles 的 exacerbation 欄位已存在，跳過 ALTER TABLE 步驟

### 🔄 變更 (Changed)
- **PatientTable 組件更新** (`frontend/dashboard/components/patients/PatientTable.tsx`)
  - 新增風險等級欄位（第 2 欄）
  - 表格 colspan 從 8 更新為 9
  - 導入風險計算工具函數
- **PatientResponse 介面擴展** (`frontend/dashboard/lib/types/patient.ts`)
  - 新增欄位: `exacerbation_count_last_12m?: number`
  - 新增欄位: `hospitalization_count_last_12m?: number`
  - 新增欄位: `last_exacerbation_date?: string`

### 📚 文件 (Documentation)
- **WBS 更新**: `docs/16-1_wbs_development_plan_sprint4-8.md` v1.1
  - Sprint 4 進度更新: 17.5h → 20.5h (19.7% ≈ 20% 完成)
  - Phase 1.6 完成: Dashboard 風險篩選快速驗證實作
  - 新增任務記錄: Frontend Build 修復 + Migration 005 + 風險計算實作
- **測試報告**: `docs/test_reports/sprint4-dashboard-risk-filter-test.md`
  - 完整測試環境準備記錄
  - 5 個測試案例定義（顯示/篩選/排序/重置）
  - 預期結果與驗證清單

### 🧪 測試 (Testing)
- **測試環境準備完成**:
  - Backend API: ✅ Running on port 8000 (uvicorn)
  - Frontend Dev: ✅ Running on port 3000 (Next.js dev server)
  - 測試帳號: therapist1@respira-ally.com / SecurePass123!
  - 測試資料: 50 位患者 (5 高風險 + 45 一般風險)
- **實作驗證 Checklist**:
  - ✅ Frontend 構建錯誤修復
  - ✅ Migration 005 執行成功
  - ✅ 風險計算工具函數實作
  - ✅ PatientTable 顯示風險等級 badge
  - ✅ PatientFilters 支持風險等級篩選
  - ✅ 患者頁面整合所有組件
  - ✅ Backend API 運行正常
  - ✅ Frontend Dev Server 運行正常
  - ⏳ 手動 UI 測試 (待執行)

### ⚙️ 技術決策 (Technical Decisions)
- **快速驗證路徑**:
  - 採用簡化風險計算（基於 exacerbation history）
  - 延後完整 GOLD ABE 引擎實作至後續 Sprint
  - 理由: 快速驗證 Dashboard 篩選功能，避免過度工程
- **向後兼容策略**:
  - 保留 exacerbation 相關欄位於 patient_profiles
  - 同時建立 risk_assessments 表格供未來完整實作
  - 支持 Hybrid 策略（簡化計算 + GOLD ABE）

### 📊 工時統計
- **Phase 1.6.1**: Frontend Build 修復 [0.5h]
- **Phase 1.6.2**: Migration 005 執行 [1.0h]
- **Phase 1.6.3**: 前端風險計算與顯示 [1.5h]
- **總計**: 3.0h

### ⚠️ 已知限制 (Known Limitations)
- **簡化風險計算**: 當前僅基於 exacerbation history，未整合 CAT/mMRC/FEV1
- **測試覆蓋率**: 0% (快速驗證路徑，未建立單元測試)
- **手動 UI 測試待執行**: 需使用者驗證實際篩選功能

---

## [2.0.0-sprint2.2] - 2025-10-20

### 待完成 (Pending)
- MinIO 檔案上傳服務完整實作 (backend/src/respira_ally/infrastructure/storage/)
- 個案管理 API 完整實作 (Patient Repository, Application Service)
- 日誌服務 API (Sprint 2 Week 2)
- Dashboard 病患列表 UI (Sprint 2 Week 2)
- LIFF 日誌表單 (Sprint 2 Week 2)

---

## [2.0.0-sprint2.2] - 2025-10-20

### ✅ 新增 (Added)
- **Patient API 端點實作** (backend/src/respira_ally/api/v1/routers/patient.py, 239 lines)
  - `POST /api/v1/patients/` - 創建病患（治療師專用）
  - `GET /api/v1/patients/{user_id}` - 查詢單一病患（含權限檢查）
  - `GET /api/v1/patients/` - 列表分頁查詢（支援 page/page_size 參數）
- **Patient Schema 定義** (backend/src/respira_ally/core/schemas/patient.py, 109 lines)
  - `PatientBase`, `PatientCreate`, `PatientUpdate`
  - `PatientResponse` (含計算欄位: age, BMI)
  - `PatientListResponse` (分頁元數據)
- **API MVP 開發指南** (docs/dev-guide-api-mvp.md, 470 lines)
  - Router-first 開發原則（重複 3 次再抽象）
  - Schema 驗證優先於手寫驗證
  - 權限檢查模式化
  - HTTP 狀態碼標準化
  - 測試優先級定義（P0: Happy Path, P1: 錯誤情況, P2: 邊界值）

### 🎯 功能 (Features)
- **Patient API 計算欄位**:
  - `age`: 根據出生日期自動計算年齡
  - `bmi`: 根據身高體重自動計算 BMI (kg/m²)
- **權限控制**:
  - 治療師只能查看自己管理的病患
  - 病患只能查看自己的資料
  - POST 端點僅限治療師使用
- **分頁支援**:
  - `page`: 頁碼（0-indexed）
  - `page_size`: 每頁筆數（1-100，預設 20）
  - `has_next`: 是否有下一頁
  - `total`: 總筆數

### 🔧 修復 (Fixed)
- **Patient Router 參數順序**: 修復 FastAPI 依賴注入參數順序錯誤
  - 問題: `Depends()` 參數在 `Query()` 參數之後導致 SyntaxError
  - 解決: 依賴注入參數前置，查詢參數後置

### 🧪 測試 (Testing)
- **Patient API 手動測試**: 全部 3 個端點測試通過 ✅
  - POST /patients/: Status 201, age=65, BMI=24.4
  - GET /patients/{user_id}: Status 200, 數據一致性驗證通過
  - GET /patients/: Status 200, 分頁功能正常

### 🔄 變更 (Changed)
- **CI 測試覆蓋率調整**: .github/workflows/ci.yml
  - 覆蓋率門檻: 80% → 50% (漸進式改善策略)
  - 理由: Sprint 2-3 聚焦核心功能，後續逐步提升至 65% → 80%
- **依賴版本鎖定增強**: backend/pyproject.toml
  - FastAPI: `>=0.109.0,<0.111.0` (鎖定 0.109-0.110 系列)
  - SQLAlchemy: `>=2.0.25,<2.1.0` (鎖定 2.0 系列)
  - Pydantic: `>=2.5.3,<2.6.0` (鎖定 2.5 系列)
  - passlib: `==1.7.4` (精確版本)
  - bcrypt: `==4.3.0` (精確版本)
- **MinIO 啟動策略**: docker-compose.yml
  - 新增 `profiles: [full]` 配置
  - 預設不啟動（按需啟動：`docker-compose up -d minio`）
  - 理由: Sprint 2-5 不需要檔案上傳服務（YAGNI 原則）

### ⚠️ 已知技術債務 (Known Technical Debt)
- **Therapist Registration 未創建 TherapistProfile**
  - 位置: `backend/src/respira_ally/api/v1/routers/patient.py:104`
  - TODO 註解: "Once TherapistProfile is created during registration, use TherapistProfileModel"
  - 暫時解法: 驗證 User.role == THERAPIST
  - 根本解法: 修改 registration use case（排程至 Sprint 3+）
  - 影響: 需手動創建 TherapistProfile 記錄進行測試

### 📚 文件 (Documentation)
- **API MVP 開發指南**: docs/dev-guide-api-mvp.md
  - 開發原則 5 條（Router 優先、測試策略、Schema 驗證等）
  - 開發流程 4 步驟（Schema → Model → API → Test）
  - 常見問題解答
- **WBS 更新**: docs/16_wbs_development_plan.md v3.0.5
  - Sprint 2 進度更新: 0% → 12.0% (17.75h/147.75h)
  - Task 4.1.3, 4.1.4, 4.1.6 完成 (14h)
  - Task 4.1.8, 4.1.9 新增並完成 (3.75h)
  - Task 4.1.1, 4.1.2 延後 (Router-first 原則)

### 📊 工時統計
- **Day 1 上午**: P0 技術債務修復 (2.5h)
  - CI 覆蓋率調整、依賴鎖定、MinIO 優化、開發指南撰寫
- **Day 1 下午**: Patient API 實作與測試 (3.5h)
  - Schema 設計 (0.3h)
  - Router 實作 (1.5h)
  - 手動測試與問題排查 (1.5h)
  - Git 提交 (0.25h)
- **總計**: 6h (ahead of schedule, 原計劃 Day 1 為 8h)

### 🚀 下一步 (Next Steps)
- **Day 2 上午** (2-3h): Patient API 單元測試
- **Day 2 下午** (4-5h): DailyLog API 實作（CRUD + 驗證）
- **Day 3 上午** (3-4h): DailyLog API 測試 + 統計端點
- **Day 3 下午** (2-3h): 整合測試 + 文檔更新 + Sprint 總結

---

## [2.0.0-sprint2.1] - 2025-10-20

### ✅ 新增 (Added)
- **MinIO 對象儲存**: 新增 S3 相容的對象儲存服務到 docker-compose.yml
  - API 端點: `localhost:9000`
  - 管理介面: `localhost:9001`
  - 預備檔案上傳基礎設施
- **GitHub Actions 依賴安全檢查**: 新增 dependency-check job
  - Python 依賴掃描: pip-audit
  - JavaScript 依賴掃描: npm audit (Dashboard + LIFF)
  - 過時依賴版本檢查: uv pip list --outdated, npm outdated

### 🔧 修復 (Fixed)
- **Auth API bcrypt 相容性**: 修復 bcrypt 5.0.0 與 passlib 1.7.4 不相容問題
  - 診斷: bcrypt 5.0 移除 `__about__` 屬性導致 passlib 初始化失敗
  - 解決: 降級 bcrypt 到 4.3.0 (穩定版本)
  - 影響: 密碼雜湊功能正常運作
- **UserRole Enum 大小寫不一致**: 修復 Python code 與數據庫 Enum 定義不一致
  - 問題: Python 定義 `PATIENT = "patient"` vs 數據庫 `Enum("PATIENT", "THERAPIST")`
  - 解決: 統一使用大寫 `PATIENT = "PATIENT"`, `THERAPIST = "THERAPIST"`
  - 驗證: 治療師註冊端點測試通過，返回完整 JWT tokens

### 🧪 測試 (Testing)
- **治療師註冊端點驗證**: POST `/api/v1/auth/therapist/register` 成功測試
  - 輸入: email, password (8+ 字元), full_name
  - 輸出: access_token, refresh_token, user info (role: THERAPIST)
  - 確認: JWT payload 正確，bcrypt 雜湊驗證通過

### 🔄 變更 (Changed)
- **pyproject.toml 依賴版本**: 新增 bcrypt 版本約束
  ```toml
  "passlib[bcrypt]>=1.7.4",
  "bcrypt>=4.0.0,<5.0.0",  # 限制到穩定的 4.x
  ```
- **CI/CD Workflow 增強**: .github/workflows/ci.yml 新增 53 行依賴檢查邏輯

### 📚 文件 (Documentation)
- **WBS 更新**: docs/16_wbs_development_plan.md v3.0.4
  - 記錄 Sprint 2 Week 1 基礎建設完成 (8h)
  - 更新專案進度: Sprint 2 整體 6.3%
- **CHANGELOG 創建**: 專案根目錄新增 CHANGELOG.md

---

## [2.0.0-sprint1] - 2025-10-20

### ✅ 新增 (Added)
- **JWT 認證系統**: 完整的 JWT access/refresh token 機制
  - Access Token: 8 小時有效期
  - Refresh Token: 30 天有效期
  - Token 黑名單機制 (Redis)
- **用戶註冊與登入**:
  - 治療師註冊: Email + Password (bcrypt 雜湊)
  - 治療師登入: Email + Password 驗證
  - 病患登入: LINE User ID (OAuth 自動註冊)
- **Token 刷新端點**: POST `/api/v1/auth/refresh`
- **登出端點**: POST `/api/v1/auth/logout` (支援單裝置或全裝置登出)
- **Docker Compose 服務**:
  - PostgreSQL 15 + pgvector
  - Redis 7 (Token 黑名單)
  - RabbitMQ 3 (預備消息佇列)

### 🏗️ 架構 (Architecture)
- **Clean Architecture 分層**:
  - Presentation Layer: FastAPI routers
  - Application Layer: Use Cases
  - Domain Layer: Entities, Value Objects, Domain Services
  - Infrastructure Layer: Repositories, Database Models
- **DDD 設計**: User Aggregate, Patient/Therapist Profiles
- **數據庫 Schema**: Alembic migrations 完整版本控制

### 🔄 變更 (Changed)
- **Python 版本**: Python 3.11+
- **套件管理**: 統一使用 uv (取代 pip/poetry)
- **代碼格式化**: Black + Ruff (取代 Flake8)
- **型別檢查**: Mypy strict mode

### 📚 文件 (Documentation)
- **系統架構設計**: docs/05_architecture_and_design.md (142KB)
- **API 設計規範**: docs/06_api_design_specification.md (29KB)
- **模組依賴分析**: docs/09_module_dependency_analysis.md (26KB)
- **類別關係設計**: docs/10_class_relationships_and_module_design.md (66KB)
- **WBS 開發計劃**: docs/16_wbs_development_plan.md (52KB)

---

## [2.0.0-sprint0] - 2025-10-19

### ✅ 新增 (Added)
- **專案初始化**: 建立 V2.0 專案結構
- **架構文檔**: 完整的 C4 模型、DDD 戰略設計
- **技術選型**:
  - Backend: FastAPI + SQLAlchemy + PostgreSQL + pgvector
  - Frontend: Next.js (Dashboard) + Vite (LIFF)
  - AI/ML: OpenAI GPT-4 + LangChain
  - DevOps: Docker + GitHub Actions + Zeabur

### 🏗️ 架構 (Architecture)
- **C4 模型設計**: Context, Container, Component, Code 四層架構圖
- **DDD 界限上下文**: Patient, DailyLog, Risk, Questionnaire, RAG 五大上下文
- **SOLID 原則遵循**: 完整的單一職責、開閉、里氏替換、介面隔離、依賴反轉證據

### 📚 文件 (Documentation)
- **需求文檔**: PRD (Product Requirements Document)
- **開發流程**: 01_development_workflow.md
- **專案結構指南**: 08_project_structure_guide.md
- **代碼審查指南**: 11_code_review_and_refactoring_guide.md

---

## 版本說明 (Version Notes)

### 版本命名規則
- **Major.Minor.Patch-sprint{N}.{week}**: 例如 `2.0.0-sprint2.1`
  - Major: 主版本 (2.0 為 V2.0 重寫)
  - Minor: 次版本 (功能迭代)
  - Patch: 修訂版本 (Bug 修復)
  - Sprint: Sprint 編號 (sprint0 ~ sprint8)
  - Week: Sprint 內週次 (1 或 2)

### 發布節奏
- **Sprint 週期**: 每 2 週一個 Sprint
- **版本發布**: 每完成關鍵任務即發布版本記錄
- **里程碑**: 每個 Sprint 結束發布階段性總結

---

## 聯繫方式 (Contact)

- **技術負責人**: Backend Lead
- **專案管理**: TaskMaster Hub (AI-Powered)
- **問題回報**: GitHub Issues
- **技術討論**: 團隊協作平台

---

**最後更新**: 2025-10-20 17:20
**維護者**: RespiraAlly Development Team
