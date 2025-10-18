-- Alembic Migration Script
-- Revision: 003
-- Description: 擴展 patient_kpi_cache 並創建數據視圖（用於前端圖表）
-- Previous: 002_add_patient_health_fields.sql
-- Created: 2025-10-18

BEGIN;

-- ============================================================================
-- Step 1: 擴展 patient_kpi_cache 表（新增更多 KPI 欄位）
-- ============================================================================

-- 新增基礎統計
ALTER TABLE patient_kpi_cache
    ADD COLUMN first_log_date DATE,
    ADD COLUMN avg_water_intake_30d INTEGER CHECK (avg_water_intake_30d >= 0),
    ADD COLUMN avg_steps_7d INTEGER CHECK (avg_steps_7d >= 0),
    ADD COLUMN avg_steps_30d INTEGER CHECK (avg_steps_30d >= 0);

-- 新增最新問卷分數（快速查詢）
ALTER TABLE patient_kpi_cache
    ADD COLUMN latest_cat_score INTEGER CHECK (latest_cat_score >= 0 AND latest_cat_score <= 40),
    ADD COLUMN latest_cat_date DATE,
    ADD COLUMN latest_mmrc_score INTEGER CHECK (latest_mmrc_score >= 0 AND latest_mmrc_score <= 4),
    ADD COLUMN latest_mmrc_date DATE;

-- 新增最新風險評分
ALTER TABLE patient_kpi_cache
    ADD COLUMN latest_risk_score INTEGER CHECK (latest_risk_score >= 0 AND latest_risk_score <= 100),
    ADD COLUMN latest_risk_level VARCHAR(20) CHECK (latest_risk_level IN ('LOW', 'MEDIUM', 'HIGH')),
    ADD COLUMN latest_risk_date DATE;

-- 新增症狀統計
ALTER TABLE patient_kpi_cache
    ADD COLUMN symptom_occurrences_30d INTEGER NOT NULL DEFAULT 0;

-- 更新欄位註解
COMMENT ON TABLE patient_kpi_cache IS
    '病患 KPI 快取表 - 預先聚合的統計數據，用於 Dashboard API 快速讀取 (< 50ms)';
COMMENT ON COLUMN patient_kpi_cache.adherence_rate_7d IS '近 7 天用藥依從率 (%)';
COMMENT ON COLUMN patient_kpi_cache.adherence_rate_30d IS '近 30 天用藥依從率 (%)';
COMMENT ON COLUMN patient_kpi_cache.latest_cat_score IS '最新 CAT 問卷分數 (0-40)';
COMMENT ON COLUMN patient_kpi_cache.latest_mmrc_score IS '最新 mMRC 問卷分數 (0-4)';
COMMENT ON COLUMN patient_kpi_cache.latest_risk_level IS '最新風險等級 (LOW/MEDIUM/HIGH)';
COMMENT ON COLUMN patient_kpi_cache.symptom_occurrences_30d IS '近 30 天出現症狀的次數';


-- ============================================================================
-- Step 2: 創建視圖 - patient_kpi_windows（動態時間窗口 KPI）
-- ============================================================================

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


-- ============================================================================
-- Step 3: 創建視圖 - patient_health_timeline（每日時間序列）
-- ============================================================================

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


-- ============================================================================
-- Step 4: 創建視圖 - patient_survey_trends（問卷趨勢）
-- ============================================================================

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


-- ============================================================================
-- Step 5: 創建觸發器函數 - 自動更新 patient_kpi_cache
-- ============================================================================

-- 5.1 當新增 daily_log 時，更新 KPI 快取
CREATE OR REPLACE FUNCTION update_patient_kpi_on_log_insert()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO patient_kpi_cache (patient_id, total_logs_count, first_log_date, last_log_date, last_calculated_at)
    VALUES (NEW.patient_id, 1, NEW.log_date, NEW.log_date, CURRENT_TIMESTAMP)
    ON CONFLICT (patient_id) DO UPDATE SET
        total_logs_count = patient_kpi_cache.total_logs_count + 1,
        first_log_date = LEAST(patient_kpi_cache.first_log_date, NEW.log_date),
        last_log_date = GREATEST(patient_kpi_cache.last_log_date, NEW.log_date),
        last_calculated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_kpi_on_daily_log_insert
