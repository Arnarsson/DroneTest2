-- Migration 012: Complete facility-aware deduplication
-- Iterative approach that finds ALL incidents within facility radius

BEGIN;

-- Iteratively merge incidents until no more duplicates found
DO $$
DECLARE
    merge_count INTEGER := 1;
    iteration INTEGER := 0;
    v_keep_id UUID;
    v_dup_id UUID;
    v_keep_title TEXT;
    v_dup_title TEXT;
    v_dup_narrative TEXT;
    v_dup_occurred TIMESTAMP WITH TIME ZONE;
    v_dup_first_seen TIMESTAMP WITH TIME ZONE;
    v_dup_last_seen TIMESTAMP WITH TIME ZONE;
BEGIN
    WHILE merge_count > 0 AND iteration < 10 LOOP
        iteration := iteration + 1;

        -- Find one pair of duplicates
        SELECT
            i1.id,
            i2.id,
            i1.title,
            i2.title,
            i2.narrative,
            i2.occurred_at,
            i2.first_seen_at,
            i2.last_seen_at
        INTO
            v_keep_id,
            v_dup_id,
            v_keep_title,
            v_dup_title,
            v_dup_narrative,
            v_dup_occurred,
            v_dup_first_seen,
            v_dup_last_seen
        FROM incidents i1
        JOIN incidents i2 ON i1.id < i2.id
            AND i1.asset_type = i2.asset_type
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
        ORDER BY i1.occurred_at ASC, i1.id ASC
        LIMIT 1;

        IF v_dup_id IS NOT NULL THEN
            merge_count := 1;

            -- Ensure source exists
            INSERT INTO public.sources (name, domain, source_type, homepage_url, trust_weight)
            VALUES ('Merged Facility', 'dronemap.cc', 'media', 'https://www.dronemap.cc', 2)
            ON CONFLICT (domain, source_type, homepage_url) DO NOTHING;

            -- Add duplicate as source
            INSERT INTO public.incident_sources (incident_id, source_id, source_url, source_title, source_quote)
            SELECT
                v_keep_id,
                s.id,
                'https://www.dronemap.cc/incident/' || v_dup_id,
                v_dup_title,
                COALESCE(v_dup_narrative, v_dup_title)
            FROM public.sources s
            WHERE s.domain = 'dronemap.cc' AND s.source_type = 'media' AND s.homepage_url = 'https://www.dronemap.cc'
            ON CONFLICT (incident_id, source_url) DO NOTHING;

            -- Update time ranges
            UPDATE public.incidents
            SET
                first_seen_at = LEAST(first_seen_at, v_dup_first_seen),
                last_seen_at = GREATEST(last_seen_at, v_dup_last_seen),
                occurred_at = LEAST(occurred_at, v_dup_occurred),
                evidence_score = LEAST(4, evidence_score + 1)
            WHERE id = v_keep_id;

            -- Delete duplicate
            DELETE FROM public.incidents WHERE id = v_dup_id;

            RAISE NOTICE 'Iteration %: Merged "%" into "%"', iteration, v_dup_title, v_keep_title;
        ELSE
            merge_count := 0;
        END IF;
    END LOOP;

    RAISE NOTICE 'Completed after % iterations', iteration;
END $$;

-- Final report
SELECT
    'COMPLETE FACILITY DEDUPLICATION' AS status,
    COUNT(*) AS remaining_incidents,
    COUNT(*) FILTER (WHERE asset_type = 'airport') AS airports,
    COUNT(*) FILTER (WHERE asset_type = 'military') AS military,
    COUNT(*) FILTER (WHERE asset_type = 'harbor') AS harbors,
    COUNT(*) FILTER (WHERE asset_type = 'other') AS other
FROM public.incidents;

COMMIT;
