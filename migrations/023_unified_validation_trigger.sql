-- Migration 023: Unified Validation Trigger
-- Date: 2025-11-25
-- Purpose: Consolidate all validation into a single authoritative trigger
--
-- This migration combines:
--   - Geographic bounds validation (35-71°N, -10-31°E)
--   - Foreign keyword rejection (Ukraine, Russia, Middle East, etc.)
--   - Content hash generation and uniqueness
--   - Evidence score recalculation
--
-- PRINCIPLE: Database is the SINGLE SOURCE OF TRUTH
-- Python validation is a fast pre-filter, database trigger is authoritative

BEGIN;

-- =====================================================
-- 1. Create unified validation function
-- =====================================================

CREATE OR REPLACE FUNCTION validate_and_prepare_incident()
RETURNS TRIGGER AS $$
DECLARE
    -- Geographic bounds for European coverage
    MIN_LAT CONSTANT FLOAT := 35.0;
    MAX_LAT CONSTANT FLOAT := 71.0;
    MIN_LON CONSTANT FLOAT := -10.0;
    MAX_LON CONSTANT FLOAT := 31.0;

    -- Non-European keywords (war zones + other continents)
    foreign_keywords TEXT[] := ARRAY[
        -- War zones (Eastern Europe beyond coverage)
        'ukraina', 'ukraine', 'ukrainian', 'kiev', 'kyiv', 'kharkiv', 'odesa', 'lviv',
        'russia', 'rusland', 'russian', 'moscow', 'moskva', 'putin',
        'belarus', 'belarusian', 'minsk',
        -- Middle East
        'israel', 'gaza', 'tel aviv', 'jerusalem', 'iran', 'tehran',
        'syria', 'damascus', 'iraq', 'baghdad', 'yemen', 'lebanon',
        -- Asia
        'china', 'beijing', 'shanghai', 'japan', 'tokyo', 'korea', 'seoul',
        'india', 'delhi', 'pakistan', 'afghanistan', 'taiwan',
        -- Americas
        'united states', 'usa', 'america', 'washington', 'new york',
        'canada', 'mexico', 'brazil', 'argentina',
        -- Africa
        'egypt', 'cairo', 'south africa', 'nigeria', 'kenya'
    ];

    lat FLOAT;
    lon FLOAT;
    keyword TEXT;
    full_text TEXT;
    max_trust INTEGER;
    source_count INTEGER;
    has_official_quote BOOLEAN;
