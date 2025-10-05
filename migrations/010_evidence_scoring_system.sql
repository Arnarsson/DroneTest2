-- Migration 010: Evidence Scoring System Enforcement
-- Created: 2025-10-05
-- Purpose: Enforce 4-tier evidence scoring based on source reliability
--
-- Evidence Tiers:
-- 4 (OFFICIAL): Police, military, NOTAM, official government
-- 3 (VERIFIED): Multiple credible sources OR single source with official quote
-- 2 (REPORTED): Single credible media source
-- 1 (UNCONFIRMED): Social media, OSINT, unverified reports

-- ============================================
-- Step 1: Add evidence calculation trigger
-- ============================================

-- Function to calculate evidence score from sources
CREATE OR REPLACE FUNCTION calculate_evidence_score(incident_id uuid)
RETURNS int AS $$
DECLARE
  max_trust int := 1;
  source_count int := 0;
  has_official_quote boolean := false;
  calculated_score int := 1;
BEGIN
  -- Get max trust weight and source count
  SELECT
    COALESCE(MAX(s.trust_weight), 1),
    COUNT(*)
  INTO max_trust, source_count
  FROM incident_sources isc
  JOIN sources s ON isc.source_id = s.id
  WHERE isc.incident_id = calculate_evidence_score.incident_id;

  -- Check for official quotes in narrative
  SELECT EXISTS(
    SELECT 1 FROM incidents
    WHERE id = calculate_evidence_score.incident_id
    AND (
      narrative ILIKE '%politi%' OR
      narrative ILIKE '%bekræfter%' OR
      narrative ILIKE '%oplyser%' OR
      narrative ILIKE '%according to police%' OR
      narrative ILIKE '%confirms%'
    )
  ) INTO has_official_quote;

  -- Calculate score based on rules:
  -- 4: Official sources (trust_weight=4) OR police/notam source_type
  -- 3: Multiple sources with trust>=3 OR single source with official quote
  -- 2: Single credible source (trust>=2)
  -- 1: Low trust source or no sources

  IF max_trust = 4 THEN
    calculated_score := 4;
  ELSIF source_count >= 2 AND max_trust >= 3 THEN
    calculated_score := 3;
  ELSIF max_trust = 3 AND has_official_quote THEN
    calculated_score := 3;
  ELSIF max_trust >= 2 THEN
    calculated_score := 2;
  ELSE
    calculated_score := 1;
  END IF;

  RETURN calculated_score;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Step 2: Create trigger to auto-update evidence score
-- ============================================

-- Trigger function to update evidence score when sources change
CREATE OR REPLACE FUNCTION update_evidence_score_on_source_change()
RETURNS TRIGGER AS $$
BEGIN
  -- Update evidence score for the affected incident
  UPDATE incidents
  SET evidence_score = calculate_evidence_score(
    CASE
      WHEN TG_OP = 'DELETE' THEN OLD.incident_id
      ELSE NEW.incident_id
    END
  )
  WHERE id = CASE
    WHEN TG_OP = 'DELETE' THEN OLD.incident_id
    ELSE NEW.incident_id
  END;

  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if exists and recreate
DROP TRIGGER IF EXISTS trigger_update_evidence_score ON incident_sources;

CREATE TRIGGER trigger_update_evidence_score
AFTER INSERT OR UPDATE OR DELETE ON incident_sources
FOR EACH ROW
EXECUTE FUNCTION update_evidence_score_on_source_change();

-- ============================================
-- Step 3: Recalculate all existing evidence scores
-- ============================================

-- Update all incidents with recalculated evidence scores
UPDATE incidents
SET evidence_score = calculate_evidence_score(id);

-- ============================================
-- Step 4: Add validation comment
-- ============================================

COMMENT ON FUNCTION calculate_evidence_score(uuid) IS
'Calculates evidence score (1-4) based on source trust weights and official quotes.
4=Official sources, 3=Multiple credible or single with quote, 2=Single credible, 1=Unverified';

COMMENT ON TRIGGER trigger_update_evidence_score ON incident_sources IS
'Automatically recalculates incident evidence_score when sources are added/removed/updated';

-- ============================================
-- Verification Queries (for testing)
-- ============================================

-- Check evidence score distribution
-- SELECT evidence_score, COUNT(*),
--        ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER () * 100, 1) as percentage
-- FROM incidents
-- GROUP BY evidence_score
-- ORDER BY evidence_score DESC;

-- Check incidents with mismatched evidence scores
-- SELECT i.id, i.title, i.evidence_score,
--        calculate_evidence_score(i.id) as calculated_score,
--        COUNT(isc.source_id) as source_count
-- FROM incidents i
-- LEFT JOIN incident_sources isc ON i.id = isc.incident_id
-- GROUP BY i.id, i.title, i.evidence_score
-- HAVING i.evidence_score != calculate_evidence_score(i.id);
