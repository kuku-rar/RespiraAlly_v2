/**
 * Auth API - Patient Registration with Mock support
 */

import { apiClient, isMockMode } from '../services/api-client'
import {
  LoginResponse,
  PatientRegisterRequest,
  UserRole,
  COPDStage,
} from '../types/auth'

// ============================================================================
// Mock Data
// ============================================================================

const MOCK_REGISTER_RESPONSE: LoginResponse = {
  access_token: 'mock_patient_access_token_12345',
  refresh_token: 'mock_patient_refresh_token_67890',
  token_type: 'bearer',
  expires_in: 28800, // 8 hours
  user: {
    user_id: '00000000-0000-0000-0000-000000000002',
    role: UserRole.PATIENT,
    line_user_id: 'Umock1234567890abcdefghijklmnopqr',
    display_name: '測試病患',
    is_active: true,
    created_at: new Date().toISOString(),
  },
}

// ============================================================================
// Auth API
// ============================================================================

export const authApi = {
  /**
   * Patient Registration - POST /auth/patient/register
   */
  async registerPatient(data: PatientRegisterRequest): Promise<LoginResponse> {
    if (isMockMode) {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 1200))
      console.log('[MOCK] POST /auth/patient/register', data)

      // Mock validation
      if (!data.line_user_id || !data.full_name || !data.date_of_birth) {
        throw new Error('必填欄位不可為空')
      }

      if (!data.gender) {
        throw new Error('請選擇性別')
      }

      if (data.copd_stage === COPDStage.UNKNOWN) {
        throw new Error('請選擇 COPD 分期')
      }

      // Return mock response with registered user data
      return {
        ...MOCK_REGISTER_RESPONSE,
        user: {
          ...MOCK_REGISTER_RESPONSE.user,
          line_user_id: data.line_user_id,
          display_name: data.full_name,
        },
      }
    }

    // Real API call
    return apiClient.post<LoginResponse>('/auth/patient/register', data)
  },
}

// ============================================================================
// Token Management Utilities
// ============================================================================

export const tokenManager = {
  /**
   * Store tokens in localStorage
   */
  storeTokens(response: LoginResponse): void {
    localStorage.setItem('access_token', response.access_token)
    localStorage.setItem('refresh_token', response.refresh_token)
    localStorage.setItem('user', JSON.stringify(response.user))

    // Store expiration time
    const expiresAt = Date.now() + response.expires_in * 1000
    localStorage.setItem('token_expires_at', expiresAt.toString())
  },

  /**
   * Get stored access token
   */
  getAccessToken(): string | null {
    return localStorage.getItem('access_token')
  },

  /**
   * Get stored user info
   */
  getUser(): LoginResponse['user'] | null {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  },

  /**
   * Clear all tokens and user data
   */
  clearTokens(): void {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    localStorage.removeItem('token_expires_at')
  },

  /**
   * Check if user is already registered
   */
  isRegistered(): boolean {
    const token = this.getAccessToken()
    const user = this.getUser()
    return !!(token && user && user.role === UserRole.PATIENT)
  },
}
