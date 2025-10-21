/**
 * Daily Log API - LIFF Daily Health Log Submission
 * Mock 模式支援前端獨立開發
 */

import { apiClient, IS_MOCK_MODE } from '../services/api-client'
import type {
  DailyLogCreate,
  DailyLogResponse,
  DailyLogListResponse,
} from '../types/daily-log'

// ============================================================================
// Mock Data
// ============================================================================

const MOCK_LOG_RESPONSE: DailyLogResponse = {
  log_id: 'mock-log-id-123',
  patient_id: 'mock-patient-id-456',
  log_date: new Date().toISOString().split('T')[0],
  medication_taken: true,
  water_intake_ml: 2000,
  steps_count: 5000,
  symptoms: '輕微咳嗽，無其他不適',
  mood: 'GOOD',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
}

const MOCK_LOGS: DailyLogResponse[] = [
  {
    log_id: 'log-1',
    patient_id: 'mock-patient-id-456',
    log_date: '2025-10-20',
    medication_taken: true,
    water_intake_ml: 2000,
    steps_count: 5000,
    symptoms: '輕微咳嗽',
    mood: 'GOOD',
    created_at: '2025-10-20T08:30:00Z',
    updated_at: '2025-10-20T08:30:00Z',
  },
  {
    log_id: 'log-2',
    patient_id: 'mock-patient-id-456',
    log_date: '2025-10-19',
    medication_taken: true,
    water_intake_ml: 1800,
    steps_count: 4500,
    symptoms: '呼吸順暢',
    mood: 'GOOD',
    created_at: '2025-10-19T09:00:00Z',
    updated_at: '2025-10-19T09:00:00Z',
  },
  {
    log_id: 'log-3',
    patient_id: 'mock-patient-id-456',
    log_date: '2025-10-18',
    medication_taken: false,
    water_intake_ml: 1500,
    steps_count: 3000,
    symptoms: '呼吸急促，輕微胸悶',
    mood: 'NEUTRAL',
    created_at: '2025-10-18T10:15:00Z',
    updated_at: '2025-10-18T10:15:00Z',
  },
]

// ============================================================================
// API Functions
// ============================================================================

export const dailyLogApi = {
  /**
   * 提交每日日誌（LIFF 表單）
   */
  async createLog(data: DailyLogCreate): Promise<DailyLogResponse> {
    if (IS_MOCK_MODE) {
      // 模擬延遲 (600-1200ms)
      await new Promise((resolve) =>
        setTimeout(resolve, 600 + Math.random() * 600)
      )

      console.log('[MOCK] POST /daily-logs', data)

      // 驗證必填欄位
      if (!data.log_date || data.medication_taken === undefined || !data.water_intake_ml) {
        throw new Error('必填欄位不可為空')
      }

      // 驗證範圍
      if (data.water_intake_ml < 0 || data.water_intake_ml > 10000) {
        throw new Error('飲水量必須在 0-10000 毫升之間')
      }

      if (data.steps_count !== undefined && data.steps_count !== null) {
        if (data.steps_count < 0 || data.steps_count > 100000) {
          throw new Error('步數必須在 0-100000 之間')
        }
      }

      // 返回 Mock 回應
      return {
        ...MOCK_LOG_RESPONSE,
        ...data,
        log_id: `log-${Date.now()}`,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }
    }

    // 真實 API 調用
    const response = await apiClient.post<DailyLogResponse>('/daily-logs', data)
    return response
  },

  /**
   * 取得病患的日誌列表（分頁）
   */
  async getLogs(params: {
    patient_id: string
    page?: number
    page_size?: number
  }): Promise<DailyLogListResponse> {
    if (IS_MOCK_MODE) {
      await new Promise((resolve) =>
        setTimeout(resolve, 600 + Math.random() * 600)
      )

      console.log('[MOCK] GET /daily-logs', params)

      const page = params.page || 0
      const pageSize = params.page_size || 20

      return {
        items: MOCK_LOGS,
        total: MOCK_LOGS.length,
        page,
        page_size: pageSize,
        has_next: false,
      }
    }

    // 真實 API 調用
    const response = await apiClient.get<DailyLogListResponse>('/daily-logs', {
      params,
    })
    return response
  },

  /**
   * 取得特定日期的日誌
   */
  async getLogByDate(
    patient_id: string,
    log_date: string
  ): Promise<DailyLogResponse | null> {
    if (IS_MOCK_MODE) {
      await new Promise((resolve) =>
        setTimeout(resolve, 300 + Math.random() * 300)
      )

      console.log('[MOCK] GET /daily-logs/by-date', { patient_id, log_date })

      const log = MOCK_LOGS.find((l) => l.log_date === log_date)
      return log || null
    }

    // 真實 API 調用
    const response = await apiClient.get<DailyLogResponse | null>(
      `/daily-logs/by-date`,
      {
        params: { patient_id, log_date },
      }
    )
    return response
  },
}
