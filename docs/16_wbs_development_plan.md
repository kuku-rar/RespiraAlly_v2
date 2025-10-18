# RespiraAlly V2.0 工作分解結構 (WBS) 開發計劃

---

**文件版本 (Document Version):** `v2.3` ✅ Git Hooks 修復完成 + 開發環境就緒
**最後更新 (Last Updated):** `2025-10-18 11:12`
**主要作者 (Lead Author):** `TaskMaster Hub / Claude Code AI`
**審核者 (Reviewers):** `Technical Lead, Product Manager, Architecture Team`
**狀態 (Status):** `執行中 - Sprint 0 進度 35.7% (專案管理 19.5% + 系統架構 48%) - 開發環境就緒`

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
| **專案狀態** | 執行中 (In Progress) - 目前進度: ~7.2% 完成 (Sprint 0 進度 35.7%) |
| **文件版本** | v2.2 ⭐ 開發流程管控完成 + 文檔結構優化 |
| **最後更新** | 2025-10-18 10:23 |

### ⏱️ 專案時程規劃

| 項目 | 日期/時間 |
|------|----------|
| **總工期** | 16 週 (8 Sprints × 14 days) (2025-10-21 ～ 2026-02-12) |
| **目前進度** | ~7.2% 完成 (~71h/983h，Sprint 0 專案管理+架構設計進行中) |
| **當前階段** | Sprint 0 準備 - 專案管理規劃、架構設計、數據庫設計、前端架構完成 |
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

2.0 系統架構與設計 (System Architecture) [112h] ✅ 48%
├── 2.1 技術架構設計 [32h] ✅ 25%
├── 2.2 資料庫設計 (PostgreSQL + pgvector) [24h] ✅ 67%
├── 2.3 API 設計規範 [16h] ✅ 38%
├── 2.4 前端架構設計 [32h] ✅ 100%
└── 2.5 DDD 戰略設計 [8h]

3.0 Sprint 1: 基礎設施 & 認證系統 [96h] [Week 1-2]
├── 3.1 環境建置與容器化 [20h]
├── 3.2 資料庫 Schema 實作 [16h]
├── 3.3 FastAPI 專案結構 [16h]
├── 3.4 認證授權系統 [32h]
└── 3.5 前端基礎架構 [20h]

4.0 Sprint 2: 病患管理 & 日誌功能 [112h] [Week 3-4]
├── 4.1 個案管理 API [28h]
├── 4.2 日誌服務 API [32h]
├── 4.3 LIFF 日誌表單 [28h]
└── 4.4 Dashboard 病患列表 [24h]

5.0 Sprint 3: 儀表板 & 問卷系統 [96h] [Week 5-6]
├── 5.1 個案 360° 頁面 [32h]
├── 5.2 CAT/mMRC 問卷 API [24h]
├── 5.3 LIFF 問卷頁 [24h]
└── 5.4 趨勢圖表元件 [16h]

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
| 2.0 系統架構 | 112h | 54h | 48% | 🔄 |
| 3.0 Sprint 1 (基礎設施) | 96h | 0h | 0% | ⬜ |
| 4.0 Sprint 2 (病患管理) | 112h | 0h | 0% | ⬜ |
| 5.0 Sprint 3 (儀表板) | 96h | 0h | 0% | ⬜ |
| 6.0 Sprint 4 (風險引擎) | 104h | 0h | 0% | ⬜ |
| 7.0 Sprint 5 (RAG 系統) | 80h | 0h | 0% | ⬜ |
| 8.0 Sprint 6 (AI 語音) | 88h | 0h | 0% | ⬜ |
| 9.0 Sprint 7 (通知系統) | 72h | 0h | 0% | ⬜ |
| 10.0 Sprint 8 (優化上線) | 96h | 0h | 0% | ⬜ |
| 11.0 測試品保 (持續) | 80h | 0h | 0% | ⬜ |
| **總計** | **983h** | **71h** | **~7.2%** | **🔄** |

**狀態圖示說明:**
- ✅ 已完成 (Completed)
- 🔄 進行中 (In Progress)
- ⚡ 接近完成 (Near Completion)
- ⏳ 計劃中 (Planned)
- ⬜ 未開始 (Not Started)

