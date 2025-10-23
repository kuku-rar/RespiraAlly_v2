/**
 * Auth Types - LIFF Patient Registration
 * Based on backend schemas: respira_ally/core/schemas/auth.py
 */

// ============================================================================
// Enums
// ============================================================================

export enum UserRole {
  PATIENT = 'PATIENT',
  THERAPIST = 'THERAPIST',
}

export enum COPDStage {
  STAGE_1 = 'stage_1',
  STAGE_2 = 'stage_2',
  STAGE_3 = 'stage_3',
  STAGE_4 = 'stage_4',
  UNKNOWN = 'unknown',
}

// ============================================================================
// Patient Registration Types
// ============================================================================

export interface PatientRegisterRequest {
  // LINE Authentication
  line_user_id: string
  line_display_name?: string
  line_picture_url?: string

  // Basic Information
  full_name: string
  date_of_birth: string // YYYY-MM-DD format
  gender: 'male' | 'female' | 'other'
  phone_number?: string

  // Medical Information
  hospital_patient_id?: string // 醫院病歷號
  height_cm?: number // 身高 (cm)
  weight_kg?: number // 體重 (kg)
  smoking_years?: number // 菸齡 (年)

  // Emergency Contact
  emergency_contact_name?: string
  emergency_contact_phone?: string
}

export interface UserInfo {
  user_id: string // UUID
  role: UserRole
  email?: string // therapist only
  line_user_id?: string // patient only
  display_name?: string
  is_active: boolean
  created_at: string // ISO 8601
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string // 'bearer'
  expires_in: number
  user: UserInfo
}

// ============================================================================
// LINE LIFF Types
// ============================================================================

export interface LiffProfile {
  userId: string
  displayName: string
  pictureUrl?: string
  statusMessage?: string
}

export interface LiffContext {
  type: 'utou' | 'room' | 'group' | 'square_chat' | 'external' | 'none'
  userId?: string
  utouId?: string
  roomId?: string
  groupId?: string
  squareChatId?: string
}
