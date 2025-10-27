/**
 * Alert Types for RespiraAlly Dashboard
 * Defines types for Alert System (Sprint 4 delivery)
 */

/**
 * Alert Type Enum
 * Based on backend AlertRuleEngine fixed rules
 */
export enum AlertType {
  GOLD_GROUP_E = 'GOLD_GROUP_E',
  HIGH_CAT_SCORE = 'HIGH_CAT_SCORE',
  FREQUENT_EXACERBATIONS = 'FREQUENT_EXACERBATIONS',
}

/**
 * Alert Severity Enum
 * Indicates the urgency level of the alert
 */
export enum AlertSeverity {
  CRITICAL = 'CRITICAL',
  HIGH = 'HIGH',
  MEDIUM = 'MEDIUM',
  LOW = 'LOW',
}

/**
 * Alert Status Enum
 * Tracks the lifecycle of an alert
 */
export enum AlertStatus {
  ACTIVE = 'ACTIVE',
  ACKNOWLEDGED = 'ACKNOWLEDGED',
  RESOLVED = 'RESOLVED',
}

/**
 * Alert Metadata Interface
 * Contains additional context for the alert
 */
export interface AlertMetadata {
  rule_triggered: string
  trigger_value?: number | string
  threshold?: number
  clinical_indicators?: {
    cat_score?: number
    mmrc_score?: number
    gold_group?: string
    exacerbation_count_12m?: number
    hospitalization_count_12m?: number
  }
  [key: string]: any // Allow additional metadata
}

/**
 * Alert Interface
 * Core alert data structure
 */
export interface Alert {
  alert_id: string
  patient_id: string
  alert_type: AlertType
  severity: AlertSeverity
  status: AlertStatus
  triggered_at: string // ISO 8601 datetime
  acknowledged_at?: string | null
  acknowledged_by?: string | null
  resolved_at?: string | null
  resolved_by?: string | null
  metadata: AlertMetadata
  created_at: string // ISO 8601 datetime
  updated_at: string // ISO 8601 datetime
}

/**
 * Alert List Response
 * Response structure for GET /api/v1/alerts/patients/{patient_id}/
 */
export interface AlertListResponse {
  alerts: Alert[]
  total: number
  page: number
  page_size: number
}

/**
 * Active Alert Count Response
 * Response structure for GET /api/v1/alerts/patients/{patient_id}/active/count
 */
export interface ActiveAlertCountResponse {
  active_count: number
}

/**
 * Alert Query Parameters
 * Used for filtering and pagination
 */
export interface AlertQueryParams {
  alert_type?: AlertType | string
  severity?: AlertSeverity | string
  status?: AlertStatus | string
  page?: number
  page_size?: number
  date_from?: string // ISO 8601 date
  date_to?: string // ISO 8601 date
}

/**
 * Alert Type Labels (Chinese)
 * For UI display
 */
export const AlertTypeLabels: Record<AlertType, string> = {
  [AlertType.GOLD_GROUP_E]: 'GOLD Group E - 最高風險病患',
  [AlertType.HIGH_CAT_SCORE]: '高症狀負擔 (CAT ≥ 20)',
  [AlertType.FREQUENT_EXACERBATIONS]: '頻繁惡化 (12個月內 ≥3次)',
}

/**
 * Alert Severity Labels (Chinese)
 */
export const AlertSeverityLabels: Record<AlertSeverity, string> = {
  [AlertSeverity.CRITICAL]: '嚴重',
  [AlertSeverity.HIGH]: '高',
  [AlertSeverity.MEDIUM]: '中',
  [AlertSeverity.LOW]: '低',
}

/**
 * Alert Status Labels (Chinese)
 */
export const AlertStatusLabels: Record<AlertStatus, string> = {
  [AlertStatus.ACTIVE]: '活動中',
  [AlertStatus.ACKNOWLEDGED]: '已確認',
  [AlertStatus.RESOLVED]: '已解決',
}

/**
 * Alert Severity Colors
 * For Ant Design Tag colors
 */
export const AlertSeverityColors: Record<AlertSeverity, string> = {
  [AlertSeverity.CRITICAL]: 'red',
  [AlertSeverity.HIGH]: 'orange',
  [AlertSeverity.MEDIUM]: 'gold',
  [AlertSeverity.LOW]: 'blue',
}

/**
 * Alert Status Colors
 * For Ant Design Tag colors
 */
export const AlertStatusColors: Record<AlertStatus, string> = {
  [AlertStatus.ACTIVE]: 'red',
  [AlertStatus.ACKNOWLEDGED]: 'orange',
  [AlertStatus.RESOLVED]: 'green',
}
