'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useFocusTrap } from '../hooks/useFocusTrap'
import { Incident, IncidentSource } from '../types'
import { EvidenceBadge } from './EvidenceBadge'
import { SourceBadge } from './SourceBadge'
import { cleanNarrative, formatIncidentDate } from '@/lib/formatters'
import { EVIDENCE_SYSTEM, type EvidenceScore } from '@/constants/evidence'

// Helper to format asset type with emoji
function formatAssetType(type: string): string {
  const icons: Record<string, string> = {
    airport: '✈️ Airport',
    harbor: '⚓ Harbor',
    military: '🛡️ Military',
    powerplant: '⚡ Power Plant',
    bridge: '🌉 Bridge',
    other: '📍 Other',
    unknown: '❓ Unknown',
  }
  return icons[type] || type
}

// Helper to get status badge styling and label
function getStatusConfig(status: Incident['status']): { label: string; className: string } {
  const configs: Record<Incident['status'], { label: string; className: string }> = {
    active: {
      label: 'Active',
      className: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800',
    },
    resolved: {
      label: 'Resolved',
      className: 'bg-gray-100 dark:bg-gray-800/50 text-gray-600 dark:text-gray-400 border-gray-200 dark:border-gray-700',
    },
    unconfirmed: {
      label: 'Unconfirmed',
      className: 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800',
    },
    false_positive: {
      label: 'False Positive',
      className: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 border-red-200 dark:border-red-800',
    },
  }
  return configs[status] || configs.unconfirmed
}

// Helper to get country flag emoji from country name/code
function getCountryFlag(country: string): string {
  // Common country code mappings
  const countryFlags: Record<string, string> = {
    'USA': '🇺🇸',
    'US': '🇺🇸',
    'United States': '🇺🇸',
    'UK': '🇬🇧',
    'GB': '🇬🇧',
    'United Kingdom': '🇬🇧',
    'Germany': '🇩🇪',
    'DE': '🇩🇪',
    'France': '🇫🇷',
    'FR': '🇫🇷',
    'Netherlands': '🇳🇱',
    'NL': '🇳🇱',
    'Sweden': '🇸🇪',
    'SE': '🇸🇪',
    'Norway': '🇳🇴',
    'NO': '🇳🇴',
    'Denmark': '🇩🇰',
    'DK': '🇩🇰',
    'Poland': '🇵🇱',
    'PL': '🇵🇱',
    'Finland': '🇫🇮',
    'FI': '🇫🇮',
    'Belgium': '🇧🇪',
    'BE': '🇧🇪',
    'Austria': '🇦🇹',
    'AT': '🇦🇹',
    'Switzerland': '🇨🇭',
    'CH': '🇨🇭',
    'Italy': '🇮🇹',
    'IT': '🇮🇹',
    'Spain': '🇪🇸',
    'ES': '🇪🇸',
    'Canada': '🇨🇦',
    'CA': '🇨🇦',
    'Australia': '🇦🇺',
    'AU': '🇦🇺',
    'Japan': '🇯🇵',
    'JP': '🇯🇵',
    'South Korea': '🇰🇷',
    'KR': '🇰🇷',
    'China': '🇨🇳',
    'CN': '🇨🇳',
    'India': '🇮🇳',
    'IN': '🇮🇳',
    'Russia': '🇷🇺',
    'RU': '🇷🇺',
    'Ukraine': '🇺🇦',
    'UA': '🇺🇦',
    'Ireland': '🇮🇪',
    'IE': '🇮🇪',
    'Portugal': '🇵🇹',
    'PT': '🇵🇹',
    'Czech Republic': '🇨🇿',
    'CZ': '🇨🇿',
    'Czechia': '🇨🇿',
    'Hungary': '🇭🇺',
    'HU': '🇭🇺',
    'Romania': '🇷🇴',
    'RO': '🇷🇴',
    'Greece': '🇬🇷',
    'GR': '🇬🇷',
    'Turkey': '🇹🇷',
    'TR': '🇹🇷',
    'Israel': '🇮🇱',
    'IL': '🇮🇱',
    'Brazil': '🇧🇷',
    'BR': '🇧🇷',
    'Mexico': '🇲🇽',
    'MX': '🇲🇽',
    'Argentina': '🇦🇷',
    'AR': '🇦🇷',
    'New Zealand': '🇳🇿',
    'NZ': '🇳🇿',
    'Singapore': '🇸🇬',
    'SG': '🇸🇬',
    'Taiwan': '🇹🇼',
    'TW': '🇹🇼',
    'Thailand': '🇹🇭',
    'TH': '🇹🇭',
    'Estonia': '🇪🇪',
    'EE': '🇪🇪',
    'Latvia': '🇱🇻',
    'LV': '🇱🇻',
    'Lithuania': '🇱🇹',
    'LT': '🇱🇹',
  }
  return countryFlags[country] || '🌍'
}