BEGIN
    -- Extract coordinates
    lat := ST_Y(NEW.location::geometry);
    lon := ST_X(NEW.location::geometry);

    -- =========================================
    -- VALIDATION 1: Geographic Bounds
    -- =========================================
    IF lat NOT BETWEEN MIN_LAT AND MAX_LAT OR lon NOT BETWEEN MIN_LON AND MAX_LON THEN
        RAISE EXCEPTION 'VALIDATION_FAILED: Coordinates outside European coverage (lat=%, lon=%). Bounds: %-% N, %-% E',
            lat, lon, MIN_LAT, MAX_LAT, MIN_LON, MAX_LON;
    END IF;

    -- =========================================
    -- VALIDATION 2: Foreign Keyword Check
    -- =========================================
    full_text := LOWER(COALESCE(NEW.title, '') || ' ' || COALESCE(NEW.narrative, ''));

    FOREACH keyword IN ARRAY foreign_keywords LOOP
        IF full_text LIKE '%' || keyword || '%' THEN
            RAISE EXCEPTION 'VALIDATION_FAILED: Non-European incident detected (keyword: "%"). Title: %',
                keyword, LEFT(NEW.title, 100);
        END IF;
    END LOOP;

    -- =========================================
    -- PREPARATION 1: Generate Content Hash
    -- =========================================
    NEW.normalized_title := LOWER(REGEXP_REPLACE(TRIM(NEW.title), '[^a-z0-9 ]', '', 'g'));

    NEW.location_hash := SUBSTRING(MD5(CONCAT(
        ROUND(lon::numeric, 3)::text,
        ROUND(lat::numeric, 3)::text,
        COALESCE(NEW.asset_type, 'other')
    )), 1, 16);

    NEW.content_hash := MD5(CONCAT(
        NEW.occurred_at::date::text,
        ROUND(lon::numeric, 3)::text,
        ROUND(lat::numeric, 3)::text,
        NEW.normalized_title,
        COALESCE(NEW.asset_type, 'other')
    ));

    -- =========================================
    -- PREPARATION 2: Set Default Values
    -- =========================================
    IF NEW.country IS NULL THEN
        -- Determine country from coordinates (approximate)
        NEW.country := CASE
            WHEN lon BETWEEN 8 AND 15.5 AND lat BETWEEN 54.5 AND 58 THEN 'DK'  -- Denmark
            WHEN lon BETWEEN 4.5 AND 31 AND lat BETWEEN 57 AND 71 THEN 'NO'   -- Norway
            WHEN lon BETWEEN 10.5 AND 24 AND lat BETWEEN 55 AND 69 THEN 'SE'  -- Sweden
            WHEN lon BETWEEN 20 AND 31 AND lat BETWEEN 59 AND 70 THEN 'FI'    -- Finland
            WHEN lon BETWEEN -10 AND 2 AND lat BETWEEN 50 AND 59 THEN 'GB'    -- UK
            WHEN lon BETWEEN 5.5 AND 15 AND lat BETWEEN 47 AND 55 THEN 'DE'   -- Germany
            WHEN lon BETWEEN -5 AND 10 AND lat BETWEEN 42 AND 51 THEN 'FR'    -- France
            WHEN lon BETWEEN 3 AND 7 AND lat BETWEEN 50 AND 52 THEN 'NL'      -- Netherlands
            WHEN lon BETWEEN 14 AND 24 AND lat BETWEEN 49 AND 55 THEN 'PL'    -- Poland
            ELSE 'EU'  -- Generic European
        END;
    END IF;

    IF NEW.status IS NULL THEN
        NEW.status := 'active';
    END IF;

    IF NEW.created_at IS NULL THEN
        NEW.created_at := NOW();
    END IF;

    NEW.updated_at := NOW();

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION validate_and_prepare_incident() IS
    'Unified validation trigger: geographic bounds, foreign keywords, content hash generation.
     This is the SINGLE SOURCE OF TRUTH for incident validation.';

-- =====================================================
-- 2. Create trigger (replaces existing triggers)
-- =====================================================

-- Drop existing triggers to avoid conflicts
DROP TRIGGER IF EXISTS validate_incident_before_insert ON incidents;
DROP TRIGGER IF EXISTS incident_hashes_trigger ON incidents;

-- Create unified trigger
CREATE TRIGGER unified_incident_validation
    BEFORE INSERT OR UPDATE ON incidents
    FOR EACH ROW
    EXECUTE FUNCTION validate_and_prepare_incident();

-- =====================================================
-- 3. Create spatial deduplication function
-- =====================================================

