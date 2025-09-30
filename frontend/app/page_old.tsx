'use client'

import { useState, useCallback, useMemo } from 'react'
import dynamic from 'next/dynamic'
import { Header } from '@/components/Header'
import { Filters } from '@/components/Filters'
import { IncidentList } from '@/components/IncidentList'
import { Timeline } from '@/components/Timeline'
import { Analytics } from '@/components/Analytics'
import { useIncidents } from '@/hooks/useIncidents'
import { isWithinInterval } from 'date-fns'
import type { FilterState, Incident } from '@/types'

// Dynamic import for map (no SSR)
const Map = dynamic(() => import('@/components/Map'), {
  ssr: false,
  loading: () => <div className="w-full h-full bg-gray-100 animate-pulse" />
})

export default function Home() {
  const [view, setView] = useState<'map' | 'list' | 'analytics'>('map')
  const [isTimelineOpen, setIsTimelineOpen] = useState(false)
  const [timelineRange, setTimelineRange] = useState<{ start: Date | null; end: Date | null }>({
    start: null,
    end: null,
  })
  const [filters, setFilters] = useState<FilterState>({
    minEvidence: 1,
    country: 'all',
    status: 'all',
    assetType: null,
    dateRange: 'all'
  })

  const { data: allIncidents, isLoading, error } = useIncidents(filters)

  // Apply timeline filtering on top of regular filters
  const incidents = useMemo(() => {
    if (!allIncidents) return []
    if (!timelineRange.start || !timelineRange.end) return allIncidents

    return allIncidents.filter((inc: Incident) =>
      isWithinInterval(new Date(inc.occurred_at), {
        start: timelineRange.start!,
        end: timelineRange.end!,
      })
    )
  }, [allIncidents, timelineRange])

  const handleFilterChange = useCallback((newFilters: FilterState) => {
    setFilters(newFilters)
  }, [])

  const handleTimelineRangeChange = useCallback((start: Date | null, end: Date | null) => {
    setTimelineRange({ start, end })
  }, [])

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-950 transition-colors">
      <Header incidentCount={incidents?.length || 0} isLoading={isLoading} />

      <Filters
        filters={filters}
        onChange={handleFilterChange}
        view={view}
        onViewChange={setView}
      />

      <main className="flex-1 relative overflow-hidden flex flex-col">
        {error && (
          <div className="absolute top-0 left-0 right-0 z-10 bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800 px-4 py-2">
            <p className="text-sm text-red-800 dark:text-red-200">
              Error loading incidents. Retrying...
            </p>
          </div>
        )}

        <div className="flex-1 relative overflow-auto">
          {view === 'map' ? (
            <Map
              incidents={incidents || []}
              isLoading={isLoading}
              center={[56.0, 10.5]}
              zoom={6}
            />
          ) : view === 'list' ? (
            <IncidentList
              incidents={incidents || []}
              isLoading={isLoading}
            />
          ) : (
            <Analytics incidents={incidents || []} />
          )}
        </div>

        {/* Timeline at bottom */}
        <Timeline
          incidents={allIncidents || []}
          onTimeRangeChange={handleTimelineRangeChange}
          isOpen={isTimelineOpen}
          onToggle={() => setIsTimelineOpen(!isTimelineOpen)}
        />
      </main>
    </div>
  )
}