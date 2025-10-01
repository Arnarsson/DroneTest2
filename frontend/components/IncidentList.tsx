'use client'

import { motion } from 'framer-motion'
import { format } from 'date-fns'
import type { Incident } from '@/types'
import { EvidenceBadge } from './EvidenceBadge'
import { SourceBadge } from './SourceBadge'

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
    <div className="max-w-5xl mx-auto px-4 py-6 min-h-full">
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
  const getTimeAgo = (date: string) => {
    const now = new Date()
    const then = new Date(date)
    const diffMs = now.getTime() - then.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffHours / 24)

    if (diffHours < 1) return 'Just now'
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return format(then, 'MMM d, yyyy')
  }

  const sourceCount = incident.sources?.length || 0
  const hasUnverifiedSources = sourceCount === 0

  return (
    <motion.div
      className="bg-white dark:bg-gray-900 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 p-8 border border-gray-200 dark:border-gray-800"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.03 }}
    >
      {/* Header Section */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4 mb-6">
        <div className="flex-1">
          <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-3 leading-tight">
            {incident.title}
          </h3>
          <div className="flex items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
            <span className="font-medium">{incident.country}</span>
            <span>•</span>
            <span>{format(new Date(incident.occurred_at), 'MMM d, yyyy')}</span>
            <span>•</span>
            <span className="text-gray-400 dark:text-gray-500">Verified {getTimeAgo(incident.occurred_at)}</span>
          </div>
        </div>
        <div className="flex gap-3 flex-wrap items-center">
          <EvidenceBadge score={incident.evidence_score as 1 | 2 | 3 | 4} />
          {sourceCount > 0 && (
            <span className="bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 text-sm px-4 py-2 rounded-lg font-semibold border border-emerald-200 dark:border-emerald-800">
              {sourceCount} {sourceCount === 1 ? 'source' : 'sources'}
            </span>
          )}
          {incident.asset_type && (
            <span className="bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-sm px-4 py-2 rounded-lg font-semibold border border-blue-200 dark:border-blue-800">
              {formatAssetType(incident.asset_type)}
            </span>
          )}
        </div>
      </div>

      {/* Narrative Section */}
      {incident.narrative && (
        <p className="text-gray-700 dark:text-gray-300 mb-6 leading-relaxed text-base">
          {incident.narrative}
        </p>
      )}

      {/* Location Details */}
      <div className="flex flex-wrap items-center gap-6 text-sm text-gray-600 dark:text-gray-400 mb-6 pb-6 border-b border-gray-100 dark:border-gray-800">
        <div className="flex items-center gap-2">
          <span className="text-base">📍</span>
          <span className="font-medium">{incident.location_name || `${incident.lat.toFixed(4)}, ${incident.lon.toFixed(4)}`}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-base">🕐</span>
          <span>{format(new Date(incident.occurred_at), 'HH:mm')}</span>
        </div>
      </div>

      {/* Sources Section */}
      {hasUnverifiedSources ? (
        <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <svg className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <p className="text-sm font-semibold text-amber-900 dark:text-amber-300">Sources pending verification</p>
              <p className="text-xs text-amber-700 dark:text-amber-400 mt-1">This incident is under review and awaiting source attribution</p>
            </div>
          </div>
        </div>
      ) : (
        <div>
          <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-3 flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            Verified Sources ({sourceCount})
          </div>
          <div className="flex gap-2 flex-wrap">
            {incident.sources.slice(0, 5).map((source, idx) => (
              <SourceBadge
                key={idx}
                url={source.source_url}
                type={source.source_type}
                title={source.source_title}
              />
            ))}
            {sourceCount > 5 && (
              <span className="inline-flex items-center text-sm text-gray-500 dark:text-gray-400 font-medium px-4 py-2 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                +{sourceCount - 5} more
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