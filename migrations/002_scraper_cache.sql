-- Migration: Scraper processed incidents cache
-- Description: Create table to track processed incidents for deduplication
-- Replaces: ingestion/processed_incidents.json file-based cache

BEGIN;

-- Create scraper_cache table to store incident hashes
CREATE TABLE IF NOT EXISTS public.scraper_cache (
  id SERIAL PRIMARY KEY,
  incident_hash VARCHAR(32) NOT NULL UNIQUE,
  title VARCHAR(500),
  occurred_at TIMESTAMPTZ,
  source_name VARCHAR(200),
  processed_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for fast lookups
CREATE INDEX IF NOT EXISTS scraper_cache_hash_idx ON public.scraper_cache(incident_hash);
CREATE INDEX IF NOT EXISTS scraper_cache_processed_at_idx ON public.scraper_cache(processed_at);

-- Add cleanup function to remove old cache entries (older than 30 days)
CREATE OR REPLACE FUNCTION public.cleanup_old_scraper_cache()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  DELETE FROM public.scraper_cache
  WHERE processed_at < NOW() - INTERVAL '30 days';
END;
$$;

-- Create table for scraper metrics
CREATE TABLE IF NOT EXISTS public.scraper_metrics (
  id SERIAL PRIMARY KEY,
  run_id UUID DEFAULT gen_random_uuid(),
  scraper_type VARCHAR(50) NOT NULL, -- 'police' or 'media'
  source_key VARCHAR(100) NOT NULL,
  source_name VARCHAR(200),
  incidents_found INTEGER DEFAULT 0,
  incidents_ingested INTEGER DEFAULT 0,
  incidents_skipped INTEGER DEFAULT 0,
  errors INTEGER DEFAULT 0,
  error_message TEXT,
  execution_time_ms INTEGER,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Create indexes for metrics queries
CREATE INDEX IF NOT EXISTS scraper_metrics_run_id_idx ON public.scraper_metrics(run_id);
CREATE INDEX IF NOT EXISTS scraper_metrics_started_at_idx ON public.scraper_metrics(started_at);
CREATE INDEX IF NOT EXISTS scraper_metrics_source_key_idx ON public.scraper_metrics(source_key);

COMMIT;

-- Add helpful comments
COMMENT ON TABLE public.scraper_cache IS
'Stores MD5 hashes of processed incidents to prevent duplicate ingestion. Replaces file-based cache.';

COMMENT ON TABLE public.scraper_metrics IS
'Tracks scraper performance metrics for monitoring and debugging.';

-- Verification queries:
/*
-- View recent scraper runs
SELECT
  run_id,
  scraper_type,
  COUNT(*) as sources_checked,
  SUM(incidents_found) as total_found,
  SUM(incidents_ingested) as total_ingested,
  SUM(errors) as total_errors,
  MAX(started_at) as run_time
FROM public.scraper_metrics
GROUP BY run_id, scraper_type, started_at
ORDER BY started_at DESC
LIMIT 10;

-- View cache size
SELECT COUNT(*) as cached_incidents,
       MIN(processed_at) as oldest_entry,
       MAX(processed_at) as newest_entry
FROM public.scraper_cache;

-- View source performance
SELECT
  source_key,
  source_name,
  AVG(incidents_found) as avg_incidents,
  AVG(execution_time_ms) as avg_time_ms,
  SUM(errors) as total_errors
FROM public.scraper_metrics
WHERE started_at > NOW() - INTERVAL '7 days'
GROUP BY source_key, source_name
ORDER BY avg_incidents DESC;
*/