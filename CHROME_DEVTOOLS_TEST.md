# Chrome DevTools Testing Guide for DroneWatch

## Setup
1. Frontend is running at: **http://localhost:3001** (or 3000)
2. API is deployed at: **https://dronewatchv2-q4a13cy9t-arnarssons-projects.vercel.app/api**

## Chrome DevTools Testing Steps

### 1. Open the Application
```bash
# In Chrome, navigate to:
http://localhost:3001
```

### 2. Open DevTools (F12)

### 3. Network Tab Analysis
1. **Clear the Network tab** (🚫 icon)
2. **Refresh the page** (F5)
3. **Look for API calls:**
   - Filter by "Fetch/XHR"
   - Should see request to: `https://dronewatchv2-q4a13cy9t-arnarssons-projects.vercel.app/api/incidents`

### 4. Expected Issues & Solutions

#### Issue 1: CORS Error
**What you'll see in Console:**
```
Access to fetch at 'https://...' from origin 'http://localhost:3001'
has been blocked by CORS policy
```

**Solution:** Already fixed - API has CORS headers configured

#### Issue 2: 500 Internal Server Error
**What you'll see in Network tab:**
- Status: 500
- Response: "Internal Server Error"

**Cause:** Database connection issue (already identified)

**Current Status:** API returns 500 because database connection fails with:
```json
{
  "error": "'aws-0-us-east-1.pooler.supabase.com' does not appear to be an IPv4 or IPv6 address"
}
```

### 5. Console Tab Checks
Look for:
- JavaScript errors
- Failed resource loads
- React errors

### 6. Test API Directly in Console
Open Console and run:
```javascript
// Test API connection
fetch('https://dronewatchv2-q4a13cy9t-arnarssons-projects.vercel.app/api')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)

// Test incidents endpoint
fetch('https://dronewatchv2-q4a13cy9t-arnarssons-projects.vercel.app/api/incidents')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

### 7. Application Tab
Check:
- Local Storage for any cached data
- Session Storage
- Cookies (if any)

## Current Known Issues

### ✅ Working:
- Frontend loads
- Map component renders
- API base endpoints respond

### ⚠️ Not Working:
- `/api/incidents` returns 500 (database connection issue)
- `/api/healthz` returns error (database connection issue)

### Fix Required:
In Vercel Dashboard, add `DATABASE_URL` environment variable with full Postgres connection string from Supabase.

## Test URLs

### API Endpoints (test in browser):
- API Info: https://dronewatchv2-q4a13cy9t-arnarssons-projects.vercel.app/api
- API Docs: https://dronewatchv2-q4a13cy9t-arnarssons-projects.vercel.app/api/docs
- Health: https://dronewatchv2-q4a13cy9t-arnarssons-projects.vercel.app/api/healthz
- Incidents: https://dronewatchv2-q4a13cy9t-arnarssons-projects.vercel.app/api/incidents

## Quick Fixes

### If map doesn't load:
1. Check Console for Leaflet errors
2. Verify CSS is loaded (check Network tab for leaflet.css)

### If no data shows:
1. Expected - database connection needs fixing
2. Once DATABASE_URL is added in Vercel, redeploy

### If frontend won't connect to API:
1. Check `.env.local` has correct API URL
2. Restart dev server: `npm run dev`