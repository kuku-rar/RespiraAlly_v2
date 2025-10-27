# RespiraAlly V2.0 整合性架構與設計文件

---

**文件版本:** v2.0
**最後更新:** 2025-10-27
**主要作者:** Claude Code AI - System Architect
**狀態:** 審核中 (Under Review)

---

## 1. 架構概述 (Architecture Overview)

### 1.1 系統背景與目標
- **問題域**: 本系統旨在解決慢性阻塞性肺病（COPD）患者在長期自我管理中面臨的挑戰，包括記錄繁瑣、缺乏即時回饋、衛教個人化不足等問題。同時，也致力於改善呼吸治療師的工作流程，解決其資料分散、風險追蹤耗時的痛點。
- **關鍵驅動力**:
  - **業務驅動力**: 提升 COPD 病患的健康行為依從率至 75% 以上，降低醫療機構的慢病管理成本與急診率。
  - **技術驅動力**: 從 V1 的 Flask 單體架構遷移至 FastAPI **Modular Monolith 架構**（未來可演進為微服務），引入 AI 語音互動、RAG 知識庫、事件驅動等現代技術，解決 V1 的技術債與擴展性問題。
  - **品質驅動力**: 追求高可用性 (99.5%)、高效能 (API P95 < 500ms)、高安全性和合規性 (符合台灣個資法)。

### 1.2 Phase-Sprint 開發階段映射

為確保文件術語一致性，本系統採用以下 Phase-Sprint 對應關係（詳見 [02_product_requirements_document.md](./02_product_requirements_document.md) Section 4.1）：

| Phase | 時程 | Sprint | 核心功能 | 狀態 |
|-------|------|--------|----------|------|
| **Phase 0: 核心驗證** | Week 1-4 | Sprint 0-2 | 專案管理、基礎設施、病患管理 | ⚡ 85.9% |
| **Phase 1: 增值功能** | Week 5-8 | Sprint 3-4 | 問卷系統、GOLD ABE 風險引擎 | 🔄 83.2% |
| **Phase 2: AI 能力** | Week 9-12 | Sprint 5-6 | RAG 知識庫、AI 語音互動 | ⏳ 計劃中 |
| **Phase 3: 優化上線** | Week 13-16 | Sprint 7-8 | 通知系統、效能優化、生產部署 | ⏳ 計劃中 |

**當前進度**: Sprint 4 (Phase 1) - GOLD ABE 風險引擎開發中 (66.4%)

### 1.3 利益相關者與關注點
| 角色 | 關注點 | 優先級 |
|---|---|---|
| COPD 病患 | 功能易用性、互動即時性、隱私安全 | 高 |
| 呼吸治療師 | 工作效率、風險預警準確性、個案資料完整性 | 高 |
| 產品經理 | 功能完整性、北極星指標達成率、上線時程 | 高 |
| 開發團隊 | 可維護性、技術棧現代化、CI/CD 效率 | 高 |
| 運維團隊 | 可部署性、可監控性、系統穩定性 | 中 |
| 法務合規 | 個資法合規、醫療資訊安全 | 高 |

### 1.3 品質屬性權衡 (Quality Attributes)

| 品質屬性 | 目標 | 度量方式 | 優先級 | 權衡考量 |
|---|---|---|---|---|
| **可用性 (Availability)** | ≥99.5% uptime | Prometheus 監控 | P0 | vs 成本 (初期接受部分單點) |
| **性能 (Performance)** | API P95 < 500ms | Prometheus 監控 | P0 | vs 開發速度 (關鍵路徑優先優化) |
| **安全性 (Security)** | 零資料洩露 | 滲透測試、日誌稽核 | P0 | vs 易用性 (兼顧便利與安全) |
| **可維護性 (Maintainability)** | 新功能交付 < 2週 | Lead Time | P1 | vs 性能 (採用 Clean Arch) |
| **擴展性 (Scalability)** | 支援 500 CCU | 負載測試 (Locust) | P1 | vs 複雜度 (MVP 後再引入 K8s) |

**關鍵權衡決策**:
- **性能 vs 可維護性**: 選擇 Clean Architecture + 微服務，犧牲少量初始開發速度與性能，換取長期可維護性與團隊並行開發能力。
- **一致性 vs 可用性**: 核心交易（如問卷提交）採強一致性，非核心資料（如事件日誌）採最終一致性。
- **成本 vs 可用性**: MVP 階段部署於 Zeabur，接受部分元件單點故障風險 (如 RabbitMQ)，上線後再遷移至高可用的 K8s 叢集。


### 1.4 架構模式選擇 (Architecture Pattern Selection)

#### 1.4.1 選定模式: Modular Monolith + Event-Driven Architecture

**核心決策**: MVP 階段採用 **Modular Monolith (模組化單體)** 架構，並引入 **事件驅動 (Event-Driven)** 通信機制實現模組間解耦。

#### 1.4.2 選擇理由 (Rationale)

| 考量維度 | Modular Monolith | 微服務架構 | 決策 |
|---------|------------------|-----------|------|
| **開發複雜度** | 低（單一代碼庫，統一部署） | 高（多服務協調，分散式除錯困難） | ✅ Modular Monolith |
| **團隊規模** | 3-5 人小團隊，適合單體 | 需多個獨立團隊 | ✅ Modular Monolith |
| **部署複雜度** | 簡單（單一容器） | 複雜（需 K8s 等編排工具） | ✅ Modular Monolith |
| **性能** | 優秀（本地函數調用） | 需網絡開銷 | ✅ Modular Monolith |
| **可維護性** | 需嚴格模組邊界 | 天然隔離 | ⚖️ 通過 Clean Arch 保證 |
| **擴展性** | 整體擴展，資源利用率較低 | 服務級擴展 | ⚠️ MVP 可接受 |

#### 1.4.3 為何引入事件驅動？

雖然採用單體架構，但仍引入事件驅動機制的原因：

1. **模組解耦**: 避免模組間直接依賴，降低耦合度
   ```python
   # ❌ 不好的設計（直接依賴）
   from risk_module import RiskService
   risk_service.calculate_risk(patient_id)  # daily_log 直接依賴 risk

   # ✅ 好的設計（事件驅動）
   event_bus.publish(DailyLogSubmitted(patient_id, data))  # 發布事件，無需知道誰消費
   ```

2. **未來可拆分**: 保留未來拆分為微服務的可能性
   - 事件驅動的模組邊界清晰，拆分時只需將 Event Bus 從 in-memory 改為 RabbitMQ
   - 無需大規模重構業務邏輯

3. **異步處理**: 非關鍵路徑的任務（如 AI 分析、通知）可異步執行，提升響應速度

4. **可審計性**: Event Store 記錄所有領域事件，便於追蹤與審計

#### 1.4.4 演進路線 (Evolution Path)

```mermaid
graph LR
    A[V2.0 MVP<br/>Modular Monolith<br/>+ In-Memory Event Bus]
    B[V2.5 擴展期<br/>Modular Monolith<br/>+ RabbitMQ]
    C[V3.0 成熟期<br/>Selective Microservices<br/>+ Message Queue]

    A -->|流量增長<br/>事件可靠性需求| B
    B -->|明確服務邊界<br/>團隊擴張| C

    style A fill:#90EE90
    style B fill:#FFD700
    style C fill:#87CEEB
```

**演進觸發條件**:
- **V2.0 → V2.5**: 當單機無法支撐流量，或需保證事件不丟失時
- **V2.5 → V3.0**: 當團隊擴張至 10+ 人，或某模組需要獨立擴展時

#### 1.4.5 相關 ADR

