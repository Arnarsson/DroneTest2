'use client'

import { useState, useCallback } from 'react'
import dynamic from 'next/dynamic'
import { Header } from '@/components/Header'
import { Filters } from '@/components/Filters'
import { IncidentList } from '@/components/IncidentList'
import { useIncidents } from '@/hooks/useIncidents'
import type { FilterState } from '@/types'

// Dynamic import for map (no SSR)
const Map = dynamic(() => import('@/components/Map'), {
  ssr: false,
  loading: () => <div className="w-full h-full bg-gray-100 animate-pulse" />
})

export default function Home() {
  const [view, setView] = useState<'map' | 'list'>('map')
  const [filters, setFilters] = useState<FilterState>({
    minEvidence: 2,
    country: 'DK',
    status: 'active',
    assetType: null,
    dateRange: 'week'
  })

  const { data: incidents, isLoading, error } = useIncidents(filters)

  const handleFilterChange = useCallback((newFilters: FilterState) => {
    setFilters(newFilters)
  }, [])

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <Header incidentCount={incidents?.length || 0} isLoading={isLoading} />

      <Filters
        filters={filters}
        onChange={handleFilterChange}
        view={view}
        onViewChange={setView}
      />

      <main className="flex-1 relative overflow-hidden">
        {error && (
          <div className="absolute top-0 left-0 right-0 z-10 bg-red-50 border-b border-red-200 px-4 py-2">
            <p className="text-sm text-red-800">
              Error loading incidents. Retrying...
            </p>
          </div>
        )}

        {view === 'map' ? (
          <Map
            incidents={incidents || []}
            isLoading={isLoading}
            center={[56.0, 10.5]}
            zoom={6}
          />
        ) : (
          <IncidentList
            incidents={incidents || []}
            isLoading={isLoading}
          />
        )}
      </main>
    </div>
  )
}