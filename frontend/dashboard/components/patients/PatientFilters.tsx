/**
 * Patient Filters Component - Advanced filtering for patient list
 * Elder-First Design: Large inputs, clear labels
 */

import { useState } from 'react'
import type { PatientsQuery } from '@/lib/types/patient'
import { RiskLevel } from '@/lib/types/patient'

interface PatientFiltersProps {
  onFilterChange: (filters: PatientsQuery) => void
  isLoading?: boolean
}

export default function PatientFilters({ onFilterChange, isLoading = false }: PatientFiltersProps) {
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState<PatientsQuery>({
    risk_bucket: undefined,
    adherence_rate_lte: undefined,
    last_active_gte: undefined,
    sort_by: 'name',
  })

  const handleFilterChange = (key: keyof PatientsQuery, value: string | number | undefined) => {
    const newFilters = {
      ...filters,
      [key]: value === '' ? undefined : value,
    }
    setFilters(newFilters)
  }

  const handleApplyFilters = () => {
    onFilterChange(filters)
  }

  const handleResetFilters = () => {
    const resetFilters: PatientsQuery = {
      risk_bucket: undefined,
      adherence_rate_lte: undefined,
      last_active_gte: undefined,
      sort_by: 'name',
    }
    setFilters(resetFilters)
    onFilterChange(resetFilters)
  }

  const hasActiveFilters =
    filters.risk_bucket ||
    filters.adherence_rate_lte !== undefined ||
    filters.last_active_gte

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-4">
          <h3 className="text-xl font-semibold text-gray-900">
            篩選與排序
          </h3>
          {hasActiveFilters && (
            <span className="bg-blue-100 text-blue-800 text-base font-medium px-3 py-1 rounded-full">
              已套用篩選
            </span>
          )}
        </div>

        <button
          onClick={() => setShowFilters(!showFilters)}
          className="text-blue-600 hover:text-blue-800 text-lg font-medium"
        >
          {showFilters ? '收起篩選 ▲' : '展開篩選 ▼'}
        </button>
      </div>

      {/* Quick Sort */}
      <div className="flex items-center space-x-4 mb-4">
        <label className="text-lg font-medium text-gray-700">
          排序：
        </label>
        <select
          value={filters.sort_by}
          onChange={(e) => {
            handleFilterChange('sort_by', e.target.value)
            onFilterChange({ ...filters, sort_by: e.target.value as PatientsQuery['sort_by'] })
          }}
          className="px-4 py-2 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          style={{ minHeight: '48px' }}
        >
          <option value="name">姓名（A-Z）</option>
          <option value="age">年齡（高→低）</option>
          <option value="risk_level">風險等級（高→低）</option>
          <option value="last_active">最後活動（新→舊）</option>
          <option value="adherence_rate">依從率（低→高）</option>
        </select>
      </div>

      {/* Advanced Filters */}
      {showFilters && (
        <div className="pt-4 border-t border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            {/* Risk Level Filter */}
            <div>
              <label className="block text-lg font-medium text-gray-700 mb-2">
                風險等級
              </label>
              <select
                value={filters.risk_bucket || ''}
                onChange={(e) => handleFilterChange('risk_bucket', e.target.value)}
                className="w-full px-4 py-2 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                style={{ minHeight: '48px' }}
              >
                <option value="">全部</option>
                <option value={RiskLevel.LOW}>低風險</option>
                <option value={RiskLevel.MEDIUM}>中風險</option>
                <option value={RiskLevel.HIGH}>高風險</option>
                <option value={RiskLevel.CRITICAL}>緊急</option>
              </select>
            </div>

            {/* Adherence Rate Filter */}
            <div>
              <label className="block text-lg font-medium text-gray-700 mb-2">
                依從率 ≤
              </label>
              <input
                type="number"
                min="0"
                max="100"
                value={filters.adherence_rate_lte || ''}
                onChange={(e) => handleFilterChange('adherence_rate_lte', e.target.value ? parseInt(e.target.value) : undefined)}
                placeholder="例如：70"
                className="w-full px-4 py-2 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                style={{ minHeight: '48px' }}
              />
              <p className="text-sm text-gray-500 mt-1">
                顯示依從率小於等於此值的病患
              </p>
            </div>

            {/* Last Active Filter */}
            <div>
              <label className="block text-lg font-medium text-gray-700 mb-2">
                最後活動 ≥
              </label>
              <input
                type="date"
                value={filters.last_active_gte || ''}
                onChange={(e) => handleFilterChange('last_active_gte', e.target.value)}
                className="w-full px-4 py-2 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                style={{ minHeight: '48px' }}
              />
              <p className="text-sm text-gray-500 mt-1">
                顯示此日期後有活動的病患
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-4">
            <button
              onClick={handleApplyFilters}
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white text-lg font-semibold px-8 py-3 rounded-lg transition-colors"
              style={{ minHeight: '52px' }}
            >
              {isLoading ? '套用中...' : '套用篩選'}
            </button>

            <button
              onClick={handleResetFilters}
              disabled={isLoading}
              className="bg-gray-200 hover:bg-gray-300 disabled:bg-gray-100 text-gray-800 text-lg font-medium px-8 py-3 rounded-lg transition-colors"
              style={{ minHeight: '52px' }}
            >
              重置篩選
            </button>

            {hasActiveFilters && (
              <span className="text-base text-gray-600">
                （篩選條件已變更，點擊「套用篩選」以生效）
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
