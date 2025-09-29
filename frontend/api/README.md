# DroneWatch API - Vercel Deployment

FastAPI backend converted to Vercel serverless functions.

## 🚀 Deployment Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Add Vercel API functions"
git push origin main
```

### 2. Deploy to Vercel

#### Via CLI:
```bash
npm i -g vercel
vercel

# Follow prompts:
# - Link to existing project or create new
# - Project name: dronewatch-api
# - Framework: Other
# - Root directory: ./
```

#### Via Dashboard:
1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repo
3. Root Directory: Leave as `./`
4. Framework Preset: Other

### 3. Set Environment Variables

In Vercel Dashboard > Settings > Environment Variables, add:

```env
# Option 1: Using Supabase credentials
SUPABASE_URL=https://uhwsuaebakkdmdogzrrz.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key

# Option 2: Direct database URL (recommended for better performance)
DATABASE_URL=postgresql://postgres.uhwsuaebakkdmdogzrrz:[SERVICE_KEY]@aws-0-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true

# Security
INGEST_TOKEN=your-secure-token-here

# CORS
ALLOWED_ORIGINS=https://dronewatch.cc,https://dronewatch.vercel.app
```

### 4. Test Deployment

Your API will be available at:
- `https://your-project.vercel.app/api`
- `https://your-project.vercel.app/api/docs` (Interactive docs)

Test endpoints:
```bash
# Health check
curl https://your-project.vercel.app/api/healthz

# List incidents
curl https://your-project.vercel.app/api/incidents?min_evidence=2
```

## 📁 Structure

```
api/
├── index.py          # Main API handler
├── requirements.txt  # Python dependencies
vercel.json          # Vercel configuration
```

## 🔄 Endpoints

All endpoints are prefixed with `/api`:

- `GET /api` - Status
- `GET /api/healthz` - Health check
- `GET /api/incidents` - List incidents
- `GET /api/incidents/{id}` - Get incident
- `POST /api/ingest` - Add incident (protected)
- `GET /api/embed/snippet` - Get embed code
- `GET /api/docs` - Interactive documentation

## 🔒 Security

- Database uses service role (server-side only)
- Ingest endpoint requires Bearer token
- CORS configured for your domains

## ⚡ Performance Notes

- Cold starts: ~1-2s (Python on Vercel)
- Use connection pooling via pgbouncer
- Cache headers set to 15s for incidents
- Consider Edge Functions for faster response

## 🐛 Troubleshooting

### Database connection fails
- Check DATABASE_URL format
- Ensure using pooler URL with pgbouncer
- Verify service key is correct

### CORS errors
- Add your domain to ALLOWED_ORIGINS env var
- Check vercel.json headers configuration

### 500 errors
- Check Vercel Functions logs
- Verify all env vars are set
- Test SQL schema is deployed to Supabase

## 🔄 Updates

Deploy updates:
```bash
git push origin main
# Vercel auto-deploys on push
```

Or manual:
```bash
vercel --prod
```