AFTER INSERT ON daily_logs
FOR EACH ROW EXECUTE FUNCTION update_patient_kpi_on_log_insert();

COMMENT ON FUNCTION update_patient_kpi_on_log_insert() IS
    '觸發器函數 - 當新增 daily_log 時，自動更新 patient_kpi_cache 的基礎統計';


-- 5.2 當新增 survey_response 時，更新最新分數
CREATE OR REPLACE FUNCTION update_patient_kpi_on_survey_insert()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.survey_type = 'CAT' THEN
        UPDATE patient_kpi_cache
        SET latest_cat_score = NEW.total_score,
            latest_cat_date = DATE(NEW.submitted_at),
            last_calculated_at = CURRENT_TIMESTAMP
        WHERE patient_id = NEW.patient_id;
    ELSIF NEW.survey_type = 'mMRC' THEN
        UPDATE patient_kpi_cache
        SET latest_mmrc_score = NEW.total_score,
            latest_mmrc_date = DATE(NEW.submitted_at),
            last_calculated_at = CURRENT_TIMESTAMP
        WHERE patient_id = NEW.patient_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_kpi_on_survey_insert
AFTER INSERT ON survey_responses
FOR EACH ROW EXECUTE FUNCTION update_patient_kpi_on_survey_insert();

COMMENT ON FUNCTION update_patient_kpi_on_survey_insert() IS
    '觸發器函數 - 當新增問卷回覆時，自動更新 patient_kpi_cache 的最新問卷分數';


-- 5.3 當新增 risk_score 時，更新最新風險
CREATE OR REPLACE FUNCTION update_patient_kpi_on_risk_insert()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE patient_kpi_cache
    SET latest_risk_score = NEW.score,
        latest_risk_level = NEW.risk_level::TEXT,
        latest_risk_date = NEW.calculation_date,
        last_calculated_at = CURRENT_TIMESTAMP
    WHERE patient_id = NEW.patient_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_kpi_on_risk_insert
AFTER INSERT ON risk_scores
FOR EACH ROW EXECUTE FUNCTION update_patient_kpi_on_risk_insert();

COMMENT ON FUNCTION update_patient_kpi_on_risk_insert() IS
    '觸發器函數 - 當新增風險分數時，自動更新 patient_kpi_cache 的最新風險評估';


-- ============================================================================
-- Step 6: 創建定期更新 KPI 的存儲過程（使用 pg_cron 或應用層調用）
-- ============================================================================

CREATE OR REPLACE FUNCTION refresh_patient_kpi_cache(p_patient_id UUID DEFAULT NULL)
RETURNS VOID AS $$
BEGIN
    -- 更新指定病患或所有病患的 KPI 快取
    UPDATE patient_kpi_cache kpi
    SET
        -- 從 patient_kpi_windows 視圖更新時間窗口 KPI
        adherence_rate_7d = w.adherence_rate_7d,
        adherence_rate_30d = w.adherence_rate_30d,
        avg_water_intake_7d = w.avg_water_intake_7d,
        avg_water_intake_30d = w.avg_water_intake_30d,
        avg_steps_7d = w.avg_steps_7d,
        avg_steps_30d = w.avg_steps_30d,

        -- 更新症狀出現次數
        symptom_occurrences_30d = (
            SELECT COUNT(*)
            FROM daily_logs
            WHERE patient_id = kpi.patient_id
              AND log_date >= CURRENT_DATE - INTERVAL '30 days'
              AND symptoms IS NOT NULL
              AND symptoms != ''
        ),

        last_calculated_at = CURRENT_TIMESTAMP
    FROM patient_kpi_windows w
    WHERE kpi.patient_id = w.patient_id
      AND (p_patient_id IS NULL OR kpi.patient_id = p_patient_id);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION refresh_patient_kpi_cache(UUID) IS
    '刷新 patient_kpi_cache 的所有計算型 KPI（依從率、飲水量等）。
    參數: p_patient_id (可選) - 指定病患 ID，NULL 則更新所有病患。
    建議: 使用 pg_cron 每小時執行一次，或在病患查詢 Dashboard 時按需調用。';


