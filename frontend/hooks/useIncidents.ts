import { useQuery } from '@tanstack/react-query'
import type { Incident, FilterState } from '@/types'
import { ENV } from '@/lib/env'
import * as Sentry from '@sentry/nextjs'

// Use NEXT_PUBLIC_API_URL from environment configuration
// This ensures frontend points to the correct API endpoint
const API_URL = ENV.API_URL

async function fetchIncidents(filters: FilterState): Promise<Incident[]> {
  return Sentry.startSpan(
    {
      op: "http.client",
      name: "GET /api/incidents",
    },
    async (span) => {
      // Add span attributes for Sentry monitoring
      span.setAttribute("api_url", API_URL)
      span.setAttribute("filters", JSON.stringify(filters))

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
      // Client-side filtering is handled in page.tsx to prevent API 500 errors with 'since' param
      /* 
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
      */

      const url = `${API_URL}/incidents?${params}`

      try {
        const response = await fetch(url, {
          cache: 'no-store', // Disable browser cache for API calls
          headers: {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
          },
        })
        span.setAttribute("http.status_code", response.status)

        if (!response.ok) {
          Sentry.captureException(new Error(`API error: ${response.status}`))
          throw new Error(`API error: ${response.status}`)
        }

        const data = await response.json()
        span.setAttribute("incident_count", data.length)

        // Monitor for empty responses
        if (data.length === 0) {
          Sentry.captureMessage('API returned empty array', {
            level: 'warning',
            extra: { url, filters }
          })
        }

        return data
      } catch (error) {
        Sentry.captureException(error, {
          extra: { url, filters, api_url: API_URL }
        })
        throw error
      }
    }
  )
}

export function useIncidents(filters: FilterState) {
  return useQuery<Incident[], Error, Incident[]>({
    queryKey: ['incidents', filters],
    queryFn: () => fetchIncidents(filters),
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    staleTime: 0, // Always fetch fresh data
    gcTime: 1000 * 60 * 5, // Garbage collection time - cache for 5 minutes after unmount
    refetchOnMount: true, // Refetch when component mounts
    refetchOnWindowFocus: true, // Refetch when window regains focus
    refetchOnReconnect: true, // Refetch when network reconnects
  })
}
