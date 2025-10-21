/**
 * Patient Pagination Component - Reusable pagination controls
 * Elder-First Design: Large buttons, clear page info
 */

interface PatientPaginationProps {
  total: number
  currentPage: number // 0-indexed
  pageSize: number
  hasNext: boolean
  onPrevPage: () => void
  onNextPage: () => void
  isLoading?: boolean
}

export default function PatientPagination({
  total,
  currentPage,
  pageSize,
  hasNext,
  onPrevPage,
  onNextPage,
  isLoading = false,
}: PatientPaginationProps) {
  if (total === 0) {
    return null
  }

  const startIndex = currentPage * pageSize + 1
  const endIndex = Math.min((currentPage + 1) * pageSize, total)
  const totalPages = Math.ceil(total / pageSize)

  return (
    <div className="bg-gray-50 px-6 py-4 border-t border-gray-200 rounded-b-xl">
      <div className="flex flex-col sm:flex-row items-center justify-between space-y-4 sm:space-y-0">
        {/* Page Info */}
        <div className="text-lg text-gray-700">
          <span className="font-medium">
            顯示 {startIndex} - {endIndex} 筆
          </span>
          <span className="text-gray-500 mx-2">，</span>
          <span className="font-medium">共 {total} 筆</span>
          <span className="text-gray-500 mx-2">|</span>
          <span className="text-gray-600">
            第 {currentPage + 1} / {totalPages} 頁
          </span>
        </div>

        {/* Navigation Buttons */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onPrevPage}
            disabled={currentPage === 0 || isLoading}
            className="bg-white hover:bg-gray-100 disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed text-gray-700 text-lg font-medium px-6 py-3 rounded-lg border-2 border-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            style={{ minHeight: '52px', minWidth: '120px' }}
          >
            ← 上一頁
          </button>

          <button
            onClick={onNextPage}
            disabled={!hasNext || isLoading}
            className="bg-white hover:bg-gray-100 disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed text-gray-700 text-lg font-medium px-6 py-3 rounded-lg border-2 border-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            style={{ minHeight: '52px', minWidth: '120px' }}
          >
            下一頁 →
          </button>
        </div>
      </div>

      {/* Loading Indicator */}
      {isLoading && (
        <div className="mt-4 text-center text-base text-gray-500">
          載入中...
        </div>
      )}
    </div>
  )
}
