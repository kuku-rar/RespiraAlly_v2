/**
 * Alert Detail Modal Component
 * Displays detailed information about a specific alert
 */

'use client'

import type { Alert } from '@/lib/types/alert'
import {
  AlertTypeLabels,
  AlertSeverityLabels,
  AlertStatusLabels,
} from '@/lib/types/alert'

interface AlertDetailModalProps {
  alert: Alert | null
  isOpen: boolean
  onClose: () => void
}

export default function AlertDetailModal({ alert, isOpen, onClose }: AlertDetailModalProps) {
  if (!isOpen || !alert) return null

  // Format datetime
  const formatDateTime = (dateString: string | null | undefined): string => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleString('zh-TW', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  // Get severity color
  const getSeverityColor = () => {
    switch (alert.severity) {
      case 'CRITICAL':
        return 'text-red-600 bg-red-50'
      case 'HIGH':
        return 'text-orange-600 bg-orange-50'
      case 'MEDIUM':
        return 'text-yellow-600 bg-yellow-50'
      case 'LOW':
        return 'text-blue-600 bg-blue-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  // Get status color
  const getStatusColor = () => {
    switch (alert.status) {
      case 'ACTIVE':
        return 'text-red-600 bg-red-50'
      case 'ACKNOWLEDGED':
        return 'text-orange-600 bg-orange-50'
      case 'RESOLVED':
        return 'text-green-600 bg-green-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="px-8 py-6 border-b border-gray-200 bg-gray-50 rounded-t-2xl">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">警示詳情</h2>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors text-3xl font-light leading-none"
              >
                ×
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="px-8 py-6 space-y-6">
            {/* Alert Type and Severity */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-600 mb-2">
                  警示類型
                </label>
                <div className="text-lg font-semibold text-gray-900">
                  {AlertTypeLabels[alert.alert_type]}
                </div>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-600 mb-2">
                  嚴重程度
                </label>
                <div
                  className={`inline-flex px-4 py-2 rounded-lg font-semibold text-lg ${getSeverityColor()}`}
                >
                  {AlertSeverityLabels[alert.severity]}
                </div>
              </div>
            </div>

            {/* Status and ID */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-600 mb-2">狀態</label>
                <div
                  className={`inline-flex px-4 py-2 rounded-lg font-semibold text-lg ${getStatusColor()}`}
                >
                  {AlertStatusLabels[alert.status]}
                </div>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-600 mb-2">警示 ID</label>
                <div className="text-base text-gray-700 font-mono">{alert.alert_id}</div>
              </div>
            </div>

            {/* Timeline */}
            <div className="border-t border-gray-200 pt-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">時間軸</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-base text-gray-600">觸發時間：</span>
                  <span className="text-base text-gray-900 font-semibold">
                    {formatDateTime(alert.triggered_at)}
                  </span>
                </div>
                {alert.acknowledged_at && (
                  <div className="flex justify-between items-center">
                    <span className="text-base text-gray-600">確認時間：</span>
                    <span className="text-base text-gray-900">
                      {formatDateTime(alert.acknowledged_at)}
                    </span>
                  </div>
                )}
                {alert.resolved_at && (
                  <div className="flex justify-between items-center">
                    <span className="text-base text-gray-600">解決時間：</span>
                    <span className="text-base text-gray-900">
                      {formatDateTime(alert.resolved_at)}
                    </span>
                  </div>
                )}
                <div className="flex justify-between items-center">
                  <span className="text-base text-gray-600">建立時間：</span>
                  <span className="text-base text-gray-900">{formatDateTime(alert.created_at)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-base text-gray-600">更新時間：</span>
                  <span className="text-base text-gray-900">{formatDateTime(alert.updated_at)}</span>
                </div>
              </div>
            </div>

            {/* Clinical Indicators */}
            {alert.metadata.clinical_indicators && (
              <div className="border-t border-gray-200 pt-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">臨床指標</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {alert.metadata.clinical_indicators.cat_score !== undefined && (
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <div className="text-sm text-blue-600 font-semibold mb-1">CAT 分數</div>
                      <div className="text-2xl font-bold text-blue-900">
                        {alert.metadata.clinical_indicators.cat_score}
                      </div>
                    </div>
                  )}
                  {alert.metadata.clinical_indicators.mmrc_score !== undefined && (
                    <div className="bg-purple-50 p-4 rounded-lg">
                      <div className="text-sm text-purple-600 font-semibold mb-1">mMRC 分級</div>
                      <div className="text-2xl font-bold text-purple-900">
                        {alert.metadata.clinical_indicators.mmrc_score}
                      </div>
                    </div>
                  )}
                  {alert.metadata.clinical_indicators.gold_group && (
                    <div className="bg-yellow-50 p-4 rounded-lg">
                      <div className="text-sm text-yellow-600 font-semibold mb-1">GOLD 分級</div>
                      <div className="text-2xl font-bold text-yellow-900">
                        {alert.metadata.clinical_indicators.gold_group}
                      </div>
                    </div>
                  )}
                  {alert.metadata.clinical_indicators.exacerbation_count_12m !== undefined && (
                    <div className="bg-red-50 p-4 rounded-lg">
                      <div className="text-sm text-red-600 font-semibold mb-1">惡化次數</div>
                      <div className="text-2xl font-bold text-red-900">
                        {alert.metadata.clinical_indicators.exacerbation_count_12m} 次/年
                      </div>
                    </div>
                  )}
                  {alert.metadata.clinical_indicators.hospitalization_count_12m !== undefined && (
                    <div className="bg-orange-50 p-4 rounded-lg">
                      <div className="text-sm text-orange-600 font-semibold mb-1">住院次數</div>
                      <div className="text-2xl font-bold text-orange-900">
                        {alert.metadata.clinical_indicators.hospitalization_count_12m} 次/年
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Metadata */}
            <div className="border-t border-gray-200 pt-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">警示元數據</h3>
              <div className="bg-gray-50 p-4 rounded-lg">
                <pre className="text-sm text-gray-700 overflow-x-auto whitespace-pre-wrap">
                  {JSON.stringify(alert.metadata, null, 2)}
                </pre>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="px-8 py-6 border-t border-gray-200 bg-gray-50 rounded-b-2xl flex justify-end gap-4">
            <button
              onClick={onClose}
              className="px-6 py-3 text-base font-semibold text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              關閉
            </button>
            {/* Future: Add action buttons (Acknowledge, Resolve) */}
            {alert.status === 'ACTIVE' && (
              <button
                onClick={() => {
                  alert('此功能將於 Sprint 5 實作')
                }}
                className="px-6 py-3 text-base font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
              >
                確認警示
              </button>
            )}
          </div>
        </div>
      </div>
    </>
  )
}
