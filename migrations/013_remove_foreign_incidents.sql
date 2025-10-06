-- Migration 013: Remove Foreign Incidents
-- Removes incidents that occurred outside the Nordic region but were incorrectly geocoded
-- to Nordic coordinates due to context mentions in news articles

-- CONTEXT:
-- Before geographic scope filtering was implemented, the scraper would ingest
-- foreign incidents (e.g., Ukrainian drone attacks) if the article mentioned
-- Nordic locations in context (e.g., "leaders meeting in Copenhagen discuss Ukraine").
-- This caused foreign incidents to appear at Nordic coordinates on the map.

-- SAFE TO RUN:
-- This migration only removes incidents with obvious foreign keywords in titles
-- that are located at major Nordic city coordinates. It does NOT remove:
-- - Actual Nordic incidents
-- - Test incidents (handled by separate migration)
-- - Incidents with unique/specific coordinates

-- Verify table exists (will error if not - which is good, don't run on wrong DB!)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'incidents') THEN
        RAISE EXCEPTION 'Table public.incidents does not exist! Check your database connection.';
    END IF;
END $$;

-- Delete incidents with Ukrainian keywords at Copenhagen coordinates
DELETE FROM public.incidents
WHERE
    -- Ukrainian incidents
    (title ILIKE '%ukraina%' OR title ILIKE '%ukraine%' OR title ILIKE '%kiev%' OR title ILIKE '%kyiv%')
    AND
    -- At Copenhagen Airport coordinates (rounded to 0.01 degree precision)
    (
        (ST_Y(location::geometry) BETWEEN 55.61 AND 55.63) AND
        (ST_X(location::geometry) BETWEEN 12.64 AND 12.66)
    );

-- Delete incidents with German location keywords at any Nordic coordinates
DELETE FROM public.incidents
WHERE
    -- German locations
    (title ILIKE '%münchen%' OR title ILIKE '%munich%' OR title ILIKE '%berlin%' OR title ILIKE '%germany%' OR title ILIKE '%tyskland%')
    AND
    -- Within Nordic region bounding box (54-71°N, 4-31°E)
    (
        (ST_Y(location::geometry) BETWEEN 54 AND 71) AND
        (ST_X(location::geometry) BETWEEN 4 AND 31)
    );

-- Delete incidents with Russian location keywords
DELETE FROM public.incidents
WHERE
    (title ILIKE '%russia%' OR title ILIKE '%rusland%' OR title ILIKE '%moscow%' OR title ILIKE '%moskva%')
    AND
    (
        (ST_Y(location::geometry) BETWEEN 54 AND 71) AND
        (ST_X(location::geometry) BETWEEN 4 AND 31)
    );

-- Delete incidents with other Eastern European keywords
DELETE FROM public.incidents
WHERE
    (title ILIKE '%belarus%' OR title ILIKE '%hviderusland%' OR title ILIKE '%poland%' OR title ILIKE '%polen%')
    AND
    (
        (ST_Y(location::geometry) BETWEEN 54 AND 71) AND
        (ST_X(location::geometry) BETWEEN 4 AND 31)
    );

-- Log the cleanup
-- (PostgreSQL will show number of rows affected)

-- VERIFICATION:
-- After running this migration, verify no foreign incidents remain:
-- SELECT title, ST_Y(location::geometry) as lat, ST_X(location::geometry) as lon
-- FROM public.incidents
-- WHERE title ILIKE '%ukraina%' OR title ILIKE '%ukraine%'
--    OR title ILIKE '%münchen%' OR title ILIKE '%berlin%';
