/**
 * KPI Types - TypeScript definitions for patient KPI data
 * Based on backend API: GET /patients/{patient_id}/kpis
 */

// ============================================================================
// KPI Response Types
// ============================================================================

export interface PatientKPI {
  patient_id: string // UUID
  updated_at: string // ISO 8601

  // Adherence Metrics
  medication_adherence_rate?: number // 0-100 percentage
  log_submission_rate?: number // 0-100 percentage
  survey_completion_rate?: number // 0-100 percentage

  // Health Metrics
  latest_bmi?: number
  latest_spo2?: number // Blood oxygen saturation (%)
  latest_heart_rate?: number // beats per minute
  latest_systolic_bp?: number // Systolic blood pressure
  latest_diastolic_bp?: number // Diastolic blood pressure

  // Survey Scores
  latest_cat_score?: number // COPD Assessment Test (0-40)
  latest_mmrc_score?: number // Modified Medical Research Council (0-4)

  // Risk Assessment
  risk_score?: number // 0-100
  risk_level?: 'low' | 'medium' | 'high' | 'critical'

  // Activity
  last_log_date?: string // YYYY-MM-DD
  days_since_last_log?: number
}

// ============================================================================
// KPI Card Props Types
// ============================================================================

export interface KPICardProps {
  title: string
  value: string | number | undefined
  unit?: string
  status?: 'good' | 'warning' | 'danger' | 'neutral'
  icon?: string
  description?: string
}

export interface HealthMetric {
  label: string
  value: number | undefined
  unit: string
  normalRange?: string
  status: 'good' | 'warning' | 'danger'
}
