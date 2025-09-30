-- Migration: Verification Workflow for Historical Incidents
-- Description: Add verification infrastructure for manual review and approval
-- Date: 2025-09-30

BEGIN;

-- =====================================================
-- 1. Add verification fields to incidents table
-- =====================================================

ALTER TABLE public.incidents
  ADD COLUMN IF NOT EXISTS confidence_score NUMERIC(3,2) DEFAULT 0.50
    CHECK (confidence_score BETWEEN 0.00 AND 1.00),
  ADD COLUMN IF NOT EXISTS requires_review BOOLEAN DEFAULT false,
  ADD COLUMN IF NOT EXISTS review_notes JSONB DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS last_reviewed_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS review_count INTEGER DEFAULT 0;

COMMENT ON COLUMN public.incidents.confidence_score IS
'Calculated confidence score 0.0-1.0 based on source trust, corroboration, location specificity, and content quality';

COMMENT ON COLUMN public.incidents.requires_review IS
'Flag indicating incident needs manual review before publishing';

COMMENT ON COLUMN public.incidents.review_notes IS
'Array of review note objects: [{"timestamp": "...", "reviewer": "...", "note": "..."}]';

-- =====================================================
-- 2. Create incident review queue table
-- =====================================================

CREATE TABLE IF NOT EXISTS public.incident_review_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  incident_id UUID NOT NULL REFERENCES public.incidents(id) ON DELETE CASCADE,

  -- Prioritization
  priority INTEGER DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
  -- 1=critical, 2=high, 3=medium, 4=low, 5=very low

  -- Reason for review
  reason TEXT NOT NULL,
  -- e.g., "Low trust source", "Missing location", "User reported"

  -- Assignment
  assigned_to TEXT,

  -- Review metadata
  tags TEXT[] DEFAULT '{}',
  metadata JSONB DEFAULT '{}'::jsonb,

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  reviewed_at TIMESTAMPTZ,

  UNIQUE(incident_id)
);

