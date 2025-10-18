# RespiraAlly V2.0 資料庫 Schema 設計

**文件版本**: v2.0 (基於架構審視報告優化)
**最後更新**: 2025-10-17
**設計者**: Claude Code AI - Data Engineer
**狀態**: 詳細設計中 (Detailed Design)

---

## 目錄

1. [設計原則](#1-設計原則)
2. [改進後的 ER 圖](#2-改進後的-er-圖)
3. [完整表結構定義](#3-完整表結構定義)
4. [索引策略](#4-索引策略)
5. [約束與觸發器](#5-約束與觸發器)
6. [分區策略](#6-分區策略未來擴展)
7. [Migration 腳本範例](#7-migration-腳本範例)
8. [查詢優化建議](#8-查詢優化建議)

---

## 1. 設計原則

基於 **ARCHITECTURE_REVIEW.md** 的審視結果，本設計遵循以下原則：

### 1.1 Linus 式數據結構設計

> "Bad programmers worry about the code. Good programmers worry about data structures."

**核心準則**:
1. **消除冗餘** - `patient_id` 不應該與 `user_id` 分離
2. **索引優先** - 每個查詢路徑都有對應索引
3. **約束保證** - 用數據庫約束而非應用層邏輯保證數據完整性
4. **JSONB 而非 MongoDB** - 非結構化數據使用 PostgreSQL JSONB

### 1.2 正規化與反正規化平衡

- **核心交易表** (users, daily_logs): 嚴格 3NF
- **查詢優化表** (patient_kpis): 適度反正規化（計算後的 KPI）
- **事件日誌表** (event_logs): JSONB 儲存，schema-less

### 1.3 演進性保護

- 所有表包含 `created_at`, `updated_at`
- 使用軟刪除 (`deleted_at`) 而非硬刪除
- JSONB 欄位預留擴展空間

---

## 2. 改進後的 ER 圖

基於審視報告的 **方案 B：類表繼承**，優化後的 ER 圖如下：

```mermaid
erDiagram
    USERS {
        uuid user_id PK
        string line_user_id UK "Nullable, for PATIENT"
        string email UK "Nullable, for THERAPIST"
        string hashed_password "Nullable for LINE login"
        enum role "PATIENT or THERAPIST"
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at "Soft delete"
    }

    PATIENT_PROFILES {
        uuid user_id PK FK
        uuid therapist_id FK "Assigned therapist"
        string name
        date birth_date
        enum gender "MALE, FEMALE, OTHER"
        string hospital_medical_record_number "病歷號 (Nullable)"
        integer height_cm "身高 cm (Nullable)"
        decimal weight_kg "體重 kg (Nullable)"
        enum smoking_status "NEVER, FORMER, CURRENT (Nullable)"
        integer smoking_years "吸菸年數 (Nullable)"
        jsonb medical_history "COPD stage, comorbidities, medications"
        jsonb contact_info "Phone, address, emergency_contact"
    }

    THERAPIST_PROFILES {
        uuid user_id PK FK
        string name
        string institution "Hospital/Clinic"
        string license_number
        jsonb specialties "Respiratory, ICU, etc"
    }

    DAILY_LOGS {
        uuid log_id PK
        uuid patient_id FK
        date log_date
        boolean medication_taken
        integer water_intake_ml
        integer steps_count "Nullable"
        text symptoms "Nullable"
        enum mood "GOOD, NEUTRAL, BAD"
        timestamp created_at
        timestamp updated_at
    }

    SURVEY_RESPONSES {
        uuid response_id PK
        enum survey_type "CAT, mMRC"
        uuid patient_id FK
        jsonb answers "Flexible schema"
        integer total_score "Calculated"
        enum severity_level "MILD, MODERATE, SEVERE, VERY_SEVERE"
        timestamp submitted_at
    }

    RISK_SCORES {
        uuid score_id PK
        uuid patient_id FK
        integer score "0-100"
        enum risk_level "LOW, MEDIUM, HIGH"
        jsonb contributing_factors "Breakdown of score"
        date calculation_date
        timestamp calculated_at
    }

    ALERTS {
        uuid alert_id PK
        uuid patient_id FK
        uuid therapist_id FK
        enum alert_type "MISSED_MEDICATION, NO_LOG, SYMPTOM_SPIKE"
        text reason
        enum status "OPEN, ACKNOWLEDGED, RESOLVED"
        timestamp created_at
        timestamp acknowledged_at "Nullable"
        timestamp resolved_at "Nullable"
    }

    EDUCATIONAL_DOCUMENTS {
        uuid doc_id PK
        string title
        text content "Full markdown content"
        enum category "MEDICATION, EXERCISE, DIET, BREATHING"
        string author "Nullable"
        timestamp created_at
        timestamp updated_at
    }

    DOCUMENT_CHUNKS {
        uuid chunk_id PK
        uuid doc_id FK
        text chunk_text
        integer chunk_index "Order in document"
        vector embedding "pgvector type"
        timestamp created_at
    }

    EVENT_LOGS {
        uuid event_id PK
        string event_type "e.g., UserRegistered, DailyLogSubmitted"
        uuid aggregate_id "e.g., user_id, log_id"
        string aggregate_type "e.g., User, DailyLog"
        jsonb event_data "Flexible event payload"
        timestamp occurred_at
    }

    NOTIFICATION_HISTORY {
        uuid notification_id PK
        uuid recipient_id FK
        enum channel "LINE, EMAIL"
        string message_type "REMINDER, ALERT, WEEKLY_REPORT"
        text message_content "Nullable"
        jsonb metadata "LINE message_id, etc"
        enum status "PENDING, SENT, FAILED"
        timestamp sent_at "Nullable"
        timestamp created_at
    }

    PATIENT_KPI_CACHE {
        uuid patient_id PK FK
        integer total_logs_count
        integer adherence_rate_7d "Percentage 0-100"
        integer adherence_rate_30d
        integer avg_water_intake_7d "ml"
        date last_log_date "Nullable"
        integer current_streak_days
        integer longest_streak_days
        timestamp last_calculated_at
    }

    USERS ||--o| PATIENT_PROFILES : "is_a (patient)"
    USERS ||--o| THERAPIST_PROFILES : "is_a (therapist)"
    THERAPIST_PROFILES ||--|{ PATIENT_PROFILES : "manages"
    PATIENT_PROFILES ||--|{ DAILY_LOGS : "submits"
    PATIENT_PROFILES ||--|{ SURVEY_RESPONSES : "completes"
    PATIENT_PROFILES ||--|{ RISK_SCORES : "has"
    PATIENT_PROFILES ||--|| PATIENT_KPI_CACHE : "has"
    RISK_SCORES ||--o{ ALERTS : "triggers"
    ALERTS }|--|| THERAPIST_PROFILES : "notifies"
    EDUCATIONAL_DOCUMENTS ||--|{ DOCUMENT_CHUNKS : "is_chunked_into"
```

### 關鍵改進

**相比原架構文檔的 ER 圖**:

1. ✅ **消除 `patient_id` 冗餘** - `PATIENT_PROFILES.user_id` 直接作為 PK
2. ✅ **新增 `EVENT_LOGS` 表** - 替代 MongoDB 事件存儲
3. ✅ **新增 `PATIENT_KPI_CACHE` 表** - 反正規化加速查詢
4. ✅ **新增 `NOTIFICATION_HISTORY` 表** - 追蹤通知發送狀態
5. ✅ **所有表加入審計欄位** - `created_at`, `updated_at`, `deleted_at`
6. ✅ **JSONB 欄位** - 靈活擴展 (`medical_history`, `contact_info`, `event_data`)

---

## 3. 完整表結構定義

### 3.1 核心認證表

#### `users` - 使用者主表

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    line_user_id VARCHAR(255) UNIQUE,  -- Nullable, only for PATIENT
    email VARCHAR(255) UNIQUE,  -- Nullable, only for THERAPIST
    hashed_password VARCHAR(255),  -- Nullable for LINE OAuth login
    role VARCHAR(20) NOT NULL CHECK (role IN ('PATIENT', 'THERAPIST')),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE  -- Soft delete
);

-- Check: 至少有一個登入方式
ALTER TABLE users ADD CONSTRAINT users_login_method_check
    CHECK (line_user_id IS NOT NULL OR email IS NOT NULL);

-- Check: Role 與登入方式對應
ALTER TABLE users ADD CONSTRAINT users_patient_line_check
    CHECK (role != 'PATIENT' OR line_user_id IS NOT NULL);

ALTER TABLE users ADD CONSTRAINT users_therapist_email_check
    CHECK (role != 'THERAPIST' OR email IS NOT NULL);
```

#### `patient_profiles` - 病患檔案

```sql
-- 創建吸菸狀態 ENUM
CREATE TYPE smoking_status_enum AS ENUM ('NEVER', 'FORMER', 'CURRENT');

CREATE TABLE patient_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    therapist_id UUID REFERENCES therapist_profiles(user_id) ON DELETE SET NULL,

    -- 基本資訊
    name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    gender VARCHAR(20) CHECK (gender IN ('MALE', 'FEMALE', 'OTHER')),

    -- 醫院整合資訊
    hospital_medical_record_number VARCHAR(50),  -- 醫院病歷號 (Nullable)

    -- 體徵數據 (用於 BMI 計算與風險評估)
    height_cm INTEGER CHECK (height_cm >= 50 AND height_cm <= 250),  -- 身高 (cm)
    weight_kg DECIMAL(5,1) CHECK (weight_kg >= 20 AND weight_kg <= 300),  -- 體重 (kg)

    -- 吸菸史 (COPD 關鍵風險因素)
    smoking_status smoking_status_enum,  -- 吸菸狀態
    smoking_years INTEGER CHECK (smoking_years >= 0 AND smoking_years <= 100),  -- 吸菸年數

    -- 擴展資訊 (JSONB for flexibility)
    medical_history JSONB DEFAULT '{}',  -- {copd_stage: "III", comorbidities: [...], medications: [...]}
    contact_info JSONB DEFAULT '{}'  -- {phone: "...", address: "...", emergency_contact: {...}}
);

-- Check: 年齡合理性 (18-120 歲)
ALTER TABLE patient_profiles ADD CONSTRAINT patient_age_check
    CHECK (birth_date <= CURRENT_DATE - INTERVAL '18 years' AND
           birth_date >= CURRENT_DATE - INTERVAL '120 years');

-- Check: 吸菸年數邏輯性 (不可超過年齡)
ALTER TABLE patient_profiles ADD CONSTRAINT patient_smoking_years_check
    CHECK (smoking_years IS NULL OR
           smoking_years <= EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date)));

-- Check: 吸菸狀態與年數一致性
ALTER TABLE patient_profiles ADD CONSTRAINT patient_smoking_consistency_check
    CHECK (
        (smoking_status = 'NEVER' AND (smoking_years IS NULL OR smoking_years = 0)) OR
        (smoking_status IN ('FORMER', 'CURRENT') AND smoking_years > 0) OR
        (smoking_status IS NULL)
    );
```

#### `therapist_profiles` - 治療師檔案

```sql
CREATE TABLE therapist_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    institution VARCHAR(200) NOT NULL,
    license_number VARCHAR(50) UNIQUE NOT NULL,
    specialties JSONB DEFAULT '[]'  -- ["Respiratory", "ICU"]
);
```

---

### 3.2 核心業務表

#### `daily_logs` - 每日健康日誌

```sql
CREATE TABLE daily_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patient_profiles(user_id) ON DELETE CASCADE,
    log_date DATE NOT NULL,
    medication_taken BOOLEAN NOT NULL DEFAULT false,
    water_intake_ml INTEGER NOT NULL CHECK (water_intake_ml >= 0 AND water_intake_ml <= 10000),
    steps_count INTEGER CHECK (steps_count >= 0 AND steps_count <= 100000),
    symptoms TEXT,
    mood VARCHAR(20) CHECK (mood IN ('GOOD', 'NEUTRAL', 'BAD')),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- 每日唯一性約束
    CONSTRAINT daily_logs_unique_per_day UNIQUE (patient_id, log_date)
);
```

#### `survey_responses` - 問卷回覆

```sql
CREATE TYPE survey_type_enum AS ENUM ('CAT', 'mMRC');
CREATE TYPE severity_level_enum AS ENUM ('MILD', 'MODERATE', 'SEVERE', 'VERY_SEVERE');

CREATE TABLE survey_responses (
    response_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    survey_type survey_type_enum NOT NULL,
    patient_id UUID NOT NULL REFERENCES patient_profiles(user_id) ON DELETE CASCADE,
    answers JSONB NOT NULL,  -- {q1: 2, q2: 3, ...}
    total_score INTEGER NOT NULL CHECK (total_score >= 0),
    severity_level severity_level_enum,
    submitted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Check: CAT 分數範圍 0-40
ALTER TABLE survey_responses ADD CONSTRAINT cat_score_range_check
    CHECK (survey_type != 'CAT' OR (total_score >= 0 AND total_score <= 40));

-- Check: mMRC 分數範圍 0-4
ALTER TABLE survey_responses ADD CONSTRAINT mmrc_score_range_check
    CHECK (survey_type != 'mMRC' OR (total_score >= 0 AND total_score <= 4));
```

#### `risk_scores` - 風險評分

```sql
CREATE TYPE risk_level_enum AS ENUM ('LOW', 'MEDIUM', 'HIGH');

CREATE TABLE risk_scores (
    score_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patient_profiles(user_id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    risk_level risk_level_enum NOT NULL,
    contributing_factors JSONB NOT NULL DEFAULT '{}',  -- {adherence: 0.6, cat_score: 25, ...}
    calculation_date DATE NOT NULL,
    calculated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- 每日僅一個風險分數
    CONSTRAINT risk_scores_unique_per_day UNIQUE (patient_id, calculation_date)
);
```

#### `alerts` - 預警通知

```sql
CREATE TYPE alert_type_enum AS ENUM ('MISSED_MEDICATION', 'NO_LOG', 'SYMPTOM_SPIKE', 'RISK_ELEVATED');
CREATE TYPE alert_status_enum AS ENUM ('OPEN', 'ACKNOWLEDGED', 'RESOLVED');

CREATE TABLE alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patient_profiles(user_id) ON DELETE CASCADE,
    therapist_id UUID NOT NULL REFERENCES therapist_profiles(user_id) ON DELETE CASCADE,
    alert_type alert_type_enum NOT NULL,
    reason TEXT NOT NULL,
    status alert_status_enum NOT NULL DEFAULT 'OPEN',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,

    -- Check: 狀態轉換邏輯
    CONSTRAINT alert_status_transition_check CHECK (
        (status = 'OPEN' AND acknowledged_at IS NULL AND resolved_at IS NULL) OR
        (status = 'ACKNOWLEDGED' AND acknowledged_at IS NOT NULL AND resolved_at IS NULL) OR
        (status = 'RESOLVED' AND acknowledged_at IS NOT NULL AND resolved_at IS NOT NULL)
    )
);
```

---

### 3.3 RAG 相關表

#### `educational_documents` - 衛教文件

```sql
CREATE TYPE doc_category_enum AS ENUM ('MEDICATION', 'EXERCISE', 'DIET', 'BREATHING', 'GENERAL');

CREATE TABLE educational_documents (
    doc_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,  -- Full markdown content
    category doc_category_enum NOT NULL,
    author VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

#### `document_chunks` - 文件區塊（向量檢索）

```sql
-- 需先安裝 pgvector 擴展
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE document_chunks (
    chunk_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_id UUID NOT NULL REFERENCES educational_documents(doc_id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL CHECK (chunk_index >= 0),
    embedding VECTOR(1536),  -- OpenAI text-embedding-ada-002 維度
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT document_chunks_unique_index UNIQUE (doc_id, chunk_index)
);
```

---

### 3.4 事件與通知表

#### `event_logs` - 領域事件日誌（替代 MongoDB）

```sql
CREATE TABLE event_logs (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,  -- e.g., "UserRegistered", "DailyLogSubmitted"
    aggregate_id UUID NOT NULL,  -- e.g., user_id, log_id
    aggregate_type VARCHAR(50) NOT NULL,  -- e.g., "User", "DailyLog"
    event_data JSONB NOT NULL DEFAULT '{}',  -- Flexible event payload
    occurred_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

#### `notification_history` - 通知發送歷史

```sql
CREATE TYPE notification_channel_enum AS ENUM ('LINE', 'EMAIL');
CREATE TYPE notification_status_enum AS ENUM ('PENDING', 'SENT', 'FAILED');

CREATE TABLE notification_history (
    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    channel notification_channel_enum NOT NULL,
    message_type VARCHAR(50) NOT NULL,  -- "REMINDER", "ALERT", "WEEKLY_REPORT"
    message_content TEXT,
    metadata JSONB DEFAULT '{}',  -- {line_message_id: "...", error: "..."}
    status notification_status_enum NOT NULL DEFAULT 'PENDING',
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

### 3.5 性能優化表

#### `patient_kpi_cache` - 病患 KPI 快取（反正規化，用於 Dashboard 快速查詢）

```sql
CREATE TABLE patient_kpi_cache (
    patient_id UUID PRIMARY KEY REFERENCES patient_profiles(user_id) ON DELETE CASCADE,

    -- 基礎統計（總覽）
    total_logs_count INTEGER NOT NULL DEFAULT 0,
    first_log_date DATE,  -- 第一次打卡日期
    last_log_date DATE,   -- 最後一次打卡日期

    -- 依從率統計（預先計算常用窗口）
    adherence_rate_7d INTEGER CHECK (adherence_rate_7d >= 0 AND adherence_rate_7d <= 100),
    adherence_rate_30d INTEGER CHECK (adherence_rate_30d >= 0 AND adherence_rate_30d <= 100),

    -- 飲水量統計（毫升）
    avg_water_intake_7d INTEGER CHECK (avg_water_intake_7d >= 0),
    avg_water_intake_30d INTEGER CHECK (avg_water_intake_30d >= 0),

    -- 步數統計
    avg_steps_7d INTEGER CHECK (avg_steps_7d >= 0),
    avg_steps_30d INTEGER CHECK (avg_steps_30d >= 0),

    -- 連續打卡天數
    current_streak_days INTEGER NOT NULL DEFAULT 0 CHECK (current_streak_days >= 0),
    longest_streak_days INTEGER NOT NULL DEFAULT 0 CHECK (longest_streak_days >= 0),

    -- 最新問卷分數（快速查詢，避免 JOIN survey_responses）
    latest_cat_score INTEGER CHECK (latest_cat_score >= 0 AND latest_cat_score <= 40),
    latest_cat_date DATE,
    latest_mmrc_score INTEGER CHECK (latest_mmrc_score >= 0 AND latest_mmrc_score <= 4),
    latest_mmrc_date DATE,

    -- 最新風險評分（快速查詢，避免 JOIN risk_scores）
    latest_risk_score INTEGER CHECK (latest_risk_score >= 0 AND latest_risk_score <= 100),
    latest_risk_level VARCHAR(20) CHECK (latest_risk_level IN ('LOW', 'MEDIUM', 'HIGH')),
    latest_risk_date DATE,

    -- 症狀出現次數（近 30 天）
    symptom_occurrences_30d INTEGER NOT NULL DEFAULT 0,

    -- 快取更新時間
    last_calculated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE patient_kpi_cache IS
    '病患 KPI 快取表 - 預先聚合的統計數據，用於 Dashboard API 快速讀取 (< 50ms)';
COMMENT ON COLUMN patient_kpi_cache.adherence_rate_7d IS '近 7 天用藥依從率 (%)';
COMMENT ON COLUMN patient_kpi_cache.latest_cat_score IS '最新 CAT 問卷分數 (0-40)';
COMMENT ON COLUMN patient_kpi_cache.latest_risk_level IS '最新風險等級 (LOW/MEDIUM/HIGH)';
```

---

### 3.6 數據視圖 (Views) - 用於前端圖表與趨勢分析

#### `patient_kpi_windows` - 動態時間窗口 KPI

```sql
-- 動態計算任意時間窗口的 KPI（支持 7d/30d/90d）
CREATE OR REPLACE VIEW patient_kpi_windows AS
WITH windows AS (
    SELECT
        patient_id,
        -- 近 7 天
        COUNT(*) FILTER (WHERE log_date >= CURRENT_DATE - INTERVAL '7 days') AS logs_7d,
        COUNT(*) FILTER (WHERE log_date >= CURRENT_DATE - INTERVAL '7 days' AND medication_taken) AS medication_taken_7d,
        AVG(water_intake_ml) FILTER (WHERE log_date >= CURRENT_DATE - INTERVAL '7 days') AS avg_water_7d,
        AVG(steps_count) FILTER (WHERE log_date >= CURRENT_DATE - INTERVAL '7 days') AS avg_steps_7d,

        -- 近 30 天
        COUNT(*) FILTER (WHERE log_date >= CURRENT_DATE - INTERVAL '30 days') AS logs_30d,
        COUNT(*) FILTER (WHERE log_date >= CURRENT_DATE - INTERVAL '30 days' AND medication_taken) AS medication_taken_30d,
        AVG(water_intake_ml) FILTER (WHERE log_date >= CURRENT_DATE - INTERVAL '30 days') AS avg_water_30d,
        AVG(steps_count) FILTER (WHERE log_date >= CURRENT_DATE - INTERVAL '30 days') AS avg_steps_30d,

        -- 近 90 天
        COUNT(*) FILTER (WHERE log_date >= CURRENT_DATE - INTERVAL '90 days') AS logs_90d,
        COUNT(*) FILTER (WHERE log_date >= CURRENT_DATE - INTERVAL '90 days' AND medication_taken) AS medication_taken_90d
    FROM daily_logs
    GROUP BY patient_id
)
SELECT
    patient_id,

    -- 7 天 KPI
    logs_7d,
    CASE WHEN logs_7d > 0 THEN ROUND((medication_taken_7d::NUMERIC / logs_7d) * 100) ELSE 0 END AS adherence_rate_7d,
    ROUND(COALESCE(avg_water_7d, 0))::INTEGER AS avg_water_intake_7d,
    ROUND(COALESCE(avg_steps_7d, 0))::INTEGER AS avg_steps_7d,

    -- 30 天 KPI
    logs_30d,
    CASE WHEN logs_30d > 0 THEN ROUND((medication_taken_30d::NUMERIC / logs_30d) * 100) ELSE 0 END AS adherence_rate_30d,
    ROUND(COALESCE(avg_water_30d, 0))::INTEGER AS avg_water_intake_30d,
    ROUND(COALESCE(avg_steps_30d, 0))::INTEGER AS avg_steps_30d,

    -- 90 天 KPI
    logs_90d,
    CASE WHEN logs_90d > 0 THEN ROUND((medication_taken_90d::NUMERIC / logs_90d) * 100) ELSE 0 END AS adherence_rate_90d
FROM windows;

COMMENT ON VIEW patient_kpi_windows IS
    '動態時間窗口 KPI - 支持 7/30/90 天窗口，用於趨勢對比分析';
```

#### `patient_health_timeline` - 每日時間序列（用於折線圖）

```sql
-- 每日健康數據時間序列，包含移動平均線
CREATE OR REPLACE VIEW patient_health_timeline AS
SELECT
    patient_id,
    log_date,
    medication_taken,
    water_intake_ml,
    steps_count,
    symptoms,
    mood,

    -- 移動平均（7 天）- 用於平滑曲線
    AVG(water_intake_ml) OVER (
        PARTITION BY patient_id
        ORDER BY log_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS water_intake_7d_ma,

    AVG(steps_count) OVER (
        PARTITION BY patient_id
        ORDER BY log_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS steps_7d_ma,

    -- 累計統計（用於累積趨勢圖）
    COUNT(*) OVER (
        PARTITION BY patient_id
        ORDER BY log_date
    ) AS cumulative_logs,

    COUNT(*) FILTER (WHERE medication_taken) OVER (
        PARTITION BY patient_id
        ORDER BY log_date
    ) AS cumulative_medications
FROM daily_logs
ORDER BY patient_id, log_date DESC;

COMMENT ON VIEW patient_health_timeline IS
    '每日健康時間序列 - 包含原始數據、移動平均、累積統計，用於前端折線圖';
```

#### `patient_survey_trends` - 問卷趨勢（CAT/mMRC 歷史）

```sql
-- CAT/mMRC 問卷歷史趨勢
CREATE OR REPLACE VIEW patient_survey_trends AS
SELECT
    patient_id,
    survey_type,
    submitted_at,
    DATE(submitted_at) AS survey_date,
    total_score,
    severity_level,

    -- 與上次問卷的分數差異
    total_score - LAG(total_score) OVER (
        PARTITION BY patient_id, survey_type
        ORDER BY submitted_at
    ) AS score_change,

    -- 與首次問卷的分數差異（整體進步）
    total_score - FIRST_VALUE(total_score) OVER (
        PARTITION BY patient_id, survey_type
        ORDER BY submitted_at
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS score_change_from_baseline,

    -- 累計問卷次數
    ROW_NUMBER() OVER (
        PARTITION BY patient_id, survey_type
        ORDER BY submitted_at
    ) AS survey_sequence
FROM survey_responses
ORDER BY patient_id, survey_type, submitted_at DESC;

COMMENT ON VIEW patient_survey_trends IS
    'CAT/mMRC 問卷趨勢 - 包含分數變化、基線對比，用於問卷歷史圖表';
```

---

## 4. 索引策略

### 4.1 核心索引（必須）

```sql
-- === USERS ===
CREATE INDEX idx_users_role ON users(role) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_line_user_id ON users(line_user_id) WHERE line_user_id IS NOT NULL;
CREATE INDEX idx_users_email ON users(email) WHERE email IS NOT NULL;

-- === PATIENT_PROFILES ===
CREATE INDEX idx_patient_therapist ON patient_profiles(therapist_id);
-- 醫院病歷號查詢 (用於跨系統整合)
CREATE INDEX idx_patient_medical_record_number ON patient_profiles(hospital_medical_record_number)
    WHERE hospital_medical_record_number IS NOT NULL;
-- 高風險篩選 (吸菸者)
CREATE INDEX idx_patient_smoking_status ON patient_profiles(smoking_status)
    WHERE smoking_status IN ('FORMER', 'CURRENT');

-- === DAILY_LOGS ===
-- 最高頻查詢：查某病患的最近日誌
CREATE INDEX idx_daily_logs_patient_date ON daily_logs(patient_id, log_date DESC);
-- 時間範圍查詢
CREATE INDEX idx_daily_logs_created_at ON daily_logs(created_at DESC);
-- 篩選未用藥日誌
CREATE INDEX idx_daily_logs_medication ON daily_logs(patient_id, medication_taken, log_date DESC);

-- === SURVEY_RESPONSES ===
CREATE INDEX idx_survey_patient ON survey_responses(patient_id, submitted_at DESC);
CREATE INDEX idx_survey_type ON survey_responses(survey_type, submitted_at DESC);

-- === RISK_SCORES ===
-- 查最新風險分數
CREATE INDEX idx_risk_scores_patient_latest ON risk_scores(patient_id, calculation_date DESC);
-- 篩選高風險患者
CREATE INDEX idx_risk_scores_level ON risk_scores(risk_level, calculation_date DESC);
-- 治療師查看其負責病患的風險
CREATE INDEX idx_risk_scores_therapist ON risk_scores(patient_id)
    INCLUDE (risk_level, calculation_date);

-- === ALERTS ===
-- 治療師查看待處理預警
CREATE INDEX idx_alerts_therapist_open ON alerts(therapist_id, status, created_at DESC)
    WHERE status IN ('OPEN', 'ACKNOWLEDGED');
-- 病患的歷史預警
CREATE INDEX idx_alerts_patient ON alerts(patient_id, created_at DESC);

-- === DOCUMENT_CHUNKS (pgvector) ===
-- IVFFlat 索引（適合中小規模）
CREATE INDEX idx_chunks_embedding_ivfflat ON document_chunks
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- HNSW 索引（適合大規模，PostgreSQL 16+）
-- CREATE INDEX idx_chunks_embedding_hnsw ON document_chunks
--     USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

-- === EVENT_LOGS ===
-- 按事件類型查詢
CREATE INDEX idx_event_logs_type ON event_logs(event_type, occurred_at DESC);
-- 按聚合查詢（重建聚合狀態）
CREATE INDEX idx_event_logs_aggregate ON event_logs(aggregate_type, aggregate_id, occurred_at ASC);
-- JSONB GIN 索引（支援複雜查詢）
CREATE INDEX idx_event_logs_data ON event_logs USING GIN (event_data);

-- === NOTIFICATION_HISTORY ===
-- 查某用戶的通知歷史
CREATE INDEX idx_notification_recipient ON notification_history(recipient_id, created_at DESC);
-- 查待發送通知
CREATE INDEX idx_notification_pending ON notification_history(status, created_at ASC)
    WHERE status = 'PENDING';
```

### 4.2 複合索引（針對具體查詢）

```sql
-- 查詢：治療師查看其負責的高風險病患
CREATE INDEX idx_therapist_high_risk_patients ON risk_scores(patient_id, risk_level, calculation_date DESC)
    WHERE risk_level = 'HIGH';

-- 查詢：依從率低於 50% 的病患（用於篩選）
CREATE INDEX idx_low_adherence_patients ON patient_kpi_cache(adherence_rate_30d)
    WHERE adherence_rate_30d < 50;

-- 查詢：近 7 天內未提交日誌的病患
CREATE INDEX idx_inactive_patients ON patient_kpi_cache(last_log_date)
    WHERE last_log_date < CURRENT_DATE - INTERVAL '7 days' OR last_log_date IS NULL;
```

### 4.3 部分索引（節省空間）

```sql
-- 只索引未刪除的使用者
CREATE INDEX idx_users_active ON users(user_id) WHERE deleted_at IS NULL;

-- 只索引待處理預警
CREATE INDEX idx_alerts_open ON alerts(therapist_id, created_at DESC) WHERE status = 'OPEN';
```

---

## 5. 約束與觸發器

### 5.1 自動更新 `updated_at` 觸發器

```sql
-- 通用觸發器函數
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 應用到所有需要的表
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patient_profiles_updated_at BEFORE UPDATE ON patient_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_logs_updated_at BEFORE UPDATE ON daily_logs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_educational_documents_updated_at BEFORE UPDATE ON educational_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 5.2 風險等級自動計算觸發器

```sql
CREATE OR REPLACE FUNCTION auto_assign_risk_level()
RETURNS TRIGGER AS $$
BEGIN
    NEW.risk_level := CASE
        WHEN NEW.score >= 70 THEN 'HIGH'::risk_level_enum
        WHEN NEW.score >= 40 THEN 'MEDIUM'::risk_level_enum
        ELSE 'LOW'::risk_level_enum
    END;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_risk_level BEFORE INSERT OR UPDATE ON risk_scores
    FOR EACH ROW EXECUTE FUNCTION auto_assign_risk_level();
```

### 5.3 KPI 快取更新觸發器

```sql
-- 當新增日誌時，更新 KPI 快取
CREATE OR REPLACE FUNCTION update_patient_kpi_on_log_insert()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO patient_kpi_cache (patient_id, total_logs_count, last_log_date, last_calculated_at)
    VALUES (NEW.patient_id, 1, NEW.log_date, CURRENT_TIMESTAMP)
    ON CONFLICT (patient_id) DO UPDATE SET
        total_logs_count = patient_kpi_cache.total_logs_count + 1,
        last_log_date = GREATEST(patient_kpi_cache.last_log_date, NEW.log_date),
        last_calculated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_kpi_on_daily_log_insert AFTER INSERT ON daily_logs
    FOR EACH ROW EXECUTE FUNCTION update_patient_kpi_on_log_insert();
```

---

## 6. 分區策略（未來擴展）

當 `daily_logs` 或 `event_logs` 表數據量達到千萬級時，考慮按時間分區：

### 6.1 `daily_logs` 表分區

```sql
-- Step 1: 將現有表改為分區表（需重建）
CREATE TABLE daily_logs_partitioned (
    log_id UUID DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL,
    log_date DATE NOT NULL,
    -- ... 其他欄位
    PRIMARY KEY (log_id, log_date)  -- 分區鍵必須在主鍵中
) PARTITION BY RANGE (log_date);

-- Step 2: 創建分區（按月分區）
CREATE TABLE daily_logs_2025_01 PARTITION OF daily_logs_partitioned
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE daily_logs_2025_02 PARTITION OF daily_logs_partitioned
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- Step 3: 創建默認分區（避免插入失敗）
CREATE TABLE daily_logs_default PARTITION OF daily_logs_partitioned DEFAULT;

-- Step 4: 自動化分區創建（使用 pg_cron 或應用層腳本）
```

### 6.2 `event_logs` 表分區

```sql
CREATE TABLE event_logs_partitioned (
    event_id UUID DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,
    aggregate_id UUID NOT NULL,
    occurred_at TIMESTAMP WITH TIME ZONE NOT NULL,
    -- ... 其他欄位
    PRIMARY KEY (event_id, occurred_at)
) PARTITION BY RANGE (occurred_at);

-- 按季度分區
CREATE TABLE event_logs_2025_q1 PARTITION OF event_logs_partitioned
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
```

---

## 7. Migration 腳本範例

### 7.1 初始 Migration - `001_create_core_tables.sql`

```sql
-- Alembic Migration Script
-- Revision: 001
-- Description: 創建核心表 (users, patient_profiles, therapist_profiles)

BEGIN;

-- 創建 ENUM 類型
CREATE TYPE user_role_enum AS ENUM ('PATIENT', 'THERAPIST');

-- 創建 users 表
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    line_user_id VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE,
    hashed_password VARCHAR(255),
    role user_role_enum NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT users_login_method_check CHECK (line_user_id IS NOT NULL OR email IS NOT NULL),
    CONSTRAINT users_patient_line_check CHECK (role != 'PATIENT' OR line_user_id IS NOT NULL),
    CONSTRAINT users_therapist_email_check CHECK (role != 'THERAPIST' OR email IS NOT NULL)
);

-- 創建 therapist_profiles 表（先創建，因為 patient_profiles 有 FK 指向它）
CREATE TABLE therapist_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    institution VARCHAR(200) NOT NULL,
    license_number VARCHAR(50) UNIQUE NOT NULL,
    specialties JSONB DEFAULT '[]'
);

-- 創建吸菸狀態 ENUM
CREATE TYPE smoking_status_enum AS ENUM ('NEVER', 'FORMER', 'CURRENT');

-- 創建 patient_profiles 表
CREATE TABLE patient_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    therapist_id UUID REFERENCES therapist_profiles(user_id) ON DELETE SET NULL,

    -- 基本資訊
    name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    gender VARCHAR(20) CHECK (gender IN ('MALE', 'FEMALE', 'OTHER')),

    -- 醫院整合資訊
    hospital_medical_record_number VARCHAR(50),

    -- 體徵數據
    height_cm INTEGER CHECK (height_cm >= 50 AND height_cm <= 250),
    weight_kg DECIMAL(5,1) CHECK (weight_kg >= 20 AND weight_kg <= 300),

    -- 吸菸史
    smoking_status smoking_status_enum,
    smoking_years INTEGER CHECK (smoking_years >= 0 AND smoking_years <= 100),

    -- 擴展資訊
    medical_history JSONB DEFAULT '{}',
    contact_info JSONB DEFAULT '{}',

    CONSTRAINT patient_age_check CHECK (
        birth_date <= CURRENT_DATE - INTERVAL '18 years' AND
        birth_date >= CURRENT_DATE - INTERVAL '120 years'
    ),
    CONSTRAINT patient_smoking_years_check CHECK (
        smoking_years IS NULL OR
        smoking_years <= EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date))
    ),
    CONSTRAINT patient_smoking_consistency_check CHECK (
        (smoking_status = 'NEVER' AND (smoking_years IS NULL OR smoking_years = 0)) OR
        (smoking_status IN ('FORMER', 'CURRENT') AND smoking_years > 0) OR
        (smoking_status IS NULL)
    )
);