-- ============================================================================
-- Rollback Script (備份用)
-- ============================================================================

-- 若需回滾, 執行以下 SQL:
/*
BEGIN;

-- 刪除觸發器
DROP TRIGGER IF EXISTS trigger_update_kpi_on_daily_log_insert ON daily_logs;
DROP TRIGGER IF EXISTS trigger_update_kpi_on_survey_insert ON survey_responses;
DROP TRIGGER IF EXISTS trigger_update_kpi_on_risk_insert ON risk_scores;

-- 刪除觸發器函數
DROP FUNCTION IF EXISTS update_patient_kpi_on_log_insert();
DROP FUNCTION IF EXISTS update_patient_kpi_on_survey_insert();
DROP FUNCTION IF EXISTS update_patient_kpi_on_risk_insert();
DROP FUNCTION IF EXISTS refresh_patient_kpi_cache(UUID);

-- 刪除視圖
DROP VIEW IF EXISTS patient_survey_trends;
DROP VIEW IF EXISTS patient_health_timeline;
DROP VIEW IF EXISTS patient_kpi_windows;

-- 刪除新增欄位
ALTER TABLE patient_kpi_cache DROP COLUMN IF EXISTS symptom_occurrences_30d;
ALTER TABLE patient_kpi_cache DROP COLUMN IF EXISTS latest_risk_date;
ALTER TABLE patient_kpi_cache DROP COLUMN IF EXISTS latest_risk_level;
ALTER TABLE patient_kpi_cache DROP COLUMN IF EXISTS latest_risk_score;
ALTER TABLE patient_kpi_cache DROP COLUMN IF EXISTS latest_mmrc_date;
ALTER TABLE patient_kpi_cache DROP COLUMN IF EXISTS latest_mmrc_score;
ALTER TABLE patient_kpi_cache DROP COLUMN IF EXISTS latest_cat_date;
ALTER TABLE patient_kpi_cache DROP COLUMN IF EXISTS latest_cat_score;
ALTER TABLE patient_kpi_cache DROP COLUMN IF EXISTS avg_steps_30d;
ALTER TABLE patient_kpi_cache DROP COLUMN IF EXISTS avg_steps_7d;
ALTER TABLE patient_kpi_cache DROP COLUMN IF EXISTS avg_water_intake_30d;
ALTER TABLE patient_kpi_cache DROP COLUMN IF EXISTS first_log_date;

COMMIT;
*/

COMMIT;

-- ============================================================================
-- Migration 完成
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration 003 completed successfully!';
    RAISE NOTICE '   - Extended patient_kpi_cache with 11 new columns';
    RAISE NOTICE '   - Created 3 views: patient_kpi_windows, patient_health_timeline, patient_survey_trends';
    RAISE NOTICE '   - Created 3 triggers for auto-updating KPI cache';
    RAISE NOTICE '   - Created refresh_patient_kpi_cache() procedure';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Next Steps:';
    RAISE NOTICE '   1. 執行初始數據填充: SELECT refresh_patient_kpi_cache();';
    RAISE NOTICE '   2. 設置定期刷新 (pg_cron): SELECT cron.schedule(''refresh-kpi'', ''0 * * * *'', $$SELECT refresh_patient_kpi_cache()$$);';
    RAISE NOTICE '   3. 更新 Backend API 使用新視圖查詢';
END $$;
