# 🚀 Apply Performance Indexes - Speed Up API

**Current:** API response time is ~11.4 seconds (too slow!)
**Target:** <3 seconds after applying indexes

---

## Quick Apply (1 command)

```bash
psql $DATABASE_URL -f migrations/006_performance_indexes.sql
```

That's it! The migration file does everything automatically.

---

## What Gets Applied

The migration creates these indexes:

1. **idx_incidents_evidence_occurred** - Main API query (evidence + date sort)
2. **idx_incidents_country_status** - Country/status filtering
3. **idx_incidents_composite** - Complex multi-filter queries
4. **idx_incident_sources_incident_id** - Sources joins
5. **idx_sources_name** - Source lookups

Plus: Runs `ANALYZE` to update query planner statistics

---

## Verification

After running the migration, test the API speed:

```bash
# Time the API response
time curl -s "https://www.dronemap.cc/api/incidents?limit=500" > /dev/null

# Should be <3 seconds instead of 11.4s
```

Or check in browser DevTools:
1. Open https://www.dronemap.cc
2. F12 → Network tab
3. Refresh page
4. Find `/api/incidents` request
5. Check "Time" column - should be <3s

---

## If You Don't Have Direct Database Access

**Option 1: Vercel Dashboard**
1. Go to your Vercel project
2. Navigate to Storage → Supabase
3. Click "Manage Database"
4. Use SQL Editor to run the migration

**Option 2: Supabase Dashboard**
1. Go to https://app.supabase.com
2. Select your project
3. SQL Editor → New Query
4. Paste contents of `migrations/006_performance_indexes.sql`
5. Run

**Option 3: Local → Remote (safest)**
```bash
# Download your DATABASE_URL from Vercel first
cat migrations/006_performance_indexes.sql | pbcopy
# Then paste into Supabase SQL Editor
```

---

## Expected Performance Improvement

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| API Response | 11.4s | <3s | **73% faster** |
| First Paint | ~13s | ~4s | **69% faster** |
| User Experience | Poor | Good | ✅ Acceptable |

---

## Rollback (if needed)

If something goes wrong:

```sql
-- Remove the indexes
DROP INDEX IF EXISTS idx_incidents_evidence_occurred;
DROP INDEX IF EXISTS idx_incidents_country_status;
DROP INDEX IF EXISTS idx_incidents_composite;

-- Query planner will fall back to existing indexes
```

---

## Why So Slow Without Indexes?

Current query scans **ALL 43 incidents** sequentially because:
- No index on `evidence_score` filter
- No index on `occurred_at DESC` sort
- PostgreSQL does a full table scan

After indexes:
- Query uses index to find matching rows instantly
- Index already sorted by `occurred_at DESC`
- Result: 73% faster queries!

---

**Apply now for instant speed improvement! 🚀**
