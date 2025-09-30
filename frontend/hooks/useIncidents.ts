import { useQuery } from '@tanstack/react-query'
import type { Incident, FilterState } from '@/types'

// Use relative API URL - the API is now in the same deployment
const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api'

async function fetchIncidents(filters: FilterState): Promise<Incident[]> {
  const params = new URLSearchParams({
    min_evidence: filters.minEvidence.toString(),
    country: filters.country,
    status: filters.status,
    limit: '500'
  })

  if (filters.assetType) {
    params.append('asset_type', filters.assetType)
  }

  // Add date range
  const now = new Date()
  if (filters.dateRange !== 'all') {
    const since = new Date()
    switch (filters.dateRange) {
      case 'day':
        since.setDate(now.getDate() - 1)
        break
      case 'week':
        since.setDate(now.getDate() - 7)
        break
      case 'month':
        since.setMonth(now.getMonth() - 1)
        break
    }
    params.append('since', since.toISOString())
  }

  const url = `${API_URL}/incidents?${params}`
  console.log('[DroneWatch] Fetching incidents from:', url)
  console.log('[DroneWatch] Filters:', filters)

  const response = await fetch(url)

  console.log('[DroneWatch] Response status:', response.status, response.statusText)
  console.log('[DroneWatch] Response headers:', Object.fromEntries(response.headers.entries()))

  if (!response.ok) {
    const errorText = await response.text()
    console.error('[DroneWatch] API error response:', errorText)
    throw new Error(`API error: ${response.status} - ${errorText}`)
  }

  const data = await response.json()
  console.log('[DroneWatch] Received incidents:', data.length)
  return data
}

export function useIncidents(filters: FilterState) {
  return useQuery({
    queryKey: ['incidents', filters],
    queryFn: () => fetchIncidents(filters),
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  })
}