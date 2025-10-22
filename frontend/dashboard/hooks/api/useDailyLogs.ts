/**
 * useDailyLogs Hook - TanStack Query hook for daily logs data
 */

import { useQuery, UseQueryOptions, UseQueryResult } from '@tanstack/react-query'
import { getPatientDailyLogs } from '@/lib/api/daily-log'
import { queryKeys } from '@/lib/query-client'
import type { DailyLogListResponse, DailyLogQueryParams } from '@/lib/types/daily-log'

/**
 * Fetch daily logs for a specific patient
 *
 * @param patientId - Patient UUID
 * @param params - Query parameters (date range, pagination, etc.)
 * @param options - TanStack Query options
 * @returns Query result with daily logs list data
 *
 * @example
 * ```tsx
 * // Get last 7 days of daily logs
 * const { data: dailyLogs, isLoading } = useDailyLogs('patient-id-123', {
 *   limit: 7,
 * })
 *
 * // Get daily logs for a specific date range
 * const { data } = useDailyLogs('patient-id-123', {
 *   start_date: '2025-10-01',
 *   end_date: '2025-10-23',
 * })
 * ```
 */
export function useDailyLogs(
  patientId: string,
  params?: Omit<DailyLogQueryParams, 'patient_id'>,
  options?: Omit<UseQueryOptions<DailyLogListResponse, Error>, 'queryKey' | 'queryFn'>
): UseQueryResult<DailyLogListResponse, Error> {
  // Merge patient_id with other params
  const queryParams: DailyLogQueryParams = {
    ...params,
    patient_id: patientId,
  }

  return useQuery<DailyLogListResponse, Error>({
    queryKey: queryKeys.dailyLogs.byPatient(patientId, params),
    queryFn: () => getPatientDailyLogs(patientId, params),
    enabled: Boolean(patientId), // Only run if patientId is provided
    staleTime: 2 * 60 * 1000, // 2 minutes (daily logs change more frequently)
    ...options,
  })
}