// Location section component with coordinates and copy-to-clipboard
function LocationSection({ incident }: { incident: Incident }) {
  const [copied, setCopied] = useState(false)

  // Format coordinates to 4 decimal places
  const formatCoordinate = (value: number): string => {
    return value.toFixed(4)
  }

  const coordinateString = `${formatCoordinate(incident.lat)}, ${formatCoordinate(incident.lon)}`

  // Generate Google Maps URL
  const googleMapsUrl = `https://www.google.com/maps?q=${incident.lat},${incident.lon}`

  // Copy coordinates to clipboard
  const handleCopyCoordinates = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(coordinateString)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Fallback for browsers that don't support clipboard API
      const textArea = document.createElement('textarea')
      textArea.value = coordinateString
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }, [coordinateString])

  return (
    <section aria-labelledby="location-heading">
      <h3
        id="location-heading"
        className="text-lg font-semibold text-gray-900 dark:text-white mb-3"
      >
        Location
      </h3>
      <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 space-y-3">
        {/* Location name */}
        {incident.location_name && (
          <div className="flex items-start gap-2">
            <span className="text-lg" role="img" aria-hidden="true">📍</span>
            <span className="text-gray-900 dark:text-white font-medium">
              {incident.location_name}
            </span>
          </div>
        )}

        {/* Region if available and different from header display */}
        {incident.region && (
          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            <span className="text-base" role="img" aria-hidden="true">🗺️</span>
            <span>{incident.region}</span>
          </div>
        )}

        {/* Coordinates with copy button */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">Coordinates:</span>
            <code className="bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded text-sm font-mono text-gray-800 dark:text-gray-200">
              {coordinateString}
            </code>
          </div>

          {/* Copy button */}
          <button
            onClick={handleCopyCoordinates}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 text-sm rounded-md bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 transition-colors focus-ring"
            aria-label={copied ? 'Coordinates copied' : 'Copy coordinates to clipboard'}
          >
            {copied ? (
              <>
                <svg className="w-4 h-4 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                <span>Copied!</span>
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <span>Copy</span>
              </>
            )}
          </button>
        </div>

        {/* Google Maps link */}
        <a
          href={googleMapsUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 hover:underline transition-colors"
          onClick={(e) => e.stopPropagation()}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
          Open in Google Maps
        </a>
      </div>
    </section>
  )
}

// Calculate duration between two dates in human-readable format
function calculateDuration(firstDate: string, lastDate: string): string | null {
  try {
    const first = new Date(firstDate)
    const last = new Date(lastDate)
    const diffMs = last.getTime() - first.getTime()

    // If same time or negative, return null
    if (diffMs <= 0) return null

    const diffMinutes = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffDays > 0) {
      return diffDays === 1 ? '1 day' : `${diffDays} days`
    } else if (diffHours > 0) {
      return diffHours === 1 ? '1 hour' : `${diffHours} hours`
    } else if (diffMinutes > 0) {
      return diffMinutes === 1 ? '1 minute' : `${diffMinutes} minutes`
    }

    return null
  } catch {
    return null
  }
}

