-- Migration: Prevent duplicate incidents
-- Description: Add unique constraint and index to prevent duplicate incidents at same location/time
-- Run this in Supabase SQL Editor after cleaning up existing duplicates

-- 1. Create a unique index on location + date (rounded to nearest hour)
-- This allows multiple incidents at same location if more than 1 hour apart
CREATE UNIQUE INDEX IF NOT EXISTS incidents_unique_location_time
ON public.incidents (
    ROUND(ST_X(location::geometry)::numeric, 4),  -- Longitude rounded to ~10 meters
    ROUND(ST_Y(location::geometry)::numeric, 4),  -- Latitude rounded to ~10 meters
    DATE_TRUNC('hour', occurred_at)               -- Round to nearest hour
);

-- 2. Add comment for documentation
COMMENT ON INDEX incidents_unique_location_time IS
'Prevents duplicate incidents at same location (within 10m) and time (within 1 hour)';

-- 3. Verify the constraint works
-- This should succeed (different locations):
-- INSERT INTO public.incidents (title, occurred_at, location, ...) VALUES (...);

-- This should fail (duplicate location/time):
-- INSERT INTO public.incidents (title, occurred_at, location, ...) VALUES (same location/time);

-- 4. Query to find potential near-duplicates before they're inserted
-- Use this in the scraper to check before inserting:
/*
SELECT id, title, occurred_at
FROM public.incidents
WHERE
    ST_DWithin(
        location,
        ST_SetSRID(ST_MakePoint($lon, $lat), 4326),
        0.0001  -- ~10 meters
    )
    AND occurred_at BETWEEN ($timestamp - INTERVAL '1 hour')
                        AND ($timestamp + INTERVAL '1 hour')
LIMIT 1;
*/

-- Note: If you get an error about existing duplicates, run the cleanup script first!