'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export function EvidenceLegend() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="absolute bottom-24 left-4 z-[500]">
      <AnimatePresence mode="wait">
        {!isOpen ? (
          <motion.button
            key="collapsed"
            onClick={() => setIsOpen(true)}
            className="bg-white/98 dark:bg-gray-900/98 backdrop-blur-2xl rounded-xl shadow-elevated px-4 py-2.5 hover:shadow-lifted transition-all border border-gray-200/70 dark:border-gray-800/70"
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            transition={{ type: 'spring', bounce: 0.5 }}
          >
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-xs font-semibold text-gray-700 dark:text-gray-300">Legend</span>
            </div>
          </motion.button>
        ) : (
          <motion.div
            key="expanded"
            className="bg-white/98 dark:bg-gray-900/98 backdrop-blur-2xl rounded-2xl shadow-elevated p-6 border border-gray-200/70 dark:border-gray-800/70 w-72"
            initial={{ scale: 0, opacity: 0, x: -20 }}
            animate={{ scale: 1, opacity: 1, x: 0 }}
            exit={{ scale: 0, opacity: 0, x: -20 }}
            transition={{ type: 'spring', bounce: 0.3 }}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold text-gray-900 dark:text-white">Evidence Levels</h3>
              <motion.button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded"
                whileHover={{ scale: 1.1, rotate: 90 }}
                whileTap={{ scale: 0.9 }}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </motion.button>
            </div>

            <div className="space-y-3">
              <LegendItem
                level={4}
                color="bg-red-600"
                title="Official Report"
                description="Police, military, or aviation authority"
                delay={0}
              />
              <LegendItem
                level={3}
                color="bg-orange-500"
                title="Verified Media"
                description="Confirmed by trusted news sources"
                delay={0.05}
              />
              <LegendItem
                level={2}
                color="bg-yellow-400"
                title="OSINT"
                description="Open-source intelligence"
                delay={0.1}
              />
              <LegendItem
                level={1}
                color="bg-gray-400"
                title="Unverified"
                description="Social media or single source"
                delay={0.15}
              />
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <a
                href="/about"
                className="text-xs text-blue-600 dark:text-blue-400 hover:underline font-medium flex items-center gap-1"
                target="_blank"
              >
                <span>Learn more about evidence scoring</span>
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

interface LegendItemProps {
  level: number
  color: string
  title: string
  description: string
  delay: number
}

function LegendItem({ level, color, title, description, delay }: LegendItemProps) {
  return (
    <motion.div
      className="flex items-start gap-3 group"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay, type: 'spring', bounce: 0.3 }}
    >
      <motion.div
        className={`w-7 h-7 rounded-full ${color} text-white flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5 shadow-md`}
        whileHover={{ scale: 1.15, rotate: 360 }}
        transition={{ type: 'spring', bounce: 0.5 }}
      >
        {level}
      </motion.div>
      <div className="flex-1">
        <div className="text-sm font-semibold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
          {title}
        </div>
        <div className="text-xs text-gray-600 dark:text-gray-400 leading-snug">
          {description}
        </div>
      </div>
    </motion.div>
  )
}