/**
 * useSurveys Hook - TanStack Query hook for survey data
 */

import { useQuery, UseQueryOptions, UseQueryResult } from '@tanstack/react-query'
import { getPatientSurveys } from '@/lib/api/surveys'
import { queryKeys } from '@/lib/query-client'
import type { SurveyListResponse, SurveysQuery } from '@/lib/types/survey'

/**
 * Fetch surveys for a specific patient
 *
 * @param patientId - Patient UUID
 * @param params - Query parameters (survey type, date range, pagination, etc.)
 * @param options - TanStack Query options
 * @returns Query result with surveys list data
 *
 * @example
 * ```tsx
 * // Get all surveys for a patient
 * const { data: surveys, isLoading } = useSurveys('patient-id-123')
 *
 * // Get only CAT surveys
 * const { data } = useSurveys('patient-id-123', {
 *   survey_type: SurveyType.CAT,
 * })
 *
 * // Get surveys for a specific date range
 * const { data } = useSurveys('patient-id-123', {
 *   start_date: '2025-10-01',
 *   end_date: '2025-10-23',
 *   page_size: 10,
 * })
 * ```
 */
export function useSurveys(
  patientId: string,
  params?: Omit<SurveysQuery, 'patient_id'>,
  options?: Omit<UseQueryOptions<SurveyListResponse, Error>, 'queryKey' | 'queryFn'>
): UseQueryResult<SurveyListResponse, Error> {
  // Merge patient_id with other params
  const queryParams: SurveysQuery = {
    ...params,
    patient_id: patientId,
  }

  return useQuery<SurveyListResponse, Error>({
    queryKey: queryKeys.surveys.byPatient(patientId, params),
    queryFn: () => getPatientSurveys(queryParams),
    enabled: Boolean(patientId), // Only run if patientId is provided
    staleTime: 3 * 60 * 1000, // 3 minutes (surveys don't change too frequently)
    ...options,
  })
}
