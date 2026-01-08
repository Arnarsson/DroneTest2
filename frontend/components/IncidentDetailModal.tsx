'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useFocusTrap } from '../hooks/useFocusTrap'
import { Incident } from '../types'
import { EvidenceBadge } from './EvidenceBadge'
import { cleanNarrative } from '@/lib/formatters'
import type { EvidenceScore } from '@/constants/evidence'

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
