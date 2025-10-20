/**
 * API Client for RespiraAlly Dashboard
 * Supports both real API and mock mode for development
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

const IS_MOCK_MODE = process.env.NEXT_PUBLIC_MOCK_MODE === 'true'
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'

// Create axios instance
const axiosInstance: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for authentication
axiosInstance.interceptors.request.use(
  (config) => {
    // Add auth token if exists
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Mock mode: log request
    if (IS_MOCK_MODE) {
      console.log(`[MOCK] ${config.method?.toUpperCase()} ${config.url}`, config.data)
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
axiosInstance.interceptors.response.use(
  (response: AxiosResponse) => {
    // Mock mode: log response
    if (IS_MOCK_MODE) {
      console.log(`[MOCK] Response:`, response.data)
    }
    return response
  },
  (error) => {
    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
    }

    // Mock mode: return mock error
    if (IS_MOCK_MODE) {
      console.error(`[MOCK] Error:`, error.message)
      return Promise.resolve({
        data: {
          error: {
            message: 'Mock mode error',
            details: error.message,
          },
        },
      })
    }

    return Promise.reject(error)
  }
)

/**
 * API Client wrapper with typed methods
 */
export class APIClient {
  private static instance: APIClient

  private constructor() {}

  public static getInstance(): APIClient {
    if (!APIClient.instance) {
      APIClient.instance = new APIClient()
    }
    return APIClient.instance
  }

  async get<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await axiosInstance.get<T>(url, config)
    return response.data
  }

  async post<T = unknown, D = Record<string, unknown>>(url: string, data?: D, config?: AxiosRequestConfig): Promise<T> {
    const response = await axiosInstance.post<T>(url, data, config)
    return response.data
  }

  async put<T = unknown, D = Record<string, unknown>>(url: string, data?: D, config?: AxiosRequestConfig): Promise<T> {
    const response = await axiosInstance.put<T>(url, data, config)
    return response.data
  }

  async delete<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await axiosInstance.delete<T>(url, config)
    return response.data
  }

  async patch<T = unknown, D = Record<string, unknown>>(url: string, data?: D, config?: AxiosRequestConfig): Promise<T> {
    const response = await axiosInstance.patch<T>(url, data, config)
    return response.data
  }
}

// Export singleton instance
export const apiClient = APIClient.getInstance()

// Export raw axios instance for advanced use
export { axiosInstance }

// Mock mode indicator
export const isMockMode = IS_MOCK_MODE
