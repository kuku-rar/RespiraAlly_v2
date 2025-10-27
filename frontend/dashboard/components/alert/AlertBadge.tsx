/**
 * Alert Badge Component
 * Displays active alert count with auto-refresh
 * Sprint 4 Alert System MVP - Phase A3
 */

'use client'

import { useState, useEffect } from 'react'
import { getActiveAlertCount } from '@/lib/api/alerts'

interface AlertBadgeProps {
  patientId: string
  onClick?: () => void
  refreshInterval?: number // in milliseconds, default 60000 (60 seconds)
}

export default function AlertBadge({
  patientId,
  onClick,
  refreshInterval = 60000,
}: AlertBadgeProps) {
  const [activeCount, setActiveCount] = useState<number>(0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load active alert count
  const loadActiveCount = async () => {
    try {
      const count = await getActiveAlertCount(patientId)
      setActiveCount(count)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load alert count')
      console.error('Error loading active alert count:', err)
    } finally {
      setIsLoading(false)
    }
  }

  // Initial load
  useEffect(() => {
    loadActiveCount()
  }, [patientId])

  // Auto-refresh interval
  useEffect(() => {
    const interval = setInterval(() => {
      loadActiveCount()
    }, refreshInterval)

    return () => clearInterval(interval)
  }, [patientId, refreshInterval])

  // Handle click
  const handleClick = () => {
    if (onClick) {
      onClick()
    }
  }

  // Don't show if loading or error or no alerts
  if (isLoading || error) {
    return null
  }

  // Don't show badge if no active alerts
  if (activeCount === 0) {
    return null
  }

  return (
    <button
      onClick={handleClick}
      className="relative inline-flex items-center gap-2 px-4 py-2 bg-red-50 hover:bg-red-100 border-2 border-red-200 rounded-lg transition-colors cursor-pointer group"
      title={`${activeCount} 個活動警示`}
    >
      {/* Bell Icon */}
      <svg
        className="w-6 h-6 text-red-600 group-hover:animate-pulse"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
        />
      </svg>

      {/* Alert Count Badge */}
      <div className="flex items-center gap-1">
        <span className="text-lg font-bold text-red-600">{activeCount}</span>
        <span className="text-sm font-semibold text-red-600">個警示</span>
      </div>

      {/* Pulse Animation Dot */}
      <span className="absolute -top-1 -right-1 flex h-3 w-3">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
        <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
      </span>
    </button>
  )
}