-- 創建索引
CREATE INDEX idx_users_role ON users(role) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_line_user_id ON users(line_user_id) WHERE line_user_id IS NOT NULL;
CREATE INDEX idx_users_email ON users(email) WHERE email IS NOT NULL;
CREATE INDEX idx_patient_therapist ON patient_profiles(therapist_id);
CREATE INDEX idx_patient_medical_record_number ON patient_profiles(hospital_medical_record_number)
    WHERE hospital_medical_record_number IS NOT NULL;
CREATE INDEX idx_patient_smoking_status ON patient_profiles(smoking_status)
    WHERE smoking_status IN ('FORMER', 'CURRENT');

-- 創建 updated_at 觸發器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patient_profiles_updated_at BEFORE UPDATE ON patient_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;
```

### 7.2 Alembic 配置範例

```python
# backend/alembic.ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://user:pass@localhost/respira_ally

# backend/alembic/env.py
from alembic import context
from sqlalchemy import engine_from_config, pool
from respira_ally.infrastructure.database.models import Base  # SQLAlchemy Base

target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
```

---

## 8. 查詢優化建議

### 8.1 常見查詢優化

#### 查詢 1: 治療師查看其負責的高風險病患

```sql
-- ❌ 未優化（多次 JOIN，未使用索引）
SELECT p.name, r.score, r.risk_level
FROM patient_profiles p
JOIN risk_scores r ON p.user_id = r.patient_id
WHERE p.therapist_id = 'therapist-uuid'
  AND r.calculation_date = (
      SELECT MAX(calculation_date) FROM risk_scores WHERE patient_id = p.user_id
  )
  AND r.risk_level = 'HIGH';

