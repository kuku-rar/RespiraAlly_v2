/**
 * ProgressBar Component - Survey Progress Indicator
 *
 * Sprint 3 Task 5.3.2 - Week 6 Day 2
 */

interface ProgressBarProps {
  current: number // Current step (0-indexed)
  total: number // Total steps
  className?: string
}

export function ProgressBar({ current, total, className = '' }: ProgressBarProps) {
  const percentage = ((current + 1) / total) * 100

  return (
    <div className={`w-full ${className}`}>
      {/* Progress Text */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-lg font-semibold text-gray-900">
          問題 {current + 1} / {total}
        </span>
        <span className="text-base font-medium text-blue-600">
          {Math.round(percentage)}%
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        <div
          className="bg-blue-600 h-full rounded-full transition-all duration-500 ease-out"
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={current + 1}
          aria-valuemin={1}
          aria-valuemax={total}
        />
      </div>

      {/* Step Indicators (Dots) */}
      <div className="flex items-center justify-between mt-3">
        {Array.from({ length: total }, (_, i) => (
          <div
            key={i}
            className={`
              w-3 h-3 rounded-full transition-all
              ${
                i <= current
                  ? 'bg-blue-600 scale-125'
                  : 'bg-gray-300'
              }
            `}
            aria-label={`步驟 ${i + 1}`}
          />
        ))}
      </div>
    </div>
  )
}
