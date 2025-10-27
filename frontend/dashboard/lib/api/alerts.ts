/**
 * Alerts API - Alert management endpoints with Mock support
 * Implements Sprint 4 Alert System MVP
 */

import { apiClient, isMockMode } from '../api-client'
import {
  Alert,
  AlertListResponse,
  ActiveAlertCountResponse,
  AlertQueryParams,
  AlertType,
  AlertSeverity,
  AlertStatus,
} from '../types/alert'

// ============================================================================
// Mock Data
// ============================================================================

const MOCK_ALERTS: Alert[] = [
  {
    alert_id: '00000000-0000-0000-0000-alert0000001',
    patient_id: '00000000-0000-0000-0000-000000000001',
    alert_type: AlertType.GOLD_GROUP_E,
    severity: AlertSeverity.CRITICAL,
    status: AlertStatus.ACTIVE,
    triggered_at: '2025-10-26T10:30:00Z',
    metadata: {
      rule_triggered: 'GOLD_GROUP_E',
      clinical_indicators: {
        gold_group: 'E',
        cat_score: 25,
        mmrc_score: 2,
        exacerbation_count_12m: 3,
        hospitalization_count_12m: 1,
      },
    },
    created_at: '2025-10-26T10:30:00Z',
    updated_at: '2025-10-26T10:30:00Z',
  },
  {
    alert_id: '00000000-0000-0000-0000-alert0000002',
    patient_id: '00000000-0000-0000-0000-000000000001',
    alert_type: AlertType.HIGH_CAT_SCORE,
    severity: AlertSeverity.HIGH,
    status: AlertStatus.ACTIVE,
    triggered_at: '2025-10-26T11:45:00Z',
    metadata: {
      rule_triggered: 'HIGH_CAT_SCORE',
      trigger_value: 25,
      threshold: 20,
      clinical_indicators: {
        cat_score: 25,
      },
    },
    created_at: '2025-10-26T11:45:00Z',
    updated_at: '2025-10-26T11:45:00Z',
  },
  {
    alert_id: '00000000-0000-0000-0000-alert0000003',
    patient_id: '00000000-0000-0000-0000-000000000002',
    alert_type: AlertType.FREQUENT_EXACERBATIONS,
    severity: AlertSeverity.MEDIUM,
    status: AlertStatus.ACKNOWLEDGED,
    triggered_at: '2025-10-25T14:20:00Z',
    acknowledged_at: '2025-10-26T09:00:00Z',
    acknowledged_by: '00000000-0000-0000-0000-000000000999',
    metadata: {
      rule_triggered: 'FREQUENT_EXACERBATIONS',
      trigger_value: 4,
      threshold: 3,
      clinical_indicators: {
        exacerbation_count_12m: 4,
      },
    },
    created_at: '2025-10-25T14:20:00Z',
    updated_at: '2025-10-26T09:00:00Z',
  },
  {
    alert_id: '00000000-0000-0000-0000-alert0000004',
    patient_id: '00000000-0000-0000-0000-000000000003',
    alert_type: AlertType.HIGH_CAT_SCORE,
    severity: AlertSeverity.HIGH,
    status: AlertStatus.RESOLVED,
    triggered_at: '2025-10-24T08:15:00Z',
    acknowledged_at: '2025-10-24T10:00:00Z',
    acknowledged_by: '00000000-0000-0000-0000-000000000999',
    resolved_at: '2025-10-25T16:30:00Z',
    resolved_by: '00000000-0000-0000-0000-000000000999',
    metadata: {
      rule_triggered: 'HIGH_CAT_SCORE',
      trigger_value: 22,
      threshold: 20,
      clinical_indicators: {
        cat_score: 22,
      },
    },
    created_at: '2025-10-24T08:15:00Z',
    updated_at: '2025-10-25T16:30:00Z',
  },
]

// ============================================================================
// API Functions
// ============================================================================

/**
 * Get alerts for a specific patient
 * GET /api/v1/alerts/patients/{patient_id}/
 */
