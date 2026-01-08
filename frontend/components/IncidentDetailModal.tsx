'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useFocusTrap } from '../hooks/useFocusTrap'
import { Incident } from '../types'

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
              {/* Header - Placeholder for subtask 2.1 */}
              <div className="mb-6 pb-6 border-b border-gray-200 dark:border-gray-800">
                <h2 id="incident-modal-title" className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white pr-12">
                  {incident.title}
                </h2>
                <p id="incident-modal-description" className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Incident details and source information
                </p>
              </div>

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
