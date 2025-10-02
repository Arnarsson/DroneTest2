# Post-Deduplication Status

**Date**: October 1, 2025
**Final Count**: 25 incidents (down from 27)

---

## ✅ What's Working

### Database
- ✅ 2 duplicates successfully merged
- ✅ Sources properly created and linked in `incident_sources` table
- ✅ Model rotation working (DeepSeek → Grok on rate limits)
- ✅ Anti-hallucination system validated

### Merged Incidents
- ✅ **Cluster 1**: Sleipner Field (9 sources total)
- ✅ **Cluster 2**: Copenhagen Airport (1 source)

---

## ⚠️ Issues to Fix

### 1. API Sources Array Empty
**Problem**: API returns `"sources": []` even though database has sources

**Database Query Works**:
```sql
-- This returns 9 sources correctly
SELECT json_agg(json_build_object(...))
FROM incident_sources is2
LEFT JOIN sources s ON is2.source_id = s.id
WHERE is2.incident_id = '24a89a45-72da-49c3-9366-c82c2135fe5b'
```

**Possible Causes**:
1. Vercel serverless function timeout (9s limit)
2. Connection pooling issue with transaction mode
3. Query execution order in `fetch_incidents()`

**Location**: `frontend/api/db.py` lines 79-90

**Fix Needed**: Debug why subquery returns empty array in serverless context

---

### 2. Evidence Score Stuck at 1
**Problem**: Both merged incidents show `evidence_score = 1` despite having sources

**Root Cause**: `_recalculate_evidence_score()` logic expects specific `source_type` values:
- Looks for: `police`, `military`, `notam`, `official`, `government`
- Actually has: `other` (all merged duplicates)

**Current Logic** (ai_deduplicate_batch.py:492-506):
```python
official_types = ['police', 'military', 'notam', 'official', 'government']
if any(st in official_types for st in source_types):
    return 4

verified_types = ['news', 'media', 'verified']
verified_count = sum(1 for st in source_types if st in verified_types)

if verified_count >= 2:
    return 3
elif verified_count >= 1:
    return 2
else:
    return 1  # ← All merged sources end up here
```

**Fix Options**:
1. Change merged source type from `'other'` to `'media'`
2. Add `'other'` to verified_types with count-based logic
3. Use source count directly: `min(4, 1 + (source_count // 3))`

---

### 3. Old "Merged Duplicate" Sources
**Problem**: Incident `24a89a45...` has 8 sources from previous test runs

**Evidence**:
- All have `source_type = 'other'`
- All have name = "Merged Duplicate"
- URLs point to other incidents (not real sources)

**Impact**: Clutters source list, makes it hard to see actual merged duplicate

**Fix**: Clean up test data from previous runs:
```sql
DELETE FROM incident_sources
WHERE source_id IN (
  SELECT id FROM sources
  WHERE name = 'Merged Duplicate'
  AND source_type = 'other'
);
```

---

## 📋 Action Items

### High Priority
1. 🔧 **Fix API sources query** - Debug why sources array is empty
2. 🔧 **Fix evidence score calculation** - Update logic to count merged sources
3. 🧹 **Clean test data** - Remove old "Merged Duplicate" sources

### Medium Priority
4. 📊 **Update CLAUDE.md** - Document deduplication completion
5. 🔄 **Schedule regular dedup** - Add weekly cron job
6. 📈 **Add monitoring** - Track merge quality and false positives

### Low Priority
7. 🎨 **Frontend display** - Show merged sources in UI
8. 📝 **User feedback** - Add merge quality rating
9. 📜 **Audit log** - Track deduplication history

---

## Quick Fixes

### Fix Evidence Score
```python
# ai_deduplicate_batch.py, replace lines 492-506 with:

# Count all sources, not just by type
source_count = len(sources)

# Simple count-based scoring
if source_count >= 6:
    return 4  # Many sources
elif source_count >= 3:
    return 3  # Multiple sources
elif source_count >= 1:
    return 2  # At least one source
else:
    return 1  # No sources
```

### Clean Test Data
```sql
-- Remove old test sources
DELETE FROM sources
WHERE name = 'Merged Duplicate'
AND source_type = 'other'
AND homepage_url LIKE 'https://www.dronemap.cc/incident/%';

-- Keep only the internal:// merged sources
-- (These are legitimate merged duplicates from today's run)
```

---

## Testing Commands

### Verify Sources in Database
```bash
psql $DATABASE_URL -c "
SELECT i.title, COUNT(s.id) as sources
FROM incidents i
LEFT JOIN incident_sources s ON i.id = s.incident_id
WHERE i.id IN (
  '24a89a45-72da-49c3-9366-c82c2135fe5b',
  '0e7a4198-4e93-4cf7-ad2e-9b464b0f7813'
)
GROUP BY i.id, i.title;
"
```

### Test API Response
```bash
curl -s "https://www.dronemap.cc/api/incidents?limit=5" | \
  jq '.[] | {title, evidence_score, source_count: (.sources | length)}'
```

### Run Deduplication Again
```bash
# Dry run to check for new duplicates
python3 scripts/ai_deduplicate_batch.py --dry-run

# Execute with auto-approve
python3 scripts/ai_deduplicate_batch.py --execute --auto-approve 0.8
```

---

## Summary

### ✅ Deduplication System Status
- **Core functionality**: Working ✅
- **Model rotation**: Working ✅
- **Anti-hallucination**: Working ✅
- **Database operations**: Working ✅

### ⚠️ Post-Merge Issues
- **API sources display**: Needs debugging
- **Evidence scoring**: Needs logic update
- **Test data cleanup**: Needs manual cleanup

### 📈 Impact
- Database cleaned: 27 → 25 incidents
- Duplicates identified: 2 confirmed, 2 rejected
- System ready for: Regular production use (after fixes)

---

**Next Steps**:
1. Debug API sources query (highest priority)
2. Update evidence score logic
3. Clean test data
4. Deploy fixes to production

🤖 Generated with [Claude Code](https://claude.com/claude-code)
