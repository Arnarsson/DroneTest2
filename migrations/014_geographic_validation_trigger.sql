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
    -- Excluded region keywords (WAR ZONES and non-EU regions ONLY)
    -- NOTE: EU countries are INCLUDED in coverage, not excluded!
    foreign_keywords TEXT[] := ARRAY[
        -- Eastern Europe WAR ZONES (highest priority to exclude)
        'ukraina', 'ukraine', 'ukrainsk', 'ukrainian', 'kiev', 'kyiv', 'odesa', 'kharkiv', 'lviv',
        'russia', 'rusland', 'russisk', 'russian', 'moscow', 'moskva', 'st. petersburg',
        'belarus', 'hviderusland', 'hviderussisk', 'belarusian', 'minsk',

        -- Middle East
        'israel', 'gaza', 'tel aviv', 'jerusalem',
        'iran', 'tehran', 'syria', 'damascus', 'iraq', 'baghdad',

        -- Asia
        'china', 'beijing', 'shanghai', 'japan', 'tokyo', 'korea', 'seoul', 'india', 'delhi', 'mumbai',

        -- Africa
        'africa', 'cairo', 'johannesburg', 'nairobi',

        -- Americas
        'united states', 'usa', 'washington', 'new york', 'canada', 'mexico'
    ];

    keyword TEXT;
    lat FLOAT;
    lon FLOAT;
BEGIN
    -- Extract coordinates from PostGIS geometry
    lat := ST_Y(NEW.location::geometry);
    lon := ST_X(NEW.location::geometry);

    -- VALIDATION 1: Coordinates must be in European coverage region (35-71°N, -10-31°E)
    -- Covers: Nordic + UK + Ireland + Western/Central Europe + Baltics
    IF lat NOT BETWEEN 35 AND 71 OR lon NOT BETWEEN -10 AND 31 THEN
        RAISE EXCEPTION 'Geographic validation failed: Coordinates outside European coverage region (lat=%, lon=%)', lat, lon
            USING HINT = 'European coverage: 35-71°N, -10-31°E (Nordic + UK + Western/Central Europe)';
    END IF;

    -- VALIDATION 2: Title AND narrative must not contain excluded region keywords
    -- This catches incidents like "Massive Russian drone attack over Ukraine"
    -- that have European coords from context mentions (e.g., "EU officials comment in Brussels")
    FOREACH keyword IN ARRAY foreign_keywords
    LOOP
        -- Check title
        IF LOWER(NEW.title) LIKE '%' || keyword || '%' THEN
            RAISE EXCEPTION 'Geographic validation failed: Excluded region incident detected in title (keyword: "%")', keyword
                USING HINT = 'Title: ' || NEW.title;
        END IF;

        -- Check narrative (if present)
        IF NEW.narrative IS NOT NULL AND LOWER(NEW.narrative) LIKE '%' || keyword || '%' THEN
            RAISE EXCEPTION 'Geographic validation failed: Excluded region incident detected in narrative (keyword: "%")', keyword
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
    RAISE NOTICE 'Coverage: 35-71°N, -10-31°E (European coverage)';
    RAISE NOTICE 'Includes: Nordic + UK + Ireland + Western/Central Europe + Baltics';
    RAISE NOTICE 'Excludes: War zones (Ukraine/Russia/Belarus), Middle East, Asia, Americas';
    RAISE NOTICE 'All incidents will now be validated at database level';
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
