/**
 * Survey Types - TypeScript definitions for survey data
 * Based on backend schemas: respira_ally/core/schemas/survey.py
 */

// ============================================================================
// Enums
// ============================================================================

export enum SurveyType {
  CAT = 'CAT',
  MMRC = 'mMRC',
}

// ============================================================================
// Survey Response Types
// ============================================================================

export interface SurveyResponse {
  response_id: string // UUID
  patient_id: string // UUID
  survey_type: SurveyType
  score: number
  responses: Record<string, number> // Question ID -> Answer value
  completed_at: string // ISO 8601
  created_at: string // ISO 8601
  updated_at?: string // ISO 8601
}

export interface SurveyListResponse {
  items: SurveyResponse[]
  total: number
  page: number // 0-indexed
  page_size: number
  has_next: boolean
}

// ============================================================================
// Survey Stats Types
// ============================================================================

export interface SurveyStats {
  total_count: number
  avg_score: number
  min_score: number
  max_score: number
  latest_score?: number
  latest_date?: string // ISO 8601
  trend?: 'improving' | 'stable' | 'declining'
}

// ============================================================================
// Query Parameters Types
// ============================================================================

export interface SurveysQuery {
  patient_id?: string // UUID
  survey_type?: SurveyType
  start_date?: string // YYYY-MM-DD
  end_date?: string // YYYY-MM-DD
  page?: number // 0-indexed (default: 0)
  page_size?: number // Items per page (default: 20, max: 100)
}

// ============================================================================
// Survey Create Types
// ============================================================================

export interface CATSurveyCreate {
  patient_id: string // UUID
  responses: {
    cough: number // 0-5
    phlegm: number // 0-5
    chest_tightness: number // 0-5
    breathlessness: number // 0-5
    activity_limitation: number // 0-5
    confidence: number // 0-5
    sleep: number // 0-5
    energy: number // 0-5
  }
}

export interface MMRCSurveyCreate {
  patient_id: string // UUID
  responses: {
    dyspnea_grade: number // 0-4 (Grade 0-4)
  }
}

// ============================================================================
// Survey Display Types (for UI)
// ============================================================================

export interface SurveyDisplayItem extends SurveyResponse {
  // Computed fields for display
  scoreLabel: string // e.g., "低影響 (0-10)"
  scoreSeverity: 'low' | 'medium' | 'high' | 'very-high'
  formattedDate: string // e.g., "2025-10-23 14:30"
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Get CAT score severity classification
 * Low: 0-10, Medium: 11-20, High: 21-30, Very High: 31-40
 */
export function getCATSeverity(score: number): SurveyDisplayItem['scoreSeverity'] {
  if (score <= 10) return 'low'
  if (score <= 20) return 'medium'
  if (score <= 30) return 'high'
  return 'very-high'
}

/**
 * Get CAT score label in Traditional Chinese
 */
export function getCATScoreLabel(score: number): string {
  const severity = getCATSeverity(score)
  const labels = {
    low: '低影響',
    medium: '中度影響',
    high: '高度影響',
    'very-high': '極高影響',
  }
  return `${labels[severity]} (${score}/40)`
}

/**
 * Get mMRC dyspnea grade label
 * Grade 0-4
 */
export function getMMRCGradeLabel(score: number): string {
  const labels = {
    0: 'Grade 0 - 僅在劇烈運動時喘',
    1: 'Grade 1 - 快走或爬緩坡時喘',
    2: 'Grade 2 - 走路比同齡慢或需停下來喘氣',
    3: 'Grade 3 - 走100公尺或數分鐘就需停下來喘氣',
    4: 'Grade 4 - 穿衣或脫衣時就會喘',
  }
  return labels[score as keyof typeof labels] || `Grade ${score}`
}
