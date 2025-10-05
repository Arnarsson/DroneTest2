-- Migration 009: Clean up test incidents and prevent future test data
-- Run this in Supabase SQL Editor

-- ============================================================================
-- PART 1: Delete existing test incidents
-- ============================================================================

-- Delete test incidents by ID
DELETE FROM incidents
WHERE id IN (
  '3ac7a745-406a-4251-98d5-e9c01ba85242',  -- DroneTest Ingest Working
  'dc906107-8299-4bb6-9999-eab3b5aec481'   -- DroneTest Success
);

-- Delete any other test incidents by title pattern (case-insensitive)
DELETE FROM incidents
WHERE LOWER(title) LIKE '%dronetest%'
   OR LOWER(title) LIKE '%test incident%'
   OR LOWER(title) LIKE '%testing%'
   OR (LOWER(title) LIKE '%test%' AND evidence_score < 3);  -- Only low-evidence test incidents

-- Report cleanup results
DO $$
DECLARE
  remaining_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO remaining_count FROM incidents;
  RAISE NOTICE 'Cleanup complete. Remaining incidents: %', remaining_count;
END $$;

-- ============================================================================
-- PART 2: Add constraints to prevent future test data
-- ============================================================================

-- Add CHECK constraint to reject test titles
ALTER TABLE incidents
ADD CONSTRAINT no_test_incidents
CHECK (
  LOWER(title) NOT LIKE '%dronetest%'
  AND LOWER(title) NOT LIKE '%test incident%'
);

-- ============================================================================
-- PART 3: Add unique constraint to prevent exact duplicates
-- ============================================================================

-- Create unique index on key fields to prevent exact duplicates
-- This allows same location with different times or different titles
CREATE UNIQUE INDEX IF NOT EXISTS idx_incidents_unique_combo
ON incidents (
  ROUND(ST_Y(location::geometry)::numeric, 4),  -- Latitude from PostGIS geometry
  ROUND(ST_X(location::geometry)::numeric, 4),  -- Longitude from PostGIS geometry
  DATE_TRUNC('hour', occurred_at),              -- Same hour
  title                                         -- Same title
);

-- Report final state
DO $$
DECLARE
  total_incidents INTEGER;
  test_incidents INTEGER;
BEGIN
  SELECT COUNT(*) INTO total_incidents FROM incidents;
  SELECT COUNT(*) INTO test_incidents FROM incidents
    WHERE LOWER(title) LIKE '%test%';

  RAISE NOTICE '========================================';
  RAISE NOTICE 'Migration 009 Complete';
  RAISE NOTICE '========================================';
  RAISE NOTICE 'Total incidents: %', total_incidents;
  RAISE NOTICE 'Test incidents remaining: %', test_incidents;
  RAISE NOTICE '========================================';
END $$;