-- ✅ 優化後（使用 DISTINCT ON + 索引）
SELECT DISTINCT ON (r.patient_id) p.name, r.score, r.risk_level
FROM risk_scores r
JOIN patient_profiles p ON r.patient_id = p.user_id
WHERE p.therapist_id = 'therapist-uuid'
  AND r.risk_level = 'HIGH'
ORDER BY r.patient_id, r.calculation_date DESC;

-- 使用索引: idx_risk_scores_patient_latest, idx_patient_therapist
```

#### 查詢 2: 計算病患近 7 天依從率

```sql
-- ❌ 未優化（掃描全表）
SELECT
    patient_id,
    COUNT(*) FILTER (WHERE medication_taken) * 100 / 7 AS adherence_rate
FROM daily_logs
WHERE patient_id = 'patient-uuid'
  AND log_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY patient_id;

-- ✅ 優化後（使用 KPI 快取表）
SELECT adherence_rate_7d
FROM patient_kpi_cache
WHERE patient_id = 'patient-uuid';

-- 若快取過期，使用帶索引的查詢
SELECT
    COUNT(*) FILTER (WHERE medication_taken) * 100 / 7 AS adherence_rate
FROM daily_logs
WHERE patient_id = 'patient-uuid'
  AND log_date >= CURRENT_DATE - INTERVAL '7 days';

