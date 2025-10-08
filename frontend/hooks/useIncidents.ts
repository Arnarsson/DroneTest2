import { useQuery } from '@tanstack/react-query'
import type { Incident, FilterState } from '@/types'

const DEFAULT_RELATIVE_API = '/api'
const REMOTE_FALLBACK_API = 'https://www.dronemap.cc/api'

const isDevelopment = process.env.NODE_ENV === 'development'
const explicitApi = process.env.NEXT_PUBLIC_API_URL
const hasLocalDatabase = Boolean(process.env.DATABASE_URL)

const apiCandidates = [
  explicitApi,
  !explicitApi && isDevelopment && !hasLocalDatabase ? REMOTE_FALLBACK_API : null,
  DEFAULT_RELATIVE_API,
  isDevelopment ? REMOTE_FALLBACK_API : null,
].filter((value, index, arr): value is string => Boolean(value) && arr.indexOf(value) === index)

function buildUrl(base: string, params: URLSearchParams) {
  const normalizedBase = base.endsWith('/') ? base.slice(0, -1) : base
  return `${normalizedBase}/incidents?${params}`
}

function isRecoverableNetworkError(error: unknown) {
  if (error instanceof TypeError) {
    return true
  }

  if (error instanceof Error) {
    return /network/i.test(error.message)
  }

  return false
}

async function requestIncidents(baseUrl: string, params: URLSearchParams) {
  const response = await fetch(buildUrl(baseUrl, params))

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }

  return response.json()
}

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

  let lastError: unknown

  for (const base of apiCandidates) {
    try {
      return await requestIncidents(base, params)
    } catch (error) {
      if (isRecoverableNetworkError(error)) {
        lastError = error
        continue
      }
      throw error
    }
  }

  throw lastError instanceof Error
    ? lastError
    : new Error('Unable to load incidents: all API endpoints failed')
}

export function useIncidents(filters: FilterState) {
  return useQuery<Incident[]>({
    queryKey: ['incidents', filters],
    queryFn: () => fetchIncidents(filters),
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  })
}
