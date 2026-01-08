'use client'

import { useCallback, useEffect, useState } from 'react'
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
 * Handles browser back/forward navigation by listening to popstate events
 * in addition to using Next.js's useSearchParams for programmatic navigation.
 *
 * @returns Object containing:
 *   - filters: Current filter state (synced with URL)
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

  // Local state that syncs with URL - allows immediate updates on navigation
  const [filters, setLocalFilters] = useState<FilterState>(() =>
    parseFilterParams(searchParams)
  )

  // Update local state when searchParams changes (Next.js programmatic navigation)
  useEffect(() => {
    setLocalFilters(parseFilterParams(searchParams))
  }, [searchParams])

  // Handle browser back/forward navigation via popstate event
  // This ensures filter state updates even when Next.js doesn't fully detect URL changes
  useEffect(() => {
    const handlePopState = () => {
      // Read directly from window.location.search for immediate update
      const currentParams = new URLSearchParams(window.location.search)
      setLocalFilters(parseFilterParams(currentParams))
    }

    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  }, [])

  // Setter that updates both local state and URL search params
  const setFilters = useCallback(
    (newFilters: FilterState) => {
      // Update local state immediately for responsive UI
      setLocalFilters(newFilters)

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
