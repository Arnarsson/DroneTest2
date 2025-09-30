-- Migration: Auto-verify existing incidents
-- Description: Set existing incidents to auto_verified so they appear in the public API
-- Date: 2025-09-30

BEGIN;

-- Update all existing incidents with 'pending' status to 'auto_verified'
-- This ensures existing incidents continue to show on the map
UPDATE public.incidents
SET
  verification_status = 'auto_verified',
  confidence_score = 0.75,  -- Reasonable default confidence
  verified_at = NOW(),
  verified_by = 'system:migration'
WHERE verification_status = 'pending'
  AND status = 'active';

-- Log the migration
DO $$
DECLARE
  updated_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO updated_count
  FROM public.incidents
  WHERE verification_status = 'auto_verified'
    AND verified_by = 'system:migration';

  RAISE NOTICE 'Auto-verified % existing incidents', updated_count;
END $$;

COMMIT;