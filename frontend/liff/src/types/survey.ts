/**
 * Survey Types - CAT & mMRC Survey Definitions
 * Based on backend schemas: respira_ally/core/schemas/survey.py
 *
 * Sprint 3 Task 5.3.1 - LIFF Survey Page
 */

// ============================================================================
// Enums
// ============================================================================

export enum SurveyType {
  CAT = 'CAT',
  MMRC = 'mMRC',
}

// ============================================================================
// Survey Response Types (API)
// ============================================================================

export interface SurveyResponse {
  response_id: string // UUID
  patient_id: string // UUID
  survey_type: SurveyType
  score: number
  responses: Record<string, number> // Question ID -> Answer value
  completed_at: string // ISO 8601
  created_at: string // ISO 8601
  updated_at?: string // ISO 8601
}

// ============================================================================
// Survey Create Types (API Request)
// ============================================================================

export interface CATSurveyCreate {
  patient_id: string // UUID
  responses: {
    cough: number // 0-5
    phlegm: number // 0-5
    chest_tightness: number // 0-5
    breathlessness: number // 0-5
    activity_limitation: number // 0-5
    confidence: number // 0-5
    sleep: number // 0-5
    energy: number // 0-5
  }
}

export interface MMRCSurveyCreate {
  patient_id: string // UUID
  responses: {
    dyspnea_grade: number // 0-4 (Grade 0-4)
  }
}

// ============================================================================
// Survey Form Types (UI State)
// ============================================================================

export interface SurveyFormState {
  surveyType: SurveyType
  currentStep: number
  totalSteps: number
  answers: Record<string, number>
  isSubmitting: boolean
  error: string | null
}

// ============================================================================
// Survey Question Types
// ============================================================================

export interface SurveyOption {
  value: number
  label: string
  description?: string
}

export interface SurveyQuestion {
  id: string // Question key (e.g., "cough", "phlegm", "dyspnea_grade")
  text: string // Question text in Traditional Chinese
  options: SurveyOption[]
  required: boolean
  ttsText?: string // Optional: custom TTS text (if different from question text)
}

// ============================================================================
// CAT Survey Questions (8 questions)
// Based on cat_form.html - Elderly-friendly version
// ============================================================================

export const CAT_QUESTIONS: SurveyQuestion[] = [
  {
    id: 'cough',
    text: '請問您最近咳嗽的情形？',
    ttsText: '請問您最近咳嗽的情形？請選擇最符合您情況的選項，從 0 到 5',
    options: [
      { value: 0, label: '✅ 完全沒咳嗽', description: '（整天都沒有）' },
      { value: 1, label: '😊 偶爾咳一下', description: '（一天1~2次）' },
      { value: 2, label: '😐 有時會咳', description: '（不太影響）' },
      { value: 3, label: '🙁 常常咳', description: '（有點困擾）' },
      { value: 4, label: '🤢 幾乎每天咳', description: '（很不舒服）' },
      { value: 5, label: '🥵 一直咳不停', description: '（非常難受）' },
    ],
    required: true,
  },
  {
    id: 'phlegm',
    text: '您覺得肺裡面有痰卡住嗎？',
    ttsText: '您覺得肺裡面有痰卡住嗎？請選擇最符合您情況的選項，從 0 到 5',
    options: [
      { value: 0, label: '✅ 完全沒痰', description: '（肺部清爽）' },
      { value: 1, label: '😊 偶爾卡痰', description: '（但能排出）' },
      { value: 2, label: '😐 有點痰', description: '（偶爾咳出）' },
      { value: 3, label: '🙁 常有痰', description: '（不舒服）' },
      { value: 4, label: '🤢 經常很多痰', description: '（影響說話）' },
      { value: 5, label: '🥵 痰多到呼吸困難', description: '' },
    ],
    required: true,
  },
  {
    id: 'chest_tightness',
    text: '您有覺得胸口會悶、會緊嗎？',
    ttsText: '您有覺得胸口會悶、會緊嗎？請選擇最符合您情況的選項，從 0 到 5',
    options: [
      { value: 0, label: '✅ 完全不悶不緊', description: '' },
      { value: 1, label: '😊 偶爾覺得胸悶', description: '' },
      { value: 2, label: '😐 有時會緊一下', description: '' },
      { value: 3, label: '🙁 常常悶住不舒服', description: '' },
      { value: 4, label: '🤢 幾乎每天胸口緊', description: '' },
      { value: 5, label: '🥵 胸悶難受到坐不住', description: '' },
    ],
    required: true,
  },
  {
    id: 'breathlessness',
    text: '您走樓梯或上坡會喘嗎？',
    ttsText: '您走樓梯或上坡會喘嗎？請選擇最符合您情況的選項，從 0 到 5',
    options: [
      { value: 0, label: '✅ 完全不喘', description: '（輕鬆走）' },
      { value: 1, label: '😊 偶爾會喘一下', description: '' },
      { value: 2, label: '😐 有時會喘', description: '（走快一點）' },
      { value: 3, label: '🙁 常常一走就喘', description: '' },
      { value: 4, label: '🤢 幾乎每天一走就喘', description: '' },
      { value: 5, label: '🥵 太喘沒辦法走', description: '' },
    ],
    required: true,
  },
  {
    id: 'activity_limitation',
    text: '在家裡活動有沒有受到影響？',
    ttsText: '在家裡活動有沒有受到影響？請選擇最符合您情況的選項，從 0 到 5',
    options: [
      { value: 0, label: '✅ 活動很方便', description: '' },
      { value: 1, label: '😊 偶爾會懶得動', description: '' },
      { value: 2, label: '😐 有些家務沒力做', description: '' },
      { value: 3, label: '🙁 常常覺得做不來', description: '' },
      { value: 4, label: '🤢 幾乎不太能動', description: '' },
      { value: 5, label: '🥵 完全無法自己活動', description: '' },
    ],
    required: true,
  },
  {
    id: 'confidence',
    text: '您有信心自己出門走走嗎？',
    ttsText: '您有信心自己出門走走嗎？請選擇最符合您情況的選項，從 0 到 5',
    options: [
      { value: 0, label: '✅ 很有信心自己出門', description: '' },
      { value: 1, label: '😊 大部分都可以出門', description: '' },
      { value: 2, label: '😐 有時會擔心出門', description: '' },
      { value: 3, label: '🙁 常常不敢自己走', description: '' },
      { value: 4, label: '🤢 幾乎都不出門', description: '' },
      { value: 5, label: '🥵 完全不敢離家', description: '' },
    ],
    required: true,
  },
  {
    id: 'sleep',
    text: '最近睡眠情況怎麼樣？',
    ttsText: '最近睡眠情況怎麼樣？請選擇最符合您情況的選項，從 0 到 5',
    options: [
      { value: 0, label: '✅ 睡得很好', description: '' },
      { value: 1, label: '😊 偶爾睡不好', description: '' },
      { value: 2, label: '😐 有時會醒來', description: '' },
      { value: 3, label: '🙁 常常睡不好', description: '' },
      { value: 4, label: '🤢 幾乎每天睡不好', description: '' },
      { value: 5, label: '🥵 完全睡不好、精神差', description: '' },
    ],
    required: true,
  },
  {
    id: 'energy',
    text: '最近精神狀況如何？',
    ttsText: '最近精神狀況如何？請選擇最符合您情況的選項，從 0 到 5',
    options: [
      { value: 0, label: '✅ 精神很好', description: '（活力充沛）' },
      { value: 1, label: '😊 偶爾覺得累', description: '' },
      { value: 2, label: '😐 有點沒精神', description: '' },
      { value: 3, label: '🙁 常常提不起勁', description: '' },
      { value: 4, label: '🤢 幾乎整天都累', description: '' },
      { value: 5, label: '🥵 完全沒力做事', description: '' },
    ],
    required: true,
  },
]

