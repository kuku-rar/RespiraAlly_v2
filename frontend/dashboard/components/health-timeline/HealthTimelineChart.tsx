/**
 * Health Timeline Chart - Main Container
 * Displays patient daily log visualizations
 * Elder-First Design: Large fonts (≥18px), High contrast, Touch-friendly (≥52px)
 */

'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { format, subDays } from 'date-fns'

import { getDailyLogsForChart, getPatientDailyLogStats } from '@/lib/api/daily-log'
import type { DailyLog, DailyLogStats } from '@/lib/types/daily-log'

import MedicationAdherenceChart from './MedicationAdherenceChart'
import WaterIntakeChart from './WaterIntakeChart'
import ExerciseBarChart from './ExerciseBarChart'
import SmokingAlertChart from './SmokingAlertChart'
import MoodTrendChart from './MoodTrendChart'

interface HealthTimelineChartProps {
  patientId: string
  defaultDays?: number // Default: 30 days
}

/**
 * Main Health Timeline Chart Container
 * Fetches data and orchestrates all sub-charts
 */
export default function HealthTimelineChart({
  patientId,
  defaultDays = 30,
}: HealthTimelineChartProps) {
  // Date range state
  const [days, setDays] = useState(defaultDays)
  const endDate = new Date()
  const startDate = subDays(endDate, days)

  const startDateStr = format(startDate, 'yyyy-MM-dd')
  const endDateStr = format(endDate, 'yyyy-MM-dd')

  // Fetch daily logs for charts
  const {
    data: dailyLogs,
    isLoading: logsLoading,
    error: logsError,
  } = useQuery<DailyLog[]>({
    queryKey: ['daily-logs-chart', patientId, startDateStr, endDateStr],
    queryFn: () => getDailyLogsForChart(patientId, startDateStr, endDateStr),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Fetch statistics
  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
  } = useQuery<DailyLogStats>({
    queryKey: ['daily-log-stats', patientId, startDateStr, endDateStr],
    queryFn: () => getPatientDailyLogStats(patientId, startDateStr, endDateStr),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Loading state
  if (logsLoading || statsLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full" />
          <span className="ml-4 text-lg text-gray-600">載入健康數據...</span>
        </div>
      </div>
    )
  }

  // Error state
  if (logsError || statsError) {
    return (
      <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-red-800 mb-2">無法載入健康數據</h3>
        <p className="text-lg text-red-600">
          {logsError?.message || statsError?.message || '發生未知錯誤'}
        </p>
      </div>
    )
  }

  // No data state
  if (!dailyLogs || dailyLogs.length === 0) {
    return (
      <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-8 text-center">
        <svg
          className="mx-auto h-16 w-16 text-gray-400 mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
          />
        </svg>
        <p className="text-xl text-gray-600">此期間尚無健康數據</p>
        <p className="text-lg text-gray-500 mt-2">請選擇其他日期範圍</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Date Range Selector (Elder-First: Large buttons ≥52px) */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">日期範圍</h3>
        <div className="flex flex-wrap gap-3">
          {[7, 14, 30, 60, 90].map((dayCount) => (
            <button
              key={dayCount}
              onClick={() => setDays(dayCount)}
              className={`
                px-6 py-4 min-h-[52px] text-lg font-medium rounded-lg transition-all
                ${
                  days === dayCount
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }
              `}
            >
              最近 {dayCount} 天
            </button>
          ))}
        </div>

        {/* Stats Summary (Elder-First: Large font ≥18px) */}
        {stats && (
          <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <p className="text-base text-gray-600 mb-1">總筆數</p>
              <p className="text-2xl font-bold text-blue-700">{stats.total_logs}</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <p className="text-base text-gray-600 mb-1">服藥遵從率</p>
              <p className="text-2xl font-bold text-green-700">
                {stats.medication_adherence_rate.toFixed(1)}%
              </p>
            </div>
            <div className="bg-indigo-50 rounded-lg p-4">
              <p className="text-base text-gray-600 mb-1">平均飲水</p>
              <p className="text-2xl font-bold text-indigo-700">
                {stats.avg_water_intake_ml?.toFixed(0) || 0} ml
              </p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <p className="text-base text-gray-600 mb-1">平均運動</p>
              <p className="text-2xl font-bold text-purple-700">
                {stats.avg_exercise_minutes?.toFixed(0) || 0} 分鐘
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Chart Grid (Elder-First: Spacious layout) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Medication Adherence Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <MedicationAdherenceChart logs={dailyLogs} />
        </div>

        {/* Water Intake Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <WaterIntakeChart logs={dailyLogs} />
        </div>

        {/* Exercise Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <ExerciseBarChart logs={dailyLogs} />
        </div>

        {/* Smoking Alert Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <SmokingAlertChart logs={dailyLogs} />
        </div>

        {/* Mood Trend Chart (Full width) */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 lg:col-span-2">
          <MoodTrendChart logs={dailyLogs} />
        </div>
      </div>
    </div>
  )
}
