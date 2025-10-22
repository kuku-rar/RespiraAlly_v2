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
// ============================================================================

export const CAT_QUESTIONS: SurveyQuestion[] = [
  {
    id: 'cough',
    text: '我從不咳嗽 ← → 我一直咳嗽',
    ttsText: '我從不咳嗽到我一直咳嗽，請選擇 0 到 5 之間的分數',
    options: [
      { value: 0, label: '0', description: '從不咳嗽' },
      { value: 1, label: '1' },
      { value: 2, label: '2' },
      { value: 3, label: '3' },
      { value: 4, label: '4' },
      { value: 5, label: '5', description: '一直咳嗽' },
    ],
    required: true,
  },
  {
    id: 'phlegm',
    text: '我的肺部完全沒有痰 ← → 我的肺部充滿痰',
    ttsText: '我的肺部完全沒有痰到我的肺部充滿痰，請選擇 0 到 5 之間的分數',
    options: [
      { value: 0, label: '0', description: '沒有痰' },
      { value: 1, label: '1' },
      { value: 2, label: '2' },
      { value: 3, label: '3' },
      { value: 4, label: '4' },
      { value: 5, label: '5', description: '充滿痰' },
    ],
    required: true,
  },
  {
    id: 'chest_tightness',
    text: '我的胸部一點也不緊繃 ← → 我的胸部非常緊繃',
    ttsText: '我的胸部一點也不緊繃到我的胸部非常緊繃，請選擇 0 到 5 之間的分數',
    options: [
      { value: 0, label: '0', description: '不緊繃' },
      { value: 1, label: '1' },
      { value: 2, label: '2' },
      { value: 3, label: '3' },
      { value: 4, label: '4' },
      { value: 5, label: '5', description: '非常緊繃' },
    ],
    required: true,
  },
  {
    id: 'breathlessness',
    text: '當我走上坡或爬一層樓梯時我不會喘 ← → 當我走上坡或爬一層樓梯時我會喘得很厲害',
    ttsText: '當我走上坡或爬一層樓梯時我不會喘到我會喘得很厲害，請選擇 0 到 5 之間的分數',
    options: [
      { value: 0, label: '0', description: '不會喘' },
      { value: 1, label: '1' },
      { value: 2, label: '2' },
      { value: 3, label: '3' },
      { value: 4, label: '4' },
      { value: 5, label: '5', description: '非常喘' },
    ],
    required: true,
  },
  {
    id: 'activity_limitation',
    text: '我做任何家事都不受限制 ← → 我做任何家事都非常受限',
    ttsText: '我做任何家事都不受限制到我做任何家事都非常受限，請選擇 0 到 5 之間的分數',
    options: [
      { value: 0, label: '0', description: '不受限' },
      { value: 1, label: '1' },
      { value: 2, label: '2' },
      { value: 3, label: '3' },
      { value: 4, label: '4' },
      { value: 5, label: '5', description: '非常受限' },
    ],
    required: true,
  },
  {
    id: 'confidence',
    text: '儘管有肺部問題，我依然有信心離開家 ← → 因為肺部問題，我完全沒有信心離開家',
    ttsText: '儘管有肺部問題，我依然有信心離開家到我完全沒有信心離開家，請選擇 0 到 5 之間的分數',
    options: [
      { value: 0, label: '0', description: '有信心' },
      { value: 1, label: '1' },
      { value: 2, label: '2' },
      { value: 3, label: '3' },
      { value: 4, label: '4' },
      { value: 5, label: '5', description: '沒信心' },
    ],
    required: true,
  },
  {
    id: 'sleep',
    text: '儘管有肺部問題，我睡得很好 ← → 因為肺部問題，我睡得很不好',
    ttsText: '儘管有肺部問題，我睡得很好到因為肺部問題，我睡得很不好，請選擇 0 到 5 之間的分數',
    options: [
      { value: 0, label: '0', description: '睡得好' },
      { value: 1, label: '1' },
      { value: 2, label: '2' },
      { value: 3, label: '3' },
      { value: 4, label: '4' },
      { value: 5, label: '5', description: '睡不好' },
    ],
    required: true,
  },
  {
    id: 'energy',
    text: '我精力充沛 ← → 我完全沒有精力',
    ttsText: '我精力充沛到我完全沒有精力，請選擇 0 到 5 之間的分數',
    options: [
      { value: 0, label: '0', description: '精力充沛' },
      { value: 1, label: '1' },
      { value: 2, label: '2' },
      { value: 3, label: '3' },
      { value: 4, label: '4' },
      { value: 5, label: '5', description: '沒有精力' },
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
