-- Migration 011: Remove Non-Nordic Incidents
-- Date: 2025-10-06
-- Purpose: Remove incidents that are not actually in Nordic countries
--          (e.g., Ukraine incident geocoded to Copenhagen by mistake)

-- Remove incidents about Ukraine, Russia, or other non-Nordic countries
DELETE FROM incidents
WHERE
  -- Ukraine incidents (incorrectly geocoded to Copenhagen)
  (title LIKE '%Ukraina%' OR title LIKE '%Ukraine%' OR narrative LIKE '%Ukraine%')
  OR
  -- Russia incidents
  (title LIKE '%Russia%' OR title LIKE '%Russ%' OR narrative LIKE '%Russia%')
  OR
  -- Other obvious non-Nordic locations that were mis-geocoded
  (title LIKE '%München%' AND country = 'DK')  -- Munich is in Germany
;

-- Log what was removed
SELECT
  'Removed incidents:' as action,
  COUNT(*) as count
FROM incidents
WHERE
  (title LIKE '%Ukraina%' OR title LIKE '%Ukraine%' OR narrative LIKE '%Ukraine%')
  OR (title LIKE '%Russia%' OR title LIKE '%Russ%' OR narrative LIKE '%Russia%')
  OR (title LIKE '%München%' AND country = 'DK');

-- Verify remaining incidents are Nordic
SELECT
  'Remaining incidents:' as status,
  country,
  COUNT(*) as count
FROM incidents
GROUP BY country
ORDER BY country;
