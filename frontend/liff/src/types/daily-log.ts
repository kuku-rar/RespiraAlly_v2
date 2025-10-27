/**
 * Daily Log Types - LIFF Daily Health Log Form
 * 每日健康日誌類型定義（匹配後端 Schema）
 */

export enum Mood {
  GOOD = 'GOOD',
  NEUTRAL = 'NEUTRAL',
  BAD = 'BAD',
}

/**
 * 基礎日誌資訊（共用欄位）
 * Updated per ADR-009: steps_count → exercise_minutes, added smoking_count
 */
export interface DailyLogBase {
  log_date: string // ISO 8601 date format (YYYY-MM-DD)
  medication_taken: boolean // 是否服藥
  water_intake_ml: number // 飲水量（毫升），範圍 0-10000
  exercise_minutes?: number | null // 運動分鐘數（選填），範圍 0-480
  smoking_count?: number | null // 吸菸支數（選填），範圍 0-100
  symptoms?: string | null // 症狀描述（選填），最多 500 字
  mood?: Mood | null // 心情（選填）
}

/**
 * 日誌提交請求（LIFF 表單提交）
 */
export interface DailyLogCreate extends DailyLogBase {
  patient_id: string // Patient User ID (UUID)
}

/**
 * 日誌 API 回應
 */
export interface DailyLogResponse extends DailyLogBase {
  log_id: string
  patient_id: string
  created_at: string // ISO 8601 datetime
  updated_at: string // ISO 8601 datetime
}

/**
 * 日誌列表回應（分頁）
 */
export interface DailyLogListResponse {
  items: DailyLogResponse[]
  total: number
  page: number // 0-indexed
  page_size: number
  has_next: boolean
}

/**
 * 日誌表單資料（前端狀態）
 * Updated per ADR-009
 */
export interface DailyLogFormData {
  log_date: string // YYYY-MM-DD
  medication_taken: boolean
  water_intake_ml: string // 輸入時為字串，提交時轉為數字
  exercise_minutes: string // 運動分鐘數（輸入時為字串）
  smoking_count: string // 吸菸支數（輸入時為字串）
  symptoms: string
  mood: Mood | ''
}
