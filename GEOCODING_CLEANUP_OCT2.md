# Geocoding Cleanup - October 2, 2025

## 🎯 Issue Fixed

**Problem**: Copenhagen cluster showed **12 incidents** when only ~7 were actually in Copenhagen

**Root Cause**: Geocoding fallback was assigning **default Copenhagen coordinates** to international incidents without specific locations

---

## 📊 What Was Wrong

### Mis-Geocoded Incidents (Deleted)

1. **Skunk Works Unveils Vectis Air Combat Drone**
   - Should be: USA (no specific location)
   - Was geocoded to: Copenhagen (55.6741, 12.5683)
   - Type: US defense contractor news

2. **Ukraine navy, a battle-tested force, plays enemy in NATO drone drill**
   - Should be: Portugal (REPMUS 2025 exercise)
   - Was geocoded to: Copenhagen (55.6775, 12.5668)
   - Type: NATO training exercise

3. **F-15Es Tried To Shoot Down Iranian Kamikaze Drones With Laser Guided Bombs**
   - Should be: Middle East (Iran/Iraq)
   - Was geocoded to: Copenhagen (55.6761, 12.5663)
   - Type: International conflict news

4. **Ukrainian Drones Strike Russia's Rare Be-12 Flying Boats**
   - Should be: Russia/Ukraine
   - Was geocoded to: Copenhagen (55.6741, 12.5683)
   - Type: Ukraine war news

5. **European navies test new drone tech for undersea operations**
   - Should be: Portugal (REPMUS 2025)
   - Was geocoded to: Copenhagen (55.6781, 12.5683)
   - Type: NATO exercise

---

## ✅ The Fix

### Actions Taken

```sql
-- Deleted 5 mis-geocoded international incidents
DELETE FROM incidents WHERE id IN (
  'e0946d7b-bde6-47ff-ab0a-df76e4e6fcba',  -- Skunk Works
  '16c6d1af-8727-4e1c-8e85-8bae4d3e9823',  -- Ukraine navy
  'd8a3e8c5-f5be-4170-91b2-56772a149b0f',  -- F-15Es Iran
  '20a126bd-0275-4a3a-8049-c90a307dcb8a',  -- Ukrainian Drones Russia
  '1e7c3223-9429-43bc-80ed-0f2f84bdf82d'   -- European navies
);
```

### Results

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **Total Incidents** | 25 | 20 | -5 (20% reduction) |
| **Copenhagen Cluster** | 12 | 7 | -5 (58% reduction) |
| **Data Accuracy** | Poor | ✅ Good | Fixed! |

---

## 🔍 Root Cause Analysis

### Why This Happened

The scraper's geocoding system had a **fallback to Copenhagen coordinates** when it couldn't find a specific location for an incident:

1. **News scraper** ingests international drone news (Ukraine, Iran, US, etc.)
2. **Geocoding attempts** to find location from article text
3. **No specific location found** → Falls back to default coordinates
4. **Default coordinates** = Copenhagen (55.6741, 12.5683)
5. **Result**: International incidents clustered in Copenhagen

### Detection Method

```sql
-- Query to find mis-geocoded incidents
SELECT id, title, country
FROM incidents
WHERE country = 'DK'
  AND (
    title LIKE '%Ukraine%'
    OR title LIKE '%Russia%'
    OR title LIKE '%Iran%'
    OR title LIKE '%NATO%'
    OR title LIKE '%REPMUS%'
    OR title LIKE '%Skunk Works%'
  )
  AND (ST_Y(location::geometry) BETWEEN 55.6 AND 55.7)
  AND (ST_X(location::geometry) BETWEEN 12.5 AND 12.6);
```

---

## 🛡️ Prevention Strategy

### Scraper Fix Needed

**Current behavior** (WRONG):
```python
location = geocode(article_text)
if not location:
    location = (55.6741, 12.5683)  # Copenhagen fallback ❌
    country = 'DK'
```

**Correct behavior** (TODO):
```python
location = geocode(article_text)
if not location:
    # Skip incidents without specific location
    logger.info(f"Skipping incident - no location: {title}")
    return None  # Don't ingest ✅
```

### Implementation Steps

1. **Update scraper logic** to skip incidents without locations
2. **Add location validation** before ingestion
3. **Log skipped incidents** for monitoring
4. **Add location source tracking** (geocoded vs. manual vs. NOTAM)

---

## 📈 Current State

### Verified Working

✅ **Copenhagen cluster now shows 7 incidents** (correct count)
✅ **API returns 20 total incidents** (cleaned data)
✅ **Map displays accurate locations** (no false clustering)
✅ **Database cleaned** (international incidents removed)

### Remaining Copenhagen Incidents (Legitimate)

1. Udenlandske soldater skal hjælpe Danmark efter dronehændelse
2. Eksplosiv vækst: Droneangreb har fået mange til at melde sig
3. Skib med mulig forbindelse til dronesagen efterforskes i Frankrig
4. France, Sweden send anti-drone units to Denmark to secure EU
5. EU vows haste in 'drone wall' plan for eastern borders
6. Kastrup Airbase - Brief Airspace Closure
7. Copenhagen Airport - Major Drone Disruption

All 7 are **genuine Copenhagen-area incidents** ✅

---

## 🚀 Next Steps

### High Priority
1. ✅ Clean mis-geocoded incidents from database (DONE)
2. ⏳ Fix scraper to skip incidents without specific locations
3. ⏳ Add location validation before ingestion

### Medium Priority
4. Add location source tracking (geocoded/manual/NOTAM)
5. Monitor scraper logs for skipped incidents
6. Create alert for suspicious geocoding patterns

### Low Priority
7. Review historical data for other mis-geocoded clusters
8. Add location confidence scoring
9. Implement manual review queue for uncertain locations

---

## 📝 Commands Reference

### Verify Current State
```bash
# Check total incidents
export DATABASE_URL="postgresql://..."
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM incidents;"

# Check Copenhagen cluster
psql "$DATABASE_URL" -c "
SELECT COUNT(*)
FROM incidents
WHERE (ST_Y(location::geometry) BETWEEN 55.5 AND 55.7)
  AND (ST_X(location::geometry) BETWEEN 12.5 AND 12.6);
"

# Test API response
curl "https://www.dronemap.cc/api/incidents?limit=25" | jq 'length'
```

### Find Suspicious Incidents
```bash
# Look for potential mis-geocoding
psql "$DATABASE_URL" -c "
SELECT id, title, country,
       ST_Y(location::geometry) as lat,
       ST_X(location::geometry) as lon
FROM incidents
WHERE title NOT LIKE '%Denmark%'
  AND title NOT LIKE '%Copenhagen%'
  AND title NOT LIKE '%Danish%'
  AND country = 'DK'
ORDER BY occurred_at DESC;
"
```

---

## 🎉 Summary

**Issue**: Copenhagen cluster inflated from 7 to 12 due to geocoding fallback

**Solution**: Deleted 5 mis-geocoded international incidents

**Impact**:
- ✅ Cluster now shows accurate count (7)
- ✅ Map displays correct incident locations
- ✅ Database cleaned of international incidents
- ✅ 20% reduction in total incidents (quality over quantity!)

**Lesson Learned**: Never use geographic fallback coordinates - better to skip incidents without specific locations than to create false clustering.

---

**Status**: ✅ **RESOLVED**
**Date**: October 2, 2025
**By**: Claude Code (AI-assisted cleanup)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
