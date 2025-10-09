-- Delete Non-Nordic Incidents
-- Date: 2025-10-06
-- Purpose: Remove Ukraine and Munich incidents incorrectly geocoded to Denmark
--
-- IDs found from production API:
-- - 033919ed-f8fe-44db-9a73-0ce64a788f4f (Ukraine attack)
-- - 3547e1c9-34ff-4f82-9620-891f13771c69 (Munich incident)

-- Show what will be deleted (VERIFY FIRST)
SELECT id, title, country, lat, lon
FROM incidents
WHERE id IN (
  '033919ed-f8fe-44db-9a73-0ce64a788f4f',
  '3547e1c9-34ff-4f82-9620-891f13771c69'
);

-- Delete the incidents
DELETE FROM incidents
WHERE id IN (
  '033919ed-f8fe-44db-9a73-0ce64a788f4f',  -- Ukraine drone attack
  '3547e1c9-34ff-4f82-9620-891f13771c69'   -- Munich incident
);

-- Verify deletion
SELECT
  'Incidents after deletion:' as status,
  COUNT(*) as total,
  COUNT(*) FILTER (WHERE country = 'DK') as denmark,
  COUNT(*) FILTER (WHERE country = 'NO') as norway,
  COUNT(*) FILTER (WHERE country = 'SE') as sweden
FROM incidents;

-- Should now show 20 total incidents (down from 22)
