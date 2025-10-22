/**
 * PatientTabs Component
 * Tab navigation for patient detail sections (Profile, Daily Logs, Surveys)
 *
 * Task 5.1.2 - Sprint 3
 */

'use client'

import { useState } from 'react'
import type { PatientResponse } from '@/lib/types/patient'
import type { DailyLogListResponse } from '@/lib/types/daily-log'
import type { SurveyListResponse } from '@/lib/types/survey'
import { getCATScoreLabel, getMMRCGradeLabel } from '@/lib/types/survey'

interface PatientTabsProps {
  patient: PatientResponse
  dailyLogs?: DailyLogListResponse
  surveys?: SurveyListResponse
}

type TabId = 'profile' | 'daily-logs' | 'surveys'

export function PatientTabs({ patient, dailyLogs, surveys }: PatientTabsProps) {
  const [activeTab, setActiveTab] = useState<TabId>('profile')

  const tabs = [
    {
      id: 'profile' as TabId,
      label: '基本資料',
      icon: '👤',
      count: null,
    },
    {
      id: 'daily-logs' as TabId,
      label: '每日紀錄',
      icon: '📊',
      count: dailyLogs?.total || 0,
    },
    {
      id: 'surveys' as TabId,
      label: '問卷評估',
      icon: '📋',
      count: surveys?.total || 0,
    },
  ]

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {/* Tab Headers */}
      <div className="border-b border-gray-200">
        <div className="flex">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 px-6 py-4 text-center font-medium transition-colors relative ${
                activeTab === tab.id
                  ? 'text-blue-600 bg-blue-50'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-center gap-2">
                <span className="text-xl">{tab.icon}</span>
                <span>{tab.label}</span>
                {tab.count !== null && (
                  <span
                    className={`ml-2 px-2 py-0.5 text-xs rounded-full ${
                      activeTab === tab.id
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-700'
                    }`}
                  >
                    {tab.count}
                  </span>
                )}
              </div>
              {activeTab === tab.id && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600"></div>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'profile' && <ProfileTab patient={patient} />}
        {activeTab === 'daily-logs' && <DailyLogsTab dailyLogs={dailyLogs} />}
        {activeTab === 'surveys' && <SurveysTab surveys={surveys} />}
      </div>
    </div>
  )
}

// ============================================================================
// Tab Content Components
// ============================================================================

function ProfileTab({ patient }: { patient: PatientResponse }) {
  const fields = [
    { label: '姓名', value: patient.name },
    { label: '性別', value: patient.gender === 'MALE' ? '男性' : patient.gender === 'FEMALE' ? '女性' : '其他' },
    { label: '出生日期', value: patient.birth_date },
    { label: '年齡', value: patient.age ? `${patient.age} 歲` : '-' },
    { label: '聯絡電話', value: patient.phone || '-' },
    { label: '身高', value: patient.height_cm ? `${patient.height_cm} cm` : '-' },
    { label: '體重', value: patient.weight_kg ? `${patient.weight_kg} kg` : '-' },
    { label: 'BMI', value: patient.bmi ? patient.bmi.toFixed(1) : '-' },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {fields.map((field) => (
        <div key={field.label}>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {field.label}
          </label>
          <p className="text-lg text-gray-900">{field.value}</p>
        </div>
      ))}
    </div>
  )
}

function DailyLogsTab({ dailyLogs }: { dailyLogs?: DailyLogListResponse }) {
  if (!dailyLogs || dailyLogs.items.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">尚無每日紀錄資料</p>
        <p className="text-gray-400 text-sm mt-2">
          病患填寫每日健康紀錄後，資料會顯示在這裡
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          最近 {dailyLogs.items.length} 筆紀錄
        </h3>
        <p className="text-sm text-gray-600">
          總計: {dailyLogs.total} 筆
        </p>
      </div>

      {/* Daily Logs List */}
      <div className="space-y-3">
        {dailyLogs.items.map((log) => (
          <div
            key={log.log_id}
            className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="font-medium text-gray-900">
                  📅 {new Date(log.log_date).toLocaleDateString('zh-TW', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    weekday: 'short',
                  })}
                </p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3 text-sm">
                  {log.water_ml !== undefined && (
                    <div>
                      <p className="text-gray-600">飲水量</p>
                      <p className="font-medium text-blue-600">{log.water_ml} ml</p>
                    </div>
                  )}
                  {log.exercise_minutes !== undefined && (
                    <div>
                      <p className="text-gray-600">運動時間</p>
                      <p className="font-medium text-green-600">{log.exercise_minutes} 分鐘</p>
                    </div>
                  )}
                  {log.medication_taken !== undefined && (
                    <div>
                      <p className="text-gray-600">用藥</p>
                      <p className={`font-medium ${log.medication_taken ? 'text-green-600' : 'text-red-600'}`}>
                        {log.medication_taken ? '✅ 已服藥' : '❌ 未服藥'}
                      </p>
                    </div>
                  )}
                  {log.mood !== undefined && (
                    <div>
                      <p className="text-gray-600">心情</p>
                      <p className="font-medium">{getMoodEmoji(log.mood)} {log.mood}/5</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function SurveysTab({ surveys }: { surveys?: SurveyListResponse }) {
  if (!surveys || surveys.items.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">尚無問卷評估資料</p>
        <p className="text-gray-400 text-sm mt-2">
          病患完成 CAT 或 mMRC 問卷後，結果會顯示在這裡
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          最近 {surveys.items.length} 筆評估
        </h3>
        <p className="text-sm text-gray-600">
          總計: {surveys.total} 筆
        </p>
      </div>

      {/* Surveys List */}
      <div className="space-y-3">
        {surveys.items.map((survey) => (
          <div
            key={survey.response_id}
            className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">
                    {survey.survey_type === 'CAT' ? '📋' : '🫁'}
                  </span>
                  <div>
                    <p className="font-semibold text-gray-900">
                      {survey.survey_type === 'CAT' ? 'CAT 評估測試' : 'mMRC 呼吸困難分級'}
                    </p>
                    <p className="text-sm text-gray-600">
                      {new Date(survey.completed_at).toLocaleString('zh-TW', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                </div>

                <div className="mt-3">
                  <div className="flex items-baseline gap-2">
                    <p className="text-sm text-gray-600">分數:</p>
                    <p className={`text-2xl font-bold ${getSeverityColor(survey.survey_type, survey.score)}`}>
                      {survey.score}
                      {survey.survey_type === 'CAT' && <span className="text-lg text-gray-600">/40</span>}
                      {survey.survey_type === 'mMRC' && <span className="text-lg text-gray-600">/4</span>}
                    </p>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    {survey.survey_type === 'CAT'
                      ? getCATScoreLabel(survey.score)
                      : getMMRCGradeLabel(survey.score)}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ============================================================================
// Helper Functions
// ============================================================================

function getMoodEmoji(mood: number): string {
  const emojis = ['😢', '🙁', '😐', '🙂', '😊', '😄']
  return emojis[mood] || '😐'
}

function getSeverityColor(surveyType: string, score: number): string {
  if (surveyType === 'CAT') {
    if (score <= 10) return 'text-green-600'
    if (score <= 20) return 'text-yellow-600'
    if (score <= 30) return 'text-orange-600'
    return 'text-red-600'
  } else {
    // mMRC
    if (score === 0) return 'text-green-600'
    if (score === 1) return 'text-yellow-600'
    if (score === 2) return 'text-orange-600'
    return 'text-red-600'
  }
}
