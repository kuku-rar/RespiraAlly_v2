# AI 處理日誌設計文檔

**文件版本**: v1.0
**最後更新**: 2025-10-18
**設計者**: Claude Code AI - Data Engineer
**狀態**: 已完成 (Completed)

---

## 目錄

1. [設計背景](#1-設計背景)
2. [核心需求](#2-核心需求)
3. [架構決策](#3-架構決策)
4. [表結構設計](#4-表結構設計)
5. [索引策略](#5-索引策略)
6. [使用範例](#6-使用範例)
7. [成本監控](#7-成本監控)
8. [維護策略](#8-維護策略)

---

## 1. 設計背景

### 1.1 問題陳述

Phase 2 的語音對話功能需要完整的處理日誌系統，用於：

1. **除錯追蹤** - 快速定位處理失敗原因
2. **成本監控** - 統計 OpenAI API Token 使用量與費用
3. **性能分析** - 分析各階段延遲瓶頸
4. **去重驗證** - 驗證 3 秒去重機制有效性
5. **合規審計** - 記錄 AI 處理歷史以符合法規要求

### 1.2 技術背景

**AI 處理流程** (基於 `/docs/ai/20_memory_management_design.md`):

```
User Voice → LINE → RabbitMQ → AI Worker
                                    ↓
                        STT (Whisper) → LLM (GPT-4 + Memory Gate) → TTS (OpenAI TTS)
                                    ↓
                        Response → LINE Push → User
```

**關鍵技術挑戰**:
- **多階段處理** - STT, LLM, TTS 可能部分失敗
- **去重機制** - 3 秒時間桶 + SHA-1 hash
- **成本追蹤** - 每個 API 呼叫需記錄 Token 與費用
- **性能監控** - 各階段延遲需獨立追蹤

---

## 2. 核心需求

### 2.1 功能需求

| 需求 ID | 需求描述 | 優先級 |
|---------|----------|--------|
| FR-1 | 記錄每個 AI 處理階段 (STT/LLM/TTS/RAG) 的輸入/輸出 | P0 |
| FR-2 | 記錄每個階段的延遲 (latency_ms) | P0 |
| FR-3 | 記錄 LLM 的 Token 使用量與成本 | P0 |
| FR-4 | 支持去重查詢 (dedup_hash) | P0 |
| FR-5 | 記錄錯誤訊息與重試次數 | P0 |
| FR-6 | 支持會話級別的查詢 (session_id) | P1 |
| FR-7 | 提供成本統計視圖 (daily/monthly) | P1 |
| FR-8 | 支持 JSONB 靈活查詢 (e.g., 語言、模型) | P2 |

### 2.2 非功能需求

| 需求 ID | 需求描述 | 目標 |
|---------|----------|------|
| NFR-1 | 寫入性能 | < 10ms (不阻塞主流程) |
| NFR-2 | 查詢性能 | < 100ms (使用索引) |
| NFR-3 | 數據保留 | 90 天 (超過則自動清理) |
| NFR-4 | 儲存空間 | < 100GB / 100萬次請求 |

---

## 3. 架構決策

### 3.1 Linus 式決策流程

#### 第一層：數據結構分析

**核心數據關係**:
```
User → Session (一次對話) → Multiple Stages (STT → LLM → TTS)
                                    ↓
                            Each Stage = One Log Entry
```

**拒絕的方案**:
- ❌ **方案 A: 主表 + 階段表** (過度設計)
  ```
  conversations (session_id, user_id)
  processing_stages (log_id, session_id, stage, ...)
  ```
  - 問題：需要 JOIN 才能看到完整流程
  - 複雜度：2 張表 + 外鍵約束

**採用的方案**:
- ✅ **方案 B: 單一表格** (簡潔至上)
  ```
  ai_processing_logs (log_id, session_id, stage, ...)
  ```
  - 優點：查詢 `WHERE session_id = X` 即可
  - 簡潔：1 張表，0 個 JOIN

#### 第二層：特殊情況識別

**消除的特殊情況**:
- ❌ 不需要區分「成功」vs「失敗」的欄位 → 統一用 `status` ENUM
- ❌ 不需要區分「STT 輸入」vs「LLM 輸入」 → 統一用 `input_data` JSONB
- ✅ **用 ENUM 消除所有 if/else 判斷**

#### 第三層：複雜度審查

**核心功能（一句話）**: 記錄每個 AI 處理階段的輸入、輸出、成本、延遲

**概念數量**:
- 方案 A (主表+階段表): 8 個概念 (2 表 + 6 關係)
- 方案 B (單一表): 4 個概念 (1 表 + 3 索引)

**優化結果**: **減少 50% 複雜度**

#### 第四層：破壞性分析

✅ **零破壞**: 新增表格，不影響現有功能

#### 第五層：實用性驗證

- ✅ **真實需求**: Phase 2 語音功能上線前必須部署
- ✅ **用戶規模**: 預計 100-1000 次/日處理量
- ✅ **複雜度匹配**: 單一表格足夠

### 3.2 最終決策

**ADR (Architecture Decision Record)**:

```yaml
Title: AI 處理日誌使用單一表格而非主表+階段表
Status: Accepted
Date: 2025-10-18

Context:
  - 需要記錄 STT/LLM/TTS 多階段處理日誌
  - 每個階段可能獨立失敗/重試
  - 需要支持成本分析、性能監控、去重驗證

Decision:
  使用單一 `ai_processing_logs` 表，每個處理階段一筆記錄

Rationale:
  - 簡潔：1 張表 vs 2 張表
  - 查詢簡單：WHERE session_id = X ORDER BY created_at
  - JSONB 靈活性：不同階段可有不同 schema
  - 符合 Linus 原則：消除不必要的複雜性

Consequences:
  - ✅ 開發速度快
  - ✅ 查詢性能好（索引優化）
  - ⚠️ JSONB 欄位需要良好文檔說明

Alternatives Considered:
  - 主表 + 階段表 (rejected: 過度設計)
  - MongoDB (rejected: 已有 PostgreSQL + JSONB)
```

---

## 4. 表結構設計

### 4.1 表定義

```sql
CREATE TABLE ai_processing_logs (
    -- 唯一識別
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 關聯使用者
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- 會話與請求追蹤
    session_id TEXT NOT NULL,  -- 格式: "session:{user_id}:{timestamp}"
    request_id TEXT NOT NULL,  -- 冪等性檢查用

    -- 處理階段
    processing_stage ENUM ('STT', 'LLM', 'TTS', 'RAG', 'MEMORY_GATE'),

    -- 輸入/輸出數據 (JSONB for flexibility)
    input_data JSONB NOT NULL DEFAULT '{}',
    output_data JSONB NOT NULL DEFAULT '{}',

    -- 性能指標
    latency_ms INTEGER CHECK (latency_ms >= 0 AND latency_ms <= 300000),
    token_usage JSONB DEFAULT '{}',
    cost_usd DECIMAL(10, 6) CHECK (cost_usd >= 0),

    -- 錯誤處理
    status ENUM ('PENDING', 'SUCCESS', 'FAILED', 'RETRYING'),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0 CHECK (retry_count >= 0 AND retry_count <= 5),

    -- 去重機制
    dedup_hash TEXT,
    is_duplicate BOOLEAN DEFAULT false,

    -- Metadata
    model_name TEXT,
    provider TEXT CHECK (provider IN ('openai', 'azure', 'anthropic', 'custom')),
    metadata JSONB DEFAULT '{}',

    -- 審計欄位
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 JSONB Schema 說明

#### `input_data` 範例

**STT 階段**:
```json
{
  "audio_url": "s3://respira-ally/audio/abc123.m4a",
  "audio_duration_sec": 3.5,
  "language": "zh-TW",
  "audio_format": "m4a"
}
```

**LLM 階段**:
```json
{
  "prompt": "你是一個 COPD 病患的語音助手...",
  "user_message": "我今天有吃藥",
  "context": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "我今天有吃藥"}
  ],
  "temperature": 0.7,
  "max_tokens": 500,
  "memory_gate_decision": "RETRIEVE"
}
```

**TTS 階段**:
```json
{
  "text": "很棒！記得要按時吃藥喔！",
  "voice": "alloy",
  "speed": 1.0,
  "language": "zh-TW"
}
```

**RAG 階段**:
```json
{
  "query": "COPD 病患的飲食建議",
  "embedding": [0.023, -0.045, ...],  // 1536 維向量
  "top_k": 3,
  "similarity_threshold": 0.7
}
```

#### `output_data` 範例

**STT 階段**:
```json
{
  "transcription": "我今天有吃藥",
  "confidence": 0.95,
  "segments": [
    {"text": "我今天", "start": 0.0, "end": 0.8},
    {"text": "有吃藥", "start": 0.8, "end": 1.5}
  ]
}
```

**LLM 階段**:
```json
{
  "response": "很棒！記得要按時吃藥喔！今天心情如何？",
  "finish_reason": "stop",
  "model_version": "gpt-4-turbo-2024-04-09"
}
```

**TTS 階段**:
```json
{
  "audio_url": "s3://respira-ally/tts/def456.mp3",
  "audio_duration_sec": 2.1,
  "audio_format": "mp3",
  "audio_size_bytes": 34567
}
```

**RAG 階段**:
```json
{
  "chunks": [
    {
      "doc_id": "uuid-1",
      "chunk_id": "uuid-2",
      "text": "COPD 病患應多攝取...",
      "score": 0.89
    },
    {
      "doc_id": "uuid-3",
      "chunk_id": "uuid-4",
      "text": "避免高鹽飲食...",
      "score": 0.85
    }
  ],
  "total_chunks_scanned": 150
}
```

#### `token_usage` 範例 (僅 LLM)

```json
{
  "prompt_tokens": 150,
  "completion_tokens": 80,
  "total_tokens": 230
}
```

---

## 5. 索引策略

### 5.1 核心索引

```sql
-- 1. 使用者會話查詢 (最高頻)
CREATE INDEX idx_ai_logs_user_session
ON ai_processing_logs(user_id, session_id, created_at DESC);

-- 2. 去重查詢
CREATE INDEX idx_ai_logs_dedup_hash
ON ai_processing_logs(dedup_hash, created_at DESC)
WHERE is_duplicate = false;

-- 3. 錯誤監控
CREATE INDEX idx_ai_logs_status
ON ai_processing_logs(status, created_at DESC)
WHERE status IN ('PENDING', 'FAILED', 'RETRYING');

-- 4. 階段分析
CREATE INDEX idx_ai_logs_stage
ON ai_processing_logs(processing_stage, created_at DESC);

-- 5. 成本分析
CREATE INDEX idx_ai_logs_cost
ON ai_processing_logs(created_at DESC) INCLUDE (cost_usd, token_usage);

-- 6. JSONB 複雜查詢
CREATE INDEX idx_ai_logs_input_data ON ai_processing_logs USING GIN (input_data);
CREATE INDEX idx_ai_logs_output_data ON ai_processing_logs USING GIN (output_data);
```

### 5.2 索引使用場景

| 查詢場景 | 使用的索引 | 預期性能 |
|----------|------------|----------|
| 查詢某使用者的會話歷史 | `idx_ai_logs_user_session` | < 50ms |
| 檢查請求是否重複 | `idx_ai_logs_dedup_hash` | < 10ms |
| 查詢失敗的處理請求 | `idx_ai_logs_status` | < 100ms |
| 統計 STT 平均延遲 | `idx_ai_logs_stage` | < 200ms |
| 生成每日成本報表 | `idx_ai_logs_cost` | < 500ms |
| 查詢使用 GPT-4 的請求 | `idx_ai_logs_input_data` | < 300ms |

---

## 6. 使用範例

### 6.1 插入日誌

```python
import uuid
import hashlib
import json
from datetime import datetime

# 計算去重 hash (3 秒時間桶)
def calculate_dedup_hash(user_id: str, timestamp: datetime) -> str:
    time_bucket = int(timestamp.timestamp() / 3) * 3  # 3 秒對齊
    hash_input = f"{user_id}:{time_bucket}"
    return hashlib.sha1(hash_input.encode()).hexdigest()

# 插入 STT 日誌
async def log_stt_processing(
    user_id: str,
    session_id: str,
    request_id: str,
    audio_url: str,
    transcription: str,
    latency_ms: int,
    cost_usd: float
):
    now = datetime.utcnow()
    dedup_hash = calculate_dedup_hash(user_id, now)

    await db.execute(
        """
        INSERT INTO ai_processing_logs (
            user_id, session_id, request_id,
            processing_stage, status,
            input_data, output_data,
            latency_ms, cost_usd,
            dedup_hash, model_name, provider
        ) VALUES (
            $1, $2, $3, 'STT', 'SUCCESS',
            $4, $5, $6, $7, $8, 'whisper-1', 'openai'
        )
        """,
        uuid.UUID(user_id),
        session_id,
        request_id,
        json.dumps({"audio_url": audio_url, "language": "zh-TW"}),
        json.dumps({"transcription": transcription, "confidence": 0.95}),
        latency_ms,
        cost_usd,
        dedup_hash
    )
```

### 6.2 去重檢查

```python
async def is_duplicate_request(user_id: str, timestamp: datetime) -> bool:
    dedup_hash = calculate_dedup_hash(user_id, timestamp)

    result = await db.fetchone(
        """
        SELECT log_id FROM ai_processing_logs
        WHERE dedup_hash = $1 AND is_duplicate = false
        AND created_at >= NOW() - INTERVAL '5 seconds'
        LIMIT 1
        """,
        dedup_hash
    )

    return result is not None
```

### 6.3 查詢會話歷史

```python
async def get_session_logs(user_id: str, session_id: str):
    logs = await db.fetch_all(
        """
        SELECT
            processing_stage,
            status,
            input_data,
            output_data,
            latency_ms,
            cost_usd,
            created_at
        FROM ai_processing_logs
        WHERE user_id = $1 AND session_id = $2
        ORDER BY created_at ASC
        """,
        uuid.UUID(user_id),
        session_id
    )
    return logs
```

### 6.4 成本統計

```python
async def get_daily_cost(date: str):
    result = await db.fetch_all(
        """
        SELECT
            processing_stage,
            COUNT(*) AS total_requests,
            SUM(cost_usd) AS total_cost,
            AVG(latency_ms) AS avg_latency_ms
        FROM ai_processing_logs
        WHERE DATE(created_at) = $1
        GROUP BY processing_stage
        """,
        date
    )
    return result
```

---

## 7. 成本監控

### 7.1 成本計算公式

**OpenAI API 定價** (2024 年 4 月):

```python
PRICING = {
    "gpt-4-turbo": {
        "prompt": 0.01 / 1000,      # $0.01 per 1K tokens
        "completion": 0.03 / 1000   # $0.03 per 1K tokens
    },
    "whisper-1": {
        "per_minute": 0.006         # $0.006 per minute
    },
    "tts-1": {
        "per_1k_chars": 0.015       # $0.015 per 1K characters
    }
}

def calculate_llm_cost(prompt_tokens: int, completion_tokens: int) -> float:
    prompt_cost = prompt_tokens * PRICING["gpt-4-turbo"]["prompt"]
    completion_cost = completion_tokens * PRICING["gpt-4-turbo"]["completion"]
    return prompt_cost + completion_cost

def calculate_stt_cost(audio_duration_sec: float) -> float:
    return (audio_duration_sec / 60) * PRICING["whisper-1"]["per_minute"]

def calculate_tts_cost(text_length: int) -> float:
    return (text_length / 1000) * PRICING["tts-1"]["per_1k_chars"]
```

### 7.2 預算告警

```python
async def check_daily_budget(max_budget_usd: float = 50.0):
    today_cost = await db.fetchone(
        """
        SELECT SUM(cost_usd) AS total_cost
        FROM ai_processing_logs
        WHERE DATE(created_at) = CURRENT_DATE
        """
    )

    if today_cost["total_cost"] > max_budget_usd:
        # 發送告警通知
        await send_alert(
            f"⚠️ AI 成本超標！今日花費: ${today_cost['total_cost']:.2f} USD"
        )
```

---

## 8. 維護策略

### 8.1 數據保留政策

**保留規則**:
- **成功日誌**: 保留 **90 天**
- **失敗日誌**: 保留 **180 天** (用於除錯)
- **高成本請求**: 永久保留 (用於分析異常)

**自動清理腳本** (pg_cron):

```sql
-- 每日凌晨 3:00 執行
SELECT cron.schedule(
    'cleanup-ai-logs',
    '0 3 * * *',  -- 每日 3:00
    $$
    DELETE FROM ai_processing_logs
    WHERE status = 'SUCCESS'
      AND created_at < NOW() - INTERVAL '90 days'
      AND cost_usd < 1.0;  -- 保留高成本請求

    DELETE FROM ai_processing_logs
    WHERE status = 'FAILED'
      AND created_at < NOW() - INTERVAL '180 days';
    $$
);
```

### 8.2 性能監控

**關鍵指標**:
- **寫入 TPS** (Transactions Per Second)
- **查詢延遲** (P50, P95, P99)
- **表大小** (每月增長趨勢)

**監控查詢**:

```sql
-- 每日寫入量
SELECT
    DATE(created_at) AS date,
    COUNT(*) AS total_logs,
    pg_size_pretty(pg_total_relation_size('ai_processing_logs')) AS table_size
FROM ai_processing_logs
GROUP BY DATE(created_at)
ORDER BY date DESC
LIMIT 30;

-- 慢查詢識別 (需啟用 pg_stat_statements)
SELECT
    query,
    mean_exec_time,
    calls
FROM pg_stat_statements
WHERE query LIKE '%ai_processing_logs%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### 8.3 備份策略

**完整備份** (每日凌晨 2:00):
```bash
pg_dump -h localhost -U postgres -t ai_processing_logs \
    -F c -f /backup/ai_logs_$(date +%Y%m%d).dump respira_ally
```

**增量備份** (WAL archiving):
```sql
-- postgresql.conf
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/archive/%f'
```

---

## 9. 審查清單

設計完成後，請確認以下檢查項：

- [x] **表結構完整** - 包含所有必要欄位
- [x] **索引策略覆蓋核心查詢** - 7 個索引
- [x] **Check 約束保護數據完整性** - 4 個約束
- [x] **JSONB Schema 有清楚文檔** - 提供範例
- [x] **成本計算公式正確** - 基於 OpenAI 定價
- [x] **數據保留政策明確** - 90/180 天
- [x] **備份策略完整** - 完整 + 增量備份
- [x] **Migration 腳本可回滾** - 提供 rollback script

---

## 10. 下一步

1. **執行 Migration** - 在開發環境測試 `004_add_ai_processing_logs.sql`
2. **實作 Repository** - 基於 DDD 的數據訪問層
3. **整合 AI Worker** - 在處理流程中插入日誌記錄
4. **建立監控儀表板** - Grafana 可視化成本與性能
5. **壓力測試** - 驗證 1000 TPS 寫入性能

---

**相關文檔**:
- [schema_design_v1.0.md](../database/schema_design_v1.0.md) - 整體 Schema 設計
- [20_memory_management_design.md](./20_memory_management_design.md) - 記憶體管理設計
- [Migration 004](../../backend/alembic/versions/004_add_ai_processing_logs.sql) - 資料庫遷移腳本

---

**記住**: "Show me your flowcharts and conceal your tables, and I shall continue to be mystified. Show me your tables, and I won't usually need your flowcharts; they'll be obvious." - Fred Brooks

**文件結束**
