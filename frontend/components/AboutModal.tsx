'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { DroneWatchLogo } from './DroneWatchLogo'
import { useFocusTrap } from '../hooks/useFocusTrap'

interface AboutModalProps {
  isOpen: boolean
  onClose: () => void
}

export function AboutModal({ isOpen, onClose }: AboutModalProps) {
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
            aria-labelledby="about-modal-title"
            aria-describedby="about-modal-description"
            initial={{ scale: 0.95, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.95, opacity: 0, y: 20 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            className="relative w-full max-w-2xl max-h-[85vh] overflow-y-auto bg-white dark:bg-gray-900 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-800"
          >
            {/* Close button */}
            <button
              ref={closeButtonRef}
              onClick={onClose}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg focus-ring"
              aria-label="Close modal"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            {/* Content */}
            <div className="p-6 sm:p-8">
              {/* Header */}
              <div className="flex items-center gap-4 mb-6 pb-6 border-b border-gray-200 dark:border-gray-800">
                <DroneWatchLogo size="lg" />
                <div>
                  <h2 id="about-modal-title" className="text-2xl font-bold text-gray-900 dark:text-white">DroneWatch</h2>
                  <p id="about-modal-description" className="text-sm text-gray-500 dark:text-gray-400 font-medium">Safety Through Transparency</p>
                </div>
              </div>

              {/* Mission */}
              <section className="mb-6">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-3">Our Mission</h3>
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                  DroneWatch provides real-time tracking and verification of drone incidents across all of Europe.
                  We aggregate data from official sources, news outlets, and aviation authorities to deliver transparent,
                  evidence-based reporting on drone activity near critical infrastructure.
                </p>
              </section>

              {/* Evidence System */}
              <section className="mb-6">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-3">Evidence-Based Verification</h3>
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed mb-4">
                  Every incident is scored using our 4-tier evidence system:
                </p>
                <div className="space-y-3">
                  <div className="flex items-start gap-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                    <span className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-green-500 text-white rounded-full font-bold text-sm">4</span>
                    <div>
                      <div className="font-semibold text-green-900 dark:text-green-300">Official</div>
                      <div className="text-sm text-green-800 dark:text-green-400">Police, military, NOTAM, or aviation authority sources</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
                    <span className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-amber-500 text-white rounded-full font-bold text-sm">3</span>
                    <div>
                      <div className="font-semibold text-amber-900 dark:text-amber-300">Verified</div>
                      <div className="text-sm text-amber-800 dark:text-amber-400">Multiple media sources with official quotes</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
                    <span className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-orange-500 text-white rounded-full font-bold text-sm">2</span>
                    <div>
                      <div className="font-semibold text-orange-900 dark:text-orange-300">Reported</div>
                      <div className="text-sm text-orange-800 dark:text-orange-400">Single credible news source</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                    <span className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-red-500 text-white rounded-full font-bold text-sm">1</span>
                    <div>
                      <div className="font-semibold text-red-900 dark:text-red-300">Unconfirmed</div>
                      <div className="text-sm text-red-800 dark:text-red-400">Social media or low-trust sources</div>
                    </div>
                  </div>
                </div>
              </section>

              {/* Coverage */}
              <section className="mb-6">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-3">Geographic Coverage</h3>
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed mb-3">
                  DroneWatch monitors drone incidents across all of Europe (35-71°N, -10-31°E), covering Nordic countries, UK, Ireland, Germany, France, Spain, Italy, Poland, Benelux, and the Baltics.
                </p>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">🇩🇰</span>
                    <span className="text-gray-700 dark:text-gray-300">Denmark</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-lg">🇳🇴</span>
                    <span className="text-gray-700 dark:text-gray-300">Norway</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-lg">🇸🇪</span>
                    <span className="text-gray-700 dark:text-gray-300">Sweden</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-lg">🇫🇮</span>
                    <span className="text-gray-700 dark:text-gray-300">Finland</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-lg">🇬🇧</span>
                    <span className="text-gray-700 dark:text-gray-300">United Kingdom</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-lg">🇩🇪</span>
                    <span className="text-gray-700 dark:text-gray-300">Germany</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-lg">🇫🇷</span>
                    <span className="text-gray-700 dark:text-gray-300">France</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-lg">🇵🇱</span>
                    <span className="text-gray-700 dark:text-gray-300">Poland</span>
                  </div>
                </div>
              </section>

              {/* Data Sources */}
              <section className="mb-6">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-3">Data Sources</h3>
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed mb-3">
                  We aggregate data from multiple trusted sources:
                </p>
                <ul className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
                  <li className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    European police departments and law enforcement agencies
                  </li>
                  <li className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    Aviation authorities and NOTAM systems
                  </li>
                  <li className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    Credible news outlets and media organizations
                  </li>
                </ul>
              </section>

              {/* Technology */}
              <section className="mb-6">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-3">Technology</h3>
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                  Built with Next.js, TypeScript, and Supabase. Real-time data ingestion with multi-source
                  consolidation, fake news detection, and PostGIS geospatial queries. Open development on{' '}
                  <a
                    href="https://github.com/Arnarsson/DroneWatch2.0"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 dark:text-blue-400 hover:underline font-medium focus-ring rounded"
                  >
                    GitHub
                  </a>
                  .
                </p>
              </section>

              {/* Footer */}
              <div className="pt-6 border-t border-gray-200 dark:border-gray-800">
                <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                  DroneWatch is an independent project providing public information for awareness and research purposes.
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
export function useAboutModal() {
  const [isOpen, setIsOpen] = useState(false)

  const openModal = () => setIsOpen(true)
  const closeModal = () => setIsOpen(false)

  return { isOpen, openModal, closeModal }
}
