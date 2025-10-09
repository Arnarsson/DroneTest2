-- Migration 016: Remove Duplicate Incidents and Add Source Constraints
-- Date: 2025-10-09
-- Purpose: Clean up duplicate incidents and prevent future duplicates via database constraints

BEGIN;

-- ============================================================================
-- STEP 1: Merge Aalborg Airport Duplicates
-- ============================================================================
-- Two incidents at same location (57.093, 9.849):
-- - KEEP: 43bedf09-104c-4841-a3d2-fe517f0d078e (Oct 7, current, 1 source)
-- - REMOVE: f38b86ba-c96e-4cf6-a254-af58779dc94f (Sept 24, old, 2 sources)
--
-- The duplicate has 2 sources:
-- - https://x.com/NjylPoliti/status/1970958976557973603 (unique - transfer)
-- - https://x.com/NjylPoliti/status/1971346044035400063 (already in primary - delete)
--
-- Strategy: Transfer unique source, delete duplicate source, delete old incident

-- First, delete the source that already exists in the primary incident
DELETE FROM incident_sources
WHERE incident_id = 'f38b86ba-c96e-4cf6-a254-af58779dc94f'
  AND source_url = 'https://x.com/NjylPoliti/status/1971346044035400063';

-- Now transfer the unique source from duplicate to primary incident
UPDATE incident_sources
SET incident_id = '43bedf09-104c-4841-a3d2-fe517f0d078e'
WHERE incident_id = 'f38b86ba-c96e-4cf6-a254-af58779dc94f';

-- Delete the old duplicate incident (no time range update needed)
DELETE FROM incidents WHERE id = 'f38b86ba-c96e-4cf6-a254-af58779dc94f';

-- ============================================================================
-- STEP 2: Merge Copenhagen Airport Duplicates
-- ============================================================================
-- Two incidents at same location (55.618, 12.648):
-- - KEEP: 94040e97-2849-4a72-9fc0-59c61a8fabd9 (Oct 7, current, 1 source)
-- - REMOVE: e92d7a8f-f3dc-4178-9ef5-a5fe27a54f05 (Sept 23, old, 1 source)
--
-- The duplicate has 1 source:
-- - https://x.com/Rigspoliti/status/1970514696793960722 (unique - transfer)
--
-- Strategy: Transfer unique source, delete old incident

-- Transfer source from duplicate to primary incident
UPDATE incident_sources
SET incident_id = '94040e97-2849-4a72-9fc0-59c61a8fabd9'
WHERE incident_id = 'e92d7a8f-f3dc-4178-9ef5-a5fe27a54f05';

-- Delete the old duplicate incident (no time range update needed)
DELETE FROM incidents WHERE id = 'e92d7a8f-f3dc-4178-9ef5-a5fe27a54f05';

-- ============================================================================
-- STEP 3: Remove Duplicate Source Entries
-- ============================================================================
-- incident_sources table has duplicate source URLs (same URL linked to multiple incidents)
-- Keep only the first occurrence of each source_url

-- Create temporary table with unique sources (keep oldest entry per URL)
CREATE TEMP TABLE unique_sources AS
SELECT DISTINCT ON (source_url) *
FROM incident_sources
ORDER BY source_url, fetched_at ASC NULLS LAST, id ASC;

-- Delete all source entries
DELETE FROM incident_sources;

-- Re-insert unique sources
INSERT INTO incident_sources
SELECT * FROM unique_sources;

-- Drop temporary table
DROP TABLE unique_sources;

-- ============================================================================
-- STEP 4: Add Database Constraints to Prevent Future Duplicates
-- ============================================================================

-- Add UNIQUE constraint on source_url globally
-- This prevents the same source URL from being added multiple times across ALL incidents
-- Note: This may fail if there are still duplicates. If it does, the temp table above missed some.
DO $$
BEGIN
    -- Check if constraint already exists
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'incident_sources_source_url_unique'
    ) THEN
        ALTER TABLE incident_sources
        ADD CONSTRAINT incident_sources_source_url_unique UNIQUE (source_url);
    END IF;
END$$;

-- ============================================================================
-- STEP 5: Verification Queries
-- ============================================================================

-- Verify incident count (should be 7 after removing 2 duplicates)
DO $$
DECLARE
    incident_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO incident_count FROM incidents;
    RAISE NOTICE 'Total incidents after cleanup: %', incident_count;

    IF incident_count != 7 THEN
        RAISE WARNING 'Expected 7 incidents, found %', incident_count;
    END IF;
END$$;

-- Verify source count (should be 12 unique sources)
DO $$
DECLARE
    source_count INTEGER;
    unique_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO source_count FROM incident_sources;
    SELECT COUNT(DISTINCT source_url) INTO unique_count FROM incident_sources;

    RAISE NOTICE 'Total source entries: %', source_count;
    RAISE NOTICE 'Unique source URLs: %', unique_count;

    IF source_count != unique_count THEN
        RAISE WARNING 'Found duplicate sources: % total, % unique', source_count, unique_count;
    END IF;
END$$;

-- Check for remaining duplicates at same location
DO $$
DECLARE
    dup_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO dup_count
    FROM (
        SELECT
            ST_Y(location::geometry) as lat,
            ST_X(location::geometry) as lon,
            asset_type,
            COUNT(*) as count
        FROM incidents
        GROUP BY ST_Y(location::geometry), ST_X(location::geometry), asset_type
        HAVING COUNT(*) > 1
    ) duplicates;

    RAISE NOTICE 'Remaining location duplicates: %', dup_count;

    IF dup_count > 0 THEN
        RAISE WARNING 'Still have % location duplicates!', dup_count;
    END IF;
END$$;

COMMIT;

-- ============================================================================
-- ROLLBACK INSTRUCTIONS
-- ============================================================================
-- To rollback this migration:
-- 1. Restore from Supabase backup taken before migration
-- OR
-- 2. Re-run ingestion to recreate incidents (will still have duplicates without API fix)
