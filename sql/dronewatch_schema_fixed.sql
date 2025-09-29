-- DroneWatch Complete Schema - Fixed for Multiple Districts
-- Supports multiple police districts from same domain

-- ============================================
-- CLEANUP (uncomment to start completely fresh)
-- ============================================
-- DROP TABLE IF EXISTS public.incident_sources, public.incidents, public.sources, public.assets, public.ingestion_log CASCADE;
-- DROP FUNCTION IF EXISTS public.upsert_incident_v2;
-- DROP VIEW IF EXISTS public.v_incidents;

-- ============================================
-- EXTENSIONS
-- ============================================
CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================
-- ASSETS TABLE
-- ============================================
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

-- ============================================
-- SOURCES TABLE - FIXED
-- ============================================
CREATE TABLE IF NOT EXISTS public.sources (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  domain text,
  source_type text NOT NULL CHECK (source_type IN ('police','notam','media','social','osint','other')),
  homepage_url text,
  feed_url text,
  trust_weight int NOT NULL DEFAULT 1 CHECK (trust_weight BETWEEN 1 AND 4),
  country text,
  district text,  -- NEW: for police districts, media regions, etc.
  is_active boolean DEFAULT true,
  last_checked_at timestamptz,
  metadata jsonb DEFAULT '{}',
  created_at timestamptz NOT NULL DEFAULT now(),
  -- CHANGED: Make combination of domain, source_type, AND homepage_url unique
  -- This allows multiple police districts from politi.dk
  UNIQUE (domain, source_type, homepage_url)
);

CREATE INDEX IF NOT EXISTS idx_sources_active ON public.sources(is_active);
CREATE INDEX IF NOT EXISTS idx_sources_type ON public.sources(source_type);
CREATE INDEX IF NOT EXISTS idx_sources_domain ON public.sources(domain);
CREATE INDEX IF NOT EXISTS idx_sources_district ON public.sources(district);

-- ============================================
-- INCIDENTS TABLE
-- ============================================
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
  confirmations jsonb DEFAULT '[]',
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

-- ============================================
-- INCIDENT SOURCES TABLE
-- ============================================
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

-- ============================================
-- INGESTION LOG TABLE
-- ============================================
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

-- ============================================
-- ROW LEVEL SECURITY
-- ============================================
ALTER TABLE public.incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.incident_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ingestion_log ENABLE ROW LEVEL SECURITY;

-- Read-only policies for anon role
CREATE POLICY "anon_read_incidents" ON public.incidents
  FOR SELECT USING (true);
CREATE POLICY "anon_read_sources" ON public.sources
  FOR SELECT USING (true);
CREATE POLICY "anon_read_assets" ON public.assets
  FOR SELECT USING (true);
CREATE POLICY "anon_read_incident_sources" ON public.incident_sources
  FOR SELECT USING (true);
-- Note: ingestion_log remains internal only (no anon policy)

-- ============================================
-- FUNCTIONS
-- ============================================

-- Upsert function for incidents
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

-- ============================================
-- VIEWS
-- ============================================

-- View with lat/lon exposed
CREATE OR REPLACE VIEW public.v_incidents AS
SELECT
  i.*,
  ST_Y(i.location::geometry) AS lat,
  ST_X(i.location::geometry) AS lon,
  a.name AS asset_name,
  a.type AS asset_type_ref
FROM public.incidents i
LEFT JOIN public.assets a ON i.asset_id = a.id;

-- ============================================
-- INITIAL DATA - ASSETS
-- ============================================

-- Danish airports and harbors
INSERT INTO public.assets(name, type, location, icao, iata, country, region) VALUES
('Copenhagen Airport', 'airport', ST_SetSRID(ST_MakePoint(12.6476, 55.6180), 4326)::geography, 'EKCH', 'CPH', 'DK', 'Zealand'),
('Aalborg Airport', 'airport', ST_SetSRID(ST_MakePoint(9.8492, 57.0928), 4326)::geography, 'EKYT', 'AAL', 'DK', 'Jutland'),
('Billund Airport', 'airport', ST_SetSRID(ST_MakePoint(9.1518, 55.7403), 4326)::geography, 'EKBI', 'BLL', 'DK', 'Jutland'),
('Aarhus Airport', 'airport', ST_SetSRID(ST_MakePoint(10.6190, 56.3000), 4326)::geography, 'EKAH', 'AAR', 'DK', 'Jutland'),
('Odense Airport', 'airport', ST_SetSRID(ST_MakePoint(10.3306, 55.4764), 4326)::geography, 'EKOD', 'ODE', 'DK', 'Funen'),
('Roskilde Airport', 'airport', ST_SetSRID(ST_MakePoint(12.1314, 55.5856), 4326)::geography, 'EKRK', 'RKE', 'DK', 'Zealand'),
('Bornholm Airport', 'airport', ST_SetSRID(ST_MakePoint(14.7596, 55.0633), 4326)::geography, 'EKRN', 'RNN', 'DK', 'Bornholm'),
('Copenhagen Harbor', 'harbor', ST_SetSRID(ST_MakePoint(12.6000, 55.6900), 4326)::geography, NULL, NULL, 'DK', 'Zealand'),
('Aarhus Harbor', 'harbor', ST_SetSRID(ST_MakePoint(10.2270, 56.1500), 4326)::geography, NULL, NULL, 'DK', 'Jutland'),
('Aalborg Harbor', 'harbor', ST_SetSRID(ST_MakePoint(9.9190, 57.0556), 4326)::geography, NULL, NULL, 'DK', 'Jutland'),
('Esbjerg Harbor', 'harbor', ST_SetSRID(ST_MakePoint(8.4450, 55.4650), 4326)::geography, NULL, NULL, 'DK', 'Jutland'),
('Frederikshavn Harbor', 'harbor', ST_SetSRID(ST_MakePoint(10.5460, 57.4370), 4326)::geography, NULL, NULL, 'DK', 'Jutland')
ON CONFLICT DO NOTHING;