export async function getPatientAlerts(
  patientId: string,
  params?: AlertQueryParams
): Promise<AlertListResponse> {
  // Mock mode
  if (isMockMode) {
    const mockDelay = new Promise((resolve) => setTimeout(resolve, 500))
    await mockDelay

    let filteredAlerts = MOCK_ALERTS.filter((alert) => alert.patient_id === patientId)

    // Apply filters
    if (params?.alert_type) {
      filteredAlerts = filteredAlerts.filter((alert) => alert.alert_type === params.alert_type)
    }

    if (params?.severity) {
      filteredAlerts = filteredAlerts.filter((alert) => alert.severity === params.severity)
    }

    if (params?.status) {
      filteredAlerts = filteredAlerts.filter((alert) => alert.status === params.status)
    }

    // Apply pagination
    const page = params?.page ?? 0
    const pageSize = params?.page_size ?? 20
    const start = page * pageSize
    const end = start + pageSize
    const paginatedAlerts = filteredAlerts.slice(start, end)

    return {
      alerts: paginatedAlerts,
      total: filteredAlerts.length,
      page,
      page_size: pageSize,
    }
  }

  // Real API call
  const queryParams = new URLSearchParams()

  if (params?.alert_type) queryParams.append('alert_type', params.alert_type)
  if (params?.severity) queryParams.append('severity', params.severity)
  if (params?.status) queryParams.append('status', params.status)
  if (params?.page !== undefined) queryParams.append('page', params.page.toString())
  if (params?.page_size !== undefined) queryParams.append('page_size', params.page_size.toString())
  if (params?.date_from) queryParams.append('date_from', params.date_from)
  if (params?.date_to) queryParams.append('date_to', params.date_to)

  const queryString = queryParams.toString()
  const url = `/alerts/patients/${patientId}/${queryString ? `?${queryString}` : ''}`

  return apiClient.get<AlertListResponse>(url)
}

/**
 * Get active alert count for a specific patient
 * GET /api/v1/alerts/patients/{patient_id}/active/count
 */
export async function getActiveAlertCount(patientId: string): Promise<number> {
  // Mock mode
  if (isMockMode) {
    const mockDelay = new Promise((resolve) => setTimeout(resolve, 300))
    await mockDelay

    const activeAlerts = MOCK_ALERTS.filter(
      (alert) => alert.patient_id === patientId && alert.status === AlertStatus.ACTIVE
    )

    return activeAlerts.length
  }

  // Real API call
  const response = await apiClient.get<ActiveAlertCountResponse>(
    `/alerts/patients/${patientId}/active/count`
  )

  return response.active_count
}

/**
 * Get alert by ID
 * GET /api/v1/alerts/{alert_id}
 */
export async function getAlertById(alertId: string): Promise<Alert> {
  // Mock mode
  if (isMockMode) {
    const mockDelay = new Promise((resolve) => setTimeout(resolve, 300))
    await mockDelay

    const alert = MOCK_ALERTS.find((a) => a.alert_id === alertId)

    if (!alert) {
      throw new Error(`Alert ${alertId} not found`)
    }

    return alert
  }

  // Real API call
  return apiClient.get<Alert>(`/alerts/${alertId}`)
}

/**
 * Acknowledge an alert (Future implementation)
 * POST /api/v1/alerts/{alert_id}/acknowledge
 */
export async function acknowledgeAlert(alertId: string): Promise<Alert> {
  // Note: MVP version is read-only, this will be implemented in Sprint 5
  throw new Error('Acknowledge alert feature not yet implemented (Sprint 5)')
}

/**
 * Resolve an alert (Future implementation)
 * POST /api/v1/alerts/{alert_id}/resolve
 */
export async function resolveAlert(alertId: string, notes?: string): Promise<Alert> {
  // Note: MVP version is read-only, this will be implemented in Sprint 5
  throw new Error('Resolve alert feature not yet implemented (Sprint 5)')
}

// ============================================================================
// Export all functions
// ============================================================================

export const alertsAPI = {
  getPatientAlerts,
  getActiveAlertCount,
  getAlertById,
  acknowledgeAlert,
  resolveAlert,
}
