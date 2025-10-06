# 🔴 URGENT: Vercel Using Wrong Database

**Date**: October 6, 2025
**Issue**: Clustering problem on https://drone-test22.vercel.app/
**Root Cause**: Vercel still connected to OLD cloud Supabase, not local self-hosted instance

---

## 🎯 Problem

Your Vercel deployment at **drone-test22.vercel.app** is showing 22 incidents clustered at one location because:

1. ❌ **Vercel is using OLD cloud Supabase database**
   - Database: `aws-1-eu-north-1.pooler.supabase.com` (cloud)
   - This database has the old bad geocoding data
   - 4 incidents clustered at default Copenhagen coordinates (55.618, 12.6476)

2. ❌ **Not using your NEW local Supabase**
   - Your local Supabase at `135.181.101.70` is working perfectly
   - REST API tested and operational
   - But Vercel doesn't know about it

---

## 📋 Current Vercel Configuration (WRONG)

**File**: `/root/repo/frontend/.env.production`

```bash
DATABASE_URL="postgresql://postgres.uhwsuaebakkdmdogzrrz:stUPw5co47Yq8uSI@aws-1-eu-north-1.pooler.supabase.com:6543/postgres"
```

This is the **OLD cloud Supabase** with bad data.

---

## ✅ Required Fix

### Option 1: Use Local Supabase with PostgreSQL (If Port Exposed)

**IF you've exposed port 5432** on your local server:

```bash
DATABASE_URL="postgresql://postgres:El54d9tlwzgmn7EH18K1vLfVXjKg5CCA@135.181.101.70:5432/postgres"
SUPABASE_URL="http://supabasekong-gsow04o4kw04w88kw0ckwkgg.135.181.101.70.sslip.io"
SUPABASE_ANON_KEY="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTY5NDE2MCwiZXhwIjo0OTE1MzY3NzYwLCJyb2xlIjoiYW5vbiJ9.imh4Gy2AbNyD8fE3ymN3WjrXofgT1vFp6zhFk5_-CHw"
SUPABASE_SERVICE_KEY="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTY5NDE2MCwiZXhwIjo0OTE1MzY3NzYwLCJyb2xlIjoic2VydmljZV9yb2xlIn0.hRzUV1kpd9fChE_rcgjJ3JnAj3QDUQaUPBfxho_WA7U"
INGEST_TOKEN="dw-secret-2025-nordic-drone-watch"
```

### Option 2: Use Local Supabase via REST API (Recommended)

**This works NOW** without exposing PostgreSQL:

You need to **rewrite the API code** to use PostgREST instead of direct PostgreSQL:

1. Modify `/root/repo/frontend/api/db.py` to use HTTP requests
2. Use the Kong gateway URL for all queries
3. Use ANON_KEY for reads, SERVICE_KEY for writes

---

## 🚀 How to Update Vercel Environment Variables

### Step 1: Go to Vercel Dashboard

1. Visit: https://vercel.com/arnarssons-projects/dronetest
2. Go to **Settings** → **Environment Variables**

### Step 2: Update Variables

**Delete or update:**
- `DATABASE_URL` - Change to local Supabase connection string

**Add new:**
- `SUPABASE_URL` - `http://supabasekong-gsow04o4kw04w88kw0ckwkgg.135.181.101.70.sslip.io`
- `SUPABASE_ANON_KEY` - (see above)
- `SUPABASE_SERVICE_KEY` - (see above)

### Step 3: Redeploy

After updating env vars, trigger a new deployment:

```bash
# Option A: Push a commit
git commit --allow-empty -m "chore: trigger redeploy with new env vars"
git push origin main

# Option B: Redeploy from Vercel dashboard
# Go to Deployments → Click "..." → "Redeploy"
```

---

## ⚠️ Important Notes

### Schema Differences

**Cloud Supabase (old):**
- Has `lat` and `lon` columns (separate)
- Old geocoding with clustering issues

**Local Supabase (new):**
- Uses PostGIS `location` geometry column
- No separate lat/lon columns
- Better geocoding

**Result**: The API code needs to handle both schemas OR you need to migrate the local Supabase to have the same schema.

### Network Access

**Issue**: Vercel is hosted on AWS/Vercel infrastructure. Your local Supabase is at `135.181.101.70`.

**Requirements:**
- ✅ Port 5432 must be accessible from Vercel's servers (if using PostgreSQL)
- ✅ OR use REST API on port 8000 (Kong gateway - tested working)
- ⚠️ Check firewall allows Vercel IP ranges

---

## 🎯 Recommended Immediate Action

**Quick Fix (5 minutes):**

1. **Expose PostgreSQL port 5432** on your server (if not done)
2. **Update Vercel env vars** to use local Supabase
3. **Redeploy** Vercel app
4. **Test** at drone-test22.vercel.app

**Better Fix (30 minutes):**

1. **Keep using REST API** (no port exposure needed)
2. **Rewrite API code** to use HTTP instead of asyncpg
3. **Update Vercel env vars** with REST API URL
4. **Redeploy** and test

---

## 🔍 Verification

After updating and redeploying, verify:

```bash
# Test API endpoint
curl "https://drone-test22.vercel.app/api/incidents?limit=5"

# Check coordinates are different
curl "https://drone-test22.vercel.app/api/incidents?limit=100" | jq -r '.[] | "\(.lat),\(.lon)"' | sort | uniq -c | sort -rn

# Should NOT show 4+ incidents at 55.618,12.6476
```

---

## 📊 Current State Summary

| Component | Status | Database |
|-----------|--------|----------|
| **Local Supabase** | ✅ Working | Self-hosted at 135.181.101.70 |
| **Vercel Deployment** | ❌ Wrong DB | Cloud Supabase (old) |
| **Production Site** | ❓ Unknown | Need to check |

---

**Action Required**: Update Vercel environment variables to point to local Supabase

**Impact**: Will fix clustering issue on drone-test22.vercel.app

**Time Estimate**: 5-10 minutes (env var update + redeploy)

---

**Last Updated**: October 6, 2025
**Priority**: 🔴 URGENT
