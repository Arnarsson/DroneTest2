import { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import 'leaflet.markercluster'
import { createClusterIcon } from './MarkerFactory'

// Fix Leaflet icon issue
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

/**
 * Custom hook for initializing Leaflet map
 *
 * @param mapRef - Ref to map container div
 * @param center - Initial map center [lat, lon]
 * @param zoom - Initial zoom level
 * @param resolvedTheme - Current theme (dark/light)
 * @returns Object with map instance, tile layer, and cluster group refs
 */
export function useMapSetup(
  mapRef: React.RefObject<HTMLDivElement>,
  center: [number, number],
  zoom: number,
  resolvedTheme?: string
) {
  const mapInstanceRef = useRef<L.Map | null>(null)
  const clusterRef = useRef<L.MarkerClusterGroup | null>(null)
  const tileLayerRef = useRef<L.TileLayer | null>(null)

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
        const isDark = document.documentElement.classList.contains('dark')
        return createClusterIcon(cluster, isDark)
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
  }, [mapRef, center, zoom, resolvedTheme])

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

  return {
    mapInstanceRef,
    clusterRef,
    tileLayerRef,
  }
}
