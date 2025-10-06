-- Migration 015: Version Tracking and Metrics
-- Adds columns to track scraper versions and validation confidence scores
-- This enables monitoring of scraper deployments and filter effectiveness

-- CONTEXT:
-- We need to know which scraper version ingested each incident to detect
-- when old code is running. Confidence scores help measure filter quality.

-- Verify table exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'incidents') THEN
        RAISE EXCEPTION 'Table public.incidents does not exist! Check your database connection.';
    END IF;
END $$;

-- Add scraper_version column
ALTER TABLE public.incidents
ADD COLUMN IF NOT EXISTS scraper_version VARCHAR(20) DEFAULT NULL;

-- Add validation_confidence column (0.00-1.00 score)
ALTER TABLE public.incidents
ADD COLUMN IF NOT EXISTS validation_confidence DECIMAL(3,2) DEFAULT NULL;

-- Add ingested_at timestamp
ALTER TABLE public.incidents
ADD COLUMN IF NOT EXISTS ingested_at TIMESTAMPTZ DEFAULT NOW();

-- Create index for version queries
CREATE INDEX IF NOT EXISTS idx_incidents_scraper_version
ON public.incidents(scraper_version);

-- Create index for recent incidents
CREATE INDEX IF NOT EXISTS idx_incidents_ingested_at
ON public.incidents(ingested_at DESC);

-- Log migration success
DO $$
BEGIN
    RAISE NOTICE 'Version tracking columns added successfully';
    RAISE NOTICE 'scraper_version: Track which code version ingested incident';
    RAISE NOTICE 'validation_confidence: Track filter confidence (0.00-1.00)';
    RAISE NOTICE 'ingested_at: Track when incident was added to database';
END $$;

-- VERIFICATION:
-- Check columns exist:
-- SELECT column_name, data_type FROM information_schema.columns
-- WHERE table_name = 'incidents' AND column_name IN ('scraper_version', 'validation_confidence', 'ingested_at');
