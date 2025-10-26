/**
 * Alert List Component - Display patient alerts with filters
 * Sprint 4 Alert System MVP UI
 */

'use client'

import { useState, useEffect } from 'react'
import type {
  Alert,
  AlertType,
  AlertSeverity,
  AlertStatus,
  AlertQueryParams,
} from '@/lib/types/alert'
import {
  AlertTypeLabels,
  AlertSeverityLabels,
  AlertStatusLabels,
  AlertSeverityColors,
  AlertStatusColors,
} from '@/lib/types/alert'
import { getPatientAlerts } from '@/lib/api/alerts'

interface AlertListProps {
  patientId: string
  onAlertClick?: (alert: Alert) => void
}

export default function AlertList({ patientId, onAlertClick }: AlertListProps) {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)
  const [currentPage, setCurrentPage] = useState(0)
  const pageSize = 20

  // Filters
  const [filterSeverity, setFilterSeverity] = useState<AlertSeverity | ''>('')
  const [filterStatus, setFilterStatus] = useState<AlertStatus | ''>('')
  const [filterAlertType, setFilterAlertType] = useState<AlertType | ''>('')

  // Load alerts
  const loadAlerts = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const params: AlertQueryParams = {
        page: currentPage,
        page_size: pageSize,
      }

      if (filterSeverity) params.severity = filterSeverity
      if (filterStatus) params.status = filterStatus
      if (filterAlertType) params.alert_type = filterAlertType

      const response = await getPatientAlerts(patientId, params)
      setAlerts(response.alerts)
      setTotal(response.total)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load alerts')
      console.error('Error loading alerts:', err)
    } finally {
      setIsLoading(false)
    }
  }

  // Load on mount and when filters/page change
  useEffect(() => {
    loadAlerts()
  }, [patientId, currentPage, filterSeverity, filterStatus, filterAlertType])

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(0)
  }, [filterSeverity, filterStatus, filterAlertType])

  // Get Tailwind color class for severity
  const getSeverityColorClass = (severity: AlertSeverity): string => {
    const colorMap: Record<AlertSeverity, string> = {
      CRITICAL: 'bg-red-100 text-red-800 border-red-300',
      HIGH: 'bg-orange-100 text-orange-800 border-orange-300',
      MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      LOW: 'bg-blue-100 text-blue-800 border-blue-300',
    }
    return colorMap[severity] || 'bg-gray-100 text-gray-800 border-gray-300'
  }

  // Get Tailwind color class for status
  const getStatusColorClass = (status: AlertStatus): string => {
    const colorMap: Record<AlertStatus, string> = {
      ACTIVE: 'bg-red-100 text-red-800 border-red-300',
      ACKNOWLEDGED: 'bg-orange-100 text-orange-800 border-orange-300',
      RESOLVED: 'bg-green-100 text-green-800 border-green-300',
    }
    return colorMap[status] || 'bg-gray-100 text-gray-800 border-gray-300'
  }

  // Format datetime
  const formatDateTime = (dateString: string): string => {
    const date = new Date(dateString)
    return date.toLocaleString('zh-TW', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  // Pagination
  const totalPages = Math.ceil(total / pageSize)
  const canGoPrevious = currentPage > 0
  const canGoNext = currentPage < totalPages - 1

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        <div className="text-center text-xl text-gray-500">載入中...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-red-200 p-8">
        <div className="text-center text-xl text-red-600">❌ {error}</div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Filters */}
      <div className="p-6 border-b border-gray-200 bg-gray-50">
        <div className="flex flex-wrap gap-4">
          {/* Severity Filter */}
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-semibold text-gray-700 mb-2">嚴重程度</label>
            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value as AlertSeverity | '')}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-base focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">全部</option>
              <option value="CRITICAL">嚴重</option>
              <option value="HIGH">高</option>
              <option value="MEDIUM">中</option>
              <option value="LOW">低</option>
            </select>
          </div>

          {/* Status Filter */}
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-semibold text-gray-700 mb-2">狀態</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value as AlertStatus | '')}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-base focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">全部</option>
              <option value="ACTIVE">活動中</option>
              <option value="ACKNOWLEDGED">已確認</option>
              <option value="RESOLVED">已解決</option>
            </select>
          </div>

          {/* Alert Type Filter */}
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-semibold text-gray-700 mb-2">警示類型</label>
            <select
              value={filterAlertType}
              onChange={(e) => setFilterAlertType(e.target.value as AlertType | '')}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-base focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">全部</option>
              <option value="GOLD_GROUP_E">GOLD Group E</option>
              <option value="HIGH_CAT_SCORE">高症狀負擔</option>
              <option value="FREQUENT_EXACERBATIONS">頻繁惡化</option>
            </select>
          </div>
        </div>
      </div>

      {/* Alert List */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-4 text-left text-lg font-semibold text-gray-900">
                警示類型
              </th>
              <th className="px-6 py-4 text-left text-lg font-semibold text-gray-900">
                嚴重程度
              </th>
              <th className="px-6 py-4 text-left text-lg font-semibold text-gray-900">狀態</th>
              <th className="px-6 py-4 text-left text-lg font-semibold text-gray-900">
                觸發時間
              </th>
              <th className="px-6 py-4 text-left text-lg font-semibold text-gray-900">
                臨床指標
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {alerts.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center">
                  <div className="text-6xl mb-4">🔔</div>
                  <div className="text-xl text-gray-500 font-medium mb-2">目前沒有警示</div>
                  <div className="text-lg text-gray-400">
                    {filterSeverity || filterStatus || filterAlertType
                      ? '請調整篩選條件'
                      : '病患狀況良好'}
                  </div>
                </td>
              </tr>
            ) : (
              alerts.map((alert) => (
                <tr
                  key={alert.alert_id}
                  onClick={() => onAlertClick?.(alert)}
                  className="hover:bg-gray-50 cursor-pointer transition-colors text-base"
                >
                  {/* Alert Type */}
                  <td className="px-6 py-4">
                    <div className="font-semibold text-gray-900">
                      {AlertTypeLabels[alert.alert_type]}
                    </div>
                  </td>

                  {/* Severity */}
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full border ${getSeverityColorClass(alert.severity)}`}
                    >
                      {AlertSeverityLabels[alert.severity]}
                    </span>
                  </td>

                  {/* Status */}
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full border ${getStatusColorClass(alert.status)}`}
                    >
                      {AlertStatusLabels[alert.status]}
                    </span>
                  </td>

                  {/* Triggered At */}
                  <td className="px-6 py-4 text-gray-700">{formatDateTime(alert.triggered_at)}</td>

                  {/* Clinical Indicators */}
                  <td className="px-6 py-4">
                    {alert.metadata.clinical_indicators && (
                      <div className="text-sm text-gray-600 space-y-1">
                        {alert.metadata.clinical_indicators.cat_score && (
                          <div>CAT: {alert.metadata.clinical_indicators.cat_score}</div>
                        )}
                        {alert.metadata.clinical_indicators.mmrc_score !== undefined && (
                          <div>mMRC: {alert.metadata.clinical_indicators.mmrc_score}</div>
                        )}
                        {alert.metadata.clinical_indicators.gold_group && (
                          <div>GOLD: {alert.metadata.clinical_indicators.gold_group}</div>
                        )}
                        {alert.metadata.clinical_indicators.exacerbation_count_12m && (
                          <div>惡化: {alert.metadata.clinical_indicators.exacerbation_count_12m}次</div>
                        )}
                      </div>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="text-base text-gray-700">
              顯示第 {currentPage * pageSize + 1} - {Math.min((currentPage + 1) * pageSize, total)}{' '}
              筆，共 {total} 筆警示
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage((prev) => Math.max(0, prev - 1))}
                disabled={!canGoPrevious}
                className={`px-4 py-2 text-base font-medium rounded-lg border ${
                  canGoPrevious
                    ? 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                    : 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed'
                }`}
              >
                上一頁
              </button>
              <span className="px-4 py-2 text-base text-gray-700">
                第 {currentPage + 1} / {totalPages} 頁
              </span>
              <button
                onClick={() => setCurrentPage((prev) => Math.min(totalPages - 1, prev + 1))}
                disabled={!canGoNext}
                className={`px-4 py-2 text-base font-medium rounded-lg border ${
                  canGoNext
                    ? 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                    : 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed'
                }`}
              >
                下一頁
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
