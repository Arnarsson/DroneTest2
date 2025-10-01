/**
 * Evidence Scoring System - Single Source of Truth
 *
 * ALL components must import from this file to ensure consistency
 * across Map markers, List badges, Popups, Legend, and Filters
 */

export const EVIDENCE_SYSTEM = {
  4: {
    label: 'OFFICIAL',
    shortLabel: 'Official',
    color: '#10b981',              // emerald-500
    colorDark: '#34d399',          // emerald-400
    bgClass: 'bg-emerald-500',
    textClass: 'text-white',
    borderClass: 'border-emerald-500',
    gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    glow: 'rgba(16, 185, 129, 0.6)',
    icon: 'shield',
    description: 'Verified by official authorities (police, military, NOTAM)',
    emoji: '🟢',
    minSources: 1,
    requiresOfficial: true
  },
  3: {
    label: 'VERIFIED',
    shortLabel: 'Verified',
    color: '#f59e0b',              // amber-500
    colorDark: '#fbbf24',          // amber-400
    bgClass: 'bg-amber-500',
    textClass: 'text-white',
    borderClass: 'border-amber-500',
    gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    glow: 'rgba(245, 158, 11, 0.6)',
    icon: 'check-circle',
    description: 'Multiple credible sources confirm this incident',
    emoji: '🟡',
    minSources: 2,
    requiresOfficial: false
  },
  2: {
    label: 'REPORTED',
    shortLabel: 'Reported',
    color: '#f97316',              // orange-500
    colorDark: '#fb923c',          // orange-400
    bgClass: 'bg-orange-500',
    textClass: 'text-white',
    borderClass: 'border-orange-500',
    gradient: 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)',
    glow: 'rgba(249, 115, 22, 0.6)',
    icon: 'alert-circle',
    description: 'Single credible source, awaiting confirmation',
    emoji: '🟠',
    minSources: 1,
    requiresOfficial: false
  },
  1: {
    label: 'UNCONFIRMED',
    shortLabel: 'Unverified',
    color: '#ef4444',              // red-500
    colorDark: '#f87171',          // red-400
    bgClass: 'bg-red-500',
    textClass: 'text-white',
    borderClass: 'border-red-500',
    gradient: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
    glow: 'rgba(239, 68, 68, 0.6)',
    icon: 'help-circle',
    description: 'Social media or unverified reports only',
    emoji: '🔴',
    minSources: 0,
    requiresOfficial: false
  }
} as const

export type EvidenceScore = 1 | 2 | 3 | 4

/**
 * Get evidence configuration by score
 */
export function getEvidenceConfig(score: EvidenceScore) {
  return EVIDENCE_SYSTEM[score]
}

/**
 * Calculate evidence score based on sources
 */
export function calculateEvidenceScore(sources: Array<{source_type: string}>): EvidenceScore {
  if (sources.length === 0) return 1

  const hasOfficial = sources.some(s =>
    ['police', 'military', 'notam', 'aviation'].includes(s.source_type.toLowerCase())
  )

  if (hasOfficial) return 4
  if (sources.length >= 3) return 3
  if (sources.length >= 2) return 3
  return 2
}
