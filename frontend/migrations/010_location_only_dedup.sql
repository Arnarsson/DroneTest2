-- Migration 010: Location-only deduplication (ignore time differences)
-- Strategy: One incident per location regardless of when events occurred
-- Keep earliest incident, merge all others as sources

-- STEP 1: Drop constraint FIRST (outside transaction to avoid rollback issues)
ALTER TABLE public.incidents DROP CONSTRAINT IF EXISTS incidents_unique_location_time;

BEGIN;

-- Drop temp table if it exists from previous run
DROP TABLE IF EXISTS location_duplicates;

-- Create temp table to identify all incidents at same location
CREATE TEMP TABLE location_duplicates AS
WITH numbered_incidents AS (
    SELECT
        id,
        title,
        occurred_at,
        first_seen_at,
        last_seen_at,
        narrative,
        location,
        evidence_score,
        ROW_NUMBER() OVER (
            PARTITION BY ST_X(location::geometry), ST_Y(location::geometry)
            ORDER BY occurred_at ASC, id ASC
        ) AS rn
    FROM incidents
)
SELECT
    i1.id AS keep_id,
    i1.occurred_at AS keep_occurred_at,
    i1.first_seen_at AS keep_first_seen,
    i1.last_seen_at AS keep_last_seen,
    i2.id AS duplicate_id,
    i2.title AS dup_title,
    i2.narrative AS dup_narrative,
    i2.occurred_at AS dup_occurred_at,
    i2.first_seen_at AS dup_first_seen,
    i2.last_seen_at AS dup_last_seen
FROM numbered_incidents i1
JOIN numbered_incidents i2
    ON ST_X(i1.location::geometry) = ST_X(i2.location::geometry)
    AND ST_Y(i1.location::geometry) = ST_Y(i2.location::geometry)
    AND i1.rn = 1  -- Keep earliest
    AND i2.rn > 1; -- Merge all others

-- Report what we found
SELECT
    'LOCATION-ONLY DEDUPLICATION REPORT' AS step,
    COUNT(DISTINCT duplicate_id) AS duplicates_to_remove,
    COUNT(DISTINCT keep_id) AS incidents_to_keep,
    COUNT(*) AS total_duplicates
FROM location_duplicates;

-- Ensure source exists for duplicates
INSERT INTO public.sources (name, domain, source_type, homepage_url, trust_weight)
VALUES ('Merged Event', 'dronemap.cc', 'media', 'https://www.dronemap.cc', 1)
ON CONFLICT (domain, source_type, homepage_url) DO NOTHING;

-- Move duplicates to sources table
INSERT INTO public.incident_sources (incident_id, source_id, source_url, source_title, source_quote)
SELECT
    ld.keep_id,
    s.id,
    'https://www.dronemap.cc/incident/' || ld.duplicate_id,
    ld.dup_title,
    COALESCE(ld.dup_narrative, ld.dup_title)
FROM location_duplicates ld
CROSS JOIN public.sources s
WHERE s.domain = 'dronemap.cc' AND s.source_type = 'media'
ON CONFLICT (incident_id, source_url) DO NOTHING;

-- STEP 2: Delete duplicates FIRST (before updating, to avoid constraint conflicts)
DELETE FROM public.incidents
WHERE id IN (SELECT duplicate_id FROM location_duplicates);

-- STEP 3: Now update time ranges for merged incidents (no conflicts now)
UPDATE public.incidents
SET
    first_seen_at = LEAST(first_seen_at, (
        SELECT MIN(dup_first_seen)
        FROM location_duplicates
        WHERE keep_id = incidents.id
    )),
    last_seen_at = GREATEST(last_seen_at, (
        SELECT MAX(dup_last_seen)
        FROM location_duplicates
        WHERE keep_id = incidents.id
    )),
    occurred_at = LEAST(occurred_at, (
        SELECT MIN(dup_occurred_at)
        FROM location_duplicates
        WHERE keep_id = incidents.id
    )),
    evidence_score = LEAST(4, evidence_score + (
        SELECT COUNT(DISTINCT duplicate_id)
        FROM location_duplicates
        WHERE keep_id = incidents.id
    ))
WHERE id IN (SELECT DISTINCT keep_id FROM location_duplicates);

-- Final report
SELECT
    'CLEANUP COMPLETE' AS status,
    COUNT(*) AS remaining_incidents,
    COUNT(DISTINCT CONCAT(ST_X(location::geometry), ',', ST_Y(location::geometry))) AS unique_locations,
    CASE
        WHEN COUNT(*) = COUNT(DISTINCT CONCAT(ST_X(location::geometry), ',', ST_Y(location::geometry)))
        THEN 'SUCCESS: One incident per location'
        ELSE 'ERROR: Still have duplicates'
    END AS validation
FROM public.incidents;

COMMIT;
