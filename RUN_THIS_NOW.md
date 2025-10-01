# 🚨 RUN THIS NOW - Remove Duplicates

## Quick Instructions

**You have 32 duplicate incidents. Run these commands to fix:**

### Option 1: If you have DATABASE_URL

```bash
# Get DATABASE_URL from Vercel or Supabase first
export DATABASE_URL="your-connection-string"

# Run migrations in order:
psql $DATABASE_URL -f migrations/006_performance_indexes.sql
psql $DATABASE_URL -f migrations/007_merge_duplicate_incidents.sql

# Done! Check results:
curl -s "https://www.dronemap.cc/api/incidents?limit=50" | python3 -c "import sys,json; print(f'Incidents: {len(json.load(sys.stdin))}')"
```

### Option 2: Supabase Dashboard (No Terminal)

1. Go to https://app.supabase.com
2. Select DroneWatch project
3. Click "SQL Editor"
4. Click "New Query"
5. Copy **ALL** of `migrations/006_performance_indexes.sql`
6. Paste and click "Run"
7. Wait for success
8. Click "New Query" again
9. Copy **ALL** of `migrations/007_merge_duplicate_incidents.sql`
10. Paste and click "Run"
11. Done!

---

## What Will Happen

**Before:**
- 46 incidents (22 duplicates + 10 duplicates + 14 unique)
- Map shows "33" cluster marker
- Looks unprofessional

**After:**
- ~14-16 unique incidents
- Each with multiple sources
- Clean map
- Professional appearance

**Time:** 5 minutes total

---

## Verification

After running, refresh https://www.dronemap.cc and check:
- Incident count should drop to ~14-16
- No more "33" cluster marker
- Each incident shows multiple sources
- Map looks clean

---

**DO THIS NOW - It's critical for credibility!**
