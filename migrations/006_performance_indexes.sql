-- Performance indexes for DroneWatch API optimization
-- Target: Reduce query time from 11.4s to <3s

-- Index for main API query (evidence_score + occurred_at DESC)
-- Used by: /api/incidents?min_evidence=X&limit=Y
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_incidents_evidence_occurred
  ON public.incidents(evidence_score, occurred_at DESC)
  WHERE evidence_score >= 1;

-- Index for country + status filtering
-- Used by: /api/incidents?country=X&status=Y
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_incidents_country_status
  ON public.incidents(country, status)
  WHERE evidence_score >= 1;

-- Composite index for complex filtering
-- Used by: /api/incidents?country=X&status=Y&min_evidence=Z
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_incidents_composite
  ON public.incidents(country, status, evidence_score, occurred_at DESC)
  WHERE evidence_score >= 1;

-- Index for incident_sources junction table (already should exist, but ensuring)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_incident_sources_incident_id
  ON public.incident_sources(incident_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_incident_sources_source_id
  ON public.incident_sources(source_id);

-- Index for sources table lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sources_name
  ON public.sources(name);

-- Analyze tables to update statistics
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