**⚠️ 重要架構決策變更記錄:**
- **v2.3 更新 (2025-10-18 11:12)** ✅ **Git Hooks 修復完成 + 開發環境就緒**:
  - ✅ **修復 Git Hooks CRLF 問題**: 修復 Windows CRLF 導致 hooks 無法執行的問題
  - ✅ **npm 依賴安裝**: 安裝 175 packages (commitlint@18.6.1, husky@8.0.3)
  - ✅ **驗證測試通過**: Invalid messages 攔截 ✅, Valid messages 通過 ✅
  - ✅ **建立防護機制**: 更新 .gitattributes 強制 .husky/** 使用 LF
  - ✅ **開發環境完全就緒**: 所有開發流程基礎設施已可用

- **v2.2 更新 (2025-10-18 10:23)** ✅ **開發流程管控完成 + 文檔結構優化**:
  - ✅ **完成 1.4.1-1.4.4 開發流程管控任務**: Git Workflow SOP, PR Review SLA, CI Quality Gates, Conventional Commits Hook
  - ✅ **建立專案管理文檔資料夾** `docs/project_management/`: 集中管理流程文檔, 建立 README 索引
  - ✅ **更新進度統計**: 專案管理 9.2% → 19.5%, 整體進度 6.3% → 7.2%, Sprint 0 進度 31% → 35.7%
  - ✅ **交付 10 個文件**: 流程文檔 × 3, PR/CI 配置 × 2, commitlint 配置 × 4, WBS 更新 × 1

- **v2.1 更新 (2025-10-18 10:00)** ⭐ **專案管理流程重構**:
  - ✅ **修正 1.0 專案管理工時低估**: 16h → 87h (+71h, +444%)
  - ✅ **新增 1.4 開發流程管控章節**: 整合 01_development_workflow.md，建立 Git/PR/CI 管控機制
  - ✅ **修正 Daily Standup 工時**: 2h → 20h (0.25h/天 × 80 工作天)
  - ✅ **修正 Sprint 儀式工時**: 4h → 32h (Planning + Review/Retro × 8 sprints)
  - ✅ **重新計算工時統計**: 912h → 983h (+71h)

- **v2.0 更新 (2025-10-18)**:
  - ✅ 移除所有 MongoDB 相關任務 - 改用 PostgreSQL JSONB 替代
  - ✅ 微服務架構 → Modular Monolith (MVP Phase 0-2)
  - ✅ 新增前端架構設計階段 (2.4)
  - ✅ 重新計算工時統計 (936h → 912h)

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
| 2.1.2 | Modular Monolith 模組邊界劃分 | ARCH | 8 | ⬜ | Sprint 0 | 2.1.1 | ADR-001 |
| 2.1.3 | Clean Architecture 分層設計 | ARCH | 8 | ⬜ | Sprint 0 | 2.1.2 | - |
| 2.1.4 | 事件驅動架構設計 | ARCH | 8 | ⬜ | Sprint 0 | 2.1.3 | - |

**關鍵變更**: MVP 採用 **Modular Monolith** 而非微服務，Phase 3 後可拆分。

#### 2.2 資料庫設計 (PostgreSQL Only)
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 2.2.1 | PostgreSQL ER 圖設計 | Data Engineer | 8 | ✅ | 2025-10-17 | 2.1.2 | database/schema_design_v1.0.md |
| 2.2.2 | 完整表結構設計 (13 tables) | Data Engineer | 8 | ✅ | 2025-10-17 | 2.2.1 | database/schema_design_v1.0.md |
| 2.2.3 | pgvector 向量表設計 | Data Engineer | 4 | ⬜ | Sprint 4 | 2.2.2 | ADR-002 |
| 2.2.4 | 索引策略規劃 | Data Engineer | 4 | ⬜ | Sprint 0 | 2.2.2 | - |

**⚠️ 重大變更**: 移除 MongoDB，使用 **PostgreSQL JSONB** 替代 (event_logs 表)。

#### 2.3 API 設計規範
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 2.3.1 | RESTful API 規範制定 | TL | 6 | ✅ | 2025-10-17 | 2.1.2 | 06_api_design_specification.md |
| 2.3.2 | OpenAPI Schema 定義 | TL | 6 | ⬜ | Sprint 1 | 2.3.1 | - |
| 2.3.3 | 錯誤處理標準 | TL | 2 | ⬜ | Sprint 1 | 2.3.2 | - |
| 2.3.4 | JWT 認證授權設計 | Security | 4 | ⬜ | Sprint 0 | 2.3.3 | - |

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

#### 2.5 DDD 戰略設計
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 2.5.1 | 界限上下文映射 | ARCH | 4 | ⬜ | Sprint 0 | 2.1.2 | - |
| 2.5.2 | 統一語言 (Ubiquitous Language) 定義 | ARCH, PO | 2 | ⬜ | Sprint 0 | 2.5.1 | - |
| 2.5.3 | 聚合根識別與設計 | ARCH | 2 | ⬜ | Sprint 1 | 2.5.2 | - |

**2.0 系統架構小計**: 112h | 進度: 48% (54/112h 已完成)

---

### 3.0 Sprint 1: 基礎設施 & 認證系統 [Week 1-2]

**Sprint 目標**: 建立可運行的專案骨架,完成 Docker 環境、資料庫、FastAPI 結構與使用者認證。

#### 3.1 環境建置與容器化
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 3.1.1 | Docker Compose 定義 | DevOps | 4 | ⬜ | Week 1 | - | - |
| 3.1.2 | PostgreSQL 容器配置 | DevOps | 2 | ⬜ | Week 1 | 3.1.1 | - |
| 3.1.3 | Redis 容器配置 | DevOps | 2 | ⬜ | Week 1 | 3.1.1 | - |
| 3.1.4 | RabbitMQ 容器配置 | DevOps | 2 | ⬜ | Week 1 | 3.1.1 | ADR-005 |
| 3.1.5 | MinIO 容器配置 | DevOps | 2 | ⬜ | Week 1 | 3.1.1 | - |
| 3.1.6 | 開發環境驗證 | DevOps | 2 | ⬜ | Week 1 | 3.1.5 | - |
| 3.1.7 | `.env` 環境變數管理 | DevOps | 2 | ⬜ | Week 1 | 3.1.6 | - |
| 3.1.8 | GitHub Actions CI/CD 初始化 | DevOps | 4 | ⬜ | Week 2 | 3.1.7 | - |

#### 3.2 資料庫 Schema 實作
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 3.2.1 | Alembic 初始化 | Backend | 2 | ⬜ | Week 1 | 2.2.4 | - |
| 3.2.2 | 核心表 Migration (users, profiles) | Backend | 4 | ⬜ | Week 1 | 3.2.1 | - |
| 3.2.3 | 業務表 Migration (daily_logs, surveys) | Backend | 4 | ⬜ | Week 1 | 3.2.2 | - |
| 3.2.4 | 事件表 Migration (event_logs JSONB) | Backend | 2 | ⬜ | Week 1 | 3.2.3 | - |
| 3.2.5 | SQLAlchemy Models 定義 | Backend | 4 | ⬜ | Week 1 | 3.2.4 | - |

**關鍵變更**: 使用 PostgreSQL `event_logs` 表 (JSONB) 替代 MongoDB。

#### 3.3 FastAPI 專案結構
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 3.3.1 | Poetry 專案初始化 | Backend | 2 | ⬜ | Week 1 | - | ADR-001 |
| 3.3.2 | Clean Architecture 目錄結構 | Backend | 3 | ⬜ | Week 1 | 3.3.1, 2.1.3 | - |
| 3.3.3 | FastAPI `main.py` 入口點 | Backend | 2 | ⬜ | Week 1 | 3.3.2 | - |
| 3.3.4 | Database Session 管理 | Backend | 3 | ⬜ | Week 1 | 3.3.3, 3.2.5 | - |
| 3.3.5 | Pydantic Settings 配置加載 | Backend | 2 | ⬜ | Week 1 | 3.3.4 | - |
| 3.3.6 | 全域錯誤處理 Middleware | Backend | 2 | ⬜ | Week 2 | 3.3.5, 2.3.3 | - |
| 3.3.7 | CORS Middleware 配置 | Backend | 1 | ⬜ | Week 2 | 3.3.6 | - |
| 3.3.8 | `/health` Endpoint 實作 | Backend | 1 | ⬜ | Week 2 | 3.3.7 | - |

#### 3.4 認證授權系統
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 3.4.1 | JWT Token 生成邏輯 | Backend | 4 | ⬜ | Week 1 | 2.3.4 | - |
| 3.4.2 | JWT Token 驗證 Dependency | Backend | 4 | ⬜ | Week 1 | 3.4.1 | - |
| 3.4.3 | RBAC 權限檢查 Decorator | Backend | 4 | ⬜ | Week 2 | 3.4.2 | - |
| 3.4.4 | LINE LIFF OAuth 整合 | Backend | 8 | ⬜ | Week 2 | 3.4.3 | ADR-004 |
| 3.4.5 | `POST /auth/register` API (US-101) | Backend | 4 | ⬜ | Week 2 | 3.4.4 | - |
| 3.4.6 | `POST /auth/token` API (US-102) | Backend | 4 | ⬜ | Week 2 | 3.4.3 | - |
| 3.4.7 | 登入失敗鎖定策略 (Redis) | Backend | 4 | ⬜ | Week 2 | 3.4.6 | ADR-008 |

#### 3.5 前端基礎架構
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 3.5.1 | Next.js Dashboard 專案初始化 | Frontend | 4 | ⬜ | Week 1 | - | - |
| 3.5.2 | Vite + React LIFF 專案初始化 | Frontend | 4 | ⬜ | Week 1 | - | ADR-004 |
| 3.5.3 | Tailwind CSS 配置 | Frontend | 2 | ⬜ | Week 1 | 3.5.1, 3.5.2 | - |
| 3.5.4 | API Client (Axios) 封裝 | Frontend | 4 | ⬜ | Week 2 | 3.5.3, 2.3.1 | - |
| 3.5.5 | Dashboard 登入頁 UI (US-102) | Frontend | 4 | ⬜ | Week 2 | 3.5.4, 3.4.6 | - |
| 3.5.6 | LIFF 註冊頁 UI (US-101) | Frontend | 2 | ⬜ | Week 2 | 3.5.4, 3.4.5 | - |

**3.0 Sprint 1 小計**: 96h | 進度: 0% (0/96h 已完成)
**關鍵交付物**: Docker Compose 環境, Database Schema, JWT 認證, 登入/註冊頁面

---

### 4.0 Sprint 2: 病患管理 & 日誌功能 [Week 3-4]

**Sprint 目標**: 完成病患 CRUD、日誌提交與查詢流程,治療師可查看病患列表。

#### 4.1 個案管理 API
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 4.1.1 | Patient Repository 實作 | Backend | 4 | ⬜ | Week 3 | 3.2.5 | - |
| 4.1.2 | Patient Application Service | Backend | 4 | ⬜ | Week 3 | 4.1.1 | - |
| 4.1.3 | `GET /patients` API (US-501) | Backend | 6 | ⬜ | Week 3 | 4.1.2 | - |
| 4.1.4 | `GET /patients/{id}` API 基礎版 | Backend | 4 | ⬜ | Week 3 | 4.1.3 | - |
| 4.1.5 | 查詢參數篩選邏輯 | Backend | 4 | ⬜ | Week 4 | 4.1.3 | - |
| 4.1.6 | 分頁與排序實作 | Backend | 4 | ⬜ | Week 4 | 4.1.5 | - |
| 4.1.7 | `POST /patients/{id}/assign` (US-103) | Backend | 2 | ⬜ | Week 4 | 4.1.4 | - |

#### 4.2 日誌服務 API
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 4.2.1 | DailyLog Domain Model | Backend | 4 | ⬜ | Week 3 | 2.5.3 | - |
| 4.2.2 | DailyLog Repository 實作 | Backend | 4 | ⬜ | Week 3 | 4.2.1 | - |
| 4.2.3 | DailyLog Application Service | Backend | 4 | ⬜ | Week 3 | 4.2.2 | - |
| 4.2.4 | `POST /daily-logs` API (US-201) | Backend | 6 | ⬜ | Week 3 | 4.2.3 | - |
| 4.2.5 | 每日唯一性檢查與更新邏輯 | Backend | 4 | ⬜ | Week 4 | 4.2.4 | - |
| 4.2.6 | `GET /daily-logs` 查詢 API | Backend | 4 | ⬜ | Week 4 | 4.2.5 | - |
| 4.2.7 | `daily_log.submitted` 事件發布 | Backend | 4 | ⬜ | Week 4 | 4.2.4, 2.1.4 | - |
| 4.2.8 | Idempotency Key 支援 | Backend | 2 | ⬜ | Week 4 | 4.2.5 | - |

#### 4.3 LIFF 日誌表單
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 4.3.1 | LIFF 日誌頁面路由 | Frontend | 2 | ⬜ | Week 3 | 3.5.2 | - |
| 4.3.2 | 日誌表單 UI 元件 | Frontend | 8 | ⬜ | Week 3 | 4.3.1 | - |
| 4.3.3 | Toggle (用藥) + Number Input | Frontend | 4 | ⬜ | Week 3 | 4.3.2 | - |
| 4.3.4 | 表單驗證邏輯 | Frontend | 4 | ⬜ | Week 4 | 4.3.3 | - |
| 4.3.5 | 提交後鼓勵訊息 | Frontend | 2 | ⬜ | Week 4 | 4.3.4, 4.2.4 | - |
| 4.3.6 | 錯誤處理與 Toast 提示 | Frontend | 4 | ⬜ | Week 4 | 4.3.5 | - |
| 4.3.7 | LIFF SDK 整合測試 | Frontend | 4 | ⬜ | Week 4 | 4.3.6 | - |

#### 4.4 Dashboard 病患列表
| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | ADR 參考 |
|---------|---------|--------|---------|------|----------|----------|---------|
| 4.4.1 | Dashboard Layout 設計 | Frontend | 4 | ⬜ | Week 3 | 3.5.1 | - |
| 4.4.2 | 病患列表頁面 UI | Frontend | 6 | ⬜ | Week 3 | 4.4.1, 4.1.3 | - |
| 4.4.3 | Table 元件 (分頁、排序) | Frontend | 6 | ⬜ | Week 4 | 4.4.2 | - |
| 4.4.4 | 篩選器元件 (風險等級、依從率) | Frontend | 4 | ⬜ | Week 4 | 4.4.3 | - |
| 4.4.5 | 搜尋功能 | Frontend | 2 | ⬜ | Week 4 | 4.4.4 | - |
| 4.4.6 | 即時數據更新 (Polling/WebSocket) | Frontend | 2 | ⬜ | Week 4 | 4.4.5 | - |

**4.0 Sprint 2 小計**: 112h | 進度: 0% (0/112h 已完成)
**關鍵交付物**: 病患列表、日誌提交 API、LIFF 日誌表單

---

### 5.0 - 11.0 (後續 Sprints)

*為節省篇幅，Sprint 3-8 與測試品保章節保持原有結構，僅移除 MongoDB 相關任務。*

**5.0 Sprint 3: 儀表板 & 問卷系統 [96h]**
**6.0 Sprint 4: 風險引擎 & 預警 [104h]**
**7.0 Sprint 5: RAG 系統基礎 [80h]** (使用 pgvector)
**8.0 Sprint 6: AI 語音處理鏈 [88h]**
**9.0 Sprint 7: 通知系統 & 排程 [72h]**
**10.0 Sprint 8: 優化 & 上線準備 [96h]**
**11.0 測試與品質保證 [80h]**

---

## 4. 專案進度摘要 (Project Progress Summary)

### 🎯 整體進度統計

| WBS 模組 | 總工時 | 已完成 | 進度 | 狀態 |
|---------|--------|--------|------|------|
| 1.0 專案管理 ⭐ | 87h (+71h) | 17h | 19.5% | 🔄 |
| 2.0 系統架構 | 112h | 54h | 48% | 🔄 |
| 3.0 Sprint 1 | 96h | 0h | 0% | ⬜ |
| 4.0 Sprint 2 | 112h | 0h | 0% | ⬜ |
| 5.0 Sprint 3 | 96h | 0h | 0% | ⬜ |
| 6.0 Sprint 4 | 104h | 0h | 0% | ⬜ |
| 7.0 Sprint 5 | 80h | 0h | 0% | ⬜ |
| 8.0 Sprint 6 | 88h | 0h | 0% | ⬜ |
| 9.0 Sprint 7 | 72h | 0h | 0% | ⬜ |
| 10.0 Sprint 8 | 96h | 0h | 0% | ⬜ |
| 11.0 測試品保 | 80h | 0h | 0% | ⬜ |
| **總計** | **983h** | **71h** | **~7.2%** | **🔄** |

### 📅 Sprint 進度分析

#### 🔄 Sprint 0 (專案準備階段) - [進行中 ~35.7%]
- **已完成進度**: 71h/199h (系統架構 54h + 專案管理 17h)
- **關鍵里程碑**:
  - ✅ **專案管理** (17h/87h, 19.5%):
    - ✅ WBS 結構設計完成 (WBS_DEVELOPMENT_PLAN.md v2.1)
    - ✅ 8 Sprint 時程規劃完成
    - ✅ Git Workflow SOP 建立 ([git_workflow_sop.md](./project_management/git_workflow_sop.md))
    - ✅ PR Review SLA 設定 ([pr_review_sla_policy.md](./project_management/pr_review_sla_policy.md))
    - ✅ CI/CD Quality Gates 配置 (Black, Ruff, Mypy, Prettier, ESLint)
    - ✅ Conventional Commits Hook 設定 (commitlint + husky)
    - ✅ 風險識別與評估完成
  - ✅ **系統架構** (54h/112h, 48%):
    - ✅ C4 架構圖完成 (05_architecture_and_design.md)
    - ✅ 資料庫 Schema 設計完成 (database/schema_design_v1.0.md)
    - ✅ API 規範文件完成 (06_api_design_specification.md)
    - ✅ 前端架構規範完成 (12_frontend_architecture_specification.md)
    - ✅ 前端信息架構完成 (17_frontend_information_architecture_template.md)
    - ⬜ Modular Monolith 模組邊界劃分
    - ⬜ DDD 戰略設計

#### ⏳ Sprint 1 (Week 1-2) - [未開始]
- **預期進度**: +96h (3.0 模組)
- **關鍵里程碑**:
  - Docker Compose 環境可運行
  - PostgreSQL/Redis/RabbitMQ 正常連接
  - JWT 認證流程完整
  - 登入/註冊頁面可用

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
| M0: 架構設計完成 | 2025-10-21 (Sprint 0 End) | 🔄 | C4 架構圖、DB Schema、API 規範、前端架構完成 (48% 已完成) |
| M1: 基礎設施完成 | 2025-11-03 (Sprint 1 End) | ⬜ | Docker 環境運行,JWT 認證完成,登入/註冊可用 |
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

**專案管理總結**: RespiraAlly V2.0 是一個高複雜度的 AI/ML Healthcare 專案,採用 8 Sprint 敏捷開發模式,總工時 983 小時 (v2.1 修正)。關鍵成功因素包括:專案管理流程的實務整合、技術架構的前置設計 (Sprint 0)、關鍵路徑的資源保障、風險的主動管理、以及測試品質的持續保證。

**架構決策**: MVP 階段採用 **Modular Monolith + PostgreSQL** 簡化技術棧，確保快速交付。Phase 3 後可根據實際需求拆分為微服務與專用向量資料庫。

**專案經理**: TaskMaster Hub / Claude Code AI
**最後更新**: 2025-10-18 10:00
**下次檢討**: 2025-10-21 (Sprint 1 Planning)

---

## 📝 專案進度更新日誌 (Progress Update Log)

### 2025-10-18 10:00 - v2.1 專案管理流程重構 ⭐ 重大更新

**✅ 完成項目** (1.0 專案管理 - 流程整合與修正):

#### 1. **專案管理流程重構** (8h/87h 已完成, 9.2%)
   - ✅ **修正 1.1 專案啟動與規劃**:
     - 移除冗餘任務「專案章程制定」(與 WBS 重複)
     - 標記已完成: WBS 結構設計, 8 Sprint 時程規劃, 風險識別與評估
     - 調整工時為實際值 (8h total)
     - 新增「證據/產出」欄位確保可驗證性

   - ✅ **修正 1.2 Sprint 規劃與執行**:
     - 修正 Daily Standup 工時低估: 2h → 20h (0.25h/天 × 80 工作天)
     - 修正 Sprint 儀式工時: 4h → 32h (Planning 16h + Review/Retro 16h)
     - 新增「單次工時」和「執行次數」欄位避免誤解
     - 總工時: 6h → 52h (+767%)

   - ✅ **重構 1.3 專案監控與報告**:
     - 移除虛幻任務「週報告制度建立」「TaskMaster 進度追蹤」
     - 改為實際可交付工具: GitHub Project Board, CI/CD Dashboard, Slack 自動化報告
     - 總工時: 2h → 8h (實際配置時間)

   - ✅ **新增 1.4 開發流程管控** ⭐ **關鍵整合**:
     - 完全整合 `01_development_workflow.md` 規範
     - Git Workflow SOP 建立
     - PR Review SLA 設定 (目標: 24h 內首次 Review)
     - CI/CD Quality Gates 配置 (Black, Ruff, Mypy, Pytest)
     - Conventional Commits 驗證 Hook (commitlint + husky)
     - 技術債追蹤機制 (每 Sprint 預留 20% 時間)
     - 每週流程健康度檢查 (PR Throughput, CI Success Rate, Review Time)
     - 新增工時: 19h

**工時修正統計**:
| 模組 | 原估計 | 修正後 | 差異 | 理由 |
|------|--------|--------|------|------|
| 1.1 專案啟動 | 8h | 8h | 0h | 調整任務但總時不變 |
| 1.2 Sprint 執行 | 6h | 52h | +46h | Daily Standup + Sprint 儀式實際工時 |
| 1.3 監控報告 | 2h | 8h | +6h | 實際工具配置時間 |
| **1.4 流程管控** | **0h** | **19h** | **+19h** | **新增關鍵章節** |
| **總計** | **16h** | **87h** | **+71h (+444%)** | **實務導向重構** |

**整體影響**:
- 總工時: 912h → 983h (+71h, +7.8%)
- 已完成: 54h → 71h (+17h)
- 整體進度: 5.9% → 7.2%

**關鍵洞察** (Linus 實用主義分析):
1. ❌ **數據說謊問題**: 原方案顯示整體進度 5.9% 但專案管理 0%，自相矛盾
2. ❌ **工時幻覺問題**: Daily Standup 估 2h 實際需 20h，低估 900%
3. ❌ **流程斷裂問題**: 專案管理與開發流程 (01_development_workflow.md) 完全不對話
4. ❌ **假大空問題**: 專案章程、週報制度無實際產出

**修正措施**:
- ✅ 修正數據結構 - 標記已完成任務
- ✅ 重構工時估計 - 顯式列出執行次數
- ✅ 整合開發流程 - 新增 1.4 章節完全對齊 01_development_workflow.md
- ✅ 自動化優先 - GitHub Project Board + CI Insights + Slack

**下一步行動** (Sprint 1 Week 1):
1. 執行 1.4.1: Git Workflow SOP 建立
2. 執行 1.4.2: PR Review SLA 設定 (24h SLA)
3. 執行 1.4.3: CI/CD Quality Gates 配置
4. 執行 1.4.4: Conventional Commits Hook (commitlint + husky)

---

### 2025-10-18 11:12 - v2.3 Git Hooks 修復完成 + 開發環境就緒 ✅ 完成

**✅ 修復項目** (Git Hooks CRLF 問題修復):

#### 1. **問題診斷與修復**

   - **根本原因**: Windows CRLF 行尾符號導致 Git hooks 無法執行
     ```
     /usr/bin/env: 'sh\r': No such file or directory
     ```

   - **修復步驟**:
     1. ✅ 執行 `npm install` - 安裝 175 個套件 (commitlint, husky 等)
     2. ✅ 執行 `dos2unix .husky/commit-msg` - 轉換 CRLF → LF
     3. ✅ 更新 `.gitattributes` - 強制 `.husky/**` 使用 LF
     4. ✅ 新增 `package-lock.json` - 鎖定依賴版本

   - **驗證測試**:
     - ✅ Invalid commit message 成功被攔截
     - ✅ Valid commit message 正常通過
     - ✅ Git hooks path 配置正確 (`core.hooksPath = .husky`)

#### 2. **開發環境狀態確認**

   - ✅ **npm 依賴**: 175 packages 已安裝
   - ✅ **Husky hooks**: 已啟用並正常運作
   - ✅ **Commitlint**: v18.6.1 驗證正常
   - ✅ **CRLF 問題**: 已修復且建立防護機制
   - ✅ **CI/CD Pipeline**: Quality Gates 就緒
   - ✅ **PR Review SLA**: 24h 政策已生效

#### 3. **團隊協作就緒**

   - ✅ 所有開發流程規範已建立
   - ✅ Git hooks 自動驗證 commit message
   - ✅ 團隊成員只需執行 `npm install` 即可啟用
   - ✅ 詳細設置指南已提供 (`docs/project_management/setup_git_hooks.md`)

**交付物**:
- `package-lock.json` (新增)
- `.gitattributes` (更新 - 新增 .husky/** 規則)
- `.husky/commit-msg` (修復 CRLF)

**Git Commits**:
- `8bdf1ca` fix(hooks): fix git hooks CRLF issue and add package-lock.json
- `278a9a1` chore(test): remove test file
- `9e029e5` test(hooks): verify commitlint hook is working

**下一步準備**:
Sprint 0 開發流程基礎設施已全部就緒，可以開始 Sprint 1 實際開發工作。

---

### 2025-10-18 10:23 - v2.2 開發流程管控完成 + 文檔結構優化 ✅ 完成

**✅ 完成項目** (1.4 開發流程管控 - 全部 4 項任務完成, +9h):

#### 1. **開發流程管控任務執行** (已完成 9h/19h, 47.4%)

   - ✅ **1.4.1 Git Workflow SOP 建立** (2h):
     - 建立 `docs/project_management/git_workflow_sop.md` (3,500+ 行完整指南)
     - 涵蓋: 分支命名規範、Commit 格式、Merge 策略、衝突解決、Hotfix 流程、FAQ
     - 完全對齊 `01_development_workflow.md` §Ⅲ.1 規範

   - ✅ **1.4.2 PR Review SLA 設定** (1h):
     - 建立 `docs/project_management/pr_review_sla_policy.md`
     - 建立 `.github/pull_request_template.md`
     - SLA 目標: <24h 首次 Review, <48h Approve, <72h Merge
     - 完全對齊 `01_development_workflow.md` §Ⅲ.5 規範

   - ✅ **1.4.3 CI/CD Quality Gates 配置** (4h):
     - 增強 `.github/workflows/ci.yml`
     - 新增 Prettier format checks (Dashboard + LIFF)
     - 新增 Coverage threshold (--cov-fail-under=80)
     - Quality Gates: Black, Ruff, Mypy, Pytest, Prettier, ESLint, TypeScript
     - 完全對齊 `01_development_workflow.md` §Ⅳ 規範

   - ✅ **1.4.4 Conventional Commits 驗證 Hook** (2h):
     - 建立 `package.json` (root, commitlint + husky dependencies)
     - 建立 `commitlint.config.js` (規則配置)
     - 建立 `.husky/commit-msg` (Git hook)
     - 建立 `docs/project_management/setup_git_hooks.md` (設置指南)
     - 完全對齊 `01_development_workflow.md` §Ⅲ.4 規範

#### 2. **文檔結構優化**

   - ✅ **建立專案管理文檔資料夾** `docs/project_management/`:
     - 整合三個開發流程文檔到專用資料夾
     - 建立 `README.md` 索引文件 (包含使用指南、檢核點、度量指標)
     - 更新 WBS 文檔中的所有引用路徑

   - ✅ **更新 WBS 進度與統計**:
     - 標記 1.4.1-1.4.4 為已完成 ✅ (2025-10-18)
     - 更新專案管理進度: 8h → 17h (9.2% → 19.5%)
     - 更新整體進度: 62h → 71h (6.3% → 7.2%)
     - 更新 Sprint 0 進度: 31% → 35.7%

**交付物清單** (10 個文件):

| # | 文件路徑 | 類型 | 說明 |
|---|---------|------|------|
| 1 | `docs/project_management/git_workflow_sop.md` | 新增 | Git 工作流程 SOP (3,500+ 行) |
| 2 | `docs/project_management/pr_review_sla_policy.md` | 新增 | PR Review SLA 政策 |
| 3 | `docs/project_management/setup_git_hooks.md` | 新增 | Git Hooks 設置指南 |
| 4 | `docs/project_management/README.md` | 新增 | 專案管理文檔索引 |
| 5 | `.github/pull_request_template.md` | 新增 | PR 描述模板 |
| 6 | `.github/workflows/ci.yml` | 增強 | CI Quality Gates (新增 Prettier, Coverage) |
| 7 | `package.json` | 新增 | Root package (commitlint + husky) |
| 8 | `commitlint.config.js` | 新增 | Commit 訊息驗證規則 |
| 9 | `.husky/commit-msg` | 新增 | Git commit hook |
| 10 | `docs/16_wbs_development_plan.md` | 更新 | v2.1 → v2.2 (進度更新, 路徑修正) + 重新命名符合 VibeCoding 序號規範 |

**進度統計**:

| 指標 | v2.1 | v2.2 | 變化 |
|------|------|------|------|
| 專案管理已完成 | 8h | 17h | +9h (+112.5%) |
| 專案管理進度 | 9.2% | 19.5% | +10.3% |
| 總已完成 | 62h | 71h | +9h |
| 整體進度 | 6.3% | 7.2% | +0.9% |
| Sprint 0 進度 | 31% | 35.7% | +4.7% |

**關鍵成就**:

1. ✅ **開發流程完全對齊**: 所有 1.4 任務 100% 對齊 `01_development_workflow.md` 規範
2. ✅ **自動化工具就緒**: commitlint hook + CI Quality Gates 確保代碼品質
3. ✅ **文檔結構優化**: 專案管理文檔集中管理,易於導航與維護
4. ✅ **SLA 明確定義**: PR Review 24h SLA,可度量可追蹤
5. ✅ **團隊 Onboarding Ready**: 完整的設置指南與使用流程

**下一步行動** (Sprint 1 Week 2):
1. 執行 3.1: 環境建置與容器化 (Docker Compose 配置)
2. 執行 3.2: 資料庫 Schema 實作 (Alembic Migrations)
3. 執行 3.3: FastAPI 專案結構建立
4. 執行 1.4.5: 技術債追蹤機制 (GitHub Issues Template)

---

### 2025-10-18 09:40 - v2.0 架構決策變更與進度更新

**✅ 完成項目** (Sprint 0 - 系統架構與設計):

1. **系統架構設計** (完成 8h)
   - ✅ C4 Level 1-2 架構圖 (05_architecture_and_design.md)

2. **資料庫設計** (完成 16h)
   - ✅ PostgreSQL ER 圖設計 (database/schema_design_v1.0.md)
   - ✅ 完整表結構設計 (13 tables, 含 event_logs JSONB 表)

3. **API 設計規範** (完成 6h)
   - ✅ RESTful API 規範制定 (06_api_design_specification.md)

4. **前端架構設計** (完成 32h) ⭐ 新增
   - ✅ 前端技術棧規範制定 (12_frontend_architecture_specification.md)
   - ✅ 前端信息架構設計 (17_frontend_information_architecture_template.md)
   - ✅ Elder-First 設計原則文檔
   - ✅ 前後端 API 契約對齊驗證

**架構決策變更**:

1. **ADR-001 更新**: 微服務 → **Modular Monolith**
   - 理由: MVP 階段簡化架構，降低開發與維運複雜度
   - 影響: 移除微服務邊界劃分任務，改為模組邊界設計

2. **ADR-003 廢棄**: MongoDB → **PostgreSQL JSONB**
   - 理由: 單一數據源，簡化技術棧，PostgreSQL JSONB 足夠靈活
   - 影響: 移除 4 個 MongoDB 任務 (共 16h)
   - 替代方案: event_logs 表使用 JSONB 欄位

**統計數據**:
- 已完成工時: 54h / 912h = **5.9%**
- 系統架構模組: 54h / 112h = **48%**
- 下一步: 完成 DDD 戰略設計與模組邊界劃分

---

**相關文檔連結**:
- **核心決策文檔**: [ADR 架構決策記錄](./adr/)
- [產品需求文件 (PRD)](./02_product_requirements_document.md)
- [系統架構設計文檔](./05_architecture_and_design.md)
- [資料庫 Schema 設計](./database/schema_design_v1.0.md)
- [API 設計規格](./06_api_design_specification.md)
- [前端架構規範](./12_frontend_architecture_specification.md)
- [前端信息架構](./17_frontend_information_architecture_template.md)
- [模組規格與測試](./07_module_specification_and_tests.md)
- [專案結構指南](./08_project_structure_guide.md)

---

*此 WBS 遵循 VibeCoding 開發流程規範,整合 TaskMaster Hub 智能協調機制,確保專案品質與交付效率。*
