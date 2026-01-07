'use client'

import { useCallback, useMemo } from 'react'
import { useSearchParams, useRouter, usePathname } from 'next/navigation'
import type { FilterState } from '@/types'
import {
  DEFAULT_FILTER_STATE,
  parseFilterParams,
  serializeFilterParams,
} from '@/lib/urlFilterParams'

// Re-export DEFAULT_FILTER_STATE for backwards compatibility
export { DEFAULT_FILTER_STATE }

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
