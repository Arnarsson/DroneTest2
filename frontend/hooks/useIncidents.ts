import { useQuery } from '@tanstack/react-query'
import type { Incident, FilterState } from '@/types'

// Use relative API URL - the API is in the same deployment
// Force relative URL to avoid CORS issues with Vercel preview URLs
// For local dev without DATABASE_URL, use production API
const API_URL = process.env.NODE_ENV === 'development' && !process.env.DATABASE_URL
  ? 'https://www.dronemap.cc/api'
  : '/api'

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
  console.log('[useIncidents] Fetching from:', url)
  console.log('[useIncidents] API_URL:', API_URL)
  console.log('[useIncidents] Filters:', filters)

  const response = await fetch(url)
  console.log('[useIncidents] Response status:', response.status, response.statusText)

  if (!response.ok) {
    console.error('[useIncidents] API error:', response.status, response.statusText)
    throw new Error(`API error: ${response.status}`)
  }

  const data = await response.json()
  console.log('[useIncidents] Received incidents:', data.length)
  return data
}

export function useIncidents(filters: FilterState) {
  return useQuery<Incident[]>({
    queryKey: ['incidents', filters],
    queryFn: () => fetchIncidents(filters),
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  })
}