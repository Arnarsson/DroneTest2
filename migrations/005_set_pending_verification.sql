-- Migration: Set verification_status to 'pending' for existing incidents
-- Purpose: Ensure all incidents are visible to the API query which filters by verification_status
-- Date: 2025-09-30

BEGIN;

-- Update all incidents without verification_status to 'pending'
UPDATE public.incidents
SET verification_status = 'pending'
WHERE verification_status IS NULL;

-- Verify the update
SELECT
  verification_status,
  COUNT(*) as count
FROM public.incidents
GROUP BY verification_status
ORDER BY count DESC;

COMMIT;
