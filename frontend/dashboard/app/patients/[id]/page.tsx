/**
 * Patient Detail Page - Patient 360° View
 * Displays comprehensive patient information: Profile, Daily Logs, Surveys, KPIs
 *
 * Sprint 3 Task 5.1: Dashboard 360° 頁面
 */

'use client'

import { useParams } from 'next/navigation'
import { usePatient, useDailyLogs, useSurveys } from '@/hooks/api'
import { PatientHeader, PatientTabs } from '@/components/patient'

export default function PatientDetailPage() {
  const params = useParams()
  const patientId = params.id as string

  // ========================================
  // TanStack Query Hooks - Parallel Data Fetching
  // ========================================

  // Fetch patient basic info
  const {
    data: patient,
    isLoading: patientLoading,
    error: patientError,
  } = usePatient(patientId)

  // Fetch last 7 days of daily logs
  const {
    data: dailyLogs,
    isLoading: logsLoading,
    error: logsError,
  } = useDailyLogs(patientId, {
    page_size: 7,
  })

  // Fetch patient surveys
  const {
    data: surveys,
    isLoading: surveysLoading,
    error: surveysError,
  } = useSurveys(patientId, {
    page_size: 10,
  })

  // ========================================
  // Loading States
  // ========================================

  const isLoading = patientLoading || logsLoading || surveysLoading

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block h-16 w-16 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent align-[-0.125em]"></div>
          <p className="mt-4 text-xl font-medium text-gray-700">載入中...</p>
        </div>
      </div>
    )
  }

  // ========================================
  // Error States
  // ========================================

  if (patientError) {
    return (
      <div className="container mx-auto py-8">
        <div className="rounded-lg border border-red-200 bg-red-50 p-6">
          <h2 className="text-xl font-semibold text-red-900 mb-2">無法載入病患資料</h2>
          <p className="text-red-700">{patientError.message}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            重試
          </button>
        </div>
      </div>
    )
  }

  if (!patient) {
    return (
      <div className="container mx-auto py-8">
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-6 text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">找不到病患資料</h2>
          <p className="text-gray-600">病患 ID: {patientId}</p>
        </div>
      </div>
    )
  }

  // ========================================
  // Main Content
  // ========================================

  return (
    <div className="container mx-auto py-8 space-y-6">
      {/* Patient Header */}
      <PatientHeader patient={patient} />

      {/* Patient Tabs (Profile, Daily Logs, Surveys) */}
      <PatientTabs patient={patient} dailyLogs={dailyLogs} surveys={surveys} />

      {/* Success Message - Task 5.1.2 Completed */}
      <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4">
        <p className="text-lg text-green-800 font-semibold">
          ✅ Task 5.1.2 完成 - PatientHeader + PatientTabs 組件實現！
        </p>
        <p className="text-sm text-green-700 mt-1">
          • PatientHeader: 顯示病患基本資訊與返回按鈕<br />
          • PatientTabs: Tab 切換介面 (基本資料、每日紀錄、問卷評估)
        </p>
      </div>
    </div>
  )
}
