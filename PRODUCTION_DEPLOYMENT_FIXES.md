# Production Deployment Fixes - drone-test22.vercel.app

**Site**: https://drone-test22.vercel.app/
**Status**: Needs configuration in Vercel Dashboard
**Issues**: 2 configuration problems (both fixable in dashboard)

---

## 🚨 Current Issues

### Issue 1: 404 NOT_FOUND (Homepage)
**Symptom**: Site shows 404 error page
**Cause**: Vercel Root Directory not configured
**Fix**: Set Root Directory to `frontend` in Vercel dashboard

### Issue 2: 500 API Error (Backend)
**Symptom**: "Error loading incidents. Retrying..."
**Cause**: `DATABASE_URL` environment variable not set
**Fix**: Add environment variables in Vercel dashboard

---

## ✅ Complete Fix Instructions

### Step 1: Configure Root Directory

**Why**: The Next.js app is in `frontend/` subdirectory, not repository root

**How**:
1. Go to https://vercel.com
2. Open **drone-test22** project
3. Settings → **General**
4. Find **Root Directory** section
5. Click **Edit**
6. Enter: `frontend`
7. Click **Save**

**Documentation**: See `VERCEL_404_FIX.md`

---

### Step 2: Add Environment Variables

**Why**: API needs database connection string to fetch incidents

**How**:
1. Still in Settings, click **Environment Variables** (left sidebar)
2. Add these variables:

**DATABASE_URL** (Required)
```
Key: DATABASE_URL
Value: postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:6543/postgres
Environments: ✓ Production ✓ Preview ✓ Development
```

**INGEST_TOKEN** (Required)
```
Key: INGEST_TOKEN
Value: dw-secret-2025-nordic-drone-watch
Environments: ✓ Production ✓ Preview ✓ Development
```

3. Click **Save** after each variable

**Documentation**: See `VERCEL_ENV_FIX.md`

---

### Step 3: Redeploy

**Option A**: Automatic (push a commit)
```bash
git commit --allow-empty -m "trigger: redeploy with fixes"
git push origin main
```

**Option B**: Manual (Vercel dashboard)
1. Go to **Deployments** tab
2. Click **•••** on latest deployment
3. Click **Redeploy**
4. ✓ Check "Use existing Build Cache"

---

## 🔍 Verification Checklist

After redeployment, verify:

### Homepage (Issue 1 Fixed)
```bash
curl -I https://drone-test22.vercel.app/
# Should return: HTTP/2 200 (not 404)
```

### API Endpoint (Issue 2 Fixed)
```bash
curl "https://drone-test22.vercel.app/api/incidents?limit=1"
# Should return: [{"id":"...", "title":"...", ...}]
```

### Frontend Functionality
- [ ] Homepage loads (no 404)
- [ ] Map displays
- [ ] Incident markers appear
- [ ] Click marker → popup shows incident details
- [ ] No "Error loading incidents" message
- [ ] Analytics page works
- [ ] List view shows incidents

---

## 📊 Before/After

### Before Fixes
```
Homepage:  404 NOT_FOUND
API:       500 Internal Server Error
Frontend:  "Error loading incidents. Retrying..."
Map:       Empty (no data)
```

### After Fixes
```
Homepage:  200 OK ✓
API:       Returns incidents JSON ✓
Frontend:  Map loads with markers ✓
Map:       Shows 27+ incidents ✓
```

---

## 🎯 Why This Happened

### Root Directory Issue
**Problem**: Vercel project configuration reset or not initially set
**Evidence**: Build succeeds but outputs to wrong location
**Not a code issue**: Code is fine, just configuration

### Environment Variables Issue
**Problem**: New Vercel project doesn't have environment variables
**Evidence**: API code expects `DATABASE_URL` but it's not set
**Not a code issue**: Code is fine, just missing configuration

---

## 🔧 Troubleshooting

### If Still 404 After Root Directory Fix

1. Check Settings → General → Root Directory shows `frontend`
2. Check Build Logs show "Building... frontend"
3. Try redeploying from scratch (not using cache)

### If Still 500 After Environment Variables

1. Verify environment variables are set:
   - Settings → Environment Variables
   - Both `DATABASE_URL` and `INGEST_TOKEN` should be listed
2. Check DATABASE_URL format:
   - Must use port **6543** (pooler, not 5432 direct)
   - Format: `postgresql://...@...pooler.supabase.com:6543/postgres`
3. Check Vercel Function Logs:
   - Deployments → Latest → Functions → api/incidents.py
   - Look for specific error message

### If Both Fixed But Map Still Empty

**Check Supabase Database**:
```sql
-- In Supabase SQL Editor
SELECT COUNT(*) FROM incidents;
-- Should return 27 or more

SELECT id, title, evidence_score FROM incidents LIMIT 5;
-- Should show incident data
```

**If database is empty**: The scraper needs to run (GitHub Actions every 15 min)

---

## 📞 Quick Reference

| Issue | Fix Location | Setting | Value |
|-------|--------------|---------|-------|
| 404 Error | Settings → General | Root Directory | `frontend` |
| API 500 | Settings → Environment Variables | DATABASE_URL | `postgresql://...` |
| API Auth | Settings → Environment Variables | INGEST_TOKEN | `dw-secret-...` |

---

## 🚀 Expected Timeline

1. **Configure settings**: 2-3 minutes
2. **Redeploy**: 2-3 minutes (automatic)
3. **Verify**: 30 seconds
4. **Total**: ~5-10 minutes

---

## 📝 Related Documentation

- `VERCEL_404_FIX.md` - Detailed Root Directory fix
- `VERCEL_ENV_FIX.md` - Detailed environment variables fix
- `DEPLOYMENT_CHECKLIST.md` - Full deployment guide
- `HANDOFF.md` - Session handoff for next developer

---

## ✅ Final Checklist

Before considering deployment complete:

- [ ] Root Directory set to `frontend`
- [ ] DATABASE_URL environment variable added
- [ ] INGEST_TOKEN environment variable added
- [ ] Redeployed after configuration
- [ ] Homepage returns 200 (not 404)
- [ ] API returns incidents JSON (not 500)
- [ ] Map loads with markers
- [ ] No console errors in browser
- [ ] Analytics page works
- [ ] Migration 010 applied in Supabase (for automatic evidence scoring)

---

**Created**: 2025-10-06
**Issues**: Root Directory + Environment Variables
**Fixes**: Dashboard configuration (no code changes needed)
**Priority**: CRITICAL (site won't work until fixed)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
