/**
 * Patient Detail Page - Single Patient View (Placeholder)
 * Future: Display patient 360° profile, health timeline, KPIs
 */

'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { patientsApi } from '@/lib/api/patients'
import { tokenManager } from '@/lib/api/auth'
import type { PatientResponse } from '@/lib/types/patient'
import { HealthKPIDashboard } from '@/components/kpi/HealthKPIDashboard'
import { HealthTimelineChart } from '@/components/health-timeline'

export default function PatientDetailPage() {
  const router = useRouter()
  const params = useParams()
  const patientId = params.id as string

  const [patient, setPatient] = useState<PatientResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Check authentication
    const token = tokenManager.getAccessToken()
    if (!token) {
      router.push('/login')
      return
    }

    fetchPatient()
  }, [patientId, router])

  const fetchPatient = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await patientsApi.getPatient(patientId)
      setPatient(response)
    } catch (err) {
      setError(err instanceof Error ? err.message : '載入失敗')
    } finally {
      setIsLoading(false)
    }
  }

  const handleBackToList = () => {
    router.push('/patients')
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-2xl font-medium text-gray-700">載入中...</div>
      </div>
    )
  }

  // Error state
  if (error || !patient) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 border border-gray-200 text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-3xl font-bold text-red-600 mb-4">
            載入失敗
          </h2>
          <p className="text-xl text-gray-600 mb-6">
            {error || '找不到病患資料'}
          </p>
          <button
            onClick={handleBackToList}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white text-xl font-semibold py-4 rounded-lg transition-colors"
            style={{ minHeight: '56px' }}
          >
            返回病患列表
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <button
            onClick={handleBackToList}
            className="text-blue-600 hover:text-blue-800 text-lg mb-2"
          >
            ← 返回病患列表
          </button>
          <h1 className="text-3xl font-bold text-gray-900">
            {patient.name}
          </h1>
          <p className="text-lg text-gray-600 mt-1">
            病患詳細資料
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Basic Information Card */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 mb-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            基本資料
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-lg font-medium text-gray-700 mb-2">
                姓名
              </label>
              <p className="text-xl text-gray-900">{patient.name}</p>
            </div>

            <div>
              <label className="block text-lg font-medium text-gray-700 mb-2">
                性別
              </label>
              <p className="text-xl text-gray-900">
                {patient.gender === 'MALE' ? '男性' : patient.gender === 'FEMALE' ? '女性' : '其他'}
              </p>
            </div>

            <div>
              <label className="block text-lg font-medium text-gray-700 mb-2">
                出生日期
              </label>
              <p className="text-xl text-gray-900">{patient.birth_date}</p>
            </div>

            <div>
              <label className="block text-lg font-medium text-gray-700 mb-2">
                年齡
              </label>
              <p className="text-xl text-gray-900">
                {patient.age ? `${patient.age} 歲` : '-'}
              </p>
            </div>

            <div>
              <label className="block text-lg font-medium text-gray-700 mb-2">
                聯絡電話
              </label>
              <p className="text-xl text-gray-900">{patient.phone || '-'}</p>
            </div>

            <div>
              <label className="block text-lg font-medium text-gray-700 mb-2">
                身高
              </label>
              <p className="text-xl text-gray-900">
                {patient.height_cm ? `${patient.height_cm} cm` : '-'}
              </p>
            </div>

            <div>
              <label className="block text-lg font-medium text-gray-700 mb-2">
                體重
              </label>
              <p className="text-xl text-gray-900">
                {patient.weight_kg ? `${patient.weight_kg} kg` : '-'}
              </p>
            </div>

            <div>
              <label className="block text-lg font-medium text-gray-700 mb-2">
                BMI
              </label>
              <p className="text-xl text-gray-900">
                {patient.bmi ? patient.bmi.toFixed(1) : '-'}
              </p>
            </div>
          </div>
        </div>

        {/* Health KPI Dashboard */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 mb-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            健康關鍵指標 (KPI)
          </h2>
          <HealthKPIDashboard patientId={patientId} />
        </div>

        {/* Health Timeline - Daily Log Charts (Phase 1) */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-semibold text-gray-900">
              📊 健康時間軸
            </h2>
            <a
              href="https://github.com/kuku-rar/RespiraAlly_v2/issues/5"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-blue-600 hover:underline"
            >
              Issue #5: Health Timeline Chart
            </a>
          </div>
          <HealthTimelineChart patientId={patientId} defaultDays={30} />
        </div>

        {/* Phase 2 Placeholder - Survey Charts */}
        <div className="bg-blue-50 rounded-xl border border-blue-200 p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            📋 Phase 2: Survey 評估圖表
          </h3>
          <p className="text-lg text-gray-700 mb-3">
            下列功能待 Survey API 完成後實作：
          </p>
          <ul className="space-y-2 text-base text-gray-600">
            <li>• <strong>CAT Score (COPD 評估測試)</strong>: 評估 COPD 對生活的影響程度</li>
            <li>• <strong>mMRC Score (呼吸困難分級)</strong>: 測量呼吸困難的嚴重程度</li>
          </ul>
          <p className="text-sm text-gray-500 mt-4">
            ⏳ 預計時程: Survey API 完成後 2-3 小時
          </p>
        </div>

        {/* Mock Mode Indicator */}
        {process.env.NEXT_PUBLIC_MOCK_MODE === 'true' && (
          <div className="mt-6 bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4">
            <p className="text-base text-yellow-800 text-center">
              🧪 <strong>Mock 模式</strong> - 顯示測試數據
            </p>
          </div>
        )}
      </main>
    </div>
  )
}
