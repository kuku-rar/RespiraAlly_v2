/**
 * App Entry Point - RespiraAlly LIFF
 * Routes to appropriate page based on user state
 */

import { useEffect, useState } from 'react'
import RegisterPage from './pages/Register'
import LogForm from './pages/LogForm'
import SurveyPage from './pages/SurveyPage'
import { tokenManager } from './api/auth'

type Page = 'home' | 'log-form' | 'survey'

function App() {
  const [isRegistered, setIsRegistered] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState<Page>('home')

  useEffect(() => {
    // Check if user is already registered
    const registered = tokenManager.isRegistered()
    setIsRegistered(registered)
    setIsLoading(false)
  }, [])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 via-white to-blue-50">
        <div className="text-2xl font-medium text-gray-700">載入中...</div>
      </div>
    )
  }

  // If not registered, show registration page
  if (!isRegistered) {
    return <RegisterPage />
  }

  // Show appropriate page
  if (currentPage === 'log-form') {
    return <LogForm />
  }

  if (currentPage === 'survey') {
    return <SurveyPage />
  }

  // Home page (default)
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            RespiraAlly
          </h1>
          <p className="text-xl text-gray-600">
            COPD 健康管理
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-200">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            歡迎回來！👋
          </h2>
          <p className="text-lg text-gray-600 mb-6">
            您已完成註冊。
          </p>

          <div className="space-y-4">
            <button
              onClick={() => setCurrentPage('log-form')}
              className="w-full bg-green-600 hover:bg-green-700 text-white text-xl font-semibold py-4 rounded-lg transition-colors"
              style={{ minHeight: '56px' }}
            >
              📝 記錄今日健康日誌
            </button>

            <button
              onClick={() => setCurrentPage('survey')}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white text-xl font-semibold py-4 rounded-lg transition-colors"
              style={{ minHeight: '56px' }}
            >
              📋 填寫問卷評估
            </button>

            <button
              onClick={() => {
                tokenManager.clearTokens()
                window.location.reload()
              }}
              className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 text-lg font-medium py-3 rounded-lg transition-colors"
              style={{ minHeight: '52px' }}
            >
              登出（測試用）
            </button>
          </div>

          {/* Mock Mode Indicator */}
          {import.meta.env.VITE_MOCK_MODE === 'true' && (
            <div className="mt-6 bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4">
              <p className="text-base text-yellow-800 text-center">
                🧪 <strong>Mock 模式</strong> - 測試環境
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
