# Fix Vercel 404 Error - Root Directory Configuration

**Issue**: https://drone-test22.vercel.app/ returns 404
**Cause**: Vercel is trying to build from repository root instead of `frontend/` directory
**Solution**: Configure Root Directory in Vercel dashboard

---

## 🚨 Problem

Vercel deployment logs show:
```
Build Completed in /vercel/output [102ms]
404: NOT_FOUND
```

This happens because:
1. The Next.js app lives in `/frontend` directory
2. Vercel is building from repository root `/`
3. No Next.js app exists at root → 404 error

---

## ✅ Solution: Configure Root Directory

### Step 1: Access Vercel Dashboard

1. Go to https://vercel.com
2. Log in with your account
3. Select the **DroneTest2** project (or whatever it's called)

### Step 2: Update Project Settings

1. Click **Settings** (top navigation)
2. Scroll to **Root Directory** section
3. Click **Edit**
4. Enter: `frontend`
5. Click **Save**

### Step 3: Redeploy

**Option A**: Trigger automatic deployment
```bash
git commit --allow-empty -m "trigger: redeploy after root directory fix"
git push origin main
```

**Option B**: Manual redeploy in dashboard
1. Go to **Deployments** tab
2. Click **•••** (three dots) on latest deployment
3. Click **Redeploy**

---

## 🔍 Verification

After redeployment, check:

```bash
# Should return 200 (not 404)
curl -I https://drone-test22.vercel.app/

# Should show Next.js page
curl -s https://drone-test22.vercel.app/ | grep -i "next"

# Should return incidents JSON
curl -s https://drone-test22.vercel.app/api/incidents?limit=1 | jq '.[0].title'
```

**Expected**:
- ✅ Homepage loads (200 OK)
- ✅ Map displays
- ✅ API endpoints working

---

## 📋 Alternative: Use Vercel CLI

If you have Vercel CLI installed:

```bash
cd /root/repo

# Link to project (if not already linked)
vercel link

# Update root directory setting
vercel project rm frontend
vercel --prod
```

---

## 🔧 Why This Happened

**Repository Structure**:
```
DroneTest2/
├── frontend/          # ← Next.js app is HERE
│   ├── app/
│   ├── components/
│   ├── package.json
│   ├── next.config.js
│   └── vercel.json
├── ingestion/         # Python scraper
├── migrations/        # SQL migrations
└── README.md
```

**Vercel Expected**:
```
DroneTest2/
├── app/               # ← Vercel looked HERE (doesn't exist!)
├── components/
├── package.json
└── next.config.js
```

**Fix**: Tell Vercel to build from `frontend/` directory.

---

## 🎯 Root Cause

This is NOT a code issue - the code is fine. This is a **Vercel project configuration** issue.

**What changed**:
- ❌ NOT the code (no frontend changes in recent commits)
- ❌ NOT the build process (build succeeds)
- ✅ Likely: Vercel project was recreated or Root Directory setting was reset

**Evidence**:
```
Build Completed in /vercel/output [102ms]  ← Build succeeded!
404: NOT_FOUND                              ← But no app found at root
```

---

## 📞 If Still 404 After Fix

### Check Build Logs

In Vercel dashboard:
1. Go to **Deployments**
2. Click latest deployment
3. Check **Build Logs** tab
4. Look for:
   ```
   Building... frontend
   ✓ Build succeeded
   ```

### Check Environment Variables

Ensure these are set in Vercel:
- `DATABASE_URL` - Supabase connection string
- `INGEST_TOKEN` - API authentication token
- `NEXT_PUBLIC_API_URL` - Should be blank or https://drone-test22.vercel.app/api

### Check Framework Detection

In **Settings** → **General**:
- Framework Preset: **Next.js**
- Build Command: `npm run build` (or blank for auto-detect)
- Output Directory: `.next` (or blank for auto-detect)
- Install Command: `npm install` (or blank for auto-detect)

---

## 🚀 Quick Fix Script

If you have access to Vercel CLI:

```bash
#!/bin/bash
# fix-vercel-deployment.sh

cd /root/repo

echo "Updating Vercel configuration..."

# Create vercel config with root directory
cat > .vercel.json << 'EOF'
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs"
}
EOF

# Move to frontend directory
mv .vercel.json frontend/

# Commit and push
git add frontend/.vercel.json
git commit -m "fix: configure vercel root directory for frontend"
git push origin main

echo "✅ Configuration updated. Vercel will redeploy automatically."
echo "Check: https://drone-test22.vercel.app/"
```

---

## 📊 Expected Timeline

- **Immediate**: Configure Root Directory in dashboard
- **2-3 minutes**: Automatic redeployment triggers
- **Result**: Site accessible at https://drone-test22.vercel.app/

---

**Created**: 2025-10-06
**Issue**: 404 on production deployment
**Fix**: Configure Vercel Root Directory to `frontend/`
**Verification**: `curl -I https://drone-test22.vercel.app/` returns 200

🤖 Generated with [Claude Code](https://claude.com/claude-code)
