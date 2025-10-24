-- Alembic Migration Script
-- Revision: 005
-- Description: 建立 Sprint 4 Risk Engine 與 Alert System 表 (GOLD 2011 ABE 分級系統)
-- Previous: 004_add_ai_processing_logs.sql
-- ADR Reference: ADR-013 v2.0, ADR-014
-- Created: 2025-10-24

BEGIN;

-- ============================================================================
-- Step 1: 建立 ENUM 型別
-- ============================================================================

-- GOLD 2011 ABE 分級
CREATE TYPE gold_group_enum AS ENUM ('A', 'B', 'E');

COMMENT ON TYPE gold_group_enum IS 'GOLD 2011 ABE 分級: A=低風險, B=中風險, E=高風險';

-- 急性發作嚴重程度
CREATE TYPE exacerbation_severity_enum AS ENUM ('MILD', 'MODERATE', 'SEVERE');

COMMENT ON TYPE exacerbation_severity_enum IS '急性發作嚴重程度: MILD=輕度, MODERATE=中度, SEVERE=重度';

-- 警示類型
CREATE TYPE alert_type_enum AS ENUM (
    'RISK_GROUP_CHANGE',      -- GOLD 分級變更
    'HIGH_RISK_DETECTED',     -- 高風險偵測
    'EXACERBATION_RISK'       -- 急性發作風險
);

COMMENT ON TYPE alert_type_enum IS '警示類型';

-- 警示嚴重程度
CREATE TYPE alert_severity_enum AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');

COMMENT ON TYPE alert_severity_enum IS '警示嚴重程度';

-- 警示狀態
CREATE TYPE alert_status_enum AS ENUM ('ACTIVE', 'ACKNOWLEDGED', 'RESOLVED');

COMMENT ON TYPE alert_status_enum IS '警示狀態: ACTIVE=啟動中, ACKNOWLEDGED=已確認, RESOLVED=已解決';


-- ============================================================================
-- Step 2: 擴展 patients 表 - 新增急性發作彙總欄位
-- ============================================================================

-- 新增急性發作彙總欄位到 patient_profiles 表
ALTER TABLE patient_profiles
    ADD COLUMN exacerbation_count_last_12m INTEGER DEFAULT 0,
    ADD COLUMN hospitalization_count_last_12m INTEGER DEFAULT 0,
    ADD COLUMN last_exacerbation_date DATE;

COMMENT ON COLUMN patient_profiles.exacerbation_count_last_12m IS
    '過去 12 個月急性發作次數 - 由 trigger 自動更新';

COMMENT ON COLUMN patient_profiles.hospitalization_count_last_12m IS
    '過去 12 個月住院次數 - 由 trigger 自動更新';

COMMENT ON COLUMN patient_profiles.last_exacerbation_date IS
    '最近一次急性發作日期 - 由 trigger 自動更新';

-- 新增索引 (用於高風險病患篩選)
CREATE INDEX idx_patient_exacerbation_count
    ON patient_profiles(exacerbation_count_last_12m DESC)
    WHERE exacerbation_count_last_12m > 0;

COMMENT ON INDEX idx_patient_exacerbation_count IS
    '急性發作次數索引 - 支持高風險病患快速篩選 (≥2 次/年為高風險)';


-- ============================================================================
-- Step 3: 建立 exacerbations 表 - 急性發作記錄
-- ============================================================================

CREATE TABLE exacerbations (
    exacerbation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patient_profiles(user_id) ON DELETE CASCADE,

    -- 發作資訊
    onset_date DATE NOT NULL,
    severity exacerbation_severity_enum NOT NULL,

    -- 治療情況
    required_hospitalization BOOLEAN DEFAULT FALSE,
    hospitalization_days INTEGER,
    required_antibiotics BOOLEAN DEFAULT FALSE,
    required_steroids BOOLEAN DEFAULT FALSE,

    -- 症狀描述與備註
    symptoms TEXT,
    notes TEXT,

    -- 元資料
    recorded_date DATE NOT NULL DEFAULT CURRENT_DATE,
    recorded_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 約束：住院天數必須 > 0 if required_hospitalization = TRUE
    CONSTRAINT exacerbation_hospitalization_days_check
        CHECK (
            (required_hospitalization = FALSE AND hospitalization_days IS NULL) OR
            (required_hospitalization = TRUE AND hospitalization_days > 0)
        )
);