-- ============================================
-- INITIAL DATA - SOURCES (ALL DISTRICTS)
-- ============================================

-- Now we can insert all police districts without conflict!
INSERT INTO public.sources(name, domain, source_type, homepage_url, district, trust_weight, country) VALUES
-- Danish Police Districts
('Nordjyllands Politi', 'politi.dk', 'police', 'https://politi.dk/nordjyllands-politi', 'Nordjylland', 4, 'DK'),
('Københavns Politi', 'politi.dk', 'police', 'https://politi.dk/koebenhavns-politi', 'København', 4, 'DK'),
('Østjyllands Politi', 'politi.dk', 'police', 'https://politi.dk/oestjyllands-politi', 'Østjylland', 4, 'DK'),
('Midt- og Vestjyllands Politi', 'politi.dk', 'police', 'https://politi.dk/midt-og-vestjyllands-politi', 'Midt- og Vestjylland', 4, 'DK'),
('Sydøstjyllands Politi', 'politi.dk', 'police', 'https://politi.dk/sydoestjyllands-politi', 'Sydøstjylland', 4, 'DK'),
('Syd- og Sønderjyllands Politi', 'politi.dk', 'police', 'https://politi.dk/syd-og-soenderjyllands-politi', 'Syd- og Sønderjylland', 4, 'DK'),
('Fyns Politi', 'politi.dk', 'police', 'https://politi.dk/fyns-politi', 'Fyn', 4, 'DK'),
('Sydsjællands og Lolland-Falsters Politi', 'politi.dk', 'police', 'https://politi.dk/sydsjaellands-og-lolland-falsters-politi', 'Sydsjælland og Lolland-Falster', 4, 'DK'),
('Midt- og Vestsjællands Politi', 'politi.dk', 'police', 'https://politi.dk/midt-og-vestsjaellands-politi', 'Midt- og Vestsjælland', 4, 'DK'),
('Nordsjællands Politi', 'politi.dk', 'police', 'https://politi.dk/nordsjaellands-politi', 'Nordsjælland', 4, 'DK'),
('Københavns Vestegns Politi', 'politi.dk', 'police', 'https://politi.dk/koebenhavns-vestegns-politi', 'Københavns Vestegn', 4, 'DK'),
('Bornholms Politi', 'politi.dk', 'police', 'https://politi.dk/bornholms-politi', 'Bornholm', 4, 'DK'),

-- Media sources
('DR Nyheder', 'dr.dk', 'media', 'https://www.dr.dk', NULL, 3, 'DK'),
('TV2 News', 'tv2.dk', 'media', 'https://tv2.dk', NULL, 3, 'DK'),
('Berlingske', 'berlingske.dk', 'media', 'https://www.berlingske.dk', NULL, 3, 'DK'),
('Politiken', 'politiken.dk', 'media', 'https://politiken.dk', NULL, 3, 'DK'),
('Jyllands-Posten', 'jyllands-posten.dk', 'media', 'https://jyllands-posten.dk', NULL, 3, 'DK'),
('Reuters Nordic', 'reuters.com', 'media', 'https://www.reuters.com', 'Nordic', 3, 'INT'),

-- NOTAM sources
('NOTAM Denmark', 'notams.aim.faa.gov', 'notam', 'https://notams.aim.faa.gov', NULL, 4, 'DK'),
('Eurocontrol', 'eurocontrol.int', 'notam', 'https://www.eurocontrol.int', NULL, 4, 'EU'),
('Naviair', 'naviair.dk', 'notam', 'https://www.naviair.dk', NULL, 4, 'DK')

ON CONFLICT (domain, source_type, homepage_url) DO UPDATE
SET
  trust_weight = EXCLUDED.trust_weight,
  district = EXCLUDED.district,
  is_active = true;

-- ============================================
-- HELPFUL QUERIES
-- ============================================

-- View all police districts
-- SELECT name, district FROM public.sources WHERE source_type = 'police' ORDER BY district;

-- Count sources by type
-- SELECT source_type, COUNT(*) FROM public.sources GROUP BY source_type;

-- ============================================
-- MIGRATION FROM OLD SCHEMA
-- ============================================

-- If you have the old schema with UNIQUE(domain, source_type):
/*
-- 1. Drop the old constraint
ALTER TABLE public.sources DROP CONSTRAINT IF EXISTS sources_domain_source_type_key;

-- 2. Add district column
ALTER TABLE public.sources ADD COLUMN IF NOT EXISTS district text;

-- 3. Add new constraint
ALTER TABLE public.sources ADD CONSTRAINT sources_domain_type_url_unique
  UNIQUE (domain, source_type, homepage_url);
*/