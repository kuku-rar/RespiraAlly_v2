/**
 * KPI API - Patient KPI endpoints with Mock support
 */

import { apiClient, isMockMode } from '../api-client'
import { PatientKPI } from '../types/kpi'

// ============================================================================
// Mock Data
// ============================================================================

const MOCK_KPI_DATA: Record<string, PatientKPI> = {
  '00000000-0000-0000-0000-000000000001': {
    patient_id: '00000000-0000-0000-0000-000000000001',
    updated_at: '2025-10-21T10:00:00Z',
    medication_adherence_rate: 85,
    log_submission_rate: 90,
    survey_completion_rate: 75,
    latest_bmi: 25.9,
    latest_spo2: 95,
    latest_heart_rate: 78,
    latest_systolic_bp: 130,
    latest_diastolic_bp: 85,
    latest_cat_score: 18,
    latest_mmrc_score: 2,
    risk_score: 45,
    risk_level: 'medium',
    last_log_date: '2025-10-21',
    days_since_last_log: 0,
  },
  '00000000-0000-0000-0000-000000000002': {
    patient_id: '00000000-0000-0000-0000-000000000002',
    updated_at: '2025-10-21T09:30:00Z',
    medication_adherence_rate: 95,
    log_submission_rate: 100,
    survey_completion_rate: 90,
    latest_bmi: 24.2,
    latest_spo2: 97,
    latest_heart_rate: 72,
    latest_systolic_bp: 120,
    latest_diastolic_bp: 80,
    latest_cat_score: 12,
    latest_mmrc_score: 1,
    risk_score: 28,
    risk_level: 'low',
    last_log_date: '2025-10-21',
    days_since_last_log: 0,
  },
  '00000000-0000-0000-0000-000000000003': {
    patient_id: '00000000-0000-0000-0000-000000000003',
    updated_at: '2025-10-20T15:00:00Z',
    medication_adherence_rate: 60,
    log_submission_rate: 70,
    survey_completion_rate: 50,
    latest_bmi: 28.3,
    latest_spo2: 92,
    latest_heart_rate: 85,
    latest_systolic_bp: 145,
    latest_diastolic_bp: 92,
    latest_cat_score: 25,
    latest_mmrc_score: 3,
    risk_score: 72,
    risk_level: 'high',
    last_log_date: '2025-10-18',
    days_since_last_log: 3,
  },
}

// ============================================================================
// KPI API
// ============================================================================

export const kpiApi = {
  /**
   * Get Patient KPI - GET /patients/{patient_id}/kpis
   */
  async getPatientKPI(patientId: string, refresh = false): Promise<PatientKPI> {
    if (isMockMode) {
      await new Promise(resolve => setTimeout(resolve, 400))
      console.log('[MOCK] GET /patients/' + patientId + '/kpis', { refresh })

      const kpi = MOCK_KPI_DATA[patientId]
      if (!kpi) {
        // Return default empty KPI
        return {
          patient_id: patientId,
          updated_at: new Date().toISOString(),
        }
      }

      return kpi
    }

    return apiClient.get<PatientKPI>(`/patients/${patientId}/kpis`, {
      params: { refresh },
    })
  },

  /**
   * Refresh Patient KPI Cache - POST /patients/{patient_id}/kpis/refresh
   */
  async refreshPatientKPI(patientId: string): Promise<void> {
    if (isMockMode) {
      await new Promise(resolve => setTimeout(resolve, 1200))
      console.log('[MOCK] POST /patients/' + patientId + '/kpis/refresh')
      return
    }

    await apiClient.post<void>(`/patients/${patientId}/kpis/refresh`)
  },
}
