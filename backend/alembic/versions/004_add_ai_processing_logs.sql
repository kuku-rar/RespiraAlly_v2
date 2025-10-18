-- Alembic Migration Script
-- Revision: 004
-- Description: 新增 AI 處理日誌表 (支持 STT/LLM/TTS/RAG 全流程追蹤)
-- Previous: 003_enhance_kpi_cache_and_views.sql
-- Created: 2025-10-18

BEGIN;

-- ============================================================================
-- Step 1: 創建 ENUM 型別
-- ============================================================================

-- AI 處理階段
CREATE TYPE ai_processing_stage_enum AS ENUM ('STT', 'LLM', 'TTS', 'RAG', 'MEMORY_GATE');

COMMENT ON TYPE ai_processing_stage_enum IS
    'AI 處理階段: STT=語音轉文字, LLM=語言模型推理, TTS=文字轉語音, RAG=向量檢索, MEMORY_GATE=記憶體閘門決策';

-- AI 處理狀態
CREATE TYPE ai_processing_status_enum AS ENUM ('PENDING', 'SUCCESS', 'FAILED', 'RETRYING');

COMMENT ON TYPE ai_processing_status_enum IS
    'AI 處理狀態: PENDING=處理中, SUCCESS=成功, FAILED=失敗, RETRYING=重試中';


-- ============================================================================
-- Step 2: 創建 ai_processing_logs 表
-- ============================================================================

