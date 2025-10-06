# 🚀 Vercel Environment Variables Update Guide

**Project**: drone-test22
**URL**: https://vercel.com/arnarssons-projects/drone-test22
**Issue**: Using wrong database (old cloud Supabase instead of local)

---

## 📋 Step-by-Step Instructions

### Step 1: Go to Environment Variables

1. Visit: **https://vercel.com/arnarssons-projects/drone-test22/settings/environment-variables**
2. Or: Project → Settings → Environment Variables

---

### Step 2: Update/Add These Variables

#### ✅ Required Variables

| Variable Name | Value | Environment |
|--------------|-------|-------------|
| `DATABASE_URL` | `postgresql://postgres:El54d9tlwzgmn7EH18K1vLfVXjKg5CCA@135.181.101.70:5432/postgres` | Production, Preview, Development |
| `SUPABASE_URL` | `http://supabasekong-gsow04o4kw04w88kw0ckwkgg.135.181.101.70.sslip.io` | Production, Preview, Development |
| `SUPABASE_ANON_KEY` | `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTY5NDE2MCwiZXhwIjo0OTE1MzY3NzYwLCJyb2xlIjoiYW5vbiJ9.imh4Gy2AbNyD8fE3ymN3WjrXofgT1vFp6zhFk5_-CHw` | Production, Preview, Development |
| `SUPABASE_SERVICE_KEY` | `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTY5NDE2MCwiZXhwIjo0OTE1MzY3NzYwLCJyb2xlIjoic2VydmljZV9yb2xlIn0.hRzUV1kpd9fChE_rcgjJ3JnAj3QDUQaUPBfxho_WA7U` | Production, Preview, Development |
| `INGEST_TOKEN` | `dw-secret-2025-nordic-drone-watch` | Production, Preview, Development |

---

### Step 3: How to Add/Update Each Variable

For **each variable** above:

1. Click **"Add New"** (or "Edit" if it exists)
2. **Name**: Enter the variable name (e.g., `DATABASE_URL`)
3. **Value**: Paste the value from the table above
4. **Environments**: Select **all three** (Production, Preview, Development)
5. Click **"Save"**

---

### Step 4: Delete Old Cloud Supabase Variables (Optional)

If you see these old variables, you can delete them:
- Any DATABASE_URL pointing to `aws-1-eu-north-1.pooler.supabase.com`
- Any old SUPABASE_URL/keys from cloud Supabase

---

### Step 5: Trigger Redeploy

After updating all variables:

**Option A: From Vercel Dashboard**
1. Go to: https://vercel.com/arnarssons-projects/drone-test22
2. Click **"Deployments"** tab
3. Find the latest deployment
4. Click **"..."** (three dots)
5. Click **"Redeploy"**
6. Click **"Redeploy"** again to confirm

**Option B: Push a commit**
```bash
cd /root/repo
git commit --allow-empty -m "chore: trigger redeploy with new Supabase env vars"
git push origin main
```

---

## ⚠️ Important Prerequisites

### Check These Before Updating:

#### 1. PostgreSQL Port Must Be Exposed

Your local server at `135.181.101.70` must:
- ✅ Have port 5432 open in firewall
- ✅ PostgreSQL listening on `0.0.0.0` (all interfaces)
- ✅ Accept connections from Vercel's IP ranges

**Test from Vercel:**
After updating, Vercel will try to connect. If it fails, check:

```bash
# On your server (135.181.101.70)
sudo ufw status | grep 5432
# Should show: 5432 ALLOW Anywhere

# Check PostgreSQL is listening
sudo netstat -tlnp | grep 5432
# Should show: 0.0.0.0:5432
```

#### 2. Schema Compatibility

**Current Issue**: Your local Supabase uses PostGIS geometry, but the API code might expect separate lat/lon columns.

**Check after redeploy:**
- If you get errors about missing columns (`lat` or `lon`)
- The API code in `/root/repo/frontend/api/db.py` may need updating

---

## 🎯 Expected Result

After updating and redeploying:

1. **Visit**: https://drone-test22.vercel.app/
2. **Map should show**:
   - ✅ Only 2 test incidents (from local Supabase)
   - ✅ No clustering at default coordinates
   - ✅ Clean, fresh database

3. **Verify with API**:
```bash
curl "https://drone-test22.vercel.app/api/incidents?limit=5"
```

Should return:
- Test incidents from local Supabase
- Different IDs than before
- Proper coordinates

---

## 🔍 Troubleshooting

### Problem: "Connection refused" or "timeout"

**Cause**: Vercel can't reach your server on port 5432

**Fix**:
1. Expose port 5432 on your server
2. Or use REST API approach (see alternative below)

### Problem: "Column 'lat' does not exist"

**Cause**: Local Supabase schema uses PostGIS, not lat/lon columns

**Fix**:
1. Add lat/lon columns to local Supabase, OR
2. Update API code to use PostGIS geometry

### Problem: Still showing old data

**Cause**: Vercel is caching or using old env vars

**Fix**:
1. Hard refresh: Ctrl+Shift+R
2. Force redeploy
3. Check env vars are saved correctly

---

## 🔄 Alternative: Use REST API (No Port Exposure Needed)

If you **cannot expose port 5432**, use the REST API instead:

### Update These Variables:
```
DATABASE_URL=(leave empty or remove)
SUPABASE_URL=http://supabasekong-gsow04o4kw04w88kw0ckwkgg.135.181.101.70.sslip.io
SUPABASE_ANON_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
SUPABASE_SERVICE_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
USE_REST_API=true
```

**But**: This requires code changes to use HTTP requests instead of asyncpg.

---

## 📊 Quick Reference

**Old Config (Wrong):**
```
DATABASE_URL=postgresql://postgres.uhwsuaebakkdmdogzrrz:...@aws-1-eu-north-1.pooler.supabase.com:6543/postgres
```

**New Config (Correct):**
```
DATABASE_URL=postgresql://postgres:El54d9tlwzgmn7EH18K1vLfVXjKg5CCA@135.181.101.70:5432/postgres
SUPABASE_URL=http://supabasekong-gsow04o4kw04w88kw0ckwkgg.135.181.101.70.sslip.io
SUPABASE_ANON_KEY=eyJ0eXAiOiJKV1Qi...
SUPABASE_SERVICE_KEY=eyJ0eXAiOiJKV1Qi...
```

---

## ✅ Verification Checklist

After updating and redeploying:

- [ ] Visit https://drone-test22.vercel.app/
- [ ] Map loads without errors
- [ ] No clustering of 22 incidents at one point
- [ ] Only 2 test incidents visible
- [ ] API endpoint returns local Supabase data: `curl https://drone-test22.vercel.app/api/incidents?limit=3`
- [ ] Check browser console for no errors

---

**Direct Link to Env Vars**: https://vercel.com/arnarssons-projects/drone-test22/settings/environment-variables

**Time Required**: 5-10 minutes

**Priority**: 🔴 Critical (fixes clustering issue)

---

**Last Updated**: October 6, 2025
