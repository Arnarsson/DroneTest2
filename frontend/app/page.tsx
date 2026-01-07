"use client";

import { Analytics } from "@/components/Analytics";
import { AtlasBadge } from "@/components/AtlasBadge";
import { EvidenceLegend } from "@/components/EvidenceLegend";
import { FilterPanel } from "@/components/FilterPanel";
import { Header } from "@/components/Header";
import { IncidentList } from "@/components/IncidentList";
import { useIncidents } from "@/hooks/useIncidents";
import { useKeyboardShortcuts, SHORTCUT_KEYS } from "@/hooks/useKeyboardShortcuts";
import type { FilterState, Incident } from "@/types";
import { isWithinInterval } from "date-fns/isWithinInterval";
import { AnimatePresence, motion } from "framer-motion";
import dynamic from "next/dynamic";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Toaster } from "sonner";

// Dynamic import for map (no SSR)
const Map = dynamic(() => import("@/components/Map"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full bg-gray-100 dark:bg-gray-900 animate-pulse" />
  ),
});

// Human-readable labels for view names
const VIEW_LABELS: Record<"map" | "list" | "analytics", string> = {
  map: "Map view",
  list: "List view",
  analytics: "Analytics view",
};

export default function Home() {
  const [view, setView] = useState<"map" | "list" | "analytics">("map");
  const [isFilterPanelOpen, setIsFilterPanelOpen] = useState(false);
  // Screen reader announcement message
  const [announcement, setAnnouncement] = useState("");
  const announcementTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
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
    searchQuery: "",
  });

  const { data: allIncidents, isLoading, error } = useIncidents(filters);

  // Apply client-side date filtering and timeline filtering
  const incidents = useMemo(() => {
    if (!allIncidents) {
      return [];
    }

    let filtered = allIncidents;

    // Apply date range filter (client-side fallback)
    if (filters.dateRange && filters.dateRange !== "all") {
      const now = new Date();
      const since = new Date();
      let shouldFilter = true;

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
        default:
          shouldFilter = false;
      }

      if (shouldFilter) {
        filtered = filtered.filter(
          (inc: Incident) => new Date(inc.occurred_at) >= since
        );
      }
    }

    // Apply timeline filtering
    if (timelineRange.start && timelineRange.end) {
      filtered = filtered.filter((inc: Incident) =>
        isWithinInterval(new Date(inc.occurred_at), {
          start: timelineRange.start!,
          end: timelineRange.end!,
        })
      );
    }

    return filtered;
  }, [allIncidents, timelineRange, filters.dateRange]);

  const handleFilterChange = useCallback((newFilters: FilterState) => {
    setFilters(newFilters);
  }, []);

  // Announce changes to screen readers
  const announce = useCallback((message: string) => {
    // Clear any pending announcement timeout
    if (announcementTimeoutRef.current) {
      clearTimeout(announcementTimeoutRef.current);
    }
    // Set the new announcement
    setAnnouncement(message);
    // Clear the announcement after a delay to allow re-announcing the same message
    announcementTimeoutRef.current = setTimeout(() => {
      setAnnouncement("");
    }, 1000);
  }, []);

  // Cleanup announcement timeout on unmount
  useEffect(() => {
    return () => {
      if (announcementTimeoutRef.current) {
        clearTimeout(announcementTimeoutRef.current);
      }
    };
  }, []);

  // Keyboard shortcuts for view switching, filter panel, and quick filters
  const keyboardShortcuts = useMemo(
    () => ({
      // View switching shortcuts
      [SHORTCUT_KEYS.MAP_VIEW]: () => {
        setView("map");
        announce(VIEW_LABELS.map);
      },
      [SHORTCUT_KEYS.LIST_VIEW]: () => {
        setView("list");
        announce(VIEW_LABELS.list);
      },
      [SHORTCUT_KEYS.ANALYTICS_VIEW]: () => {
        setView("analytics");
        announce(VIEW_LABELS.analytics);
      },
      // Filter panel toggle
      [SHORTCUT_KEYS.FILTER_TOGGLE]: () => {
        setIsFilterPanelOpen((prev) => {
          const newState = !prev;
          announce(newState ? "Filter panel opened" : "Filter panel closed");
          return newState;
        });
      },
      // Quick filter shortcuts
      // A: Toggle airports filter
      a: () => {
        setFilters((prev) => ({
          ...prev,
          assetType: prev.assetType === "airport" ? null : "airport",
        }));
        announce(filters.assetType === "airport" ? "Airport filter disabled" : "Airport filter enabled");
      },
      // M: Toggle military filter
      m: () => {
        setFilters((prev) => ({
          ...prev,
          assetType: prev.assetType === "military" ? null : "military",
        }));
        announce(filters.assetType === "military" ? "Military filter disabled" : "Military filter enabled");
      },
      // T: Toggle today (last 24 hours) filter
      t: () => {
        setFilters((prev) => ({
          ...prev,
          dateRange: prev.dateRange === "day" ? "all" : "day",
        }));
        announce(filters.dateRange === "day" ? "Today filter disabled" : "Today filter enabled");
      },
      // V: Toggle verified (3+ evidence) filter
      v: () => {
        setFilters((prev) => ({
          ...prev,
          minEvidence: prev.minEvidence >= 3 ? 1 : 3,
        }));
        announce(filters.minEvidence >= 3 ? "Verified filter disabled" : "Verified filter enabled");
      },
      // R: Reset all filters
      r: () => {
        setFilters({
          minEvidence: 1,
          country: "all",
          status: "all",
          assetType: null,
          dateRange: "all",
          searchQuery: "",
        });
        announce("All filters reset");
      },
    }),
    [announce, filters.assetType, filters.dateRange, filters.minEvidence]
  );

  // Register keyboard shortcuts
  useKeyboardShortcuts(keyboardShortcuts);

  return (
    <>
      <Toaster position="top-right" richColors />

      {/* Screen reader announcements for keyboard shortcuts */}
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      >
        {announcement}
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
                <div className="flex items-center justify-between">
                  <p className="text-sm text-red-800 dark:text-red-200">
                    {error.message || 'Error loading incidents. Retrying...'}
                  </p>
                  {isLoading && (
                    <span className="text-xs text-red-600 dark:text-red-400 ml-2">
                      Retrying...
                    </span>
                  )}
                </div>
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