COMMENT ON TABLE exacerbations IS
    'COPD 急性發作記錄表 - 追蹤病患急性惡化事件，用於 GOLD 分級與風險評估';

COMMENT ON COLUMN exacerbations.onset_date IS '急性發作發生日期';
COMMENT ON COLUMN exacerbations.severity IS '嚴重程度 (MILD/MODERATE/SEVERE)';
COMMENT ON COLUMN exacerbations.required_hospitalization IS '是否需要住院治療';
COMMENT ON COLUMN exacerbations.hospitalization_days IS '住院天數 (僅當 required_hospitalization=TRUE)';
COMMENT ON COLUMN exacerbations.required_antibiotics IS '是否使用抗生素治療';
COMMENT ON COLUMN exacerbations.required_steroids IS '是否使用類固醇治療';
COMMENT ON COLUMN exacerbations.symptoms IS '症狀描述 (如: 咳嗽加劇、痰量增加)';
COMMENT ON COLUMN exacerbations.notes IS '臨床備註';
COMMENT ON COLUMN exacerbations.recorded_date IS '記錄日期 (可能晚於發作日期)';
COMMENT ON COLUMN exacerbations.recorded_by IS '記錄者 (通常為治療師)';

-- 索引
CREATE INDEX idx_exacerbation_patient_onset_date
    ON exacerbations(patient_id, onset_date DESC);

CREATE INDEX idx_exacerbation_severity_hospitalization
    ON exacerbations(severity, required_hospitalization)
    WHERE required_hospitalization = TRUE;

COMMENT ON INDEX idx_exacerbation_patient_onset_date IS
    '病患急性發作記錄索引 - 按發作日期降序排列';

COMMENT ON INDEX idx_exacerbation_severity_hospitalization IS
    '住院案例索引 - 快速查詢需住院的嚴重急性發作';


-- ============================================================================
-- Step 4: 建立 risk_assessments 表 - GOLD ABE 風險評估
-- ============================================================================

CREATE TABLE risk_assessments (
    assessment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patient_profiles(user_id) ON DELETE CASCADE,

    -- 評估基礎數據
    cat_score INTEGER NOT NULL CHECK (cat_score >= 0 AND cat_score <= 40),
    mmrc_grade INTEGER NOT NULL CHECK (mmrc_grade >= 0 AND mmrc_grade <= 4),
    exacerbation_count_12m INTEGER NOT NULL DEFAULT 0,
    hospitalization_count_12m INTEGER NOT NULL DEFAULT 0,

    -- GOLD ABE 分級結果
    gold_group gold_group_enum NOT NULL,

    -- 向後相容欄位 (Hybrid Strategy - ADR-014)
    risk_score INTEGER CHECK (risk_score >= 0 AND risk_score <= 100),
    risk_level VARCHAR(20) CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),

    -- 評估元資料
    assessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE risk_assessments IS
    'COPD 風險評估記錄表 - 基於 GOLD 2011 ABE 分級系統';

COMMENT ON COLUMN risk_assessments.cat_score IS 'CAT 評估量表分數 (0-40)';
COMMENT ON COLUMN risk_assessments.mmrc_grade IS 'mMRC 呼吸困難量表等級 (0-4)';
COMMENT ON COLUMN risk_assessments.exacerbation_count_12m IS '過去 12 個月急性發作次數';
COMMENT ON COLUMN risk_assessments.hospitalization_count_12m IS '過去 12 個月住院次數';
COMMENT ON COLUMN risk_assessments.gold_group IS 'GOLD 2011 ABE 分級 (A/B/E)';
COMMENT ON COLUMN risk_assessments.risk_score IS '風險分數 (0-100) - 向後相容欄位，從 gold_group 映射';
COMMENT ON COLUMN risk_assessments.risk_level IS '風險等級 - 向後相容欄位，從 gold_group 映射';

-- 索引
CREATE INDEX idx_risk_assessment_patient_assessed_at
    ON risk_assessments(patient_id, assessed_at DESC);

CREATE INDEX idx_risk_assessment_gold_group
    ON risk_assessments(gold_group);

COMMENT ON INDEX idx_risk_assessment_patient_assessed_at IS
    '病患風險評估歷史索引 - 支持時序查詢';

COMMENT ON INDEX idx_risk_assessment_gold_group IS
    'GOLD 分級索引 - 支持按風險等級篩選病患';


