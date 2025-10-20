# RespiraAlly V2.0 工作分解結構 (WBS) 開發計劃

---

**文件版本 (Document Version):** `v3.0.3` ✅ Task 3.4.4 完成 - Sprint 1 認證系統 Phase 1-4 完成 (85.6%)
**最後更新 (Last Updated):** `2025-10-20 22:30`
**主要作者 (Lead Author):** `TaskMaster Hub / Claude Code AI`
**審核者 (Reviewers):** `Technical Lead, Product Manager, Architecture Team, Client Stakeholders`
**狀態 (Status):** `執行中 - Sprint 0 進度 83.9% (專案管理 19.5% + 系統架構 100% ✅) + 客戶需求整合完成 (資料準確性 10h + CAT 無障礙 TTS 24h + 營養評估 56h = 90h)`

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
| **專案狀態** | 執行中 (In Progress) - 目前進度: ~24.3% 完成 (Sprint 0 完成 83.9% + Sprint 1 進行中 85.6%) |
| **文件版本** | v3.0.3 ⭐ Task 3.4.4 完成 - Sprint 1 認證系統 Phase 1-4 完成 (85.6%) |
| **最後更新** | 2025-10-20 17:05 |

### ⏱️ 專案時程規劃

| 項目 | 日期/時間 |
|------|----------|
| **總工期** | 16 週 (8 Sprints × 14 days) (2025-10-21 ～ 2026-02-12) |
| **目前進度** | ~24.3% 完成 (~269h/1107h，Sprint 0 完成 ✅ + Sprint 1 進行中 85.6%) |
| **當前階段** | Sprint 0 收尾 (60.6%) + 客戶需求整合完成 - CR-001 資料驗證 (10h) + CR-002 CAT 無障礙 TTS (24h) + CR-003 營養評估 (56h) = 90h 已納入 Sprint 2-3 |
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

5.0 Sprint 3: 儀表板 & 問卷系統 + 營養評估 + 無障礙 TTS [176h] ⭐ v3.0 +80h [Week 5-6]
├── 5.1 個案 360° 頁面 [32h]
├── 5.2 CAT/mMRC 問卷 API [24h]
├── 5.3 LIFF 問卷頁 [24h]
├── 5.4 趨勢圖表元件 [16h]
├── 5.5 營養評估 KPI ⭐ 新增 [56h]
│   ├── 5.5.1 營養測量數據 API [16h]
│   ├── 5.5.2 營養量表 API [12h]
│   ├── 5.5.3 Dashboard 營養輸入介面 [12h]
│   ├── 5.5.4 營養風險計算整合 [8h]
│   └── 5.5.5 LIFF 營養趨勢顯示 [8h]
└── 5.6 CAT 量表無障礙設計 (TTS) ⭐ 新增 [24h - 客戶需求 2]
    ├── 5.6.1 TTS 朗讀功能整合 [12h]
    ├── 5.6.2 TTS 控制介面與設定 [8h]
    └── 5.6.3 跨瀏覽器兼容性測試 [4h]

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
| 3.0 Sprint 1 (基礎設施) ⭐ | 104h (+8h) | 97.2h | 93.5% | ⚡ |
| 4.0 Sprint 2 (病患管理) ⭐ | 128h (+16h) | 0h | 0% | ⬜ |
| 5.0 Sprint 3 (儀表板+營養) ⭐ | 176h (+80h) | 0h | 0% | ⬜ |
| 6.0 Sprint 4 (風險引擎) | 104h | 0h | 0% | ⬜ |
| 7.0 Sprint 5 (RAG 系統) | 80h | 0h | 0% | ⬜ |
| 8.0 Sprint 6 (AI 語音) | 88h | 0h | 0% | ⬜ |
| 9.0 Sprint 7 (通知系統) | 72h | 0h | 0% | ⬜ |
| 10.0 Sprint 8 (優化上線) | 96h | 0h | 0% | ⬜ |
| 11.0 測試品保 (持續) | 80h | 0h | 0% | ⬜ |
| **總計** | **1113h** (+128h) | **277.2h** | **~24.9%** | **🔄** |

**狀態圖示說明:**
- ✅ 已完成 (Completed)
- 🔄 進行中 (In Progress)
- ⚡ 接近完成 (Near Completion)
- ⏳ 計劃中 (Planned)
- ⬜ 未開始 (Not Started)

