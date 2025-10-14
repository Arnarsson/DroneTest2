import type { Incident } from '@/types'

export interface FacilityGroup {
  [facilityKey: string]: Incident[]
}

/**
 * Groups incidents by facility location and asset type
 *
 * @param incidents - Array of incidents to group
 * @returns Object with facilityKey as key and array of incidents as value
 *
 * Facility key format: `${lat.toFixed(3)},${lon.toFixed(3)}-${asset_type}`
 * - Coordinates rounded to 3 decimals (~110m precision)
 * - Includes asset_type to prevent cross-type grouping
 */
export function groupIncidentsByFacility(incidents: Incident[]): {
  facilityGroups: FacilityGroup
  singleIncidents: Incident[]
} {
  const facilityGroups: FacilityGroup = {}
  const singleIncidents: Incident[] = []

  incidents.forEach((incident) => {
    // Group by coordinates + asset_type (if asset_type exists)
    if (incident.asset_type) {
      // Round coordinates to 3 decimals (~110m precision) to group nearby incidents
      const roundedLat = incident.lat.toFixed(3)
      const roundedLon = incident.lon.toFixed(3)
      const facilityKey = `${roundedLat},${roundedLon}-${incident.asset_type}`

      if (!facilityGroups[facilityKey]) {
        facilityGroups[facilityKey] = []
      }
      facilityGroups[facilityKey].push(incident)
    } else {
      singleIncidents.push(incident)
    }
  })

  return { facilityGroups, singleIncidents }
}

/**
 * Facility emoji mapping by asset type
 */
export const FACILITY_EMOJI: Record<string, string> = {
  'airport': '✈️',
  'military': '🛡️',
  'harbor': '⚓',
  'powerplant': '⚡',
  'bridge': '🌉',
  'other': '📍'
}

/**
 * Get emoji for facility type
 * @param assetType - Asset type string
 * @returns Emoji character
 */
export function getFacilityEmoji(assetType?: string): string {
  return FACILITY_EMOJI[assetType || 'other'] || '📍'
}
