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
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-[1000] bg-white dark:bg-gray-800 rounded-lg shadow-lg px-4 py-2">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-sm font-medium text-gray-900 dark:text-gray-100">Loading incidents...</span>
          </div>
        </div>
      )}
      <div ref={mapRef} className="w-full h-full" />
    </>
  )
}

function createIncidentIcon(evidenceScore: number, isDark: boolean = false): L.DivIcon {
  const colors = {
    1: '#9ca3af',
    2: '#facc15',
    3: '#ea580c',
    4: '#dc2626',
  }

  const color = colors[evidenceScore as keyof typeof colors]
  const borderColor = isDark ? '#1f2937' : 'white'

  return L.divIcon({
    html: `
      <div style="
        width: 32px;
        height: 32px;
        background: ${color};
        border: 3px solid ${borderColor};
        border-radius: 50%;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 14px;
      ">
        ${evidenceScore}
      </div>
    `,
    className: 'custom-marker',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
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

  const evidenceColors = {
    1: '#9ca3af',
    2: '#facc15',
    3: '#ea580c',
    4: '#dc2626',
  }

  // Theme-aware colors
  const textPrimary = isDark ? '#f3f4f6' : '#111827'
  const textSecondary = isDark ? '#9ca3af' : '#4b5563'
  const textMuted = isDark ? '#6b7280' : '#6b7280'
  const badgeBg = isDark ? '#374151' : '#f3f4f6'
  const badgeText = isDark ? '#d1d5db' : '#4b5563'
  const borderColor = isDark ? '#374151' : '#e5e7eb'
  const linkColor = isDark ? '#60a5fa' : '#2563eb'

  return `
    <div style="font-family: system-ui, -apple-system, sans-serif;">
      <h3 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 600; color: ${textPrimary};">
        ${incident.title}
      </h3>

      <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
        <span style="
          background: ${evidenceColors[incident.evidence_score as keyof typeof evidenceColors]};
          color: white;
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 600;
        ">
          ${evidenceLabels[incident.evidence_score as keyof typeof evidenceLabels]}
        </span>
        ${incident.asset_type ? `
          <span style="
            background: ${badgeBg};
            color: ${badgeText};
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
          ">
            ${incident.asset_type}
          </span>
        ` : ''}
        <span style="color: ${textMuted}; font-size: 12px;">
          ${timeAgo}
        </span>
      </div>

      ${incident.narrative ? `
        <p style="margin: 0 0 12px 0; color: ${textSecondary}; font-size: 14px; line-height: 1.5;">
          ${incident.narrative}
        </p>
      ` : ''}

      ${incident.sources && incident.sources.length > 0 ? `
        <div style="border-top: 1px solid ${borderColor}; padding-top: 8px;">
          <div style="font-size: 12px; color: ${textMuted}; margin-bottom: 4px;">Sources:</div>
          ${incident.sources.map(source => `
            <a href="${source.source_url}" target="_blank" rel="noopener noreferrer" style="
              display: inline-block;
              margin-right: 8px;
              color: ${linkColor};
              font-size: 12px;
              text-decoration: none;
            ">
              ${source.source_type} →
            </a>
          `).join('')}
        </div>
      ` : ''}
    </div>
  `
}