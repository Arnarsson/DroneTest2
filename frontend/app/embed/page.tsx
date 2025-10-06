"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import dynamic from "next/dynamic";
import { useIncidents } from "@/hooks/useIncidents";

const Map = dynamic(() => import("@/components/Map"), {
  ssr: false,
  loading: () => <div className="w-full h-full bg-gray-100 animate-pulse" />,
});

function EmbedContent() {
  const searchParams = useSearchParams();

  // Parse embed parameters
  const filters = {
    minEvidence: parseInt(searchParams.get("minEvidence") || "2"),
    country: searchParams.get("country") || "DK",
    status: searchParams.get("status") || "active",
    assetType: searchParams.get("assetType") || null,
    dateRange: "week" as const,
  };

  const { data: incidents, isLoading } = useIncidents(filters);

  return (
    <div className="w-full h-screen relative">
      <Map
        incidents={incidents ?? []}
        isLoading={isLoading}
        center={[56.0, 10.5]}
        zoom={6}
      />

      {/* Minimal branding */}
      <div className="absolute bottom-4 left-4 bg-white rounded shadow px-3 py-1 text-xs">
        <a
          href="https://dronewatch.cc"
          target="_blank"
          rel="noopener noreferrer"
          className="text-gray-600 hover:text-gray-900"
        >
          DroneWatch.cc
        </a>
      </div>

      {/* Incident count */}
      <div className="absolute top-4 right-4 bg-white rounded shadow px-3 py-2">
        <div className="text-sm font-medium">
          {isLoading ? "Loading..." : `${incidents?.length || 0} incidents`}
        </div>
      </div>
    </div>
  );
}

export default function EmbedPage() {
  return (
    <Suspense
      fallback={
        <div className="w-full h-screen bg-gray-100 animate-pulse flex items-center justify-center">
          <div className="text-gray-500">Loading...</div>
        </div>
      }
    >
      <EmbedContent />
    </Suspense>
  );
}
