# Vercel Environment Variables - Fix Required

**Date**: October 8, 2025
**Status**: 🔴 BLOCKED - Scraper cannot ingest data to production

---

## Problem

The DroneWatch production API (`https://www.dronemap.cc/api/ingest`) is returning **403 Forbidden** with message "Invalid token" when the scraper attempts to POST new incidents.

**Scraper Test Result**:
```bash
$ python3 ingestion/ingest.py
❌ HTTP Error (403): Invalid token
✅ Success: 0
❌ Errors: 8
```

**cURL Test Result**:
```bash
$ curl -X POST 'https://www.dronemap.cc/api/ingest' \
  -H 'Authorization: Bearer dw-secret-2025-nordic-drone-watch' \
  -d '{"title": "test"}'

Error code: 403
Message: Invalid token.
```

---

## Root Cause

The `INGEST_TOKEN` environment variable in **Vercel** is either:
1. Not set correctly
2. Using an old/different token value
3. Missing entirely

**Expected Value**: `dw-secret-2025-nordic-drone-watch`
**Location**: Vercel Dashboard → Project Settings → Environment Variables

---

## Impact

### Current State
- ❌ Scraper runs successfully (45 sources, AI location extraction working)
- ❌ All incidents blocked at API ingestion step (403 errors)
- ❌ Only 6 incidents in production (from manual ingestion)
- ❌ European expansion (7 countries) not reflected in database

### Expected State (After Fix)
- ✅ Scraper successfully posts to production API
- ✅ 20-40 incidents from European sources (DK, NO, SE, FI, GB, DE, PL)
- ✅ Automatic updates every hour/day (when scheduler configured)

---

## Fix Required

### Step 1: Update Vercel Environment Variables

**Platform**: https://vercel.com/arnarssons-projects/dronetest/settings/environment-variables

**Variables to Set**:
```bash
# Required for scraper ingestion
INGEST_TOKEN=dw-secret-2025-nordic-drone-watch

# Required for AI location extraction (already correct)
OPENROUTER_API_KEY=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
OPENROUTER_MODEL=openai/gpt-3.5-turbo

# Required for database (already correct)
DATABASE_URL=postgresql://postgres.uhwsuaebakkdmdogzrrz:stUPw5co47Yq8uSI@aws-1-eu-north-1.pooler.supabase.com:6543/postgres
```

**Scope**: Set for **Production**, **Preview**, and **Development** environments

### Step 2: Redeploy Production

After updating environment variables:
```bash
git push origin main  # Triggers auto-deploy
```

Or manually trigger deployment in Vercel Dashboard.

### Step 3: Verify Fix

Test the API with the correct token:
```bash
curl -X POST 'https://www.dronemap.cc/api/ingest' \
  -H 'Authorization: Bearer dw-secret-2025-nordic-drone-watch' \
  -H 'Content-Type: application/json' \
  -d '{"title": "Test incident", "narrative": "Testing API", "lat": 55.6761, "lon": 12.5683}'
```

Expected response: `{"message": "Incident created", "id": "..."}`

### Step 4: Run Full Scraper

```bash
cd ingestion
python3 ingest.py
```

Expected results:
- ✅ 45+ sources scraped successfully
- ✅ AI location extraction working
- ✅ 15-30 incidents posted to production
- ✅ Success count > 0

---

## Additional Notes

### Why This Happened

The `.env` files are gitignored (correctly) for security, but this means Vercel environment variables must be set manually through the dashboard. The token mismatch likely occurred during initial deployment or when environment variables were reset.

### Security Considerations

**DO NOT** commit the `INGEST_TOKEN` to git. It should only exist in:
- Vercel environment variables (production)
- Local `.env` files (development - gitignored)

### Related Files

- `ingestion/.env` - Local development (already correct)
- `frontend/.env.local` - Frontend dev environment (already correct)
- `CLAUDE.md` - Documentation with expected values
- This file - Production fix instructions

---

## Verification Checklist

After applying the fix:

- [ ] Vercel environment variables updated
- [ ] Production redeployed
- [ ] cURL test returns 200/201 (not 403)
- [ ] Scraper test shows `Success: N` (where N > 0)
- [ ] Production database has 20+ incidents
- [ ] Map shows incidents from multiple countries
- [ ] Evidence scores visible on map

---

**Last Updated**: October 8, 2025
**Next Action**: Update Vercel environment variables in dashboard
