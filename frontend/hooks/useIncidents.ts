import { useQuery } from '@tanstack/react-query'
import type { Incident, FilterState } from '@/types'
import { ENV } from '@/lib/env'

// Use NEXT_PUBLIC_API_URL from environment configuration
// This ensures frontend points to the correct API endpoint
const API_URL = ENV.API_URL

async function fetchIncidents(filters: FilterState): Promise<Incident[]> {
  console.log('[useIncidents] ========== FETCH START ==========')
  console.log('[useIncidents] Timestamp:', new Date().toISOString())

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
  console.log('[useIncidents] Full URL:', url)
  console.log('[useIncidents] API_URL base:', API_URL)
  console.log('[useIncidents] Filters:', JSON.stringify(filters))

  try {
    console.log('[useIncidents] Starting fetch...')
    const response = await fetch(url)
    console.log('[useIncidents] Fetch complete!')
    console.log('[useIncidents] Response status:', response.status, response.statusText)
    console.log('[useIncidents] Response headers:', Object.fromEntries(response.headers.entries()))

    if (!response.ok) {
      console.error('[useIncidents] API error:', response.status, response.statusText)
      throw new Error(`API error: ${response.status}`)
    }

    console.log('[useIncidents] Parsing JSON...')
    const data = await response.json()
    console.log('[useIncidents] JSON parsed successfully!')
    console.log('[useIncidents] Received incidents:', data.length)
    console.log('[useIncidents] Sample incident:', data[0])
    console.log('[useIncidents] ========== FETCH SUCCESS ==========')

    // CRITICAL DEBUG: Log what we're actually returning
    if (data.length === 0) {
      console.error('[useIncidents] WARNING: API returned empty array!')
    }

    return data
  } catch (error) {
    console.error('[useIncidents] ========== FETCH ERROR ==========')
    console.error('[useIncidents] Error:', error)
    console.error('[useIncidents] Error type:', typeof error)
    console.error('[useIncidents] Error details:', JSON.stringify(error, null, 2))
    throw error
  }
}

export function useIncidents(filters: FilterState) {
  return useQuery<Incident[]>({
    queryKey: ['incidents', filters],
    queryFn: () => fetchIncidents(filters),
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  })
}