**⚠️ 重要架構決策變更記錄:**

> **📋 完整變更日誌**: 請參閱 [開發日誌 CHANGELOG](./dev_logs/CHANGELOG.md)

### 最近更新 (Recent Updates)

#### v3.0.2 (2025-10-20) - 模組與類別設計完成 ✅
- **階段**: Sprint 0 架構設計收尾
- **工時**: +32h (總計 1107h)
- **核心成就**:
  - ✅ **模組與類別設計** (32h):
    - Clean Architecture 分層 UML 類別圖 (Patient, DailyLog, Risk 三大 Bounded Context)
    - SOLID 原則遵循性分析 (5 大原則完整證據)
    - 設計模式應用文檔 (8 種設計模式: Repository, Aggregate, Value Object, Domain Service, Factory, Adapter, Strategy, Observer)
    - 介面契約規範定義 (15+ 介面含前置/後置條件)
    - Python 實作範例 (Patient Aggregate, BMI Value Object, RiskEngine Domain Service 含單元測試)
  - ✅ **文檔產出**:
    - `10_class_relationships_and_module_design.md` (38,000+ 行詳細設計)
    - 30+ 類別職責定義與依賴關係圖
    - 完整 Pytest 單元測試範例
- **技術決策**: 以 Clean Architecture + DDD 完成 V2.0 架構設計全部任務
- **進度**: 系統架構 91.4% → 100% ✅, 整體進度 11.7% → 16.3%
- **里程碑**: 🎉 Sprint 0 系統架構設計 100% 完成, Sprint 1 開發就緒

#### v3.0.1 (2025-10-20) - 客戶需求理解修正 🔴 Critical Fix ✅
- **階段**: 需求修正 (CR-001 驗證邏輯 + CR-002 TTS 無障礙)
- **工時**: 維持 1075h (+90h)，但 CR-002 從拒絕→接受
- **修正背景**:
  - 🔴 **CR-001 設計邏輯錯誤**:
    - 水分範圍：500-3000ml → **0-4000ml** (符合臨床實務)
    - 服藥欄位：次數 (Integer) → **布林值 (Boolean)** (有/無服藥)
    - **移除痰量**：患者無法準確自行測量
  - 🔴 **CR-002 需求理解錯誤**:
    - 錯誤理解：語音輸入 (STT 128h) → 拒絕
    - **實際需求**：語音朗讀 (TTS 24h，無障礙設計) → **接受**
    - 決策變更：從「拒絕/延後」→「接受並整合至 Sprint 3 (5.6)」
- **影響**:
  - Sprint 3 新增 5.6 模組 (CAT 無障礙 TTS - 24h)
  - 客戶需求總工時：66h → 90h (+24h)
  - 開發時程：+8 天 → +11 天
- **里程碑**: 🎯 需求理解偏差修正完成，避免實作錯誤

#### v3.0 (2025-10-19) - 客戶新需求整合完成 ✅
- **階段**: Sprint 0 完成 + 客戶需求評估
- **工時**: +90h (總計 1075h)
- **核心成就**:
  - ✅ **需求評估報告完成** - 3 項客戶需求的 Linus 式綜合評估 (128h 評估工作)
  - ✅ **需求 1: 資料準確性驗證** (10h) - 整合到 Sprint 2 (4.2.9-4.2.10)
    - Pydantic 範圍驗證 (後端)
    - React Hook Form 即時驗證 (前端)
  - ✅ **需求 2: CAT 量表無障礙設計 (TTS)** (24h) - 整合到 Sprint 3 (5.6)
    - Web Speech API TTS 朗讀問題與選項
    - 控制介面 (播放/暫停/重播/語速)
    - 跨瀏覽器兼容性測試
    - **決策修正**: 原誤解為語音輸入 (STT 128h)，實為語音朗讀 (TTS 24h)
  - ✅ **需求 3: 營養評估 KPI (簡化版)** (56h) - 整合到 Sprint 3 (5.5)
    - 營養測量 API (體重、肌肉量、小腿圍、握力)
    - 簡化版營養量表 (MNA-SF/MUST)
    - Dashboard 輸入介面 + LIFF 趨勢顯示
