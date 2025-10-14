'use client'

import { useRef } from 'react'
import { useTheme } from 'next-themes'
import type { Incident } from '@/types'
import { useMapSetup } from './useMapSetup'
import { useMarkerClustering } from './useMarkerClustering'
import { logger } from '@/lib/logger'

interface MapProps {
  incidents: Incident[]
  isLoading: boolean
  center: [number, number]
  zoom: number
}

/**
 * Map component for displaying drone incidents
 *
 * Features:
 * - Evidence-based marker colors (1-4 scale)
 * - Facility clustering (2+ incidents at same location)
 * - Theme-aware styling (dark/light mode)
 * - Multi-source verification display
 * - Interactive popups with incident details
 *
 * @param incidents - Array of incidents to display
 * @param isLoading - Whether data is currently loading
 * @param center - Initial map center [lat, lon]
 * @param zoom - Initial zoom level
 */
export default function Map({ incidents, isLoading, center, zoom }: MapProps) {
  logger.debug('[Map] Component rendered')
  logger.debug('[Map] Received incidents:', incidents.length)
  logger.debug('[Map] isLoading:', isLoading)

  const mapRef = useRef<HTMLDivElement>(null)
  const { theme, resolvedTheme } = useTheme()

  // Initialize map and get refs
  const { mapInstanceRef, clusterRef, tileLayerRef } = useMapSetup(
    mapRef,
    center,
    zoom,
    resolvedTheme
  )

  // Handle marker clustering and updates
  useMarkerClustering(incidents, clusterRef, resolvedTheme)

  return (
    <>
      {isLoading && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-[1000] bg-white/98 dark:bg-gray-900/98 backdrop-blur-2xl rounded-xl shadow-elevated px-5 py-3 border border-gray-200/70 dark:border-gray-800/70">
          <div className="flex items-center gap-3">
            <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">Loading incidents...</span>
          </div>
        </div>
      )}
      <div ref={mapRef} className="w-full h-full" />
    </>
  )
}
