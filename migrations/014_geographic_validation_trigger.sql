-- Migration 014: Geographic Validation Trigger
-- Creates database-level validation to prevent foreign incidents from being inserted
-- This is the FIRST LINE OF DEFENSE - works even if scrapers use old code

-- CONTEXT:
-- Manual cleanup is reactive and error-prone. This trigger validates ALL incidents
-- at insertion time, rejecting foreign incidents regardless of scraper version.

-- SAFE TO RUN:
-- This migration only adds validation logic, does not modify existing data.
-- Failed inserts will return clear error messages for debugging.

-- Verify table exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'incidents') THEN
        RAISE EXCEPTION 'Table public.incidents does not exist! Check your database connection.';
    END IF;
END $$;

-- Drop existing trigger if it exists (for re-running migration)
DROP TRIGGER IF EXISTS validate_incident_before_insert ON public.incidents;
DROP FUNCTION IF EXISTS validate_incident_geography();

-- Create validation function
CREATE OR REPLACE FUNCTION validate_incident_geography()
RETURNS TRIGGER AS $$
DECLARE
    -- Foreign country/location keywords (matching Python filter)
    foreign_keywords TEXT[] := ARRAY[
        -- Eastern Europe
        'ukraina', 'ukraine', 'ukrainsk', 'ukrainian', 'kiev', 'kyiv', 'odesa', 'kharkiv',
        'russia', 'rusland', 'russisk', 'russian', 'moscow', 'moskva',
        'belarus', 'hviderusland', 'hviderussisk', 'belarusian', 'minsk',
        'poland', 'polen', 'polsk', 'polish', 'warsaw', 'warszawa', 'krakow',

        -- Central/Western Europe
        'germany', 'tyskland', 'tysk', 'german', 'berlin', 'münchen', 'munich', 'hamburg',
        'france', 'frankrig', 'fransk', 'french', 'paris',
        'netherlands', 'holland', 'nederlandsk', 'dutch', 'amsterdam',
        'belgium', 'belgien', 'belgisk', 'belgian', 'brussels',
        'uk', 'england', 'britain', 'britisk', 'british', 'london',
        'spain', 'spanien', 'spansk', 'spanish', 'madrid', 'barcelona',
        'italy', 'italien', 'italiensk', 'italian', 'rome', 'milano',

        -- Baltic states
        'estonia', 'estland', 'estisk', 'estonian', 'tallinn',
        'latvia', 'letland', 'lettisk', 'latvian', 'riga',
        'lithuania', 'litauen', 'litauisk', 'lithuanian', 'vilnius'
    ];

    keyword TEXT;
    lat FLOAT;
    lon FLOAT;
BEGIN
    -- Extract coordinates from PostGIS geometry
    lat := ST_Y(NEW.location::geometry);
    lon := ST_X(NEW.location::geometry);

    -- VALIDATION 1: Coordinates must be in Nordic region (54-71°N, 4-31°E)
    IF lat NOT BETWEEN 54 AND 71 OR lon NOT BETWEEN 4 AND 31 THEN
        RAISE EXCEPTION 'Geographic validation failed: Coordinates outside Nordic region (lat=%, lon=%)', lat, lon
            USING HINT = 'Nordic region: 54-71°N, 4-31°E';
    END IF;

    -- VALIDATION 2: Title AND narrative must not contain foreign location keywords
    -- This catches incidents like "Massive Russian drone attack over Ukraine"
    -- that have Nordic coords from context mentions (e.g., "Danish officials comment")
    FOREACH keyword IN ARRAY foreign_keywords
    LOOP
        -- Check title
        IF LOWER(NEW.title) LIKE '%' || keyword || '%' THEN
            RAISE EXCEPTION 'Geographic validation failed: Foreign incident detected in title (keyword: "%")', keyword
                USING HINT = 'Title: ' || NEW.title;
        END IF;

        -- Check narrative (if present)
        IF NEW.narrative IS NOT NULL AND LOWER(NEW.narrative) LIKE '%' || keyword || '%' THEN
            RAISE EXCEPTION 'Geographic validation failed: Foreign incident detected in narrative (keyword: "%")', keyword
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
    RAISE NOTICE 'Geographic validation trigger created successfully';
    RAISE NOTICE 'All incidents will now be validated at database level';
    RAISE NOTICE 'Foreign incidents will be rejected with clear error messages';
END $$;

-- TESTING:
-- Try to insert Ukrainian incident (should be rejected):
-- INSERT INTO public.incidents (title, narrative, location, occurred_at, evidence_score, status)
-- VALUES (
--     'Massivt russisk droneangrep over hele Ukraina',
--     'Multiple drone attacks across Ukraine',
--     ST_SetSRID(ST_MakePoint(12.6476, 55.618), 4326)::geography,
--     NOW(),
--     3,
--     'active'
-- );
-- Expected: ERROR: Geographic validation failed: Foreign incident detected in title (keyword: "ukraina")

-- VERIFICATION:
-- Check trigger exists:
-- SELECT tgname, tgenabled FROM pg_trigger WHERE tgrelid = 'public.incidents'::regclass;
