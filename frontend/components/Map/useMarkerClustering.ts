import { useEffect } from 'react'
import L from 'leaflet'
import type { Incident } from '@/types'
import { groupIncidentsByFacility, getFacilityEmoji } from './FacilityGrouper'
import { createIncidentIcon, createFacilityIcon } from './MarkerFactory'
import { createPopupContent, createFacilityPopup } from './PopupFactory'
import { logger } from '@/lib/logger'

/**
 * Custom hook for managing marker clustering on the map
 *
 * @param incidents - Array of incidents to display
 * @param clusterRef - Ref to Leaflet marker cluster group
 * @param resolvedTheme - Current theme (dark/light)
 */
export function useMarkerClustering(
  incidents: Incident[],
  clusterRef: React.RefObject<L.MarkerClusterGroup | null>,
  resolvedTheme?: string
) {
  useEffect(() => {
    logger.debug('[Map] Incidents useEffect triggered with', incidents.length, 'incidents')

    if (!clusterRef.current) {
      logger.debug('[Map] No clusterRef, skipping marker creation')
      return
    }

    // Clear existing markers
    clusterRef.current.clearLayers()

    const isDark = resolvedTheme === 'dark'

    // Pre-process incidents to group by facility
    // Group key: coordinates (rounded to 3 decimals ~110m) + asset_type
    const { facilityGroups, singleIncidents } = groupIncidentsByFacility(incidents)

    // Add facility group markers (2+ incidents at same facility)
    Object.entries(facilityGroups).forEach(([facilityKey, groupIncidents]) => {
      if (groupIncidents.length >= 2) {
        // Create facility cluster marker
        const firstIncident = groupIncidents[0]
        const facilityMarker = createFacilityMarker(
          groupIncidents,
          firstIncident.lat,
          firstIncident.lon,
          isDark,
          clusterRef
        )
        clusterRef.current!.addLayer(facilityMarker)
      } else {
        // Single incident at this facility - treat as regular marker
        singleIncidents.push(groupIncidents[0])
      }
    })

    // Add single incident markers
    singleIncidents.forEach((incident) => {
      // Pass the full incident object to enable source count badges
      const icon = createIncidentIcon(incident.evidence_score, isDark, incident)
      const marker = L.marker([incident.lat, incident.lon], { icon })

      // Attach incident data to marker for cluster analysis
      ;(marker as any).incidentData = incident

      // Create popup content
      // DEBUG: Log incident data to verify sources
      if (incident.sources && incident.sources.length > 0) {
        logger.debug(`[Map] Incident "${incident.title.substring(0, 50)}" has ${incident.sources.length} sources`)
      } else {
        logger.warn(`[Map] Incident "${incident.title.substring(0, 50)}" has NO sources!`, incident)
      }
      const popupContent = createPopupContent(incident, isDark)
      marker.bindPopup(popupContent, {
        maxWidth: 350,
        className: 'incident-popup',
      })

      clusterRef.current!.addLayer(marker)
    })

    logger.debug('[Map] Added', Object.keys(facilityGroups).length, 'facility groups')
    logger.debug('[Map] Added', singleIncidents.length, 'single incident markers')
    logger.debug('[Map] Total markers created:', Object.keys(facilityGroups).length + singleIncidents.length)
  }, [incidents, clusterRef, resolvedTheme])
}

/**
 * Creates a facility marker with popup
 *
 * @param incidents - Array of incidents at this facility
 * @param lat - Latitude
 * @param lon - Longitude
 * @param isDark - Whether dark mode is active
 * @param clusterRef - Cluster group ref for adding marker
 * @returns Leaflet Marker
 */
function createFacilityMarker(
  incidents: Incident[],
  lat: number,
  lon: number,
  isDark: boolean,
  clusterRef: React.RefObject<L.MarkerClusterGroup | null>
): L.Marker {
  const count = incidents.length
  const assetType = incidents[0].asset_type || 'other'
  const locationName = incidents[0].location_name

  const icon = createFacilityIcon(count, assetType, isDark)
  const marker = L.marker([lat, lon], { icon })

  // Create popup with all incidents at this facility
  const emoji = getFacilityEmoji(assetType)
  const popupContent = createFacilityPopup(incidents, locationName || assetType || 'Facility', emoji, isDark)
  marker.bindPopup(popupContent, {
    maxWidth: 400,
    className: 'incident-popup',
  })

  return marker
}
