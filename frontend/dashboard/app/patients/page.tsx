/**
 * Patients List Page - Therapist Patient Management (Refactored)
 * Uses reusable components: PatientFilters, PatientTable, PatientPagination
 */

'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { patientsApi } from '@/lib/api/patients'
import { tokenManager } from '@/lib/api/auth'
import type { PatientResponse, PatientsQuery } from '@/lib/types/patient'

// Import reusable components
import PatientFilters from '@/components/patients/PatientFilters'
import PatientTable from '@/components/patients/PatientTable'
import PatientPagination from '@/components/patients/PatientPagination'

export default function PatientsPage() {
  const router = useRouter()

  // State management
  const [patients, setPatients] = useState<PatientResponse[]>([])
  const [total, setTotal] = useState(0)
  const [currentPage, setCurrentPage] = useState(0)
  const [pageSize] = useState(20)
  const [hasNext, setHasNext] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<PatientsQuery>({
    sort_by: 'name',
  })

  // Check authentication on mount
  useEffect(() => {
    const token = tokenManager.getAccessToken()
    if (!token) {
      router.push('/login')
      return
    }

    fetchPatients()
  }, [currentPage, filters, router])

  // Fetch patients from API
  const fetchPatients = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await patientsApi.getPatients({
        skip: currentPage * pageSize,
        limit: pageSize,
        ...filters,
      })

      setPatients(response.items)
      setTotal(response.total)
      setHasNext(response.has_next)
    } catch (err) {
      setError(err instanceof Error ? err.message : '載入失敗')
    } finally {
      setIsLoading(false)
    }
  }

  // Event handlers
  const handleFilterChange = (newFilters: PatientsQuery) => {
    setFilters(newFilters)
    setCurrentPage(0) // Reset to first page when filters change
  }

  const handlePatientClick = (patientId: string) => {
    router.push(`/patients/${patientId}`)
  }

  const handlePrevPage = () => {
    if (currentPage > 0) {
      setCurrentPage(currentPage - 1)
    }
  }

  const handleNextPage = () => {
    if (hasNext) {
      setCurrentPage(currentPage + 1)
    }
  }

  const handleBackToDashboard = () => {
    router.push('/dashboard')
  }

  const handleRefresh = () => {
    fetchPatients()
  }

  // Loading state (initial load)
  if (isLoading && patients.length === 0 && !error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="text-6xl mb-4">⏳</div>
          <div className="text-2xl font-medium text-gray-700">載入中...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <button
                onClick={handleBackToDashboard}
                className="text-blue-600 hover:text-blue-800 text-lg mb-2 hover:underline"
              >
                ← 返回主頁
              </button>
              <h1 className="text-3xl font-bold text-gray-900">
                病患管理
              </h1>
              <p className="text-lg text-gray-600 mt-1">
                共 {total} 位病患
              </p>
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={handleRefresh}
                disabled={isLoading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white text-lg font-medium px-6 py-3 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
                style={{ minHeight: '52px' }}
              >
                {isLoading ? '載入中...' : '🔄 重新整理'}
              </button>

              <button
                onClick={() => router.push('/patients/new')}
                className="bg-green-600 hover:bg-green-700 text-white text-lg font-semibold px-6 py-3 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-green-500"
                style={{ minHeight: '52px' }}
              >
                + 新增病患
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters Component */}
        <PatientFilters
          onFilterChange={handleFilterChange}
          isLoading={isLoading}
        />

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4 mb-6" role="alert">
            <p className="text-lg text-red-800 font-medium">
              ⚠️ {error}
            </p>
            <button
              onClick={handleRefresh}
              className="mt-2 text-red-600 hover:text-red-800 text-base font-medium hover:underline"
            >
              點擊重試
            </button>
          </div>
        )}

        {/* Patients Table Component */}
        <PatientTable
          patients={patients}
          isLoading={isLoading && patients.length > 0}
          onPatientClick={handlePatientClick}
        />

        {/* Pagination Component */}
        <PatientPagination
          total={total}
          currentPage={currentPage}
          pageSize={pageSize}
          hasNext={hasNext}
          onPrevPage={handlePrevPage}
          onNextPage={handleNextPage}
          isLoading={isLoading}
        />

        {/* Mock Mode Indicator */}
        {process.env.NEXT_PUBLIC_MOCK_MODE === 'true' && (
          <div className="mt-6 bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4">
            <p className="text-base text-yellow-800 text-center">
              🧪 <strong>Mock 模式</strong> - 顯示測試數據（共 8 筆），篩選功能僅支援「排序」
            </p>
            <p className="text-sm text-yellow-700 text-center mt-1">
              關閉 Mock 模式後將支援完整篩選功能（風險等級、依從率、最後活動日期）
            </p>
          </div>
        )}
      </main>
    </div>
  )
}
