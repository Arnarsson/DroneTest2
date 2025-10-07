-- Migration 015: Optimize Sources Query Performance
-- Created: 2025-10-06
-- Purpose: Add indexes to dramatically improve sources subquery performance
-- Expected improvement: 11s → <2s for incidents API

-- Add index on incident_sources for fast lookup by incident_id
CREATE INDEX IF NOT EXISTS idx_incident_sources_incident_id
ON public.incident_sources(incident_id);

-- Add index on sources for fast lookup by id (for LEFT JOIN)
CREATE INDEX IF NOT EXISTS idx_sources_id
ON public.sources(id);

-- Add composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_incident_sources_incident_source
ON public.incident_sources(incident_id, source_id);

-- Add index on incidents for common filters
CREATE INDEX IF NOT EXISTS idx_incidents_evidence_status
ON public.incidents(evidence_score, verification_status);

-- Add index for date range queries
CREATE INDEX IF NOT EXISTS idx_incidents_occurred_at
ON public.incidents(occurred_at DESC);

-- Add index for country filtering
CREATE INDEX IF NOT EXISTS idx_incidents_country
ON public.incidents(country);

-- Add index for asset_type filtering
CREATE INDEX IF NOT EXISTS idx_incidents_asset_type
ON public.incidents(asset_type);

-- Analyze tables to update statistics for query planner
ANALYZE public.incidents;
ANALYZE public.incident_sources;
ANALYZE public.sources;

-- Verify indexes were created
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename IN ('incidents', 'incident_sources', 'sources')
ORDER BY tablename, indexname;
