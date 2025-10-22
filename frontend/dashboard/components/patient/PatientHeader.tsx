/**
 * PatientHeader Component
 * Displays patient basic information at the top of patient detail page
 *
 * Task 5.1.2 - Sprint 3
 */

'use client'

import { useRouter } from 'next/navigation'
import type { PatientResponse } from '@/lib/types/patient'

interface PatientHeaderProps {
  patient: PatientResponse
}

export function PatientHeader({ patient }: PatientHeaderProps) {
  const router = useRouter()

  const handleBackToList = () => {
    router.push('/patients')
  }

  // Gender label
  const genderLabel = {
    MALE: '男性',
    FEMALE: '女性',
    OTHER: '其他',
  }[patient.gender || 'OTHER']

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {/* Back Button Bar */}
      <div className="px-6 py-3 bg-gray-50 border-b border-gray-200">
        <button
          onClick={handleBackToList}
          className="flex items-center text-blue-600 hover:text-blue-800 transition-colors"
        >
          <svg
            className="w-5 h-5 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          返回病患列表
        </button>
      </div>

      {/* Patient Info */}
      <div className="p-6">
        <div className="flex items-start justify-between flex-wrap gap-4">
          {/* Left: Name & Basic Info */}
          <div className="flex-1 min-w-[300px]">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {patient.name}
            </h1>
            <div className="flex items-center gap-4 text-gray-600">
              <span className="flex items-center gap-1">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                {genderLabel}
              </span>
              <span className="flex items-center gap-1">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                {patient.age} 歲
              </span>
              {patient.phone && (
                <span className="flex items-center gap-1">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  {patient.phone}
                </span>
              )}
            </div>
          </div>

          {/* Right: Physical Metrics */}
          <div className="flex gap-6">
            {/* Height */}
            {patient.height_cm && (
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-1">身高</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {patient.height_cm}
                  <span className="text-sm text-gray-600 ml-1">cm</span>
                </p>
              </div>
            )}

            {/* Weight */}
            {patient.weight_kg && (
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-1">體重</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {patient.weight_kg}
                  <span className="text-sm text-gray-600 ml-1">kg</span>
                </p>
              </div>
            )}

            {/* BMI */}
            {patient.bmi && (
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-1">BMI</p>
                <p
                  className={`text-2xl font-semibold ${
                    patient.bmi < 18.5
                      ? 'text-yellow-600'
                      : patient.bmi < 24
                      ? 'text-green-600'
                      : patient.bmi < 27
                      ? 'text-orange-600'
                      : 'text-red-600'
                  }`}
                >
                  {patient.bmi.toFixed(1)}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {patient.bmi < 18.5
                    ? '過輕'
                    : patient.bmi < 24
                    ? '正常'
                    : patient.bmi < 27
                    ? '過重'
                    : '肥胖'}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Additional Info (if available) */}
        {patient.birth_date && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              出生日期: <span className="text-gray-900 font-medium">{patient.birth_date}</span>
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
