/**
 * usePatient Hook - TanStack Query hook for patient data
 */

import { useQuery, UseQueryOptions, UseQueryResult } from '@tanstack/react-query'
import { patientsApi } from '@/lib/api/patients'
import { queryKeys } from '@/lib/query-client'
import type { PatientResponse } from '@/lib/types/patient'

/**
 * Fetch a single patient by ID
 *
 * @param patientId - Patient UUID
 * @param options - TanStack Query options
 * @returns Query result with patient data, loading, and error states
 *
 * @example
 * ```tsx
 * const { data: patient, isLoading, error } = usePatient('patient-id-123')
 *
 * if (isLoading) return <LoadingSpinner />
 * if (error) return <ErrorAlert error={error} />
 * if (!patient) return <NotFound />
 *
 * return <PatientHeader patient={patient} />
 * ```
 */
export function usePatient(
  patientId: string,
  options?: Omit<UseQueryOptions<PatientResponse, Error>, 'queryKey' | 'queryFn'>
): UseQueryResult<PatientResponse, Error> {
  return useQuery<PatientResponse, Error>({
    queryKey: queryKeys.patients.detail(patientId),
    queryFn: () => patientsApi.getPatient(patientId),
    enabled: Boolean(patientId), // Only run if patientId is provided
    staleTime: 5 * 60 * 1000, // 5 minutes (patient data doesn't change frequently)
    ...options,
  })
}
