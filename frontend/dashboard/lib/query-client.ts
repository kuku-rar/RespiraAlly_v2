/**
 * TanStack Query Client Configuration
 * Centralized configuration for React Query v5
 */

import { QueryClient, DefaultOptions } from '@tanstack/react-query'

/**
 * Default options for all queries and mutations
 */
const defaultOptions: DefaultOptions = {
  queries: {
    // Stale time: 5 minutes (data considered fresh for 5 mins)
    staleTime: 5 * 60 * 1000,

    // Cache time: 10 minutes (data kept in cache for 10 mins after becoming unused)
    gcTime: 10 * 60 * 1000, // v5: renamed from cacheTime

    // Retry failed requests 2 times
    retry: 2,

    // Retry delay: exponential backoff (1s, 2s, 4s)
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),

    // Refetch on window focus (useful for detecting stale data)
    refetchOnWindowFocus: true,

    // Don't refetch on mount if data is fresh
    refetchOnMount: true,

    // Refetch on reconnect
    refetchOnReconnect: true,
  },
  mutations: {
    // Retry mutations once on failure
    retry: 1,

    // Retry delay for mutations
    retryDelay: 1000,
  },
}

/**
 * Create and export QueryClient instance
 * Singleton pattern - use this instance throughout the app
 */
export const queryClient = new QueryClient({
  defaultOptions,
})

/**
 * Query Keys Factory
 * Centralized query key management following TanStack Query best practices
 *
 * Pattern: [resource, identifier?, subresource?, filter?]
 * Example: ['patients', '123', 'dailyLogs', { limit: 7 }]
 */
export const queryKeys = {
  // Patients
  patients: {
    all: ['patients'] as const,
    lists: () => [...queryKeys.patients.all, 'list'] as const,
    list: (filters?: Record<string, unknown>) => [...queryKeys.patients.lists(), filters] as const,
    details: () => [...queryKeys.patients.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.patients.details(), id] as const,
  },

  // Daily Logs
  dailyLogs: {
    all: ['dailyLogs'] as const,
    lists: () => [...queryKeys.dailyLogs.all, 'list'] as const,
    list: (filters?: Record<string, unknown>) => [...queryKeys.dailyLogs.lists(), filters] as const,
    details: () => [...queryKeys.dailyLogs.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.dailyLogs.details(), id] as const,
    byPatient: (patientId: string, filters?: Record<string, unknown>) =>
      [...queryKeys.dailyLogs.all, 'patient', patientId, filters] as const,
  },

  // Surveys
  surveys: {
    all: ['surveys'] as const,
    lists: () => [...queryKeys.surveys.all, 'list'] as const,
    list: (filters?: Record<string, unknown>) => [...queryKeys.surveys.lists(), filters] as const,
    details: () => [...queryKeys.surveys.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.surveys.details(), id] as const,
    byPatient: (patientId: string, filters?: Record<string, unknown>) =>
      [...queryKeys.surveys.all, 'patient', patientId, filters] as const,
    latest: {
      cat: (patientId: string) => [...queryKeys.surveys.all, 'latest', 'cat', patientId] as const,
      mmrc: (patientId: string) => [...queryKeys.surveys.all, 'latest', 'mmrc', patientId] as const,
    },
  },

  // KPIs
  kpis: {
    all: ['kpis'] as const,
    patient: (patientId: string) => [...queryKeys.kpis.all, 'patient', patientId] as const,
  },
} as const