- **進度**: 整體進度 12.4% → 11.7% (分母增加)
- **里程碑**: 🎯 客戶需求納入 WBS, Sprint 2-3 範圍明確

#### v2.9 (2025-10-20) - JWT 認證設計 + 索引策略規劃完成 ✅
- **階段**: Sprint 0 收尾 (60.6%)
- **工時**: +8h (總計 995h)
- **核心成就**:
  - ✅ JWT 認證授權設計完成 (4h) - `security/jwt_authentication_design.md` (60 頁)
  - ✅ 索引策略規劃完成 (4h) - `database/index_strategy_planning.md` (65 頁)
  - ✅ Sprint 1 任務細化 (+8h): Token 黑名單、刷新端點、Phase 0 核心索引
  - ✅ 實施檢查點建立: 認證系統 6 項、數據庫 4 項品質標準
- **進度**: 系統架構 78.4% → 91.4%, 整體進度 10.8% → 12.4%
- **里程碑**: 🚀 Sprint 1 準備就緒

#### v2.8 (2025-10-19) - 架構文件邏輯結構優化 ✅
- 應用 Linus "Good Taste" 原則重構架構文檔
- 事件驅動架構整合為系統通信機制

#### v2.5 (2025-10-18) - AI 處理日誌設計完成 ✅
- AI 處理日誌表設計 (4h) - `ai_processing_logs` 支持 STT/LLM/TTS/RAG
- 7 個優化索引 + 成本監控視圖

#### v2.4 (2025-10-18) - DDD 戰略設計完成 ✅
- 7 個界限上下文定義 (2 核心域 + 3 支撐子域 + 2 通用子域)
- 40+ 領域術語標準化
- 7 個聚合設計

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
| 3.4.6 | 登入失敗鎖定策略 (Redis) | Backend | 4 | ⬜ | Week 2 | 3.4.4 | ADR-008 + security/jwt_authentication_design.md §8.3 |

**Phase 1-4 詳細成果** (34h 已完成):
- ✅ Phase 1 (8h): JWT 工具函數 + Pydantic Models + 單元測試 (21 個測試, 98% 覆蓋率)
- ✅ Phase 2 (11h): Redis Client + Token Blacklist Service + FastAPI Dependencies (get_current_user, get_current_patient, get_current_therapist)
- ✅ Phase 3 (10h): User Repository Interface + 5 個 Use Cases (PatientLogin, TherapistLogin, Logout, RefreshToken, TherapistRegister)
- ✅ Phase 4 (5h): UserRepositoryImpl (Infrastructure) + Auth Router (5 個 API Endpoints) + OpenAPI 文檔自動生成
- 📦 代碼量: ~2,645 行生產代碼 (新增 445 行) + 292 行測試代碼
- 📝 Git Commits: 7c5e646 (Phase 1), d1ccd7a (Phase 2), 3680316 (Phase 3), ea4697d (Phase 4)

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
| 3.5.5 | Dashboard 登入頁 UI (US-102) | Frontend | 4 | ⏸ | Sprint 2 | 3.5.4, 3.4.6 | - |
| 3.5.6 | LIFF 註冊頁 UI (US-101) | Frontend | 2 | ⏸ | Sprint 2 | 3.5.4, 3.4.5 | - |

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
| 4.2.9 | 資料準確性驗證 - Pydantic Validators ⭐ 新增 | Backend | 4 | ⬜ | Week 4 | 4.2.1 | 客戶需求 1 |
| 4.2.10 | 資料準確性驗證 - 前端即時提示 ⭐ 新增 | Frontend | 4 | ⬜ | Week 4 | 4.3.4 | 客戶需求 1 |
| 4.2.11 | 資料異常警告機制 ⭐ 新增 | Backend | 2 | ⬜ | Week 4 | 4.2.9 | 客戶需求 1 |

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

**4.0 Sprint 2 小計**: 128h (+10h 資料驗證 +6h Sprint 1 延後) | 進度: 0% (0/128h 已完成)
**關鍵交付物**: 病患列表、日誌提交 API (含資料驗證)、LIFF 日誌表單、Dashboard/LIFF 登入註冊頁
**⭐ v3.0 新增**: 資料準確性驗證 (10h) - 後端範圍檢查 + 前端即時提示
**⭐ v4.5 新增**: Sprint 1 延後項目 (6h) - Dashboard 登入頁 + LIFF 註冊頁

