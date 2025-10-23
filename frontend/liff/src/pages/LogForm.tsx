/**
 * Daily Log Form Page - LIFF Health Log Submission
 * Elder-First Design: 18px+ fonts, 44px+ touch targets, clear labels
 */

import { useState } from 'react'
import { useLiff } from '../hooks/useLiff'
import { dailyLogApi } from '../api/daily-log'
import { type DailyLogFormData, Mood } from '../types/daily-log'

export default function LogForm() {
  const { profile } = useLiff()

  // 表單狀態
  const [formData, setFormData] = useState<DailyLogFormData>({
    log_date: new Date().toISOString().split('T')[0], // 今天日期 YYYY-MM-DD (自動設定)
    medication_taken: false,
    water_intake_ml: '',
    exercise_minutes: '',
    smoking_count: '',
    symptoms: '',
    mood: '',
  })

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  // 處理欄位變更
  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    setError(null)
  }

  // 處理 Toggle 開關
  const handleToggle = () => {
    setFormData((prev) => ({
      ...prev,
      medication_taken: !prev.medication_taken,
    }))
  }

  // 處理心情選擇
  const handleMoodChange = (mood: Mood | '') => {
    setFormData((prev) => ({ ...prev, mood }))
  }

  // 表單驗證
  const validateForm = (): string | null => {
    if (!formData.log_date) {
      return '請選擇日期'
    }

    if (formData.water_intake_ml === '') {
      return '請輸入飲水量'
    }

    const waterIntake = parseInt(formData.water_intake_ml)
    if (isNaN(waterIntake) || waterIntake < 0 || waterIntake > 10000) {
      return '飲水量必須在 0-10000 毫升之間'
    }

    // 驗證運動分鐘數（選填）
    if (formData.exercise_minutes !== '') {
      const exerciseMinutes = parseInt(formData.exercise_minutes)
      if (isNaN(exerciseMinutes) || exerciseMinutes < 0 || exerciseMinutes > 480) {
        return '運動分鐘數必須在 0-480 之間'
      }
    }

    // 驗證吸菸支數（選填）
    if (formData.smoking_count !== '') {
      const smokingCount = parseInt(formData.smoking_count)
      if (isNaN(smokingCount) || smokingCount < 0 || smokingCount > 100) {
        return '吸菸支數必須在 0-100 之間'
      }
    }

    if (formData.symptoms && formData.symptoms.length > 500) {
      return '症狀描述不可超過 500 字'
    }

    return null
  }

  // 提交表單
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // 驗證
    const validationError = validateForm()
    if (validationError) {
      setError(validationError)
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      // 準備提交資料
      const submitData = {
        patient_id: profile?.userId || 'mock-patient-id',
        log_date: formData.log_date,
        medication_taken: formData.medication_taken,
        water_intake_ml: parseInt(formData.water_intake_ml),
        exercise_minutes:
          formData.exercise_minutes !== '' ? parseInt(formData.exercise_minutes) : null,
        smoking_count:
          formData.smoking_count !== '' ? parseInt(formData.smoking_count) : null,
        symptoms: formData.symptoms || null,
        mood: formData.mood !== '' ? formData.mood : null,
      }

      console.log('📝 提交日誌:', submitData)

      // 調用 API
      await dailyLogApi.createLog(submitData)

      // 成功
      setSuccess(true)

      // 2 秒後重置表單
      setTimeout(() => {
        setFormData({
          log_date: new Date().toISOString().split('T')[0],
          medication_taken: false,
          water_intake_ml: '',
          exercise_minutes: '',
          smoking_count: '',
          symptoms: '',
          mood: '',
        })
        setSuccess(false)
      }, 2000)
    } catch (err) {
      console.error('❌ 提交失敗:', err)
      setError(err instanceof Error ? err.message : '提交失敗，請稍後再試')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-8">
      {/* Header */}
      <header className="bg-blue-600 text-white py-6 px-4 shadow-md">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-3xl font-bold mb-2">📝 每日健康日誌</h1>
          <p className="text-xl opacity-90">記錄您的健康狀況</p>
        </div>
      </header>

      {/* Form */}
      <main className="max-w-2xl mx-auto px-4 py-6">
        {/* Success Message */}
        {success && (
          <div className="bg-green-50 border-2 border-green-400 rounded-xl p-6 mb-6 animate-pulse">
            <div className="text-center">
              <div className="text-6xl mb-3">✅</div>
              <div className="text-2xl font-bold text-green-800">提交成功！</div>
              <div className="text-lg text-green-700 mt-2">
                您的健康日誌已記錄
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div
            className="bg-red-50 border-2 border-red-400 rounded-xl p-6 mb-6"
            role="alert"
          >
            <div className="flex items-start space-x-3">
              <div className="text-3xl">⚠️</div>
              <div>
                <div className="text-xl font-bold text-red-800 mb-1">
                  提交失敗
                </div>
                <div className="text-lg text-red-700">{error}</div>
              </div>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 用藥狀態 (Toggle) */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xl font-semibold text-gray-900 mb-1">
                  💊 今日是否服藥？
                </div>
                <div className="text-base text-gray-600">
                  {formData.medication_taken ? '已服藥 ✅' : '未服藥 ❌'}
                </div>
              </div>

              {/* Toggle Switch */}
              <button
                type="button"
                onClick={handleToggle}
                className={`relative inline-flex items-center h-14 w-28 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  formData.medication_taken ? 'bg-green-600' : 'bg-gray-300'
                }`}
                style={{ minHeight: '56px', minWidth: '112px' }}
              >
                <span
                  className={`inline-block h-10 w-10 transform rounded-full bg-white transition-transform shadow-md ${
                    formData.medication_taken ? 'translate-x-16' : 'translate-x-2'
                  }`}
                />
              </button>
            </div>
          </div>

          {/* 飲水量 */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <label
              htmlFor="water_intake_ml"
              className="block text-xl font-semibold text-gray-900 mb-3"
            >
              💧 今日飲水量（毫升）<span className="text-red-600">*</span>
            </label>
            <input
              type="number"
              id="water_intake_ml"
              name="water_intake_ml"
              value={formData.water_intake_ml}
              onChange={handleInputChange}
              placeholder="例如：2000"
              min="0"
              max="10000"
              className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              style={{ minHeight: '52px' }}
              required
            />
            <div className="text-sm text-gray-500 mt-2">
              建議每日飲水 1500-2000 毫升
            </div>
          </div>

          {/* 運動分鐘數 (選填) */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <label
              htmlFor="exercise_minutes"
              className="block text-xl font-semibold text-gray-900 mb-3"
            >
              🏃 今日運動分鐘數（選填）
            </label>
            <input
              type="number"
              id="exercise_minutes"
              name="exercise_minutes"
              value={formData.exercise_minutes}
              onChange={handleInputChange}
              placeholder="例如：30"
              min="0"
              max="480"
              className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              style={{ minHeight: '52px' }}
            />
            <div className="text-sm text-gray-500 mt-2">
              建議每日運動 20-60 分鐘
            </div>
          </div>

          {/* 吸菸支數 (選填) */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <label
              htmlFor="smoking_count"
              className="block text-xl font-semibold text-gray-900 mb-3"
            >
              🚬 今日吸菸支數（選填）
            </label>
            <input
              type="number"
              id="smoking_count"
              name="smoking_count"
              value={formData.smoking_count}
              onChange={handleInputChange}
              placeholder="例如：0"
              min="0"
              max="100"
              className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              style={{ minHeight: '52px' }}
            />
            <div className="text-sm text-gray-500 mt-2">
              建議戒菸以改善健康
            </div>
          </div>

          {/* 心情 */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="text-xl font-semibold text-gray-900 mb-4">
              😊 今日心情（選填）
            </div>
            <div className="grid grid-cols-3 gap-3">
              {/* 好心情 */}
              <button
                type="button"
                onClick={() => handleMoodChange(Mood.GOOD)}
                className={`flex flex-col items-center justify-center py-6 rounded-xl border-2 transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  formData.mood === 'GOOD'
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-300 bg-white hover:bg-gray-50'
                }`}
                style={{ minHeight: '100px' }}
              >
                <div className="text-5xl mb-2">😊</div>
                <div className="text-lg font-medium">好</div>
              </button>

              {/* 普通 */}
              <button
                type="button"
                onClick={() => handleMoodChange(Mood.NEUTRAL)}
                className={`flex flex-col items-center justify-center py-6 rounded-xl border-2 transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  formData.mood === 'NEUTRAL'
                    ? 'border-yellow-500 bg-yellow-50'
                    : 'border-gray-300 bg-white hover:bg-gray-50'
                }`}
                style={{ minHeight: '100px' }}
              >
                <div className="text-5xl mb-2">😐</div>
                <div className="text-lg font-medium">普通</div>
              </button>

              {/* 不好 */}
              <button
                type="button"
                onClick={() => handleMoodChange(Mood.BAD)}
                className={`flex flex-col items-center justify-center py-6 rounded-xl border-2 transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  formData.mood === 'BAD'
                    ? 'border-red-500 bg-red-50'
                    : 'border-gray-300 bg-white hover:bg-gray-50'
                }`}
                style={{ minHeight: '100px' }}
              >
                <div className="text-5xl mb-2">😢</div>
                <div className="text-lg font-medium">不好</div>
              </button>
            </div>
          </div>

          {/* 症狀描述 */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <label
              htmlFor="symptoms"
              className="block text-xl font-semibold text-gray-900 mb-3"
            >
              🩺 症狀描述（選填）
            </label>
            <textarea
              id="symptoms"
              name="symptoms"
              value={formData.symptoms}
              onChange={handleInputChange}
              placeholder="例如：輕微咳嗽，無其他不適"
              maxLength={500}
              rows={5}
              className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
            <div className="text-sm text-gray-500 mt-2">
              {formData.symptoms.length} / 500 字
            </div>
          </div>

          {/* 提交按鈕 */}
          <div className="pt-4">
            <button
              type="submit"
              disabled={isSubmitting || success}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white text-xl font-bold py-4 rounded-xl transition-colors shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              style={{ minHeight: '64px' }}
            >
              {isSubmitting ? '提交中...' : success ? '✅ 提交成功' : '📝 提交日誌'}
            </button>
          </div>
        </form>

        {/* Mock Mode Indicator */}
        {import.meta.env.VITE_MOCK_MODE === 'true' && (
          <div className="mt-6 bg-yellow-50 border-2 border-yellow-200 rounded-xl p-4">
            <p className="text-base text-yellow-800 text-center">
              🧪 <strong>Mock 模式</strong> - 資料僅保存於本地，不會傳送至伺服器
            </p>
          </div>
        )}
      </main>
    </div>
  )
}
