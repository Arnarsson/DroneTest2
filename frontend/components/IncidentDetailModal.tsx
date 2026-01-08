'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useFocusTrap } from '../hooks/useFocusTrap'
import { Incident } from '../types'
import { EvidenceBadge } from './EvidenceBadge'
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

              {/* Content sections will be added in Phase 2 */}
              <div className="space-y-6">
                {/* Narrative section placeholder */}
                {incident.narrative && (
                  <section>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Narrative</h3>
                    <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                      {incident.narrative}
                    </p>
                  </section>
                )}

                {/* Additional sections will be implemented in subtasks 2.2-2.6 */}
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