詳細決策過程參見：
- [Modular Monolith 設計 (詳見 Section 4.1)](#41-modular-monolith-模組邊界劃分)
- [ADR-005: 使用 RabbitMQ 作為消息中間件](./adr/ADR-005-rabbitmq-for-message-queue.md)

---

---

## 2. C4 模型 - 多層次視圖

### 2.1 Level 1: 系統上下文圖 (System Context)

```mermaid
C4Context
    title RespiraAlly 系統上下文圖

    Person(patient, "病患", "COPD 患者，透過 LINE 互動")
    Person(therapist, "治療師", "呼吸治療師，使用 Web 管理")
    
    System_Boundary(respira, "RespiraAlly 系統") {
        System(line, "LINE Bot/LIFF", "患者互動入口")
        System(dashboard, "Web Dashboard", "醫護管理後臺")
        System(api, "核心服務 API", "FastAPI, 處理業務邏輯")
        System(ai, "AI Worker", "語音/RAG 處理")
    }
    
    System_Ext(line_platform, "LINE Platform", "提供訊息、登入、LIFF 服務")
    System_Ext(llm_provider, "LLM Provider", "提供大型語言模型推理能力")
    
    Rel(patient, line, "使用", "HTTPS")
    Rel(therapist, dashboard, "管理", "HTTPS")
    Rel(line, api, "發送請求")
    Rel(dashboard, api, "發送請求")
    Rel(api, ai, "分派任務")
    
    Rel_Back(line, line_platform, "接收 Webhook")
    Rel(ai, llm_provider, "調用 API")
```
**外部系統依賴分析**:
- **LINE Platform**: 高依賴，是病患唯一入口。需設計降級訊息與監控其服務狀態。
- **LLM Provider**: 中依賴，AI 互動核心。可降級為罐頭回覆或提示服務不可用，並設計可抽換不同 LLM Provider 的適配層。

### 2.2 Level 2: 容器圖 (Container Diagram)

**🎯 MVP 策略變更說明**: 基於 [架構審視報告](./05_architecture_and_design.md) 的建議，**MVP 階段採用 Modular Monolith** 而非微服務架構，以降低複雜度、加速交付並便於除錯。未來可根據實際業務需求逐步拆分為微服務。

```mermaid
C4Container
    title RespiraAlly 容器圖 (Modular Monolith - MVP)

    Person(patient, "病患", "COPD 患者")
    Person(therapist, "治療師", "呼吸治療師")

    System_Boundary(line_liff, "LINE Client") {
        Container(line_app, "LINE App", "iOS/Android App")
    }

    System_Boundary(browser, "Browser") {
        Container(dashboard_spa, "Dashboard SPA", "React, Next.js", "治療師管理介面")
    }

    System_Boundary(respira_backend, "RespiraAlly Backend (on Zeabur)") {
        Container(main_app, "主應用服務", "FastAPI (Modular Monolith)", "包含所有業務模組:<br/>- auth (認證授權)<br/>- patients (個案管理)<br/>- daily_logs (日誌服務)<br/>- risk_engine (風險引擎)<br/>- rag (知識檢索)<br/>- notifications (通知排程)")

        Container(ai_worker, "AI Worker", "Python (可選)", "STT, LLM, TTS 任務處理<br/>(Phase 2 引入)")

        ContainerDb(postgres_db, "PostgreSQL 15+", "含 pgvector 擴展", "- 結構化資料<br/>- 向量資料<br/>- 事件日誌 (JSONB)")
        ContainerDb(redis, "Redis 7+", "Cache & Session", "- 會話存儲<br/>- 快取層<br/>- 分散式鎖")
        ContainerDb(minio, "MinIO", "Object Storage", "音檔存儲<br/>(Phase 2 引入)")
        Container(rabbitmq, "RabbitMQ", "Message Queue (可選)", "AI 異步任務<br/>(Phase 2 引入)")
    }

    System_Ext(line_platform, "LINE Platform", "OAuth, Messaging API")
    System_Ext(openai_api, "OpenAI API", "GPT-4, Whisper, TTS")

    Rel(patient, line_app, "使用")
    Rel(therapist, dashboard_spa, "使用")

    Rel(line_app, main_app, "API 呼叫", "HTTPS/REST")
    Rel(dashboard_spa, main_app, "API 呼叫", "HTTPS/REST")

    Rel(main_app, postgres_db, "讀寫", "SQLAlchemy ORM")
    Rel(main_app, redis, "讀寫", "Redis Client")

    Rel(main_app, rabbitmq, "發布任務", "Pika")
    Rel(rabbitmq, ai_worker, "消費任務")
    Rel(ai_worker, postgres_db, "讀寫")
    Rel(ai_worker, minio, "讀寫音檔")
    Rel(ai_worker, openai_api, "調用 API")

    Rel(main_app, line_platform, "OAuth & Push", "HTTPS")
    Rel(main_app, openai_api, "Embedding API", "HTTPS")
```

**容器職責與技術選型理由**:

| 容器 | 技術選型 | 核心職責 | 選型理由 |
|------|----------|----------|----------|
| **主應用服務 (Modular Monolith)** | FastAPI | - 統一 API 入口<br/>- 認證授權 (JWT, LINE OAuth)<br/>- 所有業務邏輯 (患者、日誌、風險、RAG、通知) | - **簡化架構**: 單一 Process，避免分散式事務<br/>- **加速開發**: 直接函數調用，無需 RPC<br/>- **易於除錯**: 統一日誌、單一部署單元<br/>- **保留演進性**: 模組邊界清晰，未來可拆分 |
| **AI Worker** | Python | - 語音轉文字 (STT)<br/>- LLM 推理<br/>- 文字轉語音 (TTS) | - **Phase 2 引入**: Phase 0/1 暫不實作<br/>- **異步處理**: 避免阻塞主服務<br/>- **可選 RabbitMQ**: 初期可用 Celery + Redis 替代 |
| **PostgreSQL** | PostgreSQL 15 + pgvector | - 所有結構化資料<br/>- 向量資料 (衛教知識庫)<br/>- 事件日誌 (JSONB 欄位) | - **單一數據源**: 移除 MongoDB，簡化技術棧<br/>- **JSONB 強大**: 支援靈活 Schema，可替代 MongoDB<br/>- **pgvector 足夠**: MVP 階段向量量 < 10萬，性能足夠 |
| **Redis** | Redis 7 | - 會話存儲 (JWT Refresh Token)<br/>- 熱點數據快取<br/>- 分散式鎖 (登入失敗計數) | - **高性能**: 毫秒級讀寫<br/>- **豐富數據結構**: String, Hash, Set, ZSet<br/>- **持久化支援**: AOF + RDB |
| **RabbitMQ** | RabbitMQ 3 | - AI 語音任務佇列 | - **可選元件**: Phase 0/1 不引入<br/>- **備選方案**: Celery + Redis 或同步 API |

**🔄 演進路徑**:
```
Phase 0/1 (Week 1-8):
  └── Modular Monolith (FastAPI) + PostgreSQL + Redis

Phase 2 (Week 9-12):
  └── 新增 AI Worker + (可選) RabbitMQ

Phase 3+ (未來):
  └── 根據瓶頸逐步拆分微服務
      ├── 候選 1: AI Worker → 獨立微服務
      ├── 候選 2: RAG Service → 獨立微服務 (若查詢量 > 1000 QPS)
      └── 候選 3: Notification Service → 獨立微服務 (若推播量過大)
```

### 2.3 Level 3: 組件圖 (Component Diagram) - 以日誌服務為例

```mermaid
C4Component
    title 日誌服務 (Log Service) - 組件圖

    Container_Boundary(log_svc, "日誌服務") {
        Component(api, "API 層", "FastAPI Routers", "接收日誌/問卷 HTTP 請求")
        Component(app, "應用層", "Use Cases", "編排日誌提交、查詢用例")
        Component(domain, "領域層", "Entities, Aggregates", "日誌、依從率等業務邏輯")
        Component(infra, "基礎設施層", "Repositories, Adapters", "數據持久化, 事件發布")
    }

    ContainerDb(db, "PostgreSQL", "日誌、問卷資料")
    Container(mq, "RabbitMQ", "訊息佇列")
    System_Ext(risk_engine, "風險引擎")

    Rel(api, app, "調用", "方法調用")
    Rel(app, domain, "使用", "方法調用")
    Rel(domain, infra, "依賴反轉", "接口")
    Rel(infra, db, "讀寫", "SQLAlchemy")
    Rel(app, mq, "發布 `daily_log.submitted` 事件", "AMQP")
    Rel(mq, risk_engine, "訂閱事件")
```

---

## 3. DDD 戰略設計 (Strategic Design)

本章節基於 Domain-Driven Design (DDD) 戰略設計原則，定義 RespiraAlly V2.0 的領域邊界、統一語言與聚合模型，確保業務邏輯與技術實現的高內聚、低耦合。

---

### 3.1 界限上下文映射 (Bounded Context Mapping)

界限上下文 (Bounded Context) 是 DDD 中定義領域邊界的核心概念。每個上下文內維護自己的模型與術語，上下文間透過明確的關係進行協作。

#### 3.1.1 上下文全景圖 (Context Map)

```mermaid
graph TD
  subgraph "核心域 (Core Domain)"
    LogContext[日誌上下文<br/>Daily Log Context<br/>📌 核心業務]
    RiskContext[風險上下文<br/>Risk Context<br/>📌 核心業務]
  end

  subgraph "支撐子域 (Supporting Subdomain)"
    PatientContext[個案上下文<br/>Patient Context<br/>🔧 支撐功能]
    SurveyContext[問卷上下文<br/>Survey Context<br/>🔧 支撐功能]
    RagContext[衛教上下文<br/>RAG Context<br/>🔧 支撐功能]
  end

  subgraph "通用子域 (Generic Subdomain)"
    AuthContext[認證上下文<br/>Auth Context<br/>⚙️ 通用功能]
    NotificationContext[通知上下文<br/>Notification Context<br/>⚙️ 通用功能]
  end

  %% 核心域間關係
  RiskContext -->|Customer-Supplier<br/>依賴日誌數據| LogContext
  RiskContext -->|Customer-Supplier<br/>依賴個案檔案| PatientContext

  %% 支撐子域關係
  LogContext -->|Customer-Supplier<br/>驗證患者存在| PatientContext
  SurveyContext -->|Customer-Supplier<br/>驗證患者存在| PatientContext

  %% 核心域與支撐子域關係
  RiskContext -->|Partner<br/>共同計算風險| SurveyContext

  %% 與通用子域關係
  LogContext -->|Published Language<br/>發布 LogSubmitted 事件| NotificationContext
  RiskContext -->|Published Language<br/>發布 AlertTriggered 事件| NotificationContext
  RagContext -->|Open Host Service<br/>提供知識檢索 API| NotificationContext

  %% 認證上下文與所有上下文的關係
  AuthContext -.->|ACL<br/>提供身份驗證| LogContext
  AuthContext -.->|ACL<br/>提供身份驗證| PatientContext
  AuthContext -.->|ACL<br/>提供身份驗證| SurveyContext
  AuthContext -.->|ACL<br/>提供身份驗證| RiskContext

  style LogContext fill:#ff9999,stroke:#cc0000,stroke-width:3px
  style RiskContext fill:#ff9999,stroke:#cc0000,stroke-width:3px
  style PatientContext fill:#99ccff,stroke:#0066cc,stroke-width:2px
  style SurveyContext fill:#99ccff,stroke:#0066cc,stroke-width:2px
  style RagContext fill:#99ccff,stroke:#0066cc,stroke-width:2px
  style AuthContext fill:#99ff99,stroke:#009900,stroke-width:2px
  style NotificationContext fill:#99ff99,stroke:#009900,stroke-width:2px
```

#### 3.1.2 上下文詳細定義

##### 🔴 核心域 (Core Domain) - 競爭優勢所在

**1. 日誌上下文 (Daily Log Context)**

| 屬性 | 內容 |
|------|------|
| **職責** | 管理患者每日健康記錄，計算健康行為依從率 |
| **核心實體** | DailyLog (聚合根), MedicationRecord, WaterIntake, SymptomRecord |
| **關鍵業務規則** | - 每位患者每日僅一筆記錄<br/>- 依從率 = (7日內用藥天數 / 7) × 100%<br/>- 提交後觸發風險重新計算 |
| **對外 API** | - `POST /daily-logs` - 提交日誌<br/>- `GET /daily-logs/{patientId}` - 查詢歷史<br/>- `GET /daily-logs/{patientId}/trends` - 獲取趨勢圖數據 |
| **發布事件** | - `DailyLogSubmitted` - 日誌提交成功<br/>- `DailyLogUpdated` - 日誌更新 |
| **訂閱事件** | 無 (作為數據源頭) |
| **依賴上下文** | Patient Context (驗證 patient_id 存在) |

**2. 風險上下文 (Risk Context)**

| 屬性 | 內容 |
|------|------|
| **職責** | 評估患者健康風險，觸發異常預警，管理預警生命週期 |
| **核心實體** | RiskScore (聚合根), Alert (聚合根), RiskEngine (領域服務) |
| **關鍵業務規則** | - 風險分數計算公式: `Score = f(依從率, CAT分數, 症狀頻率, 年齡, 吸菸史)`<br/>- 風險等級: LOW (0-40), MEDIUM (41-70), HIGH (71-100)<br/>- Alert 觸發條件: 風險等級 >= MEDIUM 且較上次提升 |
| **對外 API** | - `POST /risk-scores/calculate/{patientId}` - 計算風險<br/>- `GET /alerts?therapistId=xxx&status=OPEN` - 查詢預警列表<br/>- `PATCH /alerts/{alertId}/acknowledge` - 確認預警 |
| **發布事件** | - `RiskScoreCalculated` - 風險評分完成<br/>- `AlertTriggered` - 觸發新預警<br/>- `AlertResolved` - 預警解決 |
| **訂閱事件** | - `DailyLogSubmitted` (來自 Log Context)<br/>- `SurveyCompleted` (來自 Survey Context) |
| **依賴上下文** | - Daily Log Context (讀取近期日誌)<br/>- Patient Context (讀取患者檔案)<br/>- Survey Context (讀取最新問卷分數) |

##### 🔵 支撐子域 (Supporting Subdomain) - 支撐核心業務

**3. 個案上下文 (Patient Context)**

| 屬性 | 內容 |
|------|------|
| **職責** | 管理患者檔案、治療師分配、個案基本資料 CRUD |
| **核心實體** | Patient (聚合根), PatientProfile, TherapistAssignment |
| **關鍵業務規則** | - 患者必須分配給一位治療師<br/>- BMI 自動計算: `weight_kg / (height_cm / 100)^2`<br/>- 年齡限制: 18-120 歲 |
| **對外 API** | - `POST /patients` - 新增患者<br/>- `GET /patients/{id}` - 查詢患者檔案<br/>- `PATCH /patients/{id}/assign-therapist` - 分配治療師 |
| **發布事件** | - `PatientRegistered` - 患者註冊成功<br/>- `PatientProfileUpdated` - 檔案更新<br/>- `TherapistAssigned` - 治療師分配 |
| **訂閱事件** | - `UserCreated` (來自 Auth Context) |
| **依賴上下文** | Auth Context (驗證 user_id 與 LINE User ID 綁定) |

**4. 問卷上下文 (Survey Context)**

| 屬性 | 內容 |
|------|------|
| **職責** | 管理 CAT/mMRC 問卷、計算評分、追蹤病情嚴重度 |
| **核心實體** | SurveyResponse (聚合根), CATScorer, mMRCScorer (領域服務) |
| **關鍵業務規則** | - **CAT 評分**: 0-40 分，<10=輕微, 10-20=中度, 21-30=嚴重, >30=極嚴重<br/>- **mMRC 評分**: 0-4 分，表示呼吸困難程度<br/>- 問卷提交後觸發風險重新計算 |
| **對外 API** | - `POST /surveys/{type}` - 提交問卷 (type: CAT/mMRC)<br/>- `GET /surveys/{patientId}/history` - 查詢歷史問卷<br/>- `GET /surveys/{patientId}/latest` - 獲取最新分數 |
| **發布事件** | - `SurveyCompleted` - 問卷完成<br/>- `SeverityLevelChanged` - 嚴重度變化 |
| **訂閱事件** | 無 |
| **依賴上下文** | Patient Context (驗證 patient_id 存在) |

**5. 衛教上下文 (RAG Context)**

| 屬性 | 內容 |
|------|------|
| **職責** | 管理衛教知識庫、向量檢索、AI 語音問答 (STT → RAG → LLM → TTS) |
| **核心實體** | EducationalDocument (聚合根), DocumentChunk, EmbeddingService (領域服務) |
| **關鍵業務規則** | - 文件必須分塊 (每塊 ≤ 500 字)<br/>- 向量相似度檢索 Top-K=5<br/>- AI 回覆必須引用來源 (Citation) |
| **對外 API** | - `POST /rag/query` - 文字問答<br/>- `POST /rag/voice-query` - 語音問答 (異步)<br/>- `GET /rag/documents` - 查詢知識庫 |
| **發布事件** | - `VoiceQueryReceived` - 收到語音查詢<br/>- `VoiceResponseGenerated` - 語音回覆生成完成 |
| **訂閱事件** | 無 |
| **依賴上下文** | 無 (獨立上下文) |

##### 🟢 通用子域 (Generic Subdomain) - 可用現成方案

**6. 認證上下文 (Auth Context)**

| 屬性 | 內容 |
|------|------|
| **職責** | 用戶認證、授權、會話管理、登入鎖定策略 |
| **核心實體** | User (聚合根), Session, AccessToken (JWT), RefreshToken |
| **關鍵業務規則** | - **患者**: LINE OAuth 登入，無密碼<br/>- **治療師**: 帳密登入，登入失敗 3 次鎖定 15 分鐘<br/>- JWT 有效期: Access Token 1 小時, Refresh Token 7 天 |
| **對外 API** | - `POST /auth/line/callback` - LINE 登入回調<br/>- `POST /auth/therapist/login` - 治療師登入<br/>- `POST /auth/refresh` - 刷新 Token |
| **發布事件** | - `UserCreated` - 新用戶註冊<br/>- `UserLoggedIn` - 登入成功<br/>- `AccountLocked` - 帳號鎖定 |
| **訂閱事件** | 無 |
| **依賴上下文** | 無 (基礎服務) |

**7. 通知上下文 (Notification Context)**

| 屬性 | 內容 |
|------|------|
| **職責** | 管理通知排程、發送 LINE 訊息/Email、追蹤發送狀態 |
| **核心實體** | Notification (聚合根), NotificationSchedule, DeliveryStatus |
| **關鍵業務規則** | - 智慧提醒時段: 12:00, 17:00, 20:00<br/>- 通知失敗重試 3 次 (指數退避)<br/>- LINE 訊息擬人化口吻 (孫女語氣) |
| **對外 API** | - `POST /notifications/send` - 立即發送<br/>- `POST /notifications/schedule` - 排程發送<br/>- `GET /notifications/history/{userId}` - 查詢歷史 |
| **發布事件** | - `NotificationSent` - 通知發送成功<br/>- `NotificationFailed` - 發送失敗 |
| **訂閱事件** | - `DailyLogSubmitted` (觸發鼓勵訊息)<br/>- `AlertTriggered` (通知治療師)<br/>- `SurveyCompleted` (觸發感謝訊息) |
| **依賴上下文** | RAG Context (查詢衛教內容用於推播) |

---

#### 3.1.3 上下文間關係說明

**關係類型定義**:

1. **Customer-Supplier (客戶-供應商)**:
   - **定義**: 下游上下文 (Customer) 依賴上游上下文 (Supplier) 提供的數據或服務
   - **範例**: 風險上下文 → 日誌上下文 (風險計算需要日誌數據)
   - **實作**: 透過 REST API 或共享數據庫視圖

2. **Open Host Service (開放主機服務)**:
   - **定義**: 上下文提供公開的、文檔完善的 API 供其他上下文調用
   - **範例**: 衛教上下文提供知識檢索 API
   - **實作**: RESTful API + OpenAPI 規範

3. **Published Language (發布語言)**:
   - **定義**: 上下文透過領域事件進行異步通信，使用統一的事件 Schema
   - **範例**: 日誌上下文發布 `DailyLogSubmitted` 事件
   - **實作**: RabbitMQ + 事件版本化

4. **Anti-Corruption Layer (防腐層)**:
   - **定義**: 保護上下文不受外部系統變化影響的適配層
   - **範例**: 認證上下文 (ACL) 隔離 LINE Platform 變化
   - **實作**: Adapter Pattern

5. **Partner (合作夥伴)**:
   - **定義**: 兩個上下文緊密協作，共同實現業務目標
   - **範例**: 風險上下文 ↔ 問卷上下文 (共同計算風險)
   - **實作**: 同步 API 調用 + 共享事件

**關鍵關係矩陣**:

| 下游上下文 (Customer) | 上游上下文 (Supplier) | 關係類型 | 協作方式 |
|----------------------|---------------------|----------|----------|
| 風險上下文 | 日誌上下文 | Customer-Supplier | REST API (讀取近 30 日日誌) |
| 風險上下文 | 個案上下文 | Customer-Supplier | REST API (讀取患者檔案) |
| 風險上下文 | 問卷上下文 | Partner | REST API + Event (`SurveyCompleted`) |
| 日誌上下文 | 個案上下文 | Customer-Supplier | Database FK (驗證 patient_id) |
| 問卷上下文 | 個案上下文 | Customer-Supplier | Database FK (驗證 patient_id) |
| 通知上下文 | 衛教上下文 | Open Host Service | REST API (查詢衛教內容) |
| 通知上下文 | 日誌上下文 | Published Language | Event (`DailyLogSubmitted`) |
| 通知上下文 | 風險上下文 | Published Language | Event (`AlertTriggered`) |
| 所有上下文 | 認證上下文 | ACL | JWT Middleware (身份驗證) |

---

### 3.2 統一語言 (Ubiquitous Language)

統一語言 (Ubiquitous Language) 是 DDD 的核心實踐，確保開發團隊、領域專家、產品經理使用相同的術語描述業務概念，避免歧義與誤解。

#### 3.2.1 核心術語表

以下術語按照所屬上下文分類，並提供中英對照、精確定義與反例。

##### 🔴 認證上下文 (Auth Context)

| 術語 | 英文 | 定義 | 反例 / 注意事項 | 所屬上下文 |
|------|------|------|-----------------|-----------|
| 用戶 | User | 系統中的使用者實體，包含病患 (Patient) 與治療師 (Therapist) | ≠ 病患 (Patient 是 User 的子類型) | Auth Context |
| 角色 | Role | 用戶的身份類型，枚舉值: PATIENT 或 THERAPIST | ≠ 權限 (Role 決定權限，但不等於權限本身) | Auth Context |
| 訪問令牌 | Access Token | 短期 JWT，有效期 1 小時，用於 API 鑑權 | ≠ Refresh Token (後者用於刷新前者) | Auth Context |
| 刷新令牌 | Refresh Token | 長期 JWT，有效期 7 天，用於獲取新的 Access Token | 存儲在 Redis，單次使用後失效 (Rotation) | Auth Context |
| 帳號鎖定 | Account Lockout | 治療師登入失敗 3 次後鎖定 15 分鐘的安全機制 | 僅適用於治療師，患者無密碼登入故不適用 | Auth Context |
| LINE 用戶 ID | LINE User ID | LINE Platform 提供的唯一用戶識別碼，格式 `U{32 位十六進位}` | ≠ 系統內部 user_id (UUID) | Auth Context |

##### 🔴 個案上下文 (Patient Context)

| 術語 | 英文 | 定義 | 反例 / 注意事項 | 所屬上下文 |
|------|------|------|-----------------|-----------|
| 病患 | Patient | COPD 患者，透過 LINE 使用系統的使用者 | ≠ 治療師 (Therapist) | Patient Context |
| 治療師 | Therapist | 呼吸治療師，透過 Web Dashboard 管理病患的使用者 | ≠ 醫生 (本系統僅支援治療師角色) | Patient Context |
| 病患檔案 | Patient Profile | 病患的詳細資料，包含姓名、生日、身高體重、病歷號、吸菸史等 | ≠ User (User 僅包含認證資訊) | Patient Context |
| 病歷號 | Medical Record Number | 醫院提供的病患唯一識別碼，用於跨系統對接 | 選填欄位，未來可用於 FHIR/HL7 整合 | Patient Context |
| BMI | Body Mass Index | 身體質量指數，計算公式: `weight_kg / (height_cm / 100)^2` | 自動計算欄位，不可直接修改 | Patient Context |
| 吸菸史 | Smoking History | 病患的吸菸狀態 (從未/曾經/目前) 與吸菸年數 | COPD 關鍵風險因素，必填 | Patient Context |
| 治療師分配 | Therapist Assignment | 將病患指派給特定治療師的動作，一對多關係 | 一位治療師可管理多位病患，但病患僅有一位負責治療師 | Patient Context |

##### 🔴 日誌上下文 (Daily Log Context)

| 術語 | 英文 | 定義 | 反例 / 注意事項 | 所屬上下文 |
|------|------|------|-----------------|-----------|
| 健康日誌 | Daily Log | 病患每日提交的健康行為記錄，包含用藥、飲水、步數、症狀、心情 | ≠ 問卷 (Survey) - 後者是定期評估，前者是每日記錄 | Daily Log Context |
| 用藥記錄 | Medication Record | 病患當日是否服藥的布林值記錄 | 僅記錄是/否，不記錄藥物種類 (藥物清單在 PatientProfile.medical_history 中) | Daily Log Context |
| 飲水量 | Water Intake | 病患當日飲水量，單位毫升 (ml)，範圍 0-10000 | 異常值 (如 > 5000ml) 會觸發資料驗證警告 | Daily Log Context |
| 步數 | Steps Count | 病患當日步行步數，範圍 0-100000 | 選填欄位，未來可整合穿戴裝置 | Daily Log Context |
| 症狀 | Symptoms | 病患自述的當日症狀，自由文字欄位 | 未來可用 NLP 分析症狀關鍵詞 (咳嗽、喘、痰) | Daily Log Context |
| 心情 | Mood | 病患當日情緒狀態，枚舉值: GOOD (好), NEUTRAL (普通), BAD (不好) | 用於追蹤心理健康，與症狀嚴重度相關聯 | Daily Log Context |
| 依從率 | Adherence Rate | 病患遵循醫囑的比例，公式: `(N 日內用藥天數 / N) × 100%` | 系統支援 7 日 / 30 日兩種統計窗口 | Daily Log Context |
| 打卡天數 | Streak Days | 病患連續提交日誌的天數，用於遊戲化激勵 | 斷一天歸零，當前連續 / 歷史最長兩種統計 | Daily Log Context |

##### 🔴 問卷上下文 (Survey Context)

| 術語 | 英文 | 定義 | 反例 / 注意事項 | 所屬上下文 |
|------|------|------|-----------------|-----------|
| CAT 問卷 | COPD Assessment Test | COPD 評估測驗，8 題量表，評估 COPD 對生活品質的影響，分數 0-40 | ≠ mMRC (後者僅評估呼吸困難) | Survey Context |
| mMRC 問卷 | modified Medical Research Council | 修正版英國醫學研究委員會呼吸困難量表，單題量表，分數 0-4 | ≠ CAT (後者是多維度評估) | Survey Context |
| 問卷回覆 | Survey Response | 病患完成問卷後的答案記錄，包含原始答案 (JSONB) 與計算分數 | 提交後不可修改，僅能新增新一筆回覆 | Survey Context |
| 嚴重度 | Severity Level | 根據 CAT 分數計算的 COPD 嚴重程度，枚舉值: MILD, MODERATE, SEVERE, VERY_SEVERE | CAT < 10=輕微, 10-20=中度, 21-30=嚴重, >30=極嚴重 | Survey Context |
| 評分器 | Scorer | 領域服務，負責計算問卷總分與嚴重度分級 | 不同問卷類型有不同的 Scorer 實作 (Strategy Pattern) | Survey Context |

##### 🔴 風險上下文 (Risk Context)

| 術語 | 英文 | 定義 | 反例 / 注意事項 | 所屬上下文 |
|------|------|------|-----------------|-----------|
| 風險分數 | Risk Score | 基於多因子計算的病患健康風險量化指標，範圍 0-100 | 分數越高風險越大 | Risk Context |
| 風險等級 | Risk Level | 根據風險分數分級的枚舉值: LOW (0-40), MEDIUM (41-70), HIGH (71-100) | ≠ 嚴重度 (Severity) - 後者來自 CAT 問卷，前者是綜合評估 | Risk Context |
| 風險引擎 | Risk Engine | 領域服務，負責計算風險分數的核心邏輯 | 公式: `Score = f(依從率, CAT分數, 症狀頻率, 年齡, 吸菸史)` | Risk Context |
| 貢獻因子 | Contributing Factors | 組成風險分數的各個子因素及其權重，以 JSONB 儲存 | 範例: `{adherence: 0.3, cat_score: 0.25, symptoms: 0.2, age: 0.15, smoking: 0.1}` | Risk Context |
| 預警 | Alert | 當偵測到異常模式時系統自動產生的通知，需治療師確認與處理 | ≠ 通知 (Notification) - 預警需要人工處理，通知僅為資訊推播 | Risk Context |
| 預警類型 | Alert Type | 預警的觸發原因，枚舉值: MISSED_MEDICATION, NO_LOG, SYMPTOM_SPIKE, RISK_ELEVATED | 不同類型有不同的處理優先級 | Risk Context |
| 預警狀態 | Alert Status | 預警的處理狀態，枚舉值: OPEN (未處理), ACKNOWLEDGED (已確認), RESOLVED (已解決) | 狀態轉換單向: OPEN → ACKNOWLEDGED → RESOLVED | Risk Context |

##### 🔵 衛教上下文 (RAG Context)

| 術語 | 英文 | 定義 | 反例 / 注意事項 | 所屬上下文 |
|------|------|------|-----------------|-----------|
| 衛教文件 | Educational Document | 提供給病患的衛教知識文章，類別包含用藥、運動、飲食、呼吸訓練等 | ≠ 系統文檔 (Documentation) | RAG Context |
| 知識區塊 | Chunk | 從衛教文件中拆分出用於向量檢索的最小單位，每塊 ≤ 500 字 | 拆分策略: 按段落 + 滑動窗口 (Sliding Window) | RAG Context |
| 向量嵌入 | Embedding | 知識區塊轉換為高維向量的表示，使用 OpenAI text-embedding-3-small (維度 1536) | ≠ Tokenization (後者是文本轉數字，前者是語義向量化) | RAG Context |
| 語義檢索 | Semantic Retrieval | 根據查詢文本的語義 (而非關鍵詞) 找到最相關的知識區塊 | 使用餘弦相似度 (Cosine Similarity) 排序 | RAG Context |
| RAG | Retrieval-Augmented Generation | 檢索增強生成，先檢索相關知識，再用 LLM 生成回答的技術 | 流程: Query → Embedding → Retrieval (Top-K) → LLM Prompt → Response | RAG Context |
| 引用來源 | Citation | AI 回覆中標註的參考資料來源，包含文件標題與連結 | 透明化 AI 推理過程，提升使用者信任感 | RAG Context |
| STT | Speech-To-Text | 語音轉文字服務，使用 OpenAI Whisper API | 支援台語/國語混合辨識 (繁體中文) | RAG Context |
| TTS | Text-To-Speech | 文字轉語音服務，使用 OpenAI TTS API | 使用擬人化聲音 (孫女語氣) | RAG Context |

##### 🟢 通知上下文 (Notification Context)

| 術語 | 英文 | 定義 | 反例 / 注意事項 | 所屬上下文 |
|------|------|------|-----------------|-----------|
| 通知 | Notification | 系統發送給使用者的訊息，包含提醒、預警、週報等 | ≠ 預警 (Alert) - 預警需治療師處理，通知僅為資訊推播 | Notification Context |
| 智慧提醒 | Smart Reminder | 根據病患行為模式自動排程的提醒通知，三時段: 12:00, 17:00, 20:00 | 未填日誌時觸發，連續填寫 3 天後自動減少頻率 | Notification Context |
| 推播管道 | Channel | 通知發送的管道，枚舉值: LINE, EMAIL | MVP 階段僅支援 LINE，Phase 2 加入 Email | Notification Context |
| 發送狀態 | Delivery Status | 通知的發送狀態，枚舉值: PENDING (待發送), SENT (已發送), FAILED (失敗) | 失敗後自動重試 3 次 (指數退避) | Notification Context |
| 訊息模板 | Message Template | 預先定義的通知文案格式，支援變數替換 | 範例: `{patient_name} 您好，今日還沒記錄健康日誌喔！` | Notification Context |
| 擬人化口吻 | Humanized Tone | 通知文案使用孫女對長輩的溫馨語氣，提升親和力 | 參考 ADR-007: 擬人化訊息策略 | Notification Context |

---

#### 3.2.2 術語使用規範

**開發團隊規範**:
1. **代碼命名**: 類別、變數、函數命名必須使用統一語言的英文術語 (如 `DailyLog`, `adherence_rate`)
2. **文檔撰寫**: 技術文檔與 PRD 必須使用統一語言的中文術語，並在首次出現時附註英文
3. **溝通會議**: 需求討論與技術評審會議中，團隊成員必須使用統一語言術語，避免自創詞彙
4. **術語更新**: 當發現業務概念變化時，必須更新本詞彙表，並通知全體團隊

**常見錯誤與糾正**:

| ❌ 錯誤術語 | ✅ 正確術語 | 糾正理由 |
|------------|------------|----------|
| "日記" | "健康日誌 (Daily Log)" | "日記" 過於口語化，不精確 |
| "問題" | "症狀 (Symptoms)" 或 "預警 (Alert)" | 需區分患者自述症狀 vs 系統預警 |
| "通知" 與 "預警" 混用 | 明確區分: "通知 (Notification)" vs "預警 (Alert)" | 預警需治療師處理，通知僅為資訊 |
| "用戶" 與 "病患" 混用 | 明確區分: "用戶 (User)" 包含病患與治療師 | 病患是用戶的子類型 |
| "登入失敗次數" | "帳號鎖定 (Account Lockout)" | 應使用業務術語而非技術實作細節 |

---

### 3.3 聚合設計 (Aggregate Design)

聚合 (Aggregate) 是 DDD 戰術設計的核心模式，用於維護業務不變量 (Invariants) 與定義事務邊界。每個聚合有且僅有一個聚合根 (Aggregate Root)，作為對外訪問的唯一入口。

#### 3.3.1 聚合設計原則

遵循以下 DDD 聚合設計原則:

1. **小聚合優先** - 聚合越小越好，僅包含必須保持強一致性的實體
2. **不變量保護** - 聚合根負責維護聚合內所有業務規則
3. **事務邊界** - 每次事務僅修改一個聚合實例
4. **通過 ID 引用** - 聚合間通過 ID 關聯，而非直接持有對象引用
5. **最終一致性** - 跨聚合的業務規則透過領域事件實現最終一致性

#### 3.3.2 聚合目錄

RespiraAlly V2.0 系統包含以下 7 個核心聚合:

| 聚合根 | 所屬上下文 | 核心職責 | 不變量 (Invariants) |
|--------|-----------|----------|---------------------|
| **Patient** | Patient Context | 管理患者檔案、治療師分配 | - 年齡 >= 18 歲<br/>- BMI 由身高體重計算<br/>- 必須分配給一位治療師 |
| **DailyLog** | Daily Log Context | 記錄每日健康行為 | - 每位患者每天僅一筆記錄<br/>- 用藥狀態必須明確 (true/false)<br/>- 飲水量 0-10000ml |
| **SurveyResponse** | Survey Context | 記錄問卷答案與評分 | - CAT 分數 0-40<br/>- mMRC 分數 0-4<br/>- 提交後不可修改 |
| **RiskScore** | Risk Context | 計算並儲存風險評分 | - 分數 0-100<br/>- 風險等級由分數計算<br/>- 每天僅一個分數 |
| **Alert** | Risk Context | 管理預警生命週期 | - 狀態轉換單向: OPEN → ACKNOWLEDGED → RESOLVED<br/>- 僅能由負責治療師處理 |
| **EducationalDocument** | RAG Context | 管理衛教文件與區塊 | - 文件必須有至少一個區塊<br/>- 區塊 index 必須連續<br/>- Embedding 維度一致 |
| **User** | Auth Context | 管理認證與授權 | - LINE User ID 或 Email 至少一個<br/>- Role 與登入方式一致<br/>- 治療師登入失敗鎖定邏輯 |

---

#### 3.3.3 關鍵聚合設計範例

##### Patient Aggregate (個案聚合)

**聚合邊界**:
```
┌─────────────────────────────────────┐
│  Patient Aggregate                  │
│  ┌─────────────┐                    │
│  │  Patient    │ (Aggregate Root)   │
│  │  - user_id  │                    │
│  │  - therapist_id ──> (Reference)  │
│  │  - profile  │                    │
│  └─────────────┘                    │
└─────────────────────────────────────┘
```

**核心不變量**:
1. Patient 年齡必須 >= 18 歲
2. BMI = weight_kg / (height_cm / 100)² (自動計算)
3. 必須分配給一位治療師 (therapist_id NOT NULL)

**領域事件**:
- `PatientRegistered` - 患者註冊完成
- `TherapistAssigned` - 治療師分配變更
- `PatientProfileUpdated` - 檔案更新

##### DailyLog Aggregate (日誌聚合)

**聚合邊界**:
```
┌─────────────────────────────────────┐
│  DailyLog Aggregate                 │
│  ┌─────────────┐                    │
│  │  DailyLog   │ (Aggregate Root)   │
│  │  - log_id   │                    │
│  │  - patient_id ──> (Reference)    │
│  │  - log_date │                    │
│  │  - medication_taken │            │
│  │  - water_intake_ml │             │
│  └─────────────┘                    │
└─────────────────────────────────────┘
```

**核心不變量**:
1. 每位患者每天僅一筆記錄 (UNIQUE INDEX on patient_id, log_date)
2. 不可提交未來日期的日誌
3. 飲水量必須在 0-10000ml 範圍內

**領域事件**:
- `DailyLogSubmitted` - 觸發風險重新計算
- `AdherenceRateChanged` - 依從率變化 (可選)

##### RiskScore Aggregate (風險評分聚合)

**核心不變量**:
1. 風險分數必須在 0-100 之間
2. 風險等級 (LOW/MEDIUM/HIGH) 由分數自動計算
3. 每位患者每天僅一個風險分數

**領域服務**:
- `RiskEngine.calculate()` - 計算風險分數的領域服務
- 公式: `Score = f(adherence_rate × 0.3, cat_score × 0.25, symptom_frequency × 0.2, age × 0.15, smoking_years × 0.1)`

**領域事件**:
- `RiskScoreCalculated` - 風險評分完成
- `AlertTriggered` - 風險等級提升觸發預警

---

#### 3.3.4 聚合設計檢核清單

- [x] **每個聚合有明確的聚合根** - 所有 7 個聚合都有唯一的 Aggregate Root
- [x] **聚合邊界清晰** - 聚合內實體緊密相關,聚合間通過 ID 引用
- [x] **不變量明確** - 每個聚合都有明確的業務規則與驗證邏輯
- [x] **事務邊界** - 每次事務僅修改一個聚合實例
- [x] **領域事件** - 跨聚合操作通過領域事件實現最終一致性
- [x] **小聚合優先** - 聚合僅包含必須強一致性的實體
- [x] **通過 ID 引用** - Patient 聚合引用 Therapist 使用 `therapist_id` 而非對象引用

---

## 4. 架構設計 (Architecture Design)

本章節定義 RespiraAlly V2.0 的整體架構設計，包含水平的模組邊界劃分（Modular Monolith）與垂直的分層設計（Clean Architecture），確保系統的高內聚、低耦合、可測試與可演進。

---

### 4.1 Modular Monolith 模組邊界劃分

#### 4.1.1 設計原則與決策依據

**什麼是 Modular Monolith？**

Modular Monolith（模組化單體）是一種架構模式，在單一部署單元（Monolith）內部通過明確的模組邊界（Modules）實現邏輯隔離。每個模組：
- 擁有獨立的業務職責與數據所有權
- 對外暴露明確的 API 接口（Public Interface）
- 內部實現細節完全封裝（Private Implementation）
- 透過事件或接口與其他模組通信

**為什麼選擇 Modular Monolith？**

基於 Linus-style 五層分析：

| 分析層 | 評估 |
|--------|------|
| **數據結構分析** | 7 個界限上下文自然映射為 7 個模組，數據所有權清晰 |
| **特殊情況識別** | 通用子域（Auth, Notification）被多個模組依賴，需通過依賴注入避免循環依賴 |
| **複雜度審查** | Modular Monolith 比微服務簡單（無分布式複雜性），比傳統單體清晰（有明確邊界） |
| **破壞性分析** | 零破壞：新專案從零開始，未來可演進為微服務（模組邊界已清晰） |
| **實用性驗證** | ✅ MVP 階段 DAU < 100，Modular Monolith 足夠；未來可按模組拆分為微服務 |

**ADR 決策**: 詳見 `docs/04_architecture_decision_record/ADR-003_modular_monolith_vs_microservices.md`

---

#### 4.1.2 模組映射表 (Module Mapping)

基於 DDD 戰略設計的 7 個界限上下文（§3.1），定義 7 個 Modular Monolith 模組：

| 模組名稱 | 對應界限上下文 | 子域類型 | 核心職責 | 數據所有權 |
|----------|----------------|----------|----------|------------|
| **auth** | Auth Context | 通用子域 | 用戶認證、授權、會話管理 | `users`, `sessions`, `refresh_tokens` |
| **patient** | Patient Context | 支撐子域 | 個案檔案管理、治療師分配 | `patient_profiles`, `therapist_profiles` |
| **daily_log** | Daily Log Context | **核心域** | 每日健康日誌、依從率計算 | `daily_logs`, `patient_kpi_cache` |
| **survey** | Survey Context | 支撐子域 | CAT/mMRC 問卷、評分計算 | `survey_responses` |
| **risk** | Risk Context | **核心域** | 風險評分、異常預警 | `risk_scores`, `alerts` |
| **rag** | RAG Context | 支撐子域 | 衛教知識庫、AI 語音問答 | `educational_documents`, `document_chunks`, `chat_sessions`, `ai_processing_logs` |
| **notification** | Notification Context | 通用子域 | LINE/Email 通知、排程發送 | `notification_history` |

**模組所有權原則**:
- ✅ 每張資料表僅屬於一個模組
- ✅ 模組間不可直接 JOIN 查詢（必須通過接口或事件獲取數據）
- ✅ 共享數據通過 Read Model（如 KPI Cache）或事件同步

---

#### 4.1.3 模組依賴與通信圖 (Module Dependency & Communication)

```mermaid
graph TB
    subgraph "通用子域 (Generic Subdomain)"
        Auth[auth<br/>認證模組]
        Notification[notification<br/>通知模組]
    end

    subgraph "核心域 (Core Domain)"
        DailyLog[daily_log<br/>日誌模組]
        Risk[risk<br/>風險模組]
    end

    subgraph "支撐子域 (Supporting Subdomain)"
        Patient[patient<br/>個案模組]
        Survey[survey<br/>問卷模組]
        RAG[rag<br/>衛教模組]
    end

    %% 同步依賴 (Synchronous API Calls)
    DailyLog -->|驗證患者存在| Patient
    Survey -->|驗證患者存在| Patient
    Risk -->|讀取日誌數據| DailyLog
    Risk -->|讀取問卷分數| Survey
    Risk -->|讀取患者檔案| Patient

    %% 異步依賴 (Asynchronous Events)
    DailyLog -.->|事件: LogSubmitted| Risk
    Survey -.->|事件: SurveyCompleted| Risk
    Risk -.->|事件: AlertTriggered| Notification

    %% 認證依賴 (所有模組依賴 Auth)
    Auth -.->|提供 JWT 驗證| DailyLog
    Auth -.->|提供 JWT 驗證| Patient
    Auth -.->|提供 JWT 驗證| Survey
    Auth -.->|提供 JWT 驗證| Risk
    Auth -.->|提供 JWT 驗證| RAG

    style Auth fill:#99ff99,stroke:#009900,stroke-width:2px
    style Notification fill:#99ff99,stroke:#009900,stroke-width:2px
    style DailyLog fill:#ff9999,stroke:#cc0000,stroke-width:3px
    style Risk fill:#ff9999,stroke:#cc0000,stroke-width:3px
    style Patient fill:#99ccff,stroke:#0066cc,stroke-width:2px
    style Survey fill:#99ccff,stroke:#0066cc,stroke-width:2px
    style RAG fill:#99ccff,stroke:#0066cc,stroke-width:2px
```

**圖例說明**:
- **實線箭頭 (→)**: 同步 API 調用（通過接口）
- **虛線箭頭 (-.->)**: 異步事件通信（通過事件總線）
- **紅色邊框**: 核心域模組（競爭優勢所在）
- **藍色邊框**: 支撐子域模組（支撐核心業務）
- **綠色邊框**: 通用子域模組（可用現成方案）

---

#### 4.1.4 模組間通信機制 (Inter-Module Communication)

**通信方式選擇矩陣**:

| 場景 | 通信方式 | 範例 | 理由 |
|------|----------|------|------|
| **查詢數據** | 同步 API 調用 | Risk 模組查詢 DailyLog 的近期日誌 | 需要即時數據，簡單直接 |
| **觸發副作用** | 異步事件 | DailyLog 提交後觸發 Risk 重算 | 解耦，避免級聯失敗 |
| **通知外部** | 異步事件 | Risk 觸發 Alert 後通知 Notification | 解耦，支持多訂閱者 |
| **身份驗證** | 中間件注入 | Auth 模組提供 JWT 驗證中間件 | 橫切關注點（Cross-Cutting Concern） |

**1. 同步 API 調用 (Synchronous Calls)**

透過定義 **Port Interface** 實現依賴反轉：

```python
# daily_log/domain/ports/patient_port.py (定義接口)
from abc import ABC, abstractmethod
from uuid import UUID

class IPatientPort(ABC):
    @abstractmethod
    async def verify_patient_exists(self, patient_id: UUID) -> bool:
        """驗證患者是否存在"""
        pass

# patient/application/adapters/patient_adapter.py (實現接口)
from daily_log.domain.ports import IPatientPort

class PatientAdapter(IPatientPort):
    async def verify_patient_exists(self, patient_id: UUID) -> bool:
        # 實作邏輯
        return await db.fetchval("SELECT EXISTS(SELECT 1 FROM patient_profiles WHERE patient_id = $1)", patient_id)

# main.py (依賴注入)
from daily_log.application.use_cases import SubmitDailyLogUseCase
from patient.application.adapters import PatientAdapter

patient_port = PatientAdapter()
submit_log_use_case = SubmitDailyLogUseCase(patient_port=patient_port)
```

**2. 異步事件通信 (Asynchronous Events)**

透過 **Event Bus** 實現發布-訂閱模式：

```python
# daily_log/domain/events.py (定義事件)
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class DailyLogSubmittedEvent:
    patient_id: UUID
    log_date: datetime
    medication_taken: bool
    occurred_at: datetime

# daily_log/application/use_cases/submit_daily_log.py (發布事件)
class SubmitDailyLogUseCase:
    async def execute(self, command: SubmitDailyLogCommand):
        # 保存日誌
        log = await self.repo.save(daily_log)

        # 發布事件
        event = DailyLogSubmittedEvent(
            patient_id=log.patient_id,
            log_date=log.log_date,
            medication_taken=log.medication_taken,
            occurred_at=datetime.utcnow()
        )
        await self.event_bus.publish(event)

# risk/application/event_handlers.py (訂閱事件)
class RiskCalculationEventHandler:
    async def handle_daily_log_submitted(self, event: DailyLogSubmittedEvent):
        await self.calculate_risk_use_case.execute(patient_id=event.patient_id)
```

---

#### 4.1.5 模組目錄結構 (Module Directory Structure)

```
backend/
├── modules/
│   ├── auth/                    # 認證模組
│   │   ├── domain/              # 領域層 (純業務邏輯)
│   │   │   ├── entities/        # 實體 (User, Session)
│   │   │   ├── value_objects/   # 值對象 (Email, HashedPassword)
│   │   │   ├── services/        # 領域服務 (PasswordHasher)
│   │   │   ├── events/          # 領域事件 (UserCreated)
│   │   │   └── ports/           # 接口定義 (IUserRepository)
│   │   ├── application/         # 應用層 (用例編排)
│   │   │   ├── use_cases/       # 用例 (LoginUseCase, RefreshTokenUseCase)
│   │   │   ├── dtos/            # 數據傳輸對象 (LoginRequest, TokenResponse)
│   │   │   └── event_handlers/  # 事件處理器
│   │   ├── infrastructure/      # 基礎設施層 (實作)
│   │   │   ├── repositories/    # 倉儲實現 (SQLAlchemyUserRepository)
│   │   │   ├── adapters/        # 外部服務適配器 (LINEOAuthAdapter)
│   │   │   └── persistence/     # 數據模型 (SQLAlchemy Models)
│   │   └── presentation/        # 表現層 (API)
│   │       ├── routers/         # FastAPI 路由 (auth_router.py)
│   │       ├── schemas/         # Pydantic 模型 (LoginRequestSchema)
│   │       └── middleware/      # 中間件 (JWTAuthMiddleware)
│   │
│   ├── patient/                 # 個案模組 (結構同 auth)
│   ├── daily_log/               # 日誌模組
│   ├── survey/                  # 問卷模組
│   ├── risk/                    # 風險模組
│   ├── rag/                     # 衛教模組
│   └── notification/            # 通知模組
│
├── shared/                      # 共享基礎設施 (非業務邏輯)
│   ├── event_bus/               # 事件總線實現 (RabbitMQ 封裝)
│   ├── database/                # 數據庫連接池
│   ├── cache/                   # Redis 客戶端
│   ├── logger/                  # 日誌工具
│   └── config/                  # 配置管理
│
└── main.py                      # 應用入口 (依賴注入容器)
```

**目錄結構原則**:
1. ✅ 每個模組內部遵循 **Clean Architecture 四層分層**（§4.2）
2. ✅ `domain/` 層完全獨立，不依賴任何外部框架
3. ✅ `infrastructure/` 層實現 `domain/ports/` 定義的接口
4. ✅ `shared/` 僅包含技術性基礎設施（非業務邏輯）

---

#### 4.1.6 模組依賴規則 (Module Dependency Rules)

**鐵律 (Iron Rules)**:

| 規則 | 說明 | 範例 |
|------|------|------|
| **No Direct Database Access** | 模組不可直接查詢其他模組的資料表 | ❌ `SELECT * FROM patient_profiles WHERE ...` (在 daily_log 模組中)<br/>✅ `await patient_port.get_patient(patient_id)` |
| **No Circular Dependencies** | 模組間不可循環依賴 | ❌ `daily_log → risk → daily_log`<br/>✅ `daily_log → risk` (單向依賴) |
| **Event-Driven for Side Effects** | 副作用觸發必須使用事件 | ❌ `await risk_service.calculate()` (在 daily_log 中)<br/>✅ `await event_bus.publish(DailyLogSubmittedEvent)` |
| **Core Domain Independence** | 核心域模組不依賴支撐子域 | ❌ `daily_log → survey`<br/>✅ `risk → daily_log, survey` |

**依賴方向檢查**:

```python
# ✅ 允許的依賴
daily_log → patient  # 支撐子域依賴支撐子域
risk → daily_log     # 核心域依賴核心域
risk → patient       # 核心域依賴支撐子域
* → auth             # 所有模組依賴通用子域

# ❌ 禁止的依賴
patient → risk       # 支撐子域不可依賴核心域
daily_log → risk     # 避免核心域間雙向依賴（使用事件）
notification → risk  # 通用子域不可依賴核心域（使用事件）
```

---

#### 4.1.7 演進策略 (Evolution Strategy)

**從 Modular Monolith 到 Microservices 的遷移路徑**:

```mermaid
graph LR
    A[Phase 1<br/>Modular Monolith<br/>單一部署單元] --> B[Phase 2<br/>Hybrid<br/>核心域拆分為服務]
    B --> C[Phase 3<br/>Microservices<br/>全面微服務化]

    style A fill:#99ff99
    style B fill:#ffff99
    style C fill:#ff9999
```

| 階段 | 觸發條件 | 拆分優先級 | 理由 |
|------|----------|-----------|------|
| **Phase 1** (當前) | DAU < 100 | 保持 Monolith | 簡化運維、快速迭代 |
| **Phase 2** | DAU > 500 或核心域需獨立擴展 | 優先拆分 `risk` 模組 | 計算密集，需獨立擴展 |
| **Phase 3** | DAU > 5000 或團隊 > 20 人 | 拆分所有模組 | 支持大規模協作 |

**拆分準備清單** (每個模組已具備):
- ✅ 清晰的 API 接口定義 (`domain/ports/`)
- ✅ 獨立的數據所有權（無跨模組 JOIN）
- ✅ 事件驅動通信（低耦合）
- ✅ 完整的測試覆蓋（保證拆分後功能一致）

---

### 4.2 Clean Architecture 垂直分層設計

每個 Modular Monolith 模組內部遵循 **Clean Architecture** 四層分層，確保業務邏輯與技術實現的完全隔離。

#### 4.2.1 分層概覽圖

```
┌─────────────────────────────────────────────────┐
│  表現層 (Presentation Layer)                    │
│  - FastAPI Routers                              │
│  - WebSocket Endpoints                          │
│  - Pydantic Request/Response Schemas            │
└───────────────────┬─────────────────────────────┘
                    │ (調用用例)
┌───────────────────▼─────────────────────────────┐
│  應用層 (Application Layer)                     │
│  - Use Cases / Application Services             │
│  - DTOs (Data Transfer Objects)                 │
│  - Orchestration & Transaction Control          │
│  - Event Handlers                               │
└───────────────────┬─────────────────────────────┘
                    │ (編排領域對象)
┌───────────────────▼─────────────────────────────┐
│  領域層 (Domain Layer) - 核心業務邏輯           │
│  - Entities, Value Objects                      │
│  - Aggregates, Domain Services                  │
│  - Domain Events                                │
│  - Business Rules & Invariants                  │
│  - Ports (接口定義)                             │
└───────────────────┬─────────────────────────────┘
                    │ (依賴反轉)
┌───────────────────▼─────────────────────────────┐
│  基礎設施層 (Infrastructure Layer)              │
│  - Repositories (SQLAlchemy 實現)               │
│  - External Adapters (LINE, OpenAI, RabbitMQ)   │
│  - Persistence Models (ORM)                     │
│  - Event Bus Implementation                     │
└─────────────────────────────────────────────────┘
```

#### 4.2.2 分層職責詳解

##### **第 1 層：表現層 (Presentation Layer)**

**職責**:
- 處理 HTTP/WebSocket 請求與響應
- 驗證輸入格式（Pydantic Schema）
- 調用應用層用例
- 處理異常並返回適當的 HTTP 狀態碼

**技術棧**: FastAPI, Pydantic, WebSocket

**範例** (daily_log 模組):

```python
# modules/daily_log/presentation/routers/daily_log_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from modules.daily_log.presentation.schemas import SubmitDailyLogRequest, DailyLogResponse
from modules.daily_log.application.use_cases import SubmitDailyLogUseCase
from shared.auth import get_current_user

router = APIRouter(prefix="/daily-logs", tags=["Daily Logs"])

@router.post("/", response_model=DailyLogResponse, status_code=status.HTTP_201_CREATED)
async def submit_daily_log(
    request: SubmitDailyLogRequest,
    current_user: dict = Depends(get_current_user),
    use_case: SubmitDailyLogUseCase = Depends()
):
    """提交每日健康日誌"""
    try:
        result = await use_case.execute(
            patient_id=current_user["user_id"],
            log_date=request.log_date,
            medication_taken=request.medication_taken,
            water_intake_ml=request.water_intake_ml,
            symptoms=request.symptoms
        )
        return DailyLogResponse.from_domain(result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error")
```

```python
# modules/daily_log/presentation/schemas.py
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class SubmitDailyLogRequest(BaseModel):
    log_date: date = Field(..., description="日誌日期 (YYYY-MM-DD)")
    medication_taken: bool = Field(..., description="是否已服藥")
    water_intake_ml: int = Field(..., ge=0, le=5000, description="喝水量 (ml)")
    symptoms: Optional[str] = Field(None, max_length=500, description="症狀描述")

    class Config:
        json_schema_extra = {
            "example": {
                "log_date": "2025-10-18",
                "medication_taken": True,
                "water_intake_ml": 2000,
                "symptoms": "今天咳嗽較少"
            }
        }
```

---

##### **第 2 層：應用層 (Application Layer)**

**職責**:
- 編排用例流程（Use Case Orchestration）
- 協調多個領域對象完成業務操作
- 管理事務邊界（Transaction Boundary）
- 發布領域事件到事件總線
- 不包含業務規則（業務規則屬於領域層）

**技術棧**: 純 Python 類別，依賴注入

**範例** (daily_log 模組):

```python
# modules/daily_log/application/use_cases/submit_daily_log.py
from dataclasses import dataclass
from datetime import date
from uuid import UUID
from typing import Optional

from modules.daily_log.domain.entities import DailyLog
from modules.daily_log.domain.ports import IDailyLogRepository, IPatientPort
from modules.daily_log.domain.events import DailyLogSubmittedEvent
from shared.event_bus import IEventBus

@dataclass
class SubmitDailyLogCommand:
    patient_id: UUID
    log_date: date
    medication_taken: bool
    water_intake_ml: int
    symptoms: Optional[str]

class SubmitDailyLogUseCase:
    def __init__(
        self,
        daily_log_repo: IDailyLogRepository,
        patient_port: IPatientPort,
        event_bus: IEventBus
    ):
        self.daily_log_repo = daily_log_repo
        self.patient_port = patient_port
        self.event_bus = event_bus

    async def execute(self, command: SubmitDailyLogCommand) -> DailyLog:
        # Step 1: 驗證患者存在（跨模組調用）
        if not await self.patient_port.verify_patient_exists(command.patient_id):
            raise ValueError(f"Patient {command.patient_id} not found")

        # Step 2: 檢查當日是否已提交
        existing_log = await self.daily_log_repo.find_by_patient_and_date(
            command.patient_id, command.log_date
        )
        if existing_log:
            raise ValueError(f"Log for {command.log_date} already exists")

        # Step 3: 創建領域對象（業務規則在領域層執行）
        daily_log = DailyLog.create(
            patient_id=command.patient_id,
            log_date=command.log_date,
            medication_taken=command.medication_taken,
            water_intake_ml=command.water_intake_ml,
            symptoms=command.symptoms
        )

        # Step 4: 持久化（通過倉儲接口）
        saved_log = await self.daily_log_repo.save(daily_log)

        # Step 5: 發布領域事件（異步觸發風險計算）
        event = DailyLogSubmittedEvent(
            patient_id=saved_log.patient_id,
            log_date=saved_log.log_date,
            medication_taken=saved_log.medication_taken,
            occurred_at=datetime.utcnow()
        )
        await self.event_bus.publish(event)

        return saved_log
```

---

##### **第 3 層：領域層 (Domain Layer) - 核心業務邏輯**

**職責**:
- 實現業務規則與不變量（Invariants）
- 定義實體（Entity）、值對象（Value Object）、聚合（Aggregate）
- 定義領域服務（Domain Service）與領域事件（Domain Event）
- 定義接口（Ports），由基礎設施層實現
- **完全獨立**，不依賴任何外部框架

**技術棧**: 純 Python 類別，無外部依賴

**範例** (daily_log 模組):

```python
# modules/daily_log/domain/entities/daily_log.py
from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID, uuid4
from typing import Optional

@dataclass
class DailyLog:
    """每日健康日誌聚合根"""
    log_id: UUID = field(default_factory=uuid4)
    patient_id: UUID = field()
    log_date: date = field()
    medication_taken: bool = field()
    water_intake_ml: int = field()
    symptoms: Optional[str] = field(default=None)
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        patient_id: UUID,
        log_date: date,
        medication_taken: bool,
        water_intake_ml: int,
        symptoms: Optional[str]
    ) -> "DailyLog":
        """工廠方法：創建日誌並驗證業務規則"""
        # 業務規則 1: 喝水量必須在合理範圍
        if not (0 <= water_intake_ml <= 5000):
            raise ValueError("Water intake must be between 0 and 5000 ml")

        # 業務規則 2: 症狀描述不可過長
        if symptoms and len(symptoms) > 500:
            raise ValueError("Symptoms description must be <= 500 characters")

        # 業務規則 3: 日誌日期不可為未來
        if log_date > date.today():
            raise ValueError("Cannot create log for future dates")

        return cls(
            patient_id=patient_id,
            log_date=log_date,
            medication_taken=medication_taken,
            water_intake_ml=water_intake_ml,
            symptoms=symptoms
        )

    def update_medication_status(self, taken: bool) -> None:
        """更新用藥狀態（領域行為）"""
        self.medication_taken = taken
```

```python
# modules/daily_log/domain/ports/daily_log_repository.py
from abc import ABC, abstractmethod
from uuid import UUID
from datetime import date
from typing import Optional, List
from modules.daily_log.domain.entities import DailyLog

class IDailyLogRepository(ABC):
    """日誌倉儲接口（Port），由基礎設施層實現"""

    @abstractmethod
    async def save(self, daily_log: DailyLog) -> DailyLog:
        """保存日誌"""
        pass

    @abstractmethod
    async def find_by_id(self, log_id: UUID) -> Optional[DailyLog]:
        """根據 ID 查詢"""
        pass

    @abstractmethod
    async def find_by_patient_and_date(
        self, patient_id: UUID, log_date: date
    ) -> Optional[DailyLog]:
        """查詢患者在特定日期的日誌"""
        pass

    @abstractmethod
    async def find_recent_logs(
        self, patient_id: UUID, days: int = 7
    ) -> List[DailyLog]:
        """查詢近期日誌"""
        pass
```

```python
# modules/daily_log/domain/events.py
from dataclasses import dataclass
from datetime import datetime, date
from uuid import UUID

@dataclass
class DailyLogSubmittedEvent:
    """領域事件：日誌已提交"""
    patient_id: UUID
    log_date: date
    medication_taken: bool
    occurred_at: datetime
```

---

##### **第 4 層：基礎設施層 (Infrastructure Layer)**

**職責**:
- 實現領域層定義的接口（Ports）
- 提供技術細節實現（數據庫、外部 API、消息隊列）
- ORM 模型（SQLAlchemy Models）與領域實體的轉換
- 依賴外部框架（FastAPI, SQLAlchemy, Pika, Redis）

**技術棧**: SQLAlchemy, asyncpg, Pika, httpx, Redis

**範例** (daily_log 模組):

```python
# modules/daily_log/infrastructure/persistence/models.py
from sqlalchemy import Column, String, Date, Boolean, Integer, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from shared.database import Base
import uuid

class DailyLogModel(Base):
    """SQLAlchemy ORM 模型（基礎設施層）"""
    __tablename__ = "daily_logs"

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    log_date = Column(Date, nullable=False)
    medication_taken = Column(Boolean, nullable=False)
    water_intake_ml = Column(Integer, nullable=False)
    symptoms = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
```

```python
# modules/daily_log/infrastructure/repositories/daily_log_repository.py
from typing import Optional, List
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from modules.daily_log.domain.entities import DailyLog
from modules.daily_log.domain.ports import IDailyLogRepository
from modules.daily_log.infrastructure.persistence.models import DailyLogModel

class DailyLogRepository(IDailyLogRepository):
    """倉儲實現（基礎設施層）"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, daily_log: DailyLog) -> DailyLog:
        model = DailyLogModel(
            log_id=daily_log.log_id,
            patient_id=daily_log.patient_id,
            log_date=daily_log.log_date,
            medication_taken=daily_log.medication_taken,
            water_intake_ml=daily_log.water_intake_ml,
            symptoms=daily_log.symptoms,
            created_at=daily_log.created_at
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def find_by_patient_and_date(
        self, patient_id: UUID, log_date: date
    ) -> Optional[DailyLog]:
        stmt = select(DailyLogModel).where(
            DailyLogModel.patient_id == patient_id,
            DailyLogModel.log_date == log_date
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    @staticmethod
    def _to_domain(model: DailyLogModel) -> DailyLog:
        """ORM 模型轉換為領域實體"""
        return DailyLog(
            log_id=model.log_id,
            patient_id=model.patient_id,
            log_date=model.log_date,
            medication_taken=model.medication_taken,
            water_intake_ml=model.water_intake_ml,
            symptoms=model.symptoms,
            created_at=model.created_at
        )
```

---

#### 4.2.3 依賴反轉實踐 (Dependency Inversion Principle)

**核心原則**: 高層模組（領域層、應用層）不依賴低層模組（基礎設施層），兩者都依賴抽象（接口）。

**依賴流向圖**:

```mermaid
graph TB
    subgraph "高層模組 (High-Level)"
        Domain[領域層<br/>DailyLog Entity]
        Application[應用層<br/>SubmitDailyLogUseCase]
    end

    subgraph "抽象層 (Abstraction)"
        Port[接口定義<br/>IDailyLogRepository]
    end

    subgraph "低層模組 (Low-Level)"
        Infra[基礎設施層<br/>DailyLogRepository<br/>SQLAlchemy 實現]
    end

    Application -->|使用| Domain
    Application -->|依賴| Port
    Domain -->|定義| Port
    Infra -->|實現| Port

    style Domain fill:#ff9999
    style Application fill:#99ccff
    style Port fill:#ffff99
    style Infra fill:#99ff99
```

**依賴注入實例** (在 `main.py` 中):

```python
# backend/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from modules.daily_log.application.use_cases import SubmitDailyLogUseCase
from modules.daily_log.infrastructure.repositories import DailyLogRepository
from modules.patient.infrastructure.adapters import PatientAdapter
from shared.database import get_db_session
from shared.event_bus import get_event_bus

app = FastAPI()

# 依賴注入容器
def get_submit_daily_log_use_case(
    db_session: AsyncSession = Depends(get_db_session)
) -> SubmitDailyLogUseCase:
    daily_log_repo = DailyLogRepository(db_session)
    patient_port = PatientAdapter(db_session)
    event_bus = get_event_bus()

    return SubmitDailyLogUseCase(
        daily_log_repo=daily_log_repo,
        patient_port=patient_port,
        event_bus=event_bus
    )

# 註冊路由
from modules.daily_log.presentation.routers import daily_log_router
app.include_router(daily_log_router)
```

---

#### 4.2.4 分層規則檢查清單

| 規則 | 檢查項目 | 範例 |
|------|----------|------|
| **領域層獨立性** | 領域層不可 import 任何外部框架 | ❌ `from fastapi import Request`<br/>✅ `from uuid import UUID` |
| **依賴方向正確** | 外層依賴內層，內層不依賴外層 | ✅ `Application → Domain`<br/>❌ `Domain → Infrastructure` |
| **接口在領域層** | Repository/Service 接口定義在 `domain/ports/` | ✅ `domain/ports/daily_log_repository.py`<br/>❌ `infrastructure/repositories/interface.py` |
| **業務規則在領域層** | 驗證邏輯在 Entity/Value Object 中 | ✅ `DailyLog.create()` 驗證喝水量<br/>❌ 在 FastAPI Router 中驗證 |
| **用例編排在應用層** | 多個領域對象的協調在 Use Case 中 | ✅ `SubmitDailyLogUseCase` 協調 Repository + Event Bus<br/>❌ 在 Entity 中調用 Repository |

---

#### 4.2.5 測試策略

基於分層架構，每層有不同的測試策略：

| 層級 | 測試類型 | 測試重點 | Mock 對象 |
|------|----------|----------|-----------|
| **領域層** | 單元測試 (Unit Test) | 業務規則、不變量驗證 | 無需 Mock（純邏輯） |
| **應用層** | 單元測試 + 整合測試 | 用例編排、事務控制 | Mock Repository, Event Bus |
| **基礎設施層** | 整合測試 (Integration Test) | 數據庫操作、外部 API | 使用測試數據庫/Mock Server |
| **表現層** | API 測試 (E2E Test) | HTTP 請求/響應、錯誤處理 | 使用測試客戶端 (TestClient) |

**範例** (領域層單元測試):

```python
# tests/unit/domain/test_daily_log.py
import pytest
from datetime import date, timedelta
from modules.daily_log.domain.entities import DailyLog

def test_create_daily_log_with_valid_data():
    log = DailyLog.create(
        patient_id=uuid4(),
        log_date=date.today(),
        medication_taken=True,
        water_intake_ml=2000,
        symptoms="今天咳嗽較少"
    )
    assert log.medication_taken is True
    assert log.water_intake_ml == 2000

def test_create_daily_log_with_invalid_water_intake():
    with pytest.raises(ValueError, match="Water intake must be between 0 and 5000 ml"):
        DailyLog.create(
            patient_id=uuid4(),
            log_date=date.today(),
            medication_taken=True,
            water_intake_ml=10000,  # 超出範圍
            symptoms=None
        )

def test_cannot_create_future_log():
    with pytest.raises(ValueError, match="Cannot create log for future dates"):
        DailyLog.create(
            patient_id=uuid4(),
            log_date=date.today() + timedelta(days=1),  # 未來日期
            medication_taken=True,
            water_intake_ml=2000,
            symptoms=None
        )
```

---

### 4.3 模組間通信機制 (Inter-Module Communication)

Modular Monolith 架構中，模組間通信機制的選擇直接影響系統的耦合度與可維護性。我們採用**混合策略**：同步調用處理即時性需求，異步事件處理解耦與擴展需求。

#### 4.3.1 同步通信（Adapter Pattern）

**適用場景**: 需要即時響應的跨模組調用（如驗證、查詢）。

**實現方式**: 通過 Port-Adapter 模式實現依賴反轉。

```python
# daily_log/domain/ports/patient_port.py (定義接口)
class PatientPort(ABC):
    @abstractmethod
    def get_patient_info(self, patient_id: str) -> PatientInfo:
        pass

# patient/application/adapters/patient_adapter.py (實現接口)
class PatientAdapter(PatientPort):
    def get_patient_info(self, patient_id: str) -> PatientInfo:
        # 調用 patient 模組的服務
        return patient_service.get_by_id(patient_id)
```

#### 4.3.2 異步通信（Event-Driven Pattern）

**適用場景**: 非即時性操作、需解耦的跨模組協作（如風險計算、通知發送）。

**核心組件**:
- **Event Bus**: 事件分發中心（MVP 使用 in-memory，未來可升級為 RabbitMQ）
- **Domain Events**: 領域事件（記錄業務關鍵操作）
- **Event Handlers**: 事件處理器（訂閱並處理事件）
- **Event Store**: 事件存儲（持久化事件，支持審計與重放）

##### 領域事件目錄 (Domain Events)

**事件命名規範**: `{模組名}{聚合名}{動作過去式}` (例: `DailyLogSubmitted`)

**核心事件清單**:

| 模組 | 事件名稱 | 觸發時機 | 訂閱者 |
|------|----------|----------|--------|
| daily_log | `DailyLogSubmitted` | 患者提交日誌 | risk, notification |
| questionnaire | `QuestionnaireCompleted` | 問卷完成 | risk, analytics |
| risk | `RiskScoreCalculated` | 風險分數計算完成 | notification, analytics |
| risk | `RiskLevelElevated` | 風險等級提升 | notification, therapist_dashboard |
| ai_chat | `ChatSessionCompleted` | AI 對話完成 | analytics, risk |

**完整事件目錄**: 參見 [附錄 C: 事件驅動實作範例](#附錄-c-事件驅動實作範例)

##### Event Bus 架構設計

**MVP 階段**: 使用 in-memory Event Bus（Python `asyncio.Queue`）
**未來演進**: 升級為 RabbitMQ（支持分散式部署與高可用）

```python
# shared/event_bus/interface.py
class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """發布事件"""
        pass

    @abstractmethod
    async def subscribe(self, event_type: str, handler: Callable) -> None:
        """訂閱事件"""
        pass
```

**RabbitMQ 架構** (未來):
- Exchange 類型: Topic Exchange
- Routing Key: `{module}.{aggregate}.{action}`
- DLQ: 支持失敗重試與死信隊列

詳細設計參見 [附錄 C](#附錄-c-事件驅動實作範例)。

##### Event Store 設計

**用途**: 持久化所有領域事件，支持：
- 審計追蹤（Who did What When）
- 事件重放（重建聚合狀態）
- 數據同步（跨模組數據最終一致性）

**Outbox Pattern**: 確保事件與業務操作的事務性
```sql
CREATE TABLE event_store (
    id UUID PRIMARY KEY,
    event_type VARCHAR(255) NOT NULL,
    aggregate_id VARCHAR(255) NOT NULL,
    payload JSONB NOT NULL,
    published BOOLEAN DEFAULT FALSE,  -- Outbox Pattern
    occurred_at TIMESTAMP DEFAULT NOW()
);
```

#### 4.3.3 通信機制選擇指南

| 場景 | 推薦機制 | 理由 |
|------|----------|------|
| 驗證患者是否存在 | 同步調用 (Adapter) | 需即時回應 |
| 查詢患者基本資料 | 同步調用 (Adapter) | 讀操作，無副作用 |
| 日誌提交觸發風險計算 | 異步事件 | 非關鍵路徑，可解耦 |
| 風險提升通知治療師 | 異步事件 | 通知可容忍延遲 |
| AI 對話完成後更新記憶 | 異步事件 | 避免阻塞對話流程 |

---

## 5. 數據架構 (Data Architecture)

本章節詳述 RespiraAlly V2.0 的數據架構，包含核心數據模型、關鍵數據流、一致性策略以及數據生命週期管理，確保數據的完整性、可用性與合規性。

**📄 完整資料庫設計文檔**: 詳細的表結構、索引、約束、觸發器、存儲過程、視圖設計請參閱:
- **[Database Schema Design v1.0](./database/schema_design_v1.0.md)** - 實作層級完整設計

### 5.1 核心實體關係圖 (Core Entity-Relationship Diagram)

以下 ER 圖提供系統核心數據模型的概覽。詳細的表定義、欄位約束、索引策略請參閱上述完整設計文檔。

以下 ER 圖展示了系統中核心業務實體及其關係，這些實體主要儲存在 PostgreSQL 資料庫中。

**🔄 重要變更** (基於架構審視報告):
- ✅ **優化 USERS 表繼承模式** - `PATIENT_PROFILES` 與 `THERAPIST_PROFILES` 直接使用 `user_id` 作為 PK
- ✅ **新增 `EVENT_LOGS` 表** - 使用 PostgreSQL JSONB 替代 MongoDB
- ✅ **新增 `PATIENT_KPI_CACHE` 表** - 反正規化加速查詢
- ✅ **新增 `NOTIFICATION_HISTORY` 表** - 追蹤通知狀態

```mermaid
erDiagram
    USERS {
        uuid user_id PK
        string line_user_id UK "Nullable for PATIENT"
        string email UK "Nullable for THERAPIST"
        string hashed_password "Nullable for LINE OAuth"
        enum role "PATIENT or THERAPIST"
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at "Soft delete"
    }

    PATIENTS {
        string patient_id PK "FK to USERS.user_id"
        string therapist_id FK "Assigned Therapist"
        string name "Patient Name"
        date birth_date
        string hospital_medical_record_number "病歷號"
        integer height_cm "身高 cm"
        decimal weight_kg "體重 kg"
        enum smoking_status "NEVER, FORMER, CURRENT"
        integer smoking_years "吸菸年數"
        jsonb medical_history "COPD stage, comorbidities"
        jsonb contact_info "Phone, address"
    }

    THERAPISTS {
        string therapist_id PK "FK to USERS.user_id"
        string name "Therapist Name"
        string institution "Hospital/Clinic"
    }

    DAILY_LOGS {
        uuid log_id PK
        string patient_id FK
        date log_date
        boolean medication_taken
        integer water_intake_ml
        string symptoms
        datetime created_at
    }

    SURVEY_RESPONSES {
        uuid response_id PK
        string survey_name "e.g., CAT, mMRC"
        string patient_id FK
        jsonb answers
        datetime submitted_at
    }

    RISK_SCORES {
        uuid score_id PK
        string patient_id FK
        integer score "0-100"
        string score_level "LOW, MEDIUM, HIGH"
        jsonb contributing_factors
        datetime calculated_at
    }

    ALERTS {
        uuid alert_id PK
        string patient_id FK
        string therapist_id FK
        string reason
        string status "OPEN, ACK, RESOLVED"
        datetime created_at
    }
    
    EDUCATIONAL_DOCUMENTS {
        uuid doc_id PK
        string title
        text content
        string category
    }

    DOCUMENT_CHUNKS {
        uuid chunk_id PK
        uuid doc_id FK
        text chunk_text
        vector embedding "pgvector"
    }

    USERS ||--o{ PATIENTS : "is_a (profile)"
    USERS ||--o{ THERAPISTS : "is_a (profile)"
    THERAPISTS ||--|{ PATIENTS : "manages"
    PATIENTS ||--|{ DAILY_LOGS : "submits"
    PATIENTS ||--|{ SURVEY_RESPONSES : "completes"
    PATIENTS ||--|{ RISK_SCORES : "has"
    RISK_SCORES ||--o{ ALERTS : "triggers"
    ALERTS }|--|| THERAPISTS : "notifies"
    EDUCATIONAL_DOCUMENTS ||--|{ DOCUMENT_CHUNKS : "is_chunked_into"
```

**模型說明**:
- **USERS**: 統一儲存所有使用者（病患與治療師）的基礎認證資訊。`role` 欄位用於區分身份。
- **PATIENTS / THERAPISTS**: 分別儲存病患與治療師的詳細檔案資訊，並透過一對一關係關聯回 `USERS` 表。
- **DAILY_LOGS / SURVEY_RESPONSES**: 記錄病患的核心健康數據，是計算風險分數的基礎。
- **RISK_SCORES / ALERTS**: 風險引擎的產出，用於實現主動預警功能。
- **EDUCATIONAL_DOCUMENTS / DOCUMENT_CHUNKS**: RAG 服務的知識庫來源，`DOCUMENT_CHUNKS` 中的 `embedding` 欄位將由 `pgvector` 進行索引以實現高效相似度搜尋。

### 5.2 數據流圖 (Data Flow Diagram) - 病患提交日誌

此圖展示了系統中最核心的數據流之一：病患提交每日健康日誌後的處理流程。

```mermaid
flowchart LR
    Patient[病患 LIFF] -->|1. 提交日誌| APIGateway[API Gateway]
    APIGateway -->|2. 請求轉發| LogService[日誌服務]
    LogService -->|3. 寫入 強一致| Postgres((PostgreSQL))
    LogService -->|4. 發布事件| RabbitMQ[RabbitMQ<br/>daily_log.submitted]

    RabbitMQ -->|5. 訂閱| RiskEngine[風險引擎]
    RiskEngine -->|6. 讀取近期數據| Postgres
    RiskEngine -->|7. 更新分數| Postgres
    RiskEngine -->|8. 若有異常, 發布事件| RabbitMQ[alert.triggered]

    RabbitMQ -->|9. 訂閱| NotificationService[通知服務]
    NotificationService -->|10. 推播給治療師| LINE[LINE Platform]

    style Postgres fill:#ccffcc
    style RabbitMQ fill:#ccccff
```

### 5.3 KPI 快取層與資料視圖設計 (KPI Cache & Data Views)

**設計目標**: 為前端數據視覺化提供高效能 (<50ms) 的 KPI 查詢能力,同時保持數據的即時性與一致性。

**📄 詳細設計文檔**: 完整的 KPI 快取表、視圖、觸發器、存儲過程設計請參閱:
- **[Database Schema Design - Section 4.5](./database/schema_design_v1.0.md#45-patient_kpi_cache-kpi-快取表)** - KPI 快取層實作細節

#### 5.3.1 兩層式架構設計

```mermaid
graph TD
    subgraph "即時寫入層"
        DailyLogs[Daily Logs]
        Surveys[Survey Responses]
        Risks[Risk Scores]
    end

    subgraph "快取層 (Cache Layer)"
        KPICache[patient_kpi_cache<br/>預聚合統計<br/>查詢 < 50ms]
    end

    subgraph "視圖層 (View Layer)"
        KPIWindows[patient_kpi_windows<br/>動態時間窗口 KPI<br/>7/30/90天]
        HealthTimeline[patient_health_timeline<br/>每日時間序列<br/>含移動平均]
        SurveyTrends[patient_survey_trends<br/>問卷趨勢<br/>含分數變化]
        HealthSummary[patient_health_summary<br/>病患健康摘要<br/>含 BMI 計算]
    end

    DailyLogs -->|觸發器自動更新| KPICache
    Surveys -->|觸發器自動更新| KPICache
    Risks -->|觸發器自動更新| KPICache

    DailyLogs -.->|Window Functions| KPIWindows
    DailyLogs -.->|Window Functions| HealthTimeline
    Surveys -.->|Window Functions| SurveyTrends

    KPICache -->|API查詢| Frontend[前端 Dashboard]
    KPIWindows -->|API查詢| Frontend
    HealthTimeline -->|API查詢| Frontend
    SurveyTrends -->|API查詢| Frontend
    HealthSummary -->|API查詢| Frontend

    style KPICache fill:#ffcccc
    style KPIWindows fill:#ccffcc
    style HealthTimeline fill:#ccffcc
    style SurveyTrends fill:#ccffcc
    style HealthSummary fill:#ccffcc
```

#### 5.3.2 `patient_kpi_cache` 表設計

**用途**: 預聚合的病患 KPI 統計,支持 <50ms 快速查詢。

**核心欄位**:
- 基礎統計: `total_logs_count`, `first_log_date`, `last_log_date`
- 依從率: `adherence_rate_7d`, `adherence_rate_30d`
- 健康指標: `avg_water_intake_7d`, `avg_steps_7d/30d`
- 最新問卷: `latest_cat_score`, `latest_cat_date`, `latest_mmrc_score`
- 最新風險: `latest_risk_score`, `latest_risk_level`, `latest_risk_date`
- 症狀統計: `symptom_occurrences_30d`

**更新機制**:
1. **觸發器自動更新** (即時):
   - `update_patient_kpi_on_log_insert()` - 新增日誌時更新基礎統計
   - `update_patient_kpi_on_survey_insert()` - 新增問卷時更新最新分數
   - `update_patient_kpi_on_risk_insert()` - 新增風險評分時更新風險數據

2. **定期刷新** (按需):
   - `refresh_patient_kpi_cache(patient_id)` - 刷新所有計算型 KPI
   - 建議: 使用 pg_cron 每小時執行,或在病患查詢 Dashboard 時按需調用

#### 5.3.3 資料視圖設計

**1. patient_kpi_windows (動態時間窗口 KPI)**
- **用途**: 支持 7/30/90 天窗口的 KPI 對比分析
- **關鍵特性**: 使用 FILTER WHERE 子句實現多時間窗口聚合
- **查詢性能**: ~200ms (依賴底層日誌表索引)

**2. patient_health_timeline (每日時間序列)**
- **用途**: 前端折線圖數據源
- **關鍵特性**:
  - 7 天移動平均 (平滑曲線)
  - 累積統計 (累積趨勢圖)
  - Window Functions 計算

**3. patient_survey_trends (問卷趨勢)**
- **用途**: CAT/mMRC 問卷歷史圖表
- **關鍵特性**:
  - 分數變化 (與上次問卷對比)
  - 基線對比 (與首次問卷對比)
  - 累計問卷次數

**4. patient_health_summary (健康摘要)**
- **用途**: 病患基本資料查詢,含自動計算 BMI
- **關鍵特性**:
  - BMI 自動計算: `weight_kg / (height_cm/100)^2`
  - BMI 分級: UNDERWEIGHT/NORMAL/OVERWEIGHT/OBESE
  - 年齡自動計算

#### 5.3.4 性能優化策略

**索引設計** (參考 database/schema_design_v1.0.md):
```sql
-- patient_kpi_cache 主鍵索引
CREATE INDEX idx_patient_kpi_patient_id ON patient_kpi_cache(patient_id);

-- daily_logs 複合索引 (支持時間窗口查詢)
CREATE INDEX idx_daily_logs_patient_date
  ON daily_logs(patient_id, log_date DESC);

-- survey_responses 複合索引
CREATE INDEX idx_survey_patient_type_date
  ON survey_responses(patient_id, survey_type, submitted_at DESC);
```

**查詢性能目標**:
- `patient_kpi_cache` 直接查詢: **< 50ms**
- `patient_kpi_windows` 視圖查詢: **< 200ms**
- `patient_health_timeline` 視圖查詢 (30天): **< 300ms**

**降級策略**:
- 若 KPI Cache 過期 (last_calculated_at > 1小時), 前端顯示刷新按鈕
- 若視圖查詢超時, 降級為簡化版圖表 (僅顯示近 7 天)

### 5.4 數據一致性策略 (Data Consistency Strategy)

在分散式微服務架構中，我們根據業務場景選擇不同的一致性模型，以平衡系統的可用性、性能與數據準確性。

- **強一致性 (Strong Consistency) 場景**:
  - **用戶認證與授權**: 治療師登入、病患透過 LINE 登入時，必須立即讀取到最新的帳戶狀態與權限。
  - **核心數據寫入**: 病患提交健康日誌、問卷的核心寫入操作。系統必須確保數據成功持久化到 PostgreSQL 後才向用戶返回成功，避免數據遺失。此類操作將包裹在單一服務的資料庫事務中完成。

- **最終一致性 (Eventual Consistency) 場景**:
  - **風險分數計算**: 當日誌提交後，風險分數的更新是異步進行的。在短暫的時間窗口內（通常是毫秒到秒級），治療師看到的風險分數可能尚未反映最新的日誌，這是可接受的。
  - **觸發預警通知**: 同樣地，從風險分數更新到觸發預警並發送通知也是一個異步流程。
  - **跨服務數據同步**: 例如，更新病患基本資料後，相關的顯示名稱同步到其他服務的日誌記錄中，將透過事件傳遞，接受最終一致性。
  - **事件日誌寫入**: 寫入 PostgreSQL `event_logs` 表（JSONB 欄位）的操作日誌與事件記錄，允許極短時間的延遲。

### 5.5 數據生命週期與合規 (Data Lifecycle and Compliance)

- **數據分類 (Data Classification)**:
  - **個人身份資訊 (PII)**: 病患姓名、LINE Profile、治療師 Email。
  - **受保護健康資訊 (PHI)**: 健康日誌、問卷答案、風險分數、症狀描述等。
  - **系統操作數據**: API 請求日誌、使用者操作事件。

- **數據儲存與加密 (Data Storage and Encryption)**:
  - **傳輸中加密 (In-Transit)**: 所有對外 API 與服務間通訊均強制使用 TLS 1.3 加密。
  - **靜態加密 (At-Rest)**: 所有在 Zeabur 平台上的託管資料庫 (PostgreSQL, Redis) 和物件儲存 (MinIO) 均啟用服務商提供的靜態加密功能。

- **數據保留策略 (Data Retention Policy)**:
  - **PHI 數據**: 根據台灣醫療法規，病歷資料（包含日誌、問卷）需至少保留 7 年。
  - **PII 數據**: 當病患或治療師帳號刪除時，其個人身份資訊將被匿名化處理，但保留去識別化的 PHI 數據用於統計分析。
  - **系統日誌 (PostgreSQL JSONB)**: 操作日誌與事件記錄（存儲在 `event_logs` 表）將保留 18 個月，之後進行歸檔或刪除。

- **合規性考量 (Compliance Considerations)**:
  - 本系統設計遵循台灣**個人資料保護法（個資法）**的要求，確保數據的收集、處理、利用均獲得用戶明確同意，並提供用戶查詢、修改、刪除其個資的權利。

---

## 6. 部署架構 (Deployment Architecture) - MVP 階段

```mermaid
graph TD
  subgraph "Cloudflare"
    CDN[CDN / WAF]
  end
  
  subgraph "Zeabur Platform"
    LB[Load Balancer]

    subgraph "API Tier (Stateless Services)"
      API_Gateway[API Gateway]
      Auth_Svc[認證服務]
      Patient_Svc[個案服務]
      Log_Svc[日誌服務]
      Risk_Svc[風險引擎]
      RAG_Svc[RAG 服務]
    end

    subgraph "Worker Tier"
      AI_Worker[AI Worker]
      Scheduler[APScheduler]
    end

    subgraph "Data Tier (Managed Services)"
      Postgres_DB((PostgreSQL))
      Redis_DB((Redis))
      MinIO_Store((MinIO))
      RabbitMQ_Broker{RabbitMQ}
    end
  end

  CDN --> LB
  LB --> API_Gateway
  API_Gateway --> Auth_Svc & Patient_Svc & Log_Svc & Risk_Svc & RAG_Svc

  Log_Svc --> RabbitMQ_Broker
  RabbitMQ_Broker --> AI_Worker
  Scheduler --> RAG_Svc & Patient_Svc

  API_Tier --讀寫--> Postgres_DB & Redis_DB
  Worker_Tier --讀寫--> Postgres_DB & MinIO_Store
```

**部署特性 (MVP on Zeabur)**:
- **快速部署**: 利用 PaaS 平台 Zeabur 簡化部署流程，實現從 Git Push 到服務上線的自動化。
- **成本效益**: 初期使用託管服務，按需付費，避免過早投入大量基礎設施維護成本。
- **演進路徑**: 待業務成熟後，可將此架構平滑遷移至 Kubernetes (K8s) 叢集，以獲得更強的客製化能力與高可用性配置。

---

## 7. 關鍵設計與策略

### 7.1 治療師登入失敗鎖定策略
為防止惡意登入嘗試，認證服務 (`Auth Service`) 實作了帳號鎖定機制。
- **觸發條件**: 在 15 分鐘內，連續登入失敗 3 次。
- **鎖定時長**: 帳號將被鎖定 15 分鐘。
- **實現方式**: 使用 Redis 記錄指定帳號的失敗次數與時間戳，並設定 TTL (Time-To-Live) 自動過期。
- **對應 ADR**: [ADR-008](./adr/ADR-008-login-lockout-policy.md)

### 7.2 AI Worker 韌性設計
為確保 AI 語音處理流程的穩定性，AI Worker 採用了以下設計：
- **可靠任務佇列**: 使用 RabbitMQ，並為 `voice_tasks` 佇列啟用訊息持久化 (Durability) 與消費者確認 (Acknowledgements)，確保即使 Worker 重啟，任務也不會遺失。
- **指數退避重試**: 當 Worker 處理鏈中的任何一步（如呼叫外部 STT 或 LLM API）失敗時，任務將被拒絕並重新入隊。RabbitMQ 將根據指數退避策略延遲下一次投遞。
- **死信佇列 (Dead-Letter Queue)**: 在重試 3 次後仍然失敗的任務，將被自動路由到一個專門的死信佇列中，以便後續的人工介入分析，同時向系統管理員發送警報。

### 7.3 AI Worker 狀態機設計 (AI Worker State Machine)

AI Worker 是 RespiraAlly 的核心組件,負責處理病患語音訊息並生成 AI 回應。其設計基於**狀態機模式** (State Machine Pattern),確保處理流程的可追溯性、可恢復性與可觀測性。

#### 7.3.1 狀態機架構圖 (State Machine Diagram)

```mermaid
stateDiagram-v2
    [*] --> IDLE: Worker 啟動
    IDLE --> RECEIVED: 接收 RabbitMQ 任務

    RECEIVED --> LOCKED: 獲取音檔鎖成功
    RECEIVED --> DUPLICATE: 音檔鎖已被持有
    DUPLICATE --> [*]: ACK 訊息 (返回快取結果)

    LOCKED --> MEMORY_GATE: 檢查是否需要記憶

    MEMORY_GATE --> MEMORY_RETRIEVAL: Memory Gate = USE
    MEMORY_GATE --> GUARDRAIL: Memory Gate = SKIP

    MEMORY_RETRIEVAL --> GUARDRAIL: 檢索完成

    GUARDRAIL --> GUARDRAIL_BLOCK: Guardrail Agent = BLOCK
    GUARDRAIL --> STT: Guardrail Agent = OK

    GUARDRAIL_BLOCK --> RESPONSE_READY: 生成婉拒回應
    GUARDRAIL_BLOCK --> NOTIFY: 發送婉拒訊息

    STT --> STT_FAILED: STT API 錯誤
    STT --> LLM: STT 成功

    LLM --> RAG: 需要檢索知識庫
    LLM --> EMERGENCY_CHECK: 無需 RAG

    RAG --> EMERGENCY_CHECK: 檢索完成

    EMERGENCY_CHECK --> EMERGENCY_ALERT: 檢測到緊急情況
    EMERGENCY_CHECK --> RESPONSE_READY: 正常情況

    EMERGENCY_ALERT --> TTS: 發送通報 & 生成回應

    RESPONSE_READY --> TTS: 準備語音合成

    TTS --> TTS_FAILED: TTS API 錯誤
    TTS --> MEMORY_LOG: TTS 成功

    MEMORY_LOG --> SUMMARY_CHECK: 記錄對話

    SUMMARY_CHECK --> SUMMARY_TRIGGER: 累積 5 輪對話
    SUMMARY_CHECK --> NOTIFY: 未達門檻

    SUMMARY_TRIGGER --> NOTIFY: LLM 壓縮摘要

    NOTIFY --> COMPLETED: 發送 LINE 通知

    STT_FAILED --> RETRY: retry_count < 3
    TTS_FAILED --> RETRY: retry_count < 3
    STT_FAILED --> FAILED: retry_count >= 3
    TTS_FAILED --> FAILED: retry_count >= 3

    RETRY --> [*]: NACK 訊息 (重新入隊)
    FAILED --> [*]: 發送失敗通知 & ACK

    COMPLETED --> IDLE: 釋放鎖 & ACK 訊息

    note right of LOCKED
        音檔級鎖 (180s TTL)
        lock:audio:{user_id}#audio:{audio_id}
    end note

    note right of MEMORY_GATE
        Memory Gate 決策
        - 規則引擎 (打招呼 → SKIP)
        - LLM 判斷器 (GPT-4o-mini)
    end note

    note right of GUARDRAIL
        雙層安全檢查
        1. Guardrail Agent (違法/危險內容)
        2. Health Agent (醫療專業邊界)
    end note

    note right of EMERGENCY_CHECK
        緊急情況判斷標準
        - 自殺計畫 (有時間/方法)
        - 生命危急症狀 (嚴重呼吸困難、胸痛)
    end note

    note right of SUMMARY_TRIGGER
        滾動摘要機制
        - 每 5 輪壓縮
        - CAS 提交 (樂觀鎖)
        - 節省 85% Token
    end note
```

#### 7.3.2 狀態詳細說明 (State Descriptions)

| 狀態 | 說明 | 預期停留時間 | 可觀測性指標 |
|------|------|-------------|-------------|
| **IDLE** | Worker 空閒,等待任務 | 不定 | - |
| **RECEIVED** | 從 RabbitMQ 接收語音處理任務 | < 10ms | `worker_task_received_total` |
| **LOCKED** | 成功獲取音檔級冪等鎖 | < 5ms | `audio_lock_acquired_total` |
| **DUPLICATE** | 音檔鎖已被其他 Worker 持有 (重複任務) | < 5ms | `audio_lock_duplicate_total` |
| **MEMORY_GATE** | 使用 Memory Gate 決策是否檢索記憶 | 50-100ms | `memory_gate_decision_duration_seconds` |
| **MEMORY_RETRIEVAL** | 檢索 Redis 近期對話 + pgvector 語義記憶 | 100-200ms | `memory_retrieval_duration_seconds` |
| **GUARDRAIL** | Guardrail Agent 安全檢查 (違法/危險內容) | 500-1000ms | `guardrail_check_duration_seconds` |
| **GUARDRAIL_BLOCK** | 安全檢查判定為需攔截 | < 100ms | `guardrail_blocked_total` |
| **STT** | 呼叫 OpenAI Whisper API 語音轉文字 | 2-5s | `stt_duration_seconds` |
| **STT_FAILED** | STT API 呼叫失敗 (網路錯誤、API 限流等) | - | `stt_failed_total` |
| **LLM** | 呼叫 GPT-4 Turbo 生成 AI 回應 | 5-15s | `llm_duration_seconds` |
| **RAG** | 檢索 pgvector 知識庫 (衛教文章) | 200-500ms | `rag_retrieval_duration_seconds` |
| **EMERGENCY_CHECK** | 檢查 LLM 回應是否觸發緊急通報 | < 100ms | `emergency_check_total` |
| **EMERGENCY_ALERT** | 發送緊急通報 Email/Slack 給治療師 | 500-1000ms | `emergency_alert_sent_total` |
| **RESPONSE_READY** | AI 回應文字已生成 | - | - |
| **TTS** | 呼叫 OpenAI TTS API 文字轉語音 | 2-5s | `tts_duration_seconds` |
| **TTS_FAILED** | TTS API 呼叫失敗 | - | `tts_failed_total` |
| **MEMORY_LOG** | 記錄對話到 Redis + PostgreSQL | 50-100ms | `memory_log_duration_seconds` |
| **SUMMARY_CHECK** | 檢查是否累積 5 輪對話 (觸發摘要) | < 10ms | `summary_check_total` |
| **SUMMARY_TRIGGER** | 呼叫 LLM 壓縮歷史對話為摘要 | 2-5s | `summary_triggered_total` |
| **NOTIFY** | 發送 LINE 推播通知給病患 | 500-1000ms | `line_notification_sent_total` |
| **RETRY** | 任務失敗,準備重試 (NACK 訊息) | - | `task_retry_total` |
| **FAILED** | 超過重試次數,任務失敗 | - | `task_failed_total` |
| **COMPLETED** | 任務成功完成 | - | `task_completed_total` |

**總處理時間 (端到端)**: 約 **10-20 秒** (含所有 API 呼叫與記憶操作)

#### 7.3.3 關鍵轉換條件 (Key Transition Conditions)

##### 7.3.3.1 冪等性檢查 (RECEIVED → LOCKED/DUPLICATE)

```python
# 音檔級鎖實作 (參考 V1 beloved_grandson 設計)
lock_id = f"{user_id}#audio:{audio_id}"

if acquire_audio_lock(lock_id, ttl_sec=180):
    # 成功獲取鎖 → LOCKED 狀態
    state = "LOCKED"
else:
    # 鎖已被持有 → DUPLICATE 狀態
    cached_result = get_audio_result(user_id, audio_id)
    if cached_result:
        # 返回快取結果
        return cached_result
    else:
        # 等待其他 Worker 完成
        return "我正在處理你的語音,請稍等一下喔。"
```

**設計要點**:
- ✅ 使用 Redis `SET NX EX` 原子操作保證冪等性
- ✅ TTL 設為 180 秒 (涵蓋最壞情況處理時間)
- ✅ 即使 Worker 崩潰,TTL 會自動釋放鎖

##### 7.3.3.2 Memory Gate 決策 (MEMORY_GATE → MEMORY_RETRIEVAL/GUARDRAIL)

```python
# Memory Gate 決策邏輯 (參考 docs/ai/20_memory_management_design.md)
decision = MemoryGateTool()._run(user_input)

if decision == "USE":
    # 檢索記憶 (Redis 近期 6 輪 + pgvector 語義相似)
    state = "MEMORY_RETRIEVAL"
    context = build_prompt_from_redis(user_id, k=6, current_input=user_input)
    context += search_similar_conversations(user_id, user_input, top_k=3)
elif decision == "SKIP":
    # 跳過記憶檢索 (僅使用歷史摘要)
    state = "GUARDRAIL"
    context = get_summary(user_id)
```

**決策規則**:
- ✅ 打招呼、閒聊 → SKIP (節省 50-100ms 延遲)
- ✅ "上次你說..." → USE (需要對比歷史)
- ✅ 症狀變化描述 → USE (需要趨勢分析)
- ✅ 模糊情況 → 呼叫 GPT-4o-mini 快速判斷

##### 7.3.3.3 Guardrail 安全檢查 (GUARDRAIL → GUARDRAIL_BLOCK/STT)

```python
# Guardrail Agent 安全檢查 (參考 V1 chat_pipeline.py)
guard_result = CrewAI_Guardrail_Agent.run(user_input)

if guard_result.startswith("BLOCK:"):
    # 攔截危險內容
    state = "GUARDRAIL_BLOCK"
    block_reason = guard_result[6:].strip()

    # 跳過 STT/LLM/RAG,直接生成婉拒回應
    response = generate_polite_refusal(block_reason)
    return response
else:
    # 通過安全檢查,進入 STT
    state = "STT"
```

**攔截情境**:
- 🚫 違法行為指導 (毒品、槍械、自殺方法)
- 🚫 醫療劑量指示 ("吃幾顆藥")
- 🚫 診斷建議 ("你得的是肺癌")
- ✅ 允許情緒表達 ("我好想死" ≠ "我打算今晚跳樓")

##### 7.3.3.4 緊急情況判斷 (EMERGENCY_CHECK → EMERGENCY_ALERT/RESPONSE_READY)

```python
# 緊急情況檢測 (參考 V1 Health Agent 設計)
is_emergency, reason = check_emergency_signals(
    user_input=user_input,
    llm_response=llm_response
)

if is_emergency:
    # 發送緊急通報
    state = "EMERGENCY_ALERT"

    # Email 給治療師
    send_email_alert(
        to=therapist_email,
        subject=f"【緊急】病患 {patient_name} 觸發警報",
        body=f"原因: {reason}\n原始訊息: {user_input}"
    )

    # Slack 通知 (如果已設定)
    send_slack_alert(channel="#copd-alerts", message=f"🚨 緊急通報: {reason}")

    # 記錄事件日誌
    log_emergency_event(user_id, reason, user_input)

    state = "TTS"
else:
    state = "RESPONSE_READY"
```

**緊急判斷標準** (僅依據**當前輸入**,禁止依賴歷史推測):

| 類別 | 緊急情況範例 | 非緊急範例 |
|------|-------------|-----------|
| **自殺意圖** | "我打算今晚跳樓" (有時間+方法) | "我好累,活著好辛苦" (情緒表達) |
| **自傷計畫** | "我準備了安眠藥 100 顆" (有準備) | "我想過要結束" (念頭無計畫) |
| **呼吸危急** | "現在喘到快窒息,嘴唇發紫" | "今天走路會喘" |
| **胸痛** | "胸口劇痛+冒冷汗+噁心" | "胸口有點悶" |
| **意識改變** | "頭暈到快昏倒,講話不清楚" | "有點頭暈" |

**關鍵原則**:
- ✅ **逐字分析當前輸入**,不得依賴歷史對話或模型推測
- ✅ **有計畫/時間點/準備動作** → 緊急
- ✅ **生命危急症狀** (窒息、劇烈胸痛、意識障礙) → 緊急
- ❌ **模糊求助或情緒低落** → 非緊急 (給予情緒支持)

##### 7.3.3.5 滾動摘要觸發 (SUMMARY_CHECK → SUMMARY_TRIGGER/NOTIFY)

```python
# 檢查是否累積 5 輪對話 (參考 docs/ai/20_memory_management_design.md)
start, chunk = peek_next_n(user_id, SUMMARY_CHUNK_SIZE=5)

if start is not None and chunk:
    # 累積足夠輪數,觸發 LLM 摘要
    state = "SUMMARY_TRIGGER"

    summary_text = summarize_chunk_with_llm(chunk)

    # 使用 CAS (Compare-And-Swap) 提交摘要
    success = commit_summary_chunk(
        user_id=user_id,
        expected_cursor=start,
        advance=5,
        add_text=summary_text
    )

    if success:
        logger.info(f"Summary committed for user {user_id}, rounds {start}-{start+4}")
    else:
        logger.warning(f"Summary commit failed (CAS conflict), will retry next time")

    state = "NOTIFY"
else:
    # 未達 5 輪門檻,直接發送通知
    state = "NOTIFY"
```

**滾動摘要效益**:
- 💰 **Token 節省**: 85% (1000 tokens → 150 tokens)
- ⏱️ **延遲優化**: 減少 Prompt 長度 → 加快 LLM 推理
- 🧠 **長期記憶**: 避免 LLM "Lost in the Middle" 問題

##### 7.3.3.6 錯誤重試策略 (STT_FAILED/TTS_FAILED → RETRY/FAILED)

```python
# 錯誤處理與重試 (參考 ADR-005: RabbitMQ)
if task['retry_count'] < MAX_RETRIES:
    # NACK 訊息,RabbitMQ 將重新投遞
    state = "RETRY"
    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    # 訊息會進入 DLX (Dead Letter Exchange) 並延遲投遞
    # 指數退避: 30s → 60s → 120s
else:
    # 超過重試次數,發送失敗通知
    state = "FAILED"

    publish_line_notification(
        user_id=user_id,
        message_type="voice_error",
        data={"error": "語音處理失敗,請稍後再試或改用文字輸入"}
    )

    # ACK 訊息 (避免無限重試)
    ch.basic_ack(delivery_tag=method.delivery_tag)
```

**重試策略表**:

| 重試次數 | 延遲時間 | 累計時間 | 動作 |
|---------|---------|---------|------|
| 0 | 0s | 0s | 首次處理 |
| 1 | 30s | 30s | 第一次重試 |
| 2 | 60s | 90s | 第二次重試 |
| 3 | 120s | 210s | 第三次重試 |
| >3 | - | - | 進入 DLQ,發送失敗通知 |

#### 7.3.4 與其他子系統的整合 (Integration with Subsystems)

```mermaid
sequenceDiagram
    participant RabbitMQ
    participant Worker as AI Worker
    participant Redis
    participant PostgreSQL as PostgreSQL + pgvector
    participant OpenAI as OpenAI APIs
    participant LINE

    RabbitMQ->>Worker: 語音處理任務
    Worker->>Redis: 獲取音檔鎖 (SET NX)
    Redis-->>Worker: 成功

    Worker->>Redis: Memory Gate 決策
    Redis-->>Worker: USE (需要記憶)

    Worker->>Redis: 檢索近期 6 輪對話
    Worker->>PostgreSQL: 檢索語義相似對話 (pgvector)
    PostgreSQL-->>Worker: Top-3 相關對話

    Worker->>OpenAI: STT (Whisper)
    OpenAI-->>Worker: 轉錄文字

    Worker->>Worker: Guardrail Agent 檢查
    Worker->>OpenAI: LLM (GPT-4 Turbo)
    OpenAI-->>Worker: AI 回應文字

    Worker->>Worker: 緊急情況檢查
    alt 緊急情況
        Worker->>LINE: 發送通報 Email
        Worker->>PostgreSQL: 記錄緊急事件
    end

    Worker->>OpenAI: TTS
    OpenAI-->>Worker: 語音 URL

    Worker->>Redis: 記錄對話歷史
    Worker->>PostgreSQL: 記錄對話日誌

    Worker->>Redis: 檢查摘要觸發 (5 輪)
    alt 達到 5 輪
        Worker->>OpenAI: 壓縮摘要 (GPT-4o-mini)
        Worker->>Redis: CAS 提交摘要
    end

    Worker->>RabbitMQ: 發布 LINE 通知任務
    Worker->>Redis: 釋放音檔鎖 (DEL)
    Worker->>RabbitMQ: ACK 訊息

    RabbitMQ->>LINE: LINE 推播通知
    LINE-->>Worker: 發送成功
```

#### 7.3.5 可觀測性設計 (Observability Design)

**Prometheus 指標** (Metrics):

```python
from prometheus_client import Counter, Histogram, Gauge

# 1. 任務計數器
task_received_total = Counter(
    'ai_worker_task_received_total',
    'Total tasks received from RabbitMQ'
)

task_completed_total = Counter(
    'ai_worker_task_completed_total',
    'Total tasks completed successfully'
)

task_failed_total = Counter(
    'ai_worker_task_failed_total',
    'Total tasks failed after retries',
    ['failure_reason']  # 'stt_error', 'llm_error', 'tts_error'
)

# 2. 狀態持續時間
state_duration_seconds = Histogram(
    'ai_worker_state_duration_seconds',
    'Time spent in each state',
    ['state'],  # 'stt', 'llm', 'tts', 'memory_retrieval', etc.
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0]
)

# 3. 端到端延遲
pipeline_duration_seconds = Histogram(
    'ai_worker_pipeline_duration_seconds',
    'End-to-end pipeline latency',
    buckets=[5.0, 10.0, 15.0, 20.0, 30.0, 60.0]
)

# 4. 冪等性檢查
audio_lock_acquired_total = Counter(
    'ai_worker_audio_lock_acquired_total',
    'Audio locks successfully acquired'
)

audio_lock_duplicate_total = Counter(
    'ai_worker_audio_lock_duplicate_total',
    'Duplicate tasks skipped (lock already held)'
)

# 5. Memory Gate 決策
memory_gate_decision_total = Counter(
    'ai_worker_memory_gate_decision_total',
    'Memory Gate decisions',
    ['decision']  # 'USE', 'SKIP'
)

# 6. Guardrail 攔截
guardrail_blocked_total = Counter(
    'ai_worker_guardrail_blocked_total',
    'Tasks blocked by Guardrail Agent',
    ['block_reason']  # 'illegal_content', 'medical_advice', etc.
)

# 7. 緊急通報
emergency_alert_sent_total = Counter(
    'ai_worker_emergency_alert_sent_total',
    'Emergency alerts triggered',
    ['alert_type']  # 'suicide_risk', 'respiratory_crisis', etc.
)

# 8. 滾動摘要
summary_triggered_total = Counter(
    'ai_worker_summary_triggered_total',
    'Rolling summaries triggered'
)
```

**Grafana 儀表板面板** (Dashboard Panels):

1. **任務吞吐量** (Task Throughput): `rate(task_completed_total[5m])`
2. **失敗率** (Failure Rate): `rate(task_failed_total[5m]) / rate(task_received_total[5m])`
3. **P95 延遲** (P95 Latency): `histogram_quantile(0.95, pipeline_duration_seconds)`
4. **狀態時間分布** (State Duration Breakdown): Heatmap by state
5. **Memory Gate 決策比例** (Memory Gate Decision Ratio): Pie chart
6. **緊急通報趨勢** (Emergency Alert Trend): Time series

**OpenTelemetry 分散式追蹤** (Distributed Tracing):

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def process_voice_task(task_data):
    """處理語音任務 (含分散式追蹤)"""
    with tracer.start_as_current_span("ai_worker_pipeline") as span:
        span.set_attribute("task_id", task_data['task_id'])
        span.set_attribute("user_id", task_data['payload']['user_id'])
        span.set_attribute("audio_duration_ms", task_data['payload']['audio_duration_ms'])

        # STT
        with tracer.start_as_current_span("stt"):
            transcript = stt_service.transcribe(task_data['payload']['audio_url'])
            span.set_attribute("transcript_length", len(transcript))

        # LLM
        with tracer.start_as_current_span("llm"):
            response = llm_service.generate(user_id, transcript)
            span.set_attribute("response_length", len(response))

        # TTS
        with tracer.start_as_current_span("tts"):
            audio_url = tts_service.synthesize(response)

        return audio_url
```

**Jaeger Trace 範例** (追蹤單一任務的完整鏈路):

```
Trace ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
Duration: 12.3s

├─ ai_worker_pipeline (12.3s)
│  ├─ audio_lock_acquire (5ms)
│  ├─ memory_gate_decision (80ms)
│  ├─ memory_retrieval (150ms)
│  │  ├─ redis_lrange (30ms)
│  │  └─ pgvector_search (120ms)
│  ├─ guardrail_check (800ms)
│  │  └─ crewai_guardrail_agent (800ms)
│  ├─ stt (3.2s)
│  │  └─ openai_whisper_api (3.2s)
│  ├─ llm (8.5s)
│  │  ├─ rag_search (200ms)
│  │  │  └─ pgvector_search (200ms)
│  │  ├─ openai_gpt4_api (8.0s)
│  │  └─ emergency_check (50ms)
│  ├─ tts (2.8s)
│  │  └─ openai_tts_api (2.8s)
│  ├─ memory_log (80ms)
│  │  ├─ redis_rpush (20ms)
│  │  └─ postgresql_insert (60ms)
│  ├─ summary_check (10ms)
│  └─ notify_publish (500ms)
│     └─ rabbitmq_publish (500ms)
```

#### 7.3.6 狀態持久化與恢復 (State Persistence & Recovery)

**挑戰**: Worker 崩潰時,如何恢復未完成的任務?

**解決方案**: 使用 **RabbitMQ 訊息持久化** + **Redis 狀態快照**

```python
# 狀態檢查點 (Checkpoint) 設計
def checkpoint_state(task_id: str, state: str, data: Dict):
    """記錄狀態檢查點到 Redis"""
    r = get_redis()
    key = f"checkpoint:{task_id}"
    r.hset(key, mapping={
        "state": state,
        "data": json.dumps(data),
        "timestamp": int(time.time())
    })
    r.expire(key, 3600)  # 1h TTL

def recover_from_checkpoint(task_id: str) -> Optional[Dict]:
    """從檢查點恢復狀態"""
    r = get_redis()
    key = f"checkpoint:{task_id}"
    checkpoint = r.hgetall(key)
    if not checkpoint:
        return None

    return {
        "state": checkpoint['state'],
        "data": json.loads(checkpoint['data']),
        "timestamp": int(checkpoint['timestamp'])
    }

# Worker 啟動時恢復未完成任務
def recover_incomplete_tasks():
    """Worker 啟動時檢查是否有未完成任務"""
    r = get_redis()
    keys = r.keys("checkpoint:*")

    for key in keys:
        checkpoint = r.hgetall(key)
        task_id = key.split(":")[1]

        # 檢查任務是否已超時 (1 小時)
        age = int(time.time()) - int(checkpoint['timestamp'])
        if age > 3600:
            logger.warning(f"Task {task_id} checkpoint expired, marking as failed")
            r.delete(key)
            continue

        # 根據狀態決定恢復策略
        state = checkpoint['state']
        if state in ['STT', 'LLM', 'TTS']:
            # 外部 API 呼叫中斷 → 重新開始該步驟
            logger.info(f"Recovering task {task_id} from {state} state")
            # 重新發布到 RabbitMQ (帶 retry_count+1)
            republish_task(task_id, checkpoint['data'])
        else:
            # 其他狀態 → 標記為失敗
            logger.warning(f"Task {task_id} in {state} state, cannot recover")
            r.delete(key)
```

**恢復策略表**:

| 狀態 | 恢復策略 | 資料損失風險 |
|------|----------|-------------|
| IDLE, RECEIVED | 無需恢復 | 無 |
| LOCKED, MEMORY_GATE | 重新開始任務 | 無 |
| STT, LLM, TTS | 從檢查點恢復,重新呼叫 API | 低 (可能重複呼叫 API) |
| MEMORY_LOG, NOTIFY | 重新執行 (冪等操作) | 無 |
| COMPLETED | 無需恢復 | 無 |

#### 7.3.7 效能最佳化建議 (Performance Optimization)

| 優化項目 | 目標 | 實作方式 | 預期效果 |
|---------|------|----------|----------|
| **STT 快取** | 減少重複轉錄 | 快取 audio_id → transcript | 節省 20% STT 成本 |
| **LLM 快取** | 相同問題重用回應 | 快取 query hash → response | 節省 15% LLM 成本 |
| **RAG 預熱** | 常見問題提前檢索 | 背景 Job 建立熱點索引 | P95 延遲 -30% |
| **批次 Embedding** | 減少 API 呼叫次數 | 批次處理 10 筆對話 | 提升吞吐量 2× |
| **並行處理** | 利用多核心 | asyncio 並行呼叫 API | 端到端延遲 -20% |
| **TTS 串流** | 邊合成邊發送 | WebSocket 串流傳輸 | 首包延遲 -50% |

**並行處理範例**:

```python
import asyncio

async def process_voice_task_async(task_data):
    """使用 asyncio 並行處理"""
    # STT
    transcript = await stt_service.transcribe_async(task_data['audio_url'])

    # 並行: Memory Retrieval + RAG + Guardrail
    memory, rag_context, guardrail_result = await asyncio.gather(
        retrieve_memory_async(user_id, transcript),
        search_rag_async(transcript),
        guardrail_check_async(transcript)
    )

    # LLM (依賴前面結果,無法並行)
    response = await llm_service.generate_async(transcript, memory, rag_context)

    # TTS
    audio_url = await tts_service.synthesize_async(response)

    return audio_url
```

---

## 8. 架構決策記錄 (ADR)

關鍵 ADR 索引 (詳見 `docs/adr/` 目錄):

| ADR ID | 標題 | 狀態 | 連結 |
|--------|------|------|------|
| **ADR-001** | 採用 FastAPI 而非 Flask | 已決定 | [ADR-001](./adr/ADR-001-fastapi-vs-flask.md) |
| **ADR-002** | pgvector 作為初期向量庫 | 已決定 | [ADR-002](./adr/ADR-002-pgvector-for-vector-db.md) |
| **ADR-003** | ~~MongoDB 儲存事件日誌~~ → PostgreSQL JSONB | 已變更 | ~~[ADR-003](./adr/ADR-003-mongodb-for-event-logs.md)~~ [database/schema_design_v1.0.md](./database/schema_design_v1.0.md) |
| **ADR-004** | LINE 為唯一病患入口 | 已決定 | [ADR-004](./adr/ADR-004-line-as-patient-entrypoint.md) |
| **ADR-005** | RabbitMQ 作為訊息佇列 (Phase 2) | 已決定 | [ADR-005](./adr/ADR-005-rabbitmq-for-message-queue.md) |
| **ADR-006** | 三時段智慧提醒策略 | 已決定 | [ADR-006](./adr/ADR-006-smart-reminders-schedule.md) |
| **ADR-007** | 擬人化孫女口吻訊息 | 已決定 | [ADR-007](./adr/ADR-007-persona-based-messaging-tone.md) |
| **ADR-008** | 治療師登入失敗鎖定策略 | 已決定 | [ADR-008](./adr/ADR-008-login-lockout-policy.md) |
| **ADR-009** | Modular Monolith 而非微服務 (MVP) | 已決定 | [05_architecture_and_design.md](./05_architecture_and_design.md) |

---

## 9. 蘇格拉底檢核 (Socratic Review)

完成架構設計後,回答以下關鍵問題以驗證架構的合理性:

### Q1: 品質屬性權衡

**問題**: 性能、安全、成本三者的優先級如何排序？為什麼？

**答**:
- **優先級排序**: 安全性 > 性能 > 成本
- **理由**:
  1. **安全性 (P0)**: 涉及患者醫療數據（PHI），任何洩露都可能造成法律責任與信任危機，不可妥協
  2. **性能 (P0)**: 患者使用體驗直接影響留存率（北極星指標：依從率 ≥75%），API P95 < 500ms 是及格線
  3. **成本 (P1)**: MVP 階段可接受較高單位成本，待驗證商業模式後再優化

**驗證方式**:
- **安全性**: 滲透測試、OWASP Top 10 檢查、定期安全審計
- **性能**: APM 監控（Prometheus + Grafana）、定期壓力測試（Locust）
- **成本**: 雲端賬單監控、設定成本告警閾值（月預算上限）

---

### Q2: 單點故障分析

**問題**: 系統中是否存在單點故障 (SPOF)？如果某個關鍵組件失效，系統如何降級？

**答**:

| 組件 | 是否 SPOF | 失效影響 | 降級策略 |
|------|-----------|----------|----------|
| **API Gateway** | ❌ (可水平擴展) | 部分請求失敗 | Zeabur 內建負載均衡器自動切換至健康實例 |
| **PostgreSQL Master** | ⚠️ 是（MVP 階段） | 寫入服務中斷 | 短期：手動切換至 Read Replica（RTO ~15 分鐘）<br/>長期：Patroni 自動 Failover |
| **Redis** | ❌ (Cluster Mode) | 部分緩存失效 | 降級為直接查詢 PostgreSQL（性能下降但不影響功能） |
| **RabbitMQ** | ⚠️ 是（MVP 階段） | AI 異步任務堆積 | AI 功能降級為同步模式（用戶等待時間增加至 15 秒內） |
| **LINE Platform** | ✅ 是（外部依賴） | 患者無法使用 LIFF | Phase 2 提供 Web 版本 Backup |
| **OpenAI API** | ✅ 是（外部依賴） | AI 語音功能失效 | 降級為預設回覆模板 + 人工客服轉接 |

**改進計畫**:
- **短期（2026 Q1）**: 建立 PostgreSQL 自動 Failover 機制（Patroni + etcd）
- **中期（2026 Q2）**: RabbitMQ Cluster Mode 部署（3 節點）
- **長期（2026 Q3）**: 考慮多雲部署（AWS + GCP）降低雲平台依賴

---

### Q3: 數據一致性

**問題**: 哪些場景需要強一致性？哪些可接受最終一致性？如何處理分布式事務？

**答**:

**強一致性場景** (ACID 事務):
1. **患者註冊**: 必須確保 LINE User ID 與 Patient ID 綁定唯一性（PostgreSQL UNIQUE 約束）
2. **健康日誌提交**: 每日僅一筆記錄（`UNIQUE(patient_id, log_date)`）
3. **問卷評分**: 評分結果需與答案原子性存儲（同一事務）
4. **治療師帳號鎖定**: 登入失敗計數必須準確（Redis INCR + TTL）

**最終一致性場景** (事件驅動):
1. **風險分數計算**: 允許數秒延遲，透過 `daily_log.submitted` 事件觸發異步計算
2. **異常預警通知**: 允許失敗重試，最終送達即可（RabbitMQ 持久化 + 確認機制）
3. **統計報表**: 允許數據延遲數分鐘，不影響核心功能
4. **AI 對話歷史**: PostgreSQL `event_logs` 表寫入允許短暫延遲（非關鍵路徑）

**分布式事務處理 - Saga 模式**:

**範例：患者註冊流程**

```mermaid
sequenceDiagram
    participant Client as LIFF Client
    participant AuthSvc as 認證服務
    participant PatientSvc as 患者服務
    participant EventBus as RabbitMQ
    participant LINEAdapter as LINE Adapter

    Client->>AuthSvc: POST /register (LINE User ID)

    Note over AuthSvc: 步驟 1: 本地事務
    AuthSvc->>AuthSvc: 創建 USER 記錄（USERS 表）
    AuthSvc->>EventBus: 發布 UserCreatedEvent
    AuthSvc-->>Client: 返回 201 Created (user_id)

    Note over EventBus,PatientSvc: 步驟 2: 異步處理
    EventBus->>PatientSvc: 訂閱 UserCreatedEvent
    PatientSvc->>PatientSvc: 創建 PATIENT 記錄
    PatientSvc->>EventBus: 發布 PatientCreatedEvent

    Note over EventBus,LINEAdapter: 步驟 3: LINE 綁定
    EventBus->>LINEAdapter: 訂閱 PatientCreatedEvent
    LINEAdapter->>LINEAdapter: 綁定 Rich Menu

    alt 綁定失敗
        LINEAdapter->>EventBus: 發布 PatientCreationFailedEvent
        EventBus->>PatientSvc: 補償事務
        PatientSvc->>PatientSvc: 軟刪除 PATIENT 記錄
        PatientSvc->>EventBus: 發布 UserDeletionRequestedEvent
        EventBus->>AuthSvc: 補償事務
        AuthSvc->>AuthSvc: 軟刪除 USER 記錄
    end
```

**關鍵設計原則**:
- 每個服務僅管理自己的本地事務
- 透過領域事件實現跨服務協作
- 補償事務實現最終一致性（不使用兩階段提交 2PC）

---

### Q4: 演進性

**問題**: 未來需求變化時，哪些部分容易擴展？哪些是瓶頸？技術棧是否有升級或遷移計畫？

**答**:

**易於擴展部分** ✅:
1. **新增健康指標**: 透過 JSONB 欄位（`profile_details`）擴展，無需 Schema 變更
2. **新增問卷類型**: 透過策略模式（`SurveyScorer` 接口），新增評分演算法不影響現有代碼
3. **新增通知管道**: 透過 Adapter 模式（`NotificationAdapter`），可快速接入簡訊、Email、推播
4. **新增 AI 模型**: 透過 Adapter 模式（`LLMProvider`），可快速切換不同 LLM（OpenAI → Anthropic → Local）
5. **新增微服務**: FastAPI 模組化架構，新增服務不影響現有服務

**潛在瓶頸** ⚠️:
1. **AI 語音處理延遲**: 當前同步調用 OpenAI API（平均 10 秒），高並發時會阻塞
   - **解決方案**: Phase 2 改為異步批次處理（RabbitMQ Priority Queue）
2. **PostgreSQL 寫入瓶頸**: 當患者數達 10 萬+ 時，單一主庫可能成為瓶頸
   - **解決方案**: 垂直分庫（按服務拆分）或水平分表（按時間分區）
3. **LINE Messaging API 限流**: Push Message API 有速率限制（500 req/s）
   - **解決方案**: 實作訊息佇列 + Token Bucket 限流器
4. **pgvector 查詢效能**: 當知識庫達到 100 萬+ 向量時，IVFFlat 索引可能不夠
   - **解決方案**: 升級至 HNSW 索引或遷移至專用向量資料庫（Qdrant）

**技術棧升級計畫**:

| 技術 | 當前版本 | 目標版本 | 升級理由 | 計畫時程 |
|------|----------|----------|----------|----------|
| **Python** | 3.11 | 3.12 | 性能提升 ~5%、更好的型別提示 | 2026 Q2 |
| **FastAPI** | 0.109 | 最新穩定版 | 安全性更新、新特性 | 每季度 |
| **PostgreSQL** | 15 | 16 | 更好的分區表支持、性能優化 | 2026 Q3 |
| **Next.js** | 14 | 15 | Turbopack 穩定版、更快構建 | 2026 Q2 |
| **Redis** | 7 | 8 | Redis Stack 功能（RediSearch） | 2026 Q4 |
| **RabbitMQ** | 3 | 4 | 更好的 Streams 支持 | 2026 Q3 |

**架構演進路徑**:

```
Phase 1: MVP (2026 Q1)
├── Zeabur 單區域部署
├── PostgreSQL Master + Read Replica
└── RabbitMQ 單節點

↓

Phase 2: 優化 (2026 Q2-Q3)
├── Kubernetes 遷移（GKE / EKS）
├── PostgreSQL Patroni Cluster（自動 Failover）
├── RabbitMQ Cluster Mode（3 節點）
└── Redis Sentinel（高可用）

↓

Phase 3: 規模化 (2026 Q4+)
├── 多區域部署（台北 + 高雄）
├── Qdrant 向量資料庫（專用）
├── Kafka 替換 RabbitMQ（更高吞吐）
└── 自建 AI 模型（Whisper + LLaMA）
```

---

### Q5: 可觀測性

**問題**: 如何監控系統健康狀態？故障發生時，如何快速定位問題？

**答**:

**監控三支柱 (Three Pillars of Observability)**:

#### 1. Metrics (指標) - Prometheus + Grafana

**應用層指標**:
- **API 請求量**: `http_requests_total{method, endpoint, status}`
- **API 延遲**: `http_request_duration_seconds{method, endpoint, quantile="0.95"}`
- **錯誤率**: `http_requests_errors_total{method, endpoint}` / `http_requests_total`
- **業務指標**:
  - `daily_logs_submitted_total` (每日日誌提交數)
  - `ai_queries_total{status}` (AI 查詢數)
  - `risk_alerts_triggered_total{level}` (風險預警觸發數)

**系統層指標**:
- **CPU 使用率**: `node_cpu_usage_percent`
- **記憶體使用率**: `node_memory_usage_percent`
- **磁碟 I/O**: `node_disk_read_bytes_total`, `node_disk_write_bytes_total`
- **網路流量**: `node_network_receive_bytes_total`, `node_network_transmit_bytes_total`

**數據層指標**:
- **PostgreSQL**: Connection pool usage, query duration, replication lag
- **Redis**: Hit rate, memory usage, evicted keys
- **RabbitMQ**: Queue depth, consumer count, message rate

**告警規則 (Alerting Rules)**:

| 告警名稱 | 觸發條件 | 嚴重程度 | 通知方式 |
|----------|----------|----------|----------|
| API 高延遲 | P95 延遲 > 1 秒持續 5 分鐘 | P1 | Slack |
| API 高錯誤率 | 錯誤率 > 5% 持續 3 分鐘 | P0 | PagerDuty + Slack |
| 磁碟空間不足 | 磁碟使用率 > 85% | P1 | Email |
| PostgreSQL 連線池耗盡 | 可用連線 < 10% | P0 | PagerDuty |
| RabbitMQ 積壓 | 佇列深度 > 1000 持續 10 分鐘 | P1 | Slack |

#### 2. Logs (日誌) - Structlog + (未來) ELK Stack

**日誌級別**:
- **DEBUG**: 詳細診斷資訊（僅開發環境）
- **INFO**: 一般業務流程（如「患者 X 提交日誌」）
- **WARNING**: 可恢復的錯誤（如「Redis 連線失敗，降級為數據庫查詢」）
- **ERROR**: 需要注意的錯誤（如「OpenAI API 呼叫失敗」）
- **CRITICAL**: 嚴重錯誤（如「數據庫連線完全失效」）

**結構化日誌範例**:
```json
{
  "timestamp": "2025-10-17T10:30:15.123Z",
  "level": "INFO",
  "logger": "respira_ally.application.use_cases.create_health_log",
  "message": "Health log created successfully",
  "request_id": "req-abc123",
  "user_id": "patient-xyz789",
  "patient_id": "patient-xyz789",
  "log_date": "2025-10-17",
  "duration_ms": 45
}
```

**日誌保留策略**:
- **Hot Storage** (Elasticsearch): 30 天，快速查詢
- **Warm Storage** (S3): 90 天，歸檔壓縮
- **Cold Storage** (Glacier): 1 年，長期合規保留

#### 3. Traces (追蹤) - (未來) OpenTelemetry + Jaeger

**追蹤範圍**:
- 跨服務請求鏈路（API Gateway → 患者服務 → PostgreSQL）
- 異步任務鏈路（RabbitMQ → AI Worker → OpenAI API）
- 關鍵業務流程（患者註冊、日誌提交、風險計算）

**採樣策略**:
- **生產環境**: 10% 採樣（降低開銷）
- **測試環境**: 100% 採樣（完整追蹤）
- **關鍵路徑**: 100% 採樣（如風險預警流程）

---

**故障定位流程 (Incident Response)**:

```mermaid
flowchart TD
    Alert[收到告警<br/>PagerDuty / Slack] --> Triage[查看 Grafana 儀表板]

    Triage --> MetricCheck{指標異常類型?}

    MetricCheck -->|API 延遲高| TraceAnalysis[查看 Jaeger Trace<br/>找慢查詢 SQL]
    MetricCheck -->|錯誤率高| LogAnalysis[查看 Elasticsearch<br/>錯誤日誌與堆疊]
    MetricCheck -->|資源不足| ScaleUp[水平擴展 Pod<br/>或垂直擴展資源]
    MetricCheck -->|外部依賴失效| Degrade[啟動降級策略<br/>切換備用方案]

    TraceAnalysis --> Fix1[優化 SQL 查詢<br/>或增加索引]
    LogAnalysis --> Fix2[修復代碼 Bug<br/>部署 Hotfix]
    ScaleUp --> Monitor[持續監控 30 分鐘]
    Degrade --> Monitor

    Fix1 & Fix2 --> Deploy[部署修復版本]
    Deploy --> Monitor
    Monitor --> Postmortem[撰寫事後檢討<br/>Post-Mortem]
```

**平均故障恢復時間 (MTTR) 目標**:
- **P0 故障**（服務完全不可用）: MTTR < 30 分鐘
- **P1 故障**（功能異常）: MTTR < 2 小時
- **P2 故障**（性能下降）: MTTR < 4 小時

**事後檢討範本 (Post-Mortem Template)**:
```markdown
# 事故報告 - [標題]

## 時間軸
- 10:30 - 系統檢測到異常（API 錯誤率 15%）
- 10:35 - PagerDuty 告警觸發
- 10:40 - 工程師開始調查
- 11:00 - 確認根本原因（PostgreSQL 連線池耗盡）
- 11:15 - 部署修復（增加連線池上限）
- 11:30 - 服務恢復正常

## 根本原因
- 新功能部署後，查詢頻率增加 3 倍
- 連線池配置（max=50）未隨之調整
- 缺乏連線池使用率監控告警

## 影響範圍
- 持續時間: 60 分鐘
- 受影響用戶: ~200 位患者（15% 請求失敗）
- 數據丟失: 無

## 修復措施
1. 立即: 增加連線池上限至 100
2. 短期: 新增連線池使用率告警
3. 長期: 實作自動擴展機制

## 經驗教訓
- 部署前未進行負載測試
- 缺乏容量規劃
- 需建立 Runbook 文件
```

---

## 10. 審查清單 (Architecture Review Checklist)

在完成架構設計後，請確認以下檢查項：

- [x] **C4 模型完整性**: 包含 Level 1 (Context) 和 Level 2 (Container)，清楚展示系統邊界與容器職責
- [x] **品質屬性可度量**: 所有品質屬性（可用性、性能、安全性）都有明確的目標值與度量方式
- [x] **技術選型有理由**: 每個關鍵技術選型都有對應的 ADR 文件說明理由與權衡
- [x] **界限上下文清晰**: DDD 戰略設計中的上下文邊界明確，上下文間關係清楚標示
- [x] **數據模型合理**: 數據模型遵循正規化原則，ER 圖清楚展示實體關係
- [x] **一致性策略明確**: 清楚區分強一致性與最終一致性的使用場景
- [x] **SPOF 識別與降級**: 識別所有單點故障，並提供降級策略與改進計畫
- [x] **演進性考量**: 識別易擴展部分與潛在瓶頸，提供技術棧升級計畫
- [x] **可觀測性設計**: 包含 Metrics, Logs, Traces 三支柱，定義告警規則與故障定位流程
- [x] **合規性考量**: 數據分類、加密、保留策略符合台灣個資法要求

---

## 11. 關聯文件 (Related Documents)

- **需求來源**: [02_product_requirements_document.md](./02_product_requirements_document.md) - 產品需求文件
- **決策記錄**: [adr/](./adr/) - 架構決策記錄目錄
- **資料庫設計**: [database/schema_design_v1.0.md](./database/schema_design_v1.0.md) - 完整資料庫設計文件
- **API 設計**: [06_api_design_specification.md](./06_api_design_specification.md) - 後端 API 規範文件
- **前端架構**: [12_frontend_architecture_specification.md](./12_frontend_architecture_specification.md) - 前端架構與技術棧規範
- **前端信息架構**: [17_frontend_information_architecture_template.md](./17_frontend_information_architecture_template.md) - 前端頁面結構與用戶旅程
- **模組規範**: [07_module_specification_and_tests.md](./07_module_specification_and_tests.md) - 模組設計與測試規範
- **BDD 場景**: [bdd/](./bdd/) - 行為驅動開發場景
- **專案 README**: [../README.md](../README.md) - 專案總覽文件
- **WBS 計畫**: [16_wbs_development_plan.md](./16_wbs_development_plan.md) - 工作分解結構與時程

---

## 附錄 A: 技術選型對照表

| 需求 | 候選方案 | 最終決策 | 決策依據 |
|------|----------|----------|----------|
| **Web 框架** | Flask vs FastAPI | FastAPI | ADR-001: 異步支持、自動文檔、型別檢查 |
| **數據庫** | PostgreSQL vs MySQL | PostgreSQL | 成熟穩定、pgvector 擴展、JSON 支持 |
| **向量資料庫** | Pinecone vs Qdrant vs pgvector | pgvector | ADR-002: MVP 簡化架構、成本低 |
| **事件日誌** | ~~MongoDB vs Elasticsearch~~ PostgreSQL JSONB | PostgreSQL JSONB | ADR-003 v2.0: 簡化技術棧、統一數據源 |
| **消息隊列** | RabbitMQ vs Kafka | RabbitMQ | ADR-005: 團隊熟悉、足夠滿足需求 |
| **緩存** | Redis vs Memcached | Redis | 數據結構豐富、持久化支持 |
| **前端框架** | Next.js vs Remix | Next.js | 生態成熟、SSR 性能優秀 |
| **LLM Provider** | OpenAI vs Anthropic | OpenAI | 文檔完善、社群支持強 |
| **部署平台** | Zeabur vs Railway vs Fly.io | Zeabur | 台灣在地服務、中文支持 |

---

## 附錄 B: 縮寫與術語表

| 縮寫 / 術語 | 全稱 / 解釋 |
|-------------|------------|
| **COPD** | Chronic Obstructive Pulmonary Disease (慢性阻塞性肺病) |
| **PHI** | Protected Health Information (受保護健康資訊) |
| **PII** | Personal Identifiable Information (個人身份資訊) |
| **RAG** | Retrieval-Augmented Generation (檢索增強生成) |
| **STT** | Speech-To-Text (語音轉文字) |
| **TTS** | Text-To-Speech (文字轉語音) |
| **LLM** | Large Language Model (大型語言模型) |
| **JWT** | JSON Web Token (JSON 網頁令牌) |
| **RBAC** | Role-Based Access Control (角色基礎存取控制) |
| **DDD** | Domain-Driven Design (領域驅動設計) |
| **CQRS** | Command Query Responsibility Segregation (命令查詢職責分離) |
| **SPOF** | Single Point of Failure (單點故障) |
| **MTTR** | Mean Time To Repair (平均故障恢復時間) |
| **RTO** | Recovery Time Objective (恢復時間目標) |
| **RPO** | Recovery Point Objective (恢復點目標) |
| **APM** | Application Performance Monitoring (應用性能監控) |

---


## 附錄 C: 事件驅動實作範例

本附錄提供事件驅動架構的完整實作代碼範例，展示如何在 RespiraAlly 中實現事件發布、訂閱與處理。

### C.1 實作範例

#### C.1.1 Publisher 實現 (發布事件)

**場景**: DailyLog Service 提交日誌後發布 `DailyLogSubmitted` 事件

```python
# modules/daily_log/domain/events.py
from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

@dataclass
class DailyLogSubmitted:
    """領域事件：日誌已提交"""
    log_id: UUID
    patient_id: UUID
    log_date: date
    medication_taken: bool
    water_intake_ml: int
    exercise_minutes: int
    symptoms: str
    submitted_at: datetime

    def to_dict(self) -> dict:
        return {
            "log_id": str(self.log_id),
            "patient_id": str(self.patient_id),
            "log_date": self.log_date.isoformat(),
            "medication_taken": self.medication_taken,
            "water_intake_ml": self.water_intake_ml,
            "exercise_minutes": self.exercise_minutes,
            "symptoms": self.symptoms,
            "submitted_at": self.submitted_at.isoformat()
        }

    @property
    def routing_key(self) -> str:
        return "daily_log.log.submitted"
```

```python
# modules/daily_log/application/use_cases/submit_daily_log.py
from modules.daily_log.domain.entities import DailyLog
from modules.daily_log.domain.events import DailyLogSubmitted
from modules.daily_log.domain.ports import IDailyLogRepository
from shared.event_bus import IEventBus
from shared.event_store import IEventStore

class SubmitDailyLogUseCase:
    def __init__(
        self,
        daily_log_repo: IDailyLogRepository,
        event_store: IEventStore,
        event_bus: IEventBus
    ):
        self.daily_log_repo = daily_log_repo
        self.event_store = event_store
        self.event_bus = event_bus

    async def execute(self, command: SubmitDailyLogCommand) -> DailyLog:
        # Step 1: 創建領域對象
        daily_log = DailyLog.create(
            patient_id=command.patient_id,
            log_date=command.log_date,
            medication_taken=command.medication_taken,
            water_intake_ml=command.water_intake_ml,
            # ...
        )

        # Step 2: 原子性操作 (在同一個事務中)
        async with self.db_session.begin():
            # 2a. 持久化聚合
            saved_log = await self.daily_log_repo.save(daily_log)

            # 2b. 保存事件到 event_logs (Outbox Pattern)
            event = DailyLogSubmitted(
                log_id=saved_log.log_id,
                patient_id=saved_log.patient_id,
                log_date=saved_log.log_date,
                medication_taken=saved_log.medication_taken,
                water_intake_ml=saved_log.water_intake_ml,
                exercise_minutes=saved_log.exercise_minutes,
                symptoms=saved_log.symptoms,
                submitted_at=datetime.utcnow()
            )

            await self.event_store.append(
                event_type="daily_log.DailyLogSubmitted",
                aggregate_id=saved_log.log_id,
                aggregate_type="DailyLog",
                payload=event.to_dict(),
                metadata={
                    "correlation_id": command.correlation_id,
                    "user_id": str(command.user_id)
                }
            )

        # Step 3: 事務成功提交，返回結果
        # (後台 Worker 會自動發布 event_logs 中未發布的事件)
        return saved_log
```

#### C.1.2 Subscriber 實現 (訂閱事件)

**場景**: Risk Service 訂閱 `DailyLogSubmitted` 事件，重新計算風險分數

```python
# modules/risk/application/event_handlers/daily_log_handler.py
from modules.risk.application.use_cases import CalculateRiskScoreUseCase
from modules.daily_log.domain.events import DailyLogSubmitted
from shared.event_bus import IEventHandler

class DailyLogSubmittedHandler(IEventHandler):
    """處理 DailyLogSubmitted 事件"""

    def __init__(self, calculate_risk_use_case: CalculateRiskScoreUseCase):
        self.calculate_risk_use_case = calculate_risk_use_case

    async def handle(self, event: DailyLogSubmitted):
        """處理事件邏輯"""
        try:
            # 觸發風險分數重新計算
            await self.calculate_risk_use_case.execute(
                patient_id=event.patient_id
            )

            logger.info(
                f"Risk score recalculated for patient {event.patient_id} "
                f"after log submission on {event.log_date}"
            )

        except Exception as e:
            logger.error(
                f"Failed to calculate risk for patient {event.patient_id}: {e}",
                exc_info=True
            )
            # 重新拋出異常，讓 RabbitMQ 重試
            raise
```

```python
# modules/risk/infrastructure/event_subscribers.py
from shared.rabbitmq import RabbitMQEventBus

async def setup_event_subscribers(event_bus: RabbitMQEventBus):
    """註冊所有事件訂閱者"""

    # 註冊 DailyLogSubmitted 事件處理器
    await event_bus.subscribe(
        queue_name="risk_service.log_events",
        binding_keys=["daily_log.log.submitted", "daily_log.log.deleted"],
        handler=DailyLogSubmittedHandler(calculate_risk_use_case),
        prefetch_count=10  # 每次預取 10 條訊息
    )

    # 註冊 SurveyCompleted 事件處理器
    await event_bus.subscribe(
        queue_name="risk_service.survey_events",
        binding_keys=["survey.survey.completed"],
        handler=SurveyCompletedHandler(calculate_risk_use_case),
        prefetch_count=10
    )
```

#### C.1.3 Event Bus 介面定義

```python
# shared/event_bus/interface.py
from abc import ABC, abstractmethod
from typing import Callable, List

class IEventBus(ABC):
    """事件總線接口 (Port)"""

    @abstractmethod
    async def publish(
        self,
        routing_key: str,
        payload: dict,
        metadata: dict = None
    ) -> None:
        """發布事件到 Exchange"""
        pass

    @abstractmethod
    async def subscribe(
        self,
        queue_name: str,
        binding_keys: List[str],
        handler: Callable,
        prefetch_count: int = 1
    ) -> None:
        """訂閱事件"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """關閉連接"""
        pass
```

```python
# shared/event_bus/rabbitmq_adapter.py
import aio_pika
import json
from shared.event_bus.interface import IEventBus

class RabbitMQEventBus(IEventBus):
    """RabbitMQ 事件總線實現 (Adapter)"""

    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self.connection = None
        self.channel = None
        self.exchange = None

    async def connect(self):
        """建立連接"""
        self.connection = await aio_pika.connect_robust(self.connection_url)
        self.channel = await self.connection.channel()

        # 聲明 Exchange
        self.exchange = await self.channel.declare_exchange(
            "respira.events",
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )

    async def publish(
        self,
        routing_key: str,
        payload: dict,
        metadata: dict = None
    ) -> None:
        """發布事件"""
        message_body = {
            "payload": payload,
            "metadata": metadata or {}
        }

        message = aio_pika.Message(
            body=json.dumps(message_body).encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT  # 持久化
        )

        await self.exchange.publish(
            message,
            routing_key=routing_key
        )

        logger.debug(f"Published event to {routing_key}")

    async def subscribe(
        self,
        queue_name: str,
        binding_keys: List[str],
        handler: Callable,
        prefetch_count: int = 1
    ) -> None:
        """訂閱事件"""
        # 設置 QoS
        await self.channel.set_qos(prefetch_count=prefetch_count)

        # 聲明 Queue
        queue = await self.channel.declare_queue(
            queue_name,
            durable=True,
            arguments={
                "x-message-ttl": 86400000,  # 24 小時
                "x-dead-letter-exchange": "respira.dlx"
            }
        )

        # 綁定 Routing Keys
        for binding_key in binding_keys:
            await queue.bind(self.exchange, routing_key=binding_key)

        # 開始消費
        async def on_message(message: aio_pika.IncomingMessage):
            async with message.process(requeue=False):
                try:
                    body = json.loads(message.body.decode())
                    await handler.handle(body["payload"])

                except Exception as e:
                    logger.error(f"Handler failed: {e}", exc_info=True)
                    # 訊息會進入 DLQ (因為 requeue=False)
                    raise

        await queue.consume(on_message)
        logger.info(f"Subscribed to {queue_name} with bindings: {binding_keys}")

    async def close(self):
        """關閉連接"""
        if self.connection:
            await self.connection.close()
```

#### C.1.4 完整流程範例 (端到端)

**場景**: 用戶提交日誌 → 觸發風險計算 → 發送通知

```mermaid
sequenceDiagram
    participant User as 用戶 (LINE)
    participant API as FastAPI
    participant LogUC as SubmitDailyLogUseCase
    participant DB as PostgreSQL
    participant Worker as Event Publisher Worker
    participant RabbitMQ as RabbitMQ
    participant RiskWorker as Risk Worker
    participant NotifWorker as Notification Worker

    User->>API: POST /api/v1/daily-logs
    API->>LogUC: execute(command)

    Note over LogUC,DB: 原子性事務
    LogUC->>DB: 1. INSERT INTO daily_logs
    LogUC->>DB: 2. INSERT INTO event_logs<br/>(is_published=false)
    DB-->>LogUC: 事務提交成功

    LogUC-->>API: 返回 201 Created
    API-->>User: 日誌提交成功

    Note over Worker,RabbitMQ: 後台異步發布
    loop 每 100ms
        Worker->>DB: SELECT * FROM event_logs<br/>WHERE is_published=false
        DB-->>Worker: 返回未發布事件
        Worker->>RabbitMQ: PUBLISH to respira.events<br/>Routing Key: daily_log.log.submitted
        Worker->>DB: UPDATE event_logs<br/>SET is_published=true
    end

    Note over RabbitMQ,RiskWorker: 風險計算
    RabbitMQ->>RiskWorker: Deliver: DailyLogSubmitted
    RiskWorker->>RiskWorker: CalculateRiskScoreUseCase.execute()
    RiskWorker->>DB: UPDATE risk_scores
    RiskWorker->>DB: INSERT INTO event_logs<br/>(RiskScoreCalculated)
    RiskWorker->>RabbitMQ: ACK

    Note over RabbitMQ,NotifWorker: 通知發送
    RabbitMQ->>NotifWorker: Deliver: RiskScoreCalculated
    NotifWorker->>NotifWorker: SendNotificationUseCase.execute()
    NotifWorker->>NotifWorker: LINE Push Message
    NotifWorker->>RabbitMQ: ACK
```

**時序說明**:
1. **同步階段** (0-200ms): 用戶提交日誌 → 數據持久化 → 返回成功
2. **異步階段** (200ms-5s): 事件發布 → 風險計算 → 通知發送
3. **失敗處理**: 任一階段失敗，不影響前序階段（最終一致性）

---


---

**文件結束** | 最後更新: 2025-10-19
