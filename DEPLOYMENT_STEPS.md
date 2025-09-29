# DroneWatch Deployment Steps

## Current Status
- ✅ Frontend code ready and tested locally (http://localhost:3001)
- ✅ API deployed but missing database config (https://dronewatchv2.vercel.app/api)
- ❌ Frontend not deployed yet
- ❌ Database environment variables not configured

## Steps to Complete Deployment

### 1. Deploy Frontend to Vercel
```bash
cd frontend
npx vercel login  # Login to your Vercel account
npx vercel --prod # Deploy to production
```

### 2. Configure Environment Variables in Vercel Dashboard

Go to https://vercel.com/dashboard and find your `dronewatchv2` project.

#### Add these environment variables for the API:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_SERVICE_KEY` - Your Supabase service role key
- `INGEST_TOKEN` - A secret token for the ingestion endpoint

#### Add these for the Frontend (if deploying separately):
- `NEXT_PUBLIC_API_URL` - Set to `https://dronewatchv2.vercel.app/api`

### 3. Test the Deployment

After setting environment variables:
1. Visit https://dronewatchv2.vercel.app/api/healthz to check API health
2. Visit your frontend URL to see the map
3. Check Chrome DevTools for any errors

### 4. Alternative: Deploy Frontend to Vercel via GitHub

If CLI doesn't work, you can:
1. Push this code to GitHub
2. Import the repository in Vercel dashboard
3. Set the root directory to `frontend/`
4. Deploy

## Local Testing Commands
```bash
# Test API locally
curl https://dronewatchv2.vercel.app/api/incidents

# Run frontend locally
cd frontend
npm run dev
# Visit http://localhost:3001
```

## Debugging Tips
- Check Vercel Function Logs for API errors
- Use Chrome DevTools Network tab to see failed requests
- Verify CORS headers are working
- Check that environment variables are set correctly