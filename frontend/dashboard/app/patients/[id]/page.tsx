/**
 * Patient Detail Page - Patient 360° View
 * Displays comprehensive patient information: Profile, Daily Logs, Surveys, KPIs
 *
 * Sprint 3 Task 5.1: Dashboard 360° 頁面
 */

'use client'

import { useParams } from 'next/navigation'
import { usePatient, useDailyLogs, useSurveys } from '@/hooks/api'

// UI Components (to be implemented in Task 5.1.2)
// import { PatientHeader } from '@/components/patient/PatientHeader'
// import { PatientTabs } from '@/components/patient/PatientTabs'

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
  // Main Content (Temporary - Task 5.1.2 will add proper components)
  // ========================================

  return (
    <div className="container mx-auto py-8 space-y-6">
      {/* Success Message - Hooks Working */}
      <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4">
        <p className="text-lg text-green-800 font-semibold">
          ✅ Task 5.1.1 完成 - TanStack Query Hooks 正常運作！
        </p>
        <p className="text-sm text-green-700 mt-1">
          成功載入 Patient ({patient?.name}), Daily Logs ({dailyLogs?.items.length || 0} 筆), Surveys ({surveys?.items.length || 0} 筆)
        </p>
      </div>

      {/* Temporary: Patient Header (Task 5.1.2 will replace this) */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{patient.name}</h1>
            <p className="text-gray-600 mt-1">
              {patient.gender === 'MALE' ? '男性' : patient.gender === 'FEMALE' ? '女性' : '其他'} · {patient.age} 歲 · {patient.phone}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">身高 / 體重</p>
            <p className="text-lg font-semibold text-gray-900">
              {patient.height_cm} cm / {patient.weight_kg} kg
            </p>
            <p className="text-sm text-gray-600 mt-1">BMI: {patient.bmi?.toFixed(1)}</p>
          </div>
        </div>
      </div>

      {/* Temporary: Data Display (Task 5.1.2 will add PatientTabs) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Daily Logs Card */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">📊 每日紀錄</h2>
          {logsError ? (
            <p className="text-red-600">載入失敗: {logsError.message}</p>
          ) : dailyLogs && dailyLogs.items.length > 0 ? (
            <div className="space-y-2">
              <p className="text-gray-600">總筆數: {dailyLogs.total}</p>
              <p className="text-sm text-gray-500">
                最近 7 天: {dailyLogs.items.length} 筆
              </p>
              {/* Latest log preview */}
              {dailyLogs.items[0] && (
                <div className="mt-4 p-3 bg-gray-50 rounded">
                  <p className="text-sm font-medium text-gray-900">最新紀錄</p>
                  <p className="text-xs text-gray-600 mt-1">
                    日期: {dailyLogs.items[0].log_date}
                  </p>
                </div>
              )}
            </div>
          ) : (
            <p className="text-gray-500">尚無每日紀錄</p>
          )}
        </div>

        {/* Surveys Card */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">📋 問卷評估</h2>
          {surveysError ? (
            <p className="text-red-600">載入失敗: {surveysError.message}</p>
          ) : surveys && surveys.items.length > 0 ? (
            <div className="space-y-2">
              <p className="text-gray-600">總筆數: {surveys.total}</p>
              <div className="mt-4 space-y-2">
                {surveys.items.slice(0, 3).map((survey) => (
                  <div key={survey.response_id} className="p-3 bg-gray-50 rounded">
                    <p className="text-sm font-medium text-gray-900">
                      {survey.survey_type} - 分數: {survey.score}
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      {new Date(survey.completed_at).toLocaleDateString('zh-TW')}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-gray-500">尚無問卷評估</p>
          )}
        </div>

        {/* Next Steps Card */}
        <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
          <h2 className="text-xl font-semibold text-blue-900 mb-4">📍 下一步</h2>
          <ul className="space-y-2 text-sm text-blue-800">
            <li>✅ Task 5.1.1 - API Hooks 完成</li>
            <li>⏳ Task 5.1.2 - PatientHeader</li>
            <li>⏳ Task 5.1.2 - PatientTabs</li>
            <li>⏳ Task 5.1.3 - DailyLogsTrendChart</li>
            <li>⏳ Task 5.1.4 - 錯誤處理 & 測試</li>
          </ul>
        </div>
      </div>

      {/* Development Info */}
      {process.env.NODE_ENV === 'development' && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <details>
            <summary className="text-sm font-medium text-yellow-900 cursor-pointer">
              🔧 開發資訊 (點擊展開)
            </summary>
            <div className="mt-4 space-y-4">
              <div>
                <p className="text-xs font-semibold text-yellow-900">Patient Data:</p>
                <pre className="text-xs text-yellow-800 bg-yellow-100 p-2 rounded mt-1 overflow-auto">
                  {JSON.stringify(patient, null, 2)}
                </pre>
              </div>
              <div>
                <p className="text-xs font-semibold text-yellow-900">Daily Logs:</p>
                <pre className="text-xs text-yellow-800 bg-yellow-100 p-2 rounded mt-1 overflow-auto max-h-40">
                  {JSON.stringify(dailyLogs?.items.slice(0, 2), null, 2)}
                </pre>
              </div>
              <div>
                <p className="text-xs font-semibold text-yellow-900">Surveys:</p>
                <pre className="text-xs text-yellow-800 bg-yellow-100 p-2 rounded mt-1 overflow-auto max-h-40">
                  {JSON.stringify(surveys?.items.slice(0, 2), null, 2)}
                </pre>
              </div>
            </div>
          </details>
        </div>
      )}
    </div>
  )
}
