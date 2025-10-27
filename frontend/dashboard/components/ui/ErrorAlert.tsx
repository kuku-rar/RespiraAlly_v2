/**
 * ErrorAlert Component
 * Reusable error display with retry functionality
 *
 * Task 5.1.4 - Sprint 3
 */

interface ErrorAlertProps {
  title?: string
  message: string
  onRetry?: () => void
  fullScreen?: boolean
  className?: string
  variant?: 'error' | 'warning' | 'info'
}

const variantStyles = {
  error: {
    container: 'border-red-200 bg-red-50',
    title: 'text-red-900',
    message: 'text-red-700',
    button: 'bg-red-600 hover:bg-red-700',
    icon: '❌',
  },
  warning: {
    container: 'border-yellow-200 bg-yellow-50',
    title: 'text-yellow-900',
    message: 'text-yellow-700',
    button: 'bg-yellow-600 hover:bg-yellow-700',
    icon: '⚠️',
  },
  info: {
    container: 'border-blue-200 bg-blue-50',
    title: 'text-blue-900',
    message: 'text-blue-700',
    button: 'bg-blue-600 hover:bg-blue-700',
    icon: 'ℹ️',
  },
}

export function ErrorAlert({
  title = '發生錯誤',
  message,
  onRetry,
  fullScreen = false,
  className = '',
  variant = 'error',
}: ErrorAlertProps) {
  const styles = variantStyles[variant]

  const content = (
    <div className={`rounded-lg border p-6 ${styles.container} ${className}`}>
      <div className="flex items-start gap-3">
        <span className="text-2xl" role="img" aria-label={variant}>
          {styles.icon}
        </span>
        <div className="flex-1">
          <h2 className={`text-xl font-semibold mb-2 ${styles.title}`}>
            {title}
          </h2>
          <p className={styles.message}>{message}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className={`mt-4 px-4 py-2 text-white rounded-lg transition-colors ${styles.button}`}
            >
              重試
            </button>
          )}
        </div>
      </div>
    </div>
  )

  if (fullScreen) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 p-4">
        <div className="max-w-2xl w-full">{content}</div>
      </div>
    )
  }

  return content
}

/**
 * ErrorBox - Compact inline error display
 */
interface ErrorBoxProps {
  message: string
  className?: string
}

export function ErrorBox({ message, className = '' }: ErrorBoxProps) {
  return (
    <div
      className={`rounded-md border border-red-300 bg-red-50 p-3 ${className}`}
      role="alert"
    >
      <div className="flex items-center gap-2">
        <span className="text-red-600">⚠️</span>
        <p className="text-sm text-red-700">{message}</p>
      </div>
    </div>
  )
}

/**
 * EmptyState - Display when no data is available
 */
interface EmptyStateProps {
  icon?: string
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
  className?: string
}

export function EmptyState({
  icon = '📭',
  title,
  description,
  action,
  className = '',
}: EmptyStateProps) {
  return (
    <div className={`text-center py-12 ${className}`}>
      <span className="text-6xl mb-4 block" role="img">
        {icon}
      </span>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
      {description && <p className="text-gray-600 mb-4">{description}</p>}
      {action && (
        <button
          onClick={action.onClick}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          {action.label}
        </button>
      )}
    </div>
  )
}
