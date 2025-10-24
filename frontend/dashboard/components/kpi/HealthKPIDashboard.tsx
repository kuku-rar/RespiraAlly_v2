/**
 * Health KPI Dashboard - Display patient health metrics
 * Shows adherence rates, health vitals, survey scores, and risk level
 */

'use client'

import { useEffect, useState } from 'react'
import { kpiApi } from '@/lib/api/kpi'
import { PatientKPI } from '@/lib/types/kpi'
import { KPICard } from './KPICard'

interface HealthKPIDashboardProps {
  patientId: string
}

export function HealthKPIDashboard({ patientId }: HealthKPIDashboardProps) {
  const [kpi, setKpi] = useState<PatientKPI | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchKPI()
  }, [patientId])

  const fetchKPI = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const data = await kpiApi.getPatientKPI(patientId)
      setKpi(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : '載入失敗')
    } finally {
      setIsLoading(false)
    }
  }

  // Helper: Determine BMI status
  const getBMIStatus = (bmi?: number) => {
    if (!bmi) return 'neutral'
    if (bmi < 18.5) return 'warning' // Underweight
    if (bmi >= 18.5 && bmi < 24) return 'good' // Normal
    if (bmi >= 24 && bmi < 27) return 'warning' // Overweight
    return 'danger' // Obese
  }

  // Helper: Determine SpO2 status
  const getSpO2Status = (spo2?: number) => {
    if (!spo2) return 'neutral'
    if (spo2 >= 95) return 'good'
    if (spo2 >= 90) return 'warning'
    return 'danger'
  }

  // Helper: Determine adherence status
  const getAdherenceStatus = (rate?: number) => {
    if (!rate) return 'neutral'
    if (rate >= 80) return 'good'
    if (rate >= 60) return 'warning'
    return 'danger'
  }

  // Helper: Determine CAT score status
  const getCATStatus = (score?: number) => {
    if (!score) return 'neutral'
    if (score < 10) return 'good' // Low impact
    if (score < 20) return 'warning' // Medium impact
    if (score < 30) return 'danger' // High impact
    return 'danger' // Very high impact
  }

  // Helper: Determine risk level
  const getRiskStatus = (riskLevel?: string) => {
    if (!riskLevel) return 'neutral'
    if (riskLevel === 'low') return 'good'
    if (riskLevel === 'medium') return 'warning'
    return 'danger' // high or critical
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        <div className="text-center">
          <div className="text-2xl font-medium text-gray-700">載入中...</div>
        </div>
      </div>
    )
  }

  // Error state
  if (error || !kpi) {
    return (
      <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6">
        <div className="text-xl font-semibold text-red-700 mb-2">
          ⚠️ 載入失敗
        </div>
        <p className="text-lg text-red-600">{error || '無法取得 KPI 資料'}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Section: Adherence Metrics */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          📈 依從性指標
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <KPICard
            title="用藥依從率"
            value={kpi.medication_adherence_rate?.toFixed(0)}
            unit="%"
            status={getAdherenceStatus(kpi.medication_adherence_rate)}
            icon="💊"
            description={
              kpi.medication_adherence_rate
                ? kpi.medication_adherence_rate >= 80
                  ? '良好'
                  : '需改善'
                : undefined
            }
          />
          <KPICard
            title="日誌填寫率"
            value={kpi.log_submission_rate?.toFixed(0)}
            unit="%"
            status={getAdherenceStatus(kpi.log_submission_rate)}
            icon="📝"
            description={
              kpi.log_submission_rate
                ? kpi.log_submission_rate >= 80
                  ? '良好'
                  : '需改善'
                : undefined
            }
          />
          <KPICard
            title="問卷完成率"
            value={kpi.survey_completion_rate?.toFixed(0)}
            unit="%"
            status={getAdherenceStatus(kpi.survey_completion_rate)}
            icon="📋"
            description={
              kpi.survey_completion_rate
                ? kpi.survey_completion_rate >= 80
                  ? '良好'
                  : '需改善'
                : undefined
            }
          />
        </div>
      </div>

      {/* Section: Health Metrics */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          💓 健康指標
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <KPICard
            title="BMI 指數"
            value={kpi.latest_bmi?.toFixed(1)}
            unit=""
            status={getBMIStatus(kpi.latest_bmi)}
            icon="⚖️"
            description="正常範圍: 18.5-24"
          />
          <KPICard
            title="血氧飽和度"
            value={kpi.latest_spo2?.toFixed(0)}
            unit="%"
            status={getSpO2Status(kpi.latest_spo2)}
            icon="🫁"
            description="正常範圍: ≥95%"
          />
          <KPICard
            title="心率"
            value={kpi.latest_heart_rate?.toFixed(0)}
            unit="bpm"
            status={
              kpi.latest_heart_rate &&
              kpi.latest_heart_rate >= 60 &&
              kpi.latest_heart_rate <= 100
                ? 'good'
                : 'warning'
            }
            icon="❤️"
            description="正常範圍: 60-100 bpm"
          />
        </div>
      </div>

      {/* Section: Blood Pressure */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          🩺 血壓
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <KPICard
            title="收縮壓"
            value={kpi.latest_systolic_bp?.toFixed(0)}
            unit="mmHg"
            status={
              kpi.latest_systolic_bp && kpi.latest_systolic_bp < 130
                ? 'good'
                : 'warning'
            }
            icon="📊"
            description="正常範圍: <130 mmHg"
          />
          <KPICard
            title="舒張壓"
            value={kpi.latest_diastolic_bp?.toFixed(0)}
            unit="mmHg"
            status={
              kpi.latest_diastolic_bp && kpi.latest_diastolic_bp < 85
                ? 'good'
                : 'warning'
            }
            icon="📊"
            description="正常範圍: <85 mmHg"
          />
        </div>
      </div>

      {/* Section: Survey Scores & Risk */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          🎯 問卷與風險評估
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <KPICard
            title="CAT 評分"
            value={kpi.latest_cat_score?.toFixed(0)}
            unit="分"
            status={getCATStatus(kpi.latest_cat_score)}
            icon="📋"
            description={
              kpi.latest_cat_score
                ? kpi.latest_cat_score < 10
                  ? '低影響'
                  : kpi.latest_cat_score < 20
                    ? '中度影響'
                    : kpi.latest_cat_score < 30
                      ? '高度影響'
                      : '極高影響'
                : '範圍: 0-40'
            }
          />
          <KPICard
            title="mMRC 評分"
            value={kpi.latest_mmrc_score?.toFixed(0)}
            unit="級"
            status={
              kpi.latest_mmrc_score && kpi.latest_mmrc_score <= 1
                ? 'good'
                : 'warning'
            }
            icon="🫁"
            description="範圍: 0-4 級"
          />
          <KPICard
            title="風險等級"
            value={
              kpi.risk_level
                ? kpi.risk_level === 'low'
                  ? '低風險'
                  : kpi.risk_level === 'medium'
                    ? '中風險'
                    : kpi.risk_level === 'high'
                      ? '高風險'
                      : '極高風險'
                : '-'
            }
            unit=""
            status={getRiskStatus(kpi.risk_level)}
            icon="🎯"
            description={
              kpi.gold_group
                ? `GOLD ${kpi.gold_group} 級 | CAT: ${kpi.latest_cat_score ?? '-'}, mMRC: ${kpi.latest_mmrc_score ?? '-'}`
                : `風險分數: ${kpi.risk_score?.toFixed(0) || '-'}`
            }
          />
        </div>
      </div>

      {/* Section: Activity */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          📅 活動紀錄
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <KPICard
            title="最後日誌日期"
            value={kpi.last_log_date || '-'}
            unit=""
            status={
              kpi.days_since_last_log !== undefined
                ? kpi.days_since_last_log === 0
                  ? 'good'
                  : kpi.days_since_last_log <= 2
                    ? 'warning'
                    : 'danger'
                : 'neutral'
            }
            icon="📝"
          />
          <KPICard
            title="距今天數"
            value={kpi.days_since_last_log}
            unit="天"
            status={
              kpi.days_since_last_log !== undefined
                ? kpi.days_since_last_log === 0
                  ? 'good'
                  : kpi.days_since_last_log <= 2
                    ? 'warning'
                    : 'danger'
                : 'neutral'
            }
            icon="⏰"
            description={
              kpi.days_since_last_log === 0
                ? '今天已填寫'
                : kpi.days_since_last_log === 1
                  ? '昨天填寫'
                  : undefined
            }
          />
        </div>
      </div>

      {/* Mock Mode Indicator */}
      {process.env.NEXT_PUBLIC_MOCK_MODE === 'true' && (
        <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4">
          <p className="text-base text-yellow-800 text-center">
            🧪 <strong>Mock 模式</strong> - 顯示測試數據
          </p>
        </div>
      )}

      {/* Last Updated */}
      <div className="text-sm text-gray-500 text-right">
        最後更新: {new Date(kpi.updated_at).toLocaleString('zh-TW')}
      </div>
    </div>
  )
}
