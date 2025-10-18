# RespiraAlly V2.0 開發優先級與路線圖

**文件版本**: v1.0
**最後更新**: 2025-10-18 22:30
**作者**: TaskMaster Hub / Claude Code AI
**狀態**: Sprint 0 即將完成，準備進入 Sprint 1

---

## 📊 當前專案狀態總覽

### 整體進度 (截至 2025-10-18 22:15)

| 指標 | 數值 | 說明 |
|------|------|------|
| **總工時** | 987h | 完整 MVP 交付 (v2.5 修正) |
| **已完成** | 83h | Sprint 0 架構設計階段 |
| **整體進度** | 8.4% | Sprint 0 階段 41.7% 完成 |
| **預計完成** | 2026-02-12 | 16 週 (8 Sprints × 14 days) |

### Sprint 0 完成度分析

#### ✅ 已完成任務 (83h/199h, 41.7%)

**專案管理 (17h/87h, 19.5%)**:
- ✅ WBS 結構設計 (v2.5)
- ✅ 8 Sprint 時程規劃
- ✅ Git Workflow SOP
- ✅ PR Review SLA 政策
- ✅ CI/CD Quality Gates
- ✅ Conventional Commits Hook
- ✅ 風險識別與評估

**系統架構 (67h/116h, 57.8%)**:
- ✅ C4 Level 1-2 架構圖
- ✅ 資料庫 ER 圖設計 (13 tables)
- ✅ 完整表結構設計
- ✅ **AI 處理日誌表設計** (v2.5 新增)
- ✅ RESTful API 規範
- ✅ 前端技術棧規範
- ✅ 前端信息架構設計
- ✅ DDD 戰略設計 (7 contexts, 40+ terms, 7 aggregates)

#### 🔄 剩餘任務 (28h, Sprint 0 收尾)

| 任務編號 | 任務名稱 | 工時 | 優先級 | 依賴關係 |
|---------|---------|------|--------|----------|
| 2.1.2 | Modular Monolith 模組邊界劃分 | 8h | **P0** | 2.1.1 ✅ |
| 2.1.3 | Clean Architecture 分層設計 | 8h | **P0** | 2.1.2 |
| 2.1.4 | 事件驅動架構設計 | 8h | P1 | 2.1.3 |
| 2.2.4 | 索引策略規劃 | 4h | P1 | 2.2.2 ✅ |

---

## 🎯 開發優先級矩陣 (Prioritization Matrix)

### P0 (阻塞性任務 - 必須立即完成)

**定義**: Sprint 1 開始前必須完成，否則阻塞後續開發。

| 任務 | 理由 | 預計工時 | 目標完成日期 |
|------|------|----------|--------------|
| **2.1.2 Modular Monolith 模組邊界劃分** | 定義模組邊界，避免 Sprint 1 開發時模組耦合 | 8h | 2025-10-19 |
| **2.1.3 Clean Architecture 分層設計** | 確立分層原則，指導 Sprint 1 FastAPI 專案結構 (3.3.2) | 8h | 2025-10-19 |

**總計 P0**: 16h

### P1 (高優先級 - Sprint 0 收尾)

**定義**: Sprint 0 應該完成，但可延後至 Sprint 1 Week 1。

| 任務 | 理由 | 預計工時 | 目標完成日期 |
|------|------|----------|--------------|
| **2.1.4 事件驅動架構設計** | 定義 Domain Event 規範，影響 4.2.7 事件發布實作 | 8h | 2025-10-20 |
| **2.2.4 索引策略規劃** | 優化查詢性能，指導 3.2 Migration 索引設計 | 4h | 2025-10-20 |

**總計 P1**: 12h

### P2 (中優先級 - Sprint 1-2)

**定義**: Sprint 1-2 核心任務，按 WBS 順序執行。

| Sprint | 關鍵任務 | 工時 | 交付物 |
|--------|---------|------|--------|
| **Sprint 1 Week 1** | 環境建置 (3.1) + Schema 實作 (3.2) | 36h | Docker 環境 + PostgreSQL Schema |
| **Sprint 1 Week 2** | FastAPI 結構 (3.3) + 認證系統 (3.4) + 前端基礎 (3.5) | 60h | JWT 認證 + 登入頁 |
| **Sprint 2 Week 3** | 個案管理 API (4.1) + 日誌 API (4.2) | 60h | 病患 CRUD + 日誌提交 |
| **Sprint 2 Week 4** | LIFF 日誌表單 (4.3) + Dashboard 列表 (4.4) | 52h | 完整日誌流程 |

