"use client";

import { Analytics } from "@/components/Analytics";
import { AtlasBadge } from "@/components/AtlasBadge";
import { EvidenceLegend } from "@/components/EvidenceLegend";
import { FilterPanel } from "@/components/FilterPanel";
import { Header } from "@/components/Header";
import { IncidentList } from "@/components/IncidentList";
import { useIncidents } from "@/hooks/useIncidents";
import type { FilterState, Incident } from "@/types";
import { isWithinInterval } from "date-fns/isWithinInterval";
import { AnimatePresence, motion } from "framer-motion";
import dynamic from "next/dynamic";
import { useCallback, useMemo, useState } from "react";
import { Toaster } from "sonner";

// Dynamic import for map (no SSR)
const Map = dynamic(() => import("@/components/Map"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full bg-gray-100 dark:bg-gray-900 animate-pulse" />
  ),
});

export default function Home() {
  // Trigger Sentry test error on mount (REMOVE AFTER TESTING)
  if (typeof window !== 'undefined') {
    setTimeout(() => {
      // @ts-ignore - intentional error for Sentry testing
      myUndefinedFunction();
    }, 2000);
  }

  const [view, setView] = useState<"map" | "list" | "analytics">("map");
  const [isFilterPanelOpen, setIsFilterPanelOpen] = useState(false);
  const [timelineRange, setTimelineRange] = useState<{
    start: Date | null;
    end: Date | null;
  }>({
    start: null,
    end: null,
  });
  const [filters, setFilters] = useState<FilterState>({
    minEvidence: 1,
    country: "all",
    status: "all",
    assetType: null,
    dateRange: "all",
  });

  const { data: allIncidents, isLoading, error } = useIncidents(filters);

  // Apply client-side date filtering and timeline filtering
  const incidents = useMemo(() => {
    console.log('[page.tsx] useMemo triggered')
    console.log('[page.tsx] allIncidents:', allIncidents?.length || 0)
    console.log('[page.tsx] filters:', filters)
    console.log('[page.tsx] timelineRange:', timelineRange)

    if (!allIncidents) {
      console.log('[page.tsx] No allIncidents, returning empty array')
      return [];
    }

    console.log('[page.tsx] Starting with', allIncidents.length, 'incidents')
    let filtered = allIncidents;

    // Apply date range filter (client-side fallback)
    if (filters.dateRange !== "all") {
      const now = new Date();
      const since = new Date();

      switch (filters.dateRange) {
        case "day":
          since.setDate(now.getDate() - 1);
          break;
        case "week":
          since.setDate(now.getDate() - 7);
          break;
        case "month":
          since.setMonth(now.getMonth() - 1);
          break;
      }

      filtered = filtered.filter(
        (inc: Incident) => new Date(inc.occurred_at) >= since
      );
      console.log('[page.tsx] After date filter:', filtered.length, 'incidents')
    }

    // Apply timeline filtering
    if (timelineRange.start && timelineRange.end) {
      console.log('[page.tsx] Applying timeline filter')
      filtered = filtered.filter((inc: Incident) =>
        isWithinInterval(new Date(inc.occurred_at), {
          start: timelineRange.start!,
          end: timelineRange.end!,
        })
      );
      console.log('[page.tsx] After timeline filter:', filtered.length, 'incidents')
    }

    console.log('[page.tsx] Returning', filtered.length, 'incidents')
    return filtered;
  }, [allIncidents, timelineRange, filters.dateRange]);

  const handleFilterChange = useCallback((newFilters: FilterState) => {
    setFilters(newFilters);
  }, []);

  // DEBUG PANEL - Remove after fixing
  const debugInfo = {
    allIncidentsCount: allIncidents?.length || 0,
    filteredIncidentsCount: incidents?.length || 0,
    isLoading,
    hasError: !!error,
    filters: JSON.stringify(filters),
    timelineActive: !!(timelineRange.start && timelineRange.end)
  }

  return (
    <>
      <Toaster position="top-right" richColors />

      {/* DEBUG PANEL - VISIBLE ON SCREEN */}
      <div className="fixed top-16 right-4 z-[9999] bg-red-500 text-white p-4 rounded-lg shadow-2xl text-xs font-mono max-w-sm">
        <div className="font-bold mb-2">🐛 DEBUG INFO</div>
        <div>API Data: {debugInfo.allIncidentsCount} incidents</div>
        <div>Filtered: {debugInfo.filteredIncidentsCount} incidents</div>
        <div>Loading: {debugInfo.isLoading ? 'YES' : 'NO'}</div>
        <div>Error: {debugInfo.hasError ? 'YES' : 'NO'}</div>
        <div>Timeline: {debugInfo.timelineActive ? 'ACTIVE' : 'INACTIVE'}</div>
        <div className="mt-2 text-xs opacity-75">Filters: {debugInfo.filters}</div>
      </div>

      <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 via-gray-100 to-gray-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 transition-colors">
        <Header
          incidentCount={incidents?.length || 0}
          isLoading={isLoading}
          currentView={view}
          onViewChange={setView}
        />

        <main className="flex-1 relative overflow-hidden flex">
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="absolute top-0 left-0 right-0 z-10 bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800 px-4 py-2"
              >
                <p className="text-sm text-red-800 dark:text-red-200">
                  Error loading incidents. Retrying...
                </p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Main Content Area */}
          <motion.div
            className="flex-1 relative overflow-auto"
            key={view}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            {view === "map" ? (
              <>
                <Map
                  incidents={incidents || []}
                  isLoading={isLoading}
                  center={[56.0, 10.5]}
                  zoom={6}
                />
                <EvidenceLegend />
              </>
            ) : view === "list" ? (
              <IncidentList incidents={incidents || []} isLoading={isLoading} />
            ) : (
              <Analytics incidents={incidents || []} />
            )}
          </motion.div>

          {/* Filter Panel (Desktop: Sidebar, Mobile: Drawer) */}
          <FilterPanel
            filters={filters}
            onChange={handleFilterChange}
            incidentCount={incidents?.length || 0}
            isOpen={isFilterPanelOpen}
            onToggle={() => setIsFilterPanelOpen(!isFilterPanelOpen)}
          />
        </main>

        {/* Timeline at bottom - HIDDEN */}
        {/* <AnimatePresence>
          {view === 'map' && (
            <Timeline
              incidents={allIncidents || []}
              onTimeRangeChange={handleTimelineRangeChange}
              isOpen={isTimelineOpen}
              onToggle={() => setIsTimelineOpen(!isTimelineOpen)}
            />
          )}
        </AnimatePresence> */}

        {/* Atlas AI Badge */}
        <AtlasBadge />
      </div>
    </>
  );
}
