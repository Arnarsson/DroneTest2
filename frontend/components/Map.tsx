'use client'

import { useEffect, useRef } from 'react'
import { useTheme } from 'next-themes'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import 'leaflet.markercluster'
import type { Incident } from '@/types'
import { formatDistance } from 'date-fns'
import { EVIDENCE_SYSTEM } from '@/constants/evidence'

// Fix Leaflet icon issue
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

interface MapProps {
  incidents: Incident[]
  isLoading: boolean
  center: [number, number]
  zoom: number
}

export default function Map({ incidents, isLoading, center, zoom }: MapProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<L.Map | null>(null)
  const clusterRef = useRef<L.MarkerClusterGroup | null>(null)
  const tileLayerRef = useRef<L.TileLayer | null>(null)
  const { theme, resolvedTheme } = useTheme()

  // Initialize map
  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return

    // Initialize map
    mapInstanceRef.current = L.map(mapRef.current).setView(center, zoom)

    // Add initial tile layer (will be updated by theme effect)
    const isDark = resolvedTheme === 'dark'
    tileLayerRef.current = L.tileLayer(
      isDark
        ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
        : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      {
        attribution: isDark
          ? '© OpenStreetMap contributors © CARTO'
          : '© OpenStreetMap contributors',
        maxZoom: 18,
      }
    ).addTo(mapInstanceRef.current)

    // Initialize marker cluster group - ONLY cluster same-facility incidents
    // Mixed locations will spiderfy instead of clustering to avoid confusing count numbers
    clusterRef.current = (L as any).markerClusterGroup({
      chunkedLoading: true,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: false,
      zoomToBoundsOnClick: true,
      spiderfyOnEveryZoom: true,
      spiderfyDistanceMultiplier: 2,
      maxClusterRadius: 30,
      disableClusteringAtZoom: 13,
      iconCreateFunction: function (cluster: any) {
        const count = cluster.getChildCount()
        const isDark = document.documentElement.classList.contains('dark')

        // Analyze cluster for facility context
        const markers = cluster.getAllChildMarkers()
        const incidentData = markers.map((m: any) => m.incidentData).filter(Boolean)

        // Check if all incidents are at the same facility
        const facilityTypes = new Set(incidentData.map((inc: any) => inc.asset_type))
        const facilityNames = new Set(incidentData.map((inc: any) => inc.location_name || inc.title).filter(Boolean))
        const isSameFacility = facilityTypes.size === 1 && incidentData.length > 0 && incidentData[0].asset_type

        const facilityType = isSameFacility ? Array.from(facilityTypes)[0] : null
        const facilityName = isSameFacility && facilityNames.size === 1 ? Array.from(facilityNames)[0] : null

        // Facility emoji mapping
        const facilityEmoji: Record<string, string> = {
          'airport': '✈️',
          'military': '🛡️',
          'harbor': '⚓',
          'powerplant': '⚡',
          'bridge': '🌉',
          'other': '📍'
        }

        // ONLY cluster same-facility incidents - force spiderfy for mixed locations
        if (isSameFacility && facilityType) {
          // Same facility cluster - use emerald/green gradient with emoji
          const gradient = 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
          const emoji = facilityEmoji[facilityType as string] || '📍'
          const label = count > 1 ? `${count} events` : 'event'
          const name = facilityName || (facilityType as string).charAt(0).toUpperCase() + (facilityType as string).slice(1)
          const tooltip = `${emoji} ${name} - ${label}`

          return L.divIcon({
            html: `
              <div style="
                width: 50px;
                height: 50px;
                background: ${gradient};
                border: 3px solid ${isDark ? '#1f2937' : 'white'};
                border-radius: 50%;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 14px;
                text-shadow: 0 1px 2px rgba(0,0,0,0.3);
                cursor: pointer;
                transition: transform 0.2s;
              " title="${tooltip}">
                <div style="font-size: 18px; line-height: 1;">${emoji}</div>
                <div style="font-size: 13px; margin-top: -2px;">${count}</div>
              </div>
            `,
            className: 'marker-cluster-facility',
            iconSize: [50, 50],
          })
        }

        // Mixed/nearby incidents - return null to force spiderfy instead of clustering
        // This prevents confusing cluster numbers (7, 8, etc.) that look like evidence scores
        return null as any
      },
    })

    if (clusterRef.current) {
      mapInstanceRef.current.addLayer(clusterRef.current)
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
      }
    }
  }, [center, zoom, resolvedTheme])

  // Update tile layer when theme changes
  useEffect(() => {
    if (!mapInstanceRef.current || !tileLayerRef.current) return

    const isDark = resolvedTheme === 'dark'

    // Remove old tile layer
    tileLayerRef.current.remove()

    // Add new tile layer based on theme
    tileLayerRef.current = L.tileLayer(
      isDark
        ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
        : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      {
        attribution: isDark
          ? '© OpenStreetMap contributors © CARTO'
          : '© OpenStreetMap contributors',
        maxZoom: 18,
      }
    ).addTo(mapInstanceRef.current)
  }, [resolvedTheme])

  useEffect(() => {
    if (!clusterRef.current) return

    // Clear existing markers
    clusterRef.current.clearLayers()

    const isDark = resolvedTheme === 'dark'

    // Add new markers
    incidents.forEach((incident) => {
      const icon = createIncidentIcon(incident.evidence_score, isDark)
      const marker = L.marker([incident.lat, incident.lon], { icon })

      // Attach incident data to marker for cluster analysis
      ;(marker as any).incidentData = incident

      // Create popup content
      const popupContent = createPopupContent(incident, isDark)
      marker.bindPopup(popupContent, {
        maxWidth: 350,
        className: 'incident-popup',
      })

      clusterRef.current!.addLayer(marker)
    })
  }, [incidents, resolvedTheme])

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

