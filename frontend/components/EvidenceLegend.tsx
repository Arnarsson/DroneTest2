'use client'

import { useState } from 'react'

export function EvidenceLegend() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="absolute bottom-20 left-4 z-[500]">
      {/* Collapsed State */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="bg-white dark:bg-gray-900 rounded-lg shadow-lg px-3 py-2 hover:shadow-xl transition-shadow border border-gray-200 dark:border-gray-800"
        >
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-xs font-medium text-gray-700 dark:text-gray-300">Legend</span>
          </div>
        </button>
      )}

      {/* Expanded State */}
      {isOpen && (
        <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl p-4 border border-gray-200 dark:border-gray-800 w-64">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-bold text-gray-900 dark:text-white">Evidence Levels</h3>
            <button
              onClick={() => setIsOpen(false)}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="space-y-2">
            <div className="flex items-start gap-2">
              <div className="w-6 h-6 rounded-full bg-red-600 text-white flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                4
              </div>
              <div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">Official Report</div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Police, military, or aviation authority</div>
              </div>
            </div>

            <div className="flex items-start gap-2">
              <div className="w-6 h-6 rounded-full bg-orange-500 text-white flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                3
              </div>
              <div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">Verified Media</div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Confirmed by trusted news sources</div>
              </div>
            </div>

            <div className="flex items-start gap-2">
              <div className="w-6 h-6 rounded-full bg-yellow-400 text-white flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                2
              </div>
              <div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">OSINT</div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Open-source intelligence</div>
              </div>
            </div>

            <div className="flex items-start gap-2">
              <div className="w-6 h-6 rounded-full bg-gray-400 text-white flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                1
              </div>
              <div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">Unverified</div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Social media or single source</div>
              </div>
            </div>
          </div>

          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <a
              href="/about"
              className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
              target="_blank"
            >
              Learn more about evidence scoring →
            </a>
          </div>
        </div>
      )}
    </div>
  )
}