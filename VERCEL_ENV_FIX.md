# Fix Vercel API Error - Missing Environment Variables

**Issue**: API returns 500 error - "Error loading incidents"
**Cause**: `DATABASE_URL` environment variable not configured in Vercel
**Solution**: Add environment variables in Vercel dashboard

---

## 🚨 Current Error

**Frontend shows**: "Error loading incidents. Retrying..."
**API endpoint**: https://drone-test22.vercel.app/api/incidents
**Status**: 500 Internal Server Error
**Root cause**: `DATABASE_URL` not configured

---

## ✅ Solution: Configure Environment Variables

### Step 1: Access Vercel Dashboard

1. Go to https://vercel.com
2. Log in to your account
3. Select the **drone-test22** project (or DroneTest2)

### Step 2: Add Environment Variables

1. Click **Settings** (top navigation)
2. Click **Environment Variables** (left sidebar)
3. Add the following variables:

#### Required Variables

**DATABASE_URL**
- **Key**: `DATABASE_URL`
- **Value**: Your Supabase connection string
- **Environment**: Production, Preview, Development (all checked)
- **Format**: `postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:6543/postgres`

**INGEST_TOKEN**
- **Key**: `INGEST_TOKEN`
- **Value**: `dw-secret-2025-nordic-drone-watch` (or your custom token)
- **Environment**: Production, Preview, Development (all checked)

#### Optional Variables

**NEXT_PUBLIC_API_URL**
- **Key**: `NEXT_PUBLIC_API_URL`
- **Value**: Leave blank (defaults to same domain)
- **Note**: Only needed if API is on different domain

### Step 3: Redeploy

After adding environment variables, redeploy:

**Option A**: Automatic redeploy
```bash
git commit --allow-empty -m "trigger: redeploy after env vars"
git push origin main
```

**Option B**: Manual redeploy in dashboard
1. Go to **Deployments** tab
2. Click **•••** on latest deployment
3. Click **Redeploy**
4. ✅ Check "Use existing Build Cache" for faster deployment

---

## 🔍 How to Get DATABASE_URL

### From Supabase Dashboard

1. Go to https://supabase.com
2. Open your DroneWatch project
3. Click **Settings** (gear icon)
4. Click **Database** (left sidebar)
5. Scroll to **Connection string**
6. Select **Connection pooling** tab
7. Mode: **Transaction**
8. Copy the connection string

**Format**:
```
postgresql://postgres.PROJECT_ID:[YOUR-PASSWORD]@aws-0-REGION.pooler.supabase.com:6543/postgres
```

**Important**:
- Use port **6543** (transaction pooler, not 5432 direct)
- Replace `[YOUR-PASSWORD]` with your actual database password
- Use the **pooler** endpoint for serverless (better performance)

---

## 🧪 Verification

After redeployment with environment variables:

### Test API Directly
```bash
# Should return incidents JSON (not 500 error)
curl "https://drone-test22.vercel.app/api/incidents?limit=3"

# Should show 200 OK
curl -I "https://drone-test22.vercel.app/api/incidents"
```

### Check Frontend
1. Open https://drone-test22.vercel.app/
2. Map should load with incident markers
3. No "Error loading incidents" message
4. Incident details should appear in popups

---

## 📋 Complete Environment Variables Checklist

For a fully working deployment, ensure these are set:

### Production Environment
- [ ] `DATABASE_URL` - Supabase connection string with pooler (port 6543)
- [ ] `INGEST_TOKEN` - API authentication token
- [ ] Root Directory set to `frontend` (see VERCEL_404_FIX.md)

### Optional (for advanced features)
- [ ] `NEXT_PUBLIC_MAPBOX_TOKEN` - If using Mapbox instead of OpenStreetMap
- [ ] `NEXT_PUBLIC_API_URL` - Only if API on different domain

---

## 🔧 Troubleshooting

### If Still Getting 500 Error

**Check Vercel Function Logs**:
1. Vercel Dashboard → **Deployments**
2. Click latest deployment
3. Click **Functions** tab
4. Click **api/incidents.py**
5. View logs for error details

**Common Issues**:

**"DATABASE_URL not configured"**
- Fix: Add DATABASE_URL in environment variables
- Verify: Check Settings → Environment Variables

**"Connection timeout"**
- Fix: Use port 6543 (pooler) not 5432 (direct)
- Format: `...pooler.supabase.com:6543/postgres`

**"SSL required"**
- Fix: Ensure connection string includes SSL mode
- Add: `?sslmode=require` to connection string if needed

### Verify Environment Variables Are Set

```bash
# Using Vercel CLI (if installed)
vercel env ls

# Should show:
# DATABASE_URL    Production, Preview, Development
# INGEST_TOKEN    Production, Preview, Development
```

---

## 🚀 Quick Fix Steps Summary

1. **Vercel Dashboard** → Settings → Environment Variables
2. **Add** `DATABASE_URL` = `postgresql://postgres:[PASSWORD]@...supabase.com:6543/postgres`
3. **Add** `INGEST_TOKEN` = `dw-secret-2025-nordic-drone-watch`
4. **Redeploy** (automatic or manual)
5. **Verify** https://drone-test22.vercel.app/api/incidents returns data

---

## 📊 Expected Result

**Before Fix**:
```bash
$ curl "https://drone-test22.vercel.app/api/incidents"
# Returns: 500 Internal Server Error
```

**After Fix**:
```bash
$ curl "https://drone-test22.vercel.app/api/incidents?limit=1"
# Returns: [{"id":"...", "title":"...", "lat":55.6, "lon":12.6, ...}]
```

**Frontend**:
- ✅ Map loads with markers
- ✅ Incident popups show details
- ✅ No error messages
- ✅ Analytics page shows statistics

---

## 🔒 Security Note

**Never commit DATABASE_URL to git!**
- ❌ Don't add to `.env.local` in repository
- ❌ Don't hardcode in code
- ✅ Only in Vercel dashboard environment variables
- ✅ Keep in password manager

---

## 📞 Related Issues

**If API works but map doesn't load**:
- Check browser console for CORS errors
- Verify `NEXT_PUBLIC_API_URL` (should be blank or correct domain)

**If deployment still fails**:
- See `VERCEL_404_FIX.md` for Root Directory configuration
- Ensure `frontend/` is set as Root Directory

**If scraper can't ingest data**:
- Verify `INGEST_TOKEN` matches in:
  - Vercel environment variables
  - GitHub Actions secrets
  - `ingestion/config.py` (if hardcoded)

---

**Created**: 2025-10-06
**Issue**: API 500 error - DATABASE_URL not configured
**Fix**: Add environment variables in Vercel dashboard
**Priority**: CRITICAL (site won't work without this)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
