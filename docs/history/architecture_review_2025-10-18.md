# RespiraAlly V2.0 架構審視報告

**審視日期**: 2025-10-17
**審視者**: Claude Code AI (Linus 式審視)
**文件版本**: v1.0

---

## 執行摘要

基於 Linus Torvalds 的技術哲學對 RespiraAlly V2.0 架構進行深度審視，識別出 **7 個關鍵問題** 與 **12 個改進建議**。核心結論：**MVP 階段過度設計，需簡化架構並補充缺失的詳細設計**。

---

## 1. 三個前提問題

### Q1: 這是個真問題還是臆想出來的？
**答**: **部分是臆想的**。
- **真問題**: COPD 患者管理確實需要自動化、智能化
- **臆想問題**: MVP 階段就需要 8 個微服務？患者數 < 1000 時，微服務的複雜度 > 收益

### Q2: 有更簡單的方法嗎？
**答**: **有**。
- **當前方案**: 8 微服務 + 4 種數據庫 + 事件驅動
- **更簡單方案**: Modular Monolith (模組化單體) + PostgreSQL + Redis + 可選的 RabbitMQ
- **簡化後**: 開發效率 ↑, 部署複雜度 ↓, 運維成本 ↓

### Q3: 會破壞什麼嗎？
**答**: **不會破壞外部契約，但會增加內部複雜度**。
- 微服務拆分後，跨服務事務處理變複雜
- 分散式追蹤、監控成本增加
- 團隊協作需要更嚴格的 API 契約管理

---

## 2. 五層分析思考

### 第一層：數據結構分析

#### 問題 1: USERS 表繼承模式不夠清晰

**現狀**:
```sql
USERS {
    user_id PK
    role "PATIENT or THERAPIST"
}

PATIENTS {
    patient_id PK "FK to USERS.user_id"
}

THERAPISTS {
    therapist_id PK "FK to USERS.user_id"
}
```

**Linus 會說**: "這是個補丁設計。為什麼 `patient_id` 要等於 `user_id`？為什麼不直接用 `user_id`？"

**改進建議**:
```sql
-- 方案 A: 單表繼承（簡單但不夠優雅）
USERS {
    user_id PK
    role "PATIENT or THERAPIST"
    -- Patient 欄位
    therapist_id FK (nullable, 僅 PATIENT 使用)
    birth_date (nullable, 僅 PATIENT 使用)
    -- Therapist 欄位
    institution (nullable, 僅 THERAPIST 使用)
}

-- 方案 B: 類表繼承（複雜但結構清晰）- **推薦**
USERS {
    user_id PK
    line_user_id UK (nullable, 僅 PATIENT 使用)
    email UK (nullable, 僅 THERAPIST 使用)
    role "PATIENT or THERAPIST"
}

PATIENT_PROFILES {
    user_id PK FK "Reference to USERS"
    therapist_id FK
    name
    birth_date
}

THERAPIST_PROFILES {
    user_id PK FK "Reference to USERS"
    name
    institution
}
```

**理由**: 消除 `patient_id` 與 `user_id` 的冗餘，使關係更清晰。

---

#### 問題 2: 缺少關鍵索引設計

**現狀**: ER 圖沒有標示索引策略。

**Linus 會說**: "你知道查詢會怎麼跑嗎？沒有索引的數據模型是垃圾。"

**補充索引設計**:

```sql
-- DAILY_LOGS 表（高頻查詢表）
CREATE INDEX idx_daily_logs_patient_date ON DAILY_LOGS(patient_id, log_date DESC);
CREATE INDEX idx_daily_logs_created_at ON DAILY_LOGS(created_at DESC); -- 用於時間範圍查詢

-- RISK_SCORES 表
CREATE INDEX idx_risk_scores_patient_latest ON RISK_SCORES(patient_id, calculated_at DESC);
CREATE INDEX idx_risk_scores_level ON RISK_SCORES(score_level, calculated_at DESC); -- 用於篩選高風險患者

-- ALERTS 表
CREATE INDEX idx_alerts_therapist_status ON ALERTS(therapist_id, status, created_at DESC);
CREATE INDEX idx_alerts_patient_open ON ALERTS(patient_id, status) WHERE status = 'OPEN'; -- 部分索引

-- DOCUMENT_CHUNKS 表（向量檢索）
CREATE INDEX idx_chunks_embedding_ivfflat ON DOCUMENT_CHUNKS
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100); -- pgvector 索引
```

---

### 第二層：特殊情況識別

#### 問題 3: 微服務拆分過早，引入大量特殊情況

**現狀**: 8 個微服務在 MVP 階段。

**特殊情況**:
1. **跨服務事務**: 病患註冊需要 `AuthService` → `PatientService` → `LINEAdapter` 的 Saga 補償
2. **跨服務查詢**: 個案 360° 頁面需要聚合 4 個服務的數據
3. **分散式追蹤**: 需要引入 OpenTelemetry + Jaeger
4. **服務發現**: 需要配置服務註冊中心（雖然 Zeabur 簡化了這部分）

