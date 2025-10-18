-- Alembic Migration Script
-- Revision: 002
-- Description: 新增病患健康資料欄位 (醫院病歷號、體徵數據、吸菸史)
-- Previous: 001_create_core_tables.sql
-- Created: 2025-10-18

BEGIN;

-- ============================================================================
-- Step 1: 創建吸菸狀態 ENUM 型別
-- ============================================================================

CREATE TYPE smoking_status_enum AS ENUM ('NEVER', 'FORMER', 'CURRENT');

COMMENT ON TYPE smoking_status_enum IS '吸菸狀態: NEVER=從未吸菸, FORMER=已戒菸, CURRENT=目前吸菸';


-- ============================================================================
-- Step 2: 新增欄位到 patient_profiles 表
-- ============================================================================

-- 醫院整合資訊
ALTER TABLE patient_profiles
    ADD COLUMN hospital_medical_record_number VARCHAR(50);

COMMENT ON COLUMN patient_profiles.hospital_medical_record_number IS
    '醫院病歷號 - 用於與醫院資訊系統整合 (Nullable)';

-- 體徵數據
ALTER TABLE patient_profiles
    ADD COLUMN height_cm INTEGER,
    ADD COLUMN weight_kg DECIMAL(5,1);

COMMENT ON COLUMN patient_profiles.height_cm IS '身高 (單位: 公分)';
COMMENT ON COLUMN patient_profiles.weight_kg IS '體重 (單位: 公斤, 保留1位小數)';

-- 吸菸史
ALTER TABLE patient_profiles
    ADD COLUMN smoking_status smoking_status_enum,
    ADD COLUMN smoking_years INTEGER;

COMMENT ON COLUMN patient_profiles.smoking_status IS '吸菸狀態';
COMMENT ON COLUMN patient_profiles.smoking_years IS '吸菸年數 (若為從未吸菸或已戒菸, 表示曾經吸菸的年數)';


-- ============================================================================
-- Step 3: 新增數據完整性約束
-- ============================================================================

-- 身高範圍約束 (50-250 cm)
ALTER TABLE patient_profiles
    ADD CONSTRAINT patient_height_range_check
    CHECK (height_cm IS NULL OR (height_cm >= 50 AND height_cm <= 250));

-- 體重範圍約束 (20-300 kg)
ALTER TABLE patient_profiles
    ADD CONSTRAINT patient_weight_range_check
    CHECK (weight_kg IS NULL OR (weight_kg >= 20 AND weight_kg <= 300));

-- 吸菸年數範圍約束 (0-100 年)
ALTER TABLE patient_profiles
    ADD CONSTRAINT patient_smoking_years_range_check
    CHECK (smoking_years IS NULL OR (smoking_years >= 0 AND smoking_years <= 100));

-- 吸菸年數邏輯性約束 (不可超過年齡)
ALTER TABLE patient_profiles
    ADD CONSTRAINT patient_smoking_years_logic_check
    CHECK (
        smoking_years IS NULL OR
        smoking_years <= EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date))
    );

-- 吸菸狀態與年數一致性約束
ALTER TABLE patient_profiles
    ADD CONSTRAINT patient_smoking_consistency_check
    CHECK (
        -- 從未吸菸者: smoking_years 必須為 NULL 或 0
        (smoking_status = 'NEVER' AND (smoking_years IS NULL OR smoking_years = 0)) OR
        -- 曾經/目前吸菸者: smoking_years 必須 > 0
        (smoking_status IN ('FORMER', 'CURRENT') AND smoking_years > 0) OR
        -- 允許兩者都為 NULL (尚未填寫)
        (smoking_status IS NULL)
    );


-- ============================================================================
-- Step 4: 新增索引
-- ============================================================================

-- 醫院病歷號索引 (用於跨系統查詢)
CREATE INDEX idx_patient_medical_record_number
    ON patient_profiles(hospital_medical_record_number)
    WHERE hospital_medical_record_number IS NOT NULL;

COMMENT ON INDEX idx_patient_medical_record_number IS
    '醫院病歷號索引 - 支持跨系統整合查詢 (部分索引, 僅索引非 NULL 值)';

-- 吸菸狀態索引 (用於高風險篩選)
CREATE INDEX idx_patient_smoking_status
    ON patient_profiles(smoking_status)
    WHERE smoking_status IN ('FORMER', 'CURRENT');

