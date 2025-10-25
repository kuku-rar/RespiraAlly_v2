/**
 * Risk Assessment Utilities
 * Simple risk calculation based on exacerbation history (Sprint 4 Quick Validation)
 *
 * TODO: Replace with full GOLD ABE classification engine in complete implementation
 */

import { RiskLevel } from '@/lib/types/patient'

export interface RiskCalculationInput {
  exacerbation_count_last_12m?: number
  hospitalization_count_last_12m?: number
}

/**
 * Calculate patient risk level based on exacerbation history
 *
 * Risk Criteria (Simplified for quick validation):
 * - CRITICAL: ≥3 exacerbations OR ≥2 hospitalizations
 * - HIGH: ≥2 exacerbations OR ≥1 hospitalization
 * - MEDIUM: 1 exacerbation
 * - LOW: 0 exacerbations
 *
 * @param input - Patient exacerbation data
 * @returns RiskLevel enum value
 */
export function calculateRiskLevel(input: RiskCalculationInput): RiskLevel {
  const exacerbations = input.exacerbation_count_last_12m ?? 0
  const hospitalizations = input.hospitalization_count_last_12m ?? 0

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
