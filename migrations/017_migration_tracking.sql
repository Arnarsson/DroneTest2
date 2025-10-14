-- Migration 017: Database Migration Tracking System
-- Date: 2025-10-14
-- Purpose: Track executed migrations and prevent duplicate/missing migrations
-- Addresses: No way to determine which migrations have been executed on production

BEGIN;

-- =====================================================
-- 1. Create schema_migrations tracking table
-- =====================================================

CREATE TABLE IF NOT EXISTS public.schema_migrations (
  version TEXT PRIMARY KEY,
  description TEXT NOT NULL,
  executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  executed_by TEXT DEFAULT CURRENT_USER,
  execution_time_ms INTEGER,
  git_commit_sha TEXT,
  notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_schema_migrations_executed_at
  ON public.schema_migrations(executed_at DESC);

COMMENT ON TABLE public.schema_migrations IS
'Tracks all executed database migrations to prevent duplicates and missing migrations';

COMMENT ON COLUMN public.schema_migrations.version IS
'Migration number (e.g., "001", "016") - unique identifier';

COMMENT ON COLUMN public.schema_migrations.description IS
'Human-readable description of what the migration does';

COMMENT ON COLUMN public.schema_migrations.git_commit_sha IS
'Git commit SHA when migration was first added to repository';

-- =====================================================
-- 2. Backfill existing migrations from git history
-- =====================================================

-- Migrations 001-011: Early system setup (September-October 2025)
INSERT INTO public.schema_migrations (version, description, executed_at, executed_by, git_commit_sha, notes) VALUES
  ('001', 'Prevent duplicate incidents via unique constraint', '2025-09-30 08:34:55+00', 'system:backfill', 'd3e47a8178dee11b7c7721562cc6e07408f56f68', 'Fixed version - PostGIS STABLE function workaround'),
  ('002', 'Scraper processed incidents cache', '2025-09-30 09:36:08+00', 'system:backfill', '499f15c89fc4dbd1b494f098b50c7a5930396cba', 'Replaces file-based cache with database table'),
  ('003', 'Verification workflow for historical incidents', '2025-09-30 09:50:08+00', 'system:backfill', '29edb337bf00cb0dd85ec524b16a8c9d5b271b9e', 'Manual review queue and audit trail'),
  ('004', 'Auto-verify existing incidents', '2025-09-30 12:01:52+00', 'system:backfill', '4b7c1e2817abc42c84d8d3733a455e00e9ebd772', 'Set existing incidents to auto_verified'),
  ('005', 'Set pending verification status', '2025-09-30 12:42:23+00', 'system:backfill', '4b7c1e2817abc42c84d8d3733a455e00e9ebd772', 'Initialize verification_status for existing data'),
  ('006', 'Performance indexes for API optimization', '2025-09-30 23:59:44+02', 'system:backfill', '7821a67c5e71ef64123b05736efefb415ae44e1b', 'Reduce query time from 11.4s to <3s'),
  ('007', 'Merge duplicate incidents', '2025-10-01 12:07:15+02', 'system:backfill', '694dabb3e16c89f085227aa5397c01124ac06e93', 'One event = one incident (multi-source consolidation)'),
  ('008', 'Add geocoding jitter for overlapping incidents', '2025-10-01 16:29:06+02', 'system:backfill', '8e4d06a5b69aeaad6cf515094ef17cdc6a1d7ef8', 'Prevent exact coordinate overlap on map'),
  ('009', 'Clean up test incidents', '2025-10-01 16:29:06+02', 'system:backfill', '083da7c11339a6b949671b63e0ab1992a7413add', 'Remove test data and prevent future test incidents'),
  ('010', 'Evidence scoring system enforcement', '2025-10-05 12:42:59+02', 'system:backfill', 'eb7d533bcec100d8c3f1d8090496c402aa37605b', '4-tier evidence scoring (1-4) based on source reliability'),
  ('011', 'Remove non-Nordic incidents', '2025-10-05 20:27:45+00', 'system:backfill', 'eb7d533bcec100d8c3f1d8090496c402aa37605b', 'Clean up incidents outside Nordic region')
ON CONFLICT (version) DO NOTHING;

-- Note: Migration 012 is missing (gap in numbering)

-- Migrations 013-016: Geographic filtering and duplicate prevention (October 2025)
INSERT INTO public.schema_migrations (version, description, executed_at, executed_by, git_commit_sha, notes) VALUES
  ('013', 'Remove foreign incidents from database', '2025-10-06 09:11:19+00', 'system:backfill', 'b3e44faa001bcd4c8543c754f8dc76e598917aa6', 'Clean incidents geocoded to wrong coordinates'),
  ('014', 'Geographic validation trigger (database-level)', '2025-10-06 16:54:45+02', 'system:backfill', '908103a18f83502b7118dd8bac2bb327c6da618a', 'Multi-layer defense v2.1.0 - validates title AND narrative'),
  ('015', 'Expand to European coverage (35-71°N, -10-31°E)', '2025-10-09 10:22:20+02', 'system:backfill', '93fca4792a7dede2414f7abc889d924ec5054e9e', 'DroneWatch v2.3.0 - All of Europe support'),
  ('016', 'Remove duplicate incidents and add source constraints', '2025-10-09 19:44:28+02', 'system:backfill', 'c768305d708e133f0bbf9f0b2286a1f9d017b172', 'Database-level duplicate prevention via content_hash')
ON CONFLICT (version) DO NOTHING;

-- =====================================================
-- 3. Document conflicting/duplicate migration files
-- =====================================================

-- Note: The following migration files exist but are NOT tracked here because they conflict:
--
-- DUPLICATE 014 FILES (2 files):
--   - 014_geographic_validation_trigger.sql (EXECUTED - git: 908103a1)
--   - 014_geographic_validation_trigger 2.sql (DUPLICATE - NOT EXECUTED)
--
-- DUPLICATE 015 FILES (3 files):
--   - 015_expand_to_european_coverage.sql (EXECUTED - git: 93fca479)
--   - 015_optimize_sources_query.sql (CONFLICTING - git: de394fae)
--   - 015_version_tracking.sql (CONFLICTING - git: 8bf7494)
--
-- RECOMMENDATION: Renumber conflicting migrations to 017, 018, etc. if they need to be executed

-- =====================================================
-- 4. Add helper function to check before migration
-- =====================================================

CREATE OR REPLACE FUNCTION public.check_migration_executed(p_version TEXT)
RETURNS TABLE (
  is_executed BOOLEAN,
  executed_at TIMESTAMPTZ,
  description TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT
    EXISTS(SELECT 1 FROM public.schema_migrations WHERE version = p_version) AS is_executed,
    sm.executed_at,
    sm.description
  FROM public.schema_migrations sm
  WHERE sm.version = p_version;
END;
$$;

COMMENT ON FUNCTION public.check_migration_executed IS
'Check if a migration has been executed before running it';

-- =====================================================
-- 5. Add helper function to record new migration
-- =====================================================

CREATE OR REPLACE FUNCTION public.record_migration(
  p_version TEXT,
  p_description TEXT,
  p_git_commit_sha TEXT DEFAULT NULL,
  p_execution_time_ms INTEGER DEFAULT NULL
) RETURNS VOID
LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO public.schema_migrations (
    version,
    description,
    executed_at,
    executed_by,
    git_commit_sha,
    execution_time_ms
  ) VALUES (
    p_version,
    p_description,
    NOW(),
    CURRENT_USER,
    p_git_commit_sha,
    p_execution_time_ms
  )
  ON CONFLICT (version) DO UPDATE SET
    executed_at = NOW(),
    notes = COALESCE(public.schema_migrations.notes, '') ||
            E'\nRe-executed at ' || NOW()::TEXT;

  RAISE NOTICE 'Migration % recorded successfully', p_version;
END;
$$;

COMMENT ON FUNCTION public.record_migration IS
'Record a migration execution (call this at the end of each migration)';

-- =====================================================
-- 6. Enable RLS (read-only for public/anon)
-- =====================================================

ALTER TABLE public.schema_migrations ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to read migration history
CREATE POLICY "public_read_migrations" ON public.schema_migrations
FOR SELECT USING (true);

-- Only admins can insert/update (handled by service role)
-- No policy needed - defaults to deny

-- =====================================================
-- 7. Add this migration to tracking
-- =====================================================

INSERT INTO public.schema_migrations (
  version,
  description,
  executed_at,
  executed_by,
  git_commit_sha,
  notes
) VALUES (
  '017',
  'Database migration tracking system',
  NOW(),
  CURRENT_USER,
  NULL, -- Will be added when committed to git
  'Initial migration tracking setup - backfilled 001-016'
);

COMMIT;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- View all executed migrations
SELECT
  version,
  description,
  executed_at,
  executed_by,
  git_commit_sha
FROM public.schema_migrations
ORDER BY version;

-- Check total count
SELECT COUNT(*) AS total_migrations FROM public.schema_migrations;

-- Check for gaps in numbering
WITH numbered AS (
  SELECT
    version::INTEGER AS num,
    description
  FROM public.schema_migrations
  WHERE version ~ '^\d+$'  -- Only numeric versions
),
expected AS (
  SELECT generate_series(1, (SELECT MAX(num) FROM numbered)) AS num
)
SELECT
  e.num AS missing_migration_number,
  'GAP IN NUMBERING' AS status
FROM expected e
LEFT JOIN numbered n ON e.num = n.num
WHERE n.num IS NULL
ORDER BY e.num;

-- Usage examples:
/*
-- Before running a new migration (e.g., 018):
SELECT * FROM public.check_migration_executed('018');

-- After running a new migration:
SELECT public.record_migration(
  '018',
  'Add new feature X',
  'git-commit-sha-here',
  1250  -- execution time in milliseconds
);

-- View migration history:
SELECT * FROM public.schema_migrations ORDER BY executed_at DESC LIMIT 10;

-- Check if specific migration executed:
SELECT version, executed_at FROM public.schema_migrations WHERE version = '016';
*/
