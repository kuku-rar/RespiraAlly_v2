/**
 * Dashboard Home Page - Therapist Dashboard
 * Protected route - requires authentication
 */

'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { tokenManager } from '@/lib/api/auth'
import type { UserInfo } from '@/lib/types/auth'

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<UserInfo | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check authentication
    const token = tokenManager.getAccessToken()
    const userData = tokenManager.getUser()

    if (!token || !userData) {
      // Not authenticated, redirect to login
      router.push('/login')
      return
    }

    setUser(userData)
    setIsLoading(false)
  }, [router])

  const handleLogout = () => {
    tokenManager.clearTokens()
    router.push('/login')
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-600">載入中...</div>
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
              <h1 className="text-3xl font-bold text-gray-900">
                RespiraAlly 管理平台
              </h1>
              <p className="text-lg text-gray-600 mt-1">
                歡迎回來，{user?.display_name || '治療師'}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="px-6 py-3 text-lg font-medium text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors"
              style={{ minHeight: '48px' }}
            >
              登出
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Total Patients */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-lg text-gray-600">總病患數</p>
                <p className="text-4xl font-bold text-gray-900 mt-2">24</p>
              </div>
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-3xl">👥</span>
              </div>
            </div>
          </div>

          {/* High Risk */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-lg text-gray-600">高風險病患</p>
                <p className="text-4xl font-bold text-red-600 mt-2">5</p>
              </div>
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                <span className="text-3xl">⚠️</span>
              </div>
            </div>
          </div>

          {/* Today's Logs */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-lg text-gray-600">今日日誌</p>
                <p className="text-4xl font-bold text-green-600 mt-2">18</p>
              </div>
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-3xl">📝</span>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            快速操作
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <button
              onClick={() => router.push('/patients')}
              className="p-4 text-left bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors border-2 border-blue-200"
              style={{ minHeight: '80px' }}
            >
              <p className="text-xl font-semibold text-blue-900">病患管理</p>
              <p className="text-base text-blue-700 mt-1">查看所有病患</p>
            </button>

            <button className="p-4 text-left bg-green-50 hover:bg-green-100 rounded-lg transition-colors border-2 border-green-200">
              <p className="text-xl font-semibold text-green-900">日誌分析</p>
              <p className="text-base text-green-700 mt-1">查看健康趨勢</p>
            </button>

            <button className="p-4 text-left bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors border-2 border-purple-200">
              <p className="text-xl font-semibold text-purple-900">提醒設定</p>
              <p className="text-base text-purple-700 mt-1">管理通知提醒</p>
            </button>

            <button className="p-4 text-left bg-orange-50 hover:bg-orange-100 rounded-lg transition-colors border-2 border-orange-200">
              <p className="text-xl font-semibold text-orange-900">報表匯出</p>
              <p className="text-base text-orange-700 mt-1">下載統計報表</p>
            </button>
          </div>
        </div>

        {/* User Info (Debug) */}
        {process.env.NEXT_PUBLIC_MOCK_MODE === 'true' && (
          <div className="bg-yellow-50 border-2 border-yellow-200 rounded-xl p-6">
            <h3 className="text-xl font-semibold text-yellow-900 mb-3">
              🧪 Mock 模式資訊
            </h3>
            <pre className="text-sm text-yellow-800 bg-yellow-100 p-4 rounded overflow-auto">
              {JSON.stringify(user, null, 2)}
            </pre>
          </div>
        )}
      </main>
    </div>
  )
}
