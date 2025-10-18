# 產品需求文件 (Product Requirements Document) - RespiraAlly V2.0

---

**文件版本 (Document Version):** `v2.0`
**最後更新 (Last Updated):** `2025-10-17`
**主要作者 (Lead Author):** `Claude Code AI`
**狀態 (Status):** `草稿 (Draft)`

---

## 目錄 (Table of Contents)

1.  [專案總覽 (Project Overview)](#第-1-部分專案總覽-project-overview)
2.  [商業目標 (Business Objectives) - 「為何做？」](#第-2-部分商業目標-business-objectives---為何做)
3.  [使用者故事與允收標準 (User Stories & UAT) - 「做什麼？」](#第-3-部分使用者故事與允收標準-user-stories--uat---做什麼)
4.  [範圍與限制 (Scope & Constraints)](#第-4-部分範圍與限制-scope--constraints)
5.  [待辦問題與決策 (Open Questions & Decisions)](#第-5-部分待辦問題與決策-open-questions--decisions)

---

**目的**: 本文件旨在為 `RespiraAlly V2.0` 專案定義其「為何」、「為誰」與「做什麼」，作為所有後續設計、開發與測試工作的唯一事實來源 (Single Source of Truth)，並與敏捷開發流程中的各個產出保持同步。

---

## 第 1 部分：專案總覽 (Project Overview)

| 區塊 | 內容 |
| :--- | :--- |
| **專案名稱** | RespiraAlly V2.0 |
| **狀態** | 開發中 (In Development) |
| **目標發布日期** | 2026 Q1 |
| **核心團隊** | PM: [TBD]<br>Lead Engineer: [TBD]<br>UX Designer: [TBD] |

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
| **US-101** | **As a** 新病患,<br>**I want to** 透過 LINE 快速註冊,<br>**so that** 無需額外下載 App。 | 1. 成功使用 LINE User ID 註冊。<br>2. 註冊成功後綁定預設 Rich Menu。<br>3. 重複註冊時顯示錯誤訊息。 | [Link to `../bdd/epic_100_authentication.feature`] |
| **US-103** | **As a** 新病患,<br>**I want to** 在初次註冊時填寫基本健康資料（身高、體重、醫院病歷號、吸菸史）,<br>**so that** 系統能計算 BMI 與風險評估。 | 1. 支援輸入身高 (50-250 cm)、體重 (20-300 kg)。<br>2. 醫院病歷號為選填。<br>3. 吸菸史包含狀態（從未/曾經/目前）與年數。<br>4. 系統自動計算 BMI 並分級 (過輕/正常/過重/肥胖)。 | [Link to `../bdd/epic_100_authentication.feature`] |
| **US-102** | **As a** 治療師,<br>**I want to** 使用帳號密碼登入儀表板,<br>**so that** 我可以管理我的個案。 | 1. 使用正確的帳密成功登入。<br>2. 登入失敗 3 次後帳號鎖定 15 分鐘。<br>3. 登入成功後取得 JWT。 | [Link to `../bdd/epic_100_authentication.feature`] |

### 📗 史詩 EP-200: 日常健康管理

| 使用者故事 ID | 描述 (As a, I want to, so that) | 核心允收標準 (UAT) | 連結至 BDD 文件 |
| :--- | :--- | :--- | :--- |
| **US-201** | **As a** 病患,<br>**I want to** 在 LIFF 快速填寫今日健康日誌,<br>**so that** 記錄我的健康狀況。 | 1. 每日只能新增一筆紀錄，但可更新。<br>2. 提交後觸發風險分數重新計算。<br>3. 輸入無效資料時應提示錯誤。 | [Link to `../bdd/epic_200_daily_management.feature`] |
| **US-202** | **As a** 病患,<br>**I want to** 查看近 7 日健康趨勢,<br>**so that** 了解我的短期進步。 | 1. 應以折線圖呈現。<br>2. 包含用藥、飲水、運動等系列。<br>3. 若無資料應顯示提示。<br>4. 支援顯示移動平均線平滑曲線。 | [Link to `../bdd/epic_200_daily_management.feature`] |
| **US-203** | **As a** 病患,<br>**I want to** 查看我的核心健康 KPI（依從率、飲水量、運動量、問卷分數）,<br>**so that** 快速了解整體健康狀況。 | 1. KPI 資料從快取表讀取，查詢時間 < 50ms。<br>2. 包含 7 日與 30 日依從率對比。<br>3. 顯示最新 CAT/mMRC 問卷分數與日期。<br>4. 顯示最新風險等級。 | [Link to `../bdd/epic_200_daily_management.feature`] |
| **US-205** | **As a** 病患,<br>**I want to** 查看近 30 日健康趨勢,<br>**so that** 了解我的長期變化。 | 1. 提供 7 日/30 日切換選項。<br>2. 30 日圖表應正確顯示數據。<br>3. 支援顯示累積統計（總日誌數、總用藥次數）。 | [Link to `../bdd/epic_200_daily_management.feature`] |


### 📙 史詩 EP-300: AI 語音互動

| 使用者故事 ID | 描述 (As a, I want to, so that) | 核心允收標準 (UAT) | 連結至 BDD 文件 |
| :--- | :--- | :--- | :--- |
| **US-301** | **As a** 病患,<br>**I want to** 用語音詢問健康問題,<br>**so that** 不需要打字。 | 1. 15 秒內收到文字與語音回覆。<br>2. 支援台語/國語辨識。<br>3. 對於無法辨識的音訊應有提示。 | [Link to `../bdd/epic_300_ai_interaction.feature`] |
| **US-302** | **As an** AI Worker,<br>**I want to** 處理語音任務佇列,<br>**so that** 不阻塞主服務。 | 1. 依序執行 STT, RAG, LLM, TTS。<br>2. 任何步驟失敗應有重試機制。<br>3. 最終結果透過 WebSocket 推送。 | [Link to `../bdd/epic_300_ai_interaction.feature`] |
| **US-303** | **As a** 病患,<br>**I want to** 讓 AI 回覆引用可信來源,<br>**so that** 我能增加信任感。 | 1. 回覆應附上參考資料連結。<br>2. 當 AI 回覆信心度低時，應提示使用者諮詢治療師。 | [Link to `../bdd/epic_300_ai_interaction.feature`] |

---

## 第 4 部分：範圍與限制 (Scope & Constraints)

### 4.1 MVP 分階段交付策略 (Phased MVP Delivery)

基於架構審視報告 ([ARCHITECTURE_REVIEW.md](./ARCHITECTURE_REVIEW.md))，為避免過度設計並加速市場驗證，我們採用**分階段漸進式 MVP** 策略：

| 階段 | 時程 | 核心功能 | 成功標準 | 技術重點 |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 0: 核心驗證** | Week 1-4 | - 治療師登入<br>- 病患 LINE 註冊<br>- 每日健康日誌提交<br>- 病患列表查看<br>- 基礎依從率計算 | - 5 位治療師試用<br>- 20 位病患持續 14 天記錄<br>- 依從率 ≥60% | - Modular Monolith<br>- PostgreSQL + Redis<br>- 簡化 API 設計 |
| **Phase 1: 增值功能** | Week 5-8 | - CAT/mMRC 問卷<br>- 風險評分引擎<br>- 異常預警<br>- 智慧提醒 (12:00/17:00/20:00) | - 風險預警準確率 ≥80%<br>- 提醒點擊率 ≥30% | - 規則引擎<br>- APScheduler<br>- LINE Push API |
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
| **不做什麼 (Out of Scope)** | - **V2.0 不支援**: 生理感測裝置整合、跨院資料交換（FHIR/HL7）、原生 iOS/Android App、治療師之間的協作功能、多語言國際化（僅支援繁體中文）。<br>- **技術限制**: MVP 階段不使用 Kubernetes、不自建 LLM 模型、不使用 Kafka（使用 RabbitMQ 替代）。 |
| **假設與依賴** | - **假設**: 目標使用者（長者）皆熟悉 LINE 基本操作、治療師具備基本電腦操作能力、病患願意每日花費 2-3 分鐘記錄健康日誌。<br>- **外部依賴**: LINE Platform（病患唯一入口）、OpenAI API（STT/LLM/TTS）、Zeabur（PaaS 部署平台）。<br>- **內部依賴**: PostgreSQL ≥15、Redis ≥7、Python ≥3.11、Node.js ≥18。 |

---

## 第 5 部分：待辦問題與決策 (Open Questions & Decisions)

| 問題/決策 ID | 描述 | 狀態 | 參考 |
| :--- | :--- | :--- | :--- |
| **D-001** | 決定採用 FastAPI 作為後端框架，以支援異步與高效能需求。 | [已決定] | [ADR-001](./adr/ADR-001-fastapi-vs-flask.md) |
| **D-002** | 決定採用 pgvector 作為初期向量庫，以簡化 MVP 架構。 | [已決定] | [ADR-002](./adr/ADR-002-pgvector-for-vector-db.md) |
| **D-003** | ~~決定採用 MongoDB 儲存事件日誌~~ **已廢棄** - 改用 PostgreSQL JSONB 欄位儲存事件日誌，簡化技術棧。 | [已變更] | [ARCHITECTURE_REVIEW.md - 簡化技術棧](./DATABASE_SCHEMA_DESIGN.md#34-事件與通知表) |
| **D-004** | 決定採用 LINE 作為唯一的病患互動入口，以降低使用門檻。 | [已決定] | [ADR-004](./adr/ADR-004-line-as-patient-entrypoint.md) |
| **D-005** | 決定採用 RabbitMQ 作為異步任務的訊息佇列。 | [已決定] | [ADR-005](./adr/ADR-005-rabbitmq-for-message-queue.md) |
| **Q-001** | `ai-worker` 中使用的 STT/LLM/TTS 服務是外部 API 還是內部模型？其規格與限制為何？ | [待釐清] | - |
