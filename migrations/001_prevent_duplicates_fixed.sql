-- Migration: Prevent duplicate incidents (FIXED VERSION)
-- Description: Add unique constraint to prevent duplicate incidents at same location/time
-- Issue: PostGIS functions are STABLE, not IMMUTABLE, so can't be in index expressions
-- Solution: Use trigger to populate normalized columns, then index those columns

BEGIN;

-- Step 1: Add normalized columns for indexing
ALTER TABLE public.incidents
  ADD COLUMN IF NOT EXISTS lon_rounded numeric(10,4),
  ADD COLUMN IF NOT EXISTS lat_rounded numeric(10,4),
  ADD COLUMN IF NOT EXISTS occurred_hour timestamptz;

-- Step 2: Create trigger function to populate normalized columns
CREATE OR REPLACE FUNCTION public.incidents_set_normalized_fields()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  -- Round coordinates to ~10 meters precision
  IF NEW.location IS NOT NULL THEN
    NEW.lon_rounded := ROUND(ST_X(NEW.location::geometry)::numeric, 4);
    NEW.lat_rounded := ROUND(ST_Y(NEW.location::geometry)::numeric, 4);
  ELSE
    NEW.lon_rounded := NULL;
    NEW.lat_rounded := NULL;
  END IF;

  -- Truncate time to nearest hour
  IF NEW.occurred_at IS NOT NULL THEN
    NEW.occurred_hour := DATE_TRUNC('hour', NEW.occurred_at);
  ELSE
    NEW.occurred_hour := NULL;
  END IF;

  RETURN NEW;
END;
$$;

-- Step 3: Create trigger to run before insert/update
DROP TRIGGER IF EXISTS incidents_normalize_trigger ON public.incidents;
CREATE TRIGGER incidents_normalize_trigger
  BEFORE INSERT OR UPDATE ON public.incidents
  FOR EACH ROW
  EXECUTE FUNCTION public.incidents_set_normalized_fields();

-- Step 4: Backfill existing rows
UPDATE public.incidents
SET
  lon_rounded = ROUND(ST_X(location::geometry)::numeric, 4),
  lat_rounded = ROUND(ST_Y(location::geometry)::numeric, 4),
  occurred_hour = DATE_TRUNC('hour', occurred_at)
WHERE lon_rounded IS NULL OR lat_rounded IS NULL OR occurred_hour IS NULL;

-- Step 5: Create unique index on normalized columns
CREATE UNIQUE INDEX IF NOT EXISTS incidents_unique_location_time
  ON public.incidents (lon_rounded, lat_rounded, occurred_hour);

COMMIT;

-- Add helpful comment
COMMENT ON INDEX incidents_unique_location_time IS
'Prevents duplicate incidents at same location (within ~10m) and time (within 1 hour). Uses trigger-populated normalized columns to avoid STABLE function issue in index expression.';

-- Verification query (run this to test):
/*
-- This should show which rows would conflict if inserted again
SELECT lon_rounded, lat_rounded, occurred_hour, COUNT(*) as duplicates
FROM public.incidents
GROUP BY lon_rounded, lat_rounded, occurred_hour
HAVING COUNT(*) > 1;

-- Should return 0 rows if no duplicates exist
*/