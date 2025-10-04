-- Migration 011: Facility-aware deduplication
-- Strategy: One incident per facility using smart radius based on asset type
-- Airports/Military: 3km radius (large facilities)
-- Harbors: 1.5km radius (medium facilities)
-- Other: 500m radius (specific locations)

BEGIN;

-- Create temp table to identify incidents at same facility
DROP TABLE IF EXISTS facility_duplicates;
CREATE TEMP TABLE facility_duplicates AS
WITH ranked_incidents AS (
    SELECT
        i1.id AS keep_id,
        i1.title AS keep_title,
        i1.asset_type AS asset_type,
        i1.occurred_at AS keep_occurred_at,
        i1.first_seen_at AS keep_first_seen,
        i1.last_seen_at AS keep_last_seen,
        i2.id AS duplicate_id,
        i2.title AS dup_title,
        i2.occurred_at AS dup_occurred_at,
        i2.first_seen_at AS dup_first_seen,
        i2.last_seen_at AS dup_last_seen,
        i2.narrative AS dup_narrative,
        ST_Distance(i1.location::geography, i2.location::geography) AS distance_meters,
        ROW_NUMBER() OVER (
            PARTITION BY
                i1.asset_type,
                ST_SnapToGrid(i1.location::geometry,
                    CASE i1.asset_type
                        WHEN 'airport' THEN 0.027  -- ~3km grid
                        WHEN 'military' THEN 0.027  -- ~3km grid
                        WHEN 'harbor' THEN 0.014    -- ~1.5km grid
                        WHEN 'powerplant' THEN 0.009 -- ~1km grid
                        ELSE 0.005  -- ~500m grid
                    END
                )
            ORDER BY i1.occurred_at ASC, i1.id ASC
        ) AS facility_rank
    FROM incidents i1
    JOIN incidents i2 ON i1.id < i2.id  -- Avoid self-joins
        AND i1.asset_type = i2.asset_type  -- Same facility type
        AND ST_DWithin(
            i1.location::geography,
            i2.location::geography,
            CASE i1.asset_type
                WHEN 'airport' THEN 3000
                WHEN 'military' THEN 3000
                WHEN 'harbor' THEN 1500
                WHEN 'powerplant' THEN 1000
                WHEN 'bridge' THEN 500
                ELSE 500
            END
        )
)
SELECT DISTINCT
    keep_id,
    keep_title,
    asset_type,
    keep_occurred_at,
    keep_first_seen,
    keep_last_seen,
    duplicate_id,
    dup_title,
    dup_occurred_at,
    dup_first_seen,
    dup_last_seen,
    dup_narrative,
    distance_meters
FROM ranked_incidents
WHERE facility_rank = 1;

-- Report what we found
SELECT
    'FACILITY-AWARE DEDUPLICATION REPORT' AS step,
    COUNT(DISTINCT duplicate_id) AS duplicates_to_remove,
    COUNT(DISTINCT keep_id) AS facilities_affected,
    COUNT(*) AS total_merges,
    STRING_AGG(DISTINCT asset_type, ', ' ORDER BY asset_type) AS asset_types_affected
FROM facility_duplicates;

-- Show details grouped by facility
SELECT
    keep_title AS facility,
    asset_type,
    COUNT(duplicate_id) AS duplicates_merged,
    ROUND(AVG(distance_meters)::numeric, 0) AS avg_distance_meters
FROM facility_duplicates
GROUP BY keep_id, keep_title, asset_type
ORDER BY COUNT(duplicate_id) DESC;

-- Ensure source exists for duplicates
INSERT INTO public.sources (name, domain, source_type, homepage_url, trust_weight)
VALUES ('Merged Facility Event', 'dronemap.cc', 'media', 'https://www.dronemap.cc', 1)
ON CONFLICT (domain, source_type, homepage_url) DO NOTHING;

-- Move duplicates to sources table
INSERT INTO public.incident_sources (incident_id, source_id, source_url, source_title, source_quote)
SELECT
    fd.keep_id,
    s.id,
    'https://www.dronemap.cc/incident/' || fd.duplicate_id,
    fd.dup_title,
    COALESCE(fd.dup_narrative, fd.dup_title)
FROM facility_duplicates fd
CROSS JOIN public.sources s
WHERE s.domain = 'dronemap.cc' AND s.source_type = 'media'
ON CONFLICT (incident_id, source_url) DO NOTHING;

-- Delete duplicates FIRST (before updating)
DELETE FROM public.incidents
WHERE id IN (SELECT duplicate_id FROM facility_duplicates);

-- Update time ranges for merged incidents
UPDATE public.incidents
SET
    first_seen_at = LEAST(first_seen_at, (
        SELECT MIN(dup_first_seen)
        FROM facility_duplicates
        WHERE keep_id = incidents.id
    )),
    last_seen_at = GREATEST(last_seen_at, (
        SELECT MAX(dup_last_seen)
        FROM facility_duplicates
        WHERE keep_id = incidents.id
    )),
    occurred_at = LEAST(occurred_at, (
        SELECT MIN(dup_occurred_at)
        FROM facility_duplicates
        WHERE keep_id = incidents.id
    )),
    evidence_score = LEAST(4, evidence_score + (
        SELECT COUNT(DISTINCT duplicate_id)
        FROM facility_duplicates
        WHERE keep_id = incidents.id
    ))
WHERE id IN (SELECT DISTINCT keep_id FROM facility_duplicates);

-- Final report
WITH asset_counts AS (
    SELECT asset_type, COUNT(*) as count
    FROM public.incidents
    GROUP BY asset_type
)
SELECT
    'CLEANUP COMPLETE' AS status,
    (SELECT COUNT(*) FROM public.incidents) AS remaining_incidents,
    COUNT(DISTINCT asset_type) AS unique_asset_types,
    STRING_AGG(asset_type || ':' || count, ', ' ORDER BY count DESC) AS breakdown
FROM asset_counts;

COMMIT;
