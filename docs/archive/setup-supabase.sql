-- DroneWatch Supabase Setup Script
-- Run this in your Supabase SQL Editor

-- 1. Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- 2. Run the main schema
-- Copy contents of sql/supabase_schema.sql here or run separately

-- 3. Quick verification
SELECT
    postgis_version(),
    current_database(),
    current_user;

-- 4. Test the upsert function with sample data
SELECT public.upsert_incident(
    'Test: Copenhagen Airport drone sighting',
    'Initial test incident for DroneWatch system',
    NOW() - INTERVAL '1 hour',
    55.6180, 12.6476,
    'airport', 'active', 3, 'DK'
) as test_incident_id;

-- 5. Verify RLS is enabled
SELECT
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('incidents', 'sources', 'assets', 'incident_sources');

-- You should see rowsecurity = true for all tables