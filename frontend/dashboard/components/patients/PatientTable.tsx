/**
 * Patient Table Component - Reusable table for patient list
 * Elder-First Design: Clear headers, large fonts, hover effects
 */

import type { PatientResponse } from '@/lib/types/patient'
import { getRiskLevel, getRiskLevelLabel, getRiskLevelColor, getRiskLevelEmoji, getGoldGroupLabel, getGoldGroupColor, getGoldGroupEmoji } from '@/lib/utils/risk'

interface PatientTableProps {
  patients: PatientResponse[]
  isLoading?: boolean
  onPatientClick: (patientId: string) => void
}

export default function PatientTable({ patients, isLoading = false, onPatientClick }: PatientTableProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        <div className="text-center text-xl text-gray-500">
          載入中...
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-4 text-left text-lg font-semibold text-gray-900">
                姓名
              </th>
              <th className="px-6 py-4 text-left text-lg font-semibold text-gray-900">
                風險等級
              </th>
              <th className="px-6 py-4 text-left text-lg font-semibold text-gray-900">
                性別
              </th>
              <th className="px-6 py-4 text-left text-lg font-semibold text-gray-900">
                年齡
              </th>
              <th className="px-6 py-4 text-left text-lg font-semibold text-gray-900">
                身高 (cm)
              </th>
              <th className="px-6 py-4 text-left text-lg font-semibold text-gray-900">
                體重 (kg)
              </th>
              <th className="px-6 py-4 text-left text-lg font-semibold text-gray-900">
                BMI
              </th>
              <th className="px-6 py-4 text-left text-lg font-semibold text-gray-900">
                聯絡電話
              </th>
              <th className="px-6 py-4 text-left text-lg font-semibold text-gray-900">
                操作
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {patients.length === 0 ? (
              <tr>
                <td colSpan={9} className="px-6 py-12 text-center">
                  <div className="text-6xl mb-4">📋</div>
                  <div className="text-xl text-gray-500 font-medium mb-2">
                    目前沒有病患資料
                  </div>
                  <div className="text-lg text-gray-400">
                    請調整篩選條件或新增病患
                  </div>
                </td>
              </tr>
            ) : (
              patients.map((patient) => {
                const riskLevel = getRiskLevel({
                  gold_group: patient.gold_group,
                  exacerbation_count_last_12m: patient.exacerbation_count_last_12m,
                  hospitalization_count_last_12m: patient.hospitalization_count_last_12m,
                })

                return (
                  <tr
                    key={patient.user_id}
                    onClick={() => onPatientClick(patient.user_id)}
                    className="hover:bg-blue-50 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className="text-lg font-medium text-gray-900">
                          {patient.name}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {patient.gold_group ? (
                        // Display GOLD ABE group if available
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-base font-medium border-2 ${getGoldGroupColor(patient.gold_group)}`}>
                          {getGoldGroupEmoji(patient.gold_group)} {getGoldGroupLabel(patient.gold_group)}
                        </span>
                      ) : (
                        // Fallback to risk level display
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-base font-medium border-2 ${getRiskLevelColor(riskLevel)}`}>
                          {getRiskLevelEmoji(riskLevel)} {getRiskLevelLabel(riskLevel)}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-lg text-gray-700">
                        {patient.gender === 'MALE' ? '♂️ 男' : patient.gender === 'FEMALE' ? '♀️ 女' : '⚧️ 其他'}
                      </div>
                    </td>
                  <td className="px-6 py-4">
                    <div className="text-lg text-gray-700">
                      {patient.age ? `${patient.age} 歲` : '-'}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-lg text-gray-700">
                      {patient.height_cm || '-'}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-lg text-gray-700">
                      {patient.weight_kg || '-'}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-lg text-gray-700">
                      {(() => {
                        const numBMI = normalizeBMI(patient.bmi)
                        return numBMI !== null ? (
                          <span className={getBMIColor(patient.bmi)}>
                            {numBMI.toFixed(1)}
                          </span>
                        ) : (
                          '-'
                        )
                      })()}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-lg text-gray-700">
                      {patient.phone || '-'}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        onPatientClick(patient.user_id)
                      }}
                      className="text-blue-600 hover:text-blue-800 text-lg font-medium hover:underline focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-2 py-1"
                    >
                      查看詳情 →
                    </button>
                  </td>
                </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// Helper function: Normalize BMI value (handle both number and string from API)
function normalizeBMI(bmi: number | string | null | undefined): number | null {
  if (bmi === null || bmi === undefined) return null
  const numBMI = typeof bmi === 'string' ? parseFloat(bmi) : bmi
  return isNaN(numBMI) ? null : numBMI
}

// Helper function: BMI color coding
function getBMIColor(bmi: number | string | null | undefined): string {
  const numBMI = normalizeBMI(bmi)
  if (numBMI === null) return 'text-gray-600'

  if (numBMI < 18.5) {
    return 'text-blue-600 font-semibold' // Underweight
  } else if (numBMI < 24) {
    return 'text-green-600 font-semibold' // Normal
  } else if (numBMI < 27) {
    return 'text-yellow-600 font-semibold' // Overweight
  } else if (numBMI < 30) {
    return 'text-orange-600 font-semibold' // Obese Class I
  } else {
    return 'text-red-600 font-semibold' // Obese Class II+
  }
}
