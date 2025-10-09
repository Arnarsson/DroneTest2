-- Migration 015: Expand Geographic Coverage to All of Europe
-- Updates database-level validation to support European coverage (not just Nordic)
-- Aligns with Python filter: 35-71°N, -10-31°E

-- CONTEXT:
-- Previous migration 014 restricted to Nordic region (54-71°N, 4-31°E)
-- This expansion enables incidents from UK, Germany, France, Spain, Italy, Poland, Benelux, Baltics
-- Matches ingestion/utils.py is_nordic_incident() function

-- SAFE TO RUN:
-- Only updates validation logic, does not modify existing data
-- Incidents from expanded region will now be accepted

-- Verify table exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'incidents') THEN
        RAISE EXCEPTION 'Table public.incidents does not exist! Check your database connection.';
    END IF;
END $$;

-- Drop existing trigger (will be recreated with new bounds)
DROP TRIGGER IF EXISTS validate_incident_before_insert ON public.incidents;
DROP FUNCTION IF EXISTS validate_incident_geography();

-- Create updated validation function with European bounds
CREATE OR REPLACE FUNCTION validate_incident_geography()
RETURNS TRIGGER AS $$
DECLARE
    -- Non-European country/location keywords (matching Python filter)
    -- These are locations OUTSIDE our coverage region
    foreign_keywords TEXT[] := ARRAY[
        -- Eastern Europe (WAR ZONES - outside coverage)
        'ukraina', 'ukraine', 'ukrainsk', 'ukrainian', 'kiev', 'kyiv', 'odesa', 'kharkiv', 'lviv',
        'russia', 'rusland', 'russisk', 'russian', 'moscow', 'moskva', 'st. petersburg',
        'belarus', 'hviderusland', 'hviderussisk', 'belarusian', 'minsk',

        -- Middle East
        'israel', 'gaza', 'tel aviv', 'jerusalem',
        'iran', 'tehran', 'syria', 'damascus', 'iraq', 'baghdad',
        'saudi arabia', 'yemen', 'lebanon', 'beirut',

        -- Asia
        'china', 'beijing', 'shanghai', 'japan', 'tokyo', 'korea', 'seoul',
        'india', 'delhi', 'mumbai', 'pakistan', 'afghanistan', 'thailand', 'vietnam',

        -- Americas
        'united states', 'usa', 'america', 'washington', 'new york', 'california',
        'canada', 'toronto', 'vancouver', 'mexico',
        'brazil', 'argentina', 'chile',

        -- Africa
        'egypt', 'cairo', 'south africa', 'nigeria', 'kenya'
    ];

    keyword TEXT;
    lat FLOAT;
    lon FLOAT;
BEGIN
    -- Extract coordinates from PostGIS geometry
    lat := ST_Y(NEW.location::geometry);
    lon := ST_X(NEW.location::geometry);

    -- VALIDATION 1: Coordinates must be in European region (35-71°N, -10-31°E)
    -- Covers: Nordic + UK + Ireland + Western/Central Europe + Baltics + Mediterranean
    IF lat NOT BETWEEN 35 AND 71 OR lon NOT BETWEEN -10 AND 31 THEN
        RAISE EXCEPTION 'Geographic validation failed: Coordinates outside European coverage region (lat=%, lon=%)', lat, lon
            USING HINT = 'European region: 35-71°N, -10-31°E (Nordic + UK + Germany + France + Spain + Italy + Poland + Benelux + Baltics)';
    END IF;

    -- VALIDATION 2: Title AND narrative must not contain NON-European location keywords
    -- This catches war zone incidents (Ukraine, Russia, Middle East) that have European coords from context mentions
    FOREACH keyword IN ARRAY foreign_keywords
    LOOP
        -- Check title
        IF LOWER(NEW.title) LIKE '%' || keyword || '%' THEN
            RAISE EXCEPTION 'Geographic validation failed: Non-European incident detected in title (keyword: "%")', keyword
                USING HINT = 'Title: ' || NEW.title;
        END IF;

        -- Check narrative (if present)
        IF NEW.narrative IS NOT NULL AND LOWER(NEW.narrative) LIKE '%' || keyword || '%' THEN
            RAISE EXCEPTION 'Geographic validation failed: Non-European incident detected in narrative (keyword: "%")', keyword
                USING HINT = 'Title: ' || NEW.title || ', Narrative contains: ' || keyword;
        END IF;
    END LOOP;

    -- All validations passed
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger that runs BEFORE INSERT or UPDATE
CREATE TRIGGER validate_incident_before_insert
    BEFORE INSERT OR UPDATE ON public.incidents
    FOR EACH ROW
    EXECUTE FUNCTION validate_incident_geography();

-- Log trigger creation
DO $$
BEGIN
    RAISE NOTICE '✅ European coverage validation trigger created successfully';
    RAISE NOTICE '📍 Geographic bounds: 35-71°N, -10-31°E';
    RAISE NOTICE '🌍 Coverage: Nordic + UK + Ireland + Germany + France + Spain + Italy + Poland + Benelux + Baltics';
    RAISE NOTICE '🚫 Blocked: Ukraine, Russia, Middle East, Asia, Americas, Africa';
END $$;

-- TESTING:
-- Test 1: Nordic incident (should PASS)
-- INSERT INTO public.incidents (title, narrative, location, occurred_at, evidence_score, status)
-- VALUES (
--     'Drone spotted near Copenhagen Airport',
--     'Danish police investigate drone sighting',
--     ST_SetSRID(ST_MakePoint(12.6476, 55.618), 4326)::geography,
--     NOW(), 3, 'active'
-- );

-- Test 2: German incident (should PASS with new bounds)
-- INSERT INTO public.incidents (title, narrative, location, occurred_at, evidence_score, status)
-- VALUES (
--     'Drohne über Berlin Flughafen gesichtet',
--     'German police investigate drone sighting near airport',
--     ST_SetSRID(ST_MakePoint(13.4050, 52.5200), 4326)::geography,
--     NOW(), 3, 'active'
-- );

-- Test 3: Ukrainian incident (should FAIL - war zone)
-- INSERT INTO public.incidents (title, narrative, location, occurred_at, evidence_score, status)
-- VALUES (
--     'Massivt russisk droneangrep over hele Ukraina',
--     'Multiple drone attacks across Ukraine',
--     ST_SetSRID(ST_MakePoint(30.5234, 50.4501), 4326)::geography,
--     NOW(), 3, 'active'
-- );
-- Expected: ERROR: Geographic validation failed: Non-European incident detected in title (keyword: "ukraina")

-- VERIFICATION:
-- Check trigger exists:
-- SELECT tgname, tgenabled FROM pg_trigger WHERE tgrelid = 'public.incidents'::regclass;
