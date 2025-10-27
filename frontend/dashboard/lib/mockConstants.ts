/**
 * Mock Data Constants - Single Source of Truth
 * Centralized constants for all mock data to ensure consistency
 *
 * Linus Principle: "Multiple sources of truth = BAD"
 *
 * Sprint 5 - P0 Critical Fix
 */

// ============================================================================
// Patient IDs - Canonical Source
// ============================================================================

/**
 * Standard Mock Patient IDs
 * All mock data MUST use these IDs to ensure consistency across:
 * - Alert Mock Data
 * - Task Mock Data
 * - Patient Mock Data
 * - KPI Mock Data
 * - Daily Log Mock Data
 */
export const MOCK_PATIENT_IDS = {
  /** Primary test patient - High risk, GOLD Group E */
  PRIMARY: '00000000-0000-0000-0000-000000000001',

  /** Secondary test patient - Medium risk, GOLD Group B */
  SECONDARY: '00000000-0000-0000-0000-000000000002',

  /** Tertiary test patient - Low risk, GOLD Group A */
  TERTIARY: '00000000-0000-0000-0000-000000000003',
} as const

// ============================================================================
// Therapist IDs - Canonical Source
// ============================================================================

/**
 * Standard Mock Therapist IDs
 */
export const MOCK_THERAPIST_IDS = {
  /** Primary therapist */
  PRIMARY: '00000000-0000-0000-0000-000000000999',

  /** Secondary therapist */
  SECONDARY: '00000000-0000-0000-0000-000000000998',
} as const

// ============================================================================
// Alert IDs - Canonical Source
// ============================================================================

/**
 * Standard Mock Alert IDs
 */
export const MOCK_ALERT_IDS = {
  GOLD_GROUP_E: '00000000-0000-0000-0000-alert0000001',
  HIGH_CAT_SCORE: '00000000-0000-0000-0000-alert0000002',
  FREQUENT_EXACERBATIONS: '00000000-0000-0000-0000-alert0000003',
  LOW_SPO2: '00000000-0000-0000-0000-alert0000004',
} as const

// ============================================================================
// Task IDs - Canonical Source
// ============================================================================

/**
 * Standard Mock Task IDs
 */
export const MOCK_TASK_IDS = {
  TASK_1: '00000000-0000-0000-0000-task00000001',
  TASK_2: '00000000-0000-0000-0000-task00000002',
  TASK_3: '00000000-0000-0000-0000-task00000003',
  TASK_4: '00000000-0000-0000-0000-task00000004',
  TASK_5: '00000000-0000-0000-0000-task00000005',
  TASK_6: '00000000-0000-0000-0000-task00000006',
} as const

// ============================================================================
// User IDs - Canonical Source
// ============================================================================

/**
 * Standard Mock User IDs (for authentication)
 */
export const MOCK_USER_IDS = {
  /** Test patient user account */
  PATIENT_USER: '00000000-0000-0000-0000-user00000001',

  /** Test therapist user account */
  THERAPIST_USER: '00000000-0000-0000-0000-user00000999',
} as const

// ============================================================================
// Type Exports
// ============================================================================

export type MockPatientId = typeof MOCK_PATIENT_IDS[keyof typeof MOCK_PATIENT_IDS]
export type MockTherapistId = typeof MOCK_THERAPIST_IDS[keyof typeof MOCK_THERAPIST_IDS]
export type MockAlertId = typeof MOCK_ALERT_IDS[keyof typeof MOCK_ALERT_IDS]
export type MockTaskId = typeof MOCK_TASK_IDS[keyof typeof MOCK_TASK_IDS]
export type MockUserId = typeof MOCK_USER_IDS[keyof typeof MOCK_USER_IDS]

// ============================================================================
// Validation Helpers
// ============================================================================

/**
 * Check if a patient ID is a valid mock ID
 */
export function isMockPatientId(id: string): id is MockPatientId {
  return Object.values(MOCK_PATIENT_IDS).includes(id as MockPatientId)
}

/**
 * Check if a therapist ID is a valid mock ID
 */
export function isMockTherapistId(id: string): id is MockTherapistId {
  return Object.values(MOCK_THERAPIST_IDS).includes(id as MockTherapistId)
}

/**
 * Check if an alert ID is a valid mock ID
 */
export function isMockAlertId(id: string): id is MockAlertId {
  return Object.values(MOCK_ALERT_IDS).includes(id as MockAlertId)
}

/**
 * Get the primary patient ID for testing
 * Use this as the default patient ID in all mock data and tests
 */
export function getPrimaryPatientId(): MockPatientId {
  return MOCK_PATIENT_IDS.PRIMARY
}

/**
 * Get the primary therapist ID for testing
 * Use this as the default therapist ID in all mock data and tests
 */
export function getPrimaryTherapistId(): MockTherapistId {
  return MOCK_THERAPIST_IDS.PRIMARY
}

// ============================================================================
// Usage Examples (for documentation)
// ============================================================================

/*
GOOD PRACTICE - Single Source of Truth:

// ✅ Import and use the constant
import { MOCK_PATIENT_IDS } from '@/lib/mockConstants'

const mockPatient = {
  patient_id: MOCK_PATIENT_IDS.PRIMARY,  // Always consistent
  name: 'Test Patient'
}

BAD PRACTICE - Multiple Sources of Truth:

// ❌ Hardcoded ID (can become inconsistent)
const mockPatient = {
  patient_id: '00000000-0000-0000-0000-000000000001',  // Magic string!
  name: 'Test Patient'
}

WHY THIS MATTERS:
- AlertBadge fails when patient IDs don't match between Alert and Patient mock data
- E2E tests fail when Task mock data uses different patient IDs
- Debugging becomes nightmare when IDs are inconsistent
- Refactoring is impossible without global search-replace

LINUS SAYS:
"Bad programmers worry about the code. Good programmers worry about data structures."
*/
