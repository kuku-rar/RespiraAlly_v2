/**
 * Medication Adherence Chart
 * Visualizes patient medication compliance over time
 * Elder-First: Large fonts, High contrast, Clear indicators
 */

'use client'

import { useMemo } from 'react'
import { format } from 'date-fns'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

import type { DailyLog } from '@/lib/types/daily-log'
import { CHART_CONSTANTS } from '@/lib/types/daily-log'

interface MedicationAdherenceChartProps {
  logs: DailyLog[]
}

export default function MedicationAdherenceChart({ logs }: MedicationAdherenceChartProps) {
  // Transform data for chart
  const chartData = useMemo(() => {
    return logs.map((log) => ({
      date: format(new Date(log.log_date), 'MM/dd'),
      fullDate: log.log_date,
      taken: log.medication_taken === true,
      value: log.medication_taken === true ? 1 : 0,
      label: log.medication_taken === true ? '已服藥' : log.medication_taken === false ? '未服藥' : '未記錄',
    }))
  }, [logs])

  // Calculate adherence rate
  const adherenceRate = useMemo(() => {
    const totalRecorded = logs.filter((log) => log.medication_taken !== null).length
    const totalTaken = logs.filter((log) => log.medication_taken === true).length
    return totalRecorded > 0 ? ((totalTaken / totalRecorded) * 100).toFixed(1) : '0.0'
  }, [logs])

  // Custom tooltip (Elder-First: Large text)
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload[0]) {
      const data = payload[0].payload
      return (
        <div className="bg-white border-2 border-gray-300 rounded-lg shadow-lg p-4">
          <p className="text-lg font-semibold text-gray-800 mb-1">{data.fullDate}</p>
          <p className={`text-xl font-bold ${data.taken ? 'text-green-600' : 'text-red-600'}`}>
            {data.label}
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div>
      {/* Title and Summary */}
      <div className="mb-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-2">服藥遵從率</h3>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-green-500 rounded" />
            <span className="text-lg text-gray-700">已服藥</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-red-500 rounded" />
            <span className="text-lg text-gray-700">未服藥</span>
          </div>
          <div className="ml-auto">
            <span className="text-lg text-gray-600">遵從率: </span>
            <span className="text-2xl font-bold text-blue-700">{adherenceRate}%</span>
          </div>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={CHART_CONSTANTS.HEIGHT}>
        <BarChart
          data={chartData}
          margin={CHART_CONSTANTS.MARGIN}
        >
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
            ticks={[0, 1]}
            domain={[0, 1]}
            tickFormatter={(value) => (value === 1 ? '已服藥' : '未服藥')}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0,0,0,0.05)' }} />
          <Bar
            dataKey="value"
            radius={[8, 8, 0, 0]}
            maxBarSize={40}
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.taken ? CHART_CONSTANTS.COLORS.SUCCESS : CHART_CONSTANTS.COLORS.DANGER}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Elder-First: Large text insights */}
      <div className="mt-4 bg-blue-50 rounded-lg p-4">
        <p className="text-lg text-gray-700">
          📊 近期記錄: <span className="font-semibold">{logs.length} 天</span>
        </p>
        <p className="text-lg text-gray-700">
          ✅ 已服藥: <span className="font-semibold text-green-700">
            {logs.filter((log) => log.medication_taken === true).length} 天
          </span>
        </p>
        <p className="text-lg text-gray-700">
          ❌ 未服藥: <span className="font-semibold text-red-700">
            {logs.filter((log) => log.medication_taken === false).length} 天
          </span>
        </p>
      </div>
    </div>
  )
}