// Timeline section component showing incident dates
function TimelineSection({ incident }: { incident: Incident }) {
  const occurredAt = formatIncidentDate(incident.occurred_at)
  const firstSeenAt = formatIncidentDate(incident.first_seen_at)
  const lastSeenAt = formatIncidentDate(incident.last_seen_at)

  // Check if first and last seen are different
  const hasDifferentFirstLast = incident.first_seen_at !== incident.last_seen_at
  const duration = hasDifferentFirstLast
    ? calculateDuration(incident.first_seen_at, incident.last_seen_at)
    : null

  return (
    <section aria-labelledby="timeline-heading">
      <h3
        id="timeline-heading"
        className="text-lg font-semibold text-gray-900 dark:text-white mb-3"
      >
        Timeline
      </h3>
      <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4">
        <div className="space-y-4">
          {/* Primary date: occurred_at */}
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center">
              <span className="text-base" role="img" aria-hidden="true">📅</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                Incident Date
              </p>
              <p className="text-base font-semibold text-gray-900 dark:text-white">
                {occurredAt}
              </p>
            </div>
          </div>

          {/* First and Last Seen section with visual timeline */}
          {hasDifferentFirstLast ? (
            <div className="relative">
              {/* Vertical timeline line */}
              <div className="absolute left-4 top-8 bottom-8 w-0.5 bg-gray-300 dark:bg-gray-600" aria-hidden="true" />

              <div className="space-y-4">
                {/* First Seen */}
                <div className="flex items-start gap-3 relative">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-100 dark:bg-green-900/50 flex items-center justify-center z-10">
                    <span className="text-base" role="img" aria-hidden="true">🟢</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      First Reported
                    </p>
                    <p className="text-base text-gray-900 dark:text-white">
                      {firstSeenAt}
                    </p>
                  </div>
                </div>

                {/* Duration badge */}
                {duration && (
                  <div className="flex items-center gap-3">
                    <div className="w-8 flex justify-center" aria-hidden="true">
                      <div className="w-1 h-1 rounded-full bg-gray-400 dark:bg-gray-500" />
                    </div>
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-sm rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 font-medium">
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Duration: {duration}
                    </span>
                  </div>
                )}

                {/* Last Seen */}
                <div className="flex items-start gap-3 relative">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-red-100 dark:bg-red-900/50 flex items-center justify-center z-10">
                    <span className="text-base" role="img" aria-hidden="true">🔴</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      Last Reported
                    </p>
                    <p className="text-base text-gray-900 dark:text-white">
                      {lastSeenAt}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            /* Single sighting - first and last are the same */
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                <span className="text-base" role="img" aria-hidden="true">⏱️</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  First & Last Reported
                </p>
                <p className="text-base text-gray-900 dark:text-white">
                  {firstSeenAt}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Single sighting
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  )
}

// Helper to get trust weight configuration
function getTrustWeightConfig(weight: number | undefined): { label: string; color: string; icon: string } {
  const configs: Record<number, { label: string; color: string; icon: string }> = {
    4: {
      label: 'Official',
      color: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300',
      icon: '✓✓',
    },
    3: {
      label: 'Verified',
      color: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300',
      icon: '✓',
    },
    2: {
      label: 'Media',
      color: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300',
      icon: '○',
    },
    1: {
      label: 'Low Trust',
      color: 'bg-gray-100 dark:bg-gray-800/50 text-gray-600 dark:text-gray-400',
      icon: '?',
    },
  }
  return configs[weight ?? 1] || configs[1]
}

// Format published_at date for sources
function formatSourceDate(dateString: string | undefined): string | null {
  if (!dateString) return null
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return null
  }
}

// Sources section component showing all sources with details
function SourcesSection({ sources }: { sources: IncidentSource[] }) {
  if (!sources || sources.length === 0) {
    return null
  }

  return (
    <section aria-labelledby="sources-heading">
      <h3
        id="sources-heading"
        className="text-lg font-semibold text-gray-900 dark:text-white mb-3"
      >
        Sources ({sources.length})
      </h3>
      <div className="space-y-3">
        {sources.map((source, index) => {
          const trustConfig = getTrustWeightConfig(source.trust_weight)
          const publishedDate = formatSourceDate(source.published_at)

          return (
            <div
              key={`${source.source_url}-${index}`}
              className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 border border-gray-200 dark:border-gray-700"
            >
              {/* Source header: badge + trust weight */}
              <div className="flex flex-wrap items-center gap-2 mb-2">
                <SourceBadge
                  url={source.source_url}
                  type={source.source_type}
                  title={source.source_title || source.source_name}
                />

                {/* Trust weight indicator */}
                {source.trust_weight !== undefined && (
                  <span
                    className={`inline-flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full ${trustConfig.color}`}
                    title={`Trust Level: ${trustConfig.label}`}
                  >
                    <span aria-hidden="true">{trustConfig.icon}</span>
                    <span>{trustConfig.label}</span>
                  </span>
                )}
              </div>

              {/* Source quote if available */}
              {source.source_quote && (
                <blockquote className="mt-3 pl-3 border-l-2 border-gray-300 dark:border-gray-600 italic text-sm text-gray-600 dark:text-gray-400">
                  &ldquo;{source.source_quote}&rdquo;
                </blockquote>
              )}

              {/* Published date */}
              {publishedDate && (
                <div className="mt-2 flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-500">
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Published: {publishedDate}</span>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </section>
  )
}

// Official source types that result in evidence score 4
const OFFICIAL_SOURCE_TYPES = ['police', 'military', 'aviation_authority', 'notam']

// Helper to categorize sources by type
function categorizeSourcesByType(sources: IncidentSource[]): {
  official: IncidentSource[]
  media: IncidentSource[]
  social: IncidentSource[]
} {
  const result = {
    official: [] as IncidentSource[],
    media: [] as IncidentSource[],
    social: [] as IncidentSource[],
  }

  for (const source of sources) {
    const type = source.source_type?.toLowerCase() || ''
    if (OFFICIAL_SOURCE_TYPES.includes(type)) {
      result.official.push(source)
    } else if (['verified_media', 'media', 'news'].includes(type)) {
      result.media.push(source)
    } else {
      result.social.push(source)
    }
  }

  return result
}

// Helper to explain why a particular evidence score was assigned
function getScoreExplanation(score: EvidenceScore, sourceCounts: { official: number; media: number; social: number }): string {
  const totalSources = sourceCounts.official + sourceCounts.media + sourceCounts.social

  if (score === 4) {
    return `This incident has ${sourceCounts.official} official source${sourceCounts.official !== 1 ? 's' : ''} (police, military, or aviation authority), which automatically assigns the highest evidence level.`
  }
  if (score === 3) {
    return `This incident is verified by ${totalSources} credible source${totalSources !== 1 ? 's' : ''}, providing strong corroboration for the reported activity.`
  }
  if (score === 2) {
    return `This incident has been reported by a single credible source and is awaiting additional confirmation.`
  }
  return `This incident is based on social media or unverified reports only. Exercise caution when interpreting this information.`
}

// Evidence breakdown section showing how the score was calculated
function EvidenceBreakdownSection({ incident }: { incident: Incident }) {
  const score = incident.evidence_score as EvidenceScore
  const config = EVIDENCE_SYSTEM[score]
  const sources = incident.sources || []
  const sourceCounts = categorizeSourcesByType(sources)
  const counts = {
    official: sourceCounts.official.length,
    media: sourceCounts.media.length,
    social: sourceCounts.social.length,
  }
  const totalSources = counts.official + counts.media + counts.social

  // Get background styles based on score
  const getBgStyles = (s: EvidenceScore): string => {
    const styles: Record<EvidenceScore, string> = {
      4: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800',
      3: 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800',
      2: 'bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800',
      1: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800',
    }
    return styles[s]
  }

  const getTextStyles = (s: EvidenceScore): { title: string; text: string } => {
    const styles: Record<EvidenceScore, { title: string; text: string }> = {
      4: { title: 'text-green-900 dark:text-green-300', text: 'text-green-800 dark:text-green-400' },
      3: { title: 'text-amber-900 dark:text-amber-300', text: 'text-amber-800 dark:text-amber-400' },
      2: { title: 'text-orange-900 dark:text-orange-300', text: 'text-orange-800 dark:text-orange-400' },
      1: { title: 'text-red-900 dark:text-red-300', text: 'text-red-800 dark:text-red-400' },
    }
    return styles[s]
  }

  const textStyles = getTextStyles(score)

  return (
    <section aria-labelledby="evidence-heading">
      <h3
        id="evidence-heading"
        className="text-lg font-semibold text-gray-900 dark:text-white mb-3"
      >
        Evidence Breakdown
      </h3>

      {/* Current score display */}
      <div className={`rounded-lg p-4 border ${getBgStyles(score)} mb-4`}>
        <div className="flex items-start gap-3">
          <span
            className={`flex-shrink-0 w-10 h-10 flex items-center justify-center ${config.bgClass} text-white rounded-full font-bold text-lg`}
          >
            {score}
          </span>
          <div className="flex-1 min-w-0">
            <div className={`font-semibold text-base ${textStyles.title}`}>
              {config.label}
            </div>
            <div className={`text-sm mt-1 ${textStyles.text}`}>
              {config.description}
            </div>
          </div>
        </div>
      </div>

      {/* Source breakdown by type */}
      <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 mb-4">
        <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          Source Breakdown ({totalSources} total)
        </h4>
        <div className="grid grid-cols-3 gap-3">
          {/* Official sources */}
          <div className={`text-center p-3 rounded-lg ${counts.official > 0 ? 'bg-green-100 dark:bg-green-900/30' : 'bg-gray-100 dark:bg-gray-700/50'}`}>
            <div className={`text-2xl font-bold ${counts.official > 0 ? 'text-green-700 dark:text-green-300' : 'text-gray-400 dark:text-gray-500'}`}>
              {counts.official}
            </div>
            <div className={`text-xs font-medium mt-1 ${counts.official > 0 ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'}`}>
              Official
            </div>
            {counts.official > 0 && (
              <div className="mt-1">
                <span className="inline-flex items-center text-xs text-green-600 dark:text-green-400">
                  <svg className="w-3 h-3 mr-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  Verified
                </span>
              </div>
            )}
          </div>

          {/* Media sources */}
          <div className={`text-center p-3 rounded-lg ${counts.media > 0 ? 'bg-amber-100 dark:bg-amber-900/30' : 'bg-gray-100 dark:bg-gray-700/50'}`}>
            <div className={`text-2xl font-bold ${counts.media > 0 ? 'text-amber-700 dark:text-amber-300' : 'text-gray-400 dark:text-gray-500'}`}>
              {counts.media}
            </div>
            <div className={`text-xs font-medium mt-1 ${counts.media > 0 ? 'text-amber-600 dark:text-amber-400' : 'text-gray-500 dark:text-gray-400'}`}>
              Media
            </div>
          </div>

          {/* Social/Other sources */}
          <div className={`text-center p-3 rounded-lg ${counts.social > 0 ? 'bg-gray-200 dark:bg-gray-600/50' : 'bg-gray-100 dark:bg-gray-700/50'}`}>
            <div className={`text-2xl font-bold ${counts.social > 0 ? 'text-gray-700 dark:text-gray-300' : 'text-gray-400 dark:text-gray-500'}`}>
              {counts.social}
            </div>
            <div className={`text-xs font-medium mt-1 ${counts.social > 0 ? 'text-gray-600 dark:text-gray-400' : 'text-gray-500 dark:text-gray-400'}`}>
              Social/Other
            </div>
          </div>
        </div>
      </div>

      {/* Score explanation */}
      <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
        <div className="flex items-start gap-2">
          <svg className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h4 className="text-sm font-semibold text-blue-900 dark:text-blue-300 mb-1">
              Why this score?
            </h4>
            <p className="text-sm text-blue-800 dark:text-blue-400">
              {getScoreExplanation(score, counts)}
            </p>
          </div>
        </div>
      </div>

      {/* Highlight official sources if any */}
      {counts.official > 0 && (
        <div className="mt-4 bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
          <div className="flex items-start gap-2">
            <svg className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <div>
              <h4 className="text-sm font-semibold text-green-900 dark:text-green-300 mb-1">
                Official Sources Confirmed
              </h4>
              <ul className="text-sm text-green-800 dark:text-green-400 space-y-1">
                {sourceCounts.official.map((source, idx) => (
                  <li key={idx} className="flex items-center gap-1">
                    <span className="capitalize">{source.source_type.replace(/_/g, ' ')}</span>
                    {source.source_name && (
                      <span className="text-green-700 dark:text-green-500">
                        ({source.source_name})
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </section>
  )
}

interface IncidentDetailModalProps {
  isOpen: boolean
  onClose: () => void
  incident: Incident | null
}

export function IncidentDetailModal({ isOpen, onClose, incident }: IncidentDetailModalProps) {
  const modalRef = useRef<HTMLDivElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)

  // Trap focus within modal when open, set initial focus to close button
  useFocusTrap(modalRef, {
    isActive: isOpen,
    initialFocusRef: closeButtonRef,
    returnFocus: true,
  })

  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }
    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen, onClose])

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
        onClose()
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen, onClose])

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  // Don't render if no incident is provided
  if (!incident) return null

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4"
        >
          <motion.div
            ref={modalRef}
            role="dialog"
            aria-modal="true"
            aria-labelledby="incident-modal-title"
            aria-describedby="incident-modal-description"
            initial={{ scale: 0.95, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.95, opacity: 0, y: 20 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            className="relative w-full max-w-3xl max-h-[90vh] overflow-y-auto bg-white dark:bg-gray-900 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-800"
          >
            {/* Close button */}
            <button
              ref={closeButtonRef}
              onClick={onClose}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg focus-ring z-10"
              aria-label="Close modal"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            {/* Content */}
            <div className="p-6 sm:p-8">
              {/* Header Section */}
              <header className="mb-6 pb-6 border-b border-gray-200 dark:border-gray-800">
                {/* Title Row */}
                <h2
                  id="incident-modal-title"
                  className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white pr-12 mb-4 leading-tight"
                >
                  {incident.title}
                </h2>

                {/* Badges Row */}
                <div className="flex flex-wrap items-center gap-2 sm:gap-3 mb-4">
                  {/* Evidence Badge */}
                  <EvidenceBadge score={incident.evidence_score as EvidenceScore} size="lg" />

                  {/* Status Badge */}
                  {(() => {
                    const statusConfig = getStatusConfig(incident.status)
                    return (
                      <span
                        className={`text-sm px-3 py-1.5 rounded-full font-semibold border ${statusConfig.className}`}
                      >
                        {statusConfig.label}
                      </span>
                    )
                  })()}

                  {/* Asset Type Badge */}
                  {incident.asset_type && (
                    <span className="bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-sm px-3 py-1.5 rounded-full font-semibold border border-blue-200 dark:border-blue-800">
                      {formatAssetType(incident.asset_type)}
                    </span>
                  )}
                </div>

                {/* Country & Meta Info Row */}
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                  <span className="text-lg" role="img" aria-label={`Flag of ${incident.country}`}>
                    {getCountryFlag(incident.country)}
                  </span>
                  <span className="font-medium text-gray-700 dark:text-gray-300">{incident.country}</span>
                  {incident.region && (
                    <>
                      <span className="text-gray-400 dark:text-gray-600">•</span>
                      <span>{incident.region}</span>
                    </>
                  )}
                </div>

                {/* Screen reader description */}
                <p id="incident-modal-description" className="sr-only">
                  Incident details and source information for {incident.title}
                </p>
              </header>

              {/* Content sections */}
              <div className="space-y-6">
                {/* Narrative section - full, untruncated narrative with proper formatting */}
                {(() => {
                  const cleanedNarrative = incident.narrative ? cleanNarrative(incident.narrative) : ''
                  return cleanedNarrative ? (
                    <section aria-labelledby="narrative-heading">
                      <h3
                        id="narrative-heading"
                        className="text-lg font-semibold text-gray-900 dark:text-white mb-3"
                      >
                        Narrative
                      </h3>
                      <div className="prose prose-gray dark:prose-invert max-w-none">
                        <p className="text-gray-700 dark:text-gray-300 leading-relaxed text-base whitespace-pre-wrap">
                          {cleanedNarrative}
                        </p>
                      </div>
                    </section>
                  ) : null
                })()}

                {/* Location section */}
                <LocationSection incident={incident} />

                {/* Timeline section */}
                <TimelineSection incident={incident} />

                {/* Sources section - shows ALL sources (no limit unlike IncidentCard) */}
                <SourcesSection sources={incident.sources} />

                {/* Evidence breakdown section - shows how the score was calculated */}
                <EvidenceBreakdownSection incident={incident} />
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

// Export hook for easy use - manages modal state and selected incident
export function useIncidentDetailModal() {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null)

  const openModal = (incident: Incident) => {
    setSelectedIncident(incident)
    setIsOpen(true)
  }

  const closeModal = () => {
    setIsOpen(false)
    // Keep incident visible during exit animation, clear after
    setTimeout(() => setSelectedIncident(null), 200)
  }

  return { isOpen, selectedIncident, openModal, closeModal }
}
