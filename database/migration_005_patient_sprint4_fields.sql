-- ============================================================================
-- Migration 005: Patient Profile Sprint 4 Fields
-- ============================================================================
-- Date: 2025-10-25
-- Author: Claude Code AI (TaskMaster Hub)
-- Decision: ADR-016 - Lightweight Migration Approach
--
-- Purpose: Add Sprint 4 exacerbation summary fields to patient_profiles table
--
-- Scope:
--   ✅ Add exacerbation_count_last_12m (Integer, default=0)
--   ✅ Add hospitalization_count_last_12m (Integer, default=0)
--   ✅ Add last_exacerbation_date (Date, nullable)
--   ✅ Apply to both production and development schemas
--
-- NOT Included (deferred to full Sprint 4 implementation):
--   ❌ exacerbations table creation
--   ❌ risk_assessments table creation
--   ❌ alerts table creation
--   ❌ Auto-update triggers
-- ============================================================================

-- ============================================================================
-- Production Schema Migration
-- ============================================================================

\echo '========================================================================'
\echo 'Migration 005: Adding Sprint 4 Fields to production.patient_profiles'
\echo '========================================================================'

-- Add exacerbation_count_last_12m column
ALTER TABLE production.patient_profiles
ADD COLUMN IF NOT EXISTS exacerbation_count_last_12m INTEGER NOT NULL DEFAULT 0;

COMMENT ON COLUMN production.patient_profiles.exacerbation_count_last_12m IS
'Number of acute exacerbations in last 12 months (auto-updated by trigger in full Sprint 4)';

-- Add hospitalization_count_last_12m column
ALTER TABLE production.patient_profiles
ADD COLUMN IF NOT EXISTS hospitalization_count_last_12m INTEGER NOT NULL DEFAULT 0;

COMMENT ON COLUMN production.patient_profiles.hospitalization_count_last_12m IS
'Number of hospitalizations in last 12 months (auto-updated by trigger in full Sprint 4)';

-- Add last_exacerbation_date column
ALTER TABLE production.patient_profiles
ADD COLUMN IF NOT EXISTS last_exacerbation_date DATE;

COMMENT ON COLUMN production.patient_profiles.last_exacerbation_date IS
'Date of last exacerbation (auto-updated by trigger in full Sprint 4)';

\echo '✅ Production schema migration completed'

-- ============================================================================
-- Development Schema Migration
-- ============================================================================

\echo '========================================================================'
\echo 'Migration 005: Adding Sprint 4 Fields to development.patient_profiles'
\echo '========================================================================'

-- Add exacerbation_count_last_12m column
ALTER TABLE development.patient_profiles
ADD COLUMN IF NOT EXISTS exacerbation_count_last_12m INTEGER NOT NULL DEFAULT 0;

COMMENT ON COLUMN development.patient_profiles.exacerbation_count_last_12m IS
'Number of acute exacerbations in last 12 months (auto-updated by trigger in full Sprint 4)';

-- Add hospitalization_count_last_12m column
ALTER TABLE development.patient_profiles
ADD COLUMN IF NOT EXISTS hospitalization_count_last_12m INTEGER NOT NULL DEFAULT 0;

COMMENT ON COLUMN development.patient_profiles.hospitalization_count_last_12m IS
'Number of hospitalizations in last 12 months (auto-updated by trigger in full Sprint 4)';

-- Add last_exacerbation_date column
ALTER TABLE development.patient_profiles
ADD COLUMN IF NOT EXISTS last_exacerbation_date DATE;

COMMENT ON COLUMN development.patient_profiles.last_exacerbation_date IS
'Date of last exacerbation (auto-updated by trigger in full Sprint 4)';

\echo '✅ Development schema migration completed'

-- ============================================================================
-- Verification
-- ============================================================================

\echo ''
\echo '========================================================================'
\echo 'Verification: Checking new columns in both schemas'
\echo '========================================================================'

\echo ''
\echo '📋 Production Schema - patient_profiles columns:'
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'production'
  AND table_name = 'patient_profiles'
  AND column_name IN ('exacerbation_count_last_12m', 'hospitalization_count_last_12m', 'last_exacerbation_date')
ORDER BY column_name;

\echo ''
\echo '📋 Development Schema - patient_profiles columns:'
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'development'
  AND table_name = 'patient_profiles'
  AND column_name IN ('exacerbation_count_last_12m', 'hospitalization_count_last_12m', 'last_exacerbation_date')
ORDER BY column_name;

\echo ''
\echo '========================================================================'
\echo '✅ Migration 005 Complete!'
\echo '========================================================================'
\echo ''
\echo '📋 Next Steps:'
\echo '   1. Test generate_test_data.py to verify model sync'
\echo '   2. Verify data insertion works correctly'
\echo '   3. Commit dual-schema architecture changes'
\echo ''
\echo '📝 Notes:'
\echo '   - Full Sprint 4 migration (exacerbations, risk_assessments, alerts tables)'
\echo '     will be created when implementing those features'
\echo '   - Auto-update triggers will be added in full Sprint 4 implementation'
\echo ''
