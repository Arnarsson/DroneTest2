# Duplicate Incident Fix

## Problem
Users are seeing duplicate incidents on the map/list view. This happens when:
1. Multiple sources report the same incident
2. Same incident scraped multiple times
3. Incidents at same location but different times get merged incorrectly

## Root Causes

### 1. Missing Time Window Check
**Issue**: Deduplication only checked location + asset_type, not time
**Impact**: Old incidents (weeks/months apart) could be merged incorrectly
**Fix**: Added 7-day time window check

### 2. Existing Duplicates in Database
**Issue**: Some duplicates already exist from before deduplication was improved
**Impact**: Users see multiple markers for same incident
**Fix**: Migration script to merge existing duplicates

### 3. Source URL Deduplication
**Issue**: Same source URL could be added multiple times
**Impact**: Duplicate sources for same incident
**Fix**: Unique constraint on `source_url` in `incident_sources` table

## Fixes Implemented

### 1. Improved Deduplication Logic (`frontend/api/ingest.py`)

**Before**:
```python
# Only checked location + asset_type
existing_incident = await conn.fetchrow("""
    SELECT id FROM incidents
    WHERE ST_DWithin(location, point, radius)
    AND asset_type = $4
""")
```

**After**:
```python
# Now checks location + asset_type + 7-day time window
existing_incident = await conn.fetchrow("""
    SELECT id FROM incidents
    WHERE ST_DWithin(location, point, radius)
    AND asset_type = $4
    AND occurred_at >= $5 - INTERVAL '7 days'
    AND occurred_at <= $5 + INTERVAL '7 days'
""")
```

**Benefits**:
- Prevents merging incidents that are weeks/months apart
- Still merges incidents reported by different sources on same day
- More accurate deduplication

### 2. Migration to Merge Existing Duplicates (`migrations/021_merge_existing_duplicates.sql`)

**What it does**:
1. Finds duplicate groups (same location + same day + same asset_type)
2. Keeps the incident with highest evidence_score
3. Transfers all sources from duplicates to primary incident
4. Updates time ranges to encompass all merged incidents
5. Deletes duplicate incidents

**How to run**:
```sql
-- In Supabase SQL Editor
\i migrations/021_merge_existing_duplicates.sql
```

### 3. Duplicate Detection Tool (`frontend/api/admin/find_duplicates.py`)

**Purpose**: Identify duplicates before they cause issues

**Usage**:
```bash
# Get Bearer token from INGEST_TOKEN env var
curl -H "Authorization: Bearer $INGEST_TOKEN" \
  https://www.dronemap.cc/api/admin/find_duplicates
```

**Returns**:
- Duplicates by location + date
- Duplicates by source URL (should never happen)
- Duplicates by title + location
- Summary statistics

## Deduplication Strategy

### Multi-Layer Protection

1. **Source URL Check** (First)
   - Checks if source URL already exists globally
   - Prevents same article from being added twice
   - Fastest check

2. **Location + Time Check** (Second)
   - Checks for incidents within radius (based on asset_type)
   - Within 7-day time window
   - Same asset_type required
   - If found: adds as source to existing incident

3. **Database Constraints** (Last Resort)
   - Unique constraint on `(incident_id, source_url)`
   - Prevents duplicate sources per incident

### Radius by Asset Type

| Asset Type | Radius | Reason |
|------------|--------|--------|
| Airport | 3km | Large facilities |
| Military | 3km | Large bases |
| Harbor | 1.5km | Medium facilities |
| Power Plant | 1km | Medium facilities |
| Bridge | 500m | Specific locations |
| Other | 500m | Default |

## Testing

### Verify Deduplication Works

1. **Test same source URL**:
```bash
# First request - should create incident
curl -X POST https://www.dronemap.cc/api/ingest \
  -H "Authorization: Bearer $INGEST_TOKEN" \
  -d '{"title": "Test", "source_url": "https://example.com/1", ...}'

# Second request with same source_url - should add as source
curl -X POST https://www.dronemap.cc/api/ingest \
  -H "Authorization: Bearer $INGEST_TOKEN" \
  -d '{"title": "Test", "source_url": "https://example.com/1", ...}'
```

2. **Test same location + time**:
```bash
# Two requests with same location, same day, different sources
# Should merge into one incident with 2 sources
```

3. **Test different times**:
```bash
# Two requests with same location but 10 days apart
# Should create separate incidents (not merged)
```

## Monitoring

### Check for Duplicates

```sql
-- Find duplicates by location + date
SELECT 
    DATE(occurred_at) as event_date,
    ROUND(ST_Y(location::geometry)::numeric, 3) as lat,
    ROUND(ST_X(location::geometry)::numeric, 3) as lon,
    COUNT(*) as duplicate_count
FROM public.incidents
WHERE location IS NOT NULL
GROUP BY 
    DATE(occurred_at),
    ROUND(ST_Y(location::geometry)::numeric, 3),
    ROUND(ST_X(location::geometry)::numeric, 3)
HAVING COUNT(*) > 1;

-- Find duplicate source URLs (should return 0)
SELECT source_url, COUNT(DISTINCT incident_id) as incident_count
FROM public.incident_sources
GROUP BY source_url
HAVING COUNT(DISTINCT incident_id) > 1;
```

## Rollback Plan

If deduplication causes issues:

1. **Restore from backup** (if migration was run)
2. **Revert code changes**:
   ```bash
   git revert <commit-hash>
   ```
3. **Remove time window check** (if too strict):
   - Edit `frontend/api/ingest.py`
   - Remove `AND occurred_at >= ...` lines

## Future Improvements

1. **Content-based deduplication**: Use NLP to detect similar incidents
2. **Fuzzy location matching**: Handle slight coordinate differences
3. **Title similarity**: Merge incidents with similar titles
4. **Automatic cleanup**: Scheduled job to find and merge duplicates

## Related Files

- `frontend/api/ingest.py` - Deduplication logic
- `migrations/021_merge_existing_duplicates.sql` - Cleanup script
- `frontend/api/admin/find_duplicates.py` - Detection tool
- `migrations/016_remove_duplicates.sql` - Previous cleanup

---

**Last Updated**: 2025-01-XX  
**Status**: ✅ Fixed - Improved deduplication with time window check

