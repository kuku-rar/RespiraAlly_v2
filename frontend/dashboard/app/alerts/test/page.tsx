/**
 * Alert System Test Page
 * Sprint 4 Alert System MVP - Phase A4
 *
 * Purpose: Integration testing for AlertList and AlertDetailModal
 * Test Coverage:
 * - Complete flow: List → Click → Modal → Close
 * - Filter combinations (Severity, Status, Alert Type)
 * - Pagination
 * - Mock mode and real API mode
 * - Error handling scenarios
 */

'use client'

import { useState } from 'react'
import { AlertList, AlertDetailModal } from '@/components/alert'
import type { Alert } from '@/lib/types/alert'

export default function AlertTestPage() {
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  // Test with different patient IDs
  const [currentPatientId, setCurrentPatientId] = useState('00000000-0000-0000-0000-000000000001')

  // Handle alert click - open modal
  const handleAlertClick = (alert: Alert) => {
    setSelectedAlert(alert)
    setIsModalOpen(true)
  }

  // Handle modal close
  const handleModalClose = () => {
    setIsModalOpen(false)
    // Don't clear selectedAlert immediately to allow smooth transition
    setTimeout(() => {
      setSelectedAlert(null)
    }, 300)
  }

  // Test patient IDs
  const testPatients = [
    { id: '00000000-0000-0000-0000-000000000001', name: '病患 1 (有警示)' },
    { id: '00000000-0000-0000-0000-000000000002', name: '病患 2 (有警示)' },
    { id: '00000000-0000-0000-0000-000000000003', name: '病患 3 (有警示)' },
    { id: '00000000-0000-0000-0000-000000000999', name: '病患 999 (無警示)' },
  ]

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <h1 className="text-4xl font-bold text-gray-900">
              警示系統測試頁面
            </h1>
            <span className="px-4 py-2 bg-blue-100 text-blue-800 text-sm font-semibold rounded-lg">
              Sprint 4 MVP - Phase A4
            </span>
          </div>
          <p className="text-lg text-gray-600">
            測試 AlertList 與 AlertDetailModal 的完整功能流程
          </p>
        </div>

        {/* Test Controls */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">測試控制</h2>

          {/* Patient Selection */}
          <div>
            <label className="block text-base font-semibold text-gray-700 mb-2">
              選擇測試病患
            </label>
            <div className="flex flex-wrap gap-2">
              {testPatients.map((patient) => (
                <button
                  key={patient.id}
                  onClick={() => setCurrentPatientId(patient.id)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    currentPatientId === patient.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {patient.name}
                </button>
              ))}
            </div>
            <p className="mt-2 text-sm text-gray-500">
              當前病患 ID: <code className="bg-gray-100 px-2 py-1 rounded">{currentPatientId}</code>
            </p>
          </div>
        </div>

        {/* Test Checklist */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">測試檢查清單</h2>
          <div className="space-y-2">
            <div className="flex items-start gap-3">
              <input type="checkbox" className="mt-1 w-5 h-5" id="test1" />
              <label htmlFor="test1" className="text-base text-gray-700">
                <strong>基本顯示：</strong>警示列表正確顯示，包含類型、嚴重度、狀態、時間、臨床指標
              </label>
            </div>
            <div className="flex items-start gap-3">
              <input type="checkbox" className="mt-1 w-5 h-5" id="test2" />
              <label htmlFor="test2" className="text-base text-gray-700">
                <strong>篩選功能：</strong>嚴重程度、狀態、警示類型篩選器正常運作
              </label>
            </div>
            <div className="flex items-start gap-3">
              <input type="checkbox" className="mt-1 w-5 h-5" id="test3" />
              <label htmlFor="test3" className="text-base text-gray-700">
                <strong>分頁功能：</strong>上一頁/下一頁按鈕正常，頁數顯示正確
              </label>
            </div>
            <div className="flex items-start gap-3">
              <input type="checkbox" className="mt-1 w-5 h-5" id="test4" />
              <label htmlFor="test4" className="text-base text-gray-700">
                <strong>點擊警示：</strong>點擊警示行打開詳細資訊彈窗
              </label>
            </div>
            <div className="flex items-start gap-3">
              <input type="checkbox" className="mt-1 w-5 h-5" id="test5" />
              <label htmlFor="test5" className="text-base text-gray-700">
                <strong>彈窗內容：</strong>警示詳情、時間軸、臨床指標、元數據正確顯示
              </label>
            </div>
            <div className="flex items-start gap-3">
              <input type="checkbox" className="mt-1 w-5 h-5" id="test6" />
              <label htmlFor="test6" className="text-base text-gray-700">
                <strong>關閉彈窗：</strong>點擊關閉按鈕或背景關閉彈窗
              </label>
            </div>
            <div className="flex items-start gap-3">
              <input type="checkbox" className="mt-1 w-5 h-5" id="test7" />
              <label htmlFor="test7" className="text-base text-gray-700">
                <strong>空狀態：</strong>無警示時顯示友善的空狀態提示
              </label>
            </div>
            <div className="flex items-start gap-3">
              <input type="checkbox" className="mt-1 w-5 h-5" id="test8" />
              <label htmlFor="test8" className="text-base text-gray-700">
                <strong>顏色編碼：</strong>嚴重度與狀態的顏色正確且易於區分
              </label>
            </div>
            <div className="flex items-start gap-3">
              <input type="checkbox" className="mt-1 w-5 h-5" id="test9" />
              <label htmlFor="test9" className="text-base text-gray-700">
                <strong>長者友善：</strong>字體大小適中，按鈕易於點擊，顏色對比清晰
              </label>
            </div>
            <div className="flex items-start gap-3">
              <input type="checkbox" className="mt-1 w-5 h-5" id="test10" />
              <label htmlFor="test10" className="text-base text-gray-700">
                <strong>Mock 模式：</strong>在 Mock 模式下正常運作（顯示測試資料）
              </label>
            </div>
          </div>
        </div>

        {/* Alert List Component */}
        <div className="mb-8">
          <div className="mb-4">
            <h2 className="text-2xl font-bold text-gray-900">警示列表</h2>
            <p className="text-base text-gray-600 mt-1">
              點擊任一警示以查看詳細資訊
            </p>
          </div>

          <AlertList
            patientId={currentPatientId}
            onAlertClick={handleAlertClick}
          />
        </div>

        {/* Integration Notes */}
        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6">
          <h3 className="text-xl font-bold text-blue-900 mb-2">
            ℹ️ 整合說明
          </h3>
          <div className="text-base text-blue-800 space-y-2">
            <p>
              <strong>AlertList 組件：</strong>
              <code className="bg-blue-100 px-2 py-1 rounded ml-2">
                &lt;AlertList patientId=&#123;patientId&#125; onAlertClick=&#123;handleClick&#125; /&gt;
              </code>
            </p>
            <p>
              <strong>AlertDetailModal 組件：</strong>
              <code className="bg-blue-100 px-2 py-1 rounded ml-2">
                &lt;AlertDetailModal alert=&#123;alert&#125; isOpen=&#123;true&#125; onClose=&#123;handleClose&#125; /&gt;
              </code>
            </p>
            <p>
              <strong>AlertBadge 組件：</strong>
              <code className="bg-blue-100 px-2 py-1 rounded ml-2">
                &lt;AlertBadge patientId=&#123;patientId&#125; onClick=&#123;handleClick&#125; /&gt;
              </code>
            </p>
            <p className="mt-4">
              <strong>API 端點：</strong>
            </p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li><code>/api/v1/alerts/patients/&#123;patient_id&#125;/</code> - 取得病患警示列表</li>
              <li><code>/api/v1/alerts/patients/&#123;patient_id&#125;/active/count</code> - 取得活動警示數量</li>
              <li><code>/api/v1/alerts/&#123;alert_id&#125;</code> - 取得單一警示詳情</li>
            </ul>
          </div>
        </div>

        {/* Alert Detail Modal */}
        <AlertDetailModal
          alert={selectedAlert}
          isOpen={isModalOpen}
          onClose={handleModalClose}
        />
      </div>
    </div>
  )
}
