# RespiraAlly V2.0 工作分解結構 (WBS) 開發計劃

---

**文件版本 (Document Version):** `v3.3.4` ✅ Sprint 3 完成 + 技術債 P0/P1/P2 完成 - 100% 交付 (96h/96h)
**最後更新 (Last Updated):** `2025-10-24 00:15`
**主要作者 (Lead Author):** `TaskMaster Hub / Claude Code AI`
**審核者 (Reviewers):** `Technical Lead, Product Manager, Architecture Team, Client Stakeholders`
**狀態 (Status):** `執行中 - Sprint 1-3 完成 (Sprint 1: 85.6%, Sprint 2: 85.9%, Sprint 3: 100% ✅) + 技術債 P0/P1/P2 完成 (292/310 issues) - 實用主義路線成功交付 | 總工時: 1033h | 累計進度: ~44.5% | 品質: 前後端 builds ✅, pytest 139 tests ✅, mypy clean ✅ | ADR: ADR-010 (範圍調整), ADR-011 (TTS 方案)`

---

## 目錄 (Table of Contents)

1. [專案總覽 (Project Overview)](#1-專案總覽-project-overview)
2. [WBS 結構總覽 (WBS Structure Overview)](#2-wbs-結構總覽-wbs-structure-overview)
3. [詳細任務分解 (Detailed Task Breakdown)](#3-詳細任務分解-detailed-task-breakdown)
4. [專案進度摘要 (Project Progress Summary)](#4-專案進度摘要-project-progress-summary)
5. [風險與議題管理 (Risk & Issue Management)](#5-風險與議題管理-risk--issue-management)
6. [品質指標與里程碑 (Quality Metrics & Milestones)](#6-品質指標與里程碑-quality-metrics--milestones)

---

## 1. 專案總覽 (Project Overview)

### 🎯 專案基本資訊

| 項目 | 內容 |
|------|------|
| **專案名稱** | RespiraAlly V2.0 - COPD Patient Healthcare Platform |
| **專案經理** | TaskMaster Hub (AI-Powered Project Coordination) |
| **技術主導** | Backend Lead, Frontend Lead, AI/ML Specialist |
| **專案狀態** | 執行中 (In Progress) - 目前進度: ~44.5% 完成 (Sprint 1: 85.6%, Sprint 2: 85.9%, Sprint 3: 100% ✅) + 技術債 P0/P1/P2 完成 |
| **文件版本** | v3.3.4 ⭐ Sprint 3 完成 + 技術債修復 (P0/P1/P2: 292/310 issues) - 100% 交付 (96h/96h), 總工時 1033h (-80h) |
| **最後更新** | 2025-10-24 00:15 |

### ⏱️ 專案時程規劃

| 項目 | 日期/時間 |
|------|----------|
| **總工期** | 16 週 (8 Sprints × 14 days) (2025-10-21 ～ 2026-02-12) |
| **總工時** | 1033h ⭐ v3.3.1 調整 (-80h: 營養評估延後) |
| **目前進度** | ~44.5% 完成 (459.75h/1033h, Sprint 0-3 完成 ✅) |
| **當前階段** | Sprint 3 完成 - 實用主義路線成功交付: 360° 頁面 ✅ + LIFF 問卷 ✅ + TTS 無障礙 ✅ + E2E 測試 ✅ ([ADR-010](./adr/ADR-010-sprint3-mvp-scope-reduction.md), [ADR-011](./adr/ADR-011-tts-implementation-simplification.md)) |
| **預計交付** | 2026-Q1 (V2.0 MVP Release) |

### 👥 專案角色與職責

| 角色 | 負責人 | 主要職責 |
|------|--------|----------|
| **專案經理 (PM)** | TaskMaster Hub | Sprint 規劃、進度追蹤、風險管理、團隊協調 |
| **技術負責人 (TL)** | Backend Lead | FastAPI 架構、技術決策、代碼審查 |
| **產品經理 (PO)** | Product Owner | 需求定義、使用者故事、驗收標準、優先級排序 |
| **架構師 (ARCH)** | System Architect | C4 架構設計、DDD 戰略、技術選型、ADR 撰寫 |
| **AI/ML 工程師** | AI Specialist | RAG 系統、STT/LLM/TTS 整合、語音處理鏈 |
| **前端工程師** | Frontend Lead | Next.js Dashboard、LIFF、UI/UX |
| **質量控制 (QA)** | QA Engineer | 測試策略、自動化測試、品質保證 |
| **DevOps** | DevOps Engineer | CI/CD、Zeabur 部署、監控配置 |

---

## 2. WBS 結構總覽 (WBS Structure Overview)

### 📊 WBS 樹狀結構 (基於 8 Sprint 規劃)

```
1.0 專案管理與規劃 (Project Management) [87h] ⭐ v2.1 修正
├── 1.1 專案啟動與規劃 [8h] ✅ 100%
├── 1.2 Sprint 規劃與執行 [52h] ⏳ 持續性任務
├── 1.3 專案監控與報告 [8h]
└── 1.4 開發流程管控 [19h] ⭐ 新增 (整合 01_development_workflow.md)

2.0 系統架構與設計 (System Architecture) [116h] ✅ 91.4%
├── 2.1 技術架構設計 [32h] ✅ 100%
├── 2.2 資料庫設計 (PostgreSQL + pgvector) [28h] ✅ 86%
├── 2.3 API 設計規範 [16h] ✅ 63%
├── 2.4 前端架構設計 [32h] ✅ 100%
└── 2.5 DDD 戰略設計 [8h] ✅ 100%

3.0 Sprint 1: 基礎設施 & 認證系統 [104h] ⭐ v2.9 +8h [Week 1-2] - 93.5% 完成
├── 3.1 環境建置與容器化 [20h] ✅
├── 3.2 資料庫 Schema 實作 [19h] ✅ ⭐ +3h (新增 Phase 0 核心索引)
├── 3.3 FastAPI 專案結構 [16h] ✅
├── 3.4 認證授權系統 [37h] ✅ ⭐ +5h (新增 Token 黑名單與刷新機制)
└── 3.5 前端基礎架構 [20h] ⏸ 部分完成 (3.5.1-3.5.4 完成, 3.5.5-3.5.6 延後)

4.0 Sprint 2: 病患管理 & 日誌功能 [128h] ⭐ v3.0 +10h +6h Sprint 1延後 [Week 3-4]
├── 4.1 個案管理 API [28h]
├── 4.2 日誌服務 API [42h] ⭐ +10h (新增資料準確性驗證)
├── 4.3 LIFF 日誌表單 [28h]
└── 4.4 Dashboard 病患列表 [24h]

5.0 Sprint 3: 儀表板 & 問卷系統 + 無障礙 TTS [96h] ⭐ v3.3 MVP 範圍調整 [Week 5-6]
├── 5.1 個案 360° 頁面 [32h]
├── 5.2 CAT/mMRC 問卷 API [24h] ✅ 已完成
├── 5.3 LIFF 問卷頁 [24h]
├── 5.4 趨勢圖表元件 [16h] (P2 - 可選)
└── 5.6 CAT 量表無障礙設計 (TTS) ⭐ 調整 [8h] (Web Speech API 實現)
    ├── 5.6.1 useTTS Hook 實作 [2h]
    ├── 5.6.2 問卷頁朗讀按鈕整合 [2h]
    ├── 5.6.3 基本樣式與無障礙標籤 [2h]
    └── 5.6.4 跨瀏覽器測試 (iOS/Android) [2h]

⏸ 5.5 營養評估 KPI [56h] - 延後至 MVP 後 (Sprint 6+)
    理由: 需求不明確 (量表未選定、風險權重未確認)，採實用主義路線先聚焦核心功能

6.0 Sprint 4: 風險引擎 & 預警 [104h] [Week 7-8]
├── 6.1 風險分數計算引擎 [32h]
├── 6.2 異常規則引擎 [28h]
├── 6.3 任務管理 API [24h]
└── 6.4 Dashboard 預警中心 [20h]

7.0 Sprint 5: RAG 系統基礎 [80h] [Week 9-10]
├── 7.1 pgvector 擴展與向量化 [24h]
├── 7.2 衛教內容管理 API [20h]
├── 7.3 Hybrid 檢索實作 [28h]
└── 7.4 Dashboard 衛教管理頁 [8h]

8.0 Sprint 6: AI 語音處理鏈 [88h] [Week 11-12]
├── 8.1 RabbitMQ 任務佇列 [16h]
├── 8.2 AI Worker 服務 [40h]
├── 8.3 LIFF 語音錄製介面 [20h]
└── 8.4 WebSocket 推送機制 [12h]

9.0 Sprint 7: 通知系統 & 排程 [72h] [Week 13-14]
├── 9.1 APScheduler 排程服務 [16h]
├── 9.2 通知服務與提醒規則 [32h]
├── 9.3 週報自動生成 [16h]
└── 9.4 Dashboard 通知歷史 [8h]

10.0 Sprint 8: 優化 & 上線準備 [96h] [Week 15-16]
├── 10.1 效能優化 [24h]
├── 10.2 監控與告警 [20h]
├── 10.3 安全稽核 [16h]
├── 10.4 部署與 CI/CD [20h]
└── 10.5 文檔與培訓 [16h]

11.0 測試與品質保證 (Continuous) [80h]
├── 11.1 單元測試 [32h]
├── 11.2 整合測試 [24h]
├── 11.3 端到端測試 [16h]
└── 11.4 效能測試 [8h]
```

### 📈 工作包統計概覽

| WBS 模組 | 總工時 | 已完成 | 進度 | 狀態圖示 |
|---------|--------|--------|------|----------|
| 1.0 專案管理 ⭐ | 87h (+71h) | 17h | 19.5% | 🔄 |
| 2.0 系統架構 ⭐ | 148h (+36h) | 148h | 100% | ✅ |
| 3.0 Sprint 1 (基礎設施) ⭐ | 104h (+8h) | 89h | 85.6% | 🔄 |
| 4.0 Sprint 2 (病患管理) ⭐ | 155.75h (+27.75h) | 133.75h | 85.9% | 🔄 |
| 5.0 Sprint 3 (儀表板+TTS) ⭐ | 96h ⭐ 調整 | 96h | 100% | ✅ |
| 6.0 Sprint 4 (風險引擎) | 104h | 0h | 0% | ⬜ |
| 7.0 Sprint 5 (RAG 系統) | 80h | 0h | 0% | ⬜ |
| 8.0 Sprint 6 (AI 語音+營養) ⭐ | 144h (+56h) | 0h | 0% | ⬜ |
| 9.0 Sprint 7 (通知系統) | 72h | 0h | 0% | ⬜ |
| 10.0 Sprint 8 (優化上線) | 96h | 0h | 0% | ⬜ |
| 11.0 測試品保 (持續) | 80h | 0h | 0% | ⬜ |
| **總計** | **1033h** ⭐ 調整 | **459.75h** | **~44.5%** | **🔄** |

**狀態圖示說明:**
- ✅ 已完成 (Completed)
- 🔄 進行中 (In Progress)
- ⚡ 接近完成 (Near Completion)
- ⏳ 計劃中 (Planned)
- ⬜ 未開始 (Not Started)

**⚠️ 重要架構決策變更記錄:**

> **📋 完整變更日誌**: 請參閱 [開發日誌 CHANGELOG](./dev_logs/CHANGELOG.md)

### 最近更新 (Recent Updates)

#### v3.0.4 (2025-10-20) - Sprint 2 Week 1 基礎修復完成 ✅
- **階段**: Sprint 2 Week 1 基礎建設與修復
- **工時**: +8h (總計 1121h)
- **核心成就**:
  - ✅ **Auth API bcrypt 修復** (2h):
    - 診斷並修復 bcrypt 5.0.0 與 passlib 1.7.4 不相容問題
    - 降級 bcrypt 到穩定的 4.3.0 版本
    - 修復 UserRole Enum 大小寫不一致 (Python: "patient" → "PATIENT")
    - 成功測試治療師註冊端點，返回完整 JWT tokens
  - ✅ **MinIO 對象儲存配置** (2h):
    - 新增 MinIO 服務到 docker-compose.yml
    - 配置 S3 相容 API (port 9000) 與管理介面 (port 9001)
    - 預備檔案上傳服務基礎設施
  - ✅ **GitHub Actions CI/CD 增強** (4h):
    - 新增 dependency-check job (安全稽核)
    - 整合 pip-audit (Python) 與 npm audit (JavaScript)
    - 新增過時依賴版本檢查
    - 完整覆蓋: Backend (Black/Ruff/Mypy/Pytest) + Frontend (Prettier/ESLint/TypeScript/Build)
- **技術決策**:
  - 選擇 bcrypt 4.x 穩定版而非升級 passlib（最小影響原則）
  - 統一使用數據庫定義的大寫 Enum 值（向後相容）
  - MinIO 作為 S3 相容的本地對象儲存方案
- **進度**: Sprint 2 Week 1 基礎建設 100%, Sprint 2 整體 6.3%
- **里程碑**: 🎉 認證系統功能驗證通過，CI/CD 安全防護完成

### 歷史版本

| 版本 | 日期 | 主要成就 | 工時變化 |
|------|------|----------|----------|
| v2.3 | 2025-10-18 | Git Hooks 修復完成 + 開發環境就緒 | - |
| v2.2 | 2025-10-18 | 開發流程管控完成 + 文檔結構優化 | - |
| v2.1 | 2025-10-18 | 專案管理流程重構 | +71h |
| v2.0 | 2025-10-18 | 架構重大調整 (MongoDB→PG, 微服務→Modular Monolith) | -24h |

**📖 查看完整變更詳情**: [dev_logs/CHANGELOG.md](./dev_logs/CHANGELOG.md)

---

## 3. 詳細任務分解 (Detailed Task Breakdown)

### 1.0 專案管理與規劃 (Project Management)

#### 1.1 專案啟動與規劃 ✅ 已完成
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | 證據/產出 |
|---------|---------|--------|---------|------|----------|----------|----------|
| ~~1.1.1~~ | ~~專案章程制定~~ (移除 - 與 WBS 重複) | - | - | - | - | - | - |
| 1.1.2 | WBS 結構設計 | PM | 3 | ✅ | 2025-10-18 | - | WBS_DEVELOPMENT_PLAN.md v2.0 |
| 1.1.3 | 8 Sprint 時程規劃 | PM | 3 | ✅ | 2025-10-18 | 1.1.2 | WBS 第 2 節 Sprint 規劃 |
| 1.1.4 | 風險識別與評估 | TL | 2 | ✅ | 2025-10-18 | 1.1.3 | WBS 第 5 節風險矩陣 |


#### 1.2 Sprint 規劃與執行 (持續性任務 - 整個專案週期)
| 任務編號 | 任務名稱 | 負責人 | 單次工時 | 執行次數 | 總工時 | 狀態 | 完成日期 | 追蹤方式 | ADR 參考 |
|---------|---------|--------|----------|----------|--------|------|----------|----------|---------|
| 1.2.1 | Sprint Planning 儀式 | PM + Team | 2h | 8 sprints | 16h | ⏳ | 每 Sprint 第一天 | Sprint 開始日 09:00 | - |
| 1.2.2 | Daily Standup 執行 | Team | 0.25h | 80 工作天 | 20h | ⏳ | 每日 | 每日 09:30 (15 分鐘) | - |
| 1.2.3 | Sprint Review & Retro | PM + Team | 2h | 8 sprints | 16h | ⏳ | 每 Sprint 最後一天 | Sprint 結束日 14:00 | - |


#### 1.3 專案監控與報告 (自動化導向 - 減少人工勞動)
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | 證據/產出 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|----------|---------|
| 1.3.1 | GitHub Project Board 設定 | PM | 2 | ⬜ | Sprint 1 Week 1 | - | Kanban Board 連結 | - |
| 1.3.2 | CI/CD Dashboard 配置 | DevOps | 2 | ⬜ | Sprint 1 Week 2 | 3.1.8 | GitHub Actions Insights | - |
| 1.3.3 | 每週進度自動化報告 | PM | 4 | ⬜ | Sprint 2 | 1.3.1, 1.3.2 | GitHub Actions → Slack Webhook | - |

#### 1.4 開發流程管控 ⭐ 新增章節 (整合 01_development_workflow.md)
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | 證據/產出 | 參考規範 |
|---------|---------|--------|---------|------|----------|----------|----------|----------|
| 1.4.1 | Git Workflow SOP 建立 | TL | 2 | ✅ | 2025-10-18 | - | [git_workflow_sop.md](./project_management/git_workflow_sop.md) | 01_development_workflow.md §Ⅲ.1 |
| 1.4.2 | PR Review SLA 設定 | PM | 1 | ✅ | 2025-10-18 | 1.4.1 | [pr_review_sla_policy.md](./project_management/pr_review_sla_policy.md) + [PR Template](../.github/pull_request_template.md) | 01_development_workflow.md §Ⅲ.5 |
| 1.4.3 | CI/CD Quality Gates 配置 | DevOps | 4 | ✅ | 2025-10-18 | 3.1.8 | [ci.yml](../.github/workflows/ci.yml) (增強: Prettier, Coverage Threshold) | 01_development_workflow.md §Ⅳ |
| 1.4.4 | Conventional Commits 驗證 Hook | DevOps | 2 | ✅ | 2025-10-18 | 1.4.3 | [commitlint.config.js](../commitlint.config.js) + [.husky/commit-msg](../.husky/commit-msg) (✅ 已修復 CRLF) + [package-lock.json](../package-lock.json) + [setup_git_hooks.md](./project_management/setup_git_hooks.md) | 01_development_workflow.md §Ⅲ.4 |
| 1.4.5 | 技術債追蹤機制 | TL | 2 | ⬜ | Sprint 2 | 1.4.2 | GitHub Issues Template + Sprint 預留 20% 時間 | - |
| 1.4.6 | 每週流程健康度檢查 | PM | 0.5h × 16 週 = 8h | ⏳ | 持續 | 1.4.1-1.4.5 | 每週報告: PR Throughput, CI 成功率, Review Time | - |

**流程管控檢查點** (每週執行):
1. **Git Workflow 合規性**: 分支命名 (`feature/RA-XXX`), Commit 格式 (`feat:`, `fix:`)
2. **PR Review 效率**: 是否有 PR 超過 24h 無人 Review?
3. **CI/CD 健康度**: Pipeline 成功率, 失敗原因分析
4. **技術債積壓**: Issues 標記為 `tech-debt` 的數量趨勢

---

**1.0 專案管理小計**: 87h | 進度: 19.5% (17/87h 已完成)
- ✅ 已完成: 1.1.2-1.1.4 (8h) + 1.4.1-1.4.4 (9h)

**工時修正記錄** (v2.1):
- 原始估計: 16h (專案章程 2h + Sprint 執行 6h + 監控 2h + 預留 6h)
- 修正後: 87h (專案啟動 8h + Sprint 執行 52h + 監控 8h + 流程管控 19h)
- 差異: +71h (+444%)
- 修正理由:
  - Daily Standup 低估 (2h → 20h): 0.25h/天 × 80 工作天
  - Sprint 儀式低估 (4h → 32h): Planning + Review/Retro × 8 sprints
  - 新增開發流程管控 (0h → 19h): Git/PR/CI 整合，原方案完全缺失

---

### 2.0 系統架構與設計 (System Architecture)

#### 2.1 技術架構設計
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 2.1.1 | C4 Level 1-2 架構圖 | ARCH | 8 | ✅ | 2025-10-17 | 1.1.2 | 05_architecture_and_design.md |
| 2.1.2 | Modular Monolith 模組邊界劃分 | ARCH | 8 | ✅ | 2025-10-18 | 2.1.1 | 05_architecture_and_design.md §4.1 |
| 2.1.3 | Clean Architecture 分層設計 | ARCH | 8 | ✅ | 2025-10-18 | 2.1.2 | 05_architecture_and_design.md §4.2 |
| 2.1.4 | 事件驅動架構設計 | ARCH | 8 | ✅ | 2025-10-19 | 2.1.3 | 05_architecture_and_design.md §6 |

**關鍵變更**: MVP 採用 **Modular Monolith** 而非微服務，Phase 3 後可拆分。

#### 2.2 資料庫設計 (PostgreSQL Only)
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 2.2.1 | PostgreSQL ER 圖設計 | Data Engineer | 8 | ✅ | 2025-10-17 | 2.1.2 | database/schema_design_v1.0.md |
| 2.2.2 | 完整表結構設計 (13 tables) | Data Engineer | 8 | ✅ | 2025-10-17 | 2.2.1 | database/schema_design_v1.0.md |
| 2.2.3 | pgvector 向量表設計 | Data Engineer | 4 | ⬜ | Sprint 4 | 2.2.2 | ADR-002 |
| 2.2.4 | 索引策略規劃 | Data Engineer | 4 | ✅ | 2025-10-20 | 2.2.2 | database/index_strategy_planning.md |
| 2.2.5 | AI 處理日誌表設計 ⭐ 新增 | Data Engineer | 4 | ✅ | 2025-10-18 | 2.2.2 | ai/21_ai_processing_logs_design.md |

**⚠️ 重大變更**:
- 移除 MongoDB，使用 **PostgreSQL JSONB** 替代 (event_logs 表)
- 新增 `ai_processing_logs` 表支持語音對話處理日誌 (v2.5)

#### 2.3 API 設計規範
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 2.3.1 | RESTful API 規範制定 | TL | 6 | ✅ | 2025-10-17 | 2.1.2 | 06_api_design_specification.md |
| 2.3.2 | OpenAPI Schema 定義 | TL | 6 | ⬜ | Sprint 1 | 2.3.1 | - |
| 2.3.3 | 錯誤處理標準 | TL | 2 | ⬜ | Sprint 1 | 2.3.2 | - |
| 2.3.4 | JWT 認證授權設計 | Security | 4 | ✅ | 2025-10-20 | 2.3.3 | security/jwt_authentication_design.md |

#### 2.4 前端架構設計 ✅ 已完成
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 2.4.1 | 前端技術棧規範制定 | Frontend Lead | 8 | ✅ | 2025-10-18 | 2.1.2 | 12_frontend_architecture_specification.md |
| 2.4.2 | 前端信息架構設計 | Frontend Lead, UX | 16 | ✅ | 2025-10-18 | 2.4.1 | 17_frontend_information_architecture_template.md |
| 2.4.3 | Elder-First 設計原則文檔 | UX Designer | 4 | ✅ | 2025-10-18 | 2.4.1 | 包含在 12_frontend_architecture_specification.md |
| 2.4.4 | 前後端 API 契約對齊驗證 | Frontend Lead, TL | 4 | ✅ | 2025-10-18 | 2.4.2, 2.3.1 | - |

**技術決策**:
- Next.js 14 (App Router) + TanStack Query + Zustand
- LINE LIFF (病患端) + Next.js Dashboard (治療師端)
- Elder-First 設計: 18px 字體, 44px 觸控目標

#### 2.5 DDD 戰略設計 ✅ 已完成
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | 證據/產出 |
|---------|---------|--------|---------|------|----------|----------|----------|
| 2.5.1 | 界限上下文映射 | ARCH | 4 | ✅ | 2025-10-18 | 2.1.2 | 05_architecture_and_design.md §3.1 (7 contexts with Mermaid diagram) |
| 2.5.2 | 統一語言 (Ubiquitous Language) 定義 | ARCH, PO | 2 | ✅ | 2025-10-18 | 2.5.1 | 05_architecture_and_design.md §3.2 (40+ terms across 7 contexts) |
| 2.5.3 | 聚合根識別與設計 | ARCH | 2 | ✅ | 2025-10-18 | 2.5.2 | 05_architecture_and_design.md §3.3 (7 aggregates with invariants) |

#### 2.6 模組與類別設計 ✅ 已完成
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | 證據/產出 |
|---------|---------|--------|---------|------|----------|----------|----------|
| 2.6.1 | Clean Architecture 分層 UML 類別圖 | ARCH | 8 | ✅ | 2025-10-20 | 2.1.3, 2.5.3 | 10_class_relationships_and_module_design.md §2.1-2.4 (Complete class diagrams for 3 bounded contexts) |
| 2.6.2 | SOLID 原則遵循性分析 | ARCH | 4 | ✅ | 2025-10-20 | 2.6.1 | 10_class_relationships_and_module_design.md §4 (Evidence for all 5 principles) |
| 2.6.3 | 設計模式應用文檔 | ARCH | 4 | ✅ | 2025-10-20 | 2.6.1 | 10_class_relationships_and_module_design.md §5 (8 design patterns with rationale) |
| 2.6.4 | 介面契約規範定義 | ARCH, TL | 6 | ✅ | 2025-10-20 | 2.6.1 | 10_class_relationships_and_module_design.md §6 (Pre/post conditions for 15+ interfaces) |
| 2.6.5 | Python 實作範例 (Aggregates, Value Objects) | Backend Lead | 10 | ✅ | 2025-10-20 | 2.6.4 | 10_class_relationships_and_module_design.md §9 (Full implementations with tests) |

**技術成果**:
- 完整 UML 類別圖涵蓋 Patient, DailyLog, Risk 三大 Bounded Context
- 30+ 類別詳細職責定義與依賴關係圖
- 8 種設計模式應用 (Repository, Aggregate, Value Object, Domain Service, Factory, Adapter, Strategy, Observer)
- 完整 Python 程式碼範例 (Patient Aggregate, BMI Value Object, RiskEngine Domain Service)
- 單元測試範例 (Pytest, 涵蓋業務規則驗證)

**2.0 系統架構小計**: 148h | 進度: 100% (148/148h 已完成) ✅
- ✅ 已完成任務: 2.1.1-2.1.4 (32h) + 2.2.1-2.2.2+2.2.4+2.2.5 (24h) + 2.3.1+2.3.4 (10h) + 2.4.1-2.4.4 (32h) + 2.5.1-2.5.3 (8h) + 2.6.1-2.6.5 (32h) = 148h
- ⭐ v2.5 新增: 2.2.5 AI 處理日誌表設計 (+4h)
- ⭐ v2.6 新增: 2.1.2 Modular Monolith + 2.1.3 Clean Architecture (+16h)
- ⭐ v2.7 新增: 2.1.4 事件驅動架構設計 (+8h)
- ⭐ v3.0.2 新增: 2.6.1-2.6.5 模組與類別設計 (+32h) - 完整 UML 類別圖與 Python 實作範例

---

### 3.0 Sprint 1: 基礎設施 & 認證系統 [Week 1-2]

**Sprint 目標**: 建立可運行的專案骨架,完成 Docker 環境、資料庫、FastAPI 結構與使用者認證。

#### 3.1 環境建置與容器化
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 3.1.1 | Docker Compose 定義 | DevOps | 4 | ✅ | 2025-10-20 | - | - |
| 3.1.2 | PostgreSQL 容器配置 | DevOps | 2 | ✅ | 2025-10-20 | 3.1.1 | - |
| 3.1.3 | Redis 容器配置 | DevOps | 2 | ✅ | 2025-10-20 | 3.1.1 | Port 16379 避免衝突 |
| 3.1.4 | RabbitMQ 容器配置 | DevOps | 2 | ✅ | 2025-10-20 | 3.1.1 | ADR-005 |
| 3.1.5 | MinIO 容器配置 | DevOps | 2 | ⏸ | Sprint 2 | 3.1.1 | 延後到 Sprint 2 Week 1 |
| 3.1.6 | 開發環境驗證 | DevOps | 2 | ✅ | 2025-10-20 | 3.1.4 | 所有服務健康檢查通過 |
| 3.1.7 | `.env` 環境變數管理 | DevOps | 2 | ✅ | 2025-10-20 | 3.1.6 | 更新 .env.example |
| 3.1.8 | GitHub Actions CI/CD 初始化 | DevOps | 4 | ⏸ | Sprint 2 | 3.1.7 | 延後到 Sprint 2 Week 1 |

#### 3.2 資料庫 Schema 實作
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | 設計文檔參考 |
|---------|---------|--------|---------|------|----------|----------|-------------|
| 3.2.1 | Alembic 初始化 | Backend | 2 | ✅ | 2025-10-20 | 2.2.4 | database/schema_design_v1.0.md |
| 3.2.2 | 核心表 Migration (users, profiles) | Backend | 4 | ✅ | 2025-10-20 | 3.2.1 | database/schema_design_v1.0.md §2.1-2.2 |
| 3.2.3 | 業務表 Migration (daily_logs, surveys) | Backend | 4 | ✅ | 2025-10-20 | 3.2.2 | database/schema_design_v1.0.md §2.3-2.4 |
| 3.2.4 | 事件表 Migration (event_logs JSONB) | Backend | 2 | ✅ | 2025-10-20 | 3.2.3 | database/schema_design_v1.0.md §2.10 |
| 3.2.5 | SQLAlchemy Models 定義 | Backend | 4 | ✅ | 2025-10-20 | 3.2.4 | database/schema_design_v1.0.md |
| 3.2.6 | Phase 0 核心索引建立 ⭐ 新增 | Backend | 3 | ✅ | 2025-10-20 | 3.2.5 | database/index_strategy_planning.md §5.1 |

**關鍵變更**: 使用 PostgreSQL `event_logs` 表 (JSONB) 替代 MongoDB。

**數據庫實施檢查點** (基於索引策略規劃文檔):
1. **Phase 0 必須建立的核心索引** (Sprint 1):
   - `idx_users_email` (UNIQUE) - 登入查詢
   - `idx_users_line_user_id` (UNIQUE) - LINE 綁定查詢
   - `idx_daily_logs_patient_date` (patient_id, log_date DESC) - 極高頻查詢
   - `idx_surveys_patient_latest` (patient_id, submitted_at DESC) - 最新問卷
2. **索引驗證標準**:
   - ✅ EXPLAIN ANALYZE 確認使用 Index Scan
   - ✅ 高頻查詢 P95 < 50ms
   - ✅ `pg_stat_user_indexes.idx_scan > 0` 確認索引有被使用
3. **PostgreSQL 設定優化** (基於 SSD 環境):
   - `shared_buffers = 256MB`
   - `effective_cache_size = 1GB`
   - `random_page_cost = 1.1`
4. **Soft Delete 索引**: 所有帶 `deleted_at` 的表使用部分索引 `WHERE deleted_at IS NULL`

#### 3.3 FastAPI 專案結構
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 3.3.1 | uv 專案初始化 | Backend | 2 | ✅ | 2025-10-19 | - | ADR-001 |
| 3.3.2 | Clean Architecture 目錄結構 | Backend | 3 | ✅ | 2025-10-19 | 3.3.1, 2.1.3 | - |
| 3.3.3 | FastAPI `main.py` 入口點 | Backend | 2 | ✅ | 2025-10-19 | 3.3.2 | - |
| 3.3.4 | Database Session 管理 | Backend | 3 | ✅ | 2025-10-19 | 3.3.3, 3.2.5 | - |
| 3.3.5 | Pydantic Settings 配置加載 | Backend | 2 | ✅ | 2025-10-19 | 3.3.4 | - |
| 3.3.6 | 全域錯誤處理 Middleware | Backend | 2 | ✅ | 2025-10-20 | 3.3.5, 2.3.3 | - |
| 3.3.7 | CORS Middleware 配置 | Backend | 1 | ✅ | 2025-10-19 | 3.3.6 | - |
| 3.3.8 | `/health` Endpoint 實作 | Backend | 1 | ✅ | 2025-10-19 | 3.3.7 | - |

#### 3.4 認證授權系統
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | 設計文檔參考 |
|---------|---------|--------|---------|------|----------|----------|-------------|
| 3.4.1 | JWT Token 生成/驗證邏輯 (Phase 1) | Backend | 8 | ✅ | 2025-10-20 | 2.3.4 | security/jwt_authentication_design.md §6 |
| 3.4.2 | Token Blacklist + Dependencies (Phase 2) | Backend | 11 | ✅ | 2025-10-20 | 3.4.1 | security/jwt_authentication_design.md §8.1 |
| 3.4.3 | Auth Use Cases (Phase 3) | Backend | 10 | ✅ | 2025-10-20 | 3.4.2 | security/jwt_authentication_design.md §4 |
| 3.4.4 | Auth API Endpoints (Phase 4) | Backend | 5 | ✅ | 2025-10-20 | 3.4.3 | security/jwt_authentication_design.md |
| 3.4.5 | LINE LIFF OAuth 整合 | Backend | 3 | ⬜ | Week 2 | 3.4.4 | ADR-004 + security/jwt_authentication_design.md §4.1 |
| 3.4.6 | 登入失敗鎖定策略 (Redis) | Backend | 4 | ✅ | 2025-10-20 | 3.4.4 | ADR-008 + security/jwt_authentication_design.md §8.3 |

**Phase 1-5 詳細成果** (38h 已完成):
- ✅ Phase 1 (8h): JWT 工具函數 + Pydantic Models + 單元測試 (21 個測試, 98% 覆蓋率)
- ✅ Phase 2 (11h): Redis Client + Token Blacklist Service + FastAPI Dependencies (get_current_user, get_current_patient, get_current_therapist)
- ✅ Phase 3 (10h): User Repository Interface + 5 個 Use Cases (PatientLogin, TherapistLogin, Logout, RefreshToken, TherapistRegister)
- ✅ Phase 4 (5h): UserRepositoryImpl (Infrastructure) + Auth Router (5 個 API Endpoints) + OpenAPI 文檔自動生成
- ✅ Phase 5 (4h): Login Lockout Service (Progressive Lockout: 5→15min, 10→1hr, 20→4hr) + 19 個單元測試
- 📦 代碼量: ~3,470 行生產代碼 (新增 825 行) + 609 行測試代碼 (新增 317 行)
- 📝 Git Commits: 7c5e646 (Phase 1), d1ccd7a (Phase 2), 3680316 (Phase 3), ea4697d (Phase 4), (待提交 Phase 5)

**認證系統實施檢查點** (基於 JWT 設計文檔):
1. **Token 結構正確性**: 必須包含 `sub`, `role`, `exp`, `iat`, `jti` 欄位,使用 HS256 演算法
2. **安全性要求**:
   - ✅ Access Token 8 小時有效期
   - ✅ Refresh Token 30 天有效期
   - ✅ 密鑰長度 ≥ 256 bits
   - ✅ Redis 黑名單 TTL 自動過期
3. **性能目標**: Token 驗證 < 10ms (P95)
4. **降級策略**: Redis 故障時允許通過但記錄警告
5. **雙角色認證流程**:
   - Patient: LINE LIFF OAuth → 驗證 LINE ID → 簽發 JWT
   - Therapist: Email/Password → bcrypt 驗證 → 簽發 JWT
6. **Brute-Force 防護**: 3 次失敗鎖定 15 分鐘 (ADR-008)

#### 3.5 前端基礎架構
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 3.5.1 | Next.js Dashboard 專案初始化 | Frontend | 4 | ✅ | 2025-10-20 | - | - |
| 3.5.2 | Vite + React LIFF 專案初始化 | Frontend | 4 | ✅ | 2025-10-20 | - | ADR-004 |
| 3.5.3 | Tailwind CSS 配置 | Frontend | 2 | ✅ | 2025-10-20 | 3.5.1, 3.5.2 | - |
| 3.5.4 | API Client (Axios) 封裝 | Frontend | 4 | ✅ | 2025-10-20 | 3.5.3, 2.3.1 | - |
| 3.5.5 | Dashboard 登入頁 UI (US-102) | Frontend | 4 | ✅ | 2025-10-20 | 3.5.4, 3.4.6 | - |
| 3.5.6 | LIFF 註冊頁 UI (US-101) | Frontend | 2 | ✅ | 2025-10-20 | 3.5.4, 3.4.5 | - |

**3.0 Sprint 1 小計**: 104h (+8h) | 進度: 93.5% (97.2/104h 已完成)
- ✅ 已完成: 3.1 (20h) + 3.2 (19h) + 3.3 (16h) + 3.4.1-3.4.4 (34h) + 3.5.1-3.5.4 (8.2h) = 97.2h
- ⏸ 延後到 Sprint 2: 3.5.5-3.5.6 Dashboard/LIFF 登入註冊頁 (6h) - 等 LINE LIFF 整合完成
- ⬜ 待完成: 整合測試與文檔 (約 0.8h)
**關鍵交付物**: Docker Compose 環境, Database Schema + Phase 0 核心索引, JWT 認證 (含 Token 黑名單與刷新機制), 登入/註冊頁面
**⭐ v2.9 新增**:
- 認證系統: Token 黑名單機制 (3h) + Token 刷新端點 (2h) - 基於 JWT 設計文檔
- 數據庫: Phase 0 核心索引建立 (3h) - 基於索引策略規劃文檔

---

### 4.0 Sprint 2: 病患管理 & 日誌功能 [Week 3-4]

**Sprint 目標**: 完成病患 CRUD、日誌提交與查詢流程,治療師可查看病患列表。

**⭐ Sprint 1 延後項目 (Week 3 優先完成)**:
- 3.5.5 Dashboard 登入頁 UI (4h) - 依賴 3.4.6 OAuth 端點
- 3.5.6 LIFF 註冊頁 UI (2h) - 依賴 3.4.5 註冊端點

#### 4.1 個案管理 API
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 4.1.1 | Patient Repository 實作 | Backend | 4 | ⏸️ 延後 | Week 4+ | 3.2.5 | Router-first 原則 |
| 4.1.2 | Patient Application Service | Backend | 4 | ⏸️ 延後 | Week 4+ | 4.1.1 | Router-first 原則 |
| 4.1.3 | `GET /patients` API (US-501) | Backend | 6 | ✅ | 2025-10-20 | ~~4.1.2~~ 直接實作 | commit e34f975 |
| 4.1.4 | `GET /patients/{id}` API 基礎版 | Backend | 4 | ✅ | 2025-10-20 | 4.1.3 | commit e34f975 |
| 4.1.5 | 查詢參數篩選邏輯 | Backend | 4 | ✅ | 2025-10-21 | 4.1.3 | SQLAlchemy dynamic filtering |
| 4.1.6 | 分頁與排序實作 | Backend | 4 | ✅ | 2025-10-20 | ~~4.1.5~~ 提前實作 | commit e34f975 |
| 4.1.7 | `POST /patients/{id}/assign` (US-103) | Backend | 2 | ⬜ | Week 4 | 4.1.4 | - |
| 4.1.8 | `POST /patients` API 創建病患 ⭐ 新增 | Backend | 3 | ✅ | 2025-10-20 | 4.1.4 | commit e34f975 |
| 4.1.9 | Patient Schema 定義 ⭐ 新增 | Backend | 0.75 | ✅ | 2025-10-20 | 3.2.5 | commit e34f975 |

#### 4.2 日誌服務 API
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 4.2.1 | DailyLog Domain Model | Backend | 4 | ✅ | 2025-10-20 | 2.5.3 | - |
| 4.2.2 | DailyLog Repository 實作 | Backend | 4 | ✅ | 2025-10-20 | 4.2.1 | - |
| 4.2.3 | DailyLog Application Service | Backend | 4 | ✅ | 2025-10-20 | 4.2.2 | - |
| 4.2.4 | `POST /daily-logs` API (US-201) | Backend | 6 | ✅ | 2025-10-20 | 4.2.3 | Upsert 模式 |
| 4.2.5 | 每日唯一性檢查與更新邏輯 | Backend | 4 | ✅ | 2025-10-20 | 4.2.4 | 已整合至 Service |
| 4.2.6 | `GET /daily-logs` 查詢 API | Backend | 4 | ✅ | 2025-10-20 | 4.2.5 | 7 個端點 |
| 4.2.7 | `daily_log.submitted` 事件發布 | Backend | 4 | ✅ | 2025-10-21 | 4.2.4, 2.1.4 | InMemoryEventBus + Domain Events |
| 4.2.8 | Idempotency Key 支援 | Backend | 2 | ✅ | 2025-10-21 | 4.2.5 | User-scoped idempotency |
| 4.2.9 | Daily Log Schema Redesign ⭐ Breaking Change | Backend | 6 | ✅ | 2025-10-22 | 4.2.1-4.2.7 | ADR-001 |
| 4.2.10 | 資料準確性驗證 - Pydantic Validators ⭐ 新增 | Backend | 4 | ⬜ | Week 4 | 4.2.9 | 客戶需求 1 |
| 4.2.11 | 資料準確性驗證 - 前端即時提示 ⭐ 新增 | Frontend | 4 | ⬜ | Week 4 | 4.3.4 | 客戶需求 1 |
| 4.2.12 | 資料異常警告機制 ⭐ 新增 | Backend | 2 | ⬜ | Week 4 | 4.2.10 | 客戶需求 1 |

**DailyLog 完整架構詳細成果** (32h 已完成 + 2h Idempotency + 6h Schema Redesign = 40h):
- ✅ Task 4.2.1 (4h): Pydantic Schemas (DailyLogCreate, DailyLogUpdate, DailyLogResponse, DailyLogStats) - 106 行
- ✅ Task 4.2.2 (4h): Repository Interface + Implementation (12 個資料庫操作方法) - 426 行
- ✅ Task 4.2.3 (4h): Application Service (業務邏輯編排, 統計計算) - 355 行
- ✅ Task 4.2.4 (6h): POST /daily-logs 端點 (Upsert 模式, 一天一筆自動判斷)
- ✅ Task 4.2.5 (4h): 唯一性檢查 (get_by_patient_and_date + create_or_update 邏輯)
- ✅ Task 4.2.6 (4h): 7 個 RESTful 端點 (GET list, GET by ID, GET stats, GET latest, PATCH, DELETE)
- ✅ Task 4.2.7 (4h): Event Publishing (InMemoryEventBus + daily_log.submitted 事件)
- ✅ Task 4.2.8 (2h): Idempotency Key 支援 (User-scoped, 24h TTL)
- ✅ Task 4.2.9 (6h): **Daily Log Schema Redesign** ⭐ Breaking Change (參見 ADR-001)
  - **變更項目**:
    1. `steps_count` → `exercise_minutes` (RENAME) - 更符合 COPD 管理需求
    2. `medication_taken`, `water_intake_ml` → nullable (提升資料真實性)
    3. 新增 `smoking_count` 欄位 (COPD 關鍵風險因子)
  - **影響範圍**: 9 個檔案 (451 insertions, 85 deletions)
    - `docs/adr/ADR-001-daily-log-schema-redesign.md` (NEW)
    - `alembic/versions/4741100a10d7_redesign_daily_log_schema.py` (NEW)
    - `infrastructure/database/models/daily_log.py` (MODIFIED)
    - `core/schemas/daily_log.py` (MODIFIED - validators 更新)
    - `domain/events/daily_log_events.py` (MODIFIED)
    - `application/daily_log/daily_log_service.py` (MODIFIED)
    - `tests/unit/schemas/test_daily_log_validators.py` (8 tests 更新)
    - `tests/integration/api/test_daily_log_api.py` (2 tests 更新)
  - **Migration 策略**: 資料轉換公式 `exercise_minutes = ROUND(steps_count * 0.008)`
  - **測試結果**: ✅ Unit Tests 22/22 PASSED, ✅ Integration Tests (核心功能通過)
- 📦 **代碼量**: ~1,650 行生產代碼 (9 個檔案, 含 migration 與測試更新)
- 🎯 **API 端點清單**:
  1. `POST /daily-logs` - 創建或更新日誌 (Patient only, 自動 upsert)
  2. `GET /daily-logs/{log_id}` - 查詢單筆日誌 (權限檢查)
  3. `GET /daily-logs` - 列表查詢 (分頁 + 日期篩選)
  4. `GET /daily-logs/patient/{patient_id}/stats` - 統計資料 (依從率, 平均值)
  5. `GET /daily-logs/patient/{patient_id}/latest` - 最新一筆
  6. `PATCH /daily-logs/{log_id}` - 部分更新 (Patient only)
  7. `DELETE /daily-logs/{log_id}` - 刪除日誌 (Patient only)
- 🔑 **關鍵業務邏輯**:
  - **One log per day**: 每個病患每天只能有一筆日誌 (Service 層檢查)
  - **Upsert 模式**: create_or_update_daily_log() 自動判斷創建或更新
  - **統計計算**: 服藥依從率 (medication_adherence_rate), 平均飲水量, 平均步數, 心情分佈
  - **角色權限**: Patient 只能操作自己的日誌, Therapist 可查看病患日誌
- 📝 **Clean Architecture 分層**:
  - Domain: Repository Interface (抽象介面)
  - Infrastructure: Repository Implementation (SQLAlchemy)
  - Application: Service (用例編排 + 統計計算)
  - Presentation: API Router (HTTP 端點 + 權限檢查)

**⭐ v3.0 新增: 資料準確性驗證** (10h - 客戶需求 1):
- **目標**: 防止病人填寫異常數據 (如體重 999kg, 飲水量 -100ml)
- **實作範圍**:
  - 後端 Pydantic 範圍驗證 (水分 0-10000ml, 運動時間 0-1440min)
  - 前端 React Hook Form 即時驗證
  - 異常值警告但不阻擋提交 (由治療師判斷)
- **驗證標準**:
  - ✅ 負數、超大值被攔截
  - ✅ 前端顯示友善錯誤訊息
  - ✅ 異常資料標記為 `quality_score < 80`

#### 4.3 LIFF 日誌表單
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 4.3.1 | LIFF 日誌頁面路由 | Frontend | 2 | ✅ | 2025-10-20 | 3.5.2 | - |
| 4.3.2 | 日誌表單 UI 元件 | Frontend | 8 | ✅ | 2025-10-20 | 4.3.1 | - |
| 4.3.3 | Toggle (用藥) + Number Input | Frontend | 4 | ✅ | 2025-10-20 | 4.3.2 | - |
| 4.3.4 | 表單驗證邏輯 | Frontend | 4 | ✅ | 2025-10-20 | 4.3.3 | - |
| 4.3.5 | 提交後鼓勵訊息 | Frontend | 2 | ✅ | 2025-10-20 | 4.3.4, 4.2.4 | - |
| 4.3.6 | 錯誤處理與 Toast 提示 | Frontend | 4 | ✅ | 2025-10-20 | 4.3.5 | - |
| 4.3.7 | LIFF SDK 整合測試 | Frontend | 4 | ⬜ | Week 4 | 4.3.6 | - |

#### 4.4 Dashboard 病患列表
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 4.4.1 | Dashboard Layout 設計 | Frontend | 4 | ✅ | 2025-10-20 | 3.5.1 | - |
| 4.4.2 | 病患列表頁面 UI | Frontend | 6 | ✅ | 2025-10-20 | 4.4.1, 4.1.3 | - |
| 4.4.3 | Table 元件 (分頁、排序、篩選) | Frontend | 6 | ✅ | 2025-10-20 | 4.4.2 | - |
| 4.4.4 | 篩選器元件 (風險等級、依從率) | Frontend | 4 | ⬜ | Week 4 | 4.4.3 | - |
| 4.4.5 | 搜尋功能 | Frontend | 2 | ⬜ | Week 4 | 4.4.4 | - |
| 4.4.6 | 即時數據更新 (Polling/WebSocket) | Frontend | 2 | ⬜ | Week 4 | 4.4.5 | - |

**4.0 Sprint 2 小計**: 128h (+10h 資料驗證 +6h Sprint 1 延後 +3.75h Day 1 新增 +8h Schema Redesign) = 155.75h | 進度: 85.9% (133.75h/155.75h 已完成) ⭐ +32h (API 測試補充 + Database Model 修復 + Schema Redesign)
**完成任務 (Day 1-5)**:
- ✅ **Day 1 (10-20 AM)**: 4.1.3 GET /patients (6h), 4.1.4 GET /patients/{id} (4h), 4.1.6 分頁排序 (4h), 4.1.8 POST /patients (3h), 4.1.9 Patient Schema (0.75h)
- ✅ **Day 1 (10-20 PM)**: 3.5.5 Dashboard 登入頁 UI (4h), 3.5.6 LIFF 註冊頁 UI (2h), 4.4.1 Dashboard Layout (4h), 4.4.2 病患列表 UI (6h), 4.4.3 Table 元件 (6h)
- ✅ **Day 2 (10-20 晚)**: 3.4.6 Login Lockout 策略 (4h), 4.2.1-4.2.6 DailyLog 完整系統 (26h), 4.3.1-4.3.6 LIFF 日誌表單 (24h)
- ✅ **Day 3 (10-21)**: 4.1.5 查詢參數篩選 (4h), 4.2.7 Event Publishing 系統 (4h)
- ✅ **Day 4 (01-21)**: P0-1 API 測試 (12h), P0-2 conftest.py (3h), P0-3 Faker 測試資料 (4h), P0-4 Database Model 修復 (1h), 代碼審查 (4h)
- ✅ **Day 5 (10-22)**: 4.2.8 Idempotency Key (2h), 4.2.9 Daily Log Schema Redesign ⭐ Breaking Change (6h)
- ⏸️ 4.1.1 Repository 延後, 4.1.2 Application Service 延後 (Router-first 原則)
**關鍵交付物**:
- ✅ Patient API 完整實作 (GET/POST/List + Schema)
- ✅ Login Lockout 策略 (Progressive: 5→15min, 10→1hr, 20→4hr)
- ✅ DailyLog 完整架構 (7 個 API 端點 + Repository + Service + 統計計算)
- ✅ Database Model SQLAlchemy 2.0 修復 (6/6 檔案, 20 個錯誤全部修正)
- ✅ API 整合測試 (45 個測試, 21 passed, 測試覆蓋率 67%)
- ✅ Faker 測試資料生成 (14,577 daily logs, 50 patients, 5 therapists)
- ✅ 前端病患管理 UI (Dashboard 登入頁 + Dashboard Layout + 病患列表 + LIFF 註冊頁)
- ✅ LIFF 日誌表單 (路由 + UI 元件 + Toggle/Input + 驗證 + 鼓勵訊息 + 錯誤處理)
- ✅ Daily Log Schema Redesign ⭐ Breaking Change (9 檔案修改, ADR-001, Alembic migration with data conversion)
**⭐ v3.0 新增**: 資料準確性驗證 (10h) - 後端範圍檢查 + 前端即時提示
**⭐ v3.0.5 新增**: Patient API 實作 (3.75h) - POST/GET/List 3 端點 + Schema + 開發指南
**⭐ v3.0.9 新增**: Database Model SQLAlchemy 2.0 修復完成 (1h) - 6/6 檔案修復, 20 個錯誤全部修正, 測試執行驗證成功
**⭐ v3.0.6 新增**: Login Lockout (4h) + DailyLog 完整系統 (26h) - 認證安全強化 + 日誌 CRUD 完整功能
**⭐ v4.5 新增**: Sprint 1 延後項目 (6h) - Dashboard 登入頁 + LIFF 註冊頁
**⭐ v4.6 新增**: 前端病患管理 UI (18h) - 完整病患列表頁 + 3個可重用元件 (零技術債)
**⭐ v3.0.7 進度修正** (2025-10-21): 更新 LIFF 日誌表單任務狀態 (4.3.1-4.3.6, 24h) + Dashboard Layout (4.4.1, 4h) - 基於 INTEGRATION_TEST_REPORT.md 與 BACKEND_GAP_ANALYSIS.md 的實際完成驗證
**⭐ v3.0.8 API 測試補充** (2025-01-21): 45 個整合測試 (Patient 13 + DailyLog 14 + Auth 18) + conftest.py 重寫 (280行) + Faker 資料生成腳本 (400+行) + 代碼審查 (識別 20 個 Database Model 錯誤, 1/6 已修復) - API 覆蓋率從 10% 提升至 50%
**⭐ v3.1.0 Schema Redesign** (2025-10-22): Daily Log Schema Redesign Breaking Change (8h) - steps_count→exercise_minutes + nullable fields + smoking_count 新欄位 + ADR-001 + Alembic migration 4741100a10d7 with data conversion - 9 檔案修改 (451 insertions, 85 deletions), 所有測試通過

---

### 5.0 Sprint 3: 儀表板 & 問卷系統 + 無障礙 TTS [Week 5-6] ⭐ v3.3 MVP 範圍調整 | ADR-010

**Sprint 目標**: 完成個案 360° 頁面、CAT/mMRC 問卷系統、基礎 TTS 無障礙功能，聚焦 MVP 核心交付。

**⭐ v3.3 重大調整 - 實用主義路線** ([ADR-010: Sprint 3 MVP 範圍縮減決策](./adr/ADR-010-sprint3-mvp-scope-reduction.md)):
- ✅ **TTS 工時大幅簡化**: 24h → 8h (採用 Web Speech API，零後端成本) → [ADR-011](./adr/ADR-011-cat-accessibility-tts-solution.md)
- ⏸ **營養評估延後**: 56h 延後至 MVP 後 (Sprint 6+)，需求不明確暫緩
- 🎯 **聚焦核心**: 360° 頁面 + LIFF 問卷 + 基礎無障礙 = MVP 必要功能
- 📊 **總工時調整**: 176h → 96h (減少 80h，提升交付穩定性)

#### 5.1 個案 360° 頁面 [32h]
*詳細任務分解保持原規劃*

#### 5.2 CAT/mMRC 問卷 API [24h] ✅ 100% 完成

**業務目標**: 實作 CAT (COPD Assessment Test) 和 mMRC (Modified Medical Research Council) 問卷系統，提供完整的問卷提交、查詢、統計分析功能。

**技術亮點**:
- Domain-Driven Design (DDD) - Domain Services (CATScorer, mMRCScorer)
- Event-Driven Architecture - Survey Domain Events (SurveySubmittedEvent)
- Clean Architecture - Repository Pattern with async SQLAlchemy
- Comprehensive Integration Tests - 20+ test cases

| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | Git Commit |
|---------|---------|--------|---------|------|----------|----------|-----------|
| **5.2.1 Survey Core Components** | | | **8h** | ✅ | 2025-10-22 | | |
| 5.2.1.1 | Survey Pydantic Schemas (CAT/mMRC) | Backend | 2 | ✅ | 2025-10-22 | 3.2.5 | f399e6f |
| 5.2.1.2 | CAT Scorer Domain Service (8 questions, 0-40 score) | Backend | 2 | ✅ | 2025-10-22 | 5.2.1.1 | f399e6f |
| 5.2.1.3 | mMRC Scorer Domain Service (grade 0-4) | Backend | 2 | ✅ | 2025-10-22 | 5.2.1.1 | f399e6f |
| 5.2.1.4 | Survey Repository Interface & Implementation | Backend | 2 | ✅ | 2025-10-22 | 3.2.5 | f399e6f |
| **5.2.2 Use Cases & Application Layer** | | | **6h** | ✅ | 2025-10-22 | | |
| 5.2.2.1 | Submit CAT Survey Use Case | Backend | 2 | ✅ | 2025-10-22 | 5.2.1.2, 5.2.1.4 | f399e6f |
| 5.2.2.2 | Submit mMRC Survey Use Case | Backend | 2 | ✅ | 2025-10-22 | 5.2.1.3, 5.2.1.4 | f399e6f |
| 5.2.2.3 | Survey Application Service (orchestration) | Backend | 2 | ✅ | 2025-10-22 | 5.2.2.1, 5.2.2.2 | d36f3a8 |
| **5.2.3 Survey API Endpoints** | | | **6h** | ✅ | 2025-10-22 | | |
| 5.2.3.1 | `POST /surveys/cat` - Submit CAT survey | Backend | 1 | ✅ | 2025-10-22 | 5.2.2.3 | d36f3a8 |
| 5.2.3.2 | `POST /surveys/mmrc` - Submit mMRC survey | Backend | 1 | ✅ | 2025-10-22 | 5.2.2.3 | d36f3a8 |
| 5.2.3.3 | `GET /surveys/{id}` - Get survey by ID | Backend | 1 | ✅ | 2025-10-22 | 5.2.2.3 | d36f3a8 |
| 5.2.3.4 | `GET /surveys/patient/{id}` - List patient surveys | Backend | 1 | ✅ | 2025-10-22 | 5.2.2.3 | d36f3a8 |
| 5.2.3.5 | `GET /surveys/{type}/patient/{id}/latest` - Latest survey | Backend | 1 | ✅ | 2025-10-22 | 5.2.2.3 | d36f3a8 |
| 5.2.3.6 | `GET /surveys/{type}/patient/{id}/stats` - Survey statistics | Backend | 1 | ✅ | 2025-10-22 | 5.2.2.3 | d36f3a8 |
| **5.2.4 Domain Events & Testing** | | | **4h** | ✅ | 2025-10-22 | | |
| 5.2.4.1 | Survey Domain Events (Submitted/Updated/Deleted) | Backend | 1 | ✅ | 2025-10-22 | 5.2.1 | 8be6be6 |
| 5.2.4.2 | Survey API Integration Tests (20+ test cases) | Backend | 2 | ✅ | 2025-10-22 | 5.2.3 | 8be6be6 |
| 5.2.4.3 | Bug Fixes (Import/Method/Encoding errors) | Backend | 1 | ✅ | 2025-10-22 | 5.2.4.2 | 05bb9de |

**實施檢查點**:
- ✅ CAT 評分邏輯正確 (8 questions, 0-5 each = 0-40 total)
- ✅ mMRC 嚴重度映射正確 (Grade 0-1: MILD, 2: MODERATE, 3: SEVERE, 4: VERY_SEVERE)
- ✅ Repository 包含分析方法 (get_average_score, get_score_trend)
- ✅ 趨勢分析算法實作 (比較前後半段平均值)
- ✅ Domain Events 包含關注狀態偵測 (is_concerning)
- ✅ 整合測試涵蓋所有 8 個 API endpoints
- ✅ 安全性測試 (患者只能查看/提交自己的問卷)

#### 5.3 LIFF 問卷頁 [24h] ✅ 已完成 (2025-10-23)

**業務目標**: 提供病患填寫 CAT 和 mMRC 問卷的 LIFF 頁面，實現自動導向流程與結果顯示。

**技術方案**: React + TypeScript + TailwindCSS，整合 Web Speech API TTS，elder-friendly design。

**完成交付**:
- ✅ CAT 8 題表單 UI (大字體、高對比、44px+ 按鈕)
- ✅ mMRC 1 題表單 + 結果顯示
- ✅ CAT → mMRC → Thank You 自動導向流程
- ✅ Thank You 頁面同時顯示 CAT 和 mMRC 分數
- ✅ 表單驗證 + 錯誤處理
- ✅ 註冊頁面欄位更新 (移除 COPD 分期、新增醫院病歷號等)
- ✅ 性別按鈕 UX 改善 (選中狀態視覺指示器)
- ✅ 每日日誌符合 ADR-009 (移除日期選擇、新增運動和吸菸欄位)

**Git Commits**:
- `a1dea9e` - fix(liff): update registration and daily log forms per user feedback
- `8dbfb5c` - feat(liff): implement CAT → mMRC → Thank You survey flow

| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 |
|---------|---------|--------|---------|------|----------|----------|
| 5.3.1 | CAT 表單 UI 實作 | Frontend | 12 | ✅ | 2025-10-23 | 5.2 |
| 5.3.2 | mMRC 表單 + 結果顯示 | Frontend | 8 | ✅ | 2025-10-23 | 5.3.1 |
| 5.3.3 | 自動導向流程整合 | Frontend | 4 | ✅ | 2025-10-23 | 5.3.2 |
| **額外** | 用戶反饋修正 (註冊/日誌/UX) | Frontend | - | ✅ | 2025-10-23 | - |

#### 5.4 趨勢圖表元件 [16h] (P2 - 可選)
*詳細任務分解保持原規劃*

#### 5.6 CAT 量表無障礙設計 (TTS) [8h] ⭐ v3.3 大幅簡化 | ADR-011 | ✅ 已完成 (2025-10-23)

**⭐ v3.3 調整: Web Speech API 實現 (零後端成本)** ([ADR-011: CAT 無障礙 TTS 技術方案](./adr/ADR-011-cat-accessibility-tts-solution.md))

**業務目標**: 為 COPD 病患提供基礎語音朗讀功能，減輕閱讀疲勞，提升問卷填答體驗。

**技術方案**: 採用瀏覽器原生 Web Speech API，無需後端 TTS 服務，零額外成本。

**參考實現**: [docs/frontend/cat_form.html](./frontend/cat_form.html) - 無障礙設計範例與問卷結構

| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | 技術說明 |
|---------|---------|--------|---------|------|----------|----------|----------|
| 5.6.1 | useTTS React Hook 實作 | Frontend | 2 | ✅ | 2025-10-23 | 5.3 | speechSynthesis API 封裝 |
| 5.6.2 | 問卷頁朗讀按鈕整合 | Frontend | 2 | ✅ | 2025-10-23 | 5.6.1 | CAT 8 題 + mMRC 1 題 |
| 5.6.3 | 基本樣式與無障礙標籤 | Frontend | 2 | ✅ | 2025-10-23 | 5.6.2 | aria-label, 鍵盤操作 |
| 5.6.4 | 跨瀏覽器測試 | Frontend | 2 | ✅ | 2025-10-23 | 5.6.3 | iOS Safari, Android Chrome |

**功能範圍**:
- ✅ 基本朗讀 (播放/暫停/停止)
- ✅ 繁體中文語音 (系統預設)
- ✅ 語速調整 (0.9x，老年人友善)
- ❌ 語音選擇 (不支援，簡化範圍)
- ❌ 音檔存儲 (不需要，即時合成)

**瀏覽器支援**:
- iOS Safari 14+ (LINE 內建瀏覽器)
- Android Chrome 90+
- Desktop Chrome/Edge (開發測試)

**5.0 Sprint 3 小計**: 96h ⭐ v3.3 調整 (-80h) | 進度: 91.7% (88h/96h 已完成) ✅ Week 6 完成 | ADR-010, ADR-011
**關鍵交付物**: 個案 360° 頁面 ✅、CAT/mMRC 問卷 API ✅、LIFF 問卷頁 ✅、基礎 TTS 無障礙 ✅
**⭐ v3.3 重大變更** ([ADR-010](./adr/ADR-010-sprint3-mvp-scope-reduction.md)):
- TTS 簡化 24h → 8h (Web Speech API) → [ADR-011](./adr/ADR-011-cat-accessibility-tts-solution.md)
- 營養評估延後 56h → Sprint 6+ (實用主義路線，需求不明確)
- 聚焦 MVP 核心功能 (360° + 問卷 + TTS)
- 參考實現: [cat_form.html](./frontend/cat_form.html) 無障礙設計

---

### 6.0 - 11.0 (後續 Sprints)

*為節省篇幅，Sprint 4-8 與測試品保章節保持原有結構。*

**6.0 Sprint 4: 風險引擎 & 預警 [104h]** (需整合營養風險)
**7.0 Sprint 5: RAG 系統基礎 [80h]** (使用 pgvector)
**8.0 Sprint 6: AI 語音處理鏈 [88h]**
**9.0 Sprint 7: 通知系統 & 排程 [72h]**
**10.0 Sprint 8: 優化 & 上線準備 [96h]**
**11.0 測試與品質保證 [80h]**

---

## 4. 專案進度摘要 (Project Progress Summary)

### 🎯 整體進度統計

| WBS 模組 | 總工時 | 已完成 | 進度 | 狀態 | ADR 參考 |
|---------|--------|--------|------|------|---------|
| 1.0 專案管理 ⭐ | 87h (+71h) | 17h | 19.5% | 🔄 | - |
| 2.0 系統架構 ⭐ | 148h (+36h) | 148h | 100% | ✅ | ADR-001~009 |
| 3.0 Sprint 1 ⭐ | 104h (+8h) | 89h | 85.6% | 🔄 | - |
| 4.0 Sprint 2 ⭐ | 155.75h (+27.75h) | 133.75h | 85.9% | 🔄 | ADR-009 |
| 5.0 Sprint 3 ⭐ | 96h (-80h) | 96h | 100% | ✅ | ADR-010, ADR-011 |
| 6.0 Sprint 4 | 104h | 0h | 0% | ⬜ | - |
| 7.0 Sprint 5 | 80h | 0h | 0% | ⬜ | - |
| 8.0 Sprint 6 | 88h (+56h 營養) | 0h | 0% | ⬜ | - |
| 9.0 Sprint 7 | 72h | 0h | 0% | ⬜ | - |
| 10.0 Sprint 8 | 96h | 0h | 0% | ⬜ | - |
| 11.0 測試品保 | 80h | 0h | 0% | ⬜ | - |
| **總計** | **1033h** (+136-80h) | **459.75h** | **~44.5%** | **🔄** | **11 ADRs** |

### 📅 Sprint 進度分析

#### ✅ Sprint 0 (專案準備階段) - [已完成 83.9%]
- **已完成進度**: 167h/199h (系統架構 148h + 專案管理 17h + 審查工時 2h)
- **關鍵里程碑**:
  - ✅ **專案管理** (17h/87h, 19.5%):
    - ✅ WBS 結構設計完成 (WBS_DEVELOPMENT_PLAN.md v2.4)
    - ✅ 8 Sprint 時程規劃完成
    - ✅ Git Workflow SOP 建立 ([git_workflow_sop.md](./project_management/git_workflow_sop.md))
    - ✅ PR Review SLA 設定 ([pr_review_sla_policy.md](./project_management/pr_review_sla_policy.md))
    - ✅ CI/CD Quality Gates 配置 (Black, Ruff, Mypy, Prettier, ESLint)
    - ✅ Conventional Commits Hook 設定 (commitlint + husky)
    - ✅ 風險識別與評估完成
  - ✅ **系統架構** (148h/148h, 100%):
    - ✅ C4 架構圖完成 (05_architecture_and_design.md)
    - ✅ 資料庫 Schema 設計完成 (database/schema_design_v1.0.md v2.1)
    - ✅ 索引策略規劃完成 (database/index_strategy_planning.md)
    - ✅ AI 處理日誌表設計完成 (ai/21_ai_processing_logs_design.md)
    - ✅ JWT 認證授權設計完成 (security/jwt_authentication_design.md)
    - ✅ API 規範文件完成 (06_api_design_specification.md)
    - ✅ 前端架構規範完成 (12_frontend_architecture_specification.md)
    - ✅ 前端信息架構完成 (17_frontend_information_architecture_template.md)
    - ✅ DDD 戰略設計完成 (7 contexts, 40+ terms, 7 aggregates)
    - ✅ Modular Monolith 模組邊界劃分完成 (7 modules)
    - ✅ Clean Architecture 分層設計完成 (4 layers with examples)
    - ✅ 事件驅動架構設計完成 (27 events, RabbitMQ, Event Sourcing)
    - ✅ 模組與類別設計完成 (10_class_relationships_and_module_design.md) ⭐ v3.0.2 新增

#### ✅ Sprint 1 (Week 1-2) - [93.5% 完成]
- **實際進度**: 97.2h/104h (節省 11.8h)
- **已達成里程碑**:
  - ✅ Docker Compose 環境可運行
  - ✅ PostgreSQL/Redis/RabbitMQ 正常連接
  - ✅ JWT 認證流程完整 (含 Token 黑名單與刷新機制)
  - ✅ 前端基礎架構完成 (Dashboard + LIFF 初始化, API Client)
- **延後項目**: 登入/註冊頁面 UI (6h) → Sprint 2 Week 1

#### ⏳ Sprint 2-8 (Week 3-16) - [未開始]
- **預期進度**: +664h (4.0-10.0 模組)
- **關鍵里程碑**: 參見各 Sprint 詳細說明

---

## 5. 風險與議題管理 (Risk & Issue Management)

### 🚨 風險管控矩陣

#### 🔴 高風險項目
| 風險項目 | 影響度 | 可能性 | 緩解措施 | 負責人 | 參考 ADR |
|---------|--------|--------|----------|--------|---------|
| LINE API 配額不足導致推播失敗 | 高 | 中 | 優先使用 Reply API,監控 Push 用量,建立配額告警 | Backend Lead | ADR-004 |
| AI 模型回覆不當內容或延遲 | 高 | 中 | 信心分數閾值過濾,人工審核機制,備用 fallback 訊息 | AI/ML | - |
| pgvector 百萬級效能下降 | 中 | 高 | IVFFlat 索引優化,準備遷移至 Milvus 方案 | AI/ML | ADR-002 |
| Whisper 本地部署 GPU 需求高 | 中 | 高 | 優先使用 OpenAI Whisper API,Sprint 8 評估本地化 | AI/ML | - |
| RabbitMQ 單點故障風險 | 中 | 中 | Sprint 8 引入鏡像佇列,或遷移至 Kafka | DevOps | ADR-005 |
| 個資法合規風險 | 高 | 低 | 法規顧問審查,資料去識別化,審計日誌完整 | Security | - |

#### 🟡 中風險項目
| 風險項目 | 影響度 | 可能性 | 緩解措施 | 負責人 | 參考 ADR |
|---------|--------|--------|----------|--------|---------|
| 高齡使用者 LIFF 操作困難 | 中 | 高 | UAT 驗證,介面極簡化,語音互動為主 | Frontend | ADR-004 |
| Modular Monolith 模組耦合 | 中 | 中 | 嚴格模組邊界,Event Sourcing 解耦,定期重構 | Backend Lead | ADR-001 |
| CI/CD Pipeline 不穩定 | 中 | 中 | GitHub Actions 備用 Runner,測試環境隔離 | DevOps | - |

#### 🟢 低風險項目
| 風險項目 | 影響度 | 可能性 | 緩解措施 | 負責人 | 參考 ADR |
|---------|--------|--------|----------|--------|---------|
| Zeabur 平台穩定性 | 低 | 低 | 多區域部署,備份 K8s 部署方案 | DevOps | - |
| LINE Platform 服務中斷 | 低 | 低 | 監控 LINE 狀態頁,降級訊息通知 | Backend Lead | ADR-004 |

### 📋 議題追蹤清單

| 議題ID | 議題描述 | 嚴重程度 | 狀態 | 負責人 | 目標解決日期 |
|--------|----------|----------|------|--------|--------------|
| ISS-001 | ai-worker STT/LLM/TTS 服務選型未最終確定 | 高 | 開放 | AI/ML | Sprint 1 |
| ISS-002 | LIFF 本地測試需 ngrok,開發流程待建立 | 中 | 開放 | Frontend | Sprint 1 |
| ISS-003 | 風險分數公式權重是否可由治療師調整 | 中 | 開放 | PO | Sprint 4 |

---

## 6. 品質指標與里程碑 (Quality Metrics & Milestones)

### 🎯 關鍵里程碑

| 里程碑 | 預定日期 | 狀態 | 驗收標準 |
|--------|----------|------|----------|
| M0: 架構設計完成 | 2025-10-21 (Sprint 0 End) | ✅ | C4 架構圖、DB Schema、API 規範、前端架構完成 (100% 已完成) |
| M1: 基礎設施完成 | 2025-11-03 (Sprint 1 End) | 🔄 | Docker 環境運行✅,JWT 認證完成✅,前端基礎架構✅ (93.5% 完成, 登入/註冊 UI 延後) |
| M2: 核心功能完成 | 2025-12-01 (Sprint 4 End) | ⬜ | 病患列表、日誌提交、風險評分、預警中心可用 |
| M3: AI 能力上線 | 2025-12-29 (Sprint 6 End) | ⬜ | 語音提問完整流程可用,15 秒內回覆 |
| M4: MVP 正式發布 | 2026-02-12 (Sprint 8 End) | ⬜ | 所有功能上線,效能達標,通過安全稽核,生產部署完成 |

### 📈 品質指標監控

#### ⏳ 待達成指標 (目標值)
- **測試覆蓋率**: 目標 ≥80% (目前 0%)
- **API P95 響應時間**: 目標 < 500ms
- **AI 語音回覆時間**: 目標 < 15 秒 (端到端)
- **錯誤率**: 目標 < 0.1%
- **服務可用性**: 目標 ≥99.5%
- **北極星指標 (健康行為依從率)**: 目標 ≥75% (V1 基準 ~45%)

### 💡 改善建議

#### 立即行動項目
1. **完成 Modular Monolith 模組邊界劃分**: 避免模組耦合
2. **確立 AI 服務商**: 盡快決定 STT/LLM/TTS 使用 OpenAI API 或本地模型,撰寫 ADR
3. **建立 LIFF 開發環境**: 配置 ngrok 與 LINE Developers Console,撰寫開發指南

#### 中長期優化
1. **技術債管理**: 每 Sprint 保留 20% 時間重構,建立 Tech Debt Log
2. **監控體系完善**: Sprint 8 後持續優化 Grafana Dashboard,建立告警 Runbook
3. **架構演進規劃**: 評估 pgvector → Milvus, RabbitMQ → Kafka, Modular Monolith → Microservices 的遷移時機

---

## 7. 專案管控機制

### 📊 進度報告週期
- **Daily Standup**: 開發團隊內部同步 (15 分鐘)
- **Weekly Report**: 利害關係人更新 (每週五)
- **Sprint Review**: 演示交付物 (Sprint 最後一天)
- **Sprint Retrospective**: 流程改進 (Sprint Review 後)

### 🔄 變更管控流程
1. **變更請求提交** → 2. **影響評估** → 3. **變更委員會審核** → 4. **批准/拒絕** → 5. **執行與追蹤**

**⚠️ 重要備註 - ADR 變更追蹤機制:**
- 所有 WBS 內容的重大變更(任務範圍、技術選型、架構決策、時程調整)都必須建立對應的 [ADR](./adr/)
- 變更類型與 ADR 要求:
  - **技術架構變更** → 必須建立 ADR (如資料庫選型、框架切換、部署方式調整)
  - **任務範圍調整** → 建議建立 ADR (如功能需求變更、模組重構、整合方式調整)
  - **時程或資源調整** → 視影響程度決定是否建立 ADR
- ADR 編號規則: `ADR-XXX-[主題]` (例如: ADR-001-modular-monolith)
- 每次 WBS 更新時,須在相關任務「ADR 參考」欄位註明 ADR 編號
- 變更歷史追蹤: 所有 ADR 應在 `docs/adr/README.md` 建立索引

**v2.0 重大變更記錄 (2025-10-18)**:
- ✅ **ADR-001 變更**: 微服務架構 → Modular Monolith (MVP Phase 0-2)
- ✅ **ADR-003 廢棄**: MongoDB 事件日誌 → PostgreSQL JSONB (event_logs 表)
- ✅ 移除 16h MongoDB 相關任務 (2.2.2, 3.1.3, 3.2.7, 7.2.5)
- ✅ 新增 32h 前端架構設計任務 (2.4.1-2.4.4)
- ✅ 總工時: 936h → 912h

### ⚖️ 資源分配原則
- **關鍵路徑優先**: Sprint 1 → Sprint 4 → Sprint 6 為關鍵路徑,優先分配資源
- **風險緩解優先**: 高風險項目 (LINE API 配額、AI 模型穩定性) 獲得額外資源保障
- **技能匹配**: 根據團隊成員專長分配任務 (Backend/Frontend/AI-ML/DevOps)
- **並行開發**: Sprint 2-7 可並行開發前後端,最大化團隊產出

---

**專案管理總結**: RespiraAlly V2.0 是一個高複雜度的 AI/ML Healthcare 專案,採用 8 Sprint 敏捷開發模式,總工時 1033 小時 (v3.3.1 調整: -80h)。關鍵成功因素包括:專案管理流程的實務整合、技術架構的前置設計 (Sprint 0)、關鍵路徑的資源保障、風險的主動管理、以及測試品質的持續保證。

**架構決策**: MVP 階段採用 **Modular Monolith + PostgreSQL** 簡化技術棧，確保快速交付。Phase 3 後可根據實際需求拆分為微服務與專用向量資料庫。

**⭐ v3.3.1 ADR 關聯更新** (2025-10-22):
- Sprint 3 MVP 範圍調整 → [ADR-010](./adr/ADR-010-sprint3-mvp-scope-reduction.md)
- CAT 無障礙 TTS 技術方案 → [ADR-011](./adr/ADR-011-cat-accessibility-tts-solution.md)
- 總工時: 1113h → 1033h (-80h)
- 專案進度: 34.6% → 39.9% (+5.3%)

**⭐ v3.3.4 技術債修復完成** (2025-10-24):
- ✅ 技術債 P0/P1/P2 完成 (292/310 issues, 94.2% 修復率)
- ✅ Dashboard TypeScript 建置修復 (tsconfig baseUrl, chart type definitions)
- ✅ LIFF Mood enum 類型修復 (Mood.GOOD/NEUTRAL/BAD)
- ✅ Backend Black formatting compliance (100%)
- ✅ Backend pytest 139 tests passing
- ✅ Backend mypy type checking clean
- ✅ Frontend builds: Dashboard ✅, LIFF ✅ (365.80 kB)
- 📊 品質提升: Ruff errors 226 → 18 (-92%), 前後端完整可建置
- 🔍 已知問題: LIFF npm audit 2 moderate (esbuild/vite dev dependencies only)
- Commits: [ff835af](https://github.com/username/repo/commit/ff835af) (Dashboard fixes), [6f796ea](https://github.com/username/repo/commit/6f796ea) (LIFF Mood enum fixes)

**專案經理**: TaskMaster Hub / Claude Code AI
**最後更新**: 2025-10-24 00:15
**下次檢討**: 2025-11-05 (Sprint 3 End)

---

## 📋 專案進度日誌 (Development Progress)

> **注意**: 為了專注於 WBS 的核心功能(任務追蹤與進度管理),專案進度更新日誌已獨立管理。

### 📍 進度日誌位置

詳細的專案進度更新、版本變更記錄、里程碑達成等資訊,請參閱:

**→ [`docs/dev_logs/CHANGELOG_*.md`](./dev_logs/CHANGELOG_*.md)**

該文檔包含:
- ✅ 完整的版本歷史記錄 (v1.0 → 最新版本)
- ✅ 每個 Sprint 的詳細完成項目與交付物
- ✅ 技術決策變更記錄
- ✅ 關鍵成就與里程碑
- ✅ 工時變化與進度統計
- ✅ 經驗教訓 (Lessons Learned)

### 📊 目前專案概況

**最新版本**: v4.1 (2025-10-20)
**階段**: Sprint 1 啟動 - Task 3.2 資料庫實作完成
**總工時**: 1075h
**整體進度**: 11.7%
**Sprint 0 進度**: 60.6%

**最新更新**:
- ✅ Sprint 1 Task 3.2 完成: 資料庫實作與 Alembic Migration 成功執行
- ✅ PostgreSQL 15 + pgvector v0.8.1 環境建立完成
- ✅ 7 張核心資料表 + 16 個索引建立完成
- ✅ SQLAlchemy 2.0 ORM Models + Repository 介面定義完成

**下一步**: Sprint 1 Task 3.3 - FastAPI 專案結構建立 (16h)

---

**相關文檔連結**:
- **核心決策文檔**: [ADR 架構決策記錄](./adr/)
- **進度日誌**: [Development Changelog](./dev_logs/CHANGELOG.md) ⭐ 完整版本歷史
- [產品需求文件 (PRD)](./02_product_requirements_document.md)
- [系統架構設計文檔](./05_architecture_and_design.md)
- [模組與類別設計](./10_class_relationships_and_module_design.md)
- [資料庫 Schema 設計](./database/schema_design_v1.0.md)
- [API 設計規格](./06_api_design_specification.md)
- [前端架構規範](./12_frontend_architecture_specification.md)
- [前端信息架構](./17_frontend_information_architecture_template.md)
- [模組規格與測試](./07_module_specification_and_tests.md)
- [專案結構指南](./08_project_structure_guide.md)

---

*此 WBS 遵循 VibeCoding 開發流程規範,整合 TaskMaster Hub 智能協調機制,確保專案品質與交付效率。*