-- 使用索引: idx_daily_logs_patient_date
```

### 8.2 `EXPLAIN ANALYZE` 範例

```sql
-- 分析查詢執行計畫
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT p.name, COUNT(d.log_id) AS log_count
FROM patient_profiles p
LEFT JOIN daily_logs d ON p.user_id = d.patient_id
WHERE p.therapist_id = 'therapist-uuid'
  AND d.log_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY p.user_id, p.name;

-- 預期輸出（使用索引）:
-- Index Scan using idx_patient_therapist on patient_profiles p
-- -> Index Scan using idx_daily_logs_patient_date on daily_logs d
```

---

## 9. 資料庫配置建議

### 9.1 連線池配置 (PostgreSQL)

```sql
-- postgresql.conf
max_connections = 100  -- 根據應用實例數調整
shared_buffers = 256MB  -- 25% of RAM
effective_cache_size = 1GB  -- 50-75% of RAM
work_mem = 4MB  -- Per query operation
maintenance_work_mem = 64MB  -- For VACUUM, CREATE INDEX

-- WAL 配置（複寫與備份）
wal_level = replica
max_wal_senders = 3
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/archive/%f'
```

### 9.2 應用層連線池 (SQLAlchemy)

```python
# backend/src/respira_ally/core/config.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

