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

  // Computed fields
  bmi?: number
  age?: number
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