**Linus 會說**: "你為了『架構優雅』引入了 10 倍的複雜度。這不是好品味，這是過度設計。"

**改進建議**: **Modular Monolith（模組化單體）**

```
backend/
├── src/
│   ├── auth/          # 認證模組（獨立 bounded context）
│   ├── patients/      # 個案模組
│   ├── daily_logs/    # 日誌模組
│   ├── risk_engine/   # 風險引擎模組
│   ├── rag/           # RAG 模組
│   └── notifications/ # 通知模組
└── main.py            # 單一入口點，所有模組在同一 Process
```

**優勢**:
- ✅ **簡化事務**: 同一 Process 內，可用標準 SQLAlchemy Transaction
- ✅ **簡化查詢**: 同一數據庫內，可用 JOIN 而非 API 聚合
- ✅ **簡化部署**: 單一服務，單一容器
- ✅ **保留演進性**: 界限上下文清晰，未來可輕鬆拆分為微服務

---

### 第三層：複雜度審查

#### 問題 4: 技術棧過於複雜

**當前技術棧**:
- **數據層**: PostgreSQL + MongoDB + Redis + MinIO = 4 種存儲
- **消息隊列**: RabbitMQ
- **前端**: Next.js Dashboard + Vite LIFF
- **後端**: FastAPI × 8 微服務
- **AI**: OpenAI API (STT + LLM + TTS)
- **監控**: Prometheus + Grafana + Sentry + Jaeger

**Linus 會說**: "功能本質是什麼？**讓病患記錄健康日誌，讓治療師看到風險預警**。你需要 4 種數據庫來做這件事？"

**簡化方案**:

**MVP 階段（2026 Q1）**:
- **數據層**: PostgreSQL (主) + Redis (緩存) + MinIO (音檔)
  - 移除 MongoDB，事件日誌直接存 PostgreSQL 的 JSONB 欄位
  - 或使用 PostgreSQL 的 `pg_event_log` 擴展
- **消息隊列**: **可選** RabbitMQ
  - AI 語音處理量小時，可先用 Celery + Redis 替代
  - 等 AI 請求 > 100/day 再引入 RabbitMQ
- **監控**: Prometheus + Grafana (足夠)
  - 先不引入 Jaeger，使用 structlog + request_id 追蹤即可

---

### 第四層：破壞性分析

#### 問題 5: API 設計缺乏演進性保護

**現狀**: 文檔中缺少 API 版本策略與棄用策略。

**潛在破壞性風險**:
- API 欄位變更可能破壞 LIFF 客戶端
- 新增必填欄位會破壞舊版客戶端

**Linus 原則**: "We don't break userspace!"

**補充設計**:

**API 版本策略**:
```python
# 方案 A: URL 版本（推薦）
/api/v1/patients
/api/v2/patients  # 當 v1 需要重大變更時

# 方案 B: Header 版本
Accept: application/vnd.respira-ally.v1+json
```

**欄位演進規則**:
1. **新增欄位**: 必須為 Optional，提供默認值
2. **棄用欄位**: 保留 2 個版本週期（~6 個月），標記 `deprecated`
3. **變更欄位類型**: 視為破壞性變更，需發布新版本

**範例**:
```python
# ❌ 破壞性變更
class DailyLogRequest(BaseModel):
    water_intake_ml: int  # V1
    water_intake_liters: float  # V2 - 破壞了 V1

# ✅ 非破壞性變更
class DailyLogRequest(BaseModel):
    water_intake_ml: int
    water_intake_liters: Optional[float] = None  # V2 新增，V1 兼容
```

---

### 第五層：實用性驗證

#### 問題 6: MVP 目標不明確

**當前 MVP 定義**: "所有功能上線"（見 WBS 的 M4 里程碑）

**Linus 會說**: "什麼是 MVP？**Minimum Viable Product**。你的『所有功能』包含 AI 語音、RAG、風險引擎、週報...這叫 MVP？這叫 Maximum Viable Product。"

**真正的 MVP 應該是**:

**Phase 0: 最小可驗證核心（4 週）**
- ✅ 治療師登入
- ✅ 病患透過 LINE 註冊
- ✅ 病患提交每日健康日誌（用藥、飲水）
- ✅ 治療師查看病患列表與最近日誌
- ✅ 基礎風險評分（依從率計算）

**Phase 1: 增值功能（4 週）**
- ✅ CAT/mMRC 問卷
- ✅ 風險預警（異常規則引擎）
- ✅ 智慧提醒（12:00 問候 + 17:00/20:00 提醒）

**Phase 2: AI 能力（4 週）**
- ✅ RAG 知識庫
- ✅ AI 語音互動

**Phase 3: 優化上線（4 週）**
- ✅ 效能優化
- ✅ 生產部署

**理由**: 用 **4 週**驗證核心假設（病患願意每日記錄），而非 **16 週**後才知道方向錯誤。

---

## 3. 缺失的設計

### 缺失 1: 聚合根設計不完整

**現狀**: DDD 章節只提到界限上下文，沒有聚合根設計。

