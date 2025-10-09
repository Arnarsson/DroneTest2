-- AI Deduplication - Manual Merge for Cluster 1
-- Confidence: 0.95 (HIGH)
-- Date: 2025-10-01
--
-- PRIMARY: "Udenlandske soldater skal hjælpe Danmark efter dronehændelser" (Oct 1)
-- DUPLICATE: "Forsvaret bekrefter: Økning av droneobservasjoner ved militære anlegg" (Sept 30)
--
-- AI Reasoning: Both articles report the same military drone observation event,
-- published 19 hours apart (news coverage window).

BEGIN;

-- Add duplicate's sources to primary incident
INSERT INTO incident_sources (incident_id, source_url, source_title, published_at)
SELECT
    '24a89a45-72da-49c3-9366-c82c2135fe5b'::uuid as incident_id,
    isc.source_url,
    isc.source_title,
    isc.published_at
FROM incident_sources isc
WHERE isc.incident_id = 'd66a477a-5446-4d50-8c54-718ec3e20504'::uuid
ON CONFLICT (incident_id, source_url) DO NOTHING;

-- Update primary incident metadata
UPDATE incidents
SET
    evidence_score = evidence_score + 1,  -- Increment for additional source
    last_seen_at = GREATEST(
        last_seen_at,
        (SELECT last_seen_at FROM incidents WHERE id = 'd66a477a-5446-4d50-8c54-718ec3e20504')
    ),
    narrative = COALESCE(
        narrative,
        (SELECT narrative FROM incidents WHERE id = 'd66a477a-5446-4d50-8c54-718ec3e20504')
    )
WHERE id = '24a89a45-72da-49c3-9366-c82c2135fe5b';

-- Delete the duplicate incident
DELETE FROM incidents WHERE id = 'd66a477a-5446-4d50-8c54-718ec3e20504';

-- Verify the merge
SELECT
    id,
    title,
    evidence_score,
    (SELECT COUNT(*) FROM incident_sources WHERE incident_id = id) as source_count
FROM incidents
WHERE id = '24a89a45-72da-49c3-9366-c82c2135fe5b';

COMMIT;

-- Expected result:
-- Before: 27 incidents
-- After:  26 incidents (1 duplicate removed)
-- Primary incident now has increased evidence_score and multiple sources
