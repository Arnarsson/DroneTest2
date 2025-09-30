'use client'

import { motion } from 'framer-motion'
import { format } from 'date-fns'
import type { Incident } from '@/types'

interface IncidentListProps {
  incidents: Incident[]
  isLoading: boolean
}

export function IncidentList({ incidents, isLoading }: IncidentListProps) {
  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-6 space-y-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <motion.div
            key={i}
            className="bg-white dark:bg-gray-900 rounded-xl shadow-md p-6 border border-gray-200 dark:border-gray-800"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <div className="skeleton h-6 w-3/4 mb-3 rounded" />
            <div className="skeleton h-4 w-1/2 mb-2 rounded" />
            <div className="skeleton h-4 w-full rounded" />
          </motion.div>
        ))}
      </div>
    )
  }

  if (incidents.length === 0) {
    return (
      <motion.div
        className="flex flex-col items-center justify-center h-full"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
      >
        <div className="text-center">
          <div className="text-6xl mb-4">🔍</div>
          <p className="text-gray-500 dark:text-gray-400 text-lg font-semibold">No incidents found</p>
          <p className="text-gray-400 dark:text-gray-500 text-sm mt-2">Try adjusting your filters</p>
        </div>
      </motion.div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      <motion.div
        className="space-y-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        {incidents.map((incident, index) => (
          <IncidentCard key={incident.id} incident={incident} index={index} />
        ))}
      </motion.div>
    </div>
  )
}

function IncidentCard({ incident, index }: { incident: Incident; index: number }) {
  const evidenceLabels = {
    1: 'Unverified',
    2: 'OSINT',
    3: 'Verified Media',
    4: 'Official',
  }

  const evidenceColors = {
    1: 'bg-gray-500',
    2: 'bg-yellow-500',
    3: 'bg-orange-500',
    4: 'bg-red-600',
  }

  return (
    <motion.div
      className="bg-white dark:bg-gray-900 rounded-xl shadow-md hover:shadow-xl transition-all p-6 border border-gray-200 dark:border-gray-800"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, type: 'spring', bounce: 0.3 }}
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
    >
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-3 mb-3">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white flex-1">
          {incident.title}
        </h3>
        <div className="flex gap-2 flex-wrap">
          <motion.span
            className={`${evidenceColors[incident.evidence_score as keyof typeof evidenceColors]} text-white text-xs px-3 py-1 rounded-full font-semibold shadow-md`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {evidenceLabels[incident.evidence_score as keyof typeof evidenceLabels]}
          </motion.span>
          {incident.asset_type && (
            <motion.span
              className="bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs px-3 py-1 rounded-full font-medium"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {formatAssetType(incident.asset_type)}
            </motion.span>
          )}
        </div>
      </div>

      {incident.narrative && (
        <p className="text-gray-600 dark:text-gray-300 mb-4 leading-relaxed">
          {incident.narrative}
        </p>
      )}

      <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-gray-500 dark:text-gray-400 mb-3">
        <div className="flex items-center gap-2">
          <span className="text-base">📍</span>
          <span className="font-medium">{incident.location_name || `${incident.lat.toFixed(4)}, ${incident.lon.toFixed(4)}`}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-base">🕐</span>
          <span>{format(new Date(incident.occurred_at), 'MMM d, yyyy HH:mm')}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-base">🌍</span>
          <span>{incident.country}</span>
        </div>
      </div>

      {incident.sources && incident.sources.length > 0 && (
        <div className="flex items-center gap-2 pt-3 border-t border-gray-100 dark:border-gray-800">
          <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">Sources:</span>
          <div className="flex gap-2 flex-wrap">
            {incident.sources.slice(0, 3).map((source, idx) => (
              <motion.a
                key={idx}
                href={source.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium flex items-center gap-1 bg-blue-50 dark:bg-blue-900/20 px-2 py-1 rounded"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <span>{source.source_type}</span>
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </motion.a>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  )
}

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