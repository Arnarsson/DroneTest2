'use client'

import { useEffect, useRef } from 'react'
import { useTheme } from 'next-themes'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import 'leaflet.markercluster'
import type { Incident } from '@/types'
import { formatDistance } from 'date-fns/formatDistance'
import { format } from 'date-fns/format'
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
          // Same facility cluster - use neutral slate gradient (NOT evidence color)
          const gradient = isDark
            ? 'linear-gradient(135deg, #475569 0%, #334155 100%)'  // slate-600 to slate-700
            : 'linear-gradient(135deg, #64748b 0%, #475569 100%)'  // slate-500 to slate-600
          const emoji = facilityEmoji[facilityType as string] || '📍'
          const label = count > 1 ? `${count} incidents` : 'incident'
          const name = facilityName || (facilityType as string).charAt(0).toUpperCase() + (facilityType as string).slice(1)
          const tooltip = `${emoji} ${name} - ${label}`

          return L.divIcon({
            html: `
              <div style="
                width: 54px;
                height: 54px;
                background: ${gradient};
                border: 3px solid ${isDark ? '#0f172a' : 'white'};
                border-radius: 50%;
                box-shadow: 0 4px 12px rgba(0,0,0,0.4), inset 0 1px 2px rgba(255,255,255,0.1);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 14px;
                text-shadow: 0 1px 3px rgba(0,0,0,0.5);
                cursor: pointer;
                transition: transform 0.2s;
                position: relative;
              " title="${tooltip}">
                <div style="font-size: 20px; line-height: 1; margin-bottom: 2px;">${emoji}</div>
                <div style="
                  position: absolute;
                  bottom: -8px;
                  right: -8px;
                  background: ${isDark ? '#dc2626' : '#ef4444'};
                  color: white;
                  border-radius: 12px;
                  padding: 2px 6px;
                  font-size: 11px;
                  font-weight: bold;
                  border: 2px solid ${isDark ? '#0f172a' : 'white'};
                  box-shadow: 0 2px 6px rgba(0,0,0,0.4);
                ">${count}</div>
              </div>
            `,
            className: 'marker-cluster-facility',
            iconSize: [54, 54],
          })
        }

        // Mixed/nearby incidents - Don't cluster, force spiderfy
        // Return a single-marker icon to prevent clustering but this shouldn't be reached
        // because we'll use a custom cluster function that prevents mixed clustering
        const firstMarker = markers[0]
        if (firstMarker && firstMarker.incidentData) {
          // Just show the first marker's icon - cluster will spiderfy automatically
          const incident = firstMarker.incidentData
          const config = EVIDENCE_SYSTEM[incident.evidence_score as 1 | 2 | 3 | 4]
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
                ${incident.evidence_score}
              </div>
            `,
            className: 'custom-marker',
            iconSize: [38, 38],
            iconAnchor: [19, 19],
          })
        }

        // Fallback - this shouldn't happen
        return L.divIcon({
          html: '<div></div>',
          className: 'empty-marker',
          iconSize: [0, 0],
        })
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

    // Pre-process incidents to group by facility
    // Group key: coordinates (rounded to 3 decimals ~110m) + asset_type
    const facilityGroups: { [key: string]: Incident[] } = {}
    const singleIncidents: Incident[] = []

    incidents.forEach((incident) => {
      // Group by coordinates + asset_type (if asset_type exists)
      if (incident.asset_type) {
        // Round coordinates to 2 decimals (~1.1km precision) to group nearby incidents
        const roundedLat = incident.lat.toFixed(2)
        const roundedLon = incident.lon.toFixed(2)
        const facilityKey = `${roundedLat},${roundedLon}-${incident.asset_type}`

        if (!facilityGroups[facilityKey]) {
          facilityGroups[facilityKey] = []
        }
        facilityGroups[facilityKey].push(incident)
      } else {
        singleIncidents.push(incident)
      }
    })

    // Add facility group markers (2+ incidents at same facility)
    Object.entries(facilityGroups).forEach(([facilityKey, groupIncidents]) => {
      if (groupIncidents.length >= 2) {
        // Create facility cluster marker
        const firstIncident = groupIncidents[0]
        const facilityMarker = createFacilityMarker(
          groupIncidents,
          firstIncident.lat,
          firstIncident.lon,
          isDark
        )
        clusterRef.current!.addLayer(facilityMarker)
      } else {
        // Single incident at this facility - treat as regular marker
        singleIncidents.push(groupIncidents[0])
      }
    })

    // Add single incident markers
    singleIncidents.forEach((incident) => {
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

function createFacilityMarker(
  incidents: Incident[],
  lat: number,
  lon: number,
  isDark: boolean = false
): L.Marker {
  const count = incidents.length
  const assetType = incidents[0].asset_type
  const locationName = incidents[0].location_name

  // Facility emoji mapping
  const facilityEmoji: Record<string, string> = {
    'airport': '✈️',
    'military': '🛡️',
    'harbor': '⚓',
    'powerplant': '⚡',
    'bridge': '🌉',
    'other': '📍'
  }

  const emoji = facilityEmoji[assetType || 'other'] || '📍'
  // Use neutral slate gradient (NOT evidence color) to avoid confusion with legend
  const gradient = isDark
    ? 'linear-gradient(135deg, #475569 0%, #334155 100%)'  // slate-600 to slate-700
    : 'linear-gradient(135deg, #64748b 0%, #475569 100%)'  // slate-500 to slate-600
  const borderColor = isDark ? '#0f172a' : 'white'

  const icon = L.divIcon({
    html: `
      <div style="
        width: 50px;
        height: 50px;
        background: ${gradient};
        border: 3px solid ${borderColor};
        border-radius: 50%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4), inset 0 1px 2px rgba(255,255,255,0.1);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 14px;
        text-shadow: 0 1px 3px rgba(0,0,0,0.5);
        cursor: pointer;
        transition: transform 0.2s;
      ">
        <div style="font-size: 18px; line-height: 1;">${emoji}</div>
        <div style="font-size: 13px; margin-top: -2px;">${count}</div>
      </div>
    `,
    className: 'marker-cluster-facility',
    iconSize: [50, 50],
    iconAnchor: [25, 25],
  })

  const marker = L.marker([lat, lon], { icon })

  // Create popup with all incidents at this facility
  const popupContent = createFacilityPopup(incidents, locationName || assetType || 'Facility', emoji, isDark)
  marker.bindPopup(popupContent, {
    maxWidth: 400,
    className: 'incident-popup',
  })

  return marker
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
      <h3 style="
        margin: 0 0 10px 0;
        font-size: 17px;
        font-weight: 700;
        color: ${textPrimary};
        line-height: 1.3;
        max-width: 100%;
        word-wrap: break-word;
        overflow-wrap: break-word;
      ">
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
          ${timeAgo} · ${format(new Date(incident.occurred_at), 'dd MMM yyyy HH:mm')}
        </span>
      </div>

      <!-- Visual divider after metadata -->
      <hr style="border: 0; border-top: 1px solid ${borderColor}; margin: 12px 0;" />

      ${incident.narrative ? `
        <p style="margin: 0 0 14px 0; color: ${textSecondary}; font-size: 13px; line-height: 1.6;">
          ${incident.narrative}
        </p>
        <!-- Visual divider after narrative -->
        <hr style="border: 0; border-top: 1px solid ${borderColor}; margin: 12px 0;" />
      ` : ''}

      ${incident.sources && incident.sources.length > 0 ? `
        <div style="border-top: 1px solid ${borderColor}; padding-top: 10px; margin-top: 8px;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
            <div style="font-size: 11px; color: ${textMuted}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
              Sources ${incident.sources.length > 1 ? `(${incident.sources.length})` : ''}
            </div>
            ${incident.sources.length >= 2 ? `
              <div style="
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: 700;
                display: inline-flex;
                align-items: center;
                gap: 4px;
              ">
                ✓ Multi-source verified
              </div>
            ` : ''}
          </div>
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

              // FIX: Normalize trust weight to 0-1 scale (handles both 0-1 and 1-4 scales)
              const trustWeight = source.trust_weight || 0
              const normalizedTrust = trustWeight > 1 ? trustWeight / 4 : trustWeight
              const trustPercentage = Math.round(normalizedTrust * 100)
              const trustColor = normalizedTrust >= 0.8 ? '#10b981' : normalizedTrust >= 0.6 ? '#f59e0b' : '#6b7280'

              const sourceName = source.source_title || source.source_name || source.source_type || 'Unknown'
              const sourceQuote = (source as any).source_quote || null
              const domain = new URL(source.source_url).hostname.replace('www.', '')

              return `
                <div style="
                  padding: 12px;
                  background: ${isDark ? 'rgba(31, 41, 55, 0.5)' : 'rgba(249, 250, 251, 0.8)'};
                  border: 1px solid ${borderColor};
                  border-radius: 10px;
                  margin-bottom: 8px;
                ">
                  ${sourceQuote ? `
                    <!-- 1. SOURCE QUOTE FIRST (blockquoted, primary element) -->
                    <blockquote style="
                      border-left: 4px solid #3b82f6;
                      padding-left: 12px;
                      margin: 0 0 10px 0;
                      font-style: italic;
                      color: ${textSecondary};
                      font-size: 13px;
                      line-height: 1.5;
                      font-weight: 500;
                    ">
                      "${sourceQuote.length > 150 ? sourceQuote.substring(0, 150) + '...' : sourceQuote}"
                    </blockquote>
                  ` : ''}

                  <!-- 2. SOURCE NAME + TRUST BADGE (secondary info) -->
                  <div style="display: flex; align-items: center; justify-between; margin-bottom: 10px;">
                    <div style="display: flex; align-items: center; gap: 6px;">
                      ${favicon ? `<img src="${favicon}" width="14" height="14" style="border-radius: 2px;" />` : `<span style="font-size: 14px;">${emoji}</span>`}
                      <span style="font-size: 13px; font-weight: 600; color: ${textPrimary};">
                        ${sourceName}
                      </span>
                      <span style="
                        font-size: 10px;
                        color: ${textMuted};
                        cursor: help;
                      " title="Domain: ${domain} | Type: ${source.source_type || 'unknown'}">
                        ℹ️
                      </span>
                    </div>
                    ${trustWeight > 0 ? `
                      <span style="
                        background: ${trustColor};
                        color: white;
                        padding: 3px 8px;
                        border-radius: 12px;
                        font-size: 10px;
                        font-weight: 700;
                      ">
                        ${trustPercentage}%
                      </span>
                    ` : ''}
                  </div>

                  <!-- 3. "VIEW SOURCE" BUTTON (prominent CTA) -->
                  <a href="${source.source_url}" target="_blank" rel="noopener noreferrer" aria-label="View source: ${sourceName}" style="
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    padding: 8px 14px;
                    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 600;
                    transition: transform 0.2s, box-shadow 0.2s;
                    box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
                  " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 8px rgba(37, 99, 235, 0.3)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 4px rgba(37, 99, 235, 0.2)'">
                    View Source
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/>
                    </svg>
                  </a>
                </div>
              `
            }).join('')}
          </div>
        </div>
      ` : ''}

      <!-- Action buttons -->
      <div style="
        display: flex;
        gap: 8px;
        margin-top: 16px;
        padding-top: 12px;
        border-top: 1px solid ${borderColor};
      ">
        <button
          onclick="navigator.clipboard.writeText('https://dronewatch.cc/embed?incident=${incident.id}'); alert('Embed code copied to clipboard!');"
          style="
            flex: 1;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            padding: 8px 12px;
            background: ${isDark ? 'rgba(55, 65, 81, 0.8)' : 'rgba(243, 244, 246, 0.8)'};
            color: ${textPrimary};
            border: 1px solid ${borderColor};
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            font-family: system-ui, -apple-system, sans-serif;
          "
          onmouseover="this.style.background='${isDark ? 'rgba(75, 85, 99, 0.9)' : 'rgba(229, 231, 235, 0.9)'}'"
          onmouseout="this.style.background='${isDark ? 'rgba(55, 65, 81, 0.8)' : 'rgba(243, 244, 246, 0.8)'}'"
          aria-label="Copy embed code for this incident"
        >
          📋 Copy Embed
        </button>
        <button
          onclick="window.open('https://github.com/Arnarsson/DroneWatch2.0/issues/new?title=Report%20Incident%20${incident.id}&body=Incident%20ID:%20${incident.id}%0ATitle:%20${encodeURIComponent(incident.title)}', '_blank');"
          style="
            flex: 1;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            padding: 8px 12px;
            background: ${isDark ? 'rgba(55, 65, 81, 0.8)' : 'rgba(243, 244, 246, 0.8)'};
            color: ${textPrimary};
            border: 1px solid ${borderColor};
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            font-family: system-ui, -apple-system, sans-serif;
          "
          onmouseover="this.style.background='${isDark ? 'rgba(75, 85, 99, 0.9)' : 'rgba(229, 231, 235, 0.9)'}'"
          onmouseout="this.style.background='${isDark ? 'rgba(55, 65, 81, 0.8)' : 'rgba(243, 244, 246, 0.8)'}'"
          aria-label="Report an issue with this incident"
        >
          ⚠️ Report
        </button>
      </div>
    </div>
  `
}

