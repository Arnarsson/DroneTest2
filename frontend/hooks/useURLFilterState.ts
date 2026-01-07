'use client'

import { useCallback, useMemo } from 'react'
import { useSearchParams, useRouter, usePathname } from 'next/navigation'
import type { FilterState } from '@/types'

/**
 * Default filter values used when URL params are missing or invalid
 */
export const DEFAULT_FILTER_STATE: FilterState = {
  minEvidence: 1,
  country: 'all',
  status: 'all',
  assetType: null,
  dateRange: 'all',
}

/**
 * Valid values for dateRange filter
 */
const VALID_DATE_RANGES = ['day', 'week', 'month', 'all'] as const

/**
 * URL parameter key mapping (snake_case to match API conventions)
 */
const URL_PARAM_KEYS = {
  minEvidence: 'min_evidence',
  country: 'country',
  status: 'status',
  assetType: 'asset_type',
  dateRange: 'date_range',
} as const

/**
 * Parse and validate minEvidence value from URL
 * Valid range is 1-4, defaults to 1 if invalid
 */
function parseMinEvidence(value: string | null): number {
  if (!value) return DEFAULT_FILTER_STATE.minEvidence
  const parsed = parseInt(value, 10)
  if (isNaN(parsed) || parsed < 1 || parsed > 4) {
    return DEFAULT_FILTER_STATE.minEvidence
  }
  return parsed
}

/**
 * Parse and validate dateRange value from URL
 * Must be one of: 'day', 'week', 'month', 'all'
 */
function parseDateRange(value: string | null): FilterState['dateRange'] {
  if (!value) return DEFAULT_FILTER_STATE.dateRange
  if (VALID_DATE_RANGES.includes(value as FilterState['dateRange'])) {
    return value as FilterState['dateRange']
  }
  return DEFAULT_FILTER_STATE.dateRange
}

/**
 * Parse assetType from URL (can be null)
 */
function parseAssetType(value: string | null): string | null {
  if (!value || value === 'null' || value === '') return null
  return value
}

/**
 * Parse filter state from URL search params
 */
function parseFilterParams(searchParams: URLSearchParams): FilterState {
  return {
    minEvidence: parseMinEvidence(searchParams.get(URL_PARAM_KEYS.minEvidence)),
    country: searchParams.get(URL_PARAM_KEYS.country) || DEFAULT_FILTER_STATE.country,
    status: searchParams.get(URL_PARAM_KEYS.status) || DEFAULT_FILTER_STATE.status,
    assetType: parseAssetType(searchParams.get(URL_PARAM_KEYS.assetType)),
    dateRange: parseDateRange(searchParams.get(URL_PARAM_KEYS.dateRange)),
  }
}

/**
 * Serialize filter state to URL search params
 * Only includes non-default values to keep URLs clean
 */
function serializeFilterParams(filters: FilterState): URLSearchParams {
  const params = new URLSearchParams()

  // Only add params that differ from defaults to keep URLs clean
  if (filters.minEvidence !== DEFAULT_FILTER_STATE.minEvidence) {
    params.set(URL_PARAM_KEYS.minEvidence, filters.minEvidence.toString())
  }
  if (filters.country !== DEFAULT_FILTER_STATE.country) {
    params.set(URL_PARAM_KEYS.country, filters.country)
  }
  if (filters.status !== DEFAULT_FILTER_STATE.status) {
    params.set(URL_PARAM_KEYS.status, filters.status)
  }
  if (filters.assetType !== DEFAULT_FILTER_STATE.assetType) {
    params.set(URL_PARAM_KEYS.assetType, filters.assetType!)
  }
  if (filters.dateRange !== DEFAULT_FILTER_STATE.dateRange) {
    params.set(URL_PARAM_KEYS.dateRange, filters.dateRange)
  }

  return params
}

/**
 * Hook that syncs FilterState with URL search parameters
 *
 * @returns Object containing:
 *   - filters: Current filter state (derived from URL)
 *   - setFilters: Function to update both state and URL
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { filters, setFilters } = useURLFilterState()
 *
 *   const handleFilterChange = (newFilters: FilterState) => {
 *     setFilters(newFilters)
 *   }
 *
 *   return <FilterPanel filters={filters} onChange={handleFilterChange} />
 * }
 * ```
 */
export function useURLFilterState() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const pathname = usePathname()

  // Derive filter state from URL search params
  const filters = useMemo(() => {
    return parseFilterParams(searchParams)
  }, [searchParams])

  // Setter that updates URL search params
  const setFilters = useCallback(
    (newFilters: FilterState) => {
      const params = serializeFilterParams(newFilters)
      const queryString = params.toString()

      // Build new URL - use pathname without query if all defaults
      const newUrl = queryString ? `${pathname}?${queryString}` : pathname

      // Use replace to avoid cluttering browser history
      router.replace(newUrl, { scroll: false })
    },
    [router, pathname]
  )

  return { filters, setFilters }
}