**總計 P2**: 208h (Sprint 1-2)

### P3 (低優先級 - Sprint 3+)

**定義**: 後續 Sprint 按既定規劃執行。

---

## 🚀 推薦開發順序 (Recommended Development Sequence)

### 階段 0: Sprint 0 收尾 (2025-10-19 ~ 2025-10-20, 28h)

**目標**: 完成所有架構設計，為 Sprint 1 掃清障礙。

#### Day 1 (2025-10-19) - P0 任務

**上午 (4h)**:
```
09:00-13:00  2.1.2 Modular Monolith 模組邊界劃分
             交付物: docs/05_architecture_and_design.md §4 模組邊界圖
             內容:
             - 定義 7 個核心模組: Auth, Patient, DailyLog, Survey, Risk, RAG, Notification
             - 確立模組間通訊規範 (Interface, Event, API)
             - 繪製模組依賴圖 (Mermaid)
```

**下午 (4h)**:
```
14:00-18:00  2.1.3 Clean Architecture 分層設計
             交付物: docs/05_architecture_and_design.md §5 分層架構圖
             內容:
             - 定義 4 層結構: Presentation → Application → Domain → Infrastructure
             - 確立依賴規則 (Dependency Inversion Principle)
             - 提供目錄結構範例 (backend/src/respira_ally/...)
```

**檢查點**: 2.1.2 和 2.1.3 完成後，Sprint 1 任務 3.3.2 (FastAPI 目錄結構) 可立即開始。

#### Day 2 (2025-10-20) - P1 任務

**上午 (4h)**:
```
09:00-13:00  2.1.4 事件驅動架構設計
             交付物: docs/05_architecture_and_design.md §6 Event Sourcing 設計
             內容:
             - 定義 Domain Event 規範 (DailyLogSubmitted, RiskScoreCalculated)
             - 設計 Event Bus 機制 (RabbitMQ Topic Exchange)
             - 確立 Event Schema (JSONB in event_logs table)
```

**下午 (2h)**:
```
14:00-16:00  2.2.4 索引策略規劃
             交付物: docs/database/schema_design_v1.0.md §4 索引策略更新
             內容:
             - 分析關鍵查詢路徑 (依從率查詢, 風險篩選, 日誌時序)
             - 設計複合索引策略 (INCLUDE, Partial Index)
             - 規劃 EXPLAIN ANALYZE 驗證計畫
```

**下午 (2h)**:
```
16:00-18:00  Sprint 0 總結與 Sprint 1 準備
             - 更新 WBS 進度為 Sprint 0 完成 (100%)
             - 撰寫 Sprint 1 Planning Agenda
             - 準備 Sprint 1 Kick-off 簡報
```

**檢查點**: Sprint 0 完成，整體進度達到 11.2% (111h/987h)。

---

### 階段 1: Sprint 1 Week 1 - 基礎設施 (2025-10-21 ~ 2025-10-25, 36h)

**目標**: Docker 環境可運行，PostgreSQL Schema 部署完成。

#### 關鍵任務順序

**Day 1 (Mon) - 環境建置**:
```
任務 3.1.1-3.1.7: Docker Compose 定義與環境驗證
工時: 16h
交付物:
- docker-compose.yml (PostgreSQL, Redis, RabbitMQ, MinIO)
- .env.example (環境變數範本)
- backend/.env (本地開發配置)
依賴: 無
```

**Day 2 (Tue) - Database Schema**:
```
任務 3.2.1-3.2.4: Alembic 初始化與核心表 Migration
工時: 12h
交付物:
- backend/alembic/versions/001_create_core_tables.sql (users, profiles)
- backend/alembic/versions/002_add_patient_health_fields.sql (已存在)
- backend/alembic/versions/003_enhance_kpi_cache_and_views.sql (已存在)
- backend/alembic/versions/004_add_ai_processing_logs.sql (已存在)
依賴: 3.1.2 (PostgreSQL 容器)
```

**Day 3 (Wed) - SQLAlchemy Models**:
```
任務 3.2.5: SQLAlchemy Models 定義
工時: 4h
交付物:
- backend/src/respira_ally/infrastructure/database/models/user.py
- backend/src/respira_ally/infrastructure/database/models/patient.py
- backend/src/respira_ally/infrastructure/database/models/daily_log.py
依賴: 3.2.4 (Migration 完成)
```