function createFacilityPopup(
  incidents: Incident[],
  facilityName: string,
  emoji: string,
  isDark: boolean = false
): string {
  const textPrimary = isDark ? '#f3f4f6' : '#111827'
  const textSecondary = isDark ? '#9ca3af' : '#4b5563'
  const borderColor = isDark ? 'rgba(55, 65, 81, 0.5)' : 'rgba(229, 231, 235, 0.5)'

  // Sort incidents by date (newest first)
  const sortedIncidents = [...incidents].sort((a, b) =>
    new Date(b.occurred_at).getTime() - new Date(a.occurred_at).getTime()
  )

  return `
    <div style="font-family: system-ui, -apple-system, sans-serif; padding: 4px;">
      <h3 style="margin: 0 0 10px 0; font-size: 17px; font-weight: 700; color: ${textPrimary}; line-height: 1.3;">
        ${emoji} ${facilityName}
      </h3>

      <div style="margin-bottom: 12px; padding: 8px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 8px;">
        <div style="color: white; font-size: 13px; font-weight: 600; text-align: center;">
          ${incidents.length} incident${incidents.length !== 1 ? 's' : ''} at this location
        </div>
      </div>

      <div style="max-height: 300px; overflow-y: auto;">
        ${sortedIncidents.map((incident, idx) => {
          const config = EVIDENCE_SYSTEM[incident.evidence_score as 1 | 2 | 3 | 4]
          const timeAgo = formatDistance(new Date(incident.occurred_at), new Date(), { addSuffix: true })

          return `
            <div
              onclick="event.stopPropagation();"
              style="
                padding: 10px;
                margin-bottom: 8px;
                border: 1px solid ${borderColor};
                border-radius: 8px;
                background: ${isDark ? 'rgba(55, 65, 81, 0.3)' : 'rgba(243, 244, 246, 0.5)'};
                cursor: pointer;
                transition: all 0.2s;
                position: relative;
              "
              onmouseover="this.style.background='${isDark ? 'rgba(75, 85, 99, 0.5)' : 'rgba(229, 231, 235, 0.7)'}'; this.style.borderColor='${config.color}';"
              onmouseout="this.style.background='${isDark ? 'rgba(55, 65, 81, 0.3)' : 'rgba(243, 244, 246, 0.5)'}'; this.style.borderColor='${borderColor}';"
            >
              <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                <div style="display: flex; align-items: center; gap: 6px;">
                  <span style="
                    background: ${config.gradient};
                    color: white;
                    padding: 4px 10px;
                    border-radius: 14px;
                    font-size: 11px;
                    font-weight: 700;
                    text-shadow: 0 1px 2px rgba(0,0,0,0.2);
                  ">
                    ${config.label}
                  </span>
                  <span style="color: ${textSecondary}; font-size: 11px; font-weight: 500;">
                    ${timeAgo}
                  </span>
                </div>
                <!-- Chevron indicator -->
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="${textSecondary}"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  style="flex-shrink: 0;"
                >
                  <path d="M9 18l6-6-6-6"/>
                </svg>
              </div>

              <div style="font-size: 13px; color: ${textPrimary}; font-weight: 600; margin-bottom: 4px;">
                ${incident.title}
              </div>

              ${incident.narrative ? `
                <div style="font-size: 12px; color: ${textSecondary}; line-height: 1.4;">
                  ${incident.narrative.substring(0, 120)}${incident.narrative.length > 120 ? '...' : ''}
                </div>
              ` : ''}
            </div>
          `
        }).join('')}
      </div>
    </div>
  `
}