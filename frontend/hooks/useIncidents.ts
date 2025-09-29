import { useQuery } from '@tanstack/react-query'
import type { Incident, FilterState } from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

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

  const response = await fetch(`${API_URL}/incidents?${params}`)

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }

  return response.json()
}

export function useIncidents(filters: FilterState) {
  return useQuery({
    queryKey: ['incidents', filters],
    queryFn: () => fetchIncidents(filters),
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  })
}