**Day 4 (Thu) - CI/CD**:
```
任務 3.1.8: GitHub Actions CI/CD 初始化
工時: 4h
交付物:
- .github/workflows/ci.yml (增強: Alembic Migration Check)
- .github/workflows/cd.yml (Zeabur 部署配置)
依賴: 3.1.7 (.env 管理)
```

**Week 1 檢查點**:
- ✅ `docker-compose up` 可正常運行
- ✅ `alembic upgrade head` 成功部署 Schema
- ✅ CI Pipeline 通過 (Black, Ruff, Mypy, Migration Check)

---

### 階段 2: Sprint 1 Week 2 - 認證與前端 (2025-10-28 ~ 2025-11-01, 60h)

**目標**: JWT 認證完整，登入/註冊頁面可用。

#### 關鍵任務順序

**Day 1-2 (Mon-Tue) - FastAPI 結構**:
```
任務 3.3: FastAPI 專案結構 (16h)
交付物:
- backend/src/respira_ally/main.py (FastAPI 入口點)
- backend/src/respira_ally/core/ (Settings, Database Session)
- backend/src/respira_ally/api/ (API Routers)
- backend/src/respira_ally/application/ (Use Cases)
- backend/src/respira_ally/domain/ (Domain Models)
- backend/src/respira_ally/infrastructure/ (Repositories)
依賴: 2.1.3 (Clean Architecture 分層設計)
```

**Day 3-4 (Wed-Thu) - 認證系統**:
```
任務 3.4: 認證授權系統 (32h)
交付物:
- backend/src/respira_ally/application/auth/jwt_service.py
- backend/src/respira_ally/api/v1/auth.py (POST /auth/register, /auth/token)
- backend/src/respira_ally/api/dependencies.py (JWT Dependency)
- LINE LIFF OAuth 整合測試
依賴: 3.3 (FastAPI 結構)
```

**Day 5 (Fri) - 前端基礎**:
```
任務 3.5: 前端基礎架構 (20h)
交付物:
- dashboard/ (Next.js 14 專案)
- liff/ (Vite + React 專案)
- dashboard/src/components/auth/LoginForm.tsx
- liff/src/pages/RegisterPage.tsx
依賴: 3.4 (認證 API)
```

**Week 2 檢查點**:
- ✅ `POST /auth/token` 返回 JWT Token
- ✅ Dashboard 登入頁可正常登入
- ✅ LIFF 註冊頁可綁定 LINE 帳號

---

### 階段 3: Sprint 2 - 病患管理與日誌 (2025-11-04 ~ 2025-11-15, 112h)

**目標**: 病患列表、日誌提交完整流程可用。

#### 優先級排序

**高優先級 (P0) - Week 3**:
1. **4.1 個案管理 API** (28h) - 基礎 CRUD，治療師可查看病患列表
2. **4.2 日誌服務 API** (32h) - 病患可提交日誌，核心業務邏輯

**中優先級 (P1) - Week 4**:
3. **4.3 LIFF 日誌表單** (28h) - 病患端 UI，Elder-First 設計
4. **4.4 Dashboard 病患列表** (24h) - 治療師端 UI，篩選與搜尋

**依賴關係圖**:
```
4.1 (個案 API) ─┬─> 4.4 (Dashboard 列表)
                │
4.2 (日誌 API) ──┴─> 4.3 (LIFF 日誌表單)
```

**檢查點**:
- ✅ 治療師可查看所有負責病患
- ✅ 病患可透過 LIFF 提交日誌
- ✅ 日誌數據即時顯示在 Dashboard

---

### 階段 4: Sprint 3-8 - 按既定規劃執行 (2025-11-18 ~ 2026-02-12, 664h)

**Sprint 3 (Week 5-6)**: 儀表板 & 問卷系統 [96h]
**Sprint 4 (Week 7-8)**: 風險引擎 & 預警 [104h]
**Sprint 5 (Week 9-10)**: RAG 系統基礎 [80h]
**Sprint 6 (Week 11-12)**: AI 語音處理鏈 [88h] ⭐ **關鍵里程碑**
**Sprint 7 (Week 13-14)**: 通知系統 & 排程 [72h]
**Sprint 8 (Week 15-16)**: 優化 & 上線準備 [96h]

---

## 🔍 關鍵路徑分析 (Critical Path Analysis)

### 關鍵路徑 1: 核心業務流程 (最長路徑)

