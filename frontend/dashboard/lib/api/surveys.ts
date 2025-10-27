/**
 * Surveys API - Survey management endpoints
 */

import { apiClient } from '../api-client'
import type {
  SurveyResponse,
  SurveyListResponse,
  SurveysQuery,
  CATSurveyCreate,
  MMRCSurveyCreate,
  SurveyStats,
} from '../types/survey'

/**
 * Surveys API endpoints
 */
const ENDPOINTS = {
  CAT: '/surveys/cat',
  MMRC: '/surveys/mmrc',
  DETAIL: (responseId: string) => `/surveys/${responseId}`,
  PATIENT_LIST: (patientId: string) => `/surveys/patient/${patientId}`,
  CAT_LATEST: (patientId: string) => `/surveys/cat/patient/${patientId}/latest`,
  MMRC_LATEST: (patientId: string) => `/surveys/mmrc/patient/${patientId}/latest`,
  CAT_STATS: (patientId: string) => `/surveys/cat/patient/${patientId}/stats`,
  MMRC_STATS: (patientId: string) => `/surveys/mmrc/patient/${patientId}/stats`,
} as const

/**
 * Get list of surveys for a patient
 */
export async function getPatientSurveys(params: SurveysQuery): Promise<SurveyListResponse> {
  const queryParams = new URLSearchParams()

  if (params.patient_id) queryParams.append('patient_id', params.patient_id)
  if (params.survey_type) queryParams.append('survey_type', params.survey_type)
  if (params.start_date) queryParams.append('start_date', params.start_date)
  if (params.end_date) queryParams.append('end_date', params.end_date)
  if (params.page !== undefined) queryParams.append('page', params.page.toString())
  if (params.page_size !== undefined) queryParams.append('page_size', params.page_size.toString())

  const url = params.patient_id
    ? `${ENDPOINTS.PATIENT_LIST(params.patient_id)}?${queryParams.toString()}`
    : `/surveys?${queryParams.toString()}`

  return apiClient.get<SurveyListResponse>(url)
}

/**
 * Get a specific survey by ID
 */
export async function getSurvey(responseId: string): Promise<SurveyResponse> {
  return apiClient.get<SurveyResponse>(ENDPOINTS.DETAIL(responseId))
}

/**
 * Get latest CAT survey for a patient
 */
export async function getLatestCATSurvey(patientId: string): Promise<SurveyResponse | null> {
  return apiClient.get<SurveyResponse | null>(ENDPOINTS.CAT_LATEST(patientId))
}

/**
 * Get latest mMRC survey for a patient
 */
export async function getLatestMMRCSurvey(patientId: string): Promise<SurveyResponse | null> {
  return apiClient.get<SurveyResponse | null>(ENDPOINTS.MMRC_LATEST(patientId))
}

/**
 * Get CAT survey statistics for a patient
 */
export async function getCATStats(
  patientId: string,
  startDate?: string,
  endDate?: string
): Promise<SurveyStats> {
  const params = new URLSearchParams()
  if (startDate) params.append('start_date', startDate)
  if (endDate) params.append('end_date', endDate)

  const query = params.toString()
  const url = query ? `${ENDPOINTS.CAT_STATS(patientId)}?${query}` : ENDPOINTS.CAT_STATS(patientId)

  return apiClient.get<SurveyStats>(url)
}

/**
 * Get mMRC survey statistics for a patient
 */
export async function getMMRCStats(
  patientId: string,
  startDate?: string,
  endDate?: string
): Promise<SurveyStats> {
  const params = new URLSearchParams()
  if (startDate) params.append('start_date', startDate)
  if (endDate) params.append('end_date', endDate)

  const query = params.toString()
  const url = query
    ? `${ENDPOINTS.MMRC_STATS(patientId)}?${query}`
    : ENDPOINTS.MMRC_STATS(patientId)

  return apiClient.get<SurveyStats>(url)
}

/**
 * Submit CAT survey
 */
export async function submitCATSurvey(data: CATSurveyCreate): Promise<SurveyResponse> {
  return apiClient.post<SurveyResponse>(ENDPOINTS.CAT, data)
}

/**
 * Submit mMRC survey
 */
export async function submitMMRCSurvey(data: MMRCSurveyCreate): Promise<SurveyResponse> {
  return apiClient.post<SurveyResponse>(ENDPOINTS.MMRC, data)
}

/**
 * Surveys API export
 */
export const surveysApi = {
  getPatientSurveys,
  getSurvey,
  getLatestCATSurvey,
  getLatestMMRCSurvey,
  getCATStats,
  getMMRCStats,
  submitCATSurvey,
  submitMMRCSurvey,
}
