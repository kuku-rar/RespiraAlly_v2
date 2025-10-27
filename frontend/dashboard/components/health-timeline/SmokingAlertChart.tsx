/**
 * Smoking Alert Chart
 * CRITICAL: Tracks cigarette consumption (major COPD risk factor)
 * ANY smoking should trigger therapist alert for cessation support
 * Elder-First: Large fonts, High contrast, Red alerts for smoking
 */

'use client'

import { useMemo } from 'react'
import { format } from 'date-fns'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

import type { DailyLog } from '@/lib/types/daily-log'
import { CHART_CONSTANTS } from '@/lib/types/daily-log'

interface SmokingAlertChartProps {
  logs: DailyLog[]
}

export default function SmokingAlertChart({ logs }: SmokingAlertChartProps) {
  // Transform data for chart
  const chartData = useMemo(() => {
    return logs.map((log) => {
      const count = log.smoking_count || 0
      let status: 'none' | 'low' | 'moderate' | 'high'
      if (count === 0) status = 'none'
      else if (count < 5) status = 'low'
      else if (count < 10) status = 'moderate'
      else status = 'high'

      return {
        date: format(new Date(log.log_date), 'MM/dd'),
        fullDate: log.log_date,
        count,
        status,
        hasData: log.smoking_count !== null,
      }
    })
  }, [logs])

  // Calculate statistics
  const stats = useMemo(() => {
    const smokingDays = logs.filter((log) => log.smoking_count && log.smoking_count > 0).length
    const totalCigarettes = logs.reduce((sum, log) => sum + (log.smoking_count || 0), 0)
    const avgPerDay = smokingDays > 0 ? Math.round(totalCigarettes / smokingDays) : 0
    const smokingFree = logs.length - smokingDays

    return {
      smokingDays,
      smokingFree,
      totalCigarettes,
      avgPerDay,
    }
  }, [logs])

  // Get bar color based on smoking count (all smoking is bad for COPD)
  const getBarColor = (status: string) => {
    switch (status) {
      case 'none':
        return CHART_CONSTANTS.COLORS.SUCCESS // Green: No smoking
      case 'low':
        return CHART_CONSTANTS.COLORS.WARNING // Amber: 1-4 cigarettes
      case 'moderate':
        return CHART_CONSTANTS.COLORS.DANGER // Red: 5-9 cigarettes
      case 'high':
        return '#991B1B' // Dark Red: 10+ cigarettes (extreme danger)
      default:
        return CHART_CONSTANTS.COLORS.NEUTRAL
    }
  }

  // Custom tooltip (Elder-First: Large text with STRONG warnings)
  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ payload: { date: string; fullDate: string; count: number; status: string; hasData: boolean } }> }) => {
    if (active && payload && payload[0]) {
      const data = payload[0].payload
      if (!data.hasData) {
        return (
          <div className="bg-white border-2 border-gray-300 rounded-lg shadow-lg p-4">
            <p className="text-lg font-semibold text-gray-800 mb-1">{data.fullDate}</p>
            <p className="text-lg text-gray-500">未記錄</p>
          </div>
        )
      }

      const count = data.count
      let statusLabel = ''
      let bgColor = 'bg-white'
      if (count === 0) {
        statusLabel = '✅ 未吸菸'
        bgColor = 'bg-green-50'
      } else if (count < 5) {
        statusLabel = '⚠️ 低風險'
        bgColor = 'bg-amber-50'
      } else if (count < 10) {
        statusLabel = '🚨 高風險'
        bgColor = 'bg-red-50'
      } else {
        statusLabel = '🚨 極高風險'
        bgColor = 'bg-red-100'
      }

      return (
        <div className={`${bgColor} border-2 border-gray-300 rounded-lg shadow-lg p-4`}>
          <p className="text-lg font-semibold text-gray-800 mb-1">{data.fullDate}</p>
          <p className="text-2xl font-bold text-red-600">{count} 支香菸</p>
          <p className="text-lg font-semibold text-gray-700 mt-1">{statusLabel}</p>
          {count > 0 && (
            <p className="text-sm text-red-600 mt-2">⚠️ 吸菸會加重 COPD 症狀</p>
          )}
        </div>
      )
    }
    return null
  }

  // Check if there's any smoking - CRITICAL for COPD
  const hasSmokingData = stats.totalCigarettes > 0

  return (
    <div>
      {/* Title and Summary */}
      <div className="mb-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-2 flex items-center gap-2">
          🚭 吸菸追蹤
          {hasSmokingData && (
            <span className="text-base font-normal text-red-600 bg-red-100 px-3 py-1 rounded-full">
              ⚠️ 需關注
            </span>
          )}
        </h3>
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-green-500 rounded" />
            <span className="text-lg text-gray-700">未吸菸</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-amber-500 rounded" />
            <span className="text-lg text-gray-700">1-4支</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-red-500 rounded" />
            <span className="text-lg text-gray-700">5-9支</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-red-900 rounded" />
            <span className="text-lg text-gray-700">10+支</span>
          </div>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={CHART_CONSTANTS.HEIGHT}>
        <BarChart data={chartData} margin={CHART_CONSTANTS.MARGIN}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis
            dataKey="date"
            stroke="#6B7280"
            style={{
              fontSize: CHART_CONSTANTS.FONT_SIZE_MEDIUM,
              fontFamily: 'sans-serif',
            }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis
            stroke="#6B7280"
            style={{
              fontSize: CHART_CONSTANTS.FONT_SIZE_MEDIUM,
              fontFamily: 'sans-serif',
            }}
            domain={[0, 'auto']}
            tickFormatter={(value) => `${value}支`}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0,0,0,0.05)' }} />

          {/* Smoking bars */}
          <Bar dataKey="count" radius={[8, 8, 0, 0]} maxBarSize={40}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getBarColor(entry.status)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Statistics Grid (Elder-First: Large text) */}
      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-green-50 rounded-lg p-4">
          <p className="text-base text-gray-600 mb-1">無菸天數</p>
          <p className="text-2xl font-bold text-green-700">{stats.smokingFree} 天</p>
        </div>
        <div className="bg-red-50 rounded-lg p-4">
          <p className="text-base text-gray-600 mb-1">吸菸天數</p>
          <p className="text-2xl font-bold text-red-700">{stats.smokingDays} 天</p>
        </div>
        <div className="bg-red-50 rounded-lg p-4">
          <p className="text-base text-gray-600 mb-1">總吸菸量</p>
          <p className="text-2xl font-bold text-red-700">{stats.totalCigarettes} 支</p>
        </div>
        <div className="bg-red-50 rounded-lg p-4">
          <p className="text-base text-gray-600 mb-1">日均吸菸</p>
          <p className="text-2xl font-bold text-red-700">{stats.avgPerDay} 支</p>
        </div>
      </div>

      {/* CRITICAL: COPD-specific smoking alert */}
      {hasSmokingData ? (
        <div className="mt-4 bg-red-50 border-l-4 border-red-600 rounded-r-lg p-4">
          <p className="text-lg font-bold text-red-800">
            🚨 <strong>重要警告：吸菸對 COPD 患者的危害</strong>
          </p>
          <ul className="mt-2 space-y-1 text-base text-red-700">
            <li>• 加速肺功能衰退</li>
            <li>• 增加急性發作風險</li>
            <li>• 降低藥物治療效果</li>
            <li>• 提高住院和死亡率</li>
          </ul>
          <p className="mt-3 text-base font-semibold text-red-800">
            ⚠️ 建議：立即轉介戒菸門診，提供戒菸支持資源
          </p>
        </div>
      ) : (
        <div className="mt-4 bg-green-50 border-l-4 border-green-600 rounded-r-lg p-4">
          <p className="text-lg font-bold text-green-800">
            ✅ <strong>優秀！無吸菸記錄</strong>
          </p>
          <p className="text-base text-green-700 mt-1">
            持續保持無菸生活是管理 COPD 最重要的一步！
          </p>
        </div>
      )}
    </div>
  )
}