-- ============================================================================
-- Step 5: 建立 alerts 表 - 警示系統
-- ============================================================================

CREATE TABLE alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patient_profiles(user_id) ON DELETE CASCADE,

    -- 警示資訊
    alert_type alert_type_enum NOT NULL,
    severity alert_severity_enum NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,

    -- 警示狀態
    status alert_status_enum DEFAULT 'ACTIVE',

    -- 相關資料 (JSONB 格式)
    alert_metadata JSONB,

    -- 處理資訊
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by UUID REFERENCES users(user_id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES users(user_id),
    resolution_notes TEXT,

    -- 時間戳記
    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE alerts IS
    '警示系統表 - 儲存風險警示與通知記錄';

COMMENT ON COLUMN alerts.alert_type IS '警示類型';
COMMENT ON COLUMN alerts.severity IS '警示嚴重程度';
COMMENT ON COLUMN alerts.title IS '警示標題 (簡短描述)';
COMMENT ON COLUMN alerts.message IS '警示詳細訊息';
COMMENT ON COLUMN alerts.status IS '警示狀態 (ACTIVE/ACKNOWLEDGED/RESOLVED)';
COMMENT ON COLUMN alerts.alert_metadata IS 'JSON 格式的額外資訊 (如: {old_group: "A", new_group: "E", trigger_reason: "..."}';
COMMENT ON COLUMN alerts.acknowledged_at IS '確認時間';
COMMENT ON COLUMN alerts.acknowledged_by IS '確認者';
COMMENT ON COLUMN alerts.resolved_at IS '解決時間';
COMMENT ON COLUMN alerts.resolved_by IS '解決者';
COMMENT ON COLUMN alerts.resolution_notes IS '解決備註';

-- 索引
CREATE INDEX idx_alert_patient_status
    ON alerts(patient_id, status, triggered_at DESC)
    WHERE status IN ('ACTIVE', 'ACKNOWLEDGED');

CREATE INDEX idx_alert_severity_status
    ON alerts(severity, status)
    WHERE status = 'ACTIVE';

COMMENT ON INDEX idx_alert_patient_status IS
    '病患警示索引 - 快速查詢啟動中或已確認的警示';

COMMENT ON INDEX idx_alert_severity_status IS
    '嚴重警示索引 - 快速篩選啟動中的高優先級警示';


-- ============================================================================
-- Step 6: 建立 Trigger Function - 自動更新病患急性發作彙總
-- ============================================================================

CREATE OR REPLACE FUNCTION update_patient_exacerbation_summary()
RETURNS TRIGGER AS $$
BEGIN
    -- 在 INSERT/UPDATE/DELETE exacerbations 後，自動更新 patient_profiles 彙總欄位

    -- 判斷受影響的 patient_id
    DECLARE
        affected_patient_id UUID;
    BEGIN
        -- 根據操作類型取得 patient_id
        IF TG_OP = 'DELETE' THEN
            affected_patient_id := OLD.patient_id;
        ELSE
            affected_patient_id := NEW.patient_id;
        END IF;

        -- 更新 patient_profiles 彙總欄位
        UPDATE patient_profiles
        SET
            exacerbation_count_last_12m = (
                SELECT COUNT(*)
                FROM exacerbations
                WHERE patient_id = affected_patient_id
                AND onset_date >= CURRENT_DATE - INTERVAL '12 months'
            ),
            hospitalization_count_last_12m = (
                SELECT COUNT(*)
                FROM exacerbations
                WHERE patient_id = affected_patient_id
                AND onset_date >= CURRENT_DATE - INTERVAL '12 months'
                AND required_hospitalization = TRUE
            ),
            last_exacerbation_date = (
                SELECT MAX(onset_date)
                FROM exacerbations
                WHERE patient_id = affected_patient_id
            )
        WHERE user_id = affected_patient_id;

        RETURN NULL; -- AFTER trigger 不需要返回值
    END;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_patient_exacerbation_summary() IS
    'Trigger Function - 自動更新 patient_profiles 的急性發作彙總欄位';


-- 建立 Trigger
CREATE TRIGGER trigger_update_patient_exacerbation_summary
AFTER INSERT OR UPDATE OR DELETE ON exacerbations
FOR EACH ROW
EXECUTE FUNCTION update_patient_exacerbation_summary();

COMMENT ON TRIGGER trigger_update_patient_exacerbation_summary ON exacerbations IS
    'Trigger - 當 exacerbations 表變動時，自動更新 patient_profiles 彙總欄位';


-- ============================================================================
-- Step 7: 建立輔助視圖 - 病患最新風險評估摘要
-- ============================================================================

CREATE OR REPLACE VIEW patient_risk_summary AS
SELECT
    pp.user_id AS patient_id,
    pp.name,
    pp.birth_date,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, pp.birth_date))::INTEGER AS age,

    -- 最新風險評估
    ra.assessment_id,
    ra.gold_group,
    ra.cat_score,
    ra.mmrc_grade,
    ra.risk_score,  -- Hybrid 向後相容欄位
    ra.risk_level,  -- Hybrid 向後相容欄位
    ra.assessed_at,

    -- 急性發作彙總
    pp.exacerbation_count_last_12m,
    pp.hospitalization_count_last_12m,
    pp.last_exacerbation_date,

    -- 高風險標記
    CASE
        WHEN ra.gold_group = 'E' THEN TRUE
        WHEN pp.exacerbation_count_last_12m >= 2 THEN TRUE
        WHEN pp.hospitalization_count_last_12m >= 1 THEN TRUE
        ELSE FALSE
    END AS is_high_risk,

    -- 治療師資訊
    pp.therapist_id