```
Sprint 0 (架構設計)
    ↓
Sprint 1 (基礎設施 + 認證)
    ↓
Sprint 2 (病患管理 + 日誌) ⭐ 關鍵
    ↓
Sprint 3 (儀表板 + 問卷)
    ↓
Sprint 4 (風險引擎 + 預警) ⭐ 關鍵
    ↓
Sprint 6 (AI 語音) ⭐ 關鍵
    ↓
Sprint 8 (優化上線)
```

**總計關鍵路徑工時**: 536h / 987h = **54.3%** (決定專案最早完成日期)

### 關鍵路徑 2: AI 功能鏈

```
Sprint 2 (日誌 API - 提供對話上下文)
    ↓
Sprint 4 (風險引擎 - AI 決策依據)
    ↓
Sprint 5 (RAG 系統 - 知識檢索)
    ↓
Sprint 6 (AI 語音) ⭐ 整合點
```

**AI 功能依賴**: Sprint 6 依賴 Sprint 2/4/5 的基礎建設。

---

## ⚠️ 風險緩解策略 (Risk Mitigation)

### 高風險任務識別

| 任務 | 風險 | 影響 | 緩解措施 |
|------|------|------|----------|
| **2.1.2 模組邊界劃分** | 邊界劃分不清導致後續重構 | 延遲 2-4 週 | 參考 DDD 戰略設計，明確界限上下文 |
| **3.4.4 LINE LIFF 整合** | LINE Platform API 配額限制 | 阻塞病患端功能 | 優先使用 Reply API，監控 Push 用量 |
| **4.2.7 事件發布機制** | RabbitMQ 配置複雜，事件遺失 | 數據不一致 | 使用 Dead Letter Queue，建立重試機制 |
| **6.1 風險分數公式** | 公式權重爭議，需多次調整 | 延遲 1-2 週 | 提前與 PO/醫療專家對齊，建立 A/B 測試 |
| **8.2 AI Worker 服務** | OpenAI API 延遲/費用超標 | 用戶體驗差 | 15 秒超時降級，每日成本預算告警 |

### 關鍵依賴管理

**外部依賴**:
- **LINE Platform**: 提前申請 Messaging API，測試 LIFF 環境
- **OpenAI API**: 建立 API Key，設置成本預算告警 ($50/day)
- **Zeabur**: 確認部署配額，準備 PostgreSQL 連線池配置

**內部依賴**:
- **2.1.2 → 3.3.2**: 模組邊界 → FastAPI 目錄結構
- **2.1.4 → 4.2.7**: Event 設計 → 事件發布實作
- **2.2.4 → 3.2**: 索引策略 → Migration 索引建立

---

## 📊 資源分配建議 (Resource Allocation)

### 團隊角色與任務分配

**Sprint 0 收尾 (2天, 28h)**:
- **Backend Lead + Architect**: 2.1.2-2.1.4 模組與架構設計 (24h)
- **Data Engineer**: 2.2.4 索引策略規劃 (4h)

**Sprint 1 Week 1 (5天, 36h)**:
- **DevOps**: 3.1 環境建置 (20h)
- **Backend Lead**: 3.2 Database Schema (16h)

**Sprint 1 Week 2 (5天, 60h)**:
- **Backend Lead**: 3.3 FastAPI 結構 + 3.4 認證系統 (48h)
- **Frontend Lead**: 3.5 前端基礎架構 (20h)
- **並行開發**: Backend 與 Frontend 可同步進行

**Sprint 2 (2週, 112h)**:
- **Backend Lead**: 4.1 個案 API + 4.2 日誌 API (60h)
- **Frontend Lead**: 4.3 LIFF 表單 + 4.4 Dashboard 列表 (52h)
- **並行開發**: 前後端同步開發，Week 4 整合測試

---

## 🎯 成功指標與驗收標準 (Success Metrics)

### Sprint 0 完成標準

- ✅ 所有架構設計文檔完成 (05_architecture_and_design.md 完整)
- ✅ 模組邊界清晰可驗證 (7 個模組 + Interface 定義)
- ✅ 索引策略可執行 (Migration 腳本 ready)
- ✅ WBS 進度達到 11.2% (111h/987h)

### Sprint 1 完成標準

- ✅ `docker-compose up` 一鍵啟動所有服務
- ✅ CI Pipeline 綠燈 (所有 Quality Gates 通過)
- ✅ `POST /auth/token` API 返回有效 JWT
- ✅ Dashboard 登入頁可正常登入並跳轉
- ✅ LIFF 註冊頁可綁定 LINE 帳號

### Sprint 2 完成標準

