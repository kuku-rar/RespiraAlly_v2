/**
 * Water Intake Chart
 * Visualizes patient daily water consumption
 * COPD patients need adequate hydration (recommended: 2000-3000ml/day)
 * Elder-First: Large fonts, High contrast, Clear trend line
 */

'use client'

import { useMemo } from 'react'
import { format } from 'date-fns'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'

import type { DailyLog } from '@/lib/types/daily-log'
import { CHART_CONSTANTS } from '@/lib/types/daily-log'

interface WaterIntakeChartProps {
  logs: DailyLog[]
}

export default function WaterIntakeChart({ logs }: WaterIntakeChartProps) {
  // Transform data for chart
  const chartData = useMemo(() => {
    return logs.map((log) => ({
      date: format(new Date(log.log_date), 'MM/dd'),
      fullDate: log.log_date,
      water: log.water_intake_ml || 0,
      hasData: log.water_intake_ml !== null,
    }))
  }, [logs])

  // Calculate average
  const avgWater = useMemo(() => {
    const validLogs = logs.filter((log) => log.water_intake_ml !== null && log.water_intake_ml > 0)
    if (validLogs.length === 0) return 0
    const total = validLogs.reduce((sum, log) => sum + (log.water_intake_ml || 0), 0)
    return Math.round(total / validLogs.length)
  }, [logs])

  // Custom tooltip (Elder-First: Large text)
  const CustomTooltip = ({ active, payload }: any) => {
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

      const water = data.water
      const status =
        water < 500 ? '⚠️ 攝取不足' : water > 5000 ? '⚠️ 過量攝取' : water >= 2000 ? '✅ 良好' : '💧 可增加'

      return (
        <div className="bg-white border-2 border-gray-300 rounded-lg shadow-lg p-4">
          <p className="text-lg font-semibold text-gray-800 mb-1">{data.fullDate}</p>
          <p className="text-2xl font-bold text-blue-600">{water} ml</p>
          <p className="text-lg text-gray-700 mt-1">{status}</p>
        </div>
      )
    }
    return null
  }

  return (
    <div>
      {/* Title and Summary */}
      <div className="mb-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-2">每日飲水量</h3>
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-blue-500 rounded" />
            <span className="text-lg text-gray-700">實際攝取</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-2 bg-green-500" />
            <span className="text-lg text-gray-700">建議範圍 (2000-3000ml)</span>
          </div>
          <div className="ml-auto">
            <span className="text-lg text-gray-600">平均: </span>
            <span className="text-2xl font-bold text-blue-700">{avgWater} ml</span>
          </div>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={CHART_CONSTANTS.HEIGHT}>
        <LineChart data={chartData} margin={CHART_CONSTANTS.MARGIN}>
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
            tickFormatter={(value) => `${value}ml`}
          />
          <Tooltip content={<CustomTooltip />} />

          {/* Reference lines for recommended range */}
          <ReferenceLine
            y={2000}
            stroke={CHART_CONSTANTS.COLORS.SUCCESS}
            strokeDasharray="3 3"
            strokeWidth={2}
            label={{
              value: '建議下限 2000ml',
              position: 'right',
              fontSize: CHART_CONSTANTS.FONT_SIZE_SMALL,
              fill: CHART_CONSTANTS.COLORS.SUCCESS,
            }}
          />
          <ReferenceLine
            y={3000}
            stroke={CHART_CONSTANTS.COLORS.SUCCESS}
            strokeDasharray="3 3"
            strokeWidth={2}
            label={{
              value: '建議上限 3000ml',
              position: 'right',
              fontSize: CHART_CONSTANTS.FONT_SIZE_SMALL,
              fill: CHART_CONSTANTS.COLORS.SUCCESS,
            }}
          />

          {/* Water intake line */}
          <Line
            type="monotone"
            dataKey="water"
            stroke={CHART_CONSTANTS.COLORS.PRIMARY}
            strokeWidth={3}
            dot={{ fill: CHART_CONSTANTS.COLORS.PRIMARY, r: 6 }}
            activeDot={{ r: 8 }}
            connectNulls={false}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Elder-First: Large text insights */}
      <div className="mt-4 grid grid-cols-2 gap-4">
        <div className="bg-green-50 rounded-lg p-4">
          <p className="text-base text-gray-600 mb-1">達標天數</p>
          <p className="text-2xl font-bold text-green-700">
            {logs.filter((log) => log.water_intake_ml && log.water_intake_ml >= 2000).length} 天
          </p>
        </div>
        <div className="bg-amber-50 rounded-lg p-4">
          <p className="text-base text-gray-600 mb-1">需改善天數</p>
          <p className="text-2xl font-bold text-amber-700">
            {logs.filter((log) => log.water_intake_ml && log.water_intake_ml < 2000).length} 天
          </p>
        </div>
      </div>

      {/* COPD-specific guidance */}
      <div className="mt-4 bg-blue-50 border-l-4 border-blue-500 rounded-r-lg p-4">
        <p className="text-lg text-gray-700">
          💧 <strong>COPD 患者飲水建議：</strong>
        </p>
        <p className="text-base text-gray-600 mt-1">
          充足的水分攝取有助於稀釋痰液，使其更容易咳出。建議每日攝取 2000-3000ml 的水分。
        </p>
      </div>
    </div>
  )
}