FROM patient_profiles pp
LEFT JOIN LATERAL (
    SELECT *
    FROM risk_assessments
    WHERE patient_id = pp.user_id
    ORDER BY assessed_at DESC
    LIMIT 1
) ra ON TRUE;

COMMENT ON VIEW patient_risk_summary IS
    '病患風險評估摘要視圖 - 結合最新風險評估與急性發作彙總，用於 Dashboard KPI 顯示';


-- ============================================================================
-- Step 8: 建立索引優化視圖查詢
-- ============================================================================

-- 支持視圖的複合索引 (patient_id + assessed_at)
-- 已在 Step 4 建立 idx_risk_assessment_patient_assessed_at


-- ============================================================================
-- Rollback Script (備份用)
-- ============================================================================

-- 若需回滾，執行以下 SQL:
/*
BEGIN;

-- 刪除視圖
DROP VIEW IF EXISTS patient_risk_summary;

-- 刪除 Trigger
DROP TRIGGER IF EXISTS trigger_update_patient_exacerbation_summary ON exacerbations;
DROP FUNCTION IF EXISTS update_patient_exacerbation_summary();

-- 刪除表 (按相依順序)
DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS risk_assessments;
DROP TABLE IF EXISTS exacerbations;

-- 刪除 patient_profiles 新增欄位與索引
DROP INDEX IF EXISTS idx_patient_exacerbation_count;
ALTER TABLE patient_profiles DROP COLUMN IF EXISTS last_exacerbation_date;
ALTER TABLE patient_profiles DROP COLUMN IF EXISTS hospitalization_count_last_12m;
ALTER TABLE patient_profiles DROP COLUMN IF EXISTS exacerbation_count_last_12m;

-- 刪除 ENUM 型別
DROP TYPE IF EXISTS alert_status_enum;
DROP TYPE IF EXISTS alert_severity_enum;
DROP TYPE IF EXISTS alert_type_enum;
DROP TYPE IF EXISTS exacerbation_severity_enum;
DROP TYPE IF EXISTS gold_group_enum;

COMMIT;
*/

COMMIT;

-- ============================================================================
-- Migration 完成
-- ============================================================================

-- 驗證 Migration 是否成功
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 005 completed successfully!';
    RAISE NOTICE '   - Created 5 ENUM types for GOLD ABE classification';
    RAISE NOTICE '   - Extended patient_profiles with exacerbation summary fields';
    RAISE NOTICE '   - Created exacerbations table for tracking acute exacerbations';
    RAISE NOTICE '   - Created risk_assessments table with GOLD ABE + Hybrid legacy fields';
    RAISE NOTICE '   - Created alerts table for risk-based notifications';
    RAISE NOTICE '   - Created trigger for automatic exacerbation summary updates';
    RAISE NOTICE '   - Created patient_risk_summary view for Dashboard KPI';
    RAISE NOTICE '   ';
    RAISE NOTICE '📊 ADR Reference: ADR-013 v2.0 (GOLD 2011 ABE), ADR-014 (Hybrid Strategy)';
    RAISE NOTICE '🎯 Sprint 4: Risk Engine & Alert System - Database Schema Ready!';
END $$;