---

### 5.0 Sprint 3: 儀表板 & 問卷系統 + 營養評估 [Week 5-6]

**Sprint 目標**: 完成個案 360° 頁面、CAT/mMRC 問卷系統、趨勢圖表，並整合營養評估 KPI。

#### 5.1 個案 360° 頁面 [32h]
*詳細任務分解保持原規劃*

#### 5.2 CAT/mMRC 問卷 API [24h]
*詳細任務分解保持原規劃*

#### 5.3 LIFF 問卷頁 [24h]
*詳細任務分解保持原規劃*

#### 5.4 趨勢圖表元件 [16h]
*詳細任務分解保持原規劃*

#### 5.5 營養評估 KPI ⭐ 新增 [56h - 客戶需求 3]

**⭐ v3.0 新增: 營養評估 KPI (簡化版)**

**業務目標**: 擴展健康評估維度，整合營養狀況評估到風險評分系統。

**資料模型**: 新增 2 張表:
- `nutrition_measurements`: 體重、肌肉量、小腿圍、握力
- `nutrition_assessments`: 營養量表 (MNA-SF 或 MUST)

| 任務編號 | 任務名稱 | 負責人 | 工時(h) | 狀態 | 完成日期 | 依賴關係 | 參考文檔 |
|---------|---------|--------|---------|------|----------|----------|----------|
| **5.5.1 營養測量數據 API** | | | **16h** | | | | |
| 5.5.1.1 | 資料庫 Migration (2 張表) | Backend | 3 | ⬜ | Week 5 | 3.2.5 | 客戶需求評估報告 §3.3 |
| 5.5.1.2 | NutritionMeasurement Model & Repository | Backend | 4 | ⬜ | Week 5 | 5.5.1.1 | - |
| 5.5.1.3 | `POST /patients/{id}/nutrition-measurements` | Backend | 4 | ⬜ | Week 5 | 5.5.1.2 | - |
| 5.5.1.4 | `GET /patients/{id}/nutrition-measurements` | Backend | 3 | ⬜ | Week 5 | 5.5.1.3 | - |
| 5.5.1.5 | 營養測量數據驗證邏輯 | Backend | 2 | ⬜ | Week 5 | 5.5.1.2 | 體重 30-150kg, 握力 0-100kg |
| **5.5.2 營養量表 API** | | | **12h** | | | | |
| 5.5.2.1 | NutritionAssessment Model & Repository | Backend | 3 | ⬜ | Week 5 | 5.5.1.1 | - |
| 5.5.2.2 | 簡化版量表定義 (MNA-SF/MUST) | Backend | 3 | ⬜ | Week 5 | 5.5.2.1 | 需客戶確認選擇哪個量表 |
| 5.5.2.3 | `POST /patients/{id}/nutrition-assessments` | Backend | 4 | ⬜ | Week 6 | 5.5.2.2 | - |
| 5.5.2.4 | 營養風險分級邏輯 | Backend | 2 | ⬜ | Week 6 | 5.5.2.3 | low/medium/high |
| **5.5.3 Dashboard 營養輸入介面** | | | **12h** | | | | |
| 5.5.3.1 | 營養測量表單 UI (體重、肌肉量、小腿圍、握力) | Frontend | 6 | ⬜ | Week 5 | 5.5.1.3 | - |
| 5.5.3.2 | 營養量表填答 UI | Frontend | 4 | ⬜ | Week 6 | 5.5.2.3 | - |
| 5.5.3.3 | 治療師輸入驗證與提示 | Frontend | 2 | ⬜ | Week 6 | 5.5.3.2 | - |
| **5.5.4 營養風險計算整合** | | | **8h** | | | | |
| 5.5.4.1 | 營養風險整合到總風險評分 | Backend | 4 | ⬜ | Week 6 | 5.5.2.4, 6.1.1 | 需確認權重占比 |
| 5.5.4.2 | patient_kpis 表擴展 (營養 KPI) | Backend | 2 | ⬜ | Week 6 | 5.5.4.1 | - |
| 5.5.4.3 | 營養風險告警規則 | Backend | 2 | ⬜ | Week 6 | 5.5.4.2 | - |
| **5.5.5 LIFF 營養趨勢顯示** | | | **8h** | | | | |
| 5.5.5.1 | LIFF 營養趨勢頁面 | Frontend | 4 | ⬜ | Week 6 | 5.5.1.4 | - |
| 5.5.5.2 | 營養數據折線圖元件 | Frontend | 3 | ⬜ | Week 6 | 5.5.5.1 | - |
| 5.5.5.3 | 營養風險等級顯示 | Frontend | 1 | ⬜ | Week 6 | 5.5.2.3 | - |

