/**
 * Patient Types - TypeScript definitions for patient data
 * Based on backend schemas: respira_ally/core/schemas/patient.py
 */

// ============================================================================
// Enums
// ============================================================================

export enum Gender {
  MALE = 'MALE',
  FEMALE = 'FEMALE',
  OTHER = 'OTHER',
}

export enum RiskLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

// GOLD ABE Classification (Sprint 4)
export enum GoldGroup {
  A = 'A', // Low risk: CAT<10 AND mMRC<2
  B = 'B', // Medium risk: CAT>=10 OR mMRC>=2
  E = 'E', // High risk: CAT>=10 AND mMRC>=2
}

export enum COPDStage {
  STAGE_1 = 'stage_1',
  STAGE_2 = 'stage_2',
  STAGE_3 = 'stage_3',
  STAGE_4 = 'stage_4',
  UNKNOWN = 'unknown',
}

export enum SmokingStatus {
  NEVER = 'NEVER',
  FORMER = 'FORMER',
  CURRENT = 'CURRENT',
}

// ============================================================================
// Patient Base Types
// ============================================================================

export interface PatientBase {
  name: string // Full name
  birth_date: string // YYYY-MM-DD
  gender?: Gender
}

// ============================================================================
// Risk Assessment Types (Sprint 4 - GOLD ABE)
// ============================================================================

export interface RiskAssessmentSummary {
  gold_group: GoldGroup // GOLD ABE group (A, B, E)
  risk_level: RiskLevel // Mapped risk level (low, medium, high)
  risk_score: number // Mapped risk score (25, 50, 75)
  cat_score: number // CAT score (0-40)
  mmrc_grade: number // mMRC grade (0-4)
  exacerbation_count_12m: number // Exacerbations in last 12 months
  hospitalization_count_12m: number // Hospitalizations in last 12 months
  assessed_at: string // ISO 8601 timestamp
}

// ============================================================================
// Patient Response Types
// ============================================================================

export interface PatientResponse extends PatientBase {
  user_id: string // UUID
  therapist_id?: string // UUID

  // Physical metrics
  height_cm?: number
  weight_kg?: number

  // Contact info
  phone?: string

  // Exacerbation history (Sprint 4 - Risk Assessment)
  exacerbation_count_last_12m?: number
  hospitalization_count_last_12m?: number
  last_exacerbation_date?: string // YYYY-MM-DD

  // Computed fields
  bmi?: number
  age?: number

  // GOLD ABE Risk Assessment (Sprint 4)
  gold_group?: GoldGroup // GOLD ABE group (A, B, E)
  latest_risk_assessment?: RiskAssessmentSummary // Latest risk assessment details
}

export interface PatientListResponse {
  items: PatientResponse[]
  total: number
  page: number // 0-indexed
  page_size: number
  has_next: boolean
}

// ============================================================================
// Patient Detail Types (Future expansion)
// ============================================================================

export interface PatientDetailResponse extends PatientResponse {
  smoking_status?: SmokingStatus
  smoking_years?: number
  hospital_medical_record_number?: string
  created_at?: string // ISO 8601
  updated_at?: string // ISO 8601
}

// ============================================================================
// Query Parameters Types
// ============================================================================

export interface PatientsQuery {
  // Filtering
  risk_bucket?: RiskLevel // Filter by risk level
  adherence_rate_lte?: number // Filter by adherence rate <= value (0-100)
  last_active_gte?: string // Filter by last active date >= value (YYYY-MM-DD)

  // Sorting
  sort_by?: 'name' | 'age' | 'risk_level' | 'last_active' | 'adherence_rate'

  // Pagination
  skip?: number // Offset (default: 0)
  limit?: number // Items per page (default: 20, max: 100)
}

// ============================================================================
// Patient Create/Update Types
// ============================================================================

export interface PatientCreate extends PatientBase {
  therapist_id: string // UUID

  // Optional fields
  height_cm?: number
  weight_kg?: number
  phone?: string
}

export interface PatientUpdate {
  name?: string
  birth_date?: string // YYYY-MM-DD
  gender?: Gender
  height_cm?: number
  weight_kg?: number
  phone?: string
  therapist_id?: string // UUID
}
