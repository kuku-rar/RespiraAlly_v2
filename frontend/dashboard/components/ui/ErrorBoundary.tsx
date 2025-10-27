/**
 * ErrorBoundary Component
 * React Error Boundary to catch and handle component crashes gracefully
 *
 * Task 5.1.4 - Sprint 3
 */

'use client'

import { Component, ErrorInfo, ReactNode } from 'react'
import { ErrorAlert } from './ErrorAlert'

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
    }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught an error:', error, errorInfo)
    }

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }

    // In production, you might want to log to an error reporting service
    // Example: Sentry.captureException(error, { extra: errorInfo })
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
    })
  }

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback
      }

      // Default error UI
      return (
        <ErrorAlert
          title="應用程式發生錯誤"
          message={
            this.state.error?.message ||
            '抱歉，應用程式遇到了問題。請嘗試重新載入頁面。'
          }
          onRetry={this.handleReset}
          fullScreen
        />
      )
    }

    return this.props.children
  }
}

/**
 * PageErrorBoundary - Error boundary specifically for page-level errors
 */
interface PageErrorBoundaryProps {
  children: ReactNode
  pageName?: string
}

export function PageErrorBoundary({
  children,
  pageName = '此頁面',
}: PageErrorBoundaryProps) {
  return (
    <ErrorBoundary
      fallback={
        <div className="container mx-auto py-8">
          <ErrorAlert
            title={`${pageName}載入失敗`}
            message="頁面元件發生錯誤，請嘗試重新載入頁面或聯絡系統管理員。"
            onRetry={() => window.location.reload()}
          />
        </div>
      }
      onError={(error, errorInfo) => {
        // Log page-level errors
        console.error(`Page Error in ${pageName}:`, error, errorInfo)
      }}
    >
      {children}
    </ErrorBoundary>
  )
}

/**
 * ComponentErrorBoundary - Error boundary for individual components
 */
interface ComponentErrorBoundaryProps {
  children: ReactNode
  componentName: string
  fallbackMessage?: string
}

export function ComponentErrorBoundary({
  children,
  componentName,
  fallbackMessage,
}: ComponentErrorBoundaryProps) {
  return (
    <ErrorBoundary
      fallback={
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <div className="flex items-center gap-2">
            <span className="text-red-600">⚠️</span>
            <div>
              <p className="font-medium text-red-900">{componentName} 載入失敗</p>
              <p className="text-sm text-red-700">
                {fallbackMessage || '此元件暫時無法使用，請稍後再試。'}
              </p>
            </div>
          </div>
        </div>
      }
      onError={(error) => {
        console.error(`Component Error in ${componentName}:`, error)
      }}
    >
      {children}
    </ErrorBoundary>
  )
}
