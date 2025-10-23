/**
 * Exercise Bar Chart
 * Visualizes patient daily exercise duration
 * COPD patients recommended: 30-60 minutes of moderate exercise daily
 * Elder-First: Large fonts, High contrast, Color-coded bars
 */

'use client'

import { useMemo } from 'react'
import { format } from 'date-fns'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
} from 'recharts'

import type { DailyLog } from '@/lib/types/daily-log'
import { CHART_CONSTANTS } from '@/lib/types/daily-log'

interface ExerciseBarChartProps {
  logs: DailyLog[]
}

export default function ExerciseBarChart({ logs }: ExerciseBarChartProps) {
  // Transform data for chart
  const chartData = useMemo(() => {
    return logs.map((log) => {
      const minutes = log.exercise_minutes || 0
      let status: 'excellent' | 'good' | 'low' | 'none'
      if (minutes === 0) status = 'none'
      else if (minutes < 10) status = 'low'
      else if (minutes >= 30 && minutes <= 120) status = 'excellent'
      else status = 'good'

      return {
        date: format(new Date(log.log_date), 'MM/dd'),
        fullDate: log.log_date,
        minutes,
        status,
        hasData: log.exercise_minutes !== null,
      }
    })
  }, [logs])

  // Calculate average
  const avgExercise = useMemo(() => {
    const validLogs = logs.filter((log) => log.exercise_minutes !== null && log.exercise_minutes > 0)
    if (validLogs.length === 0) return 0
    const total = validLogs.reduce((sum, log) => sum + (log.exercise_minutes || 0), 0)
    return Math.round(total / validLogs.length)
  }, [logs])

  // Get bar color based on exercise duration
  const getBarColor = (status: string) => {
    switch (status) {
      case 'excellent':
        return CHART_CONSTANTS.COLORS.SUCCESS // Green: 30-120 min
      case 'good':
        return CHART_CONSTANTS.COLORS.PRIMARY // Blue: >10 min
      case 'low':
        return CHART_CONSTANTS.COLORS.WARNING // Amber: <10 min
      case 'none':
        return CHART_CONSTANTS.COLORS.NEUTRAL // Gray: 0 min
      default:
        return CHART_CONSTANTS.COLORS.NEUTRAL
    }
  }

  // Custom tooltip (Elder-First: Large text)
  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ payload: ExerciseDataPoint }> }) => {
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

      const minutes = data.minutes
      let statusLabel = ''
      if (minutes === 0) statusLabel = '未運動'
      else if (minutes < 10) statusLabel = '⚠️ 時間不足'
      else if (minutes >= 30 && minutes <= 120) statusLabel = '✅ 達標'
      else if (minutes > 120) statusLabel = '⚠️ 運動過量'
      else statusLabel = '💪 可增加'

      return (
        <div className="bg-white border-2 border-gray-300 rounded-lg shadow-lg p-4">
          <p className="text-lg font-semibold text-gray-800 mb-1">{data.fullDate}</p>
          <p className="text-2xl font-bold text-blue-600">{minutes} 分鐘</p>
          <p className="text-lg text-gray-700 mt-1">{statusLabel}</p>
        </div>
      )
    }
    return null
  }

  return (
    <div>
      {/* Title and Summary */}
      <div className="mb-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-2">每日運動時間</h3>
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-green-500 rounded" />
            <span className="text-lg text-gray-700">達標 (30-120分)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-blue-500 rounded" />
            <span className="text-lg text-gray-700">有運動</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-amber-500 rounded" />
            <span className="text-lg text-gray-700">時間不足</span>
          </div>
          <div className="ml-auto">
            <span className="text-lg text-gray-600">平均: </span>
            <span className="text-2xl font-bold text-blue-700">{avgExercise} 分鐘</span>
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
            tickFormatter={(value) => `${value}分`}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0,0,0,0.05)' }} />

          {/* Reference lines for recommended range */}
          <ReferenceLine
            y={30}
            stroke={CHART_CONSTANTS.COLORS.SUCCESS}
            strokeDasharray="3 3"
            strokeWidth={2}
            label={{
              value: '建議下限 30分',
              position: 'right',
              fontSize: CHART_CONSTANTS.FONT_SIZE_SMALL,
              fill: CHART_CONSTANTS.COLORS.SUCCESS,
            }}
          />
          <ReferenceLine
            y={120}
            stroke={CHART_CONSTANTS.COLORS.WARNING}
            strokeDasharray="3 3"
            strokeWidth={2}
            label={{
              value: '安全上限 120分',
              position: 'right',
              fontSize: CHART_CONSTANTS.FONT_SIZE_SMALL,
              fill: CHART_CONSTANTS.COLORS.WARNING,
            }}
          />

          {/* Exercise bars */}
          <Bar dataKey="minutes" radius={[8, 8, 0, 0]} maxBarSize={40}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getBarColor(entry.status)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Elder-First: Large text insights */}
      <div className="mt-4 grid grid-cols-3 gap-4">
        <div className="bg-green-50 rounded-lg p-4">
          <p className="text-base text-gray-600 mb-1">達標天數</p>
          <p className="text-2xl font-bold text-green-700">
            {logs.filter((log) => log.exercise_minutes && log.exercise_minutes >= 30 && log.exercise_minutes <= 120).length} 天
          </p>
        </div>
        <div className="bg-blue-50 rounded-lg p-4">
          <p className="text-base text-gray-600 mb-1">有運動</p>
          <p className="text-2xl font-bold text-blue-700">
            {logs.filter((log) => log.exercise_minutes && log.exercise_minutes > 0).length} 天
          </p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-base text-gray-600 mb-1">未運動</p>
          <p className="text-2xl font-bold text-gray-700">
            {logs.filter((log) => !log.exercise_minutes || log.exercise_minutes === 0).length} 天
          </p>
        </div>
      </div>

      {/* COPD-specific guidance */}
      <div className="mt-4 bg-blue-50 border-l-4 border-blue-500 rounded-r-lg p-4">
        <p className="text-lg text-gray-700">
          💪 <strong>COPD 患者運動建議：</strong>
        </p>
        <p className="text-base text-gray-600 mt-1">
          規律的適度運動能改善呼吸功能和生活品質。建議每日進行 30-60 分鐘的溫和運動，如散步、伸展運動。避免過度劇烈運動。
        </p>
      </div>
    </div>
  )
}
