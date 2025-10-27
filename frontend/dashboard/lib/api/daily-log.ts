/**
 * Daily Log API Client
 * Handles all daily log related API calls
 */

import { apiClient } from '../api-client'
import type {
  DailyLog,
  DailyLogListResponse,
  DailyLogStats,
  DailyLogQueryParams,
  DailyLogCreateRequest,
  DailyLogUpdateRequest,
} from '../types/daily-log'

/**
 * Daily Log API endpoints
 */
const ENDPOINTS = {
  LIST: '/daily-logs',
  DETAIL: (logId: string) => `/daily-logs/${logId}`,
  PATIENT_LOGS: (patientId: string) => `/daily-logs?patient_id=${patientId}`,
  PATIENT_STATS: (patientId: string) => `/daily-logs/patient/${patientId}/stats`,
  PATIENT_LATEST: (patientId: string) => `/daily-logs/patient/${patientId}/latest`,
} as const

/**
 * Get list of daily logs with filters and pagination
 */
export async function getDailyLogs(params?: DailyLogQueryParams): Promise<DailyLogListResponse> {
  const queryParams = new URLSearchParams()

  if (params?.patient_id) queryParams.append('patient_id', params.patient_id)
  if (params?.start_date) queryParams.append('start_date', params.start_date)
  if (params?.end_date) queryParams.append('end_date', params.end_date)
  if (params?.page !== undefined) queryParams.append('page', params.page.toString())
  if (params?.page_size !== undefined) queryParams.append('page_size', params.page_size.toString())

  const query = queryParams.toString()
  const url = query ? `${ENDPOINTS.LIST}?${query}` : ENDPOINTS.LIST

  return apiClient.get<DailyLogListResponse>(url)
}

/**
 * Get a specific daily log by ID
 */
export async function getDailyLog(logId: string): Promise<DailyLog> {
  return apiClient.get<DailyLog>(ENDPOINTS.DETAIL(logId))
}

/**
 * Get all daily logs for a specific patient
 */
export async function getPatientDailyLogs(
  patientId: string,
  params?: Omit<DailyLogQueryParams, 'patient_id'>
): Promise<DailyLogListResponse> {
  return getDailyLogs({ ...params, patient_id: patientId })
}

/**
 * Get latest daily log for a patient
 */
export async function getPatientLatestLog(patientId: string): Promise<DailyLog> {
  return apiClient.get<DailyLog>(ENDPOINTS.PATIENT_LATEST(patientId))
}

/**
 * Get statistics for a patient's daily logs
 */
export async function getPatientDailyLogStats(
  patientId: string,
  startDate: string,
  endDate: string
): Promise<DailyLogStats> {
  const url = `${ENDPOINTS.PATIENT_STATS(patientId)}?start_date=${startDate}&end_date=${endDate}`
  return apiClient.get<DailyLogStats>(url)
}

/**
 * Create or update a daily log (upsert)
 */
export async function createOrUpdateDailyLog(
  data: DailyLogCreateRequest,
  idempotencyKey?: string
): Promise<DailyLog> {
  const headers = idempotencyKey ? { 'Idempotency-Key': idempotencyKey } : undefined
  return apiClient.post<DailyLog>(ENDPOINTS.LIST, data, { headers })
}

/**
 * Update an existing daily log (partial update)
 */
export async function updateDailyLog(logId: string, data: DailyLogUpdateRequest): Promise<DailyLog> {
  return apiClient.patch<DailyLog>(ENDPOINTS.DETAIL(logId), data)
}

/**
 * Delete a daily log
 */
export async function deleteDailyLog(logId: string): Promise<void> {
  return apiClient.delete<void>(ENDPOINTS.DETAIL(logId))
}

/**
 * Get daily logs for chart visualization (convenience method)
 * Returns logs sorted by date for a specific time range
 */
export async function getDailyLogsForChart(
  patientId: string,
  startDate: string,
  endDate: string
): Promise<DailyLog[]> {
  const response = await getPatientDailyLogs(patientId, {
    start_date: startDate,
    end_date: endDate,
    page: 0,
    page_size: 365, // Get up to 1 year of data
  })

  // Sort by date ascending for chart display
  return response.items.sort((a, b) => {
    return new Date(a.log_date).getTime() - new Date(b.log_date).getTime()
  })
}
