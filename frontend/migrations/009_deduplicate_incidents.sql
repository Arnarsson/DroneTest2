-- Migration 009: Deduplicate incidents at exact same coordinates
-- Keep earliest incident, merge others as sources

BEGIN;

-- Create temp table to identify duplicates
CREATE TEMP TABLE duplicate_mapping AS
WITH numbered_incidents AS (
    SELECT
        id,
        title,
        occurred_at,
        narrative,
        location,
        ROW_NUMBER() OVER (
            PARTITION BY ST_X(location::geometry), ST_Y(location::geometry)
            ORDER BY occurred_at ASC, id ASC
        ) AS rn
    FROM incidents
)
SELECT
    i1.id AS keep_id,
    i2.id AS duplicate_id,
    i2.title AS dup_title,
    i2.narrative AS dup_narrative
FROM numbered_incidents i1
JOIN numbered_incidents i2
    ON ST_X(i1.location::geometry) = ST_X(i2.location::geometry)
    AND ST_Y(i1.location::geometry) = ST_Y(i2.location::geometry)
    AND i1.rn = 1  -- Keep earliest
    AND i2.rn > 1; -- Merge others

-- Report what we found
SELECT
    'DEDUPLICATION REPORT' AS step,
    COUNT(DISTINCT duplicate_id) AS duplicates_to_remove,
    COUNT(DISTINCT keep_id) AS incidents_to_keep,
    COUNT(*) AS total_duplicates
FROM duplicate_mapping;

-- Ensure source exists for duplicates
INSERT INTO public.sources (name, domain, source_type, homepage_url, trust_weight)
VALUES ('Merged Duplicate', 'dronemap.cc', 'media', 'https://www.dronemap.cc', 1)
ON CONFLICT (domain, source_type, homepage_url) DO NOTHING;

-- Move duplicates to sources table
INSERT INTO public.incident_sources (incident_id, source_id, source_url, source_title, source_quote)
SELECT
    dm.keep_id,
    s.id,
    'https://www.dronemap.cc/incident/' || dm.duplicate_id,
    dm.dup_title,
    COALESCE(dm.dup_narrative, dm.dup_title)
FROM duplicate_mapping dm
CROSS JOIN public.sources s
WHERE s.domain = 'dronemap.cc' AND s.source_type = 'media'
ON CONFLICT (incident_id, source_url) DO NOTHING;

-- Update evidence scores for merged incidents
UPDATE public.incidents
SET
    evidence_score = LEAST(4, evidence_score + 1),
    last_seen_at = GREATEST(last_seen_at, NOW())
WHERE id IN (SELECT DISTINCT keep_id FROM duplicate_mapping);

-- Delete duplicates
DELETE FROM public.incidents
WHERE id IN (SELECT duplicate_id FROM duplicate_mapping);

-- Final report
SELECT
    'CLEANUP COMPLETE' AS status,
    COUNT(*) AS remaining_incidents,
    COUNT(DISTINCT CONCAT(ST_X(location::geometry), ',', ST_Y(location::geometry))) AS unique_coordinate_locations
FROM public.incidents;

COMMIT;
