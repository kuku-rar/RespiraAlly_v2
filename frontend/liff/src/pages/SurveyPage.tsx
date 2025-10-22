/**
 * SurveyPage - CAT & mMRC Survey Form
 *
 * Sprint 3 Task 5.3 - LIFF Survey Implementation
 *
 * Features:
 * - CAT Survey (8 questions)
 * - mMRC Survey (1 question)
 * - TTS support for accessibility
 * - Progress tracking
 * - Result display
 */

import { useState } from 'react'
import { useTTS } from '../hooks/useTTS'
import { QuestionCard, ProgressBar } from '../components/survey'
import {
  SurveyType,
  getSurveyQuestions,
  calculateCATScore,
  calculateMMRCScore,
  getCATScoreLabel,
  getMMRCGradeLabel,
  validateSurveyResponses,
  type CATSurveyCreate,
  type MMRCSurveyCreate,
} from '../types/survey'

type SurveyPageView = 'select' | 'form' | 'result'

interface SurveyResult {
  surveyType: SurveyType
  score: number
  scoreLabel: string
}

export default function SurveyPage() {
  // ========================================
  // State Management
  // ========================================

  const [view, setView] = useState<SurveyPageView>('select')
  const [surveyType, setSurveyType] = useState<SurveyType | null>(null)
  const [currentStep, setCurrentStep] = useState<number>(0)
  const [answers, setAnswers] = useState<Record<string, number>>({})
  const [result, setResult] = useState<SurveyResult | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // TTS Hook
  const { speak, stop, isSpeaking } = useTTS()

  // ========================================
  // Helper Functions
  // ========================================

  const questions = surveyType ? getSurveyQuestions(surveyType) : []
  const totalSteps = questions.length
  const currentQuestion = questions[currentStep]

  /**
   * Start selected survey
   */
  const handleStartSurvey = (type: SurveyType) => {
    setSurveyType(type)
    setView('form')
    setCurrentStep(0)
    setAnswers({})
    setError(null)

    // Read first question with TTS
    const firstQuestion = getSurveyQuestions(type)[0]
    if (firstQuestion?.ttsText) {
      speak(firstQuestion.ttsText)
    }
  }

  /**
   * Handle answer selection
   */
  const handleAnswer = (questionId: string, value: number) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: value,
    }))
    setError(null)
  }

  /**
   * Go to next question
   */
  const handleNext = () => {
    if (!currentQuestion) return

    // Validate current answer
    if (currentQuestion.required && !(currentQuestion.id in answers)) {
      setError('請選擇一個答案')
      return
    }

    // Stop current TTS
    stop()

    // Move to next step or submit
    if (currentStep < totalSteps - 1) {
      const nextStep = currentStep + 1
      setCurrentStep(nextStep)

      // Read next question with TTS
      const nextQuestion = questions[nextStep]
      if (nextQuestion?.ttsText) {
        speak(nextQuestion.ttsText)
      }
    } else {
      handleSubmit()
    }
  }

  /**
   * Go to previous question
   */
  const handlePrevious = () => {
    if (currentStep > 0) {
      stop()
      const prevStep = currentStep - 1
      setCurrentStep(prevStep)

      // Read previous question with TTS
      const prevQuestion = questions[prevStep]
      if (prevQuestion?.ttsText) {
        speak(prevQuestion.ttsText)
      }
    }
  }

  /**
   * Submit survey
   */
  const handleSubmit = async () => {
    if (!surveyType) return

    // Validate all responses
    const validation = validateSurveyResponses(surveyType, answers)
    if (!validation.isValid) {
      setError(`請回答所有必填問題`)
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      // TODO: Replace with actual API call
      // const response = await submitSurvey({ surveyType, answers })

      // Mock submission delay
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Calculate score
      let score: number
      let scoreLabel: string

      if (surveyType === SurveyType.CAT) {
        score = calculateCATScore(answers as CATSurveyCreate['responses'])
        scoreLabel = getCATScoreLabel(score)
      } else {
        score = calculateMMRCScore(answers as MMRCSurveyCreate['responses'])
        scoreLabel = getMMRCGradeLabel(score)
      }

      // Show result
      setResult({ surveyType, score, scoreLabel })
      setView('result')

      // Read result with TTS
      const resultText = `您的${surveyType === SurveyType.CAT ? 'CAT 評估測試' : 'mMRC 呼吸困難分級'}已完成。分數為 ${score}，${scoreLabel}`
      speak(resultText)

    } catch (err) {
      console.error('Survey submission error:', err)
      setError(err instanceof Error ? err.message : '提交問卷時發生錯誤')
    } finally {
      setIsSubmitting(false)
    }
  }

  /**
   * Reset and start new survey
   */
  const handleReset = () => {
    stop()
    setView('select')
    setSurveyType(null)
    setCurrentStep(0)
    setAnswers({})
    setResult(null)
    setError(null)
  }

  // ========================================
  // Render Functions
  // ========================================

  /**
   * Render survey type selection
   */
  const renderSurveySelection = () => (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">問卷評估</h1>
          <p className="text-xl text-gray-600">選擇您要填寫的問卷</p>
        </div>

        <div className="space-y-4">
          {/* CAT Survey */}
          <button
            onClick={() => handleStartSurvey(SurveyType.CAT)}
            className="w-full bg-white hover:bg-blue-50 border-2 border-blue-200 rounded-2xl p-6 transition-colors text-left"
          >
            <div className="flex items-start gap-4">
              <span className="text-4xl">📋</span>
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  CAT 評估測試
                </h2>
                <p className="text-gray-600 mb-2">
                  COPD Assessment Test - 慢性阻塞性肺病評估測試
                </p>
                <p className="text-sm text-gray-500">
                  共 8 題 • 約需 3-5 分鐘
                </p>
              </div>
            </div>
          </button>

          {/* mMRC Survey */}
          <button
            onClick={() => handleStartSurvey(SurveyType.MMRC)}
            className="w-full bg-white hover:bg-green-50 border-2 border-green-200 rounded-2xl p-6 transition-colors text-left"
          >
            <div className="flex items-start gap-4">
              <span className="text-4xl">🫁</span>
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  mMRC 呼吸困難分級
                </h2>
                <p className="text-gray-600 mb-2">
                  Modified Medical Research Council Dyspnea Scale
                </p>
                <p className="text-sm text-gray-500">
                  共 1 題 • 約需 1 分鐘
                </p>
              </div>
            </div>
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
  )

  /**
   * Render survey form
   */
  const renderSurveyForm = () => (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 px-4 py-6 sm:py-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-6">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">
            {surveyType === SurveyType.CAT ? 'CAT 評估測試' : 'mMRC 呼吸困難分級'}
          </h1>
          <p className="text-lg text-gray-600">
            {surveyType === SurveyType.CAT
              ? 'COPD Assessment Test'
              : 'Modified Medical Research Council Dyspnea Scale'}
          </p>
        </div>

        {/* Progress Bar */}
        <ProgressBar current={currentStep} total={totalSteps} className="mb-6" />

        {/* Question Card */}
        {currentQuestion && (
          <QuestionCard
            question={currentQuestion}
            selectedValue={answers[currentQuestion.id] ?? null}
            onSelect={(value) => handleAnswer(currentQuestion.id, value)}
            onSpeak={speak}
            isSpeaking={isSpeaking}
          />
        )}

        {/* Error Message */}
        {error && (
          <div className="mt-6 bg-red-50 border-2 border-red-200 rounded-lg p-4">
            <p className="text-red-800 text-center font-medium">{error}</p>
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="mt-6 flex gap-4">
          {/* Previous Button */}
          <button
            onClick={handlePrevious}
            disabled={currentStep === 0}
            className={`
              flex-1 py-4 px-6 rounded-xl font-semibold text-lg transition-all
              ${
                currentStep === 0
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-600 hover:bg-gray-700 text-white shadow-md hover:shadow-lg'
              }
            `}
            aria-label="上一題"
          >
            ← 上一題
          </button>

          {/* Next/Submit Button */}
          <button
            onClick={handleNext}
            disabled={isSubmitting}
            className="
              flex-1 py-4 px-6 rounded-xl font-semibold text-lg
              bg-blue-600 hover:bg-blue-700 text-white
              shadow-md hover:shadow-lg transition-all
              disabled:bg-gray-400 disabled:cursor-not-allowed
            "
            aria-label={currentStep === totalSteps - 1 ? '提交問卷' : '下一題'}
          >
            {isSubmitting
              ? '提交中...'
              : currentStep === totalSteps - 1
              ? '提交問卷 →'
              : '下一題 →'}
          </button>
        </div>

        {/* Helper Text */}
        <p className="text-center text-gray-600 mt-6 text-base">
          請選擇答案後點選「下一題」繼續
        </p>

        {/* Back to Selection */}
        <button
          onClick={handleReset}
          className="mt-4 w-full py-3 text-gray-600 hover:text-gray-900 transition-colors"
        >
          ← 返回問卷選擇
        </button>
      </div>
    </div>
  )

  /**
   * Render survey result (placeholder - will be implemented in Task 5.3.3)
   */
  const renderSurveyResult = () => (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-200">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              問卷完成 ✅
            </h2>
            <p className="text-xl text-gray-600">
              {result?.scoreLabel}
            </p>

            <button
              onClick={handleReset}
              className="mt-8 px-8 py-3 bg-blue-600 text-white text-lg font-semibold rounded-lg hover:bg-blue-700"
            >
              填寫新問卷
            </button>
          </div>
        </div>
      </div>
    </div>
  )

  // ========================================
  // Main Render
  // ========================================

  if (view === 'select') {
    return renderSurveySelection()
  }

  if (view === 'form') {
    return renderSurveyForm()
  }

  if (view === 'result') {
    return renderSurveyResult()
  }

  return null
}
