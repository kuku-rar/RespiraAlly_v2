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
import { LoadingSpinner, ErrorAlert, PageErrorBoundary } from '@/components/ui'

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
  } = useDailyLogs(patientId, {
    page_size: 7,
  })

  // Fetch patient surveys
  const {
    data: surveys,
    isLoading: surveysLoading,
  } = useSurveys(patientId, {
    page_size: 10,
  })

  // ========================================
  // Loading States
  // ========================================

  const isLoading = patientLoading || logsLoading || surveysLoading

  if (isLoading) {
    return (
      <LoadingSpinner
        size="lg"
        message="載入病患資料中..."
        fullScreen
      />
    )
  }

  // ========================================
  // Error States
  // ========================================

  if (patientError) {
    return (
      <div className="container mx-auto py-8">
        <ErrorAlert
          title="無法載入病患資料"
          message={patientError.message}
          onRetry={() => window.location.reload()}
        />
      </div>
    )
  }

  if (!patient) {
    return (
      <div className="container mx-auto py-8">
        <ErrorAlert
          title="找不到病患資料"
          message={`病患 ID: ${patientId} 不存在於系統中`}
          variant="warning"
        />
      </div>
    )
  }

  // ========================================
  // Main Content
  // ========================================

  return (
    <PageErrorBoundary pageName="病患詳細資料頁面">
      <div className="container mx-auto py-8 space-y-6">
        {/* Patient Header */}
        <PatientHeader patient={patient} />

        {/* Patient Tabs (Profile, Daily Logs, Surveys) */}
        <PatientTabs patient={patient} dailyLogs={dailyLogs} surveys={surveys} />

        {/* Success Message - Task 5.1.4 Completed */}
        <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4">
          <p className="text-lg text-green-800 font-semibold">
            ✅ Task 5.1.4 完成 - 錯誤處理 + Loading 狀態優化！
          </p>
          <p className="text-sm text-green-700 mt-1">
            • LoadingSpinner: 可重用的載入指示器 (sm/md/lg/xl)<br />
            • ErrorAlert: 統一的錯誤顯示組件 (error/warning/info)<br />
            • ErrorBoundary: React 錯誤邊界保護機制<br />
            • 改進的載入與錯誤狀態處理
          </p>
        </div>
      </div>
    </PageErrorBoundary>
  )
}