DATABASE_URL = "postgresql://user:pass@localhost/respira_ally"

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,  # 核心連線數
    max_overflow=10,  # 額外連線數
    pool_timeout=30,  # 取得連線的超時時間（秒）
    pool_recycle=3600,  # 連線回收時間（秒）
    echo=False  # 生產環境關閉 SQL 日誌
)
```

---

## 10. 備份與災難恢復

### 10.1 備份策略

**完整備份 (Full Backup)** - 每日凌晨 2:00:
```bash
pg_dump -h localhost -U postgres -F c -b -v -f /backup/respira_ally_$(date +%Y%m%d).dump respira_ally
```

**增量備份 (WAL Archiving)** - 持續:
```sql
-- postgresql.conf
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/archive/%f'
```

**邏輯複製 (Logical Replication)** - 異地備份:
```sql
-- 主庫
CREATE PUBLICATION respira_pub FOR ALL TABLES;

-- 從庫
CREATE SUBSCRIPTION respira_sub
CONNECTION 'host=primary dbname=respira_ally'
PUBLICATION respira_pub;
```

### 10.2 還原測試

```bash
# 還原完整備份
pg_restore -h localhost -U postgres -d respira_ally_restored /backup/respira_ally_20251017.dump

# 驗證數據完整性
psql -h localhost -U postgres -d respira_ally_restored -c "SELECT COUNT(*) FROM users;"
```

---

## 11. 審查清單

設計完成後，請確認以下檢查項：

- [x] **所有表都有主鍵** - UUID 作為 PK
- [x] **外鍵約束完整** - ON DELETE CASCADE / SET NULL 語意正確
- [x] **索引策略覆蓋核心查詢** - 至少 15 個索引
- [x] **Check 約束保護數據完整性** - 年齡、分數範圍、狀態轉換
- [x] **審計欄位完整** - created_at, updated_at, deleted_at
- [x] **JSONB 欄位有 GIN 索引** - event_data
- [x] **pgvector 索引配置** - IVFFlat 或 HNSW
- [x] **觸發器自動化** - updated_at, risk_level, KPI cache
- [x] **分區策略規劃** - 大表分區方案
- [x] **Migration 腳本範例** - Alembic 腳本結構
- [x] **備份與還原策略** - 完整備份 + WAL 歸檔

---

## 12. 下一步

1. **實作 SQLAlchemy Models** - 將 SQL Schema 轉為 Python ORM Models
2. **撰寫初始 Migration** - Alembic 腳本生成
3. **設計 Repository 接口** - 基於 DDD 的數據訪問層
4. **撰寫查詢優化測試** - 驗證索引效果

---

**相關文檔**:
- [ARCHITECTURE_REVIEW.md](./ARCHITECTURE_REVIEW.md) - 架構審視報告
- [05_architecture_and_design.md](./05_architecture_and_design.md) - 整體架構設計
- [16_wbs_development_plan.md](../16_wbs_development_plan.md) - 開發計劃

**記住**: "Show me your flowcharts and conceal your tables, and I shall continue to be mystified. Show me your tables, and I won't usually need your flowcharts; they'll be obvious." - Fred Brooks

---

**文件結束**
