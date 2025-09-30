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

    // Initialize marker cluster group
    clusterRef.current = (L as any).markerClusterGroup({
      chunkedLoading: true,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: false,
      maxClusterRadius: 50,
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
  const colors = {
    1: { from: '#9ca3af', to: '#6b7280', glow: 'rgba(156, 163, 175, 0.4)' },
    2: { from: '#fde047', to: '#facc15', glow: 'rgba(250, 204, 21, 0.5)' },
    3: { from: '#fb923c', to: '#ea580c', glow: 'rgba(234, 88, 12, 0.6)' },
    4: { from: '#f87171', to: '#dc2626', glow: 'rgba(220, 38, 38, 0.7)' },
  }

  const colorScheme = colors[evidenceScore as keyof typeof colors]
  const borderColor = isDark ? '#1f2937' : 'white'

  return L.divIcon({
    html: `
      <div style="
        width: 38px;
        height: 38px;
        background: radial-gradient(circle at 30% 30%, ${colorScheme.from}, ${colorScheme.to});
        border: 3px solid ${borderColor};
        border-radius: 50%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3), 0 0 20px ${colorScheme.glow};
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 15px;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: float 3s ease-in-out infinite;
      ">
        ${evidenceScore}
      </div>
    `,
    className: 'custom-marker gpu-accelerated',
    iconSize: [38, 38],
    iconAnchor: [19, 19],
  })
}

function createPopupContent(incident: Incident, isDark: boolean = false): string {
  const timeAgo = formatDistance(new Date(incident.occurred_at), new Date(), { addSuffix: true })

  const evidenceLabels = {
    1: 'Unverified',
    2: 'OSINT',
    3: 'Verified Media',
    4: 'Official',
  }

  const evidenceGradients = {
    1: 'linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)',
    2: 'linear-gradient(135deg, #fde047 0%, #facc15 100%)',
    3: 'linear-gradient(135deg, #fb923c 0%, #ea580c 100%)',
    4: 'linear-gradient(135deg, #f87171 0%, #dc2626 100%)',
  }

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
          background: ${evidenceGradients[incident.evidence_score as keyof typeof evidenceGradients]};
          color: white;
          padding: 4px 10px;
          border-radius: 14px;
          font-size: 11px;
          font-weight: 700;
          letter-spacing: 0.3px;
          text-shadow: 0 1px 2px rgba(0,0,0,0.2);
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
          ${evidenceLabels[incident.evidence_score as keyof typeof evidenceLabels]}
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
                  ${favicon ? `<img src="${favicon}" width="14" height="14" style="border-radius: 2px;" />` : ''}
                  <span>${source.source_type}</span>
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