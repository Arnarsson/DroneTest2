-- Migration 015: Create scraper_cache table
-- Purpose: Enable persistent caching for scraper results to improve performance

CREATE TABLE IF NOT EXISTS public.scraper_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_hash VARCHAR(64) NOT NULL UNIQUE,
    title TEXT,
    occurred_at TIMESTAMP WITH TIME ZONE,
    source_name VARCHAR(255),
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for efficient lookups
CREATE INDEX IF NOT EXISTS idx_scraper_cache_incident_hash ON public.scraper_cache(incident_hash);
CREATE INDEX IF NOT EXISTS idx_scraper_cache_processed_at ON public.scraper_cache(processed_at);
CREATE INDEX IF NOT EXISTS idx_scraper_cache_occurred_at ON public.scraper_cache(occurred_at);

-- Add comment
COMMENT ON TABLE public.scraper_cache IS 'Caches scraper results to prevent duplicate processing and improve performance';

-- Enable RLS (Row Level Security)
ALTER TABLE public.scraper_cache ENABLE ROW LEVEL SECURITY;

-- Create policy for public read access
CREATE POLICY "anon_read_scraper_cache" ON public.scraper_cache
    FOR SELECT
    USING (true);

-- Create policy for service role write access (scrapers need this)
CREATE POLICY "service_write_scraper_cache" ON public.scraper_cache
    FOR ALL
    USING (true);
