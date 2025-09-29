'use client'

import { useEffect, useRef } from 'react'
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

  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return

    // Initialize map
    mapInstanceRef.current = L.map(mapRef.current).setView(center, zoom)

    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 18,
    }).addTo(mapInstanceRef.current)

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
  }, [center, zoom])

  useEffect(() => {
    if (!clusterRef.current) return

    // Clear existing markers
    clusterRef.current.clearLayers()

    // Add new markers
    incidents.forEach((incident) => {
      const icon = createIncidentIcon(incident.evidence_score)
      const marker = L.marker([incident.lat, incident.lon], { icon })

      // Create popup content
      const popupContent = createPopupContent(incident)
      marker.bindPopup(popupContent, {
        maxWidth: 350,
        className: 'incident-popup',
      })

      clusterRef.current!.addLayer(marker)
    })
  }, [incidents])

  return (
    <>
      {isLoading && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-[1000] bg-white rounded-lg shadow-lg px-4 py-2">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-sm font-medium">Loading incidents...</span>
          </div>
        </div>
      )}
      <div ref={mapRef} className="w-full h-full" />
    </>
  )
}

function createIncidentIcon(evidenceScore: number): L.DivIcon {
  const colors = {
    1: '#9ca3af',
    2: '#facc15',
    3: '#ea580c',
    4: '#dc2626',
  }

  const color = colors[evidenceScore as keyof typeof colors]

  return L.divIcon({
    html: `
      <div style="
        width: 32px;
        height: 32px;
        background: ${color};
        border: 3px solid white;
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

function createPopupContent(incident: Incident): string {
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

  return `
    <div style="font-family: system-ui, -apple-system, sans-serif;">
      <h3 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 600; color: #111827;">
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
            background: #f3f4f6;
            color: #4b5563;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
          ">
            ${incident.asset_type}
          </span>
        ` : ''}
        <span style="color: #6b7280; font-size: 12px;">
          ${timeAgo}
        </span>
      </div>

      ${incident.narrative ? `
        <p style="margin: 0 0 12px 0; color: #4b5563; font-size: 14px; line-height: 1.5;">
          ${incident.narrative}
        </p>
      ` : ''}

      ${incident.sources && incident.sources.length > 0 ? `
        <div style="border-top: 1px solid #e5e7eb; padding-top: 8px;">
          <div style="font-size: 12px; color: #6b7280; margin-bottom: 4px;">Sources:</div>
          ${incident.sources.map(source => `
            <a href="${source.source_url}" target="_blank" rel="noopener noreferrer" style="
              display: inline-block;
              margin-right: 8px;
              color: #2563eb;
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