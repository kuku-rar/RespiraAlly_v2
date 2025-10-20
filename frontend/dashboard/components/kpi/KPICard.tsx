/**
 * KPI Card Component - Reusable KPI display card
 * Elder-First Design: 18px+ font, clear status colors, large touch targets
 */

'use client'

import { KPICardProps } from '@/lib/types/kpi'

export function KPICard({
  title,
  value,
  unit,
  status = 'neutral',
  icon,
  description,
}: KPICardProps) {
  // Determine status color and emoji
  const statusConfig = {
    good: {
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      textColor: 'text-green-700',
      valueColor: 'text-green-900',
      emoji: '✅',
    },
    warning: {
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      textColor: 'text-yellow-700',
      valueColor: 'text-yellow-900',
      emoji: '⚠️',
    },
    danger: {
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      textColor: 'text-red-700',
      valueColor: 'text-red-900',
      emoji: '🚨',
    },
    neutral: {
      bgColor: 'bg-gray-50',
      borderColor: 'border-gray-200',
      textColor: 'text-gray-700',
      valueColor: 'text-gray-900',
      emoji: '📊',
    },
  }

  const config = statusConfig[status]

  // Display value
  const displayValue = value !== undefined && value !== null ? value : '-'

  return (
    <div
      className={`${config.bgColor} ${config.borderColor} border-2 rounded-xl p-6 transition-all hover:shadow-lg`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h3 className={`text-lg font-semibold ${config.textColor}`}>
          {title}
        </h3>
        <span className="text-2xl">{icon || config.emoji}</span>
      </div>

      {/* Value */}
      <div className="flex items-baseline gap-2 mb-2">
        <span className={`text-4xl font-bold ${config.valueColor}`}>
          {displayValue}
        </span>
        {unit && (
          <span className={`text-xl font-medium ${config.textColor}`}>
            {unit}
          </span>
        )}
      </div>

      {/* Description */}
      {description && (
        <p className={`text-base ${config.textColor} mt-2`}>
          {description}
        </p>
      )}
    </div>
  )
}
