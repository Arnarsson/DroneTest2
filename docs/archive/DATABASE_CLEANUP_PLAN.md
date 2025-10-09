# Supabase Database Cleanup Plan

**Date**: October 7, 2025
**Database**: Supabase Cloud (uhwsuaebakkdmdogzrrz)

---

## Current State Analysis

### Statistics
- **Incidents**: 13 total
- **Incident Sources**: 9 relationships
- **Sources**: 27 sources defined
- **Countries**: 5 (DK, NO, SE, NL, PL)

### Issues Identified

#### 1. Orphaned Incidents (10 incidents with 0 sources)
```
❌ Amsterdam Schiphol - Drone Near Miss with Transavia Jet
❌ Oslo Airport - Coordinated with Copenhagen
❌ Billund Airport - Early Morning Drone Closure
❌ Stockholm Arlanda - Drone Disruption
❌ Lublin Airport - Airspace Protection Closure
❌ Frigate, Radars, Troops Rushed To Copenhagen To Defend Against Mystery Drones
❌ Karup Air Base - Denmark's Largest Military Base
❌ Kastrup Airbase - Brief Airspace Closure
❌ Sønderborg Airport - Multiple Airport Coordination
❌ Skrydstrup Air Base - Military Installation Targeted
```

**Impact**: Violates data quality principle "All incidents have at least one source"

#### 2. "Merged Duplicate" Sources
- Copenhagen Airport incident has 2x "Merged Duplicate" sources
- Esbjerg Airport incident has 3x "Merged Duplicate" sources
- Aalborg Airport incident has 1x "Merged Duplicate" source

**Impact**: These are placeholder sources from migration, should be replaced with real sources

#### 3. Orphaned Sources
- "Merged Duplicate" (2 entries in sources table)
- "Merged: ..." sources (2 entries) - internal merge tracking

**Impact**: Not linked to active data collection, taking up space

---

## Cleanup Actions

### Phase 1: Remove Incidents Without Sources (Recommended)

**Rationale**: If we don't have sources, we can't verify the incident authenticity.

```sql
-- Delete incidents with no sources
DELETE FROM incidents
WHERE id IN (
    SELECT i.id
    FROM incidents i
    LEFT JOIN incident_sources iss ON i.id = iss.incident_id
    WHERE iss.id IS NULL
);
```

**Expected Result**: Remove 10 incidents, leaving 3 with sources

### Phase 2: Clean Up "Merged Duplicate" Sources

**Option A - Replace with Real Sources** (Preferred):
1. Research each incident's actual sources from web archives
2. Add real source records to `sources` table
3. Update `incident_sources` to point to real sources
4. Delete "Merged Duplicate" source records

**Option B - Delete** (Quick but loses data):
```sql
-- Remove incident_sources with "Merged Duplicate"
DELETE FROM incident_sources
WHERE source_id IN (
    SELECT id FROM sources WHERE name = 'Merged Duplicate'
);

-- Remove "Merged Duplicate" source records
DELETE FROM sources WHERE name = 'Merged Duplicate';
```

### Phase 3: Remove Internal Merge Tracking Sources

```sql
-- These are not real sources, just merge metadata
DELETE FROM incident_sources
WHERE source_id IN (
    SELECT id FROM sources
    WHERE homepage_url LIKE 'internal://merged/%'
);

DELETE FROM sources WHERE homepage_url LIKE 'internal://merged/%';
```

### Phase 4: Vacuum and Analyze

```sql
-- Reclaim space and update statistics
VACUUM ANALYZE incidents;
VACUUM ANALYZE incident_sources;
VACUUM ANALYZE sources;
```

---

## Conservative Cleanup (Recommended)

Keep data quality high without losing potentially valuable incidents:

```sql
-- Step 1: Delete incidents with no sources (can't verify)
DELETE FROM incidents
WHERE id IN (
    SELECT i.id
    FROM incidents i
    LEFT JOIN incident_sources iss ON i.id = iss.incident_id
    WHERE iss.id IS NULL
);

-- Step 2: Remove internal merge tracking (not real sources)
DELETE FROM incident_sources
WHERE source_id IN (
    SELECT id FROM sources
    WHERE homepage_url LIKE 'internal://merged/%'
);

DELETE FROM sources
WHERE homepage_url LIKE 'internal://merged/%';

-- Step 3: Update "Merged Duplicate" to show it needs research
UPDATE sources
SET
    name = 'Source Needs Research',
    trust_weight = 1
WHERE name = 'Merged Duplicate';

-- Step 4: Vacuum
VACUUM ANALYZE incidents;
VACUUM ANALYZE incident_sources;
VACUUM ANALYZE sources;
```

**Result**:
- Clean 3 incidents with valid sources
- Mark old sources as needing research
- Remove fake internal sources

---

## Aggressive Cleanup (Maximum Clean)

Remove everything that's not 100% verified:

```sql
-- Delete all incidents with "Merged Duplicate" or missing sources
DELETE FROM incidents
WHERE id IN (
    SELECT DISTINCT i.id
    FROM incidents i
    LEFT JOIN incident_sources iss ON i.id = iss.incident_id
    LEFT JOIN sources s ON iss.source_id = s.id
    WHERE iss.id IS NULL
       OR s.name = 'Merged Duplicate'
       OR s.homepage_url LIKE 'internal://%'
);

-- Clean up orphaned sources
DELETE FROM incident_sources
WHERE source_id NOT IN (SELECT id FROM sources);

DELETE FROM sources
WHERE name IN ('Merged Duplicate', 'Source Needs Research')
   OR homepage_url LIKE 'internal://%';

-- Vacuum
VACUUM ANALYZE incidents;
VACUUM ANALYZE incident_sources;
VACUUM ANALYZE sources;
```

**Result**:
- Only 100% verified incidents remain
- Clean slate for new police scraper data

---

## Expected Final State

### After Conservative Cleanup
- **Incidents**: 3 (only those with sources)
- **Incident Sources**: 6-7 (after removing internal merge tracking)
- **Sources**: 25 (all Danish police + media sources)

### After Aggressive Cleanup
- **Incidents**: 0 (clean slate)
- **Incident Sources**: 0
- **Sources**: 24 (only real sources, no placeholders)

---

## Recommendation

**Conservative Cleanup** is recommended because:
1. Preserves Copenhagen Airport incident (has real sources)
2. Marks old sources as needing research (transparent)
3. Removes fake internal sources (data quality)
4. Ready for new police scraper data

**Next Steps After Cleanup**:
1. Run police scraper to ingest Copenhagen incident with proper sources
2. Add more scrapers for news sources
3. Monitor data quality with tests
4. Build trust in the system with verified sources

---

## Rollback Plan

If cleanup causes issues:

```sql
-- Restore from Supabase backup
-- Go to Supabase Dashboard → Database → Backups
-- Select backup before cleanup timestamp
-- Click "Restore"
```

**Backup Retention**: 7 days on free tier, 30 days on paid

---

## Execution Checklist

- [ ] Backup database (Supabase dashboard)
- [ ] Run conservative OR aggressive cleanup SQL
- [ ] Verify incident count matches expected
- [ ] Check API still works (`/api/incidents`)
- [ ] Run police scraper to re-ingest Copenhagen incident
- [ ] Verify frontend displays properly
- [ ] Update documentation

---

**Status**: Ready to execute
**Risk Level**: Low (small database, easy rollback)
**Estimated Time**: 5 minutes
