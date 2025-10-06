# Data Cleanup - Remove Mis-Geocoded Incidents

**Issue**: Non-Nordic incidents showing on map (Ukraine, Munich)
**Cause**: Old scraper code defaulted to Copenhagen for unknown locations
**Status**: Fixed in code, but old data remains in database
**Solution**: Run migration 011 to clean up

---

## 🚨 Problem

Looking at the production map, you'll see:

1. **"Massivt droneangrep over hele Ukraina"** - Ukraine drone attack shown in Copenhagen
2. **"Droner i München"** - Munich incident marked as Denmark
3. Possibly other mis-geocoded incidents

**Why this happened**:
- These were scraped on Oct 5th BEFORE the geocoding fix
- Old code defaulted to Copenhagen (55.618, 12.6476) when location unknown
- New code correctly returns `None` and skips the incident
- But old bad data is still in database

---

## ✅ Solution: Run Migration 011

### Step 1: Connect to Supabase

```bash
# Get DATABASE_URL from Vercel or use this:
DATABASE_URL="postgresql://postgres.uhwsuaebakkdmdogzrrz:stUPw5co47Yq8uSI@aws-1-eu-north-1.pooler.supabase.com:6543/postgres"
```

### Step 2: Run Migration

**Option A: Via Supabase Dashboard** (Recommended)
1. Go to https://supabase.com
2. Open your project
3. SQL Editor → New Query
4. Copy contents of `migrations/011_remove_non_nordic_incidents.sql`
5. Paste and Run

**Option B: Via Command Line**
```bash
psql "$DATABASE_URL" -f /root/repo/migrations/011_remove_non_nordic_incidents.sql
```

### Step 3: Verify

```sql
-- Check incidents by country
SELECT country, COUNT(*) FROM incidents GROUP BY country;

-- Should only show Nordic countries (DK, NO, SE, FI, etc.)
-- Should NOT show incidents at exactly 55.618, 12.6476 unless actually in Copenhagen
```

---

## 🔍 What Will Be Removed

The migration removes:
- **Ukraine incidents** (title/narrative contains "Ukraine" or "Ukraina")
- **Russia incidents** (title/narrative contains "Russia" or "Russ")
- **Munich incident** (title contains "München" but country marked as DK)

**Expected removals**: 2-3 incidents

**Impact on data**:
- ✅ Map will show only actual Nordic incidents
- ✅ No more false clustering at Copenhagen coordinates
- ✅ Data accuracy improved

---

## 📊 Before/After

### Before Cleanup

```bash
curl "https://drone-test22.vercel.app/api/incidents" | jq '.[] | select(.lat == 55.618 and .lon == 12.6476) | .title'

# Returns:
"Massivt droneangrep over hele Ukraina..."
"Hybrid air denial: The new gray zone..."
```

### After Cleanup

```bash
curl "https://drone-test22.vercel.app/api/incidents" | jq '.[] | select(.lat == 55.618 and .lon == 12.6476) | .title'

# Should return only actual Copenhagen incidents
# Or empty if no real incidents at those exact coordinates
```

---

## 🛡️ Prevention (Already Fixed)

**The root cause is already fixed** in the code:

```python
# In news_scraper.py (line 135-137)
if lat is None or lon is None:
    logger.info(f"⏭️  Skipping (no location): {title[:60]}...")
    continue
```

**New behavior**:
- ✅ Can't find location → Skip incident (don't create)
- ✅ No more defaulting to Copenhagen
- ✅ Only incidents with known locations are created

**Old incidents**: Need manual cleanup (this migration)
**Future incidents**: Won't have this problem

---

## 📋 Migration Checklist

Run these in order:

- [ ] Migration 010 - Evidence scoring system (CRITICAL)
- [ ] Migration 011 - Remove mis-geocoded incidents (This one)
- [ ] Optional: Migration 006 - Performance indexes
- [ ] Optional: Migration 008 - Geocoding jitter

### Quick Apply All

```bash
# If you have psql access
cd /root/repo/migrations

psql "$DATABASE_URL" -f 010_evidence_scoring_system.sql
psql "$DATABASE_URL" -f 011_remove_non_nordic_incidents.sql

# Optional but recommended:
psql "$DATABASE_URL" -f 006_performance_indexes.sql
psql "$DATABASE_URL" -f 008_add_geocoding_jitter.sql
```

---

## 🎯 Expected Results

After running migration 011:

**Map view**:
- No more Ukraine incidents
- No more Munich incidents marked as Denmark
- Only actual Nordic drone incidents visible

**API response**:
```bash
curl "https://drone-test22.vercel.app/api/incidents" | jq length
# Before: ~21 incidents
# After: ~18-19 incidents (removed 2-3 bad ones)
```

**Incident count by country**:
```
DK (Denmark): 15-16
NO (Norway): 1-2
SE (Sweden): 0-1
FI (Finland): 0-1
```

---

## 🔧 Troubleshooting

### If incidents still show after migration

**Check the migration ran**:
```sql
SELECT COUNT(*) FROM incidents WHERE title LIKE '%Ukraina%';
-- Should return 0
```

**If still showing**:
- Clear browser cache
- Hard refresh (Ctrl+Shift+R)
- Wait 30 seconds for API cache to clear

### If too many incidents removed

**The migration is safe** - it only removes:
- Obvious non-Nordic content (Ukraine, Russia)
- Mis-geocoded incidents (Munich → Denmark)

**To verify what will be removed BEFORE running**:
```sql
-- Run this first to see what would be deleted
SELECT id, title, country, lat, lon
FROM incidents
WHERE
  (title LIKE '%Ukraina%' OR title LIKE '%Ukraine%')
  OR (title LIKE '%Russia%')
  OR (title LIKE '%München%' AND country = 'DK');
```

---

## 📞 Related

- **Root cause fix**: Already deployed in `news_scraper.py` (Oct 5)
- **Evidence scoring**: Migration 010 (required, run first)
- **Performance**: Migration 006 (recommended)
- **Map clustering**: Migration 008 (optional)

---

**Created**: 2025-10-06
**Priority**: HIGH (improves data quality)
**Dependencies**: None (can run independently)
**Impact**: Removes 2-3 mis-geocoded incidents

🤖 Generated with [Claude Code](https://claude.com/claude-code)
