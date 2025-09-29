-- DroneWatch Schema V2 - Enhanced for production ingestion
-- Drop existing tables if needed (careful in production!)
-- DROP TABLE IF EXISTS public.incident_sources, public.incidents, public.sources, public.assets CASCADE;

-- Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;

-- =========================
-- Assets (airports/harbors/military sites)
-- =========================
CREATE TABLE IF NOT EXISTS public.assets (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  type text NOT NULL CHECK (type IN ('airport','harbor','military','powerplant','bridge','other')),
  location geography(Point, 4326) NOT NULL,
  icao text,
  iata text,
  country text NOT NULL,
  region text,
  metadata jsonb DEFAULT '{}',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_assets_gix ON public.assets USING gist (location);
CREATE INDEX IF NOT EXISTS idx_assets_type ON public.assets(type);
CREATE INDEX IF NOT EXISTS idx_assets_country ON public.assets(country);

-- =========================
-- Sources (publishers/feeds)
-- =========================
CREATE TABLE IF NOT EXISTS public.sources (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  domain text,
  source_type text NOT NULL CHECK (source_type IN ('police','notam','media','social','osint','other')),
  homepage_url text,
  feed_url text,
  trust_weight int NOT NULL DEFAULT 1 CHECK (trust_weight BETWEEN 1 AND 4),
  country text,
  is_active boolean DEFAULT true,
  last_checked_at timestamptz,
  metadata jsonb DEFAULT '{}',
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (domain, source_type)
);

CREATE INDEX IF NOT EXISTS idx_sources_active ON public.sources(is_active);
CREATE INDEX IF NOT EXISTS idx_sources_type ON public.sources(source_type);

-- =========================
-- Incidents (core events)
-- =========================
CREATE TABLE IF NOT EXISTS public.incidents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Core fields
  title text NOT NULL,
  narrative text,
  occurred_at timestamptz NOT NULL,

  -- Location
  location geography(Point, 4326) NOT NULL,
  location_name text,
  asset_type text CHECK (asset_type IN ('airport','harbor','military','powerplant','bridge','other')),
  asset_id uuid REFERENCES public.assets(id),

  -- Status tracking
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active','resolved','unconfirmed','false_positive')),
  evidence_score int NOT NULL DEFAULT 1 CHECK (evidence_score BETWEEN 1 AND 4),
  verification_status text DEFAULT 'pending' CHECK (verification_status IN ('pending','verified','rejected','auto_verified')),

  -- Geographic
  country text NOT NULL,
  region text,

  -- Deduplication
  content_hash text UNIQUE,

  -- Metadata
  extracted_quotes jsonb DEFAULT '[]',
  confirmations jsonb DEFAULT '[]',  -- ["police","notam","airport_confirmed"]
  metadata jsonb DEFAULT '{}',

  -- Timestamps
  first_seen_at timestamptz NOT NULL DEFAULT now(),
  last_seen_at timestamptz NOT NULL DEFAULT now(),
  verified_at timestamptz,
  resolved_at timestamptz,

  -- Admin
  admin_notes text,
  verified_by text
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_incidents_gix ON public.incidents USING gist (location);
CREATE INDEX IF NOT EXISTS idx_incidents_time ON public.incidents(occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_incidents_evidence ON public.incidents(evidence_score);
CREATE INDEX IF NOT EXISTS idx_incidents_status ON public.incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_country ON public.incidents(country);
CREATE INDEX IF NOT EXISTS idx_incidents_hash ON public.incidents(content_hash);
CREATE INDEX IF NOT EXISTS idx_incidents_verification ON public.incidents(verification_status);

-- =========================
-- Incident Sources (many-to-many)
-- =========================
CREATE TABLE IF NOT EXISTS public.incident_sources (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  incident_id uuid NOT NULL REFERENCES public.incidents(id) ON DELETE CASCADE,
  source_id uuid NOT NULL REFERENCES public.sources(id),
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

-- =========================
-- Ingestion Log (track processing)
-- =========================
CREATE TABLE IF NOT EXISTS public.ingestion_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id uuid REFERENCES public.sources(id),
  run_at timestamptz NOT NULL DEFAULT now(),
  status text NOT NULL CHECK (status IN ('success','partial','failed')),
  items_found int DEFAULT 0,
  items_ingested int DEFAULT 0,
  items_skipped int DEFAULT 0,
  errors jsonb DEFAULT '[]',
  duration_ms int,
  metadata jsonb DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_ingestion_log_time ON public.ingestion_log(run_at DESC);
CREATE INDEX IF NOT EXISTS idx_ingestion_log_source ON public.ingestion_log(source_id);

-- =========================
-- RLS Policies
-- =========================
ALTER TABLE public.incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.incident_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ingestion_log ENABLE ROW LEVEL SECURITY;

-- Read-only for anon
CREATE POLICY "anon_read_incidents" ON public.incidents FOR SELECT USING (true);
CREATE POLICY "anon_read_sources" ON public.sources FOR SELECT USING (true);
CREATE POLICY "anon_read_assets" ON public.assets FOR SELECT USING (true);
CREATE POLICY "anon_read_incident_sources" ON public.incident_sources FOR SELECT USING (true);
-- Ingestion log is internal only

-- =========================
-- Helper Functions
-- =========================

-- Improved upsert with deduplication
CREATE OR REPLACE FUNCTION public.upsert_incident_v2(
  p_title text,
  p_narrative text,
  p_occurred_at timestamptz,
  p_lat double precision,
  p_lng double precision,
  p_location_name text,
  p_asset_type text,
  p_status text,
  p_evidence_score int,
  p_country text,
  p_content_hash text,
  p_quotes jsonb DEFAULT '[]',
  p_confirmations jsonb DEFAULT '[]'
) RETURNS uuid
LANGUAGE plpgsql AS $$
DECLARE
  v_id uuid;
  v_location geography;
BEGIN
  v_location := ST_SetSRID(ST_MakePoint(p_lng, p_lat), 4326)::geography;

  -- Check for existing by hash
  SELECT id INTO v_id FROM public.incidents WHERE content_hash = p_content_hash;

  IF v_id IS NULL THEN
    -- New incident
    INSERT INTO public.incidents(
      title, narrative, occurred_at, location, location_name,
      asset_type, status, evidence_score, country, content_hash,
      extracted_quotes, confirmations
    )
    VALUES(
      p_title, p_narrative, p_occurred_at, v_location, p_location_name,
      p_asset_type, p_status, p_evidence_score, p_country, p_content_hash,
      p_quotes, p_confirmations
    )
    RETURNING id INTO v_id;
  ELSE
    -- Update existing
    UPDATE public.incidents
    SET
      narrative = COALESCE(p_narrative, narrative),
      evidence_score = GREATEST(evidence_score, p_evidence_score),
      last_seen_at = now(),
      extracted_quotes = p_quotes,
      confirmations = p_confirmations
    WHERE id = v_id;
  END IF;

  RETURN v_id;
END$$;

-- View for easy querying with lat/lon
CREATE OR REPLACE VIEW public.v_incidents AS
SELECT
  i.*,
  ST_Y(i.location::geometry) AS lat,
  ST_X(i.location::geometry) AS lon,
  a.name AS asset_name,
  a.type AS asset_type_ref
FROM public.incidents i
LEFT JOIN public.assets a ON i.asset_id = a.id;

-- =========================
-- Initial Data
-- =========================

-- Danish assets
INSERT INTO public.assets(name, type, location, icao, iata, country, region) VALUES
('Copenhagen Airport', 'airport', ST_SetSRID(ST_MakePoint(12.6476, 55.6180), 4326)::geography, 'EKCH', 'CPH', 'DK', 'Zealand'),
('Aalborg Airport', 'airport', ST_SetSRID(ST_MakePoint(9.8492, 57.0928), 4326)::geography, 'EKYT', 'AAL', 'DK', 'Jutland'),
('Billund Airport', 'airport', ST_SetSRID(ST_MakePoint(9.1518, 55.7403), 4326)::geography, 'EKBI', 'BLL', 'DK', 'Jutland'),
('Copenhagen Harbor', 'harbor', ST_SetSRID(ST_MakePoint(12.6000, 55.6900), 4326)::geography, NULL, NULL, 'DK', 'Zealand'),
('Aarhus Harbor', 'harbor', ST_SetSRID(ST_MakePoint(10.2270, 56.1500), 4326)::geography, NULL, NULL, 'DK', 'Jutland')
ON CONFLICT DO NOTHING;

-- Initial sources
INSERT INTO public.sources(name, domain, source_type, homepage_url, trust_weight, country) VALUES
('Nordjyllands Politi', 'politi.dk', 'police', 'https://politi.dk/nordjyllands-politi', 4, 'DK'),
('Københavns Politi', 'politi.dk', 'police', 'https://politi.dk/koebenhavns-politi', 4, 'DK'),
('DR Nyheder', 'dr.dk', 'media', 'https://www.dr.dk', 3, 'DK'),
('Reuters Nordic', 'reuters.com', 'media', 'https://www.reuters.com', 3, 'INT'),
('NOTAM Denmark', 'notams.aim.faa.gov', 'notam', 'https://notams.aim.faa.gov', 4, 'DK')
ON CONFLICT (domain, source_type) DO UPDATE
SET trust_weight = EXCLUDED.trust_weight;