// ============================================================================
// mMRC Survey Questions (1 question)
// ============================================================================

export const MMRC_QUESTIONS: SurveyQuestion[] = [
  {
    id: 'dyspnea_grade',
    text: '請選擇最符合您呼吸困難程度的描述',
    ttsText: '請選擇最符合您呼吸困難程度的描述，從 Grade 0 到 Grade 4',
    options: [
      {
        value: 0,
        label: 'Grade 0',
        description: '僅在劇烈運動時感到呼吸困難',
      },
      {
        value: 1,
        label: 'Grade 1',
        description: '快走或爬緩坡時感到呼吸困難',
      },
      {
        value: 2,
        label: 'Grade 2',
        description: '因呼吸困難而走得比同齡者慢，或需要停下來喘氣',
      },
      {
        value: 3,
        label: 'Grade 3',
        description: '走約100公尺或數分鐘後就需要停下來喘氣',
      },
      {
        value: 4,
        label: 'Grade 4',
        description: '穿衣服或脫衣服時就會感到呼吸困難',
      },
    ],
    required: true,
  },
]

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Get survey questions based on survey type
 */
export function getSurveyQuestions(surveyType: SurveyType): SurveyQuestion[] {
  return surveyType === SurveyType.CAT ? CAT_QUESTIONS : MMRC_QUESTIONS
}

/**
 * Calculate CAT survey score (sum of all answers)
 */
export function calculateCATScore(responses: CATSurveyCreate['responses']): number {
  return (
    responses.cough +
    responses.phlegm +
    responses.chest_tightness +
    responses.breathlessness +
    responses.activity_limitation +
    responses.confidence +
    responses.sleep +
    responses.energy
  )
}

/**
 * Calculate mMRC survey score (single grade)
 */
export function calculateMMRCScore(responses: MMRCSurveyCreate['responses']): number {
  return responses.dyspnea_grade
}

/**
 * Get CAT score severity classification
 */
export function getCATSeverity(score: number): 'low' | 'medium' | 'high' | 'very-high' {
  if (score <= 10) return 'low'
  if (score <= 20) return 'medium'
  if (score <= 30) return 'high'
  return 'very-high'
}

/**
 * Get CAT score label in Traditional Chinese
 */
export function getCATScoreLabel(score: number): string {
  const severity = getCATSeverity(score)
  const labels = {
    low: '低影響',
    medium: '中度影響',
    high: '高度影響',
    'very-high': '極高影響',
  }
  return `${labels[severity]} (${score}/40)`
}

/**
 * Get mMRC dyspnea grade label
 */
export function getMMRCGradeLabel(score: number): string {
  const labels = {
    0: 'Grade 0 - 僅在劇烈運動時喘',
    1: 'Grade 1 - 快走或爬緩坡時喘',
    2: 'Grade 2 - 走路比同齡慢或需停下來喘氣',
    3: 'Grade 3 - 走100公尺或數分鐘就需停下來喘氣',
    4: 'Grade 4 - 穿衣或脫衣時就會喘',
  }
  return labels[score as keyof typeof labels] || `Grade ${score}`
}

/**
 * Validate survey responses
 */
export function validateSurveyResponses(
  surveyType: SurveyType,
  answers: Record<string, number>
): { isValid: boolean; missingQuestions: string[] } {
  const questions = getSurveyQuestions(surveyType)
  const missingQuestions: string[] = []

  for (const question of questions) {
    if (question.required && !(question.id in answers)) {
      missingQuestions.push(question.id)
    }
  }

  return {
    isValid: missingQuestions.length === 0,
    missingQuestions,
  }
}
