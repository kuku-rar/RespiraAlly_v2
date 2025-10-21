/**
 * Auth Types - TypeScript definitions for authentication
 * Based on backend schemas: respira_ally/core/schemas/auth.py
 */

// ============================================================================
// Enums
// ============================================================================

export enum UserRole {
  PATIENT = 'PATIENT',
  THERAPIST = 'THERAPIST',
}

// ============================================================================
// JWT Token Types
// ============================================================================

export interface TokenPayload {
  sub: string // Subject (user_id)
  role: UserRole
  type: 'access' | 'refresh'
  exp: number // Expiration timestamp (Unix epoch)
  iat: number // Issued at timestamp (Unix epoch)
  jti?: string // JWT ID for token revocation
  scope?: string[] // Token scopes/permissions
}

export interface TokenData {
  user_id: string // UUID
  role: UserRole
  token_type: 'access' | 'refresh'
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string // 'bearer'
  expires_in: number // Access token expiration in seconds
  refresh_expires_in: number // Refresh token expiration in seconds
}

// ============================================================================
// Login Request/Response Types
// ============================================================================

export interface PatientLoginRequest {
  line_user_id: string
  line_access_token?: string
}

export interface TherapistLoginRequest {
  email: string
  password: string
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
// Token Refresh Types
// ============================================================================

export interface RefreshTokenRequest {
  refresh_token: string
}

export interface RefreshTokenResponse {
  access_token: string
  refresh_token?: string // if rotation is enabled
  token_type: string
  expires_in: number
}

// ============================================================================
// Logout Types
// ============================================================================

export interface LogoutRequest {
  revoke_all_tokens?: boolean // default: false
}

// ============================================================================
// Registration Types
// ============================================================================

export interface TherapistRegisterRequest {
  email: string
  password: string
  full_name: string
}
