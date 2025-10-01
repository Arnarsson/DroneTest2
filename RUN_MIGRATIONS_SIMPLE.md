# 🚀 Run These Migrations - Simple Guide

**Both migrations are now fixed. Follow these exact steps:**

---

## Step 1: Get to Supabase SQL Editor

1. Go to https://app.supabase.com
2. Sign in
3. Click on your DroneWatch project
4. Click "SQL Editor" in the left sidebar
5. Click "New Query" button

---

## Step 2: Run Migration 007 (Merge Duplicates)

**This removes the 32 duplicate incidents**

1. Open `migrations/007_merge_duplicate_incidents.sql` on your computer
2. **Copy the ENTIRE file** (Cmd+A, Cmd+C)
3. **Paste into Supabase** SQL Editor
4. Click **"Run"** button
5. Wait for success message
6. Should say "X groups merged, Y duplicates removed"

**Expected result:** 46 incidents → ~14-16 incidents

---

## Step 3: Run Migration 006 Indexes (One at a Time)

**Run these 6 commands SEPARATELY (one by one):**

**Command 1:**
```sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_incidents_evidence_occurred
  ON public.incidents(evidence_score, occurred_at DESC)
  WHERE evidence_score >= 1;
```
Click "Run", wait for success.

**Command 2:**
```sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_incidents_country_status
  ON public.incidents(country, status)
  WHERE evidence_score >= 1;
```
Click "Run", wait for success.

**Command 3:**
```sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_incidents_composite
  ON public.incidents(country, status, evidence_score, occurred_at DESC)
  WHERE evidence_score >= 1;
```
Click "Run", wait for success.

**Command 4:**
```sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_incident_sources_incident_id
  ON public.incident_sources(incident_id);
```
Click "Run", wait for success.

**Command 5:**
```sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_incident_sources_source_id
  ON public.incident_sources(source_id);
```
Click "Run", wait for success.

**Command 6:**
```sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sources_name
  ON public.sources(name);
```
Click "Run", wait for success.

**Command 7 (All together):**
```sql
ANALYZE public.incidents;
ANALYZE public.incident_sources;
ANALYZE public.sources;
```
Click "Run", done!

---

## Step 4: Verify Results

**Check incident count:**
```sql
SELECT COUNT(*) as total_incidents FROM public.incidents;
```
Should be ~14-16 instead of 46.

**Check for duplicates:**
```sql
SELECT
    COUNT(*) as incidents_at_location,
    ROUND(ST_Y(location::geometry)::numeric, 2) as lat
FROM incidents
GROUP BY ROUND(ST_Y(location::geometry)::numeric, 2)
ORDER BY incidents_at_location DESC
LIMIT 5;
```
Should NOT show 22 or 10 at any location.

---

## Expected Results

**After Migration 007:**
- ✅ Duplicates merged
- ✅ ~14-16 unique incidents
- ✅ Sources created from duplicate narratives
- ✅ Map shows individual markers (no "33" cluster)

**After Migration 006:**
- ✅ API speed: 11.4s → <3s
- ✅ Fast page loads
- ✅ Better user experience

---

## If You Get Errors

**Migration 007 errors:**
- Copy the error message
- Check Step 2 results (shows what will be merged)
- Can skip and run 006 first if needed

**Migration 006 errors:**
- Make sure you run each CREATE INDEX separately
- Don't run all at once
- Don't put BEGIN/COMMIT around them

---

**Total time: ~5-10 minutes**

**Result: Professional, duplicate-free drone tracking platform!** 🎉
