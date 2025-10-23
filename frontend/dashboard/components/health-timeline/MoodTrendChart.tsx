/**
 * Mood Trend Chart
 * Visualizes patient emotional well-being over time
 * COPD patients often experience anxiety/depression - mood tracking is important
 * Elder-First: Large fonts, High contrast, Color-coded mood indicators
 */

'use client'

import { useMemo } from 'react'
import { format } from 'date-fns'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'

import type { DailyLog, DailyLogMood } from '@/lib/types/daily-log'
import { CHART_CONSTANTS } from '@/lib/types/daily-log'

interface MoodTrendChartProps {
  logs: DailyLog[]
}

export default function MoodTrendChart({ logs }: MoodTrendChartProps) {
  // Convert mood to numeric score for visualization
  const getMoodScore = (mood: DailyLogMood | null): number | null => {
    switch (mood) {
      case 'GOOD':
        return 3
      case 'NEUTRAL':
        return 2
      case 'BAD':
        return 1
      default:
        return null
    }
  }

  // Convert mood to label
  const getMoodLabel = (mood: DailyLogMood | null): string => {
    switch (mood) {
      case 'GOOD':
        return '良好'
      case 'NEUTRAL':
        return '普通'
      case 'BAD':
        return '不佳'
      default:
        return '未記錄'
    }
  }

  // Get mood color
  const getMoodColor = (mood: DailyLogMood | null): string => {
    switch (mood) {
      case 'GOOD':
        return CHART_CONSTANTS.COLORS.GOOD
      case 'NEUTRAL':
        return CHART_CONSTANTS.COLORS.NEUTRAL_MOOD
      case 'BAD':
        return CHART_CONSTANTS.COLORS.BAD
      default:
        return CHART_CONSTANTS.COLORS.NEUTRAL
    }
  }

  // Transform data for chart
  const chartData = useMemo(() => {
    return logs.map((log) => ({
      date: format(new Date(log.log_date), 'MM/dd'),
      fullDate: log.log_date,
      mood: log.mood,
      moodScore: getMoodScore(log.mood),
      moodLabel: getMoodLabel(log.mood),
      hasData: log.mood !== null,
    }))
  }, [logs])

  // Calculate mood distribution
  const moodStats = useMemo(() => {
    const total = logs.filter((log) => log.mood !== null).length
    const good = logs.filter((log) => log.mood === 'GOOD').length
    const neutral = logs.filter((log) => log.mood === 'NEUTRAL').length
    const bad = logs.filter((log) => log.mood === 'BAD').length
    const notRecorded = logs.length - total

    return { total, good, neutral, bad, notRecorded }
  }, [logs])

  // Custom tooltip (Elder-First: Large text)
  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ payload: { date: string; fullDate: string; mood: DailyLogMood | null; moodScore: number | null; moodLabel: string; hasData: boolean } }> }) => {
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

      const moodColor = getMoodColor(data.mood)
      const emoji = data.mood === 'GOOD' ? '😊' : data.mood === 'NEUTRAL' ? '😐' : '😟'

      return (
        <div className="bg-white border-2 border-gray-300 rounded-lg shadow-lg p-4">
          <p className="text-lg font-semibold text-gray-800 mb-1">{data.fullDate}</p>
          <p className="text-2xl font-bold flex items-center gap-2" style={{ color: moodColor }}>
            {emoji} {data.moodLabel}
          </p>
        </div>
      )
    }
    return null
  }

  // Custom dot to show mood color
  const CustomDot = (props: { cx?: number; cy?: number; payload?: { mood: DailyLogMood | null; hasData: boolean } }) => {
    const { cx, cy, payload } = props
    if (!payload.hasData) return null

    const moodColor = getMoodColor(payload.mood)
    return (
      <circle
        cx={cx}
        cy={cy}
        r={8}
        fill={moodColor}
        stroke="white"
        strokeWidth={2}
      />
    )
  }

  // Check if there are concerning mood patterns
  const hasConcerningMoods = moodStats.bad >= 3 || (moodStats.bad / moodStats.total) > 0.3

  return (
    <div>
      {/* Title and Summary */}
      <div className="mb-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-2 flex items-center gap-2">
          😊 情緒趨勢
          {hasConcerningMoods && (
            <span className="text-base font-normal text-amber-600 bg-amber-100 px-3 py-1 rounded-full">
              ⚠️ 需關注
            </span>
          )}
        </h3>
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-green-500 rounded-full" />
            <span className="text-lg text-gray-700">😊 良好</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-amber-500 rounded-full" />
            <span className="text-lg text-gray-700">😐 普通</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-red-500 rounded-full" />
            <span className="text-lg text-gray-700">😟 不佳</span>
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
            domain={[0, 4]}
            ticks={[1, 2, 3]}
            tickFormatter={(value) => {
              if (value === 3) return '😊 良好'
              if (value === 2) return '😐 普通'
              if (value === 1) return '😟 不佳'
              return ''
            }}
          />
          <Tooltip content={<CustomTooltip />} />

          {/* Reference lines for mood levels */}
          <ReferenceLine
            y={2.5}
            stroke={CHART_CONSTANTS.COLORS.SUCCESS}
            strokeDasharray="3 3"
            strokeWidth={1}
            label={{
              value: '良好區間',
              position: 'right',
              fontSize: CHART_CONSTANTS.FONT_SIZE_SMALL,
              fill: CHART_CONSTANTS.COLORS.SUCCESS,
            }}
          />
          <ReferenceLine
            y={1.5}
            stroke={CHART_CONSTANTS.COLORS.WARNING}
            strokeDasharray="3 3"
            strokeWidth={1}
            label={{
              value: '注意區間',
              position: 'right',
              fontSize: CHART_CONSTANTS.FONT_SIZE_SMALL,
              fill: CHART_CONSTANTS.COLORS.WARNING,
            }}
          />

          {/* Mood trend line */}
          <Line
            type="monotone"
            dataKey="moodScore"
            stroke={CHART_CONSTANTS.COLORS.PRIMARY}
            strokeWidth={3}
            dot={<CustomDot />}
            activeDot={{ r: 10 }}
            connectNulls={false}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Mood Distribution Stats (Elder-First: Large text) */}
      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-green-50 rounded-lg p-4">
          <p className="text-base text-gray-600 mb-1">😊 良好</p>
          <p className="text-2xl font-bold text-green-700">{moodStats.good} 天</p>
          <p className="text-sm text-gray-500">
            {moodStats.total > 0 ? `${((moodStats.good / moodStats.total) * 100).toFixed(0)}%` : '0%'}
          </p>
        </div>
        <div className="bg-amber-50 rounded-lg p-4">
          <p className="text-base text-gray-600 mb-1">😐 普通</p>
          <p className="text-2xl font-bold text-amber-700">{moodStats.neutral} 天</p>
          <p className="text-sm text-gray-500">
            {moodStats.total > 0 ? `${((moodStats.neutral / moodStats.total) * 100).toFixed(0)}%` : '0%'}
          </p>
        </div>
        <div className="bg-red-50 rounded-lg p-4">
          <p className="text-base text-gray-600 mb-1">😟 不佳</p>
          <p className="text-2xl font-bold text-red-700">{moodStats.bad} 天</p>
          <p className="text-sm text-gray-500">
            {moodStats.total > 0 ? `${((moodStats.bad / moodStats.total) * 100).toFixed(0)}%` : '0%'}
          </p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-base text-gray-600 mb-1">未記錄</p>
          <p className="text-2xl font-bold text-gray-700">{moodStats.notRecorded} 天</p>
        </div>
      </div>

      {/* COPD-specific mental health guidance */}
      {hasConcerningMoods ? (
        <div className="mt-4 bg-amber-50 border-l-4 border-amber-600 rounded-r-lg p-4">
          <p className="text-lg font-bold text-amber-800">
            ⚠️ <strong>注意：情緒低落頻率偏高</strong>
          </p>
          <p className="text-base text-amber-700 mt-1">
            COPD 患者常伴隨焦慮和憂鬱症狀。建議：
          </p>
          <ul className="mt-2 space-y-1 text-base text-amber-700">
            <li>• 進行心理健康評估 (PHQ-9, GAD-7)</li>
            <li>• 考慮轉介心理諮商或精神科</li>
            <li>• 評估是否需要調整治療計畫</li>
            <li>• 加強社會支持和家庭關懷</li>
          </ul>
        </div>
      ) : (
        <div className="mt-4 bg-blue-50 border-l-4 border-blue-500 rounded-r-lg p-4">
          <p className="text-lg text-gray-700">
            💙 <strong>COPD 患者心理健康重要性：</strong>
          </p>
          <p className="text-base text-gray-600 mt-1">
            良好的情緒狀態有助於改善治療遵從度和生活品質。持續關注患者的心理健康，提供情緒支持。
          </p>
        </div>
      )}
    </div>
  )
}