CREATE TABLE ai_processing_logs (
    -- 唯一識別
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 關聯使用者
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- 會話與請求追蹤
    session_id TEXT NOT NULL,  -- 同一次對話的多個階段共享此 ID (格式: "session:{user_id}:{timestamp}")
    request_id TEXT NOT NULL,  -- 每個請求的唯一 ID (用於冪等性檢查)

    -- 處理階段
    processing_stage ai_processing_stage_enum NOT NULL,

    -- 輸入/輸出數據 (JSONB for flexibility)
    input_data JSONB NOT NULL DEFAULT '{}',
    -- 範例:
    --   STT: {"audio_url": "s3://...", "audio_duration_sec": 3.5, "language": "zh-TW"}
    --   LLM: {"prompt": "...", "context": [...], "temperature": 0.7}
    --   TTS: {"text": "...", "voice": "alloy", "speed": 1.0}
    --   RAG: {"query": "...", "top_k": 3}

    output_data JSONB NOT NULL DEFAULT '{}',
    -- 範例:
    --   STT: {"transcription": "我今天有吃藥", "confidence": 0.95}
    --   LLM: {"response": "很棒！...", "finish_reason": "stop"}
    --   TTS: {"audio_url": "s3://...", "audio_duration_sec": 2.1}
    --   RAG: {"chunks": [...], "scores": [0.89, 0.85, 0.82]}

    -- 性能指標
    latency_ms INTEGER CHECK (latency_ms >= 0 AND latency_ms <= 300000),  -- 最大 5 分鐘

    token_usage JSONB DEFAULT '{}',
    -- 範例: {"prompt_tokens": 150, "completion_tokens": 80, "total_tokens": 230}

    cost_usd DECIMAL(10, 6) CHECK (cost_usd >= 0),  -- 美金，保留 6 位小數
    -- 範例: 0.002300 (即 $0.0023 USD)

    -- 錯誤處理
    status ai_processing_status_enum NOT NULL DEFAULT 'PENDING',
    error_message TEXT,  -- 失敗時的錯誤訊息
    retry_count INTEGER NOT NULL DEFAULT 0 CHECK (retry_count >= 0 AND retry_count <= 5),

    -- 去重機制 (3 秒時間桶 + SHA-1 hash)
    dedup_hash TEXT,  -- SHA-1(user_id + time_bucket_3s)
    is_duplicate BOOLEAN NOT NULL DEFAULT false,

    -- Metadata
    model_name TEXT,  -- 使用的 AI 模型 (e.g., "gpt-4-turbo", "whisper-1", "tts-1")
    provider TEXT CHECK (provider IN ('openai', 'azure', 'anthropic', 'custom')),
    metadata JSONB DEFAULT '{}',  -- 額外資訊 (e.g., {"redis_key": "...", "cache_hit": true})

    -- 審計欄位
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE ai_processing_logs IS
    'AI 處理日誌 - 記錄語音對話的完整處理流程 (STT → LLM → TTS)，用於除錯、成本分析、性能優化';

COMMENT ON COLUMN ai_processing_logs.session_id IS
    '會話 ID - 同一次對話的多個處理階段共享此 ID (格式: "session:{user_id}:{timestamp}")';

COMMENT ON COLUMN ai_processing_logs.request_id IS
    '請求 ID - 每個 API 請求的唯一識別 (用於冪等性檢查，格式: UUID)';

COMMENT ON COLUMN ai_processing_logs.dedup_hash IS
    '去重雜湊 - SHA-1(user_id + 3秒時間桶)，用於識別 3 秒內的重複請求';

COMMENT ON COLUMN ai_processing_logs.input_data IS
    'JSONB - 輸入數據，結構依 processing_stage 而異 (見表創建語句中的範例)';

COMMENT ON COLUMN ai_processing_logs.output_data IS
    'JSONB - 輸出數據，結構依 processing_stage 而異 (見表創建語句中的範例)';

COMMENT ON COLUMN ai_processing_logs.token_usage IS
    'JSONB - Token 使用量統計 (僅 LLM 階段有值): {prompt_tokens, completion_tokens, total_tokens}';

COMMENT ON COLUMN ai_processing_logs.cost_usd IS
    '成本 (美金) - 此次處理的 API 費用，保留 6 位小數以精確計算';


-- ============================================================================
-- Step 3: 創建索引
-- ============================================================================

-- 核心查詢：查詢某使用者的會話歷史
CREATE INDEX idx_ai_logs_user_session ON ai_processing_logs(user_id, session_id, created_at DESC);

COMMENT ON INDEX idx_ai_logs_user_session IS
    '使用者會話索引 - 用於快速查詢某使用者的對話歷史與處理流程';

-- 去重查詢：檢查請求是否重複
CREATE INDEX idx_ai_logs_dedup_hash ON ai_processing_logs(dedup_hash, created_at DESC)
    WHERE is_duplicate = false;

COMMENT ON INDEX idx_ai_logs_dedup_hash IS
    '去重索引 - 部分索引，僅索引非重複請求，用於 3 秒去重機制';

-- 錯誤追蹤：查詢失敗或待重試的請求
CREATE INDEX idx_ai_logs_status ON ai_processing_logs(status, created_at DESC)
    WHERE status IN ('PENDING', 'FAILED', 'RETRYING');

COMMENT ON INDEX idx_ai_logs_status IS
    '狀態索引 - 部分索引，用於監控失敗與待重試的 AI 處理請求';

-- 階段分析：統計各階段性能
CREATE INDEX idx_ai_logs_stage ON ai_processing_logs(processing_stage, created_at DESC);

COMMENT ON INDEX idx_ai_logs_stage IS
    '階段索引 - 用於分析各處理階段 (STT/LLM/TTS) 的性能與成本';

-- 成本分析：按時間範圍查詢成本
CREATE INDEX idx_ai_logs_cost ON ai_processing_logs(created_at DESC) INCLUDE (cost_usd, token_usage);

COMMENT ON INDEX idx_ai_logs_cost IS
    '成本索引 - INCLUDE 索引，用於高效生成成本報表 (避免回表查詢)';

-- JSONB GIN 索引：支援複雜查詢
CREATE INDEX idx_ai_logs_input_data ON ai_processing_logs USING GIN (input_data);
CREATE INDEX idx_ai_logs_output_data ON ai_processing_logs USING GIN (output_data);

COMMENT ON INDEX idx_ai_logs_input_data IS
    'GIN 索引 - 支援 JSONB 欄位的複雜查詢 (e.g., WHERE input_data @> ''{"language": "zh-TW"}'')';


-- ============================================================================
-- Step 4: 創建約束
-- ============================================================================

-- 確保失敗時有錯誤訊息
ALTER TABLE ai_processing_logs ADD CONSTRAINT ai_logs_error_message_check
    CHECK (status != 'FAILED' OR error_message IS NOT NULL);

-- 確保成功時沒有錯誤訊息
ALTER TABLE ai_processing_logs ADD CONSTRAINT ai_logs_success_no_error_check
    CHECK (status != 'SUCCESS' OR error_message IS NULL);

-- 確保重試次數邏輯
ALTER TABLE ai_processing_logs ADD CONSTRAINT ai_logs_retry_status_check
    CHECK (
        (retry_count = 0 AND status IN ('PENDING', 'SUCCESS', 'FAILED')) OR
        (retry_count > 0 AND status = 'RETRYING')
    );

-- 確保 LLM 階段有 token_usage
ALTER TABLE ai_processing_logs ADD CONSTRAINT ai_logs_llm_token_check
    CHECK (processing_stage != 'LLM' OR token_usage IS NOT NULL);


-- ============================================================================
-- Step 5: 創建輔助視圖 (Optional - 成本統計)
-- ============================================================================

-- 每日 AI 成本統計
CREATE OR REPLACE VIEW ai_daily_cost_summary AS
SELECT
    DATE(created_at) AS date,
    processing_stage,
    COUNT(*) AS total_requests,
    COUNT(*) FILTER (WHERE status = 'SUCCESS') AS successful_requests,
    COUNT(*) FILTER (WHERE status = 'FAILED') AS failed_requests,
    SUM(cost_usd) AS total_cost_usd,
    AVG(latency_ms) AS avg_latency_ms,
    SUM((token_usage->>'total_tokens')::INTEGER) AS total_tokens
FROM ai_processing_logs
GROUP BY DATE(created_at), processing_stage
ORDER BY date DESC, processing_stage;

COMMENT ON VIEW ai_daily_cost_summary IS
    '每日 AI 成本統計 - 依處理階段統計請求數、成功率、成本、延遲';


-- 使用者 AI 使用量統計 (近 30 天)
CREATE OR REPLACE VIEW ai_user_usage_30d AS
SELECT
    user_id,
    COUNT(DISTINCT session_id) AS total_sessions,
    COUNT(*) AS total_requests,
    SUM(cost_usd) AS total_cost_usd,
    AVG(latency_ms) AS avg_latency_ms,
    SUM((token_usage->>'total_tokens')::INTEGER) AS total_tokens,
    COUNT(*) FILTER (WHERE is_duplicate = true) AS duplicate_requests,
    ROUND((COUNT(*) FILTER (WHERE is_duplicate = true)::NUMERIC / COUNT(*)) * 100, 2) AS duplicate_rate_percent
FROM ai_processing_logs
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY user_id
ORDER BY total_cost_usd DESC;

COMMENT ON VIEW ai_user_usage_30d IS
    '使用者 AI 使用量統計 (近 30 天) - 用於分析使用者行為與成本分攤';


-- ============================================================================
-- Rollback Script (備份用)
-- ============================================================================

-- 若需回滾, 執行以下 SQL:
/*
BEGIN;

-- 刪除視圖
DROP VIEW IF EXISTS ai_user_usage_30d;
DROP VIEW IF EXISTS ai_daily_cost_summary;

-- 刪除索引
DROP INDEX IF EXISTS idx_ai_logs_output_data;
DROP INDEX IF EXISTS idx_ai_logs_input_data;
DROP INDEX IF EXISTS idx_ai_logs_cost;
DROP INDEX IF EXISTS idx_ai_logs_stage;
DROP INDEX IF EXISTS idx_ai_logs_status;
DROP INDEX IF EXISTS idx_ai_logs_dedup_hash;
DROP INDEX IF EXISTS idx_ai_logs_user_session;

-- 刪除約束
ALTER TABLE ai_processing_logs DROP CONSTRAINT IF EXISTS ai_logs_llm_token_check;
ALTER TABLE ai_processing_logs DROP CONSTRAINT IF EXISTS ai_logs_retry_status_check;
ALTER TABLE ai_processing_logs DROP CONSTRAINT IF EXISTS ai_logs_success_no_error_check;
ALTER TABLE ai_processing_logs DROP CONSTRAINT IF EXISTS ai_logs_error_message_check;

-- 刪除表
DROP TABLE IF EXISTS ai_processing_logs;

-- 刪除 ENUM 型別
DROP TYPE IF EXISTS ai_processing_status_enum;
DROP TYPE IF EXISTS ai_processing_stage_enum;

COMMIT;
*/

COMMIT;

-- ============================================================================
-- Migration 完成
-- ============================================================================

-- 驗證 Migration 是否成功
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 004 completed successfully!';
    RAISE NOTICE '   - Created ai_processing_stage_enum and ai_processing_status_enum types';
    RAISE NOTICE '   - Created ai_processing_logs table';
    RAISE NOTICE '   - Created 7 indexes for optimization (including GIN for JSONB)';
    RAISE NOTICE '   - Created 4 CHECK constraints for data integrity';
    RAISE NOTICE '   - Created 2 views: ai_daily_cost_summary, ai_user_usage_30d';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Next Steps:';
    RAISE NOTICE '   1. 更新 Backend API 整合 AI 處理日誌記錄';
    RAISE NOTICE '   2. 實作去重邏輯: SELECT * FROM ai_processing_logs WHERE dedup_hash = $1 AND is_duplicate = false';
    RAISE NOTICE '   3. 設置定期清理舊日誌 (保留 90 天): DELETE FROM ai_processing_logs WHERE created_at < NOW() - INTERVAL ''90 days''';
    RAISE NOTICE '   4. 監控成本: SELECT * FROM ai_daily_cost_summary ORDER BY date DESC LIMIT 30';
END $$;