**實施檢查點**:
1. **數據收集範圍明確**: ✅ 僅收集 4 項核心指標 (體重、肌肉量、小腿圍、握力)
2. **量表選擇確定**: ⚠️ 需客戶確認 MNA-SF (6 題) 或 MUST (5 題)
3. **風險整合權重**: ⚠️ 需客戶確認營養風險在總分中的占比
4. **輸入方式**: ✅ 治療師手動輸入 (非病人自填)
5. **測量頻率**: ✅ 低頻 (1-3 個月一次，非每日)

**待客戶確認事項** (Sprint 3 啟動前):
- [ ] 營養量表選擇: MNA-SF vs MUST vs 其他?
- [ ] InBody 是否還有其他「必須」收集的指標?
- [ ] 營養風險權重: 在總風險評分中占多少比例?

**5.0 Sprint 3 小計**: 176h (+80h) | 進度: 0% (0/152h 已完成)
**關鍵交付物**: 個案 360° 頁面、CAT/mMRC 問卷、趨勢圖表、營養評估 KPI (簡化版)
**⭐ v3.0 新增**: 營養評估 KPI (56h) - 測量 API + 量表 API + Dashboard 輸入 + LIFF 顯示

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

| WBS 模組 | 總工時 | 已完成 | 進度 | 狀態 |
|---------|--------|--------|------|------|
| 1.0 專案管理 ⭐ | 87h (+71h) | 17h | 19.5% | 🔄 |
| 2.0 系統架構 ⭐ | 148h (+36h) | 148h | 100% | ✅ |
| 3.0 Sprint 1 ⭐ | 104h (+8h) | 89h | 85.6% | 🔄 |
| 4.0 Sprint 2 ⭐ | 122h (+10h) | 0h | 0% | ⬜ |
| 5.0 Sprint 3 ⭐ | 176h (+80h) | 0h | 0% | ⬜ |
| 6.0 Sprint 4 | 104h | 0h | 0% | ⬜ |
| 7.0 Sprint 5 | 80h | 0h | 0% | ⬜ |
| 8.0 Sprint 6 | 88h | 0h | 0% | ⬜ |
| 9.0 Sprint 7 | 72h | 0h | 0% | ⬜ |
| 10.0 Sprint 8 | 96h | 0h | 0% | ⬜ |
| 11.0 測試品保 | 80h | 0h | 0% | ⬜ |
| **總計** | **1113h** (+128h) | **277.2h** | **~24.9%** | **🔄** |

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

**專案管理總結**: RespiraAlly V2.0 是一個高複雜度的 AI/ML Healthcare 專案,採用 8 Sprint 敏捷開發模式,總工時 983 小時 (v2.1 修正)。關鍵成功因素包括:專案管理流程的實務整合、技術架構的前置設計 (Sprint 0)、關鍵路徑的資源保障、風險的主動管理、以及測試品質的持續保證。

**架構決策**: MVP 階段採用 **Modular Monolith + PostgreSQL** 簡化技術棧，確保快速交付。Phase 3 後可根據實際需求拆分為微服務與專用向量資料庫。

**專案經理**: TaskMaster Hub / Claude Code AI
**最後更新**: 2025-10-18 10:00
**下次檢討**: 2025-10-21 (Sprint 1 Planning)

---

## 📋 專案進度日誌 (Development Progress)

> **注意**: 為了專注於 WBS 的核心功能(任務追蹤與進度管理),專案進度更新日誌已獨立管理。

### 📍 進度日誌位置

詳細的專案進度更新、版本變更記錄、里程碑達成等資訊,請參閱:

**→ [`docs/dev_logs/CHANGELOG.md`](./dev_logs/CHANGELOG.md)**

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
