/**
 * Auth API - Authentication endpoints with Mock support
 */

import { apiClient, isMockMode } from '../api-client'
import {
  LoginResponse,
  TherapistLoginRequest,
  TherapistRegisterRequest,
  RefreshTokenRequest,
  RefreshTokenResponse,
  LogoutRequest,
  UserRole,
} from '../types/auth'

// ============================================================================
// Mock Data
// ============================================================================

const MOCK_USER = {
  user_id: '00000000-0000-0000-0000-000000000001',
  role: UserRole.THERAPIST,
  email: 'therapist@example.com',
  display_name: '陳治療師',
  is_active: true,
  created_at: new Date().toISOString(),
}

const MOCK_LOGIN_RESPONSE: LoginResponse = {
  access_token: 'mock_access_token_12345',
  refresh_token: 'mock_refresh_token_67890',
  token_type: 'bearer',
  expires_in: 28800, // 8 hours
  user: MOCK_USER,
}

// ============================================================================
// Auth API
// ============================================================================

export const authApi = {
  /**
   * Therapist Login - POST /auth/therapist/login
   */
  async loginTherapist(data: TherapistLoginRequest): Promise<LoginResponse> {
    if (isMockMode) {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 800))
      console.log('[MOCK] POST /auth/therapist/login', data)

      // Mock validation
      if (!data.email || !data.password) {
        throw new Error('Email and password are required')
      }

      // Mock authentication success
      return MOCK_LOGIN_RESPONSE
    }

    // Real API call
    return apiClient.post<LoginResponse>('/auth/therapist/login', data)
  },

  /**
   * Therapist Register - POST /auth/therapist/register
   */
  async registerTherapist(data: TherapistRegisterRequest): Promise<LoginResponse> {
    if (isMockMode) {
      await new Promise(resolve => setTimeout(resolve, 1000))
      console.log('[MOCK] POST /auth/therapist/register', data)

      // Mock validation
      if (!data.email || !data.password || !data.full_name) {
        throw new Error('All fields are required')
      }

      if (data.password.length < 8) {
        throw new Error('Password must be at least 8 characters')
      }

      // Return mock response with registered user
      return {
        ...MOCK_LOGIN_RESPONSE,
        user: {
          ...MOCK_USER,
          email: data.email,
          display_name: data.full_name,
        },
      }
    }

    return apiClient.post<LoginResponse>('/auth/therapist/register', data)
  },

  /**
   * Refresh Token - POST /auth/refresh
   */
  async refreshToken(data: RefreshTokenRequest): Promise<RefreshTokenResponse> {
    if (isMockMode) {
      await new Promise(resolve => setTimeout(resolve, 500))
      console.log('[MOCK] POST /auth/refresh', { refresh_token: '***' })

      return {
        access_token: 'mock_new_access_token_' + Date.now(),
        refresh_token: 'mock_new_refresh_token_' + Date.now(),
        token_type: 'bearer',
        expires_in: 28800,
      }
    }

    return apiClient.post<RefreshTokenResponse>('/auth/refresh', data)
  },

  /**
   * Logout - POST /auth/logout
   */
  async logout(data?: LogoutRequest): Promise<void> {
    if (isMockMode) {
      await new Promise(resolve => setTimeout(resolve, 300))
      console.log('[MOCK] POST /auth/logout', data)
      return
    }

    await apiClient.post<void>('/auth/logout', data || {})
  },

  /**
   * Get Current User - GET /auth/me
   */
  async getCurrentUser(): Promise<LoginResponse['user']> {
    if (isMockMode) {
      await new Promise(resolve => setTimeout(resolve, 400))
      console.log('[MOCK] GET /auth/me')
      return MOCK_USER
    }

    return apiClient.get<LoginResponse['user']>('/auth/me')
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
    if (typeof window === 'undefined') return

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
    if (typeof window === 'undefined') return null
    return localStorage.getItem('access_token')
  },

  /**
   * Get stored refresh token
   */
  getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem('refresh_token')
  },

  /**
   * Get stored user info
   */
  getUser(): LoginResponse['user'] | null {
    if (typeof window === 'undefined') return null
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  },

  /**
   * Clear all tokens and user data
   */
  clearTokens(): void {
    if (typeof window === 'undefined') return

    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    localStorage.removeItem('token_expires_at')
  },

  /**
   * Check if token is expired
   */
  isTokenExpired(): boolean {
    if (typeof window === 'undefined') return true

    const expiresAt = localStorage.getItem('token_expires_at')
    if (!expiresAt) return true

    return Date.now() > parseInt(expiresAt, 10)
  },
}
