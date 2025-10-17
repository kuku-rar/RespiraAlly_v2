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
| **US-102** | **As a** 治療師,<br>**I want to** 使用帳號密碼登入儀表板,<br>**so that** 我可以管理我的個案。 | 1. 使用正確的帳密成功登入。<br>2. 登入失敗 3 次後帳號鎖定 15 分鐘。<br>3. 登入成功後取得 JWT。 | [Link to `../bdd/epic_100_authentication.feature`] |

### 📗 史詩 EP-200: 日常健康管理

| 使用者故事 ID | 描述 (As a, I want to, so that) | 核心允收標準 (UAT) | 連結至 BDD 文件 |
| :--- | :--- | :--- | :--- |
| **US-201** | **As a** 病患,<br>**I want to** 在 LIFF 快速填寫今日健康日誌,<br>**so that** 記錄我的健康狀況。 | 1. 每日只能新增一筆紀錄，但可更新。<br>2. 提交後觸發風險分數重新計算。<br>3. 輸入無效資料時應提示錯誤。 | [Link to `../bdd/epic_200_daily_management.feature`] |
| **US-202** | **As a** 病患,<br>**I want to** 查看近 7 日健康趨勢,<br>**so that** 了解我的短期進步。 | 1. 應以折線圖呈現。<br>2. 包含用藥、飲水、運動等系列。<br>3. 若無資料應顯示提示。 | [Link to `../bdd/epic_200_daily_management.feature`] |
| **US-205** | **As a** 病患,<br>**I want to** 查看近 30 日健康趨勢,<br>**so that** 了解我的長期變化。 | 1. 提供 7 日/30 日切換選項。<br>2. 30 日圖表應正確顯示數據。 | [Link to `../bdd/epic_200_daily_management.feature`] |


### 📙 史詩 EP-300: AI 語音互動

| 使用者故事 ID | 描述 (As a, I want to, so that) | 核心允收標準 (UAT) | 連結至 BDD 文件 |
| :--- | :--- | :--- | :--- |
| **US-301** | **As a** 病患,<br>**I want to** 用語音詢問健康問題,<br>**so that** 不需要打字。 | 1. 15 秒內收到文字與語音回覆。<br>2. 支援台語/國語辨識。<br>3. 對於無法辨識的音訊應有提示。 | [Link to `../bdd/epic_300_ai_interaction.feature`] |
| **US-302** | **As an** AI Worker,<br>**I want to** 處理語音任務佇列,<br>**so that** 不阻塞主服務。 | 1. 依序執行 STT, RAG, LLM, TTS。<br>2. 任何步驟失敗應有重試機制。<br>3. 最終結果透過 WebSocket 推送。 | [Link to `../bdd/epic_300_ai_interaction.feature`] |
| **US-303** | **As a** 病患,<br>**I want to** 讓 AI 回覆引用可信來源,<br>**so that** 我能增加信任感。 | 1. 回覆應附上參考資料連結。<br>2. 當 AI 回覆信心度低時，應提示使用者諮詢治療師。 | [Link to `../bdd/epic_300_ai_interaction.feature`] |

---

## 第 4 部分：範圍與限制 (Scope & Constraints)

| 區塊 | 內容 |
| :--- | :--- |
| **功能性需求 (In Scope)** | - **病患端**: LINE 註冊/登入、LIFF 日誌與問卷、AI 語音對話、個人健康趨勢。<br>- **治療師端**: Web Dashboard 登入、病患列表、個案 360° 檔案、風險預警、任務管理。 |
| **非功能性需求 (NFRs)** | - **性能**: API P95 < 500ms，AI 語音回覆 < 15 秒。<br>- **安全性**: RBAC 權限控制、敏感資料加密。<br>- **可用性**: 服務可用性 ≥99.5%。 |
| **不做什麼 (Out of Scope)** | - 不支援生理感測裝置（如血氧機）整合。<br>- 不支援跨院資料交換（FHIR/HL7）。<br>- 不開發原生 iOS/Android App。 |
| **假設與依賴** | - **假設**: 目標使用者皆熟悉 LINE 基本操作。<br>- **依賴**: 專案依賴 LINE Platform、LLM Provider（如 OpenAI）等外部服務。 |

---

## 第 5 部分：待辦問題與決策 (Open Questions & Decisions)

| 問題/決策 ID | 描述 | 狀態 | 參考 |
| :--- | :--- | :--- | :--- |
| **D-001** | 決定採用 FastAPI 作為後端框架，以支援異步與高效能需求。 | [已決定] | [ADR-001](./adr/ADR-001-fastapi-vs-flask.md) |
| **D-002** | 決定採用 pgvector 作為初期向量庫，以簡化 MVP 架構。 | [已決定] | [ADR-002](./adr/ADR-002-pgvector-for-vector-db.md) |
| **D-003** | 決定採用 MongoDB 儲存事件日誌，以應對靈活的 Schema 變更。 | [已決定] | [ADR-003](./adr/ADR-003-mongodb-for-event-logs.md) |
| **D-004** | 決定採用 LINE 作為唯一的病患互動入口，以降低使用門檻。 | [已決定] | [ADR-004](./adr/ADR-004-line-as-patient-entrypoint.md) |
| **D-005** | 決定採用 RabbitMQ 作為異步任務的訊息佇列。 | [已決定] | [ADR-005](./adr/ADR-005-rabbitmq-for-message-queue.md) |
| **Q-001** | `ai-worker` 中使用的 STT/LLM/TTS 服務是外部 API 還是內部模型？其規格與限制為何？ | [待釐清] | - |
