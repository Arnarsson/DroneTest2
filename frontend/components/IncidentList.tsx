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

  const evidenceGradients = {
    1: 'from-gray-500 to-gray-600',
    2: 'from-yellow-400 to-yellow-600',
    3: 'from-orange-500 to-orange-700',
    4: 'from-red-500 to-red-700',
  }

  const getFavicon = (url: string) => {
    try {
      const domain = new URL(url).hostname
      return `https://www.google.com/s2/favicons?domain=${domain}&sz=16`
    } catch {
      return null
    }
  }

  return (
    <motion.div
      className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm rounded-2xl shadow-soft hover:shadow-lifted transition-all duration-300 p-6 border border-gray-200/50 dark:border-gray-700/50 elevation-2 hover:elevation-4 gpu-accelerated"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, type: 'spring', bounce: 0.25 }}
      whileHover={{ y: -6, scale: 1.01, transition: { duration: 0.25 } }}
    >
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-3 mb-4">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white flex-1 leading-tight">
          {incident.title}
        </h3>
        <div className="flex gap-2 flex-wrap">
          <motion.span
            className={`bg-gradient-to-br ${evidenceGradients[incident.evidence_score as keyof typeof evidenceGradients]} text-white text-xs px-4 py-2 rounded-full font-bold shadow-md`}
            whileHover={{ scale: 1.08, rotate: 2 }}
            whileTap={{ scale: 0.95 }}
          >
            {evidenceLabels[incident.evidence_score as keyof typeof evidenceLabels]}
          </motion.span>
          {incident.asset_type && (
            <motion.span
              className="bg-blue-50/80 dark:bg-blue-900/40 backdrop-blur-sm text-blue-700 dark:text-blue-300 text-xs px-4 py-2 rounded-full font-semibold border border-blue-200 dark:border-blue-800/50"
              whileHover={{ scale: 1.08, rotate: -2 }}
              whileTap={{ scale: 0.95 }}
            >
              {formatAssetType(incident.asset_type)}
            </motion.span>
          )}
        </div>
      </div>

      {incident.narrative && (
        <p className="text-gray-700 dark:text-gray-300 mb-5 leading-relaxed text-[15px]">
          {incident.narrative}
        </p>
      )}

      <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-gray-600 dark:text-gray-400 mb-4">
        <div className="flex items-center gap-2">
          <span className="text-lg">📍</span>
          <span className="font-semibold">{incident.location_name || `${incident.lat.toFixed(4)}, ${incident.lon.toFixed(4)}`}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-lg">🕐</span>
          <span className="font-medium">{format(new Date(incident.occurred_at), 'MMM d, yyyy HH:mm')}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-lg">🌍</span>
          <span className="font-medium">{incident.country}</span>
        </div>
      </div>

      {incident.sources && incident.sources.length > 0 && (
        <div className="pt-4 border-t border-gray-200/70 dark:border-gray-700/70">
          <div className="text-[11px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            Sources
          </div>
          <div className="flex gap-2 flex-wrap">
            {incident.sources.slice(0, 4).map((source, idx) => {
              const favicon = getFavicon(source.source_url)
              return (
                <motion.a
                  key={idx}
                  href={source.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-semibold bg-blue-50/80 dark:bg-blue-900/30 backdrop-blur-sm px-3 py-2 rounded-lg border border-blue-200/50 dark:border-blue-800/50 transition-all"
                  whileHover={{ scale: 1.05, y: -2 }}
                  whileTap={{ scale: 0.97 }}
                >
                  {favicon && (
                    <img
                      src={favicon}
                      alt=""
                      width={14}
                      height={14}
                      className="rounded-sm"
                      onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
                    />
                  )}
                  <span>{source.source_type}</span>
                  <svg className="w-3 h-3 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </motion.a>
              )
            })}
            {incident.sources.length > 4 && (
              <span className="inline-flex items-center text-xs text-gray-500 dark:text-gray-400 font-medium px-3 py-2">
                +{incident.sources.length - 4} more
              </span>
            )}
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