function createIncidentIcon(evidenceScore: number, isDark: boolean = false): L.DivIcon {
  const config = EVIDENCE_SYSTEM[evidenceScore as 1 | 2 | 3 | 4]
  const borderColor = isDark ? '#1f2937' : 'white'

  return L.divIcon({
    html: `
      <div style="
        width: 38px;
        height: 38px;
        background: ${config.gradient};
        border: 3px solid ${borderColor};
        border-radius: 50%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3), 0 0 20px ${config.glow};
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 15px;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      ">
        ${evidenceScore}
      </div>
    `,
    className: 'custom-marker',
    iconSize: [38, 38],
    iconAnchor: [19, 19],
  })
}

function createPopupContent(incident: Incident, isDark: boolean = false): string {
  const timeAgo = formatDistance(new Date(incident.occurred_at), new Date(), { addSuffix: true })
  const config = EVIDENCE_SYSTEM[incident.evidence_score as 1 | 2 | 3 | 4]

  // Theme-aware colors
  const textPrimary = isDark ? '#f3f4f6' : '#111827'
  const textSecondary = isDark ? '#9ca3af' : '#4b5563'
  const textMuted = isDark ? '#6b7280' : '#6b7280'
  const badgeBg = isDark ? 'rgba(55, 65, 81, 0.8)' : 'rgba(243, 244, 246, 0.8)'
  const badgeText = isDark ? '#d1d5db' : '#4b5563'
  const borderColor = isDark ? 'rgba(55, 65, 81, 0.5)' : 'rgba(229, 231, 235, 0.5)'
  const linkColor = isDark ? '#60a5fa' : '#2563eb'
  const linkBg = isDark ? 'rgba(37, 99, 235, 0.1)' : 'rgba(37, 99, 235, 0.08)'

  // Extract domain for favicon
  const getFavicon = (url: string) => {
    try {
      const domain = new URL(url).hostname
      return `https://www.google.com/s2/favicons?domain=${domain}&sz=16`
    } catch {
      return ''
    }
  }

  return `
    <div style="font-family: system-ui, -apple-system, sans-serif; padding: 4px;">
      <h3 style="margin: 0 0 10px 0; font-size: 17px; font-weight: 700; color: ${textPrimary}; line-height: 1.3;">
        ${incident.title}
      </h3>

      <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 12px; flex-wrap: wrap;">
        <span style="
          background: ${config.gradient};
          color: white;
          padding: 4px 10px;
          border-radius: 14px;
          font-size: 11px;
          font-weight: 700;
          letter-spacing: 0.3px;
          text-shadow: 0 1px 2px rgba(0,0,0,0.2);
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
          ${config.label}
        </span>
        ${incident.asset_type ? `
          <span style="
            background: ${badgeBg};
            color: ${badgeText};
            padding: 4px 10px;
            border-radius: 14px;
            font-size: 11px;
            font-weight: 600;
            backdrop-filter: blur(10px);
            border: 1px solid ${borderColor};
          ">
            ${incident.asset_type}
          </span>
        ` : ''}
        <span style="color: ${textMuted}; font-size: 11px; font-weight: 500;">
          ${timeAgo}
        </span>
      </div>

      ${incident.narrative ? `
        <p style="margin: 0 0 14px 0; color: ${textSecondary}; font-size: 13px; line-height: 1.6;">
          ${incident.narrative}
        </p>
      ` : ''}

      ${incident.sources && incident.sources.length > 0 ? `
        <div style="border-top: 1px solid ${borderColor}; padding-top: 10px; margin-top: 8px;">
          <div style="font-size: 11px; color: ${textMuted}; margin-bottom: 6px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Sources</div>
          <div style="display: flex; flex-direction: column; gap: 4px;">
            ${incident.sources.map(source => {
              const favicon = getFavicon(source.source_url)
              const typeEmojis: Record<string, string> = {
                'police': '🚔',
                'notam': '🛫',
                'media': '📰',
                'news': '📰',
                'social': '💬',
                'other': '🔗'
              }
              const emoji = typeEmojis[source.source_type?.toLowerCase() || 'other'] || '🔗'
              return `
                <a href="${source.source_url}" target="_blank" rel="noopener noreferrer" style="
                  display: inline-flex;
                  align-items: center;
                  gap: 6px;
                  padding: 4px 8px;
                  background: ${linkBg};
                  border-radius: 8px;
                  color: ${linkColor};
                  font-size: 12px;
                  text-decoration: none;
                  font-weight: 500;
                  transition: all 0.2s;
                  border: 1px solid ${borderColor};
                ">
                  ${favicon ? `<img src="${favicon}" width="14" height="14" style="border-radius: 2px;" />` : `<span style="font-size: 14px;">${emoji}</span>`}
                  <span>${source.source_type || 'Unknown'}</span>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-left: auto;">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/>
                  </svg>
                </a>
              `
            }).join('')}
          </div>
        </div>
      ` : ''}
    </div>
  `
}