COMMENT ON INDEX idx_patient_smoking_status IS
    '吸菸狀態索引 - 支持高風險病患篩選 (僅索引曾經/目前吸菸者)';


-- ============================================================================
-- Step 5: 更新 medical_history JSONB 欄位註解
-- ============================================================================

COMMENT ON COLUMN patient_profiles.medical_history IS
    'JSONB - 病史資訊: {copd_stage: "III", comorbidities: [...], medications: [...], fev1_percent: 45}';

COMMENT ON COLUMN patient_profiles.contact_info IS
    'JSONB - 聯絡資訊: {phone: "...", address: "...", emergency_contact: {name: "...", phone: "..."}}';


-- ============================================================================
-- Step 6: 創建輔助視圖 (Optional - 計算 BMI)
-- ============================================================================

-- 創建 BMI 計算視圖
CREATE OR REPLACE VIEW patient_health_summary AS
SELECT
    user_id,
    name,
    birth_date,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date))::INTEGER AS age,
    gender,
    height_cm,
    weight_kg,
    -- 計算 BMI (體重kg / (身高m)^2)
    CASE
        WHEN height_cm IS NOT NULL AND weight_kg IS NOT NULL AND height_cm > 0
        THEN ROUND((weight_kg / ((height_cm / 100.0) ^ 2))::NUMERIC, 1)
        ELSE NULL
    END AS bmi,
    -- BMI 分級
    CASE
        WHEN height_cm IS NULL OR weight_kg IS NULL OR height_cm <= 0 THEN NULL
        WHEN weight_kg / ((height_cm / 100.0) ^ 2) < 18.5 THEN 'UNDERWEIGHT'
        WHEN weight_kg / ((height_cm / 100.0) ^ 2) < 24 THEN 'NORMAL'
        WHEN weight_kg / ((height_cm / 100.0) ^ 2) < 27 THEN 'OVERWEIGHT'
        ELSE 'OBESE'
    END AS bmi_category,
    smoking_status,
    smoking_years,
    hospital_medical_record_number,
    therapist_id
FROM patient_profiles;

COMMENT ON VIEW patient_health_summary IS
    '病患健康摘要視圖 - 包含年齡、BMI 計算與分級';


-- ============================================================================
-- Rollback Script (備份用)
-- ============================================================================

-- 若需回滾, 執行以下 SQL:
/*
BEGIN;

-- 刪除視圖
DROP VIEW IF EXISTS patient_health_summary;

-- 刪除索引
DROP INDEX IF EXISTS idx_patient_smoking_status;
DROP INDEX IF EXISTS idx_patient_medical_record_number;

-- 刪除約束
ALTER TABLE patient_profiles DROP CONSTRAINT IF EXISTS patient_smoking_consistency_check;
ALTER TABLE patient_profiles DROP CONSTRAINT IF EXISTS patient_smoking_years_logic_check;
ALTER TABLE patient_profiles DROP CONSTRAINT IF EXISTS patient_smoking_years_range_check;
ALTER TABLE patient_profiles DROP CONSTRAINT IF EXISTS patient_weight_range_check;
ALTER TABLE patient_profiles DROP CONSTRAINT IF EXISTS patient_height_range_check;

-- 刪除欄位
ALTER TABLE patient_profiles DROP COLUMN IF EXISTS smoking_years;
ALTER TABLE patient_profiles DROP COLUMN IF EXISTS smoking_status;
ALTER TABLE patient_profiles DROP COLUMN IF EXISTS weight_kg;
ALTER TABLE patient_profiles DROP COLUMN IF EXISTS height_cm;
ALTER TABLE patient_profiles DROP COLUMN IF EXISTS hospital_medical_record_number;

-- 刪除 ENUM 型別
DROP TYPE IF EXISTS smoking_status_enum;

COMMIT;
*/

COMMIT;

-- ============================================================================
-- Migration 完成
-- ============================================================================

-- 驗證 Migration 是否成功
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 002 completed successfully!';
    RAISE NOTICE '   - Added hospital_medical_record_number column';
    RAISE NOTICE '   - Added height_cm and weight_kg columns';
    RAISE NOTICE '   - Added smoking_status and smoking_years columns';
    RAISE NOTICE '   - Created 2 indexes for optimization';
    RAISE NOTICE '   - Created patient_health_summary view with BMI calculation';
END $$;
