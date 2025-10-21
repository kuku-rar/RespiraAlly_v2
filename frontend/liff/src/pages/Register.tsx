/**
 * Patient Registration Page - LINE LIFF
 * Elder-First Design: Large fonts, high contrast, simple forms
 */

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { useLiff } from '../hooks/useLiff'
import { authApi, tokenManager } from '../api/auth'
import type { PatientRegisterRequest } from '../types/auth'
import { COPDStage } from '../types/auth'

export default function RegisterPage() {
  const { isReady, isLoggedIn, profile, login } = useLiff()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<PatientRegisterRequest>()

  // Check if already registered
  useEffect(() => {
    if (tokenManager.isRegistered()) {
      // Already registered, redirect to home
      window.location.href = '/'
    }
  }, [])

  // Auto-fill LINE profile data
  useEffect(() => {
    if (profile) {
      setValue('line_user_id', profile.userId)
      setValue('line_display_name', profile.displayName)
      setValue('line_picture_url', profile.pictureUrl)
      setValue('full_name', profile.displayName) // Pre-fill with LINE name
    }
  }, [profile, setValue])

  const onSubmit = async (data: PatientRegisterRequest) => {
    setError(null)
    setIsSubmitting(true)

    try {
      // Call registration API
      const response = await authApi.registerPatient(data)

      // Store tokens
      tokenManager.storeTokens(response)

      // Show success message
      setSuccess(true)

      // Redirect to home after 2 seconds
      setTimeout(() => {
        window.location.href = '/'
      }, 2000)
    } catch (err) {
      setError(err instanceof Error ? err.message : '註冊失敗，請稍後再試')
    } finally {
      setIsSubmitting(false)
    }
  }

  // Loading state
  if (!isReady) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 via-white to-blue-50 px-4">
        <div className="text-center">
          <div className="text-2xl font-medium text-gray-700">載入中...</div>
        </div>
      </div>
    )
  }

  // Not logged in to LINE
  if (!isLoggedIn) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 via-white to-blue-50 px-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 border border-gray-200 text-center">
          <div className="text-6xl mb-4">🔐</div>
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            請先登入 LINE
          </h2>
          <p className="text-xl text-gray-600 mb-6">
            需要 LINE 帳號才能註冊使用
          </p>
          <button
            onClick={login}
            className="w-full bg-green-600 hover:bg-green-700 text-white text-xl font-semibold py-4 rounded-lg transition-colors"
            style={{ minHeight: '56px' }}
          >
            使用 LINE 登入
          </button>
        </div>
      </div>
    )
  }

  // Success state
  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 via-white to-blue-50 px-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 border border-gray-200 text-center">
          <div className="text-6xl mb-4">✅</div>
          <h2 className="text-3xl font-bold text-green-600 mb-4">
            註冊成功！
          </h2>
          <p className="text-xl text-gray-600 mb-6">
            即將跳轉至首頁...
          </p>
        </div>
      </div>
    )
  }

  // Registration form
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 px-4 py-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-6">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            RespiraAlly
          </h1>
          <p className="text-xl text-gray-600">
            病患註冊
          </p>
        </div>

        {/* Profile Card */}
        {profile && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6 flex items-center">
            {profile.pictureUrl && (
              <img
                src={profile.pictureUrl}
                alt="Profile"
                className="w-16 h-16 rounded-full mr-4"
              />
            )}
            <div>
              <p className="text-lg font-medium text-gray-900">
                {profile.displayName}
              </p>
              <p className="text-base text-gray-600">LINE 帳號已連結</p>
            </div>
          </div>
        )}

        {/* Registration Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-200">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Full Name */}
            <div>
              <label htmlFor="full_name" className="block text-lg font-medium text-gray-700 mb-2">
                姓名 <span className="text-red-500">*</span>
              </label>
              <input
                id="full_name"
                type="text"
                {...register('full_name', { required: '請輸入姓名' })}
                className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="請輸入您的姓名"
                style={{ minHeight: '52px' }}
              />
              {errors.full_name && (
                <p className="text-base text-red-600 mt-1">⚠️ {errors.full_name.message}</p>
              )}
            </div>

            {/* Date of Birth */}
            <div>
              <label htmlFor="date_of_birth" className="block text-lg font-medium text-gray-700 mb-2">
                出生日期 <span className="text-red-500">*</span>
              </label>
              <input
                id="date_of_birth"
                type="date"
                {...register('date_of_birth', { required: '請選擇出生日期' })}
                className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                style={{ minHeight: '52px' }}
              />
              {errors.date_of_birth && (
                <p className="text-base text-red-600 mt-1">⚠️ {errors.date_of_birth.message}</p>
              )}
            </div>

            {/* Gender */}
            <div>
              <label className="block text-lg font-medium text-gray-700 mb-2">
                性別 <span className="text-red-500">*</span>
              </label>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { value: 'male', label: '男性', icon: '♂️' },
                  { value: 'female', label: '女性', icon: '♀️' },
                  { value: 'other', label: '其他', icon: '⚧️' },
                ].map((option) => (
                  <label
                    key={option.value}
                    className="flex flex-col items-center p-4 border-2 border-gray-300 rounded-lg cursor-pointer hover:border-green-500 hover:bg-green-50 transition-colors"
                    style={{ minHeight: '80px' }}
                  >
                    <input
                      type="radio"
                      value={option.value}
                      {...register('gender', { required: '請選擇性別' })}
                      className="sr-only"
                    />
                    <span className="text-3xl mb-1">{option.icon}</span>
                    <span className="text-lg font-medium">{option.label}</span>
                  </label>
                ))}
              </div>
              {errors.gender && (
                <p className="text-base text-red-600 mt-1">⚠️ {errors.gender.message}</p>
              )}
            </div>

            {/* Phone Number */}
            <div>
              <label htmlFor="phone_number" className="block text-lg font-medium text-gray-700 mb-2">
                聯絡電話
              </label>
              <input
                id="phone_number"
                type="tel"
                {...register('phone_number')}
                className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="0912-345-678"
                style={{ minHeight: '52px' }}
              />
            </div>

            {/* COPD Stage */}
            <div>
              <label htmlFor="copd_stage" className="block text-lg font-medium text-gray-700 mb-2">
                COPD 分期 <span className="text-red-500">*</span>
              </label>
              <select
                id="copd_stage"
                {...register('copd_stage', { required: '請選擇 COPD 分期' })}
                className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                style={{ minHeight: '52px' }}
              >
                <option value="">請選擇...</option>
                <option value={COPDStage.STAGE_1}>第一期（輕度）</option>
                <option value={COPDStage.STAGE_2}>第二期（中度）</option>
                <option value={COPDStage.STAGE_3}>第三期（重度）</option>
                <option value={COPDStage.STAGE_4}>第四期（極重度）</option>
                <option value={COPDStage.UNKNOWN}>不確定</option>
              </select>
              {errors.copd_stage && (
                <p className="text-base text-red-600 mt-1">⚠️ {errors.copd_stage.message}</p>
              )}
            </div>

            {/* Diagnosis Date */}
            <div>
              <label htmlFor="diagnosis_date" className="block text-lg font-medium text-gray-700 mb-2">
                確診日期
              </label>
              <input
                id="diagnosis_date"
                type="date"
                {...register('diagnosis_date')}
                className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                style={{ minHeight: '52px' }}
              />
            </div>

            {/* Emergency Contact */}
            <div className="border-t pt-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                緊急聯絡人（選填）
              </h3>

              <div className="space-y-4">
                <div>
                  <label htmlFor="emergency_contact_name" className="block text-lg font-medium text-gray-700 mb-2">
                    姓名
                  </label>
                  <input
                    id="emergency_contact_name"
                    type="text"
                    {...register('emergency_contact_name')}
                    className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="家人或朋友姓名"
                    style={{ minHeight: '52px' }}
                  />
                </div>

                <div>
                  <label htmlFor="emergency_contact_phone" className="block text-lg font-medium text-gray-700 mb-2">
                    電話
                  </label>
                  <input
                    id="emergency_contact_phone"
                    type="tel"
                    {...register('emergency_contact_phone')}
                    className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="0912-345-678"
                    style={{ minHeight: '52px' }}
                  />
                </div>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4" role="alert">
                <p className="text-lg text-red-800 font-medium">
                  ⚠️ {error}
                </p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white text-xl font-semibold py-4 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-4 focus:ring-green-300"
              style={{ minHeight: '56px' }}
            >
              {isSubmitting ? '註冊中...' : '完成註冊'}
            </button>
          </form>
        </div>

        {/* Mock Mode Indicator */}
        {import.meta.env.VITE_MOCK_MODE === 'true' && (
          <div className="mt-6 bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4">
            <p className="text-base text-yellow-800 text-center">
              🧪 <strong>Mock 模式</strong> - 測試用，填寫任意資料即可註冊
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
