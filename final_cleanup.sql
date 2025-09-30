-- Final cleanup: Remove remaining duplicate at Karup
-- The Sept 28 entry is likely a typo - same incident happened Sept 27

-- Delete the shorter narrative version (Sept 28)
DELETE FROM public.incidents WHERE id = 'af084143-8e35-490c-87f2-ec28fc067edd';

-- Verify remaining count
SELECT COUNT(*) as total_incidents FROM public.incidents;

-- Show what's left at Karup
SELECT id, title, occurred_at, LEFT(narrative, 80) as narrative_preview
FROM public.incidents
WHERE title ILIKE '%karup%'
ORDER BY occurred_at;