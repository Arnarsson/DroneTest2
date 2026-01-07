'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { EVIDENCE_SYSTEM, type EvidenceScore } from '@/constants/evidence'

interface EvidenceLegendModalProps {
  isOpen: boolean
  onClose: () => void
}

export function EvidenceLegendModal({ isOpen, onClose }: EvidenceLegendModalProps) {
  const modalRef = useRef<HTMLDivElement>(null)

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

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="evidence-legend-title"
        >
          <motion.div
            ref={modalRef}
            initial={{ scale: 0.95, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.95, opacity: 0, y: 20 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            className="relative w-full max-w-md max-h-[85vh] overflow-y-auto bg-white dark:bg-gray-900 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-800"
          >
            {/* Close button */}
            <button
              onClick={onClose}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
              aria-label="Close evidence legend"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            {/* Content */}
            <div className="p-6">
              {/* Header */}
              <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-200 dark:border-gray-800">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-md">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <h2 id="evidence-legend-title" className="text-xl font-bold text-gray-900 dark:text-white">
                    Evidence Levels
                  </h2>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    How we verify drone incidents
                  </p>
                </div>
              </div>

              {/* Evidence Levels */}
              <div className="space-y-4" role="list" aria-label="Evidence scoring levels">
                {([4, 3, 2, 1] as EvidenceScore[]).map((level, idx) => {
                  const config = EVIDENCE_SYSTEM[level]
                  return (
                    <motion.div
                      key={level}
                      className="flex items-start gap-4 p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700/50"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05, type: 'spring', bounce: 0.3 }}
                      role="listitem"
                    >
                      <motion.div
                        className={`w-10 h-10 rounded-full ${config.bgClass} text-white flex items-center justify-center text-base font-bold flex-shrink-0 shadow-md`}
                        whileHover={{ scale: 1.1 }}
                        transition={{ type: 'spring', bounce: 0.5 }}
                        aria-hidden="true"
                      >
                        {level}
                      </motion.div>
                      <div className="flex-1 min-w-0">
                        <div className="text-base font-semibold text-gray-900 dark:text-white">
                          {config.label}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed mt-1">
                          {config.description}
                        </div>
                      </div>
                    </motion.div>
                  )
                })}
              </div>

              {/* Footer */}
              <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-800">
                <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                  Higher scores indicate more reliable evidence sources
                </p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

// Export hook for easy use
export function useEvidenceLegendModal() {
  const [isOpen, setIsOpen] = useState(false)

  const openModal = () => setIsOpen(true)
  const closeModal = () => setIsOpen(false)

  return { isOpen, openModal, closeModal }
}
