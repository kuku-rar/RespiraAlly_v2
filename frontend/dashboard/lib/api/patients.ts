/**
 * Patients API - Patient management endpoints with Mock support
 */

import { apiClient, isMockMode } from '../api-client'
import {
  PatientResponse,
  PatientListResponse,
  PatientsQuery,
  PatientCreate,
  PatientUpdate,
  Gender,
} from '../types/patient'

// ============================================================================
// Mock Data
// ============================================================================

const MOCK_PATIENTS: PatientResponse[] = [
  {
    user_id: '00000000-0000-0000-0000-000000000001',
    name: '王小明',
    birth_date: '1965-03-15',
    gender: Gender.MALE,
    age: 60,
    phone: '0912-345-678',
    height_cm: 170,
    weight_kg: 75,
    bmi: 25.9,
    therapist_id: '00000000-0000-0000-0000-000000000999',
  },
  {
    user_id: '00000000-0000-0000-0000-000000000002',
    name: '李小華',
    birth_date: '1958-07-22',
    gender: Gender.FEMALE,
    age: 67,
    phone: '0923-456-789',
    height_cm: 160,
    weight_kg: 62,
    bmi: 24.2,
    therapist_id: '00000000-0000-0000-0000-000000000999',
  },
  {
    user_id: '00000000-0000-0000-0000-000000000003',
    name: '張大同',
    birth_date: '1952-11-08',
    gender: Gender.MALE,
    age: 73,
    phone: '0934-567-890',
    height_cm: 168,
    weight_kg: 80,
    bmi: 28.3,
    therapist_id: '00000000-0000-0000-0000-000000000999',
  },
  {
    user_id: '00000000-0000-0000-0000-000000000004',
    name: '陳美玲',
    birth_date: '1960-05-30',
    gender: Gender.FEMALE,
    age: 65,
    phone: '0945-678-901',
    height_cm: 155,
    weight_kg: 58,
    bmi: 24.1,
    therapist_id: '00000000-0000-0000-0000-000000000999',
  },
  {
    user_id: '00000000-0000-0000-0000-000000000005',
    name: '林志明',
    birth_date: '1963-09-12',
    gender: Gender.MALE,
    age: 62,
    phone: '0956-789-012',
    height_cm: 175,
    weight_kg: 85,
    bmi: 27.8,
    therapist_id: '00000000-0000-0000-0000-000000000999',
  },
  {
    user_id: '00000000-0000-0000-0000-000000000006',
    name: '黃秀英',
    birth_date: '1957-02-18',
    gender: Gender.FEMALE,
    age: 68,
    phone: '0967-890-123',
    height_cm: 158,
    weight_kg: 60,
    bmi: 24.0,
    therapist_id: '00000000-0000-0000-0000-000000000999',
  },
  {
    user_id: '00000000-0000-0000-0000-000000000007',
    name: '吳文龍',
    birth_date: '1961-12-25',
    gender: Gender.MALE,
    age: 63,
    phone: '0978-901-234',
    height_cm: 172,
    weight_kg: 78,
    bmi: 26.4,
    therapist_id: '00000000-0000-0000-0000-000000000999',
  },
  {
    user_id: '00000000-0000-0000-0000-000000000008',
    name: '劉雅婷',
    birth_date: '1964-08-07',
    gender: Gender.FEMALE,
    age: 61,
    phone: '0989-012-345',
    height_cm: 162,
    weight_kg: 65,
    bmi: 24.8,
    therapist_id: '00000000-0000-0000-0000-000000000999',
  },
]

// ============================================================================
// Patients API
// ============================================================================

export const patientsApi = {
  /**
   * Get Patients List - GET /patients
   */
  async getPatients(params?: PatientsQuery): Promise<PatientListResponse> {
    if (isMockMode) {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 600))
      console.log('[MOCK] GET /patients', params)

      // Mock filtering
      const filteredPatients = [...MOCK_PATIENTS]

      // Filter by risk_bucket (not in mock data, so skip)
      // Filter by adherence_rate_lte (not in mock data, so skip)
      // Filter by last_active_gte (not in mock data, so skip)

      // Mock sorting
      if (params?.sort_by === 'name') {
        filteredPatients.sort((a, b) => a.name.localeCompare(b.name))
      } else if (params?.sort_by === 'age') {
        filteredPatients.sort((a, b) => (b.age || 0) - (a.age || 0))
      }

      // Mock pagination
      const skip = params?.skip || 0
      const limit = params?.limit || 20
      const paginatedPatients = filteredPatients.slice(skip, skip + limit)

      return {
        items: paginatedPatients,
        total: filteredPatients.length,
        page: Math.floor(skip / limit),
        page_size: limit,
        has_next: skip + limit < filteredPatients.length,
      }
    }

    // Real API call
    return apiClient.get<PatientListResponse>('/patients', { params })
  },

  /**
   * Get Patient by ID - GET /patients/{patient_id}
   */
  async getPatient(patientId: string): Promise<PatientResponse> {
    if (isMockMode) {
      await new Promise(resolve => setTimeout(resolve, 400))
      console.log('[MOCK] GET /patients/' + patientId)

      const patient = MOCK_PATIENTS.find(p => p.user_id === patientId)
      if (!patient) {
        throw new Error('Patient not found')
      }

      return patient
    }

    return apiClient.get<PatientResponse>(`/patients/${patientId}`)
  },

  /**
   * Create Patient - POST /patients
   */
  async createPatient(data: PatientCreate): Promise<PatientResponse> {
    if (isMockMode) {
      await new Promise(resolve => setTimeout(resolve, 800))
      console.log('[MOCK] POST /patients', data)

      // Mock validation
      if (!data.name || !data.birth_date) {
        throw new Error('姓名和出生日期為必填欄位')
      }

      // Return mock response
      return {
        user_id: `mock-${Date.now()}`,
        name: data.name,
        birth_date: data.birth_date,
        gender: data.gender,
        height_cm: data.height_cm,
        weight_kg: data.weight_kg,
        phone: data.phone,
        therapist_id: data.therapist_id,
      }
    }

    return apiClient.post<PatientResponse>('/patients', data)
  },

  /**
   * Update Patient - PATCH /patients/{patient_id}
   */
  async updatePatient(patientId: string, data: PatientUpdate): Promise<PatientResponse> {
    if (isMockMode) {
      await new Promise(resolve => setTimeout(resolve, 700))
      console.log('[MOCK] PATCH /patients/' + patientId, data)

      const patient = MOCK_PATIENTS.find(p => p.user_id === patientId)
      if (!patient) {
        throw new Error('Patient not found')
      }

      // Return merged data
      return {
        ...patient,
        ...data,
      }
    }

    return apiClient.patch<PatientResponse>(`/patients/${patientId}`, data)
  },

  /**
   * Delete Patient - DELETE /patients/{patient_id}
   */
  async deletePatient(patientId: string): Promise<void> {
    if (isMockMode) {
      await new Promise(resolve => setTimeout(resolve, 500))
      console.log('[MOCK] DELETE /patients/' + patientId)
      return
    }

    await apiClient.delete<void>(`/patients/${patientId}`)
  },
}