CREATE OR REPLACE FUNCTION find_nearby_incident(
    p_lat FLOAT,
    p_lon FLOAT,
    p_asset_type TEXT,
    p_occurred_at TIMESTAMP WITH TIME ZONE,
    p_search_radius INTEGER DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    existing_id UUID;
    radius INTEGER;
BEGIN
    -- Asset-type-aware search radius
    radius := COALESCE(p_search_radius, CASE p_asset_type
        WHEN 'airport' THEN 3000    -- 3km for airports (larger facilities)
        WHEN 'military' THEN 3000   -- 3km for military bases
        WHEN 'harbor' THEN 1500     -- 1.5km for harbors
        WHEN 'powerplant' THEN 1000 -- 1km for power plants
        ELSE 500                    -- 500m for other/unknown
    END);

    -- Find existing incident within radius and 7-day window
    SELECT id INTO existing_id
    FROM incidents
    WHERE ST_DWithin(
        location::geography,
        ST_SetSRID(ST_MakePoint(p_lon, p_lat), 4326)::geography,
        radius
    )
    AND asset_type = p_asset_type
    AND ABS(EXTRACT(EPOCH FROM (occurred_at - p_occurred_at))) < 604800  -- 7 days in seconds
    ORDER BY
        ST_Distance(location::geography, ST_SetSRID(ST_MakePoint(p_lon, p_lat), 4326)::geography),
        ABS(EXTRACT(EPOCH FROM (occurred_at - p_occurred_at)))
    LIMIT 1;

    RETURN existing_id;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION find_nearby_incident(FLOAT, FLOAT, TEXT, TIMESTAMP WITH TIME ZONE, INTEGER) IS
    'Find existing incident within asset-type-aware radius and 7-day time window.
     Used for source consolidation (multiple sources for same incident).
     Returns NULL if no nearby incident found.';

-- =====================================================
-- 4. Create evidence score recalculation function
-- =====================================================

CREATE OR REPLACE FUNCTION recalculate_evidence_score(p_incident_id UUID)
RETURNS INTEGER AS $$
DECLARE
    max_trust INTEGER;
    source_count INTEGER;
    has_official_quote BOOLEAN;
    new_score INTEGER;
BEGIN
    -- Get source statistics
    SELECT
        COALESCE(MAX(trust_weight), 1),
        COUNT(*),
        EXISTS(SELECT 1 FROM incident_sources WHERE incident_id = p_incident_id AND source_quote IS NOT NULL)
    INTO max_trust, source_count, has_official_quote
    FROM incident_sources
    WHERE incident_id = p_incident_id;

    -- Calculate evidence score using 4-tier system
    -- Score 4: Official sources (trust_weight = 4)
    IF max_trust >= 4 THEN
        new_score := 4;
    -- Score 3: Multiple credible sources OR single with official quote
    ELSIF source_count >= 2 AND max_trust >= 3 THEN
        new_score := 3;
    ELSIF max_trust = 3 AND has_official_quote THEN
        new_score := 3;
    -- Score 2: Single credible source
    ELSIF max_trust >= 2 THEN
        new_score := 2;
    -- Score 1: Low trust or no sources
    ELSE
        new_score := 1;
    END IF;

    -- Update incident
    UPDATE incidents SET evidence_score = new_score, updated_at = NOW()
    WHERE id = p_incident_id AND evidence_score != new_score;

    RETURN new_score;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION recalculate_evidence_score(UUID) IS
    'Recalculate evidence score based on sources.
     4-tier system: Official (4) > Verified (3) > Reported (2) > Unconfirmed (1)';

-- =====================================================
-- 5. Auto-recalculate evidence when sources change
-- =====================================================

CREATE OR REPLACE FUNCTION trigger_recalculate_evidence()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        PERFORM recalculate_evidence_score(OLD.incident_id);
        RETURN OLD;
    ELSE
        PERFORM recalculate_evidence_score(NEW.incident_id);
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS recalc_evidence_on_source_change ON incident_sources;

CREATE TRIGGER recalc_evidence_on_source_change
    AFTER INSERT OR UPDATE OR DELETE ON incident_sources
    FOR EACH ROW
    EXECUTE FUNCTION trigger_recalculate_evidence();

-- =====================================================
-- 6. Verify migration
-- =====================================================

DO $$
DECLARE
    trigger_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO trigger_count
    FROM pg_trigger
    WHERE tgrelid = 'incidents'::regclass
    AND tgname = 'unified_incident_validation';

    IF trigger_count = 1 THEN
        RAISE NOTICE '✅ Migration 023 Complete: Unified validation trigger installed';
        RAISE NOTICE '   - Geographic bounds: 35-71°N, -10-31°E (Europe)';
        RAISE NOTICE '   - Foreign keyword rejection: Active';
        RAISE NOTICE '   - Content hash generation: Active';
        RAISE NOTICE '   - Evidence score auto-recalculation: Active';
    ELSE
        RAISE EXCEPTION 'Migration 023 Failed: Trigger not installed correctly';
    END IF;
END $$;

COMMIT;

-- =====================================================
-- Post-Migration Notes
-- =====================================================
--
-- This migration creates a SINGLE SOURCE OF TRUTH for validation:
-- 1. All incidents MUST pass geographic bounds check
-- 2. All incidents MUST NOT contain foreign keywords
-- 3. Content hash is auto-generated for duplicate detection
-- 4. Evidence score is auto-recalculated when sources change
--
-- Python-side validation (Layer 1-2) is now a FAST PRE-FILTER.
-- Database trigger (Layer 4) is AUTHORITATIVE - nothing bypasses it.
--
-- Testing:
--   1. Valid European incident: Should insert successfully
--   2. Out-of-bounds incident: Should fail with VALIDATION_FAILED
--   3. Foreign keyword incident: Should fail with VALIDATION_FAILED
--   4. Duplicate incident: Should fail with unique constraint violation
