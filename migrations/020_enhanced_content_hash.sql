-- Migration 020: Enhanced Content Hash for Duplicate Prevention
-- Date: 2025-11-13
-- Purpose: Fix Layer 1 (database constraint) gap in duplicate prevention system
-- Addresses: content_hash constraint was designed but never implemented
-- Related: DUPLICATE_DETECTION_2.0_PLAN.md - Tier 1 Hash-Based Detection
--
-- This migration implements:
-- 1. Content hash column with MD5(date + location + normalized_title + asset_type)
-- 2. Normalized title (lowercase, alphanumeric only)
-- 3. Location hash (3 decimal precision ~110m + asset_type)
-- 4. Unique constraint to catch 70-80% of duplicates at database level
-- 5. Automatic hash generation via trigger
--
-- Expected Impact: Prevents exact duplicates from being inserted into database

BEGIN;

-- =====================================================
-- 1. Add columns for enhanced duplicate detection
-- =====================================================

-- Add content_hash column (MD5 of key fields)
ALTER TABLE incidents
  ADD COLUMN IF NOT EXISTS content_hash VARCHAR(32);

-- Add normalized_title (lowercase, alphanumeric only)
ALTER TABLE incidents
  ADD COLUMN IF NOT EXISTS normalized_title TEXT;

-- Add location_hash (rounded coords + asset_type)
ALTER TABLE incidents
  ADD COLUMN IF NOT EXISTS location_hash VARCHAR(16);

COMMENT ON COLUMN incidents.content_hash IS
  'MD5 hash of (date + location + normalized_title + asset_type) - catches exact duplicates';

COMMENT ON COLUMN incidents.normalized_title IS
  'Lowercase title with punctuation removed - used for semantic matching';

COMMENT ON COLUMN incidents.location_hash IS
  'Hash of rounded coordinates (3 decimals ~110m) + asset_type - fast spatial lookup';

-- =====================================================
-- 2. Generate hashes for existing incidents
-- =====================================================

-- Backfill normalized_title for existing incidents
UPDATE incidents SET
  normalized_title = LOWER(REGEXP_REPLACE(TRIM(title), '[^a-z0-9 ]', '', 'g'))
WHERE normalized_title IS NULL;

-- Backfill location_hash for existing incidents
UPDATE incidents SET
  location_hash = SUBSTRING(MD5(CONCAT(
    ROUND(ST_X(location::geometry)::numeric, 3)::text,
    ROUND(ST_Y(location::geometry)::numeric, 3)::text,
    COALESCE(asset_type, 'other')
  )), 1, 16)
WHERE location_hash IS NULL;

-- Backfill content_hash for existing incidents
UPDATE incidents SET
  content_hash = MD5(CONCAT(
    occurred_at::date::text,
    ROUND(ST_X(location::geometry)::numeric, 3)::text,
    ROUND(ST_Y(location::geometry)::numeric, 3)::text,
    LOWER(REGEXP_REPLACE(TRIM(title), '[^a-z0-9 ]', '', 'g')),
    COALESCE(asset_type, 'other')
  ))
WHERE content_hash IS NULL;

-- =====================================================
-- 3. Add unique constraint (PRIMARY DUPLICATE PREVENTION)
-- =====================================================

-- This is the core duplicate prevention at database level
-- Catches 70-80% of duplicates with 0ms latency and $0 cost
-- If this constraint fails, incident is a duplicate
DO $$
BEGIN
  -- Only add constraint if it doesn't exist
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'incidents_content_hash_unique'
  ) THEN
    ALTER TABLE incidents
      ADD CONSTRAINT incidents_content_hash_unique
      UNIQUE (content_hash);
  END IF;
END $$;

-- =====================================================
-- 4. Create indexes for fast lookups
-- =====================================================

-- Index for location-based duplicate detection
CREATE INDEX IF NOT EXISTS idx_incidents_location_hash
  ON incidents(location_hash);

-- Full-text search index for semantic matching (used by Tier 2)
CREATE INDEX IF NOT EXISTS idx_incidents_normalized_title
  ON incidents USING gin(to_tsvector('english', normalized_title));

