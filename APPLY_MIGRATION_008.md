# How to Apply Migration 008 - Geocoding Jitter

## Problem

**13 incidents share exact coordinates** causing confusing cluster display:
- **8 incidents** at `55.6761, 12.5683` (Copenhagen city center)
- **5 incidents** at `55.618, 12.6476` (Copenhagen Airport area)

These are **separate incidents from different dates**, but they're geocoded to the same generic location, so Leaflet's spiderfying cannot separate them visually.

## Solution

Migration 008 adds small offsets (+/- 0.002° ≈ 200m) to visually separate overlapping incidents while maintaining geographic accuracy.

## How to Apply

### Option 1: Supabase SQL Editor (Recommended)

1. **Go to Supabase Dashboard**
   - Navigate to https://supabase.com/dashboard
   - Select your DroneWatch project

2. **Open SQL Editor**
   - Click "SQL Editor" in the left sidebar
   - Click "New query"

3. **Copy & Paste Migration**
   ```bash
   cat migrations/008_add_geocoding_jitter.sql
   ```
   - Copy the entire contents
   - Paste into SQL Editor

4. **Run Migration**
   - Click "Run" button
   - Verify output shows:
     - `total_overlapping_incidents`: 13
     - `unique_locations`: 2
     - Rows updated successfully

5. **Verify Results**
   - Check that `remaining_overlaps` = 0
   - All 27 incidents now have unique coordinates

### Option 2: Command Line (If you have DATABASE_URL)

```bash
# Set DATABASE_URL environment variable
export DATABASE_URL="postgresql://postgres:[password]@db.[project].supabase.co:6543/postgres"

# Apply migration
psql $DATABASE_URL -f migrations/008_add_geocoding_jitter.sql
```

## Expected Results

### Before Migration
- 27 total incidents
- 14 unique locations
- 13 incidents overlapping (shown as large clusters on map)

### After Migration
- 27 total incidents
- 27 unique locations
- 0 overlapping incidents
- Cluster "8" will spiderfy into 8 individual markers
- Cluster "5" will spiderfy into 5 individual markers

## Verification

After applying the migration:

1. **Check the map** at https://www.dronemap.cc
2. **Click the large cluster** (previously showing "14" or "8")
3. **Markers should spiderfy** in a circle pattern instead of re-clustering
4. **Each incident** should be individually clickable

## Technical Details

**Jitter Pattern**:
- First incident at each location stays at original coordinates
- Additional incidents are offset in a circle pattern
- Radius: 0.002° (approximately 200 meters)
- Formula: Uses polar coordinates (angle based on incident position)

**Safety**:
- ✅ No data loss
- ✅ Original coordinates preserved for primary incident
- ✅ Offsets are small enough to maintain geographic accuracy
- ✅ Transaction-wrapped (rolls back on error)

## Notes

- **One incident, multiple sources = one database row** (this migration does NOT affect that)
- This migration only separates **legitimate different incidents** that happen to share coordinates
- After migration, map clustering will work as expected
- Future improvements should enhance geocoding to prevent this issue

---

**Created**: October 1, 2025
**Status**: Ready to apply
**Priority**: Medium (improves UX, not critical)
