-- Merge Duplicate Incidents - One Event = One Incident
-- This script merges incidents that are the same event reported by different sources

-- PROBLEM: Many incidents are duplicates (same location+time, different news articles)
-- SOLUTION: Merge into one incident, create sources from duplicate narratives

BEGIN;

-- Step 0: Ensure 'Merged Duplicate' source exists (already created, but checking)
-- Note: Source was created via Supabase with id: c9c25894-3f20-4ed5-8211-3fb1f45d7844
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM public.sources WHERE name = 'Merged Duplicate') THEN
        INSERT INTO public.sources (name, source_type, trust_weight)
        VALUES ('Merged Duplicate', 'other', 1);
    END IF;
END $$;

-- Step 1: Find duplicate groups (same location within 1km, same day)
CREATE TEMP TABLE duplicate_groups AS
SELECT
    (array_agg(id ORDER BY evidence_score DESC, occurred_at ASC))[1] as primary_id,
    array_agg(id ORDER BY evidence_score DESC, occurred_at ASC) as all_ids,
    COUNT(*) as duplicate_count,
    occurred_at::date as event_date,
    ROUND(ST_Y(location::geometry)::numeric, 2) as lat,
    ROUND(ST_X(location::geometry)::numeric, 2) as lon
FROM public.incidents
GROUP BY
    occurred_at::date,
    ROUND(ST_Y(location::geometry)::numeric, 2),
    ROUND(ST_X(location::geometry)::numeric, 2)
HAVING COUNT(*) > 1;

-- Step 2: Show what will be merged (for verification)
SELECT
    duplicate_count as incidents,
    event_date,
    ROUND(lat::numeric, 4) as latitude,
    ROUND(lon::numeric, 4) as longitude
FROM duplicate_groups
ORDER BY duplicate_count DESC;

-- Step 3: Create sources from duplicate narratives
-- For each duplicate incident, create a source entry with its narrative
INSERT INTO public.incident_sources (incident_id, source_id, source_url, source_title, source_quote)
SELECT
    dg.primary_id as incident_id,
    (SELECT id FROM public.sources WHERE name = 'Merged Duplicate' LIMIT 1) as source_id,
    COALESCE(
        'https://www.dronemap.cc/incident/' || i.id,
        'internal://merged/' || i.id
    ) as source_url,
    i.title as source_title,
    LEFT(i.narrative, 500) as source_quote
FROM duplicate_groups dg
CROSS JOIN LATERAL unnest(dg.all_ids[2:array_length(dg.all_ids, 1)]) WITH ORDINALITY AS dup(id, ord)
JOIN public.incidents i ON i.id = dup.id
WHERE i.narrative IS NOT NULL AND LENGTH(i.narrative) > 20
ON CONFLICT (incident_id, source_url) DO NOTHING;

-- Step 4: Update primary incident with best data from duplicates
UPDATE public.incidents pri
SET
    -- Use longest narrative (most detailed)
    narrative = COALESCE((
        SELECT narrative
        FROM public.incidents
        WHERE id = ANY((SELECT all_ids FROM duplicate_groups WHERE primary_id = pri.id))
        ORDER BY LENGTH(narrative) DESC
        LIMIT 1
    ), pri.narrative),

    -- Use highest evidence score
    evidence_score = GREATEST(
        pri.evidence_score,
        COALESCE((
            SELECT MAX(evidence_score)
            FROM public.incidents
            WHERE id = ANY((SELECT all_ids FROM duplicate_groups WHERE primary_id = pri.id))
        ), pri.evidence_score)
    ),

    -- Update last_seen_at to most recent
    last_seen_at = GREATEST(
        pri.last_seen_at,
        COALESCE((
            SELECT MAX(last_seen_at)
            FROM public.incidents
            WHERE id = ANY((SELECT all_ids FROM duplicate_groups WHERE primary_id = pri.id))
        ), pri.last_seen_at)
    )
WHERE pri.id IN (SELECT primary_id FROM duplicate_groups);

-- Step 5: Delete duplicate incidents (keep only primary)
DELETE FROM public.incidents
WHERE id IN (
    SELECT unnest(all_ids[2:array_length(all_ids, 1)])
    FROM duplicate_groups
);

-- Step 6: Summary
SELECT
    COUNT(DISTINCT primary_id) as groups_merged,
    SUM(duplicate_count - 1) as duplicates_removed,
    (SELECT COUNT(*) FROM public.incidents) as remaining_incidents
FROM duplicate_groups;

COMMIT;

-- Verify results
SELECT
    COUNT(*) as total_incidents,
    COUNT(DISTINCT (occurred_at::date, ROUND(ST_Y(location::geometry)::numeric, 2), ROUND(ST_X(location::geometry)::numeric, 2))) as unique_events
FROM public.incidents;

-- Expected: total_incidents ≈ unique_events (no more duplicates)
