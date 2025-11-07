-- Migration 021: Merge Existing Duplicate Incidents
-- Date: 2025-01-XX
-- Description: Find and merge duplicate incidents that slipped through deduplication
-- Strategy: Merge incidents at same location (within 1km) and same day into single incident

BEGIN;

-- ============================================================================
-- STEP 1: Find duplicate groups (same location within 1km, same day)
-- ============================================================================
CREATE TEMP TABLE duplicate_groups AS
SELECT 
    (array_agg(id ORDER BY evidence_score DESC, occurred_at ASC))[1] as primary_id,
    array_agg(id ORDER BY evidence_score DESC, occurred_at ASC) as all_ids,
    COUNT(*) as duplicate_count,
    DATE(occurred_at) as event_date,
    ROUND(ST_Y(location::geometry)::numeric, 3) as lat,
    ROUND(ST_X(location::geometry)::numeric, 3) as lon,
    asset_type
FROM public.incidents
WHERE location IS NOT NULL
GROUP BY
    DATE(occurred_at),
    ROUND(ST_Y(location::geometry)::numeric, 3),
    ROUND(ST_X(location::geometry)::numeric, 3),
    asset_type
HAVING COUNT(*) > 1;

-- ============================================================================
-- STEP 2: Show what will be merged (for verification)
-- ============================================================================
SELECT 
    duplicate_count as incidents_to_merge,
    event_date,
    ROUND(lat::numeric, 4) as latitude,
    ROUND(lon::numeric, 4) as longitude,
    asset_type,
    primary_id::text as keep_incident_id
FROM duplicate_groups
ORDER BY duplicate_count DESC;

-- ============================================================================
-- STEP 3: Transfer sources from duplicates to primary incidents
-- ============================================================================
-- For each duplicate group, transfer all sources to the primary incident
UPDATE public.incident_sources is2
SET incident_id = dg.primary_id
FROM duplicate_groups dg
WHERE is2.incident_id = ANY(dg.all_ids[2:])  -- All IDs except the first (primary)
  AND is2.incident_id != dg.primary_id
  AND NOT EXISTS (
      -- Don't transfer if source URL already exists in primary incident
      SELECT 1 
      FROM public.incident_sources existing
      WHERE existing.incident_id = dg.primary_id
        AND existing.source_url = is2.source_url
  );

-- ============================================================================
-- STEP 4: Update time ranges on primary incidents
-- ============================================================================
-- Extend time ranges to encompass all merged incidents
UPDATE public.incidents i
SET 
    first_seen_at = LEAST(
        i.first_seen_at,
        (SELECT MIN(first_seen_at) FROM public.incidents WHERE id = ANY(dg.all_ids))
    ),
    last_seen_at = GREATEST(
        i.last_seen_at,
        (SELECT MAX(last_seen_at) FROM public.incidents WHERE id = ANY(dg.all_ids))
    ),
    occurred_at = LEAST(
        i.occurred_at,
        (SELECT MIN(occurred_at) FROM public.incidents WHERE id = ANY(dg.all_ids))
    )
FROM duplicate_groups dg
WHERE i.id = dg.primary_id;

-- ============================================================================
-- STEP 5: Delete duplicate incidents (sources already transferred)
-- ============================================================================
DELETE FROM public.incidents
WHERE id IN (
    SELECT unnest(all_ids[2:])  -- All IDs except primary
    FROM duplicate_groups
);

-- ============================================================================
-- STEP 6: Recalculate evidence scores for merged incidents
-- ============================================================================
-- The trigger should handle this, but we'll force a recalculation
UPDATE public.incidents
SET evidence_score = evidence_score  -- Trigger recalculation
WHERE id IN (SELECT primary_id FROM duplicate_groups);

-- ============================================================================
-- STEP 7: Verification
-- ============================================================================
DO $$
DECLARE
    remaining_duplicates INTEGER;
    total_incidents INTEGER;
BEGIN
    -- Check for remaining duplicates
    SELECT COUNT(*) INTO remaining_duplicates
    FROM (
        SELECT 
            DATE(occurred_at),
            ROUND(ST_Y(location::geometry)::numeric, 3),
            ROUND(ST_X(location::geometry)::numeric, 3),
            asset_type
        FROM public.incidents
        WHERE location IS NOT NULL
        GROUP BY
            DATE(occurred_at),
            ROUND(ST_Y(location::geometry)::numeric, 3),
            ROUND(ST_X(location::geometry)::numeric, 3),
            asset_type
        HAVING COUNT(*) > 1
    ) remaining;
    
    SELECT COUNT(*) INTO total_incidents FROM public.incidents;
    
    RAISE NOTICE 'Merge complete. Total incidents: %', total_incidents;
    
    IF remaining_duplicates > 0 THEN
        RAISE WARNING 'Still have % duplicate groups remaining!', remaining_duplicates;
    ELSE
        RAISE NOTICE 'No duplicates remaining - merge successful!';
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- ROLLBACK INSTRUCTIONS
-- ============================================================================
-- To rollback:
-- 1. Restore from Supabase backup taken before migration
-- OR
-- 2. Re-run ingestion (will recreate duplicates if deduplication logic is fixed)

