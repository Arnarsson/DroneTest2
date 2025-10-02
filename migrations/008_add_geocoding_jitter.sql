        -- Add Geocoding Jitter for Overlapping Incidents
        -- This migration adds small offsets to incidents that share exact coordinates
        -- to improve map visualization while maintaining data integrity

        BEGIN;

        -- Step 1: Identify incidents sharing exact coordinates
        CREATE TEMP TABLE overlapping_incidents AS
        WITH incident_counts AS (
            SELECT
                i.id,
                i.title,
                i.occurred_at,
                ST_X(i.location::geometry) as lon,
                ST_Y(i.location::geometry) as lat,
                ROW_NUMBER() OVER (
                    PARTITION BY ST_X(i.location::geometry), ST_Y(i.location::geometry)
                    ORDER BY i.occurred_at DESC
                ) as row_num,
                COUNT(*) OVER (
                    PARTITION BY ST_X(i.location::geometry), ST_Y(i.location::geometry)
                ) as location_count
            FROM public.incidents i
        )
        SELECT id, title, occurred_at, lon, lat, row_num
        FROM incident_counts
        WHERE location_count > 1;

        -- Step 2: Show what will be modified
        SELECT
            COUNT(*) as total_overlapping_incidents,
            COUNT(DISTINCT (lon, lat)) as unique_locations
        FROM overlapping_incidents;

        -- Step 3: Apply jitter to overlapping incidents
        -- Add small random offset (+/- 0.002 degrees ≈ 200m) to distinguish them visually
        -- Keep first incident at original location, offset subsequent ones in a circle pattern
        UPDATE public.incidents i
        SET location = ST_SetSRID(
            ST_MakePoint(
                -- Longitude: original + offset based on position in circle
                ST_X(i.location::geometry) + (
                    CASE
                        WHEN oi.row_num = 1 THEN 0  -- Keep first incident at original location
                        ELSE 0.002 * COS(2 * PI() * (oi.row_num - 2) / (SELECT MAX(row_num) FROM overlapping_incidents WHERE lon = oi.lon AND lat = oi.lat))
                    END
                ),
                -- Latitude: original + offset based on position in circle
                ST_Y(i.location::geometry) + (
                    CASE
                        WHEN oi.row_num = 1 THEN 0  -- Keep first incident at original location
                        ELSE 0.002 * SIN(2 * PI() * (oi.row_num - 2) / (SELECT MAX(row_num) FROM overlapping_incidents WHERE lon = oi.lon AND lat = oi.lat))
                    END
                )
            ),
            4326
        )::geography
        FROM overlapping_incidents oi
        WHERE i.id = oi.id
        AND oi.row_num > 1;  -- Only offset incidents after the first one

        -- Step 4: Verify results
        SELECT
            COUNT(*) as total_incidents,
            COUNT(DISTINCT (ST_X(location::geometry), ST_Y(location::geometry))) as unique_locations,
            COUNT(DISTINCT (ST_X(location::geometry), ST_Y(location::geometry))) - COUNT(*) as remaining_overlaps
        FROM public.incidents;

        -- Step 5: Add comment for documentation
        COMMENT ON COLUMN public.incidents.location IS
        'Geographic location (PostGIS geography). Small jitter (+/- 0.002° ≈ 200m) applied to incidents sharing exact coordinates for better map visualization.';

        COMMIT;

        -- Expected result:
        -- Before: 27 incidents, 14 unique locations (13 incidents overlapping)
        -- After: 27 incidents, 27 unique locations (0 overlapping)