**補充**: [需在下一階段詳細設計]

**核心聚合根**:
1. **Patient Aggregate** (個案聚合)
   - Root: `Patient`
   - Entities: `PatientProfile`, `AssignedTherapist`
   - Value Objects: `BirthDate`, `ContactInfo`

2. **DailyLog Aggregate** (日誌聚合)
   - Root: `DailyLog`
   - Value Objects: `LogDate`, `MedicationStatus`, `WaterIntake`, `Symptoms`
   - Invariants: 每日僅一筆日誌 (`UNIQUE(patient_id, log_date)`)

3. **RiskScore Aggregate** (風險聚合)
   - Root: `RiskScore`
   - Entities: `RiskFactor[]`
   - Value Objects: `ScoreLevel(HIGH/MED/LOW)`

---

### 缺失 2: 事件清單不完整

**現狀**: 僅提到 2 個事件。

**補充完整領域事件**:

```python
# 認證上下文
class UserRegistered(DomainEvent):
    user_id: str
    role: str
    line_user_id: Optional[str]

# 個案上下文
class PatientCreated(DomainEvent):
    patient_id: str
    therapist_id: str

class PatientAssigned(DomainEvent):
    patient_id: str
    old_therapist_id: Optional[str]
    new_therapist_id: str

# 日誌上下文
class DailyLogSubmitted(DomainEvent):
    log_id: str
    patient_id: str
    log_date: date
    adherence_status: bool

# 風險上下文
class RiskScoreCalculated(DomainEvent):
    patient_id: str
    score: int
    level: str

class AlertTriggered(DomainEvent):
    alert_id: str
    patient_id: str
    reason: str
    severity: str

# 通知上下文
class NotificationSent(DomainEvent):
    notification_id: str
    recipient_id: str
    channel: str  # LINE, EMAIL
    status: str
```

---

### 缺失 3: API 錯誤處理標準

**現狀**: 架構文檔提到但未詳細定義。

**補充**: [需建立獨立文檔 `06_api_design_specification.md`]

**錯誤碼設計**:
```json
{
  "error": {
    "code": "DAILY_LOG_DUPLICATE",
    "message": "今日已提交日誌，請明日再試",
    "details": {
      "existing_log_id": "log-123",
      "log_date": "2025-10-17"
    },
    "request_id": "req-abc123"
  }
}
```

**標準錯誤碼前綴**:
- `AUTH_*`: 認證授權錯誤
- `PATIENT_*`: 個案相關錯誤
- `LOG_*`: 日誌相關錯誤
- `SYSTEM_*`: 系統錯誤

---

## 4. 改進建議總覽

### 立即行動（Sprint 0）

1. **簡化架構**: Modular Monolith 替代 8 微服務
2. **簡化技術棧**: 移除 MongoDB，使用 PostgreSQL JSONB
3. **重新定義 MVP**: Phase 0 (4 週核心驗證) 優先
4. **補充索引設計**: 在 ER 圖中標示所有索引
5. **補充 API 演進策略**: 版本控制 + 棄用政策

### 短期優化（Sprint 1-2）

6. **完善 DDD 設計**: 詳細設計 3 個核心聚合根
7. **定義完整事件清單**: 至少 10 個核心領域事件
8. **建立 API 規範文檔**: RESTful 設計 + 錯誤碼定義
9. **建立數據庫 Migration 策略**: Alembic 腳本規範

### 中長期演進（Sprint 3+）

10. **監控體系**: 先 Prometheus + Grafana，Phase 2 再引入 Jaeger
11. **AI 服務降級**: 先 OpenAI API，Phase 3 評估本地化
12. **微服務遷移準備**: 保持模組邊界清晰，為未來拆分做準備

---

## 5. 結論

### 核心判斷
❌ **不值得現在就這麼複雜**。

### 關鍵洞察
- **數據結構**: USERS 表繼承模式需優化，索引缺失嚴重
- **複雜度**: MVP 微服務 > 單體，違反 YAGNI 原則
- **風險點**: API 演進策略缺失，可能破壞客戶端

### 解決方案優先級

**P0 (必須做)**:
1. 簡化為 Modular Monolith
2. 補充索引設計
3. 定義 API 版本策略

**P1 (應該做)**:
4. 完善 DDD 聚合根設計
5. 定義完整事件清單
6. 建立 API 規範文檔

**P2 (可以做)**:
7. 簡化技術棧（移除 MongoDB）
8. 重新定義 MVP 範圍

---

## 6. Linus 式總結

> "好的架構不是設計出來的最複雜的，而是解決問題的最簡單的。你現在的架構解決了未來可能的問題，但增加了當下確定的複雜度。這是錯誤的權衡。"

**建議**: 回到基本面，先讓核心功能跑起來，再根據**真實數據**決定是否需要微服務、MongoDB、Jaeger。

---

**下一步**:
1. 基於本審視報告，修訂架構設計文檔
2. 開始詳細的 PostgreSQL Schema 設計
3. 建立 API 規範文檔