-- Index for content_hash lookups (redundant with unique constraint, but explicit)
CREATE INDEX IF NOT EXISTS idx_incidents_content_hash
  ON incidents(content_hash) WHERE content_hash IS NOT NULL;

-- =====================================================
-- 5. Auto-generate hashes on INSERT/UPDATE
-- =====================================================

CREATE OR REPLACE FUNCTION update_incident_hashes()
RETURNS TRIGGER AS $$
BEGIN
  -- Normalize title (lowercase, remove non-alphanumeric except spaces)
  NEW.normalized_title := LOWER(REGEXP_REPLACE(TRIM(NEW.title), '[^a-z0-9 ]', '', 'g'));

  -- Location hash (rounded coordinates + asset_type)
  -- 3 decimal places = ~110m precision at Nordic latitudes
  NEW.location_hash := SUBSTRING(MD5(CONCAT(
    ROUND(ST_X(NEW.location::geometry)::numeric, 3)::text,
    ROUND(ST_Y(NEW.location::geometry)::numeric, 3)::text,
    COALESCE(NEW.asset_type, 'other')
  )), 1, 16);

  -- Content hash (complete fingerprint of incident)
  -- Used for O(1) duplicate detection via unique constraint
  NEW.content_hash := MD5(CONCAT(
    NEW.occurred_at::date::text,
    ROUND(ST_X(NEW.location::geometry)::numeric, 3)::text,
    ROUND(ST_Y(NEW.location::geometry)::numeric, 3)::text,
    LOWER(REGEXP_REPLACE(TRIM(NEW.title), '[^a-z0-9 ]', '', 'g')),
    COALESCE(NEW.asset_type, 'other')
  ));

  RETURN NEW;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION update_incident_hashes() IS
  'Automatically generates normalized_title, location_hash, and content_hash before INSERT/UPDATE';

-- =====================================================
-- 6. Create trigger to auto-generate hashes
-- =====================================================

DROP TRIGGER IF EXISTS incident_hashes_trigger ON incidents;

CREATE TRIGGER incident_hashes_trigger
  BEFORE INSERT OR UPDATE ON incidents
  FOR EACH ROW
  EXECUTE FUNCTION update_incident_hashes();

-- =====================================================
-- 7. Validation and statistics
-- =====================================================

-- Count how many incidents have valid hashes
DO $$
DECLARE
  total_count INTEGER;
  hash_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO total_count FROM incidents;
  SELECT COUNT(*) INTO hash_count FROM incidents WHERE content_hash IS NOT NULL;

  RAISE NOTICE 'Migration 020 Complete:';
  RAISE NOTICE '  Total incidents: %', total_count;
  RAISE NOTICE '  Incidents with content_hash: %', hash_count;
  RAISE NOTICE '  Coverage: %%%', ROUND((hash_count::NUMERIC / NULLIF(total_count, 0)) * 100, 2);
END $$;

COMMIT;

-- =====================================================
-- Post-Migration Notes
-- =====================================================

-- This migration implements Tier 1 of the 3-tier duplicate detection system:
--
-- TIER 1 (Hash-Based) - FREE, 0ms latency
--   - Catches: 70-80% of duplicates
--   - Method: MD5 hash of normalized incident data
--   - Unique constraint prevents database insertion
--
-- TIER 2 (Embeddings) - $5-10/month, 50-100ms latency (Migration 021)
--   - Catches: 15-20% of duplicates (semantic variations)
--   - Method: Vector similarity search (cosine distance)
--
-- TIER 3 (LLM Reasoning) - $7-10/month, 300-500ms latency (Migration 022)
--   - Catches: 5-10% of duplicates (edge cases)
--   - Method: Claude/GPT analysis of borderline matches
--
-- Testing:
--   1. Try inserting same incident twice → should fail with unique constraint violation
--   2. Check content_hash is populated: SELECT COUNT(*) FROM incidents WHERE content_hash IS NOT NULL;
--   3. Verify trigger works: INSERT new incident, check hash is auto-generated
