/**
 * Risk Assessment Utilities - GOLD ABE Classification
 * Sprint 4: Complete GOLD ABE classification system integration
 */

import { RiskLevel, GoldGroup } from '@/lib/types/patient'

// ============================================================================
// GOLD ABE to Risk Level Mapping
// ============================================================================

/**
 * Map GOLD ABE group to Risk Level
 *
 * GOLD 2011 ABE Classification:
 * - Group A: CAT<10 AND mMRC<2 (Low risk) → risk_level='low'
 * - Group B: CAT>=10 OR mMRC>=2 (Medium risk) → risk_level='medium'
 * - Group E: CAT>=10 AND mMRC>=2 (High risk) → risk_level='high'
 *
 * @param goldGroup - GOLD ABE group (A, B, E)
 * @returns RiskLevel enum value
 */
export function goldGroupToRiskLevel(goldGroup: GoldGroup): RiskLevel {
  const mapping: Record<GoldGroup, RiskLevel> = {
    [GoldGroup.A]: RiskLevel.LOW,
    [GoldGroup.B]: RiskLevel.MEDIUM,
    [GoldGroup.E]: RiskLevel.HIGH,
  }
  return mapping[goldGroup]
}

/**
 * Get risk level from patient data (prefers GOLD ABE, falls back to exacerbation-based)
 *
 * Priority:
 * 1. Use gold_group if available (from latest risk assessment)
 * 2. Fallback to simplified exacerbation-based calculation
 *
 * @param patient - Patient data with optional gold_group and exacerbation data
 * @returns RiskLevel enum value
 */
export function getRiskLevel(patient: {
  gold_group?: GoldGroup
  exacerbation_count_last_12m?: number
  hospitalization_count_last_12m?: number
}): RiskLevel {
  // Priority 1: Use GOLD ABE group if available
  if (patient.gold_group) {
    return goldGroupToRiskLevel(patient.gold_group)
  }

  // Priority 2: Fallback to simplified exacerbation-based calculation
  const exacerbations = patient.exacerbation_count_last_12m ?? 0
  const hospitalizations = patient.hospitalization_count_last_12m ?? 0

  // CRITICAL: High frequency or severe cases
  if (exacerbations >= 3 || hospitalizations >= 2) {
    return RiskLevel.CRITICAL
  }

  // HIGH: Moderate frequency or hospitalization required
  if (exacerbations >= 2 || hospitalizations >= 1) {
    return RiskLevel.HIGH
  }

  // MEDIUM: One exacerbation
  if (exacerbations === 1) {
    return RiskLevel.MEDIUM
  }

  // LOW: No exacerbations
  return RiskLevel.LOW
}

// ============================================================================
// Display Utilities
// ============================================================================

/**
 * Get risk level display label (Chinese)
 */
export function getRiskLevelLabel(riskLevel: RiskLevel): string {
  const labels: Record<RiskLevel, string> = {
    [RiskLevel.LOW]: '低風險',
    [RiskLevel.MEDIUM]: '中風險',
    [RiskLevel.HIGH]: '高風險',
    [RiskLevel.CRITICAL]: '緊急',
  }
  return labels[riskLevel]
}

/**
 * Get GOLD ABE group display label (Chinese)
 */
export function getGoldGroupLabel(goldGroup: GoldGroup): string {
  const labels: Record<GoldGroup, string> = {
    [GoldGroup.A]: 'A級 (低風險)',
    [GoldGroup.B]: 'B級 (中風險)',
    [GoldGroup.E]: 'E級 (高風險)',
  }
  return labels[goldGroup]
}

/**
 * Get risk level badge color (Tailwind classes)
 */
export function getRiskLevelColor(riskLevel: RiskLevel): string {
  const colors: Record<RiskLevel, string> = {
    [RiskLevel.LOW]: 'bg-green-100 text-green-800 border-green-300',
    [RiskLevel.MEDIUM]: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    [RiskLevel.HIGH]: 'bg-orange-100 text-orange-800 border-orange-300',
    [RiskLevel.CRITICAL]: 'bg-red-100 text-red-800 border-red-300',
  }
  return colors[riskLevel]
}

/**
 * Get GOLD ABE group badge color (Tailwind classes)
 */
export function getGoldGroupColor(goldGroup: GoldGroup): string {
  const colors: Record<GoldGroup, string> = {
    [GoldGroup.A]: 'bg-green-100 text-green-800 border-green-300',
    [GoldGroup.B]: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    [GoldGroup.E]: 'bg-red-100 text-red-800 border-red-300',
  }
  return colors[goldGroup]
}

/**
 * Get risk level emoji indicator
 */
export function getRiskLevelEmoji(riskLevel: RiskLevel): string {
  const emojis: Record<RiskLevel, string> = {
    [RiskLevel.LOW]: '✅',
    [RiskLevel.MEDIUM]: '⚠️',
    [RiskLevel.HIGH]: '🔶',
    [RiskLevel.CRITICAL]: '🚨',
  }
  return emojis[riskLevel]
}

/**
 * Get GOLD ABE group emoji indicator
 */
export function getGoldGroupEmoji(goldGroup: GoldGroup): string {
  const emojis: Record<GoldGroup, string> = {
    [GoldGroup.A]: '✅',
    [GoldGroup.B]: '⚠️',
    [GoldGroup.E]: '🚨',
  }
  return emojis[goldGroup]
}
