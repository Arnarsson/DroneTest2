-- Migration 019: Fix Existing Country Codes (Backfill)
-- Date: 2025-10-14
-- Author: Claude Code
-- Description: Update country codes for existing incidents using coordinate-based detection
--
-- Context: Before migration 018 (get_country_from_coordinates), all incidents were hardcoded as "DK".
-- This migration backfills correct country codes for existing incidents based on their coordinates.

-- Function to determine country from coordinates (mirrors Python implementation)
CREATE OR REPLACE FUNCTION get_country_from_coordinates_sql(lat DOUBLE PRECISION, lon DOUBLE PRECISION)
RETURNS VARCHAR(2) AS $$
BEGIN
    -- Denmark
    IF lat BETWEEN 54.5 AND 58.0 AND lon BETWEEN 8.0 AND 15.5 THEN
        RETURN 'DK';

    -- Norway
    ELSIF lat BETWEEN 57.5 AND 71.5 AND lon BETWEEN 4.5 AND 31.5 THEN
        RETURN 'NO';

    -- Sweden
    ELSIF lat BETWEEN 55.0 AND 69.5 AND lon BETWEEN 10.5 AND 24.5 THEN
        RETURN 'SE';

    -- Finland
    ELSIF lat BETWEEN 59.5 AND 70.5 AND lon BETWEEN 19.0 AND 32.0 THEN
        RETURN 'FI';

    -- United Kingdom
    ELSIF lat BETWEEN 49.5 AND 61.0 AND lon BETWEEN -8.5 AND 2.0 THEN
        RETURN 'GB';

    -- Ireland
    ELSIF lat BETWEEN 51.0 AND 56.0 AND lon BETWEEN -11.0 AND -5.5 THEN
        RETURN 'IE';

    -- Germany
    ELSIF lat BETWEEN 47.0 AND 55.5 AND lon BETWEEN 5.5 AND 15.5 THEN
        RETURN 'DE';

    -- France
    ELSIF lat BETWEEN 41.0 AND 51.5 AND lon BETWEEN -5.5 AND 10.0 THEN
        RETURN 'FR';

    -- Spain
    ELSIF lat BETWEEN 35.5 AND 44.0 AND lon BETWEEN -10.0 AND 5.0 THEN
        RETURN 'ES';

    -- Italy
    ELSIF lat BETWEEN 35.5 AND 47.5 AND lon BETWEEN 6.0 AND 19.0 THEN
        RETURN 'IT';

    -- Poland
    ELSIF lat BETWEEN 49.0 AND 55.0 AND lon BETWEEN 14.0 AND 25.0 THEN
        RETURN 'PL';

    -- Netherlands
    ELSIF lat BETWEEN 50.5 AND 54.0 AND lon BETWEEN 3.0 AND 7.5 THEN
        RETURN 'NL';

    -- Belgium
    ELSIF lat BETWEEN 49.5 AND 51.5 AND lon BETWEEN 2.5 AND 6.5 THEN
        RETURN 'BE';

    -- Austria
    ELSIF lat BETWEEN 46.0 AND 49.5 AND lon BETWEEN 9.0 AND 17.5 THEN
        RETURN 'AT';

    -- Switzerland
    ELSIF lat BETWEEN 45.5 AND 48.0 AND lon BETWEEN 5.5 AND 11.0 THEN
        RETURN 'CH';

    -- Latvia
    ELSIF lat BETWEEN 55.5 AND 58.5 AND lon BETWEEN 20.5 AND 28.5 THEN
        RETURN 'LV';

    -- Estonia
    ELSIF lat BETWEEN 57.5 AND 60.0 AND lon BETWEEN 21.5 AND 28.5 THEN
        RETURN 'EE';

    -- Lithuania
    ELSIF lat BETWEEN 53.5 AND 56.5 AND lon BETWEEN 20.5 AND 27.0 THEN
        RETURN 'LT';

    -- Unknown/Other
    ELSE
        RETURN 'XX';
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Backup current country codes (for rollback if needed)
CREATE TABLE IF NOT EXISTS country_code_backup AS
SELECT id, country, ST_Y(location::geometry) as lat, ST_X(location::geometry) as lon
FROM incidents;

-- Update country codes based on coordinates
UPDATE incidents
SET country = get_country_from_coordinates_sql(
    ST_Y(location::geometry),
    ST_X(location::geometry)
)
WHERE country != get_country_from_coordinates_sql(
    ST_Y(location::geometry),
    ST_X(location::geometry)
);

-- Report changes
DO $$
DECLARE
    updated_count INTEGER;
    country_breakdown TEXT;
BEGIN
    -- Count updated records
    SELECT COUNT(*) INTO updated_count
    FROM incidents i
    INNER JOIN country_code_backup b ON i.id = b.id
    WHERE i.country != b.country;

    -- Get country breakdown
    SELECT string_agg(country || ': ' || count::TEXT, ', ' ORDER BY country)
    INTO country_breakdown
    FROM (
        SELECT country, COUNT(*) as count
        FROM incidents
        GROUP BY country
    ) as counts;

    RAISE NOTICE 'Migration 019 Complete:';
    RAISE NOTICE '  Updated: % incidents', updated_count;
    RAISE NOTICE '  Current distribution: %', country_breakdown;
END $$;

-- Drop backup table (comment out if you want to keep for verification)
-- DROP TABLE country_code_backup;

-- Record migration execution
INSERT INTO public.schema_migrations (version, description, executed_by, git_commit_sha)
VALUES (
    '019',
    'Fix existing country codes based on coordinates',
    CURRENT_USER,
    '8227cf1'  -- Commit SHA where get_country_from_coordinates was added
)
ON CONFLICT (version) DO NOTHING;

-- Verification query (run after migration)
-- SELECT country, COUNT(*) as count,
--        array_agg(DISTINCT title ORDER BY title) as sample_titles
-- FROM incidents
-- GROUP BY country
-- ORDER BY count DESC;

COMMENT ON FUNCTION get_country_from_coordinates_sql IS
'Determines ISO 3166-1 alpha-2 country code from coordinates. Mirrors Python implementation in utils.py.';
