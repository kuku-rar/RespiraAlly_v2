# 產品需求文件 (Product Requirements Document) - RespiraAlly V2.0

---

**文件版本 (Document Version):** `v3.0`
**最後更新 (Last Updated):** `2025-10-27`
**主要作者 (Lead Author):** `Claude Code AI`
**狀態 (Status):** `草稿 (Draft)` - 客戶新需求整合完成

---

## 目錄 (Table of Contents)

1.  [專案總覽 (Project Overview)](#第-1-部分專案總覽-project-overview)
2.  [商業目標 (Business Objectives) - 「為何做？」](#第-2-部分商業目標-business-objectives---為何做)
3.  [使用者故事與允收標準 (User Stories & UAT) - 「做什麼？」](#第-3-部分使用者故事與允收標準-user-stories--uat---做什麼)
4.  [範圍與限制 (Scope & Constraints)](#第-4-部分範圍與限制-scope--constraints)
5.  [待辦問題與決策 (Open Questions & Decisions)](#第-5-部分待辦問題與決策-open-questions--decisions)
6.  [測試與品質狀態 (Testing & Quality Status)](#第-6-部分測試與品質狀態-testing--quality-status) ⭐ **新增**
7.  [客戶新需求整合 (v3.0) (Client Requirements Integration)](#第-7-部分客戶新需求整合-v30-client-requirements-integration)

---

**目的**: 本文件旨在為 `RespiraAlly V2.0` 專案定義其「為何」、「為誰」與「做什麼」，作為所有後續設計、開發與測試工作的唯一事實來源 (Single Source of Truth)，並與敏捷開發流程中的各個產出保持同步。

---

## 第 1 部分：專案總覽 (Project Overview)

| 區塊 | 內容 |
| :--- | :--- |
| **專案名稱** | RespiraAlly V2.0 |
| **當前狀態** | Sprint 4 執行中 - GOLD ABE 風險引擎與預警系統 |
| **整體進度** | ~48.2% 完成 (479.75h / 996h) |
| **已完成階段** | ✅ Sprint 0: 專案管理與架構設計 (100%)<br>⚡ Sprint 1: 基礎設施與認證 (85.6%)<br>⚡ Sprint 2: 病患管理與日誌 (85.9%)<br>✅ Sprint 3: 儀表板與問卷系統 (100%) |
| **目標發布日期** | 2026 Q1 |
| **核心團隊** | PM: TaskMaster Hub (AI-Powered Project Coordination)<br>Technical Lead: Backend Lead + Frontend Lead<br>System Architect: Architecture Team<br>Quality Metrics: 100% 測試通過率 (75 整合測試 + 139 pytest) |

---

## 第 2 部分：商業目標 (Business Objectives) - 「為何做？」

*此部分提煉自 `AGILE_DESIGN_DOCUMENT.md` 中的產品洞察，定義了專案的核心價值與成功標準。*

| 區塊 | 內容 |
| :--- | :--- |
| **1. 背景與痛點** | 慢性阻塞性肺病（COPD）患者需要長期、持續的自我管理，但現行照護體系面臨三大挑戰：<br>1. **患者端**：傳統紙本記錄繁瑣、缺乏即時回饋、孤獨感強。<br>2. **治療師端**：資料分散、無法即時掌握風險、人工追蹤耗時。<br>3. **系統端**：靜態衛教內容無法個人化、缺乏行為預測、數據孤島嚴重。 |
| **2. 價值主張** | 我們旨在打造一個創新的數位健康管理平台，透過 **智慧提醒**、**AI 語音互動**、**即時風險預警** 和 **360° 個案儀表板**，為病患提供有溫度的陪伴，賦予治療師高效的管理工具，最終實現從「被動治療」到「主動預防」的轉變。 |
| **3. 成功指標 (Success Metrics)** | **北極星指標**: `健康行為依從率` (7日用藥 + 日誌完整度) **目標: ≥75%**。<br><br>**輔助指標**:<br>- 病患 D30 留存率<br>- 治療師週均登入次數<br>- AI 回覆首次命中率 ≥85% |

---

## 第 3 部分：使用者故事與允收標準 (User Stories & UAT) - 「做什麼？」

*這是連接「商業需求」與「技術實現」的橋樑。此處列出核心史詩與代表性使用者故事。*

### 📘 史詩 EP-100: 病患註冊與認證

| 使用者故事 ID | 描述 (As a, I want to, so that) | 核心允收標準 (UAT) | 連結至 BDD 文件 |
| :--- | :--- | :--- | :--- |
| **US-101** | **As a** 新病患,<br>**I want to** 透過 LINE 快速註冊,<br>**so that** 無需額外下載 App。 | 1. 成功使用 LINE User ID 註冊。<br>2. 註冊成功後綁定預設 Rich Menu。<br>3. 重複註冊時顯示錯誤訊息。 | [bdd/epic_100_authentication.feature](./bdd/epic_100_authentication.feature) |
| **US-103** | **As a** 新病患,<br>**I want to** 在初次註冊時填寫基本健康資料（身高、體重、醫院病歷號、吸菸史）,<br>**so that** 系統能計算 BMI 與風險評估。 | 1. 支援輸入身高 (50-250 cm)、體重 (20-300 kg)。<br>2. 醫院病歷號為選填。<br>3. 吸菸史包含狀態（從未/曾經/目前）與年數。<br>4. 系統自動計算 BMI 並分級 (過輕/正常/過重/肥胖)。 | [bdd/epic_100_authentication.feature](./bdd/epic_100_authentication.feature) |
| **US-102** | **As a** 治療師,<br>**I want to** 使用帳號密碼登入儀表板,<br>**so that** 我可以管理我的個案。 | 1. 使用正確的帳密成功登入。<br>2. 登入失敗 3 次後帳號鎖定 15 分鐘。<br>3. 登入成功後取得 JWT。 | [bdd/epic_100_authentication.feature](./bdd/epic_100_authentication.feature) |

### 📗 史詩 EP-200: 日常健康管理

| 使用者故事 ID | 描述 (As a, I want to, so that) | 核心允收標準 (UAT) | 連結至 BDD 文件 |
| :--- | :--- | :--- | :--- |
| **US-201** | **As a** 病患,<br>**I want to** 在 LIFF 快速填寫今日健康日誌,<br>**so that** 記錄我的健康狀況。 | 1. 每日只能新增一筆紀錄，但可更新。<br>2. 提交後觸發風險分數重新計算。<br>3. 輸入無效資料時應提示錯誤。 | [bdd/epic_200_daily_management.feature](./bdd/epic_200_daily_management.feature) |
| **US-202** | **As a** 病患,<br>**I want to** 查看近 7 日健康趨勢,<br>**so that** 了解我的短期進步。 | 1. 應以折線圖呈現。<br>2. 包含用藥、飲水、運動等系列。<br>3. 若無資料應顯示提示。<br>4. 支援顯示移動平均線平滑曲線。 | [bdd/epic_200_daily_management.feature](./bdd/epic_200_daily_management.feature) |
| **US-203** | **As a** 病患,<br>**I want to** 查看我的核心健康 KPI（依從率、飲水量、運動量、問卷分數）,<br>**so that** 快速了解整體健康狀況。 | 1. KPI 資料從快取表讀取，查詢時間 < 50ms。<br>2. 包含 7 日與 30 日依從率對比。<br>3. 顯示最新 CAT/mMRC 問卷分數與日期。<br>4. 顯示最新風險等級。 | [bdd/epic_200_daily_management.feature](./bdd/epic_200_daily_management.feature) |
| **US-205** | **As a** 病患,<br>**I want to** 查看近 30 日健康趨勢,<br>**so that** 了解我的長期變化。 | 1. 提供 7 日/30 日切換選項。<br>2. 30 日圖表應正確顯示數據。<br>3. 支援顯示累積統計（總日誌數、總用藥次數）。 | [bdd/epic_200_daily_management.feature](./bdd/epic_200_daily_management.feature) |


### 📙 史詩 EP-300: AI 語音互動

| 使用者故事 ID | 描述 (As a, I want to, so that) | 核心允收標準 (UAT) | 連結至 BDD 文件 |
| :--- | :--- | :--- | :--- |
| **US-301** | **As a** 病患,<br>**I want to** 用語音詢問健康問題,<br>**so that** 不需要打字。 | 1. 15 秒內收到文字與語音回覆。<br>2. 支援台語/國語辨識。<br>3. 對於無法辨識的音訊應有提示。 | [bdd/epic_300_ai_interaction.feature](./bdd/epic_300_ai_interaction.feature) |
| **US-302** | **As an** AI Worker,<br>**I want to** 處理語音任務佇列,<br>**so that** 不阻塞主服務。 | 1. 依序執行 STT, RAG, LLM, TTS。<br>2. 任何步驟失敗應有重試機制。<br>3. 最終結果透過 WebSocket 推送。 | [bdd/epic_300_ai_interaction.feature](./bdd/epic_300_ai_interaction.feature) |
| **US-303** | **As a** 病患,<br>**I want to** 讓 AI 回覆引用可信來源,<br>**so that** 我能增加信任感。 | 1. 回覆應附上參考資料連結。<br>2. 當 AI 回覆信心度低時，應提示使用者諮詢治療師。 | [bdd/epic_300_ai_interaction.feature](./bdd/epic_300_ai_interaction.feature) |
P
---

## 第 4 部分：範圍與限制 (Scope & Constraints)

### 4.1 開發進度與 MVP 分階段交付策略

基於架構審視報告 ([05_architecture_and_design.md](./05_architecture_and_design.md))，為避免過度設計並加速市場驗證，我們採用**分階段漸進式 MVP** 策略：

#### 4.1.1 Phase 與 Sprint 對照表

| Sprint | 對應 Phase | 完成狀態 | 核心交付 | 工時 |
|--------|-----------|---------|----------|------|
| **Sprint 0** | Phase 0 準備 | ✅ 100% | 專案管理、系統架構設計、ADR × 8 | 165h |
| **Sprint 1** | Phase 0 實作 | ⚡ 85.6% | 基礎設施、認證系統 (JWT + Token Blacklist)、資料庫 Schema | 89h/104h |
| **Sprint 2** | Phase 0 完成 | ⚡ 85.9% | 病患管理 API、日誌功能、Dashboard 病患列表、資料驗證 (CR-001) | 133.75h/155.75h |
| **Sprint 3** | Phase 1 開始 | ✅ 100% | CAT/mMRC 問卷、360° 頁面、TTS 無障礙 (CR-002) | 96h |
| **Sprint 4** | Phase 1 延伸 | 🔄 66.4% | GOLD ABE 風險引擎、急性發作管理、警示系統 | 44.5h/67h |
| **Sprint 5-6** | Phase 2 開始 | ⏳ 計劃中 | RAG 系統、AI 語音處理鏈 | 224h |
| **Sprint 7-8** | Phase 3 上線 | ⏳ 計劃中 | 通知系統、效能優化、監控部署 | 168h |

**註**：Phase 0-1 的核心功能已基本完成（~48% 進度），目前聚焦於 Phase 1 的進階功能（GOLD ABE 風險評估）與 Phase 2 的 AI 能力建設。

#### 4.1.2 Phase 功能規劃（原始設計）

| 階段 | 時程 | 核心功能 | 成功標準 | 技術重點 |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 0: 核心驗證** | Week 1-4 | - 治療師登入<br>- 病患 LINE 註冊<br>- 每日健康日誌提交<br>- 病患列表查看<br>- 基礎依從率計算 | - 5 位治療師試用<br>- 20 位病患持續 14 天記錄<br>- 依從率 ≥60% | - Modular Monolith<br>- PostgreSQL + Redis<br>- 簡化 API 設計 |
| **Phase 1: 增值功能** | Week 5-8 | - CAT/mMRC 問卷<br>- 風險評分引擎 (GOLD ABE)<br>- 異常預警<br>- 智慧提醒 | - 風險預警準確率 ≥80%<br>- 提醒點擊率 ≥30% | - 規則引擎<br>- APScheduler<br>- LINE Push API |
| **Phase 2: AI 能力** | Week 9-12 | - RAG 知識庫<br>- AI 語音互動 (STT/LLM/TTS)<br>- 個人化衛教推薦 | - AI 回覆首次命中率 ≥85%<br>- 語音回覆 < 15 秒 | - pgvector<br>- OpenAI API<br>- RabbitMQ (可選) |
| **Phase 3: 優化上線** | Week 13-16 | - 效能優化<br>- 監控告警<br>- 生產部署<br>- 文檔完善 | - API P95 < 500ms<br>- 服務可用性 ≥99.5%<br>- 安全稽核通過 | - Prometheus + Grafana<br>- Zeabur 部署<br>- CI/CD Pipeline |

**關鍵理念**:
- **Phase 0 是最小可驗證核心** - 用 4 週驗證核心假設（病患願意每日記錄），而非 16 週後才知道方向錯誤
- **每個 Phase 都是可獨立交付的 MVP** - 即使後續 Phase 失敗，前階段的價值依然存在
- **技術棧隨需求漸進複雜化** - Phase 0 不引入 RabbitMQ、Jaeger 等非必要技術

---

### 4.2 功能範圍定義

| 區塊 | 內容 |
| :--- | :--- |
| **功能性需求 (In Scope)** | - **病患端** (LIFF): LINE 註冊/登入、每日日誌提交、CAT/mMRC 問卷、AI 語音對話、個人健康趨勢查看。<br>- **治療師端** (Web Dashboard): 帳密登入、病患列表、個案 360° 檔案、風險預警中心、任務管理、衛教內容管理。<br>- **系統端**: 風險評分引擎、異常規則引擎、智慧提醒排程、RAG 向量檢索、AI 語音處理鏈。 |
| **非功能性需求 (NFRs)** | - **性能**: API P95 < 500ms，AI 語音端到端回覆 < 15 秒。<br>- **安全性**: RBAC 權限控制、傳輸與靜態加密、治療師登入失敗鎖定策略。<br>- **可用性**: 服務可用性 ≥99.5%（Phase 3 後）。<br>- **可維護性**: 新功能交付週期 < 2 週，測試覆蓋率 ≥80%。 |
| **不做什麼 (Out of Scope)** | - **V2.0 不支援**: 生理感測裝置整合、跨院資料交換（FHIR/HL7）、原生 iOS/Android App、治療師之間的協作功能、多語言國際化（僅支援繁體中文）。<br>- **技術限制**: MVP 階段不使用 Kubernetes、不自建 LLM 模型、~~不使用 Kafka（使用 RabbitMQ 替代）~~ **已簡化** - RabbitMQ 為 Phase 2+ 可選技術，Phase 0-1 使用同步處理。 |
| **假設與依賴** | - **假設**: 目標使用者（長者）皆熟悉 LINE 基本操作、治療師具備基本電腦操作能力、病患願意每日花費 2-3 分鐘記錄健康日誌。<br>- **外部依賴**: LINE Platform（病患唯一入口）、OpenAI API（STT/LLM/TTS，Phase 2）、Zeabur（PaaS 部署平台）。<br>- **內部依賴**: PostgreSQL ≥15（含 pgvector 擴展）、Redis ≥7、Python ≥3.11、Node.js ≥18、~~MongoDB 7+（已廢棄，改用 PostgreSQL JSONB）~~。 |

---

## 第 5 部分：待辦問題與決策 (Open Questions & Decisions)

| 問題/決策 ID | 描述 | 狀態 | 參考 |
| :--- | :--- | :--- | :--- |
| **D-001** | 決定採用 FastAPI 作為後端框架，以支援異步與高效能需求。 | [已決定] | [ADR-001](./adr/ADR-001-fastapi-vs-flask.md) |
| **D-002** | 決定採用 pgvector 作為初期向量庫，以簡化 MVP 架構。 | [已決定] | [ADR-002](./adr/ADR-002-pgvector-for-vector-db.md) |
| **D-003** | ~~決定採用 MongoDB 儲存事件日誌~~ **已廢棄** - 改用 PostgreSQL JSONB 欄位儲存事件日誌，簡化技術棧。 | [已變更] | [05_architecture_and_design.md - 簡化技術棧](./database/schema_design_v1.0.md#34-事件與通知表) |
| **D-004** | 決定採用 LINE 作為唯一的病患互動入口，以降低使用門檻。 | [已決定] | [ADR-004](./adr/ADR-004-line-as-patient-entrypoint.md) |
| **D-005** | 決定採用 RabbitMQ 作為異步任務的訊息佇列。 | [已決定] | [ADR-005](./adr/ADR-005-rabbitmq-for-message-queue.md) |
| **Q-001** | `ai-worker` 中使用的 STT/LLM/TTS 服務是外部 API 還是內部模型？其規格與限制為何？ | [待釐清] | - |

---

## 第 6 部分：測試與品質狀態 (Testing & Quality Status)

### 6.1 測試覆蓋率概況 ⭐

| 測試類型 | 完成狀態 | 測試數量 | 通過率 | 備註 |
|---------|---------|---------|--------|------|
| **整合測試** (Integration Tests) | ✅ 完成 | 75 tests | **100%** | Backend API 端點完整測試 |
| **單元測試** (Unit Tests) | ✅ 完成 | 139 tests | **100%** | Backend 業務邏輯與工具函數 |
| **類型檢查** (Type Checking) | ✅ 通過 | N/A | **100%** | Frontend TypeScript Strict Mode |
| **程式碼檢查** (Linting) | ✅ 通過 | N/A | **100%** | ESLint (Frontend) + Ruff (Backend) |
| **Elder-First 設計** (Accessibility) | ✅ 符合 | N/A | **100%** | 字體 ≥18px, 觸控目標 ≥44px |
| **E2E 測試** (End-to-End) | ⏳ 進行中 | 75+ items | TBD | 手動測試清單（參見 E2E_TEST_CHECKLIST.md） |

### 6.2 品質指標達成狀況

| 品質指標 | 目標值 | 當前值 | 狀態 | 參考文件 |
|---------|--------|--------|------|----------|
| **測試通過率** | ≥95% | **100%** | ✅ 超標 | [INTEGRATION_TEST_REPORT.md](./test_reports/INTEGRATION_TEST_REPORT.md) |
| **測試覆蓋率** | ≥80% | ~85% | ✅ 達標 | Backend pytest coverage |
| **TypeScript 嚴格模式** | 無錯誤 | **0 errors** | ✅ 達標 | Frontend type-check |
| **技術債** | 零債務 | **0 P0/P1** | ✅ 達標 | 已完成 292/310 issues |
| **Elder-First 合規** | 100% | **100%** | ✅ 達標 | [ADR-008](./adr/ADR-008-elder-first-design-principles.md) |

### 6.3 CI/CD 品質閘門

✅ **所有品質閘門已配置並通過**：
- ✅ Backend: Black (格式化), Ruff (Linting), Mypy (型別檢查), Pytest (測試)
- ✅ Frontend: Prettier (格式化), ESLint (Linting), TypeScript (型別檢查), Build (編譯)
- ✅ Security: pip-audit (Python 依賴安全), npm audit (JavaScript 依賴安全)
- ✅ Dependency Check: 過時依賴版本檢查

**測試報告文件**：
- [整合測試報告](./test_reports/INTEGRATION_TEST_REPORT.md) - 75 測試案例，100% 通過
- [E2E 測試清單](./test_reports/E2E_TEST_CHECKLIST.md) - 75+ 測試項目
- [並行開發策略](./PARALLEL_DEV_STRATEGY.md) - Mock 模式測試策略

---

## 第 7 部分：客戶新需求整合 (v3.0) (Client Requirements Integration)

**更新背景**: 客戶於 2025-10-19 提出三項新需求，經 Linus 式技術評估後，**2/3 接受並完成**（CR-001 Sprint 2 完成、CR-002 Sprint 3 完成、CR-003 延後至 Phase 2）。以下記錄完整評估結果與實際整合狀況。

---

### 7.1 需求評估總覽 (工時影響表) - **已更新實際狀態** ⭐

| 需求 ID | 需求名稱 | 決策 | 實際狀態 | 優先級 | 預估工時 | 實際工時 | 整合 Sprint | 影響模組 |
|---------|---------|------|----------|--------|---------|---------|-------------|----------|
| **CR-001** | 病患資料準確性驗證 | ✅ **接受** | ✅ **Sprint 2 完成** | **P1** | 10h | 10h | **Sprint 2** ✅ | Backend, Frontend |
| **CR-002** | CAT 量表無障礙設計 (TTS) | ✅ **接受** | ✅ **Sprint 3 完成** | **P1** | 24h → **8h** | 8h | **Sprint 3** ✅ | Frontend |
| **CR-003** | 營養評估 KPI (簡化版) | ⏸ **延後** | ⏸ **延後至 Phase 2** | **P2** | 56h | 0h | **Sprint 6+** ⏳ | Backend, Database, Frontend |
| **總計** | **已接受的新需求** | **2/3 接受** | **2/3 完成** | - | **18h** | **18h** | - | - |

**實際工時影響** ⭐:
- Sprint 2 增加 10h (4.2.9 - 4.2.11): 資料驗證 ✅ **已完成**
- Sprint 3 增加 8h (5.6 無障礙 TTS): Web Speech API 實現 ✅ **已完成**
- Sprint 3 營養評估 (5.5) **已延後至 Phase 2** ⏸
- **實際工時變化**: +18h（而非原估 90h，節省 72h）

**決策變更說明** ⭐:
- **CR-002 需求理解修正**：從「語音輸入 (STT)」→「語音朗讀 (TTS)」
- **CR-002 工時優化**：從 24h → 8h（採用 Web Speech API，參見 [ADR-011](./adr/ADR-011-tts-implementation-simplification.md)）
- **CR-002 實際交付**：✅ **Sprint 3 完成**（useTTS Hook + 基本 UI）
- **CR-003 延後決策**：基於 Linus 式實用主義，需求不明確（量表未選定），延後至 MVP 後評估

---

### 7.2 CR-001: 病患資料準確性驗證 ✅

#### 需求描述
**客戶訴求**: "病患填寫的每日健康日誌數據（水分攝取、運動時間、服藥狀況等）可能存在錯誤輸入（如水分攝取 9999ml），需要系統提供合理性驗證與警告機制。"

**業務價值**:
- 提升數據質量，確保 KPI 計算準確性
- 降低治療師審核負擔
- 避免誤判風險等級

#### 解決方案
**技術方案**: Pydantic 後端驗證 + 前端即時提示

**驗證規則表**:
| 欄位 | 資料類型 | 正常範圍 | 超過範圍提示訊息 | Schema 欄位 |
|------|---------|---------|------------------|------------|
| 水分攝取 (ml) | Integer | 0 - 4000 | "您輸入的水分攝取為 {value}ml，超過一般建議範圍 (0-4000ml)，請確認是否正確。" | `water_intake_ml` |
| 運動時間 (min) | Integer | 0 - 180 | "您輸入的運動時間為 {value}分鐘，超過 3 小時較不常見，請確認是否正確。" | `exercise_minutes` |
| 服藥狀況 | Boolean | true / false | （無需範圍驗證，僅選擇「有服藥」或「無服藥」） | `medication_taken` |
| 體重 (kg) | Float | 30 - 150 | "您輸入的體重為 {value}kg，數值異常，請確認是否正確。" | `weight_kg` (Profile) |
| **吸菸數量 (支/日)** ⭐ | Integer | 0 - 100 | "您輸入的吸菸數量為 {value}支，數值較高，請確認是否正確。" | `smoking_count` ⭐ **新增** |

**設計說明**:
- **簡化原則**: 移除「警告」與「錯誤」雙層閾值，統一為「正常範圍」+ 「超過範圍提示確認」
- **移除痰量**: 患者無法準確自行測量，已從 Schema v4.9 移除
- **服藥改為布林值**: 從「次數」改為「有/無」，更符合實際使用情境
- **新增吸菸數量** ⭐: 對應 Schema v4.9 新增的 `smoking_count` 欄位，用於追蹤戒菸進度

**允收標準** (UAT):
1. 後端: Pydantic model 驗證數值是否在正常範圍內
2. 後端: 超過範圍時 API 回傳 `warnings` 欄位提示確認
3. 前端: 超過範圍時顯示確認對話框（用戶可選擇修改或強制提交）
4. 治療師 Dashboard: 標註 "⚠️ 數據異常" 的日誌條目

#### 整合細節
**Sprint 2 新增任務** (參見 WBS v3.0 Section 4.2):
- **4.2.9** 資料準確性驗證 - Pydantic Validators (4h)
- **4.2.10** 資料準確性驗證 - 前端即時提示 (4h)
- **4.2.11** 資料異常警告機制 (2h)

**資料庫影響**: 無需 Schema 變更

**API 變更**:
```json
// POST /daily-logs 回應範例（超過範圍時）
{
  "success": true,
  "log_id": 12345,
  "warnings": [
    {
      "field": "water_intake",
      "value": 4500,
      "message": "您輸入的水分攝取為 4500ml，超過一般建議範圍 (0-4000ml)，請確認是否正確。"
    }
  ]
}
```

---

### 7.3 CR-002: CAT 量表無障礙設計 (TTS 朗讀) ✅

#### 需求描述
**客戶訴求**: "希望 LIFF 前端能夠**朗讀 CAT 量表問題**，讓視力不佳或閱讀困難的長者也能順利完成填寫。"

**需求澄清** (重要):
- ❌ **不是**語音輸入 (STT)：患者不需要說話回答
- ✅ **是**語音朗讀 (TTS)：系統朗讀問題，患者依然用按鈕/文字輸入
- ✅ 符合無障礙設計標準 (WCAG 2.1 AA)

**業務價值**:
- 解決長者視力退化、閱讀困難問題
- 提升用戶體驗，降低填寫門檻
- 符合無障礙設計最佳實踐

#### 解決方案
**技術方案**: Web Speech API (TTS) + LIFF 前端控制

**功能規格**:
| 功能 | 描述 | 互動方式 |
|------|------|----------|
| 問題朗讀 | 點擊「🔊 播放問題」按鈕朗讀題目 | 按鈕觸發 |
| 選項朗讀 | 點擊「🔊」圖標朗讀每個選項 | 選項旁按鈕 |
| 控制按鈕 | 播放/暫停/重播/語速調整 | 控制面板 |
| 自動播放 (可選) | 載入題目時自動朗讀 | 設定開關 |

**技術細節**:
- **TTS 引擎**: Web Speech API (`speechSynthesis`)
- **語音**: 繁體中文 (`zh-TW`)
- **降級方案**: 不支援 TTS 的瀏覽器顯示提示，仍可正常使用

**技術規格估算**:
- TTS 整合 (12h): Web Speech API，朗讀問題與選項
- UI 控制 (8h): 播放/暫停/重播/語速按鈕
- 跨瀏覽器測試 (4h): Chrome, Safari, LINE 內建瀏覽器
- **總計**: **24h** (約 3 工作天)

**允收標準** (UAT):
1. 前端: 點擊播放按鈕後朗讀問題文字
2. 前端: 提供暫停、重播、語速調整功能
3. 前端: 不支援 TTS 的瀏覽器顯示友善提示
4. 測試: LINE 內建瀏覽器 TTS 功能正常運作

#### 決策理由 (Linus 式評估)

**這是真實問題 (Real Problem)**:
```
長者常見狀況：
- 老花眼、視力退化 → 閱讀困難
- 識字率差異 → 理解困難
- 無障礙需求 → 符合 WCAG 標準

這不是理論問題，是實際使用者痛點。
```

**複雜度合理 (Reasonable Complexity)**:
```
僅需前端 TTS（24h）:
- Web Speech API 原生支援
- 無需後端改動
- 無需語音識別 (STT)
- 患者依然用按鈕輸入 → 零學習成本

這是簡單、實用的解決方案。
```

**實用性高 (High Practicality)**:
```
✅ 符合無障礙設計標準
✅ 零破壞（不影響現有功能）
✅ 可選功能（不喜歡可關閉）
✅ 低成本高價值（24h vs 用戶體驗提升）

Linus 語錄: "Practicality beats purity."
這是務實的無障礙設計。
```

#### 整合細節
**Sprint 3 新增任務** (參見 WBS v3.0 Section 5.6):
- **5.6.1** CAT 量表 TTS 朗讀功能 (12h)
- **5.6.2** TTS 控制介面與設定 (8h)
- **5.6.3** 跨瀏覽器兼容性測試 (4h)

**前端影響**: LIFF CAT 量表頁面新增 TTS 控制按鈕

**後端影響**: 無需變更

**UI/UX 設計**:
```
┌─────────────────────────────────┐
│ CAT 量表 - 第 1 題              │
├─────────────────────────────────┤
│ 您在咳嗽時會感到：              │
│ [🔊 播放問題]  [⏸️ 暫停] [🔁 重播]│
├─────────────────────────────────┤
│ ○ 從不 [🔊]                     │
│ ○ 偶爾 [🔊]                     │
│ ○ 有時 [🔊]                     │
│ ○ 經常 [🔊]                     │
│ ○ 總是 [🔊]                     │
├─────────────────────────────────┤
│ [語速: ▼慢 ●中 ▲快]            │
│ [☑️ 自動播放]                   │
└─────────────────────────────────┘
```

**結論**: ✅ **已於 Sprint 3 完成**

**決策歷程**:
- ❌ **初始評估（v3.0 早期）**：拒絕（因誤解為 STT 語音輸入，工時估 128h）
- ✅ **需求澄清後（v3.0 修訂）**：接受（TTS 朗讀，工時降至 24h）
- ✅ **實際交付（Sprint 3）**：Web Speech API 實現，最終 **8h 完成**（參見 [ADR-011](./adr/ADR-011-tts-implementation-simplification.md)）

**實作成果**:
- ✅ useTTS 自訂 Hook（支援播放/暫停/語速控制）
- ✅ LIFF CAT 量表頁面整合朗讀按鈕
- ✅ 基本無障礙標籤（ARIA）
- ⏸ 進階 UI（控制面板）延後至 Phase 2 優化

---

### 7.4 CR-003: 營養評估 KPI ⏸ **延後至 MVP 後 (Phase 2)**

#### 需求描述
**客戶訴求**: "希望系統能追蹤病患的營養狀態指標（如體重、肌肉量、營養量表分數），協助評估營養風險。"

**業務價值**:
- 全人照護：營養是 COPD 管理的重要環節
- 早期介入：及時發現營養不良風險
- 跨專業協作：提供營養師參考數據

#### 簡化策略 (避免過度設計)
**原始需求** (客戶期望):
- 完整營養量表 (MNA-SF, MUST, NRS-2002)
- 生化指標追蹤 (血清白蛋白、血紅素)
- 飲食日誌分析
- 營養計劃建議

**簡化後** (MVP):
- ✅ **4 核心營養測量指標**
- ✅ **1 簡化營養量表** (Mini Nutritional Assessment Short Form, MNA-SF)
- ✅ **營養風險分級**
- ❌ 生化指標（需醫療設備）
- ❌ 飲食日誌（數據輸入負擔高）
- ❌ 營養計劃（超出系統範疇）

#### 功能規格

**4 核心營養測量指標**:
| 指標 | 單位 | 合理範圍 | 測量頻率 | 備註 |
|------|------|---------|---------|------|
| 體重 (Weight) | kg | 30-150 | 每週 | 已包含在 CR-001 |
| 肌肉質量 (Muscle Mass) | kg | 10-60 | 每月 | 需家用體脂計 |
| 小腿圍 (Calf Circumference) | cm | 20-50 | 每月 | 捲尺測量 |
| 握力 (Grip Strength) | kg | 5-60 | 每月 | 需握力計 |

**MNA-SF 簡化量表** (6 題):
1. 過去 3 個月食慾下降?  (0-2 分)
2. 過去 3 個月體重減輕? (0-3 分)
3. 行動能力? (0-2 分)
4. 過去 3 個月有壓力或急性疾病? (0-2 分)
5. 神經心理問題? (0-2 分)
6. BMI? (0-3 分)

**總分**: 0-14 分
- **12-14 分**: 營養正常
- **8-11 分**: 營養不良風險
- **0-7 分**: 營養不良

**允收標準** (UAT):
1. 治療師可為病患輸入 4 項營養測量數據
2. 病患可透過 LIFF 完成 MNA-SF 量表
3. Dashboard 顯示營養風險分級與趨勢圖
4. 營養風險 < 8 分時自動標註警示

#### 延後決策說明 ⭐

**決策時間**：2025-10-24（Sprint 3 規劃階段）

**延後理由**（基於 Linus 式實用主義評估）：
1. **需求不明確**：
   - MNA-SF 量表細節未最終確認
   - 營養風險權重計算邏輯待定
   - 4 項指標中，肌肉質量、握力需要特殊設備（體脂計、握力計）

2. **外部依賴**：
   - 握力計、體脂計等設備採購流程未完成
   - 客戶確認待辦事項未回覆（參見 7.5 節）

3. **優先級調整**：
   - Sprint 3-4 聚焦核心 COPD 管理功能（問卷、GOLD ABE 風險評估）
   - 營養評估為「輔助功能」，非 MVP 關鍵路徑

4. **技術債風險**：
   - 避免在需求不明確時投入 56h，導致後續大幅重構

**Linus 語錄適用**:
> "This is solving a problem we don't have yet."
> （這是在解決我們尚未遇到的問題）

**實用性檢驗失敗**：
- ❌ 真實問題？客戶未明確要求，僅為「期望」
- ❌ 可行性？缺乏設備支持，無法實際測量
- ❌ ROI？56h 投入 vs 不確定的業務價值

#### 原規劃整合細節（保留供 Phase 2 參考）
**Sprint 3 新增模組** (原規劃 WBS v3.0 Section 5.5，**已延後**):
- **5.5.1** 營養測量數據 API (16h)
  - GET/POST `/patients/{id}/nutrition-measurements`
  - 支持 4 項指標 CRUD
  - 數據驗證 (Pydantic)
- **5.5.2** 營養量表 API (12h)
  - POST `/patients/{id}/mna-sf`
  - 自動計算總分與風險分級
  - 歷史紀錄查詢
- **5.5.3** Dashboard 營養輸入介面 (12h)
  - 表單: 4 項指標輸入
  - 趨勢圖: 體重、肌肉量折線圖
  - 風險標籤: 紅/黃/綠燈
- **5.5.4** 營養風險計算整合 (8h)
  - 風險引擎整合 MNA-SF 分數
  - Dashboard 風險總覽新增「營養風險」欄位
- **5.5.5** LIFF 營養趨勢顯示 (8h)
  - 病患端: 體重趨勢圖
  - 病患端: MNA-SF 量表填寫介面

**資料庫影響**:
- 新增表: `nutrition_measurements` (16 欄位)
- 新增表: `mna_sf_records` (10 欄位)
- 詳見 database/schema_design_v1.0.md Section 3.6

**API 新增端點**:
```
POST   /patients/{id}/nutrition-measurements
GET    /patients/{id}/nutrition-measurements
POST   /patients/{id}/mna-sf
GET    /patients/{id}/mna-sf/latest
```

---

### 7.5 客戶確認待辦事項

| 待確認事項 | 負責人 | 截止日期 | 狀態 | 備註 |
|-----------|--------|---------|------|------|
| CR-001 驗證規則閾值是否符合臨床實務？ | 客戶 (治療師) | 2025-10-25 | ⏳ 待確認 | **已交付** Sprint 2，可依回饋調整 |
| ~~CR-002 拒絕決策是否接受？或有其他考量？~~ | 客戶 (產品負責人) | ~~2025-10-22~~ | ✅ **已完成** | **已接受並交付** Sprint 3 (TTS) |
| CR-003 延後決策是否接受？Phase 2 時程？ ⭐ | 客戶 (產品負責人) | 2025-11-01 | ⏳ 待確認 | **已延後**，等待客戶確認 Phase 2 需求 |
| 握力計、體脂計等設備由誰提供？ | 客戶 (採購部門) | 2025-11-15 | ⏳ 待確認 | **依賴 CR-003 決策**，若重啟則需確認 |
| CR-003 MNA-SF 量表詳細評分規則 ⭐ | 客戶 (營養師) | TBD | ⏳ 待確認 | **Phase 2 再議**，若重啟則需提供 |

---

### 7.6 技術債務與未來考量

**已知技術債務**:
1. **CR-001**: 驗證規則目前硬編碼在 Pydantic model，未來應支持「可配置驗證規則」
2. **CR-003**: MNA-SF 量表分數計算邏輯在 Python，未來若有複雜營養演算法應抽取為獨立 Rule Engine

**Phase 2+ 可能需求**:
- CR-002 若有數據支持，可納入語音互動 Roadmap
- CR-003 擴展: MUST 量表、營養計劃推薦 AI

---

### 7.7 設計原則遵循 (Linus Philosophy Check)

**Good Taste**: 
- ✅ CR-001 驗證規則使用 Pydantic Validators，消除 if/else 特殊判斷
- ✅ CR-003 避免 8 種營養量表，只實現最簡化的 MNA-SF

**Never Break Userspace**:
- ✅ 所有新增功能為「增量」，不影響現有 API 契約
- ✅ CR-001 warnings 欄位為可選，舊客戶端忽略不影響

**Practicality Beats Purity**:
- ✅ 拒絕 CR-002 因為「實用性檢驗失敗」
- ✅ CR-003 簡化版避免生化指標等難以取得的數據

**Simplicity**:
- ✅ CR-001 只有 5 個驗證規則，不做複雜的「動態規則引擎」
- ✅ CR-003 只追蹤 4 個指標，不做「完整營養檔案」

---

**v3.0 更新總結** ⭐ **已更新實際成果**:

本次客戶需求整合遵循 Linus 式務實主義：

**決策結果**:
- ✅ **CR-001 病患資料驗證**：接受 → **Sprint 2 完成** (10h)
- ✅ **CR-002 TTS 無障礙設計**：接受（需求澄清後）→ **Sprint 3 完成** (8h)
- ⏸ **CR-003 營養評估**：延後至 MVP 後（Phase 2）- 需求不明確

**實際工時影響**:
- **原估**: +90h（CR-001: 10h + CR-002: 24h + CR-003: 56h）
- **實際**: +18h（CR-001: 10h + CR-002: 8h + CR-003: 延後）
- **節省**: 72h（主要來自 CR-002 簡化與 CR-003 延後）

**Linus 式原則驗證**:
- ✅ **Good Taste**: CR-002 從複雜 STT 簡化為輕量 TTS（8h vs 128h）
- ✅ **Practicality Beats Purity**: CR-003 延後避免過度設計（56h 技術債風險）
- ✅ **Simplicity**: 所有交付功能保持最簡實現，無過度工程

**客戶溝通狀態**: 參見 7.5 節客戶確認待辦事項

