import L from 'leaflet'
import { EVIDENCE_SYSTEM } from '@/constants/evidence'
import { getFacilityEmoji } from './FacilityGrouper'

/**
 * Creates an evidence-based marker icon for a single incident
 *
 * @param evidenceScore - Evidence score (1-4)
 * @param isDark - Whether dark mode is active
 * @returns Leaflet DivIcon
 */
export function createIncidentIcon(evidenceScore: number, isDark: boolean = false): L.DivIcon {
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

/**
 * Creates a facility cluster icon for multiple incidents at same location
 *
 * @param count - Number of incidents at facility
 * @param assetType - Type of facility (airport, military, etc.)
 * @param isDark - Whether dark mode is active
 * @returns Leaflet DivIcon
 */
export function createFacilityIcon(
  count: number,
  assetType: string,
  isDark: boolean = false
): L.DivIcon {
  const emoji = getFacilityEmoji(assetType)
  // Use neutral slate gradient (NOT evidence color) to avoid confusion with legend
  const gradient = isDark
    ? 'linear-gradient(135deg, #475569 0%, #334155 100%)'  // slate-600 to slate-700
    : 'linear-gradient(135deg, #64748b 0%, #475569 100%)'  // slate-500 to slate-600
  const borderColor = isDark ? '#0f172a' : 'white'

  return L.divIcon({
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
}

/**
 * Creates a cluster icon for automatically clustered markers
 * Used by Leaflet.markercluster for same-facility grouping
 *
 * @param cluster - Leaflet marker cluster
 * @param isDark - Whether dark mode is active
 * @returns Leaflet DivIcon
 */
export function createClusterIcon(cluster: any, isDark: boolean): L.DivIcon {
  const count = cluster.getChildCount()

  // Analyze cluster for facility context
  const markers = cluster.getAllChildMarkers()
  const incidentData = markers.map((m: any) => m.incidentData).filter(Boolean)

  // Check if all incidents are at the same facility
  const facilityTypes = new Set(incidentData.map((inc: any) => inc.asset_type))
  const facilityNames = new Set(incidentData.map((inc: any) => inc.location_name || inc.title).filter(Boolean))
  const isSameFacility = facilityTypes.size === 1 && incidentData.length > 0 && incidentData[0].asset_type

  const facilityType = isSameFacility ? Array.from(facilityTypes)[0] : null
  const facilityName = isSameFacility && facilityNames.size === 1 ? Array.from(facilityNames)[0] : null

  // ONLY cluster same-facility incidents - force spiderfy for mixed locations
  if (isSameFacility && facilityType) {
    // Same facility cluster - use neutral slate gradient (NOT evidence color)
    const gradient = isDark
      ? 'linear-gradient(135deg, #475569 0%, #334155 100%)'  // slate-600 to slate-700
      : 'linear-gradient(135deg, #64748b 0%, #475569 100%)'  // slate-500 to slate-600
    const emoji = getFacilityEmoji(facilityType as string)
    const label = count > 1 ? `${count} incidents` : 'incident'
    const name = facilityName || (facilityType as string).charAt(0).toUpperCase() + (facilityType as string).slice(1)
    const tooltip = `${emoji} ${name} - ${label}`

    return L.divIcon({
      html: `
        <div style="
          width: 50px;
          height: 50px;
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
        " title="${tooltip}">
          <div style="font-size: 18px; line-height: 1;">${emoji}</div>
          <div style="font-size: 13px; margin-top: -2px;">${count}</div>
        </div>
      `,
      className: 'marker-cluster-facility',
      iconSize: [50, 50],
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
}