- ✅ 治療師可查看病患列表 (篩選、排序、搜尋)
- ✅ 病患可透過 LIFF 提交日誌 (用藥、飲水、步數)
- ✅ 日誌數據即時顯示在 Dashboard
- ✅ 測試覆蓋率 ≥60% (核心 API 必須有測試)

---

## 🚀 下一步立即行動 (Immediate Action Items)

### 今日 (2025-10-18) 22:30 之後

**✅ 已完成**:
- WBS 更新至 v2.5 (AI 處理日誌設計完成)
- 開發優先級路線圖撰寫完成

**🔄 待辦 (今晚或明早)**:
1. **更新 05_architecture_and_design.md** 的 §4-6 章節預留位置
2. **準備 2.1.2 任務**的參考資料 (DDD 聚合邊界 vs 模組邊界)
3. **檢查開發環境**:
   ```bash
   docker --version
   docker-compose --version
   python --version  # 3.11+
   node --version    # 18+
   ```

### 明天 (2025-10-19) - Sprint 0 收尾 Day 1

**上午 09:00-13:00 (4h)**:
```
執行 2.1.2: Modular Monolith 模組邊界劃分
- 定義 7 個核心模組: Auth, Patient, DailyLog, Survey, Risk, RAG, Notification
- 繪製模組依賴圖 (Mermaid)
- 更新 05_architecture_and_design.md §4
```

**下午 14:00-18:00 (4h)**:
```
執行 2.1.3: Clean Architecture 分層設計
- 定義 4 層結構: Presentation → Application → Domain → Infrastructure
- 確立依賴規則
- 提供目錄結構範例
- 更新 05_architecture_and_design.md §5
```

### 後天 (2025-10-20) - Sprint 0 收尾 Day 2

**上午 09:00-13:00 (4h)**:
```
執行 2.1.4: 事件驅動架構設計
- 定義 Domain Event 規範
- 設計 Event Bus 機制
- 更新 05_architecture_and_design.md §6
```

**下午 14:00-18:00 (4h)**:
```
執行 2.2.4: 索引策略規劃 (2h)
Sprint 0 總結與 Sprint 1 準備 (2h)
- 更新 WBS 進度
- 撰寫 Sprint 1 Planning Agenda
```

---

## 📚 參考文檔索引

### 核心文檔
- [WBS 開發計劃](../16_wbs_development_plan.md) (v2.5)
- [架構設計文檔](../05_architecture_and_design.md) (v1.2)
- [資料庫 Schema 設計](../database/schema_design_v1.0.md) (v2.1)
- [API 設計規範](../06_api_design_specification.md)
- [前端架構規範](../12_frontend_architecture_specification.md)

### 流程文檔
- [Git Workflow SOP](./git_workflow_sop.md)
- [PR Review SLA 政策](./pr_review_sla_policy.md)
- [開發流程規範](../01_development_workflow.md)

### 設計文檔
- [DDD 戰略設計](../05_architecture_and_design.md#3-ddd-strategic-design) (§3)
- [AI 處理日誌設計](../ai/21_ai_processing_logs_design.md)

---

## 🏁 總結

### 當前狀態
- ✅ Sprint 0 完成度: **41.7%** (83h/199h)
- 🔄 剩餘任務: **28h** (2 天可完成)
- 🎯 下一步: **2.1.2 模組邊界劃分 (P0)**

### 關鍵洞察

1. **架構設計充分**: 57.8% 的系統架構已完成，為 Sprint 1 打下堅實基礎
2. **剩餘任務可控**: P0 任務僅 16h，2 天內可完成，不影響 Sprint 1 開始
3. **關鍵路徑清晰**: Sprint 2/4/6 是決定性 Sprint，需額外資源保障
4. **風險可管理**: 已識別 5 個高風險任務，緩解措施明確

### 成功因素

1. ✅ **Linus 實用主義**: 簡潔設計優於複雜方案 (單一表格 vs 多表關聯)
2. ✅ **零破壞原則**: 所有新增功能向後兼容，降低重構風險
3. ✅ **並行開發**: 前後端可同步開發，最大化團隊產出
4. ✅ **自動化優先**: CI/CD Quality Gates 確保代碼品質

---

**下一次更新**: 2025-10-20 18:00 (Sprint 0 完成)
**負責人**: TaskMaster Hub / Claude Code AI
**審核**: Technical Lead, Product Manager

---

*此路線圖遵循 VibeCoding 開發流程規範,整合 TaskMaster Hub 智能協調機制,確保專案品質與交付效率。*