CREATE INDEX IF NOT EXISTS idx_review_queue_priority ON public.incident_review_queue(priority ASC, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_review_queue_assigned ON public.incident_review_queue(assigned_to) WHERE assigned_to IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_review_queue_pending ON public.incident_review_queue(created_at) WHERE reviewed_at IS NULL;

COMMENT ON TABLE public.incident_review_queue IS
'Queue of incidents requiring manual verification before publication';

-- =====================================================
-- 3. Create verification audit log
-- =====================================================

CREATE TABLE IF NOT EXISTS public.verification_audit (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  incident_id UUID NOT NULL REFERENCES public.incidents(id) ON DELETE CASCADE,

  -- Action details
  action TEXT NOT NULL CHECK (action IN (
    'verified', 'rejected', 'flagged', 'edited',
    'auto_verified', 'status_changed', 'reassigned'
  )),

  -- Who performed it
  performed_by TEXT NOT NULL,

  -- State changes
  previous_status TEXT,
  new_status TEXT,
  previous_verification TEXT,
  new_verification TEXT,

  -- Details
  notes TEXT,
  changes JSONB DEFAULT '{}'::jsonb,

  -- Timestamp
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_verification_audit_incident ON public.verification_audit(incident_id);
CREATE INDEX IF NOT EXISTS idx_verification_audit_time ON public.verification_audit(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_verification_audit_action ON public.verification_audit(action);
CREATE INDEX IF NOT EXISTS idx_verification_audit_user ON public.verification_audit(performed_by);

COMMENT ON TABLE public.verification_audit IS
'Complete audit trail of all verification actions on incidents';

-- =====================================================
-- 4. Create helper views
-- =====================================================

-- View: Review queue with full incident details
CREATE OR REPLACE VIEW public.v_review_queue AS
SELECT
  rq.id AS queue_id,
  rq.priority,
  rq.reason,
  rq.assigned_to,
  rq.tags,
  rq.created_at AS queued_at,
  rq.reviewed_at,
  -- Incident details
  i.id AS incident_id,
  i.title,
  i.narrative,
  i.occurred_at,
  i.status,
  i.verification_status,
  i.evidence_score,
  i.confidence_score,
  i.asset_type,
  i.country,
  ST_Y(i.location::geometry) AS lat,
  ST_X(i.location::geometry) AS lon,
  i.created_at AS incident_created_at,
  -- Source information
  (SELECT COUNT(*) FROM public.incident_sources WHERE incident_id = i.id) as source_count,
  (SELECT json_agg(json_build_object(
    'source_url', source_url,
    'source_type', source_type,
    'source_quote', source_quote
  )) FROM public.incident_sources WHERE incident_id = i.id) as sources
FROM public.incident_review_queue rq
JOIN public.incidents i ON rq.incident_id = i.id
WHERE rq.reviewed_at IS NULL
ORDER BY rq.priority ASC, rq.created_at ASC;

COMMENT ON VIEW public.v_review_queue IS
'Review queue with complete incident information for admin dashboard';

-- View: Verification statistics
CREATE OR REPLACE VIEW public.v_verification_stats AS
SELECT
  COUNT(*) FILTER (WHERE verification_status = 'pending') as pending_count,
  COUNT(*) FILTER (WHERE verification_status = 'verified') as verified_count,
  COUNT(*) FILTER (WHERE verification_status = 'auto_verified') as auto_verified_count,
  COUNT(*) FILTER (WHERE verification_status = 'rejected') as rejected_count,
  COUNT(*) FILTER (WHERE requires_review = true) as requires_review_count,
  AVG(confidence_score) as avg_confidence_score,
  AVG(evidence_score) as avg_evidence_score
FROM public.incidents;

COMMENT ON VIEW public.v_verification_stats IS
'Overview statistics for verification metrics';

-- =====================================================
-- 5. Create helper functions
-- =====================================================

-- Function: Add incident to review queue
CREATE OR REPLACE FUNCTION public.add_to_review_queue(
  p_incident_id UUID,
  p_reason TEXT,
  p_priority INTEGER DEFAULT 3
) RETURNS UUID
LANGUAGE plpgsql AS $$
DECLARE
  v_queue_id UUID;
BEGIN
  -- Insert into queue if not already there
  INSERT INTO public.incident_review_queue (incident_id, reason, priority)
  VALUES (p_incident_id, p_reason, p_priority)
  ON CONFLICT (incident_id) DO UPDATE
  SET priority = LEAST(public.incident_review_queue.priority, p_priority),
      reason = p_reason
  RETURNING id INTO v_queue_id;

  -- Mark incident as requiring review
  UPDATE public.incidents
  SET requires_review = true
  WHERE id = p_incident_id;

  RETURN v_queue_id;
END;
$$;

COMMENT ON FUNCTION public.add_to_review_queue IS
'Add an incident to the manual review queue';

-- Function: Complete review (approve/reject)
CREATE OR REPLACE FUNCTION public.complete_review(
  p_incident_id UUID,
  p_action TEXT, -- 'verify' or 'reject'
  p_reviewer TEXT,
  p_notes TEXT DEFAULT NULL
) RETURNS BOOLEAN
LANGUAGE plpgsql AS $$
DECLARE
  v_old_status TEXT;
  v_old_verification TEXT;
BEGIN
  -- Get current status
  SELECT status, verification_status INTO v_old_status, v_old_verification
  FROM public.incidents WHERE id = p_incident_id;

  -- Update incident based on action
  IF p_action = 'verify' THEN
    UPDATE public.incidents
    SET
      verification_status = 'verified',
      verified_at = NOW(),
      verified_by = p_reviewer,
      requires_review = false,
      last_reviewed_at = NOW(),
      review_count = review_count + 1,
      admin_notes = COALESCE(admin_notes, '') || E'\n[' || NOW() || '] ' || p_reviewer || ': ' || COALESCE(p_notes, 'Verified')
    WHERE id = p_incident_id;

  ELSIF p_action = 'reject' THEN
    UPDATE public.incidents
    SET
      verification_status = 'rejected',
      status = 'false_positive',
      verified_by = p_reviewer,
      requires_review = false,
      last_reviewed_at = NOW(),
      review_count = review_count + 1,
      admin_notes = COALESCE(admin_notes, '') || E'\n[' || NOW() || '] ' || p_reviewer || ': ' || COALESCE(p_notes, 'Rejected')
    WHERE id = p_incident_id;

  ELSE
    RAISE EXCEPTION 'Invalid action. Must be "verify" or "reject"';
  END IF;

  -- Mark queue item as reviewed
  UPDATE public.incident_review_queue
  SET reviewed_at = NOW()
  WHERE incident_id = p_incident_id;

  -- Log to audit trail
  INSERT INTO public.verification_audit (
    incident_id, action, performed_by,
    previous_status, new_status,
    previous_verification, new_verification,
    notes
  ) VALUES (
    p_incident_id, p_action, p_reviewer,
    v_old_status, CASE WHEN p_action = 'reject' THEN 'false_positive' ELSE v_old_status END,
    v_old_verification, CASE WHEN p_action = 'verify' THEN 'verified' ELSE 'rejected' END,
    p_notes
  );

  RETURN true;
END;
$$;

COMMENT ON FUNCTION public.complete_review IS
'Complete manual review by verifying or rejecting an incident';

-- =====================================================
-- 6. Update existing API view to filter by verification
-- =====================================================

-- Drop old view if exists
DROP VIEW IF EXISTS public.v_incidents_public;

-- Create new filtered view for public API
CREATE OR REPLACE VIEW public.v_incidents_public AS
SELECT
  i.id,
  i.title,
  i.narrative,
  i.occurred_at,
  i.first_seen_at,
  i.last_seen_at,
  i.asset_type,
  i.status,
  i.evidence_score,
  i.country,
  ST_Y(i.location::geometry) AS lat,
  ST_X(i.location::geometry) AS lon,
  i.confidence_score
FROM public.incidents i
WHERE i.verification_status IN ('verified', 'auto_verified')
  AND i.status = 'active';

COMMENT ON VIEW public.v_incidents_public IS
'Public-facing incidents view - only shows verified incidents';

-- =====================================================
-- 7. Add RLS policies for new tables
-- =====================================================

ALTER TABLE public.incident_review_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.verification_audit ENABLE ROW LEVEL SECURITY;

-- Review queue is admin-only (no public access)
-- Verification audit is admin-only (no public access)

-- Public can read from filtered view
CREATE POLICY "public_read_verified_incidents" ON public.incidents
FOR SELECT USING (
  verification_status IN ('verified', 'auto_verified') AND status = 'active'
);

COMMIT;

-- =====================================================
-- Verification queries for testing
-- =====================================================

/*
-- View review queue
SELECT * FROM public.v_review_queue LIMIT 10;

-- View verification stats
SELECT * FROM public.v_verification_stats;

-- Add incident to review queue
SELECT public.add_to_review_queue(
  'incident-uuid-here',
  'Low confidence score',
  2  -- high priority
);

-- Verify an incident
SELECT public.complete_review(
  'incident-uuid-here',
  'verify',
  'admin@dronewatch.cc',
  'Confirmed with police source'
);

-- Reject an incident
SELECT public.complete_review(
  'incident-uuid-here',
  'reject',
  'admin@dronewatch.cc',
  'Commercial drone delivery, not an incident'
);

-- View audit trail for incident
SELECT * FROM public.verification_audit
WHERE incident_id = 'incident-uuid-here'
ORDER BY created_at DESC;

-- View unverified incidents count by source
SELECT
  s.source_name,
  s.source_type,
  COUNT(*) as unverified_count
FROM public.incidents i
JOIN public.incident_sources isrc ON i.id = isrc.incident_id
JOIN public.sources s ON isrc.source_id = s.id
WHERE i.verification_status = 'pending'
GROUP BY s.source_name, s.source_type
ORDER BY unverified_count DESC;
*/