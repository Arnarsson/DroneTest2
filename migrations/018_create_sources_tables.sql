-- Migration 018: Create Sources Tables
-- Date: 2025-10-14
-- Description: Creates sources and incident_sources tables for multi-source verification
-- Required for: Evidence scoring system to track multiple sources per incident

-- =========================
-- Sources (publishers/feeds)
-- =========================
CREATE TABLE IF NOT EXISTS public.sources (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  domain text,
  source_type text NOT NULL CHECK (source_type IN ('police','notam','media','social','osint','aviation_authority','other')),
  homepage_url text,
  feed_url text,
  trust_weight decimal(3,2) NOT NULL DEFAULT 1.0 CHECK (trust_weight BETWEEN 0.0 AND 4.0),
  country text,
  is_active boolean DEFAULT true,
  last_checked_at timestamptz,
  metadata jsonb DEFAULT '{}',
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (domain, source_type)
);

CREATE INDEX IF NOT EXISTS idx_sources_active ON public.sources(is_active);
CREATE INDEX IF NOT EXISTS idx_sources_type ON public.sources(source_type);
CREATE INDEX IF NOT EXISTS idx_sources_country ON public.sources(country);

-- =========================
-- Incident Sources (many-to-many)
-- =========================
CREATE TABLE IF NOT EXISTS public.incident_sources (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  incident_id uuid NOT NULL REFERENCES public.incidents(id) ON DELETE CASCADE,
  source_id uuid NOT NULL REFERENCES public.sources(id) ON DELETE CASCADE,
  source_url text NOT NULL,
  source_quote text,
  source_title text,
  published_at timestamptz,
  lang text DEFAULT 'en',
  fetched_at timestamptz NOT NULL DEFAULT now(),
  metadata jsonb DEFAULT '{}',
  UNIQUE (incident_id, source_url)
);

CREATE INDEX IF NOT EXISTS idx_incident_sources_incident ON public.incident_sources(incident_id);
CREATE INDEX IF NOT EXISTS idx_incident_sources_source ON public.incident_sources(source_id);
CREATE INDEX IF NOT EXISTS idx_incident_sources_url ON public.incident_sources(source_url);

-- =========================
-- Evidence Score Recalculation Trigger
-- =========================
-- Automatically recalculates incident evidence_score when sources change
-- Logic:
-- - Score 4 (OFFICIAL): ANY official source (police/military/NOTAM/aviation, trust_weight=4)
-- - Score 3 (VERIFIED): 2+ media sources (trust_weight≥2) WITH official quote detection
-- - Score 2 (REPORTED): Single credible source (trust_weight ≥ 2)
-- - Score 1 (UNCONFIRMED): Low trust sources (trust_weight < 2)

CREATE OR REPLACE FUNCTION update_evidence_score() RETURNS TRIGGER AS $$
DECLARE
    max_trust decimal(3,2);
    source_count int;
    official_count int;
    media_count int;
    has_quote boolean;
    new_score int;
BEGIN
    -- Get source statistics for this incident
    SELECT
        MAX(s.trust_weight),
        COUNT(*),
        COUNT(*) FILTER (WHERE s.trust_weight >= 4),
        COUNT(*) FILTER (WHERE s.trust_weight >= 2 AND s.trust_weight < 4),
        bool_or(is2.source_quote IS NOT NULL AND is2.source_quote != '')
    INTO max_trust, source_count, official_count, media_count, has_quote
    FROM public.incident_sources is2
    JOIN public.sources s ON is2.source_id = s.id
    WHERE is2.incident_id = COALESCE(NEW.incident_id, OLD.incident_id);

    -- Calculate evidence score
    IF official_count > 0 THEN
        new_score := 4;  -- OFFICIAL: Has police/military/NOTAM/aviation source
    ELSIF media_count >= 2 AND has_quote THEN
        new_score := 3;  -- VERIFIED: 2+ media sources with official quotes
    ELSIF max_trust >= 2 THEN
        new_score := 2;  -- REPORTED: Single credible source
    ELSE
        new_score := 1;  -- UNCONFIRMED: Low trust sources only
    END IF;

    -- Update incident evidence score
    UPDATE public.incidents
    SET evidence_score = new_score
    WHERE id = COALESCE(NEW.incident_id, OLD.incident_id);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger on incident_sources table
DROP TRIGGER IF EXISTS trigger_update_evidence_score ON public.incident_sources;
CREATE TRIGGER trigger_update_evidence_score
    AFTER INSERT OR UPDATE OR DELETE ON public.incident_sources
    FOR EACH ROW
    EXECUTE FUNCTION update_evidence_score();

-- =========================
-- Comments for documentation
-- =========================
COMMENT ON TABLE public.sources IS 'Publishers and news feeds that provide incident data';
COMMENT ON TABLE public.incident_sources IS 'Many-to-many relationship between incidents and sources';
COMMENT ON COLUMN public.sources.trust_weight IS 'Trust score: 4=police/official, 3=verified media, 2=media, 1=social';
COMMENT ON COLUMN public.incident_sources.source_quote IS 'Official quote from police/authority (for evidence verification)';
COMMENT ON FUNCTION update_evidence_score() IS 'Automatically recalculates evidence_score based on source trust_weights';

-- =========================
-- Record migration execution
-- =========================
INSERT INTO public.schema_migrations (version, description, executed_by)
VALUES (
    '018',
    'Create sources and incident_sources tables with evidence scoring trigger',
    current_user
)
ON CONFLICT (version) DO NOTHING;
