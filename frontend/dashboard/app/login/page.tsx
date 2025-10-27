/**
 * Login Page - Therapist Authentication
 * Elder-First Design: Large fonts, high contrast, clear feedback
 */

'use client'

import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { authApi, tokenManager } from '@/lib/api/auth'
import { TherapistLoginRequest } from '@/lib/types/auth'

export default function LoginPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [formData, setFormData] = useState<TherapistLoginRequest>({
    email: '',
    password: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      // Call login API (Mock or Real)
      const response = await authApi.loginTherapist(formData)

      // Store tokens
      tokenManager.storeTokens(response)

      // Redirect to dashboard
      router.push('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : '登入失敗，請檢查帳號密碼')
    } finally {
      setIsLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-green-50 px-4">
      <div className="w-full max-w-md">
        {/* Logo & Title */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            RespiraAlly
          </h1>
          <p className="text-xl text-gray-600">
            治療師管理平台
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            登入帳號
          </h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Input */}
            <div>
              <label
                htmlFor="email"
                className="block text-lg font-medium text-gray-700 mb-2"
              >
                電子郵件
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                autoComplete="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="your.email@example.com"
                style={{ minHeight: '52px' }} // Elder-First: 觸控目標 ≥ 44px
              />
            </div>

            {/* Password Input */}
            <div>
              <label
                htmlFor="password"
                className="block text-lg font-medium text-gray-700 mb-2"
              >
                密碼
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                autoComplete="current-password"
                value={formData.password}
                onChange={handleChange}
                className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="••••••••"
                style={{ minHeight: '52px' }}
              />
            </div>

            {/* Error Message */}
            {error && (
              <div
                className="bg-red-50 border-2 border-red-200 rounded-lg p-4"
                role="alert"
              >
                <p className="text-lg text-red-800 font-medium">
                  ⚠️ {error}
                </p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white text-xl font-semibold py-4 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-4 focus:ring-blue-300"
              style={{ minHeight: '56px' }} // Elder-First: 觸控目標 ≥ 44px
            >
              {isLoading ? '登入中...' : '登入'}
            </button>

            {/* Forgot Password Link */}
            <div className="text-center">
              <a
                href="/forgot-password"
                className="text-lg text-blue-600 hover:text-blue-800 hover:underline"
              >
                忘記密碼？
              </a>
            </div>
          </form>
        </div>

        {/* Register Link */}
        <div className="text-center mt-6">
          <p className="text-lg text-gray-600">
            還沒有帳號？{' '}
            <a
              href="/register"
              className="text-blue-600 hover:text-blue-800 font-semibold hover:underline"
            >
              註冊新帳號
            </a>
          </p>
        </div>

        {/* Mock Mode Indicator */}
        {process.env.NEXT_PUBLIC_MOCK_MODE === 'true' && (
          <div className="mt-6 bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4">
            <p className="text-base text-yellow-800 text-center">
              🧪 <strong>Mock 模式</strong> - 使用任意帳號密碼測試
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
